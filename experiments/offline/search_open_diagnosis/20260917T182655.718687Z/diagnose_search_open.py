"""Freeze real search inputs; inspect locator, display, and continuation independently."""
import hashlib
import json
import shutil
import sqlite3
import sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from llm_chat.raw_windows import RawWindowBuilder
from llm_chat.window_units import WindowSelector
from experiments.snippets.compare_multiblock import rank_chunks
from transformers import AutoTokenizer


def main():
    batch=ROOT/'experiments/batches/20260917T181920.573676Z'
    manifest=json.loads((batch/'batch.json').read_text())
    dest=ROOT/'experiments/offline/search_open_diagnosis'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');dest.mkdir(parents=True)
    config={'source_batch':str(batch.relative_to(ROOT)),'scope':'Frozen real query/documents/order; no model/retriever calls. All three open directions probed offline, not model decisions. No QA labels used.','source_sha256':{},'trace_sha256':{}}
    for relative in ['llm_chat/raw_windows.py','llm_chat/window_locator.py','llm_chat/window_units.py','experiments/snippets/compare_multiblock.py','experiments/snippets/diagnose_search_open.py']:
        src=ROOT/relative;shutil.copy2(src,dest/src.name);config['source_sha256'][relative]=hashlib.sha256(src.read_bytes()).hexdigest()
    tok=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True,use_fast=True);builder=RawWindowBuilder(tok)
    db=sqlite3.connect(f"file:{ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite'}?mode=ro",uri=True)
    rows=[]
    for qid,run in manifest['runs'].items():
        path=ROOT/run['directory']/'events.jsonl';config['trace_sha256'][qid]=hashlib.sha256(path.read_bytes()).hexdigest();query=None;n=0
        for e in map(json.loads,path.read_text().splitlines()):
            if e['kind']=='tool_start' and e['name']=='search':query=e['arguments']['query']
            if e['kind']!='tool_result' or e['name']!='search':continue
            n+=1
            for hit in e['result']:
                did=hit['docid'];text,url=db.execute('select text,url from documents where docid=?',(did,)).fetchone()
                observed=builder.search(did,text,url,query)
                assert observed=={k:v for k,v in hit.items() if k!='score'}
                key=(did,observed['document_sha256']);doc=builder.documents[key]
                ranked=rank_chunks(query,doc['chunks'])
                chunk=ranked[0] if ranked and ranked[0]['score']>0 else None
                anchors=[]
                if chunk:
                    local=WindowSelector(tok,budget=400-builder.count(doc['title']),overlap=0)
                    units=local.units(did,chunk['text'])
                    anchors=rank_chunks(query,[u[0] for u in units])[:3]
                    for a in anchors:
                        a['start_char']+=chunk['start_char'];a['end_char']+=chunk['start_char']
                opened={d:builder.open(observed['window_ref'],d) for d in ('before','after','around')}
                for v in opened.values():assert v['text']==text[v['offset']:v['end_char']]
                rows.append({'qid':qid,'search_number':n,'event':e['seq'],'query':query,'docid':did,'document_chars':len(text),
                  'top_chunks':ranked[:3],'top_anchors_in_winning_chunk':anchors,'observation':observed,'open_probes':opened})
    (dest/'config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2))
    (dest/'diagnostics.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    summary={'observations':len(rows),'distinct_documents':len({r['docid'] for r in rows}),'exact_replays':len(rows),'open_probes':len(rows)*3,
      'already_full_documents':sum(not r['observation']['has_more_before'] and not r['observation']['has_more_after'] for r in rows),
      'around_unchanged':sum(r['observation']['window_ref']==r['open_probes']['around']['window_ref'] for r in rows)}
    (dest/'summary.json').write_text(json.dumps(summary,indent=2))
    print(dest);print(summary)
    for r in rows:
        if (r['qid'],r['search_number'],r['docid']) in [('517',5,'67431'),('546',1,'38231'),('546',1,'4975'),('1094',1,'39918')]:
            print('\nCASE',r['qid'],r['search_number'],r['docid'],r['query'])
            for c in r['top_chunks']:print('CHUNK',c['start_char'],c['end_char'],c['score'],c['matched_terms'])
            for a in r['top_anchors_in_winning_chunk']:print('ANCHOR',a['score'],a['text'][:300])
            for d,v in r['open_probes'].items():print('OPEN',d,v['offset'],v['end_char'],v['status'],'Policeman 1' in v['text'])
    db.close()
if __name__=='__main__':main()
