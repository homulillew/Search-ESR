# E1 Contract Repair & Full Rerun — conclusion

## Decision

**Complete corrected E1: 72/72 valid chains, 87 fresh paid calls, zero output
contract failures. Neither H1 nor H2 passes the frozen gate. E2/E3 were not run;
production was not changed.**

Evidence projection removed the public/private alias pair that caused run001's
failures. This is an observed contract recovery, not a randomized estimate of the
repair's effect. A whole-payload audit found one residual legacy private reference
inside frozen historical C, exposed in two requests. Thus **Evidence is clean, but
an unqualified claim that every model input contains only public handles would be
false**. See question 5 below. No output was mapped or repaired.

Removing C did not reduce strengthening. Evidence-only formulation avoided the
q435 temporal error in this sample, but lost relevance and useful recall and
introduced two attribution errors in q673. The result supports neither proposed
construction change for adoption. H3 (Grounding anchoring) remains untested.

## Provenance and review

- Source remote HEAD: `99fbe47b9a6fa1bcfe628cb801cbd8e1ebcb29c5`.
- New branch: `experiment/claim-pipeline-contract-rerun` in an isolated worktree.
- Audit/code/freeze/raw commits: `92b69213`, `51522b7b`, `467c7c88`, `3762b2e7`.
- Actual paid execution HEAD: `467c7c88f45d5b5d9fa790f194c2e18c46662a62`.
- E1: D12/8 qids plus H-diagnostic12/6 qids; 24 packets, 14 qids, 8 overlapping
  relation families. Full unchanged bank:36 packets/20 qids. No confirmation calls.
- Of the24 contexts,18 are historical Reader requests and6 archived review contexts.
  Each contains one full previously observed window; this is not a full-acquisition
  or end-to-end retrieval experiment.
- 86 opaque candidate packets reviewed individually. Source-only labels were frozen
  before revealing Gap/C; relevance/dedup then frozen; individual atom coverage
  then frozen. Only afterward were arms unblinded and metrics computed.
- Single Codex reviewer, authorized by task. Familiar historical text can reveal
  provenance; this is neither independent review nor measured inter-rater reliability.
  Exact Observation redisplay used the preregistered hash cache. No gold, future
  trajectory, external source audit or answer lookup was used.
- All primary calculations use unchanged `../metrics.py` and `../REVIEW_RUBRIC.md`.
  Raw labels, reasons, hashes, paired rows and sensitivities are in `review/`.

## Primary results

FSSR = unsupported strengthened candidates / raw candidates; SSP = supported
candidates / raw candidates. GRSR uses the20 frozen useful atoms, after common
offline dedup. Candidate counts are not independent experimental replicates.

| Pooled, 24 packets each | A0: Gap+C | A1: Gap, no C | A2: select then evidence-only |
|---|---:|---:|---:|
| Raw candidates | 23 | 18 | 45 |
| FSSR | 1/23 = 4.35% | 1/18 = 5.56% | 2/45 = 4.44% |
| SSP | 22/23 = 95.65% | 17/18 = 94.44% | 43/45 = 95.56% |
| Gap relevance precision | 20/23 = 86.96% | 17/18 = 94.44% | 14/45 = 31.11% |
| Frozen GRSR, individual coverage | 18/20 = 90% | 15/20 = 75% | 8/20 = 40% |
| Correct Silence, raw | 7/10 = 70% | 5/10 = 50% | 6/10 = 60% |
| Correct Silence, semantic dedup | 7/10 = 70% | 7/10 = 70% | 7/10 = 70% |
| Raw claims/packet | 23/24 = 0.958 | 18/24 = 0.750 | 45/24 = 1.875 |
| After semantic dedup: count | 23 | 16 | 40 |
| After semantic dedup: FSSR | 1/23 = 4.35% | 1/16 = 6.25% | 2/40 = 5.00% |
| After semantic dedup: SSP | 22/23 = 95.65% | 15/16 = 93.75% | 38/40 = 95.00% |

Exact normalized dedup removes zero candidates: its results equal raw results.
Semantic dedup removes0/2/5 for A0/A1/A2. It does not remove any strengthened claim.
New supported useful candidates are18/23,13/18,12/45; ordinary relevance includes
relevant duplicates and therefore is not itself evidence gain.

### Split results and frozen gates

| Split | Arm | FSSR | SSP | GRSR | Relevance |
|---|---|---:|---:|---:|---:|
| D12 | A0 | 1/8 | 7/8 | 6/6 | 8/8 |
| D12 | A1 | 1/8 | 7/8 | 4/6 | 8/8 |
| D12 | A2 | 0/18 | 18/18 | 2/6 | 4/18 |
| H-diagnostic12 | A0 | 0/15 | 15/15 | 12/14 | 12/15 |
| H-diagnostic12 | A1 | 0/10 | 10/10 | 11/14 | 9/10 |
| H-diagnostic12 | A2 | 2/27 | 25/27 | 6/14 | 10/27 |

