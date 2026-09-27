# Search-ESR：State-Conditioned Residualization / Bootstrap-to-Residual

## 0. 本轮研究目标

继续 Search-ESR 当前研究路线，但不要直接进入完整闭环。

上一实验已经得到：

\[
Q\rightarrow SemanticSkeleton
\]

具有较强正向证据；

\[
SemanticSkeleton+Claims
\rightarrow OPEN/CLOSED
\]

在 control-equivalent 层面也具有较强正向证据；

但：

\[
OPENSet\rightarrow ActiveRequirementID
\]

失败集中于 coarse / subnode-only Requirement。

最新 bad case 表明：

> Alignment 阶段实际拥有 Claims 和 `supported_by` 信息，但 Selection 阶段只接收了 `Q + Skeleton + OPEN/CLOSED Mask`，从而丢失了“Requirement 内部哪些部分已经被 Claims 支持”的信息。

因此本轮首先测试：

\[
\boxed{
R_i+C_t
\rightarrow
CurrentLocalResidual_i
}
\]

而不是继续测试：

\[
OPENSet\rightarrow R_i
\]

第二阶段仅在第一阶段通过后研究：

\[
\boxed{
C_{R_i}=\varnothing
\quad\Rightarrow\quad
R_i\rightarrow ExploratoryProbe
\rightarrow Evidence
\rightarrow Claim
}
\]

即 coarse Requirement 的 cold-start / bootstrap。

本轮核心假设：

\[
\boxed{
\textbf{Task semantics should remain stable,
but action-level decomposition should be conditioned on current evidence.}
}
\]

---

# 1. 当前远程基线

开始前必须重新 fetch：

```bash
git fetch origin --prune
git status
git branch --show-current

git rev-parse origin/experiment/recoverable-control-equivalence

git log --oneline --decorate -20 \
  origin/experiment/recoverable-control-equivalence
```

任务编写时基线：

```text
experiment/recoverable-control-equivalence
1f5536d54bc963e27583368dbed1d8356e012ee9
```

latest：

```text
Report frontier selection failure concentrated in coarse nodes and stop at E1
```

如果远程已经前移：

1. 阅读新增 commit；
2. 确认是否已有 state-conditioned residualization / bootstrap 实验；
3. 写入 `PRE_EXECUTION_AUDIT.md`；
4. 不静默继续旧 SHA。

建议新分支：

```bash
git switch -c experiment/state-conditioned-residualization \
  origin/experiment/recoverable-control-equivalence
```

历史实验全部只读。

---

# 2. 必须保留的历史结论

不得重写任何旧实验。

当前正式事实：

```text
Task Skeleton:
Q-only canonicalization strong positive signal

Skeleton-State Alignment:
A0 FAIL
A1 PASS
Joint FAIL

Recoverable Control Equivalence:
E0 PASS

Active-ID Selection:
S0 FAIL
S1 FAIL
```

其中最新 Selection：

```text
direct/coherent valid = 62/64 = 96.88%
subnode-only valid = 19/44 = 43.18%
```

所有23个“有合法JSON但不合法”的 selection 均发生在 `subnode_only` 状态。

本实验不把旧 Selection FAIL 改写为 representation FAIL，也不反向修改其 gate。

---

# 3. 当前根因假设

当前存在两个可能同时成立的机制。

## H1：Control projection 信息丢失

Alignment 实际计算：

```text
R_i
+
Current Claims
→
status
+
supported_by
```

但 Selector 只得到：

```text
R_i = OPEN
```

因此：

```text
R_i partial because A is already supported
```

和：

```text
R_i unsupported, A/B/C are all unresolved
```

会被投影成完全相同的：

```text
R_i = OPEN
```

从而产生 state aliasing。

---

## H2：Requirement 本身过粗

即使：

```text
supported_by = []
```

某些 D2 Requirement 本身仍包含多个独立 evidence episodes：

```text
R_i = A + B
```

因此即使完整 Claims 都给回来，

也可能仍需要：

```text
R_i
→
one coherent exploratory facet
```

或者：

```text
R_i
→
{residual_a, residual_b}
```

本轮需要把 H1 与 H2 分开。

---

# 4. Persistent State 不新增字段

本轮禁止新增 persistent semantic fields。

仍保持：

```text
Episode-stable:
Q
Semantic Skeleton R

Persistent epistemic:
Verified Claims C
Hypothesis H

Mechanical:
Workspace
Trace
Search/Find/Open attempts
D#
W#
query history
```

