# Frozen-stage execution plan

1. M0: freeze provider, Python/SDK, prompt/schema/source hashes and the 13
   checkpoint hashes. Make four small ordinary/auto/forced/multi-tool calls;
   preserve raw finish reasons, tool calls and cache usage. Apply the existing
   strict atomic validator to provider and injected invalid batches. Stop
   tool-policy comparison if the gate fails.
2. M1: reuse `model_backend_atria/PREFIX_ONLY_ANNOTATIONS.json` and its
   pre-model review freeze. Request one DeepSeek no-tool diagnostic response
   on each of the 13 exact messages. Compare against the already frozen Qwen
   M1 events; keep original Qwen timeouts and malformed outputs. Use the
   pre-registered M1 evaluation rules and report complete-case sensitivity.
3. M2: mechanically select checkpoints from combined M1 planning under the
   original Group A/B/C first-in-order rule, falling back to all 13 if any
   group is undersized. Request one natural DeepSeek decision using the
   unchanged Search/Find/Open menu and original prefix. Validate whole tool
   batches without execution. Compare to the already frozen Qwen M2 cells.
4. M3: only after moderate semantic/policy signal and stable tool transport,
   freeze four selected cells and run at most four decisions in each v3a and
   Orthogonal arm. No forced final answer.
5. M4: reuse the eight exact `diagnostic_oracle_evidence` cases and the
   E0/E1 instruction. Reuse the two completed Qwen cells from the paused
   Atria M4, fill only the remaining Qwen cells, and run all DeepSeek cells.
   Score relation, belief update, unsupported override and stop calibration
   with the existing pre-call rubric.
6. M5: only after material model signal and protocol viability, freeze and
   run qid 546 and 1094 from the original questions with Orthogonal Search,
   no State, and a 12–16-decision horizon.

Every stage records errors, interruptions and unfinished cells. No best-of,
selective retry, prompt change, retriever change, or cross-model token-count
claim. Cache hit rate is the token-weighted DeepSeek `usage` hit fraction on
responses with both hit/miss fields; errors and absent fields remain unknown.
