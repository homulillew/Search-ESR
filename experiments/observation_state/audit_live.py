"""Audit API-visible observations and replay paired window variants."""
import sys,json,sqlite3,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from transformers import AutoTokenizer
from llm_chat.raw_windows import RawWindowBuilder
from llm_chat.structural_windows import TableEntryWindowBuilder,SafeTableEntryWindowBuilder
p=Path(sys.argv[1]).resolve();tok=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True);b=RawWindowBuilder(tok);c=TableEntryWindowBuilder(tok);safe=SafeTableEntryWindowBuilder(tok)
db=sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
reports=[];cache={}
for d in sorted(p.iterdir()):
 if not d.is_dir() or not (d/'observations.json').exists():continue
 summary=json.loads((d/'summary.json').read_text());events=json.loads((d/'observations.json').read_text());trace=[json.loads(l) for l in (d/'events.jsonl').read_text().splitlines()]
 tools={}
 for e in trace:
  if e['kind']=='api_request':
   for m in e['request']['messages']:
    if m['role']=='tool':tools[m['tool_call_id']]=json.loads(m['content'])
 recorded=[e['result'] for e in events]
 assert list(tools.values())==recorded
 row=dict(session=d.name,status=summary['status'],visible_payloads_match=True,returned_windows=0,counterfactual_changed_windows=0,errors=[v for v in tools.values() if isinstance(v,dict) and 'error' in v],source_mismatches=0,raw_mismatches=0,active_summary=summary['observations'],recovery=summary.get('recovery_passed',False))
 for event in events:
  for v in event['result'] if isinstance(event['result'],list) else [event['result']]:
   if 'window_ref' not in v:continue
   row['returned_windows']+=1;text,url=db.execute('select text,url from documents where docid=?',(v['docid'],)).fetchone()
   assert hashlib.sha256(text.encode()).hexdigest()==v['document_sha256']
   assert v['text']==text[v['offset']:v['end_char']]
   if event['tool'] in ['search','seed_search']:
    key=(event['arguments']['query'],v['docid'],summary['arm'])
    if key not in cache:
     old=b.search(v['docid'],text,url,key[0]);new=(safe if summary['arm']=='table_entry_safe' else c).search(v['docid'],text,url,key[0]);cache[key]=(old,new)
    old,new=cache[key];expected=old if summary['arm']=='baseline' else new
    assert all(v[k]==value for k,value in expected.items())
    row['counterfactual_changed_windows']+=old['window_ref']!=new['window_ref']
 reports.append(row)
(p/'audit.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2))
print(json.dumps(dict(sessions=len(reports),completed=sum(r['status']=='complete' for r in reports),payloads_verified=True,raw_verified=True,tool_errors=sum(len(r['errors']) for r in reports),returned_windows=sum(r['returned_windows'] for r in reports),counterfactual_changes=sum(r['counterfactual_changed_windows'] for r in reports),recoveries=sum(r['recovery'] for r in reports)),indent=2))
