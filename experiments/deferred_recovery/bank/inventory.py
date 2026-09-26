import json, hashlib, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; TOP=ROOT/'experiments/deferred_recovery'; OLD=ROOT/'experiments/goal_residual_control'
def rd(p):return json.loads(p.read_text())
def dg(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
rows=[]
for cell,c in rd(OLD/'three_round_loop_v2/results.json').items():
 for i,u in enumerate(c['updates']):
  d=next(d for d in c['decisions'] if d['round']==u['round'])
  acts=[a for a in d['actions'] if any(w==u['observation'] for w in a['observations'])]
  assert acts
  rows.append({'id':f'{cell}:{i}', 'qid':c['qid'],'cell':cell,'update_index':i,'round':u['round'],'wave':u['wave'],
    'gap':d['actor']['output']['gap'],'pre_state':u['pre_state'],'observation':u['observation'],
    'proposal':u['proposal'],'post_state':u['post_state'],'producing_actions':acts,'decision_pre_state':d['pre_state']})
wr(TOP/'bank/HISTORICAL_INVENTORY.json',rows)
# All unique observed text per qid, with minimum real context and historical admitted claims.
groups={}
for r in rows:groups.setdefault((r['qid'],dg(r['observation']['text'])),[]).append(r)
review=[]
for n,(k,rs) in enumerate(sorted(groups.items(),key=lambda x:(int(x[0][0]),x[0][1]))):
 review.append({'group_id':f'S{n:03}', 'qid':k[0], 'question':rs[0]['pre_state']['question'],
   'observation':rs[0]['observation'], 'occurrences':[{'id':r['id'],'gap':r['gap'],
     'claims_before':[x['statement'] for x in r['pre_state']['verified_claims']],
     'hypothesis':r['pre_state']['working_hypothesis'],'admitted':r['proposal']['output']} for r in rs]})
wr(TOP/'bank/SOURCE_REVIEW_PACKETS.json',review)
wr(TOP/'analysis/HISTORICAL_HASHES.json',{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in subprocess.check_output(['git','ls-tree','-rz','--name-only','2544fbf'],cwd=ROOT,text=True).rstrip('\0').split('\0')})
print('events',len(rows),'unique text',len(groups),'by qid',{q:sum(r['qid']==q for r in rows) for q in sorted({r['qid'] for r in rows})})
for q in sorted({r['qid'] for r in review},key=int):
 lines=[]
 for r in review:
  if r['qid']!=q:continue
  lines.extend([r['group_id']+' '+r['observation']['url'],r['observation']['text'], 'OCCURRENCES '+json.dumps([{'id':x['id'],'gap':x['gap'],'admitted':x['admitted']} for x in r['occurrences']],ensure_ascii=False)])
 (TOP/'bank'/f'review_q{q}.txt').write_text('\n\n'.join(lines))
