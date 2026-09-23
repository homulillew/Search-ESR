# Frozen-stage plan

## M0 protocol

`provider.json` fixes `Atria-Dawn-Preview` at `api.atria-asi.ai`, 120-second
timeout, zero SDK retries, and acceptance of a complete `stop`-finished tool
batch. `freeze_protocol.json` hashes the exact Search–Find tool menu,
prompt, source code and 13 checkpoint requests before the first M0 call.
`preflight.py` makes four minimal live requests (ordinary, auto-tool,
forced single tool, multi-tool prompt), retaining full raw responses.
Five synthetic returned batches test stop+calls, malformed JSON,
undeclared name, missing required field and batch atomicity. The harness
validates all names and arguments before executing any call. The provider is
not guaranteed to issue two calls just because the prompt asks; this live
multi-tool request is observed, while atomic multi-call validation is gated.
Any required M0 failure stops the paired study.

## M1 explicit planning

The 13 exact checkpoint `api_request.messages` from the original v3a runs
are reused verbatim. Before model calls, prefix-only labels are reviewed and
frozen in `PREFIX_ONLY_ANNOTATIONS.json`. Qwen and Atria each receive the
same messages plus exactly the diagnostic instruction specified in the user
protocol, with no tools. One sample per model/checkpoint, fixed cell order.
The prompt and selection rule are frozen in `planning_probe/freeze.json`.
Report paired need, source type, acceptable scope and plausible D#/W#
agreement, plus over-search and premature-local intent. Model/provider
token totals are only descriptive.

## M2 natural next action

On M1 completion, choose checkpoints mechanically: first three in frozen
order where Atria plans document and Qwen corpus; first two where both plan
document; first two where both plan corpus. If any stratum is too small,
use all 13. Freeze the selected IDs and original requests before calls.
Both models receive the same unmodified prefix, Search–Find prompt and tool
schema. Request one natural next action, record but never execute it.
Strictly validate the whole returned batch and classify Search, Find, Open,
Stop, invalid name/arguments. Report scope realization by model.

## M3 partial rollout (conditional)

Only a moderate M1/M2 signal permits four case-selected prefixes: qid 546
triage, qid 1094 natural verification, corpus, and stop if available. Reuse
the original P0/P1 code paths, D/W restoration, prompt/schema, four-decision
horizon and historical Qwen cells. The only new crossed variable is Atria.
No forced answer. Atria protocol compatibility may accept a valid raw
`finish_reason=stop` batch after atomic validation; raw reason is retained.
Freeze exact cells/arm order/source hashes before any M3 call.

## M4 evidence update

Prepare 6–10 exact raw-window cases spanning support, refutation and
non-support, each with E0 no addition and E1 exact evidence. Label any
post-hoc answer-bearing source `diagnostic_oracle_evidence`. Freeze the raw
spans, same-prefix messages, instructions and scoring rules before calls.
Compare paired relation judgment, belief update, unsupported override and
stop calibration. This does not measure acquisition.

## M5 Atria-native (conditional)

Only a material mechanism difference in M1–M4 permits qid 546/1094 runs
from the original questions, Orthogonal Search, no State, maximum 12–16
decisions or natural stop. Horizon is recorded as `horizon_no_answer`.
Do not expand to 10–20 questions without a validated mechanism.

Every stage retains errors and partial attempts, never selectively reruns
completed cells, and has an independent freeze before new paid calls.
