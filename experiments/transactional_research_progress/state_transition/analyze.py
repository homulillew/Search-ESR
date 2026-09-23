"""Prespecified paired E1 metrics and stage gate from committed arm outcomes."""

import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = json.loads((HERE / "CASES.json").read_text())
LABELS = json.loads((HERE / "REVIEW_LABELS.json").read_text())


def semantic_state(state):
    return {"claims": [{k: c[k] for k in ("claim_id", "statement", "status", "verified_evidence_refs")}
                       for c in state["claims"]],
            "gaps": state["gaps"]}


def score(case, arm, outcome, error):
    label = LABELS[case["case_id"]]
    old = case["previous_state"]
    new = outcome["verified_progress"] if outcome else old
    projection = outcome["control_projection"] if outcome else case["control_projection"]
    prior_claims = {c["claim_id"]: c for c in old["claims"]}
    next_claims = {c["claim_id"]: c for c in new["claims"]}
    prior_gaps = {g["gap_id"]: g for g in old["gaps"]}
    next_gaps = {g["gap_id"]: g for g in new["gaps"]}
    required_claims = {r["claim_id"]: r["status"] for r in label["required_claim_mutations"]}
    required_gaps = {r["gap_id"]: r["status"] for r in label["required_gap_mutations"]}
    ref = case["new_observation"]["ref"]
    total = correct = unrelated = false_closure = new_claims = 0
    binding_total = binding_valid = 0
    mutations = []
    for cid, before in prior_claims.items():
        after = next_claims[cid]
        if before["status"] != after["status"]:
            total += 1
            binding_total += 1
            bound = ref in after["verified_evidence_refs"]
            binding_valid += bound
            is_correct = required_claims.get(cid) == after["status"] and bound
            correct += is_correct
            if not is_correct:
                unrelated += 1
            if before["status"] == "open" and after["status"] in ("supported", "refuted") and \
                    required_claims.get(cid) != after["status"]:
                false_closure += 1
            mutations.append({"kind": "claim_status", "id": cid, "before": before["status"],
                              "after": after["status"], "correct": bool(is_correct), "bound": bound})
        if before["statement"] != after["statement"]:
            total += 1; unrelated += 1
            mutations.append({"kind": "claim_statement", "id": cid, "correct": False})
        if before["verified_evidence_refs"] != after["verified_evidence_refs"] and \
                before["status"] == after["status"]:
            total += 1; unrelated += 1
            mutations.append({"kind": "claim_refs_only", "id": cid, "correct": False})
    for cid in set(next_claims) - set(prior_claims):
        total += 1; unrelated += 1; new_claims += 1
        mutations.append({"kind": "new_claim", "id": cid, "correct": False})
    for gid, before in prior_gaps.items():
        after = next_gaps[gid]
        if before["status"] != after["status"]:
            total += 1
            is_correct = required_gaps.get(gid) == after["status"]
            correct += is_correct
            if not is_correct:
                unrelated += 1
            mutations.append({"kind": "gap_status", "id": gid, "before": before["status"],
                              "after": after["status"], "correct": bool(is_correct)})
        if before["description"] != after["description"] or \
                before["related_claim_ids"] != after["related_claim_ids"]:
            total += 1; unrelated += 1
            mutations.append({"kind": "gap_content", "id": gid, "correct": False})
    required_total = len(required_claims) + len(required_gaps)
    correct_required = sum(required_claims[cid] == next_claims[cid]["status"] and
                           ref in next_claims[cid]["verified_evidence_refs"] for cid in required_claims) + \
                       sum(required_gaps[gid] == next_gaps[gid]["status"] for gid in required_gaps)
    missed_close = sum(status in ("supported", "refuted") and next_claims[cid]["status"] == "open"
                       for cid, status in required_claims.items())
    return {"case_id": case["case_id"], "qid": case["qid"], "transition_type": case["transition_type"],
            "ambiguity": label["ambiguity"], "arm": arm, "error": error,
            "mutations": mutations, "mutation_total": total, "mutation_correct": correct,
            "required_total": required_total, "correct_required": correct_required,
            "unrelated_churn": unrelated, "false_closure": false_closure, "missed_closure": missed_close,
            "binding_total": binding_total, "binding_valid": binding_valid,
            "unsupported_new_claims": new_claims,
            "NoGain_preserved": semantic_state(old) == semantic_state(new) if case["transition_type"] == "T4" else None,
            "active_gap_retired": projection["active_gap"] == "none" if label["active_gap_should_retire"] else None,
            "stale_active_gap": label["active_gap_should_retire"] and projection["active_gap"] != "none",
            "proposed_stale_active_gap": (outcome or {}).get("proposed_stale_active_gap"),
            "verify_rejected": len((outcome or {}).get("rejected", []))}


