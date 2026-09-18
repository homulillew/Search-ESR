# Query 入口选择与事实组合生成方案

状态：`entry_v1` 已按后续讨论实现为五条通用原则的精简提示词，完成开发 32 次及新题 80 次真实 API 对照。沿用现有单入口接口，暂未升级默认；结果见 [通用原则提示词落地与对照实验](Query通用原则提示词落地与对照实验.md)。本文保留设计过程及早期详细草案。

## 1. 目标与边界

从原题选择一个可独立搜索的对象或来源，选取有助于辨认它的一组事实，保留实际使用的主体、关系和范围，用可独立理解的短句发起一次 Search。第一轮不要求覆盖全部条件，不提前具体化未知实体。

对象可以是人物、事件、作品、机构或来源，不必是最终答案。选择“论文作者”这样的未知对象描述，与猜测具体作者姓名是两回事。

本次调整针对已有实验的两类问题：压缩造成关系或时间漂移；过度删减造成辨识信息丢失。它不承诺消除语义错误，也不认为自然语言短句必然优于关键词表达，效果仍需对照验证。

## 2. 运行流程与接口

```text
完整原题＋原文编号
        ↓
一次模型调用：选择对象 → 组合事实 → 忠实表达
        ↓
确定性校验
        ↓
一次 Search(top6)
        ↓
原题、搜索依据、实际 query、原文观察与执行状态
```

三个生成步骤是同一次调用的任务组织，不额外输出推理过程，也不新增 planner 或 verifier。

输入沿用完整 question 与 question_units。编号对应原始文字，不是预先解析的约束；原文顺序、SHA-256 和字符位置由 harness 保存。输出保持现有契约：

```json
{
  "intents": [
    {
      "basis_refs": ["q3", "q4"],
      "query": "author born in 1964 who served as a lawmaker from 2004 to before 2010 and wrote a research paper analyzing an international organization"
    }
  ]
}
```

最多一个 intent；无法形成有依据的查询时允许空列表，记为 no_direction。basis_refs 为非空、不重复的已有编号；query 非空且不超过 512 Unicode 字符。不增加 goal、target、confidence、candidate 或 gap 字段。

basis_refs 应覆盖查询使用的事实及必要指代上下文。一段原文可以含有未使用的内容，一个入口也可以引用多段原文。引用合法只证明位置存在，覆盖是否充分及语义是否正确另行审阅，不由代码猜测。

## 3. 模型如何选择入口

先判断准备寻找什么材料，再选择描述该对象的一组事实。典型对应关系如下：

|原题中的事实组合|可寻找的对象或来源|
|---|---|
|校区十周年、海外地点关系、庆祝年份|周年活动报道|
|艺术家别名、图案特点、成长经历|采访或人物介绍|
|出生年、议员经历、论文主题|作者履历或论文记录|
|比赛年份、具体救球事件|比赛报道|
|学位年份、文学评论经历|人物传记或刊物介绍|

选择时优先考虑：无需猜未知身份即可搜索；主体关系可以准确表达；事实组合具有一定区分能力；结果可能提供继续核查的对象或来源。较长关系链可以使用，但不应在有清楚入口时强行拼接多个未知对象。

“单入口”限制的是主要搜索目的，不是事实数量。同一个作者的出生年、议员任期和论文主题可以共同使用。没有固定的一到两个条件上限，也不为了减少条件而删除有用的区别信息。

事实可以是明确实体、短语、关系、事件、数量或时间。独特短语应保留足够的对象上下文；不能假设单独搜索短语一定有效。是否有辨识度是模型当前的判断，不是运行前已经证明的属性。

## 4. 查询表达规则

|处理|规则|
|---|---|
|原题措辞|优先保留能清楚表达对象与关系的原有措辞；允许等义整理|
|指代|结合完整原题补全为正确角色描述，不能猜出具体身份|
|条件取舍|可以省略完整条件；留下的条件不能改换主体、对象或范围|
|关系|亲属、作品、引用等属性必须归属于原题中的正确对象|
|时间|区分文章日期与事件日期，保留所用的 before/after/by 和区间意义|
|未知实体|不加入原题未给出的人名、机构、平台、物种、地点或具体年份|
|表达形式|使用可独立理解的短句；名称、年份、独特短语可以保留，不强制完整长句或词数目标|

