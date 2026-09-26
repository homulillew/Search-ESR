你现在负责 Search-ESR 当前最重要的一项研究：

# Belief → Need Convergence
# 从研究信念状态到下一研究问题的闭环收敛实验

目标不是完成一次 prompt 对比。

目标是：

> 在不训练模型、不增加持久语义状态、不把 Harness 特化成 BC+ ontology 的前提下，通过严格的机制实验、bad-case 分析、有限迭代和 fresh confirmation，使：

\[
Belief \rightarrow Need
\]

这一环真正接近可用于最终端到端闭环。

---

# 0. 仓库与基线

仓库：

`https://github.com/homulillew/Search-ESR`

开始前：

```bash
git fetch --all --prune
```

核验远程：

`origin/experiment/evidence-scope-localization`

当前已知最新 HEAD：

`99202167ab1c693514ef87534ca9f346f0813638`

但不得直接假定它仍然最新。

必须读取远程实际 HEAD。

创建新分支，例如：

```text
experiment/belief-to-need-convergence
```

如果存在则增加明确 suffix。

---

# 1. 冻结当前架构边界

Persistent semantic state 不变：

\[
\boxed{
Belief_t =
(Q,\ Claims_t,\ Hypothesis_t)
}
\]

其中：

- `Original Question Q`：不可变研究目标；
- `Verified Claims`：已有直接证据支持、值得长期保留的事实；
- `Working Hypothesis`：当前暂定解释或候选，只用于引导研究，不是证据。

不得新增 persistent：

```text
Requirement Map
Constraint List
Progress State
Gap List
Frontier History
Source Preference
Retrieval Scope
Confidence
Candidate Schema
Relation Schema
Need History
```

Workspace、D#/W#、Recent Attempts 仍属于证据访问 / mechanical context，不属于 persistent semantic belief。

---

# 2. Need 的最终接口必须保持通用

Need 继续定义为：

\[
\boxed{
当前最值得解决的一个自然语言研究问题
}
\]

不得把最终 Runtime Need 改成：

```json
{
  "candidate": "...",
  "constraint": "...",
  "relation": "...",
  "requirement_id": "..."
}
```

允许实验 evaluator 使用离线 hard-constraint annotations。

允许 Oracle diagnostic arm 显示一个人工确认的 unresolved semantic gap。

但这些都不是最终 Harness schema。

最终模型输出的 Need 仍必须是自然语言。

例如：

```text
How many seasons did You're the Worst run for?
```

而不是：

```text
constraint_7 = total_seasons < 10
```

---

# 3. 为什么必须重新研究 Belief → Need

历史 Frontier Generation 已经测试过：

\[
Q+Claims+H
\rightarrow
Need/STOP
\]

但当时同时存在几个问题：

1. 模型需要一次完成：
   - 理解 Q；
   - 判断 coverage；
   - 判断 completion；
   - 选择 frontier；
   - phrasing Need。

2. 出现大量：
   - premature STOP；
   - whole-question Need；
   - unsupported-premise Need；
   - stale / already-covered Need。

3. 后续 strict constraint reaudit 发现：

历史 `gold_resolved=true`：

```text
12 occurrences
11 unique Q+Claims states
```

在严格 all-explicit-hard-constraints coverage 下：

\[
\boxed{0/11}
\]

仍然真正 resolved。

因此旧 Frontier 实验使用的部分 closure oracle 过宽。

过去一些被标记为：

```text
invented requirement
over-demand
missed closure
```

的行为，重新审计后实际上是在指出真正未覆盖的 Original Question hard condition。

所以必须在新的 closure semantics 下重新测试：

\[
Belief\rightarrow Need
\]

---

# 4. 当前正确的理论目标

不是：

```text
Find one explicit BC+ constraint.
```

也不是：

```text
Generate the best search query.
```

更通用的目标是：

> 比较 Original Question 和当前 Verified Claims，结合 Working Hypothesis 的暂定性质，找到一个尚未解决、能够实质推进原问题、且适合作为下一步研究对象的局部不确定性，并把它表达成一个自然语言 Need。

即：

\[
\boxed{
Need_t = F(Q,C_t,H_t)
}
\]

其中：

\[
H_t
\]

可以帮助 Need 具体化。

但是：

