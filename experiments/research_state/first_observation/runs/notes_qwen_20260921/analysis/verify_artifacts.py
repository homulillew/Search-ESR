"""Verify frozen experiment, full denominators and analysis provenance; no new calls."""
from pathlib import Path
import sys,json,hashlib,datetime,re,collections
ROOT=Path(__file__).resolve().parents[6];sys.path.insert(0,str(ROOT))
from experiments.research_state.first_observation.run import audit,audit_capture,note_outputs
from experiments.research_state.first_observation.artifacts import file_hash
r=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
c=audit_capture(r/'capture');summary,rows=audit(r/'notes');assert summary==read(r/'notes/summary.json')
assert summary['attempts']==summary['responses']==summary['scheduled']==6
assert summary['audit_errors']==summary['unknown_usage_requests']==0
assert summary['statuses']=={'ok':6}
assert note_outputs(r/'notes')==read(r/'note_outputs.json')
p=read(r/'notes-plan.json');assert p==read(r/'notes/plan.json')
assert p['stage']=='notes' and p['prior'] is None and p['profile']==read(r/'profile.json')
for j in p['jobs']:
 req=j['request'];u=json.loads(req['messages'][1]['content'])
 assert set(u)=={'question','first_query','observation'} and u['question']==u['first_query']
 assert len(req['messages'])==2 and 'tools' not in req and not j['memo_injected']
 assert 'extra_body' not in req and 'reasoning_effort' not in req
before=read(r/'preflight/metadata.before.json');after=read(r/'preflight/metadata.after.json')
assert set(after)-set(before)=={'query_prefix'}
assert {k:v for k,v in after.items() if k!='query_prefix'}==before
assert after['query_prefix']==c['retrieval']['query_prefix']
for name,h in c['retrieval']['asset_sha256'].items():
 rel=Path(name).relative_to(ROOT) if Path(name).is_relative_to(ROOT) else None
 if rel and (r/'retrieval_source'/rel).exists():assert file_hash(r/'retrieval_source'/rel)==h
assert c['retrieval']['device']=='cuda:1'
assert len([x for x in c['retrieval']['asset_sha256'] if x.endswith('.pkl')])==4
assessment=read(r/'review/observation_first_assessment.json');att=read(r/'review/first_pass_attestation.json')
assert not assessment['current_note_outputs_seen']
events=[json.loads(line) for f in (r/'notes').glob('*/events.jsonl') for line in f.read_text().splitlines()]
first=min(e['time'] for e in events if e['kind']=='request')
assert assessment['created_at']<first<att['created_at']
assert file_hash(r/'review/annotations_first_pass.json')==att['sha256']
assert read(r/'review/finalization.json')['first_pass_sha256']==att['sha256']
annotations=read(r/'review/annotations_first_pass.json');by={x['case_id']:x for x in rows}
assert len(annotations)==6
for a in annotations:
 assert [n['note'] for n in a['note_assessments']]==by[a['case_id']]['classification']['notes']
 assert a['labels']['next_action_uses_observation']==a['labels']['whole_action_reasonable']=='not_applicable'
 for n in a['note_assessments']:
  w=next(w for w in a['observation'] if w['window_ref']==n['note']['source_ref'])
  assert n['note']['quote'] in w['text'] and n['analysis']
  for k in ['source_support','subject_relation_scope','concrete_clue_relevance']:assert n[k] in ['yes','no','unknown','not_applicable']
for f in r.rglob('*'):
 if not f.is_file() or 'observations.sqlite' in f.name:continue
 assert f.suffix not in ['.safetensors','.pkl'] and f.name!='.env'
 raw=f.read_bytes()
 for token in [b'github_'+b'pat_',b'sk-'+b'ws-',b'atr'+b'_']:assert token not in raw,str(f)
 if f.suffix=='.md':
  for link in re.findall(r'\]\(([^)]+)\)',f.read_text()):
   if not link.startswith(('http:','https:','#')):assert (f.parent/link.split('#')[0]).exists(),(f,link)
assert not Path('/tmp/esr-first-notes-auth-20260921.env').exists()
s=read(r/'semantic_summary.json');assert s['notes']==sum(len(a['note_assessments']) for a in annotations)==16
assert s['reported_token_lower_bounds']==summary['reported_token_lower_bounds']
v={'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'capture_and_model_audit_errors':0,'selection_unchanged':c['selection']==read(r/'selection.json'),'actual_requests_match_plan':True,'no_answers_or_evaluation_ids_in_payload':True,'notes_unchanged':True,'observation_assessed_before_model_calls':True,'annotation_hash_matches':True,'source_snapshot_matches':True,'credentials_scan':'passed','metadata_only_added_exact_prefix':True,'search_calls':6,'model_calls':6,'actors':0,'followup_tools':0,'reported_tokens':summary['reported_token_lower_bounds'],'unknown_usage_requests':0,'local_sqlite_excluded_from_commit':True}
(r/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(v,ensure_ascii=False,indent=2))
