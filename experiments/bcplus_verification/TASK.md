你现在负责 Search-ESR 下一阶段核心研究：

# BC+ Candidate Discovery vs Constraint Verification
# 候选发现与约束验证的不对称性实验

仓库：

`https://github.com/homulillew/Search-ESR`

当前研究基线：

`experiment/asymmetric-progress-closure-audit`

开始前必须：

```bash
git fetch --all --prune
```

核验远程：

`origin/experiment/asymmetric-progress-closure-audit`

的最新 HEAD。

当前已知上一轮完成研究时 HEAD 为：

`453161c2d2335416d4f439f9419e85c2266658b5`

但不得直接假定它仍是最新值，必须以远程实际 HEAD 为准。

创建新分支，例如：

`experiment/bcplus-discovery-verification`

如果已存在则使用明确 suffix。

继续使用当前冻结的：

- `deepseek-flash`
- provider
- Search / Find / Open
- Workspace
- U1 selective Writer
- Verified Claims / Working Hypothesis schema

除本实验明确允许修改的 prompt / experiment runtime 外，不修改已有生产组件。

---

# 0. 本轮研究目标

前序研究已经逐步发现：

1. Search / Find / Open 本身不是当前主要瓶颈；
2. Selective Claim Admission 可以显著降低状态膨胀；
3. Deferred Recovery 表明，只要未来 Need 被正确重新激活，普通 Search 有能力重新获得过去未进入 Claims 的证据；
4. 直接：

\[
Q+Claims+Hypothesis \rightarrow Need/STOP
\]

承担了过多推理职责，Frontier Generation 表现不稳定；

5. 将：

\[
Q+Claims \rightarrow Progress
\]

独立出来后，completion judgment 明显改善；

6. Single-relation Progress（上一轮 L1）进一步改善 blocker 粒度；

7. 单独 Closure Audit 没有表现出额外价值，反而容易过度拒绝真实 closure；

8. 最近重新审视 BC+ / BrowseComp 类任务后，需要修正此前的一个假设：

> 不能因为当前候选已经非常强，就自动跳过 Original Question 中尚未验证的显式约束。

在开放世界中：

```text
当前只发现 Candidate A
```

不能推出：

```text
不存在 Candidate B
```

尤其可能存在：

```text
A 和 B 满足前 n-1 个约束，
只在最后一个约束上不同。
```

因此：

\[
CandidateConfidence
\neq
ConstraintCoverage
\]

---

# 1. 当前新的任务理解

BC+ 类问题可以抽象为：

\[
Q=\{C_1,C_2,\ldots,C_n,R\}
\]

其中：

- \(C_i\)：Original Question 明确用于描述目标实体的约束；
- \(R\)：用户最终要求回答的关系。

目标实体 \(x\) 应满足：

\[
C_1(x)\land C_2(x)\land\cdots\land C_n(x)
\]

并最终建立：

\[
R(x)=y
\]

候选很像答案，只代表：

\[
H_t=x
\]

是一个有价值的 Working Hypothesis。

它不意味着：

\[
C_i(x)
\]

已经成立。

---

# 2. 一个关键区别

必须区分：

## Discovery redundancy

一些约束可能对“找到候选”已经没有额外帮助。

例如：

```text
C1 + C2 + C3
```

可能已经足以让模型找到 Candidate X。

但是这不等于：

## Verification redundancy

```text
C4 / C5 / C6
```

可以被当作已经成立。

一个显式约束只有在：

1. 当前 Verified Claims 直接支持它；或
2. 当前 Verified Claims 确实逻辑蕴含它；

时才能算 covered。

禁止因为：

```text
candidate looks obvious
```

而视为 covered。

---

# 3. 当前最重要的新假设

BC+ 的一个核心性质可能是：

\[
\boxed{
Candidate\ Discovery
\text{ difficult}
}
\]

但：

\[
\boxed{
Candidate\ Conditioned\ Verification
\text{ relatively easy}
}
\]

也就是：

