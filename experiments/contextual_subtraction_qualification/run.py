"""Frozen one-attempt E1 transport; bounded parallel calls and raw retention."""
import argparse,threading,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from .common import *
from .inputs import build_schedule,validate,bank
from experiments.skeleton_state_alignment.prepare import credential
from experiments.skeleton_state_alignment.run import accounting as base_accounting,now
from experiments.minimal_need_multiquery.run import usage_audit
OUT=P/'e1_qualification'
def jobs():return read(OUT/'SCHEDULE.json')
def accounting(rows):
 audits=[usage_audit(r.get('usage')) for r in rows if r.get('attempted')]
 eligible=[a for a in audits if all(a['tokens'][k] is not None for k in ('input','hit','miss')) and 'hit+miss!=input' not in a['inconsistent']]
 hit=sum(a['tokens']['hit'] for a in eligible);tokens=sum(a['tokens']['input'] for a in eligible)
 return {**base_accounting(rows),'cache_hit_rate_reported_tokens':metric(hit,tokens),'cache_rate_eligible_calls':len(eligible),'cache_rate_excluded_attempts':len(audits)-len(eligible),'cache_rate_definition':'sum hit / sum prompt tokens on calls with complete consistent input/hit/miss counters; excludes unknown usage, not a whole-run spending estimate'}
def authorization():
 p=P/'AUTHORIZATION_E1.json'
 if not p.exists():raise PermissionError('Current task-scoped E1 authorization record missing')
 a=read(p);committed(p)
 assert a['stage']=='E1' and a['maximum_attempts']==192
 assert a['freeze_sha256']==sha(P/'FREEZE.json') and a['task_sha256']==sha(P/'TASK.md')
 assert a['user_message'].strip() and a['authorized_utc'] and a['authorization_scope']=='E1 only'
 # The human approval must be recorded honestly; this manifest is not a substitute for consent.
 return a

def audit(require_authorization=False):
 frozen=read(P/'FREEZE.json')
 for name,h in frozen['files'].items():assert sha(ROOT/name)==h,name;committed(ROOT/name)
 committed(P/'FREEZE.json');assert jobs()==build_schedule() and len(jobs())==192
 if require_authorization:authorization()
 return {'status':'PASS','head':git('rev-parse','HEAD'),'freeze_sha256':sha(P/'FREEZE.json'),'historical_files_unchanged':verify_history(),'planned':192,'paid_calls_authorized':require_authorization}

def parse(status,body,job):
 result={'valid_json':False,'valid_output':False,'output':None,'usage':None,'response_model':None,'finish_reason':None,'failure':None}
 try:raw=json.loads(body)
 except (ValueError,TypeError):raw=None
 if isinstance(raw,dict):result.update(usage=raw.get('usage'),response_model=raw.get('model'))
 if status!=200:result['failure']='http_error';return result
 try:
  choice=raw['choices'][0];result['finish_reason']=choice['finish_reason']
  if result['response_model']!=job['request']['model']:result['failure']='model_mismatch'
  elif choice['finish_reason']!='stop':result['failure']='length' if choice['finish_reason']=='length' else 'incomplete_finish'
  else:
   content=choice['message'].get('content')
   if not isinstance(content,str) or not content.strip():result['failure']='empty_output'
   else:
    try:value=json.loads(content)
    except ValueError:result['failure']='invalid_json'
    else:
     result.update(valid_json=True,output=value,valid_output=validate(value,job))
     if not result['valid_output']:result['failure']='output_contract'
 except (KeyError,IndexError,TypeError,AttributeError):result['failure']='response_schema_error'
 return result
def load_rows():
 rows=[]
 for j in jobs():
  p=OUT/'calls'/f"{j['id']}.result.json"
  if p.exists():r=read(p);assert r['request_sha256']==j['request_sha256'] and r['id']==j['id']
  else:
   attempted=(p.parent/f"{j['id']}.attempt.json").exists();r={k:j[k] for k in ('id','stage','case_id','cell_id','certificate_id','qid','arm','replicate','request_sha256')}
   r.update(attempted=attempted,valid_json=False,valid_output=False,output=None,usage=None,failure='incomplete_attempt' if attempted else 'not_started')
  rows.append(r)
 return rows
