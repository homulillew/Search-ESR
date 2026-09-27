# Skeleton–Claims Alignment / Plan–State Reconciliation

## Material Passport

Repository experiment; source branch `experiment/ephemeral-obligation-decomposition`
at7fdb048e856545facd4acfb590e8cf28c46f1013. Inputs:27 historical natural Claims
states,10 questions, fixed prior D1/D2 replicate1. Data are exposed development
material. Single Codex semantic reviewer; no human participant study. User task
TASK.md is the authoritative specification. Status: PREPARED_FOR_EXECUTION.

## Order and isolation

1. Fetch/inspect remote, create `experiment/skeleton-state-alignment`.
2. Build source-anchored Oracle only from Q and prior frozen Q-only reference;
   commit81caa52 before opening historical Claims/GoldO in this construction.
3. Whitelist current Q/Claims for all27 states. Manually freeze54 Gold Masks at
   commit4b8e9d8 before opening GoldO. Read only each current state for its label;
   later states never supply missing evidence to earlier labels.
4. Audit historical GoldO against D1/D2, then freeze all control references,
   prompts, schemas, gates, mixed schedules, rubric, code, hashes and tests.
5. TASK §70 requires new applicable paid authorization. Credential presence,
   offline preflight and previous budgets are not authorization. No live canary
   or API call before that authorization is recorded against FREEZE.json.
6. Run108 E1 slots. Commit masked first-pass judgments before aggregation.
7. Only A0 AND A1 PASS permits E2. Materialize S1 requests from A1 replicate1,
   freeze/commit actual request bytes and source hashes, then run108 E2 slots
   within the approved budget. Invalid A1 replicate1 blocks its two S1 slots.
8. Stop after E2, even if successful. No acquisition, Gap, Writer or rollout.

## E0 and reference granularity

Four classes: directly_addressable, coherently_multi_addressable, subnode_only,
not_addressable. D1 prose plus source provenance is diagnostic; D2 source spans
are primary. At most four tightly connected nodes may form a coherent episode.
All27 material historical targets are critical for the not-addressable rate.
Below80% direct+coherent or above10% critical-not-addressable warns but does not
stop E1. Primary D2 remains prior replicate1 in original node order.

Selection is existential, not GoldO matching. Subnode-only for a narrow old
LocalO does not disqualify an otherwise local whole-node discovery episode.
Independent residual objectives still bundled in a node can disqualify it.
G04/G05 have no admissible single D2 ID under the frozen locality interpretation;
keep both in the27-state denominator. The ideal-reference selection ceiling is
25/27 (92.59%), and STOP is not a fallback for unaddressability.

## Inputs and responses

E1: Q + fixed Skeleton + current Verified Claims, exactly the three whitelisted
fields. E1 system text is byte-equivalent after newline normalization to TASK
§28 fenced prompt. Oracle labels are descriptive only; source spans govern.
No hypothesis, GoldO, review label, reference mask, trajectory, final answer,
Delta/Path/H/Workspace, arm or replicate enters an E1 payload.

E2: Q + the same Runtime D2 + current Coverage Mask. Both arms project masks
identically to ordered requirement_id/status pairs. Citation IDs and claim
texts are absent; the selector receives coverage information only. Gold's
evaluation-only proof groups/reasons are never exposed. S1 always uses A1
replicate1, never best-of or fallback. System prompt is TASK §52 unchanged.

Residual is mechanically the set of non-fully-supported IDs. Invalid model
outputs have no usable mask: do not silently convert them to all unsupported.
Only one response per scheduled slot, no tools, no natural-language LocalO.

## Gold semantics and support proof

Only current Claims have epistemic authority. Q requirements are not facts.
F means all material node conditions; P a substantive proper part; U no such
part. Generic related biography, name overlap and unbound candidate mention do
not count as P. See GOLD_CONSTRUCTION.md for binding and ambiguity conventions.
Local direct relations can bind a candidate without all other Q clues being
verified; this gives pointwise node coverage, not global candidate certification.
No within-node full proof may combine properties of different candidates.

For F, at least one acceptable_full_support_group must be included in the
citation set. Extra irrelevant citations reduce precision, not sufficiency.
For P, at least one acceptable_partial_support_group must be included and Gold
must be P. The complete current Claims resolve antecedents; proof sufficiency
is contextual. reference_binding_context explicitly records such antecedents.
Strict-citation-context sensitivity asks whether those were also cited.
Contributing Claim sets need not exactly match returned citation sets.

