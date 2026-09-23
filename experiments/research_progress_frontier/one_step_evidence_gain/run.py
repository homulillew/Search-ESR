"""Freeze and execute Stage D with zero Actor resampling and zero retries."""

import hashlib
import json
import subprocess
import sys
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from BCPlus.scripts.search_bcplus import BCPlusSearcher
from experiments.model_backend_deepseek.cache_usage import extract
from experiments.search_find_v3b.orthogonal_search.run_partial import checkpoint, restore_prefix, RUNS
from llm_chat.search_find_v3b_agent import OrthogonalSearchFindTools

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
C = STUDY / "action_routing"
CONFIG = json.loads((ROOT / "experiments/model_backend_deepseek/provider.json").read_text())
CASES = {c["case_id"]: c for c in json.loads((C / "review_cases.json").read_text())}
SELECTED = json.loads((C / "stage_d_preselection.json").read_text())
C_RESULTS = {r["cell"]: r for r in json.loads((C / "results.json").read_text())["rows"]}
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"
SYSTEM_VERIFY = (
    "Judge only whether the exact observed excerpt supports or refutes the current local claim. "
    "A relevant clue is not enough to close a stronger claim. Do not use outside knowledge or retrieve text. "
    "Return four lines: Status: supported|refuted|open; Evidence refs: W# or none; "
    "Missing evidence: brief text or none; Reason: one sentence."
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def emit(kind, **fields):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "kind": kind, **fields}, ensure_ascii=False) + "\n")
        out.flush()


def seq(case):
    if not case["checkpoint"].startswith("R1:"):
        raise ValueError(case["case_id"])
    return int(case["checkpoint"].split(":")[1])


def prior_view(case, wref):
    _, prior, _ = checkpoint(case["qid"], seq(case))
    seen = {}
    for event in prior:
        if event["kind"] != "tool_internal":
            continue
        model = event["audit"].get("model_result", {})
        for item in model.get("results", []) + model.get("matches", []):
            ref = item.get("preview_ref") or item.get("window_ref")
            content = item.get("preview") or item.get("text")
            if ref and content:
                seen[ref] = content
        if model.get("window_ref") and model.get("text"):
            seen[model["window_ref"]] = model["text"]
    if wref not in seen:
        raise ValueError(f"{case['case_id']}: absent prior {wref}")
    return seen[wref]


def verify_request(case):
    if case["uncertainty_type_private"] != "closure":
        raise ValueError(case["case_id"])
    evidence = [{"ref": w, "exact_visible_excerpt": prior_view(case, w)}
                for w in case["current_evidence_refs"]]
    claim = case["active_gap"].removeprefix("Decide whether ").rstrip(".")
    return {"model": CONFIG["model"], "messages": [
        {"role": "system", "content": SYSTEM_VERIFY},
        {"role": "user", "content": json.dumps({"claim_ref": case["claim_ref"],
                                                 "claim": claim, "visible_evidence": evidence},
                                                ensure_ascii=False)}], "stream": False}


def dependencies():
    files = [
        "experiments/research_progress_frontier/one_step_evidence_gain/RUBRIC.json",
        "experiments/research_progress_frontier/one_step_evidence_gain/EXPERIMENT_PLAN.md",
        "experiments/research_progress_frontier/one_step_evidence_gain/run.py",
        "experiments/research_progress_frontier/action_routing/review_cases.json",
        "experiments/research_progress_frontier/action_routing/stage_d_preselection.json",
        "experiments/research_progress_frontier/action_routing/results.json",
        "experiments/research_progress_frontier/action_routing/events.jsonl",
        "experiments/research_progress_frontier/action_routing/freeze.json",
        "experiments/research_progress_frontier/action_routing/gate.txt",
        "experiments/model_backend_deepseek/provider.json",
        "experiments/search_find_v3b/orthogonal_search/run_partial.py",
        "llm_chat/agent.py", "llm_chat/search_find_agent.py", "llm_chat/search_find_v3b_agent.py",
        "llm_chat/raw_windows.py", "llm_chat/window_locator.py", "llm_chat/window_units.py",
        "BCPlus/scripts/search_bcplus.py",
    ]
    return {p: sha(ROOT / p) for p in files}


