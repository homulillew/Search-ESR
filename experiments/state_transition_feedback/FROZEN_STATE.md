# Historical boundary

Base branch: `experiment/state-conditioned-retrieval`, remote HEAD `22c3758bd0a810c0bd2efd1e2d5ffdea92c6afe0` after `git fetch origin`. T0 uses its frozen SC0 windows and U1 target Gaps, plus read-only source audits of the 100,195-document corpus and previous top50 retrieval. The prior S1 registered direct@5 was 21/24→23/24; one q186 canonical rescue was already answerable from an alternate S0 rank-3 source. Previous bridge labels based solely on distinct doc IDs are not imported as truth. This branch freezes new transition-specific bridge decisions before any new LLM call.

Unrelated pre-existing untracked paths under `experiments/auto_research/`, `research_loop/`, and `指令提示词/` are outside this experiment and remain untouched.

## Post-T3 integrity finding

T0 source sets, requests, model responses, and retrieval hits remain frozen. A later audit against the **original** questions found six original-answer leaks and two contradicted candidates in the 12 transition bank. At most four provisional cases across two qids remain. This crosses the preregistered severe-integrity stop rule; T4 and T5 have no calls or freezes. See `transition_bank/POST_T3_INTEGRITY_AUDIT.md`. Earlier T1/T2 11-case subsets are conditional next-Gap diagnostics, not clean original-question causal cohorts.
