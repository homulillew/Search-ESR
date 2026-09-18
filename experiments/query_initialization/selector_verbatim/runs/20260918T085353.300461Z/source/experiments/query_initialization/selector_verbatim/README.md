# Selector → 原文检索的新题对照

本轮只测试选材。20 道本地未使用的问题在请求前锁定，模型仅选择原文编号；Harness 提取原文、保留边界、构造 query 并记录来源。无 Compiler、语义 verifier 或检索反馈重试。

|组|方式|每题次数|
|---|---|---:|
|full_question|全部原文单元，按原文顺序规范空白并拼接|1|
|selector|模型选择单元，使用同一原文提取与拼接逻辑|2|

最多 40 次初始 API 与 60 次 Search；格式修复最多一次，另计。API 八线程，两份独立 Qwen3-Embedding-8B 检索进程并发使用本地 GPU，各自执行原检索器的单条查询方法，不修改 embedding、索引或排序。运行前在三条历史查询上检查两份副本的 top6 和分数一致性，这六次技术探针不混入实验 Search。

模型 qwen3.7-flash，thinking=false，生成 1536 tokens。检索输入含前缀和特殊 token 最多 1024 tokens，超限记录失败，不截断。top6、每窗口标题加正文最多 400 tokens，总计 2400。空选择记录 no_basis，不隐式换全文；全部失败进入统计。

原题切分不变。原题只有一个单元时，全选是接口的结构性结果，不解释为模型偏好。Selector 实际看到全部原题；selector_input_refs 记录该输入范围，input_refs 记录最终用于确定性 query 的选中原文，两者不混淆。

规则见 [REVIEW_PROTOCOL.md](REVIEW_PROTOCOL.md)，抽样见 [selection_lock.json](selection_lock.json)。新题是本地实验未使用，不能保证不在模型预训练中。来源审阅按完整问题判断研究价值，分别报告有用文档与实际可见依据；局部正例池不称为全库召回。

```bash
python -m pytest -q experiments/query_initialization/selector_verbatim/test_selector.py
python -m experiments.query_initialization.selector_verbatim.run --workers 8 --retrieval-workers 2
python -m experiments.query_initialization.selector_verbatim.audit <run_directory>
python -m experiments.query_initialization.selector_verbatim.review_cards <run_directory>
python -m experiments.query_initialization.single_entry.check_handoff <run_directory>
```

历史六题人工 packet 是诊断参照，不是上界，不在本轮新增三组变量。默认 Agent 不变；是否采用 Selector 由独立工程、语义和检索效用门槛共同决定。
