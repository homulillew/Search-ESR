"""Independent source-boundary and observation accounting checks on new docs."""
import json,sys,sqlite3,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from transformers import AutoTokenizer
from llm_chat.raw_windows import RawWindowBuilder
from llm_chat.structural_windows import TableEntryWindowBuilder
from llm_chat.observations import ObservationStore
p=Path(sys.argv[1]).resolve();out=p/'boundary_audit';out.mkdir(exist_ok=False)
tok=AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B',local_files_only=True);b=RawWindowBuilder(tok);c=TableEntryWindowBuilder(tok)
db=sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
rows=json.loads((p/'observations.json').read_text());probes=[];stress=[];known=set()
for qid in dict.fromkeys(r['qid'] for r in rows):
 store=ObservationStore(out/f'qid_{qid}.sqlite')
 for r in [x for x in rows if x['qid']==qid]:
  text,url=db.execute('select text,url from documents where docid=?',(r['docid'],)).fetchone();v=b.search(r['docid'],text,url,r['query']);key=c.register(r['docid'],text,url);doc=c.documents[key]
  assert v==r['baseline']
  store.record('search',{'query':r['query']},[v],b)
  repeated=store.record('search',{'query':r['query']},[v],b)
  assert repeated['observations'][0]['new_chars']==0
  assert repeated['observations'][0]['repeated_window']
  info=dict(qid=qid,docid=r['docid'],initial_span=[v['offset'],v['end_char']],starts_on_unit=v['offset'] in doc['unit_starts'] or v['offset']==0,ends_on_unit=v['end_char'] in doc['unit_ends'] or v['end_char']==len(text),probes=[])
  for direction in ['before','after','around']:
   w=b.open(v['window_ref'],direction);assert w['text']==text[w['offset']:w['end_char']]
   if direction=='after' and w['status']=='ok':assert w['offset']==v['end_char']
   if direction=='before' and w['status']=='ok':assert w['end_char']==v['offset']
   if direction=='around':assert w['offset']<=v['offset']<=v['end_char']<=w['end_char']
   m=store.record('open',{'window_ref':v['window_ref'],'direction':direction},w,b)
   info['probes'].append(dict(direction=direction,span=[w['offset'],w['end_char']],status=w['status'],metrics=m['observations'][0]))
  probes.append(info)
  if r['docid'] not in known:
   known.add(r['docid'])
   for header,body,table_end in doc['tables'][:2]:
    if body>=table_end:continue
    cap=400-c.count(doc['title']);starts=sorted({0,*[s for s in doc['unit_starts'] if s<header]})
    valid=[]
    for s in reversed(starts):
     if c.count(text[s:body])>cap:break
     valid.append(s)
    if not valid:continue
    start=min(valid);anchor_start=max(s for s in starts if start<=s<header)
    a,z=c._repair_table_entry(key,start,body,(anchor_start,header),cap)
    assert c.count(text[a:z])<=cap
    assert a<=anchor_start and z>=header
    stress.append(dict(docid=r['docid'],title=doc['title'],old_span=[start,body],new_span=[a,z],repair=c.last_repair,baseline_text=text[start:body],candidate_text=text[a:z],changed=(a,z)!=(start,body)))
 summary=store.summary();assert summary['new_source_chars']==summary['covered_source_chars']
 (out/f'qid_{qid}_summary.json').write_text(json.dumps(summary,indent=2));store.close()
result=dict(new_questions=len(set(r['qid'] for r in rows)),windows=len(rows),distinct_docs=len(known),natural_window_changes=sum(r['baseline']['window_ref']!=r['candidate']['window_ref'] for r in rows),open_probes=sum(len(r['probes']) for r in probes),raw_checks_passed=True,repeated_search_checks=len(rows),interval_accounting_passed=True,starts_on_unit=sum(r['starts_on_unit'] for r in probes),ends_on_unit=sum(r['ends_on_unit'] for r in probes),structural_stress_cases=len(stress),stress_changed=sum(r['changed'] for r in stress),stress_distinct_docs=len({r['docid'] for r in stress}),note='Stress windows deliberately terminate at real table separators; they are not naturally retrieved windows and not semantic outcome labels.')
for name,obj in [('summary.json',result),('probes.json',probes),('table_stress.json',stress)]: (out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2))
print(json.dumps(result,indent=2))
