"""V1 frozen three-arm Test representation probe."""

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
CASES = json.loads((HERE / "CASES.json").read_text())
CONFIG = json.loads((ROOT / "experiments/model_backend_deepseek/provider.json").read_text())
PROMPTS = {"C0": (STUDY / "prompts/concrete_claim_compiler.md").read_text(),
           "C1": (STUDY / "prompts/natural_test_compiler.md").read_text(),
           "C2": (STUDY / "prompts/provenance_test_compiler.md").read_text()}
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def order():
    return sorted(CASES, key=lambda c: hashlib.sha256(c["case_id"].encode()).hexdigest())


def arms(i):
    return (("C0", "C1", "C2"), ("C1", "C2", "C0"), ("C2", "C0", "C1"))[i % 3]


def user_view(case):
    return json.dumps({"raw_question": case["raw_question"],
                       "question_anchors": case["question_anchors"],
                       "working_hypothesis": case["working_hypothesis"],
                       "semantic_gap": case["semantic_gap"],
                       "existing_tests": case["existing_tests"],
                       "visible_evidence": case["visible_evidence"]}, ensure_ascii=False)


def request(case, arm):
    return {"model": CONFIG["model"], "messages": [
        {"role": "system", "content": PROMPTS[arm]},
        {"role": "user", "content": user_view(case)}], "stream": False}


def source_paths():
    own = ["PROTOCOL.md", "HYPOTHESES.md", "STATE.md",
           "test_representation/CASE_SELECTION.md", "test_representation/REVIEW_RUBRIC.md",
           "test_representation/CASES.json", "test_representation/prepare_bank.py",
           "test_representation/run.py", "test_representation/analyze.py",
           "query_bias/V2_SELECTION.json"]
    own += [str(p.relative_to(STUDY)) for p in sorted((STUDY / "prompts").glob("*.md"))]
    return [STUDY / p for p in own] + [
        ROOT / "experiments/research_state_v2/claim_admission/CASES.json",
        ROOT / "experiments/research_state_v2/claim_mutation/CASES.json",
        ROOT / "experiments/model_backend_deepseek/provider.json",
        ROOT / "experiments/model_backend_deepseek/cache_usage.py"]


def validate_bank():
    assert 30 <= len(CASES) <= 36 and len({c["case_id"] for c in CASES}) == len(CASES)
    assert len({c["qid"] for c in CASES}) >= 10
    assert sum(c["case_id"] in {"T4_186", "T5_186", "T7_186", "T4_311", "T5_311", "T4_324"} for c in CASES) == 6
    selected = json.loads((STUDY / "query_bias/V2_SELECTION.json").read_text())
    assert selected["selected_before_V1_calls"] is True
    assert 16 <= len(selected["case_ids"]) <= 24 and len({c["qid"] for c in CASES if c["case_id"] in selected["case_ids"]}) >= 8
    for c in CASES:
        assert set(c["question_anchors"]) and all(a.lower() in c["raw_question"].lower() for a in c["question_anchors"].values())
        assert c["semantic_gap"].endswith("?") and not c["semantic_gap"].lower().startswith(("find ", "locate ", "search ", "check ", "read ", "verify "))
        assert c["existing_tests"] == []
        assert c["visible_basis_refs"] == [o["ref"] for o in c["visible_evidence"]]
        if c["working_hypothesis"]:
            assert c["working_hypothesis"]["status"] == "provisional"
            assert set(c["working_hypothesis"]["basis_refs"]) <= set(c["visible_basis_refs"])
        assert 1 <= len(c["coverage_requirements"]) <= 3


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    validate_bank()
    f = {
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "base_head": "55fd5e067e49baadee3968bbc55ebac4e35f5054",
        "provider": {"host": urlsplit(CONFIG["base_url"]).hostname, "model": CONFIG["model"],
                     "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": 0},
        "sample_count": len(CASES), "qids": sorted({c["qid"] for c in CASES}),
        "case_order": [c["case_id"] for c in order()],
        "arm_order": {c["case_id"]: list(arms(i)) for i, c in enumerate(order())},
        "qid_checkpoint": {c["case_id"]: [c["qid"], c["checkpoint"]] for c in CASES},
        "prefix_sha256": {c["case_id"]: digest([c["raw_question"], c["visible_evidence"]]) for c in CASES},
        "semantic_gap_sha256": {c["case_id"]: digest(c["semantic_gap"]) for c in CASES},
        "working_hypothesis_sha256": {c["case_id"]: digest(c["working_hypothesis"]) for c in CASES},
        "question_anchor_sha256": {c["case_id"]: digest(c["question_anchors"]) for c in CASES},
        "review_requirements_sha256": {c["case_id"]: digest([c["coverage_requirements"], c["review_unknown_slots"]]) for c in CASES},
        "V2_selection_sha256": sha(STUDY / "query_bias/V2_SELECTION.json"),
        "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in source_paths()},
        "prompt_sha256": {a: hashlib.sha256(PROMPTS[a].encode()).hexdigest() for a in PROMPTS},
        "schema_sha256": digest({"C0": {"claims": ["statement"]},
                                  "C1": {"tests": ["condition", "known:string[]", "unknown:string[]"]},
                                  "C2": {"tests": ["condition", "known:slot/value/basis_type/basis_ref[]", "unknown:slot/description[]"]},
                                  "max_items": 3, "new_status": "open"}),
        "tool_schema_sha256": digest([]),
        "request_sha256": {f"{c['case_id']}:{a}": digest(request(c, a)) for c in CASES for a in PROMPTS},
        "review_rubric_sha256": sha(HERE / "REVIEW_RUBRIC.md"),
        "gate": {"unsupported_binding_rate_max": .10, "premature_case_rate_max": .15,
                 "mean_coverage_min": .70, "testability_min": .85,
                 "paired_premature_improvement_min": 8, "reverse_worsening_max": 2},
        "failure_policy": "Exactly one C0/C1/C2 call per case in rotating order, max_retries=0, no best-of; invalid/provider failures retained and scored as failed cells.",
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
                        for c in CASES for a in PROMPTS),
        "rubric": f["review_rubric_sha256"] == sha(HERE / "REVIEW_RUBRIC.md"),
        "V2_selection": f["V2_selection_sha256"] == sha(STUDY / "query_bias/V2_SELECTION.json"),
    }
    (HERE / "gate.txt").write_text("\n".join(("PASS " if v else "FAIL ") + k for k, v in checks.items()) + "\n")
    if not all(checks.values()):
        raise AssertionError(checks)


