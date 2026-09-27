# Search-ESR：Minimal Semantic Package / Scoped Partial Evaluation

## 0. 本轮核心目标

当前问题不再定义为：

> “Claim 是否支持 Requirement？”

而定义为三个独立问题：

### 问题 A：Boundary Recovery

给定：

```text
Parent Requirement
+
Locator
```

能否恢复：

> 当前 locator 成为一个独立可验证条件时，真正必须继承的最小语义依赖。

即：

\[
T^*=\operatorname{SemanticClosure}(Locator,Parent)
\]

---

### 问题 B：Target-specific Verification

在 \(T^*\) 已经固定的条件下：

\[
Claims\models T^*?
\]

能否稳定判断。

---

### 问题 C：State Update / Partial Evaluation

如果 \(T^*\) 已经由 Claims 建立：

> Parent 接下来应该怎样变化？

不是：

```text
删除对应文字
```

而是：

\[
R'=\operatorname{PartialEvaluate}(R\mid C)
\]

Runtime 中不覆盖原 Parent。

Residual 只作为 ephemeral view。

---

# 1. 当前研究假设

## H1 — Boundary Hypothesis

当前主要失败来自：

> locator 的必要语义依赖边界没有稳定恢复。

表现为：

### Under-inheritance

漏掉 governing relation。

例如 Euler：

```text
locator:
born in the early 1700s...
```

必须继承：

```text
one of the people referenced by the target book
```

否则 biography 会产生 false support。

---

### Over-inheritance

带入不必要 sibling constraints。

例如 q637 clinical：

```text
locator:
six-month clinical history
```

需要保留：

```text
the individual in the first described case
```

但不需要同时证明：

```text
country/history condition
```

---

## H2 — Gold-Boundary Verification Hypothesis

如果人工提前提供正确的 \(T^*\)：

\[
GoldT^*+Claims
\rightarrow Support
\]

应明显比 Q0/Q1 稳定。

如果 Gold \(T^*\) 下 verifier 仍失败，

则问题不是 Boundary Recovery，而是 verifier 本身。

---

## H3 — Predicted-Boundary Cascade Hypothesis

如果：

```text
Parent + Locator
→ predicted T*
```

足够准确，

则：

```text
predicted T* + Claims
→ Support
```

与 Gold \(T^*\) 的性能差距应该很小。

---

## H4 — Partial Evaluation Hypothesis

即使一个局部 condition 被支持，

Parent update 也不能简单理解为：

```text
删除这段文字
```

例如：

```text
BookDate = 2016
ArticleDate = BookDate + 6
```

确认：

```text
BookDate = 2016
```

以后应得到类似：

```text
ArticleDate = 2022
```

而不是简单删除 book information。

---

# 2. Persistent State 不变

仍然保持：

```text
Q
Semantic Skeleton R
Verified Claims C
Hypothesis H
```

本轮不使用 H。

以下全部 ephemeral：

```text
Locator
Minimal Semantic Package
Support Certificate
Residual View
```

禁止新增 persistent：

```text
Support Graph
Binding Graph
Dependency DAG
Residual Tree
Fine Requirement Tree
```

---

# 3. 实验顺序

必须严格按以下 Gate 顺序运行：

```text
E0  Reference construction
 ↓
E1  Gold Package → Support
 ↓
E2  Parent+Locator → Package
 ↓
E3  Predicted Package → Support
 ↓
E4  Gold Support → Residual View
```

每一阶段必须独立 Gate。

前一阶段 FAIL：

> 后一阶段不得运行。

这样才能定位根因。

---

# 4. 为什么先跑 Gold Package Verification

不要先训练/优化 Boundary Recovery。

首先回答：

\[
\boxed{
\text{如果“当前到底验证什么”已经定义正确，
模型会不会验证？}
}
\]

否则：

```text
Package extractor
+
Verifier
```

同时失败时无法定位问题。

---

# 5. E0 — Bank

复用：

```text
experiment/contextual-subtraction-qualification
```

中的 natural historical material。

优先使用已有：

```text
48 Certificates
24 Parent-State cells
16 natural snapshots
9 qids
```

不得根据本轮模型输出重新选 case。

必须包含：

```text
Euler
Book → Article
q637 clinical
Ding marriage
DLC mechanics
DLC nation qualifier
nationality/champion membership
memorandum/letter date
teammate same-country
alma-mater/building
```