以下仍为 ephemeral：

```text
OPEN/CLOSED Mask
support packet
Current Residual
Probe
Active Gap
```

本轮目标不是构造新的 persistent Progress Map。

---

# 5. E0 — Residual Reference Construction

E0 零模型调用。

建立一个新的：

```text
RESIDUAL_REFERENCE.json
```

Primary bank：

> 所有历史 D2 `subnode_only` natural states。

当前已知：

```text
11 / 27 states
```

全部进入 primary denominator。

不得只挑 Selection 失败状态。

---

# 6. E0 Controls

另外构造 direct/coherent controls。

目标：

> 验证新的 residualizer 不会把本来已经 action-sized 的 Requirement 过度拆碎。

机械匹配：

```text
qid
historical control type
Claims empty/non-empty
```

如果无法完全匹配，

按 frozen deterministic rule 选择。

建议至少：

```text
8 direct/coherent control states
```

Primary + controls 目标约：

```text
19 natural states
```

若实际数量不同，冻结实际 bank 并解释。

---

# 7. 每个 state 固定一个 Parent Requirement

不要重新让模型从全部 Skeleton 中选 Parent。

本轮隔离的是：

\[
R_i+C
\rightarrow Residual
\]

不是：

\[
R+C\rightarrow SelectR
\]

因此 E0 对每个 state 冻结：

```text
parent_requirement_id
```

来源优先级：

1. 已有 D2 addressability audit 中对应历史 GoldO 的 parent node；
2. 已有 Selection failure 明确选择的 coarse node；
3. 对 direct/coherent control 使用冻结 acceptable node。

不得依据本轮模型输出重新选 Parent。

---

# 8. 特别保留关键 state trajectories

必须至少包含并单独报告：

```text
q228:
G04
G05
G06

q637:
G16
G17
G18

q122:
G15
```

这些是本轮最重要的机制判例。

---

# 9. q228 必须如何理解

R2 大致包含：

```text
childless marriage
+
foundational gift / building relation
```

G04：

```text
support for R2 = none
```

G05：

```text
support for R2 = none
```

G06：

```text
C5 establishes Ding's marriage + childlessness
gift/building remains unresolved
```

因此：

### G04 / G05

可以有多个合法 exploratory residual：

```text
verify childlessness / marital condition
```

或者：

```text
establish gift/building relation
```

但不能把两个独立目标继续打包成一个 local residual。

### G06

不得重新研究已经由 C5 建立的 marital/childlessness 部分。

合法 residual 应聚焦：

```text
foundational gift / building episode
```

这是 state discrimination 的核心 test。

---

# 10. q637 必须如何理解

D2 R3 包含：

```text
first case report country / country-history condition
+
first patient's clinical history
```

G16：

```text
Claims = []
```

二者均未建立。

允许输出其中任意一个 coherent exploratory residual。

G17：

只有通用 SPS background Claims。

这些 Claims 不绑定目标病例。

因此仍不得把 clinical case-specific predicate 视为已支持。

G18：

C7 已建立第一病例的 clinical history。

因此当前 residual 不应继续要求重新验证临床症状；

应该聚焦：

```text
report country
+
required country/history/religion condition
```

---

# 11. Gold Residual 不要求唯一措辞

本实验不要设唯一 Gold sentence。

每条 state/parent 建：

```json
{
  "case_id": "G18",
  "parent_requirement_id": "R3",

  "acceptable_residual_classes": [
    {
      "semantic_target": "establish the report-country and required country-history condition",
      "source_units": ["Q3"]
    }
  ],

  "forbidden_supported_targets": [
    "re-establish the already supported first-patient clinical history"
  ],

  "forbidden_downstream_targets": []
}
```

如果当前 parent 内存在多个独立合法下一步：

```json
"acceptable_residual_classes": [
  {...},
  {...}
]
```

任何一个即可成功。

---

# 12. Residual 的定义

一个合法 Current Local Residual 必须满足：

1. 是 parent Requirement 的语义子集；
2. 当前仍未被 Claims 充分建立；
3. 不重新要求已经被 Claims 建立的 substantive condition；
4. 一次只表达一个 coherent evidence episode；
5. 不引入 Q / Claims 中不存在的候选为事实；
6. 未知对象可以本身成为 discovery target；
7. 不跳到仍依赖未建立 referent 的下游属性；
8. 保持人物角色、关系论元、时间归属、对象归属；
9. 不是 Search query；
10. 不是 source recommendation。

