"""One-attempt transport with independently measured output, schema and usage."""
import datetime,hashlib,json,subprocess,threading,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import httpx
from dotenv import dotenv_values
from jsonschema import Draft202012Validator
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def rd(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dg(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def head():return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
C=rd(P/'CONFIG.json')
NEED_SCHEMA={'type':'object','properties':{'decision':{'const':'research'},'need':{'type':'string','minLength':1,'pattern':'\\S'}},'required':['decision','need'],'additionalProperties':False}
def check_freeze(path):
 f=rd(path);runhead=head()
 assert subprocess.check_output(['git','show',runhead+':'+str(Path(path).relative_to(ROOT))],cwd=ROOT)==Path(path).read_bytes()
 for name,h in f['files'].items():assert sha(ROOT/name)==h,(name,'changed frozen file')
 return f
class Transport:
 def __init__(self):
  self.key=dotenv_values(ROOT/C['credential_file']).get(C['credential_field']);assert self.key,'missing credential'
  self.client=httpx.Client(timeout=C['timeout_seconds'],transport=httpx.HTTPTransport(retries=0),follow_redirects=False)
  self.auth=threading.Event();self.lock=threading.Lock();self.active=0;self.peak=0;self.count=0;self.runhead=head()
 def close(self):self.client.close()
 def call(self,directory,ident,request,schema=NEED_SCHEMA):
  directory=Path(directory);directory.mkdir(parents=True,exist_ok=True);prefix=directory/ident
  assert not prefix.with_suffix('.request.json').exists(),'attempt exists; no retry'
  assert 'json' in request['messages'][0]['content'].lower(),'JSON-mode literal missing from system prompt'
  save(prefix.with_suffix('.request.json'),{'request':request,'request_sha256':dg(request),'head':self.runhead,'started_utc':now()})
  r={'id':ident,'attempted':False,'request_sha256':dg(request),'finish_reason':None,'final_output_exists':False,'parse_valid':False,'schema_valid':False,'final_valid_JSON':False,'output':None,'usage':None,'error':None};start=time.monotonic();category='transport'
  if self.auth.is_set():r['error']={'category':'auth_circuit_breaker'}
  else:
   r['attempted']=True
   with self.lock:self.active+=1;self.peak=max(self.peak,self.active)
   try:
    resp=self.client.post(C['base_url']+'/chat/completions',json=request,headers={'Authorization':'Bearer '+self.key})
    save(prefix.with_suffix('.response.json'),{'status':resp.status_code,'body':resp.text,'completed_utc':now()})
    if resp.status_code==401:self.auth.set()
    resp.raise_for_status();raw=resp.json();r['response_model']=raw.get('model');r['usage']=raw.get('usage');choice=raw['choices'][0];r['finish_reason']=choice['finish_reason'];content=choice['message'].get('content') or '';r['final_output_exists']=bool(content.strip());r['final_content_chars']=len(content);category='schema'
    if r['usage']:
     u=r['usage'];reason=u.get('completion_tokens_details',{}).get('reasoning_tokens');r['token_accounting']={'input':u.get('prompt_tokens'),'output':u.get('completion_tokens'),'reasoning':reason,'final':u['completion_tokens']-reason if reason is not None else None,'reasoning_output_ratio':reason/u['completion_tokens'] if reason is not None and u['completion_tokens'] else None,'hit':u.get('prompt_cache_hit_tokens'),'miss':u.get('prompt_cache_miss_tokens')}
    if r['finish_reason']!='stop':category='length' if r['finish_reason']=='length' else 'incomplete';raise ValueError('finish_reason='+str(r['finish_reason']))
    out=json.loads(content);r['parse_valid']=True;Draft202012Validator(schema).validate(out);r['schema_valid']=True;r['final_valid_JSON']=True;r['output']=out
   except Exception as e:r['error']={'category':category,'type':type(e).__name__,'message':str(e)[:1200]}
   finally:
    with self.lock:self.active-=1
  r['elapsed_seconds']=time.monotonic()-start;r['completed_utc']=now();save(prefix.with_suffix('.result.json'),r)
  with self.lock:self.count+=1;print(self.count,ident,r['finish_reason'],'JSON' if r['final_valid_JSON'] else r['error'],flush=True)
  return r
 def batch(self,directory,jobs,schema=NEED_SCHEMA):
  results={}
  with ThreadPoolExecutor(max_workers=C['max_workers']) as pool:
   fs={pool.submit(self.call,directory,j['id'],j['request'],schema):j for j in jobs}
   for f in as_completed(fs):r=f.result();results[r['id']]=r
  return [results[j['id']] for j in jobs]
