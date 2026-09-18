# 开发：minimal / entry_v1 对照

[完整分析](../../../../../全链路排查报告/Query通用原则提示词落地与对照实验.md)。本批只执行 Query 初始化和一次本地 Search，没有运行完整 Agent 回答。

|组别|尝试|首次合法|完成|API tokens|
|---|---:|---:|---:|---:|
|minimal|16|16|16|17429|
|entry_v1|16|16|16|13208|

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
- [历史正例复核](reference_recheck.json)
- [开发决定](dev_review.json)
- [新题锁定清单](holdout_lock.json)

扩大条件：一次明确关系错误未在同题另一重复复现；歧义与缺引保留，允许锁定后观察新题，不代表通过语义验收。
