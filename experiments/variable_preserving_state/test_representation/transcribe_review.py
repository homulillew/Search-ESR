"""Transcribe Codex's arm-masked, prefix-only V1 semantic review.

Packet indexes refer to REVIEW_PACKETS.json order. The decisions and exceptional
bindings below were made by reading all 90 packet outputs and their visible W.
This helper makes the complete per-field JSON labels reproducible; it does not
call a model or inspect a future trajectory.
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKETS = json.loads((HERE / "REVIEW_PACKETS.json").read_text())

# Item-level semantic exceptions to a relevant, anchored, testable default.
NONMINIMAL = {12: [0], 14: [1], 36: [0], 51: [0], 60: [0]}
OFF_GAP = {31: [1]}
UNSUPPORTED_TEST = {
    47: {0: "W2 calls Albino Frog a publisher, not a developer; the joint developer/publisher binding exceeds the observation."},
    75: {0: "W1 names Dust as Dodrill's own game but does not identify it as Game B."},
}
PARTIAL_COVERAGE = {14: [True, True, False], 34: [True, True, False],
                    42: [True, True, False]}
# A claim that asserts a candidate satisfies a still-unverified clue is an
# unsupported relational binding. The one fully observed background claim is
# the 2005 film/director statement in packet 64, item 2.
SUPPORTED_CLAIMS = {64: [1]}
# Unknown slots whose *exact value* was filled by a declarative output.
BOUND_UNKNOWN = {
    0: ["game_b_title"], 2: ["exact_character_credit"],
    7: ["standings_season"], 10: ["program_title"],
    21: ["later_4_3_opponent", "later_4_0_opponent", "following_loss_opponent"],
    30: ["forbes_feature_album_count"], 43: ["split_founder_relation", "opponent_identity_iterations"],
    44: [], 59: ["exact_character_credit"], 64: ["exact_character_credit"],
    69: [], 74: ["later_4_3_opponent", "later_4_0_opponent", "following_loss_opponent"],
    75: ["game_b_title"], 80: [], 81: [],
    86: ["player_x", "event", "earlier_winner"], 87: [],
}


def candidate_name(packet):
    hyp = packet["working_hypothesis"]
    return hyp["binding"].split(" = ", 1)[1] if hyp else None


def basis_for_known(packet, entry):
    if isinstance(entry, dict):
        return entry["basis_type"]
    value = entry.lower()
    hyp = candidate_name(packet)
    if hyp and hyp.lower() in value and ("candidate" in value or value.startswith("h1 =")):
        return "working_hypothesis"
    if value.startswith(("source ", "visible_evidence", "w1_", "observed", "evidence =")):
        return "evidence"
    # Actual observed details (titles, dates, credit lists) are checked against
    # packet W; their presence is independently reviewed in REVIEW_NOTES.md.
    if any(k in value for k in ("the constant gardener", "fernando meirelles", "dust: an elysian tail",
                               "canal 13", "1992 on dos", "sean michael puckett", "rocco caputo",
                               "terri l. puckett", "albino frog", "gretchen goes home",
                               "ma hailong", "animation light-table", "more than 60 as of")):
        return "evidence"
    return "question"


def review_packet(idx, packet):
    error = packet["error"]
    claims = bool(packet["items"] and "claim_id" in packet["items"][0])
    items = []
    for j, item in enumerate(packet["items"]):
        bindings = []
        if claims:
            supported = j in SUPPORTED_CLAIMS.get(idx, [])
            bindings.append({"value": item["statement"], "basis": "evidence" if supported else "none",
                             "reason": "Visible W supports this background film fact." if supported else
                             "This asserts that a provisional or unidentified candidate satisfies an unresolved clue; the prefix does not establish the relation."})
        else:
            for known in item["known"]:
                value = known if isinstance(known, str) else known["value"]
                basis = basis_for_known(packet, known)
                if idx == 47 and j == 0 and "developer/publisher" in value:
                    basis = "none"
                bindings.append({"value": value, "basis": basis,
                                 "reason": "Visible question, W, or explicitly provisional H supports the value at this scope." if basis != "none" else
                                 UNSUPPORTED_TEST[idx][j]})
            if idx == 75 and j == 0:
                bindings.append({"value": "Game B = Dust: An Elysian Tail", "basis": "none",
                                 "reason": UNSUPPORTED_TEST[idx][j]})
        items.append({"gap_relevant": j not in OFF_GAP.get(idx, []),
                      "task_anchored": j not in OFF_GAP.get(idx, []),
                      "testable": True,
                      "minimal": j not in NONMINIMAL.get(idx, []),
                      "bindings": bindings,
                      "reason": "Prefix-only semantic review of the assertion or test, including its known fields and condition."})
    if error:
        coverage = [False] * len(packet["coverage_requirements"])
        preserved = [False] * len(packet["review_unknown_slots"])
        reason = f"Provider/output interruption {error}; zero coverage and unknown credit under the frozen rubric."
    elif claims:
        coverage = [False] * len(packet["coverage_requirements"])
        preserved = [s not in BOUND_UNKNOWN.get(idx, []) for s in packet["review_unknown_slots"]]
        reason = "Declarative claim(s) do not provide a supported test path for the missing relation; exact unknown values are scored separately."
    else:
        coverage = PARTIAL_COVERAGE.get(idx, [True] * len(packet["coverage_requirements"]))
        preserved = [s not in BOUND_UNKNOWN.get(idx, []) for s in packet["review_unknown_slots"]]
        reason = "Test conditions remain conditional and specify inspectable missing relations; noted exceptions are recorded at field level."
    return {"items": items, "coverage": coverage, "unknown_preserved": preserved, "reason": reason}


if __name__ == "__main__":
    assert len(PACKETS) == 90
    assert {i for i, p in enumerate(PACKETS) if p["error"]} == {9, 76, 77}
    for idx in (47, 75):
        assert PACKETS[idx]["items"]
    reviews = {p["review_id"]: review_packet(i, p) for i, p in enumerate(PACKETS)}
    (HERE / "REVIEWS.json").write_text(json.dumps(reviews, ensure_ascii=False, indent=2) + "\n")
