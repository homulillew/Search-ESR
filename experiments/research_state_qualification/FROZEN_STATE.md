# Historical handoff and stage ordering

The new branch starts at remote `origin/experiment/research-state-plan-handoff` commit `72ac72e`. The read-only P1 M1 plans and P1 handoff Actor responses provide the 13 R1 cases. P2 historical Orthogonal+Plan continuations are the only planned R3 Q0 baseline. P3 and Query Initialization are background and are never rewritten. No Atria output is substituted for DeepSeek behavior.

R1 selection is all 13 P1 checkpoints in their historical order, before examining any new R1 response. A prefix-only packet is constructed from `PREFIX_ONLY_PACKETS.json`, with the exact historical M1 broad plan attached. Single-reviewer annotations are frozen before the R1 API call. Each later stage, if its gate passes, receives a separate pre-call freeze and result directory. R4/R5 are conditional and no files are generated for them in advance.
