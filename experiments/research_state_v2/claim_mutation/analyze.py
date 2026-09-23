"""Prespecified M1 paired scoring, stage gate, and descriptive sensitivity."""

import json
from pathlib import Path

from run import CASES, LABELS

HERE = Path(__file__).resolve().parent


def score(case, arm, outcome, error):
    label = LABELS[case["case_id"]]
    old = case["previous_state"]
    new = outcome["verified_progress"] if outcome else old
    before = {c["claim_id"]: c for c in old["claims"]}
    after = {c["claim_id"]: c for c in new["claims"]}
    old_gaps = {g["gap_id"]: g for g in old["gaps"]}
    new_gaps = {g["gap_id"]: g for g in new["gaps"]}
    required_claims = {r["claim_id"]: r["status"] for r in label["required_claim_mutations"]}
    required_gaps = {r["gap_id"]: r["status"] for r in label["required_gap_mutations"]}
    unscorable_claims = set(label["routing_only_unscorable"])
    unscorable_gaps = set(label["unscorable_gap_ids"])
    new_ref = case["new_observation"]["ref"]
    mutations = []
    for cid, previous in before.items():
        current = after[cid]
        if previous["status"] != current["status"]:
            correct = required_claims.get(cid) == current["status"] and new_ref in current["verified_evidence_refs"]
            mutations.append({"kind": "claim_status", "id": cid, "correct": correct,
                              "scorable": cid not in unscorable_claims, "before": previous["status"],
                              "after": current["status"]})
        if previous["statement"] != current["statement"]:
            mutations.append({"kind": "claim_statement", "id": cid, "correct": False,
                              "scorable": cid not in unscorable_claims})
        if previous["verified_evidence_refs"] != current["verified_evidence_refs"] and previous["status"] == current["status"]:
            mutations.append({"kind": "claim_refs_only", "id": cid, "correct": False,
                              "scorable": cid not in unscorable_claims})
    for cid in set(after) - set(before):
        mutations.append({"kind": "new_claim", "id": cid, "correct": False, "scorable": True})
    for gid, previous in old_gaps.items():
        current = new_gaps[gid]
        if previous["status"] != current["status"]:
            mutations.append({"kind": "gap_status", "id": gid,
                              "correct": required_gaps.get(gid) == current["status"],
                              "scorable": gid not in unscorable_gaps,
                              "before": previous["status"], "after": current["status"]})
        if previous["description"] != current["description"] or previous["related_claim_ids"] != current["related_claim_ids"]:
            mutations.append({"kind": "gap_content", "id": gid, "correct": False,
                              "scorable": gid not in unscorable_gaps})
    scorable = [m for m in mutations if m["scorable"]]
    routed = set(outcome.get("routed_claim_ids", [])) if outcome else set()
    positives = set(label["routing_affected_claim_ids"])
    claim_recall_hits = sum(after[cid]["status"] == status and new_ref in after[cid]["verified_evidence_refs"]
                            for cid, status in required_claims.items())
    gap_recall_hits = sum(new_gaps[gid]["status"] == status for gid, status in required_gaps.items())
    false_closure = any(m["kind"] == "claim_status" and m["scorable"] and
                        m["before"] == "open" and m["after"] in ("supported", "refuted") and not m["correct"]
                        for m in mutations)
    unchanged_progress = all(not m["scorable"] for m in mutations)
    return {
        "case_id": case["case_id"], "qid": case["qid"], "transition_type": case["transition_type"],
        "arm": arm, "error": error, "mutations": mutations,
        "mutation_total": len(scorable), "mutation_correct": sum(m["correct"] for m in scorable),
        "required_total": len(required_claims) + len(required_gaps),
        "required_hit": claim_recall_hits + gap_recall_hits,
        "unrelated_churn": sum(not m["correct"] for m in scorable),
        "new_claims": sum(m["kind"] == "new_claim" for m in scorable),
        "false_closure": false_closure,
        "missed_closure": sum(status in ("supported", "refuted") and after[cid]["status"] == "open"
                              for cid, status in required_claims.items()),
        "NoGain_preserved": unchanged_progress if case["transition_type"] == "T4" else None,
        "routed_claim_ids": sorted(routed) if arm == "N" else None,
        "routing_correct": len(routed & positives) if arm == "N" else None,
        "routing_total": len(routed) if arm == "N" else None,
        "routing_gold_total": len(positives) if arm == "N" else None,
        "routing_missed": sorted(positives - routed) if arm == "N" else None,
        "active_gap_retired": outcome["control_projection"]["active_gap"] == "none" if outcome else False,
        "malformed_claim_mutations": [m for m in mutations if not m["scorable"]],
    }


