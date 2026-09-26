"""Archive integrity and actual token accounting, including unsuccessful calls."""
import sys,json,collections,subprocess
from pathlib import Path
from transport import P,ROOT,rd,sha,save,dg
out={};old=rd(P/'HISTORICAL_HASHES.json');changed=[s for s,h in old.items() if sha(ROOT/s)!=h];assert not changed
out['historical_files_unchanged']=len(old);out['historical_changes']=changed
states=rd(P/'bank/STATE_INVENTORY.json');support=rd(P/'bank/CLAIM_SUPPORT_REVIEW.json');sources=rd(P/'bank/SOURCES.json')
for s in states:
 assert dg(s['belief'])==s['belief_sha256']
 for c in s['claim_records']:
  assert any(x['statement']==c['statement'] and x['observation_hash'] in c['source_text_hashes'] for x in support)
for s in support:
 import hashlib
 assert hashlib.sha256(sources[s['observation_hash']]['text'].encode()).hexdigest()==s['observation_hash']
out['QCH_provenance_verified']=len(states);out['claim_admissions_audited']=len(support)
dev={s['qid'] for s in rd(P/'bank/DEVELOPMENT.json')};confirm={s['qid'] for s in rd(P/'bank/CONFIRMATION.json')};assert not dev&confirm
out['qid_split']={'dev':sorted(dev),'confirmation':sorted(confirm),'disjoint':True}
for arm,oldprompt in [('B0','P1.txt'),('B1','P1_local.txt')]:assert (P/'need/prompts'/f'{arm}.txt').read_bytes()==(ROOT/'experiments/belief_need_convergence/prompts'/oldprompt).read_bytes()
import re
section=(P/'TASK.md').read_text().split('# 17. Path B2')[1].split('# 18.')[0];assert (P/'need/prompts/B2.txt').read_text()==re.search(r'```text\n(You are choosing one next research question\.[\s\S]*?)\n```',section).group(1)+'\n'
out['exact_baseline_and_user_B2_prompts']=True
for f in (P/'need').glob('*/FREEZE.json'):
 frozen=rd(f)
 for s,h in frozen['files'].items():assert sha(ROOT/s)==h,(f,s)
 for j in rd(f.parent/'JOBS.json'):
  req=j['request'];assert 'max_tokens' not in req and 'tools' not in req and req['temperature']==0
  v=json.loads(req['messages'][1]['content']);assert set(v)<={'Original Question','Verified Claims','Working Hypothesis','Confirmed unresolved issue (diagnostic only)','Unresolved issue (ephemeral)'}
  b=rd(f.parent/'INPUTS.json')[j['input_id']]
  assert v['Original Question']==b['question'] and v['Verified Claims']==b['claims'] and v['Working Hypothesis']==b['hypothesis']
  assert dg(b)==j['belief_sha256']
  rpath=f.parent/'calls'/(j['id']+'.request.json')
  if rpath.exists():
   r=rd(rpath);assert r['request']==req and r['request_sha256']==dg(req)
   assert subprocess.check_output(['git','show',r['head']+':'+str(f.relative_to(ROOT))],cwd=ROOT)==f.read_bytes()
out['need_requests_frozen_before_calls']=True;out['need_tool_calls']=0;out['max_retries']=0
for name in ['e0','acquisition']:
 for s,h in rd(P/name/'FREEZE.json')['files'].items():assert sha(ROOT/s)==h,(name,s)
groups=collections.defaultdict(list)
for f in P.rglob('*.result.json'):
 r=rd(f)
 if not isinstance(r,dict) or 'attempted' not in r:continue
 groups[str(f.relative_to(P)).split('/')[0]].append(r)
tot=[]
for name,rs in groups.items():
 tot.extend(rs);tok=[r.get('token_accounting',{}) for r in rs];inp=sum(u.get('input') or 0 for u in tok);hit=sum(u.get('hit') or 0 for u in tok)
 out[name]={'attempted':sum(r['attempted'] for r in rs),'stored_results':len(rs),'finish_reasons':dict(collections.Counter(r['finish_reason'] for r in rs)),'final_JSON':sum(r['final_valid_JSON'] for r in rs),'input':inp,'cache_hit':hit,'cache_miss':sum(u.get('miss') or 0 for u in tok),'cache_hit_rate':hit/inp if inp else None,'output':sum(u.get('output') or 0 for u in tok),'reasoning':sum(u.get('reasoning') or 0 for u in tok),'final_tokens':sum(u.get('final') or 0 for u in tok)}
inp=sum(r.get('token_accounting',{}).get('input') or 0 for r in tot);hit=sum(r.get('token_accounting',{}).get('hit') or 0 for r in tot)
out['total']={'attempted':sum(r['attempted'] for r in tot),'input_tokens':inp,'output_tokens':sum(r.get('token_accounting',{}).get('output') or 0 for r in tot),'cache_hit_tokens':hit,'cache_hit_rate':hit/inp if inp else None}
save(P/'FINAL_INTEGRITY.json',out);print(json.dumps(out['total']))
