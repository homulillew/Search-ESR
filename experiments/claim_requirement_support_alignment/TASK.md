# Search-ESR：Claim–Requirement Support Alignment 实验

## 0. 本轮实验只回答一个问题

本轮禁止研究 Search、Query、Probe、Find/Open、Writer、NoGain recovery 或完整闭环。

只研究：

\[
\boxed{
\text{给定固定 Requirement 和当前 Claims，}
\text{哪些 Claims 真正构成这个 Requirement 的 substantive support？}
}
\]

进一步验证：

\[
\boxed{
\text{如果 Support Assignment 正确，}
R + Support
\rightarrow Residual
\text{ 是否稳定成立？}
}
\]

本轮核心不是“相关性匹配”。

必须严格区分：

```text
semantic relatedness
≠
substantive support
```

一个 Claim 只有在保持正确的：

- subject / actor；
- object；
- relation direction；
- temporal attachment；
- event/source binding；
- candidate branch；
- ownership / affiliation；

并实际建立 Parent Requirement 中一个 material condition 时，

才允许作为 `SUBSTANTIVE_SUPPORT`。

---

# 1. 当前研究背景

开始前重新 fetch：

```bash
git fetch origin --prune
git status
git branch --show-current

git rev-parse origin/experiment/state-conditioned-residualization

git log --oneline --decorate -20 \
  origin/experiment/state-conditioned-residualization
```

任务编写时已知最新基线：

```text
branch:
experiment/state-conditioned-residualization

HEAD:
fc799239d41e0abd6b8306cc09f9e3b7a2126586
```

如果远程已经前移：

1. 阅读全部新增 commit；
2. 检查是否已有 Claim–Requirement Support Alignment 实验；
3. 写入 `PRE_EXECUTION_AUDIT.md`；
4. 不静默沿用旧 SHA。

建议新分支：

```bash
git switch -c experiment/claim-requirement-support-alignment \
  origin/experiment/state-conditioned-residualization
```

历史实验全部只读。

---

# 2. 当前已有证据

必须保留以下旧结果，不重新解释。

### State-conditioned residualization

R0：

```text
Parent R + all Current Claims
```

整体：

```text
29/38 = 76.32%
```

R1：

```text
Parent R + Oracle contributing Claims
```

整体：

```text
31/38 = 81.58%
```

但 Partial-support P 组：

```text
R0 = 6/6
R1 = 6/6
```

且：

```text
supported-content leakage = 0
```

说明：

> 当真正的 supporting Claims 已经比较明确时，
> Required-Supported subtraction 有明显正向能力。

同时：

```text
R0 mode accuracy = 28/38
R1 mode accuracy = 37/38
```

说明：

> 全量 Claims 中的 candidate / anchor / background
> 容易被误判成 substantive support。

因此本轮直接测试该缺口。

---

# 3. 本轮主要假设

## H1 — Support Alignment Hypothesis

模型可以在：

```text
Parent Requirement
+
Current Claims
```

中可靠识别：

```text
SUBSTANTIVE_SUPPORT
```

而不会把：

```text
candidate anchor
generic background
entity relevance
adjacent relation
```

错误提升为 Support。

---

## H2 — Scope Alignment Hypothesis

当一个 Claim 是 Support 时，

模型能够识别：

> 它究竟支持 Parent Requirement 中的哪一部分。

例如：

```text
R3:
report-country/history condition
+
specific clinical history
```

Claim C7 只支持：

```text
specific clinical history
```

不能把整个 R3 判为被支持。

---

## H3 — Typed-Evidence Hypothesis

显式区分：

```text
SUBSTANTIVE_SUPPORT
BINDING_CONTEXT
BACKGROUND
IRRELEVANT
```

比简单的：

```text
support / not-support
```

更能降低 False Support。

---

## H4 — Downstream Causal Hypothesis

如果给 Residualizer 一个正确的 typed evidence view：

```text
Support Claims
+
Binding Context
```

则 Residual 表现应明显接近 Gold typed evidence view。

如果：

```text
Gold typed evidence → Residual
```

表现很好，

但：

```text
Model typed evidence → Residual
```

明显较差，

则当前真正瓶颈是 Support Alignment。

---

# 4. Persistent State 不变

本实验禁止新增 persistent semantic fields。

仍保持：

```text
Q
Semantic Skeleton R
Verified Claims C
Hypothesis H
```

