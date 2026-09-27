# Search-ESR：Source-Anchored Task Skeleton / Ephemeral Obligation Decomposition 实验任务书

## 0. 实验总目标

本轮只研究一个问题：

\[
\boxed{
Q
\rightarrow
\text{Task Skeleton}
}
\]

即：

> 给定一个复杂 Original Question，模型能否在**不依赖当前 Claims、Hypothesis、Path、Search 历史**的情况下，把原题转换成一个稳定、局部、覆盖充分、关系保真的任务骨架？

本轮不是：

```text
Q + C → next obligation
```

也不是：

```text
Q + C → Gap
```

更不是完整 Agent。

本轮只验证：

\[
\boxed{
\textbf{Question Understanding / Task Canonicalization}
}
\]

---

# 1. 研究动机

已有实验已经形成以下链条。

## 已观察到的正向结果

当局部任务范围由人工正确固定时：

\[
GoldO+C\rightarrow Gap
\]

开发集：

```text
Strict Gap Validity ≈ 92.6%
```

说明：

> 给定正确 reference 后，根据 Claims 判断当前缺失证据，相对容易。

---

## 已观察到的负向结果

模型自己做：

\[
Q+C\rightarrow O
\]

Strict 长期只有约：

```text
46%–54%
```

主要错误：

```text
whole-question / bundled broadness
downstream obligation
relation strengthening
wrong relation arguments
wrong object/date scope
```

---

## Context Sufficiency Ablation

进一步加入：

```text
Recent Claim Delta
Recent Path
Recent Observation
```

仍然没有形成可靠 Direct-O：

```text
C0 strict = 46.3%
C1 strict = 48.1%
C2 strict = 48.1%
```

Recent state information主要改变：

```text
selection stability / salience
```

没有稳定解决：

```text
semantic correctness
dependency ordering
relation fidelity
```

因此当前最合理的工作假设是：

\[
\boxed{
\text{主要瓶颈位于}
\quad
Q\rightarrow\text{local task semantics}
}
\]

而不是：

```text
Gap comparison
Path availability
Claims freshness
```

---

# 2. 当前根因假设

原始问题：

\[
Q
\]

是高度压缩的自然语言 requirement structure。

当前系统每轮实际上都在隐式执行：

\[
Q
\rightarrow
\hat R_t
\rightarrow
Align(\hat R_t,C_t)
\rightarrow
O_t
\]

问题是：

\[
\hat R_t
\]

每轮都可能不同。

于是产生：

```text
argument drift
role merging
date movement
relation strengthening
dependency jump
granularity drift
```

本轮验证新的机制：

\[
\boxed{
Q
\rightarrow
R
}
\]

其中：

\[
R=\{R_1,\ldots,R_k\}
\]

表示一个相对稳定的 Task Skeleton。

未来才可能：

\[
R+C_t
\rightarrow U_t
\]

\[
U_t+\Delta C_t
\rightarrow O_t
\]

但这些全部不在本轮范围内。

---

# 3. 最新远程基线

开始前必须：

```bash
git fetch origin --prune
git status
git branch --show-current

git rev-parse origin/main
git rev-parse origin/experiment/obligation-context-sufficiency

git log --oneline --decorate -20 \
  origin/experiment/obligation-context-sufficiency
```

任务编写时最新：

```text
origin/experiment/obligation-context-sufficiency
fc0746930edc4ad8aad4c8a04a5f2a138d1b5082
```

latest commit：

```text
Report context ablation stability signal with persistent projection failures
```

如果远程已经前移：

1. 阅读所有新增 commit；
2. 判断是否已有同类 decomposition experiment；
3. 写 `PRE_EXECUTION_AUDIT.md`；
4. 不允许静默从旧 SHA 开始。

---

# 4. 新建实验分支

建议：

```bash
git switch -c experiment/ephemeral-obligation-decomposition \
  origin/experiment/obligation-context-sufficiency
```

新目录：

```text
experiments/ephemeral_obligation_decomposition/
```

不得修改历史实验。

---

# 5. 本轮最重要的设计原则

## Principle A — Task semantics 与 research dynamics 分离

本轮只看：

\[
Q
\]

不输入：

```text
Claims
Hypothesis
Recent Claim Delta
Recent Path
Recent Observation
Workspace
Search results
Gold Obligation
Gold Gap
```

因为本轮要回答：

> 原题本身到底能不能被可靠理解？

---

## Principle B — 不把 Gold exact decomposition 当唯一答案

复杂问题可能存在多个合理 decomposition。

例如：

```text
R1 + R2
```

可能也可以合法合并成：

```text
R12
```

只要它们仍然构成：

> 一个 coherent object/event/relation episode。

因此评价：

```text
semantic coverage
structural fidelity
granularity
dependency preservation
```

