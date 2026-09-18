from pathlib import Path
import hashlib,json,shutil
from experiments.query_initialization.single_entry.source_units import model_input
root=Path('/data/WSH/Search-ESR')
base=root/'experiments/query_initialization/single_entry/runs'
for rid in ['20260918T072122.779614Z','20260918T072839.341275Z']:
 p=base/rid;m=json.loads((p/'manifest.json').read_text());source_checks={n:hashlib.sha256((p/'source'/n).read_bytes()).hexdigest()==d for n,d in m['source_sha256'].items()};assert all(source_checks.values())
 request_count=0;index=[]
 for folder in sorted(p.glob('qid_*')):
  h=json.loads((folder/'handoff.json').read_text());s=json.loads((folder/'summary.json').read_text());events=[json.loads(x) for x in (folder/'events.jsonl').read_text().splitlines()]
  reqs=[e['request'] for e in events if e['kind']=='api_request'];assert len(reqs)==1
  for req in reqs:
   assert req['messages'][0]['content']==(p/f"prompt_{s['arm']}.txt").read_text()
   assert json.loads(req['messages'][1]['content'])==model_input(h['question'])
   assert set(json.loads(req['messages'][1]['content']))=={'question','question_units','requested_directions'}
   assert 'tools' not in req and req['extra_body']=={'enable_thinking':False}
   assert req['model']==m['model'] and req['max_tokens']==1536
  request_count+=len(reqs)
  index.append(dict(session=folder.name,qid=s['qid'],arm=s['arm'],repeat=s['repeat'],trajectory=f'{folder.name}/trajectory.md',raw_events=f'{folder.name}/events.jsonl',handoff=f'{folder.name}/handoff.json'))
 assert len(index)==len(json.loads((p/'schedule.json').read_text()))
 probes=json.loads((p/'handoff_verification.json').read_text())['probes'];assert len(probes)==len(index)
 lock_checks={}
 if (p/'evaluation_lock.json').exists():
  lock=json.loads((p/'evaluation_lock.json').read_text())
  lock_checks={n:hashlib.sha256((root/n).read_bytes()).hexdigest()==d for n,d in lock['source_sha256'].items()};assert all(lock_checks.values())
  assert set(lock['qids']).isdisjoint(lock['excluded_qids'])
 result=dict(snapshot_checks=source_checks,lock_checks=lock_checks,actual_api_requests=request_count,initial_payloads_equal_original_question_and_units=True,all_requests_match_saved_prompt=True,enable_thinking=False,websearch=False,per_session_requests=1,restored_open_probes=len(probes),all_passed=True)
 (p/'archive_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 (p/'trajectory_index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2))
 print(rid,request_count,len(probes),'verified')
