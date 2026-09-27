"""Render study reporting only after the committed E1 measurements exist."""
from .common import *
from .run import OUT

def pct(m):
    return '不可估计' if m['value'] is None else f"{100*m['value']:.2f}% ({m['numerator']}/{m['denominator']})"

def render():
    metrics=read(OUT/'METRICS.json');diag=read(OUT/'DIAGNOSTICS.json')
    committed(OUT/'METRICS.json');committed(OUT/'DIAGNOSTICS.json')
    m=metrics['primary'];a=diag['study_accounting']
    ws=read(OUT/'writer/ACCOUNTING.json');ads=read(OUT/'admission/ACCOUNTING.json')
    assert metrics['gate']['status']=='FAIL','A passing E1 requires later stages, not this terminal-failure report.'
    refs=read(OUT/'CANDIDATE_REVIEW.json')['atom_support_sets']
    ceiling=sum(bool(p['sufficient_candidate_sets']) for p in refs)
    border=diag['borderline_dev_diary_subset']
    report=f'''# Minimal Recoverable Loop：E1 结果与阶段停止

## 结论

**E1 FAIL，依冻结Gate停止，E2–E4未执行。** 此次没有证明minimal loop可恢复，也没有否定这一假设；测试止于事实入口。未改旧实验结果，未重采样或修Prompt。用户最新持续授权已经覆盖后续合格阶段，停止原因是实验门槛，不是缺少API授权。

主要问题是Writer输出的Claim与所选摘录之间的上下文丢失：完整Observation可以支持一句话，截取的单句却可能没有人物名、代词前文、日期或表头。严格引用门槛与完整来源支持必须分开解释。

## 实际执行与主指标

53个真实Observation，20qid，两个Writer重复，共106次Writer。生成989候选，10条机械拒绝，979条各调用一次Admission；总计1085个计划API请求。每条候选均在看到Admission判定前完成语义评审；无额外Reviewer API。全部失败/未发送slot都计入账本。实际检索0；没有Actor或闭环C迁移。

| 指标 | 实测 | 冻结门槛 |
|---|---:|---:|
| 最终admitted Claims | {m['admitted_claims']} | — |
| 严格Claim Admission Precision | {pct(m['precision'])} | ≥97% |
| Claim Admission Recall | {pct(m['recall'])} | ≥75% |
| False Admission | {m['false_admissions']} | 描述并分型 |
| High-risk false admission（冻结rubric） | {m['high_risk_false_admissions']} | 0 |
| Relation/argument corruption | {pct(m['relation_argument_corruption_rate'])} | ≤2% |
| Temporal/modal/quantifier/conditional expansion | {pct(m['temporal_modality_quantifier_expansion_rate'])} | ≤2% |
| 最终精确摘录有效率 | {pct(m['exact_excerpt_validity'])} | 100% |
| 原始Writer精确摘录有效率 | {pct(m['raw_writer_exact_excerpt_validity'])} | 描述 |
| Writer schema | {pct(m['writer_schema'])} | ≥95% |
| Admission schema | {pct(m['admission_schema'])} | ≥95% |

最终精确摘录100%来自机械substring/source检查，不能据此说模型引用完全正确。关系/范围专项错误率较低也不能覆盖entity binding或unsupported inference失败。

## 支持边界与召回损失

- Writer在完整Observation下的候选fidelity：{pct(m['writer_observation_fidelity'])}。
- Writer在完整Observation下的参考Recall：{pct(m['writer_recall_before_admission'])}。
- 在尚未看Admission结果的冻结评审中，仅{ceiling}/112参考槽存在摘录充分的候选集合，故当前Writer输出的严格Recall上限为{100*ceiling/112:.2f}%。这已经低于75%，无需借助未来Actor行为才能解释召回障碍。
- 最终admitted集合中，{diag['accepted_quote_context_losses']}条是“完整Observation支持，但实际摘录不足”；{diag['accepted_whole_observation_unsupported']}条连完整Observation也未建立其全部含义。二者总和为严格false admissions。
- 最终admitted集合的完整Observation fidelity为{pct(diag['accepted_whole_observation_fidelity'])}，仅作诊断，不能替代冻结Gate。
- 真正摘录充分的候选被Verifier误拒{m['verifier_false_rejects']['count']}条；因调用失败而损失{m['eligible_good_candidates_lost_to_failed_calls']['count']}条。完整来源本身不支持的Writer候选共{diag['writer_full_observation_unsupported']}条，其中{diag['writer_invalid_whole_observation_that_did_not_enter_C']}条未获准进入C。
- Q/R候选强化proxy：Writer {m['writer_candidate_hardening_count']}条，最终admitted {m['QR_candidate_hardening_count']}条。H没有输入这两个组件，不能将此报成H→C干预实验的经验零泄漏。

这里“admitted”指获得写入C资格的实验判定；没有运行Actor/真实trajectory，不能说已经观察到闭环状态污染或恢复。

## 误差解释与边界案例

逐条错误证据、原始摘录、调用前reason及source分布见[DIAGNOSTICS.json](e1_admission/DIAGNOSTICS.json)。

1. **摘录上下文丢失**：有名实体替换了孤立摘录中的he/she/I，或元数据/表头/日期只在完整Observation里。此组说明当前Claim到证据片段的交接不完整，不能把全部案例称为凭空编造事实。
2. **数值列含义补全**：S025的真实窗口没有表头。把原始数值直接解释为积分、净胜球、最终名次超出冻结证据。足球领域常见格式不能替代当前prefix中的明确支持。
3. **来源内冲突被截短隐藏**：S046同时出现13August和25August2013。独立Admission只能看到一段，无法知道另一日期。该组按预先冻结的完整来源冲突规则计错，不等于Verifier不理解它收到的逐字摘录。
4. **文档类型归属边界**：S045的10个dev-diary判断在调用前已单独披露；可见窗口仅有编号条目，而原reference也用了宽松的diary词。实际admit其中{len(border['admitted'])}条。排除整个预披露组后，严格Precision为{pct(border['strict_precision_without_subset'])}，完整来源fidelity为{pct(border['whole_observation_fidelity_without_subset'])}。这只是敏感性描述，不修改标签或门槛。

元数据与表格语义判断存在空间；这些结果来自一个熟悉历史的reviewer。候选与窗口来自相同问题，两次重复也不独立，因此不做候选级显著性或夸张泛化推断。部分Claim保留了未解决指代但没有擅自绑定实体；这种窄Claim之后能否被Actor安全使用尚未测量。

## 调用与缓存账本

| 批次 | 已发送/计划 | 有效输出 | 缓存命中率 |
|---|---:|---:|---:|
| Writer | {ws['sent_or_send_intent']}/{ws['planned']} | {ws['valid_outputs']} | {pct(ws['cache_hit_rate_reported_tokens'])} |
| Admission | {ads['sent_or_send_intent']}/{ads['planned']} | {ads['valid_outputs']} | {pct(ads['cache_hit_rate_reported_tokens'])} |
| 合计 | {a['sent_or_send_intent']}/{a['planned']} | {a['valid_outputs']} | {pct(a['cache_hit_rate_reported_tokens'])} |

合计已报告token：input {a['reported_partial_totals']['input']:,}，output {a['reported_partial_totals']['output']:,}，其中reasoning {a['reported_partial_totals']['reasoning']:,}；reasoning是output子集，不重复相加。缓存率按一致计数的总hit/总input计算，排除usage缺失或不一致的{a['cache_rate_excluded_attempts']}次。HTTP错误{a['HTTP_errors']}，格式错误{a['schema_errors']}，失败分类`{json.dumps(a['failures'],ensure_ascii=False)}`。max_retries=0、实测并发峰值Writer {ws['peak_concurrency']} / Admission {ads['peak_concurrency']}，未改模型或Backend。

此事实入口共需要989条候选判定（其中979次模型调用）；说明“最小长期State”本身并不保证调用成本小。没有用重新采样、投票或裁剪候选降低该成本。价格未核验，不给虚构金额。

## 任务书20问

| 问题 | 当前证据支持的回答 |
|---|---|
| 1. Evidence→Claim足够安全吗？ | 按冻结E1 Gate，不足够。 |
| 2. Candidate/H还能静默污染C吗？ | 存在错误准入；实际H输入被隔离，H因果泄漏未测。 |
| 3. Writer比Planner更值得加强吗？ | 当前应优先修Writer–Admission证据交接；没有直接Writer/Planner对照，不能作普遍比较。 |
| 4. Minimal state能产生有用action吗？ | E2未运行。 |
| 5. Actor会把H当事实吗？ | 未测；离线权限测试不能代替模型行为。 |
| 6. 两次NoGain后真的换策略吗？ | 离线机械family规则通过；模型是否遵守未测。 |
| 7. Promising source后会local verify吗？ | 未测。 |
| 8. q1094无限global Search仍存在吗？ | 未运行该Actor/trajectory，不能回答。 |
| 9. 错误H能被Evidence淘汰吗？ | 未测。 |
| 10. bad Query可恢复吗？ | 未测。 |
| 11. Trace足够支持recovery吗？ | 离线接口已准备，因果机制未测。 |
| 12. 需要persistent Residual吗？ | 本轮没有新增证据支持其必要性；事实入口失败也不能证明需要它。 |
| 13. 需要SupportGraph/SemanticClosure吗？ | 当前失败没有证明需要增加这些长期State。 |
| 14. Closure能抓Euler/book-only relation gap吗？ | E3未运行；不以Admission结果代替Closure能力。 |
| 15. H-only candidate会错误STOP吗？ | 未测。 |
| 16. 有false READY吗？ | 没有调用Closure，指标未测，不报经验0。 |
| 17. Fresh问题能自然积累Evidence吗？ | 10个fresh已冻结、未调用、未按结果替换。 |
| 18. 局部control error不会污染长期State吗？ | 核心恢复假设尚未进入闭环验证；E1安全先决条件失败。 |
| 19. 当前主要失败点在哪里？ | 已观测为Claim/摘录的上下文交接与Admission资格判定；不是已经证实的Actor、Trace或retrieval瓶颈。 |
| 20. 能正式收缩runtime为Q/R/C/H/Trace吗？ | 暂无资格；保留production schema，先修复并重新独立验证事实入口。 |

## 下一步判断

值得研究的是：在不增加长期语义图的条件下，如何让实际证据片段保留足够的主体、表头、日期和来源内冲突，使一个窄Claim能够独立通过审计。当前可定位的修复方向在source/quote包装及权限边界，而非先增加persistent State字段。新的受控修复实验需要独立协议与请求冻结；本轮不修改Prompt、不重跑，也不越过FAIL进入E2。

原始任务与冻结参考保持不变。持续授权见[AUTHORIZATION_POLICY_AMENDMENT.json](AUTHORIZATION_POLICY_AMENDMENT.json)，主指标与门槛见[METRICS.json](e1_admission/METRICS.json)。
'''
    return report

if __name__=='__main__':write(P/'FINAL_CONCLUSION.md',render())