\[
H_t
\]

不能作为 Claim 使用，也不能降低 Original Question 的证明要求。

---

# 5. 一个核心原则

必须区分：

\[
CandidateConfidence
\]

与：

\[
ConstraintCoverage
\]

候选很像答案：

```text
H = X
```

不能推出：

```text
Original Question 中关于 X 的其他条件已成立
```

所以：

\[
\boxed{
Hypothesis可以帮助形成问题，
但不能自动解决问题。
}
\]

例如：

Working Hypothesis：

```text
The series may be You're the Worst.
```

如果总季数尚未有 Claim：

合理 Need：

```text
How many seasons did You're the Worst have?
```

而不能：

```text
resolved=true
```

---

# 6. 本轮不要首先追求 STOP

本轮主要目标首先是：

\[
\boxed{
Unresolved\ Belief \rightarrow Valid\ Need
}
\]

原因：

历史 fully-covered real states 很少。

如果强行为 STOP 构造大量人工 completed bank，会混入新的 evaluation artifact。

因此 Primary Bank 以明确 unresolved states 为主。

Closure 只用少量独立 control。

如果真实 full-coverage controls 不足：

必须明确报告：

```text
Need generation validated;
final closure decision remains incompletely validated.
```

不得为了“完整实验”合成人工 easy closure 样本并冒充真实轨迹。

---

# 7. Primary Need 的通用有效性定义

一个 Need 是 valid，当且仅当它同时满足：

## Relevance

回答这个 Need 会实质推进 Original Question。

## Unresolvedness

当前 Verified Claims 尚未已经回答它。

## Groundedness

Need 中作为前提使用的事实具有正确 epistemic status。

特别是：

- 可以测试 Working Hypothesis；
- 不可以把 Working Hypothesis 当作 Verified Claim；
- 不可以把 Original Question 中的描述条件直接偷渡成 Candidate fact。

## Atomicity

Need 应该主要解决一个局部研究不确定性。

不能重新复述整个 Original Question。

## Actionability

Need 应当可以合理通过研究、检索、阅读或证据获取来解决。

---

# 8. BC+ strict constraint 只作为 evaluator

对于 BC+ states：

离线 evaluator 可以使用：

```text
HARD_CONSTRAINT
REQUESTED_RELATION
NON_BINDING_CONTEXT
AMBIGUOUS
```

分类。

这些来自前序 strict constraint audit。

但 Primary runtime prompt 不应告诉模型：

```text
select hard_constraint C7
```

模型仍然只看到：

```text
Original Question
Verified Claims
Working Hypothesis
```

BC+ 的 hard constraints 用来判断：

> Need 是否真的对应一个尚未解决的 Original-Question requirement。

不是 Runtime ontology。

---

# 9. Stage N0：重新构建 Need Evaluation Bank

必须至少构建四类 bank。

---

# 10. U-Primary：真实 unresolved states

这是正式主 bank。

目标：

```text
>= 36 states
>= 12 qids
```

如果真实独立状态不足，使用全部 eligible states，并明确报告。

优先来源：

- Goal Residual 历史 checkpoints；
- Frontier Generation；
- Dynamic Progress；
- Asymmetric Progress；
- Candidate Discovery / Verification；
- Evidence Scope Localization；
- 其他真实 archived research states。

不能使用：

```text
模型凭空生成的 Claims
人工伪造候选
人工伪造 evidence
```

每个 state 必须由真实历史 Claims/Hypothesis 组成。

---

# 11. U-Primary 必须分层

至少覆盖：

### U1 — No Hypothesis

```text
H = empty
```

需要继续 candidate / explanation discovery。

### U2 — Weak Hypothesis

有 provisional candidate，但 evidence 很弱。

主要测试：

> Need 是否把 H 当作需要测试的方向，而不是事实。

### U3 — Strong Hypothesis + Multiple Gaps

候选很强，但 Original Question 仍有多个未覆盖条件。

测试：

> 是否选择任意一个有效局部 frontier。

### U4 — Strong Hypothesis + Exactly One Material Gap

这是最关键 stress set。

候选几乎已经锁定，只剩一个明确未覆盖条件。

主要测试：

\[
StrongCandidate
\not\Rightarrow
PrematureClosure
\]

目标至少：

```text
>= 8 states
```

