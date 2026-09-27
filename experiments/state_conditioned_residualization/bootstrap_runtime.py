"""Single-attempt query/probe transport and unchanged local Search adapter."""
import os,time,threading
from concurrent.futures import ThreadPoolExecutor,as_completed
from .common import *
from experiments.skeleton_state_alignment.prepare import credential
from experiments.skeleton_state_alignment.run import accounting,now
from experiments.minimal_need_multiquery.run import usage_audit

def request(payload,prompt='query_generator'):
 return {'model':'deepseek-flash','temperature':0,'stream':False,'response_format':{'type':'json_object'},'messages':[
  {'role':'system','content':(P/'prompts'/f'{prompt}.txt').read_text()}, {'role':'user','content':json.dumps(payload,ensure_ascii=False)}]}
def validate(value,field):
 return isinstance(value,dict) and set(value)=={field} and isinstance(value[field],str) and bool(value[field].strip()) and len(value[field])<=16000

def build_e2():
 states={s['case_id']:s for s in read(P/'e0_reference/STATES.json')};parents={s['case_id']:s['parent'] for s in read(P/'e0_reference/PARENT_REQUIREMENTS.json')};jobs=[]
 for a in read(P/'e0_reference/ACCESSIBILITY_REFERENCE.json')['rows']:
  if a['status']!='accessible':continue
  cid=a['case_id'];s=states[cid]
  for arm in ['P0','P1']:
   objective=' '.join(x['text'] for x in parents[cid]['source_spans']);source=None;blocked=None
   if arm=='P1':
    path=P/'e1_residualization/calls'/f'R0__{cid}__R1.result.json';r=read(path);source={'path':rel(path),'sha256':sha(path)}
    if not r['valid_output']:blocked='invalid_E1_R0_replicate1'
    elif r['output']['mode']!='probe':blocked='nonprobe_E1_R0_replicate1'
    else:objective=r['output']['local_residual']
   req=None if blocked else request({'Original Question':s['question'],'Research Objective':objective})
   jobs.append({'id':f'{arm}__{cid}__R1','stage':'e2_bootstrap','case_id':cid,'state_id':s['state_id'],'qid':s['qid'],'arm':arm,'replicate':1,
    'request':req,'request_sha256':digest(req),'field':'query','source':source,'blocked_reason':blocked})
 return sorted(jobs,key=lambda j:digest(['bootstrap-query-order-v1',j['id']]))

def seal(directory,extra=None):
 d=P/directory
 deps=[P/'CONFIG.json',P/'AUTHORIZATION.json',P/'GATES.json',P/'FREEZE.json',P/'bootstrap_runtime.py',P/'bootstrap_prepare.py',P/'bootstrap_freeze.py',P/'e0_reference/ACCESSIBILITY_REFERENCE.json',P/'e2_bootstrap/PREFIX_REGISTRIES.json',P/'e2_bootstrap/RUBRIC.md',P/'e2_bootstrap/BACKEND.json',d/'SCHEDULE.json',*sorted((P/'prompts').glob('*.txt'))]
 if extra:deps.extend(extra)
 write(d/'FREEZE.json',{'head_before_seal':git('rev-parse','HEAD'),'created_utc':now(),'files':{rel(p):sha(p) for p in deps},'schedule_count':len(read(d/'SCHEDULE.json')),'max_retries':0,'max_workers':8,'horizon':1})

def audit(directory):
 d=P/directory;f=read(d/'FREEZE.json');committed(d/'FREEZE.json')
 for name,h in f['files'].items():assert sha(ROOT/name)==h,name;committed(ROOT/name)
 for name,h in read(P/'FREEZE.json')['files'].items():assert sha(ROOT/name)==h,name
 for name,h in read(P/'e2_bootstrap/BACKEND.json')['code_sha256'].items():assert sha(ROOT/name)==h,name
 for name,info in read(P/'e2_bootstrap/BACKEND.json')['assets'].items():
  s=Path(name).stat();assert (s.st_size,s.st_mtime_ns)==(info['size'],info['mtime_ns']),name
 if directory=='e2_bootstrap':assert read(d/'SCHEDULE.json')==build_e2()
 assert read(P/'e1_residualization/METRICS.json')['bootstrap_eligible']
 return git('rev-parse','HEAD')

def parse(status,body,j):
 r=dict(valid_json=False,valid_output=False,output=None,usage=None,response_model=None,finish_reason=None,failure=None)
 try:
  raw=json.loads(body);r.update(usage=raw.get('usage'),response_model=raw.get('model'))
  if status!=200:r['failure']='http_error';return r
  c=raw['choices'][0];r['finish_reason']=c['finish_reason']
  if raw.get('model')!=j['request']['model']:r['failure']='model_mismatch'
  elif c['finish_reason']!='stop':r['failure']='length' if c['finish_reason']=='length' else 'incomplete_finish'
  else:
   try:o=json.loads(c['message']['content'])
   except (ValueError,TypeError):r['failure']='invalid_json'
   else:
    r.update(output=o,valid_json=True,valid_output=validate(o,j['field']))
    if not r['valid_output']:r['failure']='output_contract'
 except (ValueError,KeyError,IndexError,AttributeError,TypeError):r['failure']='response_schema_error'
 return r

def load_rows(directory):
 d=P/directory;rows=[]
 for j in read(d/'SCHEDULE.json'):
  path=d/'calls'/f"{j['id']}.result.json"
  if path.exists():r=read(path)
  else:r={k:j[k] for k in ['id','stage','case_id','state_id','qid','arm','replicate','request_sha256']};r.update(attempted=False,valid_json=False,valid_output=False,output=None,usage=None,failure=j.get('blocked_reason') or 'not_started')
  rows.append(r)
 return rows

