# Dynamic Local Obligation Derivation — frozen protocol

## Material Passport and design

User-specified development mechanism experiment. Single Codex reviewer and executor; DeepSeek Flash is the tested model. 27 natural QCH snapshots, 10 exposed question clusters, copied byte-for-byte from the prior study. No fresh, independently sampled or whole-agent performance claim. No model-generated extra state, retrieval, Writer or closure.

O0 receives exactly Q/current C. O1 adds original H (including original nulls) and exactly TASK section16 paragraph. Both return only one nonempty obligation string. Prompts are extracted from TASK sections15/16 without case examples or patches. Two independent responses per state/arm: 108 E1 requests. JSON mode, deepseek-flash, temperature 0, retries 0, omit max_tokens; max8 workers. Deterministic SHA256 schedule interleaves arms/replicates. First scheduled request is the sole auth canary and remains in denominator.

Gold O and Gold Gap are unchanged references, never model inputs in E1. Eight historical Gold O are satisfied controls. They are not legitimate active obligations now: the model may choose a different unresolved objective. Valid alternatives receive equal primary credit. Gold selection agreement must not replace validity. All current Qs retain unresolved constraints even when a local Gold O is satisfied. If a serious reference defect is discovered, quarantine that case, preserve its planned denominator and disclose; never relabel it silently.

## Mechanical contract and failure policy

Only {"obligation":"..."}; no extra keys, tools, Q echo fields, parser/binding fields or STOP. Before freeze and before sends: exact endpoint/model/config, JSON literal, schema test, serialization, 27×2×2 schedule, unique IDs/paths, no token cap, no retries, credential presence without logging, exact Q/C/H projection, no Gold/old Need/Workspace/arm leakage. Existing outputs cause refusal, not resume. Each request is recorded before one HTTP attempt. Raw response/result and missing usage retained. Contract/access/billing HTTP400/401/402/403/404/422 halts queued work; in-flight requests retained. HTTP inactivity timeout240s per operation is not a token/total billing bound. All planned slots stay in denominator; no retries, repair, best-of or sample substitution.

## E1 semantic rubric before Gold comparison

First-pass packets show only Q, Claims, generated O and mechanical validity. Hide arm, replicate, state/case ID, H, Gold O/Gap, historical audits, aggregate, provider reasoning, usage and latency. The same reviewer authored/knows earlier Gold references and cannot erase that familiarity; perfect blindness or reviewer independence is not claimed. Explicit first-pass judgments are committed before KEY/H/Gold comparison or aggregation.

Eight binary dimensions: GoalGrounded, Unresolved, Material, Local, Coherent, ScopeFaithful, NonDownstream, EvidenceResolvable. Strict = all eight AND valid schema. Missing/malformed responses get zero success dimensions, with a mechanical-failure tag rather than invented semantic diagnoses.

Operational boundaries:
- A target identity, event existence or unknown relation is a legitimate output. It need not be established before research. Establish/identify whether a described event exists differs from extracting an attribute of an assumed candidate event.
- A bounded identity objective can keep complementary distinguishing conditions. Do not penalize it merely because it is not logically atomic. Several linked cues do not automatically make a whole-question restatement.
- Reciting essentially all independent Q constraints across separate biographies/events/documents is whole-question/broadness even if wrapped as one final identity. Mere eventual usefulness to the same answer is insufficient coherence. Local may fail while goal grounding/materiality remain true.
- One meaningful dated relation or discriminative identity clue can be local. Mark over_atomic only when the isolated fragment lacks independent research value or drops the context needed to test a substantive Q relation; short length is not an error.
- Claims are accepted as the supplied verified evidence. Asking again for exactly an established fact is stale even if worded as verification. A new Q-required qualifier not established in C can make a genuinely different unresolved target.
- Named candidates already in C may be tested directly on an unverified Q clue. Do not assume a candidate satisfies other unverified Q conditions, or silently hardwire a provisional candidate into an unconditional downstream relation. A name being unknown in C does not forbid generic entity discovery.
- A question-described variable may remain unnamed when the obligation identifies it from its local clue. A dependent attribute request needs an established concrete referent/event or an explicit identifying/existence objective.
- Maintain actual role/date/object/argument scope. A relation between two other entities is not equality with a third salient entity. A covering-document date is not the enclosed object's date.
- EvidenceResolvable assesses whether a real evidence type could settle the stated objective, separately from whether it is relevant, well-scoped or stale. Scope errors need not make the statement intrinsically unverifiable.
- Minimal schema plus no search query, source prescription, plan, confidence or rationale as output. Wording such as identify/establish is an objective, not itself an action plan.

