# H contract / failure authority audit

2026-09-28. Offline repair only; paid calls = 0. `git fetch origin --prune`
confirmed remote `experiment/recoverable-loop-clean` remains
`d4351e2dfc8c886dcd6a14cd51a8ae9a78a23652`. Repair branch:
`experiment/recoverable-loop-h-isolation`. No intervening remote changes.
This audit precedes runtime edits. Historical run001 remains frozen and unrescored.

## Findings and decision (18 audit questions)

1. H is an immutable tuple of `Hypothesis(hypothesis_id, statement, status,
   basis_refs)`; statuses are active/deprioritized/rejected, at most six active.
   H records tentative candidates, never factual C or completion authority.
2. `basis_refs` records observed provenance for a tentative note/status change;
   the presence of a ref does not establish entailment or make H a Claim.
3. `roles.schemas()` currently uses arbitrary-string REFS for H bases and source
   nominations; JSON validation accepts R/C/D/H/W indiscriminately.
4. `engine._hypotheses()` calls EvidenceStore.select, which accepts only archived
   observed W handles. The public schema and runtime contract disagree.
5. H input exposes Q/R, new C, H, observations and D opportunities. Without an
   explicit namespace distinction, citing the immediately supplied R1/C3/D4 is
   natural. The error is not evidence of an API transport problem.
6. run001 has 14 H calls: 12 namespace-invalid proposals, two valid KEEP proposals.
   Breakdown by trajectory is below. Six R, fourteen D and five C invalid-ref
   occurrences were recorded. All are model-output contract violations; none
   implies existing state corruption. Two q546 proposals also renominate old D17.
7. `useful_source_refs` is generic strings in schema, but runtime requires current
   acquisition's new D and excludes inspected D. It is a different domain from W.
8. q546's old D17 is salient in pending TraceView; the prompt says newly discovered
   but does not emphasize THIS acquisition versus pending sources. Failed repeat
   nomination must leave that pending opportunity intact.
9. `step()` invokes H unconditionally after every acquisition, including empty
   repeated Search with no H, C, new windows or new documents.
10. One outer exception boundary includes tools, Reader, Grounding, C commit and
    H. A H ValueError becomes top-level `failure`; the frozen runner breaks.
11. Invalid JSON/schema, namespace, unknown W/H, repeated operations, active-H
    overflow, invalid nominations and H-provider exceptions belong to an isolated
    auxiliary transaction. Preserve raw output and reject the ENTIRE proposal.
12. Missing evidence for existing C, damaged evidence/registry, Trace hash damage,
    or C changes without replayable supported commits are authoritative integrity
    failures. They remain fatal, including when discovered during an H call.
13. H does not theoretically need persistent provenance. Removing the field now
    would require migration of seeds, loader, Actor projections and replay without
    resolving the failure-authority bug. Choose Option A: retain W-only bases.
14. T already archives requests, raw outputs, H before/after and observations.
    It suffices for detailed provenance; no new semantic provenance structure is
    needed. H keeps its compact observed references; T keeps transaction history.
15. H need not run each acquisition. Skip when no active H, no H under test, no
    new C, no new W identity and no new D identity. Existing pending sources alone
    do not force a call. Any active H conservatively permits NoGain deprioritization.
    Identity novelty is mechanical, not a claim of semantic novelty/relevance.
16. Current prompt forbids NoGain-based factual negation but underspecifies local
    versus global contradictions. REJECT requires direct contradiction of the H
    statement itself; weak/indirect/candidate-local mismatch, missing bindings,
    competitors and fruitless routes permit KEEP/DEPRIORITIZE instead.
17. Use typed, narrowly caught H output/provider exceptions. Validate state before
    and after the optional transaction; don't catch integrity/logging/programming
    errors as auxiliary. Build H and opportunities locally, validate all, then
    commit once. Never translate C/D/R refs into W or silently repair proposals.
18. Minimal repair: retain Q/R/C/H/T, add explicit W/D/H schema helpers for H only,
    clarify H prompt, isolate its transaction, add deterministic skip and mechanical
    failure/skip events. Acquisition/claim progress and feedback survive auxiliary
    failure. Other roles' prompts/schemas and real tools remain unchanged.

## Frozen failed-output inventory

| Trajectory | Slot | Invalid namespaces | Additional issue |
|---|---:|---|---|
| R1_Q1094__rep1 | 1 | R | none |
| R1_Q1094__rep2 | 1 | R | none |
| R1_Q546__rep1 | 1 | D | old D17 nomination; earlier valid ADD must not commit |
| R1_Q546__rep2 | 1 | D | old D17 nomination |
| R2_Q228__rep1 | 2 | C | C3 already grounded |
| R2_Q228__rep2 | 1 | D | none |
| R2_Q637__rep1 | 1 | C,D | local FOP does not directly refute global SPS |
| R2_Q637__rep2 | 1 | D | same semantic overreach |
| R3_Q538__rep1 | 3 | C,D | C2 already grounded |
| R3_Q538__rep2 | 2 | D | book conjunction not established |
| R3_Q922__rep1 | 2 | C | C3 grounded; memo/letter relation substitution |
| R3_Q922__rep2 | 2 | D | none |

Source: frozen `micro_recovery/analysis/SEMANTIC_REVIEW.json` H_contract_audit,
engine/roles/contracts/state/tools/replay source, and raw role logs. The 12/14
historical failure result remains unchanged.

## Implementation and validation boundaries

- Failure event: attempt, typed error, raw-output SHA-256 (null for provider with
  no output), H_unchanged. Raw output remains in existing role_response logs.
- Acquisition outcome, committed C and Gain are independent of H outcome. Step
  returns auxiliary_failures, without top-level failure for H proposal/provider
  failure. Grounding/Closure errors keep their existing conservative behavior.
- Integrity checks use the immutable starting snapshot plus existing T, evidence
  and handle registries. This is private mechanical verification, not added state.
- Replay all 12 unchanged raw H response strings. The four R1 cases would now
  skip H in production: explicitly force ONLY the skip predicate in the offline
  fault-injection replay, and separately test the actual skip path. No inference
  that the model would choose the scripted continuation.
- Test atomicity, namespace, pending opportunities, provider failure, preserved C,
  next Actor, fatal integrity, replay and real-tool/Closure regressions. Counter-
  examples are rubric/scripted checks, not measured H semantic accuracy.
- No new live runs, no old-budget reuse. Future H1 is result-informed interface
  continuation; independent recovery evidence requires new H2 prefixes.
