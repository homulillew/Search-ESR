# 探索原则提示词 v002：两步对照

状态：运行、机械审计、全部来源与行为审阅、计分完成。默认提示词不变，Query局部优化收尾。

20道既有开发题 × 当前/探索原则两组 × 两次重复，共80会话。每会话最多两次动作；首Search后第二步可Search/Open/回答，不含最终强制回答。正式155次API、147次Search、1次Open、485,427 tokens；实际API并发8、检索并发2。

| 指标 | 当前 A | 探索原则 B |
|---|---:|---:|
| 完成两步 | 38/40 | 35/40 |
| 首搜可见依据 | 35% | 40% |
| 两步累计可见依据 | 40% | 45% |
| 第二步严格新增依据 | 35% | 32.5% |

B有局部入口收益，未改善整体第二步新增；519重复改善与191重复退化并存，当前不推广。七条未完成会话保留在分母内；其中六条length、一条无首搜直接回答。两步均值按题汇总，不取best-of-two。

审阅覆盖420个题目—文档组合、527个不同窗口、80条行为轨迹。代理辅助、部分非盲，非人工金标或完整召回率。区间/散列核对是确定性检查；事实是否相关、是否语义新增来自明确披露的代理判断。

## 文件与方法

- [完整报告](../../../../../全链路排查报告/Query探索原则提示词两步对照实验.md)
- [冻结配置](manifest.json)、[题目](tasks.json)、[调度](schedule.json)、[冻结协议](source/experiments/query_initialization/exploratory_policy/PROTOCOL.md)
- [运行日志](run.log)、[实际两步动作索引](queries.md)、[执行结果](results.json)
- [预检](retrieval_preflight.json)、[机械审计](audit.json)
- [来源池](review_pool.json)、[窗口卡](utility_cards.json)、[行为卡](behavior_cards.json)
- [审阅A](review_part_a.json)、[审阅B](review_part_b.json)、[审阅C](review_part_c.json)
- [计分](review_summary.json)、[决策](decision.json)、[审阅归档](review_manifest.json)
- [离线计分器快照](review_source/score_review.py)、[离线审计器快照](review_source/audit.py)

每个session保存input/result/summary、完整API请求响应events、messages、trajectory、观察账本与handoff。二次工具结果虽保存于末尾messages，但未再发送第三次模型请求。测试的是已执行下一动作的返回价值，不能声称模型已经理解第二次工具结果。

## 兼容性诊断单列

[v001诊断批次](../20260918T092448.634346Z/README.md)共80次API、95,490 tokens，没有正式Search。完整强制工具调用被服务端标为stop，v001要求tool_calls而拒绝。v002接受stop+完整唯一合法调用；length仍拒绝。原始finish_reason与兼容标记均保留，题目/prompt/预算不变，全量另起运行，不混合比较。

本任务两批合计235次API、580,917 tokens。两批各6次检索副本预检另计，不计入147次正式Search。

## 逐题效用

每格为A/B题均，0、0.5、1分别表示两个重复均未确认、一次确认、两次确认。未确认不是全文绝对无关。

| qid | 首搜可见 | 累计可见 | 第二步新增 |
|---|---|---|---|
| 719 | 0 / 0 | 0 / 0 | 0 / 0 |
| 520 | 0 / 0 | 0 / 0 | 0 / 0 |
| 605 | 1 / 1 | 1 / 1 | 1 / 1 |
| 760 | 0 / 0 | 0 / 0 | 0 / 0 |
| 519 | 0 / 1 | 0 / 1 | 0 / 1 |
| 854 | 1 / 1 | 1 / 1 | 1 / 1 |
| 1000 | 1 / 0.5 | 1 / 0.5 | 1 / 0.5 |
| 435 | 1 / 1 | 1 / 1 | 1 / 1 |
| 60 | 0 / 0 | 0 / 0 | 0 / 0 |
| 1249 | 0 / 0 | 0 / 0 | 0 / 0 |
| 71 | 0 / 0 | 0.5 / 1 | 0.5 / 1 |
| 1039 | 0 / 0 | 0 / 0 | 0 / 0 |
| 446 | 0.5 / 1 | 0.5 / 1 | 0 / 0 |
| 1035 | 1 / 1 | 1 / 1 | 1 / 0.5 |
| 1147 | 0 / 0 | 0 / 0 | 0 / 0 |
| 124 | 0 / 0 | 0 / 0 | 0 / 0 |
| 978 | 0.5 / 0.5 | 1 / 0.5 | 0.5 / 0.5 |
| 191 | 1 / 1 | 1 / 1 | 1 / 0 |
| 134 | 0 / 0 | 0 / 0 | 0 / 0 |
| 692 | 0 / 0 | 0 / 0 | 0 / 0 |

## 全部轨迹

