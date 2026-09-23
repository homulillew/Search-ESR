"""Frozen E1 A/B/C requests, mechanical commits and triggered semantic verification."""

import copy
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
CONFIG = json.loads((ROOT / "experiments/model_backend_deepseek/provider.json").read_text())
CASES = json.loads((HERE / "CASES.json").read_text())
LABELS = json.loads((HERE / "REVIEW_LABELS.json").read_text())
SYSTEM_BC = (STUDY / "prompts/updater.md").read_text()
SYSTEM_VERIFY = (STUDY / "prompts/verifier.md").read_text()
SYSTEM_A = (
    "Given exactly one new observation, rewrite the entire current VerifiedProgress and ControlProjection "
    "as a strict JSON object. Keep all existing Claims and Gaps and their IDs; change the state only as warranted "
    "by observed evidence. Preserve unchanged statements and refs. Do not invent source refs. "
    "Output exactly keys verified_progress and control_projection. verified_progress has integer version, "
    "claims array of {claim_id, statement, status: open|supported|refuted, verified_evidence_refs: [W#], version: integer}, "
    "and gaps array of {gap_id, description, related_claim_ids: [C#], status: open|closed}. "
    "control_projection has active_gap (G# or none), expected_source_type, uncertainty_type and target_doc, "
    "target_window (D#/W# or none). Do not output explanatory text."
)
FREEZE = HERE / "freeze.json"
EVENTS = HERE / "events.jsonl"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def order():
    return sorted(CASES, key=lambda c: hashlib.sha256(c["case_id"].encode()).hexdigest())


def arm_order(i):
    return (("A", "B", "C"), ("B", "C", "A"), ("C", "A", "B"))[i % 3]


def visible(o):
    return {k: o[k] for k in ("ref", "doc_ref", "title", "text")}


def user_view(case):
    return json.dumps({"original_relevant_question_constraint": case["question_constraint"],
                       "previous_verified_progress": case["previous_state"],
                       "current_control_projection": case["control_projection"],
                       "previous_observed_evidence": [visible(x) for x in case["prior_observations"]],
                       "new_observation": visible(case["new_observation"])}, ensure_ascii=False)


def request(case, arm):
    return {"model": CONFIG["model"], "messages": [
        {"role": "system", "content": SYSTEM_A if arm == "A" else SYSTEM_BC},
        {"role": "user", "content": user_view(case)}], "stream": False}


def verify_request(case, statement, refs):
    observed = {o["ref"]: o for o in case["prior_observations"] + [case["new_observation"]]}
    return {"model": CONFIG["model"], "messages": [
        {"role": "system", "content": SYSTEM_VERIFY},
        {"role": "user", "content": json.dumps({
            "original_relevant_question_constraint": case["question_constraint"],
            "claim": statement,
            "exact_observed_evidence": [{"ref": r, "excerpt": observed[r]["text"]} for r in refs]
        }, ensure_ascii=False)}], "stream": False}


def dependencies():
    paths = [
        "experiments/transactional_research_progress/PROTOCOL.md",
        "experiments/transactional_research_progress/HYPOTHESES.md",
        "experiments/transactional_research_progress/FROZEN_STATE.md",
        "experiments/transactional_research_progress/prompts/updater.md",
        "experiments/transactional_research_progress/prompts/verifier.md",
        "experiments/transactional_research_progress/prompts/frontier_selector.md",
        "experiments/transactional_research_progress/prompts/actor_progress_view.md",
        "experiments/transactional_research_progress/state_transition/case_specs.py",
        "experiments/transactional_research_progress/state_transition/build_cases.py",
        "experiments/transactional_research_progress/state_transition/CASES.json",
        "experiments/transactional_research_progress/state_transition/REVIEW_LABELS.json",
        "experiments/transactional_research_progress/state_transition/RUBRIC.json",
        "experiments/transactional_research_progress/state_transition/EXPERIMENT_PLAN.md",
        "experiments/transactional_research_progress/state_transition/run.py",
        "experiments/transactional_research_progress/state_transition/analyze.py",
        "experiments/model_backend_deepseek/provider.json",
        "experiments/model_backend_deepseek/cache_usage.py",
    ]
    return {p: sha(ROOT / p) for p in paths}


