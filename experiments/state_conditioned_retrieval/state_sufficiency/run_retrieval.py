"""Frozen Qwen3/FAISS top50 search for every one-shot S1/control query."""
import hashlib
import json
import os
import sys
from pathlib import Path

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
sys.path.insert(0,str(ROOT))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    freeze=json.loads((BASE/'freeze.json').read_text())
    manifest=json.loads((BASE/'query_outputs_commit.json').read_text())
    assert sha(BASE/'QUERIES.json')==manifest['queries_sha256']
    assert sha(BASE/'query_events.jsonl')==manifest['events_sha256']
    assert sha(ROOT/'BCPlus/scripts/search_bcplus.py')==freeze['retriever_sha256']
    queries=json.loads((BASE/'QUERIES.json').read_text())
    truth={x['case_id']:x for x in json.loads((BASE.parent/'state_bank/PRIVATE_TRUTH.json').read_text())}
    assert len(queries)==120 and len(truth)==24
    outpath=BASE/'retrieval_results.json'
    assert not outpath.exists(), 'retrieval already run'
    os.environ['BCPLUS_DEVICE']=freeze['device']
    from BCPlus.scripts.search_bcplus import BCPlusSearcher,PREFIX
    import torch
    searcher=BCPlusSearcher()
    rows=[]
    try:
        for n,q in enumerate(queries,1):
            cid=q['case_id']; target=truth[cid]; query=q['search_query']
            row={'case_id':cid,'qid':q['qid'],'arm':q['arm'],
                 'query_sha256':q['query_sha256'],'query_error':q['error'],
                 'hits':[],'first_sufficient_rank':None,'first_bridge_rank':None,
                 'first_sufficient_docid':None,'first_bridge_docid':None,'retrieval_error':None}
            if query:
                try:
                    batch=searcher.tokenizer(PREFIX+query,return_tensors='pt',truncation=False)
                    if batch['input_ids'].shape[1]>8192:
                        raise ValueError('query exceeds 8192 tokens')
                    with torch.inference_mode():
                        hidden=searcher.model(**batch.to(searcher.device)).last_hidden_state[:,-1]
                        vector=torch.nn.functional.normalize(hidden,p=2,dim=1).float().cpu().numpy()
                    scores,positions=searcher.index.search(vector,50)
                    row['hits']=[{'rank':i,'docid':searcher.docids[int(pos)],'score':float(score)}
                                 for i,(score,pos) in enumerate(zip(scores[0],positions[0]),1)]
                    direct=set(target['sufficient_doc_ids']); bridge=set(target['bridge_doc_ids'])
                    d=next((h for h in row['hits'] if h['docid'] in direct),None)
                    b=next((h for h in row['hits'] if h['docid'] in bridge),None)
                    if d:
                        row['first_sufficient_rank']=d['rank'];row['first_sufficient_docid']=d['docid']
                    if b:
                        row['first_bridge_rank']=b['rank'];row['first_bridge_docid']=b['docid']
                except Exception as exc:
                    row['retrieval_error']={'type':type(exc).__name__,'message':str(exc)[:500]}
            rows.append(row)
            print(f"{n}/120 {cid} {q['arm']} D={row['first_sufficient_rank']} B={row['first_bridge_rank']}",flush=True)
    finally:
        searcher.close()
    outpath.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    print('complete',len(rows),'retrieval errors',sum(x['retrieval_error'] is not None for x in rows),flush=True)

if __name__=='__main__':main()
