# Claim–Requirement Support Alignment

## Material Passport

Artifact: preregistered code experiment. Status: E0 complete; E1 prepared, not executed. Source: user TASK.md; baseline fc799239d41e0abd6b8306cc09f9e3b7a2126586. Natural-state provenance, limitations and reviewer disclosure are in e0_reference/BANK_REPORT.md. This is mechanism diagnosis on familiar cases, not independent generalization confirmation.

## Research question and intervention

Given original Q, one fixed source-anchored D2 Parent R, and the complete nonempty current Verified Claims C, distinguish substantive support from candidate binding/background/irrelevance. Support scope remains an ephemeral output/evaluation annotation; no persistent representation is changed. The only E1 intervention is the binary S0 versus typed/scoped S1 system prompt. User payload is byte-identical within each cell across arms/replicates. Task-supplied system prompts are copied verbatim from sections17/19. No H, source audit, history, Gold labels, accepted fragments, old predictions or retrieval is in the model input.

## E0

Selection was committed at df671a2b before new role annotation; Gold was committed at d0e51d05 before E1 preparation. Selection SHA and GOLD_FREEZE record the precise bytes and parent commit. Repeated cells may share a snapshot/question; 24 cells are not 24 independent questions. All 82 cell×Claim references are fixed, including ambiguous cases. See BANK_REPORT for boundary decisions. Question facts specify obligations; they are not observations. Claims are the entire available evidence, even if a historical source contains more.

## E1 requests and execution

24 cells × 2 arms × 2 replicates = **96 actual frozen requests**. Model deepseek-flash at configured DeepSeek endpoint, temperature0, JSON mode, no max_tokens field, no tools, retries0. Thread pool at most8; independent requests may execute concurrently. Arm order balanced deterministically across cell/replicate. Replicates measure instability, not best-of; neither is selected or repaired.

TASK20 requires a new explicit user approval after requests are frozen, committed and actual count reported. Before approval there is no credentialed connectivity test or paid call. AUTHORIZATION_E1.json will record the actual new user message, timestamp, stage, maximum96 attempts, task SHA and FREEZE SHA; it must be committed. The runner refuses to execute without it. E2 is excluded from this authorization.

Preserve request, send intent, raw response, parsed content, finish reason, model identifier, usage, latency and failure for every slot. HTTP transport retries0; redirects disabled; 240-second HTTP inactivity timeout (not a total wall deadline). No retry/resume/overwrite after a crash. Infrastructure HTTP400/401/402/403/404/422 halts queued sends; other returned HTTP errors and timeouts remain per-slot failures. Already running requests finish. A caught interruption fills unstarted slots explicitly. An uncaught termination leaves durable attempt records; load_rows reconstructs missing slots as failures. No missing usage is treated as proof of zero spend. Cache hit rate is token-weighted, with reporting coverage and hit+miss consistency; raw counters remain available.

## Contract and failures

S0: only support_claim_ids, a list of unique observed IDs. S1: only claims; every observed Claim exactly once, known role, exact required fields. Support requires a nonempty unique list of nonempty exact Parent substrings; non-support requires []. Unknown/missing/duplicate IDs, extra fields, paraphrased fragments or malformed JSON invalidate the whole assignment. Do not repair. Truncation, non-stop finish, wrong returned model, transport errors and empty output also invalidate it.

All96 slots remain in planned denominators. Invalid/missing assignments emit no usable support: all true support in that slot is missed, exact-set fails even when Gold is empty, and schema fails. They cannot create a real accepted false-support packet. Precision is TP/accepted predicted support; recall TP/all Gold Claim-slots; promotion FP/all Gold non-support Claim-slots. Report failures alongside safety metrics so an empty failed batch cannot be called safe. A zero denominator returns null and fails the corresponding gate, not 100%.

## E1 semantic review

Export masked PACKETS and a separate KEY only after calls. Packets contain Q/R/current Claims, content-only output and schema status. No arm/replicate/cell label, provider reasoning, latency or packet origin is shown. Output structure can reveal arm; report this limitation. Codex may act as one task-familiar reviewer, without claiming independent error processes. Perform semantic first pass without KEY, seal JUDGMENTS and PACKETS before unmasking/aggregation. Gold ambiguity never justifies post-hoc primary relabeling.

Judgment fields: scope_correct_claim_ids; relation_argument_corruption; candidate_branch_mixing; false_full_support_hazard (null for S0); error_tags; reason; ambiguous_reference. Scope is correct only if the entire fragment set expresses the supported material part, is adequate and minimal, and preserves referent/arguments/time/source. Equivalent exact spans are accepted semantically; equality to one Gold string is not required. Tiny uninformative substrings do not earn scope credit. Declared joint support is evaluated with its frozen prerequisite Claims; an absent operand cannot be imported. False support receives an appropriate task taxonomy tag even when lexical fragments are exact.

False-full hazard is a semantic check that the S1 fragments taken together purport to cover all material Parent conditions despite Gold unresolved content. A single true partial-support Claim is not automatically a closure. If the output copies the whole Parent for clinical-only C7, it is a hazard. S0 gives no scope/closure claim: report its hazard as unidentifiable, never equate selection of a Claim with fully-supported. E2 measures actual false closure separately.

