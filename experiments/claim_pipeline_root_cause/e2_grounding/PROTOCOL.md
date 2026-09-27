# E2 Grounding candidate-anchoring protocol

## Fixed inputs and intervention

Selection, bank truth and canonical hashes are in BANK_FREEZE.json and CANDIDATE_BANK.json. Original selector, prompts and H3 metrics are reused unchanged. One response per role, same DeepSeek Flash configuration as corrected E1: thinking enabled, reasoning_effort high, temperature 0, max_tokens 32768, stream false, max_retries 0. No additional evidence retrieval.

G0 sees Candidate + full public Evidence. G1 inventory sees only full public Evidence and existing visible metadata. G1 Coverage sees Candidate + physically frozen inventory. Inventory model input has no candidate IDs, labels, Gap, C, question, trace or future evidence. Private provenance is archived outside messages. Public projection preserves source text and title/URL/date as present and exposes only D#/W# handles; it excludes machine provenance and has no alias map. Inventory references use the inherited dynamic observed-W enum and independent runtime membership validation.

Within this stage identical Evidence/config/prompt/schema yields one inventory. Each inventory is exclusively written, hash bound and read back before dependent Coverage can start. Coverage request hashes depend on this frozen output and are archived before dispatch; no future-dependent hash can be known at initial freeze.

## Concurrency and failures

35 G0 and 15 inventory requests are initially independent. Fixed active cap 50 and HTTP pool 70; this avoids a serial queue while reserving account capacity. Each of 35 Coverage calls waits for its corresponding inventory. This small DAG does not require further escalation. Any listed transport or output contract failure halts all unsent work, permits inflight completion, and is preserved. No retry, replacement, output repair or resumption. Any missing pair makes H3 inconclusive; no survivor-only gate.

## Source-only inventory review

Export one Evidence + inventory packet without candidates, linked IDs, qid, arm results or truth labels. A single Codex reviewer assesses every fact's source support and reason, then omissions and attribution/modality/relation losses against the observed source alone. Incomplete/clipped sources are not repaired using external knowledge. Omission review covers distinct visible factual propositions, not every paraphrase or bibliographic repetition. Distinguish important relation/condition/scope losses from incidental detail omissions. Inventory labels must be frozen before reading G0/G1 verdicts for outcome analysis. Prior knowledge of historical examples is acknowledged; packet-level information isolation does not imply an independent blinded human reviewer.

Severe inventory unreliability means losses or unsupported facts make G1 verdicts uninterpretable (e.g. systematic empty inventory or systematic attribution stripping). Report numerical H3 unchanged and separately state whether this predeclared interpretability condition blocks the final conclusion. Never promote an inventory defect into a claimed architectural success.

## Metrics and stop

Source-supported positives include irrelevant claims. Negatives are source_supported=false AND semantic_strengthening=true. Report FAR and TPR with integer denominators for pooled, D and H_diagnostic; ambiguous-negative and nonambiguous-negative FAR separately. A zero denominator is undefined.

Reuse original `metrics.e2`: pooled FAR relative reduction >=50%, G1 TPR >=85%, strict beneficial paired-negative and equal-weight negative-qid directions; H_diagnostic requires strict error reduction, TPR >=85%, paired/qid benefit. G0 FAR=0 means H3_INCONCLUSIVE_NO_BASELINE_FALSE_ADMISSION. Missingness means inconclusive. Report each rescued negative and damaged positive, with full source/inventory/reasons. q435/q673 are descriptive mechanism traces, never extra gates. Shared inventories and qids limit independence; no p-value/generalization claims.

Freeze source/input/prompt/schema/config/code hashes before calls. Archive request/response/reasoning/usage, token and cache completeness, failures, latency, wall time and concurrency. STOP_AFTER_E2 regardless of results. E3 is recommendation only; no production changes or H_confirmation execution.