而不是 exact string / exact node count。

---

## Principle C — 少生成，多锚定

当前主要怀疑：

\[
free\ paraphrase
\rightarrow
semantic\ drift
\]

所以本实验比较三个不同自由度的 decomposition。

---

# 6. 开发集不要使用 27 个 state 作为 27 个样本

上一实验 27 个 state 实际只来自 10 个 unique Original Questions。

因为本轮只有：

\[
Q\rightarrow R
\]

同一个 Q 的多个 historical state 是完全相同的输入。

不能把它们当成独立问题。

开发集必须按唯一 qid 去重。

当前 exposed bank 的 10 个 qid：

```text
122
169
228
261
538
637
843
922
971
1259
```

每个 qid 只保留一个 Original Question。

生成：

```text
e0_reference/DEV_QUESTIONS.json
```

---

# 7. 开发集性质必须明确

这 10 个问题属于：

```text
exposed development material
```

因为它们已经在：

```text
Need
Premise
Gold Gap
Dynamic Obligation
Context Sufficiency
```

实验中被反复审阅。

因此：

> E1 只能用于机制开发，不做 fresh/generalization claim。

---

# 8. 预注册 Fresh Confirmation Bank

在任何 E1 API 调用之前，同时冻结一个未来 confirmation bank。

从项目原始 question corpus 中按固定随机种子选择：

```text
12 unique qids
```

要求：

1. 不属于上面 10 qids；
2. 不出现在本项目此前所有明确 experiment bank 中；
3. 是自然问题；
4. 具有多条件、多实体或多事件结构；
5. 不依据预期难度人工挑题；
6. 不看任何未来模型 decomposition 结果后重选。

执行 repository-wide qid exposure audit。

生成：

```text
e0_reference/FRESH_SELECTION.json
e0_reference/EXPOSURE_AUDIT.json
```

这里的 “fresh” 只表示：

> repository-experiment-unexposed。

不得声称：

> foundation model 从未见过。

---

# 9. Fresh Bank 在 E1 前冻结，但只有 Gate PASS 才调用

Fresh 12 题及评价 reference 都必须：

```text
freeze before E1 model calls
```

这样避免看到 development failure 后重新挑题。

但：

```text
E2 paid calls
```

只有 E1 primary Gate PASS 后才允许执行。

---

# 10. Original Question 地址空间

所有三个 arms 必须看到同一份 Original Question 和同一份机械 Source Units。

Harness 为 Q 建立：

```text
Q1
Q2
Q3
...
```

这些 unit 只是：

\[
\boxed{
\text{source address space}
}
\]

绝不代表：

```text
one unit = one requirement
```

---

# 11. Source Unit 的机械切分规则

必须调用前冻结。

推荐：

1. 原始 bullet item 单独一个 unit；
2. 普通句子按原始 sentence boundary；
3. 明确分号可形成独立 sub-unit；
4. 不根据模型/Gold做语义切分；
5. 不在普通逗号、and/or 处强行拆分；
6. 保留原文 verbatim；
7. 每个 unit 保存 char offsets；
8. Question 最终问句也单独可寻址。

例如：

```text
Q1: A research paper was written between ...
Q2: Two people wrote it.
Q3: One has another research paper ...
Q4: As of 2023, one writer ...
Q5: There are six tables ...
Q6: One emotion is at 13.53 percent.
Q7: What is the name of the research paper?
```

再次强调：

> Q1–Q7 是地址，不是人工 Gold decomposition。

---

# 12. Exact Span 支持

除 Q-unit refs 外，D1/D2 允许引用 unit 内 exact source span。

格式：

```json
{
  "unit": "Q3",
  "text": "another research paper in the Journal of Baltic Science Education"
}
```

Harness 验证：

```text
Unicode NFC
+
whitespace normalization
+
exact substring
```

不得 fuzzy semantic matching。

如果同一 normalized span 在 unit 内多次出现：

增加：

```json
"occurrence": 1
```

---

# 13. 三个实验 Arms

本轮开发阶段比较：

```text
D0 Free-form
D1 Source-Anchored
D2 Extractive Grouping
```

---

# 14. D0 — Free-form decomposition baseline

目的：

> 测试普通“请把 Q 拆成 candidate requirements”会达到什么水平。

输入：

```text
Original Question
Addressable Source Units
```

输出：

```json
{
  "requirements": [
    {
      "requirement": "..."
    }
  ]
}
```

不要求 citation。

---

# 15. D0 System Prompt

