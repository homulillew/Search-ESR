# State transition feedback — final conclusion

## Execution and interpretation

Base: remote `experiment/state-conditioned-retrieval` at `22c3758bd0a810c0bd2efd1e2d5ffdea92c6afe0`. T0 froze 12 transitions from nine qids before calls. T1 ran 36/36 valid DeepSeek query calls and retrievals; T2 ran 12/12 new valid calls and reused T1 PRE exactly; T3 ran 12/12 valid updater calls and reviewed all 21 proposals. Model was `deepseek-flash`, `max_retries=0`; Search used the unchanged Qwen3-Embedding-8B/100,195-document index. No historical experiment was modified.

**Execution Gate failure:** a post-T3 original-question audit found six Bridge observations that already reveal the original requested answer and two more transitions with contradicted candidates. This is 8/12 (66.7%) hard exclusions. At most four provisional transitions across two qids remain; the gate requires at least eight cases and five qids. T4 and T5 were therefore **NOT_RUN**, in accordance with the task's severe-integrity exception. The frozen T0 bank and T1–T3 outputs were not edited or cherry-picked. The three Oliver Mtukudzi entries repeat one source and do not verify every distinctive question clue, so even the four-case upper bound is weak. See `transition_bank/POST_T3_INTEGRITY_AUDIT.md`.

T1 and T2 still measure real **conditional next-Gap retrieval** under fixed inputs. They do **not** prove a feedback loop toward the original question. In the 11-case diagnostic cohort excluding the earlier-recognized B07 mismatch, T1 POST versus PRE Direct@5 was 11/11 versus 8/11 (+27.27 points); six first-source ranks improved, none worsened. RAW also reached 11/11, using 8,776 prompt tokens versus POST's 4,275. The later integrity audit supersedes that cohort's “clean causal” interpretation. In the at-most-four provisional cases, PRE and POST both have Direct@5 of 4/4, with only one rank improvement, across two qids. The originally preregistered descriptive effect class for T1 was Strong; the full original-question causal claim is **unidentified**.

T2's 11-case conditional diagnostic was contrary to its hypothesis: F_EARLY Progress@5 3/11 versus F_PREMATURE 8/11. A separately marked post-retrieval audit found one omitted sufficient early source, making semantic F_EARLY 4/11; the frozen primary result stays 3/11. This is a Negative conditional result, not a reason to prefer answering downstream questions without verified referents. T3 proposal-level source support was 18/21 (85.7%), decision relevance 19/21 (90.5%), and both 16/21 (76.2%). Eight of 12 stage-local oracle bindings were recovered, but most cases are invalid for the original-question feedback estimand. T3 correctly excluded the false Hijitus candidate in B05; it also made three over-specific or over-interpreted complete claims. API cache-hit share was 29.1% T1, 44.77% T2, 19.86% T3.

## Required research answers

