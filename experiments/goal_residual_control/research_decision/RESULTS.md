# G2: execution integrity failure

120/120 API responses returned, but only **75/120 (62.5%)** satisfy the frozen Actor JSON contract. All 45 failures are action serialization: 38 discriminator/wrapper failures and 7 missing top-level query failures. No retry, repair, relaxed parser or rejected-action execution was performed. This is a harness contract omission, documented in INTERFACE_FAILURE.md, not negative evidence about the architecture.

The <80% integrity gate stops G3–G5. The frozen batch was allowed to finish so the full planned denominator and failures remain available. Primary comparisons are not interpretable because missingness differs by arm and valid STOP uses no action object.

## Diagnostic only

| Arm | Valid | Correct STOP / resolved | Premature STOP / open | Valid act decisions | Hypothesis overcommit |
|---|---:|---:|---:|---:|---:|
| A0 | 29/40 | 7/7 | 10/33 | 12 | 1 |
| A1 | 21/40 | 7/7 | 3/33 | 11 | 1 |
| A2 | 25/40 | 7/7 | 7/33 | 11 | 2 |

All denominators above retain planned snapshots; 40 snapshots are only 10 qids. Invalids have unknown semantic outcomes, not zero drift. No valid acting packet pursued a fully resolved original goal or an unrelated new objective; four overstate a candidate identity/binding. Valid-query relevance does not establish evidence progress. No tools ran, so source precision, evidence yield and efficiency are unmeasured. q435 strict closure sensitivity is retained in reviews/metrics.

A1's diagnostic premature stops cannot be attributed solely to G1: Actor can independently stop despite a nonempty residual, while G1's two empty residual errors can also propagate. These failure examples warrant study under a corrected explicit response contract, not a selected valid-only arm ranking.