---

# 13. E1 — State-Conditioned Residualization

E1 不调用 Search/Find/Open。

只测 semantic residualization。

三个 Arms。

---

# 14. R0 — Full Current Claims

输入：

```text
Original Question
Parent Requirement
ALL Current Verified Claims
```

这是 primary runtime arm。

原因：

> Claims 已经是 persistent state，无需新增字段；首先测试“信息其实已有，只是下游没有看到”这一假设。

---

# 15. R1 — Oracle Relevant Claims

输入：

```text
Original Question
Parent Requirement
only Gold contributing/supporting Claims
```

目的：

> 测最小、干净的 support packet 是否足够。

该 arm 是 diagnostic/oracle。

不得用于部署结论。

---

# 16. R2 — Frozen Model Support Packet

输入：

```text
Original Question
Parent Requirement
frozen prior model Alignment status
frozen supported_by claim texts
```

来源必须固定为：

```text
skeleton-state-alignment A1 replicate1
```

绝不：

```text
best-of replicate
人工修正
fallback Gold
```

目的：

> 测实际 Alignment 生成的 compact support routing 能否支撑 residualization。

---

# 17. 为什么同时需要 R0 / R1 / R2

若：

```text
R0 PASS
R1 PASS
R2 PASS
```

说明：

> 当前 persistent Q/R/C 已基本足够，Harness 只需要把 Claims 正确传给 local residualizer。

若：

```text
R0 PASS
R1 PASS
R2 FAIL
```

说明：

> 主要问题在模型 support routing / supported_by，不应把 compact support packet 作为唯一输入。

若：

```text
R1 PASS
R0 FAIL
```

说明：

> 全量 Claims 噪声会干扰 residualization，需要 evidence filtering。

若：

```text
R0/R1 都 FAIL
```

说明：

> 即使 evidence 给足，coarse R 本身仍不足以稳定产生局部 residual，需要研究 finer control representation。

---

# 18. E1 Residualizer System Prompt

```text
You derive one current local research residual inside a fixed parent
requirement.

You receive:

1. the Original Question;
2. exactly one fixed Parent Requirement from a source-anchored Task Skeleton;
3. the current evidence context for this Parent Requirement.

The Parent Requirement describes a region of the original task.
It may contain more than one semantic condition.

Your job is NOT to solve the whole question.
Your job is NOT to select another Task Requirement.

Your job is to identify exactly ONE coherent evidence objective inside the
Parent Requirement that still needs to be established now.

Important:

- The Parent Requirement is task semantics, not evidence.
- Only Verified Claims count as established evidence.
- A condition mentioned by the Original Question is not automatically true.
- A candidate name or related background fact does not establish a relation
  unless the relation is actually supported.
- If some part of the Parent Requirement is already established by Claims,
  do not ask to establish that part again.
- If several independent unresolved parts remain, choose exactly ONE coherent
  part. Do not bundle independent research objectives.
- An unknown entity/event/document/relation may itself be the residual target.
  It does not need to be known before you can research it.
- Do not jump to a downstream attribute whose referent still needs to be
  established.
- Preserve participant roles, relation arguments, ownership, object scope,
  temporal attachment, and uncertainty from the Parent Requirement.
- Do not add outside knowledge.
- Do not use hypotheses as evidence.
- Do not output a search query, source, website, plan, priority, or answer.

If no substantive part of the Parent Requirement is supported yet, still choose
one faithful, low-commitment facet of the Parent Requirement that can serve as
an exploratory evidence objective. Do not pretend that this facet is the
unique decomposition of the Parent Requirement.

Return JSON only:

{
  "parent_requirement_id": "R3",
  "mode": "residual",
  "used_claims": ["C7"],
  "local_residual": "..."
}
```

如果输入中没有任何 substantive supporting Claim：

```json
{
  "parent_requirement_id": "R3",
  "mode": "probe",
  "used_claims": [],
  "local_residual": "..."
}
```

注意：

`probe` 在这里仍然只是一个 evidence objective，

还不是 Search query。

---

# 19. R0 输入模板

```json
{
  "Original Question": "...",

  "Parent Requirement": {
    "requirement_id": "R3",
    "source_spans": [...]
  },

  "Current Verified Claims": [
    {
      "claim_id": "C1",
      "statement": "..."
    }
  ]
}
```

