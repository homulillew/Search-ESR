"""Descriptive paired sensitivity for differential contract attrition."""
from progress import *

def paired():
 b=TOP/'three_round_loop_v2';rows=read(b/'loop_reviews.json');by={(r['qid'],r['arm']):r for r in rows};out={}
 for a,z in [('L0','L1'),('L1','L2'),('L0','L2')]:
  qids=sorted({r['qid'] for r in rows});kept=[q for q in qids if all('failure' not in by[q,k]['status'] for k in [a,z])]
  out[a+'_vs_'+z]={'all_planned_qids':len(qids),'both_nonfailed_qids':kept,'excluded_qids':[q for q in qids if q not in kept],
   'all_planned':{k:{m:sum(by[q,k][m] for q in qids) for m in ['resolved','correct_stop','premature_stop','tool_calls','acting_decisions','progress_decisions']} for k in [a,z]},
   'both_nonfailed':{k:{m:sum(by[q,k][m] for q in kept) for m in ['resolved','correct_stop','premature_stop','tool_calls','acting_decisions','progress_decisions']} for k in [a,z]},
   'paired_resolution':{d:sum((bool(by[q,z]['resolved'])-bool(by[q,a]['resolved']))==v for q in kept) for d,v in [('second_better',1),('equal',0),('first_better',-1)]},
   'interpretation':'Descriptive small-cohort sensitivity. Removing failed cells is selection, not a repaired intention-to-treat estimate; premature stops lower costs without being efficient successes.'}
 write(b/'paired_metrics.json',out);print(json.dumps(out,indent=2));return out
if __name__=='__main__':paired()
