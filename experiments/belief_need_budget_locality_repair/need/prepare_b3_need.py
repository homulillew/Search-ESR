"""Freeze actual issue-conditioned requests after issue extraction, without filtering."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from transport import P,ROOT,C,rd,save,sha,dg,head
N=P/'need';A=N/'b3_issue';D=N/'b3_need';assert (A/'COMPLETED.json').exists();inputs=rd(A/'INPUTS.json');jobs=[];failed=[]
for sid,b in inputs.items():
 r=rd(A/'calls'/f'B3A__{sid}.result.json')
 if not r['final_valid_JSON']:failed.append(sid);continue
 view={'Original Question':b['question'],'Verified Claims':b['claims'],'Working Hypothesis':b['hypothesis'],'Unresolved issue (ephemeral)':r['output']['issue']}
 req={'model':C['model'],'messages':[{'role':'system','content':(N/'prompts/B3B.txt').read_text()},{'role':'user','content':json.dumps(view,ensure_ascii=False)}],'stream':False,'temperature':0,'response_format':C['response_format']}
 jobs.append({'id':'B3__'+sid,'arm':'B3','input_id':sid,'belief_sha256':dg(b),'request':req,'issue_result_sha256':sha(A/'calls'/f'B3A__{sid}.result.json')})
save(D/'INPUTS.json',inputs);save(D/'PAIR_REFS.json',rd(N/'development/PAIR_REFS.json'));save(D/'JOBS.json',jobs);save(D/'PLAN.json',{'head_before_freeze':head(),'preflight':[j['id'] for j in jobs if j['input_id'] in ['F01_S00','F03_S06','F04_S02']],'upstream_failures':failed,'semantic_filter':False,'horizon':2,'sample_count':1,'failure_policy':'No retries; upstream failures remain ITT failures. No substitute issue.'})
files=list(D.glob('*.json'))+list(A.glob('*.json'))+list((A/'calls').glob('*.result.json'))+[N/'prompts/B3B.txt',N/'run.py',P/'transport.py',N/'SETTINGS.json']
save(D/'FREEZE.json',{'head_before_freeze':head(),'files':{str(f.relative_to(ROOT)):sha(f) for f in files}});print('stage2',len(jobs),'upstream failures',len(failed))
