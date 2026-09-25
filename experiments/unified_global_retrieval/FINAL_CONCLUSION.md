# Unified Global Retrieval: gated conclusion

**Decision: stop after U1.** The branch tested document routing for a new Gap, not Search→Find evidence acquisition or a full Research State loop. The frozen G full-corpus arm rediscovered 19/20 historically seen sufficient documents (95%) but found only 16/20 newly required sufficient documents (80%). Overall sufficient-document Recall@5 was 35/40 (87.5%). The preregistered U1 gate required respectively ≥90%, ≥85% and ≥88%, with no qid-wide zero recall. New-source and overall requirements failed. U1b's old-source trigger did not fire, so U1b, U2 and U3 were not run.

The strongest positive signal is that old and new documents can compete without a source-scope router: q387's PC Gamer document and q517's Peter Nzioki document were rank 1, and q177's historical table escaped the old signing article in all three D cells. The limiting signal is source precision for new Gaps: q435's exact May Forbes count failed under one query despite a related old source at rank 3, q186's game document was absent, and q1094's PSG formation document was absent. q435's related Forbes list-inclusion Gap succeeded, showing that success depends on the specific Gap/query, not just entity identity.

## Answers to the required questions

1. **Old sufficient D rediscovery:** 19/20 A/B at top five. Strong on this diagnostic bank, but one miss and correlated cases prevent a deployment-level stability claim.
2. **Type A future fact without old Claim/W:** 11/12 old D at top five; q387's 5TB source ranked 1. No W was reacquired, so the fact-recovery claim is untested.
3. **Type B old D then new location:** 8/8 old D at top five; Find was not run, so location recovery is untested.
4. **Type C new document:** 9/12 at top five, 75%.
5. **Type D misleading old source escape:** 7/8 had a sufficient new D ahead of the misleading old D or no old D in top five. q435 D01 failed with the old retrospective at rank 3.
6. **Pure G Recall@1/3/5:** 23/40 (57.5%), 32/40 (80%), 35/40 (87.5%); MRR@5 0.6854.
7. **Where H helps:** A/B only, 20/20 versus G 19/20. H's single-document candidate set makes this a weak diagnostic advantage. C/D have no historical sufficient D by design.
8. **Need for history prior:** No. G already cleared the old-source threshold; the failing dimension was new-source discovery.
9. **Soft prior without new-source harm:** Unknown. U1b was not triggered or run.
10. **Find after sufficient D:** Unknown; U1 executes no Find.
11. **Main observed failure:** Fixed-k document retrieval for new Gaps, with possible Query Writer contribution. This design cannot identify query versus embedding/index causality. Localizer was not tested.
12. **Top2 parallel Find cost:** Unknown; U2 was gate-blocked.
13. **q387 uncached future fact:** The source containing 5TB returned at rank 1 without a historical source hint. Reobtaining the 5TB window remains untested.
14. **Does q517 prove old prior indispensable?** No. The old Peter Nzioki document returned at rank 1 globally; the role-bearing new location was not inspected here.
15. **q435/q177 old-source escape:** q177's three D cells succeeded. q435 was mixed: Forbes list inclusion succeeded but May feature count failed. They support a conditional, not universal, escape mechanism.
16. **q546 bottleneck:** This bank routed its professional-year source at rank 1, but it did not test the hard 2023 multi-match sequence. The latter's document-versus-localizer bottleneck remains unresolved here.
17. **Delete Historical Recall / Workspace Projection?** No deployment conclusion. Document rediscovery alone has not demonstrated useful W recovery or full-loop performance.
18. **Delete old/new source-scope router?** Not yet. A per-Gap global route is promising for old D, but its new-D gate failed.
19. **Keep Claims focused on current Gap?** This remains the sensible minimal hypothesis; U1 provides no reason to cache incidental future facts, but does not prove that such caching is unnecessary.
20. **D/W only for audit/citation/duplicates?** Plausible design, unvalidated until evidence recovery and mini-loop tests pass.
21. **Connect unified retrieval to complete Research Loop?** No; U1 stopped before Find and Claim/Gap integration.
22. **Restore persistent TestCard?** No evidence from this branch supports doing so; TestCard was outside scope.
23. **Add sentence/character pointers?** No evidence from this branch supports doing so; localizer was not exercised.
24. **Run ESR-GRPO?** No. Retrieval and evidence-acquisition gates remain unmet.
25. **Hard Search/Find/Open gating?** No causal evidence supports a hard mask. This branch used no action gate.

## Practical interpretation and limitations

The primary five misses are recorded in `document_rediscovery/SOURCE_AUDIT.md`. A11 has an alternative new publisher source, so exploratory any-sufficient-document recall is 36/40, but the old-source primary metric and 16/20 new-source metric are unchanged. No post-result source substitution changed the frozen gate. The 40 cells reuse ten qids and 19 primary target documents; one-window checkpoints understate full history, and some Gaps concern auxiliary facts rather than the original final answer. Several raw Questions already contain answer clues. These design limits mean the reported proportions are diagnostic, not independent samples or final Accuracy.

The first GPU model initialization failed with out-of-memory before any retrieval query; the failure is retained. Retrieval then completed on CPU. After GPU 1 had more free memory, a separately frozen [GPU 1 replay](document_rediscovery/gpu_replication/RESULTS.md) loaded the unchanged float16 backend and produced **identical ordered top-five documents in all 40 cells**, with the same stop decision. The earlier memory failure therefore does not weaken the observed ranking result. The 40 Query Writer calls all succeeded with zero retries and had 30.76% response-reported prompt-cache hit tokens. U1 cost was 40 model query-writing calls plus 40 corpus embeddings/Search decisions; the restricted H arm reused each embedding. GPU query inference and scoring summed to 3.29 seconds after initialization, median 0.071 seconds per cell; CPU Search took 78.30 seconds, median 1.92. Without Find/Evidence Yield, the additional Search cost cannot yet be justified by demonstrated useful evidence or by architecture simplification alone.

The next valid study would diagnose the four C/D new-source misses and reproduce a higher new-source recall under a separately frozen design. It should not add a recovery mechanism merely because global search missed a new document, and should not promote document recall into evidence-acquisition success. Search still chooses documents; Find must be tested separately for locating evidence.
