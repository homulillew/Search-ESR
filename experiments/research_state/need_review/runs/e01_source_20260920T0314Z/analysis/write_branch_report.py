import pathlib,json
r=pathlib.Path(__file__).resolve().parents[1];cards=[json.loads(x) for x in (r/'review/annotations_final.jsonl').read_text().splitlines()];cost={x['sample_id']:x for x in json.loads((r/'verification.json').read_text())['branches']}
lines=['# C0/C1 逐分支分析','','单一 Codex 辅助标注；先前缀、再 Reviewer、再 Actor，最后揭示配对。不是独立人工金标或严格盲评。全部 12 分支保留，未知/不适用分别标记。','', '主指标 action_acceptable 保留完整响应评价；检索方向是辅助轴。action_responds_to_need=yes 仅表示所提查询在语义上回应需求主题，不证明正确使用了审查的纠偏理由、需求合理或检索有收益。未执行工具。','']
for c in sorted(cards,key=lambda c:(c['condition']['checkpoint_id'],c['condition']['repeat_id'],c['condition']['review_contract'])):
 k=c['condition'];sid=k['sample_id'];co=cost[sid];group='C0' if k['review_contract']=='baseline' else 'C1';a=c['actor_response']['choices'][0]['message'];tc=a.get('tool_calls') or []
 lines += [f"## {k['checkpoint_id']} / r{k['repeat_id']} / {group} ({c['card_id']})",'',f"[完整原始记录](branches/{sid}/result.json) · [事件日志](branches/{sid}/events.jsonl)",'',f"审查状态 `{co['review_status']}`；memo_injected={co['memo_injected']}；Actor={co['actor_kind']}；reported tokens={co['reported_tokens']:,}；调用耗时合计={co['elapsed_seconds']:.3f}s。",'', '**Reviewer 来源归属 → 需求**', '',c['reviewer_analysis'],'','```json',c['review_output'],'```','','**Actor 动作 → 尚未知内容**','',c['actor_analysis'],'']
 if tc:lines+=['实际提出的工具（未执行）：','```json',json.dumps([t['function'] for t in tc],ensure_ascii=False,indent=2),'```','']
 else:lines+=['实际下一动作：最终文本作答；完整正文见原始记录。','']
 lines+=['证据界限：'+('仍无与题目一致的完整赛事/对手/比分及as-of统计链。' if '546' in k['checkpoint_id'] else '仍无同一演员的父母、出生/生肖、2005警察角色与2013影片完整关系链。' if '517' in k['checkpoint_id'] else '仍无人物—语言误用事件—作者—1940报告官方题名的完整关系链。'),'','| 评价轴 | 标签 |','|---|---|']
 for name,val in c['labels'].items():lines.append(f'| `{name}` | {val} |')
 lines+=['','配对比较：'+c['label_evidence']['regression']['notes'],'','依据索引：'+', '.join('`'+s+'`' for s in c['label_evidence']['review_source_attribution_correct']['supporting_refs'])+'。精确 message_index/path 见同卡 reference_index。','']
(r/'BRANCH_ANALYSIS.md').write_text('\n'.join(lines))
