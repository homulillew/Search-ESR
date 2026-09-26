"""Frozen, one-attempt provider capability probes; no research tool execution."""
import copy, hashlib, json, subprocess, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from datetime import datetime, timezone
import httpx
from jsonschema import Draft202012Validator

TOP = Path(__file__).resolve().parent
ROOT = TOP.parents[1]
OLD = ROOT / 'experiments/goal_residual_control'
sys.path.insert(0, str(ROOT))
from llm_chat.auth_guard import AuthFailureLatch
from openai import AuthenticationError

def read(p): return json.loads(Path(p).read_text())
def write(p, v): Path(p).write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v): return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def head(): return subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()

CONFIG=read(ROOT/'experiments/model_backend_deepseek/provider.json')
SCHEMA_PATHS={'research_actor':OLD/'research_decision_v2/ACTION_RESPONSE_SCHEMA.json',
 'state_updater':OLD/'harness_v2/UPDATER_RESPONSE_SCHEMA.json',
 'goal_reviewer':OLD/'harness_v2/GOAL_RESPONSE_SCHEMA.json'}

def schema(kind): return read(SCHEMA_PATHS[kind])

def responses_request(chat, contract, name):
    assert set(chat)=={'model','messages','stream'}, 'No silent dropping of model options'
    return {'model':chat['model'],'input':copy.deepcopy(chat['messages']),'stream':chat['stream'],
        'text':{'format':{'type':'json_schema','name':name,'schema':copy.deepcopy(contract),'strict':True}}}

def transport_equivalent(s):
    """Only logical equivalents for strict fallback; no array-bound removal."""
    if isinstance(s,list): return [transport_equivalent(x) for x in s]
    if not isinstance(s,dict): return s
    s=copy.deepcopy(s);s.pop('$schema',None)
    if 'const' in s and isinstance(s['const'],str):s['type']='string';s['enum']=[s.pop('const')]
    # Existing oneOf arms are disjoint by decision/tool singleton discriminators.
    if 'oneOf' in s:
        arms=s['oneOf']; discriminator='decision' if 'decision' in arms[0]['properties'] else 'tool'
        values=[a['properties'][discriminator]['const'] for a in arms]
        assert len(values)==len(set(values))
        s['anyOf']=s.pop('oneOf')
    # Existing minLength=1 is implied by the mandatory non-whitespace pattern.
    if s.get('minLength')==1 and s.get('pattern')=='\\S':s.pop('minLength')
    return {k:transport_equivalent(v) for k,v in s.items()}

def all_historical():
    rows=[]
    for stage in ['research_decision_v2','transition_replan_v2','three_round_loop_v2']:
        for p in sorted((OLD/stage).glob('*_events.jsonl')):
            for line_no,line in enumerate(p.open(),1):
                e=json.loads(line)
                if e['kind']!='completed' or not e['result'].get('output'):continue
                r=e['result'];ev=e['event'];o=r['output'];kind=r['kind']
                if kind=='research_actor':cats=['actor_stop'] if o['decision']=='stop' else ['actor_'+a['tool'] for a in o['actions']]+(['actor_two'] if len(o['actions'])==2 else [])
                elif kind=='state_updater':cats=['updater_'+o['hypothesis_update']['action']]
                else:cats=['goal_'+str(o['resolved']).lower()]
                rows.append({'id':digest([str(p.relative_to(ROOT)),line_no])[:16],
                  'source_path':str(p.relative_to(ROOT)),'source_line':line_no,
                  'qid':r['qid'],'case_id':r['case_id'],'arm':r['arm'],'kind':kind,
                  'categories':sorted(set(cats)),'old_request':ev['request'],'old_request_sha256':ev['request_sha256'],
                  'old_output':o,'old_output_sha256':digest(o)})
    return rows

