"""GPU replay of the frozen U1 document retrieval only; CPU results remain intact."""
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
U1=HERE.parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(U1))
sys.path.insert(0,str(ROOT))
import run_u1 as prior

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def freeze():
    path=HERE/'freeze.json'
    if path.exists():raise FileExistsError(path)
    prior.gate()
    reference=json.loads((U1/'retrieval_freeze.json').read_text())
    inputs={'bank':sha(U1/'BANK.json'),'truth':sha(U1/'PRIVATE_TRUTH.json'),
            'queries':sha(U1/'QUERIES.json'),'retrieval_freeze':sha(U1/'retrieval_freeze.json'),
            'cpu_results':sha(U1/'retrieval_results.json'),'runner':sha(__file__),
            'protocol':sha(HERE/'PROTOCOL.md')}
    assert inputs['queries']==reference['queries_file_sha256']
    path.write_text(json.dumps({'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      'device':'cuda:1','model_dtype':'float16','sample_count':40,'search_k':5,'historical_k':5,
      'query_order':[x['case_id'] for x in prior.order()], 'inputs_sha256':inputs,
      'scoring':'unchanged BCPlusSearcher Qwen3 normalized final-token query vector with FAISS inner product; historical candidates scored by the same IP',
      'failure_policy':'one GPU replay; all failures preserved; no Query Writer or query rewrite, no overwrite of CPU data'},indent=2)+'\n')

def gate():
    f=json.loads((HERE/'freeze.json').read_text());prior.gate()
    assert f['device']=='cuda:1' and f['sample_count']==40
    paths={'bank':U1/'BANK.json','truth':U1/'PRIVATE_TRUTH.json','queries':U1/'QUERIES.json',
           'retrieval_freeze':U1/'retrieval_freeze.json','cpu_results':U1/'retrieval_results.json',
           'runner':Path(__file__),'protocol':HERE/'PROTOCOL.md'}
    assert f['inputs_sha256']=={k:sha(v) for k,v in paths.items()}
    assert f['query_order']==[x['case_id'] for x in prior.order()]

def retrieve():
    gate()
    assert os.environ.get('BCPLUS_DEVICE')=='cuda:1','Set BCPLUS_DEVICE=cuda:1'
    out=HERE/'retrieval_results.json';events=HERE/'events.jsonl'
    if out.exists() or events.exists():raise FileExistsError('GPU replay already started')
    from BCPlus.scripts.search_bcplus import BCPlusSearcher,PREFIX
    import numpy as np
    import torch
    try:
        searcher=BCPlusSearcher()
    except Exception as exc:
        (HERE/'initialization_failure.json').write_text(json.dumps({'error_type':type(exc).__name__,'error':str(exc),
          'queries_executed':0},indent=2)+'\n')
        raise
    assert searcher.device=='cuda:1'
    assert next(searcher.model.parameters()).dtype==torch.float16
    positions_by_docid={d:i for i,d in enumerate(searcher.docids)}
    queries={x['case_id']:x for x in json.loads((U1/'QUERIES.json').read_text())}
    results=[]
    try:
        for case in prior.order():
            cid=case['case_id'];query=queries[cid]['search_query'];start=time.monotonic()
            try:
                batch=searcher.tokenizer(PREFIX+query,return_tensors='pt',truncation=False)
                if batch['input_ids'].shape[1]>8192:raise ValueError('query exceeds 8192 tokens')
                batch=batch.to(searcher.device)
                with torch.inference_mode():
                    hidden=searcher.model(**batch).last_hidden_state[:,-1]
                    vector=torch.nn.functional.normalize(hidden,p=2,dim=1).float().cpu().numpy()
                scores,positions=searcher.index.search(vector,5)
                g=[{'docid':searcher.docids[int(pos)],'rank':i,'score':float(score)}
                   for i,(score,pos) in enumerate(zip(scores[0],positions[0]),1)]
                hdocs=prior.TRUTH[cid]['historically_seen_doc_ids']
                historical=sorted([{'docid':d,'score':float(np.dot(vector[0],searcher.index.reconstruct(positions_by_docid[d])))}
                                   for d in hdocs],key=lambda x:(-x['score'],x['docid']))[:5]
                h=[dict(x,rank=i) for i,x in enumerate(historical,1)]
                row={'case_id':cid,'G':g,'H':h,'error':None}
            except Exception as exc:
                row={'case_id':cid,'G':[],'H':[],'error':type(exc).__name__+':'+str(exc)[:250]}
            results.append(row)
            with events.open('a') as f:f.write(json.dumps({'case_id':cid,'query_sha256':queries[cid]['query_sha256'],
               'result':row,'latency_seconds':time.monotonic()-start})+'\n')
            print(cid,'ok' if row['error'] is None else row['error'],flush=True)
    finally:searcher.close()
    out.write_text(json.dumps(results,indent=2)+'\n')

