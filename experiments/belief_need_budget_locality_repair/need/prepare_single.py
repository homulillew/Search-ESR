"""Freeze one selected policy; confirmation is a separate qid-disjoint bank."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from transport import P,ROOT,C,rd,save,sha,dg,head
stage,arm=sys.argv[1:3];N=P/'need';D=N/stage;confirm=stage.startswith('confirmation');pr=N/'prompts'/f'{arm}.txt';assert pr.exists()
if confirm:
 bank=rd(P/'bank/CONFIRMATION.json');inputs={s['state_id']:s['belief'] for s in bank};refs={};byhash={dg(b):i for i,b in inputs.items()}
 for p in rd(P/'bank/COVERAGE_PAIRS.json'):
  if p['split']!='confirmation':continue
  for side in ['A','B']:
   h=dg(p[side]);ident=byhash.get(h,p['pair_id']+'_'+side)
   if h not in byhash:inputs[ident]=p[side];byhash[h]=ident
   refs[p['pair_id']+'_'+side]=ident
 pre=['F07_S00','F14_S06','F15_S02']
else:
 inputs=rd(N/'development/INPUTS.json');refs=rd(N/'development/PAIR_REFS.json');pre=['F01_S00','F03_S06','F04_S02']
jobs=[]
for sid,b in inputs.items():
 view={'Original Question':b['question'],'Verified Claims':b['claims'],'Working Hypothesis':b['hypothesis']}
 req={'model':C['model'],'messages':[{'role':'system','content':pr.read_text()},{'role':'user','content':json.dumps(view,ensure_ascii=False)}],'stream':False,'temperature':0,'response_format':C['response_format']}
 jobs.append({'id':arm+'__'+sid,'arm':arm,'input_id':sid,'belief_sha256':dg(b),'request':req})
save(D/'INPUTS.json',inputs);save(D/'PAIR_REFS.json',refs);save(D/'JOBS.json',jobs);save(D/'PLAN.json',{'head_before_freeze':head(),'arm':arm,'preflight':[arm+'__'+s for s in pre],'horizon':1,'sample_count':1,'max_retries':0,'selection':'All frozen primary states and unique pair projections; no result selection.'})
files=list(D.glob('*.json'))+[pr,N/'run.py',Path(__file__),P/'transport.py',N/'SETTINGS.json',P/'bank/CONFIRMATION.json',P/'bank/DEVELOPMENT.json',P/'bank/COVERAGE_PAIRS.json',N/'analyze.py']
design=N/(arm+'_DESIGN.md')
if design.exists():files.append(design)
save(D/'FREEZE.json',{'head_before_freeze':head(),'files':{str(f.relative_to(ROOT)):sha(f) for f in files}});print('frozen jobs',len(jobs))
