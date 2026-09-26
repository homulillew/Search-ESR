import sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from transport import P,rd,save,head,now,Transport,check_freeze
stage=sys.argv[1] if len(sys.argv)>1 else 'development';D=P/'need'/stage
check_freeze(D/'FREEZE.json');jobs=rd(D/'JOBS.json');plan=rd(D/'PLAN.json');save(D/'STARTED.json',{'head':head(),'started_utc':now()});start=time.monotonic();tr=Transport()
preids=plan['preflight'];pre=tr.batch(D/'calls',[j for j in jobs if j['id'] in preids]);ok=all(r['final_valid_JSON'] and r.get('token_accounting',{}).get('reasoning') is not None for r in pre)
save(D/'PREFLIGHT.json',{'ok':ok,'results':pre,'max_tokens_omitted':all('max_tokens' not in j['request'] for j in jobs),'reused_in_formal_batch':True})
if not ok:tr.close();raise SystemExit('preflight failed; formal batch blocked')
out=pre+tr.batch(D/'calls',[j for j in jobs if j['id'] not in preids]);tr.close();save(D/'RESULTS.json',out);save(D/'COMPLETED.json',{'calls':tr.count,'peak_concurrency':tr.peak,'elapsed_seconds':time.monotonic()-start,'completed_utc':now()})