## E1 metrics and gate

Primary micro metrics: support precision/recall, promotion among all Gold non-support (plus Z-only diagnostic), scope correctness among correctly selected support Claim-slots, relation/object/time corruption per planned output, branch mixing per planned output, false-full hazard count, and schema validity. Secondary: exact state support sets, role confusion/accuracy, binding recall, background accuracy, fragment lexical validity (all supplied support fragments, including invalid outputs) and semantic scope. Manual error tags count outputs; automatic missed/promoted errors count Claims, in separate fields. Report each replicate, qid and Z/P/F stratum; nonambiguous sensitivity is additional, never a gate replacement.

Numerical thresholds are in GATES.json. Near zero is preregistered as both arms' promotion rates <=5%; use S1<=S0 there, otherwise strict S1<S0. S0 need not pass. Safety entry to E2 requires **all S1 absolute thresholds except recall**: precision95%, promotion<=5%, scope90%, corruption<=3%, mixing<=2%, zero false-full, schema95%. Recall-only failure may enter diagnostic E2 (TASK24C/25); unsafe support/scope failure stops. Comparative performance cannot override an unsafe absolute result. Review must be complete and sealed. E2 must be separately authorized after actual dependent requests are prepared and committed.

## Conditional E2 design (not executed or authorized)

Use the same24 cells. Four arms × two matched replicates, at most192 model requests. D0 receives raw Claims and internally decides support. D1 receives the matching S0 replicate's accepted support Claims only, marked SUBSTANTIVE SUPPORT. D2 receives the matching S1 replicate's support/binding/background Claims; irrelevant omitted. D3 receives frozen Gold typed Claims. Neither predicted nor Gold scope fragments/reasons/full-support flags enter any E2 payload. A failed S0/S1 contract blocks its matched D1/D2 slot, stays in the planned denominator and is never replaced by Gold, another replicate or a repair. D0/D3 remain scheduled. After E1, report exact unblocked send count and192 planned outcome slots separately.

All E2 arms receive the same Parent; Original Q is uniformly omitted to follow TASK27/28's specified R+evidence interface. Source-anchored Parent text itself is unchanged. D1/D2/D3 use exactly TASK28 prompt. Because that prompt requires explicitly marked support but D0 explicitly supplies raw Claims, D0 alone appends the preregistered D0_ADAPTER allowing internal identification before applying the same subtraction rules. This necessary baseline adapter is disclosed; D2 versus D3 has exactly the same prompt/interface and differs only in typed assignment. D0 is a diagnostic comparison, not a perfectly single-factor packet-only contrast.

E2 actual requests cannot be frozen before E1 outputs exist. Stage-specific runner/review/seal/accounting will be bound by a separate E2 freeze and approval; this initial freeze fixes the design and pure payload builder. No E2 network command is enabled yet.

## E2 review and scoring rubric

Use content-only masked output packets, full current Claims and fixed Parent for evaluation, without origin/arm/replicate/provider reasoning. Strict requires all: faithful coverage of every Gold unresolved material condition; correct subtraction; no false subtraction; no supported-content leakage; no downstream jump/query/probe; preserved participant/relation/object/ownership/source/time/branch. Fully-supported is valid only for F. A known fact retained merely as necessary referent/locator is not leakage; asking to establish it again is. Z requires the entire Parent semantics still unresolved, not one convenient facet. The frozen SUPPORT_SCOPE_REFERENCE unresolved notes are evaluation-only guides, not canonical residual wording.

False subtraction: any unresolved material condition lost; false FULLY_SUPPORTED: any non-F closed. Keep both output counts/planned-denominator rates and observed valid-output rates. Missing/invalid outputs fail strict/schema/full-support accuracy and cannot pass state discrimination. For D3: strict>=90%, false subtraction<=3%, false-full=0. D2: strict>=85%, D3−D2<=10 percentage points, false subtraction<=5%, false-full=0, leakage<=5%, discrimination>=80%, schema>=95%.

Primary state discrimination has two frozen pairs × two matched replicates per arm =4 opportunities: A05→A07 and A16→A17. Credit requires both endpoints strict and the correct semantic change from newly supported content; text variation is insufficient. With this small denominator80% requires4/4. Stable negative pairs are secondary invariance checks. Do not add favorable transition pairs after output inspection.

## Interpretation and stopping

Report support safety before overall role accuracy. S1 safe+recall low diagnoses conservatism; unsafe S1 stops before E2. If D3 passes but D2 fails, distinguish wrong alignment versus lost binding at the interface. D3 failure is evidence against stable coarse-Parent residualization on this bank, not by itself proof that a new persistent representation is required. No final claims before observed results.

Even if E1/E2 pass, stop. Search, Query, Probe, Find/Open, Writer, NoGain, Bootstrap, short/full loop, new state fields or persistent subrequirements are outside this task. All historical experiments remain read-only and SHA checked.
