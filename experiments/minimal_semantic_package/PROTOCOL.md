# Minimal Semantic Package / Scoped Partial Evaluation

## Material Passport

User-directed code mechanism experiment, base01895c849a064e9659f121fd05c9af3d4f23bf85,
branch `experiment/minimal-semantic-package`. All previous experiments remain
immutable. Single task-familiar Codex reference author; no independent-review
claim. The academic-research-suite experiment workflow is applied inline.
The user's experiment implementation request supplies authority to prepare
code/artifacts; TASK33 explicitly withholds paid execution until fresh approval.

## Research contract

Separate boundary recovery, verification of a fixed target, and conservative
partial evaluation. Persistent authority remains Q/R/C/H, H unused. Locator,
units, packages, support certificates and residual views are ephemeral. Original
Parent never changes. No Search, Query, Probe, Find/Open, Writer, rollout,
persistent graph or fine Requirement tree is added, even if E4 eventually passes.

Run in order: E0 → E1 Gold Package Support → E2 Package Recovery → E3 Predicted
Package Support → E4 Gold Support Residual View. A stage FAIL stops all later
stages. Each paid batch also requires its own new user authorization after exact
requests have been committed and hash-frozen. No old authorization is reused.

## E0

Keep all48 historical certificates and identical selected Claims. Use24 cells,
16 natural snapshots,9 qids. Collapse Q/Parent/Locator duplicates to17 Parents
and34 unique packages. Freeze78 ordered exact source spans, ID sets and source
hashes before constructing new support labels. The builder reads no Claims;
the human-equivalent reviewer is nevertheless familiar with past material.

The [boundary policy](e0_reference/BOUNDARY_POLICY.md) defines roles and sibling
boundaries. There are21 SUPPORTED and27 OPEN references. One old positive,
A24_CAND2, becomes OPEN under the newly explicit author-country target: its
selected C2/C3 omit that relation. This is a new reference under a new target
contract; the old result is not rewritten. Four ambiguous references are marked
before calls. They stay in primary denominators; exclusion is descriptive only.

Support annotations also enumerate minimal sufficient subsets of each supplied
ClaimSet. Any supplied superset of a listed sufficient subset is acceptable.
For example, C2 suffices for two-author support in the C1+C2 certificate, and
C2+C5 or C4+C5 can bind the observed paper/table for the triple certificate.
Ding C5 already names the candidate and gives2019 marriage/childlessness; C4
need not be cited again for a target that contains no founder predicate.

These witness labels assess the semantic sufficiency of cited evidence. They
do not turn every binding member into standalone substantive support. Gold
missing-unit anchors identify material gaps, not an exhaustive mandatory model
explanation or extra runtime instructions.

## E1 exact inputs and design

48 certificates ×2 replicates = **96 Verifier requests**. Every payload contains
only TARGET exact units, INTERPRETIVE CONTEXT exact units and the original
selected ClaimSet. No full Q/Parent, locator, siblings, Gold explanation,
certificate/category identifiers or correctness labels reach the provider.

The verifier system prompt is exactly the task's section10 text block. It may
return SUPPORTED or OPEN, cited Claim IDs and uncovered Target IDs. IDs must be
unique and exist in the actual payload. SUPPORTED requires at least one Claim
ID and no uncovered units; OPEN requires at least one uncovered Target unit.
Context/sibling IDs cannot masquerade as uncovered Target IDs. Extra fields,
unknown IDs, invalid JSON, missing content, wrong model, non-stop finish and
transport failures remain failed planned slots. No schema repair.

For each schema-valid SUPPORTED response, instantiate exactly one separate
Uncovered Material Auditor call using section11's prompt and the **cited subset**
only. The auditor sees the same target/context but not the original larger
ClaimSet, prior verdict, selected uncovered list or reasoning. An auditor is a
separate reverse-task call, not an independent model/error process and not a
vote. An OPEN or invalid verifier response has no auditor call.

The harness accepts QUALIFIED_SUPPORT only when the verifier is valid SUPPORTED
and a valid auditor reports an empty uncovered list. Auditor failure leaves a
failed/open control outcome; it is never silently treated as an empty list.

## Dependent requests and new approvals

The exact auditor requests cannot exist before the verifier chooses its Claim
IDs. Freeze the compiler and both prompts now, but do not invent future outputs
or substitute the full ClaimSet to manufacture a fixed count.

1. Prepare/commit/hash96 actual E1V requests; ask new authorization for **96 only**.
2. After E1V completes, preserve and commit all responses, including failures.
3. Materialize0–96 actual E1A requests from valid SUPPORTED results only.
4. Commit/hash that exact request list, state its exact count, and ask new E1A
   authorization. If there are zero required auditors, no call/approval is needed.
5. Only after every required auditor outcome is preserved may E1 receive a final
   PASS/FAIL decision. No intermediate Verifier-only score authorizes E2.

