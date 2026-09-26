"""One-attempt transport with structural and Harness checks kept separate."""
import copy, hashlib, json, subprocess, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import httpx
from jsonschema import Draft202012Validator

TOP=Path(__file__).resolve().parent
ROOT=TOP.parents[1]
sys.path.insert(0,str(ROOT))
from experiments.goal_residual_control_v3.capability import read,write,sha,digest,now,head,CONFIG
from experiments.goal_residual_control.harness_v2.contracts import validate_object
from llm_chat.auth_guard import AuthFailureLatch
from openai import AuthenticationError

AUTH=AuthFailureLatch((AuthenticationError,))
NAMES={'research_actor':'actor','state_updater':'updater','goal_reviewer':'goal'}
def schema(kind):return read(TOP/'schemas'/f'{NAMES[kind]}_transport.json')
def request(chat,kind,mode):
    assert set(chat)=={'model','messages','stream'}
    if mode=='responses_structured':
        return {'model':chat['model'],'input':copy.deepcopy(chat['messages']),'stream':chat['stream'],
          'text':{'format':{'type':'json_schema','name':kind,'schema':schema(kind),'strict':True}}}
    assert mode=='json_mode_fallback'
    return {**copy.deepcopy(chat),'response_format':{'type':'json_object'}}
def make_item(cid,qid,arm,kind,chat,mode):
    r=request(chat,kind,mode)
    return {'case_id':cid,'qid':qid,'arm':arm,'kind':kind,'mode':mode,'request':r,'request_sha256':digest(r)}
def check_history():
    for p,h in read(TOP/'analysis/HISTORICAL_HASHES.json').items():assert sha(ROOT/p)==h,p
def freeze(base,requests,extra):
    assert not (base/'freeze.json').exists()
    check_history();write(base/'requests.json',requests)
    paths=list(TOP.glob('*.py'))+list(TOP.glob('*.md'))+list((TOP/'prompts').glob('*'))+list((TOP/'schemas').glob('*'))
    paths += [TOP/'analysis/HISTORICAL_HASHES.json']+list(base.glob('*.json'))+list(base.glob('*.md'))
    write(base/'freeze.json',{'git_head':head(),'utc':now(),'model':CONFIG['model'],'base_url':CONFIG['base_url'],
      'max_retries':0,'max_workers':4,'timeout_seconds':240,'planned':len(requests),'extra':extra,
      'files':{str(p.relative_to(ROOT)):sha(p) for p in paths}})
def gate(base):
    check_history();f=read(base/'freeze.json')
    for p,h in f['files'].items():assert sha(ROOT/p)==h,p
    for p in [base/'freeze.json',base/'requests.json']:
        assert subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(ROOT))])==p.read_bytes()

def decode(raw,mode):
    if mode=='responses_structured':
        if raw.get('status')!='completed':raise RuntimeError('length/incomplete failure:'+str(raw.get('status')))
        b=[c['text'] for x in raw.get('output',[]) if x.get('type')=='message' for c in x.get('content',[]) if c.get('type')=='output_text']
        if len(b)!=1:raise ValueError('expected_one_output_text')
        return json.loads(b[0])
    c=raw['choices'][0]
    if c['finish_reason']!='stop':raise RuntimeError('length/incomplete failure:'+str(c['finish_reason']))
    return json.loads(c['message']['content'])
def usage(raw,mode):
    u=raw.get('usage')
    if not u:return None
    if mode=='responses_structured':
        n=u['input_tokens'];hit=u.get('input_tokens_details',{}).get('cached_tokens')
        return {'input':n,'output':u['output_tokens'],'hit':hit,'miss':n-hit if hit is not None else None,
          'reasoning':u.get('output_tokens_details',{}).get('reasoning_tokens')}
    return {'input':u['prompt_tokens'],'output':u['completion_tokens'],'hit':u.get('prompt_cache_hit_tokens'),
      'miss':u.get('prompt_cache_miss_tokens'),'reasoning':u.get('completion_tokens_details',{}).get('reasoning_tokens')}
