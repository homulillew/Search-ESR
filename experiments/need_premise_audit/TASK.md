# Search-ESR：Ephemeral Premise Audit / Need Type Checker 实验

你正在继续 `homulillew/Search-ESR` 的 Research Control 研究。

本轮实验只回答一个问题：

> **对于已经生成的 Candidate Need，把“这个问题偷偷假定了什么”显式抽出来并逐项绑定到 Original Question / Verified Claims，是否能够可靠发现并修复 unsupported premise / unresolved referent 问题？**

本轮不是：

- 新 Need Prompt sweep；
- Multi-Query 实验；
- Query 生成实验；
- Retrieval 实验；
- Closure 实验；
- 完整 autonomous loop；
- persistent Requirement Map；
- Dependency Graph；
- Planner / Frontier 实验。

不要扩大范围。

---

# 0. 当前远程研究锚点

开始前必须：

```bash
git fetch origin --prune
git status
git branch --show-current
git rev-parse origin/main
git rev-parse origin/experiment/minimal-need-multiquery
git log --oneline --decorate -15 origin/experiment/minimal-need-multiquery
```

任务编写时最新 Need 分支为：

```text
experiment/minimal-need-multiquery
a12167e0b76dae2c5747bde828c5171e0c397bab
```

commit：

```text
Report failed Need revision, retain all failures and close downstream gates
```

必须以实际 fetch 到的最新 remote 为准。

如果该分支已有更新：

1. 先阅读更新；
2. 判断是否改变本实验前提；
3. 写入 `PRE_EXECUTION_AUDIT.md`；
4. 不得静默忽略。

---

# 1. 新建独立分支

上一轮：

```text
experiment/minimal-need-multiquery
```

已经明确：

```text
STOP_E1_NO_MORE_REVISIONS
```

所以：

**绝对不要继续在该实验目录里追加第二次 prompt revision。**

从它的最新 HEAD 新建：

```bash
git switch -c experiment/need-premise-audit \
  origin/experiment/minimal-need-multiquery
```

建议实验目录：

```text
experiments/need_premise_audit/
```

旧实验全部只读。

---

# 2. 本轮研究为什么存在

最新 `minimal_need_multiquery` 真实执行已经证明：

## 原始局部 Need baseline

同一批 18 个开发状态：

```text
B0 v1:
14/18 strict-valid
```

另一次同期重采样：

```text
B0 r1:
10/18 strict-valid
```

说明：

1. 原 B0 的局部 clue-selection 有实际价值；
2. 即使 temperature=0 仍存在运行间变化。

---

## 自然语言 Premise Closure / Coherence revision

最终修订：

```text
2/18 strict-valid
No-H = 0/8
```

并且仍然出现：

- 未建立文章存在就询问标题；
- 未建立共同捐赠就询问建筑属性；
- 未建立采访事件就询问歌曲；
- memorandum date 被绑定到 letter；
- 未识别 document 就询问其属性；
- 整道问题被包装成一个所谓 coherent objective；
- stale Need；
- 65,535 reasoning-token length failure。

因此本轮冻结如下解释：

> **“请在内部检查主体和前提”没有稳定转化成最终 Need 行为。**

但这不能证明：

> 显式 premise checking 本身无效。

所以必须把：

```text
Need generation
```

和：

```text
Need premise verification
```

拆开测。

---

# 3. 当前架构假设保持不变

Persistent semantic state 继续只有：

```text
Original Question Q
Verified Claims C
Working Hypothesis H
```

即：

```text
Belief = Q + C + H
```

不增加任何 persistent semantic field。

尤其禁止：

```text
Requirement Map
OpenNeeds
Dependency Graph
Progress
Frontier
Need history
done_when
priority
confidence
persistent premise list
```

本轮新产生的 premise information：

```text
必须是 ephemeral
```

只用于当前 Candidate Need 的合法性检查。

实验结束以后不能成为长期 Research State。

---

# 4. 本轮核心理论区别

必须明确区分：

## Target

Candidate Need **真正正在询问的未知关系**。

它当然可以还没有 Claim 支持。

例如：

