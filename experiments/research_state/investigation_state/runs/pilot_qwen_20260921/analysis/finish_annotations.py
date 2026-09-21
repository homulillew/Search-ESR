"""Pair only after recording all independent card judgments."""
import pathlib,json,datetime,hashlib,collections
r=pathlib.Path(__file__).resolve().parents[1];v=r/'review'
keys={x['card_id']:x for x in json.loads((v/'private_key.json').read_text())}
rows=[json.loads(x) for x in (v/'annotations_first_pass.jsonl').read_text().splitlines()]
for c in rows:
    k=keys[c['card_id']];c['condition']={x:k[x] for x in ['sample_id','case_id','view','repeat']}
    pair=json.loads((r/'analysis/pair_judgments.json').read_text())[k['sample_id']]
    reg=pair['regression'];note=pair['notes']
    c['labels']['regression']=reg;c['label_evidence']['regression']={'refs':['question'],'notes':note}
(v/'annotations_final.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
s={'purpose':json.loads((r/'plan.json').read_text())['purpose'],'evaluator':'single Codex-assisted; prior cases known, not blind or independent human gold','scheduled':len(rows),'semantic_eligible':sum(c['execution']['semantic_eligible'] for c in rows),'by_view':{}}
for view in ['flat','typed']:
    cs=[x for x in rows if x['condition']['view']==view]
    s['by_view'][view]={'planned':len(cs),'semantic_eligible':sum(x['execution']['semantic_eligible'] for x in cs),
      'labels':{k:dict(collections.Counter(x['labels'][k] for x in cs)) for k in cs[0]['labels']}}
(r/'semantic_summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
(v/'unmask_attestation.json').write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'first_pass_sha256':hashlib.sha256((v/'annotations_first_pass.jsonl').read_bytes()).hexdigest(),
  'changes':'Only regression labels/evidence changed; condition metadata appended.'},indent=2)+'\n')
lines=['# 逐分支完整响应复核','','全部计划分支均保留。只评价已交付正文和全部工具提议，不用reasoning替代正文；没有真实工具结果。','']
for c in sorted(rows,key=lambda x:(x['condition']['case_id'],x['condition']['view'],x['condition']['repeat'])):
    k=c['condition'];sid=k['sample_id'];cost=keys[c['card_id']]
    lines += [f"## {k['case_id']} / {k['view']} / r{k['repeat']} ({c['card_id']})",'',
      f'[完整原始记录](branches/{sid}/result.json) · [事件日志](branches/{sid}/events.jsonl)','',
      '**原题限制 → 允许的下一动作**','',c['original_constraints'],'',*['- '+x for x in c['permitted_next_actions_before_output']],'',
      '**实际原文及固定笔记/任务 → 完整动作 → 未决内容**','',c['evidence_boundaries'],'',c['analysis'],'',
      '交付响应（全部选择及工具；未执行）：','```json',json.dumps(c['delivered_response'],ensure_ascii=False,indent=2),'```','',
      f"已报告usage={json.dumps(cost['reported_usage']['known'])}；未知usage请求={cost['unknown_usage_calls']}；耗时={cost['elapsed_seconds']:.3f}秒。缺失不补零。",'',
      '| 评价轴 | 标签 |','|---|---|',*[f'| `{a}` | {b} |' for a,b in c['labels'].items()],'',
      '配对归因：'+c['label_evidence']['regression']['notes'],'']
(r/'BRANCH_ANALYSIS.md').write_text('\n'.join(lines).rstrip()+'\n')
print(json.dumps({k:v for k,v in s.items() if k!='by_view'},ensure_ascii=False,indent=2))
