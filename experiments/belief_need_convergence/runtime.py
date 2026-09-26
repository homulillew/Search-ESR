"""Immutable one-attempt Need experiment transport. No tool or Writer execution."""
import argparse,concurrent.futures,datetime,hashlib,json,random,subprocess,threading,time
from pathlib import Path
import httpx
from dotenv import dotenv_values
P=Path(__file__).resolve().parent;R=P.parents[1]
def rd(p):return json.loads(p.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,ensure_ascii=False).encode())
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def head():return subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
def save(p,x):
 with p.open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def validate(x,stage):
 if stage=='P3A':
  assert set(x)=={'resolved','unresolved_issue'} and x['resolved'] is False
  assert isinstance(x['unresolved_issue'],str) and x['unresolved_issue'].strip()
 else:
  assert set(x)=={'decision','need'} and x['decision']=='research'
  assert isinstance(x['need'],str) and x['need'].strip()
 return x
CONFIG=rd(P/'CONFIG.json')
def make_request(case,stage,issue=None,prompt_override=None):
 view={'Original Question':case['question'],'Verified Claims':case['claims'],'Working Hypothesis':case['hypothesis']}
 if stage=='P4':view['One confirmed unresolved issue']=issue
 if stage=='P3B':view['Ephemeral unresolved_issue']=issue
 return {'model':CONFIG['model'],'messages':[{'role':'system','content':(prompt_override or (P/'prompts'/f'{stage}.txt')).read_text()},{'role':'user','content':json.dumps(view,ensure_ascii=False)}],'stream':False,'temperature':CONFIG['temperature'],'max_tokens':CONFIG['max_tokens'],'response_format':CONFIG['response_format']}
def freeze(folder,jobs,prompt_paths=()):
 folder.mkdir(parents=True,exist_ok=False)
 paths=[P/'CONFIG.json',P/'runtime.py',P/'RUBRIC.md',P/'PROTOCOL.md',P/'HYPOTHESES.md',*sorted((P/'bank').glob('*.json')),*sorted((P/'prompts').glob('*.txt')),*prompt_paths]
 save(folder/'FREEZE.json',{'created_utc':now(),'parent_head':head(),'jobs':jobs,'paths':{str(x.relative_to(R)):sha(x.read_bytes()) for x in paths},'samples':1,'max_retries':0,'max_workers':8,'failure_policy':'terminal/no resampling; P3A failure skips P3B','tools':[]})
