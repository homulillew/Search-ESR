# Search-ESR：Gold Obligation → Evidence Gap 核心机制验证

你正在继续 `homulillew/Search-ESR` 的 Research Control 研究。

本轮只验证一个核心假设：

> **当当前 Local Obligation 已经被人工正确冻结后，模型能否仅根据 Obligation 与当前 Verified Claims，稳定识别“已经支持什么、仍缺什么、什么类型的证据能够补齐缺口”？**

形式化：

\[
O_t + C_t \rightarrow G_t
\]

其中：

\[
G_t=
\{
supported\_by,\,
missing,\,
evidence\_needed
\}
\]

本轮特别要回答：

> **`Required(O_t) - Supported(C_t)` 这种 evidence-difference computation，是否比此前围绕自然语言 Need 的 premise/legality 判断更加稳定？**

不要扩大实验范围。

---

# 0. 当前远程锚点

开始前必须重新读取真实 remote：

```bash
git fetch origin --prune
git status
git branch --show-current

git rev-parse origin/main
git rev-parse origin/experiment/minimal-need-multiquery
git rev-parse origin/experiment/need-premise-audit

git log --oneline --decorate -15 \
  origin/experiment/need-premise-audit
```

任务编写时：

```text
main
8021aca19a1ee5201730e40b338012c65ecd51cf

experiment/minimal-need-multiquery
a12167e0b76dae2c5747bde828c5171e0c397bab

experiment/need-premise-audit
a37a1bd1afbd366dc35bc1e0c951aa5c2befbd96
```

最新 Need/Premise 实验提交：

```text
a37a1bd1afbd366dc35bc1e0c951aa5c2befbd96
Report V1 premise-checker failure and disclose invalid V0 control execution
```

这些 SHA 只是任务编写时锚点。

必须以实际 fetch 到的远程为准。

如果远程已有更新：

1. 先阅读；
2. 判断是否改变本轮实验前提；
3. 写入 `PRE_EXECUTION_AUDIT.md`；
4. 不得静默覆盖或忽略已有结果。

---

# 1. 新建独立实验分支

旧分支：

```text
experiment/minimal-need-multiquery
experiment/need-premise-audit
```

都已经完成并 Gate closed。

不得继续追加 prompt revision。

从最新：

```text
origin/experiment/need-premise-audit
```

创建：

```bash
git switch -c experiment/evidence-gap-gold-obligation \
  origin/experiment/need-premise-audit
```

新目录：

```text
experiments/evidence_gap_gold_obligation/
```

旧实验及历史输出全部只读。

---

# 2. 为什么要做这个实验

前两轮已经得到两个重要负结果。

第一轮：

```text
Q + Claims + H
→ natural-language Need
```

即使加入：

```text
premise closure
coherence
internal self-check
```

也不能稳定改善 Need。

唯一 revision 甚至出现：

```text
B0 concurrent: 10/18 strict-valid
revised B3:    2/18 strict-valid
```

第二轮：

```text
Candidate Need
→ explicit Premise Checker
```

结果：

```text
target identification:          43/44
target/premise distinction:     28/44
valid-control preservation:     10/22
invalid-candidate detection:    16/22
```

Premise Checker 最大的问题不是“完全看不懂 Need”，而是：

> 它经常把当前正在发现或验证的未知关系本身，当成必须事先成立的 prerequisite。

因此本轮不再研究：

```text
这个 Need 是否合法吗？
```

也不再研究：

```text
这句话有哪些 presuppositions？
```

而把核心计算改成：

```text
对于一个已经正确 scoped 的任务 obligation，
当前 Claims 已经支持了什么？
仍然缺什么证据？
```

---

# 3. 本轮研究假设

当前主假设：

\[
\boxed{
Evidence\ Difference
\text{ is easier and more reliable than }
Need\ Legality\ Judgment
}
\]

也就是：

```text
Gold Obligation
+
Current Verified Claims
↓
Evidence Gap
```

可能比：

```text
Natural-language Need
↓
Premise / Scope / Legality analysis
```

更加稳定。

这是本轮唯一主要机制问题。

---

# 4. 持久 State 不改变

Persistent semantic state 继续只有：

```text
Original Question Q
Verified Claims C
Working Hypothesis H
```

不增加：

```text
Requirement Map
Persistent Gap
OpenNeeds
Progress
Frontier
Dependency Graph
done_when state
binding state
coverage table
```

