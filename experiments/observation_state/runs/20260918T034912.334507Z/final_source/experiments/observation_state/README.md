# 新题边界与观察管理实验

验证范围为 Search–Open 的原文呈现、区间记账和状态恢复。当前不评价完整 BC+ 答题准确率，不使用 gold 生成 query，也不修改工具描述或系统提示词。

本轮结果与完整轨迹见 [20260918T034912.334507Z](runs/20260918T034912.334507Z/README.md)。分析见 [节点报告](../../全链路排查报告/Search-Open新题边界验证与观察管理.md)。

## 复现

在仓库根目录执行，使用已配置 API、Qwen3-Embedding-8B 模型及 BC+ 索引：

```bash
python experiments/observation_state/prepare_new.py
```

脚本先保存预选题目和实验范围，再调用 API、检索文档。记下输出的 `OUTPUT_DIR`，以下以 `<run-dir>` 表示。前两条是离线审计；live 会实际请求 API 并产生费用。

```bash
python experiments/observation_state/audit_boundaries.py <run-dir>
python experiments/observation_state/run_live.py <run-dir>
python experiments/observation_state/audit_live.py <run-dir>/live
```

`run_live.py` 选前六道预选新题、两组窗口、各一次运行。每次预置真实首轮 query 的 top5 返回，再允许四轮后续工具调用和强制终答。两组均接入不可见的观察账本。没有改变全量 rollout 默认的 64 轮预算。

单独补充或重试可执行：

```bash
python experiments/observation_state/run_live.py <run-dir> 905 table_entry_safe
```

这会创建独立的 `live_retry_<UTC>` 目录，保留此前失败。每次 live 运行保存源码副本、哈希、请求参数、完整请求响应、工具观察、答案及恢复检查。

`check_safe.py <run-dir>` 是针对本次发现的回归脚本，依赖归档的 `live/qid_905__table_entry/structural_changes.json` 和既有局部任务集，不是任意新 run 的通用评测入口。机械审计必须使用新的输出目录和观察数据库，避免跨运行累计覆盖。

```bash
python -m pytest -q tests experiments/structural_boundary/test_candidate.py
```

模型 API 有随机性和服务端失败，重跑不保证同一 query、轨迹或终答。固定区间与代码回放的结论应和真实 API 行为分开报告。