```text
You decompose one complex research question into a small set of
candidate task requirements.

You receive:
1. the Original Question;
2. addressable Source Units copied verbatim from the Original Question.

Your task is to represent what must eventually be established in order
to answer the Original Question.

This is question understanding only.

Do NOT consider:
- what is currently known;
- what has already been researched;
- search strategy;
- source selection;
- hypotheses;
- stopping;
- priority.

Produce a small set of coherent candidate requirements.

Requirements:

1. Together, the candidate requirements should preserve the material
meaning of the Original Question.

2. Each candidate should describe one coherent object, event, relation,
identity condition, or requested attribute.

3. A candidate does not have to be logically atomic.
Keep complementary conditions together when they jointly identify or
verify the same object, event, or relation.

4. Do not combine independent requirements merely because they contribute
to the same final answer.

5. Preserve relation arguments exactly.
Do not change which entities participate in a relation.

6. Preserve role identity uncertainty.
If the Original Question does not establish that two described roles are
the same person or different people, do not assume either equality or
inequality.

7. Preserve temporal attachment.
A date, interval, sequence, or duration must remain attached to the same
event or object as in the Original Question.

8. Preserve ownership and attribution.
Do not move an attribute, action, quotation, document, or relation from
one entity or event to another.

9. Include necessary intermediate identification or existence objectives
when the final requested attribute depends on an entity, event, document,
or relation that the question only describes indirectly.

10. Do not use outside knowledge.

11. Do not output search queries, source preferences, evidence claims,
current-state judgments, plans, priorities, confidence, or explanations.

12. Do not optimize for the smallest or largest number of requirements.
Use the minimum number that preserves useful semantic structure.

Return JSON only:

{
  "requirements": [
    {
      "requirement": "..."
    }
  ]
}
```

---

# 16. D1 — Source-Anchored decomposition

D1 测：

> 强制每个自然语言 requirement 回到 Q 原文，是否可以减少 semantic drift？

输出：

```json
{
  "requirements": [
    {
      "requirement": "...",
      "source_spans": [
        {
          "unit": "Q3",
          "text": "..."
        }
      ]
    }
  ]
}
```

---

# 17. D1 System Prompt

```text
You decompose one complex research question into a small set of
source-anchored candidate task requirements.

You receive:
1. the Original Question;
2. addressable Source Units copied verbatim from the Original Question.

This is question understanding only.

For every candidate requirement, provide the exact Original-Question
span or spans that support it.

A source span is an anchor, not merely a citation.
The candidate requirement must not contain a semantic relation,
entity role, date attachment, condition, or assumption that is not
supported by its cited span(s).

Requirements:

1. Together, the candidates must preserve the material requirements of
the Original Question.

2. Each candidate should correspond to one coherent object, event,
relation, identity condition, or requested attribute.

3. Multiple source spans may belong to one candidate when they jointly
describe the same semantic objective.

4. Do not merge independent requirements merely because they eventually
contribute to the same answer.

5. Preserve relation arguments exactly.

6. Do not silently merge or split described roles.

7. Preserve temporal, numeric, ownership, quotation and attribution scope.

8. If a final requested attribute depends on an indirectly described
entity, event, relation or document, preserve the identifying/existence
requirement needed to establish that referent.

9. Do not add outside knowledge.

10. Copy every source span verbatim from the supplied Source Unit.
Do not paraphrase inside source_spans.

11. Do not output search strategy, evidence state, hypotheses, priority,
confidence, rationale or STOP decisions.

12. Do not optimize for a predetermined node count.

Return JSON only:

{
  "requirements": [
    {
      "requirement": "...",
      "source_spans": [
        {
          "unit": "Q1",
          "text": "exact verbatim text"
        }
      ]
    }
  ]
}
```

---

# 18. D2 — Extractive Grouping / Minimal Generation

这是本实验 Primary Arm。

核心假设：

\[
\boxed{
\text{less generation}
\rightarrow
\text{less semantic drift}
}
\]

D2 不要求模型重新写 requirement。

模型只负责：

> 把原问题中的 verbatim spans 分组成若干 coherent task units。

输出：

```json
{
  "requirements": [
    {
      "source_spans": [
        {
          "unit": "Q3",
          "text": "..."
        }
      ]
    }
  ]
}
```

没有 authoritative requirement prose。

---

# 19. D2 System Prompt

