"""Arithmetic over explicit committed judgments; no automatic semantics."""
from collections import Counter
import subprocess
from .common import *
from .run import OUT,load_rows
DIMENSIONS=('GoalGrounded','Unresolved','Material','Local','Coherent','ScopeFaithful','NonDownstream','EvidenceResolvable')
ERRORS=('downstream_obligation','already_supported','whole_question_restatement','over_atomic','invented_requirement','wrong_object_scope','wrong_relation_arguments','relation_strengthening','irrelevant_low_value','unresolved_referent','bundled_objectives','outside_knowledge','output_contract','mechanical_failure')
PAIRS=('same_obligation','compatible_obligation','different_but_valid','one_valid_one_invalid','both_invalid')
def fraction(n,d):return {'n':n,'d':d,'rate':n/d if d else None}
def strict(r,l):return bool(r['valid_output'] and all(l['dimensions'][x] for x in DIMENSIONS))
def compute(rows,labels,comparison,pairs):
 result={}
 for a in ('O0','O1'):
  rr=[r for r in rows if r['arm']==a];n=len(rr);pp=[p for p in pairs if p['arm']==a]
  result[a]={'strict':fraction(sum(strict(r,labels[r['id']]) for r in rr),n),
   'dimensions':{k:fraction(sum(r['valid_output'] and labels[r['id']]['dimensions'][k] for r in rr),n) for k in DIMENSIONS},
   'schema':fraction(sum(r['valid_output'] for r in rr),n),
   'errors':{k:fraction(sum(k in labels[r['id']]['errors'] for r in rr),n) for k in ERRORS},
   'broadness':fraction(sum(bool(set(labels[r['id']]['errors']) & {'whole_question_restatement','bundled_objectives'}) for r in rr),n),
   'gold_selection':{k:fraction(sum(comparison[r['id']]['classification']==k for r in rr),n) for k in ('gold_equivalent','alternate_valid','invalid')},
   'pair_categories':dict(Counter(p['relation'] for p in pp)),
   'stable_both_valid':fraction(sum(p['relation'] in ('same_obligation','compatible_obligation') for p in pp),len(pp)),
   'raw_both_valid':fraction(sum(p['relation'] in ('same_obligation','compatible_obligation','different_but_valid') for p in pp),len(pp))}
 x=result['O0'];checks={'strict':x['strict']['rate']>=.8,'schema':x['schema']['rate']>=.95,'stable_both_valid':x['stable_both_valid']['rate']>=.8,
  'broadness':x['broadness']['rate']<=.1,'wrong_relation_arguments':x['errors']['wrong_relation_arguments']['rate']<=.05}
 checks.update({k:x['dimensions'][k]['rate']>=.9 for k in ('GoalGrounded','Unresolved','ScopeFaithful','NonDownstream')})
 result['gate']={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'next':'E2_REFERENCE_PREPARATION' if all(checks.values()) else 'STOP_E1'}
 return result

def main():
 path=OUT/'review/REVIEW.json';assert subprocess.check_output(['git','show','HEAD:'+rel(path)],cwd=ROOT)==path.read_bytes()
 key=read(OUT/'review/KEY.json');labels={key[l['review_id']]:l for l in read(path)};rows=load_rows()
 assert len(labels)==108 and set(labels)=={r['id'] for r in rows}
 for l in labels.values():
  assert set(l['dimensions'])==set(DIMENSIONS) and all(type(v) is bool for v in l['dimensions'].values())
  assert set(l['errors'])<=set(ERRORS) and l['reason']
 comparison={r['id']:r for r in read(OUT/'review/GOLD_COMPARISON.json')};pairs=read(OUT/'review/PAIR_REVIEW.json')
 assert len(comparison)==108 and len(pairs)==54
 assert {(p['case_id'],p['arm']) for p in pairs}=={(r['case_id'],r['arm']) for r in rows}
 for r in rows:assert (comparison[r['id']]['classification']!='invalid')==strict(r,labels[r['id']])
 for p in pairs:
  assert p['relation'] in PAIRS
  count=sum(strict(r,labels[r['id']]) for r in rows if r['case_id']==p['case_id'] and r['arm']==p['arm'])
  assert (p['relation'] in PAIRS[:3])==(count==2)
  assert (p['relation']=='one_valid_one_invalid')==(count==1)
  assert (p['relation']=='both_invalid')==(count==0)
 result=compute(rows,labels,comparison,pairs);write(OUT/'METRICS.json',result)
 hs=read(OUT/'review/H_REVIEW.json');assert len(hs)==54 and {v['id'] for v in hs}=={r['id'] for r in rows if r['arm']=='O1'}
 lookup={(r['case_id'],r['arm'],r['replicate']):r for r in rows};paired=Counter({'O0_better':0,'O1_better':0,'tie':0})
 for c in bank():
  for rep in (1,2):
   a=lookup[c,'O0',rep];b=lookup[c,'O1',rep];sa=strict(a,labels[a['id']]);sb=strict(b,labels[b['id']])
   paired['O0_better' if sa and not sb else 'O1_better' if sb and not sa else 'tie']+=1
 write(OUT/'H_ABLATION.json',{'paired':dict(paired),'H_contamination':fraction(sum(v['H_contamination'] for v in hs),54),
  'H_contamination_nonempty':fraction(sum(v['H_contamination'] for v in hs if v['H_present']),sum(v['H_present'] for v in hs)),
  'contaminated_ids':[v['id'] for v in hs if v['H_contamination']]})
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