```text
Did Kwon and his spouse make the foundational donation?
```

这里：

```text
JointDonation(Kwon, spouse, ...)
```

就是 target。

它未知完全合法。

---

## Presupposition

为了使当前问题能够这样问，已经被语言结构当作背景事实使用的关系。

例如：

```text
Which university received the building
that Kwon and his spouse donated?
```

这里：

```text
Kwon and spouse donated the building
```

已经不是 target。

它被当成背景事实。

如果 Q / Claims 没有建立它：

当前 Need 非法。

---

## 这是本轮最重要的区别

不要使用：

```text
“没有 Claim 支持 = 非法”
```

这个粗糙规则。

真正规则是：

```text
target may be unresolved
background presupposition must be grounded
```

---

# 5. 本轮实验总体结构

严格分三阶段：

```text
E0  reference premise audit 冻结
E1  Premise Checker capability
E2  Constrained Need Repair
E3  Fresh confirmation（只有 E1+E2 PASS 才允许）
```

本任务明确：

```text
不执行 Multi-Query
不执行 Search / Find / Open
不执行 Writer
不执行 Closure
不执行 autonomous loop
```

---

# 6. E0：构造 Candidate Need development bank

不要重新调用 Need generator。

复用上一轮已经真实产生并冻结的 **exact B0 Candidate Needs**。

来源：

```text
minimal_need_multiquery/e1_need/development_run/
minimal_need_multiquery/e1_need/revision/run/
```

只使用：

```text
B0
```

不要使用修订 B3 作为本轮 Candidate Need generator。

原因：

> 本轮希望保留原 B0 的 local clue-selection 能力，只研究它生成之后的 premise/referent failure。

---

# 7. Candidate bank 的机械选择方式

从两轮 B0 exact outputs 中构造 development bank。

先读取上一轮冻结 semantic review。

候选分为：

## Error candidates

包括所有：

- unsupported background relationship；
- unverified event 被当作已发生；
- wrong object/date/relation binding；
- unresolved concrete referent 被直接询问下游属性；

的 B0 Candidate Need。

如果一个 Need 同时还有别的错误，也保留并注明。

---

## Valid controls

从历史 frozen review 判为 strict-valid 的 B0 Candidate Need 中：

机械选取与 error candidates **相同数量**。

不能手挑“看起来容易”的 valid controls。

使用例如：

```text
sha256(state_id + run_id)
```

排序后取前 N。

尽可能保持：

```text
H / No-H
```

比例接近 error bank。

---

## 不把 pure broadness 作为本轮主要错误

如果某 Candidate Need 唯一问题只是：

```text
bundles independent research objectives
```

本轮不把它作为 premise checker 的主要 positive case。

可以保留为 secondary diagnostic，但不得把 premise checker 无法修复 broadness 解释成本轮失败。

---

# 8. 建议 bank 大小

如果现有 B0 历史输出能提供：

```text
10–14 个 premise/referent error candidate
```

则选择相同数量 valid controls。

目标：

```text
20–28 candidate instances
```

不要为了达到整数目标人工创造 case。

同一个 QCH 可以因为 v1 / r1 B0 生成不同 Candidate Need 而出现两次。

这种情况合法，但必须报告：

```text
candidate-instance count
unique state count
unique qid count
```

不能把它们当完全独立题。

---

# 9. E0：冻结 reference premise audit

**必须在任何本轮模型调用之前完成。**

Codex 作为单 reviewer，对每个 Candidate Need 人工写 reference audit。

必须读取：

```text
Q
Claims with IDs
H
Candidate Need
```

不得读取：

```text
未来模型 audit 输出
未来 repair 输出
gold answer
后续 trajectory
未来 Search
```

---

# 10. Reference audit schema

建议：

```json
{
  "candidate_id": "...",

  "candidate_need": "...",

  "target": {
    "description": "当前 Need 真正询问的未知关系/属性"
  },

  "subject": {
    "description": "当前问题正在谈论的具体对象/事件",
    "status": "grounded | unresolved_referent | invented",
    "basis_refs": ["Q", "C3"]
  },

  "required_background": [
    {
      "statement": "为了这样询问 target，语言上已经当作背景成立的事实",
      "status": "supported | unsupported",
      "basis_refs": ["Q", "C2"]
    }
  ],

  "reference_decision": "keep | lift_premise | discover_subject",

  "repair_target": "如果必须修复，应该提升为当前 Need 的直接未解决关系；否则 null",

  "ambiguity": "low | medium | high",

  "reason": "..."
}
```

