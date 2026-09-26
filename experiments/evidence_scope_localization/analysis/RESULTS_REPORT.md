# R1 reviewed results

Primary: exact support or refutation actually returned within at most two decisions. One model sample per case/arm. No Writer or evaluator-controlled early stopping. Fresh K has ten Need families but only five qids; N has eight families/eight qids. Challenge is separate. No population significance or equivalence claim.

## Evidence and access

| Bank | Arm | Exact | First action | Recovery after no first evidence | First existing exact D use | Mean actions | Mean actions to evidence, successes only |
|---|---|---:|---:|---:|---:|---:|---:|
| K | A0 | 9/10 | 9/10 | 0/1 | 4/10 | 1.00 | 1.00 |
| K | A1 | 8/10 | 7/10 | 1/3 | 8/10 | 1.10 | 1.12 |
| K | A2 | 10/10 | 10/10 | — | 2/10 | 1.10 | 1.00 |
| K | A3 | 9/10 | 9/10 | 0/1 | 10/10 | 1.10 | 1.00 |
| N | A0 | 6/8 | 6/8 | 0/2 | 0/8 | 1.12 | 1.00 |
| N | A1 | 6/8 | 6/8 | 0/2 | 0/8 | 1.12 | 1.00 |
| N | A2 | 6/8 | 6/8 | 0/2 | 0/8 | 1.00 | 1.00 |
| challenge | A0 | 3/5 | 2/5 | 1/3 | 2/5 | 1.60 | 1.33 |
| challenge | A1 | 5/5 | 3/5 | 2/2 | 4/5 | 1.40 | 1.40 |
| challenge | A2 | 3/5 | 2/5 | 1/3 | 1/5 | 1.60 | 1.33 |
| challenge | A3 | 3/5 | 3/5 | 0/2 | 5/5 | 1.60 | 1.00 |

Recovery denominator includes early STOP/schema failures; it is not conditional on an attempted second tool. Mean actions to evidence excludes failures and is selection-sensitive. It should be read alongside exact success. Runtime failures truncated nine trajectories after their successful first tool; costs and second decisions are therefore incomplete for those cases.

## Tools and cost

| Bank | Arm | Search | Find | Open | Input | Output | Reasoning (included in output) | API calls | Cache hit/input | Model seconds sum | Tool seconds sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| K | A0 | 6 | 4 | 0 | 85002 | 3847 | 2913 | 18 | 23.2% | 28.97 | 15.52 |
| K | A1 | 1 | 10 | 0 | 84863 | 4067 | 2927 | 19 | 14.9% | 28.93 | 7.23 |
| K | A2 | 9 | 0 | 2 | 88614 | 4762 | 3823 | 19 | 39.0% | 37.42 | 37.15 |
| K | A3 | 0 | 11 | 0 | 75581 | 5679 | 4686 | 19 | 11.0% | 37.48 | 4.12 |
| N | A0 | 8 | 0 | 1 | 46177 | 3047 | 2298 | 14 | 17.7% | 23.08 | 41.38 |
| N | A1 | 8 | 1 | 0 | 48086 | 3408 | 2550 | 14 | 14.6% | 23.56 | 41.15 |
| N | A2 | 8 | 0 | 0 | 39733 | 2786 | 2131 | 13 | 24.2% | 23.71 | 40.72 |
| challenge | A0 | 5 | 3 | 0 | 46179 | 3880 | 3169 | 10 | 21.9% | 23.53 | 16.83 |
| challenge | A1 | 1 | 5 | 1 | 45425 | 3411 | 2783 | 10 | 15.5% | 23.69 | 5.45 |
| challenge | A2 | 7 | 0 | 1 | 44995 | 2716 | 2052 | 10 | 31.0% | 20.97 | 23.32 |
| challenge | A3 | 0 | 8 | 0 | 39204 | 2947 | 2241 | 10 | 11.8% | 19.19 | 1.34 |

Total: 156 API calls, **zero Writer calls**, 53 Search / 42 Find / 5 Open; 643,859 input, 40,550 output, 31,573 reasoning tokens. Weighted cache hit **135,808/643,859 = 21.09%**; miss 508,051; nonzero-cache requests 151/156. Cache depends on concurrency/order and is a cost observation, not a semantic outcome.
Run wall time **126.71s**, including retrieval initialization; model elapsed sum 290.53s, tool elapsed sum 234.22s. Overlapping sums are not additive wall time. Recorded HTTP concurrency peak 8, tool peak 5; GPU forwards alone were locked. No monetary cost is inferred.

## Paired fresh cells

