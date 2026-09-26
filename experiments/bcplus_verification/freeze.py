"""Offline reproducibility checks; never calls provider or retriever."""
import json,hashlib,subprocess,sys,os
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
sys.path.insert(0,str(ROOT))
from experiments.bcplus_verification.runtime import schema,validate_object
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(ROOT/'experiments/deferred_recovery/freeze.json');bins={}
for path,v in old['binary_files'].items():
 p=Path(path);st=p.stat();assert(st.st_size,st.st_mtime_ns)==(v['size'],v['mtime_ns']),path
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 assert h.hexdigest()==v['sha256'],path;bins[path]=v
 print('verified binary',p.name,flush=True)
files={str(p.relative_to(ROOT)):sha(p) for p in P.rglob('*') if p.is_file() and '__pycache__' not in str(p) and p.name not in ['freeze.json','HISTORICAL_HASHES.json']}
for path in old['files']:
 if path.startswith(('llm_chat/','BCPlus/','experiments/model_backend_deepseek/')) or path in ['experiments/goal_residual_control_v3/capability.py','experiments/goal_residual_control/harness_v2/contracts.py']:
  p=ROOT/path;files[path]=sha(p);assert files[path]==old['files'][path],path
for path in ['experiments/deferred_recovery/tools.py','experiments/goal_residual_control_v3_1/prompts/state_updater_gap_conditioned.md','experiments/goal_residual_control/harness_v2/UPDATER_RESPONSE_SCHEMA.json']:
 files[path]=sha(ROOT/path)
for pre in read(P/'bank/INITIAL_CHECKPOINTS.json').values():assert sha(ROOT/pre['source_path'])==pre['source_sha256'];files[pre['source_path']]=pre['source_sha256']
assert (P/'prompts/writer.md').read_bytes()==(ROOT/'experiments/goal_residual_control_v3_1/prompts/state_updater_gap_conditioned.md').read_bytes()
# Real archived responses exercise the unchanged parser/contract, no synthetic mirror tests.
arch=read(ROOT/'experiments/deferred_recovery/r1/actor_outputs.json');n=0
for a in arch:
 if a['output'] is not None:
  from jsonschema import Draft202012Validator
  Draft202012Validator(schema('actor_H')).validate(a['output']);n+=1
reqs=read(P/'INITIAL_REQUESTS.json');assert len(reqs)==39
for r in reqs:
 assert r['request_sha256']==hashlib.sha256(json.dumps(r['request'],ensure_ascii=False,sort_keys=True).encode()).hexdigest()
 v=json.loads(r['request']['messages'][1]['content']);assert v['Current Claims']==[] and v['Historical Document Catalog']==[] and v['New Observations']==[]
 assert not any(k in v for k in ['gold_relation_status','constraint_id','reference_evidence'])
 if r['arm']=='D':assert 'Candidate' not in v and v['Working Hypothesis'] is None
config=read(ROOT/'experiments/model_backend_deepseek/provider.json')
f={'git_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'utc':datetime.now(timezone.utc).isoformat(),'remote_base':'453161c2d2335416d4f439f9419e85c2266658b5','model':config['model'],'base_url':config['base_url'],'max_retries':0,'timeout_seconds':240,'workers':4,'transport':'json_mode_fallback','sampling':'provider defaults; no override','sample_counts':{'V+':18,'V-':11,'Discovery':10},'horizon':{'V':2,'D':3},'actions_per_decision':1,'max_api_calls':528,'device':'cuda:1','k':5,'files':files,'binary_files':bins,'initial_request_hashes':{x['case_id']:x['request_sha256'] for x in reqs},'offline_checks':{'archived_actor_contract_checks':n,'initial_runtime_boundary_checks':len(reqs),'historical_binaries_unchanged':True}}
(P/'freeze.json').write_text(json.dumps(f,ensure_ascii=False,indent=2)+'\n');print('FREEZE COMPLETE',len(files),len(bins),flush=True)