本轮：

```text
Gold Obligation
Evidence Gap
```

全部只是实验中的 ephemeral computation。

---

# 5. 本轮明确不做什么

本轮禁止：

```text
Q → model-generated obligation
Need generation
Need repair
Premise Checker revision
Binding Parser
Dependency Graph
Search
Find
Open
Writer
Multi-Query
Closure
full research loop
```

即使实验成功，也停止。

下一阶段另开独立实验。

---

# 6. 最核心的因果隔离

本轮必须把：

```text
Obligation quality
```

从：

```text
Gap derivation quality
```

中完全隔离。

因此所有模型输入中的：

```text
Local Obligation
```

都必须由实验者提前人工冻结。

模型不能：

- 修改 obligation；
- 重写 obligation；
- 选择另一个 obligation；
- 输出新的 obligation；
- 重新解释完整 Original Question。

本轮真正测试的是：

\[
\boxed{
GapQuality \mid CorrectObligation
}
\]

不是：

\[
Q\rightarrow Obligation\rightarrow Gap
\]

---

# 7. 什么是 Local Obligation

Local Obligation 表示：

> 当前只考虑 Original Question 中的一项局部 research obligation。

它不是 Search Query。

它也不是一定要 atomic。

它必须：

- 来自 Original Question；
- 对最终回答有真实意义；
- scope 正确；
- 可以被当前或未来 evidence 判断；
- 不跨越尚未建立的对象/事件直接追问 downstream attribute。

---

# 8. Gold Obligation 示例

## 示例 A：Marwaha

不要：

```text
Find the title of Marwaha's later article.
```

Gold Obligation 应类似：

```text
Establish and identify the question-described later journal article
associated with the candidate author, including whether such an article exists.
```

因为当前尚未建立文章事件。

---

## 示例 B：Kwon

Gold Obligation：

```text
Establish whether Kwon Hyuk-bin and his spouse made
the question-described joint foundational donation.
```

这里：

```text
joint donation
```

就是待验证 relation。

不能要求 donation 已经成立。

---

## 示例 C：DLC

Gold Obligation：

```text
Identify the EU4 downloadable content pack that satisfies
the question-described release/mechanics profile.
```

DLC identity 本身就是 output。

不能因为 DLC 未识别就判 obligation 有问题。

---

## 示例 D：Letter

如果 Claims 只有：

```text
a covering memorandum is dated March 5
```

Gold Obligation 不能把它写成：

```text
determine the region in the March 5 letter
```

除非 letter date 本身已被 Claims 建立。

应写成能够保持正确 object scope 的 obligation。

---

# 9. Binding 的处理原则

本轮：

**不要实现完整 Binding schema。**

不要输出：

```text
variables
operators
fixed_anchors
local_variables
target_predicates
logical_form
```

但在 Gold Obligation 构造和评分规范中保留两条 invariant：

### Invariant 1

> An entity, event, relation, or attribute may itself be the information being discovered or verified. Do not require the information currently being investigated to already be supported.

### Invariant 2

> Do not jump to a downstream attribute of an entity/event/relation that has not yet been identified or established by the current Claims. In that case, the missing identifying or existence evidence is the current gap.

Binding 只作为：

```text
error-analysis theory
```

不作为 runtime representation。

---

# 10. E0：构造 development bank

优先使用已经暴露的历史状态。

这些状态已经不能算 fresh，因此非常适合 mechanism development。

来源可以包括：

```text
belief_need_budget_locality_repair
minimal_need_multiquery
need_premise_audit
```

尤其复用：

- Marwaha later article；
- Jerry Mao / championship 类；
- memorandum vs letter；
- unidentified book；
- SPS/report；
- Kwon donation；
- Sophie interview；
- DLC discovery；
- accident-site；
- FOP cases；
- 已经完全 supported 的合法 controls。

---

# 11. Bank 的目标组成

目标：

```text
24–30 natural historical state instances
```

如果真实素材不足，不人工制造案例。

至少包含五类。

## Type 1 — Identity / discovery gap

例如：

```text
which DLC
which book
which article
which person
```

未知对象本身就是 output。

---

## Type 2 — Relation verification gap

例如：

```text
whether Kwon and spouse donated
whether candidate won championship
whether interview occurred
```

relation 本身就是待验证目标。

---

## Type 3 — Downstream-attribute temptation

例如：

```text
article title before article existence
year before win event
region before source relation
property of unbound document
```