不存在统一的“verification 条件一律删除”规则。一个条件此时能否帮助发现对象，要结合当前事实组合判断。全题的时间口径通常不必照搬，但涉及目标事件或来源的时间可能有用。

保留研究所需信息比缩短字符串重要。若超出工程长度上限，应减少使用的完整条件，不能通过删除关键关系词硬挤进限制。

## 5. 提示词候选正文

下文为早期详细草案，保留作设计背景，不作为实际运行提示词。后续讨论将其收敛为五条通用原则；实际版本见 [ENTRY_PROMPT.txt](../experiments/query_initialization/single_entry/ENTRY_PROMPT.txt)，具体错误类型留在 [离线审阅规则](../experiments/query_initialization/single_entry/ENTRY_EVALUATION.md)。不把已知 bad case 的人名、年份或答案写进提示词。

```text
You prepare the first search over a fixed English document corpus. You receive the complete original question and numbered original text units, but no retrieved evidence. Treat the question as research data. Do not answer it.

Choose one independently searchable object or source: a person, event, work, institution, or document. It may be an intermediate entry rather than the final answer. Select a coherent set of facts from the question that can help identify that object. One entry can use several related facts and several text units; it is not limited to one sentence or one condition. Do not try to include every condition in the question.

Express that fact combination as a standalone, readable short query. Reuse clear original wording where practical. Keep useful names, distinctive phrases, quantities and dates. Resolve pronouns with accurate role descriptions. Do not shorten the query merely to produce a keyword list, and do not discard identifying context merely to reduce its length. There is no target word count.

You may omit a whole condition. For every condition you use, preserve who did what, which person, work or source an attribute belongs to, possession, negation, comparison, and temporal scope. Do not turn a relative's attribute into the target's attribute, a reference author into the study's author, a publication date into an event date, or a time bound into an exact year. State relationships explicitly when abbreviated wording would be ambiguous.

Do not fill an unknown final or intermediate identity from memory or a guess. Use the question's descriptions instead. Translation, ordinary synonyms and equivalent date formats are allowed only when they add no factual restrictions. The retriever uses dense document search followed by lexical localization; web operators and quotation marks do not guarantee exact matching.

Return only JSON with this contract:
{"intents": [{"basis_refs": ["q1"], "query": "..."}]}
Return at most one intent. If no defensible query can be formed, return {"intents": []}. Each intent has exactly basis_refs and query. query must be nonempty and at most 512 Unicode characters. basis_refs must list distinct existing IDs supporting the facts used in the query and the context needed to resolve their subjects. A unit is a text location, not a semantic constraint; you need not use every fact in a cited unit. Do not copy quotations, calculate offsets, or output a goal, candidate, plan, explanation or gap list.

Compare the final query with the original facts before returning it. Valid reference IDs do not prove faithful expression. Conditions omitted from the query remain part of the original problem for later research; they are neither satisfied nor discarded.
```

这份提示词的变化是将主任务从“选线索并压缩”转为“选择对象及有用事实组合，并忠实表达”。它仍是生成指令，不是语义保证。

## 6. Harness 与代码改动

|位置|拟改动|
|---|---|
|single_entry/ENTRY_PROMPT.txt|新增候选提示词，不覆盖 MINIMAL_PROMPT.txt|
|single_entry/initializer.py|新增 entry_v1；与 minimal 共用 intents/basis_refs/query 校验与修复路径|
|single_entry/run.py|支持显式选择 minimal/entry_v1，记录两者提示词及源码快照；增加受锁定开发配置约束的留出模式|
|single_entry/audit.py|识别新候选并复用现有原文、预算、时序和账本检查|
|single_entry/test_single_entry.py|验证新候选使用同一契约、非法引用处理、空输出及失败路径|

