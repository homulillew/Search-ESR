# 分析与复核脚本

`verify_artifacts.py` 是离线机械验证：计划/源/提示词哈希、实际请求与事件、配对唯一system差异、原Actor前缀/参数、无效审查精确回退、usage完整性、标注完整性及引用成员资格。不调用模型、检索或读取凭证。

`write_reviewer_labels.py`、`write_actor_labels.py`、`finish_annotations.py` 是本评阅者人工式定性标签的记录脚本，不是可泛化的自动语义评价器。两份首评脚本当时从/tmp执行，现归档；**不要重新运行来伪造首次阅读/标注时间**。原始时间与SHA保存在review/*attestation.json；只有regression标签在分组揭示后变更。工具方向判定遵照pre_output_baseline，承认近重复查询的价值具有评阅不确定性；即使宽松接受这些方向，无据正文与来源污染仍需单独处理。

`write_branch_report.py` 只将既有标签、原始Reviewer文本和实际动作整理成逐分支Markdown，不产生新语义判断。

复核：在仓库根目录运行 `python experiments/research_state/need_review/runs/e01_source_20260920T0314Z/analysis/verify_artifacts.py`。它更新verification.json中的复核时间，不修改原始实验记录。