> 从开放空间中找出“是哪一个实体”很难；
>
> 但一旦给定 Candidate X，验证“X 是否满足某一个具体约束”通常容易得多。

如果这一性质真实存在，则后续 Agent 不需要：

- 跳过未验证约束；
- 使用复杂 Closure Verifier；
- 构造 Persistent Requirement Graph。

而可以采用：

```text
自由发现候选
→
候选出现
→
逐步验证尚未覆盖的显式约束
→
候选失败则清除 Hypothesis
→
继续发现新候选
→
全部约束覆盖后结束
```

---

# 4. 本轮核心 Research Questions

必须分别回答：

## RQ1

BC+ 中：

\[
Verify(C_i\mid Candidate)
\]

是否真的比：

\[
Discover(Candidate\mid Q)
\]

显著容易？

---

## RQ2

给定正确候选后：

> 当前尚未进入 Claims 的显式约束，是否可以通过低成本 Search / Find / Open 被稳定验证？

---

## RQ3

给定错误候选后：

> 一个不满足的显式约束，是否可以被低成本证据快速击穿，从而使 Working Hypothesis 被清除？

---

## RQ4

如果 RQ1–RQ3 成立：

> 是否可以把 Frontier 从“自由生成研究方向”简化成：

```text
没有可靠候选：
    继续 Candidate Discovery

有 Working Hypothesis：
    优先验证一个尚未覆盖的 Original-Question constraint
```

---

## RQ5

这种结构是否比：

```text
Q + Claims + Hypothesis
→ free-form Need
```

更可靠、更便宜、更少产生 unsupported premise？

---

# 5. 本轮明确不研究什么

本轮不继续优化：

```text
Closure Audit
Verifier
Double Light
Materiality Audit
FULL decomposition every turn
```

不新增：

```text
verify() tool
recover() tool
planner tool
requirement graph
persistent progress
persistent checklist
confidence score
semantic router in Harness
```

本轮首先验证任务结构是否成立。

---

# 6. 非常重要：不要持久化 Requirement Map

离线实验评价允许冻结：

```text
Hard Constraint annotations
```

但它们只能作为：

- gold labels；
- experiment selection；
- offline review。

绝不能进入正常 runtime State。

Persistent semantic State 继续只有：

\[
\boxed{
Q + VerifiedClaims + WorkingHypothesis
}
\]

---

# 7. Stage S0：重新审计 BC+ Question Semantics

在进行新模型调用前，先重新审计一批真实 BC+ questions。

目标不是设计 runtime checklist。

目标是确认：

> Original Question 中哪些信息真正构成候选必须满足的显式约束。

---

# 8. S0 样本

优先覆盖前序全部主要 qids：

```text
177
186
311
387
435
517
546
580
1034
1094
```

如果仓库有更多适合的真实 BC+ qid，可以机械扩充。

目标：

```text
>=20 questions / question variants if available
>=10 qids
```

如果实际 question 数不足，使用全部可用，明确报告限制。

---

# 9. S0 Constraint Classification

只根据 Original Question 本身，将语义单元分为：

### HARD_CONSTRAINT

如果该命题为 false：

> 候选就不再满足题目对目标的描述。

例如：

```text
series has fewer than ten seasons
person was born in stated range
match contains specified event
article relation has required date/scope
```

### REQUESTED_RELATION

用户最终要求输出或回答的事实。

### NON_BINDING_CONTEXT

纯语言背景、解释、非限定性上下文。

### AMBIGUOUS

无法可靠判断是不是 hard constraint。

---

# 10. Constraint 分类规则

禁止：

```text
每一个从句 = 一个 constraint
```

禁止因为：

```text
candidate already obvious
```

把一个 HARD_CONSTRAINT 降级成 NON_BINDING。

约束性质主要由：

\[
Q
\]

决定，不由当前 candidate confidence 决定。

如果存在真正语义歧义：

标：

```text
AMBIGUOUS
```

并从 Primary constraint-verification bank 排除。