class Batch:
 def __init__(self,client,key,config,head):
  self.client,self.key,self.config,self.head=client,key,config,head;self.lock=threading.Lock();self.halt=threading.Event();self.active=self.peak=0
 def one(self,j):
  p=OUT/'calls'/j['id'];r={k:j[k] for k in ('id','stage','case_id','cell_id','certificate_id','qid','arm','replicate','request_sha256')}
  r.update(head=self.head,attempted=False,valid_json=False,valid_output=False,output=None,usage=None,started_utc=now())
  with self.lock:
   blocked=self.halt.is_set()
   if not blocked:self.active+=1;self.peak=max(self.peak,self.active)
  if blocked:r.update(failure='halted_unsent',elapsed_seconds=0);write(p.with_suffix('.result.json'),r);return
  t=time.monotonic()
  try:
   write(p.with_suffix('.request.json'),{'head':self.head,'request':j['request'],'request_sha256':j['request_sha256']})
   write(p.with_suffix('.attempt.json'),{'id':j['id'],'send_intent_utc':now()});r['attempted']=True
   try:response=self.client.post(self.config['endpoint'],json=j['request'],headers={'Authorization':'Bearer '+self.key})
   except Exception as exc:
    import httpx
    if not isinstance(exc,httpx.RequestError):self.halt.set();raise
    r.update(failure='timeout' if isinstance(exc,httpx.TimeoutException) else 'transport_error',error_type=type(exc).__name__)
   else:
    if response.status_code in self.config['halt_http_statuses']:self.halt.set()
    write(p.with_suffix('.response.json'),{'status':response.status_code,'body':response.text,'completed_utc':now()})
    r.update(http_status=response.status_code,**parse(response.status_code,response.text,j))
   r.update(elapsed_seconds=time.monotonic()-t,completed_utc=now(),accounting=usage_audit(r['usage']))
   write(p.with_suffix('.result.json'),r);print(j['id'],'valid-output' if r['valid_output'] else r['failure'],flush=True)
  except BaseException:self.halt.set();raise
  finally:
   with self.lock:self.active-=1
 def run(self,items):
  with ThreadPoolExecutor(max_workers=self.config['max_workers']) as pool:
   futures=[pool.submit(self.one,j) for j in items]
   for future in as_completed(futures):future.result()
def execute():
 check=audit(require_authorization=True);config=read(P/'CONFIG.json')
 if (OUT/'RUN.json').exists() or (OUT/'calls').exists():raise FileExistsError('No overwrite/resume/retry')
 key=credential();write(OUT/'RUN.json',{**check,'authorization_sha256':sha(P/'AUTHORIZATION_E1.json'),'started_utc':now()})
 import httpx
 t=time.monotonic();error=None
 with httpx.Client(timeout=config['timeout_seconds'],transport=httpx.HTTPTransport(retries=0),follow_redirects=False) as client:
  batch=Batch(client,key,config,check['head'])
  try:batch.run(jobs())
  except BaseException as exc:error=type(exc).__name__;raise
  finally:
   for r in load_rows():
    path=OUT/'calls'/f"{r['id']}.result.json"
    if not path.exists():write(path,r)
   write(OUT/'ACCOUNTING.json',{**accounting(load_rows()),'wall_seconds':time.monotonic()-t,'peak_concurrency':batch.peak,'harness_error':error})
def export_review():
 assert (OUT/'ACCOUNTING.json').exists();inputs=bank();packets=[];key={}
 for i,r in enumerate(sorted(load_rows(),key=lambda r:digest(['contextual-qualification-blind-v1',r['id']]))):
  bid=f'B{i+1:03d}';key[bid]=r['id']
  packets.append({'review_id':bid,'evaluation_context':inputs[r['certificate_id']],'output':r.get('output'),'schema_valid':r['valid_output']})
 write(OUT/'review/PACKETS.json',packets);write(OUT/'review/KEY.json',key)
 write(OUT/'review/DISCLOSURE.md','Single task-familiar reviewer. Arm, replicate, certificate identifier and actually supplied context mode are masked. Every packet shows full evaluation context; Q0 itself did not receive Q/Parent. Responses can indirectly reveal context awareness. Provider reasoning excluded. Gold fixed before calls; primary verdict scoring is mechanical. Missing-semantics rationale review is diagnostic and cannot relabel Gold.\n')

def seal_review():
 from .score import validate_judgment
 key=read(OUT/'review/KEY.json');judgments=read(OUT/'review/JUDGMENTS.json');rows={r['id']:r for r in load_rows()}
 assert set(key)==set(judgments) and set(key.values())==set(rows)
 for bid in key:validate_judgment(judgments[bid])
 files=[*sorted((OUT/'review').glob('*.json')),OUT/'ACCOUNTING.json',*sorted((OUT/'calls').glob('*.json'))]
 write(OUT/'review/REVIEW_SEAL.json',{'sealed_utc':now(),'head_before_review_commit':git('rev-parse','HEAD'),'files':{rel(p):sha(p) for p in files},'reviewer':'Codex single task-familiar reviewer, no provider reasoning'})

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['audit','execute','export_review','seal_review']);a=ap.parse_args();r=globals()[a.mode]()
 if r is not None:print(json.dumps(r,indent=2))
