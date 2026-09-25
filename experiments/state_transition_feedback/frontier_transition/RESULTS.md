# T2 — State–Frontier compatibility

**Post-T3 integrity qualification:** `transition_bank/POST_T3_INTEGRITY_AUDIT.md` found eight frozen transitions invalid for the full original-question feedback hypothesis. The 11-case “clean” metric below only excludes the issue known before T1 and should be read as a *conditional next-Gap diagnostic*. At most four provisional cases across two qids remain, below the execution gate. Frozen primary truth and outputs were not rewritten.

All 12 F_EARLY calls parsed and all 12 searches completed. F_PREMATURE is the exact T1 PRE query and retrieval record, with no resampling. `U1_B07` remains an invalid question-to-candidate transition and is excluded from the clean causal cohort (11 transitions, 8 qids).

| Cohort / arm | Progress@1 | @3 | @5 | @10 | @20 | @50 | First-progress MRR@50 | NoProgress@5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Clean F_EARLY | 1/11 | 2/11 | 3/11 | 4/11 | 6/11 | 7/11 | .1676 | 8/11 |
| Clean F_PREMATURE | 4/11 | 6/11 | 8/11 | 9/11 | 9/11 | 9/11 | .5114 | 3/11 |
| All F_EARLY | 1/12 | 3/12 | 4/12 | 5/12 | 7/12 | 8/12 | .1814 | 8/12 |
| All F_PREMATURE | 4/12 | 6/12 | 8/12 | 9/12 | 9/12 | 10/12 | .4710 | 4/12 |

The clean frozen-set F_EARLY contrast is **Negative**: −5/11 = −45.45 percentage points Progress@5. Paired first-progress rank favours F_PREMATURE in six cases, F_EARLY in three, with two ties. This is a source-set and task-specific diagnostic, not a general claim that premature research is preferable. A post-retrieval source audit identifies one credible omitted early bridge source (D70761 at rank 2 for `U1_B03`); counting it separately gives semantic F_EARLY Progress@5 of 4/11, still below 8/11. See `ALTERNATIVE_SOURCE_AUDIT.md`.

The mechanism is partly that the original question already contains enough distinctive material for a downstream search, while early query writing from an unbound state often copies many raw clues. The clean F_EARLY query lexical clue-load proxy is .549; the T1 PRE/F_PREMATURE proxy is .2668, although these are different Gap conditions and the proxy is only descriptive. Case examples: `U1_C07` F_EARLY copied a long season-plot list and first frozen bridge source ranked 47; F_PREMATURE reached a direct source at rank 1. `U1_B05` F_EARLY guessed a wrong programme. The source set and one-query budget also favour documents that answer the downstream Gap directly. This stage rejects a universal “always search the earliest Gap first” rule, while retaining the need to bind referents before accepting downstream claims.

DeepSeek reported 2,048 cache-hit and 2,526 cache-miss input tokens for the new F_EARLY calls (44.77% cache-hit share). No T2 call was retried or repaired. The weak early-frontier result is an evidence-strength finding; per protocol it does not block T3–T5.
