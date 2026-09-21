"""Offline audit: request identity, costs, annotation provenance; no model calls."""
import sys,pathlib,json,hashlib,datetime,collections
ROOT=pathlib.Path(__file__).resolve().parents[6];sys.path.insert(0,str(ROOT))
from experiments.research_state.investigation_state.report import audit
from experiments.research_state.investigation_state.packet import render,unpack
from experiments.research_state.investigation_state.run import request_for
r=pathlib.Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
summary,rows=audit(r);assert summary==read(r/'summary.json')
assert not summary['global_errors'] and summary['branches_with_audit_errors']==0
plan=read(r/'plan.json');b=read(r/'bundle.json');assert plan['comparison']=='layout'
times=[json.loads(line)['time'] for f in (r/'branches').glob('*/events.jsonl') for line in f.read_text().splitlines()]
assert datetime.datetime.fromisoformat(plan['fixture_review']['reviewed_at'])<datetime.datetime.fromisoformat(min(times))
gate=read(r/'gate_decision.json')
assert gate['accepted'] is True
if plan['purpose']=='formal':assert plan['acceptance']==gate['acceptance']
assert plan['profile']==read(r/'preflight/profile.json')
assert plan['fixture_review']==read(r/'preflight/fixture_review.json')
assert plan['sdk_max_retries']==0 and summary['reviewer_calls']==summary['tool_executions']==0
assert summary['scheduled_branches']==(6 if plan['purpose']=='pilot' else 12)
diff=[]
for cid,p in b['packets'].items():
    f=request_for(p,'flat',plan['profile'],plan['prompt']);t=request_for(p,'typed',plan['profile'],plan['prompt'])
    a=json.loads(f['messages'][1]['content']);c=json.loads(t['messages'][1]['content'])
    assert unpack(a)==unpack(c);assert a['reference_index']==c['reference_index']
    assert 'attempt_index' not in a and 'attempt_index' not in c
    assert f['messages'][0]==t['messages'][0]
    assert {k:v for k,v in f.items() if k!='messages'}=={k:v for k,v in t.items() if k!='messages'}
    assert f['tools']==p['checkpoint']['request']['tools']
    assert 'extra_body' not in f
    diff.append({'case_id':cid,'flat_payload_utf8_bytes':len(f['messages'][1]['content'].encode()),'typed_payload_utf8_bytes':len(t['messages'][1]['content'].encode()),'canonical_items':len(unpack(a))})
v=r/'review';first=[json.loads(x) for x in (v/'annotations_first_pass.jsonl').read_text().splitlines()]
final=[json.loads(x) for x in (v/'annotations_final.jsonl').read_text().splitlines()]
assert len(first)==len(final)==summary['scheduled_branches']
assert hashlib.sha256((v/'prefix_assessment.jsonl').read_bytes()).hexdigest()==read(v/'prefix_attestation.json')['sha256']
assert hashlib.sha256((v/'annotations_first_pass.jsonl').read_bytes()).hexdigest()==read(v/'first_pass_attestation.json')['sha256']
assert datetime.datetime.fromisoformat(gate['created_at'])<datetime.datetime.fromisoformat(read(v/'prefix_attestation.json')['created_at'])<datetime.datetime.fromisoformat(read(v/'first_pass_attestation.json')['created_at'])
rubric=read(v/'rubric.json');labels=set(rubric['labels'])
for a,c in zip(first,final):
    assert a['card_id']==c['card_id'] and set(c['labels'])==labels
    refs={x['ref'] for x in c['reference_index']}|{x['id'] for x in c['canonical_items']}
    for k,val in c['labels'].items():
        assert val in rubric['allowed'];assert set(c['label_evidence'][k]['refs'])<=refs
        assert c['label_evidence'][k]['notes']
        if k!='regression':assert a['labels'][k]==val and a['label_evidence'][k]==c['label_evidence'][k]
    if c['delivered_response'] is None:assert c['labels']['complete_response_acceptable']=='unknown'
for f in r.rglob('*'):
    if f.is_file():
        assert f.name!='.env' and f.suffix not in ['.safetensors','.sqlite','.parquet']
        raw=f.read_bytes()
        for token in [b'github_'+b'pat_',b'sk-'+b'ws-',b'atr'+b'_']:assert token not in raw
out={'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'audit_errors':0,
     'plan_sha256':plan['plan_sha256'],'bundle_sha256':b['bundle_sha256'],
     'same_items_and_tool_definitions':True,'only_view_payload_differs':True,'no_attempt_linkage':True,
     'fixture_review_bound_before_calls':plan['fixture_review']['reviewed_at'],
     'annotations_complete':len(final),'annotation_hashes_match':True,'only_regression_changed_after_mapping':True,
     'cost_accounting_complete':summary['cost_accounting_complete'],'unknown_usage_calls':summary['unknown_usage_calls'],
     'credential_scan':'passed','input_differences':diff}
(r/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
