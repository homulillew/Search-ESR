import sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from transport import P,rd,save,head,now,Transport,check_freeze
D=P/'need/b3_issue';check_freeze(D/'FREEZE.json');jobs=rd(D/'JOBS.json');plan=rd(D/'PLAN.json');save(D/'STARTED.json',{'head':head(),'started_utc':now()});start=time.monotonic();tr=Transport()
schema={'type':'object','properties':{'issue':{'type':'string','minLength':1}},'required':['issue'],'additionalProperties':False}
preids=plan['preflight'];pre=tr.batch(D/'calls',[j for j in jobs if j['id'] in preids],schema);ok=all(r['final_valid_JSON'] and r.get('token_accounting',{}).get('reasoning') is not None for r in pre);save(D/'PREFLIGHT.json',{'ok':ok,'results':pre})
if not ok:tr.close();raise SystemExit('issue preflight failed; no main batch')
out=pre+tr.batch(D/'calls',[j for j in jobs if j['id'] not in preids],schema);tr.close();save(D/'RESULTS.json',out);save(D/'COMPLETED.json',{'calls':tr.count,'peak_concurrency':tr.peak,'elapsed_seconds':time.monotonic()-start,'completed_utc':now()})
