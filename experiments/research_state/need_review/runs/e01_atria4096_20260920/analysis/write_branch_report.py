"""Render already recorded judgments; no automatic semantic evaluation."""
import pathlib,json
r=pathlib.Path(__file__).resolve().parents[1]
cards=[json.loads(x) for x in (r/'review/annotations_final.jsonl').read_text().splitlines()]
cost={x['sample_id']:x for x in json.loads((r/'verification.json').read_text())['branches']}
lines=['# 4096 上限 C0/C1 逐分支分析','','先前缀、再 Reviewer、再 Actor，最后核对配对。单一 Codex 辅助评阅，已知旧输出和稳定卡片顺序，不是盲评或独立人工金标。保留所有计划分支，未知、不适用、失败分别记录。','',
       '完整响应指标保留对正文及全部工具调用的评价。工具方向可接受不代表检索有效；没有执行任何工具。超时请求没有收到的服务端输出与成本无法补造。','']
for c in sorted(cards,key=lambda c:(c['condition']['checkpoint_id'],c['condition']['repeat_id'],c['condition']['review_contract'])):
    k=c['condition'];sid=k['sample_id'];co=cost[sid]
    group='C0' if k['review_contract']=='baseline' else 'C1'
    resp=c.get('actor_response');a=resp['choices'][0]['message'] if resp else None
    tc=(a.get('tool_calls') or []) if a else []
    lines += [f"## {k['checkpoint_id']} / r{k['repeat_id']} / {group} ({c['card_id']})",'',
      f'[原始记录](branches/{sid}/result.json) · [事件日志](branches/{sid}/events.jsonl)','',
      f"Reviewer=`{co['review_status']}`；memo_injected={co['memo_injected']}；Actor={co['actor_kind']}。已报告 token 下界 {co['reported_token_lower_bound']:,}，调用耗时合计 {co['elapsed_seconds']:.3f} 秒；未知成本另见原始记录和机械汇总。",'',
      '**原题限定及事前允许的下一动作**','',c['original_constraints_before_branch'],'',c['permitted_next_actions_before_branch'],'',
      '**Reviewer 来源归属 → 信息需求**','',c['reviewer_analysis'],'','```json',c['review_output'] or 'null','```','',
      '**Actor 完整响应 → 仍未知内容**','',c['actor_analysis'],'']
    if a is None:
        lines += ['Actor API 失败，未收到响应；不能补造工具方向或终答，也不能判断需求实际被使用。','']
    else:
        lines += ['交付正文：','```text',a.get('content') or '(empty)','```','']
        if tc:lines+=['提出但未执行的全部工具：','```json',json.dumps([x['function'] for x in tc],ensure_ascii=False,indent=2),'```','']
    lines += ['证据界限：'+('尚无题目要求的完整赛事、对手、比分及 as-of 统计链。' if '546' in k['checkpoint_id'] else '尚无同一演员的出生/生肖、父母、2005 警察角色和 2013 影片关系链。' if '517' in k['checkpoint_id'] else '尚无人物—语言误用—作者—1940 报告官方题名的完整链。'),'','| 评价轴 | 标签 |','|---|---|']
    lines += [f'| `{name}` | {val} |' for name,val in c['labels'].items()]
    lines += ['','配对比较：'+c['label_evidence']['regression']['notes'],'',
      '引用定位见同卡 `reference_index`；逐轴依据见 [annotations_final.jsonl](review/annotations_final.jsonl)。','']
(r/'BRANCH_ANALYSIS.md').write_text('\n'.join(lines).rstrip()+'\n')