如果真实状态不足，使用全部。

### U5 — Covered-condition trap

某条件过去是 gap，但现在 Claims 已经补上。

测试模型是否 stale 重查。

### U6 — Contradicted / stale candidate

当前 Claims 已经与某 Working Hypothesis 存在明显 incompatibility，或历史 transition 尚未清理。

测试：

> 是否继续围绕已经失效的候选研究。

### U7 — Historical bad frontier

包含过去真实出现过：

```text
whole-question Need
unsupported-premise Need
premature STOP
over-broad Need
stale Need
```

的状态。

这些进入 Challenge，不进入 fresh primary gate。

---

# 12. Freshness 原则

必须区分：

```text
Fresh Primary
Challenge
Exploration
Confirmation
```

过去已经反复人工分析的：

```text
q580
q1094
q435
q311
q186
```

以及其他明确历史 bad cases：

原则上不得成为 Fresh Primary 的主要来源。

它们可以：

- Challenge；
- mechanism illustration；
- exploration。

Fresh gate 必须尽可能使用未被当前 Need prompt 设计显式针对的 states。

---

# 13. Stage N1：Paired Belief-Delta Bank

这是本轮必须新增的 diagnostic。

目标：

\[
\boxed{
Need是否真正依赖Belief变化
}
\]

构建：

```text
>= 12 pairs
```

每 pair 来自真实 supported evidence。

---

# 14. Coverage Delta Pair

State A：

```text
Q
Claims C
Hypothesis H
```

存在一个明确 unresolved relation：

```text
g
```

State B：

只比 A 多一个真实 supported Claim：

```text
c_g
```

并且：

\[
c_g
\]

足以覆盖 g。

其他内容保持不变。

理想行为：

State A：

Need 可以研究 g。

State B：

不能继续把 g 作为 Need。

必须：

- 转向其他 unresolved issue；或
- 如果严格 fully covered，结束。

这直接测试：

\[
Need=f(Q,Claims,H)
\]

而不是：

\[
Need=f(Q)
\]

---

# 15. Hypothesis Delta Pair

在可能的真实 states 中构造：

State A：

```text
H = empty
```

State B：

Claims 相同，但：

```text
H = provisional candidate X
```

理想行为：

B 的 Need 可以利用 X 形成更具体的问题。

但是不能产生新的 unsupported premise。

例如：

A：

```text
Which series satisfies the remaining season-count clue?
```

B：

```text
How many seasons did X have?
```

而不是：

```text
Which episode of X contains the required event?
```

如果“X contains required event”尚未有证据。

---

# 16. Challenge Bank

必须重新包含历史典型 bad cases。

至少包括：

```text
q580
q1094
q435
q311
q186
```

以及其他历史：

- premature STOP；
- whole-question Need；
- candidate premise promotion；
- stale frontier；
- broad bundled Need。

Challenge 不改变 Primary Gate。

只用于：

> 是否修复已知 failure mechanism。

---

# 17. 多路径实验设计

第一轮必须比较几个**理论上不同**的方案。

不是多个措辞近似 prompt。

---

# 18. Path P0 — Historical Direct

作为 baseline。

目标：

\[
Q+C+H\rightarrow Need
\]

Prompt 尽量接近旧 Direct Frontier。

不要额外加入 strict coverage reasoning。

输出仅：

```json
{
  "decision": "research",
  "need": "..."
}
```

Primary U-bank 已知 unresolved，所以 P0 不允许 STOP。

这样隔离 Need generation。

---

# 19. Path P1 — Coverage-Aware Natural Need

这是最重要候选方案。

核心 prompt：

```text
You are choosing the next research question.

The Original Question defines the research goal.

Verified Claims are the only established facts.

The Working Hypothesis is provisional. It may help you formulate a concrete research question, but it is not evidence and must not be treated as established fact.

Before proposing the next research question, compare the Original Question against the Verified Claims.

Identify one uncertainty that is still genuinely unresolved and whose resolution would materially advance the Original Question.

Do not research something already established by the Verified Claims.

Do not assume that a description in the Original Question is already true of the Working Hypothesis.

Do not treat a strong-looking candidate as proof that the remaining conditions are satisfied.

Choose one focused research question rather than restating the whole Original Question.

The research question should be directly investigable and should not bundle multiple independent uncertainties unless they cannot meaningfully be separated.

Return only one natural-language research question.
```

