# 首次Observation阶段：真实资产预检阻塞

基于edcfb92，六道原题已锁定，257项离线测试通过。真实collect在初始化时发现metadata缺少query_prefix；实际Search及生成模型调用均为0，尚无O1或笔记，不能评价来源保真与遗漏。

旧Searcher把前缀写在代码中，新实验则要求从metadata读出，合同未对齐。实际8192上限与实验1024保护线不构成六题超限，两种tokenizer调用一致。此外，新资产清单漏掉实际向量分片所在的相邻目录，需要版本化修正。

按CODEX_TASK“环境不兼容时报告并暂停”停在此处；未修改检索配置、未启动A/B。下一步仅修真实检索适配与资产声明，再重新采集。

[详细报告与全部失败记录](../experiments/research_state/first_observation/runs/preflight_20260921/REPORT.zh-CN.md)
