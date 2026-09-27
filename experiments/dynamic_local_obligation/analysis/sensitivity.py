"""Explicit post-hoc robustness bounds; original labels/gates never changed."""
from experiments.dynamic_local_obligation.common import *
from experiments.dynamic_local_obligation.run import OUT,load_rows
from experiments.dynamic_local_obligation.score import strict,fraction,DIMENSIONS

def main():
 rows=load_rows();key=read(OUT/'review/KEY.json');labels={key[l['review_id']]:l for l in read(OUT/'review/REVIEW.json')};result={}
 for a in ('O0','O1'):
  rr=[r for r in rows if r['arm']==a];low=[r for r in rr if labels[r['id']]['ambiguity']=='low']
  without_local=lambda r:r['valid_output'] and all(labels[r['id']]['dimensions'][d] for d in DIMENSIONS if d not in ('Local','Coherent'))
  optimistic=lambda r:r['valid_output'] and (labels[r['id']]['ambiguity']!='low' or without_local(r))
  result[a]={'frozen_strict':fraction(sum(strict(r,labels[r['id']]) for r in rr),len(rr)),
   'low_ambiguity_only':fraction(sum(strict(r,labels[r['id']]) for r in low),len(low)),
   'ignore_locality_and_coherence':fraction(sum(without_local(r) for r in rr),len(rr)),
   'optimistic_ignore_locality_and_accept_all_medium':fraction(sum(optimistic(r) for r in rr),len(rr)),
   'medium_outputs':sum(labels[r['id']]['ambiguity']!='low' for r in rr)}
 rep1=[r for r in rows if r['arm']=='O0' and r['replicate']==1]
 result['unexecuted_cascade_arithmetic_upper_bound']={'valid_O0_rep1':fraction(sum(strict(r,labels[r['id']]) for r in rep1),27),
  'meaning':'Under frozen invalid-O direct-failure rule, even perfect downstream Gap cannot exceed this validity fraction. No E2 outputs exist; this is an arithmetic bound, not measured cascade performance.'}
 result['caveat']='Post hoc sensitivity, not revised annotation or replacement Gate; no model calls. Low-ambiguity subset changes composition and is descriptive only.'
 write(P/'analysis/SENSITIVITY.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
