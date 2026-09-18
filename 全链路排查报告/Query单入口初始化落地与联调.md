# Query 单入口初始化落地与联调

单入口初始化已实现，原题引用、一次 Search、完整轨迹和后续 Open 的交接均完成验证。它目前仍是独立实验候选，没有替换默认 Agent。新的引用接口减少了本批次摘录修复，但最小改写提示词仍出现关系和时间问题；执行完成不能作为语义通过。

## 1. 从上轮问题到本次实现

上轮结构化初始化要求模型生成 goal、逐字摘录和 query。摘录存在修复成本，goal 也可能先发生关系错误，再传给 query。双方向没有显示稳定优势，因此本轮固定单入口、一次 Search，逐步检验接口简化。

实现位于 [single_entry](../experiments/query_initialization/single_entry/README.md)，主链路为：

```text
完整问题 → 原文编号 → 模型选择依据并生成 query → 确定性校验 → Search → 原文观察交接
```

原题只增加机械定位编号，不生成语义约束摘要。模型同时看到完整问题及原文单元，输出 basis_refs，不再抄写原句或计算字符位置。换行、明确行内项目符号和保守句末构成边界；常见缩写保持在较大单元中。不确定边界不强行切小，引用可以跨单元。全库 830 道题均能无损映射，编号本身不代表独立约束。

候选输出为零或一个 intent，每条只有 basis_refs 和 query。query 上限仍为 512 字符，API 输出上限 1536 tokens，最多一次格式修复；空计划、截断和失败不退回整题搜索。代码验证的是结构与引用存在性，不判定语义忠实性。

原文窗口仍使用 baseline：top6，每个标题加正文最多 400 tokens，总上限 2400。没有改变 Search–Open、增加 focus、注入观察摘要或引入 candidate/gap/replan。

## 2. 为什么分成四个阶段

|阶段|输出|变化|
|---|---|---|
|v2|goal + source_clues + query|现有单方向 B 组|
|refs_goal|goal + basis_refs + query|摘录改为编号引用，同时加入编号后的原题输入|
|refs|basis_refs + query|移除 goal 及对应字段指令，保留原选择与改写原则|
|minimal|basis_refs + query|改用单入口、保留关系、最小改写提示词|

v2 的引用由 harness 从合法摘录位置映射，明确标记为 runtime_mapped_exact_quotes，其余是模型选择，不能混淆。前三阶段使用 directions 根字段，最终候选为 intents，harness 将它们映射为同一种交接结构。

各阶段仍允许自主选择入口，所以结果同时受到入口选择和具体表达影响。引用阶段还改变了模型输入的呈现，不能把差异全部归因于字段名称；本轮不宣称完成严格的单因素语义因果识别。

## 3. 实际运行

运行模型为 qwen3.7-flash，thinking=false，SDK 自动重试为零，timeout=120 秒。API 四线程并行，本地检索单线程共享模型与索引。

开发题为 786、551、1072、1117、583、591、645、183，均是已知题。每组每题一次，共 32 次尝试、33 次实际 API 请求，没有使用新的留出集，也没有把标准答案输入模型。

|指标|v2|refs_goal|refs|minimal|
|---|---:|---:|---:|---:|
|尝试数|8|8|8|8|
|首次合法|7|8|8|8|
|修复请求|1|0|0|0|
|执行完成|8|8|8|8|
|Search 次数|8|8|8|8|
|返回窗口|48|48|48|48|
|API total tokens|11,095|10,753|10,129|8,700|

全部共 40,677 API tokens。没有工具执行错误。192 个窗口的来源哈希、原文区间、标题、边界标记、预算、事件时序和账本一致性均通过审计。

最终测试 73 passed，三条既有依赖弃用警告。真实运行还打印了 SciPy 对当前 NumPy 版本的兼容性警告；本批检索执行成功，未因此修改依赖环境。

## 4. 接口是否真的能交给后续节点

handoff.json 保存原题与 SHA-256、定位表、attempt_id、生成计划、实际查询参数、执行状态、原始返回和窗口引用。observations.sqlite 持久化原文版本与已返回窗口。编号不依赖模型维护，失败同样保存完整轨迹。

验证在新进程中复制每个 minimal 会话的账本到临时目录，恢复其第一个返回窗口，再调用现有 Open(around)。8/8 恢复成功，来源版本保持一致，返回文字仍与持久化原文区间相符，没有新增 API 请求，也没有修改原运行账本。

这证明下游能够继续读取已有来源，不证明模型会主动选择 Open。当前还没有把 handoff 自动转换成后续研究模型的 messages 或 ResearchState，这部分留给后续节点；不能将观察交接称为完整研究链路已经通过。