```text
You identify the task structure of a complex research question by
grouping exact spans from the Original Question.

You receive:
1. the Original Question;
2. addressable Source Units copied verbatim from the Original Question.

Do NOT rewrite the question into new requirement sentences.

Instead, identify a small set of coherent task units by selecting and
grouping exact source spans.

Each output group represents one semantic requirement of the Original
Question.

Requirements:

1. The complete set of groups should preserve the material task structure
needed to answer the Original Question.

2. One group should represent one coherent object, event, relation,
identity condition, or requested attribute.

3. Multiple exact spans may be grouped when they jointly describe the
same object, event, relation, or identification objective.

4. Do not group independent requirements merely because they contribute
to the same final answer.

5. Preserve the Original Question's relation arguments by preserving the
source text that expresses them.

6. Do not assume that two described roles are the same or different
unless the Original Question states that relation.

7. Preserve the source text that carries important dates, ranges,
quantities, ownership, attribution, or relational scope.

8. When a requested final attribute refers to an entity, event,
document, or relation described indirectly by the question, keep the
descriptive span that establishes that referent as a distinct task unit
when it is semantically separable from the final attribute.

9. Do not add any entity, relation, date, condition or semantic claim
that is absent from the Original Question.

10. Every selected source span must be copied verbatim from the supplied
Source Unit.

11. Do not output explanations, labels, paraphrases, search queries,
evidence judgments, hypotheses, priorities, confidence, or plans.

12. Do not optimize for a predetermined number of groups.
Use the smallest set that preserves useful task structure without
collapsing independent objectives.

Return JSON only:

{
  "requirements": [
    {
      "source_spans": [
        {
          "unit": "Q1",
          "text": "exact verbatim text"
        }
      ]
    }
  ]
}
```

---

# 20. 为什么 D2 是 Primary

D2 不测试：

> “模型能不能把 relation 正确重新说一遍？”

而是测试：

> “模型能不能识别哪些原文 span 属于一个局部 semantic unit？”

因此它最大程度减少：

```text
SameCountry(A,B)
→
SameCountry(A,Jerry)
```

这种 rewriting corruption。

如果 D2 仍然失败：

问题就比 paraphrase 更深，

可能位于：

```text
semantic grouping / task understanding
```

本身。

---

# 21. E0：Gold / Reference Skeleton 不是单一 Gold 文本

每个 unique Q 在调用前建立人工/Codex reference：

```text
REFERENCE_TASK_STRUCTURE.json
```

但不要写：

```text
Gold requirements = exactly these 5 sentences
```

因为 decomposition 不唯一。

---

# 22. Reference 必须包含五类东西

每题：

```json
{
  "qid": "...",

  "material_units": [],

  "critical_invariants": [],

  "dependency_checkpoints": [],

  "forbidden_inferences": [],

  "answer_target": {}
}
```

这些只是 evaluation reference。

绝不进入模型输入。

---

# 23. material_units

表示原题必须被 Skeleton 覆盖的语义要求。

例如论文题可能有：

```text
M1 publication interval
M2 two-author condition
M3 one-author JBSE relation
M4 one-author Harran relation
M5 table-count condition
M6 13.53% emotion condition
M7 target paper identity
```

每个 M：

```json
{
  "id": "M3",
  "source_spans": [...],
  "description": "..."
}
```

description 只供 reviewer。

---

# 24. critical_invariants

专门记录历史上容易被改坏的关系。

例如：

```json
{
  "type": "argument_relation",
  "description": "the two other teammates share a country with each other, not necessarily with Jerry",
  "source_spans": [...]
}
```

或：

```json
{
  "type": "role_identity_open",
  "description": "the Harran-author role and the JBSE-author role are not stated to be the same or different"
}
```

或：

```json
{
  "type": "temporal_attachment",
  "description": "the date belongs to the memorandum, not the enclosed letter"
}
```

---

# 25. dependency_checkpoints

只记录原题中真正存在的 prerequisite structure。

例如：

```text
described later article
→
article title
```

reference：

```json
{
  "upstream": "establish/identify the described later article",
  "downstream": "obtain its title"
}
```

不要凭研究者偏好制造 dependency。

---

# 26. forbidden_inferences

例如：

```text
Harran author = JBSE author
Harran author != JBSE author
other teammates = Australian
article existence is already established
memo date = letter date
```

这些是历史 failure-sensitive invariants。

---

# 27. Reference 编写必须先冻结

对 10 dev + 12 fresh：

全部 reference 在任何 decomposition model call 之前 commit。

不能：

> 看 D0/D1/D2 结果后再补 Gold invariant。

若之后发现 reference defect：

```text
quarantine case
```

并完整披露。

不得静默改 Gold。

---

# 28. E1 调用规模

Development：

```text
10 unique questions
× 3 arms
× 2 independent replicates
= 60 calls
```

同一 execution window 混排。

建议：

```text
model = deepseek-flash
temperature = 0
JSON mode
max_retries = 0
omit max_tokens
max concurrency = 8
```

---

# 29. 为什么只做 2 replicates

与历史 Obligation experiments 保持一致。

主要用于测试：

```text
decomposition stability
```

不是用 best-of。

两个 response 全部保留。

不得挑最好的一次。

---

# 30. JSON Mode Preflight

DeepSeek 历史已有：

> JSON mode 要求 prompt 含 literal `json`。

正式执行前检查：

```text
literal "JSON" or "json" exists
response_format = json_object
schema parser
unique call IDs
unique file paths
no Gold leakage
no Claims leakage
no H leakage
no Path leakage
```