保留用于 sensitivity。

---

# 11. 重新审计历史 resolved labels

对前两轮曾标为：

```text
gold_resolved=true
```

的状态重新检查：

对于每个 HARD_CONSTRAINT：

\[
Claims\models C_i?
\]

对于 REQUESTED_RELATION：

\[
Claims\models R?
\]

如果存在任意 HARD_CONSTRAINT 未被 Claims 支持：

该状态在新的 strict-constraint 语义下：

```text
not resolved
```

不要修改旧实验文件。

创建新的 audit artifact，例如：

```text
experiments/bcplus_verification/constraint_audit/
```

明确记录：

```text
old_label
strict_constraint_label
reason
```

这一步是重新解释旧结果，不是篡改旧实验。

---

# 12. S0 最重要的输出

必须回答：

1. 历史 `resolved` 状态中，有多少在 strict-all-hard-constraints 标准下仍然 resolved？
2. 有多少历史 “Audit over-demand” 实际上是在要求一个真实 HARD_CONSTRAINT？
3. 最近所谓 materiality disagreement，有多少来自 gold closure 过宽，而不是模型过度保守？
4. BC+ Question 中 hard constraints 的数量分布大概是多少？
5. 明确 constraint 与纯背景信息是否总体容易区分？

---

# 13. Stage S1：验证 Candidate-Conditioned Verification 是否容易

这是本轮最核心实验。

首先构建：

```text
Verification Bank
```

每个 unit 包含：

```text
Original Question
Candidate
One explicit HARD_CONSTRAINT
Current Claims
Gold relation status
Historical provenance
```

Candidate 不进入 Verified Claims。

它只是 Working Hypothesis / test subject。

---

# 14. Verification Bank 类型

至少构建两类。

## V+ Positive Verification

Candidate 是正确候选。

Constraint 对 Candidate 为真。

但是当前 Claims 尚未充分建立该 constraint。

任务：

> 找到证据，使：

\[
Claims\models C_i(candidate)
\]

---

## V− Negative Verification

Candidate 是历史上真实出现过、后来被证据否定或明显不满足条件的 Working Hypothesis。

选择一个真实：

\[
C_j(candidate)=false
\]

或者存在直接 material contradiction 的 constraint。

任务：

> 找到证据证明 Candidate 不满足该 constraint。

最终应：

```text
add contradictory/falsifying Claim
clear Working Hypothesis
```

---

# 15. 禁止构造假的负样本

优先使用：

- historical Working Hypothesis；
- historical candidate paths；
- historical contradictions；
- corpus 中存在真实 refuting evidence。

不要凭研究者想象：

```text
Candidate X probably wrong
```

如果没有可靠 source evidence：

不进入 V− Primary。

---

# 16. Verification Bank 规模

目标：

```text
V+ >= 18
V− >= 12
>= 8 qids total
```

单 qid 不超过约 4 units，除非真实资源不足。

尽量覆盖：

```text
quantity
date
temporal scope
role relation
event binding
article attribution
identity relation
career count
release relation
source-scoped fact
```

---

# 17. Oracle Verification Need

S1 首先不要让模型自己生成 Need。

直接提供冻结的单个 HARD_CONSTRAINT。

例如：

```text
Candidate:
You're the Worst

Constraint to verify:
The series had fewer than ten seasons.
```

目标是隔离：

> “候选条件化以后，这个验证任务本身是否容易？”

不要把 Progress/Frontier 再混进来。

---

# 18. Verification Actor Prompt

使用同一个模型。

核心语义：

```text
You are researching one explicit condition from the Original Question for a provisional candidate.

The Candidate is a Working Hypothesis, not a verified fact.

Your current task is only to determine whether the Candidate satisfies the supplied Constraint to Verify.

Do not research unrelated clues.

Do not assume the constraint is true because the candidate looks likely.

Search for direct evidence about the Candidate and this specific relation.

If evidence supports the constraint, preserve only the exact supported relation.

If evidence contradicts the constraint, treat that as material evidence against the Working Hypothesis.

Do not broaden the task back into the full Original Question.

Choose Search, Find, or Open only as needed.
```

