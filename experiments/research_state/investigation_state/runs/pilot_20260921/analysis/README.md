# 本轮分析与复核

以下脚本均为离线操作，不调用模型或真实工具，不读取凭证。

- `summarize_delivery.py`：从原始记录生成交付、reasoning、耗时和usage诊断。API失败的usage保持null。
- `verify_artifacts.py`：复算原始审计；核对相同条目、工具定义、profile、复核声明、源码/请求、无S1索引、标签合法性、首评哈希及映射后仅regression变化。
- `record_prefix.py`：读取没有输出的prefix_cards，写入调用期间但读输出前已记录的判断标准；接受运行目录参数。
- `record_labels.py`：保存本批单一Codex辅助首评；不是自动评测器。边界是完整交付content与全部工具提议，隐藏reasoning不替代缺失正文。
- `finish_annotations.py`：首评完成后读配对表，仅更新regression标签及说明，生成语义汇总及逐分支报告。517的生肖背景判断附敏感性分析，不把“不在前缀中”说成“事实已证伪”。

首评脚本保存实际时间和SHA256，**不要重跑来伪造首次评阅时间**。作者知道历史病例和机械分组，不声称盲评或独立人类金标。机械复核可从仓库根目录重新运行：

```bash
python experiments/research_state/investigation_state/runs/pilot_20260921/analysis/verify_artifacts.py
```

此命令更新派生verification时间，不改原始请求/响应。复核通过表示记录一致，不表示pilot交付通过。原始gate_decision明确拒绝正式计划；本轮正式S0为0次调用。
