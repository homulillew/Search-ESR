"""Separately frozen schema-representation diagnostics after initial rejections.
No old probe is retried and no research semantic prompt or output is repaired.
"""
import capability as c
import copy,json,sys,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from threading import Lock
import httpx
from jsonschema import Draft202012Validator

BASE=c.TOP/'structured_output_preflight'/'equivalent_schema_probe'

def compile_schema(s):
    s=c.transport_equivalent(s)
    def visit(x):
        if isinstance(x,list):return [visit(v) for v in x]
        if not isinstance(x,dict):return x
        x=copy.deepcopy(x)
        if 'enum' in x and all(isinstance(v,str) for v in x['enum']):x.setdefault('type','string')
        if x.get('type')=='array' and x.get('maxItems')==0 and 'items' not in x:
            # Under maxItems=0 no item can exist; its type cannot alter the language.
            x['items']={'type':'string'}
        return {k:visit(v) for k,v in x.items()}
    return visit(s)

def requests():
    out=[c.make_probe('compiled_actor_responses',compile_schema(c.schema('research_actor')),
        'Return decision act, gap inspect, actions [{"tool":"find","doc_ref":"D1","query":"year","k":5}].'),
      c.make_probe('compiled_updater_responses',compile_schema(c.schema('state_updater')),
        'Return claims_to_add ["one","two","three"] and hypothesis_update {"action":"invent","statement":""}.'),
      c.make_probe('goal_responses',c.schema('goal_reviewer'),'Return {"resolved":"yes","residual":"","extra":1}.'),
      c.make_probe('impossible_array_responses',{'type':'object','properties':{'items':{'type':'array','minItems':3,'maxItems':2,'items':{'type':'integer'}}},'required':['items'],'additionalProperties':False},
        'Return exactly {"items":[1,2,3]}.')]
    out[-1]['expected']='No schema-valid object exists: request rejected or failed generation; a completed object demonstrates bounds are not fully enforced.'
    # An explicit impossible language is a capability negative control, not a research failure repair.
    p=c.make_probe('strict_array_auto',{'type':'object','properties':{'items':{'type':'array','minItems':1,'maxItems':2,'items':{'type':'integer'}}},'required':['items'],'additionalProperties':False},
      'Call submit_result with all four separate items [1,2,3,4].','strict_function');p['request']['tool_choice']='auto';p['request_sha256']=c.digest(p['request']);out.append(p)
    p=c.make_probe('strict_compiled_actor_auto',compile_schema(c.schema('research_actor')),
      'Call submit_result with decision act, gap inspect, and one find action with doc_ref D1 and query year.','strict_function');p['request']['tool_choice']='auto';p['request_sha256']=c.digest(p['request']);out.append(p)
    return out

def freeze():
    BASE.mkdir(exist_ok=True);assert not (BASE/'freeze.json').exists()
    c.write(BASE/'REQUESTS.json',requests())
    files=[c.TOP/'capability.py',c.TOP/'capability_extension.py',c.TOP/'test_capability_extension.py',BASE/'REQUESTS.json',BASE/'PROTOCOL.md']+list(c.SCHEMA_PATHS.values())
    c.write(BASE/'freeze.json',{'head':c.head(),'utc':c.now(),'model':c.CONFIG['model'],'max_retries':0,'max_workers':4,'timeout_seconds':240,
     'sample_count':6,'files':{str(p.relative_to(c.ROOT)):c.sha(p) for p in files},
     'prior_results':{str(p.relative_to(c.ROOT)):c.sha(p) for p in [BASE.parent/'primary_outputs.json',BASE.parent/'fallback_outputs.json']}})

def run():
    f=c.read(BASE/'freeze.json')
    for p,h in f['files'].items():assert c.sha(c.ROOT/p)==h,p
    for p in [BASE/'freeze.json',BASE/'REQUESTS.json']:
        assert c.subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(c.ROOT))])==p.read_bytes()
    assert not (BASE/'events.jsonl').exists()
    from dotenv import dotenv_values
    key=dotenv_values(c.ROOT/c.CONFIG['credential_file']).get(c.CONFIG['credential_field']);assert key
    lock=Lock();auth=c.AuthFailureLatch((c.AuthenticationError,));items=c.read(BASE/'REQUESTS.json');results={}
    with httpx.Client(timeout=240,transport=httpx.HTTPTransport(retries=0),follow_redirects=False) as client,(BASE/'events.jsonl').open('x') as log:
        def emit(e):
            with lock:log.write(json.dumps(e,ensure_ascii=False)+'\n');log.flush()
        def one(it):
            ev={'id':it['id'],'request_sha256':it['request_sha256'],'started_utc':c.now(),'run_head':c.head(),'attempted':False};start=time.monotonic()
            if auth.failure:ev['error']={'type':'blocked_by_auth'}
            else:
                ev['attempted']=True;emit({'kind':'request_started','request':it,**ev})
                try:
                    r=client.post(c.CONFIG['base_url']+it['path'],json=it['request'],headers={'Authorization':'Bearer '+key});ev['http_status']=r.status_code;ev['response_text']=r.text
                    if r.status_code==401:
                        exc=c.AuthenticationError('credential rejected',response=r,body=None);auth.observe(exc);raise exc
                    r.raise_for_status();raw=r.json();ev['response']=raw;ev['usage']=raw.get('usage');obj=c.decode(raw,it['surface']);ev['parsed_output']=obj
                    Draft202012Validator(it['validation_schema']).validate(obj);ev['schema_valid']=True
                except Exception as exc:ev['error']={'type':type(exc).__name__,'message':str(exc)[:1600]}
            ev['elapsed_seconds']=time.monotonic()-start;emit({'kind':'completed',**ev});print(ev['id'],ev.get('http_status'),ev.get('schema_valid',False),ev.get('error',{}).get('type'),flush=True);return ev
        with ThreadPoolExecutor(max_workers=4) as pool:
            for fu in as_completed([pool.submit(one,x) for x in items]):ev=fu.result();results[ev['id']]=ev
    c.write(BASE/'outputs.json',[results[x['id']] for x in items])

if __name__=='__main__':freeze() if sys.argv[1]=='freeze' else run()
