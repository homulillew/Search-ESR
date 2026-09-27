"""Prepare exact requests and offline preflight without spending a model call."""
import math
import re
from .common import *
from .selection import build_schedule
from experiments.skeleton_state_alignment.prepare import credential

def main():
    assert read(P/'e0_control_equivalence/METRICS.json')['gate']['pass']
    text=(P/'TASK.md').read_text()
    prompt=re.search(r'# 27\. .*?```text\n(.*?)```',text,re.S).group(1)
    write(P/'prompts/selection.txt',prompt)
    config={k:read(OLD/'CONFIG.json')[k] for k in ('provider','endpoint','base_url','model','temperature','max_retries','max_workers','replicates','max_tokens_policy','response_format','timeout_seconds','timeout_semantics','halt_http_statuses','credential_source','tool_calls','horizon')}
    config.update(planned_calls=108,maximum_calls=108,authorization_policy='TASK46: approval must explicitly apply to this new experiment; old authorization not inherited.',
      mask_policy='S0 frozen Gold; S1 old A1 replicate1, binary only, no fallback',paid_authorization_artifact='AUTHORIZATION.json')
    write(P/'CONFIG.json',config)
    reference=OLD/'e2_selection/SELECTION_REFERENCE.json'
    write(P/'e1_selection/SELECTION_REFERENCE.json',reference.read_text())
    jobs=build_schedule();write(P/'e1_selection/SCHEDULE.json',jobs)
    write(P/'SCHEMAS.json',{'output':{'type':'object','required':['selection'],'additionalProperties':False,
        'properties':{'selection':{'type':'string','allowed':'STOP or one requirement_id from the fixed input skeleton'}}},
        'input_keys':['Original Question','Task Skeleton','Control Mask'],
        'review_error_codes':['invalid_schema','input_closed_selected','premature_stop_under_visible_mask','downstream_skip','coarse_nonlocal_node','other_visible_selection_error','no_response'],
        'review_fields':['selection_appropriate_under_visible_mask','error_codes','reason']})
    write(P/'REVIEW_RUBRIC.md','''# First-pass selection review

View only anonymized PACKETS.json: Q, D2 Skeleton, visible binary Mask, selection. Do not open KEY, schedule identifiers, frozen acceptable IDs, historical GoldO, aggregates or provider reasoning during first pass. Existing exposed-bank familiarity is disclosed; masking is not independence.

For every review_id supply selection_appropriate_under_visible_mask (bool/null when no output), error_codes, and a concrete reason. Check schema, input OPEN, one local objective, role/scope preservation and visible unresolved prerequisites. An unknown entity can be a valid discovery goal. Multiple legitimate IDs are acceptable. A positive selection under a faulty visible mask does not establish validity under hidden Gold.

Freeze/commit all108 judgments before seal_review and aggregate. Primary scores use unchanged inherited selection references. Any disagreement remains a disclosed diagnostic, never a reference edit. G04/G05 remain in denominator. No reviewer-generated reworded requirement is sent to the selector.
''')
    try:credential();available=True
    except ValueError:available=False
    write(P/'analysis/PROVIDER_PREFLIGHT.json',{'status':'OFFLINE_PASS' if available else 'CREDENTIAL_MISSING',
        'credential_available':available,'credential_logged':False,'network_requests':0,
        'authentication_verified_this_experiment':False,'note':'Credential presence does not verify live authentication; first scheduled slot is formal canary.',
        'max_retries':0,'max_concurrency':8,'timeout_seconds':240})
    import tiktoken
    enc=tiktoken.get_encoding('cl100k_base')
    tokens=[sum(len(enc.encode(m['content']))+4 for m in j['request']['messages'])+3 for j in jobs]
    past=[read(p)['usage']['completion_tokens'] for p in (OLD/'e1_alignment/calls').glob('*.result.json')]
    past.sort();median=(past[53]+past[54])/2;p95=past[math.ceil(.95*len(past))-1]
    estimate={'planned_calls':108,'arms':2,'states':27,'replicates':2,'input_tokens_proxy':sum(tokens),
        'input_per_call_range':[min(tokens),max(tokens)],'input_tokenizer':'cl100k_base + approximate chat overhead; not provider-exact',
        'completion_scenarios':{'historical_alignment_n':len(past),'historical_p50_per_call':median,'historical_p95_per_call':p95,'historical_max_per_call':max(past),
            'at_p50_total':median*108,'at_p95_total':p95*108,'at_observed_max_total':max(past)*108},
        'scenario_limit':'Alignment completion distribution is only a budgeting proxy, not measured Selection behavior. Reasoning may dominate despite ID-only visible output. max_tokens omitted; no hard token/currency cap.',
        'cache_hit_rate':None,'cache_note':'Historical cache73.49% is not promised for this new prompt. Log actual hit/miss and weighted rate if authorized.',
        'currency_estimate':None,'currency_reason':'No current price lookup; no monetary claim.'}
    write(P/'analysis/CALL_ESTIMATE.json',estimate)
    write(P/'e1_selection/STATUS.json',{'status':'PREPARED_FOR_E1_EXECUTION','e0_gate':'PASS','planned':108,'sent':0,
        'blocker':'TASK46 requires new applicable paid-call authorization','prompt_source':'TASK section27 verbatim','mask_source':'historical A1 replicate1'})
    write(P/'analysis/EXECUTION_ACCOUNTING.json',{'new_model_calls':0,'new_paid_calls':0,'E0':'108 historical outputs reused, no new charge',
       'E1':{'planned':108,'sent':0,'returned':0,'retries':0,'cache_hit_rate':None,'status':'PREPARED_FOR_E1_EXECUTION'},
       'historical_usage':'Read-only prior artifacts; never counted as new experiment spending.'})
    print(json.dumps(estimate,indent=2))
if __name__=='__main__':main()
