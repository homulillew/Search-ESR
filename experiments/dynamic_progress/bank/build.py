import json,hashlib,copy
from pathlib import Path
T=Path(__file__).resolve().parents[1];R=T.parents[1];OLD=R/'experiments/frontier_generation/bank'
def rd(p):return json.loads(p.read_text())
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def dg(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def claims(c):return [x['statement'] for x in c['state']['verified_claims']]
def key(c):return dg({'Original Question':c['question'],'Verified Claims':claims(c)})
inv=rd(OLD/'CHECKPOINT_INVENTORY.json');challenge=rd(OLD/'CHECKPOINT_BANK.json');oldids={c['checkpoint_id'] for c in challenge};oldkeys={key(c) for c in challenge}
unique={}
for c in sorted(inv,key=lambda c:c['checkpoint_id']):
 if c['checkpoint_id'] in oldids or key(c) in oldkeys:continue
 unique.setdefault(key(c),c)
byqid={q:sorted([c for c in unique.values() if c['qid']==q],key=lambda c:(c['claim_count'],c['checkpoint_id'])) for q in sorted({c['qid'] for c in unique.values()},key=int)}
selected=[]
for q,cs in byqid.items():
 assert len(cs)>=2
 selected.extend([cs[0],cs[-1]])
 if q in ['435','580','311','1094']:
  rem=cs[1:-1];selected.append(rem[(len(rem)-1)//2])
selected=sorted(copy.deepcopy(selected),key=lambda c:(int(c['qid']),c['claim_count'],c['checkpoint_id']))
for i,c in enumerate(selected,1):c.update(case_id=f'P{i:02}',set='fresh_primary',progress_key=key(c))
for c in challenge:c.update(case_id='C'+c['case_id'][1:],set='challenge',progress_key=key(c))
assert len(selected)==len({key(c) for c in selected})==24
assert not {key(c) for c in selected}&oldkeys
wr(T/'bank/PRIMARY.json',selected);wr(T/'bank/CHALLENGE.json',challenge)
wr(T/'bank/INVENTORY.json',[{**c,'progress_key':key(c),'used_F1_checkpoint':c['checkpoint_id'] in oldids,'used_F1_QC':key(c) in oldkeys} for c in inv])
# FULL sensitivity: one lowest-Claim-count primary perqid, plus remaining midpoint strata q435/q580.
sens=[min([c for c in selected if c['qid']==q],key=lambda c:(c['claim_count'],c['checkpoint_id'])) for q in byqid]
for q in ['435','580']:sens.append(sorted([c for c in selected if c['qid']==q],key=lambda c:c['claim_count'])[1])
wr(T/'bank/SELECTION.json',{'rule':'Exclude F1checkpoint IDs and exact Q+Claim-statement keys. Deduplicate remaining keys by lexicographic checkpoint ID. Perqid select min/max claim-count(tieID), plus lower-middle remaining for435/580/311/1094 historical strata.',
 'primary_count':24,'qids':10,'max_per_qid':3,'eligible_unique_keys':len(unique),'primary':[c['checkpoint_id'] for c in selected],
 'challenge':[c['checkpoint_id'] for c in challenge],'full_sensitivity':[c['case_id'] for c in sens],'full_count':12,
 'freshness':'Novel exact Q+Claims inputs relative to F1. Same historical qids, sources and legacy/reviewer-seed provenance; not topic-heldout or never-analysed research.'})
for group,cs in [('primary',selected),('challenge',challenge)]:
 lines=[]
 for c in cs:
  lines += [f"\n{c['case_id']} qid={c['qid']} {c['checkpoint_id']}",c['question']]+[f'C{i}: {s}' for i,s in enumerate(claims(c),1)]
 (T/'bank'/f'{group}_review.txt').write_text('\n'.join(lines)+'\n')
print([(c['case_id'],c['qid'],c['checkpoint_id'],c['claim_count']) for c in selected])