---

# 19. S1 budget

Verification 应该被测试为：

```text
low-budget task
```

建议：

```text
max decisions: 2
max actions / decision: 1
```

即最多：

```text
2 tool actions
```

第一版不要给 Verification 和 Discovery 一样大的 3–5 round budget。

否则“容易验证”假设不可检验。

---

# 20. Verification Writer

继续使用当前 U1 selective Writer。

但 Current Need 必须是：

```text
verify this specific constraint for Candidate
```

从而测试：

\[
Need
\rightarrow
Evidence
\rightarrow
Claim
\]

是否能真正闭合。

禁止人工把检索到的证据写进 Claim。

---

# 21. V+ Success

一个 positive verification 成功，当：

1. 找到 useful evidence；
2. evidence 直接支持目标 constraint；
3. Writer 正确产生 Claim；
4. 不引入 stronger unsupported relation。

核心：

\[
C_i(candidate)
\]

真正进入 Verified Claims。

---

# 22. V− Success

Negative verification 成功，当：

1. 找到 Candidate 与 constraint 不匹配的直接证据；
2. Writer 保存真正的 contradictory / disqualifying Claim；
3. Working Hypothesis 被 clear；
4. 不把 absence of evidence 当作 refutation。

---

# 23. S2：Candidate Discovery Baseline

为了判断 Verification 是否“真的容易”，需要一个 Discovery baseline。

从真实历史状态中选择：

```text
尚无可靠 Working Hypothesis
```

或当前 hypothesis 没有实质 candidate identity support 的 checkpoint。

模型输入：

```text
Original Question
Verified Claims
Recent Attempts
Workspace
```

不给 candidate。

目标：

> 找到一个合理 Working Hypothesis。

---

# 24. Discovery Prompt

继续保持自由：

```text
You are trying to discover a plausible candidate for the Original Question.

Verified Claims are established facts.

There is currently no candidate that should be treated as reliable.

Choose one research uncertainty whose resolution would materially help identify a candidate.

Do not attempt to verify every clue before proposing a candidate.

A candidate may be placed in Working Hypothesis when evidence makes it useful to test, but must not be promoted to a Verified answer without sufficient support.
```

---

# 25. Discovery budget

建议：

```text
max decisions: 3
max actions / decision: 1
```

允许：

```text
3 tool actions
```

这反映 Discovery 本身被假定更困难。

---

# 26. Discovery Success

成功标准不能只是模型“说了一个名字”。

至少要求：

1. 生成正确 benchmark candidate，或一个最终能继续合理验证的真实 candidate；
2. 至少有一条直接来源证据支持 Candidate 作为 Working Hypothesis；
3. 不允许 hallucinated candidate；
4. candidate 不需要此时满足全部 constraints。

报告两个层次：

```text
candidate proposed
correct candidate proposed
```

---

# 27. S1 vs S2 核心比较

不要求做不合理的 IID 显著性结论。

主要比较：

### Goal success

```text
Verification success rate
vs
Discovery success rate
```

### Tool efficiency

```text
actions to first useful evidence
actions to successful semantic update
```

### Search efficiency

```text
useful evidence / Search
irrelevant windows / total windows
```

### Model cost

```text
input
output
reasoning proxy
elapsed
```

### State effect

```text
successful Claim admission
successful Hypothesis set/clear
```

---

# 28. 核心假设 H1

如果观察到类似：

```text
V+ / V− success >= 80–90%
within <=2 actions
```

而 Discovery 在 3 actions 内明显更低，

并且 Verification：

```text
useful evidence rate
higher
queries more specific
less irrelevant evidence
```

则支持：

\[
\boxed{
BC+\ Candidate\ Verification
确实显著容易于 Candidate Discovery
}
\]

不要提前冻结具体百分比为“科学真理”，但必须预注册用于当前实验的整数 gate。

