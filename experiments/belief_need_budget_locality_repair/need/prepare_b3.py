"""User-specified two-step arm, conditional on frozen broadness observations."""
import json,re,sys,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from transport import P,ROOT,rd,save,sha,dg,head,C
N=P/'need';task=(P/'TASK.md').read_text();section=task.split('# 19. Path B3')[1].split('# 20.')[0]
blocks=re.findall(r'```text\n([\s\S]*?)\n```',section);prompts=[b+'\n' for b in blocks if b.startswith(('Find one independently','Formulate the supplied'))];assert len(prompts)==2
for arm,pr in zip(['B3A','B3B'],prompts):
 with (N/'prompts'/f'{arm}.txt').open('x') as f:f.write(pr)
# Trigger requires actual B2 outputs; qualifying examples copied, not inferred from reasoning.
examples=['F03_S00','F03_S01','F04_S02']
trigger=[]
for sid in examples:
 r=rd(N/'development/calls'/f'B2__{sid}.result.json');assert r['final_valid_JSON'];trigger.append({'state_id':sid,'output':r['output'],'result_sha256':sha(N/'development/calls'/f'B2__{sid}.result.json')})
save(N/'B3_TRIGGER.json',{'rule':'SETTINGS.json B3_trigger','examples':trigger,'reason':'Birth+academy+profession or jersey+academy+profession; page count+publisher+date. Each bundles independently investigable attributes across at least2qids.','stage2_uses_all_stage1_outputs':'No semantic selection or repairs.'})
inputs=rd(N/'development/INPUTS.json');D=N/'b3_issue';jobs=[]
for sid,b in inputs.items():
 view={'Original Question':b['question'],'Verified Claims':b['claims'],'Working Hypothesis':b['hypothesis']}
 req={'model':C['model'],'messages':[{'role':'system','content':prompts[0]},{'role':'user','content':json.dumps(view,ensure_ascii=False)}],'stream':False,'temperature':0,'response_format':C['response_format']}
 jobs.append({'id':'B3A__'+sid,'arm':'B3A','input_id':sid,'belief_sha256':dg(b),'request':req})
save(D/'INPUTS.json',inputs);save(D/'JOBS.json',jobs);save(D/'PLAN.json',{'preflight':['B3A__F01_S00','B3A__F03_S06','B3A__F04_S02'],'semantic_filter':False,'failure_policy':'No retries. Failed issue yields no stage2 request and remains ITT failure.'})
files=list(D.glob('*.json'))+[N/'B3_TRIGGER.json',N/'prompts/B3A.txt',N/'prompts/B3B.txt',N/'run_issue.py',P/'transport.py',N/'SETTINGS.json',N/'development/INPUTS.json']
save(D/'FREEZE.json',{'head_before_freeze':head(),'files':{str(f.relative_to(ROOT)):sha(f) for f in files}})