正确 gap 应退回 identification/existence evidence。

---

## Type 4 — Scope/binding support cases

例如：

```text
memo date ≠ letter date
handoff officer ≠ final courier
generic case ≠ specific report
```

用于测试 Claims support matching。

---

## Type 5 — Fully or sufficiently supported controls

加入一部分：

```text
Gold Obligation 已被现有 Claims 完整满足
```

此时正确结果应：

```text
missing = null
evidence_needed = null
```

防止模型无论如何都制造 gap。

建议：

```text
20–30%
```

为 satisfied controls。

---

# 12. 不要人工补 Claims

每个 case 使用历史自然 QCH snapshot 中原有：

```text
Verified Claims
```

不得为了让实验容易评分而：

- 新写 Claim；
- 删除 Claim；
- 合并 Claim；
- 改写 Claim；
- 清洗 H；
- 人为制造 partial-support 状态。

---

# 13. E0 Gold Reference

在任何模型调用前，为每个 case 人工冻结：

```json
{
  "case_id": "...",

  "gold_obligation": "...",

  "reference_support": [
    {
      "claim_id": "C1",
      "supports": "obligation component supported by this claim"
    }
  ],

  "reference_status": "satisfied | partial | unsupported",

  "reference_missing": "... or null",

  "reference_evidence_needed": "... or null",

  "binding_risk": [
    "none | downstream_jump | wrong_object_scope | unresolved_referent | target_as_prerequisite"
  ],

  "ambiguity": "low | medium | high",

  "reason": "..."
}
```

---

# 14. Gold Reference 的边界

Reference reviewer 可以看：

```text
Original Question
current Claims
current H
historical Candidate Need only when necessary to locate the state
```

但 Gold Obligation / Gap 必须依据：

```text
Q + current Claims
```

不能使用：

```text
gold final answer
future trajectory
later Search/Open
future Claims
external factual lookup
```

H 可以帮助理解历史背景，但不能进入 reference support。

---

# 15. Reference freeze

生成：

```text
e0_reference/
  CASES.json
  GOLD_OBLIGATIONS.json
  GOLD_GAPS.json
  SELECTION.json
  REPORT.md
```

然后 commit。

所有 real model calls 必须发生在该 commit 之后。

---

# 16. E1：Gold Obligation → Evidence Gap

模型输入只包括：

```text
Gold Local Obligation
Verified Claims with IDs
```

**不给 Original Question。**

因为 Gold Obligation 已经承担 Required reference。

这一步必须严格回答：

\[
Required(O)-Supported(C)
\]

而不是重新理解 Q。

---

# 17. 为什么 primary arm 不给 Q

如果同时给：

```text
Q + Obligation + Claims
```

模型可能重新从 Q 选择 scope，重新引入：

```text
Obligation derivation error
```

这会破坏本轮因果隔离。

因此 primary computation：

\[
\boxed{
O+C\rightarrow Gap
}
\]

---

# 18. 为什么 primary arm 不给 H

同理，本轮 primary hypothesis 是：

> Gap 应该由 required evidence 与 supported evidence 决定。

H 不是 evidence。

因此 primary：

```text
G0:
Gold Obligation + Claims
```

完全不输入 H。

---

# 19. 同期 H ablation

为了测试 hypothesis contamination，可以增加同期第二臂：

```text
G1:
Gold Obligation + Claims + Working Hypothesis
```

其他内容完全一致。

G1 只用于回答：

> H 出现在 Gap derivation 阶段，会改善 gap，还是污染 gap？

重要：

**G0 是本轮 primary mechanism arm。**

G1 不改变 G0 的绝对 Gate。

---

# 20. G0 Prompt

使用类似下面的固定 prompt。

不要加入 case-specific 示例。