---

# 20. R1 输入模板

字段同上，

但：

```text
Current Verified Claims
```

只包含 Gold reference 判定为对 parent 有 substantive contribution 的 Claims。

如果无支持：

```json
"Current Verified Claims": []
```

---

# 21. R2 输入模板

```json
{
  "Original Question": "...",

  "Parent Requirement": {...},

  "Prior Alignment": {
    "status": "partially_supported",
    "supported_by": ["C7"]
  },

  "Supporting Claims": [
    {
      "claim_id": "C7",
      "statement": "..."
    }
  ]
}
```

---

# 22. E1 调用规模

假设最终：

```text
19 states
× 3 arms
× 2 replicates
= 114 calls
```

若实际 bank 数不同：

> 按实际冻结规模报告，不为凑114修改样本。

模型：

```text
DeepSeek deepseek-flash
temperature = 0
JSON mode
omit max_tokens
max_retries = 0
concurrency <= 8
```

所有 slot 保留分母。

不 retry。

不 repair。

---

# 23. E1 Primary Metrics

## Strict Local Residual Validity

必须同时：

```text
parent faithful
unresolved
local/coherent
non-downstream
scope faithful
no invented premise
```

---

## Supported-Content Leakage

模型 residual 是否重新要求：

> 当前 Claims 已经充分建立的 substantive content。

这是本轮最重要的新错误之一。

---

## Broad Residual Rate

是否继续把 parent 中多个独立 unresolved objectives 打包。

---

## Relation / Object / Temporal Fidelity

沿用历史错误 taxonomy。

---

## State Discrimination

对于：

```text
same Q
same Parent Requirement
different Claims
```

且 Gold residual set 实际发生变化的 pair，

输出是否也作出语义上正确变化。

重点：

```text
G05 -> G06
G17 -> G18
```

---

## Control Addressability Gain

对于历史：

```text
subnode_only
```

states，

新的 local residual 是否变成：

```text
directly actionable / coherent
```

这是 primary mechanism metric。

---

## Over-Decomposition on Controls

对于原本 direct/coherent Parent：

> residualizer 是否把它错误拆成不完整或改变语义的小片段。

---

# 24. E1 Primary Gate

R0 Full Claims 必须满足：

```text
Strict Local Residual >= 85%

Historical subnode-only:
Residual Addressability >= 85%

Supported-Content Leakage <= 5%

Broad Residual <= 10%

Downstream <= 5%

Relation/Object/Temporal corruption <= 5%

State Discrimination >= 80%

Control over-decomposition <= 10%

Schema >= 95%
```

R1 Oracle relevant Claims：

```text
Strict >= 90%
```

作为能力上界。

R2 Model Support Packet：

```text
Strict >= 80%

and
R0 - R2 Strict <= 10pp
```

如果 R0 PASS 但 R2 FAIL：

允许结论：

> 使用 full current Claims 比压缩 supported_by packet 更可靠。

不要求 R2 阻止后续 bootstrap。

---

# 25. E1 必须单独报告 Zero-Support 与 Partial-Support

分成：

```text
Z:
Gold support for parent = none

P:
Gold parent partially supported
```

不能合并后只报总准确率。

因为它们对应两个不同控制模式。

---

# 26. P 组回答的问题

\[
\boxed{
\text{Claims 能不能帮助模型正确 subtract 已完成部分？}
}
\]

关键指标：

```text
supported-content leakage
residual locality
state discrimination
```

---

# 27. Z 组回答的问题

当前没有可 subtract 的支持。

只评价：

```text
faithful
one coherent facet
low commitment
no invented candidate
no downstream jump
```

不要把它当成“完美最终 decomposition”。

Z 组输出：

```text
mode = probe
```

---

# 28. E1 结果解释

## Case A

R0/R1 均 PASS。

说明：

\[
\boxed{
Q+R+C
}
\]

已经足以动态形成局部 residual。

之前 Selection failure 的主要根因确实是 control projection 过度压缩。

---

## Case B

R1 PASS，R0 FAIL。

说明：

> 信息存在，但全 Claims 噪声干扰；需要 lightweight evidence routing/filtering。

---

## Case C

R0/R1 在 P 组 PASS，但 Z 组低。

说明：

> Claims-conditioned subtraction 可行；
> cold-start bootstrap 是下一独立瓶颈。

进入 E2。

---

## Case D

P 组也 FAIL。

