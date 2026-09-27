# Post-execution audit

## Chronology

1. Fetched remote and verified base `50f11b58a554223d8c2ac91a2d0ec8ad41dc1289`; created `experiment/contextual-subtraction-qualification`.
2. Committed E0 Gold, exact historical inputs, policy, and historical file hashes at `6776c897` before calls.
3. Committed actual192 requests, task-scoped E1 authorization, exact Q1 prompt, Q0 prompt, config, scoring and gates at `68fc2f13`.
4. Executed once using that HEAD. Freeze SHA256: `b08fefe073955fd9286bcd2e87c5cf1acc4c91e439ce8e815d41b85898b9253e`. No resend, retry, repair or replacement.
5. Exported192 masked content-only packets; grouped identical evaluation context/output into129 manual reviews. Single task-familiar reviewer; no independent-review or perfect-blinding claim.
6. Sealed raw calls, accounting, packets and192 judgments; committed at `e996b6bf` **before** aggregating/unmasking scores. Actual arm/replicate key not inspected by reviewer until after this seal. Rationale wording could reveal context awareness.
7. Aggregated frozen scores; E1 FAIL. Raw-response reparsing, score replay and accounting replay all identical. All20,796 historical experiment file hashes unchanged.
8. Added descriptive diagnostics, reports and explicit E2/E3 stop decisions. No further model or retrieval call.

## Checks and caveats

- Ten pre-execution offline checks passed; they cover isolation of Q0 input, exact Q1 prompt, actual Claim text, locator membership, paired context construction, schema rejection, gate equality and zero-denominator cases, mandatory Euler failure, and retry policy. They are synthetic harness checks, not model outcomes.
- All192 actual requests match the frozen schedule. Gold, prompts, gates and historical inputs remain unchanged.
- All192 responses have valid output; failure ledger is empty. Every planned slot appears in the score. Peak8 concurrent requests satisfies the frozen limit.
- Reported input115,146; output176,433; total291,579. Reported reasoning168,717 is contained in output. Cache hit64,379 + miss50,767 equals input. Cache counters cover all192 calls, yielding55.91075678%.
- No known currency estimate is inferred. No provider reasoning text was used in semantic review; raw responses retain provenance.
- Q0/Q1 are certificate-level, and both use the same selected ClaimSet. Q1 additionally sees Original Q/Parent and a different context-interpretation instruction. The contrast does not isolate these subcomponents.
- Three ambiguity references were frozen before calls. A fourth letter binding concern was discovered during masked review and recorded before scoring; its exclusion is explicitly post hoc. Primary labels never change.
- The six descriptive contrast pairs were recorded during execution before model-content inspection. They were not separately frozen before requests and are not primary gates.
- `RUN.json.status=PASS` denotes pre-send input/authorization audit, **not** experimental success. The final experimental decision is `METRICS.json.gate.E1_PASS=false`.
- E2/E3 initial `STATUS.json` files are frozen preparation artifacts; final `DECISION.json` and `METRICS.json` now record the stop and null measurements.
- Original TASK.md retains the attachment's CRLF bytes. Whitespace validation uses `core.whitespace=cr-at-eol`; no source-task normalization is committed. Runtime prompt line endings were normalized before freeze as disclosed.
- Unrelated untracked `experiments/auto_research/`, `research_loop/`, and the existing Chinese notes are outside this commit scope and remain untouched.

## Reproduction without calls

`python -c 'from experiments.contextual_subtraction_qualification.score import results; from experiments.contextual_subtraction_qualification.common import P, read; assert results() == read(P/"e1_qualification/METRICS.json")'`

The scorer requires the committed review seal and verifies its file hashes. `analysis/INTEGRITY.json` records the completed raw-response/accounting/history audit. `RESULTS_SEAL.json` seals final reports and derived results; it excludes itself. Do not rerun `execute`: saved attempts are exclusive, and no further calls are authorized by the failed E1 decision.