## Denominators and gates

All54 planned responses per arm remain in primary denominators. E1 counts322
planned Oracle node cells and264 D2 node cells, two replicates over27 states.
NodeStatusAccuracy is micro over planned nodes; macro per-state accuracy and
qid/type/empty-Claims/replicate strata are also reported. ExactStateMask requires
valid contract and every node status correct, per response; both-replicates
exactness is supplementary. Exactness does not silently include citation quality.

FalseSupported numerator: Gold P/U predicted F. Denominator: all planned Gold
P/U nodes. FalseUnresolved numerator: Gold F predicted P/U. Denominator: all
planned Gold F nodes. Missing outputs on Gold F are separately counted; they
are not fabricated P/U predictions. FullySupportedPrecision and FullSupport
Sufficiency use actual valid predicted F nodes. SupportPrecision uses every
citation in contract-valid outputs. PartialSupportValidity uses predicted P.
ResidualRecall is Gold-residual IDs retained by usable predicted masks / all
planned Gold residual IDs; failed outputs retain none. ResidualPrecision uses
predicted residual IDs. No success credit from schema-invalid output; preserve
its original output and review it qualitatively. No numerator is fabricated
when there is no usable prediction. A zero-denominator gate metric is NA and
fails rather than receiving vacuous success.

E2 primary valid/supported/downstream/FalseSTOP rates use all54 planned slots
per arm and frozen reference truth, not a possibly wrong model mask. Selecting
an input-mask-full ID and STOP despite an input residual are supplementary
adherence metrics. Invalid/blocked slots are incorrect for validity/schema;
they do not fabricate a supported selection or STOP. No natural positive STOP
controls exist; MissedSTOP is not evaluated. Stability accepts different valid
IDs. GATES.json specifies every threshold; comparisons use unrounded values
with only1e-12 numeric tolerance. Both E1 gates must pass before E2. E2 always
stops this experiment. No post-result threshold or prompt adaptation.

## Review and sensitivity

First-pass packets hide arm, replicate, Gold, GoldO, aggregates and provider
reasoning. E1 reviewer sees only Q/Skeleton/Claims/generated Mask; E2 sees
Q/Skeleton/supplied Mask/generated Selection. E2 first-pass judgment is relative
to that visible mask; reference-truth errors are scored after unmasking. A
familiar single reviewer may recognize content or skeleton style. Packet
masking is not independent review or memory erasure. Save judgments, commit,
then seal before aggregate. Frozen references are never revised to match outputs;
blind-reference disagreements are reported separately.

analysis/SENSITIVITY.json preregisters low-ambiguity, citation-context, semantic
convention, locality and leave-one-qid-out descriptions. These cannot rescue a
failed primary gate. Monotonic progress is descriptive only on literal
Claims-addition pairs without identified semantic refutation/refinement;
candidate-scope refinement pairs G05→G06 and G17→G18 are excluded in advance.
No independent-replicate p-value or fresh-generalization claim is made.

## Mechanical policy and accounting

DeepSeek deepseek-flash; temperature0; literal JSON prompts; JSON mode;
max_tokens omitted; max_retries0 in transport and harness; concurrency at most8.
HTTP timeout240s is per-operation inactivity, not a wall-time ceiling. First
formal slot is the authentication canary. Contract/access/billing statuses
400/401/402/403/404/422 halt unsent slots; in-flight outcomes remain. No retry,
repair, replacement, adaptive prompt patch, resume or overwritten result.
Raw responses, exact requests, attempts, failure records and usage are retained.
No credential value or Authorization header is archived.

Per stage report planned, send intent, returned, HTTP/schema errors, input,
completion, reasoning, total, cache hit/miss, weighted cache hit rate, unknown
usage, latency median/P95/max and peak concurrency. Reasoning is already inside
completion and is never added again. Send intent cannot prove provider receipt
after a transport failure. Unknown usage is not a billed zero. No currency
estimate without verified prices. Token estimates are scenarios, not caps.

## Persistence and scope

Episode-stable: Q and Skeleton. Persistent epistemic: Claims and Hypothesis.
Mechanical: Workspace/Trace/D/W. Recompute Mask, Residual, ActiveID and Gap each
control cycle in a future experiment. This task implements no persistent status,
no requires/DAG/Binding IR, no backend change or action gating. Passing exposed
development gates only justifies a separately registered4–8 decision rollout.
