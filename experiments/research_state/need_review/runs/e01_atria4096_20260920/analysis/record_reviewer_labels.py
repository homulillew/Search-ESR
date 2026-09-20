"""Archive Reviewer-first judgments before reading current Actor contents."""
import pathlib,json,datetime,hashlib
r=pathlib.Path(__file__).resolve().parents[1]/'review'
fields=['review_source_attribution_correct','assumption_grounded','need_unresolved','need_decision_relevant','need_already_answered','decision_effect_balanced']
rows=[]
for c in map(json.loads,(r/'cards.jsonl').read_text().splitlines()):
    if c['card_id']=='card_0004':
        assert c['execution_status']['review_status']=='ok'
        labels={k:'yes' for k in fields};labels['need_already_answered']='no'
        note=('引用 event:28:doc:55516 的可见 1600 字符窗口确有 professional 1999–present、>800 centuries、six maximums。审查只把这些归于来源，没有把题目比分链或早先 assistant 的 Players 赛制判断升级为观察。历史 m10/m12/m14 确实围绕 Selby×Players，故未建立的候选绑定是实际路线前提。需求完整保留 decider 后另两胜 4–3、4–0 和对手门槛，不预设赛事；此前工具没有回答完整链。作用允许支持 Selby、换符合条件者或重新理解关系，明确检索失败不等于反证。未声称可见当下统计已证明 2025-01-30 的全部门槛；日期、候选其他资格仍须后续核查。仅这一条可评语义审查，不能外推来源准确率。')
        refs=['question','event:28:doc:55516']
    else:
        assert c['review_output'] is None
        labels={k:'not_applicable' for k in fields};refs=[]
        note=('Reviewer API 超时，没有收到审查正文或 usage，成本未知；不从其他分支或 reasoning 补造来源/需求判断。' if c['execution_status']['review_status']=='api_error' else 'Reviewer 用满 4096 个输出 token，全部为 reasoning，正文为空；不存在可评的交付审查。结构失败保留计划分母，语义轴不适用，不把缺失当成来源推理错误。')
    rows.append({'card_id':c['card_id'],'labels':labels,'notes':note,'supporting_refs':refs})
(r/'reviewer_first_pass.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
(r/'reviewer_first_pass_attestation.json').write_text(json.dumps({
  'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'actor_outputs_read':False,'actor_mechanical_status_known':True,'private_key_opened_this_run':False,
  'blinding':'Not blinded: prior outputs and stable card order known; single Codex-assisted assessment.',
  'sha256':hashlib.sha256((r/'reviewer_first_pass.jsonl').read_bytes()).hexdigest()
},indent=2)+'\n')
