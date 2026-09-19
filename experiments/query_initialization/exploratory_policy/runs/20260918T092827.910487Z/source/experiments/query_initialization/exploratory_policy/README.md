# 探索原则提示词的两步对照

检验在当前模型自主 Search/Open 策略中增加三句探索原则的价值。A 为现有 Agent 提示词加共同实验预算；B 仅追加探索原则。默认 Agent 代码不变，无 Selector、Compiler 或 ResearchState schema。

复用上一轮固定的20道开发题，每组每题两次，共80会话。首步强制单次 Search top6，第二步允许 Search、Open 或回答；最多160次模型请求，没有第三次强制回答。两组共用每动作2400、每会话4800标题与正文token上限。当前Open方向接口保持不变。

协议见 [PROTOCOL.md](PROTOCOL.md)。实际请求、内容、工具调用、查询、窗口、账本与停止原因逐次归档。结果为代理辅助审阅，不是独立人工金标或泛化证明；不使用best-of-two汇总。

```bash
python -m pytest -q experiments/query_initialization/exploratory_policy/test_policy.py
# 以下命令会产生真实模型调用和本地检索。
python -m experiments.query_initialization.exploratory_policy.run --workers 8 --retrieval-workers 2
```

本轮比较的是整个三句提示词处理。多query、更换检索器、修改窗口和新增状态结构均不在实验内。无明确改善就保留原提示词，不围绕本轮bad case追加规则。
