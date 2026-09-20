# 交给 Codex：先执行 S0 状态视图节点，不扩展整条链路

目标：按“节点职责→固定输入→单点对照→bad case→下一节点”执行研究笔记与调查状态视图实验。先阅读本包README、全链路排查报告下的《ResearchNotebook与调查状态节点设计与实验》、fixtures/profile和共同actor提示词。S0只比layout；不运行attempt_linkage，不新增Reviewer、自动状态抽取、检索执行、E1或停止器。

## A. 离线准备

遵守仓库AGENTS.md（如有），保存当前提交/工作区状态，保留已有修改。不要打印密钥或.env。当前任务真正授权API实验后再运行execute；只有代码审查任务时只做离线检查。

1. 安装已有requirements-chat，运行新增test_investigation_state以及旧test_need_review测试。新增测试中的真实归档检查在完整仓库不应被skip。
2. 用全新目录prepare。程序要成功验证3个checkpoint原始blob、自校验hash、所有quote和引用。目录定位见fixtures；不要读取相邻答案、完整未见语料或未来事件来修正输入。
3. 逐项读夹具及其来源：observed_finding是否归属正确主体；原题是否只描述未知目标；hypothesis是否仍被标为假设；task是否局部且没有泄露最终答案。不要只检查引文字符串出现。
4. 夹具作者已知旧bad case，不宣称盲评或留出集。填写实际fixture review声明，另存而不伪造先前时间。若夹具有错，先修改夹具和相应文档/测试，再重新prepare并记录版本；不能付费运行中修正。
5. 复制profile示例到本批单独文件，核对当前API支持。8192/180是未验收候选，不代表关闭reasoning或最优参数。不要把旧enable_thinking字段带回。

## B. 交付pilot：6次Actor，0 Reviewer，0工具

按README用3题、2视图、1重复生成purpose=pilot的冻结计划。记录计划hash和预期调用数。无额外隐藏smoke。只使用plan中模型、端点、预算、超时与采样配置。

运行execute后即使退出非零，也审计新目录，不立即重跑：

```bash
status=0
python -m experiments.research_state.investigation_state.run execute \
  --prepared /tmp/esr-state-prepared --plan /tmp/esr-state-pilot-plan.json \
  --env-file .env --output experiments/research_state/investigation_state/runs/pilot_UNIQUE_ID || status=$?
printf 'pilot exit=%s\n' "$status"
python -m experiments.research_state.investigation_state.run audit \
  --run-dir experiments/research_state/investigation_state/runs/pilot_UNIQUE_ID \
  --output /tmp/esr-state-pilot-review
```

实际路径用本批唯一命名，不能覆盖旧产物。pilot只验交付、请求一致性和成本，不以语义分数决定哪些题进入正式批。若API超时、reasoning-only、未知字段或finish_reason不兼容，先报告原因；可以提出另一次单变量接入修正，但不在当前批内重采样/补成功。原reasoning不能拼成正文，工具调用不能私自执行。

## C. 正式S0：12次Actor，独立于pilot

同bundle、profile、提示词、代码/SDK和comparison下，使用--accepted-pilot与--fixture-review构建purpose=formal、repeats=2计划。程序会拒绝mock、交付不完整或成本不明的pilot。只改变重复数是计划设计，不复用pilot响应凑正式样本。

执行并保留所有12分支，包括API错误、非法协议、截断、受阻和自然作答。没有自动回退到原历史，也没有Reviewer失败后的“隐含对照”。完整工具批次全部记录但不执行。中断后未运行项保留在计划分母；不隐式resume。

## D. 逐节点分析

先读prefix_cards并记录允许的多种下一动作，然后看cards完整content和每个工具调用，最后才用private_key做配对。需要原始请求时回读对应分支。尽量减少组名影响，但不要称严格盲评。

保留机器summary；在新文件填写人工/代理辅助语义标签并说明评价者。不自动用重复字符串或多搜几个词判断好坏。引用合法不等于事实成立；同主题query不等于使用了调查的纠偏理由；没有新工具结果就没有召回/最终正确率。

每题每次都写：原题限制→实际原文→笔记/当前任务→下一动作→未决内容→归因。至少给1个正向、1个负向或不确定病例；没有正向时如实写没有。不挑每题两次中的最好结果。

主指标是完整响应合理性。分开来源身份、主体/时间/作用域、调查目的是否被使用、重复是否有新目的、正文无据断言、提交是否有据。形式错误不能算不存在的语义判断；执行成功也不能等于任务成功。

## E. 交付及下一步

在本次新run目录保存计划、源码、原始请求/响应、审计、成本、标注和中文报告；在全链路排查报告新增本轮结果入口，旧报告不改。报告明确pilot与正式总调用/已知token下界/未知成本、两个视图的实际输入差、全部失败分母和局限。

结论只能关于固定夹具下的视图；不能报告自动State收益、ESR效果或BC+准确率。若T未改善F，不通过增字段/换提示词掩盖；若T有效但仍重复，下一提案才是S1；合理动作后下一提案才是真实工具单步实验。后续阶段不自动执行。

提交前检查diff没有.env、密钥、权重、数据库或无关文件。本任务授权推送时提交并推送结果，提供提交和一处下一修改建议。未执行的模型调用/测试不得写成通过。
