"""Adaptive E0 ladder. Frozen old prompts and inputs; only completion key changes."""
import sys,copy,statistics,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from transport import P,ROOT,C,rd,save,sha,dg,head,now,check_freeze,Transport
BASE=P/'e0'
def request(c,budget):
 r=copy.deepcopy(c['request'])
 if budget is None:r.pop('max_tokens',None)
 else:r['max_tokens']=budget
 assert {k:v for k,v in r.items() if k!='max_tokens'}=={k:v for k,v in c['request'].items() if k!='max_tokens'}
 return r
def pct(xs,p):
 if not xs:return None
 a=sorted(xs);pos=(len(a)-1)*p;lo=int(pos);hi=min(lo+1,len(a)-1);return a[lo]+(a[hi]-a[lo])*(pos-lo)
def metrics(rows,budget):
 n=len(rows);u=[r['token_accounting'] for r in rows if r.get('token_accounting')];out=[x['output'] for x in u];reason=[x['reasoning'] for x in u if x['reasoning'] is not None]
 return {'n':n,'final_valid_JSON':sum(r['final_valid_JSON'] for r in rows),'FinalJSONCompletionRate':sum(r['final_valid_JSON'] for r in rows)/n,'final_output_exists':sum(r['final_output_exists'] for r in rows),'schema_valid':sum(r['schema_valid'] for r in rows),'length':sum(r['finish_reason']=='length' for r in rows),'LengthFailureRate':sum(r['finish_reason']=='length' for r in rows)/n,'completion_tokens':{'p50':pct(out,.5),'p90':pct(out,.9),'max':max(out) if out else None},'reasoning_tokens':{'p50':pct(reason,.5),'p90':pct(reason,.9),'max':max(reason) if reason else None},'final_tokens':sum(x['final'] for x in u if x['final'] is not None),'Reasoning_Output_ratio':sum(reason)/sum(out) if out else None,'near_explicit_cap_count':sum(v>.9*budget for v in out) if budget else None,'budget':budget,'headroom_unknown_for_default':budget is None}
def adequate(m):return m['n']==12 and m['final_valid_JSON']>=11 and m['length']<=1 and (m['budget'] is None or m['near_explicit_cap_count']<3)
def freeze():
 cases=rd(BASE/'CASES.json');sel=rd(BASE/'SELECTION.json');plan={}
 for name,b in [('E8192',8192),('E16384',16384),('E32768',32768),('EDEFAULT',None)]:plan[name]=[{'id':r['calibration_id'],'request':request(r,b)} for r in cases]
 save(BASE/'PLAN.json',plan)
 paths=[P/'transport.py',P/'CONFIG.json',P/'PROTOCOL.md',BASE/'run.py',BASE/'prepare.py',BASE/'PLAN.json',BASE/'CASES.json',BASE/'SELECTION.json',BASE/'HISTORICAL_BUDGET_PROOF.json']
 save(BASE/'FREEZE.json',{'head':head(),'utc':now(),'files':{str(p.relative_to(ROOT)):sha(p) for p in paths},'semantics_unchanged':True,'max_retries':0,'planned_cases':12,'preflight':sel['default_preflight'],'adaptive_rule':'3 DEFAULT preflight before formal calibration; if any failure, stop formal batches. Otherwise 8192→16384→32768 until >=11/12 JSON, <=1 length and <3 near-cap. Mandatory default initially three fixed cases; expand default to12 without resampling preflight cases to qualify historical-equivalent primary. Any default long-reasoning failure retained.'})
def run():
 check_freeze(BASE/'FREEZE.json');save(BASE/'STARTED.json',{'head':head(),'utc':now()});plan=rd(BASE/'PLAN.json');sel=rd(BASE/'SELECTION.json');t=Transport();summary={}
 try:
  pre=[j for j in plan['EDEFAULT'] if j['id'] in sel['default_preflight']];rows=t.batch(BASE/'EDEFAULT/calls',pre);save(BASE/'EDEFAULT/PREFLIGHT_OUTPUTS.json',rows)
  okay=all(r['final_valid_JSON'] and r['finish_reason']=='stop' and r.get('token_accounting',{}).get('reasoning') is not None for r in rows)
  save(BASE/'PREFLIGHT_VERDICT.json',{'passed':okay,'case_ids':sel['default_preflight'],'checks':['system JSON literal','finish_reason stop','parse/schema','reasoning usage present','max_tokens absent in exact request','no silent truncation'],'results':rows})
  if not okay:
   save(BASE/'STOP.json',{'reason':'preflight failed; no formal calibration batch submitted','utc':now(),'followup':'Inspect transport versus provider-default reasoning exhaustion before any semantic batch.'});return
  lowest=None
  for arm,budget in [('E8192',8192),('E16384',16384),('E32768',32768)]:
   result=t.batch(BASE/arm/'calls',plan[arm]);save(BASE/arm/'OUTPUTS.json',result);m=metrics(result,budget);summary[arm]=m;save(BASE/arm/'METRICS.json',m)
   if adequate(m):lowest=arm;break
  remaining=[j for j in plan['EDEFAULT'] if j['id'] not in sel['default_preflight']];rest=t.batch(BASE/'EDEFAULT/calls',remaining);allrows=sorted(rows+rest,key=lambda x:x['id']);save(BASE/'EDEFAULT/OUTPUTS.json',allrows);m=metrics(allrows,None);summary['EDEFAULT']=m;save(BASE/'EDEFAULT/METRICS.json',m)
  selected='EDEFAULT' if adequate(m) else lowest
  save(BASE/'EXECUTION_SELECTION.json',{'lowest_adequate_explicit':lowest,'primary_configuration':selected,'max_tokens':None if selected=='EDEFAULT' else int(selected[1:]) if selected else None,'omit_max_tokens':selected=='EDEFAULT','all_metrics':summary,'default_65535_is_observation_not_config_claim':True,'status':'qualified_calibration' if selected else 'no_adequate_configuration; inspect E-BUDGET-SPIRAL'})
 finally:t.close();save(BASE/'COMPLETED.json',{'utc':now(),'calls':t.count,'http_peak':t.peak,'max_retries':0})
if __name__=='__main__':globals()[sys.argv[1]]()
