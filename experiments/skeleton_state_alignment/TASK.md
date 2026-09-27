# Search-ESR：Skeleton–Claims Alignment / Plan–State Reconciliation 实验任务书

## 0. 本轮总目标

继续 `homulillew/Search-ESR` 当前研究路线。

本轮验证两个严格分开的机制。

第一阶段：

\[
\boxed{
TaskSkeleton + VerifiedClaims
\rightarrow
CoverageMask
}
\]

第二阶段，仅在第一阶段通过后运行：

\[
\boxed{
CoverageMask
\rightarrow
ActiveRequirementID
}
\]

本轮不重新生成自然语言 Local Obligation。

本轮不修改 Task Skeleton semantics。

本轮不运行：

```text
Gap
Search
Find
Open
Writer
full rollout
```

---

# 1. 当前已经得到的实验事实

已有研究链条：

## 1.1 Q-only Task Canonicalization

最新：

```text
experiment/ephemeral-obligation-decomposition
```

表明：

\[
Q\rightarrow TaskSkeleton
\]

在当前 bank 上具有很强绝对可行性。

Development：

```text
D0 18/20 strict
D1 20/20 strict
D2 20/20 strict
```

Repository-experiment-unexposed fresh：

```text
D0 24/24 strict
D2 24/24 strict
```

其中 D2 为 source-span extractive grouping。

Fresh comparative gate 因：

```text
D0 corruption = 0
D2 corruption = 0
```

无法满足严格：

```text
D2 < D0
```

而 FAIL。

因此正确结论是：

> Q-only Task Skeleton 的绝对可行性获得强正向信号；D2 相对于强 D0 baseline 的 superiority 未得到证明。

---

## 1.2 Dynamic Local Obligation

直接：

\[
Q+C\rightarrow LocalO
\]

长期只有约：

```text
46%–54% strict
```

加入：

```text
Recent Claim Delta
Recent Path
Recent Observation
```

仍没有得到可靠 Direct-O。

---

## 1.3 Gold-O Evidence Gap

当局部任务已经由人工正确固定：

\[
GoldO+C\rightarrow Gap
\]

开发结果约：

```text
92.6% strict
```

因此当前最重要的缺口已经移动到：

\[
\boxed{
Task semantics
\leftrightarrow
Evidence state
}
\]

即：

> 原始问题已经能够展开成稳定的 Task Skeleton，但尚未证明系统能够把当前 Verified Claims 正确映射回这个 Skeleton。

---

# 2. 当前核心假设

原始问题：

\[
Q
\]

先 canonicalize 为：

\[
R=\{R_1,\ldots,R_k\}
\]

其中 R 是相对稳定的 Task Skeleton。

当前 evidence state：

\[
C_t=\{C_1,\ldots,C_m\}
\]

真正缺失的计算可能是：

\[
\boxed{
M_t=Align(R,C_t)
}
\]

其中：

```text
R1 → fully_supported
R2 → partially_supported
R3 → unsupported
...
```

然后：

\[
Residual_t
=
\{R_i\mid status_i\neq fully\_supported\}
\]

关键原则：

\[
\boxed{
Residual\ should\ be\ derived,\ not\ freely\ generated.
}
\]

---

# 3. 当前候选闭环

若本实验最终支持该路线，则候选架构为：

```text
Original Q
   ↓
Task Skeleton R
   ↓
R + Claims
   ↓
Coverage Mask
   ↓
Residual Requirements
   ↓
select Requirement ID
   ↓
Requirement + Claims
   ↓
Evidence Gap
   ↓
Gap + H + Workspace
   ↓
Search / Find / Open
   ↓
Evidence
   ↓
Writer
   ↓
Claims update
   ↓
重新计算 Coverage Mask
```

其中：

```text
Task semantics = stable
Claims = dynamic
Mask = ephemeral
Active Requirement = ephemeral
Gap = ephemeral
```

---

# 4. 最新远程锚点

开始执行前必须：

```bash
git fetch origin --prune
git status
git branch --show-current

git rev-parse origin/main
git rev-parse origin/experiment/ephemeral-obligation-decomposition

git log --oneline --decorate -20 \
  origin/experiment/ephemeral-obligation-decomposition
```

任务编写时最新：

```text
origin/experiment/ephemeral-obligation-decomposition
7fdb048e856545facd4acfb590e8cf28c46f1013
```

latest commit：

```text
Report skeleton feasibility and fresh comparative gate failure
```

若 fetch 后分支已经前移：

1. 阅读全部新增 commit；
2. 确认是否已有 Skeleton–Claims alignment 实验；
3. 写入 `PRE_EXECUTION_AUDIT.md`；
4. 不得静默使用旧 SHA。

---

# 5. 创建新分支

建议：

