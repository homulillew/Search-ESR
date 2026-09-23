"""Frozen one-step reviewer qualification handoff to the P1 DeepSeek Actor."""

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
from llm_chat.search_find_agent import SEARCH_FIND_PROMPT, SEARCH_FIND_TOOLS
from experiments.model_backend_deepseek.cache_usage import extract
from experiments.model_backend_deepseek.protocol import validate_batch
from experiments.research_state_plan_handoff.plan_handoff_one_step.run import (
    CASES, CONFIG, digest, h1_request, plan,
)

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"
SELECTION = json.loads((HERE / "SELECTION.json").read_text())["cells"]
ANNOTATIONS = json.loads((HERE / "ANNOTATIONS.json").read_text())["rows"]
LABELS = {(r["qid"], r["seq"]): r for r in ANNOTATIONS}
P1_EVENTS = [json.loads(line) for line in
             (ROOT / "experiments/research_state_plan_handoff/plan_handoff_one_step/events.jsonl").open()]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def card(a):
    return ("Current plan qualification:\n\n"
            f"Current need:\n{a['current_need']}\n\n"
            f"Candidate target:\n{a['candidate_target']}\n\n"
            f"Target status:\n{a['status']}\n\n"
            f"Observed support:\n{', '.join(a['visible_support_refs']) or 'none'} — {a['supported_part']}\n\n"
            f"Missing prerequisite:\n{a['missing_prerequisite']}\n\n"
            "This qualification distinguishes observed support from an unverified hypothesis. "
            "Choose the next action normally using the available tools.")


def request(q, seq):
    params = json.loads(json.dumps(h1_request(q, seq)))
    params["messages"].append({"role": "user", "content": card(LABELS[(q, seq)])})
    return params


def baseline(q, seq):
    cell = f"{q}:{seq}:H1"
    matches = [e for e in P1_EVENTS if e["kind"] == "api_response" and e["cell"] == cell]
    if len(matches) != 1:
        raise ValueError(f"Missing unique P1 baseline: {cell}")
    return matches[0]


