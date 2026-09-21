# 离线分析脚本

verify_capture.py只核验已保存账本和切片，不执行工具，不向模型提供未见全文。record_judgments.py是本批逐条手工/Codex辅助判读的落盘脚本，不能重跑来改写首次时间。build_report.py联接冻结响应和用量，生成全文报告及note_outputs（不生成A/B计划）。verify_artifacts.py验证请求、响应、标签出处及凭据扫描，不验证语义蕴含。

首次支持范围、初评时间/hash均已保存；需要修改判断应另留更正记录。全部标签与边界敏感性由单Codex辅助评阅，不称独立金标或盲评。