---

# 31. 第一层：Mechanical Validity

D0：

```text
schema valid
1 <= requirement count <= 12
nonempty strings
```

D1：

另外：

```text
all source units exist
all source spans exact-match
all occurrence indices valid
```

D2：

另外：

```text
every node contains >=1 valid source span
no free semantic text field
```

---

# 32. 第二层：Set-level Coverage

对每条 response：

计算人工 review：

\[
Coverage=
\frac{\text{covered material units}}
{\text{all material units}}
\]

报告：

```text
macro coverage per Q
micro coverage across material units
```

Candidate grouping 与 Gold grouping 不一致不自动扣分。

只看 material meaning 是否仍被覆盖。

---

# 33. 第三层：Critical Structural Fidelity

分别评分：

### RelationArgumentFidelity

是否改变参与关系的实体？

### RoleIdentityFidelity

是否无依据合并/拆分角色？

### TemporalAttachmentFidelity

时间是否仍属于正确事件/对象？

### OwnershipAttributionFidelity

动作/文件/quotation/attribute 是否仍属于正确主体？

### NumericRangeFidelity

区间、数量、百分比是否被改变？

---

# 34. 第四层：Dependency Preservation

检查：

> 对于 reference 中存在 dependency checkpoint 的问题，Skeleton 是否保留上游 semantic unit？

例如不能只留下：

```text
article title
```

而完全丢失：

```text
described later article identity/existence
```

指标：

```text
dependency checkpoint recall
```

以及：

```text
downstream-only collapse rate
```

---

# 35. 第五层：Granularity

不要以 node count 判断。

每个 output 分类：

```text
acceptable
too_broad
over_fragmented
mixed
```

### too_broad

一个节点合并了多个独立 research episodes。

### over_fragmented

把一个本来需要一起理解的关系拆到失去语义。

### acceptable

多个互补条件共同描述同一对象/事件/关系可以合法合并。

---

# 36. 第六层：Unsupported Semantics

D0/D1 重点检查：

```text
invented entity
invented equality
invented inequality
invented relation
relation strengthening
attribute movement
date movement
```

D2 理论上不能自由 invention，

但可能通过错误 grouping 暗示：

```text
role merge
relation reassignment
```

所以 D2 仍需人工 semantic review。

---

# 37. D1 Anchor Entailment

D1 特有指标：

> `requirement` 是否被 `source_spans` 足够支持？

分类：

```text
fully_supported
partially_supported
unsupported
```

如果 requirement 中出现了 source span 不支持的：

```text
new equality
new role
new date relation
new subject/object relation
```

则不能算 fully_supported。

---

# 38. D2 Grouping Fidelity

D2 特有指标：

```text
compatible grouping
harmful merge
harmful split
coverage omission
```

D2 没有自然语言重写，

所以主要观察：

> “少生成”是否真的把错误从 semantic corruption 转成更容易控制的 grouping error。

---

# 39. Response-level Strict Skeleton Validity

一个 response strict-valid，当且仅当：

1. schema/mechanical valid；
2. material coverage ≥ 90%；
3. 无 critical relation-argument corruption；
4. 无 critical temporal/object attribution corruption；
5. 无 invented requirement；
6. dependency checkpoint recall ≥ 90%；
7. 没有 severe whole-question collapse；
8. 没有 severe over-fragmentation。

这里的：

```text
90%
```

是 engineering threshold。

不是统计意义上的真值。

---

# 40. 为什么允许 Coverage 90% 而不是 100%

本项目不追求理论完美。

某个非常次要 clue 被遗漏，

只要：

```text
核心结构完整
重大关系没改坏
dependency 没丢
```

仍然可能是工程可用的 Skeleton。

因此不要因一个低重要度修饰词把整个 response 判死。

Reference 中要把：

```text
critical
material
minor
```

区分清楚。

但模型看不到该标签。

---

# 41. 重要性标签只用于 Reviewer

Reference material units：

```json
{
  "importance": "critical|material|minor"
}
```

Strict 要求：

```text
critical coverage = 100%
material weighted coverage >= 90%
```

minor 只描述性报告。

---

# 42. 两次重复的稳定性

不要 exact string match。

D0/D1：

比较 semantic candidate sets。

D2：

比较 span grouping。

每 qid 分类：

```text
same_structure
compatible_structure
different_but_valid
one_valid_one_invalid
both_invalid
```

Primary stability：

```text
same_structure + compatible_structure
```

且：

```text
both responses strict-valid
```

---

# 43. First-pass Review

Reviewer 第一轮尽量看 common normalized representation。

不要先看：

```text
arm
replicate
aggregate
historical Dynamic-O failures
```

构造 common packet：

