# Final conclusion: full-corpus retrieval robustness

This branch preserves U1's failed top5 stop. It tests K0 rank depth, Q1 complementary wording under an equal ten-document budget, F1 oracle-document Find, and F2 diagnostic Top1/Top2 Find on the same frozen 40 cells. No historical experiment file was changed. A1 was not run because neither document policy passed its frozen gate.

1. **Five old misses.** A11 q186 canonical D39978 is >50; C09 q186 D39978 is rank18; C01 q435 all three frozen sufficient D are >50; D01 q435 D51535 is rank6; C12 q1094 D24763 is >50. See `rank_depth/MISS_RANKS.md` for scores and thresholds.
2. **Top5 budget or deep ranking?** Only D01 is a shallow rank6 miss. Three are >50, one rank18. The dominant frozen-target problem is deeper ranking/representation, not simply top5 budget. This is a canonical-ID metric; q186 has noncanonical related pages that may supply partial or alternative evidence.
3. **q435 wording sensitivity.** Yes. Shared sufficient D51535 goes from rank6 on D01's album-count wording to rank1 on D02's richest-musicians-list wording. Q2 rescues C01 but loses D01 under the equal budget.
4. **q186 conjunction/partial matches.** Both queries put the company page D3079 first. Five noncanonical pages in each top50 mention both Galacta and Albino Frog, including related game pages ahead of canonical D39978. The query overload hypothesis is plausible, but some alternatives themselves carry useful clues; the frozen canonical-doc recall understates every possible acquisition route.
5. **q1094 PSG source depth.** D24763 is still >50 for a query naming PSG and both merger clubs. This is a strong document ranking/representation or wording mismatch signal; this experiment cannot isolate which submechanism dominates.
6. **Single Query@10.** It reaches 36/40 overall, 19/20 A/B, and 17/20 C/D. It misses the fixed 37/40 and 18/20 gate, so Query2 was required for diagnosis and Single Query@10 was not selected.
7. **Equal-budget dual Query.** No aggregate gain: S10 and D5+5 both reach 36/40. D5+5 RRF top5 falls to 34/40; one rescue is canceled by one regression.
8. **New-source gain.** The only rescue, C01 q435, is a new-source cell, but D01 q435 regresses. C/D remains 17/20 and average top5 Jaccard is 0.513. Diversity exists but is not reliable source gain.
9. **Second Search cost.** Not justified by these paired results. Dual misses its recall and net-rescue gates. DeepSeek Query2 calls had a 39.4% aggregate prompt-cache token hit rate, but this does not change the zero net recall gain.
10. **Oracle-D Find.** Strict useful-W hit is 33/40 (82.5%); fully sufficient is also 33/40. This is the preregistered 80–90% mechanism-audit band, not a clean localizer pass.
11. **q387 5TB.** Yes. A01's original Find returns the PC Gamer line “5TB of Storage” in a single W.
12. **q517 Policeman 1.** B01 does not: Find stops at the filmography header. C10's different frozen Find query on the same D reaches the row. Correct D is insufficient without reliable local wording/window selection.
13. **q546.** C11 and D08 oracle Find recover professional-year facts, whereas F2 C11 ranks other snooker players above Ding's D. These cells point more to document ranking for their *current* Gaps. They do not retest the original hard multi-match q546 sequence, so no general bottleneck claim about that sequence is warranted.
14. **Top2 rescue.** Diagnostic P2 rescues useful W in A11 and B06 only: 24/40 P1 versus 26/40 P2 (+5 points). A11 is partial due a 1993-vs-1992 conflict; only B06 adds a fully sufficient hit.
15. **Double Find cost.** Not justified: only 5/40 extra rank2 calls are useful; useful W per call drops from 60.0% to 36.25%, violating the allowed 5-point loss. P2 is not selected.
16. **Type A end-to-end future fact.** Not measured. A1's deployable document-policy precondition failed. F2's diagnostic A useful rates (9/12 P1; 10/12 P2) cannot be reported as A1 recovery.
17. **Type B old-D/new-location.** Not measured end to end for the same reason. F1 B oracle Find is 5/8, demonstrating a localizer gap despite known D.
18. **Type C new-source Evidence.** Not measured end to end. F2 diagnostic C is 6/12 P1 and P2 useful W; it uses nondeployable U1 G ranking.
19. **Type D escape.** Not established as a deployable end-to-end outcome. Diagnostic F2 D is 5/8 useful W with no Top2 gain; D01 misses exact Forbes count.
20. **Main bottleneck.** Frozen canonical source misses are principally at document retrieval/ranking depth, with evidence of query sensitivity and likely representation dilution. F1's 82.5% and B01/C04/D03/D04 show a separate Find/localizer weakness. The present interventions do not uniquely separate ranking from document representation. Source ambiguity also matters: q186 alternative pages and the q177 interim-vs-final table must be reviewed semantically.
21. **History Prior.** No new evidence justifies it. U1 old-source 19/20 at top5 remains strong; this branch did not test a History Prior.
22. **Old/new router.** No new evidence justifies it. Old and new sources were evaluated in one corpus, and failures concentrate in new-source rank and localizer behavior.
23. **Unified corpus.** It remains a plausible common candidate space, but neither tested ten-document policy passed deployment gates. Do not claim the default Search→Find route is validated yet.
24. **Current-Gap-oriented Claim.** It remains conceptually possible to retrieve a future-useful fact again (q387 A01), but q517 B01 and failed document gates prevent a reliable no-cache Claim policy conclusion. Claim writing itself was not tested.
25. **Next full minimal Research Loop.** No. A1 start conditions failed; adding Reader/Claim now would conflate document retrieval and localizer losses.
26. **Persistent TestCard.** This experiment supplies no evidence for adding one; it was not tested.
27. **Sentence/character pointers.** No evidence yet requires them as persistent state. The observed Find misses justify a later localizer diagnostic, not an immediate state-field expansion.
28. **ESR-GRPO.** No basis. The acquisition mechanism does not yet pass its own deployment gate, and no policy-training intervention was studied.

The next bounded mechanism test should target deeper document ranking/representation and alternate-source sufficiency while preserving the frozen U1 results; a separate localizer study should investigate why correct D returns the wrong table or stops before the needed row. The q177 interim/final standings conflict shows why “Find returned a relevant-looking number” cannot substitute for source-context review. The aim remains selecting a source and action supported by the current Gap and evidence, not changing Search/Find counts for their own sake.
