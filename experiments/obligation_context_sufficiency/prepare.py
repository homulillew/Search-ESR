"""Offline preparation and immutable 216-request freeze."""
import argparse,math,re
from .common import *
from .context import prepare_context,construct

def request_for(c,arm):
 return {'model':'deepseek-flash','temperature':0,'stream':False,'response_format':{'type':'json_object'},
  'messages':[{'role':'system','content':(P/'prompts/obligation_context_unified.txt').read_text()},
              {'role':'user','content':json.dumps(input_for(c,arm),ensure_ascii=False)}]}
def credential():
 import os
 from dotenv import dotenv_values
 key=os.environ.get('DEEPSEEK_API_KEY') or dotenv_values(ROOT/'.env.deepseek').get('DEEPSEEK_API_KEY')
 if not isinstance(key,str) or not key.strip() or '\n' in key or '\r' in key:raise ValueError('Credential unavailable/invalid; STOP_BEFORE_PAID_CALL')
 return key

def preflight(jobs,cases,config,check_paths=True):
 assert config['endpoint']=='https://api.deepseek.com/chat/completions' and config['base_url']=='https://api.deepseek.com'
 assert config['model']=='deepseek-flash' and config['max_retries']==0 and config['temperature']==0
 assert config['max_workers']==8 and config['planned_calls']==216 and config['replicates']==2
 assert config['response_format']=={'type':'json_object'} and config['max_tokens_policy']=='omit'
 assert config['credential_source']=='DEEPSEEK_API_KEY environment or .env.deepseek; never archived'
 seen=set();paths=set()
 for j in jobs:
  ident=(j['case_id'],j['arm'],j['replicate']);assert ident not in seen;seen.add(ident)
  assert j['id']==f"{j['arm']}__{j['case_id']}__R{j['replicate']}"
  r=j['request'];assert r==request_for(cases[j['case_id']],j['arm'])
  assert r['model']==config['model'] and r['temperature']==0 and r['response_format']==config['response_format']
  assert 'json' in '\n'.join(m['content'] for m in r['messages']).lower(), 'STOP_BEFORE_PAID_CALL: JSON literal missing'
  assert not any(k in r for k in ('max_tokens','max_completion_tokens','tools','tool_choice','api_key','Authorization'))
  assert digest(r)==j['request_sha256'] and json.loads(json.dumps(r,ensure_ascii=False))==r
  payload=json.loads(r['messages'][1]['content']);assert set(payload)=={'Original Question','Verified Claims','Recent Context'}
  assert set(payload['Recent Context'])=={'recent_claim_delta','recent_events','recent_observations'}
  for suffix in ('request','attempt','response','result'):
   path=P/'e1_context/calls'/f"{j['id']}.{suffix}.json";assert str(path) not in paths;paths.add(str(path))
   if check_paths:assert not path.exists(),'Refuse overwrite'
 assert seen=={(c,a,r) for c in cases for a in ARMS for r in (1,2)}
 # Compare payloads against fresh mechanical reconstruction, not merely stored cards.
 for c in cases.values():
  cc,*_=construct(c)
  for a in ARMS:assert input_for(c,a)['Recent Context']==cc[a]
 return {'status':'PASS','scheduled':len(jobs),'literal_json_all':True,'exact_cross_product':True,'unique_paths':len(paths),
 'payload_isolation':True,'source_reconstruction_identical':True,'zero_network_calls':True}

