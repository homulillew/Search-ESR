"""Final read-only audit of historical bytes, freezes, request isolation and reviews."""
import json,hashlib,subprocess,sys,collections
from pathlib import Path
T=Path(__file__).resolve().parents[1];sys.path.insert(0,str(T))
from runtime import ROOT,rd,wr,dg,sha,view,decode
from cache import progress_key

def main():
 historical=rd(T/'historical_hashes.json');changed=[p for p,h in historical.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h];assert not changed,changed
 names=subprocess.check_output(['git','diff','--name-only','094b87382668fa21e68290eed3050d5f8e5f979a','HEAD'],cwd=ROOT,text=True).splitlines();assert all(p.startswith('experiments/asymmetric_progress/') for p in names)
 bank={c['case_id']:c for b in ['PRIMARY','CHALLENGE'] for c in rd(T/f'bank/{b}.json')};reviews=rd(T/'analysis/semantic_review.json');maps=rd(T/'analysis/review_map.json')
 keys=[progress_key(c['question'],c['state']['verified_claims']) for c in rd(T/'bank/PRIMARY.json')];old=set(rd(T/'bank/EXPOSURE_AUDIT.json')['excluded_keys']);assert len(set(keys))==24 and not(set(keys)&old)
 inv={c['checkpoint_id']:c for c in rd(ROOT/'experiments/frontier_generation/bank/CHECKPOINT_INVENTORY.json')}
 for c in rd(T/'bank/PRIMARY.json'):assert c['state']['verified_claims']==inv[c['checkpoint_id']]['state']['verified_claims'] and c['question']==inv[c['checkpoint_id']]['question']
 for c in rd(T/'bank/CHALLENGE.json'):
  src=next(x for x in rd(ROOT/f"experiments/dynamic_progress/bank/{c['prior_bank']}.json") if x['case_id']==c['prior_case_id'])
  assert c['state']['verified_claims']==src['state']['verified_claims'] and c['question']==src['question']
 stages={};allrows=[]
 for stage in ['canary','primary','challenge','exploration']:
  f=rd(T/stage/'freeze.json')
  for p,h in f['file_hashes'].items():assert sha(ROOT/p)==h,p
  reqs=rd(T/stage/'requests.json');rows=rd(T/stage/(stage+'_outputs.json'));events=[json.loads(l) for l in (T/stage/(stage+'_events.jsonl')).read_text().splitlines()]
  starts=[e for e in events if e['kind']=='request_started'];ends=[e for e in events if e['kind']=='completed'];assert len(reqs)==len(rows)==len(starts)==len(ends)==f['sample_count'];assert len({r['id'] for r in rows})==len(rows)
  by={i['id']:i for i in reqs};heads=set()
  for e in starts:
   it=e['item'];assert it==by[it['id']] and it['request_sha256']==dg(it['request']);heads.add(e['run_head'])
   req=it['request'];assert set(req)=={'model','messages','stream','response_format'} and req['model']=='deepseek-flash'
   assert req['response_format']=={'type':'json_object'} and 'json' in req['messages'][0]['content'].lower()
   if stage!='canary':assert json.loads(req['messages'][1]['content'])==view(bank[it['case_id']])
   expected=(T/'exploration/prompt.md').read_text() if stage=='exploration' else (T/f"prompts/{it['arm']}.md").read_text() if stage!='canary' else None
   if expected is not None:assert req['messages'][0]['content']==expected
  for e in ends:
   r=e['result'];assert r==next(x for x in rows if x['id']==r['id'])
   if r['output']:assert decode(e['event']['response'],by[r['id']])==r['output']
  for h in heads:
   # All hashed inputs, including stage manifest, were in the actual executing commit.
   for p,expected_hash in f['file_hashes'].items():
    data=subprocess.check_output(['git','show',h+':'+p],cwd=ROOT);assert hashlib.sha256(data).hexdigest()==expected_hash
   assert subprocess.check_output(['git','show',h+':'+str((T/stage/'freeze.json').relative_to(ROOT))],cwd=ROOT)==(T/stage/'freeze.json').read_bytes()
  if stage!='canary':
   stage_map={v['id']:k for k,v in maps.items() if v['stage']==stage};assert set(stage_map)==set(by)
   for r in rows:assert stage_map[r['id']] in reviews
  stages[stage]={'submissions':len(rows),'run_heads':sorted(heads),'valid_outputs':sum(r['output'] is not None for r in rows),'failures':[r['id'] for r in rows if r['error']],'retries':0};allrows+=rows
 assert sum(x['submissions'] for x in stages.values())==223
 wr(T/'analysis/INTEGRITY.json',{'passed':True,'historical_files_checked':len(historical),'historical_changes':changed,'primary_fresh_unique_keys':24,'claims_mutated':False,'all_requests_committed_before_submission':True,'no_history_labels_or_light_output_in_model_input':True,'all_noncanary_outputs_reviewed':True,'stages':stages,'production_controller_modified':False,'frontier_calls':0})
 print('integrity passed:',len(historical),'historical files; 223 one-attempt submissions')
if __name__=='__main__':main()
