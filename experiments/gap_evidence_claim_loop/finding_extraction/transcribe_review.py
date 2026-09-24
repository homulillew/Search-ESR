"""Single-reviewer semantic transcription over arm-masked F1 packets.

Indices refer only to REVIEW_PACKETS.json hash order. The reviewer inspected
each statement against its exact W, semantic Gap and pre-call labels; S1/S2
gold answers and the private arm mapping were not used for these judgments.
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
packets = json.loads((HERE / "REVIEW_PACKETS.json").read_text())
assert len(packets) == 123

# Per-packet zero-based Finding indices whose true W facts do not materially
# advance this case's Active Gap.  Remaining statements are useful partial
# context or complete required facts unless marked as duplicate below.
IRRELEVANT = {
    0:[2], 3:[0,2], 5:[0,1,2], 13:[0,1,2], 14:[0,2],
    18:[], 31:[1], 34:[1,2], 35:[1,2], 37:[0,1,2],
    46:[0,2], 49:[0,1,2], 52:[2], 54:[2], 58:[2], 59:[1],
    60:[0], 62:[1,2], 64:[0,1,2], 71:[0,1], 76:[0,1,2],
    79:[0,1,2], 81:[0,1,2], 83:[2], 86:[0], 95:[0,1,2],
    99:[1,2], 100:[0,1,2], 102:[0,1,2], 104:[0,1,2],
    108:[0,1,2], 111:[1], 116:[1], 122:[0,1,2]
}
# Special cases: a location/identity fact may be true yet only identify the
# entity, without the required relation. It can be relevant partial evidence.
IRRELEVANT[37] = [1,2]
IRRELEVANT[5] = [0,1,2]

# Existing-Claim repetition, counted for B's comparator diagnostic and C's
# precision even though B was not shown the Claim.
DUPLICATE = {3:[1], 4:[0], 9:[0,1], 35:[0], 36:[0], 44:[0],
             62:[0], 111:[0]}

# Frozen required finding indices covered by the listed statement. Some
# conjunctive atoms are jointly entailed by multiple output statements; the
# reason records that they are scored at packet level rather than by exact
# sentence matching.
MATCH = {
    0:{1:[0]}, 2:{1:[0],2:[1,2]}, 6:{0:[0]}, 7:{0:[0]},
    10:{1:[0]}, 11:{0:[0]}, 14:{1:[0]}, 15:{0:[0]},
    16:{0:[0]}, 17:{0:[0]}, 18:{1:[0]}, 19:{0:[0]},
    20:{0:[0]}, 21:{1:[0],2:[1,2]}, 22:{0:[0]}, 23:{0:[0]},
    24:{0:[0],1:[1]}, 26:{1:[0]}, 27:{0:[0]},
    31:{0:[0]}, 32:{0:[0],1:[1],2:[2]}, 33:{0:[0],1:[1],2:[2]},
    34:{0:[0]}, 40:{0:[0]}, 41:{0:[0]}, 42:{0:[0]},
    43:{1:[0]}, 45:{0:[0]}, 46:{1:[0]},
    48:{0:[0],2:[2]}, 51:{0:[0],2:[2]},
    52:{0:[0],1:[1]}, 53:{0:[0]}, 54:{1:[0]}, 56:{0:[0]},
    58:{1:[0]}, 59:{0:[0]}, 60:{1:[1,2],2:[0]},
    65:{0:[0]}, 66:{2:[0]}, 69:{0:[0]}, 71:{2:[1]},
    72:{0:[0],1:[1]}, 73:{0:[0]}, 75:{0:[0],1:[1],2:[2]},
    77:{0:[0],1:[1]}, 82:{0:[0]}, 83:{1:[0]},
    84:{0:[0],1:[1],2:[2]}, 86:{1:[0]}, 87:{0:[0]},
    93:{0:[0],2:[1]}, 99:{0:[0,1,2]},
    101:{0:[0],1:[1],2:[2]}, 106:{1:[0]},
    110:{2:[0]}, 112:{1:[0]}, 114:{0:[0]},
    116:{0:[0],2:[1]}, 119:{0:[0]}, 120:{0:[0]}
}

# W1's existence or article metadata alone is not a persistent world fact.
NOT_WORLD_FACT = {102:[0]}

reviews = {}
for i, p in enumerate(packets):
    findings = p["output"]["findings"]
    assert all(j < len(findings) for j in IRRELEVANT.get(i, []))
    assert all(j < len(findings) for j in DUPLICATE.get(i, []))
    assert all(j < len(findings) for j in MATCH.get(i, {}))
    annotations = []
    for j, f in enumerate(findings):
        relevant = j not in IRRELEVANT.get(i, [])
        duplicate = j in DUPLICATE.get(i, [])
        world = j not in NOT_WORLD_FACT.get(i, [])
        matched = MATCH.get(i, {}).get(j, [])
        if matched:
            reason = "Exact W supports this fact; together with other statements in this packet where needed, it covers frozen required item(s) " + ",".join(map(str, matched)) + "."
        elif duplicate:
            reason = "Exact W supports this fact, but it repeats the prior evidence-backed C1; no new Claim is warranted in C."
        elif not relevant:
            reason = "The statement is visible in W, but its subject or relation does not advance this case's semantic Gap."
        elif not world:
            reason = "This describes the source/article itself rather than a world fact needed for the Gap."
        else:
            reason = "W supports this partial or optional Gap-relevant fact; it does not entail a complete frozen required item."
        annotations.append({"evidence_grounded": True, "gap_relevant": relevant,
                            "world_fact": world, "overreach": False,
                            "duplicate_existing": duplicate,
                            "matched_required": matched, "reason": reason})
    reviews[p["review_id"]] = annotations
assert len(reviews) == 123
(HERE / "REVIEWS.json").write_text(json.dumps(reviews, ensure_ascii=False, indent=2) + "\n")