建议根据最终 bank denominator 设置：

```text
V+ success >= 80%
V− success >= 75%
```

并且 Verification 平均 action cost 明显低于 Discovery。

---

# 29. Stage S3：验证 Wrong Candidate 是否能被快速击穿

单独分析 V−。

关键问题不是：

> 模型能不能找到更多不支持 Candidate 的东西。

而是：

> 一个显式 constraint failure 是否足以让 Working Hypothesis 被正确撤销？

重点错误：

```text
candidate commitment bias
```

即：

模型已经有 Working Hypothesis 后，是否会不断合理化 Candidate，而不是接受反证。

---

# 30. S3 需要记录

```text
refuting evidence found
refuting evidence admitted
hypothesis cleared
hypothesis incorrectly retained
contradictory claim ignored
search redirected to unrelated supporting clues
```

如果 wrong candidate 经常：

```text
evidence clearly contradicts
but Hypothesis remains
```

那么 Candidate Verification 架构还有严重确认偏误问题。

---

# 31. Stage S4：Progress → Verification Need

只有 S1/S2/S3 给出正向证据后执行。

此阶段终于重新回到 Frontier。

问题变成：

> 有 Candidate 时，模型能否从 Original Question + Claims 中选择一个尚未覆盖的显式 constraint？

---

# 32. S4 不再问 materiality

Prompt 不应说：

```text
choose a material blocker
```

而应说：

> 找一个 Original Question 明确要求 Candidate 满足、但当前 Verified Claims 尚未建立的条件。

即：

\[
\boxed{
uncovered\ explicit\ constraint
}
\]

---

# 33. S4 Progress Prompt

建议：

```text
You are evaluating research progress for the Original Question.

Verified Claims are the only established facts.

The Working Hypothesis is a provisional candidate and is not itself evidence.

Look at the Original Question and the Verified Claims.

If there is an explicit condition that the target must satisfy but the current Claims do not establish that condition for the Working Hypothesis, return one such uncovered condition.

Do not choose a condition merely because it is interesting.
Do not repeat a condition already established by the Claims.
Do not treat the candidate's apparent plausibility as support for an unverified condition.
Do not bundle several independent conditions together.

If there is no usable Working Hypothesis, indicate that the current frontier is candidate discovery rather than candidate verification.

If every explicit target-defining condition and the requested final relation are supported by Verified Claims, return resolved=true.

Return only one current frontier.
```

---

# 34. S4 Schema

保持尽量简单：

```json
{
  "resolved": false,
  "frontier_type": "discover_candidate",
  "need": "..."
}
```

或者：

```json
{
  "resolved": false,
  "frontier_type": "verify_constraint",
  "candidate": "...",
  "constraint": "...",
  "need": "..."
}
```

或者：

```json
{
  "resolved": true,
  "frontier_type": "resolved",
  "need": ""
}
```

注意：

```text
candidate
```

仍然只是 Working Hypothesis。

不得因 schema 输出而转为 Claim。

---

# 35. 不要持久化 frontier_type

这是当前一次 decision 的派生结果。

Harness 不保存：

```text
mode=verification
```

作为长期 State。

下一轮重新计算。

这样 Candidate 被推翻后，模型自然可以回到：

```text
discover_candidate
```

---

# 36. S4 对照

至少比较：

## D — 旧 Direct Frontier

```text
Q + Claims + Hypothesis
→ free Need / STOP
```

## C — Constraint-aware Frontier

使用新 prompt：

```text
Q + Claims + Hypothesis
→ discover_candidate
or
verify one explicit uncovered constraint
or
resolved
```

---

# 37. S4 指标

```text
Valid frontier
Correct mode semantics
Correct uncovered constraint
Already-covered constraint selected
Unsupported premise
Whole-question Need
Invented constraint
Candidate treated as fact
Premature resolved
```

尤其看：

\[
\boxed{
有 Working Hypothesis 后，
是否能稳定产生 candidate-conditioned verification Need
}
\]