def main():
    events = [json.loads(s) for s in (HERE / "events.jsonl").read_text().splitlines()]
    outcomes = {e["cell"]: e["outcome"] for e in events if e["kind"] == "arm_outcome"}
    errors = {e["cell"]: e for e in events if e["kind"] == "arm_error"}
    expected = {f"{c['case_id']}:{arm}" for c in CASES for arm in ("A", "B", "C")}
    if set(outcomes) & set(errors) or set(outcomes) | set(errors) != expected:
        raise ValueError("Incomplete or duplicate E1 arm cells")
    rows = [score(c, arm, outcomes.get(f"{c['case_id']}:{arm}"),
                  errors.get(f"{c['case_id']}:{arm}", {}).get("error_type"))
            for c in CASES for arm in ("A", "B", "C")]
    by_arm = {}
    for arm in ("A", "B", "C"):
        group = [r for r in rows if r["arm"] == arm]
        total = sum(r["mutation_total"] for r in group)
        right = sum(r["mutation_correct"] for r in group)
        required = sum(r["required_total"] for r in group)
        by_arm[arm] = {"n": len(group), "errors": sum(r["error"] is not None for r in group),
                       "mutation_total": total, "mutation_correct": right,
                       "mutation_precision": right / total if total else 0,
                       "mutation_recall": sum(r["correct_required"] for r in group) / required if required else 0,
                       "unrelated_churn_cases": sum(r["unrelated_churn"] > 0 for r in group),
                       "unrelated_churn_units": sum(r["unrelated_churn"] for r in group),
                       "false_closure_cases": sum(r["false_closure"] > 0 for r in group),
                       "missed_closure_claims": sum(r["missed_closure"] for r in group),
                       "evidence_binding": [sum(r["binding_valid"] for r in group),
                                            sum(r["binding_total"] for r in group)],
                       "unsupported_new_claims": sum(r["unsupported_new_claims"] for r in group),
                       "T4_NoGain_preservation": [sum(r["NoGain_preserved"] is True for r in group), 8],
                       "T6_active_gap_retired": [sum(r["active_gap_retired"] is True for r in group), 4],
                       "proposed_stale_active_gap": sum(r["proposed_stale_active_gap"] is True for r in group),
                       "verify_rejected": sum(r["verify_rejected"] for r in group)}
    pairs = {}
    for intervention in ("B", "C"):
        improved = worsened = equal = 0
        for case in CASES:
            a = next(r for r in rows if r["case_id"] == case["case_id"] and r["arm"] == "A")
            b = next(r for r in rows if r["case_id"] == case["case_id"] and r["arm"] == intervention)
            if b["unrelated_churn"] < a["unrelated_churn"]:
                improved += 1
            elif b["unrelated_churn"] > a["unrelated_churn"]:
                worsened += 1
            else:
                equal += 1
        pairs[intervention + "_vs_A"] = {"improved": improved, "worsened": worsened, "equal": equal}
    at_risk = [r for r in rows if r["arm"] == "C" and r["transition_type"] in ("T3", "T4", "T7")]
    gate = {"G1": any(p["improved"] >= 4 and p["worsened"] * 2 < p["improved"] for p in pairs.values()),
            "G2": sum(r["false_closure"] > 0 for r in at_risk) / len(at_risk) <= .10,
            "G3": by_arm["C"]["mutation_precision"] >= .80,
            "G4": by_arm["C"]["T4_NoGain_preservation"][0] / 8 >= .80}
    by_type = {arm: {kind: {"n": len(g := [r for r in rows if r["arm"] == arm and r["transition_type"] == kind]),
                            "correct_required": sum(r["correct_required"] for r in g),
                            "required_total": sum(r["required_total"] for r in g),
                            "unrelated_churn_cases": sum(r["unrelated_churn"] > 0 for r in g),
                            "false_closure_cases": sum(r["false_closure"] > 0 for r in g)}
                          for kind in ("T1", "T2", "T3", "T4", "T5", "T6", "T7")}
               for arm in ("A", "B", "C")}
    usage = {}
    for group in ("updater_response", "verify_response"):
        reports = [e["cache_usage"] for e in events if e["kind"] == group and e["cache_usage"]["status"] == "reported"]
        hit = sum(x["prompt_cache_hit_tokens"] for x in reports)
        miss = sum(x["prompt_cache_miss_tokens"] for x in reports)
        usage[group] = {"reported": len(reports), "hit_tokens": hit, "miss_tokens": miss,
                        "weighted_hit_rate": hit / (hit + miss) if hit + miss else None}
    summary = {"by_arm": by_arm, "paired_unrelated_churn": pairs, "by_transition_type": by_type,
               "C_at_risk_false_closure": [sum(r["false_closure"] > 0 for r in at_risk), len(at_risk)],
               "gate": gate, "E1_pass": all(gate.values()), "cache": usage,
               "limitations": "Reviewer-authored states; correlated siblings and one medium-ambiguity T7 case."}
    (HERE / "results.json").write_text(json.dumps({"summary": summary, "rows": rows},
                                                   ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"by_arm": by_arm, "pairs": pairs, "gate": gate, "E1_pass": all(gate.values())},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
