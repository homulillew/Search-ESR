# Transactional Research Progress: gated conclusion

**Decision:** E1 did not pass its preregistered mechanism gate. Stop E2 Free Frontier, E3 Progress Causal Probe and E4 Short Rollout. This branch supplies no causal Actor result and no end-to-end research-utility result. The tested Delta updater is **not yet a justified replacement** for Full Rewrite; this does not refute the broader value of correct Research Progress.

The 41 E1 cases span 12 qids and seven transition types. A/B/C received the same previous state and new exact observation, with one response per arm and no retries. The frozen result is A 36/52 correct mutations (69.2%), B 36/69 (52.2%), C 36/60 (60.0%). Paired unrelated-churn changes favor C over A in four cases but worsen in ten, failing G1. C precision misses the 80% G3 threshold. G2 and G4 pass: frozen-label false closure is 1/17 at-risk C cases, and NoGain state preservation is 8/8. A post-call audit found that the qid-186 credit condition was incorrectly frozen as still open even though the new source lists the two people with the same surname. Excluding both affected qid-186 cases leaves G1 and G3 failed. These are diagnostic, correlated cases, not a population estimate.

## Requested questions

| # | Answer |
| --- | --- |
| 1. Full Rewrite versus Delta churn | In this bank, Full Rewrite changed unrelated state in **10/41** cases, Delta in **19/41**, and Delta+Verify in **14/41**. Delta did not reduce churn. |
| 2. Delta mutation precision | It decreased from A **69.2%** to B **52.2%**; C recovered to **60.0%**, still below A and the 80% gate. The frozen rubric counts unrequested new Claims as extra mutations even when their text is locally supported. |
| 3. Triggered Verify and false closure | Frozen-label cases fall from B **4** to C **2**; C rejected an insufficient-conjunction closure and a conflicting-date overcommitment. The two remaining C “false closures” are the qid-186 label defect, so this is evidence of a useful guard in specific cases, not a reliable rate estimate. |
| 4. NoGain stability | All three protocols preserved VerifiedProgress in **8/8** NoGain cases; no Delta advantage appeared. |
| 5. Evidence binding errors | Committed status transitions cited the packet-local new W ref in A **37/37**, B **37/37**, C **34/34**. The common failure was scope expansion and broad Gap closure, not a missing or invented W ref. |
| 6. Model–Oracle State gap | **Not measured.** E2 stopped at E1's gate. |
| 7. Free Frontier generation without G options | **Not measured.** |
| 8. Most common Frontier error | **Not measured.** No free Frontier was generated. |
| 9. Oracle Progress causal effect on Actor | **Not measured.** E3 was not run. |
| 10. Model-maintained Progress effect on Actor | **Not measured.** |
| 11. Actor B–A / C–A / B–C | **Not measured.** The E1 A/B/C differences are state-transition comparisons, not Actor effects. |
| 12. Useful Evidence per Retrieval | **Not measured in this branch.** E4 tool rollouts were stopped. The previous branch's one-step results are historical context, not an E1–E4 treatment effect. |
| 13. Stale Gap reduction | In E1's four narrow closure cases, B/C mechanically retired the ActiveGap **4/4**, A did not set it to `none` **0/4**. This tests a protocol invariant in synthetic states, not a live stale-gap rate. |
| 14. Redundant Retrieval reduction | **Not measured.** E1 used no retrieval tools. |
| 15. Harness-triggered Verify | Keep it as a candidate safety step for semantic transitions in a revised protocol; it blocked several concrete errors. The current reject-and-retain rule also left a previously supported date Claim stale when the verifier returned `open` but the Updater had proposed `refuted`. Reopening needs a separately frozen design test. |
| 16. Largest remaining bottleneck | The measured bottleneck is **Progress construction and maintenance**, specifically focused Delta scope and valid new-Claim creation. Frontier generation, Actor adherence, concrete-source retrieval, query generation and Find localization were not compared here. |
| 17. Formal minimal ESR runtime | **Not yet.** First revise and preregister an E1 replication with corrected reviewer labels, explicit treatment of text-supported new Claims, and recovery behavior when Verify finds conflict. It must pass its own gate before a runtime rollout. |
| 18. ESR-GRPO | **No evidence to start.** There is no live utility gain or stable state protocol result. |
| 19. Hard Search/Find/Open gating | **Still prohibited.** E1 did not show reliable state construction, and E3/E4 did not test Actor behavior or useful retrieval. |

## Mechanism interpretation

The frozen E1 result weakens H1 as implemented: a Delta-only response often proposed additional Claims or overclosed broad Gaps, while Full Rewrite was comparatively concise in this controlled bank. Many extra Claims were directly stated in the visible source, so “unrequested expansion” is the accurate diagnosis; it must not be presented as wholesale false evidence. C's Verify limited some semantic errors but cannot by itself enforce a narrow state schema or correct an Updater that proposes the wrong transition direction. The qid-186 review defect limits exact false-closure and precision interpretation, yet excluding those two cases leaves both failing gate conditions unchanged.

H2 (causal value of Progress to Actor) and H3 (research utility in matched short rollouts) remain **untested** here. The hypothesis that Progress Maintenance is the main Harness root cause requires all three links—better state mutation, better paired Actor action, and better useful evidence—to appear. This branch established none of that full chain.

The raw events, hashes, reviewer labels, frozen rubric, sensitivity audit and all three downstream `NOT_RUN.md` records are in this experiment directory. Historical results and backend code were not changed.
