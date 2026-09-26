"""Mechanical Q+C+H projection of actual archived states; no new semantic Claims."""
import collections,copy,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1]
def rd(p):return json.loads((R/p).read_text())
def dg(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def sh(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def wr(n,x):(P/'bank'/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
rows={};hashes={};trans=[]
def add(s,path,pointer,origin):
    if not s.get('question'):return
    claims=s.get('verified_claims',s.get('claims',[]));h=s.get('working_hypothesis',s.get('hypothesis','')) or ''
    assert all(isinstance(x,dict) and 'statement' in x for x in claims)
    belief={'question':s['question'],'claims':[x['statement'] for x in claims],'hypothesis':h}
    key=dg(belief);group=dg({k:v for k,v in belief.items() if k!='hypothesis'})
    if key not in rows:rows[key]={'belief_hash':key,'state_group':group,'qid':str(s['qid']),**belief,'claim_records':copy.deepcopy(claims),'origins':[]}
    if path not in hashes:hashes[path]=sh(path)
    rows[key]['origins'].append({'path':path,'file_sha256':hashes[path],'pointer':pointer,'origin':origin})
    return key
p='experiments/frontier_generation/bank/CHECKPOINT_INVENTORY.json'
for i,r in enumerate(rd(p)):add(r['state'],p,f'/{i}/state',r['state_origin'])
p='experiments/deferred_recovery/bank/HISTORICAL_INVENTORY.json'
for i,u in enumerate(rd(p)):
    a=add(u['pre_state'],p,f'/{i}/pre_state','Actual historical G5 PRE Writer state')
    b=add(u['post_state'],p,f'/{i}/post_state','Actual historical G5 POST Writer state')
    trans.append({'id':'G5_'+u['id'],'qid':str(u['qid']),'before':a,'after':b,'observation':u['observation'],'proposal':u['proposal'].get('output'),'path':p,'pointer':f'/{i}'})
p='experiments/goal_residual_control/transition_replan_v2/state_updates.json'
for i,u in enumerate(rd(p)):
    a=add(u['pre_state'],p,f'/{i}/pre_state','Actual G4 PRE Writer state')
    b=add(u['post_state'],p,f'/{i}/post_state','Actual G4 POST Writer state')
    trans.append({'id':f'G4_{i}','qid':str(u['qid']),'before':a,'after':b,'observation':u['observation'],'proposal':u['proposal'].get('output'),'path':p,'pointer':f'/{i}'})
p='experiments/bcplus_verification/RESULTS.json'
for key,c in rd(p).items():
    for i,u in enumerate(c['updates']):
        base={'qid':c['qid'],'question':c['question']}
        a=add({**base,**u['pre_state']},p,f'/{key}/updates/{i}/pre_state',f"Actual BC {c['arm']} PRE Writer state; V originated from a supplied provisional candidate")
        b=add({**base,**u['post_state']},p,f'/{key}/updates/{i}/post_state',f"Actual BC {c['arm']} POST Writer state; V originated from a supplied provisional candidate")
        trans.append({'id':f'BC_{key}_{i}','qid':str(c['qid']),'before':a,'after':b,'observation':u['observation'],'proposal':u['proposal'].get('output'),'path':p,'pointer':f'/{key}/updates/{i}'})
p='experiments/evidence_scope_localization/bank/RUNTIME_INPUTS.json'
for i,s in enumerate(rd(p)):add(s,p,f'/{i}','Previously frozen actual evidence-scope prefix projection')
# Formal frontier/progress input exposure, not inferred from output quality.
exposed=set()
for p in ['experiments/frontier_generation/bank/CHECKPOINT_BANK.json','experiments/dynamic_progress/bank/PRIMARY.json','experiments/dynamic_progress/bank/CHALLENGE.json','experiments/asymmetric_progress/bank/PRIMARY.json','experiments/asymmetric_progress/bank/CHALLENGE.json']:
 for c in rd(p):
    s=c['state'];exposed.add(dg({'question':s['question'],'claims':[x['statement'] for x in s['verified_claims']]}))
for i,r in enumerate(sorted(rows.values(),key=lambda r:(int(r['qid']),len(r['claims']),r['belief_hash'])),1):
    r['inventory_id']=f'B{i:03}';r['claim_count']=len(r['claims']);r['named_challenge_qid']=r['qid'] in ['580','1094','435','311','186'];r['prior_frontier_or_progress_exposed']=r['state_group'] in exposed
wr('INVENTORY.json',list(rows.values()));wr('TRANSITIONS.json',trans);wr('SOURCE_HASHES.json',hashes)
summary={'natural_unique_QCH_states':len(rows),'unique_QC_groups':len({r['state_group'] for r in rows.values()}),'by_qid':{q:dict(collections.Counter('challenge' if r['named_challenge_qid'] else 'exposed' if r['prior_frontier_or_progress_exposed'] else 'less_exposed' for r in rows.values() if r['qid']==q)) for q in sorted({r['qid'] for r in rows.values()},key=int)},'support_review_pending':True,'actual_archived_transitions':len(trans)}
wr('INVENTORY_SUMMARY.json',summary)
print(json.dumps(summary,indent=2))
# Compact reviewer material only, no sources/answers/old model output.
for q in sorted({r['qid'] for r in rows.values()},key=int):
    rr=sorted([r for r in rows.values() if r['qid']==q],key=lambda r:(len(r['claims']),r['inventory_id']))
    lines=[rr[0]['question']]
    for r in rr:
        lines+=[f"\n{r['inventory_id']} claims={len(r['claims'])} exposed={r['prior_frontier_or_progress_exposed']} hash={r['belief_hash'][:10]}",'H: '+r['hypothesis']]+[f'C{i+1}: {t}' for i,t in enumerate(r['claims'])]
    (P/'bank'/f'review_{q}.txt').write_text('\n'.join(lines)+'\n')
