import sys,json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from transformers import AutoTokenizer
from llm_chat.raw_windows import RawWindowBuilder
from llm_chat.structural_windows import TableEntryWindowBuilder,SafeTableEntryWindowBuilder
p=Path(sys.argv[1]).resolve();tok=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True)
b=RawWindowBuilder(tok);old=TableEntryWindowBuilder(tok);safe=SafeTableEntryWindowBuilder(tok);db=sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
local=json.loads((ROOT/'experiments/local_support/runs/20260917T184725.353925Z/tasks.offline.json').read_text());rows=[]
for t in local:
 text,url=db.execute('select text,url from documents where docid=?',(t['docid'],)).fetchone();a=b.search(t['docid'],text,url,t['query']);z=safe.search(t['docid'],text,url,t['query']);span=t['reference_span']
 hit=lambda v:None if span is None else v['offset']<=span[0] and v['end_char']>=span[1]
 assert z['text']==text[z['offset']:z['end_char']] and z['title_tokens']+z['text_tokens']<=400
 rows.append(dict(task=t['id'],baseline_hit=hit(a),safe_hit=hit(z),repair=safe.last_repair))
checks=[]
for r in json.loads((p/'live/qid_905__table_entry/structural_changes.json').read_text()):
 text,url=db.execute('select text,url from documents where docid=?',(r['docid'],)).fetchone();a=b.search(r['docid'],text,url,r['query']);v=safe.search(r['docid'],text,url,r['query'])
 assert v==a and safe.last_repair['status']=='unchanged_existing_table_rows'
 checks.append(dict(docid=r['docid'],query=r['query'],baseline_preserved=True,repair=safe.last_repair))
new=[]
for r in json.loads((p/'observations.json').read_text()):
 text,url=db.execute('select text,url from documents where docid=?',(r['docid'],)).fetchone();v=safe.search(r['docid'],text,url,r['query']);assert v==r['baseline'];new.append(r['docid'])
result=dict(local_cases=len(rows),baseline_hits=sum(r['baseline_hit'] is True for r in rows),safe_hits=sum(r['safe_hit'] is True for r in rows),regressions=sum(r['baseline_hit'] is True and r['safe_hit'] is False for r in rows),new_initial_windows_unchanged=len(new),risky_searches_guarded=len(checks))
(p/'safe_check.json').write_text(json.dumps(dict(summary=result,local=rows,guards=checks),ensure_ascii=False,indent=2));print(json.dumps(result,indent=2))
