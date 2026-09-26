# Counterfactual State growth

All arms start from the same 55 historical pre-states, totaling107,404 serialized Q+Claims+Hypothesis characters. Each packet is applied independently, with no deletion or repair of inherited Claims.

| Arm | New Claims/packet | Mutation/55 | No change/55 | Post semantic chars | Increment | Relevant Claim chars* | Incidental Claim chars* | Relevant density* |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|U0|1.382|41|14|114,556|7,152|27,425|45,212|37.76%|
|Uc|1.291|37|17|113,865|6,461|27,303|44,628|37.96%|
|U1|0.364|15|40|109,227|1,823|27,037|40,774|39.87%|

*Sensitivity: inherited Claim relevance uses archived v2 labels, new increments use current v3.1 review. All687 inherited statement occurrences mapped (repeated across independent packets); this is not687 independent facts. Density excludes Question/Hypothesis and uses Claim text characters only. Some duplicate relevant statements have no novelty; this ratio is not full admission precision. Primary increment-only character counts are in RESULTS. Invalid Uc is not a correct no-change update, although no proposal is applied.

Lower incremental growth does not remove historical bloat. Relative to Uc, total local post-state characters fall only4.08%, whereas new growth falls71.78%. No closed-loop cost or resolution effect is estimated.
