"""Describe provider-reported output budgets; no API calls or semantic judgments."""
import pathlib,json,collections,datetime
r=pathlib.Path(__file__).resolve().parents[1]
rows=[]
for f in sorted((r/'branches').glob('*/result.json')):
    d=json.loads(f.read_text())
    for stage in ['review','actor']:
        s=d[stage];resp=s.get('response');u=s.get('usage') or {}
        ch=(resp.get('choices') or [{}])[0] if resp else {}
        msg=ch.get('message') or {}
        rows.append(dict(sample_id=d['sample_id'],contract=d['review_contract'],stage=stage,
            status=s['status'],finish_reason=ch.get('finish_reason'),response_received=resp is not None,
            content_chars=len(msg.get('content') or '') if resp else None,reasoning_chars=len(msg.get('reasoning_content') or '') if resp else None,
            tool_calls=len(msg.get('tool_calls') or []) if resp else None,prompt_tokens=u.get('prompt_tokens'),
            completion_tokens=u.get('completion_tokens'),total_tokens=u.get('total_tokens'),
            reasoning_tokens=(u.get('completion_tokens_details') or {}).get('reasoning_tokens'),
            elapsed_seconds=s['elapsed_seconds'],errors=s.get('errors',[]),
            completion_cap=s['request'].get('max_tokens',s['request'].get('max_completion_tokens'))))
out={'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'scope':'Provider-reported usage; missing values stay null; known sums are lower bounds, not monetary costs.',
     'by_stage':{},'by_contract':{},'requests':rows}
for field,target in [('stage','by_stage'),('contract','by_contract')]:
    for key in sorted(set(x[field] for x in rows)):
        xs=[x for x in rows if x[field]==key]
        out[target][key]={'attempts':len(xs),'responses':sum(x['response_received'] for x in xs),
          'statuses':dict(collections.Counter(x['status'] for x in xs)),
          'reported_token_lower_bounds':{k:sum(x[k] for x in xs if x[k] is not None)
            for k in ['prompt_tokens','completion_tokens','total_tokens','reasoning_tokens']},
          'unknown_usage_requests':sum(x['total_tokens'] is None for x in xs),
          'elapsed_seconds':sum(x['elapsed_seconds'] for x in xs)}
(r/'reasoning_diagnostics.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='requests'},ensure_ascii=False,indent=2))
