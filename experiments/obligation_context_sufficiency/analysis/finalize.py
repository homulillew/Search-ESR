"""Final artifact integrity and credential check; no remote/model calls."""
from experiments.obligation_context_sufficiency.common import *
from experiments.obligation_context_sufficiency.prepare import credential
from experiments.obligation_context_sufficiency.run import OUT,load_rows
from experiments.minimal_need_multiquery.run import now
import math,statistics

def main():
 rows=load_rows();account=read(OUT/'ACCOUNTING.json');lat=sorted(r['elapsed_seconds'] for r in rows if r['attempted'] and 'elapsed_seconds' in r)
 outputs=sorted(r['usage']['completion_tokens'] for r in rows if isinstance(r.get('usage'),dict) and type(r['usage'].get('completion_tokens')) is int)
 report={**account,'sent':sum(r['attempted'] for r in rows),'returned':sum('http_status' in r for r in rows),
  'http_failures':sum(r.get('http_status',200)!=200 for r in rows),
  'schema_failures':sum(r.get('failure')=='schema_or_ref_error' for r in rows),
  'length_failures':sum(r.get('failure')=='length' for r in rows),'nonvalid_total':sum(not r['valid_output'] for r in rows),
  'latency_seconds':{'median':statistics.median(lat),'p95_nearest_rank':lat[math.ceil(.95*len(lat))-1],'max':max(lat)},
  'completion_tokens':{'median':statistics.median(outputs),'p95_nearest_rank':outputs[math.ceil(.95*len(outputs))-1],'max':max(outputs)},
  'usage_unknown_calls':sum(not (r.get('accounting') or {}).get('complete',False) for r in rows if r['attempted']),
  'reasoning_in_completion':True,'currency_cost':None,'retries':0,'extra_canary_calls':0,'retrieval_calls':0}
 write(P/'analysis/COST_AND_LATENCY.json',report)
 assert all(sha(ROOT/n)==h for n,h in read(P/'analysis/HISTORICAL_HASHES.json').items())
 key=credential().encode();files=[p for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
 assert all(key not in p.read_bytes() for p in files)
 write(P/'analysis/SECRET_SCAN.json',{'status':'PASS','files':len(files),'credential_literal_present':False,'credential_printed':False})
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
