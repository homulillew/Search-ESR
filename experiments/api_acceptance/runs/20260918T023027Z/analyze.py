import json,sys,re,sqlite3
from pathlib import Path
p=Path(sys.argv[1]);db=sqlite3.connect('file:/data/WSH/Search-ESR/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
rows=[]
for d in sorted(p.glob('local_*')):
 if not (d/'summary.json').exists():continue
 events=[json.loads(l) for l in (d/'events.jsonl').read_text().splitlines()];seen={};opens=[];errors=[];badraw=[];calls=[];forced=False
 for e in events:
  if e['kind']=='api_request' and e['request'].get('tool_choice')=='none':forced=True
  if e['kind']=='tool_start':
   calls.append(e)
   if e['name']=='open' and e['arguments'].get('window_ref') not in seen:errors.append('unseen_open_ref')
  if e['kind']=='tool_error':errors.append(e['error_type'])
  if e['kind']!='tool_result':continue
  vs=e['result'] if isinstance(e['result'],list) else [e['result']]
  for v in vs:
   if 'error' in v:errors.append(v['error']);continue
   if 'text' not in v:continue
   raw=db.execute('select text from documents where docid=?',(v['docid'],)).fetchone()[0]
   if raw[v['offset']:v['end_char']]!=v['text']:badraw.append(v['window_ref'])
   if e['name']=='open':
    intervals=sorted((z['offset'],z['end_char']) for z in seen.values() if z['docid']==v['docid'])
    a,z=v['offset'],v['end_char'];covered=0;cursor=a
    for x,y in intervals:
     x=max(x,a,cursor);y=min(y,z)
     if y>x:covered+=y-x;cursor=y
    opens.append(dict(ref=v['window_ref'],status=v['status'],new_chars=z-a-covered,direction=calls[-1]['arguments'].get('direction')))
   seen[v['window_ref']]=v
 answer=(d/'answer.md').read_text() if (d/'answer.md').exists() else ''
 refs=set(re.findall(r'w_[0-9a-f]{24}',answer));unknown=sorted(refs-set(seen))
 row=json.loads((d/'summary.json').read_text());row.update(session=d.name,tool_errors=errors,raw_mismatches=badraw,unknown_answer_refs=unknown,answer_refs=len(refs),observed_docs=sorted({v['docid'] for v in seen.values()}),opens=opens,forced_final=forced,answer=answer)
 rows.append(row)
(p/'audit.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
for r in rows:print(r['session'],r['status'],r['tool_calls'],'errors',r['tool_errors'],'refs',r['answer_refs'],'unknown',r['unknown_answer_refs'],'open',r['opens'],'\n',r['answer'],'\n')
