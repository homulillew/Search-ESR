# Search-ESR — Contextual Subtraction Qualification

## 0. 实验核心问题

当前已知结果：

- Binary Support S0：
  - Precision = 100%
  - Recall = 75%
- Typed + Scope S1：
  - Precision = 92.11%
  - Recall = 97.22%
  - 3 次 Binding Context → Substantive Support
  - 2 次 False-Full Assignment Hazard

最新 bad case 表明：

模型能够识别局部事实，但可能把局部事实从 Parent Requirement 的 governing relation 中切出来。

例如：

```text
Parent:
target book references a person
who was born in the early 1700s ...

Claim:
Euler was born in the early 1700s ...
```

局部属性成立：

```text
Euler → birth attributes
```

但缺少：

```text
target book → references → Euler
```

因此 Euler biography 不能参与 semantic subtraction。

本实验验证：

\[
\boxed{
\text{Can a verifier judge subtraction eligibility
in the full semantic context of the Parent Requirement?}
}
\]

---

# 1. 不测试的东西

本轮禁止：

- Search
- Query
- Probe
- Find/Open
- Writer
- Bootstrap
- full-loop rollout
- persistent graph
- finer persistent Requirement nodes
- RL/SFT
- majority vote
- best-of

本轮只测试：

```text
Candidate evidence
→ contextual subtraction qualification
→ qualified support
```

以及条件通过后的：

```text
qualified support
→ residual
```

---

# 2. 当前远程基线

执行前重新：

```bash
git fetch origin --prune

git rev-parse \
  origin/experiment/claim-requirement-support-alignment

git log --oneline --decorate -20 \
  origin/experiment/claim-requirement-support-alignment
```

任务编写时基线：

```text
experiment/claim-requirement-support-alignment
50f11b58a554223d8c2ac91a2d0ec8ad41dc1289
```

如果远程已经前移：

1. 阅读新增提交；
2. 检查是否已存在同目的实验；
3. 写入 PRE_EXECUTION_AUDIT；
4. 不静默沿用旧 SHA。

建议分支：

```bash
git switch -c \
  experiment/contextual-subtraction-qualification \
  origin/experiment/claim-requirement-support-alignment
```

---

# 3. 需要验证的新假设

## H1 — Contextual Entailment Hypothesis

ClaimSet 是否可参与 subtraction，不能由：

```text
Claim matches local text fragment
```

决定。

而必须由：

```text
ClaimSet
entails the candidate semantic condition
as interpreted inside the full Parent Requirement
```

决定。

---

## H2 — Governing-Context Hypothesis

即使一个局部事实本身正确，

如果它在 Parent 中要求的：

- referent binding；
- governing relation；
- comparison；
- temporal relation；
- attribution；
- quantifier；
- qualifier；
- source/document relation；

尚未被建立，

则必须：

```text
NOT_SUBTRACTABLE
```

注意：

这些只是可能的 semantic dependencies。

Runtime prompt 不得硬编码为特定任务类型列表。

---

## H3 — ClaimSet Hypothesis

真正的支持单位可能是：

```text
ClaimSet
```

而不是单个 Claim。

允许：

```text
C1
```

负责绑定 referent，

```text
C2
```

负责提供 predicate，

二者联合：

```text
{C1,C2}
```

建立一个完整条件。

---

## H4 — Cascade Hypothesis

可以组合：

```text
high-recall proposer
+
high-precision contextual verifier
```

同时获得：

```text
Support Recall >= 90%
Support Precision >= 95%
False-Full Hazard = 0
```

---

# 4. Persistent State 不变

仍保持：

```text
Q
Semantic Skeleton R
Verified Claims C
Hypothesis H
```

本轮不使用 H。

以下全部 ephemeral：

```text
candidate support
candidate ClaimSet
candidate Parent locator
qualification verdict
missing semantics
qualified support
residual
```

不得写回 persistent state。

---

# 5. 非常重要：Candidate Fragment 的定义

允许使用 Parent Requirement 中的 exact substring 作为：

```text
candidate_locator
```

但必须明确：

\[
\boxed{
candidate\_locator
\neq
standalone proposition
}
\]

它只是告诉 verifier：

> “我们正在评估 Parent 中这一部分。”

Verifier 必须按照：

```text
完整 Parent Requirement
```

解释 locator。

Locator 自动继承 Parent 中所有必要的：

```text
referents
roles
relations
comparisons
temporal structure
quantification
source/event attribution
qualifiers
```

除非当前 Verified ClaimSet 已经建立这些结构，
否则不得认为 locator 可 subtraction。

---

# 6. E0 — Qualification Reference Bank

零模型调用。

复用当前 Claim–Requirement Support Alignment 的：

```text
24 Parent-State cells
16 natural snapshots
9 qids
```

本轮是机制实验，

