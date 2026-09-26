"""Append-only v2 model execution; shared typed authentication short circuit."""
import copy,json,sys,time,subprocess,hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from threading import Lock
HERE=Path(__file__).resolve().parent
TOP=HERE.parent
ROOT=TOP.parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(TOP))
from experiments.goal_residual_control import common as old
from llm_chat.auth_guard import AuthFailureLatch
from openai import AuthenticationError
from contracts import parse

read,write,digest,sha,now,head=old.read,old.write,old.digest,old.sha,old.now,old.head
CONFIG=old.CONFIG
SEARCH_FIND_TOOLS=old.SEARCH_FIND_TOOLS
claims,goal_view,actor_view,recent=old.claims,old.goal_view,old.actor_view,old.recent
client=old.client
AUTH=AuthFailureLatch((AuthenticationError,))

def request(kind,view):
    req=old.request(kind,view)
    if kind in ('research_actor','state_updater'):req['messages'][0]['content']=(HERE/(kind+'.md')).read_text()
    return req
def item(cid,qid,arm,kind,view):
    r=request(kind,view)
    return {'case_id':cid,'qid':qid,'arm':arm,'kind':kind,'request':r,'request_sha256':digest(r)}

def batch(base,tag,items):
    base=Path(base);evpath=base/(tag+'_events.jsonl');outpath=base/(tag+'_outputs.json')
    assert not evpath.exists() and not outpath.exists(),'already attempted; never replay'
    write(base/(tag+'_requests.json'),items);done={};lock=Lock()
    with client() as c,evpath.open('w') as log:
        def emit(x):
            with lock:log.write(json.dumps(x,ensure_ascii=False)+'\n');log.flush()
        def one(it):
            start=time.monotonic();ev={**it,'started_utc':now(),'attempted':False};out=None;err=None;serialization_valid=False
            if AUTH.failure:
                err={'type':'blocked_by_auth','cause':AUTH.failure};ev['error']=err
                emit({'kind':'blocked_by_auth','item':it,'error':err})
            else:
                ev['attempted']=True;emit({'kind':'request_started','time':now(),'item':it})
                try:
                    raw=c.chat.completions.create(**it['request']).model_dump(mode='json')
                    ev['response']=raw;ev['cache_usage']=old.extract(raw)
                    out=parse(raw,it['kind']);serialization_valid=True
                    if it['kind']=='research_actor':
                        view=json.loads(it['request']['messages'][1]['content'])
                        parse(raw,it['kind'],view['Available Workspace'])
                except Exception as exc:
                    AUTH.observe(exc)
                    err={'type':type(exc).__name__,'status':getattr(exc,'status_code',None),'message':str(exc)[:500]}
                    ev['error']=err;out=None
            ev['elapsed_seconds']=time.monotonic()-start
            res={k:it[k] for k in ('case_id','qid','arm','kind','request_sha256')}
            res.update(output=out,error=err,attempted=ev['attempted'],serialization_valid=serialization_valid,
              cache_usage=ev.get('cache_usage'),usage=ev.get('response',{}).get('usage'))
            emit({'kind':'completed','event':ev,'result':res});return res
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures=[pool.submit(one,x) for x in items]
            for f in as_completed(futures):
                r=f.result();done[r['case_id'],r['arm']]=r
                print(tag,r['case_id'],r['arm'],'ok' if r['output'] else r['error']['type'],flush=True)
    rows=[done[x['case_id'],x['arm']] for x in items];write(outpath,rows);return rows

def source_files():
    paths=list(HERE.glob('*.py'))+list(HERE.glob('*.md'))+list(HERE.glob('*.json'))
    paths += [TOP/'research_decision_v2/ACTION_RESPONSE_SCHEMA.json',TOP/'bank/freeze.json',TOP/'bank/SNAPSHOTS.json',
       TOP/'bank/TRANSITIONS.json',TOP/'bank/SOURCE_WINDOWS.json',TOP/'bank/PRIVATE_TRUTH.json',TOP/'bank/HISTORICAL_SOURCE_SETS.json',
       TOP/'common.py',TOP/'tools_runner.py',TOP/'REVIEW_RUBRIC.md',TOP/'goal_review/outputs.json',
       TOP/'prompts/goal_reviewer.md',TOP/'prompts/state_updater.md',TOP/'prompts/research_actor.md']
    paths += [ROOT/p for p in ['llm_chat/auth_guard.py','llm_chat/search_find_agent.py','llm_chat/search_find_v3b_agent.py',
       'llm_chat/raw_windows.py','llm_chat/window_locator.py','BCPlus/scripts/search_bcplus.py','experiments/model_backend_deepseek/provider.json']]
    return paths

def freeze_stage(base,items,extra=None):
    base=Path(base);base.mkdir(exist_ok=True)
    assert not (base/'freeze.json').exists()
    write(base/'REQUESTS.json',items)
    write(base/'freeze.json',{'git_head':head(),'frozen_utc':now(),'provider':CONFIG,'max_workers':4,'max_retries':0,
      'requests_sha256':sha(base/'REQUESTS.json'),'sample_count':len(items),
      'files':{str(p.relative_to(ROOT)):sha(p) for p in source_files()},'extra':extra or {},
      'historical_base':'f53a43c9342fa643c117b9362dce1164abaf3e4a','same_api_surface':True,
      'tool_schema_sha256':digest(SEARCH_FIND_TOOLS),'order':[(x['case_id'],x['arm']) for x in items]})

def gate(base):
    base=Path(base);f=read(base/'freeze.json')
    assert all(sha(ROOT/p)==h for p,h in f['files'].items())
    assert sha(base/'REQUESTS.json')==f['requests_sha256']
    for p in [base/'freeze.json',base/'REQUESTS.json']:
        assert subprocess.check_output(['git','show',f'HEAD:{p.relative_to(ROOT)}'],cwd=ROOT)==p.read_bytes()
    assert not (base/'run_started.json').exists(),'already started; no resampling'
    write(base/'run_started.json',{'head':head(),'time':now(),'freeze_sha256':sha(base/'freeze.json')})

def run_g2():
    base=TOP/'research_decision_v2';gate(base)
    rows=batch(base,'actor',read(base/'REQUESTS.json'));write(base/'outputs.json',rows)
    valid=sum(x['output'] is not None for x in rows);serial=sum(x['serialization_valid'] for x in rows)
    write(base/'ENGINEERING_GATE.json',{'planned':120,'serialization_valid':serial,'contract_and_references_valid':valid,
      'valid_rate':valid/120,'continue_G3':valid/120>=.8,'response_format':'unchanged; no constrained generation',
      'blocked_by_auth':sum(bool(x['error'] and x['error']['type']=='blocked_by_auth') for x in rows)})
    print('G2v2 complete',valid,'/120',flush=True)

if __name__=='__main__':run_g2()
