"""Create E2 bank: all actual E1-P findings plus 22 authentic-W stress findings."""

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
E1 = HERE.parent / "evidence_packet"
SOURCES = {x["case_id"]: x for x in json.loads((E1 / "BANK.json").read_text())}
OUTCOMES = json.loads((E1 / "outcomes.json").read_text())
REVIEWS = json.loads((E1 / "REVIEWS.json").read_text())


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


bank = []
for source in json.loads((E1 / "BANK.json").read_text()):
    cid = source["case_id"]
    output = OUTCOMES[cid + ":P"]
    assert output["error"] is None
    for i, item in enumerate(output["output"]["findings"]):
        reviewed = REVIEWS[cid + ":P"]["findings"][i]
        assert item["statement"] == reviewed["statement"]
        assert reviewed["source_supported"]
        bank.append({"case_id": f"A_{cid}_{i}", "origin": "all_actual_E1_P_findings",
                     "source_case": cid, "qid": source["qid"],
                     "raw_question": source["raw_question"],
                     "active_gap": source["active_gap"],
                     "relevant_committed_claims": source["relevant_committed_claims"],
                     "observation": source["observation"],
                     "finding": item["statement"],
                     "review": {"source_supported": True,
                                "claim_eligible": reviewed["gap_relevant_and_new"],
                                "stress_type": None,
                                "reason": "E1 single-reviewer finding-level audit: complete source support; Gap eligibility recorded separately."}})

# Each candidate statement is new, but every observation byte is inherited from
# the real historical E1 bank. Negative statements test relations not established
# by the observed packet; positive statements require metadata or two real spans.
STRESS = [
    ("S1_01", "F3_P05_W7", "S1", "Oliver Mtukudzi had 67 albums at the time of his 2016 Forbes Africa interview.", False, "The retrospective's '67 albums later' is not dated to the 2016 interview."),
    ("S1_02", "F3_P10_W9", "S1", "A May 2016 Forbes Africa feature reported that Oliver Mtukudzi had 65 albums.", False, "The observed Forbes Africa feature is dated May 2017."),
    ("S1_03", "F3_P07_W17", "S1", "In the 2016 NPFL table Enugu Rangers finished eighth with 58 points and +8 goal difference.", False, "The observed table title identifies 2014, not 2016."),
    ("S1_04", "F1_T1_546", "S1", "Ding Junhui beat Ma Hailong 4-3 in his 2024 English Open opener.", False, "The observed report is dated 2023 and describes that year's opener."),
    ("S2_01", "F3_P03_W21", "S2", "Peter O'Toole played Policeman 1 in The Constant Gardener in 2005.", False, "The document is Peter Nzioki's filmography, not Peter O'Toole's."),
    ("S2_02", "F1_T3_1094", "S2", "AC Milan's 1908 split formed Paris Saint-Germain.", False, "The text says that split formed F.C. Internazionale."),
    ("S2_03", "F1_T2_435", "S2", "Miriam Makeba died at age 66.", False, "The observed source states age 76."),
    ("S2_04", "F1_T1_1034", "S2", "Nita Ambani is the model and singer described in the article.", False, "The article names Heart Evangelista; Nita Ambani is a comparison."),
    ("S3_01", "F1_T3_546", "S3", "After beating Ma Hailong 4-3, Ding Junhui beat Mark Allen 4-0 in his next match.", False, "The article's separate Mark Allen 4-0 result is not Ding's next match."),
    ("S3_02", "F1_T3_546", "S3", "After beating Ma Hailong, Ding Junhui defeated Andrew Pagett 4-0.", False, "The separate 4-0 Andrew Pagett result belongs to Ronnie O'Sullivan."),
    ("S3_03", "F1_T3_546", "S3", "Ding Junhui lost his next match 4-3 to John Higgins after beating Ma Hailong.", False, "The 4-3 Higgins result is against Marco Fu, not Ding's later match."),
    ("S3_04", "F1_T3_546", "S3", "Ma Hailong then played Marco Fu after losing to Ding Junhui.", False, "The article separately reports Higgins versus Fu, with no Ma-to-Fu sequence."),
    ("S4_01", "F1_T3_546", "S4", "Ding Junhui beat Ma Hailong 4-3 and then beat Ronnie O'Sullivan 4-0.", False, "The first conjunct is observed; the second is absent."),
    ("S4_02", "F1_T1_177", "S4", "Enugu Rangers signed 13 players ahead of 2022/23 and had +8 goal difference in the 2014 table.", False, "This signing article does not contain the 2014 league table."),
    ("S4_03", "F1_T1_580", "S4", "In Not a Great Bet Gretchen returns for her brother's baby and Jimmy is convinced by her friends to take her on a date.", False, "The first plot clue is observed; the season-one date clue is not."),
    ("S4_04", "F1_T1_517", "S4", "Peter King Nzioki was born in 1978 and was credited as Policeman 1 in The Constant Gardener.", False, "The biography excerpt gives the birth and film appearance, not the exact credited role."),
    ("S5_01", "F3_P07_W17", "S5", "The 2014 NPFL table puts Enugu Rangers eighth with 58 points and +8 goal difference.", True, "Title supplies 2014; the W row supplies position, points and goal difference."),
    ("S5_02", "F3_P03_W21", "S5", "Peter King Nzioki was credited as Policeman 1 in The Constant Gardener (2005).", True, "Document title supplies actor identity; the filmography row supplies film and role."),
    ("S5_03", "F3_P10_W9", "S5", "The May 2017 Forbes Africa feature reports Oliver Mtukudzi had 65 albums.", True, "Forbes Africa URL supplies source identity and W supplies date, artist and count."),
    ("S6_01", "F1_T1_517", "S6", "Peter King Nzioki, popularly known as Peter King, was born in 1978 and had a father who served in the Kenyan Army.", True, "Identity/birth and paternal work occur in distinct biography spans."),
    ("S6_02", "F1_T1_177", "S6", "Enugu-based Rangers signed 13 new players ahead of the 2022/23 NPFL season.", True, "Signing count/season and Enugu location occur in separate article spans."),
    ("S6_03", "F1_T3_435", "S6", "Oliver Mtukudzi died at age 66 and had more than 60 albums in his career.", True, "Death age and album abundance occur in distinct article spans."),
]

for cid, source_id, kind, finding, support, reason in STRESS:
    source = SOURCES[source_id]
    bank.append({"case_id": cid, "origin": "genuine_W_stress",
                 "source_case": source_id, "qid": source["qid"],
                 "raw_question": source["raw_question"],
                 "active_gap": source["active_gap"],
                 "relevant_committed_claims": source["relevant_committed_claims"],
                 "observation": source["observation"], "finding": finding,
                 "review": {"source_supported": support, "claim_eligible": support,
                            "stress_type": kind, "reason": reason}})

assert len([x for x in bank if x["origin"] == "all_actual_E1_P_findings"]) == 46
assert len(STRESS) == 22 and Counter(x[2] for x in STRESS) == {
    "S1": 4, "S2": 4, "S3": 4, "S4": 4, "S5": 3, "S6": 3}
assert len(bank) == 68 and len({x["case_id"] for x in bank}) == 68
assert all(x["observation"] == SOURCES[x["source_case"]]["observation"] for x in bank)
(HERE / "BANK.json").write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n")
print("E2", len(bank), "A", 46, "stress", len(STRESS), "qids", len({x["qid"] for x in bank}))