**H1: not supported.** Pooled relative FSSR reduction is **−27.78%** (required≥30%);
error counts remain1→1. Mean paired-packet and equal-weight qid strengthened-count
deltas are both0 (required<0). Individual-coverage recall drops15pp (allowed≤10pp).
H-diagnostic has zero baseline errors: relative reduction is undefined and cannot
provide the required positive confirmation, rather than being an automatic pass.

**H2: not supported, with adverse utility evidence.** Pooled relative FSSR reduction
is20% (below30%), while error count rises1→2. Mean packet delta is+1/24=+0.0417 and
qid mean is+0.0357, both wrong-direction. Recall drops35pp and relevance drops63.33pp.
In H-diagnostic, errors rise0→2; packet and qid means are both+0.1667. Its baseline
relative reduction is undefined, recall drops35.71pp, relevance drops52.96pp.

H2 qid deltas: q435=−0.5, q673=+1.0, all other12 qids=0. H1 deltas are0 for all14
qids. Full24-pair tables, all family/context/C/stratum sensitivities and exact
fractions are in `review/E1_METRICS.json` and `review/RESULT_TABLES.md`.

All four strengthened candidates are ambiguity-flagged under the frozen strict
source-relative rubric. As a posthoc robustness check, even treating both q673
attribution judgments as supported would leave H2's recall/relevance guards failed
and the held-out error-reduction baseline undefined. Treating all ambiguous claims
as supported would leave no baseline errors to test either reduction hypothesis.
No such alternative replaces the frozen labels.

### Compound-atom sensitivity

The primary unchanged implementation unions complete atoms assigned to individual
candidates. A post-unblinding whole-output check found two compound atoms split
across supported claims: A1 q637 age/sex plus classic-FOP diagnosis, and A2 q633
book/subject/kingship plus languages. No source/relevance label or denominator was
changed. Counting these jointly yields **18/20,16/20,9/20** (90%,80%,45%).

Under that more generous sensitivity, H1 meets the pooled10pp recall guard exactly;
its FSSR and direction gates still fail. H2 still loses35pp recall. Accordingly the
negative gate conclusion does not depend on treating split compound atoms strictly.
This supplementary review is not a new primary endpoint or threshold. Reasons and
contributing opaque IDs are in `review/PACKET_JOINT_ATOM_REVIEW.json`.

### What A2 actually did

The Selector selected all11 positive packets; it did not lose positive coverage by
failing to select a window. It selected15/24 windows overall, and **all15 Formulator
responses filled the three-claim cap**. The other9 selectors returned valid empty
selections and skipped formulation. Omission therefore often occurs after selecting
the right full window:

- q517: selected the filmography for the policeman role, then formulated The CEO,
  its premiere and Sense8 facts; the requested role was omitted.
- q261: selected the paper header/body, then produced aim, sample size and categories;
  title/authors/full publication date were omitted.
- q177: selected the Rangers table, then produced cancellation rows and Enyimba's
  row; Rangers' useful title-count row was omitted.
- q186: selected the former-company-name window, then produced game genre/release/
  input facts; Night Sky was omitted.
- q601 is a counterexample: A2 recovers two useful partial atoms that A0/A1 omit.

This is evidence of a focus bottleneck under full-window selection plus a small
evidence-only output budget. It is an inference from these traces, not a separately
isolated causal factor: A2 also changes the prompt and adds a selector call. Do not
declare that withholding Gap generally improves formulation.

## Twenty-eight required answers

1. **SemanticEvidenceView fields:** `window_ref, doc_ref, title, url, text`, plus
   originally present `date`. The optional date exception was audited before calls:
   it preserves existing semantic metadata (six E1 windows) and never adds a date.
2. **Hidden Evidence provenance:** `source_window_ref, docid, document_sha256,
   text_sha256, offset, end_char` and every other non-allowlisted Evidence field.
3. **Why hidden:** integrity, corpus lookup and byte offsets are harness bookkeeping;
   the model needs complete observed text/identity, not a choice between aliases.
   Full originals remain in bank and private request provenance.
4. **Schema/runtime aligned:** claim refs require W-pattern, unique nonempty refs,
   request-specific observed-W enum and independent runtime membership. Selector
   retains its original W-pattern and membership check. Old eight invalid outputs
   still fail contract replay; invented/unobserved W is also rejected.
5. **Any dual namespace remains?** No alias pair in any cleaned Observation/Evidence.
   However, frozen C1 in packet `P_61caf5fa7eaa43c6` retains
   `w_d10a873c7f9c87b1d58df6eb`, visible to A0 and Selector in two requests. This was
   found by the final scope audit, not the pre-call audit. C was preserved as required;
   it is not accepted as a new evidence ref. The stronger whole-payload-only-public
   goal is therefore **not fully achieved**. Future cleanup requires a separately
   frozen C display projection; do not silently rewrite this run or its inputs.
