你现在负责 Search-ESR 下一阶段核心实验：

# Dynamic Research Progress → Frontier

仓库：

`https://github.com/homulillew/Search-ESR`

当前基线：

`experiment/frontier-generation-state-sufficiency`

开始前必须：

```bash
git fetch --all --prune
```

确认远程该分支最新 HEAD，并记录 exact SHA。

从最新远程创建新分支，例如：

```text
experiment/dynamic-progress-blockers
```

如果已存在同名分支，创建明确 suffix。

本轮继续使用当前 DeepSeek provider / `deepseek-flash`。

你作为 GPT-6 负责：

- 阅读已有研究；
- 设计实验；
- 构建真实 bank；
- 编写并冻结 prompt/schema/runtime；
- 真实模型调用；
- 语义审核；
- 统计分析；
- 完整性审计；
- commit；
- push；
- 最终结论。

禁止请求用户重新确认。

---

# 0. 本轮研究问题

前序实验已经表明：

Persistent Research State 可以压缩为：

```text
Original Question
Verified Claims
Working Hypothesis
```

Selective Claim Admission 能显著减少无关状态增长。

Deferred Recovery 又表明：

当一个未来 Need 被明确给出以后，普通 Global Search 有能力重新找到过去没有进入 Claim 的信息，并由 U1 重新写入 Claim。

但是最新 Frontier Generation 实验失败：

```text
HistoryOnly:      18/48 = 37.5%
StateOnly:        18/48 = 37.5%
State + History:  19/48 = 39.6%
```

StateOnly 虽然把输入上下文压缩约 85%，但没有提高 Frontier 质量，也没有降低 reasoning-token proxy。

主要失败不是 stale search 或 goal drift，而是：

```text
premature STOP
over-broad Need
unsupported premise
```

典型错误包括：

1. 已经识别出一个强候选或最终答案值，因此错误地认为研究已经完成；
2. 知道研究还没完成，但把整个 Original Question 重新表述成一个 Need；
3. 为了产生具体 Need，偷偷把一个尚未证实的 candidate / date / event 当成已经成立的事实；
4. Selective State 遗漏某个未来 requirement 后，模型没有重新意识到该 requirement 仍未被 Claims 支持。

因此当前问题不应继续表述为：

```text
How should Need be phrased?
```

而应表述为：

> 在生成 Current Need 之前，系统是否需要动态计算“当前为什么还不能可靠结束研究”？

本轮核心研究对象：

\[
Progress_t = \Gamma(Q,C_t)
\]

其中：

- \(Q\) = immutable Original Question；
- \(C_t\) = current Verified Claims。

Progress 不是 Persistent State。

Progress 不保存长期计划。

Progress 不预先固定完整 Requirement Graph。

Progress 是：

> 基于当前 Verified Claims，对“为什么现在还不能给出一个有充分证据支持的答案”的动态判断。

---

# 1. 本轮核心理论

当前失败的 Direct Frontier 结构为：

\[
Q+C_t+H_t
\rightarrow
Need_t / STOP
\]

实际上要求同一次模型调用隐式完成：

```text
Question understanding
→ evidence coverage
→ convergence judgment
→ missing relation identification
→ frontier selection
→ Need wording
```

任务过于耦合。

本轮研究新的分解：

\[
Q+C_t
\rightarrow
Progress_t
\]

然后：

\[
Progress_t+C_t+H_t+A_t
\rightarrow
Need_t
\]

其中：

- \(H_t\) = Working Hypothesis；
- \(A_t\) = Recent Attempts。

Progress 回答：

> 我们在哪里？为什么还不能结束？

Frontier 回答：

> 下一步去哪？

这两个任务必须分开评价。

---

# 2. 一个重要限制：禁止重新引入固定问题分解

本轮不能把 Original Question 在 episode 开头一次性拆成：

```text
R1
R2
R3
...
```

然后作为长期权威 checklist 持久化。

之前 query initialization 已经显示：

> 模型在证据不足时对问题做先验完整拆分并不稳定，一旦拆错，后续整条轨迹都会继承错误。

因此禁止：

```text
Persistent Requirement Map
Persistent Goal Graph
Persistent Progress Table
Persistent Completed/Pending List
```

离线评价可以有 reviewer annotations，但绝不能进入 Runtime。

---

# 3. Dynamic Progress 的正式定义

Progress 不等于完整问题 decomposition。

定义：

