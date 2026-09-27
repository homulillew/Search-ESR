# Proposed next experiment: 2–3 decision Micro-Recovery

**UNEXECUTED / requires new explicit authorization under TASK.md §28.**
No API client, account key, paid retrieval or live BC+ rollout was used in this
implementation task. This is a proposed bounded feasibility diagnostic, not a
new OneGap exact-answer benchmark and not a causal ablation result.

## Design and selection

Six prefix-only states, two independent replicates each: **12 trajectories**, at
most **three Actor decision slots per trajectory**. READY may finish earlier.
Initial forced decisions consume a slot. A control error is deliberately injected
only in the specified first slot, logged as an intervention rather than scored
as a model-generated error. Later steps use the same clean loop and actual tools.

| Recovery channel | Candidate historical states | Frozen first-slot intervention | Main observation |
|---|---|---|---|
| R1 Bad OneGap | q1094 and q546 seed prefixes | one suboptimal repeated global search, full valid acquire decision frozen before calls | NoGain → materially different route; whether useful pending source is inspected |
| R2 Weak/wrong H | q637 F13/S01 and founder q228 F08/S01 | preserve the natural historical active candidate; first Actor is free | evidence → candidate downgraded/rejected/behaviorally abandoned, without false C |
| R3 Premature Closure | Euler q538 F11/S01 and memo q922 F16/S01 | explicit request_closure | real Closure CONTINUE → next Actor → suitable acquisition |

These are selected by known prefix mechanisms, not future answer correctness.
R2 candidates are weak, not pre-labeled globally false. If actual evidence does
not contradict a candidate, do not require a rejection to count the model correct.
R1 first action is suboptimal, not guaranteed to return NoGain; actual Gain and
irrelevant-Claim inflation must be retained. Escape after two NoGain attempts can
be observed in slot3. A next-step query paraphrase is not route escape.

The offline fixtures are selected projections. **Do not use the small fixture
corpus as live retrieval.** Before execution, restore and hash the authentic
prefix-visible Q/C/H and handle registry, pin original document bytes, and use the
Stage4 source-anchored skeleton for each question. For q546/q1094 a whole-Q R1 may
be frozen explicitly as the mechanical coarse scaffold (as in fixtures); do not
silently count it as a newly model-generated Stage4 D2 skeleton. Export only
prefix-visible material; no gold, future windows or final historical answers.

## Freeze before calls

Commit an experiment-specific freeze containing:

- repository HEAD, implementation/role-prompt/schema hashes and dependency versions;
- chosen prefix/checkpoint paths/hashes, Q/R/C/H, seed-support review and original
  document/window identity mapping; any source reconstruction limitation;
- all intervention decisions, independent replicate IDs and sample count;
- one fixed actual tool backend for all trajectories; proposed unchanged
  OrthogonalSearchFindTools to keep global discovery distinct from local inspection;
- provider `https://api.deepseek.com`, model `deepseek-flash`, generation parameters,
  thinking mode and all role output limits; these remain **unset until the paid
  experiment's preflight** and must not be inferred from historical defaults;
- three-slot horizon, no extra recovery rounds, review rubric, stop/failure policy,
  max retries **0**, budget ceiling and complete accounting fields.

Implement/review the live SemanticPort adapter only after authorization. It must
archive raw response IDs, model name, finish reason, status, usage and latency,
return just the strict role output to the loop, and never inject gold or auto-fix
action arguments. Freeze resulting code before the first experimental call.

## Parallelism and failure policy

Independent trajectories may run concurrently. With only 12, start at
`min(12, available account concurrency)`; maximum12. A synchronous loop can run in
a bounded 12-worker pool with an appropriately sized HTTP pool. Within each
trajectory preserve Actor → Observation → Reader → Grounding → H → next Actor.
No need for paid concurrency probing; no default historical 8/16 limit.
Use a separate retrieval semaphore, initial1, until existing backend capacity
supports a frozen higher value. No new encoder or GPU stress run in this phase.

Proposed transport settings to verify/freeze: connect30s, read900s, total1200s,
HTTP pool >=12. These are client choices, not a provider latency promise. SDK
max_retries=0. On timeout/429/503 terminate the affected trajectory and retain all
outputs; halve concurrency for not-yet-dispatched requests (minimum1), no increase
within this small batch, no replacement or best-of. Abort unsent work on local
resource exhaustion. Log every transition and actual peak concurrency. A serial
registry/evidence store belongs to exactly one trajectory; no cross-episode aliases.

Account-wide shared concurrency and user_id isolation follow AGENTS.md. Preserve
existing key/user isolation; never rotate keys to expand quota. Record input,
output, reasoning, cache hit/miss tokens, incomplete/inconsistent usage rows,
request failures, wall-clock time and latency distribution. Cache rate is
`sum(hit)/sum(input)` on complete internally consistent records, with coverage
reported. High concurrency does not imply high cache reuse.

## Evaluation and stop criteria

Annotate each step separately: OneGap usability, premise hardening, action
structural validity, action semantic suitability, tool execution, accepted Claim
usefulness/truth and evidence yield. Review claims/Closure against that step's
real prefix/observations; do not infer truth from a valid schema or citations.

Report trajectory-level NoGain route escape, H recovery, Closure-veto usefulness,
steps to first useful evidence, false C and false READY. For H behavioral escape,
next decisions must cease relying on the disputed premise; merely rephrasing it
is not success. For R3, CONTINUE alone is not recovery: the next OneGap/action must
address the feedback and yield progress or correctly exclude a route.

Premature Closure request is an efficiency cost. False READY, unsupported high-risk
C, or unsupported final assertions are safety/epistemic failures. Preserve local
true C while auditing global task completion. True-but-irrelevant Claim accumulation
is separately reported as Gain inflation.

This tiny diagnostic has descriptive denominators and reasons, no p-value gate.
Any observed false high-risk C or false READY stops expansion after recording the
failure; no in-run hot fix. If channels show recovery and no observed high-risk
failure, propose the next independent cohort; do not call this proof of general
safety. If not, localize the failed boundary before changing a prompt. No new state
fields, large accuracy cohort, retries or automatic rollout expansion.

## Cost ceiling

See CALL_ESTIMATE.json. Per acquisition: Actor1 + Reader<=1 + Grounding<=3 + H1,
so at most6 semantic requests. A forced first acquisition costs<=5 (no Actor).
A closure slot costs Actor1 + Closure1; READY adds Finalizer1 and terminates.
A forced first closure costs1 (or2 if READY and finalization). There are four
trajectories per recovery channel. The tight worst-case total is **192 semantic
requests**, **32 actual acquisition calls**, and36 decision slots. Failures/empty
observations reduce requests. This is a maximum, not a target to exhaust. Cost in
currency is not estimated without frozen token caps and then-current pricing.
