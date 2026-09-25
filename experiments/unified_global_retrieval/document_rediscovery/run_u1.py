"""Frozen U1 query writing, paired document retrieval and gate analysis."""
import hashlib
import json
import os
import subprocess
import sys
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
sys.path.insert(0, str(ROOT))
from dotenv import dotenv_values
from openai import OpenAI

BANK = json.loads((HERE/'BANK.json').read_text())
TRUTH = {x['case_id']: x for x in json.loads((HERE/'PRIVATE_TRUTH.json').read_text())}
PROVIDER = json.loads((ROOT/'experiments/model_backend_deepseek/provider.json').read_text())
PROMPT = (STUDY/'prompts/query_writer.md').read_text()
LOCK = threading.Lock()

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()

def digest(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def paths():
    local=['PROTOCOL.md','HYPOTHESES.md','FROZEN_STATE.md','prompts/query_writer.md','document_rediscovery/REVIEW_RUBRIC.md','document_rediscovery/build_bank.py','document_rediscovery/BANK.json','document_rediscovery/PRIVATE_TRUTH.json','document_rediscovery/run_u1.py']
    prior=['experiments/minimal_research_loop/verify_necessity/OBSERVATIONS.json','experiments/model_backend_deepseek/provider.json','BCPlus/scripts/search_bcplus.py','llm_chat/search_find_v3b_agent.py']
    index=[str(x.relative_to(ROOT)) for x in sorted((ROOT/'BCPlus/indexes/qwen3-embedding-8b').glob('*.pkl'))]
    index+=['BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite']
    return [STUDY/x for x in local]+[ROOT/x for x in prior+index]

def order():
    return sorted(BANK,key=lambda x:digest(x['case_id']))

def request(case):
    return {'model':PROVIDER['model'],'messages':[{'role':'system','content':PROMPT},{'role':'user','content':json.dumps(case['writer_input'],ensure_ascii=False)}],'stream':False}

def emit(path,kind,**fields):
    event={'time_utc':datetime.now(timezone.utc).isoformat(),'kind':kind,**fields}
    with LOCK:
        with path.open('a') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')

def freeze():
    p=HERE/'freeze.json'
    if p.exists():raise FileExistsError(p)
    if PROVIDER['model']!='deepseek-flash' or PROVIDER['max_retries']!=0:raise AssertionError('provider')
    if len(BANK)!=40 or len({x['qid'] for x in BANK})!=10:raise AssertionError('bank')
    content_hashes={str(x.relative_to(ROOT)):sha(x) for x in paths()}
    f={'frozen_at_utc':datetime.now(timezone.utc).isoformat(),
       'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
       'provider':{k:PROVIDER[k] for k in ('model','base_url','timeout_seconds','max_retries')},
       'sample_count':len(BANK),'qid_count':len({x['qid'] for x in BANK}),
       'type_counts':dict(Counter(x['primary_type'] for x in BANK)),
       'case_order':[x['case_id'] for x in order()],
       'query_order':[x['case_id'] for x in order()],
       'search_k':5,'history_k':5,'query_writer_prompt_sha256':sha(STUDY/'prompts/query_writer.md'),
       'request_hashes':{x['case_id']:digest(request(x)) for x in BANK},
       'input_hashes':{x['case_id']:{k:digest(x['writer_input'][k]) for k in ('raw_question','current_gap','relevant_committed_claims','working_hypothesis')} for x in BANK},
       'checkpoint_hashes':{x['case_id']:digest(x['historical_checkpoint']) for x in BANK},
       'private_truth_hashes':{c:digest(t) for c,t in TRUTH.items()},
       'source_hashes':content_hashes,
       'failure_policy':'one model call per case; zero retry, no repair or best-of; invalid/failing cases retained as misses',
       'global_gate':{'old_ab_recall5_min':0.90,'new_cd_recall5_min':0.85,'overall_recall5_min':0.88,'zero_qid_cluster_forbidden':True},
       'history_prior':{'k0':60,'lambda':0.95,'gain_old_min_pp':10,'new_loss_max_pp':5,'d_escape_must_not_worsen':True}}
    p.write_text(json.dumps(f,indent=2,ensure_ascii=False)+'\n')
    print('freeze',p)

def gate():
    f=json.loads((HERE/'freeze.json').read_text())
    assert f['source_hashes']=={str(x.relative_to(ROOT)):sha(x) for x in paths()},'source drift'
    assert f['case_order']==[x['case_id'] for x in order()]
    assert f['request_hashes']=={x['case_id']:digest(request(x)) for x in BANK}
    assert len(TRUTH)==len(BANK)

def cache(raw):
    u=raw.get('usage') or {}
    hit=u.get('prompt_cache_hit_tokens');miss=u.get('prompt_cache_miss_tokens')
    return {'prompt_tokens':u.get('prompt_tokens'),'prompt_cache_hit_tokens':hit,'prompt_cache_miss_tokens':miss,
            'hit_rate':hit/(hit+miss) if isinstance(hit,int) and isinstance(miss,int) and hit+miss else None}

def one_query(client,case):
    cid=case['case_id'];req=request(case);events=HERE/'query_events.jsonl'
    emit(events,'request',case_id=cid,request_hash=digest(req),request=req)
    start=time.monotonic()
    try:
        raw=client.chat.completions.create(**req).model_dump(mode='json')
        emit(events,'response',case_id=cid,response=raw,cache=cache(raw),latency_seconds=time.monotonic()-start)
        choice=raw['choices'][0]
        if choice['finish_reason']!='stop':raise ValueError('abnormal_finish')
        val=json.loads(choice['message']['content'])
        if not isinstance(val,dict) or set(val)!={'search_query','find_query'}:raise ValueError('schema')
        if not all(isinstance(val[k],str) and val[k].strip() and len(val[k])<1000 for k in val):raise ValueError('query_content')
        return {'case_id':cid,**val,'query_sha256':digest(val),'error':None}
    except Exception as exc:
        emit(events,'error',case_id=cid,error_type=type(exc).__name__,status=getattr(exc,'status_code',None),error=str(exc)[:500],latency_seconds=time.monotonic()-start)
        return {'case_id':cid,'search_query':None,'find_query':None,'query_sha256':None,'error':type(exc).__name__}

def queries():
    gate()
    out=HERE/'QUERIES.json';events=HERE/'query_events.jsonl'
    if out.exists() or events.exists():raise FileExistsError('Query stage already started')
    key=dotenv_values(ROOT/PROVIDER['credential_file']).get(PROVIDER['credential_field'])
    if not key:raise ValueError('DeepSeek credential unavailable')
    results={}
    with OpenAI(api_key=key,base_url=PROVIDER['base_url'],timeout=PROVIDER['timeout_seconds'],max_retries=0) as client:
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures={pool.submit(one_query,client,c):c for c in order()}
            for fut in as_completed(futures):
                result=fut.result();results[result['case_id']]=result
                print(result['case_id'],'ok' if result['error'] is None else result['error'],flush=True)
    assert len(results)==len(BANK)
    out.write_text(json.dumps([results[x['case_id']] for x in order()],ensure_ascii=False,indent=2)+'\n')

def retrieval_freeze():
    gate()
    p=HERE/'retrieval_freeze.json'
    if p.exists():raise FileExistsError(p)
    q=json.loads((HERE/'QUERIES.json').read_text())
    if [x['case_id'] for x in q]!=[x['case_id'] for x in order()]:raise AssertionError('order')
    p.write_text(json.dumps({'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
       'queries_file_sha256':sha(HERE/'QUERIES.json'),'queries':{x['case_id']:x['query_sha256'] for x in q},
       'search_k':5,'history_k':5,'backend_sha256':sha(ROOT/'BCPlus/scripts/search_bcplus.py'),
       'index_hashes':{k:v for k,v in json.loads((HERE/'freeze.json').read_text())['source_hashes'].items() if k.startswith('BCPlus/indexes/')},
       'arm_order':['G','H'],'find_executed':False,'failure_policy':'invalid query or tool exception retained as miss; no retry or rewrite'},indent=2)+'\n')

def retrieve():
    gate()
    qf=json.loads((HERE/'retrieval_freeze.json').read_text())
    assert qf['queries_file_sha256']==sha(HERE/'QUERIES.json')
    out=HERE/'retrieval_results.json';events=HERE/'retrieval_events.jsonl'
    if out.exists() or events.exists():raise FileExistsError('Retrieval already started')
    from BCPlus.scripts.search_bcplus import BCPlusSearcher,PREFIX
    import numpy as np
    import torch
    s=BCPlusSearcher(); docpos={d:i for i,d in enumerate(s.docids)}
    byq={x['case_id']:x for x in json.loads((HERE/'QUERIES.json').read_text())}
    results=[]
    try:
        for case in order():
            cid=case['case_id'];query=byq[cid]['search_query'];hdocs=TRUTH[cid]['historically_seen_doc_ids']
            if not query:
                results.append({'case_id':cid,'G':[],'H':[],'error':'query_failure'});continue
            start=time.monotonic()
            try:
                batch=s.tokenizer(PREFIX+query,return_tensors='pt',truncation=False)
                if batch['input_ids'].shape[1]>8192:raise ValueError('query exceeds 8192 tokens')
                batch=batch.to(s.device)
                with torch.inference_mode():
                    hidden=s.model(**batch).last_hidden_state[:,-1]
                    vector=torch.nn.functional.normalize(hidden,p=2,dim=1).float().cpu().numpy()
                scores,positions=s.index.search(vector,5)
                global_hits=[{'docid':s.docids[int(pos)],'rank':i,'score':float(score)} for i,(score,pos) in enumerate(zip(scores[0],positions[0]),1)]
                historical=sorted([{'docid':d,'score':float(np.dot(vector[0],s.index.reconstruct(docpos[d])))} for d in hdocs],key=lambda x:(-x['score'],x['docid']))[:5]
                history_hits=[dict(x,rank=i) for i,x in enumerate(historical,1)]
                row={'case_id':cid,'G':global_hits,'H':history_hits,'error':None}
                emit(events,'retrieval',case_id=cid,query_sha256=byq[cid]['query_sha256'],result=row,latency_seconds=time.monotonic()-start)
            except Exception as exc:
                row={'case_id':cid,'G':[],'H':[],'error':type(exc).__name__+':'+str(exc)[:250]}
                emit(events,'error',case_id=cid,error=row['error'],latency_seconds=time.monotonic()-start)
            results.append(row);print(cid,'ok' if row['error'] is None else row['error'],flush=True)
    finally:s.close()
    out.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')

def analyze():
    rows=json.loads((HERE/'retrieval_results.json').read_text())
    if len(rows)!=len(BANK):raise AssertionError('incomplete retrieval')
    case={x['case_id']:x for x in BANK}
    scores=[]
    for r in rows:
        t=TRUTH[r['case_id']];suff=set(t['sufficient_doc_ids']);old=set(t['historically_seen_sufficient_doc_ids'])
        g=[x['docid'] for x in r['G']];h=[x['docid'] for x in r['H']]
        gr=next((i for i,d in enumerate(g,1) if d in suff),None)
        hr=next((i for i,d in enumerate(h,1) if d in suff),None)
        scores.append({'case_id':r['case_id'],'qid':t['qid'],'type':t['primary_type'],'G_first_sufficient_rank':gr,'H_first_sufficient_rank':hr,
          'G_old_source_hit5':bool(old.intersection(g)),'H_old_source_hit5':bool(old.intersection(h)),
          'G_new_source_hit5':bool((suff-set(t['historically_seen_doc_ids'])).intersection(g)),
          'G_seen_top5':sum(x in t['historically_seen_doc_ids'] for x in g),'G_unseen_top5':sum(x not in t['historically_seen_doc_ids'] for x in g),
          'G_misleading_rank':next((i for i,d in enumerate(g,1) if d in t['misleading_seen_doc_ids']),None),
          'error':r['error']})
    def rate(xs,p):return sum(p(x) for x in xs)/len(xs) if xs else None
    bytype={k:[x for x in scores if x['type']==k] for k in 'ABCD'}
    old=[x for x in scores if x['type'] in 'AB'];new=[x for x in scores if x['type'] in 'CD']
    qids=defaultdict(list)
    for x in scores:qids[x['qid']].append(x)
    summary={'sample_count':len(scores),'qids':len(qids),'type_counts':{k:len(v) for k,v in bytype.items()},
      'G_recall_at':{str(k):rate(scores,lambda x:x['G_first_sufficient_rank'] is not None and x['G_first_sufficient_rank']<=k) for k in (1,3,5)},
      'H_recall_at':{str(k):rate(scores,lambda x:x['H_first_sufficient_rank'] is not None and x['H_first_sufficient_rank']<=k) for k in (1,3,5)},
      'G_mrr_at5':sum(1/x['G_first_sufficient_rank'] if x['G_first_sufficient_rank'] else 0 for x in scores)/len(scores),
      'H_mrr_at5':sum(1/x['H_first_sufficient_rank'] if x['H_first_sufficient_rank'] else 0 for x in scores)/len(scores),
      'G_old_ab_recall5':rate(old,lambda x:x['G_old_source_hit5']),
      'H_old_ab_recall5':rate(old,lambda x:x['H_old_source_hit5']),
      'G_new_cd_recall5':rate(new,lambda x:x['G_new_source_hit5']),
      'G_recall5_by_type':{k:rate(v,lambda x:x['G_first_sufficient_rank'] is not None) for k,v in bytype.items()},
      'H_recall5_by_type':{k:rate(v,lambda x:x['H_first_sufficient_rank'] is not None) for k,v in bytype.items()},
      'qid_recall5':{q:rate(v,lambda x:x['G_first_sufficient_rank'] is not None) for q,v in qids.items()},
      'G_seen_top5_total':sum(x['G_seen_top5'] for x in scores),'G_unseen_top5_total':sum(x['G_unseen_top5'] for x in scores),
      'D_sufficient_before_misleading':sum(x['G_first_sufficient_rank'] is not None and (x['G_misleading_rank'] is None or x['G_first_sufficient_rank']<x['G_misleading_rank']) for x in bytype['D']),
      'D_count':len(bytype['D']),'query_failures':sum(x['error']=='query_failure' for x in scores),'retrieval_failures':sum(x['error'] not in (None,'query_failure') for x in scores),
      'per_case':scores}
    global_pass=summary['G_old_ab_recall5']>=.90 and summary['G_new_cd_recall5']>=.85 and summary['G_recall_at']['5']>=.88 and all(v>0 for v in summary['qid_recall5'].values())
    if global_pass:decision='U2_G'
    elif summary['G_old_ab_recall5']<.90 and summary['H_old_ab_recall5']>=.90:decision='U1B'
    else:decision='STOP_U1'
    summary['gate_decision']=decision
    (HERE/'results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('per_case','qid_recall5')},indent=2))

if __name__=='__main__':
    command=sys.argv[1]
    {'freeze':freeze,'gate':gate,'queries':queries,'retrieval_freeze':retrieval_freeze,'retrieve':retrieve,'analyze':analyze}[command]()