> 当前 Verified Claims 下，仍然阻止系统给出可靠最终答案的少量 material blockers。

如果 unresolved：

只需指出最多 1–3 个真正重要 blocker。

不要求穷尽 Original Question 的所有线索。

如果至少存在一个 material blocker：

```text
resolved = false
```

只有在当前 Verified Claims 已经足以建立最终答案及其必要支持关系时：

```text
resolved = true
```

---

# 4. 什么叫 Material Blocker

一个 blocker 是 material 的，当其缺失或冲突会满足至少一种情况：

```text
当前候选身份仍不能得到可靠支持；
用户明确要求的最终关系仍不能得到可靠支持；
现实的替代候选仍无法排除；
Claims 中存在可能改变最终答案的重要冲突；
某个明确的原问题条件尚未得到必要的关系绑定。
```

不要把无关背景细节、可有可无的附加事实或普通来源佐证当 blocker。

不要机械要求每一个自然语言 clause 都有单独 Claim。

---

# 5. Progress 不应该做什么

Progress 不负责：

```text
选择 Search query
选择工具
决定 source
生成长期 plan
设置 priority score
设置 confidence score
建立 dependency graph
生成 Current Need
修改 Claims
修改 Hypothesis
```

Progress 只回答：

> 当前是否已经可以结束；如果不可以，为什么不可以。

---

# 6. Progress 第一版 Schema

建议先使用极简结构：

```json
{
  "resolved": false,
  "blocking_gaps": [
    {
      "gap": "The candidate series' total number of seasons is not established.",
      "status": "missing",
      "claim_refs": []
    }
  ],
  "closure_claim_refs": []
}
```

如果 resolved：

```json
{
  "resolved": true,
  "blocking_gaps": [],
  "closure_claim_refs": [2, 5, 8]
}
```

其中 `status` 只允许：

```text
missing
partial
conflict
```

不要加入：

```text
requirement_id
priority
confidence
percentage_complete
next_action
query
source
dependency
```

`claim_refs` 引用当前 Verified Claims 的索引。

Harness 只机械验证：

- ref 是否存在；
- schema 是否有效。

Harness 不判断 Claim 是否真的支持 blocker / closure。

---

# 7. status 的严格定义

`missing`：

当前 Claims 不足以建立该关键关系。

例如：

> 演员出现在第五季

不等于：

> 总季数少于十季。

这种情况仍应视为 missing，而不是 partial。

`partial`：

只有在 Claims 已经真正建立了所需关系的一部分，但尚缺必要范围、时间、角色、数量或另一端绑定时使用。

`conflict`：

当前 Claims 中存在对该 material relation 有实质影响的互相冲突事实。

禁止把：

> 已经看到某个 Claim

直接解释为：

> requirement 已解决。

---

# 8. Progress 输入

Progress Evaluator 只看：

```text
Original Question
Verified Claims
```

不看：

```text
Working Hypothesis
Research History
Workspace raw windows
Recent Attempts
Current Gap
Previous Need
Search failures
Goal Residual
offline labels
gold requirement map
```

原因：

Progress 判断的是：

> 当前 Verified Belief 是否足以支持 Original Question。

Hypothesis、搜索路径和 Workspace 本身不能让一个未被 Claim 支持的 requirement 自动变成 resolved。

本轮所有角色继续使用同一个 `deepseek-flash`。

Progress Evaluator 只是一次独立语义调用，不是新模型，也不是新的 Agent。

---

# 9. Progress Prompt

建议第一版使用以下核心语义，不要自行扩张 ontology：

```text
You are evaluating the current research progress.

The Original Question is the authoritative goal.

Verified Claims are the only facts that may be treated as established.

Your task is NOT to plan the next action and NOT to decompose the entire question into a permanent checklist.

Decide whether the Verified Claims are sufficient to support a reliable answer to the Original Question.

A strong candidate, plausible identity, Working Hypothesis, likely answer, or partial clue match is NOT enough for closure.

If an important relation, scope, date, quantity, identity link, requested final relation, or material conflict remains unsupported, the research is unresolved.

If unresolved, identify only 1 to 3 material blocking gaps that currently prevent justified closure.

A blocking gap should state what has NOT yet been established.
Do not turn a condition from the Original Question into an asserted fact about a candidate.

For example:
- If the question requires a match with a 95th-minute free kick, and no Claim establishes that a candidate match contains that event, say that this relation is not established.
- Do NOT ask who took the 95th-minute free kick in a specific candidate match unless that event has already been established for that match.

Do not invent requirements that are not materially connected to the Original Question.

Do not propose a search query, source, action, plan, priority, or next research step.

A requirement is supported only when the Verified Claims jointly entail the required relation.
Two individually true facts must not be joined into a stronger relation unless the Claims actually establish that relation.

If at least one material blocker remains:
return resolved=false.

If and only if the Verified Claims are sufficient to establish the requested answer and no material blocker remains:
return resolved=true.

When resolved=true, identify the Claim indices that form the main closure basis.

Return exactly the required JSON object.
```

