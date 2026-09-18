"""Frozen v001 top-1 versus nonoverlapping top-2, 400 tokens per block."""
import json
import math
import hashlib
import shutil
import sqlite3
import sys
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from experiments.snippets.selector import Selector, terms
from llm_chat.agent import BCPlusTools
from transformers import AutoTokenizer


def rank_chunks(query, chunks):
    frequencies = [Counter(terms(c.text)) for c in chunks]
    lengths = [sum(f.values()) for f in frequencies]
    avg = sum(lengths)/len(lengths) if lengths else 1
    df = Counter(t for f in frequencies for t in f)
    result = []
    for i,(c,f,n) in enumerate(zip(chunks,frequencies,lengths)):
        matches = sorted(set(terms(query)) & f.keys())
        score = sum(math.log(1+(len(chunks)-df[t]+.5)/(df[t]+.5))*f[t]*2.5/(f[t]+1.5*(.25+.75*n/(avg or 1))) for t in matches)
        result.append(dict(asdict(c),score=score,matched_terms=matches,index=i))
    return sorted(result,key=lambda c:(-c['score'],c['index']))


def choose_two(ranked):
    chosen, skipped = [], []
    for rank,c in enumerate(ranked,1):
        if c['score'] <= 0:
            break
        if any(c['start_char'] < x['end_char'] and x['start_char'] < c['end_char'] for x in chosen):
            skipped.append(rank)
            continue
        chosen.append(dict(c,bm25_rank=rank))
        if len(chosen)==2:
            break
    return chosen,skipped


def main():
    source = ROOT/'experiments/offline/snippets_v001/20260917T095014.433850Z'
    dest = ROOT/'experiments/offline/snippets_v003'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    dest.mkdir(parents=True)
    manifest = {'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256((source/'comparisons.jsonl').read_bytes()).hexdigest(),
      'scope':'Query-local information need only. Frozen historical query/documents/order; no gold or LLM calls.',
      'A':'v001 BM25 top-1 <=400 text tokens','B':'same top-1 plus highest positive-score nonoverlapping block; <=800 total text tokens',
      'ranking':'identical v001 BM25 k1=1.5 b=.75, same chunks, tie earliest; exact top-1 equality asserted',
      'limitations':['Additional-budget experiment; not fixed-total-budget comparison.','Character overlap excluded; semantic redundancy remains.','Historical queries are not newly decomposed single-constraint tasks.','No online behavior/answer evaluation.'],
      'open_check':'Actual BCPlusTools.get_document at each block start; paginate if >12000 characters; assert exact raw text.',
      'code_sha256':{}}
    for name in ['selector.py','compare_multiblock.py']:
        p=Path(__file__).parent/name;shutil.copy2(p,dest/name);manifest['code_sha256'][name]=hashlib.sha256(p.read_bytes()).hexdigest()
    shutil.copy2(ROOT/'llm_chat/agent.py',dest/'agent_snapshot.py')
    manifest['code_sha256']['agent_snapshot.py']=hashlib.sha256((dest/'agent_snapshot.py').read_bytes()).hexdigest()
    (dest/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    s=Selector(AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True,use_fast=True))
    dbpath=ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite'
    db=sqlite3.connect(f'{dbpath.as_uri()}?mode=ro',uri=True)
    opener=BCPlusTools(); cache={}; rows=[]; reports={}
    for line in (source/'comparisons.jsonl').read_text().splitlines():
        old=json.loads(line);did=old['docid']
        if did not in cache:
            text=db.execute('SELECT text FROM documents WHERE docid=?',(did,)).fetchone()[0]
            cache[did]=(text,s.chunks(did,text) if not old['raw_html'] else [])
        text,chunks=cache[did]
        assert hashlib.sha256(text.encode()).hexdigest()==old['document_sha256']
        ranked=rank_chunks(old['query'],chunks)
        chosen,skipped=choose_two(ranked)
        if chosen:
            assert chosen[0]['chunk_id']==old['B']['chunk_id']
            assert abs(chosen[0]['score']-old['selection']['score']) < 1e-9
        else:
            chosen=[dict(old['B'],score=0,matched_terms=[],bm25_rank=None)]
        checks=[]
        for c in chosen:
            assert c['text']==text[c['start_char']:c['end_char']]
            assert s.count(c['text'])==c['tokens']<=400
            pos=c['start_char'];parts=[];calls=[]
            while pos<c['end_char']:
                args={'docid':did,'offset':pos,'max_chars':min(12000,c['end_char']-pos)}
                response=opener.execute('get_document',args)
                parts.append(response['text']);calls.append(args);pos+=len(response['text'])
                assert response['text']
            assert ''.join(parts)==c['text']
            checks.append({'calls':calls,'exact_match':True})
        row={k:old[k] for k in ['qid','search_number','source_event','rank','query','docid','url','document_score','document_sha256']}
        row.update(A=[chosen[0]],B=chosen,skipped_overlap_ranks=skipped,open_checks=checks)
        rows.append(row)
        report=reports.setdefault(row['qid'],[f'# qid={row["qid"]} 单块 / 多块对照',''])
        report += [f'## Search {row["search_number"]} / Rank {row["rank"]} / docid {did}','',row['query'],'']
        for i,c in enumerate(chosen,1):
            report += [f'### Block {i} · BM25 rank {c["bm25_rank"]} · {c["tokens"]} tokens · [{c["start_char"]}, {c["end_char"]})','', '````text',c['text'],'````','']
    (dest/'comparisons.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    summary={}
    for qid,report in reports.items():
        (dest/f'qid_{qid}.md').write_text('\n'.join(report))
        group=[r for r in rows if r['qid']==qid]
        summary[qid]={'observations':len(group),'two_blocks':sum(len(r['B'])==2 for r in group),
          'A_tokens':sum(r['A'][0]['tokens'] for r in group),'B_tokens':sum(c['tokens'] for r in group for c in r['B']),
          'skipped_overlap_candidates':sum(len(r['skipped_overlap_ranks']) for r in group),
          'open_exact_checks':sum(len(r['open_checks']) for r in group)}
    (dest/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    opener.close();db.close();print(dest);print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
