import sys,collections,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
b=TOP/'admission_exploration';ids={r['packet_id'] for r in read(b/'selection.json')};g={r['packet_id']:r for r in read(TOP/'admission_replay/GOLD_ADMISSION_ATOMS.json')};bank={r['packet_id']:r for r in read(TOP/'admission_replay/BANK.json')}
reviews=read(b/'REVIEWS.json');old=read(TOP/'admission_replay/COUNTERFACTUAL_POST_STATES.json');rows=[r for r in old if r['packet_id'] in ids]
res=read(b/'U2_outputs.json');assert len(res)==27
for r in res:
 uid=digest(['admission-review',r['case_id'],r['output']])[:16];v=reviews[uid];c=v['claims'];o=r['output'];p=bank[r['case_id']];pre={'Original Question':p['pre_state']['question'],'Verified Claims':[x['statement'] for x in p['pre_state']['verified_claims']],'Working Hypothesis':p['pre_state']['working_hypothesis']};post=copy.deepcopy(pre)
 post['Verified Claims'].extend(o['claims_to_add']);h=o['hypothesis_update']
 if h['action']=='set':post['Working Hypothesis']=h['statement']
 elif h['action']=='clear':post['Working Hypothesis']=None
 x={'packet_id':r['case_id'],'qid':r['qid'],'arm':'U2','valid':True,'claims':len(c),'supported':sum(z['source_supported'] for z in c),'relevant':sum(z['decision_relevant'] for z in c),'incidental':sum(z['incidental'] for z in c),'novel':sum(z['novel'] for z in c),'scope_loss':sum(not z['scope_preserved'] for z in c),'captured_atoms':len(v['captured_atoms']),'atom_denominator':len(g[r['case_id']]['atoms']),'hypothesis_error':not v['hypothesis_verdict'].startswith('correct_'),'hypothesis_verdict':v['hypothesis_verdict'],'mutation':pre!=post,'no_change':pre==post,'char_delta':len(json.dumps(post,ensure_ascii=False,sort_keys=True))-len(json.dumps(pre,ensure_ascii=False,sort_keys=True)),'correct_empty':g[r['case_id']]['no_new_claim_expected'] and not c,'post_semantic_state':post}
 rows.append(x)
metrics={}
for arm in ['U0','Uc','U1','U2']:
 rr=[r for r in rows if r['arm']==arm];d={k:sum(r[k] for r in rr) for k in ['valid','claims','supported','relevant','incidental','novel','scope_loss','captured_atoms','atom_denominator','hypothesis_error','mutation','no_change','char_delta','correct_empty']};d['planned']=len(rr);d['hypothesis_verdicts']=dict(collections.Counter(r['hypothesis_verdict'] for r in rr));metrics[arm]=d
cost={k:sum(r['usage'][k] for r in res) for k in ['input','output','hit','miss','reasoning']};cost['cache_rate']=cost['hit']/(cost['hit']+cost['miss'])
write(b/'metrics.json',{'matched_arms':metrics,'U2_incremental_cost':cost,'interpretation':'adaptive same-bank diagnostic, not confirmation; original gate unchanged'})
write(b/'COUNTERFACTUAL_POST_STATES.json',rows)
print(json.dumps({'matched_arms':metrics,'cost':cost},indent=2))
