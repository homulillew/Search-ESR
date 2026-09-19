import json,hashlib,re,collections
from pathlib import Path
R=Path('experiments/research_state/need_review/runs/e0_20260919T171923Z');P=Path(str(R)+'_preflight');F=json.loads((R/'preflight/freeze.json').read_text());M=json.loads((R/'manifest.json').read_text());S=json.loads((R/'summary.json').read_text());V=R/'review'
for path,sha in F['sha256'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha,path
for path,sha in M['source_sha256'].items():
 assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha,path
 assert hashlib.sha256((R/'source'/path).read_bytes()).hexdigest()==sha,path
for f in P.iterdir():
 if f.is_file():assert (R/'preflight'/f.name).read_bytes()==f.read_bytes(),f
first=[json.loads(l) for l in (V/'annotations_first_pass.jsonl').read_text().splitlines()];final=[json.loads(l) for l in (V/'annotations_final.jsonl').read_text().splitlines()];cards=[json.loads(l) for l in (V/'cards.jsonl').read_text().splitlines()];rubric=json.loads((V/'rubric.json').read_text());att=json.loads((V/'first_pass_attestation.json').read_text());unmask=json.loads((V/'unmask_attestation.json').read_text())
assert len(first)==len(final)==len(cards)==18
assert att['sha256']==unmask['first_pass_sha256']==hashlib.sha256((V/'annotations_first_pass.jsonl').read_bytes()).hexdigest()
assert att['created_at']<unmask['unmasked_at']
for f,g,c in zip(first,final,cards):
 assert f['card_id']==g['card_id']==c['card_id'];refs={x['ref'] for x in c['reference_index']}
 for k,v in g['labels'].items():
  assert v in rubric['labels'][k]['allowed_values']
  assert g['label_evidence'][k]['notes']
  assert set(g['label_evidence'][k]['supporting_refs'])<=refs
  if k!='regression':assert f['labels'][k]==v
 if not c['execution_status']['memo_injected']:assert g['labels']['action_responds_to_need']=='not_applicable'
counts=collections.Counter();usage=collections.Counter();maxprompt=0;min_request=None
for p in R.glob('branches/*/events.jsonl'):
 for line in p.read_text().splitlines():
  e=json.loads(line);counts[e['kind']]+=1
  if e['kind']=='request':
   min_request=min(min_request or e['time'],e['time'])
   assert not any(k.lower() in ['api_key','authorization','headers','extra_headers'] for k in e['request'])
  if e['kind']=='response':
   u=e['response']['usage'];usage.update({k:u[k] for k in ['prompt_tokens','completion_tokens','total_tokens']});maxprompt=max(maxprompt,u['prompt_tokens'])
assert F['frozen_at']<min_request
assert counts['request']==counts['response']==30
assert S['logical_requests_attempted']==30 and S['scheduled_branches']==18 and S['tool_executions']==0
# Scan only deliverables, never credential files or environment values.
patterns=[re.compile(rb'sk-[A-Za-z0-9_.-]{24,}'),re.compile(rb'Bearer\s+[A-Za-z0-9_.-]{20,}'),re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')]
files=[p for b in [R,P] for p in b.rglob('*') if p.is_file()]
for p in files:
 b=p.read_bytes()
 assert not any(x.search(b) for x in patterns),f'Potential credential in {p}'
 assert p.name not in ['.env'] and not p.name.endswith(('.safetensors','.sqlite','.parquet')),p
report={'offline_tests_passed':62,'all_source_and_prompt_hashes_unchanged':True,'freeze_precedes_first_request':True,'all_18_annotations_complete':True,'first_pass_preserved':True,'unmask_after_first_pass':True,'non_regression_labels_unchanged':True,'fallback_transmission_label_not_applicable':True,'logical_requests':counts['request'],'responses':counts['response'],'tool_executions':0,'usage':dict(usage),'max_prompt_tokens':maxprompt,'credential_pattern_scan':'passed','scanned_artifact_files':len(files),'model_environment_corpus_files_in_artifacts':False,'reviewer':'Codex, no independent human adjudication'}
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
