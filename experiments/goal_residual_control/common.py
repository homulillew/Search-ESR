"""One-shot, journaled calls; no model repair, retry, or truth in production views."""
import hashlib,json,sys,time,subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone

TOP=Path(__file__).resolve().parent
ROOT=TOP.parents[1]
sys.path.insert(0,str(ROOT))
from llm_chat.search_find_agent import SEARCH_FIND_TOOLS
from experiments.model_backend_deepseek.cache_usage import extract

def read(p):return json.loads(Path(p).read_text())
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def head():return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
CONFIG=read(ROOT/'experiments/model_backend_deepseek/provider.json')
assert CONFIG['model']=='deepseek-flash' and CONFIG['max_retries']==0
SCHEMAS={t['function']['name']:t['function']['parameters'] for t in SEARCH_FIND_TOOLS}

def client():
    from openai import OpenAI
    from dotenv import dotenv_values
    key=dotenv_values(ROOT/CONFIG['credential_file']).get(CONFIG['credential_field'])
    if not key:raise ValueError('DeepSeek credential unavailable')
    return OpenAI(api_key=key,base_url=CONFIG['base_url'],timeout=240,max_retries=0)

def prompt(kind):return (TOP/'prompts'/f'{kind}.md').read_text()
def request(kind,view):
    return {'model':CONFIG['model'],'messages':[{'role':'system','content':prompt(kind)},
      {'role':'user','content':json.dumps(view,ensure_ascii=False)}],'stream':False}
def item(cid,qid,arm,kind,view):
    req=request(kind,view)
    return {'case_id':cid,'qid':qid,'arm':arm,'kind':kind,'request':req,'request_sha256':digest(req)}
def claims(state):return [c['statement'] if isinstance(c,dict) else c for c in state['verified_claims']]
def goal_view(state):return {'Original Question':state['question'],'Verified Claims':claims(state)}
def public_workspace(ws):
    return {'known_documents':[{k:v for k,v in d.items() if k!='docid'} for d in ws['known_documents']],
      'observed_windows':[{k:v for k,v in w.items() if k not in ('source_id','offset','document_sha256')} for w in ws['observed_windows']]}
def recent(state):
    if 'attempts' in state:return state['attempts']
    h=state['recent_attempt_context']
    if state['phase']=='POST' and h.get('recorded_action'):return [h['recorded_action']]
    if h.get('historical_model_query'):return [{'tool':'search','query':h['historical_model_query']}]
    return []
def actor_view(state,residual=None,gap=None,remaining=1):
    v={**goal_view(state),'Working Hypothesis':state['working_hypothesis'],
       'Recent Attempts':recent(state),'Available Workspace':public_workspace(state['available_workspace']),
       'Budget':{'remaining_decisions':remaining,'max_independent_actions':2},'Tool schema':SEARCH_FIND_TOOLS}
    if residual is not None:v['Goal Residual']=residual['residual']
    if gap is not None:v['Persisted historical Gap']=gap
    return v

def parse(raw,kind):
    if raw['choices'][0]['finish_reason']!='stop':raise ValueError('abnormal_finish')
    x=json.loads(raw['choices'][0]['message']['content'])
    if not isinstance(x,dict):raise ValueError('not_object')
    if kind=='goal_reviewer':
        if set(x)!={'resolved','residual'} or type(x['resolved']) is not bool or not isinstance(x['residual'],str):raise ValueError('goal_schema')
        if x['resolved'] != (not x['residual'].strip()):raise ValueError('goal_inconsistent')
    elif kind=='research_actor':
        from jsonschema import validate
        if set(x)!={'decision','gap','actions'} or x['decision'] not in ('stop','act') or not isinstance(x['gap'],str) or not isinstance(x['actions'],list):raise ValueError('actor_schema')
        if x['decision']=='stop':
            if x['gap']!='' or x['actions']!=[]:raise ValueError('stop_schema')
        else:
            if not x['gap'].strip() or not 1<=len(x['actions'])<=2:raise ValueError('act_schema')
            for a in x['actions']:
                if not isinstance(a,dict) or a.get('tool') not in SCHEMAS:raise ValueError('tool_schema')
                validate({k:v for k,v in a.items() if k!='tool'},SCHEMAS[a['tool']])
    elif kind=='state_updater':
        if set(x)!={'claims_to_add','hypothesis_update'} or not isinstance(x['claims_to_add'],list) or len(x['claims_to_add'])>2 or any(not isinstance(c,str) or not c.strip() for c in x['claims_to_add']):raise ValueError('updater_schema')
        h=x['hypothesis_update']
        if not isinstance(h,dict) or set(h)!={'action','statement'} or h['action'] not in ('keep','set','clear') or not isinstance(h['statement'],str):raise ValueError('hypothesis_schema')
        if h['action']=='set' and not h['statement'].strip():raise ValueError('empty_hypothesis')
    else:raise ValueError(kind)
    return x

