"""Pair only after recording all independent card judgments."""
import pathlib,json,datetime,hashlib,collections
r=pathlib.Path(__file__).resolve().parents[1];v=r/'review'
keys={x['card_id']:x for x in json.loads((v/'private_key.json').read_text())}
rows=[json.loads(x) for x in (v/'annotations_first_pass.jsonl').read_text().splitlines()]
for c in rows:
    k=keys[c['card_id']];c['condition']={x:k[x] for x in ['sample_id','case_id','view','repeat']}
    if k['view']=='flat':reg='not_applicable';note='flat为同期基线，不与自身比较退化。'
    elif k['case_id']=='qid_517_s21':
        reg='yes';note='严格可见证据口径下，typed增加未经前缀支持的历法断言，完整响应低于flat；两组的角色/演员表方向均合理。若允许生肖背景常识，双方都可通过，此退化结论不稳健，不作视图劣势推断。'
    else:reg='unknown';note='配对没有双方可消费动作，不能由截断/超时差异推断状态语义或具体决策退化。'
    c['labels']['regression']=reg;c['label_evidence']['regression']={'refs':['question'],'notes':note}
(v/'annotations_final.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
s={'purpose':'pilot exploratory review; not formal S0','evaluator':'single Codex-assisted; old cases known, not blind or independent human gold',
   'scheduled':6,'semantic_eligible':2,'formal_calls':0,'by_view':{},
   'sensitivity':{'strict_visible_evidence_acceptable':1,'if_basic_zodiac_background_allowed_acceptable':2,'fixed_planned_denominator':6,
      'affected_card':'card_0003','meaning':'Do not conflate unsupported-within-prefix with factually false. This ambiguity does not affect the delivery gate.'},
   'decision_effect_conclusion':'517 both use role/cast investigation; typed additionally explores 1979 family filter and emits calendar assertions. 546/776 have no paired observable decisions. No reliable layout benefit established.'}
for view in ['flat','typed']:
    cs=[x for x in rows if x['condition']['view']==view]
    s['by_view'][view]={'planned':len(cs),'semantic_eligible':sum(x['execution']['semantic_eligible'] for x in cs),
      'labels':{k:dict(collections.Counter(x['labels'][k] for x in cs)) for k in cs[0]['labels']}}
(r/'semantic_summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
(v/'unmask_attestation.json').write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'first_pass_sha256':hashlib.sha256((v/'annotations_first_pass.jsonl').read_bytes()).hexdigest(),
  'changes':'Only regression labels/evidence changed; condition metadata appended.'},indent=2)+'\n')
lines=['# 六次pilot逐分支复核','','全部6个计划分支均保留。这里只评价已交付正文和全部工具提议，不用reasoning替代正文。没有正式S0样本，也没有真实工具结果。','']
for c in sorted(rows,key=lambda x:(x['condition']['case_id'],x['condition']['view'])):
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
