"""Instantiate semantic prompts only after committed acquisition and labels."""
import json,sys,subprocess,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from transport import P,ROOT,C,rd,save,sha,dg,head,NEED_SCHEMA
N=P/'need';(N/'prompts').mkdir(parents=True,exist_ok=True)
assert subprocess.check_output(['git','show','HEAD:'+str((P/'bank/OFFLINE_LABELS.json').relative_to(ROOT))],cwd=ROOT)==(P/'bank/OFFLINE_LABELS.json').read_bytes()
old=ROOT/'experiments/belief_need_convergence/prompts'
for a,f in [('B0','P1.txt'),('B1','P1_local.txt'),('ORACLE','P4.txt')]:
 with (N/'prompts'/f'{a}.txt').open('x') as out:out.write((old/f).read_text())
task=(P/'TASK.md').read_text();section=task.split('# 17. Path B2')[1].split('# 18.')[0];prompt=re.search(r'```text\n(You are choosing one next research question\.[\s\S]*?)\n```',section).group(1)+'\n'
with (N/'prompts/B2.txt').open('x') as f:f.write(prompt)
save(N/'SETTINGS.json',{'model':C['model'],'provider':C['provider'],'max_tokens':'OMITTED','temperature':0,'max_retries':0,'timeout':240,'parallel_workers':8,
 'sample_count_per_input_arm':1,'horizon':1,'tools':[],'semantic_schema':NEED_SCHEMA,
 'development_gate':{'completion':.95,'strict':.85,'premise_max':.05,'stale_max':.05,'broad_max':.10,'no_h':.80,'one_gap':.90,'delta':.85},
 'confirmation_gate':{'states_min':24,'qids_min':8,'completion':.95,'strict':.90,'premise_max':.05,'stale_max':.05,'broad_max':.05,'no_h':.85,'one_gap':.90,'delta':.90},
 'delta_gate':'B strict validity and retirement among A-valid activations both meet threshold; zero activations cannot verify retirement. Also report all activation/retirement/both-valid denominators.',
 'B3_trigger':'B2 >=2 primary broad cases across >=2qids OR primary broadness>10percent. No B3 otherwise.',
 'bounded_bad_case_loops':3,'dominant_mechanisms_per_loop':1,'reasoning_regression':'Flag P90 reasoning>1.5x parent or new length failures; no adoption without cost review.',
 'one_gap_adequate':{'states':8,'qids':3},'review':'Single Codex reviewer, direct final outputs/QCH only; not model rationale. Labels and dimensions kept per item.',
 'freshness':'Offline evaluator labels do not authorize confirmation outputs for prompt design. Confirmation is called once for selected policy only.'})
def request(b,arm,issue=None):
 view={'Original Question':b['question'],'Verified Claims':b['claims'],'Working Hypothesis':b['hypothesis']}
 if issue is not None:view['Confirmed unresolved issue (diagnostic only)']=issue
 return {'model':C['model'],'messages':[{'role':'system','content':(N/'prompts'/f'{arm}.txt').read_text()},{'role':'user','content':json.dumps(view,ensure_ascii=False)}],'stream':False,'temperature':0,'response_format':C['response_format']}
bank=rd(P/'bank/DEVELOPMENT.json');pairs=[p for p in rd(P/'bank/COVERAGE_PAIRS.json') if p['split']=='development'];inputs={};refs={}
for s in bank:inputs[s['state_id']]=s['belief']
byhash={dg(b):i for i,b in inputs.items()}
for p in pairs:
 for side in ['A','B']:
  h=dg(p[side]);ident=byhash.get(h,p['pair_id']+'_'+side)
  if h not in byhash:inputs[ident]=p[side];byhash[h]=ident
  refs[p['pair_id']+'_'+side]=ident
jobs=[]
for ident,b in inputs.items():
 for a in ['B0','B1','B2']:jobs.append({'id':a+'__'+ident,'arm':a,'input_id':ident,'belief_sha256':dg(b),'request':request(b,a)})
for s in bank:jobs.append({'id':'ORACLE__'+s['state_id'],'arm':'ORACLE','input_id':s['state_id'],'belief_sha256':dg(s['belief']),'request':request(s['belief'],'ORACLE',s['label']['oracle_issue'])})
save(N/'development/INPUTS.json',inputs);save(N/'development/PAIR_REFS.json',refs);save(N/'development/JOBS.json',jobs)
save(N/'development/PLAN.json',{'head_before_freeze':head(),'primary_states':len(bank),'primary_qids':len({s['qid'] for s in bank}),'unique_beliefs_including_delta':len(inputs),'jobs':len(jobs),'preflight':['B0__F02_S00','B1__F03_S06','B2__F01_S00'],'failure_policy':'Preserve all; no retry/resample. Stop formal batch if preflight fails.'})
print('primary',len(bank),'unique inputs',len(inputs),'calls',len(jobs))
