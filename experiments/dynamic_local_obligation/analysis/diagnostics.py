"""Post-review descriptive breakdown; cannot replace frozen engineering gate."""
from collections import Counter
import math
from experiments.dynamic_local_obligation.common import *
from experiments.dynamic_local_obligation.run import OUT,load_rows
from experiments.dynamic_local_obligation.score import strict,fraction

def main():
 rows=load_rows();key=read(OUT/'review/KEY.json');labels={key[l['review_id']]:l for l in read(OUT/'review/REVIEW.json')};cases=bank();gold={g['case_id']:g for g in read(P/'e0_reference/GOLD_GAPS.json')};d={}
 for arm in ('O0','O1'):
  rr=[r for r in rows if r['arm']==arm]
  groups={status:[r for r in rr if gold[r['case_id']]['reference_status']==status] for status in ('unsupported','partial','satisfied')}
  groups.update({'empty_C':[r for r in rr if not cases[r['case_id']]['claims']], 'nonempty_C':[r for r in rr if cases[r['case_id']]['claims']],
    'null_H':[r for r in rr if cases[r['case_id']]['belief']['hypothesis'] is None],'nonempty_H':[r for r in rr if cases[r['case_id']]['belief']['hypothesis'] is not None]})
  d[arm]={'strict_by_historical_stratum':{k:fraction(sum(strict(r,labels[r['id']]) for r in subset),len(subset)) for k,subset in groups.items()},
   'strict_by_replicate':{str(rep):fraction(sum(strict(r,labels[r['id']]) for r in rr if r['replicate']==rep),27) for rep in (1,2)},
   'strict_by_question':{qid:fraction(sum(strict(r,labels[r['id']]) for r in rr if r['qid']==qid),sum(r['qid']==qid for r in rr)) for qid in sorted({r['qid'] for r in rr})},
   'G23_argument_corruption':fraction(sum('wrong_relation_arguments' in labels[r['id']]['errors'] for r in rr if r['case_id']=='G23'),sum(r['case_id']=='G23' for r in rr)),
   'G23_question_cluster_corruption':fraction(sum('wrong_relation_arguments' in labels[r['id']]['errors'] for r in rr if r['qid']=='1259'),sum(r['qid']=='1259' for r in rr)),
   'invalid':[{'id':r['id'],'review_id':labels[r['id']]['review_id'],'case_id':r['case_id'],'state_id':r['state_id'],'obligation':(r.get('output') or {}).get('obligation'),
      'failed_dimensions':[k for k,v in labels[r['id']]['dimensions'].items() if not v],'errors':labels[r['id']]['errors'],'reason':labels[r['id']]['reason']} for r in rr if not strict(r,labels[r['id']])]}
 elapsed=sorted(r.get('elapsed_seconds',0) for r in rows if r['attempted']);tokens=sorted(r['usage']['completion_tokens'] for r in rows if isinstance(r.get('usage'),dict) and isinstance(r['usage'].get('completion_tokens'),int))
 quant=lambda vals,p:vals[min(len(vals)-1,math.ceil(len(vals)*p)-1)] if vals else None
 d['execution']={'planned':len(rows),'sent':sum(r['attempted'] for r in rows),'returned':sum('http_status' in r for r in rows),
  'latency_seconds':{'median':quant(elapsed,.5),'p95':quant(elapsed,.95),'max':max(elapsed) if elapsed else None},
  'completion_tokens':{'median':quant(tokens,.5),'p95':quant(tokens,.95),'max':max(tokens) if tokens else None},
  'usage_unknown':sum(not r.get('accounting',{}).get('complete',False) for r in rows), 'failures':dict(Counter(r.get('failure') for r in rows if r.get('failure')))}
 d['caveat']='Post hoc descriptive strata only. Historical Gold status is not the status of the newly selected active O.27 snapshots/10 question clusters are exposed and dependent.'
 write(P/'analysis/DIAGNOSTICS.json',d)
 print(json.dumps({a:{k:v for k,v in d[a].items() if k!='invalid'} for a in ('O0','O1')},indent=2));print(json.dumps(d['execution'],indent=2))
if __name__=='__main__':main()