def validate_bank():
    if len(CASES) != 41 or len({c["case_id"] for c in CASES}) != 41 or len({c["qid"] for c in CASES}) != 12:
        raise ValueError("E1 count/qid quota")
    from collections import Counter
    if Counter(c["transition_type"] for c in CASES) != Counter({
        "T1": 8, "T2": 8, "T3": 8, "T4": 8, "T5": 4, "T6": 4, "T7": 1}):
        raise ValueError("E1 transition quotas")
    if set(LABELS) != {c["case_id"] for c in CASES}:
        raise ValueError("E1 label mismatch")
    for c in CASES:
        for key in ("previous_state", "control_projection", "new_observation"):
            if digest(c[key]) != c[key + "_sha256"]:
                raise ValueError(f"Packet tamper {c['case_id']}:{key}")
        if "required_claim_mutations" in user_view(c) or "transition_type" in user_view(c):
            raise ValueError("Private reviewer label leaked")
        for o in c["prior_observations"] + [c["new_observation"]]:
            if hashlib.sha256(o["text"].encode()).hexdigest() != o["provenance"]["text_sha256"]:
                raise ValueError("Excerpt hash mismatch")


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    validate_bank()
    rubric = json.loads((HERE / "RUBRIC.json").read_text())
    frozen = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
              "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "base_head": "eb5bddaf2e901db51c7e12b33bd4ff97fce2d204",
              "model": CONFIG["model"], "provider_host": urlsplit(CONFIG["base_url"]).hostname,
              "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": 0,
              "tool_schema_sha256": digest([]), "sample_count": 41, "updater_calls": 123,
              "case_order": [c["case_id"] for c in order()],
              "arm_order": {c["case_id"]: arm_order(i) for i, c in enumerate(order())},
              "qid_checkpoint": {c["case_id"]: [c["qid"], c["new_observation"]["provenance"]]
                                 for c in CASES},
              "previous_state_sha256": {c["case_id"]: c["previous_state_sha256"] for c in CASES},
              "new_observation_sha256": {c["case_id"]: c["new_observation_sha256"] for c in CASES},
              "exact_excerpt_sha256": {c["case_id"]: c["new_observation"]["provenance"]["text_sha256"]
                                       for c in CASES},
              "review_labels_sha256": sha(HERE / "REVIEW_LABELS.json"),
              "rubric": rubric, "source_sha256": dependencies(),
              "prompt_sha256": {"A": hashlib.sha256(SYSTEM_A.encode()).hexdigest(),
                                "B_C": hashlib.sha256(SYSTEM_BC.encode()).hexdigest(),
                                "Verifier": hashlib.sha256(SYSTEM_VERIFY.encode()).hexdigest()},
              "request_sha256": {f"{c['case_id']}:{a}": digest(request(c, a))
                                 for c in CASES for a in ("A", "B", "C")},
              "failure_policy": rubric["failure_policy"]}
    FREEZE.write_text(json.dumps(frozen, ensure_ascii=False, indent=2) + "\n")


