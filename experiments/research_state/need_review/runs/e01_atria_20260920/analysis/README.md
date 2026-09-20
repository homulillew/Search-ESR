# 本批分析脚本

`verify_artifacts.py` 为离线机械复核，不调用模型或工具、不读取凭证。检查计划、源/提示词、真实请求与事件、model覆盖、精确回退、token恒等式、首轮标注哈希及引用成员资格；附本批reasoning-only截断和配对Actor输入相同的检查。

`record_reviewer_labels.py`、`record_actor_labels.py`、`finish_annotations.py` 保存本次单一Codex辅助判断，不是独立人类金标或自动语义分类器。不要重跑来伪造首次评阅时间。已知旧报告和相同卡片顺序，本轮不声称盲评。首轮到最终仅regression标签/说明变化。

`write_branch_report.py` 将既有标签、Reviewer输出（本批全部null）和Actor动作整理成Markdown。正文支持轴针对交付content；没有正文时为not_applicable，不把空正文伪装为验证过事实。原始reasoning保留在response，不替代未交付的Reviewer JSON。

preflight内的verify_artifacts_template.py仅是运行期间准备的离线验证模板；正式复核使用analysis/verify_artifacts.py。comparison_scope.md为运行期间补充说明，非独立事前预注册；实际首次调用前冻结记录是approved_plan.json、preflight.json与pre_output_baseline.json。

从仓库根目录运行 `python experiments/research_state/need_review/runs/e01_atria_20260920/analysis/verify_artifacts.py` 可以复核，更新时间字段，不修改原始模型记录。