---

# 11. Reference audit 的语义规则

## `keep`

Candidate Need 的主体足够确定，并且除了 target 本身以外，没有 unsupported background assumption。

---

## `lift_premise`

Candidate Need 正在询问：

```text
Attribute(R)?
```

但：

```text
R
```

尚未建立。

此时 repair target 是：

```text
Does R hold?
```

---

## `discover_subject`

当前 Need 询问一个具体对象/事件的属性，但这个具体 referent 还没有被识别。

例如：

```text
Does the target book cite Euler?
```

如果当前只知道“存在一本满足若干描述的书”，还没有具体书籍绑定：

应先做 subject/source discovery。

---

# 12. 特别注意：Q 中的描述可以合法形成 discovery question

例如 Q 描述：

```text
a book with N illustrations and telephone/telegraph content
```

那么：

```text
Which book matches these features?
```

可以是合法 discovery Need。

不要因为“书还没识别”而拒绝所有 discovery question。

区别是：

```text
Which book matches X?
```

是在发现 subject；

而：

```text
Does that book cite Euler?
```

通常已经把一个未绑定 book 当成可直接检查的具体 subject。

---

# 13. Reference audit freeze

生成：

```text
e0_reference/
  CANDIDATES.json
  REFERENCE_AUDIT.json
  SELECTION.json
  REPORT.md
```

然后：

```bash
git add ...
git commit -m "Freeze premise-audit development bank and reference labels"
```

模型调用前记录：

```text
exact commit
sha256 of every frozen input
```

---

# 14. E1：只测试 Premise Checker

E1 **不生成新 Need**。

输入：

```text
Q
Claims with IDs
H
Candidate Need
```

只判断这个 Candidate Need 的：

```text
target
subject grounding
background presuppositions
```

---

# 15. E1 两个模型 Arm

为了控制“多调用一次本身”的收益，做两个同期 verifier。

## V0 — Generic second-pass verifier

不教它显式 target/presupposition 分解。

任务只是：

> 判断 Candidate Need 相对于当前 Q / Claims / H 是否可以安全作为下一研究问题；指出 unsupported assumption / wrong binding / unresolved referent。

这是 generic reflection compute control。

---

## V1 — Explicit Premise Checker

强制：

```text
target
subject
required_background
basis binding
```

显式化。

这是本轮 treatment。

---

# 16. V0 prompt

使用以下 prompt，除非实现需要机械字段调整，否则不要改语义：

```text
You are checking a proposed next research question.

The input contains:
- Original Question
- Verified Claims, each with an ID
- Working Hypothesis
- Candidate Need

Judge only whether the Candidate Need is safe and well-grounded relative to this input.

A Candidate Need is not invalid merely because the relation it asks about is unresolved. The point of research is to investigate unresolved relations.

It is invalid when it treats an unsupported identity, event, relationship, date, role, or concrete referent as already established background in order to ask a downstream question.

The Working Hypothesis is provisional and cannot establish a fact.

Do not choose a different research direction. Do not plan searches. Do not answer the Original Question.

Return only:

{
  "decision": "keep" | "revise",
  "issue": "short description or null",
  "basis_refs": ["Q", "C1", "..."]
}

basis_refs may contain only Q or existing Verified Claim IDs.
If the problem is precisely that no Q/Claim supports the assumption, use an empty list.
```

---

# 17. V1 Explicit Premise Checker prompt

这是本轮核心 treatment：