不要求 fresh generalization。

Fresh bank 后续单独验证。

---

# 7. E0 Candidate Certificates

对每个 Parent-State 构造若干候选 Certificate。

每个 Certificate：

```json
{
  "certificate_id": "A15_CAND1",

  "parent_requirement_id": "R4",

  "candidate_locator": "born in the early 1700s ...",

  "candidate_claim_ids": ["C1"],

  "gold_verdict": "NOT_SUBTRACTABLE",

  "gold_reason": "The target-book reference relation is not established."
}
```

---

# 8. Candidate Bank 必须包含四类

## Positive

Claims / ClaimSets 真正足以使某个 Parent 条件可 subtraction。

---

## Binding-missing hard negatives

局部属性正确，

但 governing relation / referent binding 尚未建立。

重点：

```text
Euler biography
book anchor without article relation
candidate identity without target relation
```

---

## Qualifier-incomplete hard negatives

核心事实有证据，

但 Parent 的限定范围没有完整建立。

重点：

```text
DLC mechanics
vs
specific playable European nation
```

---

## Background / irrelevant controls

避免 verifier 只在困难相关 case 上工作。

---

# 9. Positive / Negative 平衡

不要只采 false-support bad cases。

目标：

```text
40–60 candidate certificates
```

其中大致：

```text
40–60% positive
40–60% negative
```

优先保持 natural historical ClaimSets。

不要人工构造不存在于历史 State 的 Claims。

---

# 10. 必须纳入的核心证书

### Euler

```text
Claim:
Euler biography

Locator:
Euler-like attributes inside the target-book referenced-person condition

Gold:
NOT_SUBTRACTABLE
```

---

### Book → Article

```text
Claim:
target candidate wrote the book

Locator:
publishing the book

Full Parent:
later article + six-year relation

Gold:
NOT_SUBTRACTABLE
```

---

### q637 specific clinical case

```text
ClaimSet:
specific case record with clinical history

Gold:
SUBTRACTABLE
```

---

### q228 Ding marriage

```text
ClaimSet:
candidate binding + 2019 marriage/childlessness evidence

Gold:
SUBTRACTABLE
```

---

### DLC mechanics

建立 technology/religion/mechanics 的局部 positive certificate，

同时建立：

```text
playable-European-nation qualifier
```

不完整的 negative certificate。

---

### Memorandum / letter

Memo date 不得让 letter-date condition subtraction。

---

### teammate country

Jerry nationality / teammate names
不得让：

```text
other two teammates same-country-with-each-other
```

subtraction。

---

# 11. E1 — Contextual Qualification Mechanism Test

E1 不测试 candidate proposal。

使用 frozen E0 certificates。

这样可以把：

```text
candidate discovery
```

和：

```text
qualification
```

完全隔离。

---

# 12. E1 输入

```json
{
  "original_question": "...",

  "parent_requirement": {
    "requirement_id": "R4",
    "text": "..."
  },

  "candidate_locator": "...",

  "candidate_verified_claims": [
    {
      "claim_id": "C1",
      "statement": "..."
    }
  ]
}
```

---

# 13. E1 核心 System Prompt

You are deciding whether a candidate semantic condition may be safely removed
from the unresolved part of a research task.

You receive:

1. the Original Question;
2. one full Parent Requirement;
3. a Candidate Locator copied from inside that Parent Requirement;
4. a set of current Verified Claims.

The Candidate Locator is NOT a standalone proposition.

It only identifies which part of the Parent Requirement is under review.

Interpret it inside the FULL semantic context of the Parent Requirement.

Any referent, relation, dependency, comparison, temporal structure,
attribution, quantification, qualifier, or other semantic condition required
by the Parent remains required even if it is not repeated inside the short
Candidate Locator.

Your only control question is:

"Do the supplied Verified Claims, taken together, establish this candidate
condition strongly enough in its full Parent context that it can now be safely
removed from the unresolved task?"

Use only the supplied Verified Claims.

Do not use outside knowledge.

Do not use hypotheses.

Do not treat semantic relevance, entity overlap, candidate identity,
background information, or the truth of a local attribute as sufficient when
the Parent requires additional semantic relations or bindings that remain
unestablished.

Multiple Claims may jointly establish a condition.

A Claim does NOT need to contain the whole condition in one sentence if the
supplied Verified Claims jointly establish it.

Return:

SUBTRACTABLE
only when the complete candidate condition, interpreted in the full Parent
context, is entailed strongly enough to be treated as solved.

Otherwise return:

NOT_SUBTRACTABLE

If NOT_SUBTRACTABLE, briefly state only the most important missing or
unsupported semantic requirement. Do not propose a search query.

Return JSON only:

{
  "verdict": "SUBTRACTABLE",
  "missing_or_unsupported": null
}

or

