# S1 controls (same 12 frozen cells)

| Arm | Direct @1 | @3 | @5 | @10 | @20 | @50 | MRR@50 |
|---|---:|---:|---:|---:|---:|---:|---:|
| S0 | 7 | 9 | 10 | 11 | 12 | 12 | 0.6893 |
| S3 | 10 | 10 | 12 | 12 | 12 | 12 | 0.8750 |
| S_noise | 6 | 7 | 9 | 10 | 11 | 12 | 0.6040 |
| S_history | 8 | 10 | 11 | 12 | 12 | 12 | 0.7847 |

The frozen 12-cell control subset rose from S0 10/12 to S3 12/12 at top5. Truthful incidental noise fell to 9/12, so extra context length alone did not reproduce the S3 result in this subset. Raw prior W reached 11/12. Against S3, raw history had a better canonical rank in 1 cell, tied in 8, and worse rank in 3. Median provider-reported input prompt tokens were 391.5 for S3 and 746.5 for raw history on the same 12 cells: S3 used about 52.4% as many tokens. This supports useful compression in these cases, subject to the high baseline ceiling and repeated qids.

Noise facts had 0.87–1.22 times the S3 whitespace word count and were sourced from the same prior W. Word count approximates, rather than exactly matches, model tokens. One raw-history query for q580 named `You're the Worst` although the provided raw W text did not contain that series name; this is an unsupported model inference and illustrates why history performance cannot automatically be attributed to observed evidence. The observed URL in SC0 did support the series name used in structured State.

The control results cannot rescue the failed 24-cell primary gate. Their 12 cases were frozen before calls, but the target set was already easy under S0 (10/12 top5), and one canonical rescue in the controls is q186 B06 with an alternative S0 answer source at rank 3.
