# F2 Top1 versus parallel Top2 Find

Because both document-policy gates failed, F2 used historical U1 G top5 ranking **only as a diagnostic**. It cannot be selected for deployment. Each case predetermined rank1 and rank2 D before either Find; both Find calls ran in parallel with the same frozen query. P1 is the rank1 call; P2 is the two-call batch. Raw windows and audits are in `policy_find_events.jsonl`, and every returned W has a single-reviewer judgment and reason in `REVIEWS.json`.

| Outcome | P1 rank1 | P2 rank1 + rank2 |
|---|---:|---:|
| Useful-W hit | 24/40 (60.0%) | 26/40 (65.0%) |
| Fully sufficient W hit | 23/40 (57.5%) | 24/40 (60.0%) |
| A useful hit | 9/12 | 10/12 |
| B useful hit | 4/8 | 5/8 |
| C useful hit | 6/12 | 6/12 |
| D useful hit | 5/8 | 5/8 |
| Useful W per Find call | 24/40 (60.0%) | 29/80 (36.25%) |

The second D rescued two P1 useful misses: A11 q186 returned an Albino Frog publisher statement for Galacta but with a conflicting 1993 release date, so it is **partial useful**, not fully sufficient for the frozen November 1992 Gap; B06 q186 found the planned “Last Stand on Mars” episode and is fully sufficient. The extra rank2 W was useful in only 5/40 calls; 35/40 yielded no useful fact for the current Gap. P2 gains 5 percentage points in case-level useful hit but loses 23.75 percentage points of useful W per call. It fails both frozen selection conditions (gain must be at least 10 points; per-call loss at most 5 points). **Top2 is not selected.**

Source and window matter independently. In C04 and D03/D04, the final 2014 Enugu Rangers table is among the ranked D, but Find misses its row and lands on early rows or a “days as leaders” table. D03/D04's rank1 alternative is a 37-match interim table showing sixth place, while the frozen final table has 38 matches and eighth place; the interim position is not a valid final answer. In C10, a film cast page returns a list of role names including “Policeman 1” without the actor-to-role mapping. These are not useful-W hits under the frozen Gap rubric. D01's rank1 “more than 60 albums” passage likewise does not establish Forbes Africa's exact count of 65.

The diagnostic ranking and case selection were frozen before the calls. This comparison is paired and descriptive for the 40-cell cohort; it does not establish an independent policy effect in a new cohort.