def aggregate(rows):
    result = {}
    for arm in ("W", "N"):
        group = [r for r in rows if r["arm"] == arm]
        total = sum(r["mutation_total"] for r in group)
        correct = sum(r["mutation_correct"] for r in group)
        required = sum(r["required_total"] for r in group)
        hits = sum(r["required_hit"] for r in group)
        result[arm] = {
            "n": len(group), "errors": sum(r["error"] is not None for r in group),
            "final_mutation_precision": correct / total if total else 0,
            "final_mutation_precision_fraction": [correct, total],
            "final_mutation_recall": hits / required if required else 0,
            "final_mutation_recall_fraction": [hits, required],
            "unrelated_churn_cases": sum(r["unrelated_churn"] > 0 for r in group),
            "unrelated_churn_units": sum(r["unrelated_churn"] for r in group),
            "new_claims": sum(r["new_claims"] for r in group),
            "false_closure_cases": sum(r["false_closure"] for r in group),
            "NoGain_preservation": [sum(r["NoGain_preserved"] is True for r in group), 8],
            "missed_closure_claims": sum(r["missed_closure"] for r in group),
        }
    narrow = [r for r in rows if r["arm"] == "N"]
    selected = sum(r["routing_total"] for r in narrow)
    correct = sum(r["routing_correct"] for r in narrow)
    gold = sum(r["routing_gold_total"] for r in narrow)
    result["N"]["routing_precision"] = correct / selected if selected else 0
    result["N"]["routing_precision_fraction"] = [correct, selected]
    result["N"]["routing_recall"] = correct / gold if gold else 0
    result["N"]["routing_recall_fraction"] = [correct, gold]
    return result


def main():
    events = [json.loads(line) for line in (HERE / "events.jsonl").read_text().splitlines()]
    outcomes = {e["cell"]: e["outcome"] for e in events if e["kind"] == "arm_outcome"}
    errors = {e["cell"]: e for e in events if e["kind"] == "arm_error"}
    expected = {f"{c['case_id']}:{arm}" for c in CASES for arm in ("W", "N")}
    if set(outcomes) & set(errors) or set(outcomes) | set(errors) != expected:
        raise ValueError("Incomplete or duplicate M1 arm cells")
    rows = [score(c, arm, outcomes.get(f"{c['case_id']}:{arm}"),
                  errors.get(f"{c['case_id']}:{arm}", {}).get("error_type"))
            for c in CASES for arm in ("W", "N")]
    by_arm = aggregate(rows)
    improved = worsened = equal = 0
    for case in CASES:
        w = next(r for r in rows if r["case_id"] == case["case_id"] and r["arm"] == "W")
        n = next(r for r in rows if r["case_id"] == case["case_id"] and r["arm"] == "N")
        if n["unrelated_churn"] < w["unrelated_churn"]:
            improved += 1
        elif n["unrelated_churn"] > w["unrelated_churn"]:
            worsened += 1
        else:
            equal += 1
    at_risk = [r for r in rows if r["arm"] == "N" and r["transition_type"] in ("T3", "T4", "T7")]
    conflict = next(r for r in rows if r["case_id"] == "T7_186" and r["arm"] == "N")
    gate = {
        "routing_recall": by_arm["N"]["routing_recall"] >= .90,
        "mutation_precision": by_arm["N"]["final_mutation_precision"] >= .85,
        "mutation_recall": by_arm["N"]["final_mutation_recall"] >= .90,
        "NoGain_preservation": by_arm["N"]["NoGain_preservation"][0] / 8 >= .90,
        "false_closure": sum(r["false_closure"] for r in at_risk) / len(at_risk) <= .10,
        "paired_churn": improved >= 6 and worsened * 2 < improved,
    }
    cache = {}
    for kind in ("updater_response", "wide_verify_response", "router_response", "narrow_verify_response"):
        reports = [e["cache_usage"] for e in events if e["kind"] == kind and e["cache_usage"]["status"] == "reported"]
        hit = sum(x["prompt_cache_hit_tokens"] for x in reports)
        miss = sum(x["prompt_cache_miss_tokens"] for x in reports)
        cache[kind] = {"reported": len(reports), "hit_tokens": hit, "miss_tokens": miss,
                       "weighted_hit_rate": hit / (hit + miss) if hit + miss else None}
    summary = {
        "by_arm": by_arm, "paired_unrelated_churn": {"improved": improved, "worsened": worsened, "equal": equal},
        "N_at_risk_false_closure": [sum(r["false_closure"] for r in at_risk), len(at_risk)],
        "N_conflict_recovery_T7_186": {"C1_reopened": any(m["id"] == "C1" and m["after"] == "open" for m in conflict["mutations"] if m["kind"] == "claim_status"),
                                       "G1_reopened": any(m["id"] == "G1" and m["after"] == "open" for m in conflict["mutations"] if m["kind"] == "gap_status")},
        "gate": gate, "M1_pass": all(gate.values()), "cache": cache,
        "sensitivity_excluding_qid186_T5_T7": aggregate([r for r in rows if r["case_id"] not in ("T5_186", "T7_186")]),
        "limitations": "Reviewer-authored state; correlated sibling cases; qid186 malformed credit Claims and ambiguous title identity are separated."
    }
    (HERE / "results.json").write_text(json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