不要额外加入“be conservative”之类模糊措辞，除非后续实验明确证明需要。

---

# 10. Harness 调度假设

Persistent semantic state 仍然是：

\[
S_t=(Q,C_t,H_t)
\]

Progress：

\[
P_t=\Gamma(Q,C_t)
\]

Harness 维护：

```text
claims_version
progress_input_hash
progress_cache
```

推荐：

\[
progress\_key=Hash(Q,C_t)
\]

如果 key 未变化：

```text
reuse Progress
```

如果 Verified Claims 发生变化：

```text
invalidate Progress
```

下一次 Research Decision 前：

```text
if progress_cache is stale:
    recompute Progress
```

Hypothesis 变化不触发 Progress 重算。

Workspace 变化不触发 Progress 重算。

Search/Find/Open 没有生成新 Claim 时，不触发 Progress 重算。

本轮首先验证该简单规则，不增加其他 refresh policy。

---

# 11. Stage P0：构建实验 Bank

需要两个数据集。

## Challenge Set

保留 Frontier Generation F1 已经使用过的 24 checkpoint。

这些只用于机制诊断。

它们已经被反复分析，不能冒充 fresh primary validation。

## Fresh Primary Set

从已有真实 checkpoint inventory 中排除 F1 使用过的 checkpoint。

从剩余真实历史状态中机械选择：

```text
24–30 checkpoints
>=8 qids
单qid尽量<=4
```

不得根据本轮模型输出选择。

不得人工修改 Claims。

不得删除不利 Claim。

不得人工加入缺失 Claim。

不得构造 synthetic State。

优先覆盖：

```text
明显未完成；
强候选但仍有material blocker；
Claims存在重要冲突；
Selective State可能遗漏未来requirement；
near closure；
真正resolved。
```

---

# 12. Bank 的离线评价方式

不要重新构造一个完整 Runtime Requirement Map。

对每个 checkpoint，只冻结：

```text
gold_resolved: true / false
```

如果 unresolved：

记录若干：

```text
acceptable_blockers
```

它们表示：

> 当前任何一个都足以作为“为什么还不能结束”的合理解释。

不要求穷尽所有 blocker。

另外记录：

```text
known_unsupported_assumptions
```

例如：

```text
“Liverpool–Milan contains the required 95th-minute event”
```

如果当前 evidence 没有建立这一点，就记录为非法前提。

这些标签只能用于离线 evaluation。

绝不能进入模型请求。

---

# 13. Stage P1：Dynamic Progress 本身是否可靠

P1 不运行：

```text
Search
Find
Open
Writer
Frontier
```

只研究：

\[
Q+Claims\rightarrow Progress
\]

比较两个主要 arm。

---

# 14. P1-R：旧 Goal Residual

沿用旧 Goal Reviewer 的基本形式：

```json
{
  "resolved": false,
  "residual": "..."
}
```

同样只看：

```text
Original Question
Verified Claims
```

不要调旧 Prompt 来适配结果。

它代表：

> 自由文本 Residual。

---

# 15. P1-B：Dynamic Blocker Progress

使用新的 blocker schema。

输入与 R 完全相同：

```text
Q + Claims
```

区别只在：

- prompt；
- 输出表示。

这样可以回答：

> 是额外一次 Goal Review 本身有用，还是明确的 blocker 表示更有用。

---

# 16. P1 调用设计

每个 checkpoint：

```text
R × 2 independent calls
B × 2 independent calls
```

两次都必须进入 denominator。

禁止：

```text
best-of
retry
repair
挑选更好的replicate
```

如果 Fresh Set 24：

```text
24 × 2 arms × 2 replicates = 96 calls
```

Challenge Set 可单独做 diagnostic，不与 fresh 主分母混合。

---

# 17. P1 核心指标

## False Closure

在真实 unresolved checkpoint 上：

```text
resolved=true
```

这是最高优先级错误。

