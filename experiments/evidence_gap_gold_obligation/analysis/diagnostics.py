"""Post-freeze descriptive strata and cost; no gate changes or live calls."""
from collections import Counter
import math
from experiments.evidence_gap_gold_obligation.common import *
from experiments.evidence_gap_gold_obligation.run import load_rows,OUT
from experiments.evidence_gap_gold_obligation.score import strict,fraction

def main():
 rows=load_rows();key=read(OUT/'review/KEY.json');labels={key[l['review_id']]:l for l in read(OUT/'review/REVIEW.json')};cases=bank();gold={g['case_id']:g for g in read(P/'e0_reference/GOLD_GAPS.json')}
 result={}
 for a in ('G0','G1'):
  arm=[r for r in rows if r['arm']==a]
  groups={s:[r for r in arm if gold[r['case_id']]['reference_status']==s] for s in ('unsupported','partial','satisfied')}
  groups.update({'empty_claims':[r for r in arm if not cases[r['case_id']]['claims']],
   'nonempty_claims':[r for r in arm if cases[r['case_id']]['claims']],
   'nonempty_H':[r for r in arm if cases[r['case_id']]['belief']['hypothesis'] is not None],
   'null_H':[r for r in arm if cases[r['case_id']]['belief']['hypothesis'] is None],
   'exclude_medium_ambiguity':[r for r in arm if gold[r['case_id']]['ambiguity']=='low']})
  result[a]={'strict_by_stratum':{name:fraction(sum(strict(r,labels[r['id']]) for r in rr),len(rr)) for name,rr in groups.items()},
   'question_clusters':{qid:fraction(sum(strict(r,labels[r['id']]) for r in arm if r['qid']==qid),sum(r['qid']==qid for r in arm)) for qid in sorted({r['qid'] for r in arm})},
   'replicate_strict':{str(rep):fraction(sum(strict(r,labels[r['id']]) for r in arm if r['replicate']==rep),27) for rep in (1,2)},
   'failures':[{'id':r['id'],'review_id':labels[r['id']]['review_id'],'case_id':r['case_id'],'state_id':r['state_id'],'reason':labels[r['id']]['reason'],'errors':labels[r['id']]['errors']} for r in arm if not strict(r,labels[r['id']])],
   'nonempty_claim_support_correct':fraction(sum(labels[r['id']]['support_correct'] for r in groups['nonempty_claims']),len(groups['nonempty_claims'])),
   'responses_citing_refs':sum(bool(r['output']['supported_by']) for r in arm)}
 elapsed=sorted(r['elapsed_seconds'] for r in rows);tokens=sorted(r['usage']['completion_tokens'] for r in rows)
 quant=lambda x,p:x[min(len(x)-1,math.ceil(len(x)*p)-1)]
 result['execution']={'responses':len(rows),'latency_seconds':{'min':min(elapsed),'median':quant(elapsed,.5),'p95':quant(elapsed,.95),'max':max(elapsed)},
  'completion_tokens':{'min':min(tokens),'median':quant(tokens,.5),'p95':quant(tokens,.95),'max':max(tokens)},'unknown_usage':sum(not r['accounting']['complete'] for r in rows),'http_statuses':dict(Counter(r['http_status'] for r in rows))}
 result['caveat']='Descriptive post hoc strata, no replacement gates. Status/type distribution and question clustering prevent treating 54 responses as 54 independent questions.'
 write(P/'analysis/DIAGNOSTICS.json',result);print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
