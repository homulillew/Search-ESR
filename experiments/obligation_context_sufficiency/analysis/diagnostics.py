"""Descriptive post-unmask diagnostics over frozen first-pass labels."""
from collections import Counter
import subprocess
from experiments.obligation_context_sufficiency.common import *
from experiments.obligation_context_sufficiency.run import OUT,load_rows
from experiments.obligation_context_sufficiency.score import summarize,strict,DIMENSIONS,fraction,compute

def main():
 path=OUT/'review/FIRST_PASS.json';assert subprocess.check_output(['git','show','HEAD:'+rel(path)],cwd=ROOT)==path.read_bytes()
 key=read(OUT/'review/KEY.json');labels={key[l['review_id']]:l for l in read(path)}
 rows=load_rows();pairs=read(OUT/'review/PAIR_REVIEW.json');cases=bank()
 groups={}
 for name,keep in [('qid_'+str(q),{c for c,v in cases.items() if v['qid']==q}) for q in sorted({c['qid'] for c in cases.values()})]:
  groups[name]=summarize([r for r in rows if r['case_id'] in keep],labels,[p for p in pairs if p['case_id'] in keep])
 replicates={str(rep):summarize([r for r in rows if r['replicate']==rep],labels,[]) for rep in (1,2)}
 contrasts={}
 lookup={(r['case_id'],r['arm'],r['replicate']):r for r in rows}
 for a,b in [('CDELTA','C0'),('C1','C0'),('C2','C0'),('C1','CDELTA'),('C2','C1')]:
  ct=Counter({'first_better':0,'second_better':0,'tie':0});detail=[]
  for cid in cases:
   for rep in (1,2):
    x=lookup[cid,a,rep];y=lookup[cid,b,rep];sx=strict(x,labels[x['id']]);sy=strict(y,labels[y['id']])
    label='first_better' if sx and not sy else 'second_better' if sy and not sx else 'tie';ct[label]+=1
    if sx!=sy:detail.append({'case_id':cid,'replicate':rep,'first':x['id'],'second':y['id'],'comparison':label})
  contrasts[a+'-'+b]={'counts':dict(ct),'discordant':detail}
 context=read(OUT/'review/CONTEXT_REVIEW.json');assert len(context)==216 and {x['id'] for x in context}=={r['id'] for r in rows}
 tags=('path_fact_promotion','path_created_requirement','path_candidate_hardening','observation_overreach')
 for x in context:assert all(type(x[t]) is bool for t in tags) and x['reason']
 context_metrics={a:{t:fraction(sum(x[t] for x in context if x['arm']==a),54) for t in tags} for a in ARMS}
 failures={a:{t:[r['id'] for r in rows if r['arm']==a and t in labels[r['id']]['errors']] for t in ('downstream_obligation','wrong_relation_arguments','wrong_object_scope','already_supported','relation_strengthening')} for a in ARMS}
 write(P/'analysis/DIAGNOSTICS.json',{'question_clusters':groups,'replicates':replicates,'paired_descriptive':contrasts,'context_contamination':context_metrics,'error_ids':failures,
  'caution':'Exposed clustered bank; shared reviewer familiarity; paired replicate IDs do not ensure identical provider draws. Contamination flags are content provenance judgments, not individual causal effects.'})
 leave={}
 for q in sorted({c['qid'] for c in cases.values()}):
  rr=[r for r in rows if r['qid']!=q];cc={r['case_id'] for r in rr};leave[str(q)]=summarize(rr,labels,[p for p in pairs if p['case_id'] in cc])
 low=[r for r in rows if labels[r['id']]['ambiguity']=='low'];lp=[p for p in pairs if all(labels[lookup[p['case_id'],p['arm'],rep]['id']]['ambiguity']=='low' for rep in (1,2))]
 relaxed={a:fraction(sum(r['valid_output'] and all(labels[r['id']]['dimensions'][k] for k in DIMENSIONS if k not in ('Local','Coherent')) for r in rows if r['arm']==a),54) for a in ARMS}
 write(P/'analysis/SENSITIVITY.json',{'eligible_and_empty_context':'e1_context/METRICS.json','replicates_and_questions':'analysis/DIAGNOSTICS.json','leave_one_question_out':leave,
  'low_ambiguity_only':summarize(low,labels,lp),'ignore_Local_Coherent_only':relaxed,'primary_labels_unchanged':True,'scope':'Prespecified descriptive sensitivity; not additional gates or relabels.'})
 result=compute(rows,labels,pairs);assert result==read(OUT/'METRICS.json')
 write(P/'analysis/SCORE_REPLAY.json',{'status':'PASS','rows':216,'pair_rows':108,'metrics_sha256':sha(OUT/'METRICS.json'),'first_pass_sha256':sha(path),'replay_exact':True})
if __name__=='__main__':main()
