# Context ablation results

Primary labels committed at `3834417d56e031b99808d0ab149b0b9295045d8c` before key/context review or semantic aggregation. Freeze commit `0cc6d11`. All216 slots retained;2 length failures, both in C0.

## Overall primary:27 states

| Context | Strict | Broad | Downstream | RelationArg | Scope | Stable |
|---|---:|---:|---:|---:|---:|---:|
| C0 | 25/54 (46.3%) | 13/54 (24.1%) | 10/54 (18.5%) | 2/54 (3.7%) | 40/54 (74.1%) | 6/27 (22.2%) |
| CΔ | 23/54 (42.6%) | 20/54 (37.0%) | 14/54 (25.9%) | 3/54 (5.6%) | 43/54 (79.6%) | 11/27 (40.7%) |
| C1 | 26/54 (48.1%) | 14/54 (25.9%) | 13/54 (24.1%) | 1/54 (1.9%) | 42/54 (77.8%) | 9/27 (33.3%) |
| C2 | 26/54 (48.1%) | 18/54 (33.3%) | 14/54 (25.9%) | 3/54 (5.6%) | 42/54 (77.8%) | 10/27 (37.0%) |

| Contrast to C0 | Δ Strict | Δ Broad | Δ Downstream | Δ RelationArg | Δ Stable | Mechanism signal |
|---|---:|---:|---:|---:|---:|---|
| CΔ | -3.70 pp | +12.96 pp | +7.41 pp | +1.85 pp | +18.52 pp | True |
| C1 | +1.85 pp | +1.85 pp | +5.56 pp | -1.85 pp | +11.11 pp | False |
| C2 | +1.85 pp | +9.26 pp | +7.41 pp | +1.85 pp | +14.81 pp | False |

## Delta/path eligible:17 states

| Context | Strict | Broad | Downstream | RelationArg | Scope | Stable |
|---|---:|---:|---:|---:|---:|---:|
| C0 | 16/34 (47.1%) | 6/34 (17.6%) | 8/34 (23.5%) | 1/34 (2.9%) | 23/34 (67.6%) | 3/17 (17.6%) |
| CΔ | 18/34 (52.9%) | 9/34 (26.5%) | 10/34 (29.4%) | 2/34 (5.9%) | 24/34 (70.6%) | 9/17 (52.9%) |
| C1 | 19/34 (55.9%) | 6/34 (17.6%) | 9/34 (26.5%) | 0/34 (0.0%) | 25/34 (73.5%) | 7/17 (41.2%) |
| C2 | 19/34 (55.9%) | 7/34 (20.6%) | 10/34 (29.4%) | 2/34 (5.9%) | 23/34 (67.6%) | 8/17 (47.1%) |

| Contrast to C0 | Δ Strict | Δ Broad | Δ Downstream | Δ RelationArg | Δ Stable | Mechanism signal |
|---|---:|---:|---:|---:|---:|---|
| CΔ | +5.88 pp | +8.82 pp | +5.88 pp | +2.94 pp | +35.29 pp | True |
| C1 | +8.82 pp | +0.00 pp | +2.94 pp | -2.94 pp | +23.53 pp | True |
| C2 | +8.82 pp | +2.94 pp | +5.88 pp | +2.94 pp | +29.41 pp | True |

## Observation eligible:15 states

| Context | Strict | Broad | Downstream | RelationArg | Scope | Stable |
|---|---:|---:|---:|---:|---:|---:|
| C0 | 15/30 (50.0%) | 4/30 (13.3%) | 6/30 (20.0%) | 1/30 (3.3%) | 21/30 (70.0%) | 3/15 (20.0%) |
| CΔ | 16/30 (53.3%) | 8/30 (26.7%) | 8/30 (26.7%) | 2/30 (6.7%) | 22/30 (73.3%) | 8/15 (53.3%) |
| C1 | 18/30 (60.0%) | 5/30 (16.7%) | 7/30 (23.3%) | 0/30 (0.0%) | 24/30 (80.0%) | 7/15 (46.7%) |
| C2 | 17/30 (56.7%) | 6/30 (20.0%) | 8/30 (26.7%) | 2/30 (6.7%) | 21/30 (70.0%) | 7/15 (46.7%) |

| Contrast to C0 | Δ Strict | Δ Broad | Δ Downstream | Δ RelationArg | Δ Stable | Mechanism signal |
|---|---:|---:|---:|---:|---:|---|
| CΔ | +3.33 pp | +13.33 pp | +6.67 pp | +3.33 pp | +33.33 pp | True |
| C1 | +10.00 pp | +3.33 pp | +3.33 pp | -3.33 pp | +26.67 pp | True |
| C2 | +6.67 pp | +6.67 pp | +6.67 pp | +3.33 pp | +26.67 pp | True |

## Empty context:10 identical-input states

