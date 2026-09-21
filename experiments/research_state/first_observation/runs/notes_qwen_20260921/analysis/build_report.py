"""Join immutable annotations to actual delivery/cost records. No model or tool calls."""
from pathlib import Path
import sys,json,collections,datetime,hashlib
ROOT=Path(__file__).resolve().parents[6];sys.path.insert(0,str(ROOT))
from experiments.research_state.first_observation.run import audit,note_outputs
r=Path(__file__).resolve().parents[1]
summary,raw=audit(r/'notes');by={x['case_id']:x for x in raw}
rows=json.loads((r/'review/annotations_first_pass.json').read_text())
notes=[n for c in rows for n in c['note_assessments']]
s={'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selected_cases':6,'search_attempts':6,'search_successes':6,'windows':30,'model_attempts':summary['attempts'],'responses':summary['responses'],'structurally_valid_nonempty_sets':summary['statuses'].get('ok',0),'empty_sets':summary['statuses'].get('empty',0),'invalid_sets':summary['statuses'].get('invalid',0),'unknown_usage_requests':summary['unknown_usage_requests'],'notes':len(notes),'note_source_support':dict(collections.Counter(n['source_support'] for n in notes)),'note_relation_scope':dict(collections.Counter(n['subject_relation_scope'] for n in notes)),'note_concrete_clue_relevance':dict(collections.Counter(n['concrete_clue_relevance'] for n in notes)),'case_labels':{k:dict(collections.Counter(c['labels'][k] for c in rows)) for k in rows[0]['labels']},'whole_note_set_acceptable':dict(collections.Counter(c['whole_note_set_acceptable'] for c in rows)),'reported_token_lower_bounds':summary['reported_token_lower_bounds'],'reported_reasoning_tokens':sum((x['response'].get('usage',{}).get('completion_tokens_details') or {}).get('reasoning_tokens',0) for x in raw),'monetary_cost':None,'monetary_cost_reason':'No invoice/applicable price verified. Local retrieval/hash cost not metered. Usage counts are provider reported.','actor_calls':0,'followup_tool_calls':0,'sensitivity':'776 title-only timeline and519 attribution extension are strict failures;71 provenance/location and191 missing2025 context remain unknown. Permissive readings do not demonstrate downstream benefit.'}
(r/'semantic_summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
lines=['# 六题完整窗口、笔记与逐条评阅','','单Codex辅助复核。先Q/O1后笔记；本文件保留全部30窗口及16笔记，不将reasoning拼入正文，不读取未交付全文。所有下一动作轴不适用，因为未运行Actor。','']
for c in sorted(rows,key=lambda c:int(c['case_id'])):
 q=c['case_id'];rawrow=by[q];assert rawrow['classification']['notes']==[n['note'] for n in c['note_assessments']]
 lines += [f'## {q} / {c["card_id"]}','',c['question'],'','首次query与上述原题逐字相同；top5，无改写。','',f'[完整请求/响应/usage](notes/{rawrow["id"]}/events.jsonl)','', '### 先行原文支持范围','',c['observation_first_assessment']['support'],'',c['observation_first_assessment']['limits'],'','### 全部实际可见窗口','']
 for w in c['observation']:
  lines += [f'#### {w["window_ref"]} / doc {w["docid"]}','',f'标题：{w["title"]}；来源：{w["url"]}；字符范围[{w["offset"]},{w["end_char"]})；正文+标题token={w["text_tokens"]+w["title_tokens"]}。','', '```text',w['text'],'```','']
 lines += ['### 全部交付笔记及评阅','']
 for n in c['note_assessments']:
  lines += [f'#### 笔记 {n["index"]}','', '```json',json.dumps(n['note'],ensure_ascii=False,indent=2),'```','',f'来源支持={n["source_support"]}；主体/关系/范围={n["subject_relation_scope"]}；具体线索相关性={n["concrete_clue_relevance"]}。','',n['analysis'],'']
 lines += ['### 遗漏、全组评价与成本','',c['omission_analysis'],'',f'完整笔记集合可接受性={c["whole_note_set_acceptable"]}。此轴同时考虑来源与选材，不是答案正确率；边界情况见逐条说明。','',f'耗时{rawrow["elapsed_seconds"]:.3f}秒；原始usage：','```json',json.dumps(rawrow['response']['usage'],ensure_ascii=False,indent=2),'```','']
(r/'CASE_ANALYSIS.zh-CN.md').write_text('\n'.join(lines)+'\n')
(r/'note_outputs.json').write_text(json.dumps(note_outputs(r/'notes'),ensure_ascii=False,indent=2)+'\n')
(r/'review/finalization.json').write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'first_pass_sha256':hashlib.sha256((r/'review/annotations_first_pass.json').read_bytes()).hexdigest(),'labels_changed_after_mapping':False,'mapping_used_only_for_costs_and_case_identity':True},indent=2)+'\n')
print(json.dumps(s,ensure_ascii=False,indent=2))
