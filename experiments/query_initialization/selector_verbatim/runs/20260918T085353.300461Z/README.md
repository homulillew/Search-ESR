# Selector 原文选材：20260918T085353.300461Z

20 道本地既有实验未使用的问题；整题原文每题一次，Selector 每题两次。不含 Compiler，不做结果驱动修复。运行已完成，默认 Agent 未变更。

| 指标 | 整题 | Selector |
|---|---:|---:|
| 完成 Search | 20/20 | 40/40 |
| 确认有用来源 | 9/20（45%） | 19/40（题均47.5%） |
| 可见有用依据 | 9/20（45%） | 18/40（题均45%） |
| API 请求 | 0 | 40 |
| API tokens | 0 | 21,944 |

API 并发配置8，实际峰值5；两个独立检索进程，实际检索峰值2。预检6次与正式Search60次分别记录。工程审计及60次恢复账本后的Open通过。40个Selector packet经代理辅助审阅均可理解；19个来源正例的44个原文区间经数据库校验。

结论：代理标注下数值门槛通过，但可见依据持平，qid71重复退化、qid1147重复改善，额外调用尚无稳定净收益依据。不默认推广Selector；已验证的原文构造、来源记录与观察恢复接口可用于后续节点。

## 方法限制

审阅是编码代理进行的事后定性判断，部分非盲，非独立人工金标。它不满足冻结协议“不使用LLM judge”的严格表述，此偏差已明确保留。覆盖166个题目—文档组合、193个窗口，额外全文检查范围逐项记录；未确认不等于全文无关，指标不是完整召回率。先取同题两次均值再汇总20题，不采用best-of-two。

## 文件

- [节点报告](../../../../../全链路排查报告/Selector原文选材与整题检索对照实验.md)
- [冻结配置](manifest.json)、[抽样锁](selection_lock.json)、[题目原文](tasks.json)、[执行顺序](schedule.json)
- [冻结协议](source/experiments/query_initialization/selector_verbatim/REVIEW_PROTOCOL.md)、[冻结提示词](source/experiments/query_initialization/selector_verbatim/SELECTOR_PROMPT.txt)
- [检索副本预检](retrieval_preflight.json)、[机械审计](audit.json)、[恢复Open](handoff_verification.json)
- [实际query汇总](queries.md)、[调用结果](results.json)、[原始运行日志](run.log)
- [语义卡](semantic_cards.json)、[窗口卡](utility_cards.json)、[合并来源池](review_pool.json)
- [审阅A](review_part_a.json)、[审阅B](review_part_b.json)、[审阅C](review_part_c.json)、[审阅D1](review_part_d1.json)、[审阅D2](review_part_d2.json)
- [逐题及总计分](review_summary.json)、[复算器快照](review_source/summarize_review.py)、[复核方法](review_manifest.json)

每个session包含input、原始API请求/响应events、packet、query与原始Search结果、trajectory、观察账本、handoff。API凭据不写入轨迹。source保存运行前快照，review_source单独保存运行后分析实现，避免混淆。

## 全部轨迹

| qid | 整题原文 | Selector 第一次 | Selector 第二次 |
|---|---|---|---|
| 719 | [整题](qid_719__full_question__r1/trajectory.md) | [Selector r1](qid_719__selector__r1/trajectory.md) | [Selector r2](qid_719__selector__r2/trajectory.md) |
| 520 | [整题](qid_520__full_question__r1/trajectory.md) | [Selector r1](qid_520__selector__r1/trajectory.md) | [Selector r2](qid_520__selector__r2/trajectory.md) |
| 605 | [整题](qid_605__full_question__r1/trajectory.md) | [Selector r1](qid_605__selector__r1/trajectory.md) | [Selector r2](qid_605__selector__r2/trajectory.md) |
| 760 | [整题](qid_760__full_question__r1/trajectory.md) | [Selector r1](qid_760__selector__r1/trajectory.md) | [Selector r2](qid_760__selector__r2/trajectory.md) |
| 519 | [整题](qid_519__full_question__r1/trajectory.md) | [Selector r1](qid_519__selector__r1/trajectory.md) | [Selector r2](qid_519__selector__r2/trajectory.md) |
| 854 | [整题](qid_854__full_question__r1/trajectory.md) | [Selector r1](qid_854__selector__r1/trajectory.md) | [Selector r2](qid_854__selector__r2/trajectory.md) |
| 1000 | [整题](qid_1000__full_question__r1/trajectory.md) | [Selector r1](qid_1000__selector__r1/trajectory.md) | [Selector r2](qid_1000__selector__r2/trajectory.md) |
| 435 | [整题](qid_435__full_question__r1/trajectory.md) | [Selector r1](qid_435__selector__r1/trajectory.md) | [Selector r2](qid_435__selector__r2/trajectory.md) |
| 60 | [整题](qid_60__full_question__r1/trajectory.md) | [Selector r1](qid_60__selector__r1/trajectory.md) | [Selector r2](qid_60__selector__r2/trajectory.md) |
| 1249 | [整题](qid_1249__full_question__r1/trajectory.md) | [Selector r1](qid_1249__selector__r1/trajectory.md) | [Selector r2](qid_1249__selector__r2/trajectory.md) |
| 71 | [整题](qid_71__full_question__r1/trajectory.md) | [Selector r1](qid_71__selector__r1/trajectory.md) | [Selector r2](qid_71__selector__r2/trajectory.md) |
| 1039 | [整题](qid_1039__full_question__r1/trajectory.md) | [Selector r1](qid_1039__selector__r1/trajectory.md) | [Selector r2](qid_1039__selector__r2/trajectory.md) |
| 446 | [整题](qid_446__full_question__r1/trajectory.md) | [Selector r1](qid_446__selector__r1/trajectory.md) | [Selector r2](qid_446__selector__r2/trajectory.md) |
| 1035 | [整题](qid_1035__full_question__r1/trajectory.md) | [Selector r1](qid_1035__selector__r1/trajectory.md) | [Selector r2](qid_1035__selector__r2/trajectory.md) |
| 1147 | [整题](qid_1147__full_question__r1/trajectory.md) | [Selector r1](qid_1147__selector__r1/trajectory.md) | [Selector r2](qid_1147__selector__r2/trajectory.md) |
| 124 | [整题](qid_124__full_question__r1/trajectory.md) | [Selector r1](qid_124__selector__r1/trajectory.md) | [Selector r2](qid_124__selector__r2/trajectory.md) |
| 978 | [整题](qid_978__full_question__r1/trajectory.md) | [Selector r1](qid_978__selector__r1/trajectory.md) | [Selector r2](qid_978__selector__r2/trajectory.md) |
| 191 | [整题](qid_191__full_question__r1/trajectory.md) | [Selector r1](qid_191__selector__r1/trajectory.md) | [Selector r2](qid_191__selector__r2/trajectory.md) |
| 134 | [整题](qid_134__full_question__r1/trajectory.md) | [Selector r1](qid_134__selector__r1/trajectory.md) | [Selector r2](qid_134__selector__r2/trajectory.md) |
| 692 | [整题](qid_692__full_question__r1/trajectory.md) | [Selector r1](qid_692__selector__r1/trajectory.md) | [Selector r2](qid_692__selector__r2/trajectory.md) |

## 离线复算

在仓库根目录执行，不产生新API或Search：

```bash
python -m experiments.query_initialization.selector_verbatim.summarize_review experiments/query_initialization/selector_verbatim/runs/20260918T085353.300461Z
```