```bash
git switch -c experiment/skeleton-state-alignment \
  origin/experiment/ephemeral-obligation-decomposition
```

新目录：

```text
experiments/skeleton_state_alignment/
```

历史实验全部只读。

---

# 6. 本轮最重要的职责分离

本实验严格区分：

### Task Skeleton R

表示：

> 原始问题要求最终建立什么。

它不是 evidence。

---

### Claims C

表示：

> 当前已经被证据支持什么。

只有 Claims 有 epistemic authority。

---

### Coverage Mask M

表示：

> 当前 Claims 对每个 Requirement 覆盖到什么程度。

它是 ephemeral calculation。

---

### Residual

机械定义为：

\[
status\neq fully\_supported
\]

不让模型重新生成一个 residual question。

---

# 7. E0 — Control Addressability Audit

在任何新模型 API 调用前，先做纯离线审计。

目的：

> 当前 Task Skeleton 的节点粒度是否真的足以表示历史上合理的 Local Obligation？

输入材料：

```text
27 historical natural states
historical Gold Obligations
D1 Task Skeleton
D2 Task Skeleton
```

Gold Obligation 只用于评价。

绝不进入后续 alignment 模型输入。

---

# 8. 为什么必须先做 Addressability

Task Skeleton “语义正确”不意味着“控制粒度合适”。

例如 Skeleton：

```text
R3:
identify a paper satisfying
A+B+C+D
```

而历史合理 LocalO 可能只是：

```text
verify C
```

如果 C 与 A/B/D 是独立的 research objective，

那 R3 对 runtime control 来说可能太粗。

因此本轮需要新增：

\[
\boxed{
Control\ Addressability
}
\]

---

# 9. Addressability 分类

对每个：

```text
historical state × Gold Local Obligation
```

分别在 D1 / D2 Skeleton 上标：

### directly_addressable

一个 Skeleton node 可以作为该 LocalO，

且不会捆绑明显独立目标。

---

### coherently_multi_addressable

LocalO 合理对应少量多个 node，

且它们共同构成一个 coherent research episode。

---

### subnode_only

LocalO 只是某个 Skeleton node 中的一小部分，

而该 node 还包含当前无关的独立研究目标。

---

### not_addressable

当前 Skeleton 无法忠实表示该 LocalO。

---

# 10. Addressability 不是 exact-match

不要要求：

```text
GoldO wording == Skeleton node wording
```

只判断：

> 当前 Skeleton 是否能够不破坏语义地承载一个合法 research control target。

---

# 11. E0 指标

分别报告 D1 / D2：

```text
Direct addressability
Direct + coherent-multi addressability
Subnode-only rate
Not-addressable rate
```

同时按历史类型分层：

```text
identity_discovery
relation_verification
downstream_temptation
scope_binding
satisfied_control
```

---

# 12. E0 不允许自动选“最好 Skeleton”

D2 仍然是本实验预注册 runtime primary representation。

原因不是“D2 已证明更准确”，而是：

```text
source spans are authoritative
free paraphrase is minimized
task semantics remain directly auditable
```

D1 作为结构粒度诊断参考。

如果 E0 显示 D2：

```text
direct+coherent addressability < 80%
```

或者：

```text
critical not-addressable > 10%
```

仍然保留结果并继续 E1，

但必须明确：

> runtime representation 可能太粗。

不得事后切换到 D1 并称为 primary。

---

# 13. Runtime Skeleton 的冻结规则

对于每个 exposed qid：

D2 Runtime Skeleton 使用上一实验：

```text
D2 replicate 1
```

固定选择。

不得：

```text
best-of R1/R2
manual merge
manual split
post-hoc repair
```

生成：

```text
e0_reference/RUNTIME_SKELETON_D2.json
```

Skeleton node ID 机械按原输出顺序：

```text
R1
R2
R3
...
```

---

# 14. Oracle Skeleton

另外构建：

```text
ORACLE_RUNTIME_SKELETON.json
```

目的：

> 提供 alignment 能力的上界路径。

Oracle Skeleton 必须：

1. 只依据 Original Question；
2. 只依据上一实验已经冻结的 Task Structure reference；
3. source-anchored；
4. 不看当前 state Claims；
5. 不看 historical Gold Obligation；
6. 不为某个具体 research checkpoint 优化粒度。

因此 Oracle Skeleton 是：

> question-level semantic reference，

不是 state-specific plan。

---

# 15. Oracle Skeleton 先冻结，再看 GoldO Addressability

顺序必须是：

```text
Q
→ Oracle Skeleton
→ freeze
→ 再做 historical GoldO addressability
```

不得使用历史 Gold LocalO 反过来设计 Oracle Skeleton。

否则会把 state-specific control 泄漏到 Task semantics。

---

# 16. E1 — Skeleton–Claims Alignment

核心问题：

