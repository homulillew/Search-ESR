# Asymmetric Progress / Closure Audit

结论入口：[FINAL_CONCLUSION.md](FINAL_CONCLUSION.md)。正式 C1/C2/C3 全失败，Frontier 未运行；唯一 materiality 探索也未通过预定目标。

## 记录

- `TASK.md`：用户原任务；`PROTOCOL.md`、`DESIGN_AUDIT.md`、`FROZEN_STATE.md`：调用前设计。
- `bank/`：44 状态 inventory、fresh 排除、24 主样本、9 压力样本、标签、replicate 配对。
- `primary/`、`challenge/`：预冻请求、逐调用原始 journal、输出、指标与报告。
- `exploration/`：唯一 12 checkpoint / 24 call 的事后机制探索，独立冻结，不覆盖 gate。
- `analysis/`：逐条 semantic review、评分脚本、成本、gate、完整性检查。
- `frontier/NOT_RUN.md`：未过 gate，不进入下一阶段。

## 只读复算

从仓库根目录运行，不会产生模型调用：

```bash
python experiments/asymmetric_progress/analysis/packets.py
python experiments/asymmetric_progress/analysis/score.py
python experiments/asymmetric_progress/analysis/diagnostics.py
python experiments/asymmetric_progress/exploration/score.py
python experiments/asymmetric_progress/analysis/integrity.py
```

Review 源码为 `analysis/review_01.py` 至 `review_28.py`，逐条保留理由。各 `runtime.py <stage>` 已有日志时会拒绝重跑。不要用删日志方式重采样。