其中本实验完全不使用 H。

以下全部只是 ephemeral experiment outputs：

```text
Support Assignment
Binding Context
Background classification
Residual
```

不得写回长期 State。

---

# 5. 一个非常重要的设计原则

本轮不要再创建新的 persistent：

```text
R3a
R3b
R3c
```

也不要创建新的 Evidence Need graph。

Requirement 继续使用现有 source-anchored D2 Skeleton。

Support scope 的评估只能作为：

```text
evaluation-time annotation
```

不得成为 runtime Task representation。

---

# 6. E0 — Evaluation Bank

E0 零模型调用。

从以下历史来源构造 natural-state bank：

```text
experiments/skeleton_state_alignment/
experiments/recoverable_control_equivalence/
experiments/state_conditioned_residualization/
```

优先复用 natural snapshots。

---

# 7. Primary bank 只使用 Claims 非空的状态

原因：

本轮研究：

```text
Claims → Requirement Support
```

没有 Claims 的状态不是核心 denominator。

目标：

```text
约 18–24 parent-state snapshots
>= 10 unique qids
```

不要为了凑数量新增人工伪造状态。

如果实际数量较少，冻结实际数量。

---

# 8. Bank 必须覆盖三类状态

## P — True Partial Support

Parent Requirement 中至少一个 substantive condition
已经由 Current Claims 支持，

但 Parent 未完全完成。

例如：

```text
q228 G06
q637 G18
```

---

## Z — Hard Negative / Zero Parent Support

Claims 非空，

但没有任何 Claim 真正支持当前 Parent。

Claims 可以非常相关，

甚至包含：

```text
candidate identity
generic disease facts
related university
related person
background date
```

但它们不能满足 Parent condition。

这组是 Primary Safety Bank。

---

## F — Full Support

当前 Claims 已经足以支持 Parent Requirement。

用于测试：

```text
support recall
full-support sufficiency
future closure safety
```

F 不要求很多，

但不能完全缺失。

---

# 9. 必须包含的历史 hard cases

如果相应 natural state 可用，必须纳入：

```text
Euler biography
vs
target-book → Euler reference relation
```

```text
generic SPS symptoms
vs
specific patient/case relation
```

```text
memorandum date
vs
enclosed letter date
```

```text
patient nationality
vs
case-report country
```

```text
candidate alma mater
vs
building affiliation
```

```text
teammate names
vs
same-country relation
```

```text
coder / Australia
vs
other teammates same-country-with-each-other
```

```text
artist identity
vs
artist → charity relation
```

以及：

```text
q228 Kwon / Ding
q637 clinical case / report-country
```

不得只采集过去模型犯错的负例。

必须加入相同比例的明确 true-support controls。

---

# 10. E0 Gold Reference

为每个：

```text
state × Parent Requirement × Claim
```

冻结如下 reference。

推荐结构：

```json
{
  "case_id": "G18",
  "parent_requirement_id": "R3",

  "claims": {
    "C7": {
      "epistemic_role": "SUBSTANTIVE_SUPPORT",
      "supported_requirement_fragments": [
        "the individual presented with a half-year history of pain ..."
      ],
      "binding_context": false
    },

    "C3": {
      "epistemic_role": "BACKGROUND",
      "supported_requirement_fragments": [],
      "binding_context": false
    }
  },

  "gold_support_claim_ids": ["C7"],
  "gold_binding_context_claim_ids": [],
  "parent_fully_supported": false
}
```

---

# 11. Epistemic Role 定义

只能使用四类：

## SUBSTANTIVE_SUPPORT

Claim 实际建立 Parent Requirement 中一个 material condition。

要求：

- referent 正确；
- relation 正确；
- role 正确；
- object 正确；
- temporal scope 正确；
- candidate branch 正确。

---

## BINDING_CONTEXT

Claim 本身不满足 Parent condition，

但帮助识别：

- 哪个 candidate；
- 哪个 entity；
- 哪个 event；
- 哪个 document；

从而解释另一个 supporting Claim 属于哪条 branch。

例如：

```text
C4:
Ding founded NetEase
```

相对于一个：

```text
Ding + spouse + childlessness
```

condition，

C4 可能只是 candidate branch context，

而不是 marriage support。

---

## BACKGROUND

一般背景事实。

例如：

```text
SPS generally causes stiffness and walking difficulty
```

相对于：

