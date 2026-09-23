"""Frozen concurrent M1 W/N calls and mechanical State v2 commits."""

import copy
import hashlib
import importlib.util
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
OLD = ROOT / "experiments/transactional_research_progress/state_transition/run.py"
spec = importlib.util.spec_from_file_location("historical_e1", OLD)
historical = importlib.util.module_from_spec(spec)
spec.loader.exec_module(historical)

CASES = json.loads((HERE / "CASES.json").read_text())
LABELS = json.loads((HERE / "REVIEW_LABELS_V2.json").read_text())
GAP_RULES = json.loads((HERE / "GAP_RULES.json").read_text())
CONFIG = json.loads((ROOT / "experiments/model_backend_deepseek/provider.json").read_text())
ROUTER = (STUDY / "prompts/evidence_router.md").read_text()
VERIFIER = (STUDY / "prompts/claim_verifier.md").read_text()
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def order():
    return sorted(CASES, key=lambda c: hashlib.sha256(c["case_id"].encode()).hexdigest())


def arm_order(i):
    return ("N", "W") if i % 2 == 0 else ("W", "N")


def router_request(case):
    return {"model": CONFIG["model"], "messages": [
        {"role": "system", "content": ROUTER},
        {"role": "user", "content": historical.user_view(case)}], "stream": False}


def narrow_verify_request(case, claim_id, new_refs):
    claim = next(c for c in case["previous_state"]["claims"] if c["claim_id"] == claim_id)
    observed = {o["ref"]: o for o in case["prior_observations"] + [case["new_observation"]]}
    prior_refs = claim["verified_evidence_refs"]
    return {"model": CONFIG["model"], "messages": [
        {"role": "system", "content": VERIFIER},
        {"role": "user", "content": json.dumps({
            "original_relevant_question_anchors": case["question_constraint"],
            "existing_claim": {k: claim[k] for k in ("claim_id", "statement", "status")},
            "previous_verified_evidence": [{"ref": r, "excerpt": observed[r]["text"]} for r in prior_refs],
            "new_cited_exact_evidence": [{"ref": r, "excerpt": observed[r]["text"]} for r in new_refs],
        }, ensure_ascii=False)}], "stream": False}


def source_paths():
    own = ["PROTOCOL.md", "HYPOTHESES.md", "STATE_V2.md", "claim_mutation/RUBRIC.md",
           "claim_mutation/CASES.json", "claim_mutation/REVIEW_LABELS_V2.json", "claim_mutation/GAP_RULES.json",
           "claim_mutation/prepare_bank.py", "claim_mutation/run.py", "claim_mutation/analyze.py"]
    own += [str(p.relative_to(STUDY)) for p in sorted((STUDY / "prompts").glob("*.md"))]
    return [STUDY / p for p in own] + [OLD, OLD.parent / "CASES.json",
           ROOT / "experiments/transactional_research_progress/prompts/updater.md",
           ROOT / "experiments/transactional_research_progress/prompts/verifier.md",
           ROOT / "experiments/model_backend_deepseek/provider.json",
           ROOT / "experiments/model_backend_deepseek/cache_usage.py"]


