"""Freeze actual retrieved documents and compare equal-cap prefix vs lexical chunks."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.snippets.selector import Selector
from transformers import AutoTokenizer


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--batch', default='20260917T090903.022551Z')
    ap.add_argument('--qids', nargs='+', default=['546','1094','517'])
    ap.add_argument('--budget', type=int, default=400)
    args = ap.parse_args()
    batchpath = ROOT/'experiments/batches'/args.batch/'batch.json'
    batch = json.loads(batchpath.read_text())
    dest = ROOT/'experiments/offline/snippets_v001'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    dest.mkdir(parents=True)
    tokenizer = AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B', local_files_only=True, use_fast=True)
    selector = Selector(tokenizer, args.budget)
    dbpath = ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite'
    db = sqlite3.connect(f'{dbpath.as_uri()}?mode=ro', uri=True)
    manifest = {'source_batch':args.batch,'qids':args.qids,'tokenizer':'/data/model/Qwen3-Embedding-8B',
                'per_document_text_token_cap':args.budget,'target_chunk_tokens':args.budget,'overlap_max_tokens':50,
                'ranking':'BM25 within each document; k1=1.5 b=0.75; unique query terms; ties prefer earliest',
                'scope':'Offline only. Original query, docids, order and document scores frozen. No gold or extra API calls.',
                'html_policy':'Raw HTML: both arms use prefix; flagged, no cleaning in this experiment.',
                'budget_note':'Equal upper bounds, not necessarily equal consumed tokens. Headers/JSON overhead excluded from text budget.',
                'source_sha256':{}}
    for name in ['selector.py','compare.py']:
        src=Path(__file__).parent/name; shutil.copy2(src,dest/name);manifest['source_sha256'][name]=hashlib.sha256(src.read_bytes()).hexdigest()
    (dest/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    cache={}; allrows=[]
    for qid in args.qids:
        run=ROOT/batch['runs'][qid]['directory']
        events=[json.loads(x) for x in (run/'events.jsonl').read_text().splitlines()]
        report=[f'# qid={qid} · 离线片段对照','', 'A/B 每篇文本上限相同，均为 '+str(args.budget)+' tokens；不是强制填满。原始 query 与 top-k 文档顺序固定。',
                'B 仅按 query 词项排序，无标准答案输入。以下每个条目均保留原文，不生成摘要。','']
        query=None; round_number=0
        for event in events:
            if event['kind']=='tool_start' and event['name']=='search':query=event['arguments']['query']
            if event['kind']!='tool_result' or event['name']!='search':continue
            round_number+=1
            report += [f'## 搜索 {round_number} · 原始事件 {event["seq"]}', '', f'Query: {query}', '']
            for rank, hit in enumerate(event['result'],1):
                did=hit['docid']
                if did not in cache:
                    row=db.execute('SELECT text,url FROM documents WHERE docid=?',(did,)).fetchone()
                    text,url=row
                    html=text.lstrip().lower().startswith(('<!doctype html','<html'))
                    cache[did]=(text,url,html,selector.prefix(text),[] if html else selector.chunks(did,text))
                text,url,html,prefix,chunks=cache[did]
                assert text[:len(hit['text'])]==hit['text'], 'Current corpus differs from recorded view'
                selected,why=selector.select(query,chunks) if not html else (None,{'fallback':'raw_html_deferred_use_prefix','matched_terms':[],'score':0.0})
                chosen=asdict(selected) if selected else {'chunk_id':None,'start_char':0,'end_char':len(prefix),'text':prefix,'tokens':selector.count(prefix),'boundary':'prefix_fallback'}
                assert chosen['text']==text[chosen['start_char']:chosen['end_char']]
                assert chosen['tokens']<=args.budget and selector.count(prefix)<=args.budget
                record={'qid':qid,'search_number':round_number,'source_event':event['seq'],'rank':rank,'query':query,'docid':did,'url':url,
                        'document_score':hit['score'],'document_chars':len(text),'document_sha256':hashlib.sha256(text.encode()).hexdigest(),
                        'raw_html':html,'chunk_count':len(chunks),'A':{'start_char':0,'end_char':len(prefix),'text':prefix,'tokens':selector.count(prefix)},
                        'B':chosen,'selection':why,'historical_view_chars':len(hit['text']),
                        'historical_view_tokens':selector.count(hit['text'])}
                allrows.append(record)
                report += [f'### Rank {rank} · docid {did}', '', f'URL: {url}',
                           f'全文 {len(text)} 字符；候选片段 {len(chunks)} 个；BM25={why["score"]:.4f}；匹配词：{", ".join(why["matched_terms"])}；回退：{why["fallback"]}', '',
                           f'**A：开头，{selector.count(prefix)} tokens，位置 [0, {len(prefix)})**','', '````text',prefix,'````','',
                           f'**B：所选片段，{chosen["tokens"]} tokens，位置 [{chosen["start_char"]}, {chosen["end_char"]})，边界 {chosen["boundary"]}**','',
                           '````text',chosen['text'],'````','']
            print(f'qid={qid} search={round_number} processed',flush=True)
        (dest/f'qid_{qid}.md').write_text('\n'.join(report))
    with (dest/'comparisons.jsonl').open('w') as f:
        for row in allrows:f.write(json.dumps(row,ensure_ascii=False)+'\n')
    summary={}
    for q in args.qids:
        rows=[r for r in allrows if r['qid']==q]
        summary[q]={'comparisons':len(rows),'distinct_documents':len({r['docid'] for r in rows}),
                    'nonprefix_selected':sum(r['B']['start_char']>0 for r in rows),
                    'selected_outside_historical_view':sum(r['B']['start_char']>=r['historical_view_chars'] for r in rows),
                    'fallback_count':sum(r['selection']['fallback'] is not None for r in rows),
                    'A_tokens':sum(r['A']['tokens'] for r in rows),'B_tokens':sum(r['B']['tokens'] for r in rows)}
    (dest/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    db.close();print('OUTPUT_DIR='+str(dest),flush=True)


if __name__=='__main__':main()
