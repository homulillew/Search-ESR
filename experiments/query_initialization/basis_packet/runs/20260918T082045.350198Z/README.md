# BasisPacket 四组固定原文实验

运行完成。6 道开发题，54 次真实 API、48 次 Search、288 个窗口；12 次合法弃答，无格式修复或执行错误。默认策略未修改，自动 Selector 尚未测试。

[节点分析报告](../../../../../全链路排查报告/BasisPacket固定原文与保守编译对照实验.md)

|组|计划|Search|弃答|API tokens|
|---|---:|---:|---:|---:|
|verbatim|6|6|0|0|
|conservative|18|12|6|6303|
|expression_packet|18|15|3|9807|
|expression_full_context|18|15|3|12678|

A 每题一次，其他组各三次。重复不等于独立题目；人工 packet 结果不代表自动选择能力。

## 结果与复核

- [全部查询及冻结参考命中](queries.md)
- [机械审计及逐题数据](audit.json)
- [语义、补充来源与成本汇总](analysis.json)
- [48 次恢复 Open 验证](handoff_verification.json)
- [实验决策](decision.json)
- [运行前实际输入及 packet](tasks.json)
- [提示词与源码版本](manifest.json)
- [运行日志](run.log)

语义标签由协作代理对原文和 query 逐条审阅，部分隐藏组别，不是人工金标准。12 次 null 未公开原因，不算忠实度成功。补充正例形成于运行后，与冻结参考分开；未标注来源不能直接当负例。

## 逐次完整轨迹

