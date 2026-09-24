# C1 Claim-only Gap closure

This independent local diagnostic uses 40 packets across 10 qids. Each supplied Claim is copied from a historical supported `V_commit` in `gap_evidence_claim_loop/claim_commit/outcomes.json`, with its W ref retained by the Harness. The reviewer composed local semantic Gaps from the original Question and those stable Claims before either C1 arm was called. These are diagnostic Claim sets assembled from real source-bound Claims; they are **not** asserted to be literal historical runtime states or solutions to the full question.

Each qid contributes two locally fully resolved Gaps, one incomplete conjunction and one broader missing-condition trap. The ten traps include dense Claim sets that still omit a date, count, relation, sequence or identity condition. `BANK.json` freezes the required status and material missing condition. The model input contains only Question, Active Gap and Committed Claims. Historical packet IDs and reviewer labels remain private.

C0 returns binary `status`. C1 first writes a nonpersistent `missing` string, then returns `status`. The Harness treats a nonempty `missing` with `resolved`, or an empty `missing` with `open`, as an invalid decision. Both arms use the same 40 packets, one DeepSeek `deepseek-flash` call per packet and arm, no retries or repairs. Failed or invalid responses count as wrong on all applicable metrics.

Report premature close among open packets, missed close among fully resolved packets, fully resolved recall, near-complete trap rejection, and reviewer assessment of missing descriptions. A policy is deployable only if premature close ≤5%, missed close ≤10%, fully resolved recall ≥90%, and near-complete trap rejection ≥90%. If C0 passes, it is preferred to C1.
