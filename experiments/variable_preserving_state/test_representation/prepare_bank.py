"""Build 30 prefix-only normalized SemanticGap packets and preselect 16 V2 cells."""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A1 = ROOT / "experiments/research_state_v2/claim_admission/CASES.json"
M1 = ROOT / "experiments/research_state_v2/claim_mutation/CASES.json"

EXTRA_IDS = ("T4_186", "T5_186", "T7_186", "T4_311", "T5_311", "T4_324")

SEMANTIC_GAPS = {
    "546": "Does provisional player H1 satisfy the required ordered later 2023 match sequence after the opening decider?",
    "1094": "Do the clubs in provisional fixture H1 satisfy the split-founded and evolving-identity histories?",
    "517": "Did provisional person H1 play the specified policeman role in the 2005 film?",
    "435": "What count did the specified May Forbes Africa feature report for provisional musician H1, and was H1's first album in the required period?",
    "580": "Does provisional series H1 contain the specified early season-one reconciliation scene?",
    "177": "Did provisional team H1 have the required equal-points position and goal difference in the specified 2011–2016 season?",
    "1034": "Did provisional person H1 study Business Administration in the stated period and have a child born in the United States?",
    "387": "Did provisional person H1 create Game B's intro/end animations on ordinary 8×11-inch paper?",
    "186": "Which game satisfies the November DOS single-player shareware and shared-surname credit clues, and the developer-name history?",
    "311": "Which Argentine television program satisfies the early-1990s short-episode, network and character clues?",
    "324": "Which earlier event winner is linked to the still-unidentified player and event satisfying the question's poker clues?",
}

REQUIREMENTS = {
    "546": ["A later 4–3 win by the same candidate", "A following 4–0 win by the same candidate", "The following loss and opponent condition"],
    "1094": ["Split/discord founding history of the proposed first club", "Evolving identity history of the proposed opponent"],
    "517": ["Exact policeman-character credit for the provisional actor in the specified film"],
    "435": ["Album count in the specified May Forbes Africa feature", "First-album period matches the question"],
    "580": ["Early season-one date reconciliation scene belongs to the same series"],
    "177": ["Candidate's final-table position and equal-points tie in the specified season", "Candidate's same-season goal difference"],
    "1034": ["Candidate's university entry period and Business Administration subject", "Candidate's child's US birthplace"],
    "387": ["Candidate created Game B's intro and end animations", "Candidate used ordinary 8×11-inch paper for those animations"],
    "186": ["November early-1990s DOS release with one player/shareware", "Three game credits include two people with a shared surname", "Developer's name history and amphibian name"],
    "311": ["Program's early-1990s January–December run and yearly episode count", "Sub-five-minute runtime on the three-character network with a number", "Character set and Argentine release name"],
    "324": ["Identify qualifying player and winning event from the heads-up/final-table clues", "Identify the winner of the same event two years earlier"],
}

UNKNOWN_SLOTS = {
    "546": ["later_4_3_opponent", "later_4_3_date", "later_4_0_opponent", "later_4_0_date", "following_loss_opponent"],
    "1094": ["split_founder_relation", "opponent_identity_iterations"],
    "517": ["exact_character_credit"],
    "435": ["forbes_feature_album_count", "first_album_year"],
    "580": ["season_one_episode_title"],
    "177": ["standings_season", "tied_team", "points", "goal_difference"],
    "1034": ["university_name", "child_identity"],
    "387": ["game_b_title", "animation_credit_evidence"],
    "186": ["game_title", "developer_earlier_name"],
    "311": ["program_title", "qualifying_run_year", "episode_count"],
    "324": ["player_x", "event", "earlier_winner"],
}

EXTRA_ANCHORS = {
    "186": ["published in the early 1990s in november on DOS and has only a single-player mode and has a shareware business model", "Three people have credits for the game, two of them share the same family name", "software company named after an amphibian, yet had a different name in the early 1990s"],
    "311": ["Aired and ended in the early 1990s", "50 to 60 episodes were created in one year", "The name of the network in which the program aired has three characters, one of which is a number", "Among its characters is a set of twins, a poet, a complainer, and a means of transport that's alive"],
    "324": ["X won one of the events in a poker tournament between 2009 and 2015 (exclusive)", "In the heads-up play of the event, X called after their opponent had raised all in for their remaining chips", "Who won this event two years before X did?"],
}

HYPOTHESIS_VALUES = {
    "546": "candidate_player = Ding Junhui",
    "1094": "candidate_fixture = PSG–Lille",
    "517": "candidate_actor = Peter King Nzioki",
    "435": "candidate_musician = Oliver Mtukudzi",
    "580": "candidate_series = series containing 'Not a Great Bet'",
    "177": "candidate_team = Enugu Rangers",
    "1034": "candidate_person = Heart Evangelista",
    "387": "candidate_animator = Dean Dodrill",
    "186": "candidate_game = Galacta: The Battle for Saturn",
    "311": "candidate_program = The Adventures of Hijitus",
}

