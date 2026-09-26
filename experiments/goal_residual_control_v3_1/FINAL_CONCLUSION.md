# v3.1 Final conclusion: selectivity improves; durable belief still needs qualification

Base: `4ca582269ef7831373d0168d87494f2a58e9bb45`. Branch: `experiment/goal-residual-control-v3-admission-replay`. One production transport canary, full 55-packet Uc/U1 replay and one user-authorized 27-packet exploratory U2 completed. No G4/G5 or retrieval calls; the original Admission Gate failed recall. Historical data was preserved.

**The main result is positive for selective admission but insufficient for a clean online Writer.** U1 removes most irrelevant writes while losing some important facts. A small general coverage amendment recovers recall, but introduces stronger-than-supported Hypothesis relations. Source-supported Claims alone do not certify persistent Research Belief.

| Confirmatory metric | Uc | U1 |
|---|---:|---:|
| Incidental Claims | 44 | **2** |
| Decision-relevant admission | 27/71 (38.03%) | **18/20 (90%)** |
| Frozen useful-atom recall | **23/27 (85.19%)** | 20/27 (74.07%) |
| Correct empty /38 | 17 | **36** |
| Local State character increment | 6,461 | **1,823** |
| Semantic Hypothesis errors | 10 | **3** |

U1–Uc is the primary contrast, controlling transport but jointly changing the semantic instruction and adding Current Gap. It is not a Gap-only effect. The 55 packets cluster within ten qids; q580 has only one actual historical update. Effects are descriptive, diagnostic and single-reviewer.

## Answers to the 21 required questions

1. **Production constrained transport:** object-root schemas were accepted, but one of 12 Actor responses still emitted Find+k. All 24 requests returned;23/24 were structurally and Harness valid. Per freeze, all research calls used `json_mode_fallback`; no further capability probes.
2. **Remaining structural failures:** canary1/24 (4.17%, Actor1/12). JSON replay0/110, exploratory0/27. One Uc length/incomplete failure remains separate; no Harness control violation or provider/API error. Small zero-event samples do not prove a zero production error rate.
3. **Uc vs U0 surface effects:** archived U0 incidental50 and recall21/27 become44 and23/27 under Uc. The outputs vary; API/transport and stochastic variation cannot be separated by this single rerun. U0 is not the primary causal control.
4. **Incidental reduction:** U1 removes42/44 incidental Claims (95.45%);25 paired packets improve, none worsen, across nine qids. Source-supported but irrelevant writes are substantially reduced.
5. **Recall preserved?** No in original U1:23→20/27, five worse pairs/two better. Runtime precision, a source conflict, and an independent career requirement are important misses. U2 recovers to23/27 on its matched diagnostic, but is adaptive and not an independent confirmation.
6. **Scope/qualifier retention:** Claim scope-loss counts Uc2→U1 1; U1 nevertheless strengthens ambiguous five wins into five league titles. U2 has zero scored Claim scope losses on its subset but adds a stronger temporal statement in Hypothesis. Claims and hypotheses require separate review.
7. **No-change:** U1 actual no-change40/55 versus Uc17/55. Correct empty admission36/38 versus17/38. Some additional empties wrongly omit useful atoms; silence alone is not success.
8. **State growth:** new Claims71→20; local semantic-character increment6,461→1,823 (−71.78%); incidental new characters3,992→138. Historical pre-states are unchanged and already bloated. Independent local counterfactuals are not cumulative rollout projections.
9. **q580 Workspace→Claim loss:** not demonstrated improved. Its only replay Observation is a cast list, not the initial five-season W3. U1 correctly stays empty; U2 incorrectly uses the maximum season mentioned as apparent support for a total bound. That exposes an admission/inference issue without retesting actual W3 uptake.
10. **Online vs Oracle gap:** unmeasured; G4 was not run after the failed Admission Gate.
11. **Hypothesis contradiction changes action:** U1 clears both newly observed PSG scoring contradictions whereas Uc retains them. No subsequent Actor ran, so improved **action** recovery is unmeasured. Two already-known contradictions remain retained when the new source is unrelated.
12. **G4 Evidence Progress:** unmeasured, zero G4 tools, not zero Progress success rate.
13. **L0/L1/L2 Original Goal Resolution:** all unmeasured this round; do not substitute historical1/10 each.
14. **L0/L1/L2 premature STOP:** unmeasured. No controller winner can be inferred from Writer replay.
15. **L0/L1/L2 State Growth:** unmeasured as trajectories. The reported U-arm growth is local replay only.
16. **L2 Reviewer calls reduced?** Not measured. Fewer Writer mutations make this plausible under unchanged batch-boundary scheduling, but cannot quantify saved calls without rollout.
17. **Residual mainly stopping signal?** This round does not retest that historical interpretation. No new acquisition or stopping superiority claim.
18. **Persistent Gap harmful?** Not tested. Current Gap aids relevance yet may become an overly narrow filter. This does not prove persisting a prior focus is harmful.
19. **Direct Replan sufficient?** Not established. Cleaner reliable online belief must be qualified before comparing controllers.
20. **Keep Claims + Working Hypothesis?** Yes as the unchanged minimal mutable semantic representation, with immutable authoritative Q and operational Workspace. The results justify better admission boundaries, not extra persistent fields. They do not prove end-to-end sufficiency; Hypothesis cannot be a route for unsupported relation strengthening.
21. **Dominant failure now:** directly observed at Admission: proposition coverage, scope-sensitive novelty/conflict recognition, and the qualification of Hypothesis content. Candidate overcommit remains. Actor/Search/Retriever/Localizer were not intervened on or executed here, so cannot be ranked causally from this run.

