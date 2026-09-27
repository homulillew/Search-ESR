"""Deterministic offline schedule, contract preflight, exposure and freeze."""
import argparse
import math
import re
from .common import *

def request_for(c, arm):
 name='o0_no_h' if arm=='O0' else 'o1_with_h'
 return {'model':'deepseek-flash','temperature':0,'stream':False,'response_format':{'type':'json_object'},
  'messages':[{'role':'system','content':(P/f'prompts/{name}.txt').read_text()},
              {'role':'user','content':json.dumps(input_for(c,arm),ensure_ascii=False)}]}

def credential():
 import os
 from dotenv import dotenv_values
 key=os.environ.get('DEEPSEEK_API_KEY') or dotenv_values(ROOT/'.env.deepseek').get('DEEPSEEK_API_KEY')
 if not isinstance(key,str) or not key.strip() or '\n' in key or '\r' in key: raise ValueError('Credential unavailable/invalid; STOP_BEFORE_PAID_CALL')
 return key

def preflight(jobs, cases, config, check_paths=True):
 assert config['endpoint']=='https://api.deepseek.com/chat/completions'
 assert config['model']=='deepseek-flash' and config['max_retries']==0
 assert config['credential_source']=='DEEPSEEK_API_KEY environment or .env.deepseek; never archived'
 seen=set(); paths=set()
 for j in jobs:
  ident=(j['case_id'],j['arm'],j['replicate'])
  assert ident not in seen; seen.add(ident)
  assert j['id']==f"{j['arm']}__{j['case_id']}__R{j['replicate']}"
  request=j['request']; assert request==request_for(cases[j['case_id']],j['arm'])
  assert request['model']==config['model'] and request['temperature']==0
  assert request['response_format']=={'type':'json_object'}
  assert 'json' in '\n'.join(m['content'] for m in request['messages']).lower(), 'STOP_BEFORE_PAID_CALL: JSON literal missing'
  assert not any(k in request for k in ('max_tokens','max_completion_tokens','tools','tool_choice','api_key','Authorization'))
  assert digest(request)==j['request_sha256']
  assert json.loads(json.dumps(request,ensure_ascii=False))==request
  payload=json.loads(request['messages'][1]['content'])
  expected={'Original Question','Verified Claims'} | ({'Working Hypothesis'} if j['arm']=='O1' else set())
  assert set(payload)==expected
  for suffix in ('request','attempt','response','result'):
   path=P/'e1_obligation/calls'/f"{j['id']}.{suffix}.json"
   assert str(path) not in paths;paths.add(str(path))
   if check_paths: assert not path.exists(), 'Refuse output overwrite'
 assert seen=={(cid,a,r) for cid in cases for a in ('O0','O1') for r in (1,2)}
 return {'status':'PASS','scheduled':len(jobs),'literal_json_all':True,'payload_isolation':True,'exact_cross_product':True,'unique_paths':len(paths),'zero_network_calls':True}