SOURCE_TYPES = {
    "546": "dated round-by-round tournament results",
    "1094": "club founding and historical name records",
    "517": "film cast credits",
    "435": "dated Forbes Africa feature and album discography",
    "580": "season-one episode plot summary",
    "177": "dated final league standings table",
    "1034": "biography or interview on education and family",
    "387": "Game B animation credits and animator interview",
    "186": "DOS game catalog and developer history",
    "311": "television program episode and broadcast catalog",
    "324": "dated tournament event results and player profile",
}


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def visible(o):
    return {k: o[k] for k in ("ref", "doc_ref", "title", "text")}


def hypothesis(case_id, qid, evidence):
    if case_id in ("T3_1094", "T4_186", "T4_311", "T4_324"):
        return None
    if case_id == "T2_435":
        value = "candidate_musician = Miriam Makeba"
    else:
        value = HYPOTHESIS_VALUES[qid]
    ref = evidence[-1]["ref"]
    return {"hypothesis_id": "H1", "binding": value, "status": "provisional", "basis_refs": [ref]}


def main():
    a1 = json.loads(A1.read_text())
    old = {c["case_id"]: c for c in json.loads(M1.read_text())}
    bank = []
    for c in a1:
        qid = c["qid"]
        evidence = [c["latest_observation"]]
        h = hypothesis(c["case_id"], qid, evidence)
        gap = SEMANTIC_GAPS[qid] if h else "Which clubs in the target 95th-minute fixture satisfy the split-founded and evolving-identity histories?"
        packet = {"case_id": c["case_id"], "qid": qid, "checkpoint": c["checkpoint"],
                  "raw_question": c["raw_question"], "question_anchors": c["question_anchors"],
                  "working_hypothesis": h, "semantic_gap": gap,
                  "existing_tests": [], "visible_evidence": evidence,
                  "visible_basis_refs": [x["ref"] for x in evidence],
                  "coverage_requirements": REQUIREMENTS[qid], "review_unknown_slots": UNKNOWN_SLOTS[qid],
                  "expected_source_type": SOURCE_TYPES[qid], "source_case_sha256": digest(c)}
        bank.append(packet)
    for cid in EXTRA_IDS:
        c = old[cid]
        qid = c["qid"]
        evidence = [visible(x) for x in c["prior_observations"] + [c["new_observation"]]]
        h = hypothesis(cid, qid, evidence)
        gap = SEMANTIC_GAPS[qid]
        if h and qid == "186":
            gap = "Does provisional game H1 satisfy the November DOS, one-player/shareware, shared-surname credit and developer-name clues?"
        if h and qid == "311":
            gap = "Does provisional program H1 satisfy the early-1990s short-episode, network and character clues?"
        anchors = {f"Q{i}": a for i, a in enumerate(EXTRA_ANCHORS[qid], 1)}
        unknown_slots = UNKNOWN_SLOTS[qid]
        if h and qid == "186":
            unknown_slots = ["developer_earlier_name"]
        if h and qid == "311":
            unknown_slots = ["qualifying_run_year", "yearly_episode_count"]
        packet = {"case_id": cid, "qid": qid, "checkpoint": c["new_observation"]["provenance"],
                  "raw_question": c["question_constraint"], "question_anchors": anchors,
                  "working_hypothesis": h, "semantic_gap": gap,
                  "existing_tests": [], "visible_evidence": evidence,
                  "visible_basis_refs": [x["ref"] for x in evidence],
                  "coverage_requirements": REQUIREMENTS[qid], "review_unknown_slots": unknown_slots,
                  "expected_source_type": SOURCE_TYPES[qid], "source_case_sha256": digest(c)}
        bank.append(packet)
    assert len(bank) == 30 and len({c["qid"] for c in bank}) == 11
    for c in bank:
        assert all(a.lower() in c["raw_question"].lower() for a in c["question_anchors"].values()), c["case_id"]
        assert not c["semantic_gap"].lower().startswith(("find ", "locate ", "search ", "check ", "read ", "verify "))
        if c["working_hypothesis"]:
            assert c["working_hypothesis"]["basis_refs"][-1] in c["visible_basis_refs"]
            assert c["working_hypothesis"]["status"] == "provisional"
    bank.sort(key=lambda c: hashlib.sha256(c["case_id"].encode()).hexdigest())
    (HERE / "CASES.json").write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n")
    selected = [c for c in bank if c["qid"] in {"546", "1094", "517", "435", "580", "177", "1034", "387"}
                and c["case_id"].startswith(("T1_", "T2_"))]
    assert len(selected) == 16 and len({c["qid"] for c in selected}) == 8
    (HERE.parent / "query_bias").mkdir(parents=True, exist_ok=True)
    (HERE.parent / "query_bias/V2_SELECTION.json").write_text(json.dumps({
        "selected_before_V1_calls": True,
        "case_ids": [c["case_id"] for c in selected],
        "per_case": {c["case_id"]: {"qid": c["qid"], "prefix_sha256": digest([c["raw_question"], c["visible_evidence"]]),
                                     "semantic_gap_sha256": digest(c["semantic_gap"]),
                                     "known_suitable_D": "none",
                                     "reason": "Observed W addresses a different or incomplete clue; the current SemanticGap requires a new source type."}
                     for c in selected},
    }, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
