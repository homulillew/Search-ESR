# 观察摘要最小对照

比较后台账本不可见与模型收到机械观察摘要。生产默认不启用此摘要。当前版本在局部阅读控制上出现回归，不应直接升级默认。

- [预设方案](PLAN.md)
- [结果与轨迹](runs/20260918T045524.575952Z/README.md)
- [分析报告](../../全链路排查报告/Search-Open观察摘要最小对照.md)

从仓库根目录执行：

```bash
python -m pytest -q experiments/observation_summary/test_summary.py
python experiments/observation_summary/run.py
python experiments/observation_summary/audit.py <run-dir>
```

`run.py` 创建独立 UTC 目录，保存预选任务、40 次会话的固定随机顺序和源码快照，再实际调用 API。依赖当前模型、语料库、API 配置及上一轮归档首轮返回；后续检索真实执行。也可以给 `run.py` 传入不存在的输出目录。

每次最多四轮后续工具调用及强制终答，输出上限 2048 tokens，无自动重试。失败保留。`audit.py` 重新生成摘要、核查原文与实际请求、计算全部尝试及完整配对指标。它不会自动评价全部语义主张。

`review_blinded.json` 隐藏会话组名供进一步审阅，`review_key.json` 保存映射。本次人工审阅者已看过组别，因此 `manual_controls.json` 不声称独立盲评。核心事实和新增摘录通过原文位置检查，其他解释错误单独备注。