|qid|组|重复|状态|轨迹|
|---|---|---:|---|---|
|551|conservative|1|abstained|[trajectory](qid_551__conservative__r1/trajectory.md)|
|551|conservative|2|abstained|[trajectory](qid_551__conservative__r2/trajectory.md)|
|551|conservative|3|abstained|[trajectory](qid_551__conservative__r3/trajectory.md)|
|551|expression_full_context|1|abstained|[trajectory](qid_551__expression_full_context__r1/trajectory.md)|
|551|expression_full_context|2|complete|[trajectory](qid_551__expression_full_context__r2/trajectory.md)|
|551|expression_full_context|3|complete|[trajectory](qid_551__expression_full_context__r3/trajectory.md)|
|551|expression_packet|1|complete|[trajectory](qid_551__expression_packet__r1/trajectory.md)|
|551|expression_packet|2|abstained|[trajectory](qid_551__expression_packet__r2/trajectory.md)|
|551|expression_packet|3|complete|[trajectory](qid_551__expression_packet__r3/trajectory.md)|
|551|verbatim|1|complete|[trajectory](qid_551__verbatim__r1/trajectory.md)|
|645|conservative|1|complete|[trajectory](qid_645__conservative__r1/trajectory.md)|
|645|conservative|2|complete|[trajectory](qid_645__conservative__r2/trajectory.md)|
|645|conservative|3|complete|[trajectory](qid_645__conservative__r3/trajectory.md)|
|645|expression_full_context|1|complete|[trajectory](qid_645__expression_full_context__r1/trajectory.md)|
|645|expression_full_context|2|complete|[trajectory](qid_645__expression_full_context__r2/trajectory.md)|
|645|expression_full_context|3|complete|[trajectory](qid_645__expression_full_context__r3/trajectory.md)|
|645|expression_packet|1|complete|[trajectory](qid_645__expression_packet__r1/trajectory.md)|
|645|expression_packet|2|complete|[trajectory](qid_645__expression_packet__r2/trajectory.md)|
|645|expression_packet|3|complete|[trajectory](qid_645__expression_packet__r3/trajectory.md)|
|645|verbatim|1|complete|[trajectory](qid_645__verbatim__r1/trajectory.md)|
|786|conservative|1|abstained|[trajectory](qid_786__conservative__r1/trajectory.md)|
|786|conservative|2|abstained|[trajectory](qid_786__conservative__r2/trajectory.md)|
|786|conservative|3|abstained|[trajectory](qid_786__conservative__r3/trajectory.md)|
|786|expression_full_context|1|complete|[trajectory](qid_786__expression_full_context__r1/trajectory.md)|
|786|expression_full_context|2|complete|[trajectory](qid_786__expression_full_context__r2/trajectory.md)|
|786|expression_full_context|3|complete|[trajectory](qid_786__expression_full_context__r3/trajectory.md)|
|786|expression_packet|1|abstained|[trajectory](qid_786__expression_packet__r1/trajectory.md)|
|786|expression_packet|2|complete|[trajectory](qid_786__expression_packet__r2/trajectory.md)|
|786|expression_packet|3|abstained|[trajectory](qid_786__expression_packet__r3/trajectory.md)|
|786|verbatim|1|complete|[trajectory](qid_786__verbatim__r1/trajectory.md)|
|1072|conservative|1|complete|[trajectory](qid_1072__conservative__r1/trajectory.md)|
|1072|conservative|2|complete|[trajectory](qid_1072__conservative__r2/trajectory.md)|
|1072|conservative|3|complete|[trajectory](qid_1072__conservative__r3/trajectory.md)|
|1072|expression_full_context|1|complete|[trajectory](qid_1072__expression_full_context__r1/trajectory.md)|
|1072|expression_full_context|2|abstained|[trajectory](qid_1072__expression_full_context__r2/trajectory.md)|
|1072|expression_full_context|3|abstained|[trajectory](qid_1072__expression_full_context__r3/trajectory.md)|
|1072|expression_packet|1|complete|[trajectory](qid_1072__expression_packet__r1/trajectory.md)|
|1072|expression_packet|2|complete|[trajectory](qid_1072__expression_packet__r2/trajectory.md)|
|1072|expression_packet|3|complete|[trajectory](qid_1072__expression_packet__r3/trajectory.md)|
|1072|verbatim|1|complete|[trajectory](qid_1072__verbatim__r1/trajectory.md)|
|1117|conservative|1|complete|[trajectory](qid_1117__conservative__r1/trajectory.md)|
|1117|conservative|2|complete|[trajectory](qid_1117__conservative__r2/trajectory.md)|
|1117|conservative|3|complete|[trajectory](qid_1117__conservative__r3/trajectory.md)|
|1117|expression_full_context|1|complete|[trajectory](qid_1117__expression_full_context__r1/trajectory.md)|
|1117|expression_full_context|2|complete|[trajectory](qid_1117__expression_full_context__r2/trajectory.md)|
|1117|expression_full_context|3|complete|[trajectory](qid_1117__expression_full_context__r3/trajectory.md)|
|1117|expression_packet|1|complete|[trajectory](qid_1117__expression_packet__r1/trajectory.md)|
|1117|expression_packet|2|complete|[trajectory](qid_1117__expression_packet__r2/trajectory.md)|
|1117|expression_packet|3|complete|[trajectory](qid_1117__expression_packet__r3/trajectory.md)|
|1117|verbatim|1|complete|[trajectory](qid_1117__verbatim__r1/trajectory.md)|
|1172|conservative|1|complete|[trajectory](qid_1172__conservative__r1/trajectory.md)|
|1172|conservative|2|complete|[trajectory](qid_1172__conservative__r2/trajectory.md)|
|1172|conservative|3|complete|[trajectory](qid_1172__conservative__r3/trajectory.md)|
|1172|expression_full_context|1|complete|[trajectory](qid_1172__expression_full_context__r1/trajectory.md)|
|1172|expression_full_context|2|complete|[trajectory](qid_1172__expression_full_context__r2/trajectory.md)|
|1172|expression_full_context|3|complete|[trajectory](qid_1172__expression_full_context__r3/trajectory.md)|
|1172|expression_packet|1|complete|[trajectory](qid_1172__expression_packet__r1/trajectory.md)|
|1172|expression_packet|2|complete|[trajectory](qid_1172__expression_packet__r2/trajectory.md)|
|1172|expression_packet|3|complete|[trajectory](qid_1172__expression_packet__r3/trajectory.md)|
|1172|verbatim|1|complete|[trajectory](qid_1172__verbatim__r1/trajectory.md)|
