# 36次API结构窗口对照

[综合分析](../../../../全链路排查报告/Search-Open表格入口结构修复对照.md)

- [配置、相同系统提示词与工具Schema](manifest.json)
- [机械汇总](metrics.json)
- [逐例完整回答及机械审计](audit.json)
- [人工核心事实审阅](manual_review.json)
- [输入一致性和原文校验](validation.json)
- [各任务修复信息](repairs.json)

每个任务目录保存events.jsonl完整SDK请求响应、trajectory.md、answer.md及summary.json。source是运行前快照，postrun_source保留审计及测试代码。合成初始Search历史不计为真实检索调用。
