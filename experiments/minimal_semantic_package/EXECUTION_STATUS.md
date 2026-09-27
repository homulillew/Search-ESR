# E1V完成；35条Auditor请求待新授权

已执行本次用户授权的全部96次Verifier请求，零HTTP/格式/超时失败、零重试。缓存命中率 **24,188 / 51,556 = 46.92%**，批次耗时76.36秒，峰值8并发。

Verifier输出35次SUPPORTED、61次OPEN。按照冻结的Target/Witness参考：

| Verifier-only指标 | 结果 |
|---|---:|
| Precision | 32/35 = 91.43% |
| Recall | 32/42 = 76.19% |
| False Support / False OPEN | 3 / 10 |
| q637 clinical recall | 0/6 |
| Ding marriage recall | 2/2 |
| Schema | 96/96 |

**召回门槛已不可达。** 冻结Auditor只能把SUPPORTED改为OPEN，不能恢复Verifier已判OPEN的10个正例。因此最终Recall上界仍是76.19%，临床Recall上界仍是0%。E2不能因此获得进入资格。

这不是已完成的Auditor结果。E1完整审计指标尚待35条实际请求，能够回答误接受能被救回多少、是否产生额外误拒。35条请求严格使用各Verifier实际引用的Claim子集，未补入其它Claims、旧verdict或reasoning。

本次96次授权已用完。按任务书第33节和此前约定，Auditor须在实际请求commit/hash freeze后重新获得明确授权；当前Auditor调用为0。若获得授权，E1总调用将是96+35=131次。

- [Verifier详细报告](e1_gold_support/VERIFIER_REPORT.md)
- [中期机器指标](e1_gold_support/VERIFIER_INTERIM_METRICS.json)
- [实际Auditor请求](e1_gold_support/AUDITOR_SCHEDULE.json)
- [Auditor请求冻结](e1_gold_support/AUDITOR_FREEZE.json)
- [原始响应与usage核验](analysis/VERIFIER_INTEGRITY.json)

初始README、CURRENT_STATUS、FROZEN_STATE是执行前记录，保持原样。本文件记录本次授权执行后的状态。历史实验和本轮Gold、Prompt均未改动。
