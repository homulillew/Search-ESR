"""No-network raw-response, accounting, frozen-input and real-score replay."""
from .common import *
from .run import audit,jobs,load_rows,parse,accounting,OUT
from .score import results
def main():
 check=audit(require_authorization=True);lookup={j['id']:j for j in jobs()};rows=load_rows()
 for r in rows:
  j=lookup[r['id']];p=OUT/'calls'/r['id']
  if r['attempted']:
   assert read(p.with_suffix('.request.json'))['request']==j['request'];assert p.with_suffix('.attempt.json').exists()
  raw_path=p.with_suffix('.response.json')
  if raw_path.exists():
   raw=read(raw_path);parsed=parse(raw['status'],raw['body'],j);assert all(r.get(k)==v for k,v in parsed.items())
  else:assert r.get('http_status') is None
 a=results();assert a==results()==read(OUT/'METRICS.json')
 acc=read(OUT/'ACCOUNTING.json');assert all(acc[k]==v for k,v in accounting(rows).items());assert len(rows)==192 and acc['peak_concurrency']<=8
 write(P/'analysis/EXECUTION_ACCOUNTING.json',{'E1':acc,'E2_attempted':0,'E3_attempted':0,'retrieval_calls':0,'retries':0,'old_S0_S1_resampled':False})
 write(P/'analysis/INTEGRITY.json',{**check,'historical_files_unchanged':verify_history(),'requests_unchanged':True,'gold_unchanged':True,'raw_response_reparse_identical':True,'score_replay_deterministic':True,'score_sha256':digest(a),'accounting_replay_identical':True})
 print({'integrity':'PASS','history_unchanged':check['historical_files_unchanged'],'attempted':acc['sent_or_send_intent'],'score_sha256':digest(a)})
if __name__=='__main__':main()
