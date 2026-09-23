# Search–Find / document-level verification: final bounded conclusion

2026-09-23. Branch `experiment/search-find-v3b-orthogonal`. This record adds
to, but does not rewrite, the frozen v3a/v3b studies. All claims below are
about **two selected historical bad questions** and short continuations,
not a population estimate. Complete protocols, freezes, gates, raw events
and stage results are in `orthogonal_search/`, `verification_state/`,
`scoped_search/` and `api_name_probe/`. The alias probe contains one preserved
turn-interrupted partial attempt and a separately frozen completion of the
two unfinished cells; no completed cell was rerun.

## Result in one paragraph

The global Search backend **can** re-localize an already discovered document:
in 13 P0 checkpoint continuations it created 65 new old-document Search
windows. Orthogonal Search removed that ability completely (0 P1 old-document
new windows), while still discovering 77 new documents. Yet the model made
Find in only 2/13 P1 cells, never within two decisions of 38 no-gain Searches,
and none of its new Find windows answered the unresolved need. Minimal Need
and Need+Focus cards produced no useful local evidence; a coherent scoped
API failed at required `scope` arguments, and the same-arguments
`search_document` alias was not selected in any of four cells. The current
dominant observed failure is **failure to promote a promising source and a
specific gap into a productive local verification action**, followed by
weak evidence use when local actions do occur. There is **no validated
minimal effective harness intervention** ready for a larger cohort.

## Answers to the required research questions

1. **Why was v3a Find 0/88?** The backend works: on qid 546, `find` with
   `turned professional` on the discovered Ding document returns the
   otherwise unseen professional/century/maximum-break facts (v3a audit).
   Model behavior stayed in global Search. The new experiment shows that
   Search's ability to deliver another old-document preview was a real
   competing capability, but removing it did not make the model switch
   reliably. The original qid 546 model also failed to elevate D17 Ding
   after discovery; qid 1094 repeatedly entertained Inter/Pirlo yet kept
   searching. These are different failures, not a single missing Find rule.

2. **Why did Tool Competition not fully test H1?** Its preregistered Arm C
   result remains **4/50 exploratory Find, weak band**. But Arm B/C returned
   undeclared `search` function calls in 41/50 and 36/50 first actions,
   respectively; the provider allowed them. Arm C's system prompt still
   opened by saying `search, find, and open` were available, and prefixes
   repeatedly showed successful Search. Schema removal did not remove
   Search's generated action or execute a no-Search environment. The
   additive amendment records this without changing old results.

3. **Did Orthogonal Search change behavior?** It changed the environment
   exactly as intended, but only slightly changed Find selection (P0 1/13
   cells, P1 2/13). P1 generated **38 no-gain Searches** and searched again
   after no-gain in **11/13** cells. In three prefix-selected local-opportunity
   checkpoints, Find was **0/3 in both arms**. No useful P1 Find window was
   obtained. P1 raw observation text was lower (122,515 vs 438,313 chars),
   but total prompt tokens were higher (2.234M vs 1.906M) because P1 kept
   running while many P0 cells stopped. Orthogonalization alone is not an
   effective verification policy in this sample.

4. **Was Search really simulating local Find?** Yes, operationally. P0
   produced 65 new W# for already discovered documents and injected 304,710
   preview characters from them. P1 produced zero such windows or text,
   despite 318 old-document hits. This verifies the *capability overlap*.
   It does not establish that overlap was the main cause of non-adoption.

5. **Is Document Triage an independent failure?** Yes, as an observed
   case class. The correct Ding document D17 appeared in the qid 546 v3a
   workspace at event seq28. The following two reasoning responses did not
   promote Ding to a candidate or treat D17 as a focus, though its full text
   had the needed facts. Calling this a pure Find/verification failure would
   use hindsight gold. Later reasoning touched Ding but never substantiated
   the final candidate. In qid 1094, the model did positively treat the
   Inter founding split as plausible after D37, a different state.