```text
You compute the current evidence gap for one already-selected research obligation.

The Local Obligation has already been chosen correctly.
Do NOT replace it, broaden it, narrow it, or choose another research objective.

You receive:
1. Local Obligation
2. Verified Claims with exact Claim IDs

Your task is only to compare the evidence required by the Local Obligation
with the evidence currently supported by the Verified Claims.

Return:

- which Claims actually support relevant parts of the obligation;
- what meaningful information or evidence is still missing;
- what kind of evidence would be sufficient to reduce or resolve that missing part.

Important rules:

1. The information being discovered or verified by the Local Obligation
   is allowed to be unknown.
   Do not require the current target itself to already be supported.

2. Do not jump to a downstream attribute of an entity, event, relation,
   document, or source that has not yet been identified or established
   by the current Claims.
   If an underlying entity/event/relation must first be established,
   state that identifying or existence evidence as the missing information.

3. A Verified Claim supports only the entity, event, relation, role,
   date, quantity, and scope that it actually states.
   Do not transfer a date or property from one object to another.
   Do not strengthen a Claim.

4. Do not use outside knowledge.

5. Do not invent a new requirement that is not part of the supplied
   Local Obligation.

6. Do not output a search query, plan, candidate answer, hypothesis,
   confidence score, or next research question.

7. "evidence_needed" describes a sufficient evidence signature,
   not a specific website, query string, or source that must be used.

If the Local Obligation is already sufficiently supported by the
Verified Claims, return null for both "missing" and "evidence_needed".

Return only JSON:

{
  "supported_by": ["C1", "C3"],
  "missing": "specific unresolved evidence deficit" | null,
  "evidence_needed": "type of evidence sufficient to reduce or resolve it" | null
}
```

---

# 21. G1 Prompt

G1 与 G0 完全相同，只增加：

```text
You also receive a Working Hypothesis.

The Working Hypothesis is a provisional candidate or search hint.
It is NOT evidence.

It may not:
- appear in supported_by;
- create a new research obligation;
- turn a candidate-specific property into established information;
- change the true evidence deficit.

Use it only if it helps understand possible wording.
The evidence gap itself must still be determined only from
the Local Obligation and Verified Claims.
```

但请注意：

这里的实验目标不是让 G1 “用好 H”。

而是检查：

> 即使明确禁止，H 的出现是否仍污染 missing。

---

# 22. 输出 schema 必须保持最小

不要输出：

```text
obligation
known
reason
premises
target
subject
depends_on
mode
status
priority
done_when
confidence
```

因为 obligation 已经在输入里。

本轮只允许：

```json
{
  "supported_by": [],
  "missing": null,
  "evidence_needed": null
}
```

三个字段。

---

# 23. Harness mechanical validation

Harness 只机械检查：

### JSON/schema

字段完整、类型正确。

### Claim ID

`supported_by` 只能包含当前输入实际存在的：

```text
C1...Cn
```

不能包含：

```text
Q
H
memory
URL
source name
不存在的 C#
```

### Null consistency

如果：

```text
missing == null
```

则：

```text
evidence_needed
```

也必须：

```text
null
```

反之如果 missing 非 null：

```text
evidence_needed
```

必须非 null。

Harness 不机械判断语义 entailment。

---

# 24. Provider contract preflight

上一轮 V0 因 JSON mode prompt 不含字面：

```text
json
```

导致 44/44 HTTP400。

这次必须在 freeze 前离线检查：

- JSON-mode provider prompt requirement；
- output schema；
- model endpoint；
- authentication handling；
- max-token parameter；
- request serialization；
- duplicate output path；
- all scheduled prompts include literal `JSON/json` where required。

必须添加 automated preflight test。

任何一个请求在真实发送前若不通过：

```text
STOP_BEFORE_PAID_CALL
```

---

# 25. 被测模型配置

为了与最近实验连续：

```text
model = deepseek-flash
temperature = 0
max_retries = 0
JSON mode
omit max_tokens
```

不要因为执行者是 Codex GPT-6 而更换 policy model。

Codex 是实验编排者，不是被测模型。

如果远程历史配置或 provider 已改变：

先记录并报告。

---

# 26. Replicate

最近两轮已证明：

```text
temperature = 0
```

不等于 deterministic。

所以每个：

```text
case × arm
```

执行：

```text
2 independent responses
```

不得：

- best-of；
- retry；
- 选择较好 replicate；
- 用 replicate 2 替换 replicate 1。

两条都进入分母。

---

# 27. 调用规模

如果最终 bank 为：

```text
24 cases
```

则：

```text
24 × 2 arms × 2 replicates
= 96 calls
```

如果：

```text
30 cases
```

则：

```text
120 calls
```

真实调用前必须给出：

```text
exact planned calls
estimated prompt tokens
historical completion distribution
65,535-token tail-risk
expected concurrency
```

本提示词本身不等价于授权无限付费调用。

如果当前 Codex 任务中没有用户明确授权：

完成所有：

```text
design
code
tests
reference freeze
schedule
dry-run
cost exposure report
```