```text
the specific patient in the target case had those symptoms
```

只能是 BACKGROUND。

---

## IRRELEVANT

对当前 Parent 的支持和绑定均无实质作用。

---

# 12. 一个 Claim 同时有多种用途怎么办？

Primary role 按以下优先级：

```text
SUBSTANTIVE_SUPPORT
>
BINDING_CONTEXT
>
BACKGROUND
>
IRRELEVANT
```

如果一个 Claim 自身已经支持 material condition，

即使同时有 candidate-binding 价值，

Primary role 仍标：

```text
SUBSTANTIVE_SUPPORT
```

必要时另加：

```json
"also_binding_context": true
```

该字段只用于诊断，不进入主计分。

---

# 13. Gold support scope

对于：

```text
SUBSTANTIVE_SUPPORT
```

必须冻结它实际支持的 Requirement 片段。

优先使用：

> Parent Requirement 中的 exact verbatim substring。

禁止为了评分重新自由改写一个新的 sub-requirement。

如果无法用一个连续 substring 表达，

允许多个 verbatim fragments。

这些 fragment 只用于 evaluation。

不得进入 runtime state。

---

# 14. E0 Gold 构造纪律

Gold reference 必须在任何新模型调用之前：

1. 完成；
2. commit；
3. SHA freeze。

可以参考已有历史：

```text
GOLD_MASKS.json
acceptable_full_support_groups
acceptable_partial_support_groups
contributing_claims
reference_binding_context
historical review reasons
```

但必须重新核对：

```text
Original Q
Parent R
Current Claims
```

不得直接把旧模型预测当 Gold。

---

# 15. E1 — Claim–Requirement Support Alignment

E1 不调用 Search。

两个 Arms。

---

# 16. S0 — Binary Support Assignment

输入：

```text
Original Question
Parent Requirement
Current Verified Claims
```

输出：

```json
{
  "support_claim_ids": ["C5"]
}
```

这里只问：

> 哪些 Claims 可以参与 Requirement subtraction？

不提供 anchor/background 分类。

这是最小基线。

---

# 17. S0 System Prompt

```text
You identify which current Verified Claims provide substantive evidentiary
support for one fixed Parent Requirement.

The Original Question and Parent Requirement describe what must ultimately be
established. They are not evidence.

A Claim counts as SUBSTANTIVE SUPPORT only when the Claim itself establishes a
material part of the Parent Requirement with the required entity, participant
role, relation direction, object, temporal attachment, event/document binding,
and candidate branch.

Do NOT count a Claim as support merely because it is:

- topically related;
- about the same person;
- about the same disease;
- about the same university;
- useful for identifying a candidate;
- useful for constructing a search query;
- generic background knowledge;
- compatible with the Requirement.

Examples of non-support:

- a biography of a person does not establish that a target book cites them;
- general disease symptoms do not establish that a specific target patient had
  those symptoms;
- a memorandum date does not establish the date of a different enclosed letter;
- a person's nationality does not establish the country in which a case report
  was reported;
- knowing teammate names does not establish a same-country relation.

Use only the supplied Verified Claims.
Do not use outside knowledge.
Do not use hypotheses.
Do not combine properties from different candidate branches.

Return JSON only:

{
  "support_claim_ids": ["C1", "C5"]
}

If no Claim provides substantive support:

{
  "support_claim_ids": []
}
```

---

# 18. S1 — Typed Scope-Preserving Alignment

输入与 S0 相同。

但要求每个 Claim 被分类。

---

# 19. S1 System Prompt

