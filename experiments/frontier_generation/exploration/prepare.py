import sys,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
BASE=TOP/'exploration'
assert not (BASE/'freeze.json').exists()
r=rd(TOP/'f1_state_sufficiency/reviewed_outputs.json')
assert not rd(TOP/'f1_state_sufficiency/summary.json')['gate']['pass']
old={x['id']:x for x in rd(TOP/'f1_state_sufficiency/requests.json')}
cases=sorted({x['case_id'] for x in r if x['over_broad']})[:12]
selection=[];items=[]
for i,c in enumerate(cases,1):
    a=next(a for a in ['S','H','SH'] if any(x['case_id']==c and x['arm']==a and x['over_broad'] for x in r))
    parent=old[f'{c}_{a}_1'];selection.append({'case_id':c,'qid':parent['qid'],'source_arm':a,'parent_id':parent['id'],'parent_request_sha256':parent['request_sha256']})
    for cond in ['A0','A1']:
        x=copy.deepcopy(parent);x.update(id=f'X{i:02}_{cond}',arm=cond,replicate=1,source_arm=a,parent_id=parent['id'])
        if cond=='A1':x['request']['messages'][0]['content']+='\nChoose the smallest currently useful unresolved research question.\n'
        x['request_sha256']=dg(x['request']);items.append(x)
items.sort(key=lambda x:dg(['frontier-exploration-A-order',x['id']]))
assert len(items)==18 and len(cases)==9
wr(BASE/'selection.json',selection);wr(BASE/'requests.json',items)
paths=[TOP/'EXPLORATION_PLAN.md',TOP/'runtime.py',TOP/'schemas/frontier.json',TOP/'prompts/frontier.md',TOP/'analysis/RUBRIC.md',TOP/'bank/COVERAGE.json',TOP/'bank/REQUIREMENT_MAP.json',TOP/'f1_state_sufficiency/semantic_review.json',TOP/'f1_state_sufficiency/summary.json',TOP/'f1_state_sufficiency/reviewed_outputs.json',TOP/'f1_state_sufficiency/requests.json',ROOT/'experiments/model_backend_deepseek/provider.json']+list(BASE.glob('*.py'))+[BASE/'selection.json',BASE/'requests.json']
wr(BASE/'freeze.json',{'created_utc':now(),'construction_head':head(),'exploration':'A only; one appended sentence; failure-conditioned9checkpoints',
    'provider':CONFIG,'sample_count':18,'horizon':1,'tool_calls':0,'max_retries':0,'workers':4,'timeout_seconds':240,
    'failure_policy':'All18planned slots count; no retries or replacements; same auth latch and raw journal as F1.',
    'file_hashes':{str(p.relative_to(ROOT)):sha(p) for p in paths},'request_hashes':{x['id']:x['request_sha256'] for x in items}})
print('Frozen',len(items),'calls',selection)