def validate():
    if len(SELECTED) != 8 or len(set(SELECTED)) != 8:
        raise ValueError("Selection count")
    kinds = [CASES[c]["uncertainty_type_private"] for c in SELECTED]
    if any(kinds.count(k) != 2 for k in ("source", "location", "context", "closure")):
        raise ValueError("Unbalanced preselection")
    if not json.loads((C / "results.json").read_text())["summary"]["stage_C_pass"]:
        raise ValueError("Stage C gate failed")
    for cid in SELECTED:
        case = CASES[cid]
        response = C_RESULTS[cid + ":B"]
        if not response["argument_valid"] or not response["parsed"]["all_calls"]:
            raise ValueError(f"Invalid C-B first call: {cid}")
        if case["uncertainty_type_private"] == "closure":
            verify_request(case)
        tool = OrthogonalSearchFindTools()
        try:
            _, prior, _ = checkpoint(case["qid"], seq(case))
            restore_prefix(tool, prior)
            args = response["parsed"]["arguments"]
            name = response["action"]
            if name == "find":
                tool.handles.resolve_document(args["doc_ref"])
            if name == "open":
                tool.handles.resolve_window(args["window_ref"])
        finally:
            tool.close()


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    validate()
    doc = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
           "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
           "provider_host": urlsplit(CONFIG["base_url"]).hostname, "model": CONFIG["model"],
           "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": 0,
           "selection": SELECTED, "sample_count": 8, "actor_source": "frozen Stage C-B first response, no resampling",
           "first_actions": {cid: {"name": C_RESULTS[cid + ":B"]["action"],
                                   "arguments": C_RESULTS[cid + ":B"]["parsed"]["arguments"]}
                             for cid in SELECTED},
           "case_qid_checkpoint": {cid: [CASES[cid]["qid"], CASES[cid]["checkpoint"]] for cid in SELECTED},
           "prefix_sha256": {cid: CASES[cid]["prefix_sha256"] for cid in SELECTED},
           "evidence_excerpt_sha256": {cid: CASES[cid]["visible_evidence_sha256"] for cid in SELECTED},
           "review_labels": {cid: {"uncertainty_type": CASES[cid]["uncertainty_type_private"],
                                   "expected_action": CASES[cid]["expected_action"]} for cid in SELECTED},
           "closure_review_status": {"C_closure_546": "supported", "C_closure_1094": "supported"},
           "verify_prompt_sha256": hashlib.sha256(SYSTEM_VERIFY.encode()).hexdigest(),
           "verify_request_sha256": {cid: digest(verify_request(CASES[cid])) for cid in SELECTED
                                     if CASES[cid]["uncertainty_type_private"] == "closure"},
           "verify_excerpt_sha256": {cid: {w: hashlib.sha256(prior_view(CASES[cid], w).encode()).hexdigest()
                                           for w in CASES[cid]["current_evidence_refs"]}
                                     for cid in SELECTED if CASES[cid]["uncertainty_type_private"] == "closure"},
           "source_sha256": dependencies(),
           "historical_run_sha256": {q: sha(RUNS[q] / "events.jsonl") for q in ("546", "1094")},
           "rubric": json.loads((HERE / "RUBRIC.json").read_text()),
           "order": "selection order; V0 first retrieval/verify then V1 for each closure case",
           "failure_policy": "One frozen C-B first action per case, one V1 verifier per closure, zero retries; retain all errors."}
    FREEZE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def gate():
    frozen = json.loads(FREEZE.read_text())
    checks = {
        "Stage_C_pass": json.loads((C / "results.json").read_text())["summary"]["stage_C_pass"],
        "sources": dependencies() == frozen["source_sha256"],
        "historical_runs": {q: sha(RUNS[q] / "events.jsonl") for q in ("546", "1094")}
        == frozen["historical_run_sha256"],
        "provider": CONFIG["model"] == frozen["model"] and urlsplit(CONFIG["base_url"]).hostname
        == frozen["provider_host"] and CONFIG["timeout_seconds"] == frozen["timeout_seconds"]
        and CONFIG["max_retries"] == frozen["max_retries"] == 0,
        "selection_and_actions": SELECTED == frozen["selection"] and all(
            {"name": C_RESULTS[cid + ":B"]["action"],
             "arguments": C_RESULTS[cid + ":B"]["parsed"]["arguments"]} == frozen["first_actions"][cid]
            and CASES[cid]["prefix_sha256"] == frozen["prefix_sha256"][cid]
            and CASES[cid]["visible_evidence_sha256"] == frozen["evidence_excerpt_sha256"][cid]
            for cid in SELECTED),
        "verify_requests": hashlib.sha256(SYSTEM_VERIFY.encode()).hexdigest() == frozen["verify_prompt_sha256"]
        and all(digest(verify_request(CASES[cid])) == h for cid, h in frozen["verify_request_sha256"].items()),
        "rubric": json.loads((HERE / "RUBRIC.json").read_text()) == frozen["rubric"],
        "sample": frozen["sample_count"] == len(SELECTED) == 8,
    }
    (HERE / "gate.txt").write_text("\n".join(f'{"PASS" if v else "FAIL"} {k}' for k, v in checks.items()) +
                                    f"\n{sum(checks.values())}/{len(checks)} PASS\n")
    if not all(checks.values()):
        raise AssertionError(checks)
    validate()


