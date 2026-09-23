"""Frozen C-A abstract routing and C-B optional-tool routing."""

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from experiments.model_backend_deepseek.cache_usage import extract
from experiments.model_backend_deepseek.protocol import validate_batch
from llm_chat.search_find_agent import SEARCH_FIND_TOOLS

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
CONFIG = json.loads((ROOT / "experiments/model_backend_deepseek/provider.json").read_text())
CASES = json.loads((HERE / "review_cases.json").read_text())
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"
VERIFY_TOOL = {"type": "function", "function": {
    "name": "verify",
    "description": "Ask a semantic verifier whether an observed C# claim is supported, refuted or still open by specific observed W# excerpts. This retrieves no new corpus text.",
    "parameters": {"type": "object", "properties": {
        "claim_ref": {"type": "string", "pattern": "^C[1-9][0-9]*$"},
        "evidence_refs": {"type": "array", "items": {"type": "string", "pattern": "^W[1-9][0-9]*$"},
                          "minItems": 1, "uniqueItems": True}},
        "required": ["claim_ref", "evidence_refs"], "additionalProperties": False}}}
TOOLS = SEARCH_FIND_TOOLS + [VERIFY_TOOL]
SYSTEM_A = (
    "Choose the single next research action from the current progress view. Available action classes are "
    "search, find, open, verify and submit. Search discovers a source; Find locates evidence in a known document; "
    "Open reads adjacent context around a known relevant window; Verify semantically closes an observed claim using "
    "known evidence refs; Submit/Stop ends a complete local research task. Choose normally; no class is masked. "
    "Return exactly three lines:\nAction: [one of search, find, open, verify, submit]\n"
    "Arguments: [one JSON object appropriate to the action; {} for submit]\nReason: [one sentence]"
)
SYSTEM_B = (
    "Choose the single next research action from the current progress view. The available tools are search, find, "
    "open and verify; if the local task is complete, submit a brief final answer without calling a tool. "
    "Search discovers source documents, Find locates a fact inside a known D#, Open reads adjacent context around "
    "a known W#, and Verify judges a claim using already observed W# evidence without corpus retrieval. "
    "Choose normally; all tools remain available."
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def order():
    return sorted(CASES, key=lambda c: hashlib.sha256(c["case_id"].encode()).hexdigest())


def view(case):
    return (f"Diagnostic scope: {case['diagnostic_scope']}\n"
            f"Current active gap: {case['active_gap']}\n"
            f"Current claim status: {case['current_claim_status']}\n"
            f"Expected source type: {case['expected_source_type']}\n"
            f"Known suitable document: {case['known_suitable_document']}\n"
            f"Known relevant window: {case['known_relevant_window']}\n"
            f"Current evidence refs: {', '.join(case['current_evidence_refs']) or 'none'}\n"
            f"Verification status: {case['verification_status']}")


def request(case, arm):
    params = {"model": CONFIG["model"], "messages": [
        {"role": "system", "content": SYSTEM_A if arm == "A" else SYSTEM_B},
        {"role": "user", "content": view(case)}], "stream": False}
    if arm == "B":
        params.update(tools=TOOLS, tool_choice="auto")
    elif arm != "A":
        raise ValueError(arm)
    return params


def validate():
    stage_b = json.loads((STUDY / "frontier_selection/results.json").read_text())["summary"]
    if not stage_b["stage_B_pass"]:
        raise ValueError("Stage B did not pass")
    from case_specs import STAGE_D_PRESELECTION
    if len(CASES) != 25 or len({c["case_id"] for c in CASES}) != 25 or len(STAGE_D_PRESELECTION) != 8:
        raise ValueError("Stage C selection count")
    expected = {"source": "search", "location": "find", "context": "open",
                "closure": "verify", "complete": "submit"}
    from collections import Counter
    if Counter(c["uncertainty_type_private"] for c in CASES) != Counter({k: 5 for k in expected}):
        raise ValueError("Unbalanced C diagnosis")
    for c in CASES:
        if c["expected_action"] != expected[c["uncertainty_type_private"]]:
            raise ValueError(c["case_id"])
        if "uncertainty_type_private" in view(c) or "expected_action" in view(c):
            raise ValueError("Private label leaked")


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    validate()
    sources = ["experiments/research_progress_frontier/action_routing/case_specs.py",
               "experiments/research_progress_frontier/action_routing/build_cases.py",
               "experiments/research_progress_frontier/action_routing/review_cases.json",
               "experiments/research_progress_frontier/action_routing/source_aliases.json",
               "experiments/research_progress_frontier/action_routing/stage_d_preselection.json",
               "experiments/research_progress_frontier/action_routing/EXPERIMENT_PLAN.md",
               "experiments/research_progress_frontier/action_routing/RUBRIC.json",
               "experiments/research_progress_frontier/action_routing/run.py",
               "experiments/research_progress_frontier/action_routing/analyze.py",
               "llm_chat/search_find_agent.py", "experiments/model_backend_deepseek/protocol.py",
               "experiments/model_backend_deepseek/provider.json"]
    history = ["experiments/research_progress_frontier/closure_probe/review_cases.json",
               "experiments/research_progress_frontier/frontier_selection/review_cases.json",
               "experiments/research_progress_frontier/frontier_selection/results.json",
               "experiments/research_state_qualification/qualification_upper_bound/review_packets.json"]
    doc = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
           "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
           "model": CONFIG["model"], "provider_host": urlsplit(CONFIG["base_url"]).hostname,
           "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": 0,
           "prompt_sha256": {"A": hashlib.sha256(SYSTEM_A.encode()).hexdigest(),
                             "B": hashlib.sha256(SYSTEM_B.encode()).hexdigest()},
           "tool_schema_sha256": digest(TOOLS), "sample_count": 50, "cases": len(CASES),
           "case_order": [c["case_id"] for c in order()],
           "arm_order": {c["case_id"]: (["A", "B"] if i % 2 == 0 else ["B", "A"])
                         for i, c in enumerate(order())},
           "qid_checkpoint": {c["case_id"]: [c["qid"], c["checkpoint"]] for c in CASES},
           "prefix_sha256": {c["case_id"]: c["prefix_sha256"] for c in CASES},
           "evidence_excerpt_sha256": {c["case_id"]: c["visible_evidence_sha256"] for c in CASES},
           "review_labels": {c["case_id"]: c["expected_action"] for c in CASES},
           "source_sha256": {p: sha(ROOT / p) for p in sources},
           "history_sha256": {p: sha(ROOT / p) for p in history},
           "request_sha256": {f"{c['case_id']}:{arm}": digest(request(c, arm))
                              for c in CASES for arm in ("A", "B")},
           "stage_d_preselection": json.loads((HERE / "stage_d_preselection.json").read_text()),
           "gate": json.loads((HERE / "RUBRIC.json").read_text())["gate"],
           "failure_policy": "One A and one B response per case; zero retries, no tools executed or selective repair."}
    FREEZE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def gate():
    doc = json.loads(FREEZE.read_text())
    checks = {"sources": all(sha(ROOT / p) == h for p, h in doc["source_sha256"].items()),
              "history": all(sha(ROOT / p) == h for p, h in doc["history_sha256"].items()),
              "provider": doc["model"] == CONFIG["model"] and
                          doc["provider_host"] == urlsplit(CONFIG["base_url"]).hostname and
                          doc["timeout_seconds"] == CONFIG["timeout_seconds"] and doc["max_retries"] == 0,
              "prompts_schema": doc["prompt_sha256"] == {
                  "A": hashlib.sha256(SYSTEM_A.encode()).hexdigest(),
                  "B": hashlib.sha256(SYSTEM_B.encode()).hexdigest()} and
                  doc["tool_schema_sha256"] == digest(TOOLS),
              "sample": doc["sample_count"] == 50 and doc["cases"] == len(CASES) == 25 and
                        doc["case_order"] == [c["case_id"] for c in order()] and
                        all(doc["review_labels"][c["case_id"]] == c["expected_action"] and
                            doc["prefix_sha256"][c["case_id"]] == c["prefix_sha256"] and
                            doc["evidence_excerpt_sha256"][c["case_id"]] == c["visible_evidence_sha256"]
                            for c in CASES),
              "order_requests": all(doc["request_sha256"][f"{c['case_id']}:{arm}"] == digest(request(c, arm))
                                    for c in CASES for arm in ("A", "B")) and
                                all(doc["arm_order"][c["case_id"]] == (["A", "B"] if i % 2 == 0 else ["B", "A"])
                                    for i, c in enumerate(order())),
              "rubric": doc["gate"] == json.loads((HERE / "RUBRIC.json").read_text())["gate"] and
                        doc["stage_d_preselection"] == json.loads((HERE / "stage_d_preselection.json").read_text())}
    (HERE / "gate.txt").write_text("\n".join(f'{"PASS" if v else "FAIL"} {k}' for k, v in checks.items()) +
                                    f"\n{sum(checks.values())}/{len(checks)} PASS\n")
    if not all(checks.values()):
        raise AssertionError(checks)