不要出现：

```text
hard constraint
constraint ID
candidate verification mode
```

等 BC+ 专属术语。

---

# 20. Path P2 — Coverage-Aware + Internal Candidate Check

仍然是单次模型调用。

不输出中间 reasoning。

在 P1 基础上增加一个内部检查步骤：

```text
Before finalizing your Need, silently test the candidate Need against three questions:

1. Is this question already answered by Verified Claims?
2. Does this question assume any fact that is only present in the Original Question or Working Hypothesis but not established by Claims?
3. Is this the smallest useful research uncertainty, rather than a restatement of several unresolved parts?

If the candidate Need fails any check, revise it before returning the final Need.
```

输出仍只有：

```json
{
  "decision": "research",
  "need": "..."
}
```

不能输出 self-check。

目的：

> 测试一个最小的 generate→check→revise 是否能够解决 stale / premise promotion / broadness。

---

# 21. Path P3 — Ephemeral Progress → Need

这是唯一允许的双调用方案。

它不是新 Persistent State。

也不是独立 Verifier。

同一个 base model，不同短 prompt。

---

## P3-A：Ephemeral Progress

输入：

```text
Q
Claims
Hypothesis
```

输出：

```json
{
  "resolved": false,
  "unresolved_issue": "..."
}
```

Primary U-bank 已知 unresolved：

所以必须：

```text
resolved=false
```

这里的 `unresolved_issue`：

- 只描述当前缺失的一个问题；
- 不需要写成搜索 query；
- 不持久化；
- 下一步调用后丢弃。

Prompt 应强调：

```text
Describe one unresolved uncertainty in the Original Question that is not established by Verified Claims.

The Working Hypothesis is provisional and cannot itself satisfy a missing condition.

Do not propose a search query.
Do not restate the full Original Question.
Do not introduce facts that are not established.
```

---

## P3-B：Need Formulation

输入：

```text
Q
Claims
Hypothesis
Ephemeral unresolved_issue
```

任务：

> 把这个 unresolved issue 转成一个单一、自然、可研究的问题。

输出：

```json
{
  "decision": "research",
  "need": "..."
}
```

目的：

测试：

\[
Belief
\rightarrow
Progress
\rightarrow
Need
\]

是否比一次直接调用稳定。

注意：

Progress 仍然是：

```text
derived control state
```

不是 Persistent State。

---

# 22. Path P4 — Oracle Gap Diagnostic

不是部署候选。

只用于诊断。

模型收到：

```text
Q
Claims
Hypothesis
```

以及离线 evaluator 提供：

```text
One confirmed unresolved issue:
...
```

例如：

```text
It is not yet established how many seasons the provisional series had.
```

然后只要求：

> 写一个安全、局部、自然语言 Need。

如果：

```text
P4 高
P1/P2/P3 低
```

说明问题主要在：

\[
Belief\rightarrow unresolved\ issue
\]

而不是 Need phrasing。

如果：

```text
P4 也低
```

说明：

\[
unresolved\ issue\rightarrow Need
\]

本身仍然有问题。

P4 不进入 production selection。

---

# 23. 第一轮调用原则

第一轮建议：

```text
Fresh development bank:
24–30 states
>=10 qids
```

所有 P0–P4 使用相同 states。

不要一开始就在所有 36+ primary states 上做大规模 prompt sweep。

先做机制开发。

每 arm：

```text
1 sample / state
```

不 best-of。

不 retry semantic failure。

transport/schema failure 保留。

---

# 24. Need Rubric

每个输出必须离线人工 / frozen rubric 评价：

## V — Valid frontier

Need 是否指向一个真正 unresolved 且 materially useful 的问题。

多个有效 frontier 均允许。

不得要求 exact match researcher wording。

## S — Stale

Need 是否已经被 Claims 回答。

## P — Unsupported premise

Need 是否把：

- Original Question condition；
- Working Hypothesis；
- related evidence；

强化成尚未建立的事实。

## W — Whole-question / overly broad

是否基本重述整题，或捆绑多个可分离研究问题。

## I — Irrelevant

回答后不会实质推进 Original Question。

## H — Hypothesis misuse

