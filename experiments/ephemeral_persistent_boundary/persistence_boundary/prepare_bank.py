"""Freeze controlled binding challenges over all historical transitions except qid 776."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
old = json.loads((ROOT / "experiments/research_state_v2/claim_mutation/CASES.json").read_text())
questions = {x["qid"]: x["raw_question"] for x in json.loads((ROOT / "experiments/variable_preserving_state/test_representation/CASES.json").read_text())}

# category, slot, relation/condition, observed correct value or None, temporary
# query guess, optional seeded old binding.  Categories and labels are fixed
# before any S2 model call.  Query text is a controlled challenge, not a claim
# that this precise query historically produced the real W.
SPECS = {
"T1_546": ("P1","opening_opponent","Who did Ding Junhui beat 4-3 in the 2023 English Open opening match?","Ma Hailong","Ma Hailong",None),
"T2_546": ("P2","next_match_opponent","Who was Ding Junhui's opponent in his next match after that opening win?",None,"John Higgins",None),
"T3_546": ("P5","opening_opponent","Who did Ding Junhui beat 4-3 in the 2023 English Open opening match?","Ma Hailong","John Higgins",None),
"T1_1094": ("P1","free_kick_taker","Who took the last-gasp 95th-minute free kick in the PSG-Lille 4-3 match?","Lionel Messi","Lionel Messi",None),
"T2_1094": ("P5","free_kick_taker","Who took the last-gasp 95th-minute free kick in the PSG-Lille 4-3 match?","Lionel Messi","Neymar",None),
"T3_1094": ("P1","split_founded_club","Which football club was formed after Milan's 1908 split over signing foreign players?","F.C. Internazionale","F.C. Internazionale",None),
"T1_517": ("P1","popular_name","What popular name does the Kenyan actor Peter King Nzioki Mwania use?","Peter King","Peter King",None),
"T2_517": ("P3","policeman_role","What exact cast role did Peter King play in The Constant Gardener (2005)?",None,"policeman",None),
"T3_517": ("P5","birth_name","What is the actor Peter King's full birth name?","Peter King Nzioki Mwania","Peter King",None),
"T1_435": ("P1","death_age","At what age did Oliver Mtukudzi die?","66","66",None),
"T2_435": ("P2","death_age","At what age did Oliver Mtukudzi die?",None,"76",None),
"T3_435": ("P5","death_age","At what age did Oliver Mtukudzi die?","66","76",None),
"T1_580": ("P1","season_four_episode_title","What is the season-four episode title where Gretchen goes home for her brother's baby's birth?","Not a Great Bet","Not a Great Bet",None),
"T2_580": ("P2","season_one_episode_title","What is the season-one episode title where Jimmy's friends convince him to take Gretchen on a date?",None,"Not a Great Bet",None),
"T3_580": ("P5","season_four_episode_title","What is the season-four episode title where Gretchen goes home for her brother's baby's birth?","Not a Great Bet","Insouciance",None),
"T1_177": ("P1","club_city","Which city is Rangers, the club that signed 13 new players, based in?","Enugu","Enugu",None),
"T2_177": ("P3","total_major_trophies","How many total major trophies has the club won across all competitions?",None,"seven",None),
"T3_177": ("P5","club_city","Which city is Rangers, the club that signed 13 new players, based in?","Enugu","Abuja",None),
"T1_1034": ("P1","model_person","Which person in this article is explicitly described as a model?","Heart Evangelista","Heart Evangelista",None),
"T2_1034": ("P3","child_birthplace","Where was Heart Evangelista's child born?",None,"US",None),
"T3_1034": ("P5","model_person","Which person in this article is explicitly described as a model?","Heart Evangelista","Nita Ambani",None),
"T1_387": ("P1","current_game_title","Which game does Dean Dodrill name as his own finished title?","Dust: An Elysian Tail","Dust: An Elysian Tail",None),
"T2_387": ("P2","game_b_title","Which game did Dean Dodrill animate the introduction and ending for?",None,"Dust: An Elysian Tail",None),
"T3_387": ("P3","animation_paper_size","What exact paper size did Dean Dodrill use for Game B animation?",None,"8x11",None),
"T4_546": ("P4","next_match_opponent","Who was Ding Junhui's next 2023 English Open opponent after Ma Hailong?",None,"John Higgins",None),
"T4_1094": ("P4","split_founded_club","Which club was founded by a split over signing foreign players?",None,"Paris Saint-Germain",None),
"T4_177": ("P4","club_city","Which city is Nigerian Rangers based in?",None,"Enugu",None),
"T4_517": ("P4","film_role","What exact role did Peter King play in The Constant Gardener?",None,"policeman",None),
"T4_311": ("P4","argentine_program_title","What is the Argentine native title of the short educational television program?",None,"Las aventuras de Hijitus",None),
"T4_324": ("P4","earlier_event_winner","Who won the specified poker event two years before player X?",None,"Annie Duke",None),
"T4_186": ("P4","developed_game_title","Which early-1990s DOS shareware game was developed by the amphibian-named company?",None,"Galacta: The Battle for Saturn",None),
"T5_546": ("P5","professional_start_year","In which year did Ding Junhui turn professional?","2003","2005",None),
"T5_517": ("P5","birth_name","What is the actor Peter King's full birth name?","Peter King Nzioki Mwania","Peter King",None),
"T5_311": ("P5","argentine_program_title","What is the complete Argentine native title of The Adventures of Hijitus?","Las aventuras de Hijitus","Hijitus",None),
"T5_186": ("P5","game_title","What is the title of the November 1992 DOS shareware game listed on this page?","Galacta: The Battle for Saturn","Frogger",None),
"T6_546": ("P6","opening_opponent","Who did Ding Junhui beat 4-3 in the 2023 English Open opening match?","Ma Hailong","John Higgins","John Higgins"),
"T6_1094": ("P6","split_founded_club","Which club was formed after Milan's 1908 split over foreign player signings?","F.C. Internazionale","AC Milan","AC Milan"),
"T6_435": ("P6","death_age","At what age did Oliver Mtukudzi die?","66","76","76"),
"T6_177": ("P6","club_city","Which city is Rangers, the club that signed 13 new players, based in?","Enugu","Abuja","Abuja"),
"T7_186": ("P2","developer_company","Which company developed Galacta: The Battle for Saturn?",None,"Albino Frog Software, Inc.",None),
}

assert len(SPECS) == 40
assert set(SPECS) == {c["case_id"] for c in old if c["qid"] != "776"}
bank = []
for c in old:
    if c["qid"] == "776":
        continue
    cat, slot, condition, truth, guess, prior = SPECS[c["case_id"]]
    w = c["new_observation"]
    if truth is not None:
        assert truth.lower() in w["text"].lower(), (c["case_id"], truth)
    if cat == "P2":
        assert guess.lower() in w["text"].lower(), (c["case_id"], guess)
    bank.append({"case_id": c["case_id"], "qid": c["qid"], "category": cat,
        "source_transition": c["case_id"], "raw_question": questions[c["qid"]],
        "working_hypothesis": {"hypothesis_id": "H1", "binding": c["question_constraint"], "status": "provisional", "basis_refs": []},
        "semantic_gap": condition,
        "test_card": {"test_id": "T1", "condition": condition, "known": [], "unknown": [slot], "status": "open", "evidence_refs": []},
        "previous_persistent_bindings": {slot: prior} if prior else {},
        "ephemeral_query": f"{condition} {guess}", "ephemeral_guess_values": [guess],
        "new_observation": {"ref": w["ref"], "text": w["text"], "title": w["title"], "provenance": w["provenance"]},
        "review": {"correct_new_value": truth, "correct_action": "replace" if cat == "P6" else "bind" if truth else "preserve_unknown",
                   "reason": cat + ": annotated exact new-W relation; query guess is not evidence."}})
assert len({c["qid"] for c in bank}) == 11
assert sum(c["category"] == "P6" for c in bank) == 4
(HERE / "BANK.json").write_text(json.dumps(bank,ensure_ascii=False,indent=2)+"\n")
