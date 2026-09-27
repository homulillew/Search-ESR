"""Arithmetic over committed manual judgments. No automated semantic scoring."""
from collections import Counter
import subprocess
from .common import *
from .run import OUT,load_rows
from experiments.dynamic_local_obligation.score import DIMENSIONS,ERRORS,PAIRS,fraction,strict

def summarize(rows,labels,pairs):
 result={}
 for a in ARMS:
  rr=[r for r in rows if r['arm']==a];n=len(rr);pp=[p for p in pairs if p['arm']==a]
  result[a]={'strict':fraction(sum(strict(r,labels[r['id']]) for r in rr),n),
   'dimensions':{k:fraction(sum(r['valid_output'] and labels[r['id']]['dimensions'][k] for r in rr),n) for k in DIMENSIONS},
   'schema':fraction(sum(r['valid_output'] for r in rr),n),
   'errors':{k:fraction(sum(k in labels[r['id']]['errors'] for r in rr),n) for k in ERRORS},
   'broadness':fraction(sum(bool(set(labels[r['id']]['errors']) & {'whole_question_restatement','bundled_objectives'}) for r in rr),n),
   'pair_categories':dict(Counter(p['relation'] for p in pp)),
   'stable_both_valid':fraction(sum(p['relation'] in PAIRS[:2] for p in pp),len(pp)),
   'raw_both_valid':fraction(sum(p['relation'] in PAIRS[:3] for p in pp),len(pp))}
 return result

def differences(x,base):
 metrics=lambda a:{'strict':a['strict']['rate'],'broadness':a['broadness']['rate'],
  'downstream':a['errors']['downstream_obligation']['rate'],'relation_arg':a['errors']['wrong_relation_arguments']['rate'],
  'stable':a['stable_both_valid']['rate'],'scope':a['dimensions']['ScopeFaithful']['rate']}
 return {k:100*(v-metrics(base)[k]) for k,v in metrics(x).items()}
def mechanism(d):
 return (d['strict']>=10-1e-8 or d['broadness']<=-10+1e-8 or d['stable']>=15-1e-8) and d['relation_arg']<=5+1e-8
def viability(x):
 checks={'strict':x['strict']['rate']>=.75,'broadness':x['broadness']['rate']<=.15,'downstream':x['errors']['downstream_obligation']['rate']<=.15,
  'scope':x['dimensions']['ScopeFaithful']['rate']>=.85,'stable':x['stable_both_valid']['rate']>=.65,'relation_arg':x['errors']['wrong_relation_arguments']['rate']<=.075}
 return {'checks':checks,'signal':all(checks.values())}
def compute(rows,labels,pairs):
 available=read(P/'analysis/CONTEXT_AVAILABILITY.json')['subsets'];subsets={'overall':list(bank()),**{k:available[k] for k in ('delta_eligible','path_eligible','observation_eligible')},'empty_context':[c for c in bank() if c not in available['path_eligible']]}
 result={}
 for name,cases in subsets.items():
  rr=[r for r in rows if r['case_id'] in cases];pp=[p for p in pairs if p['case_id'] in cases];table=summarize(rr,labels,pp)
  changes={a:differences(table[a],table['C0']) for a in ARMS[1:]}
  increments={a+'-'+b:differences(table[a],table[b]) for a,b in [('C1','CDELTA'),('C2','C1')]}
  result[name]={'cases':cases,'metrics':table,'delta_vs_C0_pp':changes,'incremental_pp':increments,
   'mechanism_vs_C0':{a:mechanism(d) for a,d in changes.items()},'incremental_mechanism':{a:mechanism(d) for a,d in increments.items()},
   'viability':{a:viability(table[a]) for a in ARMS}}
 return result

def main():
 path=OUT/'review/FIRST_PASS.json';assert subprocess.check_output(['git','show','HEAD:'+rel(path)],cwd=ROOT)==path.read_bytes()
 key=read(OUT/'review/KEY.json');labels={key[l['review_id']]:l for l in read(path)};rows=load_rows();pairs=read(OUT/'review/PAIR_REVIEW.json')
 assert len(labels)==216 and set(labels)=={r['id'] for r in rows} and len(pairs)==108
 for l in labels.values():
  assert set(l['dimensions'])==set(DIMENSIONS) and all(type(v) is bool for v in l['dimensions'].values())
  assert set(l['errors'])<=set(ERRORS) and l['reason'] and l['ambiguity'] in ('low','medium','high')
 assert {(p['case_id'],p['arm']) for p in pairs}=={(r['case_id'],r['arm']) for r in rows}
 for p in pairs:
  assert p['relation'] in PAIRS and p['reason']
  count=sum(strict(r,labels[r['id']]) for r in rows if r['case_id']==p['case_id'] and r['arm']==p['arm'])
  assert (p['relation'] in PAIRS[:3])==(count==2)
  assert (p['relation']=='one_valid_one_invalid')==(count==1)
  assert (p['relation']=='both_invalid')==(count==0)
 result=compute(rows,labels,pairs);write(OUT/'METRICS.json',result)
 print(json.dumps(result['overall'],indent=2))
if __name__=='__main__':main()