def analyze():
    gpu=json.loads((HERE/'retrieval_results.json').read_text())
    cpu={x['case_id']:x for x in json.loads((U1/'retrieval_results.json').read_text())}
    assert len(gpu)==40
    per=[];groups=defaultdict(list)
    for row in gpu:
        cid=row['case_id'];truth=prior.TRUTH[cid]
        suff=set(truth['sufficient_doc_ids']);seen=set(truth['historically_seen_doc_ids'])
        g=[x['docid'] for x in row['G']];h=[x['docid'] for x in row['H']]
        gr=next((i for i,d in enumerate(g,1) if d in suff),None)
        hr=next((i for i,d in enumerate(h,1) if d in suff),None)
        old=bool(suff.intersection(seen).intersection(g));new=bool((suff-seen).intersection(g))
        oldrank=next((i for i,d in enumerate(g,1) if d in truth['misleading_seen_doc_ids']),None)
        cpug=[x['docid'] for x in cpu[cid]['G']]
        result={'case_id':cid,'qid':truth['qid'],'type':truth['primary_type'],'G_rank':gr,'H_rank':hr,
           'old_hit5':old,'new_hit5':new,'misleading_rank':oldrank,'top5_changed':g!=cpug,
           'cpu_G':[x['docid'] for x in cpu[cid]['G']],'gpu_G':g,'error':row['error']}
        per.append(result);groups[truth['qid']].append(result)
    def rate(xs,p):return sum(p(x) for x in xs)/len(xs)
    old=[x for x in per if x['type'] in 'AB'];new=[x for x in per if x['type'] in 'CD']
    summary={'sample_count':len(per),'G_recall_at':{str(k):rate(per,lambda x:x['G_rank'] is not None and x['G_rank']<=k) for k in (1,3,5)},
       'G_old_ab_recall5':rate(old,lambda x:x['old_hit5']),'H_old_ab_recall5':rate(old,lambda x:x['H_rank'] is not None),
       'G_new_cd_recall5':rate(new,lambda x:x['new_hit5']),
       'G_recall5_by_type':{t:rate([x for x in per if x['type']==t],lambda x:x['G_rank'] is not None) for t in 'ABCD'},
       'qid_recall5':{q:rate(xs,lambda x:x['G_rank'] is not None) for q,xs in groups.items()},
       'changed_top5_cells':sum(x['top5_changed'] for x in per),'retrieval_errors':sum(x['error'] is not None for x in per),
       'per_case':per}
    passed=summary['G_old_ab_recall5']>=.90 and summary['G_new_cd_recall5']>=.85 and summary['G_recall_at']['5']>=.88 and all(v>0 for v in summary['qid_recall5'].values())
    summary['gate_decision']='U2_G' if passed else 'U1B' if summary['G_old_ab_recall5']<.90 and summary['H_old_ab_recall5']>=.90 else 'STOP_U1'
    (HERE/'results.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('per_case','qid_recall5')},indent=2))

if __name__=='__main__':
    {'freeze':freeze,'gate':gate,'retrieve':retrieve,'analyze':analyze}[sys.argv[1]]()
