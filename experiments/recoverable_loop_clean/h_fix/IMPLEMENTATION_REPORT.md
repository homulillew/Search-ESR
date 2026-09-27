# H contract and failure isolation — implementation report

## Result and scope

Offline repair validated on runtime commit `4e91b59c0d1ea15d46aaf31e802e394e30de2232`.
144 tests pass. All 12 original invalid H outputs were injected without alteration;
all 12 executions reached a subsequent scripted Actor, and all five historical new
grounded Claim commits survived. Four additional R1 replays use the production skip
policy and perform no H call. Paid calls and live retrieval calls: **0**.

This establishes executable failure isolation, not model recovery accuracy.
The historical run001 conclusion remains: Micro-Recovery did not complete recovery
validation; 12 trajectories were truncated by H contract failure. No rescoring.

## Required questions (1–25)

1. **What is H?** Tentative candidates/hypotheses with active, deprioritized or
   rejected status. It is low-authority and may be wrong; H cannot write C or READY.
2. **H Manager duties?** Propose atomic ADD/KEEP/DEPRIORITIZE/REJECT operations and
   nominate a few newly discovered, uninspected useful D sources. No truth or
   completion adjudication was delegated to it.
3. **Why did 12/14 fail?** Their basis_refs contained R/C/D references where runtime
   accepted only observed W. Two proposals additionally nominated old pending D17.
   The remaining two were valid KEEP proposals, not semantic improvements.
4. **Why no schema rejection?** Generic string arrays admitted every namespace.
   New H schemas distinguish WINDOW_REFS, DOCUMENT_REFS and HYPOTHESIS_REFS.
   REJECT additionally requires at least one W reference. Existence remains a
   runtime check, because regex correctness alone cannot establish observation.
5. **Why trajectory termination?** Mandatory H ran inside the main step exception
   boundary; its ValueError produced a top-level failure consumed by the runner.
6. **Why inappropriate?** An auxiliary candidate note effectively had authority to
   terminate research after successful grounded factual progress. Failure authority
   now follows mutation authority.
7. **Keep basis_refs?** Yes: Option A, minimal backward-compatible change.
8. **Namespace?** Only `^W[1-9][0-9]*$` and already observed. No mapping of C/D/R/H
   into W. Question-inspired ADD may use an empty basis.
9. **Provenance migration?** None. Historical H records/loaders retain their format.
   Existing T records request, raw response, observations and H transitions; the
   compact W refs remain in H. Failure records add only mechanical metadata to T.
10. **useful_source_refs restriction?** D-only schema plus membership in current
    acquisition's new documents, excluding inspected documents. H sees the explicit
    eligible list. Invalid nomination rejects the entire H proposal; old pending
    opportunities continue in TraceView until inspection.
11. **Mandatory H?** No. It is an optional auxiliary transaction after the factual
    acquisition/Reader/Grounding/C chain.
12. **When skip?** No active H, no H under test, no newly committed C, no new W
    identity and no new D identity. All five conditions must hold. Any active H
    conservatively allows NoGain-based deprioritization. Mechanical W/D novelty
    does not assert semantic novelty or usefulness. Pending D alone does not force
    H, and an old W can still yield new C and therefore trigger H.
13. **Does H failure end step?** Model JSON/schema/namespace/existence/ID/duplicate/
    active-bound/nomination failures and H semantic-port exceptions produce
    `auxiliary_failures`, `hypothesis_outcome=failed`, and no top-level failure.
    `hypothesis_update_failed` records attempt, error, raw-output SHA-256 and
    H_unchanged. Provider exceptions with no output have a null raw hash and an
    archived role_failure. There is no retry, substitute output or repair.
14. **Does failure revoke C?** No. All H changes and opportunities are prepared in a
    local candidate before commit. Failure preserves H exactly and preserves the
    already committed acquisition evidence and C. The whole proposal is atomic.
15. **Feedback?** Existing Gain rules remain: new verified C, new nonduplicate H,
    active-H downgrade, or new useful uninspected source. Failed H itself adds no
    Gain. New C plus bad H is Gain; no progress plus bad H is NoGain. Both can
    continue. Acquisition, claim and H outcomes are separately recorded.
