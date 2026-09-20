import pathlib,json,hashlib,datetime,collections
r=pathlib.Path(__file__).resolve().parents[1];v=r/'review';key=json.loads((v/'private_key.json').read_text());mapping={c['card_id']:c for c in key['cards']};rows=[]
for c in map(json.loads,(v/'annotations_first_pass.jsonl').read_text().splitlines()):
 k=mapping[c['card_id']];baseline=k['review_contract']=='baseline';c['labels']['regression']='not_applicable' if baseline else 'no'
 c['label_evidence']['regression']={'supporting_refs':['question'],'notes':'同期C0对照不对自身做退化判断。' if baseline else '按本批完整响应标签未比配对C0更差；但双方都回退，Actor输入相同，差异不能归因来源合同。'}
 c['condition']={f:k[f] for f in ['sample_id','checkpoint_id','repeat_id','review_contract']};rows.append(c)
(v/'annotations_final.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in rows))
s={'reviewer':'single Codex-assisted; prior reports/stable card order known; not blind or independent human gold','review_source_attribution_rate':None,'reason':'All Reviewer content absent after reasoning-only cap truncation; no valid semantic review denominator.','by_contract':{}}
for contract in ['baseline','source_grounded_v1']:
 cs=[c for c in rows if c['condition']['review_contract']==contract];s['by_contract'][contract]={'scheduled':len(cs),'valid_reviews':0,'review_source_attribution_rate':None,'labels':{k:dict(collections.Counter(c['labels'][k] for c in cs)) for k in cs[0]['labels']},'acceptable_actions_after_valid_review':0,'valid_review_denominator':0}
prior=json.loads((r/'preflight/prior_qwen_labels.json').read_text());s['cross_model_descriptive']={'qwen_acceptable':sum(c['labels']['action_acceptable']=='yes' for c in prior['cards']),'atria_acceptable':sum(c['labels']['action_acceptable']=='yes' for c in rows),'denominator_each':12,'qwen_memos':sum(c['memo_injected'] for c in prior['cards']),'atria_memos':0,'caveat':'Not equal effective inputs or reasoning compute; repeated development cases, no population accuracy claim.'}
(r/'semantic_summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');(v/'unmask_attestation.json').write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'first_pass_sha256':hashlib.sha256((v/'annotations_first_pass.jsonl').read_bytes()).hexdigest(),'changes':'Only regression labels/evidence changed; condition metadata appended.'},indent=2)+'\n')
print(json.dumps(s,ensure_ascii=False,indent=2))
