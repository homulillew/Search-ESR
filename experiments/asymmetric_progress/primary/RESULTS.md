# C1/C2/C3 primary results

24 fresh exact Q+Claims checkpoints, 9 qids; 19 unresolved +5 resolved. Resolved controls cover only2 qids. Strict near-closure:1 checkpoint/1qid. These constraints limit generalization to stopping-boundary states.

| Metric | L0 | L1 | Audit |
|---|---:|---:|---:|
| Valid output |46/48|48/48|48/48|
| False closure |0/38|0/38|0/38|
| Correct closure |7/10|10/10|4/10|
| Valid blocker presence |34/38|38/38|37/38|
| Blocker precision |60/111 (54.1%)|90/109 (82.6%)|37/44 (84.1%)|
| Strict content+status+refs |46/111|74/109|37/44|
| Certificate adequacy among confirmations |7/7|8/10|4/4|
| Outputs with broad units |27|14|0|
| Outputs with over-demand |7|3|6|
| Unsupported-premise outputs |0|1|1|
| Status errors (units) |24|19|N/A|

L1 shows a large directional precision improvement, full valid-blocker presence and preserved closure. It does not reach the frozen90%precision gate. Remaining broad units include two opponent century counts, actor-role plus film-director joins, and occupation plus source-of-wealth. These are scored using the one-relation rule; do not replace it with a more permissive post-result rubric.

Audit rejects all38 unresolved slots but only37 have a valid blocker: A24 once presupposes a95th-minute event in the candidate final. Six resolved rejections require redundant song/quote, literal male-lead, or final-episode wording. By frozen materiality, these are over-demand, not useful cautious rejections. Adequate4/4certificates apply only to its four selected confirmations; they do not compensate for6missed closures.

L1's one unsupported-premise output imports a Horse zodiac mapping absent from Claims. Its two inadequate closure references cite only the dated album count, omitting the discriminative identity basis. A valid completion Boolean is not a full certificate.

## Frozen STOP policy pairing

| Policy |False stop|Correct stop|Missed stop|Valid decision accuracy|Calls/decision|
|---|---:|---:|---:|---:|---:|
|L|0/19|5/5|0/5|24/24|1.000|
|LL|0/19|5/5|0/5|24/24|1.208|
|LA|0/19|2/5|3/5|21/24|1.208|

Both second-call policies trigger on5/24decisions. LA loses three true stops without preventing a false stop in this primary bank. L has no false stops here, so a safety benefit has a floor effect; the bank is mostly not near closure. These data do not support an Audit semantic advantage over a second Light call.

| Mean tokens/decision |L|LL|LA|
|---|---:|---:|---:|
|Input|1243.17|1466.67|1436.04|
|Output, includes reasoning|5768.29|6161.08|7768.38|
|Reasoning subset|5609.83|5995.79|7587.46|

LA adds1977.63reasoning tokens/decision versus385.96forLL under the same20.8%trigger rate. Total formal calls, including unused replicas, are reported separately in analysis/cost.json. Two L0 schema failures lack closure_claim_refs; their raw responses and usage remain in the journal, with zero completion/presence credit and no generated validated units in the precision denominator.

## Review limitations

One Q+Claims-only reviewer; no independent replication of semantic labels. Related states/replicas are correlated. “Broad” distinguishes separate relations from minimal attributes of one relation: a dated role-qualified event is permitted, two separate opponents' career totals are not. Boundary judgments and historical materiality are auditable in review scripts; all formal gates retain that rubric. The resolved-label question is especially important because Audit failures often concern explicit but historically redundant wording.
