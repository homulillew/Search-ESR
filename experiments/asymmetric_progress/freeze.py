"""Prepare frozen requests before calls. Never overwrite a completed freeze."""
import sys,hashlib,subprocess
from runtime import TOP,ROOT,rd,wr,item,sha,head,now

def main(stage):
 base=TOP/stage
 assert not (base/'freeze.json').exists()
 if stage=='canary':
  c={'case_id':'CANARY','qid':'dummy','set':'canary','question':'Return the supplied dummy label as established. This is a serialization check, not a research case.','state':{'verified_claims':[{'statement':'The dummy label is K.'}]}}
  # Exactly one dummy provider request, exercising JSON mode and the new Audit schema.
  reqs=[item(c,'Audit',1,prompt='This is a mechanical JSON serialization check. Return exactly {"confirmed":true,"blocking_gap":null,"closure_support":[{"relation":"dummy label","claim_refs":[1]}]}.')]
 else:
  assert stage in ['primary','challenge']
  reqs=[item(c,a,r) for c in rd(TOP/f'bank/{stage.upper()}.json') for a in ['L0','L1','Audit'] for r in [1,2]]
  reqs.sort(key=lambda x:hashlib.sha256(x['id'].encode()).hexdigest())
 wr(base/'requests.json',reqs)
 files=[p for p in TOP.rglob('*') if p.is_file() and '__pycache__' not in str(p) and p.name not in ['freeze.json'] and not p.name.endswith('_events.jsonl') and not p.name.endswith('_outputs.json') and '/.git/' not in str(p)]
 files += [ROOT/'experiments/model_backend_deepseek/provider.json',ROOT/'experiments/dynamic_progress/prompts/blocker.md']
 f={'prepared_utc':now(),'preparation_head':head(),'base_remote_head':'094b87382668fa21e68290eed3050d5f8e5f979a','stage':stage,'provider':'DeepSeek','model':'deepseek-flash','transport':'JSON object, provider defaults, no tools, no seed/temperature/max-token overrides','max_retries':0,'timeout_seconds_per_http_operation':240,'workers':4,'horizon':1,'sample_count':len(reqs),'file_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted(files)},'failure_policy':'One attempt only. Keep raw failures; no repair/resample. Failure gets no semantic/closure credit and cannot authorize STOP. Auth failure latches remaining requests.','run_head_policy':'Commit this manifest and every hashed input before running; exact executing HEAD is logged for every request.'}
 wr(base/'freeze.json',f)
 print(stage,len(reqs),'prepared; commit before run')
if __name__=='__main__':main(sys.argv[1])
