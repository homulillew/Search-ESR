# T5 three-round document mini-loop

**Status: NOT_RUN.** The T0 bank failed the severe-integrity Execution Gate before rollout. No actor/updater call, Search trajectory, observation materialization, or T5 freeze was made. The design below is retained to explain what could be tested after building a genuinely valid bank.

The intended design required eight valid cases across at least five qids with a pre-reviewed bridge-only source and real corpus text that can be materialized as an observation. For each case, Stateful and Stateless would each receive at most three Search decisions. The DeepSeek actor would jointly output `next_gap` and `search_query` in one call. Search would use the unchanged Qwen3-Embedding-8B index, top five. A frozen direct-source hit would end the trajectory; otherwise the highest ranked frozen bridge-only source would supply its pre-frozen real text. All other top-five sets would produce NoProgress. No query rewrite, source relabel, or retry would be allowed.

Both intended arms would see the latest real observation. Stateful would also persist valid parsed updater proposals, at most two per bridge observation, with offline source-support review after rollout. Stateless would retain only its original `S_pre` and the latest observation. Any future execution must first freeze case IDs, arm run order, source material and hashes, prompt hashes, source truth, search budget, stop rule, and model policy in a new bank and commit them before calls.

Metrics: direct source within three decisions, first direct round, Bridge→Direct transitions, NoProgress rounds, repeated query/path, candidate grounding, query clue load, state size, and prompt tokens. This tests document routing only; it does not evaluate Find, Reader, or final answer accuracy.