| Case | QID | Structure | A0 | A1 | A2 | A3 |
|---|---|---|---:|---:|---:|---:|
| K_VN06 | 546 | prose | ✓ | ✓ | ✓ | × |
| K_VN08 | 546 | mixed | ✓ | ✓ | ✓ | ✓ |
| K_VN09 | 546 | mixed | ×* | ✓ | ✓ | ✓ |
| K_VP01 | 177 | list | ✓* | ×* | ✓* | ✓* |
| K_VP09 | 435 | prose | ✓ | ✓ | ✓ | ✓ |
| K_VP10 | 435 | prose | ✓ | ✓ | ✓ | ✓ |
| K_VP11 | 517 | prose | ✓ | ✓ | ✓ | ✓ |
| K_VP13 | 546 | prose | ✓ | ✓ | ✓ | ✓ |
| K_VP14 | 546 | mixed | ✓ | × | ✓ | ✓ |
| K_VP18 | 1034 | prose | ✓ | ✓ | ✓ | ✓ |
| N_VN05 | 311 | not_applicable | × | × | × | — |
| N_VP01 | 177 | not_applicable | ✓ | ✓ | ✓ | — |
| N_VP03 | 186 | not_applicable | × | × | × | — |
| N_VP08 | 435 | not_applicable | ✓* | ✓* | ✓* | — |
| N_VP11 | 517 | not_applicable | ✓ | ✓ | ✓ | — |
| N_VP13 | 546 | not_applicable | ✓ | ✓ | ✓ | — |
| N_VP15 | 580 | not_applicable | ✓* | ✓* | ✓* | — |
| N_VP17 | 1034 | not_applicable | ✓ | ✓ | ✓ | — |
| C_VN01 | 311 | table | ✓ | ✓ | ✓ | × |
| C_VN03 | 311 | table | ✓ | ✓ | ✓ | ✓ |
| C_VN07 | 546 | prose | × | ✓ | × | × |
| C_VP06 | 387 | prose | × | ✓ | × | ✓ |
| C_VP12 | 517 | table | ✓ | ✓ | ✓ | ✓ |

* Retained schema/runtime failure; a ✓* means actual exact evidence preceded the runtime error. See engineering/INCIDENT.md for the independent failure-free sensitivity.

## Source-hit versus window-hit

Action denominator: Search calls returning any audited exact source; numerator: none of their windows provides exact evidence. Window denominator: returned windows from exact sources; numerator: that particular window omits the relation. A Search can include a missed window and another successful one.

| Bank | Arm | Failed exact-source Search actions | Exact-source Search windows missing relation |
|---|---|---:|---:|
| K | A0 | 0/6 | 2/9 |
| K | A1 | 0/1 | 0/2 |
| K | A2 | 0/9 | 4/14 |
| N | A0 | 0/6 | 0/10 |
| N | A1 | 0/6 | 0/9 |
| N | A2 | 1/7 | 2/11 |
| challenge | A0 | 5/5 | 6/6 |
| challenge | A1 | 0/1 | 0/1 |
| challenge | A2 | 5/7 | 5/7 |

Overall: **11/48 (22.9%)** source-hit Search actions fail at window access, and **19/69 (27.5%)** correct-source windows miss the relation. Five of 53 Search calls return no audited exact source. K alone: 0/16 failed source-hit Search actions despite 6/25 missed individual windows; other returned windows recover the relation. Challenge drives most action-level misses.

## Structure sensitivity (fresh K only)

| Relation region | Cases | A0 | A1 | A2 | A3 |
|---|---:|---:|---:|---:|---:|
| list | 1 | 1/1 | 0/1 | 1/1 | 1/1 |
| mixed | 3 | 2/3 | 2/3 | 3/3 | 3/3 |
| prose | 6 | 6/6 | 6/6 | 6/6 | 5/6 |

Structure labels describe the relation region. No fresh pure-table case survived eligibility; three table/infobox challenges are not a fresh structural comparison. K_VP14 A1 repeats the start of the correct WPBSA table, but K_VN06 A3 misses the Class-of-92 relation in prose. Table-specific superiority or failure is not established.

## Failures, including nonsemantic incidents