是否因为 H 很强就跳过未覆盖问题，或把 H 当已验证 identity。

## A — Actionability

是否形成可合理研究的问题。

---

# 25. Primary Composite Validity

一个 Need 计：

```text
STRICT_VALID = true
```

当：

```text
V = true
S = false
P = false
W = false
I = false
H = false
A = true
```

必须同时报告每个错误维度。

不能只报告 composite。

---

# 26. 特殊子集指标

必须单独报告：

### Strong-H / One-Gap Recall

在：

```text
strong hypothesis
+
exactly one remaining valid gap
```

的 states 中：

Need 是否重新激活该 gap。

这是本轮最重要指标之一。

---

### Covered-Delta Sensitivity

对于 Coverage Delta Pair：

State A 是否允许目标 gap Need；

State B 加入 covering Claim 后是否不再选择该 gap。

Pair 正确必须两边都正确。

---

### Hypothesis Delta Safety

增加 H 后：

Need 可以更具体，

但 unsupported premise rate 不得提高。

---

### No-H Discovery Validity

没有 H 时：

Need 是否仍然能形成合理 candidate / explanation discovery frontier。

---

# 27. 第一轮方案选择不能只看总分

Production candidate 的选择采用以下优先顺序：

1. `STRICT_VALID`
2. unsupported premise
3. stale Need
4. Strong-H / One-Gap
5. Belief-Delta sensitivity
6. whole-question rate
7. call/token cost

不能因为某方案便宜但 premise errors 多就选。

不能因为某方案在 challenge 全修复而在 fresh 较差就选。

---

# 28. 第一轮建议门槛

冻结 denominator 后转成整数 gate。

建议目标：

```text
STRICT_VALID >= 85%
unsupported premise <= 5%
stale Need <= 5%
whole-question/bundled <= 10%
Strong-H / One-Gap >= 90%
Coverage Delta Pair correctness >= 85%
No-H validity >= 80%
```

这是进入 Fresh Confirmation 的门槛。

不是最终 PASS。

---

# 29. P3 成本要求

P3 是双调用。

只有在：

```text
P3 strict validity
```

比最佳单调用方案至少高：

```text
>= 8 percentage points
```

或者明显修复一个单调用无法解决的关键 failure mechanism，

才值得作为最终候选。

否则优先简单单调用方案。

目标仍然是：

> 最小可靠 Harness。

---

# 30. 如果第一轮没有方案通过

这是整个提示词最重要的部分。

不要停止。

也不要立即写“Need generation 失败”。

进入：

# BAD-CASE ANALYSIS LOOP

---

# 31. Bad-case 分析必须逐例读取真实输入

对最佳候选方案所有失败 case：

读取：

```text
Original Question
Claims
Hypothesis
Need output
offline valid-gap set
historical context
```

不得只根据 aggregate metrics 猜原因。

---

# 32. 必须把失败归入机制类别

至少考虑：

### B1 — Coverage omission

真实 unresolved issue 存在，但模型没有意识到。

典型：

> strong candidate 后遗漏最后一个条件。

### B2 — Stale coverage

Claims 已经解决，但模型还在查。

### B3 — Hypothesis promotion

把 H 当成事实。

### B4 — Question-condition promotion

把 Original Question 中描述的条件直接绑定到 H。

### B5 — Broad frontier

知道缺口但 Need 捆绑太多。

### B6 — Wrong frontier priority

选择的研究问题虽然 unresolved，但实际不推进目标或价值很低。

### B7 — Phrasing failure

内部 gap 基本正确，但写成不安全 / 不可检索的问题。

### B8 — Discovery collapse

没有 H 时无法形成合理 research frontier。

### B9 — Closure leakage

Primary 明知 unresolved，却表现出“已经完成”的语义。

### B10 — State interpretation conflict

Claims 之间存在 conflict / scope nuance，导致 coverage 判断错误。

允许新增 category。

但必须给真实例子。

---

# 33. 选择主导失败机制

每次迭代只允许选择：

\[
\boxed{
一个主要机制
}
\]

作为下一轮干预目标。

选择依据：

- 失败数；
- 严重度；
- 是否跨 qid；
- 是否影响闭环；
- 是否可由 Harness/prompt-level 修复。

