"""Real-corpus search observation/open smoke checks; no retriever or LLM calls."""
import json
import hashlib
import shutil
import sqlite3
import sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from llm_chat.raw_windows import RawWindowBuilder
from transformers import AutoTokenizer


def main():
    dest=ROOT/'experiments/offline/raw_windows_v001'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');dest.mkdir(parents=True)
    b=RawWindowBuilder(AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True,use_fast=True))
    db=sqlite3.connect(f"file:{ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite'}?mode=ro",uri=True)
    cases=[('67431','actor played policeman in The Constant Gardener 2005'),('23800','2008 Champions League final 95th minute free kick'),('84585','"Mark Selby" 2023 Players Championship snooker results'),('55516','"Mark Selby" 2023 Players Championship snooker results')]
    rows=[]
    for did,q in cases:
        text,url=db.execute('select text,url from documents where docid=?',(did,)).fetchone()
        search=b.search(did,text,url,q);assert search['text_tokens']+search['title_tokens']<=400
        initial=b.windows[search['window_ref']]
        opened={d:b.open(search['window_ref'],d) for d in ['before','after','around']}
        for v in [search,*opened.values()]:assert v['text']==text[v['offset']:v['end_char']]
        assert b.windows[search['window_ref']]==initial
        assert search['text'] in opened['around']['text']
        # Repeated around saturates explicitly; after advances to document end.
        cursor=search
        for _ in range(500):
            if not cursor['has_more_after']:break
            nxt=b.open(cursor['window_ref'],'after');assert nxt['end_char']>cursor['end_char'];cursor=nxt
        assert not cursor['has_more_after']
        rows.append(dict(docid=did,query=q,search=search,open=opened,forward_paging_reaches_end=True))
    (dest/'results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    manifest={'scope':'Four real documents with fixed queries, no document recall, no API; structural checks only.','source_sha256':{}}
    for name in ['raw_windows.py','window_locator.py','window_units.py','agent.py']:
        p=ROOT/'llm_chat'/name;shutil.copy2(p,dest/name);manifest['source_sha256'][name]=hashlib.sha256(p.read_bytes()).hexdigest()
    shutil.copy2(__file__,dest/'check_raw_windows.py')
    (dest/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(dest)
    for r in rows:print(r['docid'],r['search']['title'],r['search']['text_tokens'],r['search']['offset'])
    db.close()
if __name__=='__main__':main()
