"""Reviewer-authored E1 transition selection, fixed before new model calls."""

BASE = {
    "546": ("546_support_opening", "546_refute_opening_loss", "546_open_full_run",
            "Ding's professional-start year and break totals still need separate checking."),
    "1094": ("1094_support_messi", "1094_refute_inter_lille", "1094_open_full_match",
             "The split-founded club must be linked to the same fixture."),
    "517": ("517_support_biography", "517_refute_birth_1979", "517_open_policeman",
            "Peter Nzioki's specific character in The Constant Gardener remains unverified."),
    "435": ("435_support_oliver_age", "435_refute_miriam_age", "435_open_full_identity",
            "The candidate's exact album total and article clues remain unverified."),
    "580": ("580_support_birth_plot", "580_refute_sister_birth", "580_open_all_seasons",
            "The season-one scene still needs a separate episode source."),
    "177": ("177_support_13", "177_refute_12", "177_open_league",
            "Rangers' historical equal-points table position and goal difference remain unverified."),
    "1034": ("1034_support_model", "1034_refute_no_model", "1034_open_education_child",
             "The candidate's university subject and child's birthplace remain unverified."),
    "387": ("387_support_dean_equipment", "387_refute_no_pc", "387_open_paper",
            "The named animation and 8x11-inch paper clue remains unverified."),
}

# Eight NoGain/irrelevant real observed windows, including four additional qids.
T4 = [
    ("546", "prior_D", "C_source_546", "D18", "The linked 2023 snooker match sequence is established."),
    ("1094", "prior_D", "C_source_1094", "D44", "The Lille club-name history is established."),
    ("177", "legacy", "47006", 15, "The 2011–2016 Rangers league-table conditions are established."),
    ("517", "legacy", "98322", 20, "Peter Nzioki's Constant Gardener character is established."),
    ("311", "baseline", "34974", 4, "The proposed cartoon satisfies its director/writers/episode constraints."),
    ("324", "baseline", "51275", 4, "The target WSOP event winner and third-tournament player are established."),
    ("776", "baseline", "53714", 4, "The exact title of the requested 1940 report is established."),
    ("186", "baseline", "44369", 4, "The amphibian-named company's specific November DOS game is established."),
]

# Multi-claim updates from one exact observed source.
T5 = [
    ("546", "prior_D", "C_location_546_bio", "W32", [
        "Ding Junhui turned professional in 2003.",
        "Ding Junhui compiled more than 600 century breaks.",
        "Ding Junhui made seven maximum breaks."],
     "Ding's later 2023 match sequence remains unverified."),
    ("517", "stage_A", "517_support_biography", [
        "Peter King Nzioki was born in 1978.",
        "Peter King Nzioki's father served in the Kenyan Army.",
        "Peter King Nzioki's mother worked at a military hospital."],
     "His specific Constant Gardener character remains unverified."),
    ("311", "baseline", "20521", 4, [
        "The Adventures of Hijitus was directed by Manuel García Ferré.",
        "The Adventures of Hijitus lists Inés Geldstein among its writers.",
        "The Adventures of Hijitus aired on Canal 13."],
     "The requested 1990s short program still needs a separate identity check."),
    ("186", "baseline", "39978", 8, [
        "Galacta: The Battle for Saturn was released in November 1992 on DOS.",
        "Galacta: The Battle for Saturn had one offline player.",
        "Galacta: The Battle for Saturn used a shareware business model."],
     "The original question's two-people-sharing-a-family-name credit condition is still open."),
]

T6 = [
    ("546", "546_support_opening", "Was Ding's opening match against Ma Hailong a 4-3 win?"),
    ("1094", "stale_1094_inter_split", "Did the 1908 Milan split form Internazionale?"),
    ("435", "435_support_oliver_age", "Did Oliver Mtukudzi die at 66?"),
    ("177", "177_support_13", "Did Rangers sign 13 new players before 2022/23?"),
]

# Authentic source disagreement, but title shortening makes this medium ambiguity.
T7 = ("186", "20115", "39978", "Galacta was released in 1993.")