后停在：

```text
PREPARED_FOR_REAL_RUN
```

---

# 28. E1 Primary semantic metrics

## 1. Strict Gap Validity

一条 response 只有同时满足：

```text
support binding correct
missing correct
evidence_needed correct
no invented requirement
no downstream jump
no target-as-prerequisite error
```

才 strict-valid。

这是 primary metric。

---

## 2. Missing correctness

判断：

> `missing` 是否准确表达当前 obligation 相对 Claims 的未支持部分。

特别标记：

```text
correct
too_downstream
too_upstream
too_broad
too_atomic
already_supported
invented
wrong_object_scope
```

---

## 3. Support binding

两层报告。

### Micro

每个 Claim ref 是否真的支持它被使用的 scope。

### Response-level

整条 `supported_by` 是否：

- 没有错误 ref；
- 没漏掉 materially necessary support；
- 没 scope strengthening。

Primary 使用 response-level。

---

## 4. Evidence-needed quality

检查它是否：

- 对应真正 missing；
- 是现实可获取的证据类型；
- 足以缩小/解决 gap；
- 没写成 query；
- 没硬编码某网站；
- 没要求比 obligation 更大的证明。

---

## 5. Satisfied-control specificity

对于 reference：

```text
status = satisfied
```

模型是否正确：

```text
missing = null
evidence_needed = null
```

这可以测试它是否有“永远制造 gap”的偏置。

---

# 29. 专门的错误分类

必须记录：

### Downstream jump

正确应该先 establish/identify X，却直接 missing X 的属性。

---

### Target-as-prerequisite

当前 obligation 正是在验证关系 R，却认为 R 应该已经成立。

---

### False requirement

生成 obligation 中不存在的新要求。

---

### Scope transfer

把：

```text
memo date
```

当成：

```text
letter date
```

之类错误支持。

---

### Wrong referent

Claim 与 obligation 讨论的不是同一个实体/事件/来源。

---

### Over-strengthening

Claim 只支持：

```text
possibly / around / relation A
```

却把它当：

```text
exact / stronger / relation B
```

---

### Stale gap

missing 实际已经被 Claims 支持。

---

### H contamination

仅 G1：

Gap 出现了只有 H 中存在、但 Gold Obligation / Claims 中没有的 candidate-specific 内容。

---

# 30. Replicate stability

报告：

```text
strict-valid both replicates
strict-valid exactly one replicate
both invalid
```

以及 semantic equivalence：

```text
same gap
compatible gap
different gap
```

不能只看 aggregate accuracy。

一个 autonomous Agent 更关心：

\[
\boxed{stability}
\]

---

# 31. G0 的 frozen Gate

建议 primary G0 同时满足：

```text
Strict Gap Validity >= 80%

Missing correctness >= 85%

Response-level support binding >= 85%

Satisfied-control specificity >= 85%

Downstream-jump rate <= 10%

Target-as-prerequisite error <= 10%

Schema-valid output >= 95%

Exact/semantic replicate agreement >= 80%
```

这些是工程 Gate，不声明统计显著性。

---

# 32. G1 的作用

G1 不作为 Evidence Gap mechanism 是否可行的主要 Gate。

它回答：

> H 是否应该参与 Gap formation？

重点报告：

```text
G0 strict
G1 strict

G0 downstream-jump
G1 downstream-jump

G0 candidate-specific unsupported content
G1 candidate-specific unsupported content

paired G0 better
paired G1 better
tie
```

---

# 33. H contamination 判定

如果 G1 比 G0 更频繁产生：

- H 中候选名字进入 missing；
- H 中未验证时间进入 gap；
- H 中候选 relation 被当成 obligation；
- generic identity gap 被改成 candidate-specific attribute gap；

记为：

```text
hypothesis contamination
```

---

# 34. H ablation 的研究解释

如果：

\[
G0 > G1
\]

并且主要差异来自 H contamination：

可以支持：

\[
\boxed{
Hypotheses\ should\ guide\ acquisition,
not\ gap\ formation.
}
\]

只能支持这一层。

不能因此说 H 应从整个系统删除。

未来仍允许：

\[
Gap + H + Workspace \rightarrow Action
\]

---

# 35. 如果 G1 与 G0 一样

如果几乎无差异：

不能说：

> H 必须进入 Gap。

只能说：

> 在当前 development bank 上，H 的 presence 没有显著改变 Gap quality。