| Context | Strict | Broad | Downstream | RelationArg | Scope | Stable |
|---|---:|---:|---:|---:|---:|---:|
| C0 | 9/20 (45.0%) | 7/20 (35.0%) | 2/20 (10.0%) | 1/20 (5.0%) | 17/20 (85.0%) | 3/10 (30.0%) |
| CΔ | 5/20 (25.0%) | 11/20 (55.0%) | 4/20 (20.0%) | 1/20 (5.0%) | 19/20 (95.0%) | 2/10 (20.0%) |
| C1 | 7/20 (35.0%) | 8/20 (40.0%) | 4/20 (20.0%) | 1/20 (5.0%) | 17/20 (85.0%) | 2/10 (20.0%) |
| C2 | 7/20 (35.0%) | 11/20 (55.0%) | 4/20 (20.0%) | 1/20 (5.0%) | 19/20 (95.0%) | 2/10 (20.0%) |

| Contrast to C0 | Δ Strict | Δ Broad | Δ Downstream | Δ RelationArg | Δ Stable | Mechanism signal |
|---|---:|---:|---:|---:|---:|---|
| CΔ | -20.00 pp | +20.00 pp | +10.00 pp | +0.00 pp | -10.00 pp | False |
| C1 | -10.00 pp | +5.00 pp | +10.00 pp | +0.00 pp | -10.00 pp | False |
| C2 | -10.00 pp | +20.00 pp | +10.00 pp | +0.00 pp | -10.00 pp | False |

## All eight dimensions and schema

| Dimension | C0 | CΔ | C1 | C2 |
|---|---:|---:|---:|---:|
| GoalGrounded | 52/54 (96.3%) | 54/54 (100.0%) | 54/54 (100.0%) | 54/54 (100.0%) |
| Unresolved | 49/54 (90.7%) | 53/54 (98.1%) | 53/54 (98.1%) | 54/54 (100.0%) |
| Material | 52/54 (96.3%) | 54/54 (100.0%) | 54/54 (100.0%) | 54/54 (100.0%) |
| Local | 39/54 (72.2%) | 34/54 (63.0%) | 40/54 (74.1%) | 36/54 (66.7%) |
| Coherent | 52/54 (96.3%) | 54/54 (100.0%) | 54/54 (100.0%) | 54/54 (100.0%) |
| ScopeFaithful | 40/54 (74.1%) | 43/54 (79.6%) | 42/54 (77.8%) | 42/54 (77.8%) |
| NonDownstream | 42/54 (77.8%) | 40/54 (74.1%) | 41/54 (75.9%) | 40/54 (74.1%) |
| EvidenceResolvable | 52/54 (96.3%) | 54/54 (100.0%) | 54/54 (100.0%) | 54/54 (100.0%) |
| schema | 52/54 (96.3%) | 54/54 (100.0%) | 54/54 (100.0%) | 54/54 (100.0%) |

## All frozen error types (overlapping, /54)

| Error | C0 | CΔ | C1 | C2 |
|---|---:|---:|---:|---:|
| downstream_obligation | 10 | 14 | 13 | 14 |
| already_supported | 3 | 1 | 1 | 0 |
| whole_question_restatement | 7 | 14 | 11 | 14 |
| over_atomic | 0 | 0 | 0 | 0 |
| invented_requirement | 0 | 0 | 0 | 0 |
| wrong_object_scope | 0 | 0 | 2 | 0 |
| wrong_relation_arguments | 2 | 3 | 1 | 3 |
| relation_strengthening | 9 | 8 | 9 | 9 |
| irrelevant_low_value | 0 | 0 | 0 | 0 |
| unresolved_referent | 10 | 14 | 13 | 14 |
| bundled_objectives | 6 | 6 | 3 | 4 |
| outside_knowledge | 2 | 0 | 1 | 0 |
| output_contract | 0 | 0 | 0 | 0 |
| mechanical_failure | 2 | 0 | 0 | 0 |

## Pair outcomes (/27)

| Pair category | C0 | CΔ | C1 | C2 |
|---|---:|---:|---:|---:|
| same_obligation | 4 | 8 | 7 | 7 |
| compatible_obligation | 2 | 3 | 2 | 3 |
| different_but_valid | 3 | 0 | 2 | 1 |
| one_valid_one_invalid | 7 | 1 | 4 | 4 |
| both_invalid | 11 | 15 | 12 | 12 |
| raw_both_valid | 9/27 (33.3%) | 11/27 (40.7%) | 11/27 (40.7%) | 11/27 (40.7%) |
| stable_both_valid | 6/27 (22.2%) | 11/27 (40.7%) | 9/27 (33.3%) | 10/27 (37.0%) |

Stable does not credit repeated invalid obligations. CΔ has15 both-invalid pairs despite11 stable valid pairs, versus11 both-invalid for C0. It concentrates outcomes, which must not be confused with better marginal validity. Distinct valid branches still receive strict credit but not stable-selection credit.