```text
You classify the epistemic role of every current Verified Claim relative to one
fixed Parent Requirement.

The Parent Requirement states what must ultimately be established.
Claims are the only evidence.

For each Claim assign exactly one primary role:

SUBSTANTIVE_SUPPORT
- The Claim actually establishes a material condition inside the Parent
  Requirement for the correct referent/branch.

BINDING_CONTEXT
- The Claim helps identify or disambiguate a candidate, entity, event, document
  or branch, but does not itself establish a material condition of the Parent
  Requirement.

BACKGROUND
- The Claim provides generic or contextual information that may help reasoning
  or search, but neither establishes the Parent condition nor binds the target
  referent.

IRRELEVANT
- The Claim has no material support or binding role for this Parent Requirement.

Critical rules:

1. Semantic relevance is not evidentiary support.

2. Entity overlap is not relation support.

3. A candidate identity is not evidence for every property attributed to the
   target.

4. Generic background facts cannot satisfy case-specific conditions.

5. Preserve participant roles and relation arguments.

6. Preserve temporal attachment. A date belonging to one object/event cannot be
   transferred to another.

7. Preserve source/document binding.

8. Never combine facts from different candidate branches.

9. Only SUBSTANTIVE_SUPPORT may later be subtracted from the Parent Requirement.

10. BINDING_CONTEXT may help interpret a Support Claim, but can never satisfy a
    Requirement by itself.

For every SUBSTANTIVE_SUPPORT Claim, copy the smallest exact verbatim fragment
or fragments from the Parent Requirement that the Claim actually supports.

Do not paraphrase those fragments.

For non-support Claims use an empty fragment list.

Return JSON only:

{
  "claims": [
    {
      "claim_id": "C1",
      "role": "BINDING_CONTEXT",
      "supported_requirement_fragments": []
    },
    {
      "claim_id": "C5",
      "role": "SUBSTANTIVE_SUPPORT",
      "supported_requirement_fragments": [
        "..."
      ]
    }
  ]
}
```

---

# 20. E1 调用协议

模型：

```text
DeepSeek deepseek-flash
temperature = 0
JSON mode
omit max_tokens
max_retries = 0
concurrency <= 8
```

每 state：

```text
S0 × 2 replicates
S1 × 2 replicates
```

如果最终 N=20：

```text
20 × 2 arms × 2 reps
= 80 calls
```

开始付费调用前：

1. 冻结全部 requests；
2. commit；
3. 输出实际 call estimate；
4. 等待新的明确授权。

不得复用历史授权。

---

# 21. E1 Primary Metrics

## 21.1 Support Precision

\[
\frac{\text{predicted true support}}
{\text{all predicted support}}
\]

这是本轮最重要指标。

False Support 比 Missed Support 更危险。

---

## 21.2 Support Recall

\[
\frac{\text{recovered gold support}}
{\text{all gold support}}
\]

---

## 21.3 Hard-Negative False Promotion

在 Gold role 为：

```text
BINDING_CONTEXT
BACKGROUND
IRRELEVANT
```

的 Claims 中，

被错误升级成：

```text
SUBSTANTIVE_SUPPORT
```

的比例。

---

## 21.4 Support Scope Precision

对于正确识别的 Support Claim，

它复制出的 Requirement fragment 是否真的是该 Claim 支持的 scope。

重点检测：

```text
supporting one component
→ falsely covering whole parent
```

---

## 21.5 Candidate/Branch Mixing

是否把：

```text
Candidate A 的事实
+
Candidate B 的事实
```

合并成同一 Requirement support。

---

## 21.6 Relation-Argument Corruption

包括：

```text
actor ↔ director
subject ↔ spouse
patient nationality ↔ report country
coder country ↔ teammates relation
book author ↔ cited person
memorandum ↔ enclosed letter
```

---

## 21.7 False Full-Support Hazard

根据模型 Support Assignment，

是否可能使一个 Gold 尚未完整支持的 Parent
被错误视为 fully supported。

这是高风险指标。

---

## 21.8 Exact State Support Set

每个 state：

```text
predicted support_claim_ids
==
gold support_claim_ids
```

---

# 22. E1 Secondary Metrics

S1 额外报告：

```text
role accuracy
binding-context recall
background accuracy
exact fragment validity
exact fragment scope
```

但这些不是 closure safety 的替代指标。

---

# 23. E1 Gate

Primary S1 必须满足：

```text
Substantive Support Precision >= 95%

Substantive Support Recall >= 90%

Hard-negative false promotion <= 5%

Support-scope correctness >= 90%

Relation/object/time corruption <= 3%

Candidate-branch mixing <= 2%

False full-support hazard = 0

Schema validity >= 95%
```

S0 作为 baseline 不要求 PASS。

比较：

```text
S1 false-promotion < S0
```

如果两者都已经接近 0，

则不要求严格 `<`，

避免再次出现：

```text
0 < 0
```

这种错误 comparative gate。

改为：

```text
S1 <= S0
```

且满足绝对门槛。

---

# 24. E1 结果解释

## Case A

S1 PASS，S0 较差。

说明：

> 显式 epistemic role + support scope
> 对 Claim–Requirement Alignment 有实际价值。

---

## Case B

