# Query 初始化节点

已完成 [BasisPacket 固定原文四组实验](basis_packet/README.md)：54 次真实 API、48 次 Search，12 次合法弃答。输入与来源交接通过，保守 Compiler 尚无稳定收益，自动 Selector 未测试；当前默认未修改。见 [结果报告](../../全链路排查报告/BasisPacket固定原文与保守编译对照实验.md) 与 [设计](../../全链路排查报告/BasisPacket与保守查询编译设计.md)。

新增候选：[入口选择与事实组合生成方案](../../全链路排查报告/Query入口选择与事实组合生成方案.md)。沿用单入口接口，entry_v1 使用五条通用原则；先与 minimal 做开发对照，不自动升级默认策略。

最新结果：[通用原则提示词落地与对照实验](../../全链路排查报告/Query通用原则提示词落地与对照实验.md)。已完成开发 32 次及新题 80 次真实 API 调用。成本下降，质量优势尚未得到支持，默认策略未替换。

后续诊断：[固定线索的完整表达、整体删除与模型压缩对照](fixed_anchor/README.md)，7 题、35 次检索，检查表达阶段错误与辅助线索价值。

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

## Selector 原文选材的新题对照

[实现与配置](selector_verbatim/README.md) · [60 次完整轨迹](selector_verbatim/runs/20260918T085353.300461Z/README.md) · [结果与根因分析](../../全链路排查报告/Selector原文选材与整题检索对照实验.md)

本轮 20 题比较整题原文与 Selector 选材后直接检索，不使用 Compiler。40 次 API、60 次 Search 完成，机械审计及账本恢复 Open 通过。代理辅助审阅下，来源命中 45%→47.5%，可见依据 45%→45%；重复改善与退化并存，未默认启用 Selector。审阅方法及预注册表述差异见报告，不称人工金标或完整召回率。

## 模型自主探索的提示词对照

[实验说明](exploratory_policy/README.md) · [80 条完整轨迹](exploratory_policy/runs/20260918T092827.910487Z/README.md) · [分析报告](../../全链路排查报告/Query探索原则提示词两步对照实验.md)

复用上述 20 道开发题，当前提示词与追加三句探索原则各重复两次，观察首搜及下一步 Search/Open。首步可见依据 35%→40%，两步累计 40%→45%，第二步严格新增依据 35%→32.5%。保留当前默认提示词，不新增 Selector/Compiler，结束本轮 Query 局部优化；下一设计节点转向观察如何形成可修正的研究判断并驱动行动。本轮补充了返回池审阅，不能与旧实验百分比直接拼成三组排序。