16. **REJECT/DEPRIORITIZE?** REJECT requires direct observed contradiction of the
    hypothesis itself with matching identity/relation. NoGain, weak inconsistency,
    competitor, missing binding, local mismatch or futile route support
    DEPRIORITIZE; inconclusive local evidence may KEEP a global hypothesis.
17. **q637 avoided?** Its original invalid proposal is rejected atomically, leaving
    SPS H unchanged. The revised prompt/rubric explicitly disallows global SPS
    rejection based solely on an unbound local FOP report. **Semantic prevention
    is not established:** a structurally valid W-only REJECT could still be wrong.
    No H Grounding/Admission agent was added. Scripted counterexamples demonstrate
    the intended boundary and H-to-C isolation, not real model compliance.
18. **q228 C3 plus invalid H?** Yes: rep1 replays both historical slots, commits C3
    from W4, rejects unchanged raw C3-in-basis output, retains Gain and reaches the
    next scripted Actor. No C3-to-W4 conversion occurs.
19. **R1 NoGain reaches Actor?** Yes: all four original prefixes skip H normally.
    Separate forced-scheduling fault injections replay all four invalid outputs
    and preserve NoGain. A real-tool mock regression then chooses a materially
    different Find/localization route and can acquire a supported Claim.
20. **Closure→C→bad H continues?** Yes. q922 rep1 replays CONTINUE, Open W4, new W6,
    grounded North Transylvania C3 and invalid H, then reaches the next scripted
    Actor. Dedicated scripted Closure-veto regression also passes.
21. **Still fatal?** Missing evidence for existing C, corrupted text/hash or Trace,
    inconsistent bidirectional D/W registry, and state changes without replayable
    supported commits raise IntegrityError. They are checked at step boundaries
    and around H, including when a provider fails. Unexpected H programming/logging
    failures are outside the narrow auxiliary catch. Reader/Grounding/Closure and
    Actor errors retain their previous conservative top-level failure behavior.
22. **Added persistent semantic state?** None. State remains exactly Q/R/C/H/T;
    Q/R remain unchanged and OneGap ephemeral. Private initial-state/evidence
    snapshots are mechanical replay baselines, not additional semantic state.
23. **Search/Find/Open changed?** No. Backend, orthogonal semantics, handles, tools,
    RawWindowBuilder and real action schemas are unchanged. Historical replay uses
    a separate RecordedBridge, never installed as the production tool backend.
24. **Reader/Grounding/Closure changed?** Their prompts, schemas and the core
    `_claim_chain`/`_closure` method ASTs are identical to the base. Actor and
    Finalizer prompts/schemas and `finalize` AST are also identical. Only step
    orchestration/outcome isolation and shared replay plumbing changed. Closure
    still sees Q/R/C/supporting Evidence only, without H, OneGap or Trace.
25. **New paid calls?** None. API config loading and sockets are denied in offline
    validation; transport tests use MockTransport. No key was read, no live BC+
    rollout or replacement sample executed. Future plans require new authorization
    under this task's explicit scope.

## Evidence and limitations

- [Validation and coverage](OFFLINE_VALIDATION.md), [exact historical replay](RUN001_FAILURE_REPLAY.md).
- [Integrity manifest](offline_validation/run001/INTEGRITY.json): all 313 protected
  historical files match the base Git blobs, with SHA-256 recorded for each.
- Model semantic quality remains unmeasured after the prompt change. The four
  historical semantic risks remain open model risks, not automatically solved.
- Integrity replay trusts the externally reviewed initial C snapshot, just as
  historical loading did. It validates all subsequent commits and evidence links;
  recorded supported verdicts are not a new semantic entailment oracle.
- Replay checks currently traverse the short episode history at transaction
  boundaries. This favors auditability; throughput on much longer episodes has
  not been benchmarked. No speculative optimization or new runtime state added.
- A subsequent Actor/provider failure may still stop a trajectory for its own
  reason. H failure isolation guarantees a reachable next decision boundary,
  not provider availability or a correct next action.

## Commit discipline

1. `b1a216b7`: design audit before runtime edits.
2. `4e91b59c`: isolated H implementation, tests and offline replay driver.
3. Validation commit: these reports and reproducible offline results; no old result
   or historical conclusion changed, no squash.
