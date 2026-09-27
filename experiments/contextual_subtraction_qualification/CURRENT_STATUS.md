# 当前状态：E1 FAIL，实验在 Qualification 阶段结束

192/192 请求完成并保留；无失败、重试或重采样。48 个 Certificate × Q0/Q1 × 两次重复，DeepSeek `deepseek-flash`，最多8并发。

| 指标 | Q0：独立片段 | Q1：完整上下文 |
|---|---:|---:|
| Subtraction Precision | 44/54 = 81.48% | 32/35 = 91.43% |
| Subtraction Recall | 44/44 = 100% | 32/44 = 72.73% |
| Binding-missing false acceptance | 10/30 = 33.33% | 3/30 = 10% |
| False-full-risk acceptance | 4/26 | 2/26 |
| Replicate verdict agreement | 48/48 = 100% | 41/48 = 85.42% |

Q1 修正7次错误接受，同时新增12次漏接受。精度改善成立，但安全性、召回及相对召回门槛均未通过。E2/E3实际调用为0，下游能力指标为未测量。

缓存命中64,379 / 115,146 input tokens = **55.91%**，192次 usage 均完整且一致。总 tokens 291,579；运行耗时126.41秒。

- [最终结论](FINAL_CONCLUSION.md)
- [E1完整结果与门槛](e1_qualification/REPORT.md)
- [九类必答 bad cases 与配对对照](analysis/CASE_REPORT.md)
- [执行审计](analysis/POST_EXECUTION_AUDIT.md)、[机器可读完整性核验](analysis/INTEGRITY.json)
- [E2最终决定](e2_cascade/DECISION.json)、[E3最终决定](e3_residual/DECISION.json)

初始 README、Protocol、E2/E3 STATUS 是已冻结的执行前记录，保持原样；本文件和各阶段 DECISION 记录最终状态。
