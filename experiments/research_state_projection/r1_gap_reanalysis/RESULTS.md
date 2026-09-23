# S0: post-hoc R1 action-gap diagnostic

This review does **not** revise R1's failed preregistered target-routing gate. It is a post-hoc mechanism diagnostic with zero new model calls. The reviewer read each checkpoint prefix, frozen R1 qualification, and the name/arguments of all 71 historical R1 H0/H1 one-step tool calls. No tool results, future trajectories or gold were used. Every call has an explicit score and reason in `action_gap_scores.json`.

| Call-level score | H0 historical Broad Plan | H1 appended qualification |
| --- | ---: | ---: |
| Calls | 36 | 35 |
| Directly addresses current gap (`yes`) | 6/36 | 7/35 |
| Directly or partially addresses gap | 22/36 | 24/35 |
| Repeats an already visible supported fact | 1/36 | 0/35 |
| Candidate inspection classified as gap test | 3 | 6 |
| Candidate inspection classified as local fact repeat | 1 | 0 |

The table's arm labels refer to **R1 H0/H1**; H0 was historical P1 Broad Plan only, H1 added Qualification. At the checkpoint level, 6/13 cells in either arm had at least one direct gap action. At least one direct-or-partial action fell from 13/13 H0 to 10/13 H1; H1's three all-`no` cells were 546:33, 1094:34 and 1094:61. Call-level counts cluster within the same 13 prefixes and are subjective single-reviewer labels, not independent trials.

The old `candidate_inspected` metric was too coarse for a mechanism claim. At 546:25, H0 Find(D10, `Ding Junhui 4-3 Ma Hailong`) repeats the W13 opening-win fact, whereas H1 Find(D10, `4-3 4-0 next round`) tries to test the missing continuation. D10 may still be a weak source; query intent and source suitability are separate. At 1094:45, both arms open W38 after the Messi PSG-Lille article, potentially testing goal chronology while leaving club histories unverified. At 1094:69, two new H1 Opens of W38 can likewise test chronology, even though they do not by themselves settle the club-origin conjunction. At 1094:53, H0 opens an alternate match window and H1 issues two speculative fixture searches plus one query combining goal timing and the 95th-minute clue.

The diagnostic does not establish that R1 qualification helped overall. Only one extra call was directly aligned by this review, and three H1 cells lost even a partial alignment; the response did not receive any returned evidence. The useful distinction for S1 is to project the **verification gap and suitable source type** without repeatedly naming a merely plausible candidate. R1's original failure and uncertainty about actual evidence gain remain intact.
