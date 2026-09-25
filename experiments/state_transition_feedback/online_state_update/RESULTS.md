# T3 — Online bridge-state construction

All 12 frozen DeepSeek calls produced schema-valid proposals with no retries. The single-reviewer offline labels in `REVIEWS.json` apply the pre-frozen `REVIEW_RUBRIC.md` to all 21 proposals. Labels do not alter model output.

| Diagnostic | Result |
|---|---:|
| Complete-claim source support | 18/21 = 85.7% |
| Decision relevance | 19/21 = 90.5% |
| Both supported and relevant | 16/21 = 76.2% |
| Oracle binding recovered, stage-local | 8/12 = 66.7% |
| Incidental or marginal proposal | 2/21 = 9.5% |
| Over-specific / false evidence promotion | 3/21 = 14.3% |
| Next-Gap answer asserted absent from observation | 0/21 |

The strongest positive behavior is `U1_B05`: instead of copying the incorrect frozen oracle candidate, the updater checks the source's three writers, Canal 13, and 1967–1996 run against the original question and proposes two evidence-backed exclusions. This is a useful online correction, but it exposes an invalid T0 transition. In `U1_B03`, the proposal says Oliver Mtukudzi matches all question clues, while the observed window only establishes age and broad album career. In `U1_B07`, wealthy family background is incorrectly treated as disproving showbiz-derived wealth. In `U1_C11`, the article date is promoted to an exact match date. These are the three complete-claim support failures.

The “target leak” rubric above tests whether a proposal invents the next-Gap answer **absent from the observation**. A separate original-question integrity audit found that six observations already expose the original requested answer, and two more cases have contradicted candidates. Thus the 8/12 stage-local binding recovery does **not** mean that eight valid research transitions were learned. At most four cases across two qids remain provisionally interpretable, below the execution floor. Among those four, five of six proposals are source supported and three of four stage-local oracle bindings are recovered; this tiny subset is descriptive only.

DeepSeek reported 2,048 cache-hit and 8,263 cache-miss input tokens (19.86% cache-hit share). The offline review provides a diagnostic of claim quality, not an online acceptance filter or a production Claim Admission result.
