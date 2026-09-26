# Additional diagnostics

## Actual-history quartile replicate instability

Mixed-validity replicate pairs (one valid, one invalid); six checkpoint pairs per arm per quartile. Different valid requirements are not instability failures.

| Quartile | H | S | SH |
|---|---|---|---|
| Q1 | 2/6 | 3/6 | 2/6 |
| Q2 | 0/6 | 0/6 | 1/6 |
| Q3 | 1/6 | 0/6 | 0/6 |
| Q4 | 1/6 | 1/6 | 0/6 |

Full category counts are in analysis/HISTORY_LENGTH_SENSITIVITY.json. These small, correlated strata have different qids and closure states; no causal length trend is inferred.

## Critical repair decomposition

The frozen gate flags F06,F13,F15,F16 across3qids. F15/F16 have identical STOP outputs in S and SH, but SH has source evidence for total seasons that S cannot see. They are differences in evidence-relative admissibility, not changed behavior. F06 changes from S STOP to SH character testing; F13 has one S unsupported premise with another S replicate valid. This decomposition explains the gate without changing its definition.

## Exact provenance

All24selected full States compare equal to their original historical JSON pointer, not merely to an internally generated hash. Production exposes only authorized view fields. See analysis/PROVENANCE_CHECK.json.