S0/S1 都 PASS。

说明：

> Support Alignment 本身对当前 bank 已较容易，
> 不需要额外复杂 typed layer。

优先采用更简单接口。

---

## Case C

S1 precision PASS，但 recall FAIL。

说明：

> 系统保守但容易漏掉已有支持。

这主要造成重复研究，

不是最危险的 false-close 类型。

---

## Case D

S1 false-support / false-full-support FAIL。

说明：

> Claim–Requirement support assignment
> 仍然是当前核心 semantic bottleneck。

停止。

不要进入 E2。

---

# 25. E2 — Downstream Causal Test

只有 S1 不出现严重 false-support hazard 才运行。

E2 测：

\[
\boxed{
Support Alignment
\rightarrow
Residual
}
\]

是否形成因果桥。

---

# 26. E2 使用同一批 states

不要换 bank。

这是一项机制实验，

不是 fresh generalization confirmation。

Fresh validation 后续单独注册。

---

# 27. E2 四个 Arms

## D0 — Raw Claims Baseline

输入：

```text
Parent Requirement
ALL Current Claims
```

这是上一轮 R0 风格 baseline。

模型自己判断什么算 support。

---

## D1 — Binary Model Support Packet

使用对应：

```text
S0 replicate k
```

输出。

输入：

```text
Parent Requirement
Predicted Support Claims
```

不提供其它 Claims。

---

## D2 — Typed Model Evidence View

使用对应：

```text
S1 replicate k
```

输出。

构造：

```text
Parent Requirement

SUBSTANTIVE SUPPORT:
[...]

BINDING CONTEXT:
[...]

BACKGROUND:
[...]

IRRELEVANT:
[omitted]
```

Residualizer 被明确告知：

```text
Only SUBSTANTIVE SUPPORT may satisfy or subtract Parent semantics.

BINDING CONTEXT may only identify/disambiguate referents.
```

---

## D3 — Gold Typed Evidence View

使用 E0 Gold。

这是 capability ceiling / oracle diagnostic。

---

# 28. E2 Residualizer Prompt

```text
You derive the current unresolved semantic residual of one fixed Parent
Requirement.

You receive:

1. the Parent Requirement;
2. an evidence view.

The Parent Requirement is authoritative task semantics.

Only evidence explicitly marked SUBSTANTIVE SUPPORT may count as establishing
part of the Parent Requirement.

BINDING CONTEXT may help determine which entity, candidate, event or document a
Support Claim refers to, but it may not satisfy any Requirement condition by
itself.

BACKGROUND and IRRELEVANT Claims may not be used to subtract Requirement
content.

Your job is to state what material semantic content of the Parent Requirement
still remains unresolved.

Rules:

- Do not repeat content already established by substantive Support.
- Do not subtract content supported only by background or candidate anchors.
- Preserve participant roles, relation direction, object ownership, candidate
  branch, source/event binding and temporal attachment.
- Do not introduce outside knowledge.
- Do not generate a Search query.
- Do not generate a Probe.
- Do not select another Requirement.
- If the Parent Requirement is fully supported, output FULLY_SUPPORTED.
- Otherwise output one faithful residual. The residual may contain multiple
  semantically inseparable conditions if they form one coherent relation.

Return JSON only:

{
  "status": "UNRESOLVED",
  "residual": "..."
}

or:

{
  "status": "FULLY_SUPPORTED",
  "residual": null
}
```

---

# 29. E2 调用协议

每 state：

```text
D0
D1
D2
D3
```

各 2 replicates。

如果 N=20：

```text
20 × 4 × 2
= 160 calls
```

E2 必须在 E1 完成、冻结评分并通过入口后，
再次给出独立 call estimate。

不要把 E1/E2 授权合并。

---

# 30. E2 Primary Metrics

## Strict Residual Validity

必须：

```text
faithful
correct subtraction
no false subtraction
no supported-content leakage
no downstream jump
no argument corruption
```

---

## False Subtraction

Gold unresolved content 被错误删除。

这是 E2 最危险指标。

---

## Supported-Content Leakage

已经真正 supported 的内容仍然出现在 residual。

---

## Full-Support Accuracy

Gold full support 时是否正确输出：

```text
FULLY_SUPPORTED
```

---

## False Full-Support

Gold 未完成时错误输出：

```text
FULLY_SUPPORTED
```

必须单独统计。

---

