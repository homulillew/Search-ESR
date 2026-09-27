"""Run after first-pass sealing and primary aggregation; no newAPI requests."""
from .common import *
from .run import OUT,jobs,load_rows,audit,parse
from .score import assert_review,calculate
from experiments.skeleton_state_alignment.run import accounting

def execute():
 assert_review();checked=audit();rows=load_rows();lookup={j['id']:j for j in jobs()};run=read(OUT/'RUN.json')
 for row in rows:
  if not row['attempted']:continue
  assert row['head']==run['head'];stem=OUT/'calls'/row['id'];q=read(stem.with_suffix('.request.json'))
  assert q['request']==lookup[row['id']]['request'] and q['request_sha256']==row['request_sha256']
  if row.get('http_status') is not None:
   raw=read(stem.with_suffix('.response.json'));parsed=parse(raw['status'],raw['body'],lookup[row['id']])
   for k,v in parsed.items():assert row[k]==v,(row['id'],k)
 metrics=read(OUT/'METRICS.json');assert metrics==calculate()
 account=read(OUT/'ACCOUNTING.json')
 for k,v in accounting(rows).items():assert account[k]==v,k
 assert len(list((OUT/'calls').glob('*.attempt.json')))==account['sent_or_send_intent']
 write(P/'analysis/E1_EXECUTED_FILES.json',{rel(p):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts})
 write(P/'analysis/E1_INTEGRITY.json',{'status':'PASS',**checked,'raw_replay_attempts':sum(r['attempted'] for r in rows),
  'metrics_exact_replay':True,'accounting_exact_replay':True,'review_sealed':True,'max_retries':0})
 print('E1 raw/modeloutput/score/usage/history replay PASS')
if __name__=='__main__':execute()