```text
Original Question
Candidate task units
```

D0：

显示 requirement。

D1：

第一轮只显示 requirement，不显示 anchor。

D2：

Harness 将 source spans verbatim 拼成一个 candidate unit。

这样第一轮可以较少受到 arm schema 影响。

---

# 44. Second-pass Provenance Review

第一轮 commit 后揭示：

```text
arm
source anchors
exact spans
```

再评：

```text
anchor entailment
source fidelity
grouping fidelity
mechanical validity
```

不得修改第一轮语义标签，

除非发现明确 reference/mechanical defect，

并按协议披露。

---

# 45. Primary Metrics 表

必须至少输出：

```text
| Arm | Strict | Coverage | RelationErr | RoleErr | TemporalErr | DependencyRecall | Broad | Stability |
```

另外：

```text
InventedSemantics
AnchorValidity
AnchorEntailment
HarmfulMerge
HarmfulSplit
Schema
```

---

# 46. Primary Mechanism Hypotheses

## H1 — Source anchoring

\[
D1
\]

相对 D0：

```text
critical semantic corruption ↓
```

同时：

```text
coverage 不显著下降
```

---

## H2 — Less generation

\[
D2
\]

相对 D1/D0：

```text
relation/role/date corruption ↓
```

如果主要错误只是转移为：

```text
harmful grouping
```

也必须完整报告。

---

## H3 — Dependency preservation

Source-anchored / extractive representation 应减少：

```text
downstream-only task skeleton
```

即：

> 只保留最终 attribute，而丢掉间接 referent/object branch。

---

## H4 — Stability

减少自由文本 generation 应提高：

```text
cross-replicate structural stability
```

---

# 47. 特别追踪历史 failure families

开发 reference 必须覆盖至少：

### Paper / two-author role ambiguity

不能强制：

```text
Harran author = JBSE author
```

或：

```text
Harran author != JBSE author
```

---

### Jerry Mao / teammate-country

必须保留：

```text
SameCountry(teammate1, teammate2)
```

而不是：

```text
SameCountry(teammate, Jerry)
```

---

### Memorandum / enclosed letter date

日期不能换对象。

---

### Later article / title

不能只表示：

```text
get title
```

而完全丢失：

```text
identify/establish question-described later article
```

---

### Sophie interview/song relation

不能直接把未建立的 interview/song relation 当成已存在对象。

不过注意：

Skeleton 本身可以表示：

> 原题要求该 interview/song relation 成立。

它不是在做当前 evidence judgment。

这里不要把：

```text
Task requirement
```

错误判成：

```text
Unsupported current fact.
```

这是本轮与 Dynamic-O review 非常重要的区别。

---

# 48. Skeleton 评价与 Claims 评价必须严格分开

本轮 Skeleton 描述：

> 原题要求世界满足什么条件。

所以：

```text
“there is a later article...”
```

作为 Task requirement 是合法的。

不要因为 Claims 尚未建立它就判错。

本轮没有 Claims。

因此：

\[
\boxed{
TaskSemantics
\neq
CurrentEvidenceState
}
\]

---

# 49. E1 Primary Gate：D2

D2 是预注册 primary arm。

建议要求全部满足：

```text
Strict Skeleton Validity >= 80%

Critical coverage = 100%

Material coverage >= 90%

Critical relation/role/time corruption <= 5%

Invented semantic requirement <= 5%

Dependency checkpoint recall >= 90%

Severe broadness <= 10%

Mechanical/schema validity >= 95%

Both-replicate strict-valid qids >= 70%
```

---

# 50. Mechanism Comparison Gate

另外至少满足：

```text
D2 critical structural corruption
<= D0 corruption - 10pp
```

或者：

```text
D2 absolute structural corruption <= 5%
```

并且：

```text
D2 material coverage
not worse than D0 by >5pp
```

这样才支持：

\[
\boxed{
less\ generation
}
\]

是有价值的机制。

---

# 51. D1 的角色

D1 不作为最终 Gate。

它是 mechanism bridge。

如果：

```text
D1 << D0 errors
D2 ≈ D1
```

说明：

> anchoring 本身已经足够。

如果：

```text
D2 << D1 << D0
```

说明：

> free paraphrase 确实是重要 error amplifier。

如果：

```text
D0 ≈ D1 ≈ D2
```

说明根因更深：

> semantic grouping/question understanding 本身不稳定。

---

# 52. E1 FAIL 时的行为

如果 D2 Gate FAIL：

\[
\boxed{STOP}
\]

不得：

```text
改 prompt
加入 Binding IR
加入 DAG
加入 Claims
跑 ActiveO selection
跑 Gap
跑 Search
```

最终只分析：

```text
coverage failure?
grouping failure?
dependency failure?
role/coreference failure?
```

---

