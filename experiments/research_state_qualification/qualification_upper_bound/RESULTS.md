# R1: reviewed qualification upper bound

All 13 historical P1 checkpoints were retained in their frozen order. The single-reviewer prefix-only annotation produced two `no_target`, seven `hypothesis_only` and four `inspectable` cells. H0 is the historical one-step Actor response with its broad M1 Plan; H1 is one new response to that exact request plus the descriptive Qualification Card. All 13 H1 responses passed the unchanged tool validator, no tools ran, no retries occurred and there were no API errors. The review packets, annotation, request hashes, provider configuration and rubric were frozen before calls.

| Prefix-only status | Primary paired measure | H0 broad Plan | H1 + qualification |
| --- | --- | ---: | ---: |
| `hypothesis_only` (7) | Inspected named unqualified candidate | 2/7 | **3/7** |
| `hypothesis_only` (7) | Candidate inspected as first call | 1/7 | **3/7** |
| `inspectable` (4) | Inspected qualified candidate | 2/4 | **2/4** |
| `inspectable` (4) | Candidate inspected as first call | 1/4 | **1/4** |
| `no_target` (2) | Any Find/Open | 0/2 | **0/2** |

Target-level changes explain the flat/worse aggregates. At 546:17, H1 gained Find(D11), the reviewed 2023 tournament-results source, but it first opened D12 in the same batch. At 546:33, H0 found qualified D17 while H1 reverted to two Search calls. At 1094:69, H0 only searched while H1 opened the unqualified D34 candidate twice. The two historical hypothesis-target inspections at 546:25 and 1094:45 persisted under H1; at 546:25 Find(D10) moved from second to first call. The four remaining `hypothesis_only` cells did not inspect the named candidate in either arm. Both `no_target` cells only searched in both arms.

Across statuses, ten of 13 batches differ by tool count, order, or target. Much of that difference is a change in the number of Search calls rather than improved qualification use. Search/Find/Open calls in H0 versus H1 were 29/5/2 versus 27/4/4. For `inspectable`, three of four H1 cells still contained a Search outside the frozen acceptable immediate scopes, the same count as H0. One cell gained the qualified source and another lost it. The results therefore fail the preregistered R1 progression rule: there are not two paired target improvements with preserved inspectable utilization, and harmful hypothesis inspection increased.

The candidate-inspection metric maps Open(W#) to its prefix-visible parent D#. It is a **routing proxy**: R1 performs no Find/Open tool execution, so it cannot determine evidence yield or whether an individual query/window would succeed. Opening a hypothesis source could be a reasonable attempt to falsify part of it; the metric records failure to *de-target* that source, not proof that the call itself was harmful. The reviewer's curated immediate need and the status are delivered together; this upper-bound intervention does not isolate the effect of the status word. With only two questions and one model sample per cell, the result is mechanistic and descriptive, not a population effect estimate.

## Failure classification

| Code | R1 observation |
| --- | --- |
| QF1 unsupported candidate promoted | The hypothesis-only D34 was newly inspected at 1094:69; D10 and D34 inspection persisted at 546:25 and 1094:45. This is an action proxy, not a claim that an answer was adopted. |
| QF2 observed evidence over-interpreted | No explicit evidence-to-belief claim was scored from one-step outputs; this needs R2 or a continued trajectory. |
| QF3 stale target retained | The already visible D10/D34 candidate remained attractive at 546:25 and 1094:45 despite the missing prerequisite; one-step R1 cannot attribute when it became stale. |
| QF4 suitable source not promoted | The reviewer explicitly promoted D11/D17/D37; model self-promotion would be tested only in R2. |
| QF5 correct qualification ignored | Flagged at 546:25, 546:33, 1094:45, 1094:61 and 1094:69 by the frozen target/status rubric; hypothesis-source inspection could instead be exploratory falsification. |
| QF6 correct qualification but wrong D selected | No case is confirmed: the extra D12 open at 546:17 may also be a relevant match source, and R1 has no returned observation. |
| QF7 correct D but local query/window fails | Unobservable: no tools executed. |
| QF8 useful evidence but belief fails to update | Unobservable: no tools or next belief state. |

**Stop decision:** R1 does not supply the predicted helpful behavioral signal. Under the frozen protocol, R2 self-qualification, R3 Orthogonal rollout, R4 Workspace Directory and R5 Guard are not run. The next controlled question is how an Actor should consume a three-way status without treating the mere mention of an unqualified D# as an invitation to inspect it. A controller/encoding experiment should precede any persistent model-generated qualifier.