6. **Automatic alias mapping:** No. Neither old nor new output was normalized to W.
7. **run001 byte-identical:** Yes, checked against source HEAD and the new freeze.
8. **Bank byte-identical:** Yes, including C, OneGap, observations, splits and atoms.
9. **Prompts byte-identical:** Yes. Only mechanically generated schema suffixes and
   the shared Evidence representation changed; semantic prompt files did not.
10. **H1/H2 thresholds unchanged:** Yes, original protocol/rubric/metrics retained.
11. **24×3 complete:** Yes,24 valid chains per arm,72 total, no selective reuse.
12. **Contract failure zero:** Yes,0/87 attempted calls; allHTTP200. No unsent failure,
    retry, repair or replacement. This result does not prove universal reliability.
13. **A0 raw:**23 candidates; FSSR1/23=4.35%; SSP22/23=95.65%.
14. **A1 raw:**18 candidates; FSSR1/18=5.56%; SSP17/18=94.44%.
15. **A2 raw:**45 candidates; FSSR2/45=4.44%; SSP43/45=95.56%.
16. **H1 full gate:** No. C removal did not lower errors or improve paired direction;
    held-out baseline error floor also prevents confirmation.
17. **H2 full gate:** No. Below reduction threshold, adverse paired/qid direction,
    severe recall/relevance losses, and held-out errors increase.
18. **H-diagnostic direction consistent?** No positive replication. H1 is0→0;
    H2 is0→2 and opposite the q435 improvement.
19. **A1 reduces q435 strengthening?** No. A0 and A1 both attach67 albums to2016.
    C visibility is not necessary for this error in this packet.
20. **A2 q435:** Selector passes the fullW3. Formulator emits birth,1975 first
    recording deal and1977 band membership, not67-by-2016. These are supported but
    all off-gap. This is not evidence of answering the album/date need correctly.
21. **Cross-family reduction?** No. q435 temporal errors go1/1/0 across arms, while
    q673 attribution errors go0/0/2. Other six error types have zero events. Families
    assigned to packets overlap; their sensitivity denominators must not be summed.
22. **Recall collapse?** A2 clearly loses utility:40% primary or45% joint sensitivity,
    versus A1's75%/80% and A0's90%. A1 loss is15pp strict or10pp joint, not an error
    reduction benefit. The compound-atom caveat is explicitly retained.
23. **Correct Silence improved?** No pooled postdedup improvement:all7/10. Raw is
    7/10,5/10,6/10. Duplicate/no-new postdedup is3/6,3/6,4/6; relevant/no-new is
    4/4,4/4,3/4. The separate three off-gap silence cases are3/3 for all arms and
    never added to the primary denominator.
24. **A2 fact bloat?** Yes:45 raw candidates versus18 in A1 (2.5×);40 versus16 after
    semantic dedup (2.5×). Only14/45 are Gap-relevant and12/45 new supported useful.
25. **Root-cause hypotheses:** Do not accept H1 or H2 as general explanations or
    validated repairs. H1 receives no error-reduction support. H2 has one local
    temporal sanity-check improvement but fails transfer and utility guards.
    Evidence-only formulation can itself lose attribution scope (q673), so Gap/C
    removal is insufficient. Sparse errors in two qids cannot establish the dominant
    population-level cause or disprove all contextual effects.
26. **Worth entering E2?** A limited independent H3 admission diagnostic is reasonable,
    since actual supported and strengthened pairs now exist in both splits. It
    would test Grounding, not validate A2. Negatives remain concentrated in q435
    and q673, and all four new errors are ambiguity-flagged. See `E2_NEXT_PLAN.md`.
    No production promotion or integrated E3 is justified by E1.
27. **E2/E3 executed?** **No.** Calls0/0. Only an offline future-budget estimate exists.
28. **Production runtime modified?** **No.** No production file, tool semantics,
    persistent state field or historical experiment result was changed.

## Usage and execution

DeepSeek endpoint `https://api.deepseek.com/chat/completions`, `deepseek-flash`,
thinking enabled, reasoning effort high, temperature0, max_tokens32768,
stream=false, user_id omitted, max_retries0. Independent chains ran concurrently;
each Selector→Formulator dependency remained sequential. Peak concurrency72; no
limit change; wall48.5057s. Call latency p50=5.9246s,p95=29.4776s,max=48.3683s.

87 complete, consistent usage records; missing/inconsistent0. Input87,568,
output163,269,total250,837 tokens. Cache hit6,016,miss81,552:
**6,016 / 87,568 = 6.8701%**. This is observed accounting, not a claim that higher
concurrency improves cache reuse. No separate connectivity probe or retrieval call.

84 offline tests passed before the freeze. All87 actual requests match the frozen
possible-request hashes; all prior artifacts/production remain byte-identical.
Final audit and file hashes are in `FINAL_INTEGRITY.json`.

**Mechanical provenance must stay in the Harness. Semantic models should operate
only on stable public handles.**

**Do not ask a language model to choose between two machine identities when the
Harness already knows they are aliases.**

The remaining C display exception is explicitly documented against these principles;
zero output failures must not conceal that scope limitation.