| # | Question | Answer supported by this run |
|---:|---|---|
| 1 | Verified Bridge Claim improves next retrieval? | Conditional next-Gap routing improved in T1, but bank contamination prevents a valid original-question causal claim. |
| 2 | Mainly referent binding? | The query-level signal is candidate inclusion 2/11 PRE to 11/11 POST in the earlier diagnostic cohort; independent causal attribution is unavailable. |
| 3 | Constraint resolution independently useful? | Not isolated; the bank and arms cannot estimate a separate constraint effect. |
| 4 | Hypothesis exclusion useful? | T3's B05 exclusions are source supported and expose a wrong oracle candidate; no retrieval effect was tested. |
| 5 | Raw Observation versus Minimal State? | Equal any-sufficient @5 and MRR in the 11-case conditional cohort; no valid full-loop comparison. |
| 6 | Fewer tokens for Minimal State? | Yes for that conditional comparison: POST 4,275 versus RAW 8,776 prompt tokens, with equal 11/11 @5. |
| 7 | Truthful noise harmful? | NOISE arm was not run; no conclusion. |
| 8 | Candidate inclusion, clue load, relation specificity? | Candidate inclusion rose 2/11→11/11; lexical clue-load proxy fell .2668→.0500. Relation lexical coverage fell .5313→.4958, so specificity improvement was not established by this proxy. |
| 9 | Clearest qids? | Conditional rank improvement appeared in q517, q435, q1094, q311, q186, q546, but five of these qids include answer leakage or wrong-candidate transitions. q435 remains provisional. |
| 10 | Clean POST failures? | The only miss in the earlier 12-case POST set was q1034/B07, itself invalid. No adequately sized clean cohort exists. |
| 11 | Clean-State misses prove Retriever limitation? | No; the apparent remaining miss is invalid, and the conditional successes do not isolate Retriever quality. |
| 12 | q1094 Retriever-limited? | No such conclusion: B04's match Observation already names Messi, the original answer. |
| 13 | q435 stably Context-limited? | No. The repeated same-source entries and partial clue support preclude a stable classification; conditional ranks vary by checkpoint. |
| 14 | State–Frontier compatibility important? | Plausible, but T2's actual conditional comparison is negative and its truth set has one omitted early source. No general causal rule follows. |
| 15 | Early Gap easier than premature Gap? | No in the frozen 11-case diagnostic: 3/11 versus 8/11 Progress@5, or 4/11 versus 8/11 with separately audited alternative. |
| 16 | Premature failure mainly clue soup or guessing? | Not established. Clue-heavy or guessed queries occurred in the early arm too; many premature searches found a sufficient source. |
| 17 | Online updater support precision? | 18/21 = 85.7% complete proposals, using single-reviewer source-only labels. |
| 18 | Decision-relevance precision? | 19/21 = 90.5%; both supported and relevant 16/21 = 76.2%. |
| 19 | Mostly candidate binding instead of incidental facts? | Eight of 12 stage-local oracle bindings recovered; only two of 21 proposals were marginal/incidental. This is not a valid full-task binding rate. |
| 20 | Oracle versus online Minimal State gap? | Unmeasured in retrieval: T4 R2/R3 comparison was not run. |
| 21 | R0/R1/R2/R3 Bridge→Direct conversion? | Unmeasured; all four T4 arms are NOT_RUN. |
| 22 | Minimal State better than Forget? | Conditional T1 POST beats PRE, but original-question causal inference fails; T4 unmeasured. |
| 23 | Minimal State reaches Raw Observation? | Yes for conditional 11-case T1 @5 and MRR; broader claim unmeasured. |
| 24 | Three-round Stateful faster than Stateless? | Unmeasured; T5 NOT_RUN. |
| 25 | Fewer NoProgress rounds? | Unmeasured; T5 NOT_RUN. |
| 26 | Fewer clue-heavy queries in loop? | Unmeasured; only one-step T1 query proxy improved. |
| 27 | Fewer repeated paths? | Unmeasured; T5 NOT_RUN. |
| 28 | State value as verified binding plus constraint maintenance? | A coherent *working hypothesis*, not validated by this contaminated bank. |
| 29 | Shift Claim Admission to decision-uncertainty reduction? | Do not change production admission from this run. T3 B05 shows that source-supported exclusion can matter, but further prospective evidence is needed. |
| 30 | What should enter State? | Candidate binding, discriminative constraint, or exclusion only when the original-question role and complete source support are checked; preserve provenance. This is a proposed qualification rule, not an evaluated policy. |
| 31 | Which future answer facts need not be stored? | Facts irrelevant to the next decision should remain in Evidence until needed; this run does not establish a safe general discard rule. |
| 32 | Independent Frontier Selector needed? | Not tested. T2 argues against blindly fixing either early or downstream Gap, but does not identify a selector architecture. |
| 33 | Joint `next_gap + action/query` actor supported? | Not tested; T5 NOT_RUN. |
| 34 | History Prior needed? | No evidence from this run. |
| 35 | Old/new source scope router needed? | No evidence from this run. |
| 36 | Passage-level Retriever needed? | No clean-State failure cohort identifies that intervention. |
| 37 | Specific clean-State failure cohort? | None established. Do not promote B07 or answer-leaking cases as Retriever misses. |
| 38 | Find/localizer changes needed? | Not tested; both were frozen. |
| 39 | Persistent TestCard needed? | No evidence; not part of this run. |
| 40 | Finer Evidence pointer needed? | The audit demonstrates a need for explicit original-target and source provenance checks. It does not isolate finer W/offset granularity as the cause. |
| 41 | ESR-GRPO foundation? | No. The transition bank and online labels are not clean enough to define rewards or training targets. |
| 42 | Main bottleneck among Online State Construction, Frontier Selection, Retriever, Localizer? | This run cannot rank those four. The immediate demonstrated bottleneck is **transition qualification/bank validity**, upstream of all four. T3 also shows some online over-interpretation; Retriever and Localizer limitations are unproven. |

## Next valid experiment

Build a **new**, prospectively frozen bank of at least eight transitions across five qids. For every candidate, review the entire original question and observation text **including URL/title** before any model call; reject observations containing the original requested answer. Require the bridge claim to be source supported without promoting a partial clue to full candidate proof. Keep the next Gap anchored to the original unresolved target rather than inventing a convenient downstream question. Include an independent check that direct and bridge source sets are sufficiently exhaustive. Only after that bank passes the Execution Gate should R0–R3 and the three-round loop be run. The present frozen outputs remain read-only evidence about conditional query behavior and about why the bank must be qualified first.
