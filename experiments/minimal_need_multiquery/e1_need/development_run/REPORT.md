# E1 development v1 — mechanism gate not met

## Material Passport

72 real DeepSeek calls,18 exposed natural QCH/9qids; four concurrent arms, one response each. No tools, retries, repairs or sample replacement. Exact execution HEAD is in RUN.json. Single Codex reviewer read arm-masked QCH/Need packets before unmasking; prior prompt/E0 familiarity precludes perfect blinding.

| Arm | Strict /18 | P | A | W_independent | No-H /8 |
|---|---:|---:|---:|---:|---:|
| B0 exact old B5 |14|3|1|0|8|
| B1 premise addition |12|4|1|1|7|
| B2 coherence addition |10|5|2|1|7|
| B3 combined additions |12|3|2|1|6|

All72 outputs were valid JSON; no execution failure explains the semantic losses. B1 and B2 have no paired strict gains versus B0, with2 and4 losses. B3 fixes F13_S01's presumed SPS case by testing swelling directly, but loses F08_S00 (unknown building attribute), F13_S06 (Pakistan history asserted) and F14_S00 (thesis plus advisor education/bibliography).

## Interpretation

The two mechanisms did not separate. Premise rules did not lower aggregate P/A; all four arms ask a reference question about an unidentified book in F11_S01. Memorandum-to-letter date binding remains wrong. B0 already has zero W under the new coherent-objective rubric, so a W reduction is unidentifiable on this sample. The coherence addition actually introduces W cases. Selecting historical failures does not guarantee their concurrent replication; it is why historical responses were not used as the causal baseline.

B2/B3 inherit old one-relation wording and append a broader coherent-objective rule. That instruction conflict is a plausible explanation, not causally established by this batch. The empirical failures also require sharper referent binding: an unidentified document is not a grounded subject for its downstream attribute test. A single bounded combined-policy revision is justified as a diagnostic; the v1 findings remain negative regardless of its outcome.

## Sensitivities

Strict prefix-only review additionally rejects naming President Roosevelt where Q/C only say President of the United States. Two cells have this as their sole failure: B1 F16_S01 and B3 F16_S02. Allowing that external historical identity inference gives13/18 and13/18, still below B0 and still failing the gate. Other letter-date/region assumptions remain failures. Medium-ambiguity coherence/referent judgments are explicitly retained in review/REVIEW.json. They are single-reviewer judgments, not gold truth.

The frozen mechanism gate yields STOP_FOR_MECHANISM_ANALYSIS. This is not fresh confirmation and does not open E2. The allowed one-revision diagnostic follows separately frozen criteria; there will be no further prompt sweep.

## Accounting

Input41,700; completion265,265 including reasoning262,343; total306,965. Cache hit22,400 / input41,700 = **53.72%**; miss19,300. All72 responses have complete consistent usage. Wall200.01s, peak concurrency8. No monetary price inferred. See ACCOUNTING.json, METRICS.json, review/REVIEW.json and INTEGRITY.json.