---

# 6. Parent Unitization

不能让 LLM 自由重写 Parent。

对每个 Parent 在调用前人工/机械冻结 source-anchored units。

例如：

```text
U1: one of the people referenced by the target book
U2: was born in the early 1700s
U3: in a central European country
U4: with the initials L. E.
```

要求：

1. 每个 unit 必须是 Parent 原文的 exact span；
2. 保持原顺序；
3. 不添加新实体；
4. 不自由 paraphrase；
5. unitization 在调用前 commit + hash freeze。

允许一个 semantic relation 跨多个 units。

这不是问题：

> Target Package 可以选择多个 units。

---

# 7. Gold Minimal Semantic Package

针对每个 unique：

```text
Parent + Locator
```

人工冻结：

```json
{
  "locator_unit_ids": ["U2"],

  "target_unit_ids": [
    "U1",
    "U2",
    "U3",
    "U4"
  ],

  "interpretive_context_unit_ids": []
}
```

定义：

## target_unit_ids

当前 condition 的 truth condition 必须包含的语义。

这些内容必须被 Claims 共同支持。

---

## interpretive_context_unit_ids

只用于：

```text
pronoun resolution
ellipsis
entity/reference disambiguation
```

但其内容不因为进入 Context 就自动成为验证目标。

---

## sibling units

既不属于 target，也不属于 interpretive context。

不进入 verifier。

---

# 8. Gold Package 示例

## Euler

```text
Locator:
born in the early 1700s...

Target:
- one of the people referenced by the target book
- born in the early 1700s
- central European...
- initials L.E.
```

关键：

```text
book → referenced person
```

属于 Target semantics，

不是 interpretive context。

---

## q637 clinical

```text
Target:
- individual in the first described case
- six-month clinical history
- walking / shoulder symptoms
```

不包含：

```text
country/history condition
```

因为它是 sibling constraint。

---

## Ding marriage

Target 包含：

```text
candidate Ding branch binding
+
married
+
without children as of 2019
```

不包含：

```text
foundational gift
building
```

---

## DLC technology

Target 包含：

```text
the DLC / base-game binding
+
technology changed
```

不包含：

```text
specific playable European nation
```

除非 locator 本身就是 nation condition。

---

# 9. E1 — Gold Package Support Verification

输入：

```text
Gold Target Package
+
Gold Interpretive Context
+
Frozen ClaimSet
```

不显示 Full Parent 的其它 sibling units。

---

# 10. E1 System Prompt

```text
You verify one fixed semantic TARGET against a supplied set of Verified Claims.

The TARGET has already been constructed from the source Parent Requirement.

TARGET SEMANTICS are the exact task semantics that must be established.

INTERPRETIVE CONTEXT may help resolve references or understand the TARGET, but
its presence does not create additional facts that must independently be
verified unless those facts also appear in TARGET SEMANTICS.

Use only the supplied Verified Claims.

Judge whether the Claims, taken together, establish all material TARGET
SEMANTICS.

Multiple Claims may jointly establish the TARGET.

Do not use outside knowledge.

Do not use hypotheses.

Do not require sibling task conditions that are not present in TARGET
SEMANTICS.

Do not accept a target merely because a related entity, operand, candidate or
attribute is present.

If any material TARGET semantic content remains unsupported, keep it OPEN.

Return JSON only:

{
  "verdict": "SUPPORTED",
  "supporting_claim_ids": ["C1", "C4"],
  "uncovered_target_unit_ids": []
}

or:

{
  "verdict": "OPEN",
  "supporting_claim_ids": ["C1"],
  "uncovered_target_unit_ids": ["U3"]
}
```

---

# 11. E1 第二个方向相反的检查

不要再问一次：

> “Are you sure?”

建立独立：

```text
Uncovered Material Auditor
```

输入：

```text
Gold Target Package
+
Claims that the first verifier claimed were sufficient
```

System Prompt：

```text
You are auditing a claim that the supplied Verified Claims fully establish a
fixed TARGET.

Your only task is to find material TARGET semantics that are NOT established by
the supplied Claims.

Do not judge sibling conditions outside the TARGET.

Do not add new requirements.

Return JSON only:

{
  "uncovered_target_unit_ids": []
}
```

或：

