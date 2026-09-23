"""S1 paired target accounting and prefix-only action review cards."""

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R1 = ROOT / "experiments/research_state_qualification/qualification_upper_bound"


def read(path):
    return [json.loads(line) for line in path.open()]


def main():
    annotations = {(a["qid"], a["seq"]): a for a in json.loads((R1 / "ANNOTATIONS.json").read_text())["rows"]}
    projections = {(a["qid"], a["seq"]): a for a in json.loads((HERE / "PROJECTION_ANNOTATIONS.json").read_text())["rows"]}
    packets = {(a["qid"], a["seq"]): a for a in json.loads((R1 / "review_packets.json").read_text())}
    cases = [(a["qid"], a["seq"]) for a in json.loads((R1 / "SELECTION.json").read_text())["cells"]]
    events = read(HERE / "events.jsonl")
    score_path = HERE / "semantic_scores.json"
    scores = json.loads(score_path.read_text()) if score_path.exists() else {}
    rows, cards = [], []
    for q, seq in cases:
        a, p, packet = annotations[(q, seq)], projections[(q, seq)], packets[(q, seq)]
        windows = {d["preview_ref"]: d["doc_ref"] for d in packet["observed_documents"]}
        for arm in ("B", "C"):
            cell = f"{q}:{seq}:{arm}"
            e = next((e for e in events if e["kind"] == "actor_response" and e["cell"] == cell), None)
            err = next((e for e in events if e["kind"] == "actor_error" and e["cell"] == cell), None)
            valid = bool(e and e["validation"] == "valid")
            calls = (e.get("parsed_calls") or []) if valid else []
            details = []
            for index, c in enumerate(calls, 1):
                name, arguments = c["name"], c["arguments"]
                doc = arguments.get("doc_ref") if name == "find" else windows.get(arguments.get("window_ref")) if name == "open" else None
                key = f"{cell}:{index}"
                score = scores.get(key)
                if score and (score.get("addresses_verification_gap") not in {"yes", "partial", "no", "unclear"} or
                              not isinstance(score.get("repeats_already_supported_fact"), bool) or not score.get("reason")):
                    raise ValueError(f"Bad semantic score {key}")
                details.append({"id": key, "name": name, "arguments": arguments, "doc_ref": doc,
                                "inspects_unpromoted_candidate": a["status"] == "hypothesis_only" and doc == a["candidate_target"],
                                "uses_promoted_target": a["status"] == "inspectable" and doc == p["promoted_target"],
                                "addresses_verification_gap": score.get("addresses_verification_gap") if score else None,
                                "repeats_already_supported_fact": score.get("repeats_already_supported_fact") if score else None})
                cards.append({"id": key, "cell": cell, "qid": q, "seq": seq, "arm": arm, "call_index": index,
                              "original_question": packet["original_question"],
                              "prefix_packet": f"{q}:{seq} in R1 review_packets.json",
                              "current_verification_gap": p["current_verification_gap"],
                              "required_source_type": p["required_source_type"],
                              "visible_supported_part": a["supported_part"],
                              "missing_prerequisite": a["missing_prerequisite"],
                              "status_private": a["status"], "candidate_private": a["candidate_target"],
                              "promoted_target": p["promoted_target"],
                              "tool_name": name, "arguments": arguments, "doc_ref": doc,
                              "review_boundary": "Use only current prefix, frozen projection, and this call; no result/future/gold."})
            rows.append({"cell": cell, "qid": q, "seq": seq, "arm": arm,
                         "status_private": a["status"], "candidate_private": a["candidate_target"],
                         "promoted_target": p["promoted_target"],
                         "response": bool(e), "api_error": err.get("error_type") if err else None,
                         "validation": e.get("validation") if e else None,
                         "finish_reason": e.get("raw_finish_reason") if e else None,
                         "calls": details, "first_call": details[0]["name"] if details else None,
                         "mixed_batch": len({d["name"] for d in details}) > 1,
                         "unpromoted_candidate_inspected": any(d["inspects_unpromoted_candidate"] for d in details),
                         "unpromoted_candidate_first": bool(details and details[0]["inspects_unpromoted_candidate"]),
                         "promoted_target_utilized": any(d["uses_promoted_target"] for d in details),
                         "promoted_target_first": bool(details and details[0]["uses_promoted_target"]),
                         "direct_gap_cell": any(d["addresses_verification_gap"] == "yes" for d in details),
                         "any_gap_cell": any(d["addresses_verification_gap"] in ("yes", "partial") for d in details),
                         "first_call_gap": details[0]["addresses_verification_gap"] if details else None,
                         "semantic_reviewed_calls": sum(d["addresses_verification_gap"] is not None for d in details)})
    if set(scores) - {c["id"] for c in cards}:
        raise ValueError("Unknown semantic score id")
    (HERE / "semantic_review_cards.json").write_text(json.dumps(cards, ensure_ascii=False, indent=2) + "\n")
    aggregate = {}
    for arm in ("B", "C"):
        group = [r for r in rows if r["arm"] == arm]
        actions = Counter(c["name"] for r in group for c in r["calls"])
        aggregate[arm] = {"cells": len(group), "responses": sum(r["response"] for r in group),
                          "valid": sum(r["validation"] == "valid" for r in group),
                          "api_errors": sum(r["api_error"] is not None for r in group),
                          "actions": dict(actions), "mixed_batches": sum(r["mixed_batch"] for r in group),
                          "hypothesis_cells": sum(r["status_private"] == "hypothesis_only" for r in group),
                          "unpromoted_inspection": sum(r["unpromoted_candidate_inspected"] for r in group),
                          "unpromoted_first": sum(r["unpromoted_candidate_first"] for r in group),
                          "inspectable_cells": sum(r["status_private"] == "inspectable" for r in group),
                          "promoted_utilization": sum(r["promoted_target_utilized"] for r in group),
                          "promoted_first": sum(r["promoted_target_first"] for r in group),
                          "semantic_reviewed_calls": sum(r["semantic_reviewed_calls"] for r in group),
                          "direct_gap_cells": sum(r["direct_gap_cell"] for r in group),
                          "any_gap_cells": sum(r["any_gap_cell"] for r in group),
                          "gap_yes_calls": sum(c["addresses_verification_gap"] == "yes" for r in group for c in r["calls"]),
                          "gap_yes_or_partial_calls": sum(c["addresses_verification_gap"] in ("yes", "partial") for r in group for c in r["calls"]),
                          "repeat_supported_fact_calls": sum(c["repeats_already_supported_fact"] is True for r in group for c in r["calls"])}
    pairs = []
    for q, seq in cases:
        b, c = (next(r for r in rows if r["qid"] == q and r["seq"] == seq and r["arm"] == arm) for arm in ("B", "C"))
        pairs.append({"cell": f"{q}:{seq}", "status": b["status_private"],
                      "B_calls": [(d["name"], d["doc_ref"]) for d in b["calls"]],
                      "C_calls": [(d["name"], d["doc_ref"]) for d in c["calls"]],
                      "B_unpromoted": b["unpromoted_candidate_inspected"], "C_unpromoted": c["unpromoted_candidate_inspected"],
                      "B_promoted": b["promoted_target_utilized"], "C_promoted": c["promoted_target_utilized"],
                      "B_direct_gap": b["direct_gap_cell"], "C_direct_gap": c["direct_gap_cell"]})
    result = {"aggregate": aggregate, "pairs": pairs, "rows": rows,
              "note": "B/C are concurrent one-step samples, no tool observations. Mechanical target rates use private R1 status and prefix W-to-D map. Semantic gap labels are single-reviewer prefix-only judgments, not source yield."}
    (HERE / "mechanical_summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"aggregate": aggregate, "pairs": pairs}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
