"""Transcribe answer-blind single-reviewer W judgments for the frozen F1 outputs."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKETS = json.loads((HERE / "REVIEW_PACKETS.json").read_text())

# A listed W contributes a new, directly visible material fact or exclusion to
# the named frozen Gap. All other W were inspected and judged non-gaining.
POSITIVE = {
 "F1_F1_T1_546:A0": {"W2": (["G2"], "A dated later 2023 English Open last-16 result names Ding and Brecel with a 4-3 score.")},
 "F1_F1_T1_546:A1": {"W2": (["G2"], "The dated English Open table gives a later Ding–Brecel 4-3 result."),
                         "W3": (["G1"], "Ding biography states more than 600 centuries and seven maximum breaks, absent from the initial W.")},
 "F1_F1_T4_546:A0": {"W8": (["G1"], "Ding biography directly states more than 600 centuries and seven maximums.")},
 "F1_F1_T4_546:A1": {"W4": (["G1"], "Ding biography directly states professional start in 2003 and the century/maximum totals.")},
 "F1_F1_T1_1094:A0": {"W4": (["G3"], "Match report supplies the 2-0, 3-2, 3-3 and late-winner chronology."),
                          "W6": (["G3"], "A separate report gives the lead reversal and late equalizer before Messi's winner.")},
 "F1_F1_T3_1094:A0": {"W5": (["G1"], "Fixture report identifies PSG–Lille and Messi's 95th-minute free kick.")},
 "F1_F1_T3_1094:A1": {"W5": (["G1"], "Fixture report identifies PSG–Lille and Messi's 95th-minute free kick."),
                         "W6": (["G1"], "Report directly names Messi, PSG–Lille, minute 95 and the 4-3 result.")},
 "F1_F1_T1_517:A0": {"W2": (["G2"], "The candidate's filmography lists The Constant Gardener, 2005, Policeman 1.")},
 "F1_F1_T1_517:A1": {"W3": (["G2"], "Director profile links the 2005 film The Constant Gardener to Meirelles and his Iracema inspiration; actor role remains open.")},
 "F1_F1_T4_517:A0": {"W6": (["G2"], "Director profile identifies Meirelles as inspired by Iracema, narrowing the specified 2005-film clue.")},
 "F1_F1_T4_517:A1": {"W4": (["G2"], "Director profile identifies Meirelles as inspired by Iracema, narrowing the specified 2005-film clue.")},
 "F1_F1_T1_435:A1": {"W2": (["G1", "G3"], "Mtukudzi biography connects the age-66 lead to 1977 first-album period and human-rights activism."),
                        "W4": (["G1"], "Independent article states the same musician released more than 60 albums.")},
 "F1_F1_T2_435:A0": {"W2": (["G1", "G3"], "Mtukudzi biography gives career period, first album and activism, distinguishing the age-76 source lead."),
                        "W3": (["G1"], "Obituary directly identifies Mtukudzi as the musician who died at 66."),
                        "W4": (["G1"], "Independent obituary gives the more-than-60-album career fact.")},
 "F1_F1_T2_435:A1": {"W7": (["G1", "G3"], "Report connects Mtukudzi's death age, 67 career albums and the 2001 political song.")},
 "F1_F3_P05_W6:A0": {"W2": (["G1", "G3"], "Mtukudzi biography adds activism and first-album period beyond the initial 65-album W."),
                         "W3": (["G1"], "Obituary adds the death-at-66 identity clue."),
                         "W4": (["G1"], "Independent obituary adds the career total exceeding 60 albums."),
                         "W6": (["G1", "G3"], "Report adds 67 career albums at death and the 2001 political song."),
                         "W8": (["G3"], "Artist interview describes coded political messaging in Mtukudzi's music.")},
 "F1_F3_P05_W6:A1": {"W2": (["G1", "G3"], "Mtukudzi biography adds activism and first-album period beyond the initial 65-album W."),
                         "W3": (["G1"], "Obituary adds the death-at-66 identity clue."),
                         "W4": (["G1"], "Independent obituary adds the career total exceeding 60 albums.")},
 "F1_F1_T1_580:A1": {"W2": (["G2"], "Season-three episode source mentions Edgar's sacrifice."),
                        "W3": (["G2"], "Character source identifies Edgar as Jimmy's roommate."),
                        "W4": (["G4"], "Series source connects Jimmy, Gretchen and Edgar in the same five-season show."),
                        "W6": (["G1"], "Season-one episode source gives the assumption, anger and date-invitation plot.")},
 "F1_F3_P12_W2:A0": {"W2": (["G4"], "Series source connects the named characters and confirms five seasons."),
                         "W3": (["G2"], "Season-three episode source mentions Edgar's sacrifice.")},
 "F1_F3_P12_W2:A1": {"W2": (["G2"], "Season-three episode source mentions Edgar's sacrifice."),
                         "W3": (["G2"], "Character source identifies Edgar as Jimmy's roommate."),
                         "W4": (["G4"], "Series source connects the named characters and confirms five seasons.")},
 "F1_F3_P12_W4:A0": {"W2": (["G3"], "Season-four episode source gives the brother's-baby return and old-friend reconnection."),
                         "W4": (["G1"], "Season-one episode source gives the date-scene clue.")},
 "F1_F1_T1_177:A1": {"W2": (["G3"], "Club source directly states Enugu Rangers was founded in 1970 in Nigeria."),
                        "W3": (["G2"], "2016 league source identifies an additional Rangers league title.")},
 "F1_F1_T4_177:A1": {"W4": (["G2"], "Rangers source gives the 13-player signing and Enugu base, absent from the Chicago Bears prefix.")},
 "F1_F3_P07_W17:A0": {"W3": (["G2"], "Article adds the 13 signings and Enugu base to the prior 2014 table.")},
 "F1_F3_P07_W17:A1": {"W2": (["G2"], "Article adds the 13 signings and Enugu base to the prior 2014 table."),
                         "W3": (["G2"], "Club source reports multiple league wins between 1974 and 1983."),
                         "W4": (["G2"], "League source identifies Rangers' 2016 championship.")},
 "F1_F1_T4_186:A0": {"W2": (["G1", "G4"], "Company source connects Galacta to amphibian-named Albino Frog and its earlier name Night Sky."),
                        "W6": (["G1"], "Game listing adds Sean Puckett as developer alongside the Albino Frog publisher.")},
 "F1_F1_T4_186:A1": {"W2": (["G1", "G4"], "Company source connects Galacta to amphibian-named Albino Frog and its earlier name Night Sky.")},
 "F1_F1_T5_186:A0": {"W2": (["G4", "G1"], "Company source identifies the former name Night Sky and lists Galacta among its games."),
                        "W3": (["G1"], "Game listing adds Sean Puckett as developer alongside the Albino Frog publisher."),
                        "W8": (["G1"], "Game source explicitly identifies Albino Frog as Galacta's developer, not only its publisher.")},
 "F1_F1_T5_186:A1": {"W2": (["G4", "G1"], "Company source identifies the former name Night Sky and lists Galacta among its games.")},
 "F1_F1_T5_311:A0": {"W3": (["G2"], "Director biography says Hijitus aired in 1967–1974, directly contradicting the early-1990s end clue.")},
 "F1_F1_T1_387:A0": {"W2": (["G1"], "Game-series source names Dean Dodrill as an animator for Jazz Jackrabbit 2; exact intro/end credit remains open.")},
 "F1_F1_T1_387:A1": {"W2": (["G1"], "Game-series source names Dean Dodrill as an animator for Jazz Jackrabbit 2; exact intro/end credit remains open.")},
}

SCATTER = {
 "F1_F1_T4_546:A1", "F1_F1_T5_546:A0", "F1_F1_T2_435:A1",
 "F1_F1_T4_177:A0", "F1_F1_T4_177:A1", "F1_F1_T1_1034:A0",
 "F1_F1_T4_186:A0", "F1_F1_T4_186:A1", "F1_F1_T4_311:A0",
 "F1_F1_T5_311:A0", "F1_F1_T5_311:A1",
}
SCOPE_WRONG = {"F1_F1_T1_1094:A0", "F1_F1_T1_517:A1"}
REDUNDANT = {"F1_F1_T1_1094:A1"}


def main():
    target = HERE / "REVIEWS.json"
    if target.exists():
        raise FileExistsError(target)
    cells = {p["cell"] for p in PACKETS}
    assert set(POSITIVE) <= cells and SCATTER <= cells and SCOPE_WRONG <= cells and REDUNDANT <= cells
    rows = []
    for packet in PACKETS:
        cell = packet["cell"]
        available = {w["window_ref"] for w in packet["observations"]}
        assert set(POSITIVE.get(cell, {})) <= available, cell
        reviews = []
        for w in packet["observations"]:
            ref = w["window_ref"]
            positive = POSITIVE.get(cell, {}).get(ref)
            if positive:
                gap_ids, reason = positive
                assert set(gap_ids) <= {g["gap_id"] for g in packet["open_gaps"]}
                reviews.append({"window_ref": ref, "useful_evidence": True,
                                "advanced_gap_ids": gap_ids,
                                "frontier_specific": packet["selected_gap"] in gap_ids if packet["selected_gap"] else False,
                                "reason": reason})
            else:
                title = w.get("title") or w["text"][:55].replace("\n", " ")
                reviews.append({"window_ref": ref, "useful_evidence": False,
                                "advanced_gap_ids": [], "frontier_specific": False,
                                "reason": f"{title}: no new directly supported fact for a frozen Open Gap beyond the initial W and Claims."})
        action = packet["action"]
        rows.append({"cell": cell, "observation_reviews": reviews,
                     "scope_correct": action is not None and cell not in SCOPE_WRONG,
                     "gap_scatter": cell in SCATTER,
                     "redundant": cell in REDUNDANT,
                     "action_reason": packet["error"] or
                         ("At least one returned W adds a material Open-Gap fact."
                          if any(x["useful_evidence"] for x in reviews)
                          else "The executed action returned no new material Open-Gap fact."),
                     "reviewer": "Codex single-reviewer, action-result and prefix only"})
    assert len(rows) == 48
    target.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    print("reviewed", len(rows), "windows", sum(len(x["observation_reviews"]) for x in rows),
          "useful cells", sum(any(w["useful_evidence"] for w in x["observation_reviews"]) for x in rows))


if __name__ == "__main__":
    main()