## 5. 初步检索复核

沿用上轮保存的原文正例与参考区间，检查本次是否再次取得对应来源，以及参考依据是否实际可见：

|保守计数，每组 8 次|v2|refs_goal|refs|minimal|
|---|---:|---:|---:|---:|
|取得已有确认入口文档|4|5|4|5|
|实际展示已有参考依据|3|5|3|3|

这是固定正例集合的复核，不是本轮全部结果的完整相关性标注。qid=645 不在此前正例池范围，其他未匹配文档也不能被视为无关。每题只有一次重复，没有统计显著性判断。

最终候选没有在这个指标上超过旧版。保留 goal 的引用阶段反而计数最高，因此不能宣布“删除 goal 已被证明更好”。API tokens 下降和格式修复减少，也不替代入口质量。

### qid=583 与 qid=183：出现可继续研究的来源

minimal 在 qid=583 选择艺术家采访线索，保留别名、童年经历、圆形图案、人类行为与 2012 年，取得文档 996。qid=183 选择教学经历博客，取得文档 90095。对应原文参考依据可见。

这里的 query 并不极短。多个条件仍共同描述同一个入口，这符合“单入口而非单关键词”的设计。但不能只凭两题断言选择策略已经稳定。

### qid=1072：忠实表达仍可能失去有效入口

minimal 保留了出生年和议员任期，生成：

```text
author born in 1964 served as lawmaker from 2004 to before 2010
```

它没有召回此前核实的文档 69382。v2 和 refs_goal 包含 international organization / research paper，均返回该文档。这个差异提示，需要检验“缩小到单条线索”是否删掉了有辨识度的辅助信息；目前尚未通过固定 query 的词语增删实验确定因果。

### qid=551 与 qid=1117：最小改写并未自动保持关系

minimal 的 qid=551 仍写出 retired 2020，省略原题的 as of/by，存在被解释为确定退役年份的风险。

qid=1117 更明确：原题是 Major 配偶的兄弟姐妹，query 却写成 sibling of Major。引用 q2/q3 都合法，实际关系仍错。

这些错误不会被结构校验发现；代码没有擅自把它们修正成另一个 query。原始错误已保存为下一轮表达验证的开发样例。

### qid=786：换入口避开错误，不等于修好了原关系

v2 再次将“目标人物与侄子拍短片”接到另一位导演。minimal 改为只找相关导演，没有拼接侄子关系。

这次输出避免了原来的错误组合，但搜索对象也改变了，不能据此证明模型已经能正确表达那条侄子关系。refs 阶段则只查询 Perfectly formed，返回泛化的 perfection 内容，表明去掉 goal 后也可能过度压缩入口。

### qid=645：引用合法与依据完整必须分开

minimal 写明 Farjon authors the first reference，没有像 refs_goal 一样把 Farjon 明确当作目标研究作者，这是本次可观察到的改善。

但它只引用 q4，query 中的 Mediterranean 实际来自 q2。这个信息存在于完整原题，并非凭空添加，却没有被 basis_refs 完整覆盖。引用存在性校验不能证明引用覆盖了 query 的所有事实，也不能作为后续方向身份或已验证条件的依据。

## 6. 当前决定

工程接口保留，默认 Agent 不升级。本次主要完成了可运行、可审计、可继续 Open 的单入口节点，尚未达到语义策略冻结标准。

后续优先使用本批开发题做固定线索的表达对照，隔离“选哪条线索”和“怎么表达”。重点检查姻亲/作品关系、时间边界、过度删减，以及 basis_refs 是否遗漏 query 所依赖的原题位置。当前不增加语义 verifier，不把引用编号升级成约束图，也不继续增加 Search–Open 窗口规则。

在表达策略固定后，再抽取新题做留出验证。现阶段没有依据自动进入大规模留出或完整 rollout。

## 7. 复核材料

- [代码与运行方法](../experiments/query_initialization/single_entry/README.md)
- [32 次完整轨迹索引](../experiments/query_initialization/single_entry/runs/20260918T062309.405859Z/README.md)
- [机械审计](../experiments/query_initialization/single_entry/runs/20260918T062309.405859Z/audit.json)
- [逐题语义审阅](../experiments/query_initialization/single_entry/runs/20260918T062309.405859Z/semantic_review.json)
- [已有参考片段复核](../experiments/query_initialization/single_entry/runs/20260918T062309.405859Z/reference_recheck.json)
- [重启后 Open 验证](../experiments/query_initialization/single_entry/runs/20260918T062309.405859Z/handoff_verification.json)
