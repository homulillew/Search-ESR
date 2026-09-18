# 固定 BasisPacket 的查询编译实验

设计见 [节点设计](../../../全链路排查报告/BasisPacket与保守查询编译设计.md)。第一阶段固定人工选择的六组原文，区分原文直送、编译指令与完整原题暴露的作用，不运行自动 Selector，不修改默认初始化器或 Search–Open。

|组|输入|每题次数|
|---|---|---:|
|verbatim|packet 原文确定性拼接|1|
|conservative|仅 packet，保守 Compiler|3|
|expression_packet|仅 packet，适配后的旧表达指令|3|
|expression_full_context|与上一组相同指令，额外提供完整原题|3|

6 道已知开发题：1117、551、645、786、1072、1172。最多 54 次初始 API 请求与 60 次 Search，格式修复另计。四线程 API、单线程共享检索器。所有组查询上限为含检索前缀和特殊 token 的 1024 embedding tokens；每次 top6，标题与正文各窗口合计最多 400 tokens，总计最多 2400。新预算与历史 512 字符实验不同，不能直接合并统计。

Compiler 请求不携带内部 ID、选择器历史、标准答案或手写目标。D 的完整原题是有意设置的上下文对照，其全部输入来源另行记录。输入来源记录不等于输出事实已获原文支持。

运行前固定 cases、packet、提示词、审阅规则、参数与源码摘要；运行后保留每次实际 SDK 请求响应、query、SearchAttempt、窗口、账本和轨迹。无效输出最多修复一次，合法 null 不搜索、不切换策略，失败计入统计。

```bash
python -m pytest -q experiments/query_initialization/basis_packet/test_packet.py
python -m experiments.query_initialization.basis_packet.run --workers 4 --repeats 3
python -m experiments.query_initialization.basis_packet.audit <run_directory>
python -m experiments.query_initialization.single_entry.check_handoff <run_directory>
```

审阅标准见 [REVIEW_PROTOCOL.md](REVIEW_PROTOCOL.md)。已知正例标注仅覆盖部分题目，未匹配是待审阅，不是负例。结果只能支持该节点的局部判断，不代表完整 Agent 准确率。
