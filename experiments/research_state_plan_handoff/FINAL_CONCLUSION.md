# Search–Find / Research State: Plan handoff and AtomicNeed timing

## Scope and audit trail

This branch adds one append-only DeepSeek `deepseek-flash` study. The 13 historical M1/M2 checkpoints, four historical M3 checkpoints, Qwen results, Atria provider-failure records, and Query Initialization results were read but not rewritten. Every new stage froze its provider, prompts, schema, historical inputs, selection, rubric and sample count before new model calls. P1 made 13 one-step Actor calls; P2 made 24 Planner and 32 Actor calls across eight four-decision trajectories; P3 made ten Planner and 16 one-step Actor calls. All 95 new provider responses completed, were usable for their stage, and were recorded with zero SDK retries; there were no provider failures. Tools ran only in P2. P3's frozen analysis script had an integer/string packet-index bug; `analyze_postcall.py` corrects only the reporting lookup after all model calls, while the frozen runner and event log remain intact.

Manual source/semantic labels are explicit in P2 `inspection_scores.json` and P3 `semantic_review.json`. These are small, two-question, unblinded judgments against visible prefixes; no population confidence interval or answer-accuracy claim is warranted. P2 H0 trajectories were historical rather than concurrently resampled. A1's eight rows represent two unique persistent question-only plans, not eight independent plans. Provider cache usage is token-weighted and reported separately below.

## Findings against the 15 required questions

1. **Did Same Prefix + Plan change DeepSeek Actor?** Yes, in this fixed one-step comparison. Among four frozen M1 document plans, H0 used Find in 0/4 and H1 in 3/4; first-call Find occurred in 2/4. Across all 13 cells, a plan-consistent action rose from 8/13 to 11/13. Three H1 batches mixed matching and conflicting actions, so this is a tool-distribution change, not perfect adherence.

2. **How much of the M1→M2 gap is explained by Plan persistence?** On the narrow document-plan action metric, visible persistence removes three of four observed H0 failures. The remaining 1/4 still chose Search. A numeric fraction of the full diagnostic-planning versus natural-policy gap is not identifiable: M1 and M2 are different tasks, and the intervention changes an Actor context message rather than isolating every planning component.

3. **Is Plan quality or realization more limiting?** Both. H1 realized document scope in 3/4, but only one of the four historical document targets was prefix-plausible. P2 often realized a broad scope while mixing Search with Inspect. The current bottleneck for useful evidence is the quality of need/source/target selection after the card changes behavior, not only the Actor's willingness to call Find.

4. **Does Orthogonal Search interact with Plan handoff?** The paired four-checkpoint trajectories show a suggestive behavioral interaction: in the Orthogonal arm, next-decision Inspect after no-gain Search rose from 2/8 H0 to 4/5 H1. There is no established **useful-source** interaction: P1H1 had only 4/16 confirmed compatible inspections and 3/16 useful observations, all useful ones from q546:33. The denominator is small and H0 was recorded earlier.

5. **Does Plan improve the scope switch after NoGainSearch?** It increases the chance that the next response *contains* Inspect, as above. It does not replace Search: all five P1H1 next responses after no-gain also contained Search, versus 7/8 P1H0. Mixed batches make a simple switch-rate claim false.

6. **Can Plan simply make Actor follow a wrong target?** Yes. P1's 546:25 Find(D10) followed the frozen target even though that target failed the prefix-only plausible-document check. P2 q1094 trajectories inspected unrelated match/stoppage documents after premature match hypotheses. Control realization and evidence utility must remain separate metrics.

7. **Did question-only AtomicNeed show the old Query Initialization premature-commitment failure?** In these two unique DeepSeek A1 outputs, no: 0/8 reused-checkpoint evaluations were marked premature. The q546 planner returned legal `none`; q1094 kept a generic taker need. The observed failure was **staleness and low utility**: q546 `none` persisted across four later evidence-rich checkpoints and A1 produced 22 Search calls with zero Inspect.

8. **Can DeepSeek initialize AtomicNeed from only a question more safely than old Qwen?** This sample suggests it can avoid unsupported specificity by returning `none` or a low-commitment generic need. It does not show that such initialization helps tool policy. The old Query Initialization protocol and this one differ, so a model-specific superiority claim would require a matched comparison.

9. **Is evidence-conditioned AtomicNeed more faithful to current uncertainty?** No clear advantage here. Manual current-need fidelity was 3/8 for A2 versus 4/8 for reused A1; the repeated A1 rows are not independent. A2 sometimes reverted to original-question criteria or advanced an unverified PSG–Lille hypothesis. A2 had 3/8 premature commitments versus 0/8 for A1.

10. **Does AtomicNeed improve concrete source selection beyond Find count?** Not established. A2 produced Inspect in 4/8 cells versus A1 0/8, and 7/8 cards named a source class compatible with their *stated* need. Yet one of the two inspected sources scored plausible for its stated need was D34 for the unverified PSG–Lille match; only q546:41 combined a currently relevant need with a plausible D17 source. P3 executed no tools, so useful evidence is unobserved.

11. **When should AtomicNeed form?** The experiment does not identify an optimal time. A durable question-only `none` was safe but became stale; evidence-conditioned generation was more actionable but sometimes overcommitted. A defensible next design is to preserve a low-commitment seed and form or revise one atomic need only when a visible observation or explicitly marked hypothesis supports its specificity, with a check before persisting it. This is a proposal, not a demonstrated rule.

12. **Should a Progressive Research Frontier be implemented now?** No. The pre-registered condition required clear P3 support for A2, which did not occur. A full persistent schema would encode unsupported targets too readily on these results.

13. **Is there evidence for hard state gating?** Not yet. P1/P2 show soft plans leave repeat Search, satisfying only the first prerequisite. P3 fails to establish reliable atomic need and source quality, the second prerequisite. Masking Search on these cards could force wrong-source inspection. No guarded-action experiment was run.

14. **Which State fields have demonstrated causal value?** The **visible broad-plan card as a bundle** changed action selection in P1, especially document scope. The study does not identify the separate causal contribution of `CurrentNeed`, `ExpectedSourceType`, `Scope` or `Target`, because those fields were always handed off together. Target fidelity can be harmful when its source is weak. Deterministic D#/W#, no-gain and inspection history support audit and are prerequisites for a future controlled test, not proven semantic causes here.

15. **Continue State research or turn to Workspace/source routing?** Prioritize workspace/source routing and evidence checks: show the Actor which existing D# could answer the current need, distinguish event records from biographies and generic pages, and require match-clue verification before promoting a candidate. A smaller State experiment can then isolate one field or evidence-grounding rule. The P1 causal signal justifies continued limited State work; P2/P3 do not justify a large runtime state or training intervention.

## Cache and decision

DeepSeek reported prompt-cache usage for all 95 new responses. The weighted hit rate, `sum(hit tokens) / sum(hit + miss tokens)`, was **90.46%** overall: 3,649,024 hit tokens and 384,693 miss tokens. By call group: P1 Actor 99.14% (13); P2 Actor 85.92% (32); P2 Planner 87.39% (24); P3 Planner 98.63% (10); P3 Actor 99.28% (16). These are provider-reported prompt-token cache rates, not response reuse or model-accuracy rates. There were zero API errors and zero missing usage records. The per-response ledger is in `CACHE_USAGE.json`.

The authorized sequence stops after P3 analysis: no P3 short rollout, P4 prototype, hard action guard, RL or SFT was undertaken. The positive finding is limited but real: visible Plan handoff changes the Actor's next action distribution. The remaining chain—state-appropriate action to compatible source to useful evidence—was not reliably achieved.
