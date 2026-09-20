"""Offline integrity checks only; never calls API, tools, or reads credentials."""
import json,pathlib,hashlib,datetime,collections,sys
ROOT=pathlib.Path(__file__).resolve().parents[6];sys.path.insert(0,str(ROOT))
from experiments.research_state.need_review.run import load_prepared,build_plan,load_prompts,summarize
from experiments.research_state.need_review.integrity import verify_plan,read_events
from experiments.research_state.need_review.audit import verify_branch_requests
r=pathlib.Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
m=read(r/'manifest.json');plan=read(r/'preflight/approved_plan.json');verify_plan(plan,m['approved_plan']); assert plan['plan_sha256']==m['plan_sha256'];assert m['git_head']=='6319c64cbff6995a879ed4fb8ceca095ec8d1b2a';assert m['plan_approved']
for p,h in m['source_sha256'].items():assert hashlib.sha256((r/'source'/p).read_bytes()).hexdigest()==h
prompts={k:(r/'prompts'/f'{k}.txt').read_text() for k in m['prompt_sha256']}
for k,v in prompts.items():assert hashlib.sha256(v.encode()).hexdigest()==m['prompt_sha256'][k]
rows=[];pairs=collections.defaultdict(dict);times=[]
for item in m['schedule']:
 b=r/'branches'/item['sample_id'];d=read(b/'result.json');c=read(r/'checkpoints'/f"{item['checkpoint_id']}.json");events,errors=read_events(b/'events.jsonl');assert not errors;assert not verify_branch_requests(c,d,item,m['settings'],prompts,events)
 assert d['actor']['request']['messages'][:len(c['request']['messages'])]==c['request']['messages'];a=dict(d['actor']['request']);a.pop('messages');orig=dict(c['request']);orig.pop('messages');orig['model']='Atria-Dawn-Preview';assert a==orig
 if not d['memo_injected']:
  expected=dict(c['request'],model='Atria-Dawn-Preview');assert d['actor']['request']==expected
 for stage in ['review','actor']:
  request=d[stage]['request'];resp=d[stage]['response'];assert request['model']=='Atria-Dawn-Preview';assert request['extra_body']=={'enable_thinking':False};assert resp
  u=resp['usage'];assert all(type(u[k]) is int and u[k]>=0 for k in ['prompt_tokens','completion_tokens','total_tokens']);assert u['prompt_tokens']+u['completion_tokens']==u['total_tokens']
  if stage=='review':assert not request.get('tools');assert request.get('max_tokens',request.get('max_completion_tokens'))==512
 pairs[(item['checkpoint_id'],item['repeat_id'])][item['review_contract']]=d['review']['request']
 times.extend(e['time'] for e in events)
 rows.append({'sample_id':item['sample_id'],'review_status':d['review']['status'],'review_finish_reason':d['review']['response']['choices'][0]['finish_reason'],'review_errors':d['review']['errors'],'memo_injected':d['memo_injected'],'actor_kind':d['actor']['classification']['response_kind'],'reported_tokens':sum(d[s]['usage']['total_tokens'] for s in ['review','actor']),'elapsed_seconds':sum(d[s]['elapsed_seconds'] for s in ['review','actor'])})
for p in pairs.values():
 a=p['baseline'];b=p['source_grounded_v1'];assert a['messages'][1:]==b['messages'][1:];assert {k:v for k,v in a.items() if k!='messages'}=={k:v for k,v in b.items() if k!='messages'}