def gate():
    f = json.loads(FREEZE.read_text())
    checks = {
        "sources": dependencies() == f["source_sha256"],
        "bank": len(CASES) == f["sample_count"] == 41 and sha(HERE / "REVIEW_LABELS.json") == f["review_labels_sha256"],
        "provider": CONFIG["model"] == f["model"] and urlsplit(CONFIG["base_url"]).hostname == f["provider_host"]
        and CONFIG["timeout_seconds"] == f["timeout_seconds"] and CONFIG["max_retries"] == f["max_retries"] == 0,
        "order": [c["case_id"] for c in order()] == f["case_order"] and all(
            f["arm_order"][c["case_id"]] == arm_order(i) for i, c in enumerate(order())),
        "requests": all(digest(request(c, a)) == f["request_sha256"][f"{c['case_id']}:{a}"]
                        for c in CASES for a in ("A", "B", "C")),
        "rubric": json.loads((HERE / "RUBRIC.json").read_text()) == f["rubric"],
        "no_tools": f["tool_schema_sha256"] == digest([]),
    }
    (HERE / "gate.txt").write_text("\n".join(f'{"PASS" if v else "FAIL"} {k}' for k, v in checks.items()) +
                                    f"\n{sum(checks.values())}/{len(checks)} PASS\n")
    if not all(checks.values()):
        raise AssertionError(checks)
    validate_bank()


def emit(kind, **fields):
    with EVENTS.open("a") as out:
        out.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "kind": kind, **fields},
                             ensure_ascii=False) + "\n")
        out.flush()


def response_content(raw):
    choice = (raw.get("choices") or [{}])[0]
    if choice.get("finish_reason") != "stop":
        raise ValueError("abnormal_finish")
    content = (choice.get("message") or {}).get("content") or ""
    value = json.loads(content)
    if not isinstance(value, dict):
        raise ValueError("not_json_object")
    return value


def check_refs(refs, observed, *, require_new=None):
    if not isinstance(refs, list) or len(refs) != len(set(refs)) or any(r not in observed for r in refs):
        raise ValueError("invalid_evidence_refs")
    if require_new is not None and require_new not in refs:
        raise ValueError("mutation_missing_new_observation_ref")


def validate_a(case, value):
    if set(value) != {"verified_progress", "control_projection"}:
        raise ValueError("A_top_level_schema")
    state = value["verified_progress"]
    projection = value["control_projection"]
    if not isinstance(state, dict) or set(state) != {"version", "claims", "gaps"} or not isinstance(state["version"], int):
        raise ValueError("A_state_schema")
    old = case["previous_state"]
    if not isinstance(state["claims"], list) or not isinstance(state["gaps"], list):
        raise ValueError("A_array_schema")
    old_ids = {c["claim_id"] for c in old["claims"]}
    got_ids = {c.get("claim_id") for c in state["claims"] if isinstance(c, dict)}
    if len(got_ids) != len(state["claims"]) or not old_ids <= got_ids:
        raise ValueError("A_claim_ids")
    observed = {o["ref"] for o in case["prior_observations"] + [case["new_observation"]]}
    for c in state["claims"]:
        if set(c) != {"claim_id", "statement", "status", "verified_evidence_refs", "version"} or \
                c["status"] not in ("open", "supported", "refuted") or not isinstance(c["statement"], str) or \
                not isinstance(c["version"], int):
            raise ValueError("A_claim_schema")
        check_refs(c["verified_evidence_refs"], observed)
        if c["claim_id"] not in old_ids and c["status"] != "open":
            raise ValueError("A_new_claim_not_open")
        previous = next((x for x in old["claims"] if x["claim_id"] == c["claim_id"]), None)
        if previous and previous["status"] != c["status"] and not c["verified_evidence_refs"]:
            raise ValueError("A_status_transition_without_ref")
    if {g.get("gap_id") for g in state["gaps"] if isinstance(g, dict)} != {g["gap_id"] for g in old["gaps"]}:
        raise ValueError("A_gap_ids")
    for g in state["gaps"]:
        if set(g) != {"gap_id", "description", "related_claim_ids", "status"} or g["status"] not in ("open", "closed") or \
                not isinstance(g["description"], str) or not isinstance(g["related_claim_ids"], list) or \
                any(x not in got_ids for x in g["related_claim_ids"]):
            raise ValueError("A_gap_schema")
    if not isinstance(projection, dict) or set(projection) != set(case["control_projection"]) or \
            projection["active_gap"] not in {"none", "G1", "G2"}:
        raise ValueError("A_projection_schema")
    return {"verified_progress": state, "control_projection": projection}


