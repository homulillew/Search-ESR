# C1 Claim-only Gap closure: result

Forty local Gap packets from ten qids used real, previously accepted and W-bound Claim statements. Twenty Gaps were fully answered; twenty omitted a material condition, including nine broader near-complete traps. No raw W text entered either model call. These assembled Claim sets test local closure semantics; they are not literal runtime prefixes or proof that the original multi-hop questions were solved.

| Arm | Premature close | Missed close | Fully resolved recall | Near-complete trap rejection | Valid outputs |
| --- | ---: | ---: | ---: | ---: | ---: |
| C0 binary | 0/20 | 0/20 | 20/20 | 9/9 | 40/40 |
| C1 missing-first | 0/20 | 1/20 | 19/20 | 9/9 | 39/40 |

Both arms meet the pre-registered numerical gate. C0 is the chosen policy because it achieves the same or better closure behavior with one field and fewer tokens. C1 accurately described the material missing condition in all 20 open packets, but one fully resolved case returned `{"missing":"None","status":"resolved"}`. The Harness's pre-frozen invariant rejected that output; it was counted as a missed close and was not repaired. It is a schema/serialization failure, not a wrong semantic belief in the model's displayed status.

C0 used 13,307 prompt and 6,347 completion tokens; C1 used 15,667 and 9,005. Prompt cache hits reported by the provider were 1,792/13,307 (13.47%) for C0 and 3,968/15,667 (25.33%) for C1. Higher cache-hit fraction did not erase C1's larger total token load. Per-cell output and raw usage are retained in `events.jsonl`.

The earlier premature-close signal was **not reproduced** in this Claim-only local bank. The ceiling result is descriptive: multiple packets reuse Claims within qid, the gaps were deliberately composed around known Claim coverage, and the sample is not an end-to-end Actor rollout. It supports using binary review for these local decisions, while V1 still prevents R1 integration.