def emit(kind, **fields):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "kind": kind, **fields},
                             ensure_ascii=False) + "\n")
        out.flush()


def run():
    gate()
    if EVENTS.exists():
        raise FileExistsError(EVENTS)
    key = dotenv_values(ROOT / CONFIG["credential_file"]).get(CONFIG["credential_field"])
    if not key:
        raise ValueError("DeepSeek credential unavailable")
    with OpenAI(api_key=key, base_url=CONFIG["base_url"],
                timeout=CONFIG["timeout_seconds"], max_retries=0) as client:
        for i, case in enumerate(order()):
            for arm in (("A", "B") if i % 2 == 0 else ("B", "A")):
                cell = f"{case['case_id']}:{arm}"
                params = request(case, arm)
                emit("api_request", cell=cell, request=params, request_sha256=digest(params))
                try:
                    raw = client.chat.completions.create(**params).model_dump(mode="json")
                    choice = (raw.get("choices") or [{}])[0]
                    calls, error = (validate_batch(choice, TOOLS,
                        allow_stop_with_calls=CONFIG["allow_tool_calls_with_stop"])
                                    if arm == "B" else ([], None))
                    emit("api_response", cell=cell, response=raw,
                         parsed_calls=calls, validation=error or "valid", cache_usage=extract(raw))
                    print(cell, error or "response", flush=True)
                except Exception as exc:
                    emit("api_error", cell=cell, error_type=type(exc).__name__,
                         http_status=getattr(exc, "status_code", None), error=str(exc)[:500])
                    print(cell, "error", type(exc).__name__, flush=True)


if __name__ == "__main__":
    action = sys.argv[1]
    if action == "freeze":
        freeze()
    elif action == "gate":
        gate()
        print("PASS")
    elif action == "run":
        run()
    else:
        raise SystemExit("freeze|gate|run")
