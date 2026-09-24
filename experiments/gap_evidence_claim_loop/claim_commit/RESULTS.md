# F2 Claim commit results

All 53 frozen packets ran once with `deepseek-flash`, `max_retries=0`; all
calls completed and every failure would have remained in the denominator.
The bank contained all 38 F1-C Findings plus 15 negative or ambiguous
proposals over genuine historical observations. The direct arm D committed
every proposal. The verifier arm V admitted only `supported` verdicts.

| Metric | D | V |
| --- | ---: | ---: |
| Committed Claim precision | 38/53 (71.7%) | 37/37 (100%) |
| Recall of labelled supported Findings | 38/38 (100%) | 37/38 (97.4%) |
| False promotion of labelled negatives | 15/15 (100%) | 0/15 (0%) |
| Rejection of stress negatives | 0/15 | 15/15 |
| Evidence binding accuracy | 53/53 | 37/37 |
| Unsupported Claim bloat | 15 | 0 |

V passed every frozen gate: precision ≥95%, recall ≥90%, false promotion ≤5%,
and stress rejection ≥90%. The one labelled false negative is
`A_T3_580_1`. A [separate sensitivity audit](POSTHOC_LABEL_AUDIT.md)
explains why its preregistered positive label is probably too permissive.
The result supports a verifier before persistence, within this curated bank;
it does not yet establish end-to-end retrieval benefit. DeepSeek reported
0 prompt-cache hit tokens across 32,916 prompt tokens (0% weighted hit rate).
