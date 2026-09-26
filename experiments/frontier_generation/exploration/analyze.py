import sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
sys.path.insert(0,str(TOP/'analysis'))
from summarize import metrics
b=TOP/'exploration';ann=rd(b/'semantic_review.json');key=rd(b/'private_review_key.json');assert set(ann)==set(key)
rows=rd(b/'frontier_outputs.json');byid={key[k]:v for k,v in ann.items()}
for r in rows:r.update(byid[r['id']]);r['critical']=any(r[k] for k in ['premature_stop','drift','unsupported_premise'])
summary={'arms':{a:metrics([r for r in rows if r['arm']==a]) for a in ['A0','A1']}}
v=summary['arms'];summary['positive_descriptive_signal']=v['A1']['over_broad']['n']<v['A0']['over_broad']['n'] and v['A1']['valid']['n']>=v['A0']['valid']['n'] and v['A1']['critical']['n']<=v['A0']['critical']['n']
summary['paired']={c:{r['arm']:{k:r[k] for k in ['valid','over_broad','critical','unsupported_premise','premature_stop','output','reason']} for r in rows if r['case_id']==c} for c in sorted({r['case_id'] for r in rows})}
summary['total_usage']=metrics(rows);summary['primary_gate_unchanged']=True
wr(b/'reviewed_outputs.json',rows);wr(b/'summary.json',summary)
print(json.dumps({'arms':{a:{k:v[a][k] for k in ['valid','over_broad','critical','premature_stop','provider_or_contract_failure','cache_hit_rate']} for a in v},'positive':summary['positive_descriptive_signal']},indent=2))
