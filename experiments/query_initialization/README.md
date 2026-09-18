# Query 初始化节点

最新：已落地 [v003 单入口与原题引用](single_entry/README.md)，完成 8 道开发题、四阶段共 32 次真实 API 联调，仍保持独立实验。见 [落地报告](../../全链路排查报告/Query单入口初始化落地与联调.md)。

已实现并完成真实 API 局部对照，当前为独立实验候选，未替换默认 Agent。v001、v002 开发各 12 次；v002 留出 20 题、A/B/C 各重复两次，共 120 次。包括修复在内合计 163 次 API 请求。

- [节点设计与实验方案](../../全链路排查报告/Query初始化节点设计与实验方案.md)
- [首轮结果与根因分析](../../全链路排查报告/Query初始化首轮对照实验.md)
- [初始化提示词 v0.2](INITIALIZER_PROMPT.md)
- [v001 开发](runs/20260918T053308.889887Z/README.md)
- [v002 开发](runs/20260918T053531.523685Z/README.md)
- [v002 留出与全部轨迹](runs/20260918T053659.834656Z/README.md)

范围：从原题生成 goal/source_clues/query，确定性校验后执行首轮 Search，保存原文观察。未接入 candidate、gap、REPLAN 或完整回答评估。

A 为当前 Agent 第一个 Search query，B 为单方向改写，C 为双方向改写。A/B top6，C 各 top3；每个窗口标题与正文不超过 400 tokens。冻结原窗口与检索器。A 的首次响应受本轮 1536 输出 tokens 上限约束；B/C 最多一次格式修复。

结果：A/B/C 各 40 次中有 34/39/37 次完成检索；人工核实参考片段可见计数为 11/13/13。后者是正例池的保守计数，尚未完成穷尽相关性标注，不能当作全库召回率。没有稳定证据支持替换默认方案。

## 文件

|文件|用途|
|---|---|
|initializer.py|生成、结构与原题子串校验、一次修复|
|run.py|四线程 API、共享检索器、固定预算、完整归档|
|audit.py|原文/标题/预算/时序/账本机械审计|
|review_cards.py|离线阅览辅助，可读取答案，不参与在线生成|
|score_review.py|从人工原文标注计算可见区间与题目配对计数，不产生自动语义判断|
|test_initializer.py|确定性契约测试|

## 运行与复核

从仓库根目录执行。以下 run 命令会产生新的 API 调用；凭据沿用现有环境配置。

```bash
python experiments/query_initialization/run.py --phase dev
python experiments/query_initialization/run.py --phase holdout --dev-run experiments/query_initialization/runs/20260918T053531.523685Z
```

留出命令要求开发批次存在 `dev_review.json`、允许进入留出，并且当前 initializer.py 与提示词哈希匹配开发快照。排除清单会纳入既有运行题目，因此再次运行会选择新的题目，不会自动重跑旧清单。原运行的确切题目和顺序见各自 tasks.json、schedule.json。

以下命令只复核已完成数据，不调用模型：

```bash
python experiments/query_initialization/audit.py experiments/query_initialization/runs/20260918T053659.834656Z
python experiments/query_initialization/score_review.py experiments/query_initialization/runs/20260918T053659.834656Z
python -m pytest -q tests experiments/structural_boundary/test_candidate.py experiments/observation_summary/test_summary.py experiments/query_initialization/test_initializer.py
```

人工标注为离线附件，没有回流到在线提示词。新版本继续优化时，本批题目应转为开发材料。