\[
\boxed{
Given\ R\ and\ C_t,
can\ the\ model\ correctly\ determine
which\ requirements\ are\ already\ supported?
}
\]

---

# 17. E1 使用 27 个 historical natural states

这次应该保留全部 27 states。

原因：

虽然只有 10 个 unique Q，

但 Claims 状态不同：

\[
C_0,C_1,C_2,\ldots
\]

这正是本实验要测试的变化。

因此 primary unit 为：

```text
state
```

而不是 unique question。

同时所有结果都必须按 qid cluster 分层报告。

---

# 18. E1 两个主要 Arms

## A0 — Oracle Skeleton

输入：

\[
Q+R^{oracle}+C_t
\]

测试：

> 如果 Task Skeleton 是人工正确且粒度合理的，alignment 本身能做到多好？

---

## A1 — Runtime D2 Skeleton

输入：

\[
Q+R^{D2}+C_t
\]

测试：

> 实际模型生成并冻结的 source-anchored Skeleton 是否明显拖累 alignment？

---

# 19. 为什么暂时不加入 D1 模型调用

D1 在 E0 中继续作为 granularity diagnostic。

但 E1 只测试：

```text
Oracle
vs
Runtime D2
```

这样保持实验清晰。

如果未来发现 D2 alignment 明显受节点粗度影响，

另开实验测试 D1。

---

# 20. Original Q 是否继续提供？

提供。

但 System Prompt 必须明确：

> Original Question is only contextual support for resolving references and source spans.

禁止模型：

```text
重新分解 Q
新增 Requirement
合并 Requirement
修改 Skeleton
```

Task Skeleton 是当前 call 中的固定 semantic plan。

---

# 21. Coverage Mask 状态定义

每个 Requirement 只能是：

```text
fully_supported
partially_supported
unsupported
```

---

## fully_supported

只有当 Verified Claims **共同建立了 Requirement 中全部 material semantic conditions** 时才能使用。

不是：

> “看起来很像”。

不是：

> “Claims 里出现了相同实体”。

不是：

> “搜索过相关内容”。

---

## partially_supported

Requirement 中至少一个 substantive condition 已由 Claims 支持，

但至少一个 material condition 仍未支持。

---

## unsupported

Claims 尚未支持 Requirement 的任何 substantive material condition。

仅有：

```text
同名实体
相关背景
相关来源
候选猜测
```

不能算 partial。

---

# 22. Task Requirement 不是事实

System Prompt 必须重点强调：

> A requirement states what the Original Question requires to be established.
>
> Its presence in the Task Skeleton does NOT mean the requirement is true or already supported.

这是本轮最关键的 invariant。

否则会重现 Premise Checker 错误。

---

# 23. E1 输出结构

严格：

```json
{
  "requirements": [
    {
      "requirement_id": "R1",
      "status": "fully_supported",
      "supported_by": ["C1", "C3"]
    },
    {
      "requirement_id": "R2",
      "status": "partially_supported",
      "supported_by": ["C4"]
    },
    {
      "requirement_id": "R3",
      "status": "unsupported",
      "supported_by": []
    }
  ]
}
```

不得输出：

```text
next_action
priority
gap
query
reasoning
confidence
STOP
hypothesis
```

---

# 24. `supported_by` 的含义

只列：

> 实际对该 Requirement 当前覆盖有实质贡献的 Verified Claims。

不得因为 Claim：

```text
提到同一个人
提到同一个文档
主题相关
```

就引用。

---

# 25. fully_supported 的 supported_by

如果 status：

```text
fully_supported
```

则：

```text
supported_by
```

中的 Claims 必须共同足以支持 Requirement 的全部 material content。

---

# 26. partial 的 supported_by

如果：

```text
partially_supported
```

则 supported_by：

> 必须真正支持 Requirement 的一个 substantive 部分，

但不能完整覆盖全部 material condition。

---

# 27. unsupported

如果：

```text
unsupported
```

原则上：

```json
"supported_by": []
```

除非未来 schema 专门允许 background relation。

本轮不要允许。

这样语义更干净。

---

# 28. E1 统一 System Prompt