def validate_delta(case, value):
    if set(value) != {"claim_updates", "new_claims", "gap_updates", "active_gap_action", "notes"} or \
            any(not isinstance(value[k], list) for k in ("claim_updates", "new_claims", "gap_updates")) or \
            value["active_gap_action"] not in ("keep", "retire") or not isinstance(value["notes"], str):
        raise ValueError("delta_top_level_schema")
    new_ref = case["new_observation"]["ref"]
    observed = {o["ref"] for o in case["prior_observations"] + [case["new_observation"]]}
    known_claims = {c["claim_id"] for c in case["previous_state"]["claims"]}
    known_gaps = {g["gap_id"] for g in case["previous_state"]["gaps"]}
    ids = []
    for c in value["claim_updates"]:
        if not isinstance(c, dict) or set(c) != {"claim_id", "status", "evidence_refs"} or \
                c["claim_id"] not in known_claims or c["status"] not in ("open", "supported", "refuted"):
            raise ValueError("delta_claim_update_schema")
        check_refs(c["evidence_refs"], observed, require_new=new_ref)
        ids.append(c["claim_id"])
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate_claim_update")
    for c in value["new_claims"]:
        if not isinstance(c, dict) or set(c) != {"statement", "status", "evidence_refs"} or \
                not isinstance(c["statement"], str) or not c["statement"].strip() or c["status"] != "open":
            raise ValueError("new_claim_schema")
        check_refs(c["evidence_refs"], observed, require_new=new_ref)
    ids = []
    for g in value["gap_updates"]:
        if not isinstance(g, dict) or set(g) != {"gap_id", "status", "evidence_refs"} or \
                g["gap_id"] not in known_gaps or g["status"] not in ("open", "closed"):
            raise ValueError("delta_gap_update_schema")
        check_refs(g["evidence_refs"], observed, require_new=new_ref)
        ids.append(g["gap_id"])
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate_gap_update")
    return value


def commit_delta(case, delta, *, verified_claims=None):
    state = copy.deepcopy(case["previous_state"])
    projection = copy.deepcopy(case["control_projection"])
    verified_claims = verified_claims or {}
    rejected = []
    for update in delta["claim_updates"]:
        current = next(x for x in state["claims"] if x["claim_id"] == update["claim_id"])
        if update["claim_id"] in verified_claims and not verified_claims[update["claim_id"]]["accepted"]:
            rejected.append({"claim_id": update["claim_id"], "reason": "transition_rejected_by_verify",
                             "verifier_status": verified_claims[update["claim_id"]]["status"]})
            continue
        if current["status"] != update["status"] or current["verified_evidence_refs"] != update["evidence_refs"]:
            current["status"] = update["status"]
            current["verified_evidence_refs"] = update["evidence_refs"]
            current["version"] += 1
    for i, item in enumerate(delta["new_claims"], start=len(state["claims"]) + 1):
        state["claims"].append({"claim_id": f"C{i}", "statement": item["statement"],
                                "status": "open", "verified_evidence_refs": item["evidence_refs"],
                                "version": 1})
    for update in delta["gap_updates"]:
        target = next(x for x in state["gaps"] if x["gap_id"] == update["gap_id"])
        if update["status"] == "closed" and any(
            claim_id in verified_claims and not verified_claims[claim_id]["accepted"]
            for claim_id in target["related_claim_ids"]):
            rejected.append({"gap_id": update["gap_id"], "reason": "dependent_closure_rejected"})
            continue
        if target["status"] != update["status"]:
            target["status"] = update["status"]
    if delta["active_gap_action"] == "retire":
        projection["active_gap"] = "none"
    if projection["active_gap"] != "none" and next(g for g in state["gaps"] if g["gap_id"] == projection["active_gap"])["status"] == "closed":
        projection["active_gap"] = "none"
    if state["claims"] != case["previous_state"]["claims"] or state["gaps"] != case["previous_state"]["gaps"]:
        state["version"] += 1
    return {"verified_progress": state, "control_projection": projection,
            "rejected": rejected,
            "proposed_stale_active_gap": delta["active_gap_action"] == "keep" and any(
                g["gap_id"] == case["control_projection"]["active_gap"] and g["status"] == "closed"
                for g in delta["gap_updates"])}


