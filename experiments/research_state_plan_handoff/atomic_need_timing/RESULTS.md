# P3 results: when to form one AtomicNeed

Eight prefix-only checkpoints were frozen before calls: four for q546 and four for q1094. A0 reuses the historical broad M1 plan and P1 Actor response. A1 generated **one** question-only need per question and reused it at all four checkpoints. A2 generated one need per current prefix. Sixteen new Actor responses were sampled once each with identical prefix and tool menu within a checkpoint, differing only in the control card. All ten new planner responses and all 16 Actor responses arrived and passed parsing/validation; no tool was executed and there were no retries.

The pre-call `analyze.py` had a post-call reporting bug: it indexed the historical packet's integer `seq` as a string. No request or response was affected. The frozen script remains unchanged; `analyze_postcall.py` copies it with only that key-type correction and produced the summaries and review cards. The 16 A1/A2 semantic scores in `semantic_review.json` use the question and currently visible prefix only. `none` is legal at question initialization, but a state carried to a later prefix is also judged for current utility.

| Measure | A0 broad | A1 question-only | A2 evidence-conditioned |
| --- | ---: | ---: | ---: |
| Actor cells with Inspect | 5/8 | 0/8 | 4/8 |
| Search / Find / Open calls | 13 / 5 / 2 | 22 / 0 / 0 | 13 / 5 / 1 |
| Scope realized where explicitly stated | 6/8 | n/a | 7/8 |
| Current-need fidelity in manual review | not scored | 4/8 | 3/8 |
| Appropriate one-need granularity | not scored | 4/8 | 4/8 |
| Premature commitment | not scored | 0/8 | 3/8 |
| Stated need ↔ proposed source class compatible | not scored | 4/8 | 7/8 |
| Action appropriate to current need | not scored | 3/8 | 2/8 |

A1's two plans are **not eight independent planner samples**. For q546, the question-only planner returned `none`; this avoided an unsupported guess at t=0, but remained unhelpful through all four later checkpoints, where the 2023 tournament sequence and candidate statistics had become verifiable. For q1094, the single reusable need was simply to name the 95th-minute free-kick taker from a match report. It was safe and unresolved at all four checkpoints, but did not use observed club or event clues. Every A1 Actor batch used Search.

A2 produced more explicitly scoped actions, but the semantic chain did not improve consistently. At q546:25 it targeted D10, an article about one Ding opening match, while claiming its preview showed the broader 4-3/4-0 sequence; the visible preview did not establish that. At q546:33 it returned to broad player-statistics identification despite an unresolved match chain. At q1094:45 it promoted PSG–Lille from an unverified 95th-minute candidate to the named match in the need and sent Find(D34); D34 can answer that *conditional* question, but the club-origin conjunction was not established. At q1094:69 it again targeted D34 while stating corpus scope, and at q1094:77 it reverted to identifying the split-founded club despite existing D37/W42 evidence. The two inspections marked plausible for their **stated** atomic need include the unverified PSG–Lille candidate; only q546:41 has both a plausible source and a need that remains relevant to the original question. This is why the 7/8 source-class compatibility cannot be read as 7/8 good source routing.

P3 therefore gives **no clear A2 advantage** in current-need fidelity, premature-commitment safety, or concrete source choice. The observed A2 Scope realization shows that a specific card can drive a tool, including toward a weak or wrong target. The one-step design has no evidence-gain observation and cannot establish answer accuracy. Under the frozen contingent rule, no short rollout or Progressive Frontier prototype is initiated. The guarded-action prerequisite also fails because the atomic need and concrete source quality are not yet acceptable. A later study could test a low-commitment seed plus evidence-backed, falsifiable source hypothesis on more questions, with tool observations, before introducing persistent atomic state.