def validate_bank():
    assert len(CASES) == 41 and len({c["case_id"] for c in CASES}) == 41
    assert len({c["qid"] for c in CASES}) == 12
    assert set(LABELS) == {c["case_id"] for c in CASES}
    assert set(GAP_RULES) == {c["case_id"] for c in CASES}
    assert sha(HERE / "CASES.json") == sha(OLD.parent / "CASES.json")
    for case in CASES:
        for field in ("previous_state", "control_projection", "new_observation"):
            assert historical.digest(case[field]) == case[field + "_sha256"]
        label = LABELS[case["case_id"]]
        ids = {c["claim_id"] for c in case["previous_state"]["claims"]}
        assert set(label["routing_affected_claim_ids"]) <= ids
        assert set(label["routing_only_unscorable"]) <= set(label["routing_affected_claim_ids"])
        assert GAP_RULES[case["case_id"]] == {g["gap_id"]: "all_supported" for g in case["previous_state"]["gaps"]}


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    validate_bank()
    f = {
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "base_head": "bf8eb3262da99a5a29b3b133ed89e2d04f6e755f",
        "provider": {"host": urlsplit(CONFIG["base_url"]).hostname, "model": CONFIG["model"],
                     "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": 0},
        "sample_count": 41, "qids": sorted({c["qid"] for c in CASES}),
        "case_order": [c["case_id"] for c in order()],
        "arm_order": {c["case_id"]: list(arm_order(i)) for i, c in enumerate(order())},
        "case_provenance": {c["case_id"]: c["new_observation"]["provenance"] for c in CASES},
        "prefix_hashes": {c["case_id"]: digest([c["question_constraint"], c["prior_observations"]]) for c in CASES},
        "state_hashes": {c["case_id"]: c["previous_state_sha256"] for c in CASES},
        "observation_hashes": {c["case_id"]: c["new_observation_sha256"] for c in CASES},
        "review_labels_sha256": sha(HERE / "REVIEW_LABELS_V2.json"),
        "gap_rules_sha256": sha(HERE / "GAP_RULES.json"),
        "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in source_paths()},
        "prompt_sha256": {"W_updater": hashlib.sha256(historical.SYSTEM_BC.encode()).hexdigest(),
                          "W_verifier": hashlib.sha256(historical.SYSTEM_VERIFY.encode()).hexdigest(),
                          "N_router": hashlib.sha256(ROUTER.encode()).hexdigest(),
                          "N_verifier": hashlib.sha256(VERIFIER.encode()).hexdigest()},
        "tool_schema_sha256": digest([]),
        "schema_sha256": digest({"router_keys": ["affected_claims", "notes"],
                                  "router_item_keys": ["claim_id", "evidence_refs"],
                                  "verifier_keys": ["status", "evidence_refs", "missing_evidence", "reason"],
                                  "verifier_statuses": ["open", "supported", "refuted"]}),
        "request_sha256": {f"{c['case_id']}:{arm}": digest(historical.request(c, "C") if arm == "W" else router_request(c))
                           for c in CASES for arm in ("W", "N")},
        "rubric_sha256": sha(HERE / "RUBRIC.md"),
        "gate": {"routing_recall_min": .90, "final_mutation_precision_min": .85,
                 "final_mutation_recall_min": .90, "NoGain_preservation_min": .90,
                 "false_closure_max": .10, "paired_churn_improvement_min": 6,
                 "reverse_worsening_less_than_half": True},
        "failure_policy": "One fresh first-stage call per arm per case. No retries or best-of. W verifier errors reject transition. N verifier errors preserve previous status and score as misses. All errors remain in denominator.",
    }
    FREEZE.write_text(json.dumps(f, ensure_ascii=False, indent=2) + "\n")


def gate():
    validate_bank()
    f = json.loads(FREEZE.read_text())
    checks = {
        "source_hashes": f["source_sha256"] == {str(p.relative_to(ROOT)): sha(p) for p in source_paths()},
        "provider": f["provider"] == {"host": urlsplit(CONFIG["base_url"]).hostname, "model": CONFIG["model"],
                                      "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": CONFIG["max_retries"]},
        "order": f["case_order"] == [c["case_id"] for c in order()],
        "requests": all(f["request_sha256"][f"{c['case_id']}:{arm}"] ==
                        digest(historical.request(c, "C") if arm == "W" else router_request(c))
                        for c in CASES for arm in ("W", "N")),
        "labels": f["review_labels_sha256"] == sha(HERE / "REVIEW_LABELS_V2.json"),
        "gap_rules": f["gap_rules_sha256"] == sha(HERE / "GAP_RULES.json"),
        "no_tools": f["tool_schema_sha256"] == digest([]),
    }
    (HERE / "gate.txt").write_text("\n".join(("PASS " if v else "FAIL ") + k for k, v in checks.items()) + "\n")
    if not all(checks.values()):
        raise AssertionError(checks)


def emit(kind, **fields):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "kind": kind, **fields}, ensure_ascii=False) + "\n")
        out.flush()


def model_call(client, req, cell, kind, claim_id=None):
    fields = {"cell": cell, "request": req, "request_sha256": digest(req)}
    if claim_id:
        fields["claim_id"] = claim_id
    emit(kind + "_request", **fields)
    try:
        raw = client.chat.completions.create(**req).model_dump(mode="json")
        emit(kind + "_response", cell=cell, claim_id=claim_id, response=raw, cache_usage=extract(raw))
        return historical.response_content(raw)
    except Exception as exc:
        emit(kind + "_error", cell=cell, claim_id=claim_id, error_type=type(exc).__name__,
             http_status=getattr(exc, "status_code", None), error=str(exc)[:500])
        raise


def validate_router(case, value):
    if not isinstance(value, dict) or not {"affected_claims"} <= set(value) or set(value) - {"affected_claims", "notes"}:
        raise ValueError("router_top_level_schema")
    if not isinstance(value["affected_claims"], list) or not isinstance(value.get("notes", ""), str):
        raise ValueError("router_array_schema")
    ids = {c["claim_id"] for c in case["previous_state"]["claims"]}
    selected = []
    for item in value["affected_claims"]:
        if not isinstance(item, dict) or set(item) != {"claim_id", "evidence_refs"} or item["claim_id"] not in ids:
            raise ValueError("router_claim_schema")
        historical.check_refs(item["evidence_refs"], {o["ref"] for o in case["prior_observations"] + [case["new_observation"]]},
                              require_new=case["new_observation"]["ref"])
        selected.append(item["claim_id"])
    if len(set(selected)) != len(selected):
        raise ValueError("router_duplicate_claim")
    return value["affected_claims"]


