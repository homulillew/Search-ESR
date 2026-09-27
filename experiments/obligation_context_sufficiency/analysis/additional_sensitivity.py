"""Disclosed post-hoc robustness checks. No primary labels/denominators changed."""
import copy
from experiments.obligation_context_sufficiency.common import *
from experiments.obligation_context_sufficiency.run import OUT,load_rows
from experiments.obligation_context_sufficiency.score import summarize,strict,fraction,mechanism,differences
key=read(OUT/'review/KEY.json');labels={key[x['review_id']]:x for x in read(OUT/'review/FIRST_PASS.json')};rows=load_rows();pairs=read(OUT/'review/PAIR_REVIEW.json')
alt=copy.deepcopy(pairs)
for p in alt:
 if p['case_id']=='G12' and p['arm']=='C0':
  assert p['relation']=='different_but_valid';p['relation']='compatible_obligation'
t=summarize(rows,labels,alt)
eligible=set(read(P/'analysis/CONTEXT_AVAILABILITY.json')['subsets']['path_eligible'])
et=summarize([r for r in rows if r['case_id'] in eligible],labels,[p for p in alt if p['case_id'] in eligible])
failed={r['case_id'] for r in rows if not r['valid_output']};rr=[r for r in rows if r['case_id'] not in failed]
write(P/'analysis/ADDITIONAL_SENSITIVITY.json',{
 'status':'POST_HOC_DIAGNOSTIC_ONLY','primary_unchanged':True,
 'motivation':'Overall Delta threshold depends on five stable-pair gains and a single reviewer; baseline alone has two mechanical failures.',
 'pair_perturbation':{'hypothetical_change':'C0 G12: different_but_valid -> compatible_obligation; primary classification is retained because supervisor identity and broader author academic profile have distinct targets, but one includes part of the other.',
  'overall_baseline_stable':t['C0']['stable_both_valid'],'overall_delta_stable_gain_pp':differences(t['CDELTA'],t['C0'])['stable'],
  'overall_delta_mechanism':mechanism(differences(t['CDELTA'],t['C0'])),
  'eligible_mechanism_after_perturbation':{a:mechanism(differences(et[a],et['C0'])) for a in ARMS[1:]}},
 'schema_conditional_strict':{a:fraction(sum(strict(r,labels[r['id']]) for r in rows if r['arm']==a and r['valid_output']),sum(r['valid_output'] for r in rows if r['arm']==a)) for a in ARMS},
 'common_complete_case_subset':{'excluded_case_ids':sorted(failed),'all_arms_matched':True,'metrics':summarize(rr,labels,[p for p in pairs if p['case_id'] not in failed])},
 'caution':'Output-conditioned fractions and post-hoc exclusions are sensitivity descriptions, never a replacement for frozen planned denominators or a new gate.'})
print(json.dumps(read(P/'analysis/ADDITIONAL_SENSITIVITY.json')['pair_perturbation'],indent=2))
