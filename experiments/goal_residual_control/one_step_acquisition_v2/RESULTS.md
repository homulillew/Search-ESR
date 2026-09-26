# G3v2 real one-step acquisition

All 157 valid proposed actions executed: 149 Search, 6 Find, 2 Open. Two upstream Actor schema failures remain failures; STOP sends no tool call. No retry or backend change.

| Arm | Any Progress / 40 planned | Direct | Decision | Acting No Progress | Tool calls | Calls / Progress |
|---|---:|---:|---:|---:|---:|---:|
| A0 State-only | 18 | 15 | 5 | 5/23 | 45 | 2.50 |
| A1 Derived Residual | 19 | 16 | 5 | 10/29 | 58 | 3.05 |
| A2 Historical Gap | 21 | 18 | 7 | 6/27 | 54 | 2.57 |

Direct and Decision can overlap. All arms have 33 open frozen snapshots. Correct stops are included in the planned denominator but are not failures of acquisition. Conditional progress by tool and valid/open/acting denominators are in progress_metrics.json. Search progress is 21/45, 21/54, 23/50 respectively; Find 0/0, 1/3, 2/3; Open 0/0, 1/1, 1/1. The sparse inspection sample does not establish tool superiority.

A1's reduction in premature stopping does **not** translate to the highest primary Evidence Progress: 19 versus A0 18 and A2 21, with higher cost. This is a mixed result, not a reason to stop G4/G5. The 40 cells cluster in only 10 questions.

Second actions add a distinct primary fact in 5/22, 8/29, 7/27 batches. One A2 second action only repeats the first action's qualifying fact; most others have no qualifying new primary fact. Exact repeated action objects within a batch: zero. These counts describe observed incremental yield; there is no randomized one-action control proving net causal benefit. Orthogonal discovery suppresses already-discovered source previews.

## Review and boundaries

Single Codex reviewer used arm-hidden packets and exact returned windows, original Q, committed Claims and frozen residual. Explicit belief updates and next-decision implications are in progress_reviews.json and analysis_v2/FACT_DEFINITIONS.json. Primary positives require both frozen pool membership and actual novel support. Known-pool windows were read in full. Primary nonpositives include unrelated portions of a correct document (e.g. 2013 Ding sequence), already committed facts, and unsupported joins. Observed but uncommitted facts can still reduce the Claims-based residual under the unchanged rubric.

A separately identified alternative-source sensitivity adds the Neves match, Cococinel, developer company history, director links and the British Open route. Its Any Progress counts are A0=20, A1=25, A2=25. Outside-pool sources were screened by title/topic with full-text follow-up for plausible candidates; this is a **non-exhaustive lower-bound sensitivity**, not an exhaustive corpus audit or revised primary truth. EVIDENCE_LABELS records review depth. No production model saw these annotations.

Examples: Galacta's explicit developer/former-name link is new support; the 2015 Mtukudzi interview quote can satisfy the strict quote requirement; Peter Nzioki's 1979 category creates an unresolved conflict with the existing 1978 claim. Neither the lifetime 67-album retrospective nor a 2016 interview alone supports the May 2017 count.
