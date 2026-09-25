# State-conditioned retrieval: conclusion

**Decision:** S1 changes query wording and sometimes canonical document rank, but the registered direct-retrieval gate fails. S2 and S3 were not run. The strongest clean top5 rescue is q435 C01; one of the other two apparent canonical misses (q186 B06) already had an answer-bearing document at S0 rank 3. Do not change the retriever, State admission policy, or action space on this result.

The experiment used 24 paired cells across 10 qids, DeepSeek `deepseek-flash` for 120 one-shot queries, and the unchanged Qwen3-Embedding-8B/100,195-document FAISS index. All requests, provenance, truth, and gates were frozen and committed before their respective calls. S0→S3 canonical Direct@5 was 21/24→23/24 (+8.33 points), with first-rank movement 5 improved, 19 tied, 0 worsened. S0 was already 87.5% at top5, and the ceiling fallback required at least 12 rank improvements. The protocol therefore stops. The 12-cell truthful-noise control fell from S0 10/12 to 9/12, while S3 reached 12/12; raw history reached 11/12 with about twice S3's prompt tokens. These control differences are descriptive under a high baseline ceiling.

## Required research answers

1. **Direct Recall:** Yes numerically, 21/24→23/24 at top5; below the registered gate.
2. **Rank:** Five improved, nineteen tied, none worsened; no systematic majority movement.
3. **Candidate grounding:** It produced nearly all observed rank gain. S1 already matched S3 at 23/24 top5 and 0.8542 MRR@50.
4. **Extra constraints:** No consistent incremental gain. S2 worsened one canonical rank against S1; S3 recovered it.
5. **Query form:** Yes. Candidate inclusion rose 15/24→24/24; in C cells, 1/8→8/8. Lexical raw-question clue load fell 0.1841→0.0729 overall.
6. **More tokens alone:** The matched truthful-noise arm did not reproduce the 12-cell S3 result, but the sample is ceiling limited.
7. **Noise replication:** No: noise 9/12 top5 versus S3 12/12, with noise/S3 word counts within 0.87–1.22×.
8. **Raw History advantage:** No in these controls: raw history 11/12 top5 versus S3 12/12; it beat S3 rank in one cell and lost in three.
9. **Compression:** In this subset, S3 retained equal or better top5 retrieval at median 391.5 versus 746.5 provider-reported prompt tokens. General decision sufficiency remains unproven.
10. **q186:** B06 canonical rank 13→1, but S0 rank-3 alternative D51927 already stated the episode answer. The original q186 publisher Gap was excluded because the available prior W leaked its answer. This does not establish the original miss as context limited.
11. **q435:** C01 improved 9→4 with Oliver named and shorter Forbes query. Other q435 cells were already top5; the effect is local, not six independent successes.
12. **q1094:** C12 canonical merger D24763 stayed >50, while B04 match source stayed rank 4. C12's S3 match facts did not ground the merger relation; a plausible partial alternate merger source appeared at rank 16. It is a canonical retriever miss, not a clean proof that a sufficient State defeated the retriever.
13. **q177:** All four cells were already top5 under S0. One 2014-table rank improved 2→1. This experiment cannot settle the previously observed Find/localizer issue.
14. **Bridge as progress:** A nonanswer source can be progress in principle, but frozen ProgressHit@5 equaled DirectHit@5 in all main arms. Some bridge labels were overinclusive, so this bank does not establish the claim empirically.
15. **Bridge→Direct:** Not tested; the controlled two-round stage was gated off.
16. **State–Gap mismatch:** Plausible, especially q1094's match facts for a merger Gap, but no causal S2 test ran.
17. **Premature versus actionable Gap:** Untested because S2 did not run.
18. **Independent Frontier Selector:** No new evidence for one; historical F1 also did not establish its benefit.
19. **Noisy history→precise Evidence Need:** The q435 query change is consistent with this mechanism, but no two-round State update was tested.
20. **Claim Admission:** Decision-relevant, verified candidate facts are a sensible research hypothesis; do not change production admission rules yet.
21. **Most helpful facts:** Candidate names or identities were most visibly query shaping here. The extra constraint and relation facts did not show consistent rank gain.
22. **5TB-like future-answer fact:** Not directly tested. This result gives no reason to cache it in persistent State ahead of a decision need.
23. **Candidate facts in State:** Worth further controlled testing, not automatic long-term admission on one high-ceiling bank.
24. **Failure partition:** q435 C01 is a clean context-sensitive example; q186 B06 is a canonical-truth miss with alternative evidence already found. q1094 C12 is a canonical deep miss with incomplete relation State and possible alternate evidence. Gap-limited and compression-limited classes are unestablished; Find/localizer remains a separate historical concern.
25. **Search backend change:** Not justified by the aggregate result.
26. **Clean-State backend evidence:** None decisive yet. q1094 C12 warrants a source-truth and relation-State audit before any retriever-representation experiment.
27. **Find/localizer change:** This experiment did not call Find. Prior oracle-document Find failures remain an independent reason to study localizer behavior later, with a separate freeze.
28. **History Prior:** No new supporting evidence.
29. **Old/new scope router:** No new supporting evidence.
30. **Persistent TestCard:** No new supporting evidence.
31. **Sentence/character pointer:** No new supporting evidence.
32. **ESR-GRPO:** No causal or reliable-State basis from this result.
33. **Next priority:** Improve the *experimental construction and audit of decision-relevant State* before production admission changes: select genuinely unresolved early Gaps, audit all alternative answer-bearing sources, require relation-relevant bridge evidence, and avoid a top5 ceiling. Then repeat the paired test. Frontier control, retriever representation, and localizer interventions should follow their own qualified cases rather than be inferred from this S1 result.

## Scope and validity

Seventeen cells had a later target W in the same replay; seven target events were right-censored at the selected prefix. Several cells share a qid and target document. Some B cases had already observed a different window of the sufficient document. The frozen canonical sufficient set omitted at least one answer-bearing document, and some mechanically assigned bridge labels were not decision relevant. The primary score was not retroactively edited. These limitations make the small positive mechanism signal useful for designing the next audit, but too weak for a deployment or training claim.