| qid | 当前 r1 | 当前 r2 | 探索 r1 | 探索 r2 |
|---|---|---|---|---|
| 719 | [current r1](qid_719__current__r1/trajectory.md) | [current r2](qid_719__current__r2/trajectory.md) | [exploratory r1](qid_719__exploratory__r1/trajectory.md) | [exploratory r2](qid_719__exploratory__r2/trajectory.md) |
| 520 | [current r1](qid_520__current__r1/trajectory.md) | [current r2](qid_520__current__r2/trajectory.md) | [exploratory r1](qid_520__exploratory__r1/trajectory.md) | [exploratory r2](qid_520__exploratory__r2/trajectory.md) |
| 605 | [current r1](qid_605__current__r1/trajectory.md) | [current r2](qid_605__current__r2/trajectory.md) | [exploratory r1](qid_605__exploratory__r1/trajectory.md) | [exploratory r2](qid_605__exploratory__r2/trajectory.md) |
| 760 | [current r1](qid_760__current__r1/trajectory.md) | [current r2](qid_760__current__r2/trajectory.md) | [exploratory r1](qid_760__exploratory__r1/trajectory.md) | [exploratory r2](qid_760__exploratory__r2/trajectory.md) |
| 519 | [current r1](qid_519__current__r1/trajectory.md) | [current r2](qid_519__current__r2/trajectory.md) | [exploratory r1](qid_519__exploratory__r1/trajectory.md) | [exploratory r2](qid_519__exploratory__r2/trajectory.md) |
| 854 | [current r1](qid_854__current__r1/trajectory.md) | [current r2](qid_854__current__r2/trajectory.md) | [exploratory r1](qid_854__exploratory__r1/trajectory.md) | [exploratory r2](qid_854__exploratory__r2/trajectory.md) |
| 1000 | [current r1](qid_1000__current__r1/trajectory.md) | [current r2](qid_1000__current__r2/trajectory.md) | [exploratory r1](qid_1000__exploratory__r1/trajectory.md) | [exploratory r2](qid_1000__exploratory__r2/trajectory.md) |
| 435 | [current r1](qid_435__current__r1/trajectory.md) | [current r2](qid_435__current__r2/trajectory.md) | [exploratory r1](qid_435__exploratory__r1/trajectory.md) | [exploratory r2](qid_435__exploratory__r2/trajectory.md) |
| 60 | [current r1](qid_60__current__r1/trajectory.md) | [current r2](qid_60__current__r2/trajectory.md) | [exploratory r1](qid_60__exploratory__r1/trajectory.md) | [exploratory r2](qid_60__exploratory__r2/trajectory.md) |
| 1249 | [current r1](qid_1249__current__r1/trajectory.md) | [current r2](qid_1249__current__r2/trajectory.md) | [exploratory r1](qid_1249__exploratory__r1/trajectory.md) | [exploratory r2](qid_1249__exploratory__r2/trajectory.md) |
| 71 | [current r1](qid_71__current__r1/trajectory.md) | [current r2](qid_71__current__r2/trajectory.md) | [exploratory r1](qid_71__exploratory__r1/trajectory.md) | [exploratory r2](qid_71__exploratory__r2/trajectory.md) |
| 1039 | [current r1](qid_1039__current__r1/trajectory.md) | [current r2](qid_1039__current__r2/trajectory.md) | [exploratory r1](qid_1039__exploratory__r1/trajectory.md) | [exploratory r2](qid_1039__exploratory__r2/trajectory.md) |
| 446 | [current r1](qid_446__current__r1/trajectory.md) | [current r2](qid_446__current__r2/trajectory.md) | [exploratory r1](qid_446__exploratory__r1/trajectory.md) | [exploratory r2](qid_446__exploratory__r2/trajectory.md) |
| 1035 | [current r1](qid_1035__current__r1/trajectory.md) | [current r2](qid_1035__current__r2/trajectory.md) | [exploratory r1](qid_1035__exploratory__r1/trajectory.md) | [exploratory r2](qid_1035__exploratory__r2/trajectory.md) |
| 1147 | [current r1](qid_1147__current__r1/trajectory.md) | [current r2](qid_1147__current__r2/trajectory.md) | [exploratory r1](qid_1147__exploratory__r1/trajectory.md) | [exploratory r2](qid_1147__exploratory__r2/trajectory.md) |
| 124 | [current r1](qid_124__current__r1/trajectory.md) | [current r2](qid_124__current__r2/trajectory.md) | [exploratory r1](qid_124__exploratory__r1/trajectory.md) | [exploratory r2](qid_124__exploratory__r2/trajectory.md) |
| 978 | [current r1](qid_978__current__r1/trajectory.md) | [current r2](qid_978__current__r2/trajectory.md) | [exploratory r1](qid_978__exploratory__r1/trajectory.md) | [exploratory r2](qid_978__exploratory__r2/trajectory.md) |
| 191 | [current r1](qid_191__current__r1/trajectory.md) | [current r2](qid_191__current__r2/trajectory.md) | [exploratory r1](qid_191__exploratory__r1/trajectory.md) | [exploratory r2](qid_191__exploratory__r2/trajectory.md) |
| 134 | [current r1](qid_134__current__r1/trajectory.md) | [current r2](qid_134__current__r2/trajectory.md) | [exploratory r1](qid_134__exploratory__r1/trajectory.md) | [exploratory r2](qid_134__exploratory__r2/trajectory.md) |
| 692 | [current r1](qid_692__current__r1/trajectory.md) | [current r2](qid_692__current__r2/trajectory.md) | [exploratory r1](qid_692__exploratory__r1/trajectory.md) | [exploratory r2](qid_692__exploratory__r2/trajectory.md) |

## 离线复核

从仓库根目录执行；不会产生API或新Search：

```bash
python -m experiments.query_initialization.exploratory_policy.audit experiments/query_initialization/exploratory_policy/runs/20260918T092827.910487Z
python -m experiments.query_initialization.exploratory_policy.score_review experiments/query_initialization/exploratory_policy/runs/20260918T092827.910487Z
```
