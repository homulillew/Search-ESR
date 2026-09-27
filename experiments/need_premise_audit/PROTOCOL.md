# Ephemeral Premise Audit / Need Type Checker — protocol

## Material Passport

Code experiment, single-reviewer prefix-only semantic reference and response review. User TASK is the governing authority. Persistent semantics remain Q+C+H. E0 and all E1 inputs/rules/code are committed before paid calls. Old experiments are read-only. No external factual research, gold, future trajectories or source audits are used in semantic labeling.

## E0 selection and interpretation

Take every B0 instance with historical P or A in the two frozen minimal_need_multiquery runs. Equal strict-valid controls are sampled by ascending SHA256(UTF8(state_id + run_id)) **within H/No-H strata**, matching the error group's counts exactly. No favorable semantic hand-selection.22 candidate instances:11 errors and11 controls,12 states,7 qids; each group10H/1No-H. One pure-W B0 instance is excluded. Exact duplicated Needs across runs remain distinct historical candidate instances, not independent questions.

Claim IDs are deterministic C1…Cn in unchanged historical statement order. No new claims or H changes. E0 reviewer knows the historical labels; this is a reference construction, not independent adjudication. All22 audits contain target, subject, required background, anchors, decision, repair target, ambiguity and reason. B# identifiers are annotation-only and never sent to models.

An unresolved target is legal. Subject status `grounded` means adequately identifiable **for this question form**: a Q-described discovery target can be grounded as a description without a concrete discovered answer. Named entities/provisional candidates can be directly tested without establishing their satisfaction of Q. Attribute questions cannot import a candidate event/date/role from H. Lift an unsupported relation/event around a known candidate; discover an unbound source/referent. When both mechanisms overlap, use the narrowest local unsupported relation if one is identifiable; otherwise discover the subject. Do not require solving every original condition first.

The strict reference interpretation marks unidentified book/report/accident/letter attribute tests as discover_subject. Medium-ambiguity alternative discovery readings, plus initial-handoff versus final-courier binding, are recorded before calls. Primary labels will not be changed to fit responses. Report sensitivity excluding all medium/high-ambiguity candidate instances; do not use sensitivity to override a failed primary gate.

## E1 computation isolation

Candidate generation is not called.22 fixed candidates ×2 verifier arms ×2 independent responses = **88** scheduled requests. V0 and V1 prompts are exact text extracted from TASK §§16/17. Same Q, ordered claims with IDs, H and exact Candidate Need in both arms. No historical labels, reference audits, previous outputs or other replicate outputs are model-visible. Requests differ only by system prompt; replicates use identical payloads. Schedule order is deterministic SHA256 of a fixed salt and job ID, interleaving arms/replicates. No best-of, repair, tools or Writer.

Provider/config are frozen separately. Temperature0 is not assumed deterministic. Zero retries at client and semantic levels. max_tokens/max_completion_tokens omitted. First scheduled replicate is the formal authentication preflight; no extra probe. After401/402/403, unsent jobs are blocked; in-flight requests are retained. Unknown transport cost remains unknown. All88 slots stay in denominator after failures. Existing run/call files prevent restart or implicit resume.

## Schema and support checks

Exact output keys/types and enums are checked. Every ref in any slot must be Q or an existing Claim ID in that candidate. H, memory, nonexistent IDs, URLs and titles fail schema. Parsed schema-invalid content remains archived and receives no successful semantic credit. An existing ref is not evidence of entailment. No deterministic checker attempts to adjudicate factual support.

Review all responses in a frozen hash order, without aggregate arm metrics or replicate identity. Output schemas expose which verifier is being read, so the review is **not arm-blind**. Reviewer familiarity with E0 is disclosed. Model hidden reasoning is archived but excluded from semantic scoring, which uses the submitted output and QCH/reference. Complete all semantic review before aggregating/gating. No reference revision, retries or prompt sweeps follow results.

## E1 metrics and denominators