```text
You are a Need Premise Checker.

You do NOT choose the next research direction.
You do NOT rewrite the Candidate Need.
You do NOT plan a search.
You only analyze the Candidate Need that has already been proposed.

The input contains:
- Original Question
- Verified Claims, each with an ID
- Working Hypothesis
- Candidate Need

Your task is to separate:

1. TARGET:
   What relation or attribute is the Candidate Need actually asking us to discover?
   The TARGET is allowed to be unresolved.

2. SUBJECT:
   What concrete entity, source, event, relationship, or object is the Candidate Need asking about?
   Determine whether that subject is already identifiable from the Original Question or Verified Claims.

3. REQUIRED BACKGROUND:
   What facts must already be true for the Candidate Need to ask its TARGET in this form?
   These are background presuppositions, not the TARGET itself.

For every required background fact, bind it only to:
- "Q" if the Original Question itself establishes that fact, or
- an exact Verified Claim ID if that Claim establishes it.

The Working Hypothesis may suggest a candidate to test, but it can never be used as support.

IMPORTANT:
Do not reject a question merely because its TARGET is unresolved.

Example of the distinction in abstract form:

"Did X perform event R?"
→ R is the TARGET. It may be unresolved.

"What year did X perform event R?"
→ X performed R is REQUIRED BACKGROUND.
If that event has not been established, the question is premature.

"Which entity matches description D?"
→ identifying the entity is the TARGET.

"Does the entity described by D have property P?"
→ if no concrete entity has yet been identified and checking P requires such a binding, the subject may still be unresolved.

Do not use outside knowledge.
Do not infer facts merely because they are plausible.
Do not copy facts from the Working Hypothesis into support.

Return only one JSON object:

{
  "target": "short natural-language description",

  "subject": {
    "description": "the concrete subject/event/source being queried",
    "status": "grounded" | "unresolved_referent" | "invented",
    "basis_refs": ["Q", "C1"]
  },

  "required_background": [
    {
      "statement": "one background fact",
      "status": "supported" | "unsupported",
      "basis_refs": ["Q", "C2"]
    }
  ],

  "decision": "keep" | "lift_premise" | "discover_subject"
}

Use "keep" when the subject is adequately grounded and every required background fact is supported.

Use "lift_premise" when the Candidate Need asks a downstream attribute or consequence of a relation/event that is itself still unsupported.

Use "discover_subject" when the Candidate Need requires a concrete entity/source/event that has not yet been identified.

Do not output a revised Need.
Do not output explanations outside JSON.
```

---

# 18. basis_refs 的 Harness 校验

程序必须机械检查：

```text
Q
或
现有 Claim ID
```

之外的 ref 一律 schema invalid。

例如：

```text
H
memory
C99（不存在）
source title
URL
```

都不允许作为 support ref。

注意：

Harness 只能验证：

```text
ref exists
```

不能自动证明：

```text
ref semantically entails premise
```

语义 binding 仍由 frozen reviewer 评分。

---

# 19. E1 replicate

上一实验已经看到：

```text
exact B0:
14/18 → 10/18
```

因此本轮不能继续假定：

```text
temperature=0 == deterministic
```

每个：

```text
candidate × arm
```

执行：

```text
2 independent responses
```

都保留。

不得 best-of。

不得选择更好的一次。

---

# 20. E1 模型配置

为了和上一轮连续比较，默认仍使用：

```text
model = deepseek-flash
temperature = 0
JSON mode
max_retries = 0
omit max_tokens
```

不要因为 Codex 本身是 GPT-6 就把被测模型改成 GPT-6。

Codex 是实验执行者。

被测 policy model 保持历史可比性。

如果仓库真实配置已经变化：

先报告，不得静默替换。

---

# 21. E1 评分

V0 评分：

```text
invalid-candidate detection recall
valid-control specificity
balanced accuracy
replicate agreement
```

---

V1 除上述外，再评：

```text
target identification accuracy
subject-status accuracy
required-background recall
required-background precision
support-binding accuracy
final decision accuracy
replicate agreement
```

---

# 22. 最重要的错误类型

必须区分：

## Missed premise

Reference 有 unsupported background，checker 没找到。

---

## Target/premise confusion

把真正正在研究的 target 当成“必须已经有 Claim”。

这会造成过度保守。

---

## False premise

凭空发明一个“问题必须假设”的事实。

---

## Wrong anchor

