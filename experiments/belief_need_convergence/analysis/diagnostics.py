"""Explicit semantic pair/issue annotations and derived diagnostic counts."""
from aggregate import rd,wr,P,metric
import collections,json
R=rd(P/'round_0/REVIEW.json');M={(r['case_id'],r['arm']):r for r in R};pairs=rd(P/'bank/DELTA_PAIRS.json')
# Single-reviewer exact-g matching after reading A/B Need text, not keyword grading.
active={'DC01':[], 'DC02':['P4'], 'DC03':['P3','P4'], 'DC04':['P4'], 'DC05':[], 'DC06':['P0','P1','P4'], 'DC07':['P0','P3','P4'], 'DC08':['P0','P3'], 'DC09':['P4'], 'DC10':['P4'], 'DC11':['P3','P4'], 'DC12':['P3']}
rows=[];summary={}
for a in ['P0','P1','P2','P3','P4']:
 cov=[];hy=[]
 for d in pairs:
  x,y=M[d['A_case'],a],M[d['B_case'],a]
  if d['kind']=='coverage':
   r={'pair_id':d['pair_id'],'arm':a,'A_case':d['A_case'],'B_case':d['B_case'],'A_strict':x['STRICT_VALID'],'B_strict':y['STRICT_VALID'],'A_asks_g':a in active[d['pair_id']] if x['output'] else None,'B_asks_covered_g':False if y['output'] else None,'pair_correct':x['STRICT_VALID'] and y['STRICT_VALID'],'reason':'Manual exact-local-g review: no returned B Need re-asks the exact newly covered relation. Generic animation credit does not cover intro/end role; capital-city scope differs from base-city name; name/film joins differ from a supported local role. Broad full-Q B failures remain invalid regardless of no literal g repetition.','A_output':x['output'],'B_output':y['output']};cov.append(r)
  else:
   r={'pair_id':d['pair_id'],'arm':a,'A_case':d['A_case'],'B_case':d['B_case'],'A_P':x['P'],'B_P':y['P'],'A_strict':x['STRICT_VALID'],'B_strict':y['STRICT_VALID'],'both_assessable':bool(x['output'] and y['output']),'A_output':x['output'],'B_output':y['output'],'specificity_note':'Same Claim-named candidates can remain concrete without H. P3 DH02 shifts anonymous role to named candidate; DH01/DH03 add global/bundled verification. Do not assume H always increases useful specificity.'};hy.append(r)
  rows.append(r)
 act=[r for r in cov if r['A_asks_g']];acts=[r for r in act if r['A_strict']];paired=[r for r in hy if r['both_assessable']]
 summary[a]={'coverage_pairs':len(cov),'pair_correct':sum(r['pair_correct'] for r in cov),'A_g_activated':len(act),'A_g_activated_and_strict':len(acts),'strict_success_after_valid_activation':sum(r['pair_correct'] for r in acts),'observable_g_retirement_after_valid_activation':sum(r['B_asks_covered_g'] is False for r in acts),'B_assessable':sum(r['B_asks_covered_g'] is not None for r in cov),'B_exact_g_stale':sum(r['B_asks_covered_g'] is True for r in cov),'H_pairs_both_assessable':len(paired),'H_premise_before':sum(r['A_P'] is True for r in paired),'H_premise_after':sum(r['B_P'] is True for r in paired)}
wr(P/'analysis/PAIR_REVIEW.json',rows);wr(P/'analysis/PAIR_METRICS.json',summary)
# P3A issue semantics. These codes follow actual issue strings read in full.
broad={1,2,5,12,15,16,20,21,27,33,35,47,49};issue=[]
for n in range(1,56):
 cid=f'N{n:03}';a=rd(P/'round_0_p3_format_repair/calls'/f'{cid}_P3A.result.json');b=M[cid,'P3']
 valid=bool(a['output']) and n not in broad and n!=44
 reason='One material local uncertainty not established by Claims; provisional candidate may specialize it.'
 if n in broad:reason='Missing issue is whole-candidate identity or a bundle of separable conditions; breadth exists before formulation.'
 if n==44:reason='Tests one identity join while assuming a separate full-name/credit join; strict alias boundary, reported in sensitivity.'
 if not a['output']:reason='No issue output: reasoning length cap reached, not semantically assessable.'
 issue.append({'case_id':cid,'issue':a['output'],'issue_valid':valid,'assessable':bool(a['output']),'reason':reason,'need_strict':b['STRICT_VALID'],'valid_issue_to_invalid_need':valid and not b['STRICT_VALID'],'need_reason':b['reason']})
wr(P/'analysis/P3_ISSUE_REVIEW.json',issue)
wr(P/'analysis/P3_ISSUE_METRICS.json',{'states':55,'issues_returned':sum(r['assessable'] for r in issue),'valid_issues':sum(r['issue_valid'] for r in issue),'valid_issue_to_invalid_need':sum(r['valid_issue_to_invalid_need'] for r in issue),'introduced_cases':[r['case_id'] for r in issue if r['valid_issue_to_invalid_need']]})
print(json.dumps(summary,indent=2));print('P3 valid issues',sum(r['issue_valid'] for r in issue),'introduced errors',sum(r['valid_issue_to_invalid_need'] for r in issue))
