"""Carry forward the pre-call criteria after checking the exported visible prefixes."""
import pathlib,json,datetime,hashlib
r=pathlib.Path(__file__).resolve().parents[1];v=r/'review'
baseline=json.loads((r/'preflight/pre_output_baseline.json').read_text())['cases']
previous=r.parent/'e01_atria_20260920/review/prefix_cards.jsonl'
old={x['card_id']:x for x in map(json.loads,previous.read_text().splitlines())}
rows=[]
for c in map(json.loads,(v/'prefix_cards.jsonl').read_text().splitlines()):
    assert c==old[c['card_id']]
    q=c['visible_history'][1]['content']
    key='776' if 'shaman' in q else '546' if 'centuries' in q else '517'
    b=baseline[key]
    c['permitted_next_actions_before_branch']=b['permitted']
    c['original_constraints_before_branch']=b['constraints']
    c['unsupported_before_branch']=b['unsupported'];rows.append(c)
    print(c['card_id'],key,len(c['visible_history']),len(c['reference_index']),b['permitted'])
(v/'prefix_assessment.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in rows))
(v/'prefix_attestation.json').write_text(json.dumps({
  'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'current_semantic_outputs_read':False,'mechanical_status_and_usage_read':True,
  'prior_historical_outputs_known':True,
  'reviewer':'single Codex-assisted; same prefix and pre-call criteria; not blind or independent human gold',
  'prefix_assessment_sha256':hashlib.sha256((v/'prefix_assessment.jsonl').read_bytes()).hexdigest()
},ensure_ascii=False,indent=2)+'\n')