```json
{
  "uncovered_target_unit_ids": ["U3"]
}
```

Harness：

```text
if verifier.verdict != SUPPORTED:
    OPEN

elif uncovered_target_unit_ids != []:
    OPEN

else:
    QUALIFIED_SUPPORT
```

---

# 12. E1 Metrics

Primary：

```text
Support Precision
Support Recall
False Support
False OPEN
Uncovered-audit rescue
False-full-risk
Replicate stability
```

重点：

```text
Euler
Book-only
DLC nation qualifier
q637 clinical
Ding marriage
```

---

# 13. E1 Gate

Gold Package：

```text
Precision >= 97%
Recall >= 90%

Euler false support = 0
Book-only false support = 0

False-full-risk = 0

q637 clinical recall >= 90%
Ding marriage recall = 100%

Schema >= 95%
```

如果 E1 FAIL：

```text
STOP
```

说明：

> 即使 Target boundary 正确，
> verifier 仍不够可靠。

此时不要研究 package extractor。

---

# 14. E2 — Minimal Semantic Package Recovery

只有 E1 PASS 才运行。

E2 完全不显示 Claims。

原因：

> Boundary 的定义不能被当前 Evidence 反向塑造。

输入只有：

```text
Original Question
Parent Requirement
Frozen Parent Units
Locator
```

---

# 15. E2 Arm B0 — One-shot Selection

模型只能选择 ID。

Prompt：

```text
You recover the minimal semantic scope needed to verify one fixed Locator inside
a Parent Requirement.

The Parent has already been split into immutable source units.

Do not rewrite any unit.

Select:

1. TARGET units:
   source units whose truth-conditional content must hold for the Locator to be
   correctly treated as an independently verifiable condition inside the
   Parent.

2. INTERPRETIVE CONTEXT units:
   source units needed only to resolve reference, ellipsis or interpretation,
   but whose factual content does not itself become part of the verification
   target.

Do NOT include sibling constraints merely because they occur in the same
Parent.

Do NOT omit a governing relation, required referent binding, comparison,
temporal relation, attribution, quantifier or qualifier if removing it changes
what proposition the Locator expresses.

Return source IDs only.

{
  "target_unit_ids": ["U1", "U2"],
  "interpretive_context_unit_ids": ["U0"]
}
```

---

# 16. E2 Arm B1 — Select + Sufficiency Audit + Minimality Pruning

第一步使用 B0。

第二步做 missing-context audit。

---

# 17. Missing-context Auditor

输入：

```text
Parent units
Locator
current predicted target/context package
```

Prompt：

```text
The current semantic package is intended to preserve the meaning of one Locator
inside its Parent Requirement.

Check whether any omitted Parent unit is necessary because removing it changes:

- the referent being discussed;
- a required predicate-argument relation;
- a comparison or temporal relation;
- attribution or source binding;
- a quantifier or qualifier;
- another truth-conditional dependency of the Locator.

Do NOT add a sibling condition that is merely another unresolved requirement.

Return source IDs only:

{
  "missing_required_target_units": ["U4"]
}
```

如果无：

```json
{
  "missing_required_target_units": []
}
```

Harness 把这些 ID 加入 target set。

---

# 18. Minimality Pruning

对于当前 package 中每个非-locator unit \(U_j\)，

做 leave-one-out。

Prompt：

```text
Consider the current TARGET semantic package.

If unit Uj is removed while all other selected units remain, does the meaning
or truth condition of the Locator change?

Answer REMOVE only if Uj is unnecessary for the Target's referent, relation,
arguments, comparison, temporal structure, attribution, quantification or
qualification.

A sibling condition that is independently important elsewhere in the Parent is
still unnecessary here unless it changes this Target's meaning.

Return JSON only:

{
  "decision": "KEEP"
}
```

或：

```json
{
  "decision": "REMOVE"
}
```

---

# 19. E2 允许 Abstain

如果 frozen units 无法表达：

> minimal but semantically complete target

允许：

```json
{
  "status": "UNITIZATION_INSUFFICIENT"
}
```

不得自由生成新语义。

这是非常重要的诊断结果：

> 说明 source segmentation 本身需要更细。

不允许模型用 paraphrase 修补。

---

# 20. E2 Metrics

## Target Under-Inheritance

Gold target unit 被漏掉。

这是最高风险错误。