## Threshold accounting

The frozen mechanism rule is disjunctive with only a relation-argument guard. Thus CΔ meets it overall via stable +18.52pp even though strict falls3.70pp and broadness rises12.96pp. This is a real recorded threshold crossing, not an overall-quality endorsement. C1 and C2 do not cross overall versus C0; C2 +14.81pp stable is below15, without rounding up. All three cross on the17 eligible states via stable selection. These subset signals are not substituted for overall success.

C1-CΔ overall crosses the incremental mechanism rule through broadness -11.11pp, but stable falls7.41pp. On17 path-eligible states the broadness increment is only -8.82pp (no incremental crossing); on15 observation-eligible states it is -10.00pp (crossing). Half the six-count overall broadness advantage comes from the identical-input empty-context states. Therefore there is limited mixed incremental evidence, not established path necessity or equivalence to Delta.

Every arm fails all five overall viability checks for strict, broadness, downstream, scope and stability; all satisfy the relation-argument<=7.5% check. No arm qualifies for Direct-O engineering under the complete criterion. All eligible-subset viability conjunctions also fail. Stop after this experiment, without revision or cascade.

## Context provenance second pass

Six outputs receive both path_fact_promotion and path_candidate_hardening as **content-compatible unsupported bindings**: C1 G08 R1/R2, C1 G14 R2; C2 G08 R1/R2, C2 G09 R1. They bind SOPHIE to an unverified partner interview/song-reference utterance or Euler to an unverified book citation also represented in a past query. Names already occur in C. Analogous/same errors occur in C0 or CΔ, so these are NOT six identified causal effects of adding path. Context-exclusive new facts observed:0. See per-response provenance and attribution limits in review/CONTEXT_REVIEW.json.

No path-created requirement or raw-observation-only factual promotion is demonstrated in the final obligations. In particular, the Melbourne query candidate is not hardened as ICPC host; raw FOP details at G17 do not appear as established diagnosis; unrelated artists/biographies/game citations are not imported. This does not establish that raw context is harmless or unused internally.

## Sensitivity and limitations

Replicate1 strict counts C0/CΔ/C1/C2=12/11/14/13; replicate2=13/12/12/13, each/27. Paired strict wins/losses/ties versus C0: CΔ8/10/36; C1 and C2 each7/6/41. Repeated states and question clusters are dependent.

Leaving out one question yields strict ranges: C0 41.7–50.0%, CΔ35.4–47.9%, C1 43.8–52.0%, C2 41.7–52.1%. Strict contrasts can change sign: CΔ -10.42 to+4.17pp, C1 -2.08 to+6.25pp, C2 -4.17 to+6.25pp. Low-ambiguity strict:14/23,15/21,14/18,14/17, respectively. These are arm-dependent selected response subsets, not matched populations or gate rescue. Ignoring Local and Coherent entirely gives32/54,35/54,37/54,36/54 (59.3–68.5%): structural/stale/mechanical problems remain even under this relaxed sensitivity.

Ten initial states have exactly identical requests across arms, but strict is9/20,5/20,7/20,7/20. Temperature0 did not remove variation. C1/C2 are also identical at G06 and G26 because the last4 events contain only Writer updates; the G26 replicate difference contributes one extra C2 valid response without any observation intervention.76 unique request payloads produced216 independent responses, with no reuse.

Single reviewer, prior familiarity, exposed bank, narrow mechanical window, tied batch-window recency, and2 C0 length failures limit inference. Exact bounded text is reconstructed from the historical Actor-view buffer before Writer waves; intermediate checkpoints have no contemporaneous Actor API call. No later Actor request or source audit was consulted. Raw text is often tangential under the frozen last-block rule, so lack of benefit is not a universal claim about all possible path representations. Historical53.7% used a different prompt; concurrent C0 is the formal comparison.

## Additional post-hoc robustness disclosure

These checks were added after the primary aggregate, not preregistered. They do not replace any frozen label or denominator. If the overlapping C0 G12 pair (supervisor identity versus broader author academic profile) were hypothetically treated as compatible rather than different-but-valid, C0 stable would be7/27, and the Delta stable gain would be14.81pp instead of18.52pp: its overall mechanism crossing would disappear. All three17-state eligible mechanism signals would remain. The primary pair classification is retained; the purpose is to expose one-pair threshold sensitivity.

C0 has both length failures. Conditional on schema-valid responses, strict is25/52=48.08% for C0, compared with48.15% for C1/C2; this is not the primary comparison. Removing the same two affected cases G07/G14 from every arm gives C0/CΔ/C1/C2 strict25/23/26/25 out of50. This common complete-case subset is also post-hoc. Neither check supports a large robust strict gain. See analysis/ADDITIONAL_SENSITIVITY.json.