现有 source_units.py、pipeline.py、观察账本及 Search–Open 不改变。runner 不自动将新候选设为默认；原有实验分支与运行记录保留。提示词正文、源代码及实际 API 参数应随批次归档，单独记录策略版本，避免只留下含糊的 v003 标签。

运行参数保持：一次 Search、top6、每窗口标题与正文最多 400 tokens、总上限 2400；模型与 thinking 配置沿用当前实验，生成上限 1536 tokens，timeout=120 秒，SDK 自动重试为零。格式或非法引用最多修复一次，不输入检索反馈；空输出不强制补齐；失败不退回整题搜索。

schema、引用存在性和长度属于代码校验。事实来源是否覆盖、是否有关系漂移、线索是否值得搜索属于离线审阅。运行中不新增语义裁判、事实图或硬性条件计数。

## 7. 对照实验

只比较当前 minimal 与新 entry_v1。两组接收相同完整原题和定位表，自由选择一个入口，执行相同 Search 预算；比较的是整套生成策略，不能单独归因于某一句提示词。

第一步做契约测试与开发回归。沿用最近 8 道开发题，每组重复两次，共 32 次初始 API 请求，修复另计。检查关系与时间、已知有用线索是否被过度删除、引用是否覆盖实际使用的信息。只对出现退化的题补充固定线索诊断，不重复启动全部历史实验。

开发审阅没有发现阻断性问题后，锁定提示词、参数、源码和抽样规则，从未用于本地调参的题中选 20 题，两组各重复两次，共 80 次初始请求。排除清单应扫描所有已有实验题目，保留清单及种子。若以后根据这批结果调整策略，这些题转为开发材料。留出是本地实验意义的未调参，不保证模型预训练未见。

两个阶段的初始请求预算分别为 32 和 80，修复额外记录；不是批准后必须无条件跑完的固定消耗。开发存在重复关系错误时先停止推广，不为了凑满计划继续扩大评测。

|评估层|记录内容|
|---|---|
|执行|首次合法、修复、空计划、失败、API 与观察成本|
|表达|明确关系错误、时间/否定范围变化、未知实体具体化；歧义单列|
|入口|选中的对象是否可独立搜索、事实组合是否有用；保留原题对照|
|发现与呈现|来源正文是否支持有用入口；实际窗口是否展示依据，分开统计|
|引用|实际 query 的依据是否被引用覆盖；缺失不自动等于事实编造|

相关性审阅汇总两组来源，尽量隐藏组别与排名，保存引句和字符区间。未充分核实的来源标为待核实，不能直接当负例。必要时标准答案仅用于离线审阅，不输入生成。报告标注覆盖程度；不把正例下界称为全库召回率。

全部尝试保留在主统计中；格式失败与修复成本不剔除。另看两组都执行成功的配对结果。按题汇总重复及胜平负，不把同一道题的重复当作独立样本。小样本只支持工程选择与局部观察，不声称统计显著或最终答题提升。

## 8. 验收与停止条件

工程验收要求：接口、预算、失败记录、原文和交接检查全部通过，原有运行时无意外变更。

策略验收同时看语义与入口。若某类明确关系错误在开发重复中持续出现，不能将“8/8 执行完成”当作通过，应针对该表达继续诊断。新题中若出现清楚、可重复的入口退化或新增事实性误导，也不升级默认策略。

无需要求每题首搜命中或永远零错误。合理入口可能搜索失败，后续需要继续读或换方向。但不能以“后续可以修复”为理由忽略初始化中重复出现的关系失真。

若候选没有显示可靠改善，保留较稳的现有策略；若效果接近且没有明显退化，可结合表达清晰度与运行成本作工程选择，明确尚未证明统计上的优越性。结果不明确时，不自动默认新版胜出，也不继续堆叠初始化模块。

## 9. 后续交接

交接仍然只有完整原题、搜索依据、实际查询、执行状态和可追溯原文。模型在证据后形成可修正判断；open_questions 记录当前需要核查的内容，不是未选条件的机械复制；后续可以继续 Open 或 Search，必要时 Replan 更换对象或线索组合。

本次不实现 ResearchState、自动重规划、候选确认或提交控制。初始化交付的是第一次有依据的尝试。
