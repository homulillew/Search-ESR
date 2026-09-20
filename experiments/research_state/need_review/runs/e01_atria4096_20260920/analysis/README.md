# 本批离线复核与标注

本目录脚本不调用模型或执行模型提出的工具，也不读取凭证。

- `compare_budget.py`：核对相邻批次仅 Reviewer `max_tokens` 从 512 改为 4096，保留模型、完整检查点、提示词、实现及调度；逐请求核对并报告 Actor 实际输入差异。
- `diagnose_budget.py`：统计原始响应的 finish reason、正文长度、reasoning 和 usage。缺失保持 null，合计明确为已报告下界，不能当作货币费用。
- `verify_artifacts.py`：检查计划、源/提示词哈希、实际请求与事件、回退一致性、usage 恒等式、全部标注和首次评阅哈希、引用成员资格及凭证模式。
- `record_prefix.py`：核对当前导出的前缀和上一批完全一致，应用真实调用前冻结的判断标准。
- `record_reviewer_labels.py`、`record_actor_labels.py`、`finish_annotations.py`：归档本批单一 Codex 辅助判断。不是自动语义评测器或独立人类金标。已知历史输出和稳定卡片顺序，不声称盲评。
- `write_branch_report.py`：将既有标签与原始交付文本整理成逐分支报告；API 失败不补造响应。

首次评阅文件带真实时间和 SHA256；不要重跑标注脚本来伪造首次审阅时间。最终配对阶段只改变 regression 标签及说明，并补充分组元数据。原始 reasoning 保留在响应中，不替代缺失的正式 Reviewer JSON，也不当作已交付 Actor 正文。

从仓库根目录运行以下命令可重新做机械复核（仅重写派生文件的复核时间）：

```bash
python experiments/research_state/need_review/runs/e01_atria4096_20260920/analysis/verify_artifacts.py
python experiments/research_state/need_review/runs/e01_atria4096_20260920/analysis/compare_budget.py
python experiments/research_state/need_review/runs/e01_atria4096_20260920/analysis/diagnose_budget.py
```