## State Discrimination

同一：

```text
Q + Parent R
```

随着 Claims 改变，

Residual 是否在需要改变时正确改变。

重点：

```text
q228 G05 → G06
q637 G17 → G18
```

---

# 31. E2 Gate

D3 Gold Typed：

```text
Strict >= 90%

False subtraction <= 3%

False FULLY_SUPPORTED = 0
```

用于证明：

> 如果 support assignment 正确，
> downstream residualizer 有能力工作。

D2 Model Typed：

```text
Strict >= 85%

D3 - D2 <= 10pp

False subtraction <= 5%

False FULLY_SUPPORTED = 0

Supported-content leakage <= 5%

State discrimination >= 80%

Schema >= 95%
```

D1/D0 为诊断 arms。

---

# 32. 最关键的因果解释矩阵

## 情况 1

```text
S1 PASS
D3 PASS
D2 PASS
```

支持：

\[
\boxed{
Claim\text{-}Requirement\ Support\ Alignment
\rightarrow Residual
}
\]

这条 grounded control path 基本成立。

下一独立问题才是：

```text
Support = none
→ Bootstrap
```

---

## 情况 2

```text
S1 FAIL
D3 PASS
```

说明：

> Residualizer 有能力，
> 当前真正瓶颈就是 Claim–Requirement Support Alignment。

这是最清楚的 root-cause result。

---

## 情况 3

```text
S1 PASS
D3 PASS
D2 FAIL
```

说明：

> Alignment 指标看起来正确，
> 但 typed packet 到 Residual 的接口仍丢失关键 binding/context。

检查 packet contract，

不要立刻新增 persistent state。

---

## 情况 4

```text
D3 FAIL
```

说明：

> 即使提供 Gold Support/Context，
> coarse R 仍不能稳定 residualize。

此时才有更强证据支持：

```text
finer control representation
```

或更严格的 relation decomposition。

---

# 33. 本轮必须特别回答的历史 bad cases

最终报告逐个回答：

### Euler

为什么 biography：

```text
不是 book-reference support
```

---

### SPS

为什么 generic disease symptoms：

```text
不是 specific-case support
```

---

### q922

为什么 memorandum date：

```text
不能支持 enclosed-letter date
```

---

### q637

为什么：

```text
patient nationality
```

不能自动支持：

```text
report country
```

---

### q1259

为什么：

```text
coder is Australian
```

不能支持：

```text
the other two teammates are from the same country as each other
```

---

### q228

哪些 Claims 是：

```text
candidate branch context
```

哪些是真正：

```text
marital/childlessness support
```

---

# 34. 错误分类必须至少包含

```text
false_support_entity_overlap
false_support_generic_background
false_support_wrong_relation
false_support_wrong_argument
false_support_wrong_temporal_attachment
false_support_wrong_object
false_support_cross_candidate_merge
missed_true_support
support_scope_overreach
binding_context_promoted_to_support
background_promoted_to_support
false_full_support
```

不要把所有错误笼统写成：

```text
alignment error
```

---

# 35. 不要研究 Zero-Claim Bootstrap

本轮如果：

```text
gold_support_claim_ids = []
```

这些 state 只作为：

> Hard-negative Support Assignment case。

不要运行 Search。

不要生成 Probe。

不要测试 query。

它们的作用是回答：

> 模型会不会因为 Claims 很相关，
> 就错误制造 Support？

---

# 36. 为什么本轮必须这样收窄

因为当前需要先回答：

\[
\boxed{
\textbf{Evidence 已经存在时，
系统是否能正确理解它解决了什么？}
}
\]

如果这一步还不可靠，

继续研究：

```text
无 Claim 时如何搜索第一条 Claim
```

会把两个问题重新混在一起。

---

# 37. 运行纪律

必须：

```text
temperature 0
no retries
no best-of
no post-hoc prompt repair
all failures stay in denominator
```

所有请求、raw outputs、usage 保存。

任何 output schema failure 不补样。

---

# 38. Review 纪律

新 Gold Reference 必须在模型调用前冻结。

模型输出 review：

- mask arm；
- mask replicate；
- 尽可能 mask model packet origin。

Reviewer 不得查看 provider reasoning 来判断 semantic correctness。

如果存在 ambiguous case：

```text
AMBIGUOUS_REFERENCE
```

单独记录，

不得事后为了提高指标改标签。

---

