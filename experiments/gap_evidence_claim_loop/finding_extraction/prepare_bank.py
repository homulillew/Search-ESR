"""Freeze semantic F1 packets and single-reviewer labels before model calls."""

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
HIST = json.loads((ROOT / "experiments/research_state_v2/claim_mutation/CASES.json").read_text())
QUESTIONS = {x["qid"]: x["raw_question"] for x in json.loads((ROOT / "experiments/variable_preserving_state/test_representation/CASES.json").read_text())}
CLOSURE = {x["case_id"]: x for x in json.loads((ROOT / "experiments/research_progress_frontier/closure_probe/review_cases.json").read_text())}


def spec(kind, gap, required=(), optional=(), duplicate=(), forbidden=()):
    return {"kind": kind, "gap": gap, "required_findings": list(required),
            "optional_findings": list(optional), "duplicate_existing_facts": list(duplicate),
            "forbidden_inferences": list(forbidden)}


SPECS = {
    "T1_546": spec("E4", "Who won Ding Junhui's 2023 English Open opening decider and against whom?",
        ["Ding Junhui beat Ma Hailong 4–3 in his opening 2023 English Open match."],
        forbidden=["John Higgins or Ronnie O'Sullivan was Ding's next opponent."]),
    "T2_546": spec("E8", "Who were Ding Junhui's later opponents and results after his opening 2023 English Open win?",
        forbidden=["John Higgins, Ronnie O'Sullivan or Mark Allen was Ding's next opponent based on this W."]),
    "T3_546": spec("E2", "Which parts of Ding's required 2023 opening-win → 4–3 win → 4–0 win → loss sequence does this source establish?",
        ["Ding beat Ma Hailong 4–3 in the opening English Open match."],
        forbidden=["The source establishes the later 4–3, 4–0 and loss sequence."]),
    "T1_1094": spec("E4", "Which fixture had the 95th-minute free kick, and who took it?",
        ["Lionel Messi's last-gasp free kick gave PSG a 4–3 win over Lille in the 95th minute."],
        forbidden=["The match report establishes either club's split-founded history."]),
    "T2_1094": spec("E2", "Which match satisfies the late free-kick clue, and do its clubs satisfy the historical clues?",
        ["Messi scored a last-gasp 95th-minute free kick in PSG's 4–3 win over Lille."],
        forbidden=["The source verifies PSG/Lille split or identity evolution."]),
    "T3_1094": spec("E8", "Which of the clubs in the PSG–Lille fixture was formed through the described split?",
        forbidden=["AC Milan's 1908 split proves PSG or Lille was formed by a split."]),
    "T1_517": spec("E4", "What popular name and family background identify the 1970s-born actor?",
        ["Peter King Nzioki Mwania is popularly known as Peter King.",
         "Peter King Nzioki was born in 1978; his father served in the Kenyan Army and his mother worked at a military hospital."],
        forbidden=["Peter King played a policeman in The Constant Gardener."]),
    "T2_517": spec("E1", "In which year was actor Peter King Nzioki born?",
        ["Peter King Nzioki was born in 1978."]),
    "T3_517": spec("E3", "What exact credited role did Peter King play in The Constant Gardener?",
        forbidden=["Peter King played a policeman in The Constant Gardener."]),
    "T1_435": spec("E1", "Which musician in this source died at age 66?",
        ["Oliver Mtukudzi died at age 66."]),
    "T2_435": spec("E2", "Does Miriam Makeba meet the age-66 death clue?",
        ["Miriam Makeba died at age 76, not 66."]),
    "T3_435": spec("E2", "Does Oliver Mtukudzi meet the death-age, album and Forbes-feature clues?",
        ["Oliver Mtukudzi died at age 66."],
        optional=["The source says Oliver Mtukudzi had more than 60 albums."],
        forbidden=["The source establishes the exact Forbes Africa May album count."]),
    "T1_580": spec("E4", "Which season-four episode contains Gretchen's return for a family baby's birth?",
        ["Not a Great Bet is a season-four episode in which Gretchen returns home for her brother's baby's birth."],
        forbidden=["The source verifies the specified season-one reconciliation scene."]),
    "T2_580": spec("E8", "Which season-one episode has the Jimmy/Gretchen reconciliation date scene?",
        forbidden=["Not a Great Bet is the season-one reconciliation episode."]),
    "T3_580": spec("E2", "Which of the season-one, season-three and season-four plot clues does this episode source verify?",
        ["A season-four episode titled Not a Great Bet has Gretchen return for her brother's baby's birth."],
        forbidden=["The source verifies season-one and season-three clues too."]),
    "T1_177": spec("E4", "Which club signed 13 new players for 2022/23 and where is it based?",
        ["Enugu-based Rangers signed 13 new players ahead of the 2022/23 NPFL season."],
        forbidden=["The source establishes a 2011–2016 equal-points table goal difference."]),
    "T2_177": spec("E1", "Did the report say Rangers signed 12 or 13 players ahead of 2022/23?",
        ["Rangers signed 13 new players ahead of 2022/23."]),
    "T3_177": spec("E2", "Does Rangers meet the signing, city and historical equal-points table clues?",
        ["Enugu-based Rangers signed 13 new players ahead of 2022/23."],
        optional=["The source describes Rangers as seven-time NPFL champions."],
        forbidden=["The 2011–2016 tied-points table condition is established."]),
    "T1_1034": spec("E4", "Which person described in the article is a model and singer?",
        ["Heart Evangelista is described as a model and singer."],
        forbidden=["Nita Ambani is the target model/singer."]),
    "T2_1034": spec("E3", "Did Heart Evangelista study Business Administration and have a US-born child?",
        forbidden=["Heart's time living in the US proves a child was born there."]),
    "T3_1034": spec("E8", "Did Heart Evangelista study Business Administration and have a US-born child?",
        forbidden=["Nita Ambani is Heart Evangelista or the article's target person.",
                   "Heart's time living in the US proves a child was born there."]),
    "T1_387": spec("E4", "Did Dean Dodrill use a gaming PC with a wireless keyboard?",
        ["Dean Dodrill's workstation doubled as his gaming PC and had a wireless keyboard."],
        forbidden=["The source says his animation used 8×11-inch paper."]),
    "T2_387": spec("E1", "Did Dean Dodrill use a gaming PC?",
        ["Dean Dodrill used a workstation that doubled as his gaming PC."]),
    "T3_387": spec("E3", "Did Dean Dodrill draw Game B's intro/end animation on ordinary 8×11-inch paper?",
        forbidden=["An animation light-table proves 8×11-inch paper or Game B credit."]),
    "T4_546": spec("E6", "What was Ding Junhui's ordered 2023 English Open match sequence after his opening decider?"),
    "T4_1094": spec("E6", "Do PSG and Lille satisfy the split-founded and evolving-identity club-history clues?"),
    "T4_177": spec("E6", "What was Rangers' position and goal difference in the relevant tied-points NPFL season?"),
    "T4_517": spec("E6", "What exact role did Peter King play in The Constant Gardener?"),
    "T4_311": spec("E6", "What is the native Argentine title of the specified short educational television program?"),
    "T4_324": spec("E6", "Who won the specified poker event two years before player X?",
        forbidden=["Annie Duke's appearance in a later virtual tournament establishes the earlier event winner."]),
    "T4_776": spec("E6", "What is the official journal-record title of the requested 1940 cultural report?"),
    "T4_186": spec("E6", "What November 1992 DOS shareware game was developed by the amphibian-named company?"),
    "T5_546": spec("E7", "Which professional-start and break-count clues does Ding Junhui satisfy?",
        ["Ding Junhui turned professional in 2003.", "Ding Junhui made more than 600 century breaks.",
         "Ding Junhui made seven maximum breaks."]),
    "T5_517": spec("E7", "Which birth and parental-work clues does Peter King Nzioki satisfy?",
        ["Peter King Nzioki was born in 1978.", "His father served in the Kenyan Army.",
         "His mother worked at the military hospital."]),
    "T5_311": spec("E7", "What director, writer, network and first-airing facts does this cartoon source establish?",
        ["The Adventures of Hijitus was directed by Manuel García Ferré and names Inés Geldstein among its writers.",
         "The Adventures of Hijitus aired on Canal 13.",
         "The Adventures of Hijitus first aired in 1967, unlike the question's early-1990s clue."],
        forbidden=["The 1967 series satisfies the question's early-1990s first-run condition."]),
    "T5_186": spec("E7", "Which release, mode and credit facts does the Galacta page establish?",
        ["Galacta: The Battle for Saturn was released on DOS in November 1992.",
         "The game was a one-player shareware game.",
         "The listed credits include Sean Michael Puckett and Terri L. Puckett."],
        forbidden=["Albino Frog is explicitly the developer rather than the publisher."]),
    "T6_546": spec("E5", "What was Ding's opening result, and what happened in the later linked 2023 match sequence?",
        duplicate=["Ding beat Ma Hailong 4–3 in the 2023 English Open opening match."],
        forbidden=["The later linked 4–3, 4–0 and loss sequence is established."]),
    "T6_1094": spec("E5", "Which club did Milan's 1908 split form, and do the PSG–Lille clubs satisfy the history clues?",
        duplicate=["A 1908 AC Milan split over foreign-player signings formed Internazionale."],
        forbidden=["The AC Milan source establishes PSG/Lille histories."]),
    "T6_435": spec("E5", "What was Oliver Mtukudzi's death age, and what exact album count did the May Forbes feature report?",
        duplicate=["Oliver Mtukudzi died at age 66."],
        forbidden=["The source establishes the exact Forbes Africa May album count."]),
    "T6_177": spec("E5", "How many players did Rangers sign, and what was its goal difference in the tied-points season?",
        duplicate=["Rangers signed 13 new players ahead of 2022/23."],
        forbidden=["The source establishes Rangers' tied-points season goal difference."]),
    "T7_186": spec("E7", "What does the full-title Galacta source say about release year and shared-surname credits?",
        ["The full-title Galacta: The Battle for Saturn page lists a November 1992 DOS release.",
         "Its credits list Sean Michael Puckett and Terri L. Puckett."],
        forbidden=["The shortened-title 1993 source must describe exactly the same release as the full-title 1992 source."]),
}

