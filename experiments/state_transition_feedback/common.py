"""Frozen one-shot model and unchanged top50 Search runners for T1/T2/T3/T4."""
import hashlib,json,os,sys,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
from pathlib import Path

TOP=Path(__file__).resolve().parent
ROOT=TOP.parents[1]
PROVIDER=ROOT/'experiments/model_backend_deepseek/provider.json'

def read(p):return json.loads(Path(p).read_text())
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def provider():
    p=read(PROVIDER)
    assert p['model']=='deepseek-flash' and p['max_retries']==0
    return p
def model_request(prompt,content):
    return {'model':'deepseek-flash','messages':[{'role':'system','content':prompt},
      {'role':'user','content':json.dumps(content,ensure_ascii=False)}],'stream':False}

def parse(raw,schema):
    if raw['choices'][0]['finish_reason']!='stop':raise ValueError('abnormal_finish')
    obj=json.loads(raw['choices'][0]['message']['content'])
    if not isinstance(obj,dict):raise ValueError('schema')
    if schema=='query':
        if set(obj)!={'search_query'} or not isinstance(obj['search_query'],str) or not obj['search_query'].strip() or len(obj['search_query'])>=1000:
            raise ValueError('schema')
    elif schema=='updater':
        if set(obj)!={'claims'} or not isinstance(obj['claims'],list) or len(obj['claims'])>2:raise ValueError('schema')
        for claim in obj['claims']:
            if not isinstance(claim,dict) or set(claim)!={'statement','decision_effect'}:raise ValueError('schema')
            if not isinstance(claim['statement'],str) or not claim['statement'].strip() or len(claim['statement'])>500:raise ValueError('schema')
            if claim['decision_effect'] not in ('candidate_binding','constraint_resolution','hypothesis_exclusion'):raise ValueError('schema')
    elif schema=='actor':
        if set(obj)!={'next_gap','search_query'} or any(not isinstance(obj[k],str) or not obj[k].strip() or len(obj[k])>1000 for k in obj):raise ValueError('schema')
    else:raise ValueError(schema)
    return obj

def one(client,item,schema):
    start=time.monotonic()
    event={'case_id':item['case_id'],'arm':item['arm'],'request_sha256':item['request_sha256'],
           'request':item['request'],'started_utc':datetime.now(timezone.utc).isoformat()}
    out=None;err=None
    try:
        raw=client.chat.completions.create(**item['request']).model_dump(mode='json')
        event['response']=raw;out=parse(raw,schema)
    except Exception as exc:
        err={'type':type(exc).__name__,'status':getattr(exc,'status_code',None),'message':str(exc)[:500]}
        event['error']=err
    event['elapsed_seconds']=time.monotonic()-start
    result={'case_id':item['case_id'],'qid':item['qid'],'arm':item['arm'],
            'request_sha256':item['request_sha256'],'output':out,'error':err,
            'usage':event.get('response',{}).get('usage')}
    return event,result

def run_model(base,schema):
    from dotenv import dotenv_values
    from openai import OpenAI
    base=Path(base);freeze=read(base/'freeze.json');items=read(base/'REQUESTS.json')
    assert sha(base/'REQUESTS.json')==freeze['requests_sha256']
    assert [(x['case_id'],x['arm'],x['request_sha256']) for x in items]==[tuple(x) for x in freeze['call_order']]
    assert all(digest(x['request'])==x['request_sha256'] for x in items)
    events=base/'query_events.jsonl' if schema=='query' else base/'events.jsonl'
    outputs=base/'QUERIES.json' if schema=='query' else base/'OUTPUTS.json'
    assert not events.exists() and not outputs.exists(),'outputs exist; never rerun'
    p=provider();assert p['model']==freeze['provider']['model'] and p['base_url']==freeze['provider']['base_url']
    key=dotenv_values(ROOT/p['credential_file']).get(p['credential_field'])
    if not key:raise ValueError('DeepSeek credential unavailable')
    completed={}
    with OpenAI(api_key=key,base_url=p['base_url'],timeout=p['timeout_seconds'],max_retries=0) as client,events.open('w') as f:
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures={pool.submit(one,client,x,schema):(x['case_id'],x['arm']) for x in items}
            for future in as_completed(futures):
                event,result=future.result();completed[(result['case_id'],result['arm'])]=result
                f.write(json.dumps(event,ensure_ascii=False)+'\n');f.flush()
                print(result['case_id'],result['arm'],'ok' if result['error'] is None else result['error']['type'],flush=True)
    write(outputs,[completed[(x['case_id'],x['arm'])] for x in items])
    print('complete',len(items),'valid',sum(x['output'] is not None for x in completed.values()),flush=True)

def run_retrieval(base,depth=50):
    base=Path(base);freeze=read(base/'freeze.json');manifest=read(base/'query_outputs_commit.json')
    assert sha(base/'QUERIES.json')==manifest['queries_sha256']
    assert sha(base/'query_events.jsonl')==manifest['events_sha256']
    assert sha(ROOT/'BCPlus/scripts/search_bcplus.py')==freeze['retriever_sha256']
    rows=read(base/'QUERIES.json');outpath=base/'retrieval_results.json'
    assert not outpath.exists(),'retrieval outputs exist; never rerun'
    os.environ['BCPLUS_DEVICE']=freeze['device']
    sys.path.insert(0,str(ROOT))
    from BCPlus.scripts.search_bcplus import BCPlusSearcher,PREFIX
    import torch
    searcher=BCPlusSearcher();results=[]
    try:
        for n,x in enumerate(rows,1):
            query=x['output']['search_query'] if x['output'] else None
            result={'case_id':x['case_id'],'qid':x['qid'],'arm':x['arm'],'search_query':query,
                    'query_error':x['error'],'hits':[],'retrieval_error':None}
            if query:
                try:
                    batch=searcher.tokenizer(PREFIX+query,return_tensors='pt',truncation=False)
                    if batch['input_ids'].shape[1]>8192:raise ValueError('oversize query')
                    with torch.inference_mode():
                        hidden=searcher.model(**batch.to(searcher.device)).last_hidden_state[:,-1]
                        vec=torch.nn.functional.normalize(hidden,p=2,dim=1).float().cpu().numpy()
                    scores,positions=searcher.index.search(vec,depth)
                    result['hits']=[{'rank':i,'docid':searcher.docids[int(pos)],'score':float(score)}
                      for i,(score,pos) in enumerate(zip(scores[0],positions[0]),1)]
                except Exception as exc:
                    result['retrieval_error']={'type':type(exc).__name__,'message':str(exc)[:500]}
            results.append(result)
            print(n,len(rows),x['case_id'],x['arm'],len(result['hits']),flush=True)
    finally:searcher.close()
    write(outpath,results)

if __name__=='__main__':
    base=Path(sys.argv[2])
    if sys.argv[1]=='query':run_model(base,'query')
    elif sys.argv[1]=='updater':run_model(base,'updater')
    elif sys.argv[1]=='retrieve':run_retrieval(base)
    else:raise SystemExit('common.py query|updater|retrieve STAGE_DIR')
