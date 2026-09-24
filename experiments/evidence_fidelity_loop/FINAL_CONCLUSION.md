# Evidence Fidelity: gated conclusion

E1 alone ran. The 44-case, 12-qid paired DeepSeek study used 88 genuine historical Tool Observations and one response per arm with zero retries or errors. The full packet recovered all three frozen identity/time-dependent facts missed by text only: the Forbes Africa source identity, the 2014 season attached to Rangers' table row, and Peter King attached to the filmography role. Denominators are only one M2 and two M3 facts.

Every P finding was supported by its full source packet (46/46). Its required-finding recall was 35/37 (94.6%) and no metadata overreach was observed. Four P findings, however, were source-supported yet off-Gap or redundant. The pre-call local rubric counted only supported **and** new, Gap-relevant findings toward its precision gate, giving 42/46 (91.3%), below 95%. E1 therefore failed its *frozen local gate* and E2, E3, and F3b were not run. The task's narrower source-support precision definition would give 46/46 and pass; this mismatch is a protocol-design limitation, not evidence that P fabricated those facts. We cannot change the gate after seeing results. The branch preserves both measures and all raw requests and outcomes.

## Answers to the 22 research questions

| # | Conclusion from this branch |
|---:|---|
| 1 | Yes, in three selected pairs, text-only input omitted the source identity or year needed for the full Finding. This is a small, targeted diagnostic. |
| 2 | Yes in those pairs: P recovered 3/3 M2/M3 required facts versus T 0/3. Broader reliability is unmeasured. |
| 3 | No unsupported metadata relation was emitted in E1 (0/46 P findings). Four P findings were supported but off-Gap or redundant. |
| 4 | Not tested in E2. Historical F3 contained a 67-albums/2016 join error, but E1 produced neither such finding. |
| 5 | Not tested; support-pointer verification was gated out. |
| 6 | Exact-span binding remains a hypothesis; this branch does not establish its need or benefit. |
| 7 | Match results, biography details, and episode plot facts in these cases were in the W body. Rangers' 2014 year came from the title; Peter King's filmography identity came from the D title; the direct Forbes Africa source identity came from its URL and document context. |
| 8 | Not tested; E3 was gated out. |
| 9 | Not tested; no `missing`-field experiment ran. |
| 10 | Not tested; pending-W-first rollout was gated out. |
| 11 | Not tested in a new runner; duplicate `(Gap,W)` handling remains open. |
| 12 | Not tested; immediate-stop runner was not changed. |
| 13 | Not tested; no new Useful-W-to-Valid-Claim conversion rate exists. |
| 14 | Not tested; no Group A paired rollout occurred. |
| 15 | Not tested in F3b. Historical retrieval-limited q546 and q1094 remain useful controls, but query/source/localizer attribution is not resolved here. |
| 16 | Evidence-packet truncation is a demonstrated local mechanism; the main end-to-end bottleneck cannot be ranked against source acquisition, query generation, or localizer without E2–F3b. |
| 17 | The minimal Question–Claims–Gap–optional-Hypothesis state remains compatible with these results; sufficiency has not been proven by rollout. |
| 18 | No result calls for a persistent TestCard graph. |
| 19 | No. This gated branch gives no basis to enter multi-Gap Frontier. |
| 20 | No. It gives no basis for a longer rollout. |
| 21 | Yes: there is still insufficient evidence to start ESR-GRPO. |
| 22 | Yes: keep hard Search/Find/Open gating prohibited. |

## Interpretation and next admissible step

The full packet moved three selected factual bindings into correct Findings without inventing a metadata relation. It also increased tangential extraction in four places, so source completeness alone is not a sufficient Claim-admission policy. The frozen E1 gate stops this branch before testing pointers, closure, or runner effects. If this line is resumed, use a new independent E1 bank and pre-register source-support precision and Gap relevance as separate gates before any calls; retain this branch's results rather than replacing them. No historical experiment result or backend was rewritten.
