# P3: timing of one active AtomicNeed

This stage begins only after P1 and P2 complete. Select eight checkpoints
prospectively from the historical prefix-only annotations and original
checkpoint IDs: qid 546 seq 17/25/33/41, and qid 1094 seq 45/53/69/77.
They contain candidate-specific verification, source-type distinction, or
search observations that can motivate a new subquestion. These IDs are fixed
before any P3 model call; no gold or future trajectory is used for selection.

At each checkpoint, A0 is the existing broad evidence-conditioned M1 plan and
P1 handoff response, reused without resampling. A1 is one question-only
AtomicNeed generated *once per qid* and reused unchanged at all four selected
checkpoints for that qid. A2 is a new evidence-conditioned AtomicNeed generated
independently at each checkpoint. The A1 planner receives only the original
question; A2 receives the exact current prefix. Both may return `none`, and
both must express at most one active atomic need. Neither receives tools.

For each selected prefix, A1 and A2 actor requests use identical historical
messages, model, and Search/Find/Open menu; only the descriptive control card
differs. Each arm gets one actor response without tool execution. No best-of,
prompt repair, Source repair, or selective retry. Compare premature commitment,
need fidelity/granularity, source compatibility, scope/target realization,
and concrete D# quality separately. Evidence gain is unobserved in this
one-step phase; a short rollout is contingent on a clear A2 signal.