不能为了提高 aggregate score 同时加入五条针对性规则。

---

# 34. 新方案生成规则

GPT-6 必须先写：

```text
Observed mechanism:
...

Why existing prompt failed:
...

Minimal intervention:
...

What should improve:
...

What could regress:
...
```

然后才能创建新的 prompt variant。

新 variant 只能改变一个核心机制。

例如：

### coverage miss 主导

可以增强：

```text
Compare Q against Claims before choosing the Need.
A condition remains unresolved unless Claims actually establish it.
```

### hypothesis promotion 主导

可以增强：

```text
A Need may investigate the Working Hypothesis, but must phrase uncertain relations as questions rather than presuppositions.
```

### stale Need 主导

可以增强：

```text
Before output, verify that current Claims do not already answer the proposed Need.
```

### broadness 主导

可以增强：

```text
Choose the smallest independently researchable uncertainty.
```

不得同时全加。

---

# 35. 允许探索的架构空间

因为本项目明确：

```text
NO TRAINING
HARNESS / PROMPT ONLY
```

允许探索：

- 单调用 prompt；
- 同模型 ephemeral Progress → Need；
- 单调用 internal self-check；
- context ordering；
- 是否给 H；
- 是否给 short Recent Attempts；
- 是否让 Progress 只看 Q+Claims，再由 Need formulation 看 H；
- 是否让 Need generator看到 Workspace metadata；
- 是否加入一个短的 already-covered guard。

但不允许：

```text
finetuning
RL
new learned retriever
persistent requirement map
external verifier model
hard-coded semantic BC+ parser
candidate/constraint state machine
```

---

# 36. 特别值得探索的一个路径：Progress 不看 H

如果 bad case 显示：

> Working Hypothesis 导致 coverage 被污染，

允许探索：

第一步：

\[
Progress=f(Q,Claims)
\]

不看 H。

只回答：

> 当前还缺什么？

第二步：

\[
Need=f(Progress,H)
\]

此时 H 只用于：

> 把 research question 具体化。

这可能形成一个很干净的职责隔离：

\[
\boxed{
Claims决定coverage；
Hypothesis帮助formulate action。
}
\]

这不是默认必须做。

只有 bad-case evidence 指向 H contamination 时才实验。

---

# 37. Exploration Bank

机制探索使用 failure-enriched bank。

建议：

```text
<=16 states
<=8 qids
```

可以包含历史 challenge。

目的是：

> 验证机制是否被修复。

不能作为最终 PASS。

每轮 exploration 最多比较：

```text
baseline best
vs
one new variant
```

如果必要，可保留 Oracle diagnostic。

禁止多 prompt sweep。

---

# 38. Fresh Confirmation

如果一个新方案在 exploration 明显修复目标机制：

必须使用新的：

```text
fresh confirmation bank
```

建议：

```text
>=24 states
>=8 qids
```

不能包含：

- 本轮用于设计 intervention 的 failure cases；
- 直接写进 prompt 的历史 examples；
- 被多次人工分析的 challenge。

如果没有足够 fresh historical states：

必须明确停止并报告：

> evidence exhausted; cannot claim confirmation.

不得重复使用 challenge 冒充 fresh。

---

# 39. Confirmation PASS

建议：

```text
STRICT_VALID >= 90%
unsupported premise <= 5%
stale Need <= 5%
whole-question <= 5%
Strong-H / One-Gap >= 90%
Coverage Delta Pair >= 90%
No-H validity >= 85%
```

并且：

```text
>=8 qids
```

无单一 qid 主导。

---

# 40. “NEAR PASS” 定义

如果无法达到正式 PASS，但满足：

```text
STRICT_VALID >= 85%
unsupported premise <= 5%
stale Need <= 7.5%
Strong-H / One-Gap >= 90%
Coverage Delta >= 85%
```

并且剩余失败：

- 集中在一个明确机制；
- 没有系统性 premature closure；
- 没有系统性 hypothesis promotion；
- 没有大规模 whole-question regression；

则可以标：

```text
NEAR_PASS
```

这意味着：

> Belief → Need 已足够成熟，可以进入小规模 end-to-end confirmation，同时继续记录该尾部 failure。

不得把 NEAR_PASS 写成完全解决。

---

# 41. Iteration Policy