```text
You reconcile a fixed Task Skeleton with the current Verified Claims.

You receive:

1. the Original Question;
2. a fixed Task Skeleton derived from that Original Question;
3. the current Verified Claims.

The Task Skeleton describes what the Original Question requires to be
established.

IMPORTANT:
A Task Requirement is NOT evidence.
Its presence in the Task Skeleton does not mean that it is true,
that its referent exists, or that it has already been established.

Only the Verified Claims may establish support.

For every Task Requirement, assign exactly one status:

- fully_supported
- partially_supported
- unsupported

Definitions:

fully_supported:
The Verified Claims collectively establish all material semantic
conditions expressed by this requirement.

partially_supported:
The Verified Claims establish at least one substantive material part
of the requirement, but one or more material parts remain unsupported.

unsupported:
The Verified Claims do not establish any substantive material part of
the requirement. Mere topical relevance, entity-name overlap,
candidate mention, prior search direction, or background context does
not count as support.

Rules:

1. Do not change, merge, split, rewrite, add, or delete Task Requirements.

2. Use the Original Question only to resolve references or interpret the
fixed Task Skeleton. Do not re-decompose the question.

3. Treat the Verified Claims as the complete evidence state available
for this judgment.

4. Do not use outside knowledge.

5. Do not infer a fact merely because the Original Question requires it.

6. Do not infer a fact merely because an entity, event, document, date,
role, relation, or attribute is mentioned by the Task Skeleton.

7. A Claim supports a Requirement only when the Claim materially
establishes part of what that Requirement requires.

8. For fully_supported, the cited Claims must collectively cover all
material content of the Requirement.

9. For partially_supported, the cited Claims must establish a substantive
subset but not all material content.

10. For unsupported, supported_by must be empty.

11. Do not output a search plan, next action, priority, hypothesis,
confidence, evidence gap, coverage summary, or STOP decision.

12. Preserve every input requirement_id exactly once.

Return JSON only:

{
  "requirements": [
    {
      "requirement_id": "R1",
      "status": "fully_supported",
      "supported_by": ["C1"]
    }
  ]
}
```

---

# 29. E1 输入 schema

例如：

```json
{
  "Original Question": "...",

  "Task Skeleton": [
    {
      "requirement_id": "R1",
      "source_spans": [
        {
          "unit": "Q2",
          "text": "..."
        }
      ]
    }
  ],

  "Verified Claims": [
    {
      "claim_id": "C1",
      "statement": "..."
    }
  ]
}
```

Oracle Skeleton 可以有：

```text
label
```

但 source spans 仍是语义 authority。

Runtime D2 不需要 authoritative prose。

---

# 30. E1 Gold Alignment Reference

任何模型调用前，

对：

```text
27 states × A0/A1 skeleton
```

全部冻结人工/Codex Gold Mask。

格式：

```json
{
  "state_id": "...",
  "skeleton_arm": "A1",

  "requirements": {
    "R1": {
      "status": "fully_supported",
      "acceptable_full_support_groups": [
        ["C1", "C2"],
        ["C4"]
      ],
      "contributing_claims": ["C1", "C2", "C4"]
    },

    "R2": {
      "status": "partially_supported",
      "acceptable_full_support_groups": [],
      "contributing_claims": ["C3"]
    },

    "R3": {
      "status": "unsupported",
      "acceptable_full_support_groups": [],
      "contributing_claims": []
    }
  }
}
```

---

# 31. Gold reference 允许多个支持组合

不要要求模型：

```text
supported_by
```

与人工 reference 完全相同。

如果：

```text
C1+C2
```

足够，

而：

```text
C4
```

单独也足够，

两者都合法。

---

# 32. Gold Mask 编写纪律

必须：

1. 只看当前 Q；
2. 当前 Skeleton；
3. 当前 Verified Claims；
4. 不看模型未来 alignment 输出；
5. 不看 future Claims；
6. 不用 outside knowledge；
7. 不因为 historical GoldO 暗示当前 active target 而改变 status。

---

# 33. E1 调用规模

两个 arms：

```text
27 states
× 2 arms
× 2 replicates
= 108 calls
```

DeepSeek：

```text
model = deepseek-flash
temperature = 0
JSON mode
max_retries = 0
omit max_tokens
max concurrency = 8
```

所有 calls 在同一个 deterministic mixed schedule 中。

---

# 34. E1 First-pass Review

Reviewer 第一轮只看：

```text
Original Q
Task Skeleton
Claims
Generated Mask
```

隐藏：

```text
arm
replicate
Gold mask
historical GoldO
aggregate
provider reasoning
```

先评：

```text
status correctness
support correctness
```

commit 后才揭盲。

---

# 35. E1 Primary Metrics

## Node Status Accuracy

\[
\frac{correct\ node\ statuses}
{all\ skeleton\ nodes}
\]

---

## Fully-Supported Precision

模型预测 fully_supported 中，

真正 fully_supported 的比例。

---

## False-Supported Rate

Gold 为：

```text
partial / unsupported
```

却预测：

```text
fully_supported
```

这是最危险指标。

---

## False-Unresolved Rate

Gold：

```text
fully_supported
```

却预测：

```text
partial / unsupported
```

这主要导致重复研究。

---

# 36. Residual Metrics

Harness 机械定义：

```text
Residual =
all nodes not predicted fully_supported
```

然后比较 Gold Residual。

报告：

```text
Residual Recall
Residual Precision
Residual F1
```

其中：

\[
\boxed{
ResidualRecall
}
\]