def emit(kind, **fields):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "kind": kind, **fields}, ensure_ascii=False) + "\n")
        out.flush()


def nonempty(s):
    return isinstance(s, str) and bool(s.strip())


def validate_output(case, arm, value):
    if not isinstance(value, dict) or set(value) != ({"claims"} if arm == "C0" else {"tests"}):
        raise ValueError("top_level_schema")
    items = value["claims" if arm == "C0" else "tests"]
    if not isinstance(items, list) or len(items) > 3:
        raise ValueError("item_count_schema")
    if arm == "C0":
        if any(not isinstance(x, dict) or set(x) != {"statement"} or not nonempty(x["statement"]) for x in items):
            raise ValueError("claim_schema")
        return [{"claim_id": f"C{i}", "statement": x["statement"], "status": "open"} for i, x in enumerate(items, 1)]
    if arm == "C1":
        for x in items:
            if not isinstance(x, dict) or set(x) != {"condition", "known", "unknown"} or not nonempty(x["condition"]) or \
                    not isinstance(x["known"], list) or not isinstance(x["unknown"], list) or \
                    any(not nonempty(s) for s in x["known"] + x["unknown"]):
                raise ValueError("natural_test_schema")
        return [{"test_id": f"T{i}", **x, "status": "open", "evidence_refs": []} for i, x in enumerate(items, 1)]
    observed = {o["ref"] for o in case["visible_evidence"]}
    for x in items:
        if not isinstance(x, dict) or set(x) != {"condition", "known", "unknown"} or not nonempty(x["condition"]) or \
                not isinstance(x["known"], list) or not isinstance(x["unknown"], list):
            raise ValueError("provenance_test_schema")
        known_slots = []
        unknown_slots = []
        for k in x["known"]:
            if not isinstance(k, dict) or set(k) != {"slot", "value", "basis_type", "basis_ref"} or \
                    not all(nonempty(k[n]) for n in k):
                raise ValueError("known_binding_schema")
            allowed = {"question": set(case["question_anchors"]), "evidence": observed,
                       "working_hypothesis": {case["working_hypothesis"]["hypothesis_id"]} if case["working_hypothesis"] else set()}
            if k["basis_type"] not in allowed or k["basis_ref"] not in allowed[k["basis_type"]]:
                raise ValueError("invalid_basis_ref")
            known_slots.append(k["slot"])
        for u in x["unknown"]:
            if not isinstance(u, dict) or set(u) != {"slot", "description"} or not all(nonempty(u[n]) for n in u):
                raise ValueError("unknown_slot_schema")
            unknown_slots.append(u["slot"])
        if len(known_slots + unknown_slots) != len(set(known_slots + unknown_slots)):
            raise ValueError("overlapping_or_duplicate_slots")
    return [{"test_id": f"T{i}", **x, "status": "open", "evidence_refs": []} for i, x in enumerate(items, 1)]


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
                    value = json.loads(raw["choices"][0]["message"]["content"])
                    items = validate_output(case, arm, value)
                    emit("arm_outcome", cell=cell, items=items)
                    print(cell, "ok", len(items), flush=True)
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
