"""Concurrent frozen A1 Observation-driven and Gap-driven Claim Admission calls."""

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

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
CASES = json.loads((HERE / "CASES.json").read_text())
CONFIG = json.loads((ROOT / "experiments/model_backend_deepseek/provider.json").read_text())
PROMPTS = {"O": (HERE / "prompts/observation_compiler.md").read_text(),
           "G": (STUDY / "prompts/claim_compiler.md").read_text()}
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def order():
    return sorted(CASES, key=lambda c: hashlib.sha256(c["case_id"].encode()).hexdigest())


def arm_order(i):
    return ("O", "G") if i % 2 == 0 else ("G", "O")


def user_view(case):
    return json.dumps({
        "raw_question": case["raw_question"],
        "question_anchors": case["question_anchors"],
        "existing_state": {"active_gap": case["active_gap"],
                           "working_hypothesis": case["working_hypothesis"],
                           "existing_claims": case["existing_claims"]},
        "latest_observation": case["latest_observation"],
        "relevant_basis_refs": case["relevant_basis_refs"],
    }, ensure_ascii=False)


def request(case, arm):
    return {"model": CONFIG["model"], "messages": [
        {"role": "system", "content": PROMPTS[arm]},
        {"role": "user", "content": user_view(case)}], "stream": False}


def sources():
    names = ["claim_admission/PROTOCOL.md", "claim_admission/RUBRIC.md",
             "claim_admission/CASES.json", "claim_admission/prepare_bank.py",
             "claim_admission/prompts/observation_compiler.md", "claim_admission/run.py",
             "claim_admission/analyze.py", "prompts/claim_compiler.md"]
    paths = [STUDY / p for p in names]
    paths += [ROOT / "experiments/research_progress_frontier/frontier_selection/review_cases.json",
              ROOT / "experiments/research_state_v2/claim_mutation/CASES.json",
              ROOT / "experiments/model_backend_deepseek/provider.json",
              ROOT / "experiments/model_backend_deepseek/cache_usage.py"]
    return paths


def validate_bank():
    assert len(CASES) == 24 and len({c["qid"] for c in CASES}) == 8
    assert len({c["case_id"] for c in CASES}) == 24
    for c in CASES:
        assert c["active_gap"]["status"] == "open"
        assert all(a.lower() in c["raw_question"].lower() for a in c["question_anchors"].values())
        assert c["relevant_basis_refs"] == [c["latest_observation"]["ref"]]
        assert len(c["coverage_requirements"]) in (1, 2)


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    validate_bank()
    f = {
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "provider": {"host": urlsplit(CONFIG["base_url"]).hostname, "model": CONFIG["model"],
                     "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": 0},
        "case_order": [c["case_id"] for c in order()],
        "arm_order": {c["case_id"]: list(arm_order(i)) for i, c in enumerate(order())},
        "sample_count": 24, "qids": sorted({c["qid"] for c in CASES}),
        "checkpoint": {c["case_id"]: c["checkpoint"] for c in CASES},
        "prefix_sha256": {c["case_id"]: digest([c["raw_question"], c["existing_claims"]]) for c in CASES},
        "state_sha256": {c["case_id"]: digest([c["active_gap"], c["working_hypothesis"], c["existing_claims"]]) for c in CASES},
        "observation_sha256": {c["case_id"]: digest(c["latest_observation"]) for c in CASES},
        "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in sources()},
        "prompt_sha256": {a: hashlib.sha256(PROMPTS[a].encode()).hexdigest() for a in ("O", "G")},
        "schema_sha256": digest({"keys": ["claims"], "claim_keys": ["statement", "question_anchor_ids", "hypothesis_id", "why_needed_for_gap"], "claim_count": [0, 3], "new_status": "open"}),
        "tool_schema_sha256": digest([]),
        "rubric_sha256": sha(HERE / "RUBRIC.md"),
        "request_sha256": {f"{c['case_id']}:{a}": digest(request(c, a)) for c in CASES for a in ("O", "G")},
        "gate": {"paired_precision_improvement_min": 5, "reverse_worsening_less_than_half": True,
                 "coverage_decline_max_pp": 10, "premature_rate_max": .15, "redundant_rate_max": .15},
        "failure_policy": "One O and one G request per packet in rotating order, max_retries=0, invalid responses retained as failed cells; no best-of.",
    }
    FREEZE.write_text(json.dumps(f, ensure_ascii=False, indent=2) + "\n")


def gate():
    validate_bank()
    f = json.loads(FREEZE.read_text())
    checks = {
        "sources": f["source_sha256"] == {str(p.relative_to(ROOT)): sha(p) for p in sources()},
        "provider": f["provider"] == {"host": urlsplit(CONFIG["base_url"]).hostname, "model": CONFIG["model"],
                                      "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": CONFIG["max_retries"]},
        "order": f["case_order"] == [c["case_id"] for c in order()],
        "requests": all(f["request_sha256"][f"{c['case_id']}:{a}"] == digest(request(c, a))
                        for c in CASES for a in ("O", "G")),
        "rubric": f["rubric_sha256"] == sha(HERE / "RUBRIC.md"),
    }
    (HERE / "gate.txt").write_text("\n".join(("PASS " if v else "FAIL ") + k for k, v in checks.items()) + "\n")
    if not all(checks.values()):
        raise AssertionError(checks)


def emit(kind, **fields):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "kind": kind, **fields}, ensure_ascii=False) + "\n")
        out.flush()


def validate_output(case, value):
    if not isinstance(value, dict) or set(value) != {"claims"} or not isinstance(value["claims"], list) or len(value["claims"]) > 3:
        raise ValueError("claim_admission_top_schema")
    claims = []
    for item in value["claims"]:
        if not isinstance(item, dict) or set(item) != {"statement", "question_anchor_ids", "hypothesis_id", "why_needed_for_gap"} or \
                not isinstance(item["statement"], str) or not item["statement"].strip() or \
                not isinstance(item["question_anchor_ids"], list) or not item["question_anchor_ids"] or \
                any(q not in case["question_anchors"] for q in item["question_anchor_ids"]) or \
                item["hypothesis_id"] != "none" or not isinstance(item["why_needed_for_gap"], str):
            raise ValueError("claim_admission_item_schema")
        claims.append({**item, "parent_gap_id": case["active_gap"]["gap_id"], "status": "open"})
    return claims


def run():
    gate()
    if EVENTS.exists():
        raise FileExistsError(EVENTS)
    key = dotenv_values(ROOT / CONFIG["credential_file"]).get(CONFIG["credential_field"])
    if not key:
        raise ValueError("DeepSeek credential unavailable")
    with OpenAI(api_key=key, base_url=CONFIG["base_url"], timeout=CONFIG["timeout_seconds"], max_retries=0) as client:
        for i, case in enumerate(order()):
            for arm in arm_order(i):
                cell = f"{case['case_id']}:{arm}"
                req = request(case, arm)
                emit("compiler_request", cell=cell, request=req, request_sha256=digest(req))
                try:
                    raw = client.chat.completions.create(**req).model_dump(mode="json")
                    emit("compiler_response", cell=cell, response=raw, cache_usage=extract(raw))
                    if raw["choices"][0]["finish_reason"] != "stop":
                        raise ValueError("abnormal_finish")
                    value = json.loads(raw["choices"][0]["message"]["content"])
                    claims = validate_output(case, value)
                    emit("arm_outcome", cell=cell, claims=claims)
                    print(cell, "ok", len(claims), flush=True)
                except Exception as exc:
                    emit("arm_error", cell=cell, error_type=type(exc).__name__,
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
