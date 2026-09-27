# e1_alignment

Planned slots:108. Single-reviewer exposed historical development bank.

## A0: FAIL

| Metric | Value | Threshold | Pass |
|---|---:|---:|---|
| node_status_accuracy | 0.9255 | >= 0.9 | True |
| false_supported_rate | 0.0252 | <= 0.05 | True |
| residual_recall | 0.9748 | >= 0.95 | True |
| support_precision | 0.8658 | >= 0.9 | False |
| full_support_sufficiency | 0.8627 | >= 0.9 | False |
| exact_state_mask | 0.7037 | >= 0.8 | False |
| schema_validity | 1.0000 | >= 0.95 | True |

## A1: PASS

| Metric | Value | Threshold | Pass |
|---|---:|---:|---|
| node_status_accuracy | 0.9394 | >= 0.85 | True |
| false_supported_rate | 0.0132 | <= 0.075 | True |
| residual_recall | 0.9868 | >= 0.9 | True |
| support_precision | 0.8759 | >= 0.85 | True |
| exact_state_mask | 0.7778 | >= 0.7 | True |
| schema_validity | 1.0000 | >= 0.95 | True |
| alignment_loss | -0.0741 | <= 0.1 | True |
| node_accuracy_loss | -0.0139 | <= 0.1 | True |

Joint gate: FAIL.

See METRICS.json for qid/type/empty-Claims/replicate strata, denominators and paired metrics.
E1 failure stops E2. E2 completion stops this experiment regardless of outcome.