## Bounded remedy and next research implication

[U2](admission_exploration/RESULTS.md) adds a general internal check of individual propositions against all unresolved original requirements and scoped conflicts. No named-case guidance, extra fields or nodes. On27 matched packets it restores recall20→23/27, with25/25 source-supported Claims and only3 incidental versus Uc16. Yet it introduces two questionable persistent Hypothesis bindings (total-season bound and May/count relation). It is mixed-positive evidence about a remedy, not a reason to overwrite U1 failure or declare a production-ready Writer.

A next confirmatory admission test should validate **both** requirement coverage and the support boundary of Hypothesis updates on fresh frozen observations. No further prompt sweep, schema expansion or controller rollout was performed. No result supports a tool-frequency objective.

## Cost, integrity and limits

161 new model calls total:24 canary+110 replay+27 exploratory; U0 reused at zero incremental calls. Reported totals:326,955 input+593,450 output=920,405 tokens, including reasoning. Token-weighted cache162,304 hit/326,955 input=49.64%. Per-stage rates: canary40.49%, Uc47.11%, U1 53.32%, U2 56.11%. All calls reported usage; failures remain charged. No monetary-price estimate.

All 10,227 baseline tracked files remain byte-identical; each stage's exact requests and source hashes were committed before calls.55/55 Uc message pairs match v2 bytes;55/55 U1 views differ only by exact generating Current Gap, while the system semantic prompt is the intended treatment. No output repair/retry/best-of, hidden gold input, changed model, disabled thinking or modified retrieval backend.

Frozen atoms and explicit per-output semantic reviews support the metrics. A [post hoc sensitivity](analysis/SCOPE_SENSITIVITY.md) makes the ambiguous league-title reading permissive and removes two less-decisive recall atoms without changing primary results. These qualifications matter: the mechanism is useful, while its recall and belief-boundary reliability are unresolved. Single-reviewer judgments and adaptive same-bank U2 limit generalization.

- [Confirmatory results and gate](admission_replay/RESULTS.md)
- [Exploratory remedy](admission_exploration/RESULTS.md)
- [Transport canary](structured_transport_canary/RESULTS.md)
- [Design audit](DESIGN_AUDIT.md)
