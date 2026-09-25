# T1 — Oracle bridge-state effect

**Post-T3 integrity qualification:** `transition_bank/POST_T3_INTEGRITY_AUDIT.md` found that eight of the 12 frozen transitions either already expose the original requested answer or use a contradicted candidate. The 11-case cohort below only excludes the issue known before T1; it is a *conditional next-Gap retrieval diagnostic*, not a clean causal cohort for the original-question feedback hypothesis. At most four provisional cases across two qids remain, below the execution gate. The requests, primary truth, and numerical results below are preserved without relabeling.

All 36 frozen DeepSeek calls parsed successfully; Search returned 50 documents for each query with no retrieval error. The primary any-sufficient truth set was frozen in T0. `U1_B07` has a question-to-candidate mismatch documented in `transition_bank/PRECALL_GAP_AMENDMENT.md`; it remains in the raw record but is excluded from causal interpretation. The clean cohort has 11 transitions across 8 qids, above the execution floor.

| Cohort / arm | Direct@1 | @3 | @5 | @10 | @20 | @50 | MRR@50 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Clean PRE | 4/11 | 6/11 | 8/11 | 9/11 | 9/11 | 9/11 | .5114 |
| Clean POST | 10/11 | 10/11 | 11/11 | 11/11 | 11/11 | 11/11 | .9318 |
| Clean RAW | 10/11 | 10/11 | 11/11 | 11/11 | 11/11 | 11/11 | .9318 |
| All PRE | 4/12 | 6/12 | 8/12 | 9/12 | 9/12 | 10/12 | .4710 |
| All POST | 10/12 | 10/12 | 11/12 | 11/12 | 11/12 | 11/12 | .8542 |
| All RAW | 11/12 | 11/12 | 12/12 | 12/12 | 12/12 | 12/12 | .9375 |

On the clean cohort, POST raises Direct@5 by 3/11 = 27.27 percentage points. Six paired first-source ranks improve, none worsen, and five tie; these improvements span six qids. This is **Strong** by the preregistered descriptive rule. The all-case POST difference is +25 points, with six improvements, one worsening, five ties. The lone worsening is the invalid `U1_B07` transition. The case-by-case query and rank record is in `CASE_ANALYSIS.md`.

The clean POST query includes the bridge candidate in 11/11 cases versus PRE 2/11; the latter two are unsupported guesses, rather than observed bindings. The lexical clue-load proxy falls from .2668 to .0500. The relation lexical-coverage proxy falls slightly from .5313 to .4958, so the gain should not be described as greater lexical relation coverage. RAW and POST tie on clean any-sufficient ranks. POST uses 4,275 prompt tokens across the clean cohort, versus RAW 8,776 (51.3% fewer). DeepSeek reported 5,504 cache-hit and 13,412 cache-miss input tokens across all T1 calls, a 29.1% hit share; this is descriptive API usage, not an arm effect.

Canonical-only ranks differ from any-sufficient ranks, confirming that a single target document would understate retrieval quality. On the clean cohort canonical @5 is 8/11 PRE, 11/11 POST, 11/11 RAW; canonical MRR is .4841, .8182, .7727. These are secondary because the expanded source set was frozen before the calls.

The observed mechanism is a more often grounded referent and shorter query, with better direct-source routing. This one-step oracle probe does not establish online updater reliability or a full feedback loop. All queries, failures, retrieval hits, and frozen request hashes remain in machine-readable artifacts.
