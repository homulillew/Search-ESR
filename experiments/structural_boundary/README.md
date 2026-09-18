# 表格入口结构修复候选

独立版本`v003_table_entry_candidate`，不改变生产默认。只在Search窗口已有表头而首条数据行未完整展示时，尝试在400-token预算内完成首行，并完整保留原定位锚点。Open、定位器、系统提示词和工具描述不变。

- `python -m pytest -q experiments/structural_boundary/test_candidate.py`
- `python experiments/structural_boundary/offline.py`
- `python experiments/structural_boundary/run_api.py`
- `python experiments/structural_boundary/analyze_api.py <api_run_dir>`

[实验分析](../../全链路排查报告/Search-Open表格入口结构修复对照.md)。本轮只在一篇真实文档上触发修复，收益是局部回归证据，尚非泛化结论。原始窗口与新增/删除原文都保存在离线observations.json，API事件和人工核心事实审阅独立保存。
