from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,collections
R=Path(__file__).resolve().parents[1];V=R/'review';key=json.loads((V/'private_key.json').read_text());K={x['card_id']:x for x in key['cards']};first=[json.loads(l) for l in (V/'annotations_first_pass.jsonl').read_text().splitlines()]
reg={1:('no','相比同题 A/r2，未观察到额外明确退化，但仍无有效推进。'),2:('unknown','最终查询撤掉1975，但正文更强认定 Idris、放宽角色；局部得失混合，不能判整条改善或恶化。'),3:('unknown','A/r1也编造赛程；B继续错误赛事并换未经证实对手，不能从一次响应确定相对严重度。'),4:('no','与A/r2同样保留职业过滤；未见改善，也不足判更差。'),7:('unknown','查询解除绑定，但冗长无证据赛程更多；不同质量轴混合。'),8:('yes','A/r1尚未加职业过滤到本次Query；B/r1新增确定期刊/作者断言并把 anthropologist 加入Query。'),12:('yes','A/r2继续检索，本分支无新证据便提交 Bingham，且漏一场胜利。'),13:('no','回退分支和A/r1都在重复已有检索；不是审查传递成功。'),14:('unknown','相对A/r2从无依据1975过滤改回显式Idris确认；都差，不能可靠量化孰差。'),15:('unknown','相对A/r1查询方向更合理，但整条正文更强无证据身份断言；混合。'),17:('yes','相对A/r2，工具仍可用却直接最终提交未证实的Idris，纠偏转成提前结束。'),18:('yes','相对A/r2，未取新证据直接给Trump最终答案。')}
for row in first:
 meta=K[row['card_id']];idx=int(row['card_id'].split('_')[1]);label,note=reg.get(idx,('not_applicable','A 是匹配比较基线，不与自身判退化。'))
 row['labels']['regression']=label;row['label_evidence']['regression']['notes']=note
 row['group_mapping']={k:meta[k] for k in ['sample_id','checkpoint_id','arm','repeat_id']};row['cost']={k:meta[k] for k in ['logical_requests','review_usage','actor_usage','review_elapsed_seconds','actor_elapsed_seconds','review_validation_errors']}
(V/'annotations_final.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in first))
(V/'unmask_attestation.json').write_text(json.dumps({'unmasked_at':datetime.now(timezone.utc).isoformat(),'first_pass_sha256':hashlib.sha256((V/'annotations_first_pass.jsonl').read_bytes()).hexdigest(),'changed_labels':['regression'],'unchanged_all_other_labels':True,'annotation_origin':'Codex qualitative judgments, no additional reviewer API calls or independent human review'},indent=2))
# Generate per-branch tables strictly from completed annotations and raw cost records.
summary={}
for arm in 'ABC':
 rows=[x for x in first if x['group_mapping']['arm']==arm]
 summary[arm]={'denominator':len(rows),'acceptable_whole_response':sum(x['labels']['action_acceptable']=='yes' for x in rows),'query_direction_only_positive':sum(x['tool_query_direction_only']=='yes' for x in rows),'final_answers':sum(x['labels']['answer_vs_abstention']=='answer' for x in rows),'regression_yes':sum(x['labels']['regression']=='yes' for x in rows),'regression_unknown':sum(x['labels']['regression']=='unknown' for x in rows),'semantic_abstentions':sum(x['labels']['answer_vs_abstention'] in ['abstention','mixed'] for x in rows)}
(R/'semantic_summary.json').write_text(json.dumps({'reviewer':'Codex; metadata-masked first pass, not guaranteed blind; no human adjudication','scope':'three development checkpoints, two repetitions; no tool execution or answer scoring','whole_response_rule':'Evaluate full response including unsupported confident claims; query direction separately descriptive, not replacement primary metric','groups':summary},indent=2))
lines=['# 逐分支定性标注与成本','\n由 Codex 单评阅者完成；初评先于 private_key 揭示。人工复核尚未进行。原始 cards 与 first_pass 文件未改写。', '\n计数口径：整体下一响应包含前导文字和全部工具调用；工具查询方向仅作补充描述。未查询外部答案、未读取 gold 或未来事件。']
for row in sorted(first,key=lambda x:(x['group_mapping']['checkpoint_id'],x['group_mapping']['repeat_id'],x['group_mapping']['arm'])):
 m=row['group_mapping'];co=row['cost'];tokens=sum((co[s+'_usage'] or {}).get('total_tokens',0) for s in ['review','actor']);sec=sum(co[s+'_elapsed_seconds'] or 0 for s in ['review','actor'])
 lines+=['\n## '+m['sample_id']+' / '+row['card_id'],f'\n调用 {co["logical_requests"]} 次；报告总 token {tokens:,}；调用耗时合计 {sec:.2f}s；备忘注入 {row["execution_status"]["memo_injected"]}；审查错误 `{co["review_validation_errors"]}`。',f'\n完整响应可接受：{row["labels"]["action_acceptable"]}；仅 Query 方向：{row["tool_query_direction_only"]}；相对匹配 A 退化：{row["labels"]["regression"]}。']
 for field in row['labels']:
  ev=row['label_evidence'][field];lines.append(f'\n- **{field} = {row["labels"][field]}**：{ev["notes"]} 依据：'+', '.join(ev['supporting_refs']))
 lines+=['\n引用语义：'+row['citation_semantics'],'\n517 回归检查：'+row['regression_517_note']]
(R/'BRANCH_ANALYSIS.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(summary,indent=2))
