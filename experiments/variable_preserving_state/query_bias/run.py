"""Frozen V2 one-query, three-arm probe. No Search execution."""

import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from experiments.model_backend_deepseek.cache_usage import extract

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
CASES = json.loads((HERE / "V2_CASES.json").read_text())
SELECTION = json.loads((HERE / "V2_SELECTION.json").read_text())
CONFIG = json.loads((ROOT / "experiments/model_backend_deepseek/provider.json").read_text())
PROMPT = (STUDY / "prompts/search_query_actor.md").read_text()
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def order():
    return sorted(CASES, key=lambda c: hashlib.sha256(c["case_id"].encode()).hexdigest())


def arms(i):
    return (("Q0", "Q1", "Q2"), ("Q1", "Q2", "Q0"), ("Q2", "Q0", "Q1"))[i % 3]


def user_view(case, arm):
    shared = {key: case[key] for key in ("raw_question", "question_anchors", "visible_evidence",
                                      "working_hypothesis", "semantic_gap", "expected_source_type")}
    if arm == "Q1":
        shared["concrete_claim_state"] = case["concrete_claim_state"]
        if case["claim_state_error"]:
            shared["state_generation_error"] = case["claim_state_error"]
    elif arm == "Q2":
        shared["test_card_state"] = case["test_card_state"]
        if case["test_state_error"]:
            shared["state_generation_error"] = case["test_state_error"]
    return json.dumps(shared, ensure_ascii=False)


def request(case, arm):
    return {"model": CONFIG["model"], "messages": [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": user_view(case, arm)}], "stream": False}


def source_paths():
    own = [HERE / x for x in ("V2_SELECTION.json", "V2_CASES.json", "prepare_cases.py",
                                 "PROTOCOL.md", "REVIEW_RUBRIC.md", "run.py", "analyze.py")]
    return own + [STUDY / "prompts/search_query_actor.md",
                  STUDY / "test_representation/CASES.json",
                  STUDY / "test_representation/events.jsonl",
                  STUDY / "test_representation/results.json",
                  ROOT / "experiments/model_backend_deepseek/provider.json",
                  ROOT / "experiments/model_backend_deepseek/cache_usage.py"]


def validate_bank():
    assert [c["case_id"] for c in CASES] == SELECTION["case_ids"]
    assert len(CASES) == 16 and len({c["qid"] for c in CASES}) >= 8
    for c in CASES:
        frozen = SELECTION["per_case"][c["case_id"]]
        assert c["qid"] == frozen["qid"]
        assert digest([c["raw_question"], c["visible_evidence"]]) == frozen["prefix_sha256"]
        assert digest(c["semantic_gap"]) == frozen["semantic_gap_sha256"]
        assert frozen["known_suitable_D"] == "none"
        assert c["expected_source_type"]
        assert c["claim_state_error"] is None or not c["concrete_claim_state"]
        assert c["test_state_error"] is None or not c["test_card_state"]


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    validate_bank()
    f = {
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "provider": {"host": urlsplit(CONFIG["base_url"]).hostname, "model": CONFIG["model"],
                     "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": 0},
        "v1_selected_arm": "C1",
        "sample_count": len(CASES), "qids": sorted({c["qid"] for c in CASES}),
        "case_order": [c["case_id"] for c in order()],
        "arm_order": {c["case_id"]: list(arms(i)) for i, c in enumerate(order())},
        "qid_checkpoint": {c["case_id"]: [c["qid"], c["checkpoint"]] for c in CASES},
        "prefix_sha256": {c["case_id"]: digest([c["raw_question"], c["visible_evidence"]]) for c in CASES},
        "semantic_gap_sha256": {c["case_id"]: digest(c["semantic_gap"]) for c in CASES},
        "hypothesis_sha256": {c["case_id"]: digest(c["working_hypothesis"]) for c in CASES},
        "question_anchor_sha256": {c["case_id"]: digest(c["question_anchors"]) for c in CASES},
        "expected_source_sha256": {c["case_id"]: digest(c["expected_source_type"]) for c in CASES},
        "state_sha256": {c["case_id"]: digest([c["concrete_claim_state"], c["claim_state_error"],
                                               c["test_card_state"], c["test_state_error"]]) for c in CASES},
        "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in source_paths()},
        "prompt_sha256": hashlib.sha256(PROMPT.encode()).hexdigest(),
        "schema_sha256": digest({"query": "nonempty string", "reason": "nonempty string"}),
        "tool_schema_sha256": digest([]),
        "request_sha256": {f"{c['case_id']}:{a}": digest(request(c, a)) for c in CASES for a in ("Q0", "Q1", "Q2")},
        "review_rubric_sha256": sha(HERE / "REVIEW_RUBRIC.md"),
        "gate": {"net_paired_leakage_improvement_min": 6,
                 "reverse_worsening": "strictly less than half improvements",
                 "gap_alignment": "Q2 >= Q1", "source_type_alignment": "Q2 >= Q1"},
        "failure_policy": "Exactly one query-generation call per arm/case; max_retries=0; all errors retained; no Search tool call.",
    }
    FREEZE.write_text(json.dumps(f, ensure_ascii=False, indent=2) + "\n")


def gate():
    validate_bank()
    f = json.loads(FREEZE.read_text())
    checks = {
        "sources": f["source_sha256"] == {str(p.relative_to(ROOT)): sha(p) for p in source_paths()},
        "provider": f["provider"] == {"host": urlsplit(CONFIG["base_url"]).hostname, "model": CONFIG["model"],
                                      "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": CONFIG["max_retries"]},
        "order": f["case_order"] == [c["case_id"] for c in order()],
        "requests": all(f["request_sha256"][f"{c['case_id']}:{a}"] == digest(request(c, a))
                        for c in CASES for a in ("Q0", "Q1", "Q2")),
        "rubric": f["review_rubric_sha256"] == sha(HERE / "REVIEW_RUBRIC.md"),
    }
    (HERE / "gate.txt").write_text("\n".join(("PASS " if v else "FAIL ") + k for k, v in checks.items()) + "\n")
    if not all(checks.values()):
        raise AssertionError(checks)


def emit(kind, **fields):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "kind": kind, **fields}, ensure_ascii=False) + "\n")
        out.flush()


