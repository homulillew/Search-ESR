"""Frozen v004 candidates and quotas: prefix vs local query-centered windows."""
import hashlib
import json
import shutil
import sqlite3
import sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from experiments.snippets.short_window import shorten
from experiments.snippets.selector import Selector,terms
from transformers import AutoTokenizer
from llm_chat.agent import BCPlusTools


def main():
    source=ROOT/'experiments/offline/snippets_v004/20260917T173648.577447Z'
    dest=ROOT/'experiments/offline/snippets_v005'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');dest.mkdir(parents=True)
    manifest={'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256((source/'comparisons.jsonl').read_bytes()).hexdigest(),
      'scope':'Freeze v004 C parent chunks and D per-block quotas; compare D prefix with within-parent sentence/line BM25 anchor and context expansion. No global reranking, gold, API or online rollout.',
      'budget':'Same per-block quotas, total <=400 text tokens; metadata excluded; no redistribution after window construction.',
      'limits':['Regex sentence rules inherited from v002; only Markdown headings are section boundaries.','Cannot recover context outside parent chunk; parent edges may already be incomplete.','Oversize units may still be split. Local lexical matching is not semantic support.','Fitting blocks unchanged; sentence boundaries not retroactively repaired.'],
      'source_hashes':{}}
    for name in ['selector.py','window.py','short_window.py','compare_short_window.py']:
        path=Path(__file__).parent/name;shutil.copy2(path,dest/name);manifest['source_hashes'][name]=hashlib.sha256(path.read_bytes()).hexdigest()
    shutil.copy2(ROOT/'llm_chat/agent.py',dest/'agent_snapshot.py');manifest['source_hashes']['agent_snapshot.py']=hashlib.sha256((dest/'agent_snapshot.py').read_bytes()).hexdigest()
    (dest/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    tok=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True,use_fast=True);counter=Selector(tok)
    db=sqlite3.connect(f"file:{ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite'}?mode=ro",uri=True);opener=BCPlusTools()
    cache={};rows=[];reports={}
    for line in (source/'comparisons.jsonl').read_text().splitlines():
        old=json.loads(line);did=old['docid']
        if did not in cache:cache[did]=db.execute('select text from documents where docid=?',(did,)).fetchone()[0]
        text=cache[did];assert hashlib.sha256(text.encode()).hexdigest()==old['document_sha256']
        parents=old['arms']['C_whitespace'];baseline=old['arms']['D_equal_cap'];new=[];checks=[]
        for parent,previous in zip(parents,baseline):
            cap=previous.get('allocated_cap',400)
            view=shorten(old['query'],parent,cap,tok)
            assert parent['start_char']<=view['start_char']<=view['end_char']<=parent['end_char']
            assert view['text']==text[view['start_char']:view['end_char']]
            assert view['tokens']==counter.count(view['text'])<=cap
            parts=[];pos=view['start_char'];calls=[]
            while pos<view['end_char']:
                args={'docid':did,'offset':pos,'max_chars':min(12000,view['end_char']-pos)}
                result=opener.execute('get_document',args);assert result['text'];parts.append(result['text']);pos+=len(result['text']);calls.append(args)
            assert ''.join(parts)==view['text'];checks.append({'exact':True,'calls':calls})
            new.append(view)
        assert sum(c['tokens'] for c in new)<=400
        row={k:old[k] for k in ['qid','search_number','rank','query','docid','document_sha256']}
        row.update(A=baseline,B=new,open_checks=checks);rows.append(row)
        report=reports.setdefault(row['qid'],[f'# qid={row["qid"]} 前缀与短窗口',''])
        report += [f'## Search {row["search_number"]} / rank {row["rank"]} / docid {did}','',row['query'],'']
        for name in ('A','B'):
            report += [f'### {name}','']
            for c in row[name]:report += [f'{c["tokens"]} tokens / [{c["start_char"]}, {c["end_char"]})','','````text',c['text'],'````','']
    summary={}
    for qid,report in reports.items():
        (dest/f'qid_{qid}.md').write_text('\n'.join(report));group=[r for r in rows if r['qid']==qid]
        pairs=[(a,b,r['query']) for r in group for a,b in zip(r['A'],r['B'])]
        summary[qid]={'observations':len(group),'blocks':len(pairs),'A_tokens':sum(a['tokens'] for a,b,q in pairs),'B_tokens':sum(b['tokens'] for a,b,q in pairs),
          'changed_blocks':sum(a['text']!=b['text'] for a,b,q in pairs),'local_window_blocks':sum(b['method']=='local_anchor_window' for a,b,q in pairs),
          'oversize_anchors':sum((b.get('anchor') or {}).get('boundary')=='oversize_split' for a,b,q in pairs),
          'fewer_query_terms':sum(len(set(terms(b['text']))&set(terms(q)))<len(set(terms(a['text']))&set(terms(q))) for a,b,q in pairs)}
    (dest/'comparisons.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows));(dest/'summary.json').write_text(json.dumps(summary,indent=2))
    opener.close();db.close();print(dest);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