Errors (overlapping): downstream_obligation, already_supported, whole_question_restatement, over_atomic, invented_requirement, wrong_object_scope, wrong_relation_arguments, relation_strengthening, irrelevant_low_value, unresolved_referent, bundled_objectives, outside_knowledge, output_contract, mechanical_failure. H_contamination is a second-pass label only. Report wrong_relation_arguments specifically for historical G23 (F15_S01) and its question cluster, without prompt patches.

## Post-first-pass comparison and E1 gate

After committed first-pass judgments, classify valid O as gold_equivalent or alternate_valid; invalid remains invalid even if text resembles Gold. Semantic equivalence, not exact text, is the rule. Satisfied Gold equivalents cannot be strict-valid because Unresolved fails. Record H-exclusive content/provisional relations separately; candidate names already in Q/C are not automatically H contamination. Report O0 better/O1 better/tie over 54 matched case×replicate pairs; this is input+instruction ablation with repeated, clustered data.

Pairs: same_obligation (both valid, semantically same), compatible_obligation (both valid, same bounded objective with compatible differences), different_but_valid (both valid but distinct independent objectives), one_valid_one_invalid, both_invalid. If outputs repeat the same wrong objective, both_invalid. Primary stable_both_valid counts same+compatible only, denominator27. Report raw both-valid separately; legitimate target diversity is not a strict-validity error but does not establish stable selection.

O0 must satisfy ALL: strict≥80%; GoalGrounded≥90%; Unresolved≥90%; ScopeFaithful≥90%; NonDownstream≥90%; whole-question/broadness≤10% (union whole_question_restatement or bundled_objectives); wrong_relation_arguments≤5%; schema≥95%; stable_both_valid≥80%. Planned response denominator54; pair denominator27. Engineering gates, no p-value/significance claim. O1 cannot rescue a failed O0. On E1 FAIL stop; no revision, E2 calls, Gold editing or acquisition.

## Gated E2 design (not execution authorization without E1 PASS)

If E1 passes, fixed Dynamic O is always O0 replicate1. Invalid/missing rep1 causes direct Dynamic path failure; no rep2 substitution. All27 states remain end-to-end denominator (54 gap-replicate slots). Skip paid Gap requests for invalid O, recording structural O failures in both planned Dynamic slots. Oracle is all27 historical Gold O, two replicates each. Thus at most108 E2 calls, at most216 total. Skipped dynamic slots are never removed or replaced.

Before any E2 call, create/commit Dynamic-O reference gaps using only Q/current C/dynamic O. Gold-equivalent may inherit frozen reference; alternate-valid needs its own support groups, missing, evidence signature and ambiguity. References exclude future results, outside knowledge and original H. If a serious Gold error is discovered quarantine it explicitly; no post-hoc alteration.

Oracle and Dynamic use exactly the prior g0_gap_no_h.txt bytes, same endpoint/model/config and current C, in the same execution window with mixed schedule, two gap replicates. No Q/H in Gap inputs. Separate E2 freeze covers references, prompts, schedule, schema, rubric, denominator, preflight and code. Gap review mirrors prior support/missing/evidence rubric and uses arm/replicate-masked packets with O/C/reference; first-pass labels committed before aggregation.

Report Oracle strict /54; Dynamic strict conditional on valid O /(2×valid rep1 states); Dynamic end-to-end strict /54. Loss = Oracle strict minus Dynamic end-to-end in percentage points, descriptive, not an exact causal decomposition: alternate O and satisfied historical Gold have different target difficulty. Report failure due to O, Gap given valid O, and state/replicate overlap with Oracle failure. No claims about Gap failure on skipped invalid-O paths.

E2 gate: Oracle≥80%, Dynamic|valid O≥80%, Dynamic end-to-end≥75%, loss≤15pp. Freeze 'no explosion' as BOTH downstream and target-as-prerequisite conditional Dynamic rates≤10% AND increase versus Oracle≤5pp; failures do not get semantic error labels by default. No undefined qualitative gate after results. Stop after E2 PASS or FAIL. Only a future independent fresh confirmation may be suggested.

## Cost and interpretation

Earlier API authorization persists, bounded to these gated calls. Credentials alone are not the authorization. No unverified currency pricing; report prompt/completion/reasoning/cache totals, weighted hit/(hit+miss), latency, peak concurrency, unknown usage and all failures. Reasoning belongs inside completion. Historical 65,535-token tail is a scenario, not a hard limit with max_tokens omitted.

The previous 92.6% Gold-Gap aggregate included easy empty-C and satisfied controls; partial-support strict was71.4%. Carry this limit forward. Both state/question clustering and single-reviewer judgment limit reliability claims. No new persistent semantics or claim of closed-loop success follows from either gate.
