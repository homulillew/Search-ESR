# G4v2 transition, state update and replan

20 frozen real transitions, 29 source-window updater calls, 40 Goal Reviewer calls, 80 Actor calls. All updaters/reviewers valid; 79/80 Actors valid. One R0 Find contains forbidden k and is retained as invalid. 88 real actions executed without tool errors.

## Source-supported state

52 proposed Claim sentences: **51/52 supported (98.08%)**; 36/52 atomic under the one-independently-checkable-proposition rule. Support is not equivalent to task relevance. One temporal join is unsupported: T19 binds retrospective 67 albums to the 2016 Forbes interview. No direct partial-clue-to-full-candidate Claim promotion was found. T14's identification is supported jointly by prior plots/roommate and current five-season observation.

Both materially contradicted candidates (Heart and Hijitus) are cleared. Yet R3 on T07 pursues Heart's birth name despite the cleared hypothesis and timing evidence. Correct state rejection is therefore insufficient to guarantee rejection in the next action. This failure occurs with online Residual, not with the persistent-Gap comparator.

## Decisions and actual evidence

| Arm | Correct stop / resolved | Premature / open | Late | Any Progress / 20 | Tool calls |
|---|---:|---:|---:|---:|---:|
| R0 Legacy Persist | 6/6 | 5/14 | 0 | 4 | 16 |
| R1 State-only | 6/6 | 3/14 | 0 | 6 | 21 |
| R2 Oracle + Residual | 5/5 | 1/15 | 0 | 8 | 28 |
| R3 Online + Residual | 6/6 | 2/14 | 0 | 6 | 23 |

R3 reduces premature stopping by one versus R1, with equal primary Progress and two extra tool calls, plus the Reviewer cost. R2 is strongest descriptively, but its different claim state prevents attributing the whole difference to residual computation. At T13 the online updater commits the S1 plot and five-season count present in the real batch; the frozen oracle POST deliberately leaves those uncommitted. Consequently online T13 is resolved, oracle T13 remains open, and oracle-arm STOP is premature. Source-grounded online truth is evaluated independently instead of copying oracle labels.

Primary resolution follows the frozen discriminative-identity plus requested-relation policy. The strict all-clues sensitivity marks q435 resolved cells open: correct stops become R0/R1/R2/R3=3/3/2/3; premature=8/6/4/5. This sensitivity also exposes missing first-album wording in online T11/T12; primary identification has strong age/activist/67-album/Wasakara support plus exact May 2017 count. No alternate truth enters production.

Goal Reviewer closure matches independent primary labels in **38/40**: oracle 20/20, online 18/20. Online T02 and T16 prematurely resolve partial identities. T19 stays open but its residual inherits the updater's false count-at-2016 premise, narrowing the remaining work to whether that feature was in May. One Actor further says to confirm 67 at the May feature. This is an upstream state error propagated by a controller that trusts Claims.

No unrelated new-goal drift or late research after supported closure was found. Persistent Gap is not shown to cause over-research in this bank. Several gaps call Rangers “identified” too early while still researching the requested founding relation; these are overcommit warnings, not unrelated-goal drift.

Alternative-source sensitivity Any Progress: 5/8/10/10. It includes observed Goat-year calendars and the Milan–Liverpool candidate; these do not resolve the disputed birth date or football match. As in G3, this sensitivity is a non-exhaustive lower bound. Primary review reads every known-pool returned window and requires a new relation, not document membership. Per-tool yield, marginal second actions, source repetition, literal claims and reasons are in the adjacent JSON artifacts.
