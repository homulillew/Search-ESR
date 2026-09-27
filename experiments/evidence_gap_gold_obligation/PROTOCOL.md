# Frozen protocol: Gold Obligation → Evidence Gap

## Material Passport

User supplied experiment; exposed development states; single Codex reference/response reviewer; no human subjects. Frozen model is DeepSeek Flash. Scope is conditional gap quality, not whole-agent accuracy.

## Design and selection

Census of 27 F07–F16 natural snapshots in the historical confirmation INPUTS, one local obligation per snapshot, 10 question clusters. The 14 D* synthetic delta states are excluded. Eight satisfied controls (29.63%). Original question, claim statements and H are copied from the original acquisition snapshots. The confirmation API projection had replaced null H with empty strings; original nulls are preserved here. Historical source admission is inherited, not a fresh truth audit.

O is manually scoped from each Q/current C. Multiple historical snapshots are familiar to the same reviewer; no gold answer, source audit, later tool result or outside knowledge enters a reference. Claims in a later case are never support for an earlier case. Gold references are local and can be satisfied even if Q globally remains unresolved. Control scope is fixed before calls.

G0 = O+C. G1 = O+C+unaltered H plus exactly the supplied H paragraph. No Q in either payload. Fixed prompt extracted from TASK sections 20/21. 2 independent requests per case/arm; 108 total; temperature zero, JSON mode, no max_tokens, retries zero. SHA256 deterministic mixed schedule. First scheduled request is the only auth canary and counts normally; subsequent requests use at most 8 workers.

## Mechanical contract

Exactly supported_by / missing / evidence_needed; existing Claim IDs only, unique IDs, nulls paired; otherwise nonempty strings. No semantic entailment automation. Check every scheduled payload, JSON literal, model/endpoint, serialization, prohibited parameters, credential availability without logging, output path uniqueness, complete cross product and input isolation before freeze and again before execution. Exact payload and JSON literal checked before each send. Reject overwrite/resume. Network failures and invalid content remain in denominator; no repair/retry. Contract/access HTTP 400/401/402/403/404/422 halts queued work; concurrent in-flight requests are retained. All planned slots still count. HTTP timeout 240s per inactive I/O operation, not a total billing/token bound.

## First-pass semantic review

Packets hide arm, replicate, qid/state/call ID, H, model reasoning, latency, usage and aggregate metrics. Show only O, unchanged Claims, output, validity/failure and frozen reference. One Codex reviewer; familiarity with reference inputs and inference of H-derived content prevent a claim of perfect blinding. Do not inspect KEY or aggregate until all first-pass labels are written and committed.

Per response record:
- support_correct: entire cited set has no wrong-scope refs, no materially necessary omissions and no strengthening.
- support_refs: one correct/incorrect label and reason per unique citation; micro excludes omitted refs, whole-response does not.
- missing_label: correct / too_downstream / too_upstream / too_broad / too_atomic / already_supported / invented / wrong_object_scope.
- evidence_needed_correct; evidence_level (not a query/site prescription); candidate_specific_unsupported.
- error labels: downstream_jump, target_as_prerequisite, false_requirement, scope_transfer, wrong_referent, over_strengthening, stale_gap; overlapping allowed.
- explicit reason. H_contamination reserved for separate unmasked second pass.

Gold support groups specify material facts: at least one ref per alternative group. Optional anchor refs may locate the exact entity/source, but cannot be credited as proof of an unobserved relation. Other refs need explicit semantic justification. Equivalent/redundant evidence can be accepted if it really supplies the same component. Lack of exact wording or exact gold ref-set identity is not itself an error. Generic symptom overlap is compatibility only. A date calculated arithmetically from O/C is allowed; geography or article existence inferred from outside knowledge is not.

Strict validity requires valid mechanical output AND response support_correct AND missing_label=correct AND evidence_needed_correct AND no false_requirement/downstream_jump/target_as_prerequisite/scope_transfer/wrong_referent/over_strengthening/stale_gap. Thus schema failures are never successful responses. Other failures receive zero success; semantic error rates distinguish observed coded errors from transport failures (failures cannot increase success gates).

Satisfied specificity requires valid output and both gap fields null, denominator all 16 planned satisfied slots per arm. Missing correctness for controls requires no invented gap. Support precision micro is correct cited refs / all cited refs, with ref-less rows not counted as perfectly precise; also report response-level support.

## Replicates and H second pass

After first-pass label commit, inspect same-case same-arm pairs without aggregate metrics. Classify same_gap (same semantic deficit/evidence scope, including both-null), compatible_gap (compatible but substantively different granularity), different_gap. Report raw semantic sameness, plus gate agreement = same_gap AND both missing labels correct AND both evidence_needed_correct AND both schema valid. Two consistently wrong gaps never pass the stability gate. Compatible does not count as same. Strict both / exactly-one / both-invalid reported separately over 27 pairs per arm.

Unmask H only after first-pass commit. H contamination requires actual gap content exclusive to H, absent from O/C, or H-driven narrowing/strengthening. Naming a candidate already in O/C is not contamination. Empty-H G1 cases cannot be H-contaminated. Report contamination independently and do not alter first-pass labels silently. Paired strict comparison over 54 matched case×replicate cells; descriptive only. G1 is an input+instruction ablation, not a pure H-token-only effect.

## Primary absolute engineering gate

G0 must meet all: strict ≥80%; missing ≥85%; whole support ≥85%; satisfied specificity ≥85%; downstream ≤10%; target-as-prerequisite ≤10%; schema ≥95%; semantic replicate agreement as defined above ≥80%. All 54 planned G0 slots and 27 pairs are denominators. No significance claim, optional stopping, best-of, sample replacement or adaptive revision. G1 does not change the G0 gate. Stop after E1 on PASS or FAIL. Q→O, retrieval, Writer, closure and persistent-state changes are forbidden.

## Interpretation and accounting

Report numerator/denominator, all failures, question clustering and small exposed development bank. Prior checker 28/44 distinction and 30/44 whole binding are descriptive comparators only: different output tasks, banks and runtime preclude causal improvement claims. Do not use prior V0's HTTP400 as model accuracy.

Report planned/sent/returned/failures; known prompt/completion/reasoning/cache hit/miss totals; weighted hit/(hit+miss); latency and peak concurrency; missing usage unknown, never zero billed cost. Reasoning is a subset of completion and not added again. No currency claim without validated prices. Frozen score code performs arithmetic only; reviewer supplies semantics.