| Cell | Final status | Labels | Explanation |
|---|---|---|---|
| C_VN01:A3 | budget_exhausted | S5, S6 | Production writer/director credits are absent; fictional museum director or a clipped infobox is not the requested credit list. |
| C_VN07:A0 | budget_exhausted | S1, S5 | No Higgins professional-debut relation; Williams professional date and Higgins junior matches cannot establish it. |
| C_VN07:A2 | budget_exhausted | S1, S5 | No Higgins professional-debut relation; Williams professional date and Higgins junior matches cannot establish it. |
| C_VN07:A3 | budget_exhausted | S5, S6 | No Higgins professional-debut relation; Williams professional date and Higgins junior matches cannot establish it. |
| C_VP06:A0 | budget_exhausted | S1, S5 | Dated setup preview repeats wireless keyboard but still omits exact paper/animation relation. |
| C_VP06:A2 | budget_exhausted | S1, S5 | Dated setup preview repeats wireless keyboard but still omits exact paper/animation relation. |
| K_VN06:A3 | budget_exhausted | S5, S6 | No Ronnie professional-debut relation; maximum counts and Williams own 1992 debut cannot substitute. |
| K_VN09:A0 | actor_failure | API/schema | No valid tool observation; retained schema/provider failure. |
| K_VP01:A0 | runtime_failure | runtime/tool | {'type': 'AttributeError', 'message': "'dict' object has no attribute 'append'"} |
| K_VP01:A1 | actor_failure | API/schema | No valid tool observation; retained schema/provider failure. |
| K_VP01:A2 | runtime_failure | runtime/tool | {'type': 'AttributeError', 'message': "'dict' object has no attribute 'append'"} |
| K_VP01:A3 | runtime_failure | runtime/tool | {'type': 'AttributeError', 'message': "'dict' object has no attribute 'append'"} |
| K_VP14:A1 | budget_exhausted | S5, S6 | Wrong player, global per-year maximum totals or table beginning omit Ding qualifying dated count. |
| N_VN05:A0 | budget_exhausted | S4 | No Brum run dates in this window. A2 retrieves correct full source 68507 once, but its preview starts below the Brum 1991–2002 row. |
| N_VN05:A1 | budget_exhausted | S4 | No Brum run dates in this window. A2 retrieves correct full source 68507 once, but its preview starts below the Brum 1991–2002 row. |
| N_VN05:A2 | budget_exhausted | S4, S5 | No Brum run dates in this window. A2 retrieves correct full source 68507 once, but its preview starts below the Brum 1991–2002 row. |
| N_VP03:A0 | actor_stop | S2, S8 | One offline player, reviews and game credits do not exclude other player modes; no explicit no-multiplayer source was acquired. |
| N_VP03:A1 | actor_stop | S2, S8 | One offline player, reviews and game credits do not exclude other player modes; no explicit no-multiplayer source was acquired. |
| N_VP03:A2 | actor_stop | S8 | One offline player, reviews and game credits do not exclude other player modes; no explicit no-multiplayer source was acquired. |
| N_VP08:A0 | runtime_failure | runtime/tool | {'type': 'AttributeError', 'message': "'dict' object has no attribute 'append'"} |
| N_VP08:A1 | runtime_failure | runtime/tool | {'type': 'AttributeError', 'message': "'dict' object has no attribute 'append'"} |
| N_VP08:A2 | runtime_failure | runtime/tool | {'type': 'AttributeError', 'message': "'dict' object has no attribute 'append'"} |
| N_VP15:A0 | runtime_failure | runtime/tool | {'type': 'AttributeError', 'message': "'dict' object has no attribute 'append'"} |
| N_VP15:A1 | runtime_failure | runtime/tool | {'type': 'AttributeError', 'message': "'dict' object has no attribute 'append'"} |
| N_VP15:A2 | runtime_failure | runtime/tool | {'type': 'AttributeError', 'message': "'dict' object has no attribute 'append'"} |

S1–S8 are multi-label descriptions, not mutually exclusive causal estimates. N_VP03 A0/A1 stops after one local inspection; A2 stops immediately. This is S8/overinterpretation, not S3, which requires two unsuccessful inspections of the same wrong source. K_VP14 A1 selects a correct source twice; its repeated query is S6, not wrong-source local lock.

## Query attributes

Exact repetition means the same tool, same local target (if any), and identical query bytes. Entity/relation presence is a frozen lexical annotation, not a subjective good-query score.

| Tool | Actions | Repeated query | Entity terms | Relation terms | Same-document rediscoveries (windows) |
|---|---:|---:|---:|---:|---:|
| search | 53 | 0 | 53 | 51 | 102 |
| find | 42 | 1 | 9 | 40 | 0 |
| open | 5 | 0 | 0 | 0 | 0 |

Local query wording can choose a wrong occurrence even in the gold document (Class of92; production credits; WPBSA table start). Global queries can repeatedly retrieve a correct source with the same unsuitable preview (paper setup challenge). This bank does not identify a single universal query defect.