未来 Acquisition 实验仍单独研究 H 的价值。

---

# 36. 与 Premise Checker 的历史比较

可以做**描述性比较**，但不能假装 randomized direct A/B。

可以报告：

```text
historical premise checker:
target/premise distinction 28/44
support-binding whole-response 30/44
...
```

然后描述当前 Evidence Gap 指标。

但必须说明：

- output task 不同；
- bank 可能不同；
- prompt/runtime 不完全相同；
- 不能直接把百分点差异称为 causal improvement。

真正主要结论依赖本轮绝对 Gate。

---

# 37. 如果 G0 FAIL

立即停止。

不要：

```text
加 requires
加 binding
改 prompt
重新选 bank
跑 Q → Obligation
跑 Search
```

先分析失败究竟主要来自：

```text
support comparison
downstream scope
evidence-needed formulation
model variance
```

本任务不允许 adaptive revision。

下一实验另立。

---

# 38. 如果 G0 PASS

本任务仍然停止真实调用。

只输出下一实验建议：

```text
Q → Local Obligation
```

并明确：

> Gold Obligation → Gap 已通过 development mechanism Gate，因此现在才有资格研究 obligation derivation。

不要自动继续。

---

# 39. 不要在这轮测试 Q → Obligation

这一点必须严格遵守。

如果现在又让模型：

```text
Q → obligation → gap
```

那么 Gap 出错后无法判断：

- obligation scope 错；
- 还是 evidence comparison 错。

所以本轮到：

\[
O+C\rightarrow Gap
\]

为止。

---

# 40. Future-only：下一阶段的方向

只有当前实验 PASS 后，后续独立实验才测试：

\[
Q\rightarrow LocalObligation
\]

到那个时候才研究：

- 是否会选 downstream obligation；
- obligation 是否太宽；
- 是否过度 atomic；
- 是否 invent requirement；
- 是否应该输入 limited Claims。

本轮禁止提前执行。

---

# 41. ACT / STOP 也不在本轮

虽然长期理论可能是：

```text
ACT:
local evidence gap

STOP:
global coverage audit
```

但本轮不测试：

```text
Global Closure
STOP
reactivation
coverage
```

这些都依赖 Evidence Gap 核心机制先成立。

---

# 42. 代码目录建议

```text
experiments/evidence_gap_gold_obligation/
├── README.md
├── TASK.md
├── PRE_EXECUTION_AUDIT.md
├── HYPOTHESES.md
├── PROTOCOL.md
├── CONFIG.json
├── FREEZE.json
│
├── prompts/
│   ├── g0_gap_no_h.txt
│   └── g1_gap_with_h.txt
│
├── e0_reference/
│   ├── CASES.json
│   ├── GOLD_OBLIGATIONS.json
│   ├── GOLD_GAPS.json
│   ├── SELECTION.json
│   └── REPORT.md
│
├── e1_gap/
│   ├── SCHEDULE.json
│   ├── calls/
│   ├── review/
│   ├── ACCOUNTING.json
│   ├── METRICS.json
│   └── REPORT.md
│
├── analysis/
│   ├── PROVIDER_PREFLIGHT.json
│   ├── DRY_RUN.json
│   ├── EXECUTION_ACCOUNTING.json
│   ├── INTEGRITY.json
│   ├── H_ABLATION.json
│   └── FINAL_CONCLUSION.md
│
├── prepare.py
├── run.py
├── score.py
└── test_contracts.py
```

---

# 43. Freeze 纪律

真实模型调用前必须 freeze：

```text
base commit
case bank
all Gold Obligations
all Gold Gap references
prompts
schemas
model profile
replicate count
schedule
metrics
Gate
failure policy
provider preflight
```

然后 commit。

调用后不得修改。

---

# 44. Semantic review

Response review 尽量做 arm-masked。

Reviewer 至少不能在第一次 semantic judgment 时看到：

```text
G0 / G1
replicate number
aggregate metrics
```

可以看到：

```text
Gold Obligation
Claims
model output
Gold reference
```

如果因为 schema 暴露 arm 无法完全 blind：

明确披露。

所有 first-pass labels 必须在 aggregate 前冻结并 commit。

---

# 45. 失败必须保留

保留全部：

```text
HTTP error
provider rejection
schema error
length failure
timeout
empty output
invalid Claim ref
reasoning exhaustion
auth error
```

不得：