def prepare():
 task=(P/'TASK.md').read_text();prompt=re.search(r'# 26\. Unified Obligation Prompt.*?```text\n(.*?)```',task,re.S).group(1)
 write(P/'prompts/obligation_context_unified.txt',prompt)
 config=read(OLD/'CONFIG.json');config.pop('maximum_total_calls_if_E1_pass');config['planned_calls']=216
 config['paid_authorization']='Prior user explicitly authorized API calls and subsequent stages; applicable bounded authorization for this task: exactly 216 scheduled DeepSeek requests, no extra canary, retry, revision, Gap, retrieval, Writer or loop calls.'
 write(P/'CONFIG.json',config);prepare_context();cases=bank();jobs=[]
 for c in cases.values():
  for arm in ARMS:
   for rep in (1,2):
    request=request_for(c,arm);jobs.append({'id':f"{arm}__{c['case_id']}__R{rep}",'case_id':c['case_id'],'state_id':c['state_id'],'qid':c['qid'],'arm':arm,'replicate':rep,'request':request,'request_sha256':digest(request)})
 jobs.sort(key=lambda j:digest(['obligation-context-schedule-v1',j['id']]))
 write(P/'e1_context/SCHEDULE.json',jobs)
 checked=preflight(jobs,cases,config);credential()
 write(P/'analysis/PROVIDER_PREFLIGHT.json',{**checked,'credential_available':True,'credential_value_logged':False,'auth_handling':'header only; no redirects; HTTPTransport retries=0'})
 write(P/'analysis/DRY_RUN.json',{**checked,'real_calls':0,'model_outputs':0,'source_snapshots_verified':27})
 import tiktoken
 enc=tiktoken.get_encoding('cl100k_base');est=[sum(len(enc.encode(m['content']))+4 for m in j['request']['messages'])+3 for j in jobs]
 old=[]
 for directory in ('need_premise_audit/e1_checker/calls','minimal_need_multiquery/e1_need/development_run/calls','minimal_need_multiquery/e1_need/revision/run/calls','evidence_gap_gold_obligation/e1_gap/calls','dynamic_local_obligation/e1_obligation/calls'):
  for p in (ROOT/'experiments'/directory).glob('*.result.json'):
   u=read(p).get('usage') or {}
   if isinstance(u.get('completion_tokens'),int):old.append(u['completion_tokens'])
 old.sort();q=lambda p:old[min(len(old)-1,math.ceil(p*len(old))-1)]
 write(P/'analysis/CALL_ESTIMATE.json',{'planned_calls':216,'cases':27,'arms':4,'replicates':2,'peak_concurrency':8,
  'estimated_prompt_tokens':sum(est),'prompt_range':[min(est),max(est)],'prompt_tokens_by_arm':{a:sum(v for j,v in zip(jobs,est) if j['arm']==a) for a in ARMS},
  'tokenizer':'cl100k_base proxy; actual DeepSeek tokens can differ','historical_observed_usage_responses':len(old),
  'completion_quantiles':{'p50':q(.5),'p90':q(.9),'p95':q(.95),'max':max(old)},
  'completion_exposure_at_historical_median':216*q(.5),'completion_exposure_at_observed_65535_tail':216*65535,
  'tail_caveat':'Observed historical tail is a scenario, not a hard maximum with max_tokens omitted.', 'currency_cost':'Not estimated: no price verification.'})
 identity={rel(p):sha(p) for p in (OLD/'e0_reference').glob('*.json')}
 identity[rel(OLD/'PROTOCOL.md')]=sha(OLD/'PROTOCOL.md')
 write(P/'analysis/REFERENCE_IDENTITY.json',{'status':'PASS','read_only_originals':identity,'exact_QC_states':27,'Gold_unchanged':True,'no_gold_inputs':True})
 history={s:sha(ROOT/s) for s in git('ls-files','experiments').splitlines() if s and not s.startswith(rel(P)+'/') and (ROOT/s).is_file()}
 write(P/'analysis/HISTORICAL_HASHES.json',history)
def freeze():
 assert not (P/'e1_context/calls').exists()
 preflight(read(P/'e1_context/SCHEDULE.json'),bank(),read(P/'CONFIG.json'));assert read(P/'analysis/OFFLINE_TESTS.json')['passed']
 files={rel(p):sha(p) for p in sorted(P.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='FREEZE.json'}
 write(P/'FREEZE.json',{'base_commit':'8562c166326417e73be1eadb3b891b7c5769b0ad','preparation_head':git('rev-parse','HEAD'),'files':files,'calls':216,'arms':list(ARMS),'replicates':2,
  'mechanism_thresholds':{'strict_improvement_pp':10,'broadness_reduction_pp':10,'stable_improvement_pp':15,'relation_arg_worsening_max_pp':5},
  'viability_thresholds':{'strict_min':.75,'broadness_max':.15,'downstream_max':.15,'scope_min':.85,'stable_min':.65,'relation_arg_max':.075},
  'failure_policy':'All planned slots remain denominator; no retry, repair, replacement or resume. Halt queued requests on provider contract/access/billing errors. Stop after 216 scheduled slots regardless of outcome. No cascade or decomposition.'})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','freeze']);globals()[p.parse_args().mode]()
