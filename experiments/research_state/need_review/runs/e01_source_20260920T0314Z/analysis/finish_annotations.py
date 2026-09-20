import json,pathlib,hashlib,datetime,collections
r=pathlib.Path(__file__).resolve().parents[1];v=r/'review';key=json.loads((v/'private_key.json').read_text());mapping={c['card_id']:c for c in key['cards']}
reg={2:('no','相对同期C0/r2终答，继续Search避免立即终答；来源/正文仍错，不是完整响应改善。'),3:('unknown','相比C0/r1无支持终答改成Search，但指向自称1963出生的候选，方向退化与停止改善并存，无法单序排序。'),4:('yes','相比同期C0/r1仅验证的短正文，C1新增确定答案与大量未见对阵断言；两者完整响应均不通过。'),5:('no','相比C0/r2造出赛事链并终答，C1只提出验证性查询；重复方向仍不通过主指标。'),6:('no','相比C0/r1重复职业查询且确定期刊，C1回退原Actor产生合理候选期刊查询；这是整组结果，非有效审查收益。'),11:('no','相比C0/r2保留职业过滤，C1去除该过滤；仍近重复与无来源正文，主指标未改善。')}
rows=[]
for c in map(json.loads,(v/'annotations_first_pass.jsonl').read_text().splitlines()):
 k=mapping[c['card_id']]; n=int(c['card_id'][-4:]);value,note=reg.get(n,('not_applicable','本批同期C0对照，不对自身做regression判断。'))
 c['labels']['regression']=value;c['label_evidence']['regression']={'supporting_refs':['question'],'notes':note};c['condition']={f:k[f] for f in ['sample_id','checkpoint_id','repeat_id','review_contract']};rows.append(c)
(v/'annotations_final.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in rows))
summary={'reviewer':'single Codex-assisted, not independent human gold; prior E0 outputs and audits known','basis':'metadata-masked first pass; Reviewer labels saved before Actor inspection; private mapping opened after first pass','by_contract':{}}
for contract in ['baseline','source_grounded_v1']:
 cs=[c for c in rows if c['condition']['review_contract']==contract];summary['by_contract'][contract]={'scheduled':len(cs),'valid_reviews':sum(c['execution_status']['review_status']=='ok' for c in cs),'labels':{k:dict(collections.Counter(c['labels'][k] for c in cs)) for k in cs[0]['labels']},'valid_review_source_correct':sum(c['labels']['review_source_attribution_correct']=='yes' and c['execution_status']['review_status']=='ok' for c in cs),'acceptable_actions_after_valid_review':sum(c['labels']['action_acceptable']=='yes' and c['execution_status']['review_status']=='ok' for c in cs)}
(r/'semantic_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
(v/'unmask_attestation.json').write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'first_pass_sha256':hashlib.sha256((v/'annotations_first_pass.jsonl').read_bytes()).hexdigest(),'changes':'Only regression labels/evidence changed; condition metadata appended; all other labels preserved.'},indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
