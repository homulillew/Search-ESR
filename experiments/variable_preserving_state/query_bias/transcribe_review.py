"""Transcribe Codex's arm-masked, prefix-only review of 48 V2 queries."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKETS = json.loads((HERE / "REVIEW_PACKETS.json").read_text())

# These strings do not occur as bindings in the question, current observed W,
# or explicit provisional H for the corresponding packet. Range-year searches
# (2011/2013/2014) are treated as exploratory slices of the supplied range,
# not an assertion that a particular year is the answer.
LEAKS = {
    1: ["Jazz Jackrabbit 2"],
    2: ["You're the Worst"],
    3: ["Jazz Jackrabbit 2"],
    4: ["Ronnie O'Sullivan"],
    7: ["Jazz Jackrabbit 2"],
    8: ["David Grace", "Zak Surety", "John Higgins"],
    10: ["Oliver Mtukudzi"],
    11: ["Paris FC", "Stade Saint-Germain", "Olympique Lillois", "SC Fives"],
    12: ["Jazz Jackrabbit"],
    13: ["You're the Worst", "Insouciance"],
    14: ["Jazz Jackrabbit 2"],
    17: ["Paris FC"],
    18: ["Rangers International"],
    26: ["Oliver Mtukudzi"],
    29: ["You're the Worst"],
    30: ["Paris FC", "Stade Saint-Germain"],
    32: ["John Higgins"],
    34: ["You're the Worst"],
    39: ["Jazz Jackrabbit"],
    43: ["Michael White", "Liam Highfield", "Ronnie O'Sullivan"],
    44: ["You're the Worst"],
    46: ["Nana Ama McBrown"],
    47: ["Oliver Mtukudzi"],
}

OFF_GAP = {10, 26, 46, 47}
OFF_SOURCE = {46}
NONCONFIRMING_LEAKS = {18}  # Unsupported team-name variant, but the query seeks the missing table.


def review(idx, packet):
    assert packet["error"] is None
    leak = LEAKS.get(idx, [])
    assert all(s.lower() in packet["query"].lower() for s in leak)
    return {
        "gap_alignment": idx not in OFF_GAP,
        "source_type_alignment": idx not in OFF_SOURCE,
        "unsupported_binding_leakage": bool(leak),
        "confirmation_bias": bool(leak) and idx not in NONCONFIRMING_LEAKS,
        "unknown_targeting": idx not in OFF_GAP,
        "leaking_values": leak,
        "specificity": "high" if leak else "medium",
        "reason": ("Query includes at least one exact entity, title, opponent, or club relation absent from the current question/W/H; packet 18 remains a table-discovery query despite its unobserved team-name variant."
                   if leak else "Query uses the supplied range, observed entities and/or provisional H to seek the unresolved relation without an extra exact answer value."),
    }


if __name__ == "__main__":
    assert len(PACKETS) == 48 and not any(p["error"] for p in PACKETS)
    labels = {p["review_id"]: review(i, p) for i, p in enumerate(PACKETS)}
    (HERE / "REVIEWS.json").write_text(json.dumps(labels, ensure_ascii=False, indent=2) + "\n")
