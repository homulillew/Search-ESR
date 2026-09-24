"""Arm-blind V1 packets and frozen metric computation from reviewer labels."""

import hashlib
import json
import statistics
import sys
from pathlib import Path

from run import CASES

HERE = Path(__file__).resolve().parent
FLAGS = ("gap_relevant", "task_anchored", "testable", "minimal")


def events_index():
    events = [json.loads(s) for s in (HERE / "events.jsonl").read_text().splitlines()]
    outcomes = {e["cell"]: e["items"] for e in events if e["kind"] == "arm_outcome"}
    errors = {e["cell"]: e for e in events if e["kind"] == "arm_error"}
    expected = {f"{c['case_id']}:{a}" for c in CASES for a in ("C0", "C1", "C2")}
    if set(outcomes) & set(errors) or set(outcomes) | set(errors) != expected:
        raise ValueError("incomplete or duplicate V1 cells")
    return events, outcomes, errors


def review_id(cell):
    return "V" + hashlib.sha256(("V1 blind prefix review:" + cell).encode()).hexdigest()[:14]


def prepare_review():
    if (HERE / "REVIEW_PACKETS.json").exists():
        raise FileExistsError("REVIEW_PACKETS.json")
    events, outcomes, errors = events_index()
    mapping = {}
    packets = []
    for case in CASES:
        for arm in ("C0", "C1", "C2"):
            cell = f"{case['case_id']}:{arm}"
            rid = review_id(cell)
            mapping[rid] = cell
            packets.append({"review_id": rid, "case_id": case["case_id"], "qid": case["qid"],
                            "raw_question": case["raw_question"], "question_anchors": case["question_anchors"],
                            "working_hypothesis": case["working_hypothesis"], "semantic_gap": case["semantic_gap"],
                            "visible_evidence": case["visible_evidence"], "existing_tests": case["existing_tests"],
                            "coverage_requirements": case["coverage_requirements"],
                            "review_unknown_slots": case["review_unknown_slots"],
                            "items": outcomes.get(cell, []), "error": errors.get(cell, {}).get("error_type")})
    packets.sort(key=lambda p: hashlib.sha256(p["review_id"].encode()).hexdigest())
    (HERE / "REVIEW_PACKETS.json").write_text(json.dumps(packets, ensure_ascii=False, indent=2) + "\n")
    (HERE / "PRIVATE_MAPPING.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n")


def validate_review(packet, review):
    if set(review) != {"items", "coverage", "unknown_preserved", "reason"} or \
            len(review["items"]) != len(packet["items"]) or \
            len(review["coverage"]) != len(packet["coverage_requirements"]) or \
            len(review["unknown_preserved"]) != len(packet["review_unknown_slots"]) or \
            not isinstance(review["reason"], str) or not review["reason"].strip():
        raise ValueError("review schema " + packet["review_id"])
    if any(not isinstance(x, bool) for x in review["coverage"] + review["unknown_preserved"]):
        raise ValueError("review booleans " + packet["review_id"])
    for item in review["items"]:
        if set(item) != set(FLAGS) | {"bindings", "reason"} or \
                any(not isinstance(item[k], bool) for k in FLAGS) or \
                not isinstance(item["bindings"], list) or not isinstance(item["reason"], str) or not item["reason"].strip():
            raise ValueError("review item " + packet["review_id"])
        for b in item["bindings"]:
            if set(b) != {"value", "basis", "reason"} or not isinstance(b["value"], str) or not b["value"] or \
                    b["basis"] not in ("question", "evidence", "working_hypothesis", "none") or \
                    not isinstance(b["reason"], str) or not b["reason"].strip():
                raise ValueError("binding review " + packet["review_id"])


