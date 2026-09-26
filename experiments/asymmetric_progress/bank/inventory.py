import json,hashlib,copy
from pathlib import Path
T=Path(__file__).resolve().parents[1];R=T.parents[1]
def rd(p):return json.loads(p.read_text())
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def key(c):return hashlib.sha256(json.dumps({'Original Question':c['question'],'Verified Claims':[x['statement'] for x in c['state']['verified_claims']]},sort_keys=True,ensure_ascii=False).encode()).hexdigest()
inv=rd(R/'experiments/frontier_generation/bank/CHECKPOINT_INVENTORY.json')
old=rd(R/'experiments/frontier_generation/bank/CHECKPOINT_BANK.json')+rd(R/'experiments/dynamic_progress/bank/PRIMARY.json')
# Dynamic semantic exploration is entirely a subset of its primary; check rather than assume.
ex=rd(R/'experiments/dynamic_progress/exploration/requests.json');pri={c['case_id']:c for c in rd(R/'experiments/dynamic_progress/bank/PRIMARY.json')}
old += [pri[i['case_id']] for i in ex]
keys={key(c) for c in old};seen={}
for c in sorted(inv,key=lambda c:c['checkpoint_id']):
 if key(c) not in keys:seen.setdefault(key(c),copy.deepcopy(c))
cs=sorted(seen.values(),key=lambda c:(int(c['qid']),c['claim_count'],c['checkpoint_id']))
for i,c in enumerate(cs,1):c.update(pool_id=f'E{i:02}',progress_key=key(c))
wr(T/'bank/ELIGIBLE_POOL.json',cs)
wr(T/'bank/EXPOSURE_AUDIT.json',{'inventory_size':len(inv),'excluded_unique_QC_keys':len(keys),'eligible_unique_QC_keys':len(cs),'eligible_by_qid':{q:sum(c['qid']==q for c in cs) for q in sorted({c['qid'] for c in cs},key=int)},'dedup_rule':'lexicographically first checkpoint for identical Q+Claim statement key','exclusion_inputs':['frontier_generation/bank/CHECKPOINT_BANK.json','dynamic_progress/bank/PRIMARY.json','dynamic_progress/exploration/requests.json'],'excluded_keys':sorted(keys)})
for q in sorted({c['qid'] for c in cs},key=int):
 group=[c for c in cs if c['qid']==q];lines=[group[0]['question']]
 for c in group:
  lines += [f"\n{c['pool_id']} {c['checkpoint_id']} claims={c['claim_count']}"]+[f"C{i}: {x['statement']}" for i,x in enumerate(c['state']['verified_claims'],1)]
 (T/'bank'/f'review_{q}.txt').write_text('\n'.join(lines)+'\n')
print([(c['pool_id'],c['qid'],c['checkpoint_id'],c['claim_count']) for c in cs])
