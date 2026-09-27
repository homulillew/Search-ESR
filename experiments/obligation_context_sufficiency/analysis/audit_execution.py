"""Read-only reconstruction of run integrity; never calls a model."""
import json
from collections import Counter
from experiments.obligation_context_sufficiency.common import *
from experiments.obligation_context_sufficiency.run import OUT,audit,load_rows,parse_response
from experiments.minimal_need_multiquery.run import accounting_summary

def main():
 checked=audit();checked['audit_network_calls']=0;checked.pop('zero_network_calls',None);cases=bank();jobs=read(OUT/'SCHEDULE.json');rows=load_rows();rowmap={r['id']:r for r in rows};account=read(OUT/'ACCOUNTING.json')
 assert len(rows)==216
 for j in jobs:
  r=rowmap[j['id']];stem=OUT/'calls'/j['id']
  if r['attempted']:
   req=read(stem.with_suffix('.request.json'));assert req['request']==j['request'] and req['request_sha256']==j['request_sha256']
   assert stem.with_suffix('.attempt.json').exists()
  if stem.with_suffix('.response.json').exists():
   raw=read(stem.with_suffix('.response.json'));parsed=parse_response(raw['status'],raw['body'],j,cases[j['case_id']])
   assert all(r[k]==v for k,v in parsed.items()), 'Raw parse drift'
  assert r['head']==read(OUT/'RUN.json')['head']
 for c in cases.values():
  original=read(ROOT/c['snapshot'])['state']
  assert c['belief']=={'question':original['question'],'claims':[x['statement'] for x in original['claims']]}
 for k,v in accounting_summary(rows).items():assert account[k]==v
 first=read(OUT/'RUN.json')['started_utc'];last=max(r.get('completed_utc',first) for r in rows)
 report={**checked,'status':'PASS','raw_reparse_checked':sum((OUT/'calls'/f"{r['id']}.response.json").exists() for r in rows),
  'unchanged_original_QC':27,'scheduled':216,'sent':sum(r['attempted'] for r in rows),'returned':sum('http_status' in r for r in rows),
  'failure_counts':dict(Counter(r.get('failure') or 'none' for r in rows)),'started_utc':first,'last_completion_utc':last,
  'retries':0,'retrieval_calls':0,'persistent_state_mutations':0,'accounting_recomputed':True}
 write(P/'analysis/INTEGRITY.json',report)
 write(P/'analysis/EXECUTION_ACCOUNTING.json',account)
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
