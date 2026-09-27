# Micro-Recovery run001 — frozen protocol

## Material Passport

Mode: experiment execution; source: clean Stage4 loop at a583e9ef; author: Codex;
user authorization: “我授权，并行调用吧”; scope: six fixed prefix states, two
independent replicates, <=3 decisions each. No sample replacement, prompt tuning,
retry, vote, action repair or extra model reviewer. Codex conducts prefix-relative
semantic review after this bounded batch. Such review is single-reviewer,
unblinded to trajectory order, and does not establish a causal comparison.

## Design

Follow ../NEXT_EXPERIMENT_PLAN.md and its192-request/32-acquisition ceilings.
R1 uses the exact last historical Search on q1094/q546 and the historical reviewed
active gap; it tests a suboptimal action, not necessarily a wrong gap. R2 uses
literal weak historical H on q228/q637. R3 forces request_closure on q538/q922.
A forced decision uses a deterministic port response and is archived as an
intervention; it consumes a slot but no model request. All subsequent choices
are free. Each trajectory receives its own state, handles, tokenizer and DB
connection. No tool is masked. Finalizer runs only after actual Closure READY.

The complete prefix-observed registry is restored, not the offline fixture
projection. All90 document entries /118 windows across the six cells are checked
against original full document hashes and exact offsets (repeated documents count
per cell). Original full text stays local; only prior observed windows or newly
returned real windows reach roles. D/W aliases and historical canonical refs are
preserved. A new backend span may receive a new canonical alias, never replace an
old W's bytes. Historical writer snapshots occur after the entire acquisition
returned: all windows of that acquisition are legitimately already visible, but
only C/H up to the snapshot are retained. No later writer output is exposed.
R1 C comes from the historical reviewed single-gap bank, not an original Qwen C
runtime. q546's D17/W31 pending opportunity is a frozen prefix-only annotation,
identical across replicates. It is not a model-produced source nomination.
Historical attempt Gain is unknown and is labeled unassessed, not invented NoGain.

R is exact Stage4 D2 spans for q228/q637/q538/q922. q546/q1094 use the predeclared
whole-Q mechanical R1; no extra skeleton model call. Original Q has highest
closure authority in every cell. Seed C is supported source-relative, not a
claim that the whole question is resolved. All data provenance is hashed.

## Model and transport

DeepSeek Flash; temperature0 (documented as ignored in thinking mode), explicit
thinking enabled/high; max_tokens32768 uniformly including reasoning; JSON-object
mode. No tools are sent to the model endpoint: the Actor decision JSON embeds the
unchanged executable tool schema and is validated locally. Role semantics/prompts
are unchanged from the offline implementation; transport adds their existing
schema and an instruction to output one JSON object. No user_id supplied, matching
historical calls; no key rotation. Length/empty/non-JSON/wrong model/invalid output
is a retained failure, not a repaired sample.

Provider documentation checked2026-09-28:
- https://api-docs.deepseek.com/zh-cn/api/create-chat-completion/
- https://api-docs.deepseek.com/zh-cn/quick_start/rate_limit/

Flash account ceiling2500 is above this batch's12 dependent-trajectory maximum.
Async I/O uses a12-connection pool, maximum12 in-flight requests. Retrieval uses
unchanged BCPlusSearcher on free GPU0 and a one-search semaphore; other API/local
work overlaps. No paid preflight or separate throughput probe. First requests
are formal scheduled observations. Initial credentials are checked for presence
only; no keys archived. Connect30/read900/write60/pool30 seconds; independent
asyncio total request deadline1200 seconds, including keep-alive body delivery.
Partial response bytes are retained when available. Transport retries0.

On timeout/429/503, end that trajectory and halve the limit for unsent requests,
minimum1; no in-batch increase or replacement. HTTP400/401/402/403/404/422 or model
mismatch also closes the batch circuit for unsent model work. Structural role or
tool failure terminates its trajectory. In-flight requests complete and remain
recorded. No further cohort starts after this batch. Semantic false C/READY is
reviewed after the batch and bars expansion; no completion-order-dependent
prompt edits or filtering. User safety stops can interrupt earlier.

## Review rubric

Every actual decision receives separate labels with reasons:
- OneGap usability and premise hardening (forced decisions kept separate);
- action validity, semantic suitability and tool execution;
- accepted C source-relative support, gap usefulness and global-task usefulness;
- H action: justified downgrade, unjustified rejection, mere new candidate churn;
- inspection source compatibility and actual new useful evidence;
- closure missing feedback correctness and next-action response to that feedback;
- NoGain route escape: materially different research route, not query paraphrase;
- false high-risk C, false READY and unsupported final assertion.

Unknown/ambiguous is explicit. Review uses Q/R/C/H plus exact observed evidence up
to the relevant decision, never gold or future source text. Positive local facts
are not erased when global candidate binding remains open. A premature Closure
request is an efficiency cost if vetoed; false READY is a high-risk error. Count
true-but-irrelevant C and semantic H duplicates as Gain inflation, not recovery.
Source relevance and factual support have separate denominators. R1 can fail by
continuing the same route despite formally valid actions. R2 can be inconclusive
when no contradictory evidence arrives. R3 requires CONTINUE→next action, not
CONTINUE alone. Three decisions do not measure long-horizon answer accuracy.

## Artifacts / stopping

FREEZE.json pins source/prompts/schemas/selection/initial states/interventions,
model parameters, rubric, original source files and local binary identity metadata.
Commit it before executing run.py. Initial and every dependent role request gets
its exact hash before transmission; raw response and usage are kept separately.
Run folders use exclusive creation, so failed outputs cannot be overwritten.
Final state is replay-checked. The post-run report includes request counts,
complete/inconsistent/missing usage rows, input/output/cache hit/miss, actual peak
concurrency, changes, wall time and latency quantiles. Cache hit rate uses only
complete consistent rows; never equate an absent record with zero usage.