- Binary invalid recall: non-keep valid output among11 reference-invalid candidates ×2 =22 slots. Specificity: keep valid output among11 controls ×2 =22. Failures are incorrect in either stratum. Balanced accuracy is the arithmetic mean; report each replicate, H/No-H, candidate, qid, and valid-output-conditional results separately.
- Final decision accuracy: V1 exact keep/lift_premise/discover_subject versus reference; V0 binary decision versus reference keep/non-keep.
- Replicate agreement: both outputs schema-valid and exactly same decision, divided by22 pairs. Two identical failures are not agreement. Also report binary agreement. Never pick a better replicate.
- Target identification: semantic identification of the actual questioned relation/property. Target/premise distinction: target correct **and** no target-as-required-proof error. Planned44 V1 responses form both denominators.
- Subject-status accuracy: semantic reference classification; report separately from decision and distinction.
- Required-background recall: reference B# items semantically covered by returned background items / total reference items across planned responses. Precision: legitimate background items / returned items on valid outputs. Extra legitimate background may have no B# match; invented prerequisites and targets promoted to background are false premises. Also report unsupported-background detection with correct unsupported status. Subject-field recognition of an unresolved referent contributes to binary detection even when the same gap is not redundantly listed in required_background; background-only recall must be interpreted accordingly.
- **Primary support-binding accuracy is response-level**: all submitted subject/background binding slots semantically correct, divided by all44 V1 slots. Each supported fact requires at least one entailing ref; all cited refs must support the asserted scope/object/role/date. An unsupported fact must not be presented as established by Q/C. Unresolved-subject refs may ground its description/known part without falsely proving identity. Also report micro slot accuracy so long lists cannot hide response-level failures. Missing background is measured by recall; a correct decision does not make an incorrect anchor valid.
- Error taxonomy: missed_premise, target_premise_confusion, false_premise, wrong_anchor, subject_error, and target_identification_error. Execution failure has unknown semantics, not fabricated semantic labels.

### Frozen E1 gate (all conjunctive, no rounded comparisons)

V1 recall≥85% (≥19/22); specificity≥85% (≥19/22); response-level all-binding accuracy≥85% (≥38/44); target/premise distinction≥85% (≥38/44); exact decision replicate agreement≥80% (≥18/22); schema-valid complete output≥95% in **each** arm (≥42/44); V1 balanced accuracy≥V0. Schema-valid complete output is the stricter operational form of TASK's valid-JSON gate. Report syntax and schema validity separately.

If any fails: **STOP E1**, no E2/E3 and no revision. If passes but V0 is similar, E2 is permitted only as repair-utility diagnosis; explicit decomposition is not yet proven superior to generic second-pass verification. Descriptive differences on exposed clustered cases are not independent-qid significance evidence.

## E2 only after E1 PASS

22 candidates ×2 audit-source arms, one repair response each =44 calls, same supplied repair prompt. Model source uses **V1 replicate1**, never best-of. Invalid replicate1 blocks its dependent repair and remains failed in the22-slot model-pipeline denominator; no substitution from replicate2. Oracle source projects the E0 reference into exactly V1's target/subject/background/decision schema, excluding B# IDs, repair_target, reasons and labels. It must not provide a ready-made repaired Need. Freeze model and oracle audit inputs and request schedules in a new commit before calls.

Keep must return the exact Candidate Need byte-for-byte as its `need` value. Other operations only lift the implicated relation or discover the needed subject, retaining locality. Semantic review: original six strict dimensions plus operation, locality, new P/A/W/stale and paired gain/regression. Gate: model final strict≥80%, invalid repairs≥70%, control preservation≥90%, gains>regressions, objective drift≤5%; oracle strict≥85%. All planned slots count; no downstream stage if either required gate fails.

## E3 only after E1 and E2 PASS

12–15 untouched qids /30–40 **archived natural** QCH; exclude current and all previous Need-development/confirmation/review-exposed qids. No new retrieval, Writer or fabricated claims to manufacture states. First exact original B0 makes one Candidate Need per state, then freeze it before V1→repair. Separately freeze all later request batches. If suitable archived states cannot be established, record unavailable; do not violate this task's no-tools scope to acquire them.

Fresh gate: final strict≥80%, P/A union≤5%, net paired gain≥15 percentage points of all states, valid-candidate regression≤10%, complete valid output≥95%. Also report conservative P+A sum and No-H. Failures from generation/check/repair stay in end-to-end denominators.30–40 states are not a large-cohort efficacy claim. Stop after E3 even if successful; no Multi-Query/retrieval/Closure/loop.

## Accounting and scope

Before requests, record planned counts, approximate prompt tokens, all108 previous completion-token distribution and the65535-token observed tail scenario. This is not a guaranteed cost maximum when max_tokens is omitted. Every response's raw usage/cache hit/cache miss is retained; report weighted hit/(hit+miss), reasoning as a component of completion, missing fields and latency/concurrency. No monetary estimate without verified pricing. No external price lookup is needed to execute this bounded user-authorized task.

Freeze task, selection, references, historical/source hashes, prompts, schemas/code, metrics, gates, sample counts, replicates, failure policy and provider. Record actual execution HEAD before sending. Preserve original experiments and all new failed outputs. Final conclusion answers the fifteen TASK questions and distinguishes observed findings, reviewer judgments, hypotheses and unmeasured stages.
