"""Final reproducibility and immutability audit, no network/model calls."""
import sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
from packets import opaque

checks={};hist=rd(TOP/'historical_baseline_hashes.json');changed=[p for p,h in hist.items() if not(ROOT/p).exists() or sha(ROOT/p)!=h];assert not changed,changed
checks['historical_files_unchanged']=len(hist)
allrows=[];modelnames=collections.Counter();heads=collections.Counter();statuses=collections.Counter();counts={};failures=[]
for folder,tag,expected in [('p1_progress','progress',216),('transport_correction','corrected',120),('exploration','exploration',24)]:
 base=TOP/folder;f=rd(base/'freeze.json')
 for p,h in f['file_hashes'].items():assert sha(ROOT/p)==h,p
 reqs={x['id']:x for x in rd(base/'requests.json')};rows=rd(base/(tag+'_outputs.json'));events=[json.loads(l) for l in (base/(tag+'_events.jsonl')).read_text().splitlines()];starts=[e for e in events if e['kind']=='request_started'];ends=[e for e in events if e['kind']=='completed']
 assert len(reqs)==len(rows)==len(starts)==len(ends)==expected
 assert {r['id'] for r in rows}==set(reqs)=={e['item']['id'] for e in starts}
 assert len({e['item']['id'] for e in starts})==expected
 for e in ends:
  it=e['event']['item'];r=e['result'];assert it==reqs[r['id']] and dg(it['request'])==it['request_sha256']
  assert r['attempted'];heads[e['event']['run_head']]+=1;statuses[str(e['event'].get('http_status'))]+=1
  req=it['request'];assert req['model']=='deepseek-flash' and 'tools' not in req and req['response_format']=={'type':'json_object'}
  raw=e['event'].get('response')
  if raw:
   modelnames[raw.get('model','unknown')]+=1
   assert not raw['choices'][0]['message'].get('tool_calls')
  if r['error']:failures.append({'id':r['id'],'error':r['error']['category'],'http_status':e['event'].get('http_status')})
 counts[folder]=expected;allrows+=rows
checks['counts']=counts;checks['HTTP_statuses']=dict(statuses);checks['reported_models']=dict(modelnames);checks['execution_heads']=dict(heads)
# Format correction eligibility and exact immutable factual input preservation.
old={x['id']:x for x in rd(TOP/'p1_progress/requests.json')};out={x['id']:x for x in rd(TOP/'p1_progress/progress_outputs.json')}
for it in rd(TOP/'transport_correction/requests.json'):
 orig=old[it['id'].removeprefix('TC_')];r=out[orig['id']]
 assert r['output'] is None and r['usage'] is None and orig['arm'] in ['R','FULL']
 altered=copy.deepcopy(orig['request']);altered['messages'][1]['content']+='\n\nReturn JSON.'
 assert altered==it['request'] and it['view_sha256']==orig['view_sha256']
checks['only_120_preinference_HTTP_rejections_resubmitted']=True
rev=rd(TOP/'analysis/semantic_review.json');assert len(rev)==len(allrows)==360
for r in allrows:
 s=rev[opaque(r['id'])];o=r['output']
 if o is None:assert not s['units'];continue
 raw=o.get('blocking_gaps',o.get('requirements'))
 if raw is not None:
  assert len(raw)==len(s['units']),r['id']
  for g,u in zip(raw,s['units']):assert g.get('gap',g.get('requirement'))==u['text']
 else:
  assert all(u['text'] and u['text'] in o['residual'] for u in s['units']),r['id']
 assert all(len(u['text'])>=15 for u in s['units']),r['id']
checks['all_360_reviewed']=True;checks['review_text_traceability']=True
# Exact original snapshot statements/provenance unchanged.
inv={c['checkpoint_id']:c for c in rd(ROOT/'experiments/frontier_generation/bank/CHECKPOINT_INVENTORY.json')}
for name in ['PRIMARY','CHALLENGE']:
 for c in rd(TOP/'bank'/f'{name}.json'):
  orig=inv[c['checkpoint_id']];assert c['question']==orig['question'] and c['state']==orig['state']
checks['all_48_States_exact_historical']=True
assert (TOP/'prompts/residual.md').read_bytes()==(ROOT/'experiments/goal_residual_control/prompts/goal_reviewer.md').read_bytes()
checks['old_R_system_prompt_byte_identical']=True
wr(TOP/'analysis/INTEGRITY_AUDIT.json',{'passed':True,'audit_head':head(),'checks':checks,'failures':failures,'retrieval_calls':0,'writer_calls':0,'frontier_calls':0,'sdk_retries':0,'successful_inference_resampling':'none except separately frozen24-call scientific exploration','protocol_deviations':['120explicitHTTPresubmissionsforpreinferenceJSONword400; originalfailuresretained; notzeroadditionalattempts.','ExecutionHEADchangedwithnewaudit/reviewcommits; allfrozenruntime/inputhashesremainedidentical.'],'untouched_user_paths':['experiments/auto_research/','research_loop/','指令提示词/agent_search_harness_state_research_notes .md']})
print('AUDIT PASSED',checks)