6. **When is there a real Find opportunity?** A document must be discovered,
   the model must consider it promising, and there must be a *specific*
   unresolved fact reasonably likely to be in it. Mere rediscovery is not
   enough. The three new B checkpoints were selected from prefixes under
   this plausibility rule, but post-run full-text audit found D38 had no
   `95th` or `free-kick` and D14's two `95th` mentions concerned penalties.
   Thus B was an imperfect proxy for an answer-bearing focus. An oracle
   insertion of qid 546 D17 would be a separate diagnostic upper bound,
   never a natural-state effect; it was not run in this batch.

7. **Did CurrentNeed help?** S0 and S1 each had Find in **1/4** cells, and
   neither produced useful local evidence. S1 searched, found D5 twice,
   then stopped with a specific Mark Williams answer and match details not
   supported by its cited W5. Need alone was insufficient here.

8. **Did FocusDocument add value?** S2 had Find in **2/4** cells, versus
   1/4 for S1. Its extra 1094 case tried D38 three times; all were lexical
   `no_match`. Its 546 local windows did not establish the match sequence.
   Explicit D# changed an action in one case, but did not yield useful
   evidence. The chosen documents came from fallible prefix belief, not gold.

9. **Is there a tool/API prior?** There is a strong *observed Search call
   pattern*: undeclared `search` survived schema deletion; in the scoped
   arm 27/29 provider-returned `search` calls omitted the required `scope`
   (two valid corpus, zero valid document). The trace cannot separate model
   generation from provider normalization. A final coherent
   `search_document(doc_ref, query)` alias retained Find's argument shape
   and backend but was selected **0/4** times, versus S2 Find in 2/4. Thus
   an independent Find-name prior is **not established**, and a simple name
   substitution did not solve the problem. Strict harness validation was
   essential to prevent invalid calls from masquerading as treatment.

10. **What is the minimal effective Harness intervention?** None was
    validated. Orthogonal Search removes old-document re-localization and
    duplicate raw text, but did not create useful local verification. Need,
    Need+Focus, scoped Search and the alias did not cross the evidence gate.
    The minimal *engineering safeguard* confirmed here is strict validation
    of declared names and arguments plus truthful `already_discovered`
    feedback; it is not an accuracy/verification improvement claim.

11. **What is the new bottleneck?** Mapping a research gap to an actually
    useful focus document and then using the retrieved text as evidence.
    qid 546 shows triage loss; the 1094 continuations show Search persistence
    after candidate formation; S1 shows unsupported belief despite Find.
    Some chosen local queries hit irrelevant tables or `no_match`, so local
    query formulation and locator quality are also limiting. This work does
    not isolate one universal dominant component.

12. **Proceed to a 10–20 question cohort?** No. The frozen success gate
    required useful new evidence at multiple checkpoints without premature
    stop. All tested arms yielded **zero useful local-evidence checkpoints**.
    The small bad-case sample and correlated 1094 prefixes permit mechanism
    diagnosis, not expected benchmark improvement.

13. **What is paused?** Further Find prompt emphasis, extra State fields,
    more API aliases, broad rollout, multi-query/localizer expansions,
    grounded submit, and ESR-GRPO/process reward. A future branch should
    first obtain prefix-valid, source-audited verification opportunities and
    a reliable evidence-use signal, then freeze a new minimal intervention.

## Failure taxonomy for future sampling

| Stage | Observable test | Example here |
|---|---|---|
| Retrieval success | A potentially valuable document appears in a tool result. | qid 546 D17; qid 1094 D37. |
| Document triage failure | Source appeared but was not promoted as worth inspecting from prefix belief. | qid 546 shortly after D17 discovery. |
| Local verification opportunity | Prefix has promising D#, explicit missing need, and plausible source containment; next action is Search/stop. | 1094 B checkpoints were plausible but post-run source audit showed poor focus quality. |
| Evidence recognition failure | A relevant raw window is obtained but not treated according to what it actually says. | S1 546 cited W5 for an invented match run; W5 did not contain it. |
| Belief update failure | Model keeps/strengthens a candidate despite contrary or absent evidence. | S1 Mark Williams answer after non-supportive Finds. |

**Boundary:** 13 Orthogonal Search checkpoints, four State/alias checkpoints,
one continuation per complete cell, two historical questions, and no final
answer accuracy experiment. Several Find calls returned an old W# or an
irrelevant table row; `new W#` is not synonymous with useful evidence.
