"""Parallel isolated trajectories; no evaluator labels or semantic routing."""
import copy,json,os,sqlite3,sys,time,threading,subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from types import SimpleNamespace
import httpx
from jsonschema import Draft202012Validator
TOP=Path(__file__).resolve().parent;ROOT=TOP.parents[1];sys.path.insert(0,str(ROOT))
from experiments.goal_residual_control_v3.capability import read,write,sha,digest,now,head,CONFIG
from experiments.bcplus_verification.runtime import decode,usage
from experiments.deferred_recovery.tools import restore,registry,execute
from llm_chat.search_find_agent import SEARCH_FIND_TOOLS

def contract(arm,oracle=None,reg=None):
 s=read(TOP/'actor_schema.json');allowed={'search','find','open'}
 if arm=='A2':allowed.remove('find')
 if arm=='A3':allowed.remove('search')
 s['oneOf'][1]['properties']['actions']['items']['oneOf']=[a for a in s['oneOf'][1]['properties']['actions']['items']['oneOf'] if a['properties']['tool']['const'] in allowed]
 ts=copy.deepcopy([t for t in SEARCH_FIND_TOOLS if t['function']['name'] in allowed])
 if arm=='A3' and oracle and reg is not None:
  refs=[w['window_ref'] for w in reg['windows'] if w['doc_ref']==oracle]
  for a in s['oneOf'][1]['properties']['actions']['items']['oneOf']:
   if a['properties']['tool']['const']=='find':a['properties']['doc_ref']={'const':oracle}
   else:a['properties']['window_ref']={'enum':refs}
  for t in ts:
   if t['function']['name']=='find':t['function']['parameters']['properties']['doc_ref']={'const':oracle}
   else:t['function']['parameters']['properties']['window_ref']={'enum':refs}
 return s,ts

def make_request(c,arm,oracle=None):
 schema,ts=contract(arm,oracle,c['registry'])
 p=(TOP/'prompts/actor.md').read_text()
 if arm=='A1':p+='\n'+(TOP/'prompts/scope.md').read_text()
 if arm=='A3':p+=f'\nFor this diagnostic only, the required evidence is located somewhere in document {oracle}.\n'
 view={'Original Question':c['question'],'Current Claims':[x['statement'] for x in c['claims']],
 'Working Hypothesis':c['hypothesis'],'Current Research Need':c['need'],
 'Historical Document Catalog':[{k:d[k] for k in ['doc_ref','title','url']} for d in c['registry']['documents']],
 'Recent Attempts':c['attempts'],'New Observations':[{k:w[k] for k in ['window_ref','doc_ref','title','url','text']} for w in c['registry']['windows']],
 'Budget':{'remaining_decisions':2-len(c.get('decisions',[])),'max_actions_this_decision':1},
 'Tool schema':ts,'Response schema':schema}
 return {'model':CONFIG['model'],'messages':[{'role':'system','content':p},{'role':'user','content':json.dumps(view,ensure_ascii=False)}],'stream':False,'response_format':{'type':'json_object'}}

def validate(out,c,arm,oracle):
 Draft202012Validator(contract(arm,oracle,c['registry'])[0]).validate(out)
 if out['decision']=='stop':return
 a=out['actions'][0];docs={d['doc_ref'] for d in c['registry']['documents']};ws={w['window_ref']:w for w in c['registry']['windows']}
 if 'query' in a and (not a['query'].strip() or len(a['query'])>16000):raise ValueError('invalid_query')
 if a['tool']=='find':
  if a['doc_ref'] not in docs:raise ValueError('unknown_document')
  if arm=='A3' and a['doc_ref']!=oracle:raise ValueError('oracle_document_scope_violation')
 if a['tool']=='open':
  if a['window_ref'] not in ws:raise ValueError('unknown_window')
  if arm=='A3' and ws[a['window_ref']]['doc_ref']!=oracle:raise ValueError('oracle_window_scope_violation')

class LockedModel:
 def __init__(self,model):self.model=model;self.lock=threading.Lock()
 def __call__(self,**kwargs):
  with self.lock:return self.model(**kwargs)

class SearchProxy:
 def __init__(self,shared):
  self.index=shared.index;self.docids=shared.docids;self.device=shared.device;self.model=shared.model
  self.tokenizer=copy.deepcopy(shared.tokenizer)
  self.db=sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
 def search(self,query,k=5):
  from BCPlus.scripts.search_bcplus import BCPlusSearcher
  return BCPlusSearcher.search(self,query,k)
 def close(self):self.db.close()

def check(stage='r1'):
 f=read(TOP/stage/'FREEZE.json')
 for p,h in f['files'].items():assert sha(ROOT/p)==h,p
 for p,s in f['binary_files'].items():
  st=Path(p).stat();assert st.st_size==s['size'] and st.st_mtime_ns==s['mtime_ns'],p
 assert subprocess.check_output(['git','show',f'HEAD:experiments/evidence_scope_localization/{stage}/FREEZE.json'])==(TOP/stage/'FREEZE.json').read_bytes()

def prepare(stage='r1'):
 cells={x['case_id']:x for x in read(TOP/'bank/RUNTIME_INPUTS.json')};manifest=read(TOP/stage/'MANIFEST.json')
 initial=[{'case_id':m['case_id'],'arm':m['arm'],'request':make_request(cells[m['case_id']],m['policy_arm'],m.get('oracle'))} for m in manifest]
 write(TOP/stage/'INITIAL_REQUESTS.json',initial)