def prepare():
 task=(P/'TASK.md').read_text()
 g0=re.search(r'# 15\. O0 Prompt.*?```text\n(.*?)```',task,re.S).group(1)
 addition=re.search(r'# 16\. O1 Prompt.*?```text\n(.*?)```',task,re.S).group(1)
 write(P/'prompts/o0_no_h.txt',g0);write(P/'prompts/o1_with_h.txt',g0+'\n'+addition)
 config={'provider':'deepseek','endpoint':'https://api.deepseek.com/chat/completions','base_url':'https://api.deepseek.com','model':'deepseek-flash','temperature':0,
  'max_retries':0,'max_workers':8,'replicates':2,'max_tokens_policy':'omit','response_format':{'type':'json_object'},
  'timeout_seconds':240,'timeout_semantics':'HTTP inactivity per connect/read/write/pool; not total wall timeout',
  'halt_http_statuses':[400,401,402,403,404,422], 'credential_source':'DEEPSEEK_API_KEY environment or .env.deepseek; never archived',
  'paid_authorization':'Prior user explicitly authorized API calls and subsequent stages; bounded current task only: E1 108 scheduled DeepSeek requests, plus at most 108 E2 gap requests only after the frozen E1 gate passes; no canary/retry/revision or acquisition calls.',
  'tool_calls':0,'horizon':1,'planned_calls':108,'maximum_total_calls_if_E1_pass':216}
 write(P/'CONFIG.json',config)
 cases=bank();jobs=[]
 oldroot=ROOT/'experiments/evidence_gap_gold_obligation'
 source_checks={}
 for name in ('CASES.json','GOLD_OBLIGATIONS.json','GOLD_GAPS.json'):
  oldfile=oldroot/'e0_reference'/name;newfile=P/'e0_reference'/name
  assert oldfile.read_bytes()==newfile.read_bytes()
  source_checks[name]=sha(oldfile)
 for c in cases.values():
  original=read(ROOT/c['snapshot'])['state']
  assert c['belief']=={'question':original['question'],'claims':[x['statement'] for x in original['claims']],'hypothesis':original['hypothesis']}
  assert sha(ROOT/c['snapshot'])==c['snapshot_sha256']
 write(P/'analysis/REFERENCE_IDENTITY.json',{'status':'PASS','copied_files':source_checks,'original_snapshots_checked':27,
  'frozen_gap_prompt_path':rel(oldroot/'prompts/g0_gap_no_h.txt'),'frozen_gap_prompt_sha256':sha(oldroot/'prompts/g0_gap_no_h.txt')})
 for c in cases.values():
  for arm in ('O0','O1'):
   for rep in (1,2):
    request=request_for(c,arm)
    jobs.append({'id':f"{arm}__{c['case_id']}__R{rep}",'case_id':c['case_id'],'state_id':c['state_id'],'qid':c['qid'],'arm':arm,'replicate':rep,'request':request,'request_sha256':digest(request)})
 jobs.sort(key=lambda j:digest(['dynamic-obligation-schedule-v1',j['id']]))
 write(P/'e1_obligation/SCHEDULE.json',jobs)
 checked=preflight(jobs,cases,config); credential()
 write(P/'analysis/PROVIDER_PREFLIGHT.json',{**checked,'credential_available':True,'credential_value_logged':False,'auth_handling':'header only, no redirects, no transport retries'})
 from experiments.dynamic_local_obligation.run import validate_output
 assert validate_output({'obligation':'Identify the relevant entity from question-grounded clues.'},next(iter(cases.values())))
 write(P/'analysis/DRY_RUN.json',{**checked,'real_calls':0,'model_outputs':0,'source_snapshots_verified':27,'schema_example_valid':True})
 # Token estimates use a surrogate tokenizer; no API call or price lookup.
 import tiktoken
 enc=tiktoken.get_encoding('cl100k_base')
 estimates=[sum(len(enc.encode(m['content']))+4 for m in j['request']['messages'])+3 for j in jobs]
 old=[]
 for directory in ('need_premise_audit/e1_checker/calls','minimal_need_multiquery/e1_need/development_run/calls','minimal_need_multiquery/e1_need/revision/run/calls','evidence_gap_gold_obligation/e1_gap/calls'):
  for p in (ROOT/'experiments'/directory).glob('*.result.json'):
   u=read(p).get('usage') or {}
   if isinstance(u.get('completion_tokens'),int):old.append(u['completion_tokens'])
 old.sort()
 q=lambda p:old[min(len(old)-1,math.ceil(p*len(old))-1)]
 write(P/'analysis/CALL_ESTIMATE.json',{'planned_calls':len(jobs),'cases':27,'arms':2,'replicates':2,'peak_concurrency':8,
  'estimated_prompt_tokens':sum(estimates),'prompt_range':[min(estimates),max(estimates)],'tokenizer':'cl100k_base proxy; actual DeepSeek tokens can differ',
  'historical_observed_usage_responses':len(old),'completion_quantiles':{'p50':q(.5),'p90':q(.9),'p95':q(.95),'max':max(old)},
  'completion_exposure_at_historical_median':len(jobs)*q(.5),'completion_exposure_at_observed_65535_tail':len(jobs)*65535,
  'tail_caveat':'65,535-token completion previously observed; omit max_tokens means observed-tail scenario is not a hard maximum or provider guarantee.',
  'currency_cost':'Not estimated; no live price verification. Unknown response usage remains unknown.'})
 history={s:sha(ROOT/s) for s in git('ls-files','experiments').splitlines() if s and not s.startswith(rel(P)+'/') and (ROOT/s).is_file()}
 write(P/'analysis/HISTORICAL_HASHES.json',history)

def freeze():
 assert not (P/'e1_obligation/calls').exists()
 preflight(read(P/'e1_obligation/SCHEDULE.json'),bank(),read(P/'CONFIG.json'))
 assert read(P/'analysis/OFFLINE_TESTS.json')['passed']
 files={rel(p):sha(p) for p in sorted(P.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='FREEZE.json'}
 write(P/'FREEZE.json',{'base_commit':'fb61da13d3be2511f37da590429ebea7f706bd0d','preparation_head':git('rev-parse','HEAD'),
  'files':files,'calls':108,'arms':['O0','O1'],'replicates':2,'gates':{'strict':.8,'GoalGrounded':.9,'Unresolved':.9,'ScopeFaithful':.9,'NonDownstream':.9,'broadness_max':.1,'wrong_relation_arguments_max':.05,'schema':.95,'stable_both_valid':.8},
  'failure_policy':'All scheduled slots remain denominator; no retry/resample/repair; stop batch on provider contract/access/billing errors; retain unknown usage. Stop on E1 failure; E1 pass alone permits separate E2 reference/schedule freeze. Stop after E2 regardless of outcome.'})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','freeze']);globals()[p.parse_args().mode]()
