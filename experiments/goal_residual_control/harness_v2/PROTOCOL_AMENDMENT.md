# Contract v2: engineering amendment before live calls

## Material Passport

Mode: implement and execute the user-specified experiment. Material: immutable G0 bank, old G1 outputs, old G2 requests/results, and the task attachment. Historical base: f53a43c9342fa643c117b9362dce1164abaf3e4a. Branch: experiment/goal-residual-control-contract-v2. No literature search or new answer key. Single Codex semantic reviewer; no subagents or claim of independent human review.

## Phase A boundary

The old Actor research instructions remain an exact prefix. Only the explicit full response schema, flat serialization instructions and five formatting examples are appended. Examples use an observatory/instrument topic unrelated to the frozen qids. Search requires k in the response, range 1–10; the underlying Search default/implementation is unchanged. Find/Open schemas exactly match llm_chat/search_find_agent.py. No response_format, sampling option, model, endpoint, retries or concurrency change. Four workers, 240s timeout, zero retries. Unknown D/W are rejected against the pre-batch registry before either action executes. Serialization validity and registry validity are separately recorded.

Goal Reviewer prompt is byte-identical to the old prompt. The same goal parser constraints are represented in a machine-readable schema and semantic consistency check. State Updater keeps its original semantic instructions and output fields; concrete keep/set/clear examples and the exact same field schema are appended only to remove interface ambiguity. All schemas are closed-world. No normalization, repairs, best-of or resampling.

## Shared authentication implementation

Main commit 8021aca19a1ee5201730e40b338012c65ecd51cf is already an ancestor; no merge/cherry-pick is required. Its typed credential-rejection latch was extracted to llm_chat/auth_guard.py. The existing first_observation execution loop now calls this shared latch, preserving its behavior; the v2 runner uses that same class across all workers. This is the only refactor outside new v2 paths. Historical experimental artifacts, archived source snapshots, requests, responses, old G1/G2 and FINAL_CONCLUSION.md are not changed. Existing authentication regression tests must pass. No Evidence Pointer fields or pipeline are imported into research state.

After AuthenticationError, queued jobs stay unsent with blocked_by_auth. Up to four already in-flight calls may complete. Network/schema failures are retained without retries. This is not a change to research semantics.

## Phase B

G2v2 repeats all 120 frozen case×arm inputs in their original order. A1 uses the old G1 result unchanged. REQUEST_DIFF_AUDIT proves old/new request equality after removal of the appended system contract; user messages and API fields are exactly equal. Old validity remains permanently 75/120.

If valid rate is at least 80%, execute G3, G4 and G5 regardless of research effect size. Below 80%, no tools; a separately frozen constrained-output v3 may be investigated without relaxing parsers. G3 executes every valid action; invalids and stops retain planned denominators. G4 uses all 20 original transitions and R0/R1/R2/R3. G5 uses the original deterministic 10-qid selection, L0/L1/L2, three decisions and two independent actions maximum. All stages have new v2 directories and freezes. No original truth or hypothesis is revised after results.

## Evaluation

The original REVIEW_RUBRIC.md and q435 strict sensitivity remain in force. Production models never see private labels. Review packets hide arm labels; Codex reviews source support and original-goal relevance. Known source sets are frozen; new sufficient sources are sensitivity additions with exact supporting observations. Topic relevance alone is No Progress. Cached prompt hit/miss tokens and all failed-call costs remain included. Repeated snapshots are clustered by qid; no independent-sample significance claim.
