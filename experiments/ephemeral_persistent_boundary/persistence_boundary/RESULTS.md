# S2 persistence boundary results

The pre-call bank contains 40 controlled slot challenges from exact historical
Observation text across 11 qids: P1 9, P2 5, P3 4, P4 7, P5 11, P6 4. The
ephemeral query and four stale old bindings are seeded interventions. Several
cells reuse the same W with a different Test relation. They measure whether
the boundary promotes a query guess, not whether the whole original question
is solved. This is a single fixed sample, with no retries or best-of.

All 120 Binder and 72 semantic Verifier calls succeeded. The request audit
confirms the query field is absent from all 80 I/X Binder requests and all
72 Verifier requests. Every Binder proposed exactly the 24 correct supported
values and none of the 16 no-binding values. All 72 proposals passed the
Verifier; there was no mechanical or semantic rejection to study.

| Measure | L | I | X |
|---|---:|---:|---:|
| False-proposal cases | 0/40 | 0/40 | 0/40 |
| Committed precision | 24/24 | 24/24 | 24/24 |
| Binding recall | 24/24 | 24/24 | 24/24 |
| False promotion in P2–P4 | 0/16 | 0/16 | 0/16 |
| P4 NoGain state preservation | 7/7 | 7/7 | 7/7 |
| P5 alternative recovery | 11/11 | 11/11 | 11/11 |
| P6 seeded-conflict replacement | 4/4 | 4/4 | 4/4 |
| Value equals prior query guess | 9/40 | 9/40 | 9/40 |

The nine equal-value proposals are all P1, where the new W itself supports
the value. Equality with a prior guess is not evidence that query content
contaminated the Binder: I and X never saw the query and produced the same
value from W. Weighted DeepSeek prompt-cache hit rate was 10.8% for Binder
calls and 43.5% for Verifier calls; this is operational telemetry.

**Gate: FAIL.** X met the six absolute performance thresholds, including
4/4 conflict recovery, but did not produce the required six paired reductions
in false proposals or promotions versus L (0 improvements, 0 worsenings).
This sample gives no causal evidence that isolation or extractive rejection
improves over the explicitly cautioned L prompt. It also gives no evidence
that the Verifier or mechanical gate is unnecessary in harder cases, because
neither encountered a wrong proposal. Per protocol, S3 and S4 were not run.