# 53. E1 PASS 后执行 E2 Fresh Confirmation

Fresh E2 只跑：

```text
D0 baseline
D2 primary
```

D1 不再跑。

规模：

```text
12 fresh questions
× 2 arms
× 2 replicates
= 48 calls
```

因此整个实验最大：

```text
60 + 48 = 108 calls
```

---

# 54. Fresh E2 Prompt 必须 byte-frozen

D0/D2 prompt：

必须和 E1 完全相同。

不得根据 E1 failures 修改。

Source-unit splitter 同样冻结。

---

# 55. Fresh Confirmation Gate

考虑 fresh bank 更难，建议稍宽：

```text
D2 Strict >= 75%

Critical coverage = 100%

Material coverage >= 85%

Critical structural corruption <= 10%

Dependency recall >= 85%

Severe broadness <= 15%

Mechanical/schema >= 95%

Both-replicate strict-valid >= 65%
```

并要求：

```text
D2 structural corruption < D0
```

方向一致。

---

# 56. E2 PASS 能说明什么

只允许结论：

> Source-anchored extractive decomposition is a promising representation for preserving task semantics across these development and repository-unexposed complex questions.

不能说：

```text
完整 Agent 成功
Gap 成功
selection 成功
production ready
```

---

# 57. E2 PASS 后的下一实验

只建议，不执行：

```text
experiment/skeleton-state-alignment
```

测试：

\[
R+C
\rightarrow
Supported/Unresolved
\]

而不是马上：

\[
R+C+Path\rightarrow Search
\]

下一层只回答：

> 给定稳定 Skeleton 后，Claims 能不能正确 mask 哪些 requirement 已满足？

---

# 58. 再下一层才是 Selection

只有：

\[
R+C\rightarrow U
\]

通过以后，

才测试：

\[
U+\Delta C
\rightarrow ActiveO
\]

这里 Recent Claim Delta 的作用才是：

```text
frontier preference
```

而不是：

```text
task semantics
```

---

# 59. Lazy Hierarchical Expansion 暂时不执行

虽然最终架构可能需要：

```text
coarse skeleton
→ selected branch
→ local expansion
```

但不要与本轮 source-anchored mechanism 混在一起。

如果 E1/E2 表明：

```text
flat Skeleton 经常过粗
```

再独立研究：

```text
experiment/lazy-skeleton-expansion
```

---

# 60. 不要提前加入 depends_on / DAG

Dependency 当前先作为：

```text
evaluation criterion
```

而不是 runtime field。

只有后续 Skeleton 能覆盖 requirement，

但 selection 仍频繁 downstream jump，

才有实验依据加入最小：

```text
requires
```

在此之前：

```text
NO typed DAG
NO logical form
NO Binding AST
```

---

# 61. Episode-Stable，而不是绝对 Immutable

本轮如果成功，

未来 Skeleton 的设计原则应该是：

\[
\boxed{
Stable\ by\ default
}
\]

不是：

\[
Immutable\ forever
\]

未来允许显式版本：

```text
R_v1
R_v2
```

但只能因为：

```text
identified decomposition defect
```

而修改。

不能因为：

```text
Search result inconvenient
candidate failed
current hypothesis changed
```

就重新解释 Original Question。

---

# 62. 未来版本修订原则

未来如果允许 skeleton revision：

必须记录：

```text
old skeleton
new skeleton
reason
source-span evidence
which invariant was violated
```

Research evidence：

\[
C_t
\]

只能改变：

```text
which R remains unresolved
```

不能自动改变：

```text
what R means
```

---

# 63. 代码/产物建议目录

```text
experiments/ephemeral_obligation_decomposition/
├── README.md
├── TASK.md
├── HYPOTHESES.md
├── PROTOCOL.md
├── PRE_EXECUTION_AUDIT.md
├── CONFIG.json
├── FREEZE.json
│
├── e0_reference/
│   ├── DEV_QUESTIONS.json
│   ├── FRESH_QUESTIONS.json
│   ├── EXPOSURE_AUDIT.json
│   ├── SOURCE_UNITS.json
│   ├── REFERENCE_TASK_STRUCTURE.json
│   └── REPORT.md
│
├── prompts/
│   ├── d0_freeform.txt
│   ├── d1_source_anchored.txt
│   └── d2_extractive_grouping.txt
│
├── e1_development/
│   ├── SCHEDULE.json
│   ├── RUN.json
│   ├── calls/
│   ├── review/
│   ├── METRICS.json
│   └── REPORT.md
│
├── e2_fresh/
│   ├── STATUS.json
│   ├── SCHEDULE.json
│   ├── RUN.json
│   ├── calls/
│   ├── review/
│   ├── METRICS.json
│   └── REPORT.md
│
└── analysis/
    ├── PROVIDER_PREFLIGHT.json
    ├── INTEGRITY.json
    ├── SENSITIVITY.json
    ├── EXECUTION_ACCOUNTING.json
    └── FINAL_CONCLUSION.md
```

