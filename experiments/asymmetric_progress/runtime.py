"""Single-attempt JSON mode Progress transport. No research tools or semantic Harness routing."""
import copy, hashlib, json, subprocess, time, sys
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Event
import httpx
from jsonschema import Draft202012Validator

TOP = Path(__file__).resolve().parent
ROOT = TOP.parents[1]
def rd(p): return json.loads(Path(p).read_text())
def wr(p,v): Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def dg(v): return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def head(): return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
def now(): return datetime.now(timezone.utc).isoformat()
CONFIG = rd(ROOT/'experiments/model_backend_deepseek/provider.json')
SCHEMAS = {a:rd(TOP/f'schemas/{a}.json') for a in ['L0','L1','Audit']}

def view(c):
    return {'Original Question':c['question'],'Verified Claims':[
        {'index':i,'statement':x['statement']} for i,x in enumerate(c['state']['verified_claims'],1)]}

def item(c,arm,rep,prompt=None):
    v=view(c);name=arm
    req={'model':CONFIG['model'],'messages':[{'role':'system','content':prompt or (TOP/f'prompts/{name}.md').read_text()},
         {'role':'user','content':json.dumps(v,ensure_ascii=False)}], 'stream':False,'response_format':{'type':'json_object'}}
    return {'id':f"{c['case_id']}_{arm}_{rep}",'case_id':c['case_id'],'qid':c['qid'],'arm':arm,'replicate':rep,
            'set':c['set'],'claim_count':len(v['Verified Claims']),
            'request':req,'request_sha256':dg(req),'view_sha256':dg(v)}

def validate(out,arm,n):
    Draft202012Validator(SCHEMAS[arm]).validate(out)
    if arm=='Audit':
        refs=[r for u in out['closure_support'] for r in u['claim_refs']]
        if out['blocking_gap']: refs+=out['blocking_gap']['claim_refs']
    else: refs=out['closure_claim_refs']+[r for x in out['blocking_gaps'] for r in x['claim_refs']]
    for ref in refs:
        if not 1 <= ref <= n: raise ValueError('Claim index does not exist')
    return out

def decode(raw,it):
    c=raw['choices'][0]
    if c['finish_reason']!='stop': raise EOFError(str(c['finish_reason']))
    return validate(json.loads(c['message']['content']),it['arm'],it['claim_count'])

def usage(raw):
    u=raw.get('usage',{})
    return {'input':u.get('prompt_tokens'),'output':u.get('completion_tokens'),
            'hit':u.get('prompt_cache_hit_tokens'),'miss':u.get('prompt_cache_miss_tokens'),
            'reasoning':u.get('completion_tokens_details',{}).get('reasoning_tokens')}

def verify_freeze(path):
    f=rd(path)
    for p,h in f['file_hashes'].items(): assert sha(ROOT/p)==h,p
    tracked=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()
    for p in f['file_hashes']:
        assert p in tracked,p
        assert subprocess.check_output(['git','show','HEAD:'+p],cwd=ROOT)==(ROOT/p).read_bytes(),p
    return f

def batch(base,items,tag='frontier'):
    from dotenv import dotenv_values
    evpath=base/(tag+'_events.jsonl');outpath=base/(tag+'_outputs.json')
    assert not evpath.exists() and not outpath.exists(),'Previously attempted: never resubmit or overwrite'
    assert len({it['id'] for it in items})==len(items)
    key=dotenv_values(ROOT/CONFIG['credential_file']).get(CONFIG['credential_field']);assert key
    lock=Lock();authfailed=Event();done={}
    with httpx.Client(timeout=240,transport=httpx.HTTPTransport(retries=0),follow_redirects=False) as client,evpath.open('x') as log:
        def emit(e):
            with lock: log.write(json.dumps(e,ensure_ascii=False)+'\n');log.flush()
        def one(it):
            t=time.monotonic();r={k:it[k] for k in ['id','case_id','qid','arm','replicate','request_sha256','view_sha256','set']}
            r.update(attempted=False,output=None,usage=None,error=None)
            e={'item':it,'started_utc':now(),'run_head':head()};category='provider failure'
            if authfailed.is_set(): r['error']={'category':category,'type':'blocked_by_auth'}
            else:
                r['attempted']=True;emit({'kind':'request_started',**e})
                try:
                    response=client.post(CONFIG['base_url'].rstrip('/')+'/chat/completions',json=it['request'],headers={'Authorization':'Bearer '+key})
                    e.update(http_status=response.status_code,response_text=response.text)
                    if response.status_code==401: authfailed.set()
                    response.raise_for_status()
                    category='transport failure';raw=response.json();e['response']=raw;r['usage']=usage(raw)
                    category='Harness violation';r['output']=decode(raw,it)
                except EOFError as err: r['error']={'category':'length/incomplete','type':type(err).__name__,'message':str(err)}
                except Exception as err: r['error']={'category':category,'type':type(err).__name__,'message':str(err)[:1500]}
            r['elapsed_seconds']=time.monotonic()-t
            emit({'kind':'completed','event':e,'result':r})
            print(tag,it['id'],'ok' if r['output'] else r['error']['category'],flush=True)
            return r
        with ThreadPoolExecutor(max_workers=4) as pool:
            for fut in as_completed([pool.submit(one,it) for it in items]):
                r=fut.result();done[r['id']]=r
    rows=[done[it['id']] for it in items];wr(outpath,rows);return rows

if __name__=='__main__':
    stage=sys.argv[1]
    assert stage in ['primary','challenge','canary','exploration']
    base=TOP/stage
    verify_freeze(base/'freeze.json')
    batch(base,rd(base/'requests.json'),tag=stage)
