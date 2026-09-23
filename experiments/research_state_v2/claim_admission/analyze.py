"""Make arm-blind A1 review packets and apply the frozen reviewer rubric/gate."""

import hashlib
import json
import sys
from pathlib import Path

from run import CASES

HERE = Path(__file__).resolve().parent
FLAGS = ("task_anchored", "gap_relevant", "testable", "no_premature_commitment", "nonredundant", "minimal")


def event_index():
    events = [json.loads(line) for line in (HERE / "events.jsonl").read_text().splitlines()]
    outcomes = {e["cell"]: e["claims"] for e in events if e["kind"] == "arm_outcome"}
    errors = {e["cell"]: e for e in events if e["kind"] == "arm_error"}
    expected = {f"{c['case_id']}:{a}" for c in CASES for a in ("O", "G")}
    if set(outcomes) & set(errors) or set(outcomes) | set(errors) != expected:
        raise ValueError("incomplete or duplicate A1 cells")
    return events, outcomes, errors


def review_id(cell):
    return "R" + hashlib.sha256(("A1 blind review:" + cell).encode()).hexdigest()[:12]


def prepare_review():
    if (HERE / "REVIEW_PACKETS.json").exists():
        raise FileExistsError("REVIEW_PACKETS.json")
    _, outcomes, errors = event_index()
    mapping = {}
    packets = []
    for case in CASES:
        for arm in ("O", "G"):
            cell = f"{case['case_id']}:{arm}"
            rid = review_id(cell)
            mapping[rid] = cell
            packets.append({
                "review_id": rid, "case_id": case["case_id"], "qid": case["qid"],
                "raw_question": case["raw_question"], "question_anchors": case["question_anchors"],
                "active_gap": case["active_gap"], "existing_claims": case["existing_claims"],
                "latest_observation": case["latest_observation"],
                "coverage_requirements": case["coverage_requirements"],
                "proposed_claims": outcomes.get(cell, []),
                "error": errors.get(cell, {}).get("error_type"),
            })
    packets.sort(key=lambda p: hashlib.sha256(p["review_id"].encode()).hexdigest())
    (HERE / "REVIEW_PACKETS.json").write_text(json.dumps(packets, ensure_ascii=False, indent=2) + "\n")
    (HERE / "PRIVATE_MAPPING.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n")


def score():
    events, outcomes, errors = event_index()
    mapping = json.loads((HERE / "PRIVATE_MAPPING.json").read_text())
    reviews = json.loads((HERE / "REVIEWS.json").read_text())
    if set(reviews) != set(mapping):
        raise ValueError("review ids mismatch")
    case_by_id = {c["case_id"]: c for c in CASES}
    rows = []
    for rid, cell in mapping.items():
        case_id, arm = cell.rsplit(":", 1)
        case = case_by_id[case_id]
        review = reviews[rid]
        proposed = outcomes.get(cell, [])
        marks = review["claim_reviews"]
        covered = review["coverage"]
        if len(marks) != len(proposed) or len(covered) != len(case["coverage_requirements"]):
            raise ValueError("review dimensions " + rid)
        if not isinstance(review["reason"], str) or not review["reason"].strip():
            raise ValueError("missing review reason " + rid)
        for mark in marks:
            if set(mark) != set(FLAGS) | {"semantically_plausible", "reason"} or \
                    any(not isinstance(mark[k], bool) for k in FLAGS + ("semantically_plausible",)) or \
                    not isinstance(mark["reason"], str) or not mark["reason"].strip():
                raise ValueError("claim review schema " + rid)
        if any(not isinstance(x, bool) for x in covered):
            raise ValueError("coverage schema " + rid)
        appropriate = sum(all(mark[k] for k in FLAGS) for mark in marks)
        full_coverage = all(covered)
        precision = appropriate / len(marks) if marks else (1.0 if full_coverage else 0.0)
        rows.append({"review_id": rid, "case_id": case_id, "qid": case["qid"], "arm": arm,
                     "error": errors.get(cell, {}).get("error_type"),
                     "claims": len(marks), "appropriate": appropriate, "precision": precision,
                     "coverage": sum(covered) / len(covered), "covered": covered,
                     "premature": sum(not m["no_premature_commitment"] for m in marks),
                     "redundant": sum(not m["nonredundant"] for m in marks),
                     "task_anchor_valid": sum(m["task_anchored"] for m in marks),
                     "testable": sum(m["testable"] for m in marks),
                     "plausible": sum(m["semantically_plausible"] for m in marks),
                     "review": review})
    by_arm = {}
    for arm in ("O", "G"):
        group = [r for r in rows if r["arm"] == arm]
        count = sum(r["claims"] for r in group)
        good = sum(r["appropriate"] for r in group)
        by_arm[arm] = {"n": len(group), "errors": sum(r["error"] is not None for r in group),
                       "claims": count, "claims_per_case": count / len(group),
                       "progress_appropriate_precision": good / count if count else 0,
                       "progress_appropriate_fraction": [good, count],
                       "case_mean_precision": sum(r["precision"] for r in group) / len(group),
                       "coverage": sum(r["coverage"] for r in group) / len(group),
                       "premature_rate": sum(r["premature"] for r in group) / count if count else 0,
                       "redundant_rate": sum(r["redundant"] for r in group) / count if count else 0,
                       "task_anchor_valid": sum(r["task_anchor_valid"] for r in group) / count if count else 0,
                       "testability": sum(r["testable"] for r in group) / count if count else 0,
                       "semantic_plausibility": sum(r["plausible"] for r in group) / count if count else 0}
    improved = worsened = equal = 0
    for case in CASES:
        o = next(r for r in rows if r["case_id"] == case["case_id"] and r["arm"] == "O")
        g = next(r for r in rows if r["case_id"] == case["case_id"] and r["arm"] == "G")
        if g["precision"] > o["precision"]:
            improved += 1
        elif g["precision"] < o["precision"]:
            worsened += 1
        else:
            equal += 1
    gate = {"paired_precision": improved >= 5 and worsened * 2 < improved,
            "coverage": by_arm["G"]["coverage"] + .10 >= by_arm["O"]["coverage"],
            "premature": by_arm["G"]["premature_rate"] <= .15,
            "redundant": by_arm["G"]["redundant_rate"] <= .15}
    cache = {}
    for arm in ("O", "G"):
        reports = [e["cache_usage"] for e in events if e["kind"] == "compiler_response" and
                   e["cell"].endswith(":" + arm) and e["cache_usage"]["status"] == "reported"]
        hit = sum(x["prompt_cache_hit_tokens"] for x in reports)
        miss = sum(x["prompt_cache_miss_tokens"] for x in reports)
        cache[arm] = {"reported": len(reports), "hit_tokens": hit, "miss_tokens": miss,
                      "weighted_hit_rate": hit / (hit + miss) if hit + miss else None}
    summary = {"by_arm": by_arm, "pairs": {"improved": improved, "worsened": worsened, "equal": equal},
               "gate": gate, "A1_pass": all(gate.values()), "cache": cache}
    (HERE / "results.json").write_text(json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    action = sys.argv[1]
    if action == "prepare_review":
        prepare_review()
    elif action == "score":
        score()
    else:
        raise SystemExit("prepare_review|score")
