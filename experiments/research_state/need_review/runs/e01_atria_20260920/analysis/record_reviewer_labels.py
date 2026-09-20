"""Record this batch's unavailable Reviewer judgments; not a semantic model."""
import pathlib,json,datetime,hashlib
r=pathlib.Path(__file__).resolve().parents[1]/'review';rows=[]
fields=['review_source_attribution_correct','assumption_grounded','need_unresolved','need_decision_relevant','need_already_answered','decision_effect_balanced']
for c in map(json.loads,(r/'cards.jsonl').read_text().splitlines()):
 assert c['review_output'] is None and c['execution_status']['review_status']=='node_invalid' and not c['execution_status']['memo_injected']
 rows.append({'card_id':c['card_id'],'labels':{k:'not_applicable' for k in fields},'notes':'没有输出可用Reviewer正文/四字段JSON，来源归属与需求没有可评价对象；节点失败保留全分母，不从reasoning内容补造审查，不记为语义错误或需求传递失败。','supporting_refs':[]})
(r/'reviewer_first_pass.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
(r/'reviewer_first_pass_attestation.json').write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actor_outputs_read':False,'private_key_opened_this_run':False,'blinding':'Not blinded: prior audit and stable card order known; single Codex-assisted assessment','sha256':hashlib.sha256((r/'reviewer_first_pass.jsonl').read_bytes()).hexdigest()},indent=2)+'\n')
