"""Deterministic accounting of executed state writes and review scheduling."""
from progress import *

def growth():
 b=TOP/'three_round_loop_v2';cells=read(b/'results.json');out=[]
 for key,c in cells.items():
  count=collections.Counter()
  for u in c['updates']:
   o=u['proposal']['output'];count['updater_calls']+=1
   if o is None:count['invalid_updaters']+=1;continue
   a=u['pre_state'];z=u['post_state'];ss={v['statement'] for v in a['verified_claims']}
   for statement in o['claims_to_add']:
    count['admitted_claim_sentences']+=1
    count['exact_duplicate_admissions']+=statement in ss
    ss.add(statement)
   view=lambda s:{'claims':[v['statement'] for v in s['verified_claims']],'hypothesis':s['working_hypothesis']}
   changed=view(a)!=view(z)
   count['serialized_state_mutations']+=changed
   count['no_state_change']+=not changed
   count['hypothesis_string_changes']+=a['working_hypothesis']!=z['working_hypothesis']
  out.append({'cell':key,'arm':c['arm'],**count,'goal_reviewer_calls':len(c['goal_reviews']),
   'seed_claim_count':len(c['decisions'][0]['pre_state']['verified_claims']) if c['decisions'] else len(c['state']['verified_claims']),
   'final_claim_count':len(c['state']['verified_claims'])})
 sums={a:{k:sum(r.get(k,0) for r in out if r['arm']==a) for k in sorted({k for r in out for k,v in r.items() if isinstance(v,int)})} for a in ['L0','L1','L2']}
 result={'cells':out,'by_arm':sums,'limitations':'Exact duplicate strings are a lower bound on semantic redundancy. Serialized-state mutation is the executed trigger, including incidental/duplicate appends; Goal Reviewer calls are coalesced at tool-batch decision boundaries.'}
 write(b/'state_growth_metrics.json',result);return result
if __name__=='__main__':print(json.dumps(growth()['by_arm'],indent=2))