比 Precision 更重要。

因为漏掉真正 unresolved node 可能导致 premature STOP。

---

# 37. Support Binding

分别报告：

### Support Precision

模型引用的 Claim 是否真的对 Requirement 有贡献。

---

### Full-Support Sufficiency

对于：

```text
fully_supported
```

引用 Claims 是否足以完整覆盖该 Requirement。

---

### Partial-Support Validity

对于：

```text
partially_supported
```

引用 Claims 是否确实覆盖了 substantive subset，

但没有完整支持 Requirement。

---

# 38. State-Level Exact Mask

一个 state 中所有 requirement：

```text
status
```

全部正确，才算：

```text
ExactMask = true
```

这是非常重要的 end-state metric。

---

# 39. Monotonic Progress Consistency

对同一个 qid 的历史状态序列：

```text
S0 → S1 → S2 ...
```

如果 Claims 只增加、没有 refutation，

检查 Requirement status 是否出现不合理：

```text
fully_supported → unsupported
```

这只是描述性指标。

不要作为 primary gate，

因为 Claims 可能发生语义 refinement。

---

# 40. E1 A0 Gate — Alignment 本身是否可行

Oracle Skeleton A0 必须满足全部：

```text
Node Status Accuracy >= 90%

False-Supported Rate <= 5%

Residual Recall >= 95%

Support Precision >= 90%

Full-Support Sufficiency >= 90%

Exact State Mask >= 80%

Schema Validity >= 95%
```

如果 A0 FAIL：

\[
\boxed{STOP}
\]

不要进入 Selection。

结论：

> 即使任务语义由人工固定，Task–Evidence Alignment 仍不够可靠。

---

# 41. E1 A1 Gate — Runtime Skeleton 是否可用

Runtime D2 A1 建议：

```text
Node Status Accuracy >= 85%

False-Supported <= 7.5%

Residual Recall >= 90%

Support Precision >= 85%

Exact State Mask >= 70%

Schema >= 95%
```

同时定义：

\[
AlignmentLoss
=
A0\ ExactMask
-
A1\ ExactMask
\]

要求：

```text
AlignmentLoss <= 10 percentage points
```

以及：

```text
Node Status Accuracy loss <= 10pp
```

---

# 42. E1 结果解释

### Case A

A0 PASS，A1 PASS。

说明：

> stable Task Skeleton 与 Claims 可以可靠形成 Coverage Mask。

进入 E2。

---

### Case B

A0 PASS，A1 FAIL。

说明：

> Alignment 能力本身存在，但 Runtime D2 Skeleton 的 representation/granularity 正在拖累它。

下一步研究 D1 或 Skeleton refinement。

不进入 E2。

---

### Case C

A0 FAIL。

说明：

> 真正瓶颈就是 Task–Evidence Alignment。

接受结果。

不要继续架构堆叠。

---

# 43. E2 — Active Requirement Selection

只有：

```text
A0 PASS
AND
A1 PASS
```

才运行。

E2 不生成自然语言 Obligation。

输出：

```text
requirement_id
```

---

# 44. 为什么只输出 ID

因为 Task Skeleton 已经有稳定 semantics。

如果再次：

```text
R3
→ paraphrase
→ Local Obligation sentence
```

会重新引入：

```text
argument corruption
date movement
relation strengthening
```

所以：

\[
\boxed{
ActiveO
=
RequirementID
}
\]

而不是重新写一句话。

---

# 45. E2 固定使用 Runtime D2 Skeleton

两条 Mask Path：

## S0 — Oracle Mask

使用：

```text
D2 Skeleton
+
human Gold Mask
```

目的：

> 单独测试 selection 本身。

---

## S1 — Model Mask

使用：

```text
D2 Skeleton
+
A1 replicate 1 predicted Mask
```

固定：

```text
replicate 1
```

绝不 best-of。

目的：

> 测真实 Mask error 传入 selection 后的 end-to-end loss。

---

# 46. 为什么 Oracle Mask 也用 D2 Skeleton

为了保持：

```text
Skeleton semantics
```

完全相同。

S0 与 S1 唯一区别：

```text
Gold Mask
vs
Model Mask
```

这样才能定位 selection loss 与 alignment loss。

---

# 47. E2 Selection Reference

在任何 E2 model call 前，

对 27 states 冻结：

```text
SELECTION_REFERENCE.json
```

每条：

```json
{
  "state_id": "...",

  "acceptable_active_ids": ["R3", "R4"],

  "invalid_supported_ids": ["R1"],

  "blocked_or_downstream_ids": ["R5"],

  "stop_allowed": false
}
```

---

# 48. Acceptable Selection 不是唯一 Gold

ACT 是 existential。

如果：

```text
R3
```

和：

```text
R4
```