{
  "verdict": "NOT_SUBTRACTABLE",
  "missing_or_unsupported": "..."
}

---

# 14. 为什么 Prompt 不硬编码三道门

不要在 runtime prompt 中写：

```text
person?
object?
document?
event?
```

也不要硬编码：

```text
Gate A
Gate B
Gate C
```

核心只有：

```text
full-context entailment
for safe subtraction
```

后续人工评审可把失败诊断成：

```text
local_fact_missing
semantic_binding_missing
qualifier_or_scope_missing
other
```

这些只是 error taxonomy，

不是模型必须逐项填的 runtime schema。

---

# 15. E1 两个诊断 Arms

## Q0 — Standalone-fragment verifier

故意只给：

```text
candidate locator
+
Claims
```

不提供 full Parent。

它代表我们过去容易犯的：

```text
local fragment verification
```

---

## Q1 — Full-context verifier

给：

```text
Original Q
Full Parent
candidate locator
Claims
```

使用上面的 Contextual Qualification Prompt。

---

# 16. E1 目的

如果：

```text
Q1 >> Q0
```

尤其 Euler / book-article false positive 被消除，

则支持：

> Governing context 是当前 support-safety 的关键缺失信息。

---

# 17. E1 Metrics

Primary：

```text
Subtraction Precision
Subtraction Recall
Hard-negative rejection
Binding-missing false acceptance
Qualifier-incomplete false acceptance
False-full-risk acceptance
Schema validity
Replicate agreement
```

最重要的是：

\[
\boxed{Subtraction\ Precision}
\]

和：

\[
\boxed{HardNegativeFalseAccept}
\]

---

# 18. E1 Gate

Q1：

```text
Subtraction Precision >= 97%

Subtraction Recall >= 90%

Binding-missing false acceptance <= 3%

Qualifier-incomplete false acceptance <= 5%

Euler false acceptance = 0

Book→article false acceptance = 0

False-full-risk acceptance = 0

Schema >= 95%
```

比较：

```text
Q1 Precision >= Q0 Precision
Q1 Recall >= Q0 Recall - 5pp
```

不要用严格：

```text
Q1 > Q0
```

避免 100%=100% 造成伪 FAIL。

---

# 19. E1 调用

假设最终：

```text
48 certificates
× 2 arms
× 2 replicates
= 192 calls
```

如果预算太高，

允许取消 Q0 replicate2：

```text
Q0 ×1
Q1 ×2
```

但必须在请求冻结前确定。

不得执行后删减。

---

# 20. E1 成功后的解释

如果 Q1 PASS：

支持：

\[
\boxed{
Support safety can be expressed as
contextual subtraction eligibility
}
\]

而不是：

```text
four-way Claim role classification
```

下一步进入 E2。

---

# 21. E2 — End-to-End Propose → Qualify

E1 PASS 后单独授权。

E2 才测试：

\[
R+C
\rightarrow CandidateProposal
\rightarrow ContextualQualification
\rightarrow QualifiedSupport
\]

---

# 22. E2 Proposer 的职责

Proposer 追求 Recall。

它没有 subtraction 权限。

它可以：

- 提出单 Claim；
- 提出 2–3 Claim 的 ClaimSet；
- 指定 Parent 中可能受到支持的 exact locator。

它不能输出：

```text
SOLVED
FULLY_SUPPORTED
SUBTRACTABLE
```

---

# 23. E2 Proposer Prompt

You propose candidate evidence groups that MAY establish some material part of
one Parent Requirement.

Your goal is high recall, not final verification.

You receive the full Parent Requirement and all current Verified Claims.

Identify up to 4 candidate ClaimSets that are worth strict downstream
verification.

Each candidate may contain 1 to 3 Claims.

For each candidate:

1. select the Claim IDs;
2. copy a short exact locator from the Parent Requirement indicating which
   part may be supported.

The locator is only a pointer into the Parent.
It is not a standalone proposition and does not mean the condition is proven.

Do not decide whether any candidate is actually subtractable.

Do not use outside knowledge or hypotheses.

Return JSON only:

{
  "candidates": [
    {
      "claim_ids": ["C1", "C4"],
      "candidate_locator": "..."
    }
  ]
}

If no Claim appears potentially useful:

{
  "candidates": []
}

---

# 24. E2 Qualification

每个 proposer candidate
使用 E1 Q1 contextual verifier。

最终 Qualified Support 只包含：

```text
verdict = SUBTRACTABLE
```

的 candidates。

---

# 25. Candidate overlap

如果多个 candidate ClaimSets
支持同一 Parent content，

允许去重。

不得：

```text
union fragments
```

自动推导 full support。

Full Parent 是否完成，
只能后续由 Residual/coverage stage 判断。

---

# 26. E2 Baselines

直接复用已经冻结的历史：

```text
S0 Binary
S1 Typed+Scope
```