def execute_models(directory):
 d=P/directory;head=audit(directory);config=read(P/'CONFIG.json');key=credential();jobs=read(d/'SCHEDULE.json')
 assert not (d/'RUN.json').exists() and not (d/'calls').exists(),'No repeated attempts'
 write(d/'RUN.json',{'head':head,'utc':now(),'freeze_sha256':sha(d/'FREEZE.json'),'slots':len(jobs)})
 import httpx
 lock=threading.Lock();halt=threading.Event();active=0;peak=0;t=time.monotonic()
 with httpx.Client(timeout=config['timeout_seconds'],transport=httpx.HTTPTransport(retries=0),follow_redirects=False) as client:
  def one(j):
   nonlocal active,peak
   path=d/'calls'/j['id'];r={k:j[k] for k in ['id','stage','case_id','state_id','qid','arm','replicate','request_sha256']};r.update(head=head,attempted=False,valid_output=False,valid_json=False,output=None,usage=None,failure=None)
   if j['request'] is None or halt.is_set():
    r['failure']=j.get('blocked_reason') or 'halted_unsent';write(path.with_suffix('.result.json'),r);return
   with lock:active+=1;peak=max(peak,active)
   start=time.monotonic()
   try:
    write(path.with_suffix('.request.json'),{'request':j['request'],'request_sha256':j['request_sha256'],'head':head})
    write(path.with_suffix('.attempt.json'),{'send_intent_utc':now(),'id':j['id']});r['attempted']=True
    try:resp=client.post(config['endpoint'],json=j['request'],headers={'Authorization':'Bearer '+key})
    except httpx.RequestError as exc:r.update(failure='timeout' if isinstance(exc,httpx.TimeoutException) else 'transport_error',error_type=type(exc).__name__)
    else:
     if resp.status_code in config['halt_http_statuses']:halt.set()
     write(path.with_suffix('.response.json'),{'status':resp.status_code,'body':resp.text,'completed_utc':now()});r.update(http_status=resp.status_code,**parse(resp.status_code,resp.text,j))
    r.update(elapsed_seconds=time.monotonic()-start,accounting=usage_audit(r['usage']),completed_utc=now());write(path.with_suffix('.result.json'),r)
    print(directory,j['id'],'valid' if r['valid_output'] else r['failure'],flush=True)
   finally:
    with lock:active-=1
  try:
   with ThreadPoolExecutor(max_workers=8) as pool:
    for f in as_completed([pool.submit(one,j) for j in jobs]):f.result()
  finally:write(d/'ACCOUNTING.json',{**accounting(load_rows(directory)),'wall_seconds':time.monotonic()-t,'peak_concurrency':peak})

def retrieve(directory):
 d=P/directory;head=audit(directory);jobs=read(d/'SCHEDULE.json');rows={r['id']:r for r in load_rows(directory)}
 committed(d/'ACCOUNTING.json')
 for r in rows.values():committed(d/'calls'/f"{r['id']}.result.json")
 assert not (d/'RETRIEVAL_RUN.json').exists()
 write(d/'RETRIEVAL_RUN.json',{'head':head,'utc':now(),'backend_sha256':sha(P/'e2_bootstrap/BACKEND.json'),'queries_sha256':digest(rows)})
 os.environ['BCPLUS_DEVICE']='cuda:1'
 import faiss;faiss.omp_set_num_threads(1)
 from BCPlus.scripts.search_bcplus import BCPlusSearcher
 from experiments.evidence_scope_localization.runtime import LockedModel,SearchProxy
 from experiments.deferred_recovery.tools import restore,registry,execute
 shared=BCPlusSearcher();shared.model=LockedModel(shared.model);regs=read(d/'RETRIEVAL_REGISTRIES.json') if (d/'RETRIEVAL_REGISTRIES.json').exists() else read(P/'e2_bootstrap/PREFIX_REGISTRIES.json')
 start=time.monotonic()
 def one(j):
  r=rows[j['id']];path=d/'retrieval'/f"{j['id']}.json";out={'id':j['id'],'case_id':j['case_id'],'arm':j['arm'],'attempted':False,'error':None,'tool':None,'registry':None}
  if not r['valid_output']:out['error']='query_source_failure:'+str(r['failure']);write(path,out);return out
  proxy=None;t=None
  try:
   proxy=SearchProxy(shared);t=restore(regs[j['case_id']],proxy)
   write(d/'retrieval'/f"{j['id']}.attempt.json",{'query':r['output']['query'],'k':5,'utc':now()});out['attempted']=True
   out['tool']=execute(t,{'tool':'search','query':r['output']['query'],'k':5});out['registry']=registry(t);out['error']=out['tool']['error']
  except Exception as e:out['error']={'type':type(e).__name__,'message':str(e)[:500]}
  finally:
   if t:t.close()
   if proxy:proxy.close()
  write(path,out);print('SEARCH',j['id'],'ok' if not out['error'] else out['error'],flush=True);return out
 try:
  with ThreadPoolExecutor(max_workers=4) as pool:done=[f.result() for f in as_completed([pool.submit(one,j) for j in jobs])]
 finally:shared.close()
 write(d/'RETRIEVAL_ACCOUNTING.json',{'head':head,'attempted':sum(x['attempted'] for x in done),'errors':sum(x['attempted'] and bool(x['error']) for x in done),'wall_seconds':time.monotonic()-start,'workers':4,'embedding_forward':'shared original method with lock; ranking/localizer unchanged','find_open_calls':0})
if __name__=='__main__':
 import sys
 globals()[sys.argv[1]](sys.argv[2])