报告：

\[
FalseClosureRate
\]

---

## Correct Closure

真正 resolved checkpoint：

```text
resolved=true
```

的比例。

---

## Valid Blocker Presence

对 unresolved checkpoint：

是否至少有一个 blocker：

```text
material
currently unresolved
grounded in Original Question
does not assume unsupported candidate relation
```

---

## Blocker Precision

所有生成 blocker 中：

合理 blocker / 全部 blocker。

---

## Unsupported Premise

是否把：

```text
question constraint
```

错误变成：

```text
candidate fact
```

---

## Over-broad Progress

blocker 是否基本重新复述整道 Original Question。

---

## Invented Requirement

是否提出 Original Question 实际不需要的 material requirement。

---

## Closure Witness Quality

resolved=true 时：

`closure_claim_refs` 是否至少构成合理的主要支持链。

---

# 18. P1 Replicate Stability

对相同：

\[
Q,C
\]

两次调用，记录：

```text
both resolved correctly
both unresolved with compatible valid blockers
one correct / one incorrect
both incorrect
```

不要求 blocker wording 一致。

不要求两次选择完全相同 blocker。

重点是：

> completion judgment 和 blocker semantics 是否稳定。

---

# 19. P1 参考 Gate

预注册前可微调整数阈值，但不得看结果后修改。

建议：

```text
False closure <= 10%
Valid blocker presence >= 85%
Blocker precision >= 90%
Correct closure >= 90%
```

并且关键错误不能集中由单个 qid 假性撑起。

如果 B 没明显超过当前 Direct Frontier 的 completion reliability：

不要进入正式 P2。

---

# 20. 一个独立的小型 decomposition sensitivity

为直接回应此前 query initialization 的失败：

从 Fresh Set 中机械选择：

```text
12 checkpoints
>=6 qids
```

额外比较：

### FULL

要求模型：

> 完整列出所有 material requirements，并标记 supported / missing / conflict。

### BLOCKER

只要求：

> 输出最多三个当前 blocker。

主要比较：

```text
invented requirement
omitted material blocker
replicate stability
false closure
tokens
reasoning proxy
```

这是 sensitivity，不是新的 Runtime 方案。

目标是验证：

> 完整拆题是否真的比局部动态 blocker 更可靠。

如果 FULL 没明显更好，则不继续维护完整 requirement table。

---

# 21. Stage P2：正确 Progress 是否真的能改善 Need

只有 P1-B 达到基本可靠性后执行。

此阶段仍然不调用 Search。

比较三个 arm。

---

# 22. P2-D：Direct Frontier

基线：

\[
Q+C+H
\rightarrow
Need/STOP
\]

使用与最新 Frontier Generation 实验同类的 direct prompt。

不要事后强化。

---

# 23. P2-O：Oracle Blocker

使用离线冻结的一个真实 blocker。

模型看到：

```text
Original Question
Verified Claims
Working Hypothesis
Current Blocking Gap
Recent Attempts
```

不允许 STOP。

只生成：

```text
Need
```

这是 Frontier Selector 的能力上界诊断。

---

# 24. P2-B：Generated Blocker

使用 P1-B 同 checkpoint 实际生成的 blocker。

同样不允许 STOP。

Frontier Selector 从该 blocker 生成 Need。

禁止根据 P1 结果挑选“好的 blocker”。

所有 predeclared cells 都进入 denominator。

---

# 25. Frontier Selector Prompt

核心语义建议：

```text
You are selecting the next research frontier.

Research is already known to be unresolved.

The Current Blocking Gaps describe what is still preventing a justified answer.
They are not verified facts about any candidate.

Choose exactly one current research need that would materially reduce one of these blocking gaps.

The need should be a question about what must still be established.

Do not assume that a candidate satisfies a missing condition merely because that condition appears in the Original Question.

If a candidate relation is not yet verified, phrase the need as a test:
“Does candidate X satisfy Y?”
rather than assuming:
“Who/what is Y in candidate X?”

Choose a bounded current uncertainty, not the entire Original Question.

You may use the Working Hypothesis to choose a candidate to test, but the Hypothesis remains provisional.

Recent Attempts may be used to avoid repeating an unproductive path.

Do not output a search query, tool, source, plan, confidence score, or list of multiple needs.

Return exactly one Need.
```

---

# 26. P2 核心指标

```text
Valid Need
Unsupported premise
Over-broad Need
Stale Need
Goal drift
Need corresponding to provided blocker
Replicate stability
```