不要重新付费重跑 S0/S1。

比较：

```text
S0
S1
Cascade
```

---

# 27. E2 Metrics

最终 qualified support：

```text
Support Precision
Support Recall
Exact support-set compatibility
False support
False-full hazard
Binding-missing false promotion
```

另外：

```text
Candidate proposal recall
Verifier rejection precision
ClaimSet size distribution
```

---

# 28. E2 Gate

Cascade：

```text
Support Precision >= 95%

Support Recall >= 90%

Binding-context false promotion <= 2%

False-full hazard = 0

Candidate proposal recall >= 95%

Schema >= 95%
```

且：

```text
Cascade Precision >= S1 Precision
Cascade Recall >= S0 Recall
```

---

# 29. E3 — Downstream Residual Causal Bridge

只有 E2 PASS 才运行。

这一步补上上一分支因为 safety gate 而没有执行的实验。

---

# 30. E3 Arms

## D1 — Model Qualified Support

输入：

```text
Parent
+
qualified ClaimSets
```

---

## D2 — Gold Qualified Support

输入：

```text
Parent
+
Gold subtractable evidence
```

作为 capability ceiling。

---

# 31. 不需要重新跑 Raw Claims baseline

可引用：

```text
state-conditioned-residualization R0
```

作为历史描述性比较。

本轮主要回答：

\[
\boxed{
ModelQualification
\rightarrow Residual
}
\]

与：

\[
\boxed{
GoldQualification
\rightarrow Residual
}
\]

差多少。

---

# 32. E3 Residual Prompt

You derive the remaining unresolved semantic content of one Parent Requirement.

You receive the full Parent Requirement and evidence groups that have already
passed a strict contextual subtraction verifier.

Only the supplied QUALIFIED evidence may be treated as solved.

Derive the semantic residual that still remains unresolved.

Do not add outside knowledge.

Do not repeat content already established by Qualified Evidence.

Do not remove content that is not established by Qualified Evidence.

Preserve the Parent Requirement's semantic relations, dependencies,
comparisons, temporal structure, attribution, quantification and qualifiers.

Do not output a Search query or Probe.

If no material unresolved content remains:

{
  "status": "FULLY_SUPPORTED",
  "residual": null
}

Otherwise:

{
  "status": "UNRESOLVED",
  "residual": "..."
}

---

# 33. E3 Metrics

```text
Strict residual validity
False subtraction
Supported-content leakage
False FULLY_SUPPORTED
True FULLY_SUPPORTED recall
State discrimination
Schema
```

---

# 34. E3 Gate

Gold Qualified:

```text
Strict >= 90%
False subtraction <= 3%
False FULLY_SUPPORTED = 0
```

Model Qualified:

```text
Strict >= 85%
Gold - Model <= 10pp
False subtraction <= 5%
False FULLY_SUPPORTED = 0
State discrimination >= 80%
```

---

# 35. 结果解释

## Case A

```text
E1 PASS
E2 PASS
E3 PASS
```

支持 grounded control chain：

\[
\boxed{
Claims
\rightarrow CandidateEvidence
\rightarrow ContextualQualification
\rightarrow QualifiedSupport
\rightarrow Residual
}
\]

此时：

> 已有 Evidence 时如何驱动下一动作

基本成立。

---

## Case B

```text
E1 PASS
E2 FAIL
```

Verifier 本身可行，

问题在 Candidate Proposal / ClaimSet construction。

---

## Case C

```text
E1 FAIL
```

full-context qualification
本身仍不能解决 relation-safety。

此时再考虑：

```text
explicit relation representation
```

但仍不要自动增加 persistent graph。

---

## Case D

```text
E1/E2 PASS
E3 FAIL
```

Support 已经安全，

真正问题转移到 Residual semantic subtraction。

---

# 36. 必须回答的 bad cases

最终报告逐个回答：

```text
Euler biography
book → article
DLC qualifier
generic SPS
patient nationality / report country
memo date / letter date
teammate same-country
Kwon/Ding
q637 clinical case
```

特别回答：

> full-context verifier 是否真正消除了“局部属性脱离 governing relation”的错误。

---

# 37. 不新增 persistent State

无论结果如何，

本实验不得新增：

```text
SupportGraph
BindingGraph
RelationDAG
EvidenceNeedGraph
persistent qualification certificate
```

Qualification certificate 全部 ephemeral。

---

# 38. 本轮最终命题

本实验不是验证：

> Claim 是否和 Requirement 相关。

而是验证：

\[
\boxed{
\textbf{
Can the agent safely decide whether current evidence
fully entails a candidate condition in the semantic context
in which that condition appears in the Parent Requirement?
}
}
\]

也就是：

\[
\boxed{
\textbf{“这部分现在真的敢不敢从 unresolved 中减掉？”}
}
\]