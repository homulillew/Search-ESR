# T4 controlled two-round feedback

**Status: NOT_RUN.** Post-T3 original-question integrity audit leaves at most four provisional cases across two qids. This is below the frozen Execution Gate (eight cases, five qids), so no R3 request or Search was made. The arm definitions below record the intended comparison only; no T4 freeze or results exist.

The intended arms would receive an identical, valid Round 1 bridge observation. Round 2 would use the same original question, referent-preserving next Gap, DeepSeek query-writer prompt, retriever, and top-50 budget. R0 would forget the observation and retain `S_pre`; R1 would receive raw observation text; R2 would receive a verified `S_post`; R3 would receive `S_pre` plus T3's actual parsed online claims. Invalid or empty T3 output would leave `S_pre` intact. R0/R1/R2 could reuse valid T1 requests, queries, and retrieval hits exactly; only R3 would create new model requests. All inputs and reused artifact hashes must be frozen and committed before any future calls.

Primary metrics: any frozen direct-source Recall@1/3/5 and MRR@50, first sufficient rank, paired comparisons R2/R3 vs R0/R1, prompt tokens. Bridge→Direct uses only the cases whose Round 1 source is bridge-only for the frozen downstream Gap. All 12 cases are preserved; `U1_B07` is excluded from the clean causal cohort. No performance gate prevents T5.
