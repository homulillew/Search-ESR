# F1 results

All planned outputs are retained; gate uses valid decisions including correct STOP. Two replicates are correlated samples, not best-of. Primary closure and coverage were frozen before calls.

| Metric | H | S | SH |
|---|---|---|---|
| valid | 18/48 (37.5%) | 18/48 (37.5%) | 19/48 (39.6%) |
| valid_act | 10/23 (43.5%) | 14/27 (51.9%) | 11/26 (42.3%) |
| correct_stop | 8/24 (33.3%) | 4/21 (19.0%) | 8/21 (38.1%) |
| stale | 0/48 (0.0%) | 0/48 (0.0%) | 0/48 (0.0%) |
| drift | 0/48 (0.0%) | 0/48 (0.0%) | 0/48 (0.0%) |
| unsupported_premise | 7/48 (14.6%) | 9/48 (18.8%) | 7/48 (14.6%) |
| over_broad | 9/48 (18.8%) | 6/48 (12.5%) | 11/48 (22.9%) |
| premature_stop | 16/48 (33.3%) | 17/48 (35.4%) | 13/48 (27.1%) |
| missed_stop | 0/48 (0.0%) | 0/48 (0.0%) | 0/48 (0.0%) |
| belief_error | 23/48 (47.9%) | 26/48 (54.2%) | 21/48 (43.8%) |
| critical | 23/48 (47.9%) | 26/48 (54.2%) | 20/48 (41.7%) |
| provider_or_contract_failure | 1/48 (2.1%) | 0/48 (0.0%) | 1/48 (2.1%) |

## Gate

```json
{
  "S_at_least_85_percent": false,
  "SH_minus_S_at_most_5pp": true,
  "no_multicase_critical_deficit": false,
  "SH_minus_S_pp": 2.0833333333333313,
  "pass": false,
  "SH_positive_refutation": true
}
```

Critical repairs count checkpoints once, requiring an S critical failure and both SH replicates valid. Cases: {'cases': ['F06', 'F13', 'F15', 'F16'], 'qids': ['311', '546', '580']}. Long-term blocking omission is unmeasured in static F1.

## Per-question valid decisions

| qid | H | S | SH |
|---|---|---|---|
| 1034 | 1/6 (16.7%) | 5/6 (83.3%) | 2/6 (33.3%) |
| 1094 | 0/4 (0.0%) | 0/4 (0.0%) | 0/4 (0.0%) |
| 177 | 4/4 (100.0%) | 2/4 (50.0%) | 2/4 (50.0%) |
| 186 | 2/4 (50.0%) | 4/4 (100.0%) | 4/4 (100.0%) |
| 311 | 0/6 (0.0%) | 0/6 (0.0%) | 2/6 (33.3%) |
| 387 | 0/4 (0.0%) | 0/4 (0.0%) | 0/4 (0.0%) |
| 435 | 1/6 (16.7%) | 1/6 (16.7%) | 0/6 (0.0%) |
| 517 | 1/4 (25.0%) | 1/4 (25.0%) | 1/4 (25.0%) |
| 546 | 3/4 (75.0%) | 3/4 (75.0%) | 2/4 (50.0%) |
| 580 | 6/6 (100.0%) | 2/6 (33.3%) | 6/6 (100.0%) |

## Actual H input token quartiles

Four equal groups of six checkpoints; same memberships for every arm. Table cells valid / stale / drift / premature-stop counts, each denominator12.

| Quartile | H | S | SH |
|---|---|---|---|
| Q1 | 4 / 0 / 0 / 4 | 7 / 0 / 0 / 2 | 8 / 0 / 0 / 1 |
| Q2 | 2 / 0 / 0 / 4 | 4 / 0 / 0 / 2 | 3 / 0 / 0 / 2 |
| Q3 | 7 / 0 / 0 / 5 | 2 / 0 / 0 / 10 | 6 / 0 / 0 / 6 |
| Q4 | 5 / 0 / 0 / 3 | 5 / 0 / 0 / 3 | 2 / 0 / 0 / 4 |

Quartile failures are confounded by question, checkpoint phase and closure opportunities; no causal long-history or significance claim.

## Replicate stability

| Category | H | S | SH |
|---|---|---|---|
| same_valid_requirement | 7 | 7 | 8 |
| different_both_valid | 0 | 0 | 0 |
| one_valid | 4 | 4 | 3 |
| both_invalid | 13 | 13 | 13 |

Each arm has24pairs. Shared requirement IDs may encompass different subrelations; exact narrow focuses are preserved in replicate_stability.json.

## Measured usage and elapsed time

| Arm | Input total / mean | Output total / mean | Reasoning proxy total / mean | Mean sec | Median sec | Cache hit tokens/input |
|---|---|---|---|---|---|---|
| H | 244214 / 5087.8 | 383763 / 7995.1 | 381945 / 7957.2 | 36.65 | 20.44 | 129146/244214 (52.9%) |
| S | 37128 / 773.5 | 434453 / 9051.1 | 432768 / 9016 | 42.77 | 20.92 | 19968/37128 (53.8%) |
| SH | 259934 / 5415.3 | 398596 / 8304.1 | 396576 / 8262 | 39.07 | 22.06 | 138494/259934 (53.3%) |

Reasoning tokens are an inference-burden proxy, not cognitive load. Provider elapsed is per-call wall time including provider/network, with four concurrent requests and shared cache warmth. No monetary estimate was made.

## Deferred reactivation

```json
{
  "full_requirement_outputs": [],
  "subrelation_outputs": [],
  "eligible_S_calls": 6
}
```

Failure to select a deferred requirement immediately is not scored wrong if another valid Need exists. Subrelation reactivation is separately annotated and not counted as full-composite recovery. No tools or Writer executed.

## Predeclared closure sensitivity

| Arm | Valid with F24 discriminative-identity closure |
|---|---|
| H | 20/48 (41.7%) |
| S | 20/48 (41.7%) |
| SH | 21/48 (43.8%) |

Only the predeclared F24 policy changes. The primary coverage and gate are not overwritten.

## Audit trail

Exact requests and committed freeze; append-only raw events; masked_contexts/packets; individual semantic_review; private unmask key; reviewed_outputs; replicate_stability and summary. STOP is mechanically scored against the human-reviewed frozen closure label. ACT Needs are individually semantically reviewed. The reviewer can infer treatment from view content; this is not perfect blinding.

The bank is24archived checkpoints/10qids with complete recorded-episode history, but unrecovered ancestral chronology and inherited legacy Writer States. It is not a fresh minimal-U1 cohort.
