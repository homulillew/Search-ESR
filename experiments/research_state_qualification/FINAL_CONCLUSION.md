# When can a candidate judgment become Research Control State?

## Boundary and result

This branch starts from remote `experiment/research-state-plan-handoff` at `72ac72e` and writes only in `experiments/research_state_qualification/`. All 13 historical P1 broad-plan checkpoints were reused without outcome-based selection. A single reviewer labeled each exact visible prefix before calls: two `no_target`, seven `hypothesis_only`, four `inspectable`. R1 sampled one new Actor response per checkpoint after the unchanged broad Plan plus a descriptive Qualification Card. All 13 responses were valid; no tool ran, no retry or provider failure occurred. Historical experiments were not edited.

The R1 upper-bound signal was adverse or flat: inspection of the named `hypothesis_only` source rose **2/7 → 3/7**, including first-call inspection **1/7 → 3/7**; utilization of `inspectable` sources stayed **2/4 → 2/4** with one gain and one loss; arbitrary inspection in `no_target` remained **0/2 → 0/2**. Merely naming a tentative D# alongside the word `hypothesis_only` did not prevent its inspection. The frozen stop rule failed, so R2 and R3 were not run; R4 Workspace Directory and R5 Guard were also not entered. See `qualification_upper_bound/RESULTS.md` for paired cells and failure codes.

## Answers to the 12 required questions

1. **Does reviewed Qualification change the Actor?** H1 differs from historical H0 in many batches, but beneficial target selection did not improve overall. At 546:17 it gained a Find of reviewed D11; at 546:33 it lost a Find of reviewed D17; at 1094:69 it added two Opens of unqualified D34. This paired result concerns the full card; the status label alone was not isolated, and single samples with historical H0 limit causal certainty.

2. **Does it mitigate Plan-handoff error amplification?** No in R1. Find(D10) at 546:25 and Open(D34 via W38) at 1094:45 persisted despite explicit missing prerequisites. The new 1094:69 D34 inspection extends the problem. H1 makes D10 the first call at 546:25, whereas it was the second H0 call.

3. **Can DeepSeek reliably distinguish `hypothesis_only` from `inspectable` itself?** Unmeasured. R2 self-qualification was conditional on a helpful R1 card effect and was stopped before any qualifier model call. R1 uses reviewer labels, not model-generated labels.

4. **What is the most common Qualification error?** Model qualification errors are unmeasured. The observed *use* discrepancy is QF5 by the frozen target rubric: five cells did not follow the reviewer-scoped target/status. An Open of a tentative source could also be exploratory falsification, so QF5 here is a routing flag rather than proof of a mistaken belief. Candidate salience is a plausible mechanism, not proven by a status-only ablation.

5. **Is there false evidence promotion?** R1 shows a routing analogue: a 95th-minute event source that lacks the club-history conjunction was inspected despite `hypothesis_only`. It does not show a post-observation textual claim that partial evidence proves the whole match. The latter QF2 metric is unmeasured because R2 and post-tool belief updates did not run.

6. **Does Qualification increase Inspection Precision?** Unmeasured as a source-observation metric: R1 does not execute Find/Open. The one-step proxy moved in the wrong direction for unqualified candidate inspection. No R3 precision denominator or source audit exists for this branch.

7. **Does it increase Evidence Yield?** Unmeasured; there are no new tool observations. Do not infer yield from an Open/Find count.

8. **Is Search persistence still unreasonable by status?** R1 has no NoGain-to-next-decision transition, so the requested stratified persistence measure is unmeasured. At one step, Search calls were 6→6 for `no_target`, 17→14 for `hypothesis_only`, and 6→7 for `inspectable`; neither all Search nor all inspection is inherently wrong. R3 was stopped.

9. **Where is the current bottleneck?** R1 exposes a control-card-to-Actor routing problem even with curated, prefix-supported qualification. It does not isolate Actor internals from card wording, or Workspace representation from local query/window quality. Qualification-model reliability is unknown until R2. The next controlled test should vary the encoding/controller for an unqualified candidate while holding the need and source directory fixed.

10. **Proceed to Workspace Directory?** No. R4 required reliable qualification with residual wrong-D selection in R3. Neither prerequisite was established. A deterministic directory may still be useful later, but this study supplies no R4 evidence.

11. **Is hard action gating justified?** No. Even reviewer-qualified soft cards were not used in the intended direction, and model self-qualification was not tested. A hard mask would risk enforcing an unverified target or withholding needed Search.

12. **What belongs in persistent Research State?** Observed D#/W# identities, source provenance and tool results can be kept as machine-owned evidence. Candidate identity, match equivalence and target status must retain their hypothesis/support distinction. This study does not qualify a model-generated `hypothesis_only` or `inspectable` label for persistent control: even a reviewed label did not reliably improve routing. Persistence requires a later demonstration that the Actor uses the qualified judgment to select a suitable source and gains evidence.

## Cache and limitations

The 13 new DeepSeek responses all reported prompt-cache usage; provider-reported token-weighted hit rate was **99.11%**. The per-response ledger is in `CACHE_USAGE.json`. This two-question, 13-prefix, single-sample study is descriptive. R1's treatment combines a reviewer-selected immediate need, target, support and status, so it cannot attribute a change to the status token. H0 was recorded historically. `Inspectable` means a reasonable source for a subquestion, not a correct answer. One-step R1 cannot measure localizer quality, actual source compatibility after inspection, evidence gain or belief update.

The operational conclusion is narrower than “less Search, more Find”: a tentative source must remain visibly tentative **and** the Actor must act on that distinction before the judgment merits persistence as control state. That second link failed the present R1 gate.
