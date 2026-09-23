"""Validate per-call S0 judgments and aggregate without altering historical R1."""

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    cards = json.loads((HERE / "review_cards.json").read_text())
    manual = json.loads((HERE / "manual_codes.json").read_text())
    expected = {f"{c['cell']}:{c['arm']}:{c['call_index']}" for c in cards}
    if expected != set(manual):
        raise ValueError({"missing": sorted(expected - set(manual)), "extra": sorted(set(manual) - expected)})
    scores = []
    for card in cards:
        key = f"{card['cell']}:{card['arm']}:{card['call_index']}"
        gap, repeat, role, reason = manual[key]
        if gap not in {"yes", "partial", "no", "unclear"} or not isinstance(repeat, bool) or \
           role not in {"gap_test", "local_fact_repeat", "unrelated", "not_candidate_inspection", "unclear"} or not reason:
            raise ValueError(key)
        scores.append({"cell": card["cell"], "arm": card["arm"], "call_index": card["call_index"],
                       "tool_name": card["tool_name"], "arguments": card["arguments"],
                       "addresses_verification_gap": gap,
                       "repeats_already_supported_fact": repeat,
                       "candidate_inspection_role": role, "reason": reason})
    (HERE / "action_gap_scores.json").write_text(json.dumps(scores, ensure_ascii=False, indent=2) + "\n")
    aggregate = {}
    for arm in ("H0", "H1"):
        group = [s for s in scores if s["arm"] == arm]
        roles = Counter(s["candidate_inspection_role"] for s in group)
        aggregate[arm] = {"calls": len(group), "gap_yes": sum(s["addresses_verification_gap"] == "yes" for s in group),
                          "gap_yes_or_partial": sum(s["addresses_verification_gap"] in {"yes", "partial"} for s in group),
                          "repeat_supported_fact": sum(s["repeats_already_supported_fact"] for s in group),
                          "candidate_inspection_roles": dict(roles)}
    focus = {}
    for cell in ("546:25", "1094:45", "1094:53", "1094:69"):
        focus[cell] = {arm: [{"call_index": s["call_index"], "gap": s["addresses_verification_gap"],
                              "repeat": s["repeats_already_supported_fact"],
                              "candidate_role": s["candidate_inspection_role"]}
                             for s in scores if s["cell"] == cell and s["arm"] == arm]
                       for arm in ("H0", "H1")}
    output = {"aggregate": aggregate, "focus": focus,
              "note": "Post-hoc single-reviewer judgments of one-step tool arguments only. Calls cluster within 13 checkpoints. No tool result, future trajectory, gold or answer used. R1 preregistered gate remains failed."}
    (HERE / "mechanical_summary.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(aggregate, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
