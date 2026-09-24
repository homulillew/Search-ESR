"""Transcribe the single reviewer's top-five preview decisions, by packet order.

Each grouping below was decided from REVIEW_PACKETS.json without its S/D mapping.
The complete query, preview, ranks and short reason remain in the audit files.
"""

import json
from pathlib import Path

here = Path(__file__).resolve().parent
packets = json.loads((here / "REVIEW_PACKETS.json").read_text())

# Review groups: all members share the same specific visible support pattern.
episode = {24, 27, 32, 36, 42, 49, 50, 54, 56, 62}
episode_miss = {51}
table = {35, 38, 52, 55, 64, 67, 70}
artist_may = {23, 26, 57, 60}
artist_bio = {9, 13, 21, 31, 34}
setup_interview = {1, 2, 6, 7, 10, 14, 17, 20, 29, 44, 59, 63}
other = set(range(len(packets))) - episode - episode_miss - table - artist_may - artist_bio - setup_interview
assert len(packets) == 71 and len(other) == 32

reviews = {}
for i, p in enumerate(packets):
    hits = p["results"]
    spec = bool(p["speculative_values_in_query"])
    suitable = useful = direct = False
    support = False if spec else None
    ranks = []
    breadth = "unclear"
    if i in episode:
        ranks = [j + 1 for j, r in enumerate(hits) if "Insouciance - You're the Worst" in r.get("title", "")]
        assert ranks
        suitable = useful = direct = True
        support = True if spec else None
        breadth = "one_candidate"
        reason = "Episode 2 preview names the series and matches Jimmy/Gretchen and the friends-convince-date scene; it resolves the current scene/series test."
    elif i in episode_miss:
        reason = "Generic episode guides are for other series; no returned preview matches the Jimmy/Gretchen scene."
        breadth = "multiple_directions"
    elif i in table:
        ranks = [j + 1 for j, r in enumerate(hits) if "Nigeria Premier League 2014, Results and Standings" in r.get("title", "") or "Table Nigeria Professional Football League 2014" in r.get("title", "")]
        assert ranks
        suitable = True
        useful = i != 52
        breadth = "multiple_directions"
        reason = ("A 2014 standings source is suitable, but this preview only exposes bottom rows and not the current club's needed comparison." if i == 52 else "The 2014 standings preview contains Enugu Rangers at 58 points/+8 and neighboring rows; this can check or exclude that season, but does not establish the requested tied-points season.")
        # A speculative season or club is present, but the row does not establish
        # the full tied-points condition required by this gap.
    elif i in artist_may:
        ranks = [j + 1 for j, r in enumerate(hits) if "Forbes Africa announces Top 10 Richest African Musicians" in r.get("title", "") or "10 Richest African Musicians" in r.get("title", "")]
        suitable = useful = bool(ranks)
        breadth = "multiple_directions"
        support = (i in {26, 57, 60}) if spec else None
        reason = "The May Forbes Africa list identifies Oliver Mtukudzi, an alternative to provisional Miriam Makeba; some previews also give 65 albums, but do not show that the Forbes feature itself reported that count."
    elif i in artist_bio:
        ranks = [j + 1 for j, r in enumerate(hits) if "Oliver Mtukudzi - Wikipedia" in r.get("title", "") or "Remembering Oliver Mtukudzi" in r.get("title", "")]
        suitable = bool(ranks) and i in {13, 31, 34}
        breadth = "one_candidate"
        reason = "Oliver Mtukudzi biographical material is returned, but the preview does not verify the provisional Miriam Makeba Test or the Forbes-reported album count."
    elif i in setup_interview:
        ranks = [j + 1 for j, r in enumerate(hits) if "How I Game: Dean Dodrill" in r.get("title", "")]
        suitable = bool(ranks)
        breadth = "multiple_directions" if any("Jazz Jackrabbit" in r.get("title", "") for r in hits) else "one_candidate"
        reason = "The 2013 Dean Dodrill setup interview is a plausible source for the paper/setup Test, but its returned preview gives no 8×11-paper statement or Game B credit."
    else:
        qid = p["qid"]
        reason = {
            "1034": "Heart profile or other-parent results do not show her Business Administration enrollment or US-born child; mere person match is insufficient.",
            "1094": "League tables and PSG–Lille match reports do not show the required split-founded or changing-identity club histories.",
            "517": "Actor biography repeats a minor film role and the film page lists technical details, but neither preview supplies the policeman cast credit.",
            "546": "Opening-match article and unrelated snooker results do not establish Ding's ordered later-match sequence; Higgins/Ronnie mentions concern other matches.",
        }[qid]
        breadth = "multiple_directions" if qid in {"1034", "1094", "517"} else "one_candidate"
    if i in {57, 60}:
        # The 65 figure is visible, but source attribution to the May Forbes
        # feature remains unproved; hence no direct unknown resolution.
        direct = False
    review = {
        "suitable_source": suitable,
        "useful_evidence": useful,
        "direct_unknown_resolution": direct,
        "no_gain": not suitable and not useful,
        "speculative_value_support": support,
        "candidate_breadth": breadth,
        "supporting_ranks": ranks,
        "reason": reason,
    }
    reviews[p["review_id"]] = review

assert len(reviews) == 71
(here / "REVIEWS.json").write_text(json.dumps(reviews, ensure_ascii=False, indent=2) + "\n")
