# Confirmatory Admission Replay — positive selectivity, gate not passed

55 real packets from 10 qid clusters; U0 archived, Uc and U1 55 new one-attempt calls each. Uc system/user strings are byte-equivalent to v2. U1 changes admission semantics and adds only the exact generating Actor Gap to the view. All 10,227 baseline tracked files and both freezes verified unchanged. Single Codex semantic reviewer; arm-masked deduplicated output queue, not independent or perfectly blind review.

| Metric | U0 archived | Uc transport control | U1 selective admission |
|---|---:|---:|---:|
| Valid / planned | 55/55 | 54/55 | 55/55 |
| New Claims | 76 | 71 | 20 |
| Source-supported | 75/76 | 71/71 | 19/20 |
| Decision-relevant | 26/76 | 27/71 | 18/20 |
| Incidental | 50 | 44 | 2 |
| Novel | 74/76 | 68/71 | 20/20 |
| Fully admissible (support+relevance+novelty+scope) | 24/76 | 25/71 | 18/20 |
| Frozen scoped atom recall | 21/27 | 23/27 | 20/27 |
| Material scope losses | 4 | 2 | 1 |
| Semantic Hypothesis errors | 11 | 10 | 3 |
| Correct empty admission /38 no-new-fact packets | 14 | 17 | 36 |
| Actual no-change updates /55 planned | 14 | 17 | 40 |
| State mutation /55 | 41 | 37 | 15 |
| Local semantic-character increment | 7,152 | 6,461 | 1,823 |
| Relevant new Claim characters | 2,203 | 2,081 | 1,815 |
| Incidental new Claim characters | 4,576 | 3,992 | 138 |

U1–Uc incidental count falls 42 (95.45%), with 25 improving packets and no worsening packet, across nine qids (q387 unchanged at zero). Relevant precision rises 38.03%→90.00%. State character increment falls 71.78%; this is independent local replay, not a cumulative rollout estimate. Average new Claims per packet: 1.38/1.29/0.36. Hypothesis semantic errors improve in seven pairs, worsen in none. One Uc interface failure is kept separate from semantic Hypothesis errors.

However, recall falls **85.19%→74.07% (−11.11 percentage points)**: five worsening packets, two improving, 48 ties. The source-support decline is one ambiguous-count strengthening, not a large unsupported-answer pattern; its precision impact is magnified by the smaller denominator. These mixed results do not pass the stipulated no-material-recall-loss gate.

## Mechanism review

- q311: U1 retains French/Belgian origin but again misses the explicitly visible **four-minute runtime**, despite the prior 4–10-minute Claim. Uc captures both. The runtime is a more precise/source-conflicting discriminator, not redundant topic information.
- q546: U1 emits nothing from a wrong-sequence-year page that nevertheless states a **fifth career 147 in 2012/13**. Uc captures that independent original-question criterion with the year. Current Gap matching appears to suppress a useful separate requirement. U1 also drops a partial 2007 maximum tally anchor.
- q186: U1 drops a conflicting 1993 release listing; a later 1992 corroboration is omitted by all under the strict source-bound recall rubric. Source support is not the only issue: conflict/novelty interpretation matters.
- q177: U1 drops the 1974-double atom when it retains the 1982 championship; that is a less severe loss because both bear on historical success. Its other emitted Claim strengthens ambiguous “five wins” into “five league titles,” a local scope error.
- q435: U1 preserves the secondary source/list/date context of 65 albums better than Uc in one pair. Neither a retrospective count nor an article date should be converted into a stronger event relation. Uc additionally puts an overbound Forbes-reporting statement in Hypothesis.
- q1094: U1 correctly clears the PSG/Messi fixture on both newly observed scoring contradictions; Uc retains it. Two inherited contradictions remain uncleared when the new Observation is unrelated (q311 and q1094).
- q1034: U1 still sets Jun. K from only a debut-single date, a weak new-candidate promotion. Other unrelated profiles are mostly suppressed.
- q580: the only historical Updater Observation in this bank is a cast list. It cannot establish a season-count upper bound. Initial Workspace W3 was not reprocessed here, so the five-season Workspace→Claim failure is not retested by this packet.

Atoms were frozen before replay. Some atoms are scoped composite relations and two (1974 double, partial maximum tally) are less decisive; report that sensitivity rather than alter their denominator after results. The high-impact runtime and independent maximum-threshold misses remain concrete recall failures. No new atom was inserted into primary scoring after output review.

## Gate decision

**FAIL_RECALL_TRADEOFF; no confirmatory G4/G5.** Selectivity and mutation control clearly improve, but useful information is also lost. This does not establish that cleaner online State improves a controller. Per user discretion, a separate bounded exploratory prompt amendment may test proposition-level requirement coverage and scoped novelty. It cannot replace these outputs, retrospectively pass this gate, or be called an independent confirmation.

## Transport and cost

Replay JSON mode: zero structural failures, zero Harness violations, one Uc length/incomplete failure; 109/110 usable. The failure is packet 15 and had no frozen useful atom, so it does not explain the recall decline. All 110 calls report usage; no retry, repair or replacement.

| Arm | Input tokens | Output including reasoning | Cache hit / input | Cache rate |
|---|---:|---:|---:|---:|
| Uc | 87,754 | 316,468 | 41,344 / 87,754 | 47.11% |
| U1 | 114,033 | 126,974 | 60,800 / 114,033 | 53.32% |

U0 incremental cost is zero. Uc–U0 changes show that the transport/sampling surface matters (incidental 50→44; recall21→23), but one stochastic rerun cannot identify API causality alone. The larger U1–Uc selectivity change is the primary controlled result. U1 is a combined semantic instruction+Gap intervention, not an isolated Gap-token effect.

Inherited Claim density sensitivity uses archived v2 relevance labels: 25,222 relevant versus 40,636 incidental characters across repeated pre-states (280/407 Claims, no unmapped statement). Add each arm's reviewed new-character totals for local post-state density; this mixes historical and current rubrics and is explicitly secondary. The main treatment contrast uses newly admitted characters. Full Q+Claims+Hypothesis local post-state characters are 114,556 /113,865 /109,227.