---

# 38. Stage S5：小型闭环

只有 S1–S4 均正向后执行。

选择：

```text
8–12 held-out real cases
>=6 qids
```

每个最多：

```text
4 decisions
1 action / decision
```

运行：

\[
Belief
\rightarrow
Progress/Frontier
\rightarrow
Search/Find/Open
\rightarrow
Observation
\rightarrow
Writer
\rightarrow
Belief
\]

---

# 39. S5 期望观察的自然轨迹

例如：

```text
No candidate
→ Discovery Need
→ Search
→ Candidate X becomes Working Hypothesis

→ Verify constraint C4(X)
→ supported Claim

→ Verify C7(X)
→ contradiction
→ clear X

→ Discovery
→ Candidate Y

→ verify remaining constraints
→ all covered
→ final relation supported
→ STOP
```

这才是本轮最终想验证的闭环。

---

# 40. Closure 规则

本轮暂时采用严格 BC+ 语义：

如果 \(C_i\) 是 S0 确认的 HARD_CONSTRAINT：

必须满足：

\[
Claims\models C_i(candidate)
\]

或者由 Claims 明确逻辑蕴含。

不得因为：

```text
candidate is highly plausible
```

跳过。

最终：

\[
resolved=true
\]

至少要求：

\[
\forall C_i\in HardConstraints:
Claims\models C_i(candidate)
\]

并且：

\[
Claims\models RequestedRelation(candidate)
\]

---

# 41. 注意：Runtime 不使用 S0 gold Requirement Map

S0 hard-constraint annotation：

只用于：

- evaluation；
- error attribution；
- primary bank construction。

真实 S4/S5 模型只能看到：

```text
Original Question
Claims
Hypothesis
```

不能看到研究者的：

```text
C1
C2
C3
```

标签。

模型需要动态从 Q 中理解约束。

---

# 42. 必须区分三类错误

## Discovery failure

找不到候选。

## Verification failure

已有正确候选，但无法验证一个明确 constraint。

## Coverage/Frontier failure

证据实际上可验证，但模型没有意识到这个 constraint 仍未覆盖，或选择了错误 frontier。

这三个不能再混成：

```text
agent failed
```

---

# 43. 本轮最重要的因果分解

最终报告：

\[
P(\text{candidate discovered})
\]

\[
P(\text{evidence found}\mid candidate,constraint)
\]

\[
P(\text{Claim admitted}\mid useful evidence)
\]

\[
P(\text{Hypothesis cleared}\mid contradiction)
\]

\[
P(\text{correct verification frontier}\mid candidate)
\]

\[
P(\text{resolved correctly}\mid full coverage)
\]

这样可以第一次真正知道：

> BC+ Research Agent 的困难究竟集中在 Discovery、Verification、State Update 还是 Frontier。

---

# 44. 重新解释前序实验

最终必须重新检查：

- Dynamic Progress 的 false/missed closure；
- Asymmetric Audit 的所谓 over-demand；
- q435；
- q580；
- q186；
- q311；
- q1094。

基于新的 strict constraint semantics，

说明：

> 哪些历史“missed closure”其实可能是合理地发现了尚未覆盖的显式 constraint。

不要修改历史结果。

只提供新的 reinterpretation artifact。

---

# 45. 本轮禁止的捷径

禁止：

```text
candidate looks unique → skip remaining constraints
```

禁止：

```text
current search has no alternative → conclude uniqueness
```

禁止：

```text
absence of another candidate = proof
```

禁止：

```text
one strong source = all question constraints covered
```

禁止：

```text
question constraint → candidate fact
```

---

# 46. 一个重要原则

研究效率优化发生在：

```text
Which constraint should I verify next?
```

而不是：

```text
Which constraints can I ignore?
```

系统可以优先验证：

- 最容易；
- 最有区分力；
- 最可能击穿当前 hypothesis；
- 可由已知文档直接 Find 的 constraint。

但最终 closure 不允许留下未覆盖的 HARD_CONSTRAINT。

