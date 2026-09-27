# Future experiments — proposed, not executed or authorized here

Current repair task paid_calls=0. The task's §34 explicitly limits this work to
offline repair, despite earlier standing API authorization. No remaining run001
budget is consumed or transferred. This document prepares a reviewable next step;
it does not launch it.

## H1: contract continuation diagnostic

- Same six frozen prefixes, two replicates each, three decision slots maximum;
  retain existing R1 repeated-Search and R3 Closure interventions.
- New directory, new freeze and raw logs; no overwrite of run001.
- **Result-informed; not independent confirmation.** Prompts were changed after
  observing these failures. Purpose: ensure the interface and nonfatal H boundary
  actually run with DeepSeek Flash outputs.
- Keep real Search/Find/Open, orthogonal semantics, Actor/Reader/Grounding/Closure/
  Finalizer unchanged. Only this H contract, skip and isolation repair varies.
- Primary execution checks: H schema/runtime violations; which were isolated;
  retained C/Gain; actual next Actor after H failure; mechanical skip counts;
  integrity failures. Also review direct versus local/global rejection and all
  new C/READY source support. Count failures, not replacement trajectories.
- Report actual NoGain route change, new evidence and claim progress descriptively.
  A clean interface run alone is not a recoverability mechanism pass.

## H2: independent recovery cohort

Only after H1 establishes executable interfaces without authoritative corruption.
Proposal: 12 **new** prefix/checkpoint cells, four each for NoGain recovery,
wrong-H recovery, and Closure-veto recovery; one trajectory each, three slots max.
Choose mechanically from eligible held-out checkpoints before any new model call,
without gold answers, future tool results or successful-continuation selection.
Freeze eligibility and selection order first; perform prefix-only review of seeds,
local facts, expected missing bindings and intervention validity.

If fewer cells qualify, report the shortage before freezing sample count; do not
silently backfill with H1 prefixes. A checkpoint whose trajectory was used to design
the repair is not an independent confirmation cell merely because its ID differs.

Review model behavior separately from interface success:

1. NoGain reaches a new Actor; distinguish query paraphrase from a changed route.
2. Wrong H is tested and revised without unsupported C or premature global REJECT.
3. Closure CONTINUE leads to a usable new OneGap and grounded progress when possible.
4. Useful evidence/Claim yield and false C/READY; no final-accuracy large cohort.

No new persistent fields, semantic admission layer or hard gating proposed.
If interface execution still fails, diagnose that boundary before expanding H2.
If semantic H quality is poor but isolation works, report those as separate results.

## Freeze and resource policy for either future batch

Before first paid request, pin runtime HEAD, provider/model parameters, prompt and
schema hashes, prefix/Q/R/C/H/T/evidence hashes, source snapshot, selection/review
rubric, intervention schedule, sample count, horizon and failure policy. Recheck
the endpoint/model identity using authorized experiment requests, not extra probes.

- Proposed provider/model: https://api.deepseek.com / deepseek-flash.
- Proposed existing decoding settings: temperature 0, thinking enabled/high,
  max_tokens 32768, JSON object; final values must be frozen anew.
- max_retries=0; no replacement, automatic correction or output overwrite.
- Each phase has 12 independent trajectories: initial and maximum API concurrency
  `min(12, available shared-account capacity)`. Dependencies within a trajectory
  remain sequential. This follows min(pending,256,capacity); 12 is the number of
  independent requests available here, not a provider limit or inherited default.
- Use asynchronous transport and matching HTTP connection capacity. Shared account
  budget remains <=2400 under AGENTS.md, with at least 100 nominal slots reserved.
- On timeout/429/503 or resource congestion, halve concurrency for unsent requests,
  minimum 1; preserve failures without retry. Log concurrency changes and reasons.
  No ramp above 12 is useful for these proposed cohorts.
- Proposed timeouts: connect30/read900/write60/pool30/total1200 seconds. Preserve
  existing user_id behavior; no key/user rotation for concurrency or cache gains.
- Retrieval starts at one concurrent backend call, increased only if actual GPU
  capacity permits and frozen policy allows. No extra paid load test.
- Record input/output/hit/miss tokens, missing/inconsistent usage records, failure
  counts, peak concurrency, wall time and latency distribution. Compute cache rate
  as sum(hit)/sum(input) only over complete consistent records.

See [CALL_ESTIMATE.json](CALL_ESTIMATE.json) for conservative future ceilings.
These are proposals, not permission to run or spend an old budget.