def validate_output(value):
    if not isinstance(value, dict) or set(value) != {"query", "reason"} or \
            not all(isinstance(value[k], str) and value[k].strip() for k in ("query", "reason")):
        raise ValueError("query_schema")
    if len(value["query"]) > 400:
        raise ValueError("query_too_long")
    return value


def run():
    gate()
    if EVENTS.exists():
        raise FileExistsError(EVENTS)
    key = dotenv_values(ROOT / CONFIG["credential_file"]).get(CONFIG["credential_field"])
    if not key:
        raise ValueError("DeepSeek credential unavailable")
    with OpenAI(api_key=key, base_url=CONFIG["base_url"], timeout=CONFIG["timeout_seconds"], max_retries=0) as client:
        for i, case in enumerate(order()):
            for arm in arms(i):
                cell = f"{case['case_id']}:{arm}"
                req = request(case, arm)
                emit("model_request", cell=cell, request=req, request_sha256=digest(req))
                started = time.monotonic()
                try:
                    raw = client.chat.completions.create(**req).model_dump(mode="json")
                    elapsed = time.monotonic() - started
                    emit("model_response", cell=cell, response=raw, cache_usage=extract(raw), latency_seconds=elapsed)
                    if raw["choices"][0]["finish_reason"] != "stop":
                        raise ValueError("abnormal_finish")
                    value = validate_output(json.loads(raw["choices"][0]["message"]["content"]))
                    emit("arm_outcome", cell=cell, output=value)
                    print(cell, "ok", flush=True)
                except Exception as exc:
                    emit("arm_error", cell=cell, error_type=type(exc).__name__,
                         http_status=getattr(exc, "status_code", None), error=str(exc)[:500],
                         latency_seconds=time.monotonic() - started)
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