都是合法、有用、当前 unresolved 的局部目标，

二者均成功。

不得要求模型复现 historical GoldO。

---

# 49. Selection Reference 的依据

一个 Requirement 可列入：

```text
acceptable_active_ids
```

必须：

1. 当前不是 fully supported；
2. 对回答 Q 有 material value；
3. 本身 sufficiently local；
4. 当前 referent / relation 已足够可研究，或者该 requirement 本身就是用于建立该 referent/relation；
5. 不跳过明显 prerequisite；
6. 选择后能够合理进入 `Requirement + Claims → Gap`。

---

# 50. blocked/downstream

例如：

```text
R2 = establish later article
R3 = obtain article title
```

若 R2 仍未建立，

且 R3 只是纯 attribute extraction，

则：

```text
R3
```

应标：

```text
blocked_or_downstream
```

---

# 51. STOP

E2 schema 允许：

```json
{
  "selection": "STOP"
}
```

但 STOP 只有当：

> 所有 material Task Requirements fully supported

时合法。

如果当前 27 states 中没有完整完成的自然状态：

必须明确报告：

```text
No natural positive STOP controls in this bank.
```

不得凭空生成 complete state。

---

# 52. E2 Unified Selection Prompt

```text
You select the next active Task Requirement from a fixed research plan.

You receive:

1. the Original Question;
2. a fixed Task Skeleton;
3. the current Coverage Mask for that Skeleton.

The Task Skeleton defines the meaning of the research task.
Do not rewrite or reinterpret it.

Choose exactly ONE requirement_id that is appropriate to work on next.

A useful active requirement must:

1. not be fully supported;

2. materially advance answering the Original Question;

3. be sufficiently local to serve as one current research objective;

4. not skip an unresolved prerequisite merely to request a downstream
attribute;

5. be allowed to establish or identify an entity, event, relation,
document, or value that is itself still unknown;

6. not be rejected merely because the information it asks to establish
is currently unknown;

7. preserve the fixed meaning and scope of the selected Task Requirement.

If multiple requirements are equally legitimate current objectives,
choose any one.

Do not attempt a complete global replanning.
Finding one useful active requirement is sufficient.

You may return STOP only if every material Task Requirement is already
fully supported.

Do not output:
- a rewritten obligation;
- a search query;
- a plan;
- a source preference;
- a hypothesis;
- a confidence score;
- an explanation.

Return JSON only:

{
  "selection": "R3"
}

or:

{
  "selection": "STOP"
}
```

---

# 53. E2 不加入 Delta/Path

第一轮 selection 实验只测试：

\[
ResidualMask
\rightarrow ActiveID
\]

不要重新加入：

```text
Recent Claim Delta
Recent Path
H
Workspace
```

否则又无法知道 selection 本身是否已经足够。

如果 Selection PASS，

未来再独立测试：

```text
Residual
vs
Residual + Delta
```

---

# 54. E2 调用规模

```text
27 states
× 2 mask arms
× 2 replicates
= 108 calls
```

因此如果 E1 + E2 全执行：

```text
108 + 108 = 216 calls
```

---

# 55. E2 Metrics

## Valid Selection

选择属于：

```text
acceptable_active_ids
```

---

## Selected Supported

选择一个：

```text
fully_supported
```

Requirement。

这是明显错误。

---

## Downstream Selection

选择：

```text
blocked_or_downstream
```

Requirement。

---

## False STOP

Mask/reference 中仍有 material unresolved，

却输出：

```text
STOP
```

---

## Missed STOP

存在完整 coverage control 时，

应该 STOP 却选 Requirement。

如果无 natural positive STOP：

只报告：

```text
not evaluated
```

---

## Selection Stability

同一 state 两次：

```text
same acceptable ID
compatible different valid IDs
one valid one invalid
both invalid
```

不同但合法的 ID 不算 semantic failure。

---

# 56. E2 S0 Gate — Selection 本身

Oracle Mask S0：

```text
Valid Selection >= 85%

Selected Supported <= 5%

Downstream Selection <= 10%

False STOP <= 5%

Schema >= 95%
```

如果 S0 FAIL：

停止。

说明：

> 即使 Coverage Mask 正确，Active Requirement Selection 仍是独立瓶颈。

---

# 57. E2 S1 Gate — End-to-End Control Bridge

Model Mask S1：

```text
Valid Selection >= 80%

Selected Supported <= 7.5%

Downstream <= 10%

False STOP <= 7.5%

Schema >= 95%
```

定义：

\[
SelectionLoss
=
S0\ ValidSelection
-
S1\ ValidSelection
\]

要求：

```text
SelectionLoss <= 10pp
```

---

# 58. 如果 E2 PASS

本轮立即停止。

不要继续：

```text
Gap
Search
Writer
full loop
```

只允许结论：

