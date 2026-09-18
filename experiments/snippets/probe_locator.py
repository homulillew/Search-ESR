"""Frozen-input locator ablations: top-3 parent pool and score-aware lexical terms."""
import json,re,math,hashlib,shutil,sys
from collections import Counter
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from llm_chat.raw_windows import RawWindowBuilder
from llm_chat.window_units import WindowSelector
from llm_chat.window_locator import terms
from transformers import AutoTokenizer


def score_terms(text):
    # Normalize dash variants; preserve score pair, suppress its constituent digits.
    value=re.sub(r'(\d+)\s*[-–—]\s*(\d+)',lambda m:' scorepair'+m[1]+'x'+m[2]+' ',text)
    return terms(value)


def rank(query, chunks, tokenizer=terms):
    fs=[Counter(tokenizer(c.text)) for c in chunks];lens=[sum(f.values()) for f in fs];avg=sum(lens)/len(lens) if lens else 1
    df=Counter(t for f in fs for t in f);qt=set(tokenizer(query));out=[]
    for i,(c,f,n) in enumerate(zip(chunks,fs,lens)):
        matches=sorted(qt&f.keys());score=sum(math.log(1+(len(chunks)-df[t]+.5)/(df[t]+.5))*f[t]*2.5/(f[t]+1.5*(.25+.75*n/(avg or 1))) for t in matches)
        out.append((score,-i,c,matches))
    return sorted(out,key=lambda x:(x[0],x[1]),reverse=True)


def main():
    source=ROOT/'experiments/offline/search_open_diagnosis/20260917T182655.718687Z'
    dest=ROOT/'experiments/offline/locator_ablation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');dest.mkdir(parents=True)
    import sqlite3
    db=sqlite3.connect(f"file:{ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite'}?mode=ro",uri=True)
    tok=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True,use_fast=True);builder=RawWindowBuilder(tok)
    config={'source':str(source.relative_to(ROOT)),'source_hash':hashlib.sha256((source/'diagnostics.jsonl').read_bytes()).hexdigest(),'arms':{'A':'unchanged','B_pool3':'original BM25 top3 parent chunks, joint unit BM25; exact spans deduplicated','C_scores':'top1 parent, score-pair lexical tokens at both stages; otherwise unchanged'},'scope':'Frozen 75 query/document pairs, no LLM/retrieval/gold. No production ranking changes.','code_hashes':{}}
    for path in [Path(__file__),ROOT/'llm_chat/raw_windows.py',ROOT/'llm_chat/window_locator.py',ROOT/'llm_chat/window_units.py']:
        shutil.copy2(path,dest/path.name);config['code_hashes'][path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
    rows=[]
    for line in (source/'diagnostics.jsonl').read_text().splitlines():
        old=json.loads(line);did=old['docid'];q=old['query'];text,url=db.execute('select text,url from documents where docid=?',(did,)).fetchone()
        a=builder.search(did,text,url,q);assert a==old['observation'];key=(did,a['document_sha256']);doc=builder.documents[key];cap=400-builder.count(doc['title']);arms={'A':a};details={}
        for name,count,lex in [('B_pool3',3,terms),('C_scores',1,score_terms)]:
            ranked=rank(q,doc['chunks'],lex);parents=[x for x in ranked[:count] if x[0]>0]
            candidates=[];seen=set()
            from dataclasses import replace
            for _,_,parent,_ in parents:
                local=WindowSelector(tok,budget=cap,overlap=0)
                for c,_ in local.units(did,parent.text):
                    c=replace(c,start_char=c.start_char+parent.start_char,end_char=c.end_char+parent.start_char)
                    span=(c.start_char,c.end_char)
                    if span not in seen:seen.add(span);candidates.append(c)
            candidates.sort(key=lambda c:c.start_char)
            anchors=rank(q,candidates,lex)
            if anchors and anchors[0][0]>0:
                anchor=anchors[0][2];start,end=builder._expand(key,anchor.start_char,anchor.end_char,cap);v=builder._emit(key,start,end)
            else:v=a
            assert v['text']==text[v['offset']:v['end_char']];assert v['text_tokens']+v['title_tokens']<=400
            arms[name]=v;details[name]={'parents':[{'start':c.start_char,'end':c.end_char,'score':s,'matches':m} for s,_,c,m in parents],
                'anchors':[{'start':c.start_char,'end':c.end_char,'text':c.text,'score':s,'matches':m} for s,_,c,m in anchors[:3]]}
        rows.append({k:old[k] for k in ['qid','search_number','query','docid']}|{'arms':arms,'details':details})
    (dest/'config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2));(dest/'results.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    summary={name:{'changed':sum(r['arms'][name]['text']!=r['arms']['A']['text'] for r in rows),'tokens':sum(r['arms'][name]['text_tokens']+r['arms'][name]['title_tokens'] for r in rows)} for name in ['A','B_pool3','C_scores']}
    (dest/'summary.json').write_text(json.dumps(summary,indent=2));print(dest);print(summary)
    for r in rows:
        if (r['qid'],r['search_number'],r['docid']) in [('517',5,'67431'),('546',1,'38231'),('546',1,'4975')]:
            print('\nCASE',r['qid'],r['docid'])
            for name,v in r['arms'].items():print(name,v['offset'],v['end_char'],v['text'])
    db.close()
if __name__=='__main__':main()
