"""Build 40 claim-only local Gap diagnoses from prior verified Claim commits."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OLD = ROOT / "experiments/gap_evidence_claim_loop/claim_commit"
PACKETS = {x["packet_id"]: x for x in json.loads((OLD / "BANK.json").read_text())}
OUTCOMES = json.loads((OLD / "outcomes.json").read_text())
QUESTIONS = {x["qid"]: x["raw_question"] for x in json.loads((ROOT / "experiments/minimal_research_loop/verify_necessity/OBSERVATIONS.json").read_text())}

# Exactly four local diagnostic packets per qid: two genuinely resolved local
# Gaps, one incomplete conjunction, and one near-complete or identity trap.
# Every supplied Claim below is an immutable historical V_commit, with W refs.
SPECS = {
 "546": [
  ("opening", "Who won Ding Junhui's 2023 English Open opener, against whom and by what score?", ["A_T1_546_0"], "resolved", "", "full"),
  ("career", "Did Ding turn professional between 1995 and 2006, compile more than 300 centuries, and make more than three maximum breaks?", ["A_T5_546_0","A_T5_546_1","A_T5_546_2"], "resolved", "", "full"),
  ("career_partial", "Did Ding turn professional between 1995 and 2006 and make more than three maximum breaks?", ["A_T5_546_1"], "open", "professional start and maximum-break count", "missing_date_quantity"),
  ("run_trap", "After Ding's 2023 opening decider, did his next linked matches follow 4-3, 4-0, then a loss?", ["A_T1_546_0","A_T5_546_0","A_T5_546_1","A_T5_546_2"], "open", "later ordered match results", "near_complete"),
 ],
 "1094": [
  ("kick", "Which fixture had the 95th-minute free kick, and who took it?", ["A_T1_1094_0","A_T1_1094_1"], "resolved", "", "full"),
  ("score", "In the PSG–Lille fixture, did Messi's 95th-minute free kick turn a 3-3 score into a PSG 4-3 win?", ["A_T2_1094_0"], "resolved", "", "full"),
  ("fixture_partial", "Which fixture had Messi's 95th-minute free kick?", ["A_T1_1094_1"], "open", "fixture identity", "missing_identity"),
  ("history_trap", "Do both clubs in that 95th-minute fixture satisfy the split-founded and evolving-identity club-history clues?", ["A_T1_1094_0","A_T1_1094_1","A_T2_1094_0"], "open", "club-history facts and link to the same fixture", "near_complete"),
 ],
 "517": [
  ("birth_parents", "When was Peter King Nzioki born and what work did both parents do?", ["A_T1_517_0","A_T1_517_1"], "resolved", "", "full"),
  ("date", "On what day, month and year was Peter King Nzioki born?", ["A_T5_517_0"], "resolved", "", "full"),
  ("mother_partial", "What work did both of Peter King Nzioki's parents do?", ["A_T5_517_1"], "open", "mother's occupation", "missing_relation"),
  ("film_trap", "Did Peter King Nzioki play the policeman in The Constant Gardener?", ["A_T1_517_0","A_T1_517_1","A_T5_517_0","A_T5_517_1","A_T5_517_2"], "open", "film role and character", "near_complete"),
 ],
 "435": [
  ("death", "Which musician in these Claims died at age 66?", ["A_T3_435_0"], "resolved", "", "full"),
  ("career", "Did Oliver Mtukudzi have more than 60 albums over a 45-year career?", ["A_T3_435_1"], "resolved", "", "full"),
  ("age_partial", "Did Oliver Mtukudzi die at age 66 after a career of more than 60 albums?", ["A_T3_435_1"], "open", "age at death", "missing_quantity"),
  ("forbes_trap", "What exact album total did the May 2017 Forbes Africa feature report for Oliver Mtukudzi?", ["A_T3_435_0","A_T3_435_1","A_T1_435_0"], "open", "exact count in the dated Forbes feature", "near_complete"),
 ],
 "177": [
  ("signing", "How many new players did Rangers sign ahead of 2022/23?", ["A_T1_177_0"], "resolved", "", "full"),
  ("city", "Which city is Rangers based in?", ["A_T1_177_1"], "resolved", "", "full"),
  ("city_partial", "Did Rangers sign 13 new players ahead of 2022/23 and have a base in Enugu?", ["A_T1_177_0"], "open", "Enugu base", "missing_relation"),
  ("table_trap", "Did Rangers meet the requested historical equal-points position and goal-difference table clue?", ["A_T3_177_0","A_T3_177_1","A_T1_177_0","A_T1_177_1"], "open", "historical table position, points tie and goal difference", "near_complete"),
 ],
 "387": [
  ("keyboard", "Did Dean Dodrill's gaming PC setup include a wireless keyboard?", ["A_T1_387_0"], "resolved", "", "full"),
  ("storage", "How much storage did Dean Dodrill's gaming PC have?", ["A_T2_387_1"], "resolved", "", "full"),
  ("keyboard_partial", "Did Dean Dodrill have a gaming PC and a wireless keyboard?", ["A_T2_387_0"], "open", "wireless keyboard", "missing_relation"),
  ("paper_trap", "Did Dean Dodrill draw the named game's intro and ending animation on ordinary 8x11-inch paper?", ["A_T1_387_0","A_T2_387_0","A_T2_387_1"], "open", "named animation credit and paper size", "near_complete"),
 ],
 "311": [
  ("director", "Who directed The Adventures of Hijitus?", ["A_T5_311_0"], "resolved", "", "full"),
  ("broadcast", "On which channel and date did The Adventures of Hijitus first air?", ["A_T5_311_2"], "resolved", "", "full"),
  ("writer_partial", "Who directed and wrote The Adventures of Hijitus?", ["A_T5_311_0"], "open", "writers", "missing_relation"),
  ("schedule_trap", "Did The Adventures of Hijitus end in the early 1990s after a January-to-December run with 50–60 short episodes in one year?", ["A_T5_311_0","A_T5_311_1","A_T5_311_2"], "open", "end year, annual schedule, episode count and duration", "near_complete"),
 ],
 "186": [
  ("release", "In which month and year was Galacta: The Battle for Saturn released on DOS?", ["A_T7_186_0"], "resolved", "", "full"),
  ("credits", "Which two of Galacta's three credited people share a surname?", ["A_T7_186_1"], "resolved", "", "full"),
  ("mode_partial", "Was Galacta released in November of the early 1990s on DOS with one offline player?", ["A_T7_186_0"], "open", "single-player mode", "missing_quantity"),
  ("developer_trap", "Was Galacta developed by the amphibian-named software company that had a different original name?", ["A_T5_186_0","A_T5_186_1","A_T5_186_2","A_T7_186_0"], "open", "developer identity and its earlier name", "near_complete"),
 ],
 "1034": [
  ("person", "Who is identified as the model and singer in the article?", ["A_T1_1034_0"], "resolved", "", "full"),
  ("roles", "Is Heart Evangelista identified as a model and singer?", ["A_T1_1034_0"], "resolved", "", "full"),
  ("child_partial", "Is the model and singer identified as Heart Evangelista and is her child stated to have been born in the United States?", ["A_T1_1034_0"], "open", "US birthplace of child", "missing_relation"),
  ("name_trap", "What is the model and singer's birth name, and did she study Business Administration?", ["A_T1_1034_0"], "open", "birth name and university course", "missing_identity"),
 ],
 "580": [
  ("episode", "What is the Season 4 episode title for Gretchen's return home for a baby's birth?", ["A_T1_580_0"], "resolved", "", "full"),
  ("number", "Which Season 4 episode number is 'Not a Great Bet'?", ["A_T1_580_0"], "resolved", "", "full"),
  ("season1_partial", "Does the series have the cited Season 4 birth episode and the specified Season 1 date scene?", ["A_T1_580_0"], "open", "Season 1 date scene", "missing_sequence"),
  ("series_trap", "Does the same series have the Season 1 date scene, Season 3 roommate sacrifice and Season 4 birth return in that order?", ["A_T1_580_0","A_T3_580_0"], "open", "series identity and Season 1/3 plot links", "near_complete"),
 ],
}


def main():
    target = HERE / "BANK.json"
    if target.exists():
        raise FileExistsError(target)
    rows = []
    for qid, specs in SPECS.items():
        assert len(specs) == 4
        for suffix, gap, packet_ids, status, missing, category in specs:
            claims = []
            for index, packet_id in enumerate(packet_ids, 1):
                packet, outcome = PACKETS[packet_id], OUTCOMES[packet_id]
                assert packet["qid"] == qid and outcome["error"] is None
                assert outcome["V_commit"] is not None
                claim = outcome["V_commit"]
                claims.append({"claim_id": f"C{index}", "statement": claim["statement"],
                               "evidence_refs": claim["evidence_refs"]})
            rows.append({"case_id": f"C1_{qid}_{suffix}", "qid": qid,
                         "raw_question": QUESTIONS[qid], "active_gap": gap,
                         "committed_claims": claims, "historical_claim_packet_ids": packet_ids,
                         "review": {"status": status, "missing": missing,
                                    "category": category, "reason": "Only the supplied verified historical Claim statements can resolve this local Gap."}})
    assert len(rows) == 40 and len({r["qid"] for r in rows}) == 10
    assert sum(r["review"]["status"] == "resolved" for r in rows) == 20
    target.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    print("C1 bank", len(rows), "qids", len({r["qid"] for r in rows}))


if __name__ == "__main__":
    main()