> Stable Task Skeleton → Coverage Mask → Active Requirement ID is sufficiently promising on the exposed historical development bank to justify a separately preregistered closed-loop rollout.

---

# 59. E2 PASS 后下一独立实验

建议新分支：

```text
experiment/skeleton-guided-research-loop
```

只做：

```text
4–8 decision rollout
```

链路：

```text
R
→ Mask
→ ActiveRequirementID
→ frozen Gap Generator
→ Search/Find/Open
→ Writer
→ Claims
→ recompute Mask
```

然后看真实：

```text
useful evidence
redundant search
downstream jump
mask progress
final coverage
STOP
```

---

# 60. 本轮不要重新训练 Gap Generator

如果 E2 后未来进入闭环：

使用已经冻结验证过的：

```text
Gold-O evidence-gap prompt
```

但输入中的 Local Obligation 改成：

```text
selected Requirement
```

不要重新设计 Gap prompt。

---

# 61. Persistent / Ephemeral Boundary

即使本实验 PASS：

仍不要直接 persistent 保存：

```text
status
progress
Residual
ActiveO
```

推荐：

### Episode-stable

```text
Original Q
Task Skeleton R
```

### Persistent epistemic

```text
Claims C
Hypothesis H
```

### Mechanical

```text
Workspace
Trace
D/W
```

### Recomputed each control cycle

```text
Coverage Mask
Residual
Active Requirement
Gap
```

---

# 62. 为什么 Mask 应每轮重算

不要维护：

```text
R3.status = partial
```

然后增量修改。

而是：

\[
Mask_t=Align(R,C_t)
\]

每轮重新计算。

这样避免：

```text
stale status
state-transition bookkeeping bugs
persistent semantic drift
```

Task meaning 稳定。

Evidence state 更新。

Status 临时计算。

---

# 63. STOP 的未来定义

未来如果：

\[
Residual_t=\varnothing
\]

并且：

```text
answer target fully supported
```

可以进入 final closure audit。

但 STOP 仍建议：

\[
Q+R+C
\rightarrow GlobalCoverageAudit
\]

做最后一次 verification。

不要仅因为 selector 没有找到节点就 STOP。

---

# 64. 失败时如何解释

## A0 FAIL

根因定位：

\[
\boxed{
Task\text{-}Evidence\ Alignment
}
\]

即使正确 Skeleton 给定，

Claims 仍不能稳定 mask Task Plan。

---

## A0 PASS / A1 FAIL

根因：

\[
\boxed{
Runtime\ Skeleton\ representation
}
\]

可能包括：

```text
node too broad
pronoun/reference ambiguity
source span not self-contained
control resolution insufficient
```

---

## E1 PASS / S0 FAIL

根因继续下移到：

\[
\boxed{
Frontier\ Selection
}
\]

---

## S0 PASS / S1 FAIL

Selection 本身可以，

但 Alignment errors 会传播到 control。

---

## E1 + E2 PASS

则目前最核心的 Plan–Monitor–Select bridge 已经建立。

这时才值得正式跑闭环。

---

# 65. 预注册错误 taxonomy

E1：

```text
false_supported
false_unresolved
partial_as_full
partial_as_none
wrong_support_claim
insufficient_support_group
entity_overlap_as_support
task_requirement_as_fact
outside_knowledge
output_contract
mechanical_failure
```

E2：

```text
selected_supported
downstream_selection
low_value_selection
false_stop
missed_stop
invalid_requirement_id
output_contract
mechanical_failure
```

---

# 66. 特别追踪 Premise Checker 老错误是否复发

重点 case：

### unknown target promoted to fact

例如：

```text
question describes a later article
```

Skeleton 中有 later article requirement，

但 Claims 尚未建立它。

不得因此：

```text
fully_supported
```

---

### candidate entity mention

Claims 中仅出现：

```text
Euler
```

不等于：

> Euler 是目标书中 L.E.

---

### relation target

Requirement 本身要验证：

```text
same country(A,B)
```

不能因为 A/B 已知：

> 自动判 relation fully supported。

---

# 67. E0/E1/E2 Reference Freeze

所有以下内容必须在对应 model call 前 commit：

```text
Oracle Skeleton
D2 Runtime Skeleton
Addressability labels
Gold Coverage Masks
Selection acceptable sets
blocked sets
STOP labels
prompts
schemas
gates
schedule
review rubric
```

不得看到结果后修改。

---

# 68. Review Independence

单 Reviewer 限制必须明确。

建议：

E1 first pass 隐藏：

```text
arm
replicate
Gold
aggregate
provider reasoning
```

E2 first pass 隐藏：

```text
mask arm
replicate
acceptable selection set
historical GoldO
```

所有 primary labels commit 后再 aggregate。

---

# 69. Provider / Mechanical Rules

继续沿用历史：