premise 判断本身合理，但错误地说 Q/C 支持它。

---

## Subject error

没有识别出具体 referent 尚未绑定，或把 Q 的描述性目标错误判成 concrete grounded subject。

---

# 23. E1 Gate

这是 development mechanism gate。

建议全部满足：

```text
V1 invalid-case recall >= 85%
V1 valid-control specificity >= 85%
V1 support-binding accuracy >= 85%
V1 target/premise distinction accuracy >= 85%
V1 decision replicate agreement >= 80%
valid JSON >= 95%
```

并比较 V0：

```text
V1 balanced accuracy >= V0 balanced accuracy
```

如果 V1 没明显优于 V0：

不能声称 explicit premise structure 有额外价值。

但如果 V1 达到绝对 Gate，而 V0 相近：

可以继续 E2 作为“结构是否帮助 repair”的诊断，但最终结论必须写：

```text
explicit decomposition not yet proven superior to generic second-pass verification
```

如果 V1 连绝对 Gate 都不过：

```text
STOP
```

不得进入 E2。

---

# 24. E2：Constrained Need Repair

只有 E1 PASS 才执行。

这里不重新规划研究。

输入：

```text
Q
Claims
H
Candidate Need
Premise Audit
```

输出：

```text
Final Need
```

---

# 25. Repair 的设计原则

Repair 必须：

```text
verification rich
repair narrow
```

也就是说：

Premise Audit 可以有结构；

最终修复不能自由重新研究整道题。

---

# 26. Repair prompt

```text
You are repairing one already-selected Candidate Need.

Do NOT choose a new research direction.
Do NOT reconsider the whole Original Question.
Do NOT add independent clues or requirements.
Do NOT plan queries or tools.

You receive:
- Original Question
- Verified Claims
- Working Hypothesis
- Candidate Need
- A Premise Audit of that Candidate Need

Apply exactly one of the following operations.

1. KEEP

If the audit decision is "keep":
return the Candidate Need unchanged.

2. LIFT

If the audit decision is "lift_premise":
the Candidate Need asks a downstream attribute or consequence of an unsupported relation/event.

Replace the downstream question with a direct question asking whether that unsupported relation/event holds.

Preserve the same local research focus.
Do not add other Original Question conditions.

Abstract transformation:

"What is Attribute(R)?" 
→
"Does R hold?"

3. DISCOVER

If the audit decision is "discover_subject":
the Candidate Need requires a concrete subject/source/event that has not yet been identified.

Ask a discovery question for that subject using only the minimum identifying description already available in Q or Verified Claims.

Do not ask any downstream property until the subject is identified.

IMPORTANT:

- The Working Hypothesis is not evidence.
- Do not add names, dates, places or relations not supported by Q/Claims.
- Do not broaden the Need into the whole Original Question.
- Do not add a second independent research objective.
- Preserve the Candidate Need's local objective as much as possible.

Return only:

{
  "operation": "keep" | "lift" | "discover",
  "need": "one natural-language research question"
}
```

---

# 27. E2 两种 audit source

为了分离：

```text
checker failure
```

和：

```text
repair failure
```

必须跑两个 repair 条件。

## R1 — Model Audit Repair

使用：

```text
V1 的第一条预注册 replicate
```

不能事后选更好的 replicate。

---

## R2 — Oracle Audit Repair

使用 E0 冻结的：

```text
REFERENCE_AUDIT
```

作为 audit。

同一个 repair prompt。

---

# 28. 为什么 Oracle Repair 很重要

如果：

```text
Oracle audit + Repair
```

仍然大量失败：

说明问题在：

```text
repair transformation
```

不是 premise checker。

---

如果：

```text
Oracle Repair 很好
Model Audit Repair 很差
```

说明真正瓶颈是：

```text
premise extraction / binding
```

---

如果两者都很好：

才说明整个：

```text
Generate → Check → Repair
```

值得进入 fresh confirmation。

---

# 29. E2 primary metrics

相对于原 Candidate Need：

```text
overall strict-valid rate
invalid-candidate repair rate
valid-control preservation rate
paired improve
paired regress
new unsupported premise
new unresolved referent
new broadness
stale introduction
objective drift
```

