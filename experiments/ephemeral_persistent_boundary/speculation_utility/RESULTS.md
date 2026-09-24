# S1 actual retrieval results

The 48 frozen V2 queries and all 23 mechanically de-speculated variants were
executed once against the unchanged local BC+ Search stack (top 5). All 71
Search cells succeeded. A single reviewer used the frozen, arm-masked top-five
preview rubric; no full-document audit or later trajectory was used. `REVIEWS.json`
contains each decision and reason, and `results.json` contains the paired IDs.

| Original V2 arm | Suitable source | Useful evidence | Direct unknown resolution | NoGain |
|---|---:|---:|---:|---:|
| Q0 (16) | 7 | 3 | 2 | 9 |
| Q1 (16) | 7 | 5 | 2 | 9 |
| Q2 (16) | 8 | 4 | 2 | 8 |

Of 23 original speculative-query versus deletion pairs, suitable source
favored S in 1 and D in 2 (20 ties); useful evidence favored S in 1 and D
in 3 (19 ties); direct unknown resolution favored S in 1 and D in 0 (22 ties).
The original speculative value was supported in the required relation in
5/23 pairs. Mean top-five document-ID overlap was 2.78/5.

The one S-only direct resolution was the Jimmy/Gretchen season-one scene:
the series-specific query retrieved `Insouciance`, whereas its de-speculated
generic episode-guide query returned other series. In contrast, removal of
`Oliver Mtukudzi` sometimes surfaced the May Forbes Africa list or related
album-count article. That source supports an *alternative* to provisional
Miriam Makeba; it does not prove that the Forbes feature itself reported 65
albums. The 2014 Nigerian league table exposed Rangers' 58 points and +8,
but did not establish the question's tied-points season. Incidental John
Higgins/Ronnie mentions in a Ding article did not prove the later-match chain.

Thus speculative wording can help, be neutral, or narrow retrieval badly.
These are descriptive correlated cells from eight qids, not an estimate of
population-level query quality. A retrieved name is never a persistent binding.