def validate_design():
    cases = [(x["qid"], x["seq"]) for x in SELECTION]
    if cases != CASES or len(cases) != 13 or set(cases) != set(LABELS):
        raise ValueError("Selection/annotation mismatch against all 13 P1 cases")
    packets = {(p["qid"], p["seq"]): p for p in json.loads((HERE / "review_packets.json").read_text())}
    for q, seq in cases:
        a = LABELS[(q, seq)]
        observed = {d["doc_ref"] for d in packets[(q, seq)]["observed_documents"]}
        windows = {d["preview_ref"] for d in packets[(q, seq)]["observed_documents"]}
        if a["status"] not in {"no_target", "hypothesis_only", "inspectable"} or \
           a["ambiguity"] not in {"low", "medium", "high"} or \
           not a["current_need"] or not a["reason"] or not a["missing_prerequisite"]:
            raise ValueError(f"Bad annotation {q}:{seq}")
        if (a["status"] == "no_target") != (a["candidate_target"] == "none"):
            raise ValueError(f"Target/status conflict {q}:{seq}")
        if a["candidate_target"] != "none" and a["candidate_target"] not in observed | windows:
            raise ValueError(f"Target absent from prefix {q}:{seq}")
        if not set(a["visible_support_refs"]) <= windows:
            raise ValueError(f"Support ref absent from prefix {q}:{seq}")
        if not a["acceptable_next_scopes"] or not set(a["acceptable_next_scopes"]) <= {
            "corpus", "document", "window", "stop"}:
            raise ValueError(f"Bad acceptable scope {q}:{seq}")
        if packets[(q, seq)]["prefix_messages"] != h1_request(q, seq)["messages"][:-1]:
            raise ValueError(f"Review packet prefix mismatch {q}:{seq}")
        if packets[(q, seq)]["broad_plan"] != plan(q, seq):
            raise ValueError(f"Review packet plan mismatch {q}:{seq}")
        baseline(q, seq)


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    validate_design()
    sources = ["experiments/research_state_qualification/qualification_upper_bound/run.py",
               "experiments/research_state_qualification/qualification_upper_bound/analyze.py",
               "experiments/research_state_qualification/qualification_upper_bound/prepare_packets.py",
               "experiments/research_state_qualification/qualification_upper_bound/SELECTION.json",
               "experiments/research_state_qualification/qualification_upper_bound/ANNOTATIONS.json",
               "experiments/research_state_qualification/qualification_upper_bound/RUBRIC.json",
               "experiments/research_state_qualification/qualification_upper_bound/review_packets.json",
               "experiments/model_backend_deepseek/provider.json",
               "experiments/model_backend_deepseek/protocol.py",
               "llm_chat/search_find_agent.py"]
    historical = ["experiments/research_state_plan_handoff/plan_handoff_one_step/events.jsonl",
                  "experiments/research_state_plan_handoff/plan_handoff_one_step/freeze.json",
                  "experiments/model_backend_deepseek/planning_probe/mechanical_summary.json",
                  "experiments/model_backend_deepseek/natural_action_probe/events.jsonl",
                  "experiments/model_backend_atria/PREFIX_ONLY_PACKETS.json"]
    obj = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
           "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
           "model": CONFIG["model"], "provider_host": urlsplit(CONFIG["base_url"]).hostname,
           "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": 0,
           "selection": SELECTION, "sample_count": len(SELECTION), "horizon": "one Actor response, no tools executed",
           "prompt_sha256": hashlib.sha256(SEARCH_FIND_PROMPT.encode()).hexdigest(),
           "schema_sha256": digest(SEARCH_FIND_TOOLS),
           "source_sha256": {s: sha(ROOT / s) for s in sources},
           "historical_sha256": {s: sha(ROOT / s) for s in historical},
           "plan_sha256": {f"{q}:{seq}": digest(plan(q, seq)) for q, seq in CASES},
           "baseline_response_sha256": {f"{q}:{seq}": digest(baseline(q, seq)) for q, seq in CASES},
           "h0_request_sha256": {f"{q}:{seq}": digest(h1_request(q, seq)) for q, seq in CASES},
           "h1_request_sha256": {f"{q}:{seq}": digest(request(q, seq)) for q, seq in CASES},
           "failure_policy": "one new H1 response per cell; max_retries=0; errors retained; no selective retry"}
    FREEZE.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def gate():
    obj = json.loads(FREEZE.read_text())
    checks = {
        "sources": all(sha(ROOT / s) == h for s, h in obj["source_sha256"].items()),
        "history": all(sha(ROOT / s) == h for s, h in obj["historical_sha256"].items()),
        "selection_and_annotation": obj["selection"] == SELECTION and obj["sample_count"] == 13,
        "provider": obj["model"] == CONFIG["model"] and obj["provider_host"] == urlsplit(CONFIG["base_url"]).hostname and obj["timeout_seconds"] == CONFIG["timeout_seconds"] and obj["max_retries"] == 0,
        "prompt_schema": obj["prompt_sha256"] == hashlib.sha256(SEARCH_FIND_PROMPT.encode()).hexdigest() and obj["schema_sha256"] == digest(SEARCH_FIND_TOOLS),
        "plans": all(obj["plan_sha256"][f"{q}:{seq}"] == digest(plan(q, seq)) for q, seq in CASES),
        "baselines": all(obj["baseline_response_sha256"][f"{q}:{seq}"] == digest(baseline(q, seq)) for q, seq in CASES),
        "requests": all(obj["h0_request_sha256"][f"{q}:{seq}"] == digest(h1_request(q, seq)) and obj["h1_request_sha256"][f"{q}:{seq}"] == digest(request(q, seq)) for q, seq in CASES),
        "one_step": obj["horizon"] == "one Actor response, no tools executed",
    }
    (HERE / "gate.txt").write_text("\n".join(f'{"PASS" if good else "FAIL"} {name}' for name, good in checks.items()) + f"\n{sum(checks.values())}/{len(checks)} PASS\n")
    if not all(checks.values()):
        raise AssertionError(checks)


def emit(kind, **kwargs):
    with EVENTS.open("a") as output:
        output.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "kind": kind,
                                 **kwargs}, ensure_ascii=False) + "\n")
        output.flush()


def run():
    gate()
    if EVENTS.exists():
        raise FileExistsError(EVENTS)
    key = dotenv_values(ROOT / CONFIG["credential_file"]).get(CONFIG["credential_field"])
    if not key:
        raise ValueError("DeepSeek credential unavailable")
    with OpenAI(api_key=key, base_url=CONFIG["base_url"],
                timeout=CONFIG["timeout_seconds"], max_retries=0) as client:
        for q, seq in CASES:
            cell = f"{q}:{seq}:Q1"
            params = request(q, seq)
            emit("actor_request", cell=cell, request=params, request_sha256=digest(params))
            try:
                raw = client.chat.completions.create(**params).model_dump(mode="json")
                choice = (raw.get("choices") or [{}])[0]
                parsed, error = validate_batch(choice, SEARCH_FIND_TOOLS,
                    allow_stop_with_calls=CONFIG["allow_tool_calls_with_stop"])
                emit("actor_response", cell=cell, response=raw,
                     raw_finish_reason=choice.get("finish_reason"),
                     raw_tool_calls=(choice.get("message") or {}).get("tool_calls"),
                     parsed_calls=parsed, validation=error or "valid", cache_usage=extract(raw))
                print(cell, error or "valid", flush=True)
            except Exception as exc:
                emit("actor_error", cell=cell, error_type=type(exc).__name__,
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
