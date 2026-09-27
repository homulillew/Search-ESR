"""Freeze requests and evaluation before any new model invocation."""
import re,math
from .common import *
from .inputs import build_schedule
from experiments.skeleton_state_alignment.prepare import credential

def main():
 task=(P/'TASK.md').read_text();base=re.search(r'# 18\. .*?```text\n(.*?)```',task,re.S).group(1)
 suffix='\nIf the input contains no substantive supporting Claim, use "mode": "probe" and "used_claims": []. In this case local_residual is still one exploratory evidence objective, not a search query.\n'
 write(P/'prompts/residualizer_base_from_task.txt',base);write(P/'prompts/residualizer.txt',base+suffix)
 write(P/'prompts/MODE_FORMAT_NOTE.md','The system prompt includes TASK18 exact English block plus a literal English rendering of TASK18 required no-substantive-support mode=probe/used_claims=[] alternative. No added semantic strategy, examples, or prompt iteration. Both return branches reach the model.\n')
 for sec,name in ((33,'query_generator'),(40,'orthogonal_probe')):
  write(P/f'prompts/{name}.txt',re.search(r'# '+str(sec)+r'\. .*?```text\n(.*?)```',task,re.S).group(1))
 config={k:read(PREV/'CONFIG.json')[k] for k in ('provider','endpoint','base_url','model','temperature','max_retries','max_workers','replicates','max_tokens_policy','response_format','timeout_seconds','timeout_semantics','halt_http_statuses','credential_source','tool_calls','horizon')}
 config.update(planned_E1=114,conditional_E2_maximum_query_calls=32,conditional_E2B_maximum_model_calls=32,
  maximum_model_calls_all_stages=178,E2_P1_source='E1 R0 replicate1, no best-of/repair/fallback',
  E2_replicates=1,E2_comparison_rule='P1-P0 NewMaterialEvidence rate >=0.10, not wins-minus-losses alternative',
  E2B_maximum_attempts='one additional probe+query only per eligible P1 NoGain state',
  permission='Current TASK explicitly requests these model/retrieval stages; no new-approval requirement in this task. Prior scoped approval is not reused.')
 write(P/'CONFIG.json',config)
 gates={'R0':{'strict_validity':['>=',.85],'residual_addressability':['>=',.85],'supported_content_leakage':['<=',.05],
    'broad_residual':['<=',.10],'downstream':['<=',.05],'relation_object_temporal_corruption':['<=',.05],
    'state_discrimination':['>=',.80],'control_over_decomposition':['<=',.10],'schema':['>=',.95]},
  'R1':{'strict_validity':['>=',.90]},'R2':{'strict_validity':['>=',.80],'strict_loss_R0_minus_R2':['<=',.10]},
  'P_gate_R0':{'strict_validity':['>=',.85],'residual_addressability':['>=',.85],'supported_content_leakage':['<=',.05],
    'broad_residual':['<=',.10],'downstream':['<=',.05],'relation_object_temporal_corruption':['<=',.05],'control_over_decomposition':['<=',.10],'schema':['>=',.95]},
  'P_gate_R1':{'strict_validity':['>=',.90]},
  'E2':{'minimum_accessible_states':8,'minimum_qids':4,'P1_new_material':.60,'P1_binding':.50,'candidate_commitment_max':.05,'drift_max':.05,'P1_minus_P0_material_min':.10}}
 write(P/'GATES.json',gates)
 write(P/'e1_residualization/SCHEDULE.json',build_schedule())
 for stage in ('e2_bootstrap','e2b_escalation'):
  write(P/stage/'STATUS.json',{'status':'CONDITIONAL_NOT_RUN','condition':'P_gate_R0 AND P_gate_R1 pass; E2 accessible bank frozen before calls' if stage=='e2_bootstrap' else 'Actual P1 NoGain, accessible source, untried source-anchored facet',
   'new_calls':0,'no_unfrozen_stage_dispatch':True})
 try:credential();key=True
 except ValueError:key=False
 write(P/'analysis/PROVIDER_PREFLIGHT.json',{'credential_available':key,'credential_logged':False,'network_requests':0,'authentication_test':'first formal slot only; no extra canary'})
 import tiktoken
 enc=tiktoken.get_encoding('cl100k_base');jobs=build_schedule();tokens=[sum(len(enc.encode(m['content']))+4 for m in j['request']['messages'])+3 for j in jobs]
 write(P/'analysis/CALL_ESTIMATE.json',{'E1_calls':114,'input_tokens_proxy':sum(tokens),'per_call_range':[min(tokens),max(tokens)],
  'tokenizer':'cl100k_base proxy, not provider tokenizer','completion_scenarios_note':'Historical ID selector had long reasoning despite short output, including4 length failures. No token cap promised with max_tokens omitted.',
  'prior_selection_completion_total_108':695973,'prior_alignment_completion_total_108':259559,
  'estimated_E1_completion_at_prior_per_call_means':{'alignment_mean':259559/108*114,'selector_mean':695973/108*114},
  'currency_cost':None,'max_concurrency':8,'max_retries':0,'conditional_calls_require_new_stage_freeze':True})
 write(P/'AUTHORIZATION.json',{'status':'AUTHORIZED_BY_CURRENT_TASK','experiment':'state-conditioned-residualization',
  'task_sha256':sha(P/'TASK.md'),'basis':'User supplied execution task specifies114 E1 calls and gated E2/E2B retrieval; applicable authorization is this request, not earlier exhausted108-call approval.',
  'maximum_model_calls':178,'E1':114,'conditional_E2':32,'conditional_E2B':32,'no_full_rollout':True})
if __name__=='__main__':main()