def run(stage='r1',tool_adapter=None):
 check(stage);base=TOP/stage;assert not (base/'STARTED.json').exists(),'No repeated attempts'
 write(base/'STARTED.json',{'utc':now(),'head':head(),'max_retries':0,'workers':8,'gpu':'cuda:1'});wall=time.monotonic()
 # Retrieval initialization is shared; the production class and search method stay unchanged.
 os.environ['BCPLUS_DEVICE']='cuda:1'
 from BCPlus.scripts.search_bcplus import BCPlusSearcher
 shared=BCPlusSearcher();shared.model=LockedModel(shared.model)
 from dotenv import dotenv_values
 key=dotenv_values(ROOT/CONFIG['credential_file']).get(CONFIG['credential_field']);assert key
 auth=threading.Event();cells={x['case_id']:x for x in read(TOP/'bank/RUNTIME_INPUTS.json')}
 initial={(r['case_id'],r['arm']):r['request'] for r in read(base/'INITIAL_REQUESTS.json')}
 order=sorted(read(base/'MANIFEST.json'),key=lambda m:digest(['scope-order-v1',m['case_id'],m['arm']]))
 done={};(base/'cells').mkdir(exist_ok=False)
 with httpx.Client(timeout=240,transport=httpx.HTTPTransport(retries=0),follow_redirects=False) as client:
  def one(m):
   cid=m['case_id'];arm=m['arm'];pa=m['policy_arm'];oracle=m.get('oracle');c=copy.deepcopy(cells[cid]);c.update(arm=arm,decisions=[],status='active',started_utc=now())
   outdir=base/'cells'/f'{cid}__{arm}';outdir.mkdir(exist_ok=False)
   t=None;proxy=None
   try:
    proxy=SearchProxy(shared);t=restore(c['registry'],proxy)
    if tool_adapter is not None:tool_adapter(t)
    for step in range(2):
     req=make_request(c,pa,oracle)
     if step==0:assert req==initial[cid,arm]
     request_path=outdir/f'decision{step+1}_request.json';write(request_path,req)
     write(outdir/f'decision{step+1}_REQUEST_FREEZE.json',{'utc':now(),'head':head(),'request_sha256':digest(req),'request_file_sha256':sha(request_path),'prefix_sha256':digest({k:c[k] for k in ['question','claims','hypothesis','need','attempts','registry']}),'previous_decision_sha256':digest(c['decisions'][-1]) if c['decisions'] else None})
     d={'step':step+1,'actor':{'request_sha256':digest(req),'started_utc':now(),'output':None,'usage':None,'error':None,'attempted':False},'tool':None};start=time.monotonic();a=d['actor'];category='provider/API failure'
     if auth.is_set():a['error']={'category':category,'type':'blocked_by_auth'}
     else:
      a['attempted']=True
      try:
       resp=client.post(CONFIG['base_url'].rstrip('/')+'/chat/completions',json=req,headers={'Authorization':'Bearer '+key})
       raw={'http_status':resp.status_code,'text':resp.text};write(outdir/f'decision{step+1}_raw_response.json',raw)
       if resp.status_code==401:auth.set()
       resp.raise_for_status();raw=resp.json();a['usage']=usage(raw,'json_mode_fallback');category='transport_structural_failure'
       try:o=decode(raw,'json_mode_fallback')
       except RuntimeError:category='length/incomplete failure';raise
       Draft202012Validator(contract(pa)[0]).validate(o);category='harness_control_violation';validate(o,c,pa,oracle);a['output']=o
      except Exception as e:a['error']={'category':category,'type':type(e).__name__,'message':str(e)[:1500]}
     a.update(elapsed_seconds=time.monotonic()-start,completed_utc=now());c['decisions'].append(d)
     write(outdir/'checkpoint.json',c)
     if a['output'] is None:c['status']='actor_failure';break
     if a['output']['decision']=='stop':c['status']='actor_stop';break
     d['tool_started_utc']=now();write(outdir/'checkpoint.json',c)
     d['tool']=execute(t,a['output']['actions'][0]);d['tool_completed_utc']=now();c['registry']=registry(t)
     r=d['tool']
     c['attempts'].append({'action':r['action'],'status':r['result']['status'] if r['result'] else 'tool_error','returned_windows':[w['window_ref'] for w in r['observations']]})
     print(stage,cid,arm,'step',step+1,r['action']['tool'],'ok' if not r['error'] else r['error'],flush=True)
     write(outdir/'checkpoint.json',c)
     if r['error']:c['status']='tool_failure';break
    if c['status']=='active':c['status']='budget_exhausted'
   except Exception as e:
    c['status']='runtime_failure';c['runtime_error']={'type':type(e).__name__,'message':str(e)[:1500]}
   finally:
    if t is not None:t.close()
    if proxy is not None:proxy.close()
   c['completed_utc']=now();write(outdir/'RESULT.json',c);print('completed',cid,arm,c['status'],flush=True);return c
  with ThreadPoolExecutor(max_workers=8) as pool:
   for f in as_completed([pool.submit(one,m) for m in order]):
    c=f.result();done[c['case_id']+':'+c['arm']]=c
 shared.close();write(base/'RESULTS.json',done);write(base/'COMPLETED.json',{'utc':now(),'head':head(),'wall_seconds':time.monotonic()-wall,'trajectories':len(done),'max_retries':0})

if __name__=='__main__':
 mode=sys.argv[1];stage=sys.argv[2] if len(sys.argv)>2 else 'r1'
 globals()[mode](stage)
