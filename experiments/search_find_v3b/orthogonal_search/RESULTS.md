# Orthogonal Search partial rollout results

Run on 2026-09-23 from `freeze.json`; offline gate `103/103 PASS`. The
`events.jsonl` file contains all 26 cells and their full API requests,
responses, tool results and private audits. `mechanical_summary.json` is
computed from those events by `analyze_results.py`. Thirteen frozen checkpoints
(broad 10, local-verification 3) were paired P0/P1, one continuation per arm,
at most four API decisions; no forced answer. **26/26 completed**, no API,
tool, malformed or undeclared-call errors. No cell was selectively rerun.

## Treatment fidelity

P1 called the original global retriever for its original top-k. It still
discovered **77 new documents** across 13 cells (P0: 84). On **318 old-document
hits**, P1 ran no localizer, created **zero new Search W#**, and injected **zero
old-document preview characters**. P0 had **231 old-document hits**, including
**65 new Search W#** and **304,710 old-document preview characters**. The arm
queries and number of rounds diverged naturally, so these totals demonstrate
mechanism removal; they are not a paired estimate of saved characters per
identical query. P1 retained top-k hits and did not refill new-document slots.

## Action and cost observations

| Cohort / arm | cells with Find | Find before next Search | new Find W# | no-gain Searches | Find within 2 decisions after no-gain | Search again after no-gain (cells) | natural stop |
|---|---:|---:|---:|---:|---:|---:|---:|
| Broad P0 | 1/10 | 0/10 | 1 | 0 by P1 definition | — | — | 8/10 |
| Broad P1 | 2/10 | 1/10 | 3 | 22 | 0 | 8/10 | 0/10 |
| Local verification P0 | 0/3 | 0/3 | 0 | 0 by P1 definition | — | — | 0/3 |
| Local verification P1 | 0/3 | 0/3 | 0 | 16 | 0 | 3/3 | 0/3 |
| **All P0** | **1/13** | **0/13** | **1** | — | — | — | **8/13** |
| **All P1** | **2/13** | **1/13** | **3** | **38** | **0/38** | **11/13** | **0/13** |

`NoGainSearch` means >half of returned hits were already discovered **and**
the Search result contained no new raw preview. The 38 occurrences are nested
within 13 correlated continuations, not 38 independent samples. `Find within
1/2/3` was 1/2/2 cells for P1 and 0/1/1 for P0. Raw observation characters
were P0 **438,313** versus P1 **122,515**; P1 nevertheless used more prompt
tokens (**2,234,056** vs **1,906,278**) and total tokens (**2,338,245** vs
**2,006,951**), because all P1 cells continued through four decisions whereas
eight P0 cells stopped earlier. The counts are workload outcomes, not a
controlled per-decision token efficiency estimate.

The local-verification cohort is three checkpoints from the *same* qid 1094
trajectory. They are correlated and some focus-document judgments are weak
(`EXPERIMENT_PLAN.md` says so). All three P1 cells kept searching and none
used Find. A rediscovered document alone therefore did not make the model
form a local verification action.

**Post-run source audit (not used to select checkpoints):** D38 `Inter Milan`
is 3,751 characters and contains neither `95th` nor `free-kick`. D14
`Last-minute goal` is 80,884 characters and contains two `95th` mentions,
both about penalties, not a matching 95th-minute free kick. Thus the B
focuses were reasonable from prefix titles and reasoning but poor in hindsight
for the missing player fact. B cannot estimate Find adoption conditional on
an *answer-bearing* focus document. It usefully exposes the scope-selection
problem that lies between retrieval and local verification.

## Independent review of every Find window

Five `find` calls yielded one new P0 window and three new P1 windows; the
remaining P1 call returned an **already observed W5**. The following labels use the unresolved need visible before the
call, raw returned text, and the following reasoning, not the gold answer.

| Cell / call | Need and returned text | New fact / support-refute / belief update | Useful for the current need? |
|---|---|---|---|
| P1 546:9 d1, D5 | Seeks 2023 4–3 then 4–0 run; W5 is Mark Williams' finals table, including `2023 Championship League ... 0–3`. | W5 was already in the prefix. It added no new text or requested sequence; the next reasoning says the exact sequence was not found and retries D5. | No |
| P1 546:9 d2, D5 | Seeks that Championship League path; W15 lists finals including 2021 Championship League Invitational. | No 2023 match sequence or changed conclusion. | No |
| P1 546:9 d4, D12 | Seeks 2023 Mark Selby path; W18 shows 2024/2025 Championship League final rows. | Year and event mismatch; no 4–3/4–0 sequence. | No |
| P0 546:17 d2, D14 | Seeks Ding's 2023 English Open path; W27 lists ranking finals, chiefly a 2023 UK final. | Does not establish the match sequence; the model then asserted a detailed English Open path without this support. | No |
| P1 546:33 d2, D18 | Seeks Selby's 2023 decider/4–3/4–0 path; W33 again shows 2024/2025 Championship League finals. | No matching sequence; later reasoning returns to other speculative candidates. | No |

Thus **0/2 distinct P1 checkpoints** obtained useful new local evidence by
the preregistered standard. W5 has weak candidate context, but neither the
specific need nor a subsequent belief update is satisfied. There was no
grounding success to credit to Find. The P0 546:17 example is a separate
evidence-utilization warning: it performed Find, received an irrelevant
window, then narrated unsupported match details.

## Decision and limits

The orthogonal intervention worked at the execution layer and prevented
global Search from simulating a new Find window in an old document. It did
**not** produce the strong H1 mechanism signal: Find adoption rose only from
1/13 to 2/13 cells, no Find followed any of 38 no-gain Searches within two
decisions, 11/13 P1 cells searched again after no-gain, and no useful P1 Find
window appeared. The small, selected, correlated sample cannot prove the
effect is zero. It does show capability overlap alone is insufficient in
these trajectories.

The slight adoption difference and different stopping rates reflect one
stochastic continuation per cell. The preregistered strong-support gate fails
unambiguously on useful evidence and no-gain switching, so this batch does
not justify a broad cohort or a selective rerun. Proceed to the next frozen
minimal State comparison (S0/S1/S2). This result does not support a complex
research-state architecture or a prompt patch.