最关键的因果解释：

如果：

```text
Oracle Blocker >> Generated Blocker
```

说明主要瓶颈在 Progress。

如果：

```text
Oracle Blocker 仍然很差
```

说明 Frontier Selection 有独立问题。

如果：

```text
Generated Blocker ≈ Oracle Blocker >> Direct
```

这是两阶段解耦最强的正向信号。

---

# 27. Stage P3：Progress 是否真的动态跟随 Claims 变化

只有 P1 证明静态 Progress 有基本可靠性后执行。

构建：

```text
12–20 real transitions
>=6 qids
```

必须来自真实历史：

```text
pre Claims
real Observation / real Writer mutation
post Claims
```

不得人工造 post-state。

---

# 28. P3 Transition 类型

至少覆盖：

### T1 blocker resolved

新增 Claim 解决一个此前 blocker。

Post Progress 不应继续报告同一 blocker。

### T2 new conflict

新增 Claim 与旧 Claim 在 material relation 上冲突。

Post Progress 应能够形成 conflict blocker。

### T3 incidental Claim

新增 Claim 对 Original Question 的完成状态没有实质价值。

Progress 不应大幅漂移。

### T4 final closure

最后 material blocker 被解决。

应：

```text
resolved=false
→
resolved=true
```

---

# 29. P3 主要指标

```text
Resolved-blocker disappearance
New-conflict appearance
Incidental-mutation invariance
Correct closure transition
False closure after transition
Progress semantic stability
```

不要用文字 equality 判断 blocker。

使用离线语义审查。

---

# 30. Harness 缓存规则的验证

同时离线验证：

\[
Progress=f(Q,Claims)
\]

是否足以解释真实 Progress mutation。

记录：

```text
Claims unchanged / Hypothesis changed
Claims unchanged / Workspace changed
Claims changed
```

检查：

> Progress 是否主要只需要在 Claims mutation 后更新。

如果大量 case 显示：

```text
Claims unchanged
but correct Progress should change
```

则：

\[
Hash(Q,Claims)
\]

缓存假设失败。

不要在看到结果前增加额外 trigger。

---

# 31. Stage P4：小型真实闭环

只有 P1–P3 均给出正向机制证据后执行。

使用：

```text
8–12 held-out real cases
>=6 qids
```

不要用 Challenge Set 作为唯一来源。

每个最多：

```text
3 decisions
1 action / decision
```

继续使用冻结的：

```text
v3a Search
Find
Open
U1 selective Writer
same model/provider
```

不得修改 Retrieval 或 Writer。

---

# 32. P4-D：Direct Loop

继续：

```text
State
→ Need/STOP
→ Action
→ Evidence
→ Writer
```

---

# 33. P4-P：Progress Loop

执行：

```text
if Progress stale:
    Progress = Evaluate(Q, Claims)

if Progress.resolved:
    STOP
else:
    Need = SelectFrontier(
        Progress,
        Claims,
        Hypothesis,
        RecentAttempts
    )

Action = Actor(
    Need,
    Workspace,
    RecentAttempts,
    Budget
)

Observation = Execute(Action)

Claims/Hypothesis = U1(...)
```

然后：

```text
if Claims changed:
    invalidate Progress
```

---

# 34. P4 不新增 verify/recover Tool

Runtime action space仍然只有：

```text
Search
Find
Open
```

Progress Evaluation 不是 Actor action。

它由 Harness 在 decision boundary 机械触发。

Harness 不做语义 Progress 判断。

---

# 35. P4 Failure 分层

最终必须分别统计：

```text
Progress failure
Frontier failure
Retrieval failure
Localization failure
Admission failure
Hypothesis/control failure
False closure
Missed closure
Horizon exhausted
```

禁止把所有失败归为：

```text
agent failed
```

---

# 36. P4 最重要指标

完整成功链：

\[
Belief
\rightarrow
Progress
\rightarrow
Need
\rightarrow
Evidence
\rightarrow
Belief
\]

特别记录：

```text
Autonomous deferred requirement reactivation
```

即：

过去没有进入 Claim 的 requirement，

是否后来通过：

```text
Progress blocker
→ Need
→ Search/Find/Open
→ Observation
→ Claim
```

重新进入 Belief。

这是整个 Minimal State + Recovery 架构最重要的闭环测试。

---

# 37. 冻结不允许修改的组件

本轮固定：

