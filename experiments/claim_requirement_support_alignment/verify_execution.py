"""Post-review deterministic replay and immutable-artifact audit. No network."""
from .common import *
from .run import audit,jobs,load_rows,parse,accounting,OUT
from .score import results

def main():
 checks=audit(require_authorization=True);schedule=jobs();rows=load_rows();lookup={j['id']:j for j in schedule}
 for r in rows:
  j=lookup[r['id']];p=OUT/'calls'/r['id']
  if r['attempted']:
   assert read(p.with_suffix('.request.json'))['request']==j['request']
   assert p.with_suffix('.attempt.json').exists()
  raw_path=p.with_suffix('.response.json')
  if raw_path.exists():
   raw=read(raw_path);reparsed=parse(raw['status'],raw['body'],j)
   assert all(r.get(k)==v for k,v in reparsed.items()),r['id']
  elif r.get('http_status') is not None:raise AssertionError('HTTP result missing raw response')
 a=results();b=results();assert a==b==read(OUT/'METRICS.json')
 acc=read(OUT/'ACCOUNTING.json');recomputed=accounting(rows);assert all(acc[k]==v for k,v in recomputed.items())
 assert len(rows)==96 and len(list((OUT/'calls').glob('*.attempt.json')))<=96 and acc['peak_concurrency']<=8
 write(P/'analysis/EXECUTION_ACCOUNTING.json',{'stage':'E1','authorized_maximum':96,'E1':acc,'E2_attempted':0,'retrieval_tool_calls':0,'retry_attempts':0,'completion':'all planned slots retained','usage_note':'Reported usage only; missing counters or responses must not be interpreted as zero cost.'})
 write(P/'analysis/E1_INTEGRITY.json',{**checks,'previous_experiments_unchanged':True,'frozen_requests_unchanged':True,'gold_reference_unchanged':True,'raw_response_reparse_identical':True,'score_replay_deterministic':True,'score_replay_sha256':digest(a),'accounting_replay_identical':True,'authorization_scope':'E1 only','planned_slots':len(rows),'protected_historical_files':verify_history(),'preparation_integrity_remains_frozen':True})
 print(json.dumps({'integrity':'PASS','historical_files_unchanged':checks['historical_files_unchanged'],'planned':96,'attempted':acc['sent_or_send_intent'],'score_sha256':digest(a)},indent=2))
if __name__=='__main__':main()
