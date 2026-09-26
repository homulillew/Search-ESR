import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
base=TOP/'exploration';assert not (base/'freeze.json').exists()
rows=rd(TOP/'analysis/reviewed_outputs.json');b=[r for r in rows if r['arm']=='B' and r['set']=='fresh_primary']
assert len(b)==48 and all(r['review'] for r in b)
ids=sorted({r['case_id'] for r in b if r['gold_resolved'] or any('over_broad' in u['errors'] for u in r['units'])});assert len(ids)==12
wr(base/'baseline.json',[r for r in b if r['case_id'] in ids])
prompt=(TOP/'prompts/blocker.md').read_text()+'''\nEach blocking gap must describe one missing or conflicting relation. Do not combine several independent conditions into a whole-question or whole-profile bundle. A gap may include the scope or endpoint binding necessary for that one relation. You do not need to fill all three gap slots or cover every clue; a single material blocker is sufficient to explain why research is unresolved.\n'''
(base/'prompt.md').write_text(prompt)
items=[]
for c in rd(TOP/'bank/PRIMARY.json'):
 if c['case_id'] not in ids:continue
 for rep in [1,2]:
  it=item(c,'B',rep,prompt);it['id']='EX_'+it['id'];items.append(it)
items.sort(key=lambda x:dg(['dynamic-progress-one-relation',x['id']]))
wr(base/'requests.json',items)
files=[base/'EXPLORATION_PLAN.md',base/'freeze_exploration.py',base/'run.py',base/'baseline.json',base/'prompt.md',base/'requests.json',TOP/'runtime.py',TOP/'analysis/RUBRIC.md',TOP/'bank/PRIMARY_LABELS.json']
wr(base/'freeze.json',{'created_utc':now(),'construction_head':head(),'case_ids':ids,'sample_count':24,'qid_count':len({i['qid'] for i in items}),'provider':CONFIG,'workers':4,'max_retries':0,'best_of':0,'timeout_seconds':240,'horizon':1,'tool_calls':0,'primary_override':False,'file_hashes':{str(p.relative_to(ROOT)):sha(p) for p in files},'request_hashes':{i['id']:i['request_sha256'] for i in items}})
print('Frozen exploration',ids)