GPT-6 不应在第一次 gate fail 后停下。

必须按：

```text
Run
→ Review bad cases
→ Identify dominant mechanism
→ Design one minimal intervention
→ Exploration
→ Fresh confirmation
```

循环。

但为了避免无限过拟合：

最多：

```text
4 major intervention cycles
```

或者直到：

```text
没有新的fresh bank可用
```

二者任一先发生则停止。

如果 4 轮后仍未 NEAR_PASS：

必须给出：

```text
best achieved design
remaining dominant mechanism
why further prompt tuning is unlikely to help
what architectural question should be revisited
```

不得为了“必须成功”继续在同一 bank 上调 prompt。

---

# 42. 每轮必须 append-only

每次实验必须保留：

```text
ROUND_0
ROUND_1
ROUND_2
...
```

包括：

```text
prompt
inputs
outputs
metrics
bad-case review
hypothesis
gate
decision
```

不得覆盖旧结果。

每轮新 intervention 必须在 API 调用前 commit / freeze。

---

# 43. 不允许事后改 gold 来过 gate

如果 bad-case review 发现 evaluator 真有错误：

必须：

1. 保留旧 label；
2. 新建 append-only correction；
3. 解释为什么；
4. 同时报告 original metric 和 corrected sensitivity。

不能因为模型输出“看起来合理”就即时重写 gold。

---

# 44. Closure Control

当 Need Primary 已接近通过后，再运行 Closure Control。

Closure 不应一开始和 Need 混在一起。

构建：

```text
strict fully-covered states
```

只使用：

- 真实历史 full-coverage；
- 或由真实 supported Claims 合并得到、且逐 Claim 有来源 provenance 的 evidence-complete control。

人工 assembled controls 必须单列。

不能与自然历史 state 混在一个 denominator。

---

# 45. Closure Prompt

使用最终候选 Need policy，

允许：

```json
{
  "decision": "resolved",
  "need": ""
}
```

只有当：

> Original Question 已不存在仍需研究的 material uncertainty。

对于 BC+：

离线 strict evaluator 要求：

```text
all explicit target-defining hard conditions
+
requested final relation
```

已由 Claims 支持。

Hypothesis 不算 coverage。

---

# 46. Closure 指标

```text
false resolved
missed resolved
correct unresolved
correct resolved
```

最重要：

\[
PrematureResolvedRate
\]

目标：

```text
<=5%
```

尤其历史 q580/q1094 类 strong-candidate states：

必须单列 Challenge。

---

# 47. 最终小型 autonomous simulation

只有达到：

```text
NEAR_PASS
```

或 PASS 后才运行。

不要直接进入真实 Search end-to-end。

先做离线 transition simulation。

对一批 state：

1. 生成 Need；
2. evaluator 给出历史真实的 matching Claim transition；
3. 更新 Claims；
4. 再生成 Need；
5. 看 Need 是否随着 Belief 正确移动。

目的：

\[
\boxed{
Need sequence follows Belief evolution
}
\]

而不是：

> 同一类 gap 一直循环。

---

# 48. 最终 held-out end-to-end eligibility

只有同时满足：

### Belief → Need

NEAR_PASS/PASS。

### Need → Evidence

已有 Evidence Scope 实验没有新的系统性 regression。

### Evidence → Belief

沿用 U1，且 target Evidence → Claim 条件性能保持。

才允许下一阶段：

\[
Belief
\rightarrow
Need
\rightarrow
Search/Find/Open
\rightarrow
Observation
\rightarrow
Belief'
\]

真实多轮闭环。

---

# 49. 本轮不允许顺手优化 Retrieval

这轮 Primary 不运行 Search。

Need 先离线评价。

最新 Evidence Scope 已经说明：

```text
v3a Search/Open fresh K: 10/10
```

以及：

```text
Find has tail-case value but no global-first advantage.
```

因此不要因为某个 Need “看起来搜索困难”就在本轮改 Search/Find。

Need 的目标只是：

> 它是否是正确的下一研究问题。

---

# 50. 本轮也不改 U1

当前 U1 已经行为上实现：

\[
Need
\ OR
OriginalQuestionRelevance
\]

历史 audit：

```text
off-Need full condition immediate admission:
30/38 = 78.9%

deduplicated eventual:
30/36 = 83.3%

components included:
67/77 = 87.0%
```

