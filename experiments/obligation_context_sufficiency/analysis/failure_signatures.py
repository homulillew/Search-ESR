"""Post-hoc descriptive intersections of frozen dimensions; no new success gate."""
from collections import Counter
from experiments.obligation_context_sufficiency.common import *
from experiments.obligation_context_sufficiency.run import OUT,load_rows
from experiments.obligation_context_sufficiency.score import strict
from experiments.minimal_need_multiquery.run import accounting_summary
key=read(OUT/'review/KEY.json');labels={key[x['review_id']]:x for x in read(OUT/'review/FIRST_PASS.json')};rows=load_rows();out={}
for a in ARMS:
 c=Counter();ids={}
 for r in rows:
  if r['arm']!=a:continue
  l=labels[r['id']];d=l['dimensions']
  if not r['valid_output']:k='mechanical'
  elif strict(r,l):k='valid'
  else:
   locality=not(d['Local'] and d['Coherent']);structure=not(d['ScopeFaithful'] and d['NonDownstream'])
   k='both_locality_and_structure' if locality and structure else 'locality_only' if locality else 'structure_only' if structure else 'other_semantic'
  c[k]+=1;ids.setdefault(k,[]).append(r['id'])
 out[a]={'counts':dict(c),'ids':ids}
write(P/'analysis/FAILURE_SIGNATURES.json',{'definition':'Locality = fail Local or Coherent. Structure = fail ScopeFaithful or NonDownstream. Mechanical excluded from semantic categories. Descriptive intersections, not causal fractions.', 'arms':out})
write(P/'analysis/ACCOUNTING_BY_ARM.json',{a:accounting_summary([r for r in rows if r['arm']==a]) for a in ARMS})
print(json.dumps({a:x['counts'] for a,x in out.items()},indent=2))