def run(folder):
 f=rd(folder/'FREEZE.json');assert all(sha((R/p).read_bytes())==h for p,h in f['paths'].items()),'frozen dependency changed'
 assert not (folder/'RUN.json').exists(),'already started; never retry'
 runhead=head();save(folder/'RUN.json',{'head':runhead,'started_utc':now(),'freeze_sha256':sha((folder/'FREEZE.json').read_bytes())})
 key=dotenv_values(R/CONFIG['credential_file']).get(CONFIG['credential_field']);assert key,'missing credential'
 cases={x['case_id']:x for x in rd(P/'bank/RUNTIME_INPUTS.json')};labs={x['case_id']:x for x in rd(P/'bank/LABELS.json')}
 calls=folder/'calls';calls.mkdir();lock=threading.Lock();auth=threading.Event();stats={'active':0,'peak':0,'finished':0};results=[]
 with httpx.Client(timeout=CONFIG['timeout_seconds'],transport=httpx.HTTPTransport(retries=0),follow_redirects=False) as client:
  def call(cid,stage,issue=None,override=None):
   req=make_request(cases[cid],stage,issue,P/override if override else None);path=calls/f'{cid}_{stage}';started=time.monotonic()
   record={'case_id':cid,'stage':stage,'request':req,'request_sha256':digest(req),'head':runhead,'started_utc':now()}
   save(path.with_suffix('.request.json'),record)
   result={'case_id':cid,'stage':stage,'attempted':False,'output':None,'error':None,'usage':None,'request_sha256':digest(req)}
   category='transport'
   if auth.is_set():result['error']={'category':'auth_circuit_breaker'}
   else:
    result['attempted']=True
    with lock:stats['active']+=1;stats['peak']=max(stats['peak'],stats['active'])
    try:
     res=client.post(CONFIG['base_url']+'/chat/completions',json=req,headers={'Authorization':'Bearer '+key})
     save(path.with_suffix('.response.json'),{'status_code':res.status_code,'body':res.text,'completed_utc':now()})
     if res.status_code==401:auth.set()
     res.raise_for_status();raw=res.json();result['usage']=raw.get('usage');result['response_model']=raw.get('model');category='schema'
     choice=raw['choices'][0]
     if choice['finish_reason']!='stop':category='length';raise ValueError('finish_reason='+str(choice['finish_reason']))
     result['output']=validate(json.loads(choice['message']['content']),stage)
    except Exception as e:result['error']={'category':category,'type':type(e).__name__,'message':str(e)[:1200]}
    finally:
     with lock:stats['active']-=1
   result['elapsed_seconds']=time.monotonic()-started;save(path.with_suffix('.result.json'),result)
   with lock:stats['finished']+=1;print(stats['finished'],cid,stage,'ok' if result['output'] else result['error'],flush=True)
   return result
  def one(job):
   cid=job['case_id'];arm=job['arm'];stages=[]
   if arm=='P3':
    a=call(cid,'P3A');stages.append(a)
    if a['output']:stages.append(call(cid,'P3B',a['output']['unresolved_issue']))
   else:stages.append(call(cid,arm,labs[cid]['oracle_gap'] if arm=='P4' else None,job.get('prompt_override')))
   last=stages[-1];out=last['output'] if last['stage']!='P3A' else None
   row={'case_id':cid,'arm':arm,'output':out,'call_stages':[s['stage'] for s in stages],'errors':[s['error'] for s in stages if s['error']]}
   save(folder/f'{cid}_{arm}.json',row);return row
  jobs=list(f['jobs']);random.Random(20260927).shuffle(jobs)
  with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
   for future in concurrent.futures.as_completed([pool.submit(one,j) for j in jobs]):results.append(future.result())
 save(folder/'OUTPUTS.json',sorted(results,key=lambda x:(x['case_id'],x['arm'])))
 save(folder/'SUMMARY.json',{'completed_utc':now(),'jobs':len(results),'output_success':sum(r['output'] is not None for r in results),'calls':stats['finished'],'max_concurrent_http':stats['peak'],'errors':sum(bool(r['errors']) for r in results)})
def preflight():
 cases=rd(P/'bank/RUNTIME_INPUTS.json');labels={x['case_id']:x for x in rd(P/'bank/LABELS.json')}
 assert len(cases)==55 and len({digest({k:x[k] for k in ['question','claims','hypothesis']}) for x in cases})==55
 for c in cases:
  for s in ['P0','P1','P2','P3A','P3B','P4']:
   req=make_request(c,s,'synthetic contract test' if s in ['P3B','P4'] else None);v=json.loads(req['messages'][1]['content'])
   assert v['Original Question']==c['question'] and v['Verified Claims']==c['claims'] and v['Working Hypothesis']==c['hypothesis']
   assert len(v)==(4 if s in ['P3B','P4'] else 3)
 validate({'decision':'research','need':'Which local relation remains?'},'P0');validate({'resolved':False,'unresolved_issue':'A relation'},'P3A')
 for bad in [{'decision':'stop','need':''},{'decision':'research','need':'x','confidence':1}]:
  try:validate(bad,'P0')
  except AssertionError:pass
  else:raise AssertionError('invalid output accepted')
 for pair in rd(P/'bank/DELTA_PAIRS.json'):
  a,b=pair['A'],pair['B'];assert a['question']==b['question']
  if pair['kind']=='coverage':assert b['claims']==a['claims']+[pair['real_added_claim']] and a['hypothesis']==b['hypothesis']
  else:assert a['claims']==b['claims'] and not a['hypothesis']
 print('preflight passed: input boundaries, no STOP/extra output, 55 unique states, exact Delta invariants; no network')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['preflight','freeze','run']);ap.add_argument('--folder',default='round_0');args=ap.parse_args()
 if args.action=='preflight':preflight()
 elif args.action=='freeze':freeze(P/args.folder,[{'case_id':c['case_id'],'arm':a} for c in rd(P/'bank/RUNTIME_INPUTS.json') for a in CONFIG['paths']])
 else:run(P/args.folder)
