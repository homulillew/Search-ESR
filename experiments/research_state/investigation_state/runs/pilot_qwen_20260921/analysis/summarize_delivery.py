"""Summarize actual delivery and provider usage without scoring model semantics."""
import sys,pathlib,json,datetime,collections
ROOT=pathlib.Path(__file__).resolve().parents[6];sys.path.insert(0,str(ROOT))
from experiments.research_state.investigation_state.report import audit
r=pathlib.Path(__file__).resolve().parents[1];summary,rows=audit(r)
out=[]
for row in rows:
    resp=row['response'];choices=resp.get('choices',[]) if resp else []
    usage=(resp.get('usage') or {}) if resp else {}
    out.append({k:row[k] for k in ['sample_id','case_id','view','repeat','status','semantic_eligible','elapsed_seconds','unknown_usage_calls','errors']}|{
      'response_received':resp is not None,'classification':{k:v for k,v in (row['classification'] or {}).items() if k!='tool_calls'},
      'choices':[{'finish_reason':c.get('finish_reason'),'content_chars':len(c.get('message',{}).get('content') or ''),
        'reasoning_chars':len(c.get('message',{}).get('reasoning_content') or ''),
        'proposed_calls':len(c.get('message',{}).get('tool_calls') or [])} for c in choices],
      'usage':usage if resp else None})
events=[]
for f in (r/'branches').glob('*/events.jsonl'):
    for line in f.read_text().splitlines():events.append(json.loads(line)['time'])
data={'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'first_event':min(events),'last_event':max(events),
      'event_span_seconds':(datetime.datetime.fromisoformat(max(events))-datetime.datetime.fromisoformat(min(events))).total_seconds(),
      'scope':'No raw reasoning is substituted for delivered content. Missing usage stays unknown.','branches':out}
(r/'delivery_diagnostics.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(data,ensure_ascii=False,indent=2))