- 删除失败；
- silent retry；
- 修 JSON 后当成功；
- 重发语义失败；
- 替换样本。

---

# 46. 成本统计

报告：

```text
planned requests
sent requests
responses
failures
input tokens
completion tokens
reasoning tokens
cache hit/miss
weighted cache hit rate
latency
peak concurrency
unknown usage
```

注意：

```text
reasoning tokens
```

已经是 completion 的组成部分时，不得重复计入 total。

没有实时验证价格就不要虚构货币成本。

---

# 47. 最终报告必须回答

1. 在 Gold Obligation 已正确固定时，模型能否稳定做 `Required - Supported`？
2. 最常见 Evidence Gap 错误是什么？
3. 模型是否仍会把正在研究的 target 当 prerequisite？
4. 是否仍会出现 downstream jump？
5. Claim support scope 是否仍然是主要瓶颈？
6. `supported_by` 的 response-level reliability 多高？
7. `missing` 是否比此前 Premise Checker 的 legality judgment 更稳定？
8. `evidence_needed` 是否能保持 evidence-level，而不退化成 query/source prescription？
9. 模型是否会在已经 satisfied 的 obligation 上制造假 gap？
10. 两次 replicate 的稳定性怎样？
11. H 是否污染 Gap formation？
12. 如果没有 H，Gap 是否明显更稳定？
13. 是否有证据需要增加 `requires / depends_on`？
14. 是否有证据需要完整 Binding representation？
15. 是否已经有资格进入 `Q → Local Obligation` 实验？

---

# 48. 对结果的允许解释

## 如果 G0 PASS

可以说：

> 在人工正确冻结 Local Obligation 后，Evidence Difference 是一个有希望的控制计算；下一步可以单独研究从 Q 动态派生 Local Obligation。

不能说：

> 完整 Evidence-Gap architecture 已经成功。

---

## 如果 G0 FAIL

可以说：

> 即使 obligation 已正确给定，模型仍不能稳定判断当前 Claims 与 required evidence 的差异，因此 Evidence Gap 作为控制抽象尚未获得支持。

然后根据错误进一步定位。

不能直接回到 Requirement Map 或 Binding Graph。

---

## 如果 G0 PASS、G1 FAIL/明显更差

可以说：

> 当前证据支持将 Working Hypothesis 从 Gap formation 中后移；H 更适合作为 acquisition hint，而不是决定真实缺口。

---

## 如果 G0/G1 都 PASS

只能说：

> 在本 development bank 上没有观察到 H 明显污染 Gap。

不能据此证明 H 应参与 Gap formation。

---

# 49. Complexity escalation rule

当前复杂度等级：

```text
Level 0:
Obligation
+
SupportedBy
+
Missing
+
EvidenceNeeded
```

只有本实验 FAIL 且错误明确属于：

```text
unresolved external dependency
```

时，下一个独立实验才可以测试：

```text
Level 1:
+ requires
```

不要直接跳到：

```text
variables
logical predicates
binding graph
typed DAG
```

所有新增结构必须由真实 failure 证明需要。

---

# 50. 本轮真正想证明的东西

最终目标不是证明：

> “一个新 JSON schema 很好。”

而是验证下面这个计算是否成立：

\[
\boxed{
\text{Given a correctly scoped research obligation,}
\quad
\text{can the model reliably identify the evidence deficit}
\quad
\text{relative to current verified claims?}
}
\]

如果答案是 YES：

下一步才有资格测试：

\[
Q\rightarrow LocalObligation
\]

最终可能形成：

\[
Q
\rightarrow
LocalObligation
\rightarrow
EvidenceGap
\rightarrow
Action
\]

如果答案是 NO：

就说明问题不仅在 Natural-language Need 或 Premise Checker。

而是：

\[
Required-Supported
\]

这个 evidence comparison 本身仍然需要进一步研究。

---

# 51. 当前长期架构假设仅作为背景，不作为本轮结论

仍然暂定：

```text
Persistent epistemic state:
Q + Claims + H

Ephemeral control:
Local Obligation
Local Evidence Gap

Mechanical state:
Workspace / Trace / D# / W# / attempts

Acquisition:
Gap + H + Workspace → Search / Find / Open
```

但本轮只验证其中这一条箭头：

\[
\boxed{
GoldObligation + Claims
\rightarrow
EvidenceGap
}
\]

没有通过之前，不要实现后面的架构。