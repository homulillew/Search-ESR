from runtime import *
from cache import ProgressCache

def main():
 cs=rd(TOP/'bank/PRIMARY.json');seen={};calls=[];cache=ProgressCache();c=cs[0]
 facts=[x['statement'] for x in c['state']['verified_claims']]
 def evaluate(q,claims): calls.append(copy.deepcopy((q,claims)));return {'opaque':len(calls)}
 first=cache.decision(c['question'],facts,evaluate)
 first['opaque']=999
 for extras in [{'hypothesis':'changed'},{'workspace':['newwindow']},{'attempts':['search0gain']}]:
  assert cache.decision(c['question'],facts,evaluate,**extras)=={'opaque':1}
 assert len(calls)==1 and cache.claims_version==1
 changed=facts+['offline cache sentinel, never a model input']
 assert cache.decision(c['question'],changed,evaluate)=={'opaque':2} and cache.claims_version==2
 assert cache.decision(c['question']+'?',changed,evaluate)=={'opaque':3} and cache.claims_version==2
 for c in cs+rd(TOP/'bank/CHALLENGE.json'):
  v=view(c);assert set(v)=={'Original Question','Verified Claims'}
  assert [x['statement'] for x in v['Verified Claims']]==[x['statement'] for x in c['state']['verified_claims']]
  assert item(c,'R',1)['request']['messages'][1]==item(c,'B',1)['request']['messages'][1]
 assert (TOP/'prompts/residual.md').read_bytes()==(ROOT/'experiments/goal_residual_control/prompts/goal_reviewer.md').read_bytes()
 good={'resolved':False,'blocking_gaps':[{'gap':'unestablished relation','status':'missing','claim_refs':[]}],'closure_claim_refs':[]}
 validate(good,'B',2)
 bad=copy.deepcopy(good);bad['blocking_gaps'][0]['claim_refs']=[3]
 try:validate(bad,'B',2);raise AssertionError('index validation did not fire')
 except ValueError:pass
 # Harness intentionally accepts semantically unsupported but existing references.
 good['blocking_gaps'][0]['claim_refs']=[1];validate(good,'B',2)
 wr(TOP/'contract_checks.json',{'passed':True,'checks':['cache-only-Q-Claims','copy-isolation','Claim-mutation-invalidation','question-invalidation','H-Workspace-attempt-reuse','no-input-leak','exact-Claims-preservation','same-R-B-input','byte-identical-R-prompt','structural-index-validation-only'],'live_model_calls':0,'semantic_cache_adequacy':'not tested by unit checks'})
 print('contract checks passed')
if __name__=='__main__':main()