说明：

> 即使提供准确支持证据，coarse R 仍不能稳定 residualize。

停止。

下一研究方向才是：

```text
D1-like finer control nodes
+
D2 source-span authority
```

不得继续 E2 retrieval。

---

# 29. E2 — Zero-Support Bootstrap

只有：

```text
P-group residualization PASS
```

才运行。

E2 只使用：

```text
Z-group
```

即 parent 当前没有 substantive supporting Claim 的 states。

---

# 30. E2 开始前做 Oracle Accessibility Audit

E2 任何模型调用前，

对每个 Z state 离线判断：

> 当前 corpus / historical trajectory 中是否存在至少一份能够为 parent 提供新 material evidence 的来源。

只用于评价。

绝不输入模型。

分类：

```text
accessible
uncertain
known_unavailable
```

Primary retrieval bank 只要求：

```text
accessible
```

但另外两类必须完整保留并报告。

不得根据模型 query 结果重新标 accessibility。

---

# 31. Oracle Accessibility 可以使用什么

允许作为 evaluation-only：

```text
later historical Claims
their source provenance
later historical D#/W#
known corpus documents
```

禁止进入 model prompt。

目的只是回答：

> 如果理想地寻找，这个 state 是否存在能获得新 evidence 的 observation channel？

---

# 32. E2 两个一阶 Bootstrap Arms

## P0 — Coarse Region Query

输入：

```text
Original Q
Parent Requirement
```

直接生成一条 Search query。

它模拟：

> “没有 Claim 时，直接拿粗 R 搜。”

---

## P1 — Probe-Objective Query

使用 E1 R0 的冻结 `mode=probe` local residual。

先得到：

```text
probe objective
```

再使用统一 Query Generator：

```text
probe objective
→ one Search query
```

Query Generator 在两 arms 保持同一 system prompt。

唯一差别：

```text
P0 sees coarse parent
P1 sees local exploratory probe
```

---

# 33. Bootstrap Query Generator Prompt

```text
You generate one exploratory search query for the supplied research objective.

The objective is provisional and is intended to obtain new evidence, not to
state a proven fact.

Generate exactly ONE query that is likely to retrieve evidence relevant to the
objective.

Rules:

1. Preserve the objective's entities, roles, relation direction and temporal
   constraints.

2. Do not insert a candidate name, event, source, date, place or relation that
   is not already present in the supplied objective.

3. Do not attempt to solve the whole Original Question.

4. Prefer a query that can establish an entity/relation/source anchor rather
   than a query that presupposes the final answer.

5. Do not output explanations.

Return JSON only:

{
  "query": "..."
}
```

---

# 34. Retrieval Protocol

冻结使用当前现有 Search backend。

不得同时修改：

```text
embedding model
index
top-k
preview length
ranking
Search semantics
```

每 query：

```text
1 Search
```

固定 top-k 和 preview budget 与当前 baseline 一致。

本阶段不自动 Find/Open。

目的是隔离：

\[
Probe\rightarrow Search\ EvidenceGain
\]

---

# 35. E2 评价不能只看 Gold final answer

Primary Evidence Gain：

## New Material Claim Opportunity

top-k 中是否出现至少一段 evidence：

> 可以支持一个当前 Claims 中不存在、且 parent-relevant 的新 Verified Claim。

---

## Binding Gain

是否获得：

```text
entity binding
event binding
document binding
relation binding
```

之一，

使 coarse parent 的后续 decomposition 变得更具体。

---

## Direct vs Bridge Gain

分别报告：

```text
direct evidence
bridge evidence
```

Bridge 必须确实缩小 uncertainty，

不能只因“主题相关”就算 progress。

---

## Duplicate / No-Gain

是否只是：

```text
已有 Claim 重复
已有 document 重复
generic background
same candidate without new relation
```

---

# 36. E2 Primary Metrics

分别 P0 / P1：

```text
NewMaterialEvidence@K
BindingGain@K
DirectGain@K
BridgeGain@K
NoGain rate
Query drift
Unsupported-candidate commitment
Repeated-document rate
```

paired 报告：

```text
P1 wins
P0 wins
tie
```

---

# 37. E2 Gate

前提：

```text
accessible states >= 8
and
unique qids >= 4
```

否则：

```text
UNDERPOWERED_BOOTSTRAP_BANK
```

不作资格结论。

若样本足够：

