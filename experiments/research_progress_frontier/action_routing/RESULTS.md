# Stage C: Action routing and optional Verify

The frozen 25-case bank contains five cases each for source, location, context, closure, and complete uncertainty. The two arms each received one response per case; no tool was executed. The pre-call gate passed 7/7 checks, and there were no provider errors or retries.

| Arm | Correct first action | Search/source | Find/location | Open/context | Verify/closure | Submit/complete | Schema-compatible arguments |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C-A, no tool schema | 25/25 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 10/25 |
| C-B, real tool schema | 23/25 | 5/5 | 5/5 | 5/5 | 3/5 | 5/5 | 25/25 |

The prespecified C-A gate (at least 75% overall and 60% in each class) passed. The frozen eight-case Stage D selection is unaffected by these responses. In C-B, two closure cases (`C_closure_546`, `C_closure_177`) chose `open` around an already observed window instead of invoking optional `verify`. This is RP12, not a failed semantic verification: Stage C did not execute either tool.

C-A's low argument validity is a real distinction between abstract routing and callable tool arguments. All five `find` responses used `doc_id` or `document_id` instead of `doc_ref`; all five `open` responses used `window`, `window_id`, or omitted the required `direction` instead of the exact `window_ref`/`direction` pair; all five `verify` responses used `claim` or `claim_id` instead of `claim_ref`. They were **not** repaired or rescored. The C-A prompt requested an appropriate JSON object but supplied no actual tool parameter schema; therefore 10/25 measures deployability of these free-form arguments, not a schema-following comparison with C-B.

DeepSeek reported prompt cache hits/misses of 0/5,971 tokens in C-A and 18,304/6,217 in C-B (weighted hit rate 74.65% for C-B). These provider counters are descriptive.

The five `complete` cases are deliberately completed **local subtasks**. Their 5/5 Submit rate does not establish that the original multi-hop questions were solved.
