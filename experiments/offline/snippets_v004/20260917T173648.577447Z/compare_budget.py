"""Whitespace-overlap ablation and equal-cap top-1/top-2 observation replay."""
import json
import hashlib
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from experiments.snippets.compare_multiblock import rank_chunks,choose_two
from experiments.snippets.selector import Selector
from transformers import AutoTokenizer
from llm_chat.agent import BCPlusTools


def fit_blocks(blocks,tokenizer,budget=400):
    if len(blocks)==1:return [dict(blocks[0])]
    # Allocate half to each; transfer unused quota when one source block is short.
    caps=[budget//2,budget-budget//2]
    for i in (0,1):
        if blocks[i]['tokens']<caps[i]:
            caps[1-i]+=caps[i]-blocks[i]['tokens'];caps[i]=blocks[i]['tokens']
    result=[]
    for block,cap in zip(blocks,caps):
        b=dict(block)
        if b['tokens']>cap:
            s=Selector(tokenizer,budget=cap,overlap=0)
            raw=s.prefix(b['text'])
            b.update(text=raw,end_char=b['start_char']+len(raw),tokens=s.count(raw))
        b['parent_chunk_id']=b.pop('chunk_id',None)
        b['view_id']=hashlib.sha256(f"{b['parent_chunk_id']}:{b['start_char']}:{b['end_char']}".encode()).hexdigest()[:24]
        b['allocated_cap']=cap
        result.append(b)
    return result


def main():
    source=ROOT/'experiments/offline/snippets_v001/20260917T095014.433850Z'
    dest=ROOT/'experiments/offline/snippets_v004'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');dest.mkdir(parents=True)
    manifest={'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256((source/'comparisons.jsonl').read_bytes()).hexdigest(),
      'arms':{'A':'Original top1 <=400','B_strict':'Original strict-disjoint top2 <=800','C_whitespace':'Allow only whitespace overlap top2 <=800','D_equal_cap':'C blocks clipped at prefixes to 200+200; unused quota from short source block transferred; total <=400'},
      'scope':'Frozen queries/chunks/BM25. No gold, LLM or online rollout. Query-local needs only.',
      'limitations':['Same upper bound, not identical consumed tokens. Text-only budget excludes metadata.','Prefix clipping can cut sentences and discard query matches; this experiment evaluates this explicit allocation policy, not all multiblock methods.','Whitespace overlap retained verbatim and counted in each block; substantive overlap still excluded.'],
      'source_hashes':{}}
    for file in ['selector.py','compare_multiblock.py','compare_budget.py']:
        p=Path(__file__).parent/file;shutil.copy2(p,dest/file);manifest['source_hashes'][file]=hashlib.sha256(p.read_bytes()).hexdigest()
    shutil.copy2(ROOT/'llm_chat/agent.py',dest/'agent_snapshot.py')
    manifest['source_hashes']['agent_snapshot.py']=hashlib.sha256((dest/'agent_snapshot.py').read_bytes()).hexdigest()
    (dest/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    tok=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True,use_fast=True);s=Selector(tok)
    db=sqlite3.connect(f"file:{ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite'}?mode=ro",uri=True)
    opener=BCPlusTools();cache={};rows=[];reports={}
    for line in (source/'comparisons.jsonl').read_text().splitlines():
        old=json.loads(line);did=old['docid']
        if did not in cache:
            t=db.execute('select text from documents where docid=?',(did,)).fetchone()[0]
            cache[did]=(t,s.chunks(did,t) if not old['raw_html'] else [])
        text,chunks=cache[did];assert hashlib.sha256(text.encode()).hexdigest()==old['document_sha256']
        ranked=rank_chunks(old['query'],chunks)
        strict,_=choose_two(ranked);relaxed,_=choose_two(ranked,text)
        if not strict:strict=[old['B']];relaxed=[old['B']]
        assert strict[0]['chunk_id']==relaxed[0]['chunk_id']==old['B']['chunk_id']
        arms={'A':[strict[0]],'B_strict':strict,'C_whitespace':relaxed,'D_equal_cap':fit_blocks(relaxed,tok)}
        checks={}
        for name,blocks in arms.items():
            assert sum(c['tokens'] for c in blocks)<=(400 if name in ('A','D_equal_cap') else 800)
            for c in blocks:
                a,b=c['start_char'],c['end_char'];assert c['text']==text[a:b];assert s.count(c['text'])==c['tokens']
                key=f'{a}:{b}'
                if key not in checks:
                    pos=a;parts=[];calls=[]
                    while pos<b:
                        args={'docid':did,'offset':pos,'max_chars':min(12000,b-pos)}
                        out=opener.execute('get_document',args);assert out['text'];parts.append(out['text']);pos+=len(out['text']);calls.append(args)
                    assert ''.join(parts)==c['text'];checks[key]={'exact':True,'calls':calls}
        row={k:old[k] for k in ['qid','search_number','rank','query','docid','document_sha256']};row.update(arms=arms,open_checks=checks);rows.append(row)
        report=reports.setdefault(row['qid'],[f'# qid={row["qid"]} 空白重叠与等预算对照',''])
        report += [f'## Search {row["search_number"]} / rank {row["rank"]} / docid {did}','',row['query'],'']
        for name,blocks in arms.items():
            report += [f'### {name}','']
            for c in blocks:report += [f'{c["tokens"]} tokens / [{c["start_char"]}, {c["end_char"]})','','````text',c['text'],'````','']
    summary={}
    for qid,report in reports.items():
        group=[r for r in rows if r['qid']==qid];(dest/f'qid_{qid}.md').write_text('\n'.join(report))
        summary[qid]={'observations':len(group),'arms':{name:{'tokens':sum(c['tokens'] for r in group for c in r['arms'][name]),'two_blocks':sum(len(r['arms'][name])==2 for r in group)} for name in arms},
          'whitespace_changed_selection':sum([c['chunk_id'] for c in r['arms']['B_strict']]!=[c['chunk_id'] for c in r['arms']['C_whitespace']] for r in group),'open_exact_spans':sum(len(r['open_checks']) for r in group)}
    (dest/'comparisons.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows));(dest/'summary.json').write_text(json.dumps(summary,indent=2))
    opener.close();db.close();print(dest);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