---

## Target Over-Inheritance

错误加入 sibling semantic unit。

---

## Interpretive-context confusion

把 context 当 target，

或 target 当 context。

---

## Exact Target Set

---

## Safe Package

定义：

```text
no target under-inheritance
AND
no forbidden sibling target expansion
```

---

## Stability

两 replicate target sets 是否一致。

---

# 21. E2 Gate

B1：

```text
Target under-inheritance <= 3%

Safe Package >= 90%

Exact target set >= 80%

Sibling over-inheritance <= 10%

UNITIZATION_INSUFFICIENT <= 10%

Schema >= 95%
```

优先级：

```text
UnderInheritance >> OverInheritance
```

因为：

```text
under-inheritance
→ false support
```

而：

```text
over-inheritance
→ false reject / keep open
```

后者更安全。

---

# 22. E3 — Predicted Package → Support

只有 E2 PASS。

使用 B1 predicted package。

输入与 E1 完全一样，

只把：

```text
Gold Package
```

替换为：

```text
Predicted Package
```

Verifier prompt 不变。

---

# 23. E3 Metrics

比较：

```text
Gold Package Verification
vs
Predicted Package Verification
```

重点：

```text
Precision loss
Recall loss
false-support increase
false-open increase
```

---

# 24. E3 Gate

```text
Precision >= 95%
Recall >= 85%

Gold-Predicted precision gap <= 5pp
Gold-Predicted recall gap <= 10pp

Euler false support = 0

False-full-risk = 0
```

如果：

```text
Gold verifier PASS
Predicted verifier FAIL
```

则根因被非常干净地定位为：

```text
Boundary Recovery
```

---

# 25. E4 — Residual View / Partial Evaluation

只有 E3 PASS。

这一步不要永久改写 Parent。

输入：

```text
Immutable Parent
Current Claims
Gold Qualified Support
```

先用 Gold Support。

---

# 26. E4 目标

不是：

```text
Rewrite the remaining Requirement.
```

而是产生：

```json
{
  "known_bindings": [],
  "still_missing": [],
  "derived_constraints": []
}
```

---

# 27. E4 Prompt

```text
You derive a temporary research Residual View from an immutable Parent
Requirement.

The Parent Requirement must never be rewritten or replaced.

You receive Verified Claims and Qualified Supports that have already passed a
separate support verifier.

Your task is to describe what remains unresolved while preserving every
governing relation or dependency that is still needed downstream.

Use supported information conservatively.

A supported fact may have different effects:

- an independent conjunct may be discharged;
- a known entity/value may become a binding;
- a comparison or temporal relation may become more specific;
- a governing relation may remain necessary even when one operand is known.

Do not delete unresolved semantics.

Do not infer unsupported facts.

Return JSON only:

{
  "known_bindings": [
    {
      "binding": "...",
      "claim_ids": ["C1"]
    }
  ],

  "derived_constraints": [
    "..."
  ],

  "still_missing": [
    "..."
  ]
}
```

---

# 28. Book→Article 必须专门测试

例如：

```text
BookDate = 2016
```

已经 supported。

期望不是：

```text
book condition disappears completely
```

而是 Residual View 体现：

```text
Known:
book = ...
publication year = 2016

Derived:
target article expected six years later ≈ 2022

Still missing:
later article
same-author relation
similar-topic relation
actual publication timing
```

不能把 article relation 错删。

---

# 29. E4 State-Pair Test

必须重点使用同一 Parent 的 progressive states。

例如：

```text
State0:
C = {}

State1:
C = {A}

State2:
C = {A,B}

State3:
C = {A,B,C}
```

检查：

> 随着可靠 Evidence 增加，Residual View 是否合理收缩/具体化。

重点历史 trajectory：

```text
q228 G05 → G06
q637 G17 → G18
Book-only → Book+Article
Nationality-only → +championship membership
```

---

# 30. E4 Metrics

最重要：

```text
False Shrink
Residual Recall
Governing-relation retention
Known-binding correctness
Derived-constraint correctness
State discrimination
State-pair monotonicity
False FULLY_SUPPORTED
```

---

# 31. E4 Gate

```text
False Shrink <= 3%

False FULLY_SUPPORTED = 0

Residual Recall >= 90%

Governing-relation retention >= 95%

State discrimination >= 85%

Schema >= 95%
```

