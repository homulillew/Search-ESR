"""Mechanical audit only. Semantic judgments are recorded separately."""
import json,re,sqlite3,sys
from pathlib import Path
p=Path(sys.argv[1]);root=Path(__file__).resolve().parents[2]
tasks={t['id']:t for t in json.loads((p/'tasks.offline.json').read_text())}
db=sqlite3.connect(f'file:{root}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
rows=[];initials={};requests={}
for d in sorted(p.iterdir()):
 if not (d/'summary.json').exists():continue
 r=json.loads((d/'summary.json').read_text());t=tasks[r['task']];events=[json.loads(l) for l in (d/'events.jsonl').read_text().splitlines()]
 seen={};errors=[];opens=[];marker=False;source_hit=False;first=None;badraw=[]
 for e in events:
  if e['kind']=='api_request' and r['task'] not in requests:requests[r['task']]=e['request']
  if e['kind']=='tool_start':
   if first is None:first=e['name']
   if e['name']=='open' and e['arguments']['window_ref'] not in seen:errors.append('unseen_open_ref')
  if e['kind']=='tool_error':errors.append(e['error_type'])
  if e['kind'] not in ['seeded_observation','tool_result']:continue
  views=e['result'] if isinstance(e['result'],list) else [e['result']]
  for v in views:
   if 'error' in v:errors.append(v['error']);continue
   if 'text' not in v:continue
   raw=db.execute('select text from documents where docid=?',(v['docid'],)).fetchone()[0]
   if raw[v['offset']:v['end_char']]!=v['text']:badraw.append(v['window_ref'])
   if e['kind']=='seeded_observation':
    if (ik:=r['task']+'__'+r['arm']) in initials:assert initials[ik]==v
    initials[ik]=v
   if e.get('name')=='open':
    spans=sorted((x['offset'],x['end_char']) for x in seen.values() if x['docid']==v['docid']);cursor=v['offset'];covered=0
    for a,z in spans:
     a=max(a,cursor,v['offset']);z=min(z,v['end_char'])
     if z>a:covered+=z-a;cursor=z
    opens.append(dict(ref=v['window_ref'],status=v['status'],new_chars=len(v['text'])-covered))
   seen[v['window_ref']]=v
   if t['needle']:
    target={'role_gardener':'Policeman 1','role_estate':'Oscar Kamau Kingara','birth':'25 May 1978','riise':"Riise's free kick was blocked",'poker':'Anh Le'}[t['id']]
    marker=marker or target.casefold() in v['text'].casefold()
    a,z=t['reference_span'];source_hit=source_hit or (v['docid']==t['docid'] and v['offset']<=a and v['end_char']>=z)
 answer=(d/'answer.md').read_text() if (d/'answer.md').exists() else ''
 refs=set(re.findall(r'w_[0-9a-f]{24}',answer))
 r.update(session=d.name,first_action=first or 'answer',reference_span_visible=source_hit if t['needle'] else None,answer_marker_observed=marker if t['needle'] else None,tool_errors=errors,raw_mismatches=badraw,answer_refs=len(refs),unknown_answer_refs=sorted(refs-seen.keys()),opens=opens,answer=answer)
 # Verify first requests within each arm/task preserve the same seeded observation.
 first_request=next(e['request'] for e in events if e['kind']=='api_request')
 normalized=json.loads(json.dumps(first_request));normalized['messages'][0]['content']='SYSTEM';normalized['tools']='TOOLS'
 if (key:=t['id']+'__'+r['arm']+'__normalized') in requests:assert requests[key]==normalized
 else:requests[key]=normalized
 rows.append(r)
summary={}
for arm in sorted({r['arm'] for r in rows}):
 rr=[r for r in rows if r['arm']==arm];groups={}
 for group in sorted({r['group'] for r in rr}):
  gg=[r for r in rr if r['group']==group];groups[group]=dict(n=len(gg),search=sum(r['tool_calls'].get('search',0) for r in gg),open=sum(r['tool_calls'].get('open',0) for r in gg),first_actions={a:sum(r['first_action']==a for r in gg) for a in ['answer','search','open']},answer_marker_observed=sum(r['answer_marker_observed'] is True for r in gg),reference_span_visible=sum(r['reference_span_visible'] is True for r in gg))
 summary[arm]=dict(n=len(rr),groups=groups,tool_errors=sum(len(r['tool_errors']) for r in rr),raw_mismatches=sum(len(r['raw_mismatches']) for r in rr),invalid_answer_refs=sum(len(r['unknown_answer_refs']) for r in rr),sessions_with_window_citation=sum(r['answer_refs']>0 for r in rr),forced_final=sum(r['forced_final'] for r in rr),api_tokens=sum(r['usage']['total_tokens'] for r in rr))
(p/'audit.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));(p/'metrics.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print(json.dumps(summary,ensure_ascii=False,indent=2))