s=summarize(r,m['schedule'],write_output=False);assert s==read(r/'summary.json');assert s['logical_requests_attempted']==s['responses_received']==24;assert s['tool_executions']==0
v=r/'review';first=[json.loads(x) for x in (v/'annotations_first_pass.jsonl').read_text().splitlines()];final=[json.loads(x) for x in (v/'annotations_final.jsonl').read_text().splitlines()];assert len(first)==len(final)==12
assert hashlib.sha256((v/'annotations_first_pass.jsonl').read_bytes()).hexdigest()==read(v/'first_pass_attestation.json')['annotations_sha256']
assert hashlib.sha256((v/'reviewer_first_pass.jsonl').read_bytes()).hexdigest()==read(v/'reviewer_first_pass_attestation.json')['sha256']
assert hashlib.sha256((v/'prefix_assessment.jsonl').read_bytes()).hexdigest()==read(v/'prefix_attestation.json')['prefix_assessment_sha256']
rubric=read(v/'rubric.json')['labels']
for a,b in zip(first,final):
 assert a['card_id']==b['card_id'];refs={x['ref'] for x in b['reference_index']}
 for k,x in b['labels'].items():
  assert x in rubric[k]['allowed_values'];assert set(b['label_evidence'][k]['supporting_refs'])<=refs
  if k!='regression':assert a['labels'][k]==x;assert a['label_evidence'][k]==b['label_evidence'][k]
 if not b['execution_status']['memo_injected']:assert b['labels']['action_responds_to_need']=='not_applicable'
 assert not b['execution_status']['export_errors']
assert datetime.datetime.fromisoformat(read(r/'preflight/preflight.json')['created_at'])<datetime.datetime.fromisoformat(min(times))
for p in r.rglob('*'):
 if p.is_file():
  assert p.name!='.env';assert p.suffix not in ['.safetensors','.parquet','.sqlite']
  # Split literals avoid self-matching this source file.
  raw=p.read_bytes();assert b'github_'+b'pat_' not in raw;assert b'sk-'+b'ws-' not in raw;assert b'atr'+b'_' not in raw
out={'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'plan_sha256':plan['plan_sha256'],'source_and_prompt_hashes_match':True,'request_and_event_audit_errors':0,'paired_requests_only_reviewer_system_differs':True,'actor_prefix_and_settings_unchanged':True,'invalid_review_fallback_exact':True,'all_12_annotations_complete':True,'first_pass_hashes_match':True,'post_unmask_only_regression_changed':True,'credential_pattern_scan':'passed','cost_accounting_complete':s['cost_accounting_complete'],'unknown_cost_requests':s['failed_requests_with_unknown_cost'],'responses_missing_usage':s['responses_missing_usage'],'responses_inconsistent_usage':s['responses_inconsistent_usage'],'missing_usage_fields_by_stage':s['missing_usage_fields_by_stage'],'first_event':min(times),'last_event':max(times),'event_span_seconds':(datetime.datetime.fromisoformat(max(times))-datetime.datetime.fromisoformat(min(times))).total_seconds(),'branches':rows}
(r/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
# Batch-specific reasoning-cap and fallback mediation checks.
reasoning_rows=[]
for item in m['schedule']:
 d=read(r/'branches'/item['sample_id']/'result.json');rv=d['review'];act=d['actor']
 assert rv['response']['choices'][0]['finish_reason']=='length' and rv['raw_text'] is None
 assert rv['usage']['completion_tokens']==512 and rv['usage']['completion_tokens_details']['reasoning_tokens']==512
 reasoning_rows.append({'sample_id':item['sample_id'],'review_reasoning_tokens':rv['usage']['completion_tokens_details']['reasoning_tokens'],'actor_reasoning_tokens':act['usage']['completion_tokens_details']['reasoning_tokens'],'review_content_absent':True,'actor_content_absent':not act['response']['choices'][0]['message'].get('content'),'review_errors':rv['errors']})
for checkpoint_id in {i['checkpoint_id'] for i in m['schedule']}:
 for repeat_id in [1,2]:
  ds=[read(r/'branches'/f'{checkpoint_id}__C__r{repeat_id}__{contract}'/'result.json') for contract in ['baseline','source_grounded_v1']]
  assert ds[0]['actor']['request']==ds[1]['actor']['request']
(r/'reasoning_diagnostics.json').write_text(json.dumps({'source':'provider-reported completion_tokens_details.reasoning_tokens; no missing counters imputed','all_12_reviews_reasoning_only_512_length':True,'all_six_actor_request_pairs_identical':True,'rows':reasoning_rows},indent=2)+'\n')