---

# 30. Locality preservation

必须额外检查：

> Repair 后是否仍然围绕 Candidate Need 原来选中的局部 clue / relation family？

不能出现：

```text
Candidate:
检查文章是否存在

Repair:
重新识别作者、学历、任职、其他出版物
```

这种“修复”虽然可能相关，但已经重新 planning。

记为：

```text
objective drift
```

---

# 31. E2 Gate

建议 Model-Audit pipeline 至少：

```text
overall strict-valid >= 80%
invalid-candidate repaired >= 70%
valid-control preserved >= 90%
paired improvements > paired regressions
objective drift <= 5%
```

同时 Oracle Repair：

```text
overall strict-valid >= 85%
```

如果 Oracle Repair 明显失败：

停止。

不要归罪于 Checker。

如果 Oracle 很好而 Model Audit 差：

下一轮只研究 Premise Checker，不再改 Repair。

---

# 32. E3：Fresh Confirmation

只有：

```text
E1 PASS
E2 PASS
```

才允许执行。

不得使用：

```text
当前 development qids
旧 B5 dev qids
旧 B5 confirmation qids
minimal-need-multiquery development qids
Need Review 调参 qids
```

作为 fresh。

---

# 33. Fresh bank

目标：

```text
12–15 completely new qids
30–40 natural QCH states
```

必须来自自然 trajectory / archived state。

不能人工拼 Claims。

不能为了制造 premise error 而修改 H。

Candidate Need 仍由：

```text
exact original B0
```

生成。

不要使用失败的 revised B3 prompt。

---

# 34. Fresh 比较

对于每个 fresh QCH：

先运行一次：

```text
B0 → Candidate Need
```

冻结。

然后：

```text
Candidate Need → V1 Premise Audit → Repair
```

比较：

```text
Candidate Need
vs
Final Need
```

同一个 Candidate，因此 paired。

---

# 35. Fresh primary question

不是：

> Checker 能不能制造更多变化？

而是：

\[
\boxed{
\text{显式 premise checking 是否提高最终 Need 的 strict validity，且不明显破坏原本合法 Need？}
}
\]

---

# 36. Fresh Gate

工程 gate 建议：

```text
Final Need strict-valid >= 80%
unsupported-premise / referent errors <= 5%
paired improvements >= paired regressions + 15 percentage points
valid Candidate regression <= 10%
valid output >= 95%
```

No-H 单独报告。

如果 sample 规模不足，不做显著性声称。

---

# 37. Fresh 结束后必须停止

即使 E3 PASS：

本任务也不要继续执行：

```text
Multi-Query
Search
Find
Open
Writer
Closure
full loop
```

因为这是下一独立实验。

本轮最终只回答：

> `Q+C+H → Candidate Need → explicit premise check → Final Need`

这一计算是否成立。

---

# 38. 不允许的解释

如果实验成功，最多可以说：

> 一个短暂、显式、局部的 premise audit 能提高 Candidate Need 的合法性。

不能说：

```text
Dependency Graph is needed
Requirement Map is needed
OpenNeeds is needed
persistent premise state is useful
Multi-Query works
Closure works
full loop works
```

---

如果实验失败，也不能直接说：

```text
Q+C+H state is insufficient
```

因为失败也可能是：

```text
checker computation failure
repair computation failure
model instability
```

只有正确定位后才能增加 state。

---

# 39. 成本控制

在任何真实调用前计算：

```text
planned call count
replicate count
estimated prompt tokens
historical completion-token distribution
worst-case exposure
```

由于上一轮出现过：

```text
65,535 reasoning-token length failure
```

必须单独报告 tail-risk。

不要通过 retry 删除这种失败。

---

# 40. 真实调用纪律

本任务允许执行这一轮**有界的 Premise Audit 机制实验**。

但必须遵守：

```text
先 freeze
再 commit
再调用
```

不得：

```text
看几条结果后修改 prompt
删掉奇怪输出
重试 semantic failure
替换样本
挑选较好 replicate
```

如果凭证、费用、服务端权限阻止调用：

保留状态并停止；

