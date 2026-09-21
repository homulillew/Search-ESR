"""Aggregate provider-reported usage without inventing missing cost. No API calls."""
from pathlib import Path
import json,datetime
r=Path(__file__).resolve().parents[1];p=r.parent/'pilot_qwen_20260921'
a=json.loads((p/'summary.json').read_text());b=json.loads((r/'summary.json').read_text())
d={'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pilot':a,'formal':b,'combined':{'planned':a['scheduled_branches']+b['scheduled_branches'],'requests':a['logical_requests_attempted']+b['logical_requests_attempted'],'responses':a['responses_received']+b['responses_received'],'unknown_usage_calls':a['unknown_usage_calls']+b['unknown_usage_calls'],'reported_token_lower_bounds':{k:a['reported_token_lower_bounds'][k]+b['reported_token_lower_bounds'][k] for k in a['reported_token_lower_bounds']},'monetary_cost':None,'monetary_cost_reason':'No verified billing record or applicable price; missing usage is not zero. Reasoning is a component of completion tokens, not added again.'}}
(r/'combined_costs.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps(d['combined'],ensure_ascii=False,indent=2))
