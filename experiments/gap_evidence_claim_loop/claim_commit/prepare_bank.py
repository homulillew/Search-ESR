"""Use all F1 C outputs plus frozen negative verifier challenges."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
F1 = HERE.parent / "finding_extraction"
CASES = {c["case_id"]: c for c in json.loads((F1 / "BANK.json").read_text())}
OUTCOMES = json.loads((F1 / "outcomes.json").read_text())
REVIEWS = json.loads((F1 / "REVIEWS.json").read_text())
MAPPING = json.loads((F1 / "PRIVATE_MAPPING.json").read_text())
REVIEW_BY_CELL = {cell: REVIEWS[rid] for rid, cell in MAPPING.items()}

# Stress proposals are reviewer-authored against real historical W.  The
# seventh field records the exact unsupported relation and is frozen before
# verifier requests.  Same real W may appear in multiple controlled packets.
STRESS = [
    ("V1", "T2_546", "John Higgins was Ding Junhui's next 2023 English Open opponent after Ma Hailong.", "Higgins beat Marco Fu elsewhere; Ding's next opponent is not given."),
    ("V1", "T2_387", "Dust: An Elysian Tail is the game for which Dean Dodrill animated the introduction and ending.", "The interview names Dust as his own game, not the required Game B animation credit."),
    ("V1", "T4_324", "Annie Duke won the specified earlier poker event two years before player X.", "The 2022 page says she hosted a different virtual tournament."),
    ("V2", "T3_435", "Oliver Mtukudzi released exactly 65 albums, and the May Forbes Africa feature reported that number.", "W says more than 60 albums; neither exact 65 nor Forbes attribution appears."),
    ("V2", "T3_580", "The series of Not a Great Bet also satisfies the specified season-one date and season-three roommate clues.", "W provides only the season-four episode."),
    ("V2", "T3_177", "Rangers finished in the question's tied-points season with a goal difference of +8.", "W's 2022/23 signing report does not establish the target historical table."),
    ("V3", "T3_546", "After beating Ma Hailong 4–3, Ding won the next match 4–3, then 4–0, then lost to an opponent with over 400 centuries.", "W gives the opening win only; other player results are incidental."),
    ("V3", "T2_580", "Not a Great Bet is the season-one date scene that precedes Gretchen's season-four family visit.", "W explicitly dates Not a Great Bet to season four and says nothing about the season-one scene."),
    ("V4", "T3_1094", "Paris Saint-Germain was formed by AC Milan's 1908 foreign-player split.", "W says that split formed F.C. Internazionale, not PSG."),
    ("V4", "T2_435", "Miriam Makeba died at age 66.", "W explicitly states age 76."),
    ("V4", "T3_1034", "Nita Ambani is the model and singer profiled in this article.", "Nita Ambani is only a comparison; Heart Evangelista is the subject."),
    ("V4", "T3_517", "Peter King played a policeman in The Constant Gardener.", "W says only minor role and never names the exact character."),
    ("V5", "T7_186", "The earlier 1993 Galacta record is definitively false because the 1992 full-title page describes the same release.", "The shortened-title/full-title identity equivalence is not established by this W."),
    ("V5", "T5_186", "Albino Frog Software developed Galacta: The Battle for Saturn.", "W labels Albino Frog as publisher; developer relation is absent."),
    ("V5", "T5_311", "The Adventures of Hijitus first aired in the early 1990s.", "W says first aired in 1967, though later broadcasts continued."),
]
assert len(STRESS) == 15

bank = []
for c in json.loads((F1 / "BANK.json").read_text()):
    cell = c["case_id"] + ":C"
    findings = OUTCOMES[cell]["output"]["findings"]
    reviews = REVIEW_BY_CELL[cell]
    assert len(findings) == len(reviews)
    for j, (finding, review) in enumerate(zip(findings, reviews)):
        good = (review["evidence_grounded"] and review["gap_relevant"] and
                review["world_fact"] and not review["overreach"] and
                not review["duplicate_existing"])
        bank.append({"packet_id": f"A_{c['case_id']}_{j}", "part": "A", "qid": c["qid"],
                     "source_case": c["case_id"], "source_checkpoint": c["source_checkpoint"],
                     "active_gap": c["active_gap"], "finding": finding,
                     "new_observation": c["new_observation"],
                     "existing_claims": c["existing_claims"],
                     "review": {"expected_supported": good,
                                "reason": "F1 single-reviewer evidence/gap/novelty assessment; all C Findings included."}})
for i, (kind, cid, statement, reason) in enumerate(STRESS):
    c = CASES[cid]
    existing = c["existing_claims"]
    if kind == "V5" and cid == "T7_186":
        # Real historical previous_state C1, with the earlier W1 evidence.
        existing = [{"claim_id": "C1", "statement": "Galacta was released in 1993.",
                     "evidence_refs": ["W1"], "version": 1}]
    bank.append({"packet_id": f"B_{i:02d}_{kind}_{cid}", "part": "B", "stress_type": kind,
                 "qid": c["qid"], "source_case": cid,
                 "source_checkpoint": c["source_checkpoint"],
                 "active_gap": c["active_gap"],
                 "finding": {"statement": statement, "evidence_refs": [c["new_observation"]["ref"]]},
                 "new_observation": c["new_observation"], "existing_claims": existing,
                 "review": {"expected_supported": False, "reason": reason}})
assert len([p for p in bank if p["part"] == "A"]) == 38
assert len(bank) == 53 and len({p["packet_id"] for p in bank}) == 53
(HERE / "BANK.json").write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n")
