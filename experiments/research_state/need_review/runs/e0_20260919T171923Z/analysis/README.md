# 离线复核辅助

从仓库根目录运行 `PYTHONPATH=. python experiments/research_state/need_review/runs/e0_20260919T171923Z/analysis/audit_requests.py` 可重核原请求/参数一致性（会重写派生 integrity_and_cost.json，原始请求响应不变）。

两个 write_*_labels.py 保存本次 Codex 定性判断的具体录入内容，不是自动语义评分器，也不是新的人类评价。运行它们会重写派生评价及时间戳；审计应直接读取已冻结的初评、最终评价和时间戳，不通过重跑来伪造盲评。所有脚本仅本地处理，不调用 API 或执行工具。