---

# 64. Freeze Discipline

调用前 freeze：

```text
base SHA
dev 10 qids
fresh 12 qids
exposure audit
source-unit algorithm
all source units
all human references
critical invariants
dependency checkpoints
three prompts
schemas
review rubric
gates
call schedule
replicate count
model/config
failure handling
```

commit 后才能调用 API。

---

# 65. Failure Policy

与历史实验一致：

```text
no retries
no best-of
no response repair
no sample replacement
no post-result prompt patch
```

Provider contract failure：

停止未发队列。

所有 planned cells 留在 denominator。

---

# 66. Cost Accounting

至少报告：

```text
planned
sent
returned
HTTP failures
schema failures
anchor failures

input tokens
completion tokens
reasoning tokens
total

cache hit
cache miss
weighted hit rate

latency median
P95
max
peak concurrency
```

reasoning 包含于 completion 时不得重复计总量。

---

# 67. 最终报告必须回答的问题

1. Free-form decomposition 的 strict validity 多高？
2. Source anchoring 是否减少 semantic corruption？
3. Extractive grouping 是否进一步减少 corruption？
4. D2 是否以 coverage 损失换 fidelity？
5. relation-argument error 最常出现在哪类 Q？
6. role identity uncertainty 能否被保留？
7. temporal attachment 能否稳定保存？
8. downstream prerequisite 是否被 Skeleton 保留？
9. 主要 failure 是 harmful merge 还是 harmful split？
10. D2 的主要错误是否已经从 semantic rewriting 转成 grouping？
11. 两次 decomposition 是否稳定？
12. Gold exact grouping 是否必要？还是 alternate grouping 很多？
13. exposed dev 与 fresh confirmation 是否方向一致？
14. Source anchoring 是否值得成为正式 runtime representation？
15. 是否需要 Lazy Expansion？
16. 是否已经有证据需要 explicit `requires`？
17. 是否有证据需要 Binding IR？
18. Task Skeleton 是否值得 episode-stable reuse？
19. 下一阶段是否有资格进入 `R+C → Supported/Unresolved`？
20. 是否仍需要 Direct `Q+C→O` 路线？

---

# 68. 本轮成功的真正意义

本轮不是要证明：

> “模型能完美理解复杂问题。”

而是证明：

\[
\boxed{
\text{我们可以构造一个比每轮自由生成 Obligation 更稳定的 task-semantic reference}
}
\]

如果能做到：

```text
80%左右 response usable
critical structural corruption 很低
coverage 足够高
两次生成相对稳定
```

已经足够有工程意义。

---

# 69. 本轮失败的意义也很明确

如果连：

\[
Q\rightarrow SourceAnchoredSkeleton
\]

都无法稳定完成，

说明问题已经不是：

```text
Research state
Need
Gap
Path
```

的问题。

而是：

\[
\boxed{
\textbf{complex-question semantic decomposition itself}
}
\]

不足。

这时应考虑：

```text
更强 decomposer
specialized model
constrained extraction
training/SFT
人工或规则辅助 canonicalization
```

而不是继续在 Agent controller 上加状态字段。

---

# 70. 最终实验问题

整个实验最后只需要回答：

\[
\boxed{
\textbf{
Can a complex original research question be converted into a
source-faithful, structurally stable task skeleton without repeatedly
rewriting its semantics?
}
}
\]

如果答案是 YES：

下一阶段才有资格测试：

\[
R+C
\rightarrow
UnresolvedRequirements
\]

如果答案是 NO：

接受这个结果，

不要继续把 decomposition failure 伪装成：

```text
Need problem
Gap problem
Path problem
```

---

# 71. 最终架构假设——只记录，不在本轮实现

如果本轮最终通过，

候选长期架构为：

\[
\boxed{
Q
\rightarrow
R
}
\]

**Task semantics**

然后：

\[
\boxed{
R+C_t
\rightarrow
U_t
}
\]

**Current unresolved requirements**

然后：

\[
\boxed{
U_t+\Delta C_t/P_t
\rightarrow
O_t
}
\]

**Frontier selection**

然后：

\[
\boxed{
O_t+C_t
\rightarrow
Gap_t
}
\]

**Evidence deficit**

最后：

\[
\boxed{
Gap_t+H_t+Workspace_t
\rightarrow
Action_t
}
\]

**Acquisition**

其核心原则是：

\[
\boxed{
\textbf{
Canonicalize conservatively,
anchor to source,
keep stable by default,
select dynamically,
compare evidence locally.
}
}
\]

本轮只验证第一箭头。

不要提前实现后四箭头。