Total E1 calls are96–192, but the present concrete authorization request is only
96. Monetary/output-token cost is unknown; estimates are not spending caps.
E2/E3/E4 require their own concrete reference/request freeze and fresh approvals.

## Provider and failure policy

DeepSeek `deepseek-flash`, `https://api.deepseek.com/chat/completions`, temperature0,
JSON mode, max_tokens omitted as in the prior backend, max_retries0, at most8
concurrent independent requests. Inherited240-second HTTP inactivity timeout,
not a total wall deadline. No new backend/model, smoke call or credential print.

HTTP400/401/402/403/404/422 halts new sends; in-flight work finishes. Preserve all
timeouts, schema failures, halted-unsent slots and interrupted send intents.
Exclusive files disallow overwrites or automatic resume. No retry, repair,
best-of, majority vote, prompt hot-fix or failed-case replacement. Do not edit
the frozen prompts/Gold after observing outputs.

## E1 primary scoring and gates

Unit: Certificate × replicate.42 positive and54 negative planned Verifier slots.
All96 remain denominators, including failures. No pooling as independent qids.

Primary Support Precision concerns an accepted **support certificate including
its cited witness**: TP is QUALIFIED_SUPPORT with positive target Gold and a
sufficient cited ClaimSet. FP is any other QUALIFIED_SUPPORT. Accepting the right
target using an insufficient cited subset is an unsafe certificate even when
the original larger input contained sufficient evidence. Report a separate
Verifier-only verdict metric to make this distinction visible.

Recall=TP/all42 Gold positive slots. A positive with insufficient cited witness
is missed support. False OPEN counts valid chains ending OPEN on a Gold positive;
failed chains are reported separately and still lower Recall/schema. The
primary schema rate is valid decisions along the required call path /96;
also report per-component request schema rates.

Uncovered-audit rescue counts an unsafe Verifier support changed to OPEN by a
valid nonempty audit / all unsafe Verifier supports. Auditor failures are not
rescues. Also count previously safe positive supports incorrectly rejected by
the auditor. This prevents portraying indiscriminate rejection as an improvement.

False-full-risk is acceptance of one of14 frozen risk negatives (28 slots),
including new A24_CAND2. It is a potential control hazard, not an observed E4
False FULLY_SUPPORTED. The clinical metric uses3 certificates ×2=6 slots; Ding
uses1×2=2. The requested90% and100% thresholds both require all their slots
correctly supported in this small bank. Euler and book-only each have2 slots.

Gate: Precision≥97%, Recall≥90%, Euler false support0, book-only false support0,
false-full-risk0, clinical Recall≥90%, Ding Recall100%, schema≥95%. Every clause
must pass. A required null metric cannot pass. Gate remains PENDING until all
required auditor outcomes are retained. Replicate stability requires two valid
chains with matching final decisions; failures never disappear from its48-pair
denominator. No majority decision.

Report raw Verifier and final audited performance, paired audit effects, all
required bad cases, both replicates, ambiguity sensitivity and per-question
strata. Do not directly compare new witness-certificate Precision with old
Claim-role Precision. Reuse old Q0/Q1 only as descriptive baselines, on visibly
different input contracts/references; do not resample them.

## Review and integrity

Freeze Gold before corresponding model calls. Semantic review uses content
outputs and supplied Claims/units only, never provider reasoning. Reasoning may
remain in raw response archives but is excluded from review packets and parsing.
Review may disclose reference disagreements; it cannot relabel primary Gold.
Report the one old-to-new label change before any new output exists.

Verify all historical tracked experiment files by SHA. After execution, reparse
raw responses, replay scores and usage accounting, and verify frozen inputs.
Cache rate=sum reported cache-hit tokens / sum input tokens over complete,
consistent counters; disclose missing usage and exclusions. Output reasoning
tokens are a subset of output, not an additive second output count.

## Conditional later stages

E2 uses34 unique Q/Parent/Locator packages, no Claims, with two replicates. B1
begins from the corresponding B0 response, adds source IDs from the missing-
context audit, then performs sequential leave-one-out pruning so individually
redundant alternatives are not all removed in parallel. Packages preserve source
order and cannot paraphrase; UNITIZATION_INSUFFICIENT is a recorded abstention.
Actual dependent requests require later freezes/approvals. No E2 implementation
or call is triggered on E1 failure.

E3 uses the B1 package in the unchanged E1 verifier/auditor interface; source IDs
and evidence are the only data replacement. It is conditional on E2 PASS.

E4 is conditional on E3 PASS and begins with Gold support. Before its calls,
freeze references for known bindings, still-missing obligations and valid
derived constraints across actual historical progressive states. Book2016 may
be an evidence-backed value binding without proving the later article relation;
the latter stays unresolved while the expected publication year becomes2022.
Separate directly verified bindings from qualified target discharge. Parent
text remains unchanged. No E4 result or reference is fabricated in preparation.

All18 requested final questions will be answered with measured evidence or
explicitly “unmeasured due to gate/authorization.” Even E4 PASS cannot authorize
a dynamic closed loop in this task.