def run():
    gate()
    if EVENTS.exists():
        raise FileExistsError(EVENTS)
    key = dotenv_values(ROOT / CONFIG["credential_file"]).get(CONFIG["credential_field"])
    if not key:
        raise ValueError("DeepSeek credential unavailable")
    with OpenAI(api_key=key, base_url=CONFIG["base_url"],
                timeout=CONFIG["timeout_seconds"], max_retries=0) as client, closing(BCPlusSearcher()) as searcher:
        for cid in SELECTED:
            case = CASES[cid]
            action = C_RESULTS[cid + ":B"]
            name, args = action["action"], action["parsed"]["arguments"]
            emit("case_start", case_id=cid, qid=case["qid"], checkpoint=case["checkpoint"],
                 expected_action=case["expected_action"], free_action=name, arguments=args,
                 active_gap=case["active_gap"])
            if name == "verify":
                call_verify(client, cid, "V0")
            else:
                tool = OrthogonalSearchFindTools()
                try:
                    _, prior, _ = checkpoint(case["qid"], seq(case))
                    restored = restore_prefix(tool, prior)
                    tool.searcher = searcher
                    emit("tool_request", case_id=cid, arm="V0", name=name,
                         arguments=args, restoration=restored)
                    try:
                        result = tool.execute(name, args)
                        emit("tool_result", case_id=cid, arm="V0", name=name,
                             arguments=args, result=result, audit=tool.audit_record())
                        print(cid, name, result.get("status"), flush=True)
                    except Exception as exc:
                        emit("tool_error", case_id=cid, arm="V0", name=name, arguments=args,
                             error_type=type(exc).__name__, error=str(exc)[:1000])
                        print(cid, name, type(exc).__name__, flush=True)
                finally:
                    tool.searcher = None  # shared searcher belongs to the outer scope
                    tool.close()
            if case["uncertainty_type_private"] == "closure":
                call_verify(client, cid, "V1")


def call_verify(client, cid, arm):
    request = verify_request(CASES[cid])
    emit("verify_request", case_id=cid, arm=arm, request=request,
         request_sha256=digest(request))
    try:
        raw = client.chat.completions.create(**request).model_dump(mode="json")
        emit("verify_response", case_id=cid, arm=arm, response=raw, cache_usage=extract(raw))
        print(cid, arm, "verify_response", flush=True)
    except Exception as exc:
        emit("verify_error", case_id=cid, arm=arm, error_type=type(exc).__name__,
             http_status=getattr(exc, "status_code", None), error=str(exc)[:1000])
        print(cid, arm, type(exc).__name__, flush=True)


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
