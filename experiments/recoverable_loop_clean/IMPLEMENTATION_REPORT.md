# Implementation report — Clean Recoverable Loop

## Status

**Offline implementation and validation complete. No new paid experiment run.**
Audit committed first: `ea2ce2fd`. Base Stage4 remote HEAD:
`7fdb048e856545facd4acfb590e8cf28c46f1013`.
Branch: `experiment/recoverable-loop-clean`.

76 offline tests passed, including73 new checks and3 unchanged backend regressions.
Ten historical regression fixtures and12 replayable traces are delivered. Reports
and manifests are in `OFFLINE_VALIDATION.md` and `offline_validation/run001/`.

## Answers to the fifteen required questions

1. **Clean Stage4 branch?** Yes. The remote Stage4 ref was fetched/checked; it had
   not advanced. The new branch descends directly from that ref. No later
   diagnostic implementation was merged or cherry-picked. Historical files are
   unchanged. AGENTS.md is copied operational guidance, not experimental logic.
2. **Old Writer/Admission imported?** No. No control-blind Writer,
   single-excerpt-only Admission or old E1 gate. The historical Gap-conditioned
   selective Reader/source-relative verification principles were reimplemented
   as narrow roles, with deviations documented before code in DESIGN_AUDIT.md.
3. **OneGap ephemeral?** Yes. No OneGap state field. It is current control input
   and historical T data only. Persistent semantic state remains exactly Q/R/C/H/T.
4. **Actor actions align1:1?** Yes. The action arguments are generated from the
   real tool schema; dispatch passes the exact tool name and arguments to execute.
   Closure is a separate decision and never enters that acquisition union.
5. **Open/Find ambiguity?** The old parameter ambiguity is removed. Open accepts
   only W plus before/after/around; Find accepts only D plus query. Their returned
   text can overlap naturally. No semantic translation or intent repair exists.
6. **Gap-conditioned relevance restored?** Yes. Reader receives OneGap + existing
   C + current actual observations, and proposes0–3 useful new facts per acquisition.
   It cannot write state. Model relevance quality remains unmeasured.
7. **Evidence sole truth basis?** Architecturally yes. Grounding sees the candidate
   and full cited actual windows/source metadata only. Q/R/H/OneGap/Trace are not
   evidence. The semantic verifier can still make a mistake; offline mocks do not
   prove all committed statements will be true in live runs.
8. **H low authority?** Yes. H only guides investigation and has bounded typed
   transitions. It cannot become C without actual evidence/grounding, close R, or
   grant READY. H is absent from Reader, Grounding, Closure and Finalizer inputs.
9. **NoGain implementation?** Mechanical deltas over accepted C, novel H, active-H
   downgrade and newly nominated useful uninspected sources. Nothing else means
   Gain automatically. Same-family consecutive NoGain ignores query paraphrase.
   True-but-irrelevant C and semantic duplicates remain logged failure mechanisms.
10. **Closure real recovery channel?** Yes, in implemented control flow and offline
    invocation: Actor request → Closure CONTINUE → feedback T → next Actor.
    Ten historical fixtures exercise this round trip. Autonomous usefulness is
    not yet measured; the fixture responses are scripted.
11. **Premature Closure classification?** An evidence-insufficient request with a
    CONTINUE is allowed and incurs an efficiency cost, not a safety violation.
    Malformed Closure output is a retained execution failure. A semantically
    false READY remains the substantive high-risk error.
12. **Historical bad cases covered?** Yes, all ten requested mechanisms have
    provenance-bearing regression fixtures: Euler, book/article, memo/letter,
    patient/report country, teammate relation, DLC qualifier, q637 local/global,
    Ding2019, q546 source opportunity and q1094 repeated Search. These are selected
    projections with explicit interventions, not evidence of full model success.
13. **Known interface risks?** No live SemanticPort/SDK adapter is installed yet.
    Live resumption needs full pinned documents and complete handle hydration;
    state/evidence replay alone cannot recreate unseen source text. The test
    tokenizer/corpus are substitutes. Structural validation does not determine
    natural-language premise correctness. A tool/provenance normalization failure
    should terminate a live trajectory, rather than continue with partial registry
    effects. Additive semantic unions are not assumed to be provider-native JSON
    schema features; the future transport must preserve output and validate locally.
14. **Scheme-level risks?** Grounding and Closure can both over-infer binding;
    explicit prompts are not guarantees. Selective Reader can miss useful facts
    or accept irrelevant truths that inflate Gain. H novelty and source usefulness
    are semantic judgments. The coarse route-family signal can merge different
    routes or be evaded by a label change. Closure feedback can become stale.
    C is append-only in v1; contradictory source-relative facts stay visible for
    Closure, and erroneous accepted C has no autonomous retraction mechanism.
    Long C/H/T can grow despite bounded active H and short TraceView. Finalizer
    citations do not mechanically prove answer entailment. No new state graph is
    justified by these risks alone.
15. **Qualified for Micro-Recovery?** Qualified to prepare its real freeze after
    authorization: interface/permission/replay prerequisites passed offline. Not
    qualified to claim model reliability or skip the experimental gate. Next plan
    specifies six states × two replicates × at most three decisions, with a tight
    ceiling192 semantic requests and32 acquisitions. Provider parameters, authentic
    live prefixes, transport and their final hashes must be frozen before calls.

## Files and use

- `ARCHITECTURE.md`: state, role order, recovery and replay.
- `INTERFACE_CONTRACTS.md`: exact schemas and semantic limitations.
- `OFFLINE_VALIDATION.md`: results, provenance and scope.
- `NEXT_EXPERIMENT_PLAN.md`, `CALL_ESTIMATE.json`: unexecuted bounded diagnostic.
- `llm_chat/recoverable_loop/`: narrow reusable implementation.
- `tests/recoverable_loop_clean/`: network-denied unit/integration regressions.
- `build_fixtures.py`: deterministic extraction from historical artifacts.
- `validate_offline.py`: repeatable checks with a new output directory each run.

## Stop boundary

TASK.md §28 explicitly restricts this task to repository analysis, implementation,
offline tests, historical fixture replay and mock tools. It requires new explicit
authorization before paid/live experiments, overriding earlier standing API
permission for this task. **Stopped after offline delivery.** Zero paid requests,
zero live BC+ rollout, zero tokens; cache rate is undefined. No request was queued.
