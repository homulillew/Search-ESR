"""Arm-masked V2 query packets and frozen paired gate."""

import hashlib
import json
import statistics
import sys
from pathlib import Path

from run import CASES

HERE = Path(__file__).resolve().parent
FLAGS = ("gap_alignment", "source_type_alignment", "unsupported_binding_leakage",
         "confirmation_bias", "unknown_targeting")


def events_index():
    events = [json.loads(s) for s in (HERE / "events.jsonl").read_text().splitlines()]
    outcomes = {e["cell"]: e["output"] for e in events if e["kind"] == "arm_outcome"}
    errors = {e["cell"]: e["error_type"] for e in events if e["kind"] == "arm_error"}
    expected = {f"{c['case_id']}:{a}" for c in CASES for a in ("Q0", "Q1", "Q2")}
    if set(outcomes) & set(errors) or set(outcomes) | set(errors) != expected:
        raise ValueError("incomplete or duplicate V2 cells")
    return events, outcomes, errors


def review_id(cell):
    return "Q" + hashlib.sha256(("V2 blind prefix review:" + cell).encode()).hexdigest()[:14]


def prepare_review():
    if (HERE / "REVIEW_PACKETS.json").exists():
        raise FileExistsError("REVIEW_PACKETS.json")
    _, outcomes, errors = events_index()
    mapping = {}
    packets = []
    for c in CASES:
        for arm in ("Q0", "Q1", "Q2"):
            cell = f"{c['case_id']}:{arm}"
            rid = review_id(cell)
            mapping[rid] = cell
            packets.append({"review_id": rid, "case_id": c["case_id"], "qid": c["qid"],
                            "raw_question": c["raw_question"], "question_anchors": c["question_anchors"],
                            "visible_evidence": c["visible_evidence"],
                            "working_hypothesis": c["working_hypothesis"],
                            "semantic_gap": c["semantic_gap"], "expected_source_type": c["expected_source_type"],
                            "query": outcomes.get(cell, {}).get("query"),
                            "error": errors.get(cell)})
    packets.sort(key=lambda p: hashlib.sha256(p["review_id"].encode()).hexdigest())
    (HERE / "REVIEW_PACKETS.json").write_text(json.dumps(packets, ensure_ascii=False, indent=2) + "\n")
    (HERE / "PRIVATE_MAPPING.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n")


def validate_review(packet, review):
    if set(review) != set(FLAGS) | {"leaking_values", "specificity", "reason"}:
        raise ValueError("review schema " + packet["review_id"])
    if any(not isinstance(review[k], bool) for k in FLAGS):
        raise ValueError("review flags " + packet["review_id"])
    if not isinstance(review["leaking_values"], list) or any(not isinstance(x, str) for x in review["leaking_values"]):
        raise ValueError("leak strings " + packet["review_id"])
    if review["unsupported_binding_leakage"] != bool(review["leaking_values"]):
        raise ValueError("leak consistency " + packet["review_id"])
    if review["confirmation_bias"] and not review["unsupported_binding_leakage"]:
        raise ValueError("confirmation requires leakage " + packet["review_id"])
    if review["specificity"] not in ("low", "medium", "high", "none") or not review["reason"].strip():
        raise ValueError("review detail " + packet["review_id"])
    if packet["error"] and (any(review[k] for k in FLAGS) or review["specificity"] != "none"):
        raise ValueError("invalid query cannot score positive " + packet["review_id"])


def score():
    events, outcomes, errors = events_index()
    packets = {p["review_id"]: p for p in json.loads((HERE / "REVIEW_PACKETS.json").read_text())}
    mapping = json.loads((HERE / "PRIVATE_MAPPING.json").read_text())
    reviews = json.loads((HERE / "REVIEWS.json").read_text())
    if set(reviews) != set(mapping) or set(packets) != set(mapping):
        raise ValueError("review mapping mismatch")
    rows = []
    for rid, cell in mapping.items():
        p, review = packets[rid], reviews[rid]
        validate_review(p, review)
        case_id, arm = cell.rsplit(":", 1)
        response = next((e for e in events if e["kind"] == "model_response" and e["cell"] == cell), None)
        usage = response["response"].get("usage", {}) if response else {}
        rows.append({"review_id": rid, "case_id": case_id, "qid": p["qid"], "arm": arm,
                     "query": p["query"], "error": errors.get(cell), "review": review,
                     "output_tokens": usage.get("completion_tokens"),
                     "latency_seconds": response.get("latency_seconds") if response else None})
    by_arm = {}
    for arm in ("Q0", "Q1", "Q2"):
        group = [r for r in rows if r["arm"] == arm]
        by_arm[arm] = {"n": len(group), "errors": sum(r["error"] is not None for r in group),
                       **{k: sum(r["review"][k] for r in group) / len(group) for k in FLAGS},
                       "mean_output_tokens": statistics.mean(r["output_tokens"] for r in group if r["output_tokens"] is not None),
                       "mean_latency_seconds": statistics.mean(r["latency_seconds"] for r in group if r["latency_seconds"] is not None)}
    improved = worsened = equal = 0
    for c in CASES:
        q1 = next(r for r in rows if r["case_id"] == c["case_id"] and r["arm"] == "Q1")
        q2 = next(r for r in rows if r["case_id"] == c["case_id"] and r["arm"] == "Q2")
        one = q1["review"]["unsupported_binding_leakage"]
        two = q2["review"]["unsupported_binding_leakage"]
        if one and not two:
            improved += 1
        elif two and not one:
            worsened += 1
        else:
            equal += 1
    paired = {"improved": improved, "worsened": worsened, "equal": equal,
              "net_improvements": improved - worsened}
    gate = {"paired_leakage": improved - worsened >= 6 and 2 * worsened < improved,
            "gap_alignment": by_arm["Q2"]["gap_alignment"] >= by_arm["Q1"]["gap_alignment"],
            "source_type_alignment": by_arm["Q2"]["source_type_alignment"] >= by_arm["Q1"]["source_type_alignment"]}
    cache = {}
    for arm in ("Q0", "Q1", "Q2"):
        reports = [e["cache_usage"] for e in events if e["kind"] == "model_response" and e["cell"].endswith(":" + arm)
                   and e["cache_usage"]["status"] == "reported"]
        hit = sum(x["prompt_cache_hit_tokens"] for x in reports)
        miss = sum(x["prompt_cache_miss_tokens"] for x in reports)
        cache[arm] = {"reported": len(reports), "hit_tokens": hit, "miss_tokens": miss,
                      "weighted_hit_rate": hit / (hit + miss) if hit + miss else None}
    summary = {"by_arm": by_arm, "paired": paired, "gate": gate, "V2_pass": all(gate.values()), "cache": cache}
    (HERE / "results.json").write_text(json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if sys.argv[1] == "prepare_review":
        prepare_review()
    elif sys.argv[1] == "score":
        score()
    else:
        raise SystemExit("prepare_review|score")