def call(c,it):
    start=time.monotonic();ev={**it,'started_utc':now()};out=None;error=None
    try:
        raw=c.chat.completions.create(**it['request']).model_dump(mode='json')
        ev['response']=raw;ev['cache_usage']=extract(raw);out=parse(raw,it['kind'])
    except Exception as exc:
        error={'type':type(exc).__name__,'status':getattr(exc,'status_code',None),'message':str(exc)[:500]};ev['error']=error
    ev['elapsed_seconds']=time.monotonic()-start
    result={k:it[k] for k in ('case_id','qid','arm','kind','request_sha256')}
    result.update(output=out,error=error,cache_usage=ev.get('cache_usage'),usage=ev.get('response',{}).get('usage'))
    return ev,result

def freeze_stage(base,items,extra=None):
    base=Path(base);base.mkdir(parents=True,exist_ok=True)
    assert not (base/'freeze.json').exists(),'already frozen'
    write(base/'REQUESTS.json',items)
    files=[TOP/'common.py',TOP/'PROTOCOL.md',TOP/'bank/freeze.json',TOP/'REVIEW_RUBRIC.md']+sorted((TOP/'prompts').glob('*.md'))
    files += [ROOT/p for p in ('llm_chat/search_find_agent.py','llm_chat/search_find_v3b_agent.py','llm_chat/raw_windows.py','llm_chat/window_locator.py','BCPlus/scripts/search_bcplus.py')]
    write(base/'freeze.json',{'git_head':head(),'frozen_utc':now(),'provider':CONFIG,
      'requests_sha256':sha(base/'REQUESTS.json'),'files':{str(p.relative_to(ROOT)):sha(p) for p in files},
      'tool_schema_sha256':digest(SEARCH_FIND_TOOLS),'order':[(x['case_id'],x['arm']) for x in items],
      'sample_count':len(items),'max_retries':0,'max_workers':4,'extra':extra or {}})

def run_stage(base):
    base=Path(base);f=read(base/'freeze.json');items=read(base/'REQUESTS.json')
    assert f['requests_sha256']==sha(base/'REQUESTS.json')
    assert all(sha(ROOT/p)==h for p,h in f['files'].items())
    assert all(digest(x['request'])==x['request_sha256'] for x in items)
    # Require the complete freeze and inputs to be committed before any call.
    for p in [base/'freeze.json',base/'REQUESTS.json']:
        committed=subprocess.check_output(['git','show',f'HEAD:{p.relative_to(ROOT)}'],cwd=ROOT)
        assert committed==p.read_bytes()
    events=base/'events.jsonl';outs=base/'outputs.json'
    assert not events.exists() and not outs.exists(),'already attempted; no rerun'
    complete={}
    with client() as c, events.open('w') as log:
        with ThreadPoolExecutor(max_workers=4) as pool:
            fs={}
            for it in items:
                log.write(json.dumps({'kind':'request_started','time':now(),'case_id':it['case_id'],'arm':it['arm'],'request_sha256':it['request_sha256']})+'\n');log.flush()
                fs[pool.submit(call,c,it)]=it
            for future in as_completed(fs):
                ev,res=future.result();complete[res['case_id'],res['arm']]=res
                log.write(json.dumps({'kind':'completed','event':ev,'result':res},ensure_ascii=False)+'\n');log.flush()
                print(res['case_id'],res['arm'],'ok' if res['output'] is not None else res['error']['type'],flush=True)
    write(outs,[complete[x['case_id'],x['arm']] for x in items])
    print('complete',len(items),'valid',sum(x['output'] is not None for x in complete.values()),flush=True)

if __name__=='__main__':run_stage(sys.argv[1])