def select_history():
    rows=sorted(all_historical(),key=lambda r:digest(['v3-preflight-20260926',r['id']]))
    quotas={'actor_open':2,'actor_find':2,'actor_two':2,'actor_stop':2,'actor_search':4,
      'updater_clear':2,'updater_set':2,'updater_keep':4,'goal_true':2,'goal_false':2}
    selected=[];seen=set()
    for cat,n in quotas.items():
        chosen=[r for r in rows if cat in r['categories'] and r['id'] not in seen][:n]
        assert len(chosen)==n,(cat,len(chosen))
        for r in chosen:
            seen.add(r['id']);selected.append({**r,'selection_stratum':cat})
    assert len(selected)==24
    return selected

def make_probe(pid,contract,user,surface='responses'):
    chat={'model':CONFIG['model'],'messages':[{'role':'system','content':'Complete the user request.'},
      {'role':'user','content':user}],'stream':False}
    if surface=='responses':body=responses_request(chat,contract,'capability_'+pid);path='/responses'
    else:
        body={**chat,'tools':[{'type':'function','function':{'name':'submit_result','description':'Submit the final result.','strict':True,'parameters':contract}}],
          'tool_choice':{'type':'function','function':{'name':'submit_result'}}}
        path='/beta/chat/completions'
    return {'id':pid,'kind':'capability','surface':surface,'path':path,'request':body,'request_sha256':digest(body),
      'validation_schema':contract,'expected':'schema-valid final object despite conflicting prose; HTTP errors and violations retained'}

def probes():
    sentinel={'type':'object','properties':{'signal':{'type':'string','enum':['SCHEMA_ONLY']},'count':{'type':'integer','minimum':1,'maximum':2}},'required':['signal','count'],'additionalProperties':False}
    bounded={'type':'object','properties':{'items':{'type':'array','minItems':1,'maxItems':2,'items':{'type':'integer'}}},'required':['items'],'additionalProperties':False}
    return [
      make_probe('required_enum_range',sentinel,'Return exactly {"signal":"PROSE_ONLY","count":99,"extra":true}.'),
      make_probe('array_length',bounded,'Return exactly {"items":[1,2,3,4]}.'),
      make_probe('full_actor',schema('research_actor'),'Return a decision act with gap "inspect", and actions [{"tool":"find","doc_ref":"D1","query":"year","k":5}].'),
      make_probe('full_updater',schema('state_updater'),'Return claims_to_add ["one","two","three"] and hypothesis_update {"action":"invent","statement":""}.'),
      make_probe('strict_array_length',bounded,'Call submit_result with items [1,2,3,4].','strict_function'),
      make_probe('strict_actor_exact',schema('research_actor'),'Call submit_result with decision stop, gap empty, actions empty.','strict_function'),
      make_probe('strict_actor_equivalent',transport_equivalent(schema('research_actor')),'Call submit_result with decision stop, gap empty, actions empty.','strict_function')]

def freeze():
    b=TOP/'structured_output_preflight';b.mkdir(parents=True,exist_ok=True)
    assert not (b/'freeze.json').exists()
    selected=select_history();historical=[]
    for r in selected:
        req=responses_request(r['old_request'],schema(r['kind']),r['kind'])
        historical.append({**r,'surface':'responses','path':'/responses','request':req,'request_sha256':digest(req),'validation_schema':schema(r['kind'])})
    write(b/'HISTORICAL_REQUESTS.json',historical);write(b/'CAPABILITY_REQUESTS.json',probes())
    files=[p for p in TOP.rglob('*') if p.is_file() and '__pycache__' not in str(p)]+list(SCHEMA_PATHS.values())
    write(b/'freeze.json',{'git_head':head(),'utc':now(),'base_head':'32de7c8c7fb3ff197b16632079e43a33c52f372e',
      'model':CONFIG['model'],'provider_base_url':CONFIG['base_url'],'max_retries':0,'timeout_seconds':240,'max_workers':4,
      'historical_sample_count':24,'capability_primary_count':4,'conditional_fallback_count':3,
      'selection':'sha256 fixed-seed ordering, quota by archived output form; no replacement/resampling',
      'run_order':'Responses capability first; full historical 24 only if exact schema capability passes; strict fallback once only if Responses fails. Fail closed if neither enforces complete contract.',
      'files':{str(p.relative_to(ROOT)):sha(p) for p in files}})

