# Research Progress Frontier: final conclusion

This branch tested four local links in order, with each later stage opened only after the earlier prespecified practical gate passed. The evidence supports a **small, explicitly versioned Research Progress prototype** as the next experiment. It does not establish full-question accuracy, a production state machine, hard tool masking or a training objective. The strongest remaining uncertainty is whether the system can form and update these clean states in a live multi-step history; here the Claim/Gap views were reviewer constructed and the real tool stage stopped after one action.

| Link | Observed result | Main limit |
| --- | --- | --- |
| Evidence → Closure | 29/29 three-way agreement; false close 0/8; stale subclaims closed 5/5 | Repeated facts, easy explicit refutations, eight qids |
| Closure → ActiveGap | 8/8 acceptable; closed gap reselected 0/8; premature narrowing 1/8 | Clean reviewer-authored views; four choices per case |
| ActiveGap → action | No-tool class 25/25; tool-schema first action 23/25; optional Verify 3/5 | Controlled low-ambiguity states; no no-state paired arm |
| Action → evidence | Suitable retrieval 6/7; useful evidence 4/7; local progress 4/7 | Only qids 546/1094, one step, one extra redundant Open |

## Answers to the requested research questions

1. **Can DeepSeek judge supported/refuted/open?** In this frozen prefix-only bank, yes: 13/13 supported, 8/8 refuted and 8/8 open. This is a local capability result, not a population reliability estimate.
2. **Most common Closure error?** None crossed the frozen status boundary. One W38 explanation mildly overstated chronology while leaving the claim open. The bank is small and correlated, so absence of errors is not proof of a robust verifier.
3. **Can it recover stale gaps?** Yes for the five frozen stale claim-level cases (5/5; low-ambiguity subset 4/4). Other constraints in the same original questions may remain open.
4. **Can correct Closure support a reasonable ActiveGap?** Yes in the eight clean Progress Views: 8/8 selected gaps were in the pre-call acceptable sets. The model did not have to build the Closure Table itself.
5. **Does it revisit closed gaps?** None of eight Stage B choices did.
6. **Does it jump to unverified downstream properties?** Once: qid 1094's selected gap was acceptable, but the reason invented an Inter–Milan fixture before that link was observed. An unsupported phrase also appeared in qid 387's rationale.
7. **Does expected Source Type match ActiveGap?** The reviewer judged 8/8 source types compatible in Stage B. This evaluates type, not whether a concrete D is correctly chosen or whether a query finds evidence.
8. **Can it route by uncertainty type?** Given the clean state, no-tool class choice was 25/25 and real-schema first action was 23/25. Search/source, Find/location and Open/context were 5/5 each in both arms; real-schema Verify/closure was 3/5. C-A free-form argument validity was only 10/25 because its prompt did not supply exact schema keys; C-B arguments were 25/25 valid.
9. **Will it freely invoke Verify?** In the five C-B closure diagnoses, 3/5 chose Verify and 2/5 chose Open. In the two selected real-step closure cases, 1/2 chose Verify. Invocation is less reliable than semantic verification on supplied evidence.
10. **Does harness-triggered Verify help?** In the two Stage D closure cases, V1 produced 2/2 correct local closures and no extra corpus retrieval; V0 produced 1/2 and made one redundant Open. This is a diagnostic contrast, not a robust effect estimate or authorization for a default runtime change.
11. **Do real Search/Find/Open produce useful evidence?** Yes, in 4/7 actual retrieval actions (Search 1/2, Find 1/2, Open 2/3), with suitable sources in 6/7. Excluding the closure case's redundant Open, nominal retrieval yield is 4/6. The snooker sequence Search produced no new relevant preview, and one correctly targeted Find localized the wrong part of a results table.
12. **Where is the bottleneck?** Closure semantics and source-type selection were strong under the clean inputs. The observed failures are optional Verify invocation (RP12), retrieval of a suitable *concrete* source for one Search, and one Find query/window miss (RP9). The most serious unmeasured bottleneck is building and maintaining the correct Closure/Frontier state from live observations. With one failed Find, there is not enough evidence to call the localizer the dominant bottleneck.
13. **Does this more directly support “the model does not know current research progress”?** It supports the *usefulness* of an explicit progress view: the model routed clean states well while historical natural actors were Search-heavy. It does not isolate a causal effect of progress state in this stage, because there is no matched same-prefix/no-progress arm and the views were reviewer made. The stronger claim remains a hypothesis.
14. **Is a minimal ESR Frontier runtime worth testing next?** Yes, as a bounded prototype on a new branch: mechanically tracked D/W and observation versions, prefix-bound Verify for concrete claims, one selected open gap, uncertainty type, and a 4–8-decision comparison against a matched baseline. It must measure suitable source and useful evidence, preserve all tool choices, and test live state construction. The first bootstrap action can remain an ordinary Search from the original question, with no initial claim graph.
15. **Is there evidence for full ESR-GRPO?** No. The sample is diagnostic, mostly reviewer constructed, and contains no training or reward-generalization result.
16. **Should hard action gating remain prohibited?** Yes. The soft progress view had two optional-Verify misses, a failed source Search and a failed Find locator; a wrong or stale state could still suppress the right tool. Harness-triggered *semantic review* on explicit closure is a narrower experiment than masking Search/Find/Open.

## What should persist

Persist canonical observed D#/W# and raw-result identities mechanically; persist claim/version/evidence-ref associations and explicit verified supported/refuted/open outcomes; keep the set of genuinely open, prerequisite-satisfied gaps and one current ActiveGap with its evidence basis; record current uncertainty type and visited/query results. Hypotheses, source relevance guesses and unverified candidate details remain provisional. A new tool observation must be able to invalidate or reopen the relevant claim/gap. The state should represent where research stands, without turning a plausible candidate into evidence.

## Scope and failure accounting

The study used existing DeepSeek `deepseek-flash` and frozen Search/Find/Open code. Stage D initially failed to load its GPU retriever before any case, then ran on CPU with the same index/weights and device-dependent numeric precision. Provider retries were zero. Historical experiment directories were not modified. The Stage D cells share two qids and are not independent; complete-case Submit results concern synthetic local subtasks. A single Find miss does not meet the preregistered trigger for the optional full-document localizer audit, so no localizer follow-up or long rollout ran in this branch.

The practical target is **Evidence → correct Closure → acceptable ActiveGap → appropriate action → suitable source → useful evidence**, with each link measured separately. An increase in Find or decrease in Search alone would not satisfy it.
