# H1 — contract continuation diagnostic

Authorization: user “授权，后续你自己直接调用就行了不用我授权”. This supersedes
the completed repair task's no-live-call boundary. It also authorizes subsequent
in-scope research calls without asking again, subject to gates and sample budgets.
Historical repair CALL_ESTIMATE and zero-paid-call report remain unchanged.

## Design frozen before new model calls

- Parent repair result: 3fdb19bc, implementation 4e91b59c; new research branch
  experiment/recoverable-loop-h-continuation.
- Same six byte-identical historical prefixes and interventions, two replicates
  each; 12 independent trajectories, <=3 decision slots, <=192 paid requests and
  <=32 actual tool acquisitions. No replacement or retry; max_retries=0.
- R1 q1094/q546 forced exact previous Search; R2 q228/q637 free Actor with the
  original H; R3 q538/q922 forced request_closure. Forced decisions consume a slot
  but no paid request. Every later Actor is free, all tools available.
- **Result-informed diagnostic, not independent confirmation.** Same-cell results
  can show interface execution but cannot establish an unbiased recovery effect.
- Engine, role prompts and schemas from the repair are unchanged. Full Q/R/C/H/T
  and all observed D/W retained. OneGap remains ephemeral. Tools and orthogonal
  semantics unchanged. No hard gating or hidden ref translation.
- Reader/Grounding/C chain precedes optional H. H skip/failure events and separate
  acquisition/claim/auxiliary outcomes are measured. Failed H cannot revoke C or
  manufacture READY; true integrity errors remain fatal.

## New transport adapter

The historical transport checks every output schema before returning to the role
engine. That would classify H schema errors as provider exceptions and hide their
raw strings from engine role_response logs. This batch's transport returns final
H content verbatim, leaving H parse/schema/existence validation to the repaired
engine. HTTP, model identity, finish reason and nonempty-content checks remain;
other roles retain their old transport validation. No model output repair occurs.
Mock integration tests cover invalid H through HTTP → engine → next Actor.
Historical transport and run001 artifacts are untouched.

## Resources and failure policy

DeepSeek Flash parameters in CONFIG.json: temperature0, thinking enabled/high,
max_tokens32768, JSON object, no user_id change. No separate paid probe.
12 independent next requests imply initial/max concurrency12, consistent with
min(independent requests,256,available account budget). This run has no other known
Search-ESR API batch; external account load cannot be observed directly. Async I/O,
12 HTTP connections, retries0, connect30/read900/write60/pool30/total1200 seconds.
Record peak/changes, per-request raw response, latency and usage. Timeout/429/503
halves unsent concurrency to minimum1, no automatic retry or new sample. HTTP
400/401/402/403/404/422 or model mismatch halts unsent model work. Existing in-flight
results are preserved. A H provider/output error alone is auxiliary; higher-authority
role errors and integrity failures terminate their trajectory. No prompt tuning
mid-batch. No unused old budget is transferred.

GPU0 was free at preflight; GPU1 has unrelated work. Load the unchanged local
BCPlusSearcher on GPU0, serialize shared-model retrieval, and overlap it with API
work. Thread-local tokenizers/DB and episode-local registries prevent cross-episode
leakage. Verify original full-document hashes and source spans before calls; full
unobserved source text stays local and is not role evidence. Pin ignored BC+ source
against the previously committed identical snapshot. Freeze binary file size/mtime
metadata as in the original run.

## Review rubric and H2 gate

Codex single-reviewer, unblinded, source-relative review. No gold/future source or
final answer used to judge earlier decisions. Every new Claim reviewed against its
actual supporting observations; every H proposal reviewed for namespace/existence,
direct contradiction versus local/global mismatch, conjecture presented as fact,
and candidate churn. Every Closure reviewed against Q/R/C/evidence. No paid reviewer.

Record per decision: usable OneGap, premise hardening, action/source compatibility,
new useful raw evidence, supported/useful C, H correctness, NoGain route change
(paraphrase alone does not qualify), and response to Closure missing feedback.
Keep forced decisions and free Actor decisions separate. Runtime Gain is not a
semantic recovery score. R2 can be inconclusive without contradictory evidence;
three-slot horizons do not establish final-answer accuracy.

Primary H1 checks: executable trajectories, namespace failure rate, isolated H
failures and following Actor opportunities, H skips, C/Gain preservation, fatal
integrity errors. No arbitrary p-value gate on this six-cell diagnostic.

Enter H2 only if this review establishes executable repaired interfaces and no
authoritative corruption (including confirmed false new C or false READY). H-only
semantic weakness is reported separately and cannot be hidden by clean formatting.
If blocked, record the exact failure and a bounded next repair proposal; don't
spend H2 budget on replacements or tune H1 after seeing outputs.

H2 remains conditional: 12 new held-out prefixes/checkpoints, four per recovery
family, one replicate, three slots, <=192 calls. Freeze eligibility and mechanical
ordering before inspecting candidate outcomes. The six H1 questions and repair
counterexample trajectories are excluded; a changed checkpoint in a used trajectory
is not independent. Review only its prefix. If the available bank is insufficient,
report the shortage; no silent backfill. H2 selection/freeze must precede H2 calls.

## Accounting

Report attempted/not-sent/failed requests, role counts, total input/output/cache
hit/miss, missing/inconsistent usage counts, cache rate=sum(hit)/sum(input) over
complete consistent records, latency distribution, peak and actual concurrency,
wall time, step outcomes and review denominators. Retain all failures and byte
hashes. Store all new outputs in this directory; historical run001 is immutable.