```text
model
provider
Search
Find
Open
retriever
localizer
Workspace implementation
U1 Writer
Claim schema
Working Hypothesis schema
corpus
question set
DeepSeek JSON transport
retry=0
best-of=0
```

不得添加：

```text
confidence
persistent Progress
persistent blocker IDs
Requirement Graph
Plan Graph
Recovery tool
Memory tool
semantic Harness router
query optimizer
```

---

# 38. 一次有限探索

如果一个主要 Gate 失败：

允许一次 bounded exploration。

必须先写：

```text
EXPLORATION_PLAN.md
```

commit + freeze。

只能选择 observed dominant failure 的一个方向。

允许方向例如：

```text
A. false closure：加强 closure witness 要求；
B. blocker 偷渡候选事实：强化“missing relation must remain unresolved”约束；
C. blocker过宽：限制每个blocker只描述一个关系；
D. generated Progress 对但 Need 错：调整 Frontier Selector；
E. Q+Claims 明显不足：小型 Q+Claims+recent observation/history sensitivity。
```

最多：

```text
12 checkpoints
<=24 Progress/Frontier calls
```

探索不能覆盖 Primary Gate。

禁止 prompt sweep。

---

# 39. 最终报告必须回答

最终必须明确回答以下核心问题：

```text
Q+Claims 能否可靠判断是否仍存在material blocker？
false closure到底是多少？
Dynamic Blocker 是否比旧自由文本 Residual 更可靠？
完整 Requirement decomposition 是否真的有额外价值？
blocker 是否容易发明 requirement？
blocker 是否容易把 question constraint 偷渡成 candidate fact？
给定正确 blocker 后，Frontier Selector 能否稳定生成合理 Need？
Oracle Blocker 与 Generated Blocker 差多少？
Direct Frontier 与 Progress-assisted Frontier 差多少？
Claims mutation 后 blocker 是否合理消失/出现？
Hypothesis变化但Claims不变时是否需要Progress重算？
Q+Claims hash 缓存策略是否成立？
Progress是否真的减少premature STOP？
是否减少whole-question Need？
是否减少unsupported premise？
是否提升deferred requirement自主重新激活？
最终主要瓶颈落在Progress、Frontier、Retrieval还是Admission？
```

---

# 40. 最终理论判断标准

如果观察到：

\[
ProgressAccuracy\ high
\]

并且：

\[
GeneratedProgress\rightarrow Need
\approx
OracleProgress\rightarrow Need
\]

且显著优于：

\[
DirectState\rightarrow Need/STOP
\]

那么可以支持：

> 长程 Research Agent 在 Persistent Belief 和 Current Frontier 之间，需要一个显式但非持久的动态研究进度表示。

最终架构可写为：

\[
S_t=(Q,C_t,H_t)
\]

\[
P_t=\Gamma(Q,C_t)
\]

\[
N_t=\Pi(P_t,C_t,H_t,A_t)
\]

\[
a_t=Policy(N_t,Workspace_t,A_t,Budget_t)
\]

\[
O_t=Execute(a_t)
\]

\[
(C_{t+1},H_{t+1})
=
Update(C_t,H_t,N_t,O_t)
\]

从而形成：

\[
\boxed{
Belief
\rightarrow
Progress
\rightarrow
Frontier
\rightarrow
Action
\rightarrow
Evidence
\rightarrow
Belief
}
\]

---

# 41. 最重要的负面结果解释

如果 Dynamic Blocker 本身仍然大量：

```text
false closure
invented requirement
unsupported candidate relation
instability
```

不要继续堆 Frontier prompt。

这说明真正的瓶颈仍在：

\[
Q+Claims
\rightarrow
Progress
\]

如果 Oracle Blocker 给出后 Need 仍然失败：

说明 Frontier Selection 有独立困难。

如果 Progress 和 Need 都很好，但闭环仍失败：

再看 Retrieval / Admission。

不要为了让最终系统“看起来完整”而跨越失败 Gate。

---

# 42. 最终原则

本轮始终坚持：

```text
不要持久化“问题怎么拆”。

只动态计算“当前为什么还不能结束”。

不要让Harness理解语义。

只让Harness知道何时需要重新计算。

不要让Progress规划下一步。

Progress只描述当前位置。

不要让Frontier决定是否完成。

Frontier只决定下一步去哪。
```

让实验回答：

\[
\boxed{
Dynamic\ Progress
是否真的是
Belief
与
Frontier
之间缺失的那一层。
}
\]