def validate(out,kind,view):
    Draft202012Validator(schema(kind)).validate(out)
    validate_object(out,kind,view.get('Available Workspace'))
    return out
def batch(base,tag,items):
    evpath=base/(tag+'_events.jsonl');outpath=base/(tag+'_outputs.json')
    assert not evpath.exists() and not outpath.exists(),'already attempted; no retry'
    from dotenv import dotenv_values
    key=dotenv_values(ROOT/CONFIG['credential_file']).get(CONFIG['credential_field']);assert key
    lock=Lock();done={}
    with httpx.Client(timeout=240,transport=httpx.HTTPTransport(retries=0),follow_redirects=False) as c,evpath.open('x') as log:
        def emit(e):
            with lock:log.write(json.dumps(e,ensure_ascii=False)+'\n');log.flush()
        def one(it):
            t=time.monotonic();result={k:it[k] for k in ['case_id','qid','arm','kind','request_sha256','mode']}
            result.update(attempted=False,structural_valid=False,harness_valid=False,output=None,error=None)
            event={'item':it,'started_utc':now(),'run_head':head()};category='provider/API failure'
            if AUTH.failure:result['error']={'category':category,'type':'blocked_by_auth'}
            else:
                result['attempted']=True;emit({'kind':'request_started',**event})
                try:
                    path='/responses' if it['mode']=='responses_structured' else '/chat/completions'
                    r=c.post(CONFIG['base_url'].rstrip('/')+path,json=it['request'],headers={'Authorization':'Bearer '+key})
                    event.update(http_status=r.status_code,response_text=r.text)
                    if r.status_code==401:
                        e=AuthenticationError('credential rejected',response=r,body=None);AUTH.observe(e);raise e
                    r.raise_for_status();raw=r.json();event['response']=raw;result['usage']=usage(raw,it['mode'])
                    category='transport_structural_failure'
                    try:out=decode(raw,it['mode'])
                    except RuntimeError:category='length/incomplete failure';raise
                    event['parsed_output']=out
                    Draft202012Validator(schema(it['kind'])).validate(out);result['structural_valid']=True
                    category='harness_control_violation'
                    messages=it['request'].get('input',it['request'].get('messages'))
                    view=json.loads(messages[1]['content'])
                    validate_object(out,it['kind'],view.get('Available Workspace'));result['harness_valid']=True;result['output']=out
                except Exception as e:result['error']={'category':category,'type':type(e).__name__,'message':str(e)[:1500]}
            result['elapsed_seconds']=time.monotonic()-t
            emit({'kind':'completed','event':event,'result':result})
            print(tag,it['case_id'],it['arm'],'ok' if result['output'] is not None else result['error']['category'],flush=True)
            return result
        with ThreadPoolExecutor(max_workers=4) as pool:
            for f in as_completed([pool.submit(one,it) for it in items]):
                r=f.result();done[r['case_id'],r['arm']]=r
    rows=[done[it['case_id'],it['arm']] for it in items];write(outpath,rows);return rows

if __name__=='__main__':
    base=TOP/sys.argv[1];gate(base);items=read(base/'requests.json')
    if sys.argv[1]=='structured_transport_canary':batch(base,'canary',items)
    else:
        rows=batch(base,'paired',items)
        events=[json.loads(l) for l in (base/'paired_events.jsonl').open()]
        for arm in ['Uc','U1']:
            write(base/(arm+'_outputs.json'),[r for r in rows if r['arm']==arm])
            with (base/(arm+'_events.jsonl')).open('x') as f:
                for e in events:
                    a=e['item']['arm'] if e['kind']=='request_started' else e['result']['arm']
                    if a==arm:f.write(json.dumps(e,ensure_ascii=False)+'\n')
