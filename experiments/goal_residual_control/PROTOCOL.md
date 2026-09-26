# Goal Residual Control

Base: `experiment/state-transition-feedback`, `2d0c55995badd14ab4bc8241ca9caa97a1eef3a1`.
Branch: `experiment/goal-residual-control`. Historical experiments are read-only.

## Material passport

This is an empirical harness experiment, not a literature review. Source material is the archived real BC+ observations, model reasoning, actions and tool results identified in `bank/`. Reviewer-normalized replay states are explicitly distinguished from native historical model states. Original questions are authoritative. No answer key is used in production inputs. The original task is the user attachment dated this session; its three production prompts are copied verbatim.

## Invariants

Persistent semantic state contains Question, Verified Claims and Working Hypothesis. Goal Reviewer sees exactly Question and claim statements. Hypothesis never enters that request. Residual is recomputed after semantic mutation; Gap and action are ephemeral except in the explicit legacy comparator. Claims proposed online are retained as-is, including errors, with observation provenance; the word Verified in production is an architectural intention, evaluated independently afterward.

No hard gating, dependency ordering, retriever/localizer changes, prompt tuning, new schema beyond the requested three roles, query repair, sample replacement, retry or best-of. Search/Find/Open remain the historical Orthogonal implementation and schema. The JSON Actor interface uses those same argument schemas. Before either action in a batch, all D/W arguments must exist in the pre-batch workspace. Invalid batches fail without partial execution.

## Ordered stages

1. G0: 40 snapshots, 20 source-backed transitions, 10 qids. Selection and reviewer truth committed before calls.
2. G1: one Goal Reviewer call per snapshot, 40 planned calls; no tools.
3. G2: A0 state-only, A1 actual G1 residual, A2 historical gap; one Actor call per cell, 120 planned calls. All common fields identical. A1 inherits an invalid reviewer result as failure, never repaired.
4. G3: execute every valid G2 action, at most two independent actions; stop produces no tool call. One frozen round. Progress assessed against Original Question and current Claims, never local Gap alone.
5. G4: each of 20 transitions is replayed from the same pre-state. For batches with several real windows, updater processes windows in recorded order, one source per updater call, max two new claims per source. R0 online-post+historical gap; R1 online-post only; R2 oracle-post+Goal Reviewer; R3 online-post+Goal Reviewer. Each arm gets one decision and actual tool execution. No counterfactual manual repair.
6. G5: 10 qids (one deterministic starting snapshot per qid), L0/L1/L2, three decisions per arm, max two independent actions per decision. Selection: earliest POST snapshot per qid, except q580 uses T14_PRE (real near-resolution state), q435 uses T19_POST (real unsupported-join trap). Every returned source window gets an updater call. L0 persists historical gap until its Actor chooses a new gap. L1 replans from state. L2 recomputes goal review initially and after semantic mutation, stops immediately on resolved=true. An Actor stop in any arm is independently evaluated. No final answering call.

G1–G5 always continue regardless of effect size. Only serious integrity failures (clean cases<8, qids<5, irreparable leakage>25%, valid API/tool calls<80%, source truth unavailable) permit a stop, documented with denominator. Effects are descriptive with paired cell and qid summaries; repeated snapshots from the same qid are not independent trials. No p-value claims.

## Freeze and failure policy

Each stage has committed inputs or a committed deterministic adaptive-input construction policy, hashes, prompt/schema hashes, provider, sample count/budget, case/arm order and failure rules before real calls. Dynamic G4/G5 requests are journaled before submission. Raw successes and failures are retained. DeepSeek `deepseek-flash`, timeout 240s, `max_retries=0`, concurrency at most four. A submitted request is never resampled, even after timeout. Invalid outputs remain failures; downstream dependent branches fail rather than inventing a state/residual. Tool failures are archived. No hidden online source audit informs Actor or updater.

Execution uses GPU1 when memory permits; GPU0 is also authorized. Device choice does not change search semantics. Cache accounting uses sum(reported hit tokens)/sum(hit+miss), with missing/inconsistent usage separately reported.

## Evaluation boundaries

See `REVIEW_RUBRIC.md`. Codex performs source-grounded semantic review with arm labels withheld in exported review packets. This is a single reviewer in the same overall session, not independent human replication or a claim of perfect cognitive blinding. Maps are unmasked only for aggregation. New alternative sources may enter a separately reported sensitivity audit; frozen primary source truth is never rewritten. Document membership alone cannot count as progress.

The closure policy requires enough discriminative evidence to identify the requested entity and support the requested relation, not mechanical verification of every incidental clue. q435 is ambiguous under a stricter all-clues reading: frozen sensitivity treats its four resolved snapshots as open because the exact interview quote is absent. Both interpretations must be reported. q517 has an explicit unresolved birth-year/Goat inconsistency; no name-only closure. No claim that all 40 snapshots are distinct natural trajectories.