# 39. 完整性

继续保护历史实验文件。

输出：

```text
HISTORICAL_HASHES.json
INTEGRITY.json
EXECUTION_ACCOUNTING.json
ERROR_LEDGER.json
```

必须确认：

```text
previous experiments unchanged
frozen requests unchanged
gold reference unchanged
score replay deterministic
```

---

# 40. 建议目录

```text
experiments/claim_requirement_support_alignment/
├── README.md
├── TASK.md
├── HYPOTHESES.md
├── PROTOCOL.md
├── GATES.json
├── CONFIG.json
├── PRE_EXECUTION_AUDIT.md
├── FREEZE.json
│
├── e0_reference/
│   ├── STATES.json
│   ├── PARENTS.json
│   ├── CLAIM_ROLE_REFERENCE.json
│   ├── SUPPORT_SCOPE_REFERENCE.json
│   └── BANK_REPORT.md
│
├── e1_support_alignment/
│   ├── SCHEDULE.json
│   ├── calls/
│   ├── review/
│   ├── METRICS.json
│   └── REPORT.md
│
├── e2_downstream_residual/
│   ├── STATUS.json
│   ├── SCHEDULE.json
│   ├── calls/
│   ├── review/
│   ├── METRICS.json
│   └── REPORT.md
│
└── analysis/
    ├── ERROR_LEDGER.json
    ├── STATE_DISCRIMINATION.json
    ├── EXECUTION_ACCOUNTING.json
    ├── SENSITIVITY.json
    ├── INTEGRITY.json
    └── FINAL_CONCLUSION.md
```

---

# 41. 最终报告必须回答

1. 模型能否可靠区分 semantic relatedness 与 substantive support？
2. False Support 的主要来源是什么？
3. Candidate anchor 是否经常被提升成 support？
4. Generic background 是否经常被提升成 support？
5. Relation argument / temporal / object binding 是否稳定？
6. S1 typed alignment 是否优于 simple binary alignment？
7. Support scope 能否正确定位到 Parent 的实际语义片段？
8. Gold typed Support 是否足以稳定产生正确 Residual？
9. Model typed Support 与 Gold typed Support 差多少？
10. Raw all-Claims 与 typed packet 相比谁更可靠？
11. false subtraction 的来源主要是 alignment 还是 residualizer？
12. 是否观察到 false-full-support hazard？
13. q228 / q637 的 trajectory 是否被正确区分？
14. 历史 Euler / SPS / letter-date / teammate bad case 是否重现？
15. 当前是否需要新的 persistent State field？
16. 当前是否需要 finer persistent Requirement nodes？
17. grounded path：

```text
Claims
→ Support Assignment
→ Residual
```

是否已经足够可靠？
18. 是否有资格进入下一独立：

```text
Zero-Support Evidence Bootstrap
```

实验？

---

# 42. 本轮最重要的成功标准

这次不要把重点放在：

```text
role classification overall accuracy
```

最重要的是：

\[
\boxed{
\textbf{False Support 是否被压到足够低。}
}
\]

因为：

```text
Missed Support
→ 多搜一次
```

通常仍然可恢复。

而：

```text
False Support
→ Wrong subtraction
→ False close
→ Potential false STOP
```

是更危险的不可逆控制方向。

因此所有最终结论必须优先报告：

```text
Support Precision
Hard-negative false promotion
False subtraction
False FULLY_SUPPORTED
```

---

# 43. 本轮停止条件

即使 E1、E2 全部 PASS：

也必须停止。

禁止自动进入：

```text
Search
Probe
Writer
4–8 step loop
```

下一实验再独立研究：

\[
\boxed{
\textbf{当 Support(R,C)=∅ 时，
如何获取第一条真正的 Support Claim。}
}
\]

即：

```text
experiment/zero-support-evidence-bootstrap
```

---

# 44. 本轮最终要验证的核心命题

不是：

> Claims 与 Requirement 是否“相关”。

而是：

\[
\boxed{
\textbf{
Can the agent distinguish evidence that merely helps search
from evidence that actually satisfies part of the task?
}
}
\]

如果这一步成立，

那么 grounded research control 可以写成：

\[
\boxed{
R+C
\rightarrow Support
\rightarrow Residual
}
\]

而无 Support 时再进入：

\[
\boxed{
R
\rightarrow Bootstrap
}
\]

这是下一阶段才处理的问题。