def score():
    events, outcomes, errors = events_index()
    packets = {p["review_id"]: p for p in json.loads((HERE / "REVIEW_PACKETS.json").read_text())}
    mapping = json.loads((HERE / "PRIVATE_MAPPING.json").read_text())
    reviews = json.loads((HERE / "REVIEWS.json").read_text())
    if set(mapping) != set(packets) or set(reviews) != set(mapping):
        raise ValueError("review mapping mismatch")
    rows = []
    for rid, cell in mapping.items():
        p = packets[rid]
        review = reviews[rid]
        validate_review(p, review)
        case_id, arm = cell.rsplit(":", 1)
        item_count = len(p["items"])
        bindings = [b for item in review["items"] for b in item["bindings"]]
        unsupported = [b for b in bindings if b["basis"] == "none"]
        error = errors.get(cell, {}).get("error_type")
        if error and (any(review["coverage"]) or any(review["unknown_preserved"])):
            raise ValueError("invalid cell cannot receive credit " + cell)
        response = next((e for e in events if e["kind"] == "model_response" and e["cell"] == cell), None)
        raw_usage = response["response"].get("usage", {}) if response else {}
        rows.append({"review_id": rid, "case_id": case_id, "qid": p["qid"], "arm": arm,
                     "error": error, "item_count": item_count,
                     "known_count": sum(len(x.get("known", [])) for x in p["items"]),
                     "unknown_count": sum(len(x.get("unknown", [])) for x in p["items"]),
                     "binding_count": len(bindings), "unsupported_count": len(unsupported),
                     "unsupported_values": [b["value"] for b in unsupported],
                     "premature_case": bool(unsupported) or bool(error),
                     "coverage": sum(review["coverage"]) / len(review["coverage"]),
                     "testable_items": sum(x["testable"] for x in review["items"]) if not error else 0,
                     "testability_denominator": max(1, item_count),
                     "testability": sum(x["testable"] for x in review["items"]) / max(1, item_count) if not error else 0,
                     "minimality": sum(x["minimal"] for x in review["items"]) / max(1, item_count) if not error else 0,
                     "unknown_preservation": sum(review["unknown_preserved"]) / len(review["unknown_preserved"]),
                     "output_tokens": raw_usage.get("completion_tokens"),
                     "latency_seconds": response.get("latency_seconds") if response else errors[cell].get("latency_seconds"),
                     "review": review})
    by_arm = {}
    for arm in ("C0", "C1", "C2"):
        group = [r for r in rows if r["arm"] == arm]
        bindings = sum(r["binding_count"] for r in group)
        unsupported = sum(r["unsupported_count"] for r in group)
        by_arm[arm] = {
            "n": len(group), "errors": sum(r["error"] is not None for r in group),
            "unsupported_binding_rate": unsupported / bindings if bindings else 0,
            "unsupported_binding_fraction": [unsupported, bindings],
            "premature_specificity_case_rate": sum(r["premature_case"] for r in group) / len(group),
            "premature_specificity_cases": sum(r["premature_case"] for r in group),
            "mean_coverage": statistics.mean(r["coverage"] for r in group),
            "mean_testability": sum(r["testable_items"] for r in group) / sum(r["testability_denominator"] for r in group),
            "mean_minimality": statistics.mean(r["minimality"] for r in group),
            "mean_unknown_preservation": statistics.mean(r["unknown_preservation"] for r in group),
            "mean_items": statistics.mean(r["item_count"] for r in group),
            "mean_known_fields": statistics.mean(r["known_count"] for r in group),
            "mean_unknown_fields": statistics.mean(r["unknown_count"] for r in group),
            "mean_output_tokens": statistics.mean(r["output_tokens"] for r in group if r["output_tokens"] is not None),
            "mean_latency_seconds": statistics.mean(r["latency_seconds"] for r in group if r["latency_seconds"] is not None),
        }
    paired = {}
    for arm in ("C1", "C2"):
        improved = worsened = equal = 0
        for case in CASES:
            c0 = next(r for r in rows if r["case_id"] == case["case_id"] and r["arm"] == "C0")
            test = next(r for r in rows if r["case_id"] == case["case_id"] and r["arm"] == arm)
            if c0["premature_case"] and not test["premature_case"]:
                improved += 1
            elif test["premature_case"] and not c0["premature_case"]:
                worsened += 1
            else:
                equal += 1
        paired[arm] = {"improved": improved, "worsened": worsened, "equal": equal}
    gates = {}
    for arm in ("C1", "C2"):
        m = by_arm[arm]
        p = paired[arm]
        gates[arm] = {"unsupported_binding": m["unsupported_binding_rate"] <= .10,
                      "premature_cases": m["premature_specificity_case_rate"] <= .15,
                      "coverage": m["mean_coverage"] >= .70,
                      "testability": m["mean_testability"] >= .85,
                      "paired_improvement": p["improved"] >= 8 and p["worsened"] <= 2}
    passed = [arm for arm in gates if all(gates[arm].values())]
    selected = None
    if passed:
        selected = "C1" if "C1" in passed else "C2"
        if len(passed) == 2:
            c1, c2 = by_arm["C1"], by_arm["C2"]
            if (c2["unsupported_binding_rate"] + .05 < c1["unsupported_binding_rate"] or
                c2["errors"] + 2 <= c1["errors"] or
                c2["mean_unknown_preservation"] >= c1["mean_unknown_preservation"] + .10):
                selected = "C2"
    cache = {}
    for arm in ("C0", "C1", "C2"):
        reports = [e["cache_usage"] for e in events if e["kind"] == "model_response" and e["cell"].endswith(":" + arm)
                   and e["cache_usage"]["status"] == "reported"]
        hit = sum(x["prompt_cache_hit_tokens"] for x in reports)
        miss = sum(x["prompt_cache_miss_tokens"] for x in reports)
        cache[arm] = {"reported": len(reports), "hit_tokens": hit, "miss_tokens": miss,
                      "weighted_hit_rate": hit / (hit + miss) if hit + miss else None}
    summary = {"by_arm": by_arm, "paired": paired, "gate": gates,
               "V1_pass": bool(passed), "selected_TestCard_arm": selected, "cache": cache}
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
