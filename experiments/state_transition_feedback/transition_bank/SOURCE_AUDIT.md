# T0 source-set audit

Before any new model call, the reviewer checked the historical direct documents, the previous S1 top50 candidate pool under S0/S3, and known duplicate pages. `SOURCE_REVIEWS.json` preserves each admitted document's ID, URL, full-text hash, role, and the candidate-pool size. The frozen primary `DirectSourceSet` is the union of the old canonical set and only manually confirmed alternatives. This is expanded known truth, not a guarantee that all 100,195 documents were read.

| Case | Added direct documents | Reason |
|---|---|---|
| B03 q435 song | D70761, D79895 | Both name Wasakara and link its interpretation to Mugabe's retirement/age. |
| B04 q1094 match goal | D70117, D82883 | Both identify Neymar as PSG's second scorer in the Lille match. |
| B05 q311 magical object | D53641 | The Hijitus page says the hat `sombreritus` carries the transformation power. |
| B06 q186 episode | D51927 | Explicitly lists `Episode 2: Last Stand on Mars`; this was the prior S0 rank-3 omission. |
| C05 q177 2016 winner | D86072 | Rangers club history explicitly says Enugu won the 2016 league. |

The old q435 C01/C03 sets already contain D56154, D48151, and D51535; their body text ties the 65-album count to the 2017 Forbes feature/listing. The q517 cast-list D63369 has `Policeman 1` but does not link that role to Peter King, so it is **not** direct. The q1094 news item D78668 mentions a Neymar goal but does not explicitly identify it as PSG's second goal, so it is excluded from frozen direct truth. The q546 maximum-break article D64519 gives Ding's count but not his professional-start year and cannot close the combined Gap.

Bridge-only documents are audited separately. D43080 identifies Peter King through family and film clues without his exact Constant Gardener role. D2855, D22411, and D20115 identify Galacta and its DOS/game context without the second-episode name. The historically observed D43657, D86819, D78633, and D84118 can bind their respective unresolved referents before the next answer; some are also direct documents when later sections are considered, and that overlap is explicit in `PRIVATE_TRUTH.json`. A related article without a verified variable binding is not in the bridge set.

Any newly discovered answer-bearing source after retrieval will be shown in a separate semantic any-sufficient sensitivity audit; it will not be added to the frozen primary set.
