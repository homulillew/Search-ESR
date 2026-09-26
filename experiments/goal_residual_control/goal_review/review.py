"""Codex semantic annotations after reading all 40 exact G1 outputs."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *

base=TOP/'goal_review';states={s['case_id']:s for s in read(TOP/'bank/SNAPSHOTS.json')}
truth=read(TOP/'bank/PRIVATE_TRUTH.json');outs=read(base/'outputs.json')
notes={
 'T03_POST':('precise,new_goal_drift','Adds an exact Fifth Estate role requirement absent from the original question.'),
 'T04_POST':('complete','Retains feature count but omits the still provisional identity and discriminative clues.'),
 'T06_POST':('complete','Omits capital-city and full three-pair table conditions from remaining identity constraints.'),
 'T10_POST':('precise,new_goal_drift','Introduces Game B = Dust as a requirement, although no such equality is required by the original question.'),
 'T11_PRE':('complete,identity_promotion','Says musician identity established from only age and broad career count.'),
 'T12_PRE':('complete,identity_promotion','Treats Oliver as established target from partial biography; exact feature relation stays open.'),
 'T13_PRE':('complete','Premature closure with only the S4 clue; S1/S3/season-count requirements unsupported.'),
 'T14_PRE':('complete','Premature closure before fewer-than-ten-seasons claim is committed.'),
 'T15_POST':('complete','Retains table/founding uncertainty but omits trophy, city and title-period identity constraints.'),
 'T16_PRE':('complete','Retains founding/trophies/title-period but omits table-pair and city identity constraints.'),
 'T19_PRE':('complete','Retains feature count but fails to retain still provisional musician identification.'),
 'T19_POST':('complete,identity_promotion','Correctly refuses the 67-count join, but describes musician identity as verified from partial clues.'),
}
reviews=[]
for x in outs:
 cid=x['case_id'];out=x['output'];gold=truth['snapshots'][cid]['goal_status']=='resolved'
 r={'case_id':cid,'qid':x['qid'],'gold_resolved':gold,'valid':out is not None,
    'resolved_correct':out is not None and out['resolved']==gold,
    'premature_resolve':out is not None and out['resolved'] and not gold,
    'missed_resolve':out is not None and not out['resolved'] and gold,
    'complete':True,'precise':True,'goal_anchored':True,'unsupported_join':False,
    'identity_promotion':False,'solved_item_repetition':False,'new_goal_drift':False,
    'reason':'Residual preserves original-goal uncertainty and does not conflate the partial candidate with a resolved answer.' if not gold else 'Frozen primary Claims jointly support original-goal identity and requested relation; empty residual is appropriate.',
    'categories':states[cid]['categories']}
 if cid in notes:
  flags,reason=notes[cid];r['reason']=reason
  for flag in flags.split(','):r[flag]=False if flag in ('complete','precise') else True
 r['goal_anchored']=not r['new_goal_drift']
 strict_gold=gold and cid not in truth['sensitivity_open_cases']
 r['strict_gold_resolved']=strict_gold;r['strict_resolved_correct']=out is not None and out['resolved']==strict_gold
 reviews.append(r)
write(base/'reviews.json',reviews)
monotonic=[]
for t in read(TOP/'bank/TRANSITIONS.json'):
 monotonic.append({'transition_id':t['transition_id'],'qid':t['qid'],
  'no_new_goal_after_update':t['transition_id'] not in ('T03','T10'),
  'residual_reopened_after_added_claims':t['transition_id']=='T13',
  'newly_solved_requirement_removed':t['transition_id'] not in ('T13','T14'),
  'reason':{'T03':'POST adds unnecessary Fifth Estate role.','T10':'POST adds unsupported Game B=Dust equality.',
     'T13':'PRE falsely empty; POST reopens the actually missing requirements. This is a closure inconsistency, not harmful factual growth.',
     'T14':'PRE already falsely empty before season count is committed; cannot credit a correct residual contraction.'}.get(t['transition_id'],'New supported facts are acknowledged; remaining original requirements retained or resolved status preserved.')})
write(base/'transition_reviews.json',monotonic)
def summary(rows):
 return {'n':len(rows),'resolved_accuracy':sum(x['resolved_correct'] for x in rows),
  'premature_resolve':sum(x['premature_resolve'] for x in rows),'open_n':sum(not x['gold_resolved'] for x in rows),
  'missed_resolve':sum(x['missed_resolve'] for x in rows),'resolved_n':sum(x['gold_resolved'] for x in rows),
  **{k:sum(x[k] for x in rows) for k in ['complete','precise','goal_anchored','unsupported_join','identity_promotion','solved_item_repetition','new_goal_drift']}}
metrics={'all':summary(reviews),'cohorts':{c:summary([x for x in reviews if c in x['categories']]) for c in ['fully_resolved','hypothesis_only','unsupported_join','stale_gap']},
 'strict_accuracy':sum(x['strict_resolved_correct'] for x in reviews),'strict_resolved_n':3,'strict_premature':6,'strict_open_n':37,
 'monotonic_reviews':monotonic,'reviewer':'single Codex; read original questions, frozen truth, claims, exact outputs; no new model judge'}
write(base/'metrics.json',metrics)
hit=sum(x['cache_usage']['prompt_cache_hit_tokens'] for x in outs);miss=sum(x['cache_usage']['prompt_cache_miss_tokens'] for x in outs)
(base/'RESULTS.md').write_text(f'''# G1 results

40/40 valid calls. Primary closure accuracy 38/40 (95%); premature 2/33 open (6.1%); missed 0/7 resolved. Resolved cohort spans only q435/q580. Under pre-frozen strict q435 sensitivity: accuracy 34/40, premature 6/37, missed 0/3.

Two premature closures are q580 T13_PRE (S4 only) and T14_PRE (season count uncommitted). T05_POST and T13_PRE have identical Question+Claims but different outcomes, exposing one-shot instability without any Hypothesis input.

No lifetime-count/Forbes unsupported join. Three residuals overstate musician identity from partial facts. Two introduce unnecessary requirements: Fifth Estate exact role; Game B=Dust equality. Complete residuals {metrics['all']['complete']}/40; precise 38/40; goal-anchored 38/40; no solved-item repetition detected. Detailed semantic and paired transition labels are in reviews.json and transition_reviews.json. Labels are single-reviewer judgments, not independent human replication.

Hypothesis is structurally absent in all requests; this prevents direct leakage but does not prove a causal improvement over a hypothesis-visible reviewer, which was not run. Correct facts do not guarantee stable closure. No performance gate is applied; continue G2–G5.

Cache: {hit}/({hit}+{miss}) = {hit/(hit+miss):.2%}; all 40 responses reported consistent hit/miss tokens.
''')
print(metrics['all'])