宁可：

```text
NoShrink / KeepOpen
```

不要：

```text
FalseShrink
```

---

# 32. 结果解释矩阵

## Case A

```text
E1 FAIL
```

说明：

> 即使 Gold Target boundary 正确，
> verifier 仍然是主要瓶颈。

不要研究 boundary extractor。

---

## Case B

```text
E1 PASS
E2 FAIL
```

说明：

> verifier 能做，
> 当前真正问题是 Target Boundary Recovery。

---

## Case C

```text
E1 PASS
E2 PASS
E3 FAIL
```

说明：

> Boundary 单独指标看起来好，
> 但 cascade 中仍存在关键小误差。

检查：

```text
under-inheritance
target/context confusion
```

---

## Case D

```text
E1/E2/E3 PASS
E4 FAIL
```

说明：

> Verification 已经可靠，
> 真正问题转移到 State Update / Partial Evaluation。

---

## Case E

```text
E1/E2/E3/E4 PASS
```

支持：

\[
\boxed{
Source\text{-}Anchored\ Scope
\rightarrow
Target\ Verification
\rightarrow
Conservative\ Partial\ Evaluation
}
\]

成为 grounded research-control path。

---

# 33. 调用与冻结纪律

每个付费阶段：

1. 构建完整 requests；
2. commit；
3. hash freeze；
4. 输出准确 call count；
5. 等待新的明确授权；
6. 不复用前一实验授权。

参数：

```text
deepseek-flash
temperature=0
JSON mode
max_retries=0
concurrency<=8
```

所有失败保留分母。

禁止：

```text
retry
repair
best-of
majority vote
prompt hot-fix
failed-case replacement
```

---

# 34. Review Discipline

所有 Gold：

```text
Target Package
Support labels
Residual references
```

必须在对应阶段调用前冻结。

模型 reasoning 不参与 semantic review。

Ambiguous cases：

```text
AMBIGUOUS_REFERENCE
```

预先标记。

不得执行后改 Gold。

---

# 35. Harness 最终权威边界

继续保持：

```text
Q / R
    ↓ highest semantic authority

C
    ↓ evidence-backed epistemic state

Qualified Support
    ↓ ephemeral, recomputable

Residual View
    ↓ ephemeral, recomputable

Probe
    ↓ disposable

Query
    ↓ disposable
```

原则：

\[
\boxed{
\text{No LLM-derived ephemeral object may permanently rewrite }R.
}
\]

---

# 36. 本轮不要进入 Search

即使 E4 全部 PASS：

必须停止。

禁止自动：

```text
Probe
Query
Search
Find/Open
Writer
closed-loop rollout
```

下一实验才运行真正动态闭环。

---

# 37. 本轮最终必须回答的问题

1. Gold Target 已知时 verifier 是否可靠？
2. 当前主要失败到底是 verifier 还是 boundary recovery？
3. Parent+Locator 是否能恢复最小语义完整 Target？
4. Under-inheritance 是否被压住？
5. Over-inheritance 是否仍集中于 q637/paper/DLC？
6. Target 与 interpretive context 能否稳定区分？
7. Euler 是否不再 false support？
8. Book-only 是否不再被错误视为 solved relation operand？
9. q637 clinical 是否不再被 country/history 阻塞？
10. Ding marriage 是否保持局部成立而不关闭 gift？
11. Predicted package 相比 Gold package 损失多少？
12. 已验证 Support 是否能安全改变 Residual View？
13. Book→Article 是否发生 partial evaluation，而不是 textual deletion？
14. 是否出现 False Shrink？
15. 是否有必要引入 persistent graph？
16. 是否有必要引入 finer persistent Requirement nodes？
17. Q/R/C 是否仍足够作为 persistent semantic state？
18. 是否有资格进入 4–8 step dynamic closed loop？

---

# 38. 最终研究命题

本实验真正验证的是：

\[
\boxed{
\textbf{
Can the system recover the smallest source-anchored semantic unit
that is complete enough to verify, verify it against aligned evidence,
and use the result to update a non-destructive residual view?
}
}
\]

中文：

> **系统能否恢复一个最小但语义完整、source-anchored 的局部验证单元；用正确对齐的 Claims 验证它；并在不改写原始 Requirement 的情况下，让已确认事实安全地改变当前 Residual View。**