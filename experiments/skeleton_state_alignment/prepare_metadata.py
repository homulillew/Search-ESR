"""Pre-call design metadata; no outputs, model calls or synthetic result files."""
from .common import *

def main():
    gates={
      'A0':{'node_status_accuracy':['>=',.90],'false_supported_rate':['<=',.05],'residual_recall':['>=',.95],
        'support_precision':['>=',.90],'full_support_sufficiency':['>=',.90],'exact_state_mask':['>=',.80],'schema_validity':['>=',.95]},
      'A1':{'node_status_accuracy':['>=',.85],'false_supported_rate':['<=',.075],'residual_recall':['>=',.90],
        'support_precision':['>=',.85],'exact_state_mask':['>=',.70],'schema_validity':['>=',.95],
        'alignment_loss':['<=',.10],'node_accuracy_loss':['<=',.10]},
      'S0':{'valid_selection':['>=',.85],'selected_supported':['<=',.05],'downstream_selection':['<=',.10],'false_stop':['<=',.05],'schema_validity':['>=',.95]},
      'S1':{'valid_selection':['>=',.80],'selected_supported':['<=',.075],'downstream_selection':['<=',.10],'false_stop':['<=',.075],'schema_validity':['>=',.95],'selection_loss':['<=',.10]}}
    write(P/'GATES.json',gates)
    schemas={
      'E1_output':{'type':'object','required':['requirements'],'additionalProperties':False,'properties':{'requirements':{'type':'array','items':{
        'type':'object','required':['requirement_id','status','supported_by'],'additionalProperties':False,'properties':{
        'requirement_id':{'type':'string'},'status':{'enum':list(STATUSES)},'supported_by':{'type':'array','uniqueItems':True,'items':{'type':'string'}}}}}}},
      'E2_output':{'type':'object','required':['selection'],'additionalProperties':False,'properties':{'selection':{'type':'string'}}},
      'additional_mechanical_checks':['Every input requirement ID exactly once; no unknown IDs','Citations exist in current Claims, no duplicate citations',
        'F/P nonempty citations; U empty citations','E2 one existing D2 ID or literal STOP','Exact response model and finish_reason=stop'],
      'E1_input_keys':['Original Question','Task Skeleton','Verified Claims'],
      'E2_input_keys':['Original Question','Task Skeleton','Coverage Mask'],
      'E2_mask_fields':['requirement_id','status'],
      'error_taxonomy':{
       'e1_alignment':['false_supported','false_unresolved','partial_as_full','partial_as_none','wrong_support_claim','insufficient_support_group',
        'entity_overlap_as_support','task_requirement_as_fact','outside_knowledge','output_contract','mechanical_failure'],
       'e2_selection':['selected_supported','downstream_selection','low_value_selection','false_stop','missed_stop','invalid_requirement_id','output_contract','mechanical_failure']}}
    write(P/'SCHEMAS.json',schemas)
    pairs=[];cases=list(bank().values())
    for q in sorted({c['qid'] for c in cases}):
        group=sorted([c for c in cases if c['qid']==q],key=lambda c:int(c['state_id'].rsplit('_S',1)[1]))
        for a,b in zip(group,group[1:]):
            before={c['claim_id']:c['statement'] for c in a['claims']};after={c['claim_id']:c['statement'] for c in b['claims']}
            addition=all(after.get(i)==v for i,v in before.items()) and len(after)>len(before)
            refinement=(a['case_id'],b['case_id']) in [('G05','G06'),('G17','G18')]
            pairs.append({'qid':q,'from':a['case_id'],'to':b['case_id'],'literal_claim_addition':addition,'eligible':addition and not refinement,
              'reason':'Candidate/role grounding refines from founder Kwon to an additional founder Ding, or generic SPS background to specific FOP records; exclude from no-refinement monotonic summary.' if refinement else 'Literal preserved Claims plus added Claims, with no explicit refutation identified in the current prefix pair.'})
    write(P/'analysis/MONOTONIC_PAIRS.json',pairs)
    sensitivity={'status':'PREREGISTERED_NOT_EVALUATED','primary_gates_unchanged':True,'analyses':[
      {'name':'low_ambiguity_nodes','rule':'Recompute E1 node and support metrics on only Gold nodes marked ambiguity=low; do not report all-state exactness for a partial node subset.'},
      {'name':'strict_citation_context','rule':'For contextual full proofs require cited group UNION reference_binding_context. Report full-support sufficiency only; primary contextual sufficiency remains unchanged.'},
      {'name':'unqualified_author_list','overrides':[{'case_id':'G03','arm':'A0','id':'R2','status':'partially_supported'}],
       'reason':'Conservative alternative: an unqualified two-coauthor bibliographic Claim may not certify no additional authors.'},
      {'name':'writing_vs_publication','overrides':[{'case_id':'G03','arm':a,'id':'R1','status':'partially_supported'} for a in ('A0','A1')],
       'reason':'Conservative alternative refuses to equate bibliographic publication year with writing year.'},
      {'name':'tribute_partner_scope','overrides':[{'case_id':'G09','arm':'A0','id':'R4','status':'unsupported'},{'case_id':'G09','arm':'A1','id':'R3','status':'unsupported'}],
       'reason':'Alternative stricter relation-binding requires an evidenced interview before partnership can count as partial interview support.'},
      {'name':'relaxed_selection_locality','add_acceptable':{'G04':['R2'],'G05':['R2']},
       'reason':'Descriptive alternative treats the full childless-couple/donation group as one discovery episode; never changes primary no-admissible-ID labels.'},
      {'name':'strict_selection_locality','remove_acceptable_by_qid':{'261':['R2'],'169':['R2'],'637':['R4'],'843':['R3','R4'],'922':['R1']},
       'reason':'Narrower interpretation of multi-clue identification episodes; report dependence on whole-node locality conventions.'},
      {'name':'leave_one_qid_out','rule':'Recompute descriptive gates excluding each of10 qids, without changing primary stage progression.'}],
      'limitations':['One familiar reviewer, exposed bank, correlated state/replicate samples','No new labels or masks based on model outputs','No outside facts imported in any sensitivity','No all-task same-candidate closure certificate from pointwise masks']}
    write(P/'analysis/SENSITIVITY.json',sensitivity)
    write(P/'HYPOTHESES.md','''# Preregistered hypotheses

H1: A stable Q-only skeleton can be reconciled with changing Claims, meeting all
A0 gates without treating task requirements as evidence. H2: fixed prior D2
replicate1 loses at most10pp exact-state and node accuracy relative to Oracle,
while meeting its absolute gates. H3 (conditional): one useful next requirement
can be selected by ID under a Gold Mask (S0). H4: fixed A1 replicate1 masks do
not cost more than10pp selection validity, while S1 meets absolute gates.

E0 diagnoses the different question of control addressability. It cannot choose
a better D2 replicate or promote D1 into the primary arm. D2's E0 warning is
retained when interpreting any E1 success. Broad masks could be accurate even
while the remaining useful local action is not expressible by one node.

All comparisons concern27 exposed historical natural states across10 questions.
Neither fresh generalization nor final-answer improvement is tested. No causal
claim about reducing natural-language corruption is licensed by ID-only output
without a paired natural-language baseline in this experiment.
''')
    write(P/'PROTOCOL.md','''# Skeleton–Claims Alignment / Plan–State Reconciliation

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
''')
    write(P/'REVIEW_RUBRIC.md','''# Frozen first-pass rubric

Read only the stage's review/PACKETS.json. Do not open KEY.json, Gold Masks,
selection reference, historical GoldO, provider raw/reasoning or aggregates until
JUDGMENTS.json has been committed. One familiar Codex reviewer; no independence
claim. Provider reasoning is never needed for primary semantic judgments.

E1 packet: input Q/Skeleton/Claims and generated JSON. For every fixed node,
judge whether its status follows from all current Claims, then whether cited
Claims make a substantive contribution and jointly justify the asserted status.
Requirement wording/name overlap does not establish a fact. Trace role, event,
date and same-entity bindings; never import geography or biography from memory.
F must cover all material conditions; P must cover a proper substantive subset;
U requires no citations. Different sufficient proof sets are accepted.

Write JUDGMENTS.json as an object keyed only by review_id. E1 value:
  {"node_judgments":{"R1":{"status_correct":true,
    "support_correct":true,"reason":"Prefix-only semantic judgment"}},
   "error_codes":[],"reason":"Overall judgment"}
Include every input ID. On missing output use null judgments with a mechanical
reason, not invented statuses. Mark ambiguity in the reason if relevant. Use
SCHEMAS.json taxonomy; semantic codes require observed content, not speculation
about hidden reasoning. task_requirement_as_fact requires unsupported promotion
specifically tracing to a Q/Skeleton predicate, not just any wrong F.

E2 packet: Q/D2/supplied status Mask and generated selection. Judge one useful,
local, unresolved ID that does not skip an obvious prerequisite, or STOP only
when supplied mask is all-full. Unknown entities can themselves be discovery
targets. Do not demand a unique favorite ID. E2 value:
  {"selection_appropriate_under_visible_mask":true,
   "error_codes":[],"reason":"Visible-mask judgment"}
Use null for no usable response/input. Gold-truth downstream/full errors are
computed only after this pass; the packet does not expose actual Claims.

Commit PACKETS/KEY/JUDGMENTS, run score seal_review, then score aggregate. Report
blind-reference disagreement without changing frozen Gold. A schema-invalid
response can receive qualitative reasons but never success credit in gates.
''')

if __name__=='__main__':main()