SEED = {"T6_546": "stale_546_opening", "T6_1094": "stale_1094_inter_split",
        "T6_435": "435_support_oliver_age", "T6_177": "stale_177_signings_first"}
assert len(SPECS) == len(HIST) == 41
assert set(SPECS) == {h["case_id"] for h in HIST}
bank = []
for h in HIST:
    cid = h["case_id"]
    s = SPECS[cid]
    w = h["new_observation"]
    existing = []
    if cid in SEED:
        seed = CLOSURE[SEED[cid]]
        assert seed["review_label"] == "supported"
        assert seed["visible_evidence"][0]["excerpt"] == w["text"]
        existing = [{"claim_id": "C1", "statement": seed["claim"],
                     "evidence_refs": [seed["visible_evidence"][0]["ref"]], "version": 1}]
    question = QUESTIONS.get(h["qid"], h["question_constraint"])
    bank.append({"case_id": cid, "qid": h["qid"], "source_checkpoint": w["provenance"],
                 "raw_question": question, "active_gap": s["gap"],
                 "existing_claims": existing,
                 "new_observation": {"ref": w["ref"], "doc_ref": w["doc_ref"],
                                     "title": w["title"], "text": w["text"]},
                 "review": {"type": s["kind"], "required_findings": s["required_findings"],
                            "optional_findings": s["optional_findings"],
                            "duplicate_existing_facts": s["duplicate_existing_facts"],
                            "forbidden_inferences": s["forbidden_inferences"],
                            "no_gain": s["kind"] == "E6"}})
assert len(bank) == 41 and len({b["qid"] for b in bank}) == 12
counts = Counter(b["review"]["type"] for b in bank)
assert all(counts[t] for t in ("E1","E2","E3","E4","E5","E6","E7","E8")), counts
(HERE / "BANK.json").write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n")
print(dict(counts))