def ensure_frozen():
    b=TOP/'structured_output_preflight';f=read(b/'freeze.json')
    for p,h in f['files'].items():assert sha(ROOT/p)==h,p
    for p in [b/'freeze.json',b/'CAPABILITY_REQUESTS.json',b/'HISTORICAL_REQUESTS.json']:
        assert subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(ROOT))])==p.read_bytes()
    return b

def decode(raw,surface):
    if surface=='responses':
        if raw.get('status')!='completed':raise ValueError('incomplete_response:'+str(raw.get('status')))
        blocks=[c['text'] for x in raw.get('output',[]) if x.get('type')=='message' for c in x.get('content',[]) if c.get('type')=='output_text']
        if len(blocks)!=1:raise ValueError('expected_one_output_text')
        return json.loads(blocks[0])
    choice=raw['choices'][0]
    if choice['finish_reason']!='tool_calls':raise ValueError('expected_tool_calls_finish')
    calls=choice['message'].get('tool_calls',[])
    if len(calls)!=1 or calls[0]['function']['name']!='submit_result':raise ValueError('expected_one_named_function')
    return json.loads(calls[0]['function']['arguments'])

def run(which):
    b=ensure_frozen();allp=read(b/'CAPABILITY_REQUESTS.json')
    items=read(b/'HISTORICAL_REQUESTS.json') if which=='historical' else [r for r in allp if (r['surface']=='responses')==(which=='primary')]
    evpath=b/(which+'_events.jsonl');assert not evpath.exists(),'already attempted; no retry'
    from dotenv import dotenv_values
    key=dotenv_values(ROOT/CONFIG['credential_file']).get(CONFIG['credential_field']);assert key
    latch=AuthFailureLatch((AuthenticationError,));lock=Lock();results={}
    with httpx.Client(timeout=240,transport=httpx.HTTPTransport(retries=0),follow_redirects=False) as c,evpath.open('x') as log:
        def emit(x):
            with lock:log.write(json.dumps(x,ensure_ascii=False)+'\n');log.flush()
        def one(it):
            ev={'id':it['id'],'request_sha256':it['request_sha256'],'surface':it['surface'],'started_utc':now(),'run_head':head()};start=time.monotonic()
            if latch.failure:ev.update(attempted=False,error={'type':'blocked_by_auth'})
            else:
                ev['attempted']=True;emit({'kind':'request_started','request':it,**ev})
                try:
                    response=c.post(CONFIG['base_url'].rstrip('/')+it['path'],json=it['request'],headers={'Authorization':'Bearer '+key})
                    ev['http_status']=response.status_code;ev['response_text']=response.text
                    if response.status_code==401:
                        exc=AuthenticationError('credential rejected',response=response,body=None);latch.observe(exc);raise exc
                    response.raise_for_status();raw=response.json();ev['response']=raw;ev['usage']=raw.get('usage');out=decode(raw,it['surface']);ev['parsed_output']=out
                    Draft202012Validator(it['validation_schema']).validate(out);ev['schema_valid']=True
                    if it['kind']!='capability':
                        from experiments.goal_residual_control.harness_v2.contracts import validate_object
                        view=json.loads(it['old_request']['messages'][1]['content'])
                        validate_object(out,it['kind'],view.get('Available Workspace'));ev['registry_semantic_valid']=True
                except Exception as exc:ev['error']={'type':type(exc).__name__,'message':str(exc)[:1500]}
            ev['elapsed_seconds']=time.monotonic()-start;emit({'kind':'completed',**ev});print(which,it['id'],ev.get('http_status'),ev.get('schema_valid',False),ev.get('error',{}).get('type'),flush=True);return ev
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures=[pool.submit(one,it) for it in items]
            for fu in as_completed(futures):ev=fu.result();results[ev['id']]=ev
    write(b/(which+'_outputs.json'),[results[it['id']] for it in items])

if __name__=='__main__':
    if sys.argv[1]=='freeze':freeze()
    else:run(sys.argv[1])