def validate_verifier(case, value, supplied_refs):
    if not isinstance(value, dict) or set(value) != {"status", "evidence_refs", "missing_evidence", "reason"} or \
            value["status"] not in ("open", "supported", "refuted") or \
            not isinstance(value["reason"], str) or not isinstance(value["missing_evidence"], str):
        raise ValueError("verifier_schema")
    historical.check_refs(value["evidence_refs"], set(supplied_refs))
    if case["new_observation"]["ref"] not in value["evidence_refs"]:
        raise ValueError("verifier_missing_new_ref")
    return value


def commit_narrow(case, routed, verifications):
    state = copy.deepcopy(case["previous_state"])
    projection = copy.deepcopy(case["control_projection"])
    old = case["previous_state"]
    for item in routed:
        cid = item["claim_id"]
        value = verifications.get(cid)
        if value is None:
            continue
        claim = next(c for c in state["claims"] if c["claim_id"] == cid)
        if value["status"] != claim["status"]:
            claim["status"] = value["status"]
            claim["verified_evidence_refs"] = list(dict.fromkeys(claim["verified_evidence_refs"] + value["evidence_refs"]))
            claim["version"] += 1
    for gap in state["gaps"]:
        if GAP_RULES[case["case_id"]][gap["gap_id"]] != "all_supported":
            raise ValueError("unsupported_frozen_gap_rule")
        if not gap["related_claim_ids"]:
            continue
        related = [next(c for c in state["claims"] if c["claim_id"] == cid) for cid in gap["related_claim_ids"]]
        desired = "closed" if all(c["status"] == "supported" for c in related) else "open"
        if gap["status"] != desired:
            gap["status"] = desired
    if projection["active_gap"] != "none":
        active = next(g for g in state["gaps"] if g["gap_id"] == projection["active_gap"])
        if active["status"] == "closed":
            projection["active_gap"] = "none"
    if state["claims"] != old["claims"] or state["gaps"] != old["gaps"]:
        state["version"] += 1
    return {"verified_progress": state, "control_projection": projection,
            "routed_claim_ids": [x["claim_id"] for x in routed], "verifications": verifications}


def run_w(client, case, cell):
    value = model_call(client, historical.request(case, "C"), cell, "updater")
    delta = historical.validate_delta(case, value)
    verified = {}
    for update in delta["claim_updates"]:
        old = next(x for x in case["previous_state"]["claims"] if x["claim_id"] == update["claim_id"])
        if old["status"] != update["status"]:
            v = call_old_verifier(client, case, update["claim_id"], update["evidence_refs"], cell)
            verified[update["claim_id"]] = {"status": v, "accepted": v == update["status"]}
    for update in delta["gap_updates"]:
        if update["status"] != "closed":
            continue
        gap = next(x for x in case["previous_state"]["gaps"] if x["gap_id"] == update["gap_id"])
        for cid in gap["related_claim_ids"]:
            if cid not in verified:
                v = call_old_verifier(client, case, cid, update["evidence_refs"], cell)
                verified[cid] = {"status": v, "accepted": v in ("supported", "refuted")}
    outcome = historical.commit_delta(case, delta, verified_claims=verified)
    outcome["wide_delta"] = delta
    outcome["verify_decisions"] = verified
    return outcome


def call_old_verifier(client, case, cid, refs, cell):
    claim = next(c for c in case["previous_state"]["claims"] if c["claim_id"] == cid)
    all_refs = list(dict.fromkeys(claim["verified_evidence_refs"] + refs))
    try:
        value = model_call(client, historical.verify_request(case, claim["statement"], all_refs), cell, "wide_verify", cid)
        if set(value) != {"status", "evidence_refs", "missing_evidence", "reason"} or \
                value["status"] not in ("open", "supported", "refuted") or \
                not isinstance(value["reason"], str) or not isinstance(value["missing_evidence"], str):
            raise ValueError("wide_verifier_schema")
        historical.check_refs(value["evidence_refs"], set(all_refs))
        return value["status"]
    except Exception:
        return None


def run_n(client, case, cell):
    value = model_call(client, router_request(case), cell, "router")
    routed = validate_router(case, value)
    verified = {}
    for item in routed:
        cid = item["claim_id"]
        claim = next(c for c in case["previous_state"]["claims"] if c["claim_id"] == cid)
        supplied = list(dict.fromkeys(claim["verified_evidence_refs"] + item["evidence_refs"]))
        try:
            response = model_call(client, narrow_verify_request(case, cid, item["evidence_refs"]), cell, "narrow_verify", cid)
            verified[cid] = validate_verifier(case, response, supplied)
        except Exception:
            verified[cid] = None
    return commit_narrow(case, routed, verified)


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
                try:
                    outcome = run_w(client, case, cell) if arm == "W" else run_n(client, case, cell)
                    emit("arm_outcome", cell=cell, outcome=outcome)
                    print(cell, "ok", flush=True)
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
