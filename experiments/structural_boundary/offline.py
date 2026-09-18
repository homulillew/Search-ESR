import json,sys,sqlite3,hashlib,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from transformers import AutoTokenizer
from llm_chat.raw_windows import RawWindowBuilder
from experiments.structural_boundary.candidate import TableEntryWindowBuilder
out=ROOT/'experiments/structural_boundary/runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
print('OUTPUT_DIR='+str(out),flush=True)
tok=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True,use_fast=True)
b=RawWindowBuilder(tok);c=TableEntryWindowBuilder(tok)
db=sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
local=json.loads((ROOT/'experiments/local_support/runs/20260917T184725.353925Z/tasks.offline.json').read_text())
items=[dict(id=t['id'],docid=t['docid'],query=t['query'],group='local20',reference_span=t['reference_span']) for t in local]
for d in sorted((ROOT/'experiments/api_acceptance/runs/20260918T023027Z').glob('local_*')):
 q=None
 for line in (d/'events.jsonl').read_text().splitlines():
  e=json.loads(line)
  if e['kind']=='tool_start' and e['name']=='search':q=e['arguments']['query']
  if e['kind']=='tool_result' and e['name']=='search':
   for v in e['result']:items.append(dict(id=f'{d.name}_{e["seq"]}_{v["docid"]}',docid=v['docid'],query=q,group='replay610',reference_span=None))
cache={};rows=[]
for i,t in enumerate(items):
 pair=(t['docid'],t['query'])
 if pair not in cache:
  text,url=db.execute('select text,url from documents where docid=?',(t['docid'],)).fetchone()
  old=b.search(t['docid'],text,url,t['query']);new=c.search(t['docid'],text,url,t['query']);repair=c.last_repair
  assert new['text']==text[new['offset']:new['end_char']]
  assert new['text_tokens']+new['title_tokens']<=400
  assert set(old)==set(new)
  if repair and repair['status']=='repaired':
   a,z=repair['protected_anchor'];assert new['offset']<=a and new['end_char']>=z
   # Check all directions from candidate remain raw and callable.
   for direction in ['before','after','around']:
    v=c.open(new['window_ref'],direction);assert v['text']==text[v['offset']:v['end_char']]
  cache[pair]=dict(baseline=old,candidate=new,repair=repair,source_sha256=hashlib.sha256(text.encode()).hexdigest(),lost_left=text[old['offset']:new['offset']],added_right=text[old['end_char']:new['end_char']])
 data=cache[pair]
 def hit(v):
  return None if t['reference_span'] is None else v['offset']<=t['reference_span'][0] and v['end_char']>=t['reference_span'][1]
 rows.append(dict(**t,**data,baseline_hit=hit(data['baseline']),candidate_hit=hit(data['candidate'])))
 if i%100==0:print('PROGRESS',i,len(items),flush=True)
summary={}
for group in ['local20','replay610']:
 rr=[r for r in rows if r['group']==group];unique={(r['docid'],r['query']):r for r in rr}
 summary[group]=dict(occurrences=len(rr),unique_query_doc=len(unique),changed_occurrences=sum(r['baseline']['window_ref']!=r['candidate']['window_ref'] for r in rr),changed_unique=sum(r['baseline']['window_ref']!=r['candidate']['window_ref'] for r in unique.values()),blocked_unique=sum(bool(r['repair'] and r['repair']['status']!='repaired') for r in unique.values()),baseline_hits=sum(r['baseline_hit'] is True for r in rr),candidate_hits=sum(r['candidate_hit'] is True for r in rr),baseline_tokens=sum(r['baseline']['text_tokens']+r['baseline']['title_tokens'] for r in rr),candidate_tokens=sum(r['candidate']['text_tokens']+r['candidate']['title_tokens'] for r in rr))
for name,obj in [('observations.json',rows),('summary.json',summary)]: (out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2))
hashes={}
for rel in ['experiments/structural_boundary/candidate.py','experiments/structural_boundary/offline.py','experiments/structural_boundary/PLAN.md','llm_chat/raw_windows.py','llm_chat/window_locator.py','llm_chat/window_units.py']:
 dest=out/'source'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,dest);hashes[rel]=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
(out/'manifest.json').write_text(json.dumps(dict(scope='Offline same-query same-doc table entrance repair, no API/gold input to locator',source_sha256=hashes),indent=2))
print(json.dumps(summary,indent=2));print('FINISHED',out)