```text
P1 NewMaterialEvidence@K >= 60%

P1 BindingGain@K >= 50%

Unsupported candidate commitment <= 5%

Semantic drift <= 5%

P1 vs P0 evidence-gain improvement >= 10pp
OR
paired wins exceed losses by >= 3 cases
```

二选一比较条件必须预先冻结。

---

# 38. E2B — No-Gain Escalation

只有 P1 出现真实 NoGain case 才运行。

不是所有 case 都跑第二次。

Eligibility：

```text
P1 no useful new evidence
AND
oracle accessibility still positive
AND
at least one untried source-anchored facet remains
```

---

# 39. E2B 输入

模型看到：

```text
Original Question
Parent Requirement
previous probe objective
previous query
mechanical result summary
```

mechanical result summary 只能包含：

```text
returned document IDs/titles
whether any new claim was admitted: no
whether new binding was found: no
```

不要给人工 Gold failure reason。

---

# 40. E2B Orthogonal Probe Prompt

```text
The previous exploratory probe did not produce a new verified claim or a new
entity/event/relation binding.

Generate ONE new exploratory evidence objective for the same Parent Requirement.

The new objective must:

1. target a different substantive facet, relation, entity anchor, temporal
   clue, or source type than the previous failed probe;

2. remain faithful to the Parent Requirement;

3. not invent a candidate or treat a hypothesis as evidence;

4. not simply paraphrase the previous probe;

5. seek information that could reduce uncertainty about the Parent Requirement.

Do not output a search query.

Return JSON only:

{
  "probe": "..."
}
```

然后使用同一个 Query Generator。

---

# 41. E2B 指标

```text
Rescue Rate
Near-duplicate probe rate
Near-duplicate query rate
New document rate
New binding rate
New material claim opportunity
```

如果同一 query family 连续无 gain：

不得继续第三次付费微调 query。

本实验最多：

```text
2 probes per zero-support state
```

---

# 42. Starvation 分类

E2 结束后，每个 Z state 分成：

### Bootstrap-success

得到新 material/binding evidence。

### Query-limited

Oracle source accessible，

但模型两次 probe 均未召回。

### Retriever-limited

冻结 Oracle query / known relevant source 也无法进入当前 backend top-k。

### Evidence-recognition-limited

relevant source 已返回，

但可见窗口没有被识别为 material evidence。

### Corpus/source-limited

已知 evaluation source 不在当前 corpus / observation channel。

不得把这些全部叫：

```text
decomposition failure
```

---

# 43. Oracle Counterfactual Diagnostic

对于最终 starvation case，

最多做离线或冻结受控诊断：

```text
Oracle query → Search
```

或：

```text
Oracle document → preview
```

用于区分：

```text
query problem
retriever problem
localizer problem
```

不得把 Oracle 结果作为主 arm 的补救 evidence。

---

# 44. Hypothesis H 的边界

E1/E2 primary 均不让 H 进入 residual semantics。

E2B 如果未来要测试 H-assisted exploration，

必须另开实验。

当前原则：

\[
H\rightarrow acquisition\ hint
\]

但：

\[
H\not\rightarrow support
\]

本轮不要混入。

---

# 45. 本轮不测试 STOP

没有充分自然 positive STOP control 时，

不要新增 closure 结论。

OPEN/CLOSED 继续只承担 Monitoring。

---

# 46. Harness 的职责

Harness 不做复杂 semantic subtraction。

Harness 只负责：

```text
固定 parent R
读取当前 Claims
构造 arm-specific input
验证 claim IDs
记录 query history
记录 returned docs
机械计算 no-gain
执行 gate
保存 provenance
```

LLM 负责：

```text
semantic residualization
exploratory facet selection
query generation
```

---

# 47. 本轮不要新增这些结构

禁止：

```text
persistent residual tree
persistent fine-grained requirement map
dependency DAG
Binding IR
second verifier
majority vote
confidence field
hard action masking
RL / SFT
```

除非本轮 failure 明确要求。

---

# 48. 建议目录