---

# 47. Harness 原则保持不变

Harness 不做：

```text
constraint extraction
candidate selection
constraint coverage semantics
mode selection
```

Harness 只做：

```text
Claims version
Hypothesis version
Workspace
tool refs
budget
cache invalidation
schema validation
```

所有语义仍由模型处理。

---

# 48. 缓存

如果：

```text
Claims changed
or
Hypothesis changed
```

则当前 Frontier 必须重新计算。

这里和过去 Progress cache 略有不同：

因为：

```text
Hypothesis changes
```

会直接改变：

```text
verify which candidate?
```

所以 Constraint-aware Frontier 的 cache key 应包括：

\[
Hash(Q,Claims,Hypothesis)
\]

这只适用于 Frontier。

如果未来另有纯 coverage computation，再单独讨论。

---

# 49. 一次 bounded exploration

如果某个正式 gate 失败：

最多：

```text
12 units
<=24 calls
```

只能解决一个主要 observed mechanism。

例如：

```text
candidate-conditioned queries仍太宽
wrong candidate不愿被清除
constraint extraction经常bundle
model混淆explicit constraint和background
```

不得 prompt sweep。

探索不能覆盖正式 Gate。

---

# 50. 最终必须回答

至少回答：

1. BC+ 的 hard constraints 是否总体容易从 Q 中语义识别？
2. 历史 resolved labels 有多少在 strict-all-constraints 标准下仍成立？
3. BC+ 是否确实呈现 “hard to discover, easier to verify”？
4. Positive constraint verification 成功率是多少？
5. Negative candidate falsification 成功率是多少？
6. Verification 平均需要多少 Search/Find/Open？
7. Discovery 平均需要多少？
8. Candidate-conditioned query 是否显著减少 irrelevant evidence？
9. U1 是否能正确把验证结果写成 Claim？
10. contradiction 是否能稳定 clear Hypothesis？
11. 有候选后，Frontier 是否能稳定选择一个 uncovered explicit constraint？
12. 是否仍然会 whole-question Need？
13. 是否仍然会把 question constraint 偷渡成 candidate fact？
14. strict-all-constraints closure 是否消除 q580 类 premature stop？
15. strict closure 是否带来不可接受的研究成本？
16. 是否需要 Persistent Requirement Map？
17. 是否需要 Closure Verifier？
18. 是否需要 Harness semantic router？
19. dominant bottleneck 是 Discovery、Verification、Frontier 还是 Writer？
20. 是否已有资格运行完整 held-out loop？

---

# 51. 最终理论目标

如果实验支持：

\[
Verification(C_i\mid Candidate)
\gg
Discovery(Candidate\mid Q)
\]

并且：

\[
Progress/Frontier
\]

能够在有 Working Hypothesis 时稳定选择尚未覆盖的显式约束，

那么 Search-ESR 的核心控制结构可以进一步简化为：

\[
\boxed{
Belief
\rightarrow
Candidate/Constraint\ Frontier
\rightarrow
Evidence
\rightarrow
Belief
}
\]

其中：

没有候选时：

\[
Frontier=CandidateDiscovery
\]

有候选时：

\[
Frontier=ConstraintVerification
\]

候选被证伪时：

\[
Hypothesis\rightarrow clear
\]

全部显式约束与最终关系被支持时：

\[
STOP
\]

---

# 52. 最终原则

不要优化：

> “哪些约束可以跳过？”

而优化：

> “在已经有候选以后，如何用最低成本把剩余约束验证完？”

不要因为当前只有一个候选就认为唯一。

不要把 Working Hypothesis 当 Claim。

不要把验证阶段变成新的独立 Verifier Agent。

不要把 Question decomposition 持久化。

利用 BC+ 的任务结构：

\[
\boxed{
发现难，
验证易；
路径可以跳，
闭合不能漏。
}
\]

让实验判断：

> 这是否才是 BC+ 长程 Research Agent 最自然、最简单的控制结构。