不要伪造执行结果。

---

# 41. 建议目录

```text
experiments/need_premise_audit/
├── README.md
├── TASK.md
├── PRE_EXECUTION_AUDIT.md
├── HYPOTHESES.md
├── PROTOCOL.md
├── CONFIG.json
├── FREEZE.json
│
├── prompts/
│   ├── generic_verifier.txt
│   ├── premise_checker.txt
│   └── constrained_repair.txt
│
├── e0_reference/
│   ├── CANDIDATES.json
│   ├── SELECTION.json
│   ├── REFERENCE_AUDIT.json
│   └── REPORT.md
│
├── e1_checker/
│   ├── SCHEDULE.json
│   ├── calls/
│   ├── review/
│   ├── METRICS.json
│   └── REPORT.md
│
├── e2_repair/
│   ├── SCHEDULE.json
│   ├── model_audit/
│   ├── oracle_audit/
│   ├── METRICS.json
│   └── REPORT.md
│
├── e3_fresh/
│   ├── STATUS.md
│   └── ...
│
└── analysis/
    ├── EXECUTION_ACCOUNTING.json
    ├── INTEGRITY.json
    └── FINAL_CONCLUSION.md
```

---

# 42. 研究假设必须预注册

至少：

## H1

显式区分：

```text
target
vs
background presupposition
```

能提高 unsupported-premise / unresolved-referent 检测能力。

---

## H2

显式 basis binding：

```text
Q / Claim ID / unsupported
```

能减少把 H、常识或错误对象关系当作事实依据。

---

## H3

在正确 premise audit 条件下，受限：

```text
KEEP / LIFT / DISCOVER
```

repair 可以提高最终 Need 合法性，而不明显破坏 valid Candidate Need。

---

## H4

如果 generic second-pass verifier 与 explicit premise checker 表现相同：

则不能宣称结构化 Premise Audit 本身有额外价值。

---

# 43. 最终必须回答的问题

最终报告按顺序回答：

1. Candidate Need 中最常见的隐藏前提是什么？
2. 模型能否稳定区分 target 和 presupposition？
3. 模型能否发现未绑定 subject/source/event？
4. 它是否会把真正 target 错判成“必须已经支持”？
5. 它能否正确绑定 premise 到 Q / exact Claim？
6. Explicit Premise Checker 是否优于 generic second-pass verifier？
7. 两次重复调用的一致性如何？
8. Oracle premise audit 下，Constrained Repair 是否可靠？
9. Model audit 与 Oracle audit 的差距多大？
10. Repair 是否保留原 Candidate Need 的局部性？
11. Repair 是否产生新的 broadness / stale / hallucination？
12. Fresh QCH 是否复制 development 结果？
13. 这是否足以支持 `Generate → Check → Repair`？
14. 是否有任何结果真正要求 persistent state 增加？
15. 下一步是否有资格重新打开 Need → Multi-Query 实验？

---

# 44. 最重要的停止规则

如果：

```text
Premise Checker 本身不能可靠识别 target / presupposition
```

停止。

不要继续修 Need。

---

如果：

```text
Oracle Audit + Repair
```

都不能稳定改善 Need，

停止。

不要继续改 Checker。

---

如果：

```text
development PASS
fresh FAIL
```

接受 fresh failure。

不要回到开发集继续 patch。

---

# 45. 本轮真正想验证的理论

最终不是验证：

> 多一个 Reviewer 会不会更好。

而是验证：

\[
\boxed{
\text{生成一个研究问题}
\neq
\text{验证这个研究问题的隐含前提}
}
\]

以及：

\[
\boxed{
\text{第二个任务是否足够窄，以至于模型能比第一次生成更可靠地完成它。}
}
\]

如果答案是 YES：

我们得到的不是新的 Persistent State。

而是：

```text
Belief
  ↓
Local Candidate Need
  ↓
Ephemeral Premise Check
  ↓
Constrained Repair
  ↓
Final Need
```

然后中间结构全部丢弃。

Persistent semantic state 仍然只有：

```text
Q + Verified Claims + Working Hypothesis
```

这才是本实验真正值得证明的东西。