# One bounded exploration: A, narrower Frontier wording

## Trigger and boundary

F1 fails: S18/48valid, four repaired critical checkpoints across3qids. Premature STOP is the largest failure class; no allowed exploration direction directly changes closure rules. A separate substantial observed failure is breadth:26/76structurally valid ACTs carry `over_broad` (flags can overlap). This exploration addresses **only that secondary failure**, not the primary STOP bottleneck or overall sufficiency qualification.

Choose permitted direction A once. Append exactly:

> Choose the smallest currently useful unresolved research question.

No other prompt change. No new field, schema, state cleaning, tool, Writer or provider change. This cannot promote the failed primary gate or authorize F2–F4.

## Mechanical selection and paired design

Take every distinct F1 checkpoint with at least one over-broad output. There are9: F02,F05,F13,F17,F18,F19,F20,F21,F22, spanning5qids. For each, select one input view using fixed priority S then H then SH among views with at least one over-broad output. Selection is explicitly failure-conditioned, not held out.

Each selected exact view gets two fresh single submissions: A0original prompt, A1same prompt plus the single sentence.18Frontier calls total,9checkpoints, one replicate per condition, no tool. Fresh A0 is required to expose resampling/regression-to-mean effects; the selected unfavorable F1 response is not the causal comparator. Requests are hash-shuffled, workers4, JSON mode, provider defaults, timeout240HTTP operation waits, retries0, no replacement. All failures retained.

## Frozen evaluation

Reuse original question-derived Requirement Map, per-view coverage and semantic rubric without relabeling. Mask condition IDs while reviewing actual views/outputs. Primary diagnostics are paired valid decisions, over-broad outputs, and critical failures (premature_stop/drift/unsupported_premise). Positive descriptive signal requires fewer broad outputs, no lower valid count and no higher critical count than fresh A0. No p-value threshold, tuning sweep or claim that9selectedcheckpoints prove generalization. Report any migration from broad Needs to unsupported specific premises or premature STOP.

Freeze exact selected views, requests, prompt change, analysis inputs, sample count18, horizon1 and failure policy in `exploration/freeze.json`, commit, then call. This is the only exploration. F2–F4 stay unmeasured regardless of outcome.