def call_verifier(client, case, claim_id, refs, cell):
    claim = next(x for x in case["previous_state"]["claims"] if x["claim_id"] == claim_id)
    prior_refs = claim["verified_evidence_refs"]
    all_refs = list(dict.fromkeys(prior_refs + refs))
    req = verify_request(case, claim["statement"], all_refs)
    emit("verify_request", cell=cell, claim_id=claim_id, request=req, request_sha256=digest(req))
    try:
        raw = client.chat.completions.create(**req).model_dump(mode="json")
        emit("verify_response", cell=cell, claim_id=claim_id, response=raw, cache_usage=extract(raw))
        value = response_content(raw)
        if set(value) != {"status", "evidence_refs", "missing_evidence", "reason"} or \
                value["status"] not in ("open", "supported", "refuted") or \
                not isinstance(value["reason"], str) or not isinstance(value["missing_evidence"], str):
            raise ValueError("verifier_schema")
        check_refs(value["evidence_refs"], set(all_refs))
        return {"status": value["status"], "response": value}
    except Exception as exc:
        emit("verify_error", cell=cell, claim_id=claim_id, error_type=type(exc).__name__,
             http_status=getattr(exc, "status_code", None), error=str(exc)[:500])
        return {"status": None, "error": type(exc).__name__}


def run():
    gate()
    if EVENTS.exists():
        raise FileExistsError(EVENTS)
    key = dotenv_values(ROOT / CONFIG["credential_file"]).get(CONFIG["credential_field"])
    if not key:
        raise ValueError("DeepSeek credential unavailable")
    with OpenAI(api_key=key, base_url=CONFIG["base_url"], timeout=CONFIG["timeout_seconds"],
                max_retries=0) as client:
        for i, case in enumerate(order()):
            for arm in arm_order(i):
                cell = f"{case['case_id']}:{arm}"
                req = request(case, arm)
                emit("updater_request", cell=cell, request=req, request_sha256=digest(req))
                try:
                    raw = client.chat.completions.create(**req).model_dump(mode="json")
                    emit("updater_response", cell=cell, response=raw, cache_usage=extract(raw))
                    value = response_content(raw)
                    if arm == "A":
                        outcome = validate_a(case, value)
                    else:
                        delta = validate_delta(case, value)
                        verified = {}
                        if arm == "C":
                            for update in delta["claim_updates"]:
                                old = next(x for x in case["previous_state"]["claims"] if x["claim_id"] == update["claim_id"])
                                if old["status"] != update["status"]:
                                    v = call_verifier(client, case, update["claim_id"], update["evidence_refs"], cell)
                                    verified[update["claim_id"]] = {"status": v["status"],
                                                                     "accepted": v["status"] == update["status"]}
                            for update in delta["gap_updates"]:
                                if update["status"] != "closed":
                                    continue
                                gap = next(x for x in case["previous_state"]["gaps"] if x["gap_id"] == update["gap_id"])
                                for claim_id in gap["related_claim_ids"]:
                                    if claim_id in verified:
                                        continue
                                    v = call_verifier(client, case, claim_id, update["evidence_refs"], cell)
                                    verified[claim_id] = {"status": v["status"],
                                                          "accepted": v["status"] in ("supported", "refuted")}
                        outcome = commit_delta(case, delta, verified_claims=verified)
                        if arm == "C" and verified:
                            outcome["verify_decisions"] = verified
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