```text
DeepSeek deepseek-flash
temperature 0
JSON mode
omit max_tokens
max_retries 0
max concurrency 8
```

JSON prompt 必须含 literal：

```text
JSON
```

所有 planned slot 留 denominator。

不允许：

```text
retry
best-of
repair
response replacement
adaptive prompt patch
```

---

# 70. Paid Call 授权

如果当前环境已经存在对本新实验明确适用的用户授权：

按冻结计划执行。

否则先完成：

```text
offline reference
freeze
tests
preflight
call estimate
```

然后停止在：

```text
PREPARED_FOR_EXECUTION
```

不得把旧实验授权自动扩展到新的 paid call budget。

---

# 71. 建议目录

```text
experiments/skeleton_state_alignment/
├── README.md
├── TASK.md
├── HYPOTHESES.md
├── PROTOCOL.md
├── CONFIG.json
├── GATES.json
├── FREEZE.json
├── PRE_EXECUTION_AUDIT.md
│
├── e0_addressability/
│   ├── ORACLE_RUNTIME_SKELETON.json
│   ├── RUNTIME_SKELETON_D1.json
│   ├── RUNTIME_SKELETON_D2.json
│   ├── ADDRESSABILITY.json
│   └── REPORT.md
│
├── e1_alignment/
│   ├── GOLD_MASKS.json
│   ├── SCHEDULE.json
│   ├── calls/
│   ├── review/
│   ├── METRICS.json
│   └── REPORT.md
│
├── e2_selection/
│   ├── STATUS.json
│   ├── SELECTION_REFERENCE.json
│   ├── SCHEDULE.json
│   ├── calls/
│   ├── review/
│   ├── METRICS.json
│   └── REPORT.md
│
└── analysis/
    ├── PROVIDER_PREFLIGHT.json
    ├── EXECUTION_ACCOUNTING.json
    ├── INTEGRITY.json
    ├── SENSITIVITY.json
    └── FINAL_CONCLUSION.md
```

---

# 72. 成本报告

分别报告 E1/E2：

```text
planned
sent
returned
HTTP errors
schema errors

input tokens
completion tokens
reasoning tokens
total tokens

cache hit
cache miss
weighted cache hit rate

median latency
P95
max
peak concurrency
```

reasoning 已包含于 completion 时：

不得重复加入 total。

不验证价格：

不报告货币成本。

---

# 73. 最终必须回答的问题

1. Historical Gold LocalO 在 D1/D2 Skeleton 中有多高 Control Addressability？
2. D2 是否因为过粗产生大量 subnode-only target？
3. Oracle Skeleton + Claims 的 status accuracy 多高？
4. False-supported 是否受控？
5. Task requirement 是否再次被误当成已建立事实？
6. Support binding precision 多高？
7. Residual recall 是否足够高？
8. Exact state mask 是否达到可用水平？
9. D2 Runtime Skeleton 相对 Oracle Alignment loss 多大？
10. alignment failure 主要来自 coarse node、reference ambiguity 还是 evidence entailment？
11. 同 qid 随 Claims 增长，Mask 是否表现出合理 progress？
12. Oracle Mask 下 Active Requirement selection 多高？
13. Selection 是否仍频繁 downstream jump？
14. Model Mask 会损失多少 Selection validity？
15. Requirement-ID selection 是否显著减少历史自然语言 Obligation 的 relation corruption 风险？
16. 当前是否仍需要 Recent Path？
17. 当前是否需要 explicit `requires`？
18. 当前是否需要 Binding IR？
19. 是否已经有资格进入 4–8 step closed-loop rollout？
20. 当前真正剩余的瓶颈到底位于 Alignment、Selection，还是已经转移到 Acquisition？

---

# 74. 本实验最重要的成功标准

本轮真正想证明的不是：

> “又一个 prompt 达到高准确率。”

而是：

\[
\boxed{
\textbf{
A stable semantic plan can be reconciled with a changing evidence state
without regenerating the task semantics.
}
}
\]

然后：

\[
\boxed{
\textbf{
The next research objective can be selected by ID from the remaining plan,
rather than rewritten from the original question.
}
}
\]

如果这两个机制都成立，

Search-ESR 就第一次真正具备：

```text
Plan
→ Monitor
→ Select
→ Execute
→ Update
→ Monitor
```

的闭环控制骨架。

---

# 75. 最后纪律

不要因为我们觉得“只差最后一点”就跳过分层实验。

现在最有价值的就是继续保持：

\[
\boxed{
\textbf{one uncertain link at a time}
}
\]

E1 先回答：

> **Plan 和 Evidence 能不能正确对齐？**

只有答案为 YES，

E2 才回答：

> **知道剩什么以后，能不能选出下一步？**

只有两个答案都为 YES，

才进入真正 closed-loop rollout。