虽然仍有 admission recall 和 unsupported strengthening 问题，

但这不是本轮变量。

冻结 Writer。

---

# 51. 最终报告必须回答

必须回答：

1. 旧 Direct Frontier 在新的 strict semantics 下到底多差？
2. Coverage-aware one-call 是否显著改善？
3. Internal self-check 是否有边际价值？
4. Ephemeral Progress → Need 是否比 one-call 更可靠？
5. Oracle gap → Need 的上限是多少？
6. 主要失败在 coverage detection 还是 Need phrasing？
7. Strong-H + one-gap 能否稳定重新激活最后一个缺口？
8. 加入 covering Claim 后 Need 是否正确改变？
9. Working Hypothesis 是否导致 unsupported premise？
10. 无 H 时能否产生有效 discovery Need？
11. 模型是否仍然生成 whole-question Need？
12. 模型是否仍然重复 already-covered Need？
13. bad-case exploration 找到了哪些可复现机制？
14. 哪个 intervention 真正在 fresh confirmation 上复现？
15. 最终最佳方案是 one-call 还是 ephemeral two-call？
16. 是否需要新增 persistent state？
17. 是否需要 Requirement Map？
18. 是否需要 separate verifier？
19. Belief → Need 达到 FAIL / NEAR_PASS / PASS 哪一级？
20. 是否有资格进入最终 held-out end-to-end loop？

---

# 52. 最终架构偏好

除非实验强烈反驳，否则优先保持：

\[
\boxed{
Persistent:
Q + Claims + Hypothesis
}
\]

派生：

\[
\boxed{
Need =
one natural-language research question
}
\]

而不是新增 ontology。

如果双调用 Progress → Need 明显优于单调用：

允许最终 Harness 使用：

```text
ephemeral Progress
```

但它必须满足：

- 不持久化；
- 不形成 Requirement Map；
- 不增加 semantic state；
- 下一次 Claims/H 改变后重新计算。

这仍然符合：

\[
\boxed{
Persist epistemic state,
derive control state.
}
\]

---

# 53. 最重要的实验哲学

不要要求模型找到“研究者唯一指定的 frontier”。

当多个未解决问题都合理时：

任何一个：

```text
relevant
unresolved
grounded
atomic
actionable
```

的 Need 都是正确的。

我们研究的不是：

> 模型能否复刻人工研究顺序。

而是：

> 模型能否持续提出不会浪费动作、不会偷渡事实、能够真正减少剩余研究不确定性的下一问题。

---

# 54. 最终目标

本轮最终希望证明：

\[
\boxed{
(Q,C_t,H_t)
\rightarrow
N_t
}
\]

具有以下性质：

\[
N_t
\notin
AlreadyKnown(C_t)
\]

\[
N_t
\text{ materially advances }Q
\]

\[
Premises(N_t)
\subseteq
Verified(C_t)
\cup
ProperlyMarkedHypothesis(H_t)
\]

并且当：

\[
C_t\rightarrow C_{t+1}
\]

发生真实 Belief 更新后：

\[
N_{t+1}
\]

会相应改变。

也就是：

\[
\boxed{
Need真正由当前Belief驱动，
而不是由Original Question机械驱动。
}
\]

只有做到这一点：

\[
Belief
\rightarrow
Need
\rightarrow
Evidence
\rightarrow
Belief'
\]

才真正构成可持续研究闭环。

---

# 55. 最终停止条件

不要因为第一次失败就停止。

不要因为 challenge 被修复就宣称成功。

不要为了成功不断调同一批样本。

继续：

```text
分析
→提出机制假设
→最小干预
→探索
→新的fresh confirmation
```

直到：

```text
PASS
```

或者至少：

```text
NEAR_PASS
```

且剩余 bad cases 已收敛为一个明确的长尾机制。

如果 fresh evidence 用尽或四轮机制干预后仍未 NEAR_PASS：

必须停止继续 prompt tuning，并明确指出：

> Belief → Need 的哪个基本假设仍然不成立。

研究目标不是强行得到好看的数字。

研究目标是：

\[
\boxed{
真正知道这一环什么时候可靠，
为什么可靠，
以及剩下哪里不可靠。
}
\]