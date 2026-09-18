# 新题：minimal / entry_v1 对照

[完整分析](../../../../../全链路排查报告/Query通用原则提示词落地与对照实验.md)。本批只执行 Query 初始化和一次本地 Search，没有运行完整 Agent 回答。

|组别|尝试|首次合法|完成|API tokens|
|---|---:|---:|---:|---:|
|minimal|40|40|40|40599|
|entry_v1|40|40|40|30215|

两组均无修复或执行失败。模型 qwen3.7-flash，thinking=false；top6，每窗口标题加正文最多 400 tokens。

- [全部查询与审阅](queries.md)
- [完整轨迹索引](trajectory_index.json)
- [逐条语义审阅](semantic_review.json)
- [工程审计](audit.json)
- [请求及快照验证](archive_verification.json)
- [恢复引用与 Open 检查](handoff_verification.json)
- [实际源码快照](source/experiments/query_initialization/single_entry/initializer.py)
- [实际精简提示词](prompt_entry_v1.txt)
- [实际对照提示词](prompt_minimal.txt)
- [请求前锁定清单](evaluation_lock.json)
- [汇总来源池](review_pool.json)
- [有限正例原文依据](entry_evidence_annotations.json)
- [有限正例比较](entry_evidence_recheck.json)
- [本批决定](decision.json)

20 道本地未调参问题，两组各重复两次。有限正例涉及 6 题、12 个题号—来源组合，不能当作全库召回率或总体正确率。默认版本未升级。