```text
experiments/state_conditioned_residualization/
├── README.md
├── TASK.md
├── HYPOTHESES.md
├── PROTOCOL.md
├── CONFIG.json
├── GATES.json
├── FREEZE.json
├── PRE_EXECUTION_AUDIT.md
│
├── e0_reference/
│   ├── STATES.json
│   ├── PARENT_REQUIREMENTS.json
│   ├── RESIDUAL_REFERENCE.json
│   ├── SUPPORT_REFERENCE.json
│   └── ACCESSIBILITY_REFERENCE.json
│
├── e1_residualization/
│   ├── SCHEDULE.json
│   ├── calls/
│   ├── review/
│   ├── METRICS.json
│   └── REPORT.md
│
├── e2_bootstrap/
│   ├── STATUS.json
│   ├── SCHEDULE.json
│   ├── calls/
│   ├── retrieval/
│   ├── review/
│   ├── METRICS.json
│   └── REPORT.md
│
├── e2b_escalation/
│   ├── STATUS.json
│   ├── SCHEDULE.json
│   ├── calls/
│   ├── retrieval/
│   ├── METRICS.json
│   └── REPORT.md
│
└── analysis/
    ├── ERROR_LEDGER.json
    ├── STATE_DISCRIMINATION.json
    ├── STARVATION_DIAGNOSTICS.json
    ├── SENSITIVITY.json
    ├── EXECUTION_ACCOUNTING.json
    ├── INTEGRITY.json
    └── FINAL_CONCLUSION.md
```

---

# 49. 结果必须回答的核心问题

1. Full Current Claims 是否足以把 coarse R 动态减成局部 residual？
2. Gold relevant Claims 相比 all Claims 是否更稳定？
3. Frozen model `supported_by` packet 是否足够？
4. q228 G04/G05/G06 能否被当前 Claims 正确区分？
5. q637 G16/G17/G18 能否随着 Claim 增长改变 residual？
6. 已支持内容是否仍被重复研究？
7. coarse R 是否继续产生 broad residual？
8. direct/coherent controls 是否被过度拆解？
9. 历史 subnode-only states 的 actionable addressability 提高多少？
10. Zero-support state 能否生成 faithful low-commitment probe？
11. Probe 是否获得新 material evidence？
12. Probe 是否获得新的 entity/relation binding？
13. state-conditioned probe 是否优于直接拿 coarse R 搜索？
14. no-gain 后的正交 probe 能救回多少 case？
15. starvation 最终来自 decomposition、query、retriever、localizer 还是 corpus？
16. 是否出现 candidate hardening？
17. 是否需要 finer persistent control nodes？
18. 是否需要新的 persistent State field？
19. 当前 Q+R+C 是否已经是足够的最小 persistent semantic state？
20. 是否有资格进入独立的 4–8 decision closed-loop rollout？

---

# 50. 最终解释矩阵

如果：

```text
Partial-support residualization PASS
Zero-support bootstrap PASS
```

则支持：

\[
\boxed{
Q+R+C
}
\]

作为最小 persistent semantic state，

并支持：

```text
stable semantic plan
+
dynamic residual decomposition
+
exploratory bootstrap
```

进入下一轮短闭环。

如果：

```text
Partial-support residualization PASS
Bootstrap FAIL
```

则：

> Research State 基本足够，主要瓶颈在 acquisition cold-start / retrieval。

如果：

```text
Gold relevant Claims PASS
All Claims FAIL
```

则：

> 需要 evidence routing/filtering，而不是更细 Skeleton。

如果：

```text
Full Claims 和 Gold relevant Claims 都 FAIL
```

则：

> coarse semantic Requirement 本身不能可靠 residualize；
> 此时才有经验依据测试 D1-like fine control nodes + D2 source-span authority。

---

# 51. 最终停止纪律

即使 E1 + E2 + E2B 全部通过：

本实验仍然停止。

禁止自动进入：

```text
full Gap cascade
Search/Find/Open multi-step loop
Writer loop
final-answer rollout
```

下一轮必须单独 preregister：

```text
experiment/bootstrap-residual-research-loop
```

进行：

```text
4–8 decisions
```

的真实闭环。

---

# 52. 本轮最核心的问题

本实验不是要证明：

> 模型可以在初始化时完美拆复杂问题。

而是要验证：

\[
\boxed{
\textbf{
Can current evidence turn a coarse semantic requirement into
a better local research objective?
}
}
\]

以及在没有 evidence 时：

\[
\boxed{
\textbf{
Can a low-commitment exploratory probe bootstrap the first useful
piece of evidence without hardening an unsupported decomposition?
}
}
\]

最终目标不是完美初始化。

最终目标是：

\[
\boxed{
\textbf{
粗任务允许不完美地开始，
但每获得一份真正的证据，都应该让下一轮任务分解变得更准确。
}
}
\]