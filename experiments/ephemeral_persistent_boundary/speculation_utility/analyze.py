"""Arm-masked S1 Search packets and paired descriptive metrics."""

import hashlib
import json
import statistics
import sys
from pathlib import Path

from run import BANK, CASES

HERE = Path(__file__).resolve().parent
FLAGS = ("suitable_source", "useful_evidence", "direct_unknown_resolution", "no_gain")


def events_index():
    events = [json.loads(s) for s in (HERE / "events.jsonl").read_text().splitlines()]
    results = {e["search_id"]: e for e in events if e["kind"] == "search_result"}
    errors = {e["search_id"]: e for e in events if e["kind"] == "search_error"}
    expected = {b["search_id"] for b in BANK}
    if set(results) & set(errors) or set(results) | set(errors) != expected:
        raise ValueError("incomplete or duplicate S1 cells")
    return events, results, errors


def review_id(search_id):
    return "R" + hashlib.sha256(("S1 blind retrieval review:" + search_id).encode()).hexdigest()[:14]


def prepare_review():
    if (HERE / "REVIEW_PACKETS.json").exists():
        raise FileExistsError("REVIEW_PACKETS.json")
    _, results, errors = events_index()
    mapping = {}
    packets = []
    for b in BANK:
        sid = b["search_id"]
        c = CASES[b["case_id"]]
        rid = review_id(sid)
        mapping[rid] = sid
        speculative = b["frozen_leaking_values"] if b["variant"] == "S" else []
        packets.append({"review_id": rid, "case_id": b["case_id"], "qid": b["qid"],
                        "raw_question": c["raw_question"], "working_hypothesis": c["working_hypothesis"],
                        "semantic_gap": c["semantic_gap"], "test_card": c["test_card_state"],
                        "expected_source_type": c["expected_source_type"], "query": b["query"],
                        "speculative_values_in_query": speculative,
                        "results": results.get(sid, {}).get("result", {}).get("results", []),
                        "error": errors.get(sid, {}).get("error_type")})
    packets.sort(key=lambda p: hashlib.sha256(p["review_id"].encode()).hexdigest())
    (HERE / "REVIEW_PACKETS.json").write_text(json.dumps(packets, ensure_ascii=False, indent=2) + "\n")
    (HERE / "PRIVATE_MAPPING.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n")


def validate_review(packet, review):
    expected = set(FLAGS) | {"speculative_value_support", "candidate_breadth", "supporting_ranks", "reason"}
    if set(review) != expected or any(not isinstance(review[k], bool) for k in FLAGS):
        raise ValueError("review schema " + packet["review_id"])
    if review["speculative_value_support"] not in (True, False, None):
        raise ValueError("speculation review " + packet["review_id"])
    if bool(packet["speculative_values_in_query"]) != (review["speculative_value_support"] is not None):
        raise ValueError("speculation eligibility " + packet["review_id"])
    if review["candidate_breadth"] not in ("one_candidate", "multiple_directions", "unclear"):
        raise ValueError("breadth " + packet["review_id"])
    if not isinstance(review["supporting_ranks"], list) or any(type(x) is not int or x not in range(1, 6) for x in review["supporting_ranks"]):
        raise ValueError("ranks " + packet["review_id"])
    if not isinstance(review["reason"], str) or not review["reason"].strip():
        raise ValueError("reason " + packet["review_id"])
    if review["direct_unknown_resolution"] and not review["useful_evidence"]:
        raise ValueError("resolution must be useful " + packet["review_id"])
    if review["no_gain"] != (not review["suitable_source"] and not review["useful_evidence"]):
        raise ValueError("NoGain definition " + packet["review_id"])
    if packet["error"] and (any(review[k] for k in ("suitable_source", "useful_evidence", "direct_unknown_resolution")) or review["supporting_ranks"]):
        raise ValueError("failed Search positive credit " + packet["review_id"])


def score():
    events, results, errors = events_index()
    packets = {p["review_id"]: p for p in json.loads((HERE / "REVIEW_PACKETS.json").read_text())}
    mapping = json.loads((HERE / "PRIVATE_MAPPING.json").read_text())
    reviews = json.loads((HERE / "REVIEWS.json").read_text())
    if set(packets) != set(mapping) or set(reviews) != set(mapping):
        raise ValueError("review mapping mismatch")
    by_sid = {b["search_id"]: b for b in BANK}
    rows = []
    for rid, sid in mapping.items():
        p, review, b = packets[rid], reviews[rid], by_sid[sid]
        validate_review(p, review)
        hits = results.get(sid, {}).get("audit", {}).get("hits", [])
        rows.append({"review_id": rid, "search_id": sid, "source_cell": b["source_cell"],
                     "case_id": b["case_id"], "qid": b["qid"], "v2_arm": b["v2_arm"],
                     "variant": b["variant"], "query": b["query"], "error": errors.get(sid, {}).get("error_type"),
                     "docids": [h["docid"] for h in hits],
                     "latency_seconds": results.get(sid, errors.get(sid, {})).get("latency_seconds"),
                     "review": review})
    originals = [r for r in rows if r["variant"] == "S"]
    by_v2_arm = {}
    for arm in ("Q0", "Q1", "Q2"):
        group = [r for r in originals if r["v2_arm"] == arm]
        by_v2_arm[arm] = {"n": len(group), "errors": sum(r["error"] is not None for r in group),
                          **{k: sum(r["review"][k] for r in group) / len(group) for k in FLAGS}}
    pairs = []
    for b in BANK:
        if b["variant"] != "D":
            continue
        s = next(r for r in rows if r["search_id"] == b["source_cell"] + ":S")
        d = next(r for r in rows if r["search_id"] == b["search_id"])
        pairs.append({"source_cell": b["source_cell"], "case_id": b["case_id"], "qid": b["qid"],
                      "speculative_values": b["frozen_leaking_values"],
                      "S": {k: s["review"][k] for k in FLAGS},
                      "D": {k: d["review"][k] for k in FLAGS},
                      "S_speculative_value_support": s["review"]["speculative_value_support"],
                      "top5_docid_overlap": len(set(s["docids"]) & set(d["docids"])),
                      "S_docids": s["docids"], "D_docids": d["docids"]})
    paired = {}
    for k in FLAGS:
        higher_S = sum(p["S"][k] and not p["D"][k] for p in pairs)
        higher_D = sum(p["D"][k] and not p["S"][k] for p in pairs)
        paired[k] = {"S_true_D_false": higher_S, "D_true_S_false": higher_D,
                     "equal": len(pairs) - higher_S - higher_D}
    summary = {"n_original": len(originals), "n_pairs": len(pairs), "by_v2_arm": by_v2_arm,
               "paired": paired,
               "speculative_value_supported": sum(p["S_speculative_value_support"] for p in pairs),
               "mean_top5_docid_overlap": statistics.mean(p["top5_docid_overlap"] for p in pairs),
               "search_errors": sum(r["error"] is not None for r in rows)}
    (HERE / "results.json").write_text(json.dumps({"summary": summary, "rows": rows, "pairs": pairs}, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if sys.argv[1] == "prepare_review":
        prepare_review()
    elif sys.argv[1] == "score":
        score()
    else:
        raise SystemExit("prepare_review|score")
