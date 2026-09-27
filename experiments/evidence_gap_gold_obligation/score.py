"""Arithmetic only, after committed masked semantic labels and pair/H reviews."""
import subprocess
from collections import Counter
from .common import *
from .run import load_rows, OUT
ERRORS=('downstream_jump','target_as_prerequisite','false_requirement','scope_transfer','wrong_referent','over_strengthening','stale_gap')
def fraction(n,d):return {'n':n,'d':d,'rate':n/d if d else None}
def strict(r,l):return r['valid_output'] and l['support_correct'] and l['missing_label']=='correct' and l['evidence_needed_correct'] and not any(e in l['errors'] for e in ERRORS)
def compute(rows,labels,pairs,gold):
 result={}
 for a in ('G0','G1'):
  rr=[r for r in rows if r['arm']==a];n=len(rr);sat=[r for r in rr if gold[r['case_id']]['reference_status']=='satisfied']
  good=lambda r:bool(strict(r,labels[r['id']]))
  supportrefs=[v for r in rr for v in labels[r['id']]['support_refs']]
  ap=[p for p in pairs if p['arm']==a]
  st=Counter(sum(good(r) for r in rr if r['case_id']==cid) for cid in {r['case_id'] for r in rr})
  same=sum(p['relation']=='same_gap' for p in ap)
  agreement=sum(p['relation']=='same_gap' and all(r['valid_output'] and labels[r['id']]['missing_label']=='correct' and labels[r['id']]['evidence_needed_correct'] for r in rr if r['case_id']==p['case_id']) for p in ap)
  result[a]={'strict':fraction(sum(good(r) for r in rr),n),'missing':fraction(sum(r['valid_output'] and labels[r['id']]['missing_label']=='correct' for r in rr),n),
   'support':fraction(sum(r['valid_output'] and labels[r['id']]['support_correct'] for r in rr),n),
   'support_micro':fraction(sum(v['correct'] for v in supportrefs),len(supportrefs)),
   'evidence_needed':fraction(sum(r['valid_output'] and labels[r['id']]['evidence_needed_correct'] for r in rr),n),
   'evidence_level':fraction(sum(r['valid_output'] and labels[r['id']]['evidence_level'] for r in rr),n),
   'satisfied_specificity':fraction(sum(r['valid_output'] and r['output']['missing'] is None and r['output']['evidence_needed'] is None for r in sat),len(sat)),
   'schema':fraction(sum(r['valid_output'] for r in rr),n),'replicate_semantic':fraction(agreement,len(ap)),
   'raw_same_gap':fraction(same,len(ap)),'replicate_relations':dict(Counter(p['relation'] for p in ap)),
   'strict_pair_counts':{'both_valid':st[2],'exactly_one':st[1],'both_invalid':st[0]},
   'errors':{e:fraction(sum(e in labels[r['id']]['errors'] for r in rr),n) for e in ERRORS},
   'missing_labels':dict(Counter(labels[r['id']]['missing_label'] for r in rr)),
   'candidate_specific_unsupported':fraction(sum(labels[r['id']]['candidate_specific_unsupported'] for r in rr),n)}
 g=result['G0'];gate={k:g[k]['rate']>=v for k,v in {'strict':.8,'missing':.85,'support':.85,'satisfied_specificity':.85,'schema':.95,'replicate_semantic':.8}.items()}
 gate['downstream']=g['errors']['downstream_jump']['rate']<=.1;gate['target_prerequisite']=g['errors']['target_as_prerequisite']['rate']<=.1
 result['gate']={'status':'PASS' if all(gate.values()) else 'FAIL','checks':gate,'stop':'STOP_E1; no additional model calls on either outcome'}
 return result

def main():
 reviewpath=OUT/'review/REVIEW.json';assert subprocess.check_output(['git','show','HEAD:'+rel(reviewpath)],cwd=ROOT)==reviewpath.read_bytes()
 rows=load_rows();key=read(OUT/'review/KEY.json');review=read(reviewpath);labels={key[l['review_id']]:l for l in review}
 assert len(labels)==108 and set(labels)=={r['id'] for r in rows}
 for r in rows:
  l=labels[r['id']];refs=(r.get('output') or {}).get('supported_by',[])
  assert {v['claim_id'] for v in l['support_refs']}==set(refs)
  assert l['reason'] and set(l['errors'])<=set(ERRORS)
 pairs=read(OUT/'review/PAIR_REVIEW.json');assert len(pairs)==54
 assert {(p['case_id'],p['arm']) for p in pairs}=={(r['case_id'],r['arm']) for r in rows}
 gold={g['case_id']:g for g in read(P/'e0_reference/GOLD_GAPS.json')}
 metrics=compute(rows,labels,pairs,gold);write(OUT/'METRICS.json',metrics)
 h=read(OUT/'review/H_REVIEW.json');assert len(h)==54 and {v['id'] for v in h}=={r['id'] for r in rows if r['arm']=='G1'}
 lookup={(r['case_id'],r['arm'],r['replicate']):r for r in rows};comparison=Counter()
 for c in bank():
  for rep in (1,2):
   r0=lookup[c,'G0',rep];r1=lookup[c,'G1',rep];s0=bool(strict(r0,labels[r0['id']]));s1=bool(strict(r1,labels[r1['id']]))
   comparison['G0_better' if s0 and not s1 else 'G1_better' if s1 and not s0 else 'tie']+=1
 write(P/'analysis/H_ABLATION.json',{'paired_strict_comparison':dict(comparison),'H_contamination':fraction(sum(v['H_contamination'] for v in h),54),
  'denominators':'54 matched case×replicate pairs; 11 original null-H cases included. Exposed, clustered development data; descriptive.',
  'contaminated_ids':[v['id'] for v in h if v['H_contamination']]})
 print(json.dumps(metrics,indent=2))
if __name__=='__main__':main()
