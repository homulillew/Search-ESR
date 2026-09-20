"""Record visible-prefix judgments before reading current semantic outputs."""
import pathlib,json,sys,datetime,hashlib
r=pathlib.Path(sys.argv[1]);v=r/'review'
criteria=json.loads((r/'preflight/pre_output_criteria.json').read_text())['cases']
rows=[]
for c in map(json.loads,(v/'prefix_cards.jsonl').read_text().splitlines()):
    q=next(x['value']['content'] for x in c['canonical_items'] if x['kind']=='original_question')
    case='776' if 'shaman' in q else '546' if 'centuries' in q else '517'
    c['original_constraints']=criteria[case]['constraints']
    c['permitted_next_actions_before_output']=criteria[case]['allowed']
    c['evidence_boundaries']=criteria[case]['boundaries'];rows.append(c)
    print(c['card_id'],case,c['permitted_next_actions_before_output'])
(v/'prefix_assessment.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in rows))
(v/'prefix_attestation.json').write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'current_semantic_outputs_read':False,'prior_cases_known':True,'evaluator':'single Codex-assisted, not blinded or independent human gold',
  'sha256':hashlib.sha256((v/'prefix_assessment.jsonl').read_bytes()).hexdigest()},indent=2)+'\n')
