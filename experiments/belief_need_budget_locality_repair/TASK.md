你现在负责继续修复 Search-ESR 的：

# Belief → Need

当前实验不能直接继续基于上一轮 FAIL 调 prompt。

上一轮暴露了两个相互耦合的问题：

---

# Problem A — Execution Budget Bug

上一轮 Belief → Need 实验显式冻结：

```text
max_tokens = 4096
```

但历史 Search-ESR 主要实验：

- Dynamic Progress
- Asymmetric Progress
- BC+ Verification
- Evidence Scope Localization

并没有显式设置 `max_tokens`。

历史 provider 配置中也不存在：

```text
max_tokens
```

字段。

历史请求依赖 provider 默认 completion budget。

并且已有真实调用：

```text
BC+ Verification
D10 / round2 / actor
```

实际 usage：

```text
input = 3885
output = 65535
reasoning = 65535
finish_reason = length
```

因此仓库证据至少证明：

> 历史默认执行环境允许模型生成约 65,535 completion/reasoning tokens。

不能严格声称 provider 配置字段就是 65,536，因为历史请求没有显式设置 max_tokens。

但可以确定：

\[
4096
\]

不是历史等价配置。

上一轮 391 个请求中：

```text
111 length failures
```

绝大多数：

```text
reasoning ≈ 4096
final JSON absent
```

因此上一轮 strict score 混合了：

\[
SemanticPolicyFailure
\]

与：

\[
ExecutionBudgetFailure
\]

必须先消除这个 confound。

---

# Problem B — Frontier Compression Bug

即使只看实际返回的输出，当前模型仍存在一个稳定语义问题：

> 模型能够大致意识到剩余任务，但不能稳定地把复杂 Belief 压缩成一个“独立可回答、动作级”的局部 unresolved issue。

典型表现：

```text
验证候选是否满足整个题目
```

或：

```text
同时验证排名 + goal difference + 同分关系
```

虽然语义相关，

但仍然过宽。

当前更准确的瓶颈不是简单：

```text
coverage detection
```

而是：

\[
\boxed{
Belief
\rightarrow
one\ action-sized\ unresolved\ issue
}
\]

---

# 0. 仓库与分支

仓库：

`https://github.com/homulillew/Search-ESR`

开始前：

```bash
git fetch --all --prune
```

核验：

`origin/experiment/belief-to-need-convergence`

当前已知 HEAD：

`3d754d160a02eae8900c4f6bb43ef4999bb530a2`

但必须读取实际远程 HEAD。

创建新分支，例如：

```text
experiment/belief-need-budget-locality-repair
```

如已存在，加明确 suffix。

---

# 1. 本轮绝对不修改的东西

Persistent semantic state 保持：

\[
\boxed{
Q + VerifiedClaims + WorkingHypothesis
}
\]

不增加：

```text
Requirement Map
Constraint IDs
Progress State
Persistent Gap
Frontier History
Confidence
Candidate schema
Relation schema
Retrieval scope
```

不训练模型。

不修改：

```text
Search
Find
Open
U1 Writer
Retriever
Workspace schema
```

本轮 Primary 不调用 Search / Find / Open。

只研究：

\[
Belief\rightarrow Need
\]

---

# 2. 首先修复模型执行配置

在任何新的 Need prompt 实验之前，

必须先运行：

# Stage E0 — Completion Budget Calibration

目标不是提高语义分数。

唯一目标：

> 找到一个不会系统性截断 final JSON 的 execution configuration。

---

# 3. 历史等价原则

历史主要实验没有显式 `max_tokens`。

因此最终 Primary 配置优先使用：

```text
omit max_tokens
```

即恢复历史 provider-default 行为。

不要直接声称：

```text
max_tokens = 65536
```

就是历史配置。

历史事实只是：

```text
request did not set a completion limit
```

并且 provider 曾允许真实 completion 达到：

```text
65535
```

tokens。

---

# 4. Calibration cases

从上一轮真实：

```text
finish_reason = length
```

病例中机械选择：

```text
12 cases
>= 4 qids
```

优先：

```text
6 P1 failures
6 P5 failures
```

覆盖：

```text
No-H
weak-H
strong-H
broad-frontier cases
```

不得根据预期答案挑选。

冻结这些 inputs。

---

# 5. Calibration arms

语义 prompt 完全不变。

只改 completion budget。

依次测试：

```text
E4096 = max_tokens 4096
E8192 = max_tokens 8192
E16384 = max_tokens 16384
E32768 = max_tokens 32768
EDEFAULT = omit max_tokens
```

4096 如果已有完全相同 frozen result，可以直接复用。

其余为独立配置 arm。

不是 retry。

---

# 6. Adaptive calibration

不要无条件把所有 arm 全跑完。

顺序：

```text
8192
→
16384
→
32768
→
provider default
```

第一个满足：

```text
>= 11/12 final valid JSON
```

且：

```text
length failure <= 1/12
```

即可暂定为最低可用配置。

但是如果该配置明显使 reasoning 持续贴近上限：

例如：

```text
>=25% requests use >90% completion budget
```

继续测试下一档。

目标不是：

> 恰好能返回。

而是：

> 有合理安全余量。

---

# 7. Historical-default control 必须至少测试一次

无论较低显式 budget 是否通过，

都必须对一个小的固定子集测试：

```text
EDEFAULT
```

因为历史 Search-ESR 运行条件就是：

```text
no explicit max_tokens
```

这样才能回答：

> 4096 是否真正造成行为差异。

---

# 8. Completion metrics

必须独立报告：

```text
FinalJSONCompletionRate
LengthFailureRate
SchemaValidity
ReasoningTokens
FinalAnswerTokens
Reasoning/Output ratio
P50 / P90 / max completion usage
```

尤其区分：

```text
semantic failure
```

和：

```text
no final output
```

以后任何 Need score 必须同时报告：

```text
ITT strict validity
```

以及：

```text
SemanticValidity | final output exists
```

不能再把两者混成一个数字解释。

---

# 9. Preflight

在正式调用前必须用：

```text
3 representative requests
```

验证：

1. JSON mode 可用；
2. system prompt 中包含 provider JSON-mode 所需的字面 `JSON`；
3. `finish_reason=stop`；
4. final JSON 可解析；
5. usage 中能读取 reasoning tokens；
6. chosen completion budget 实际生效；
7. 无 silent truncation。

如果 preflight 失败：

不得提交正式 batch。

先修 transport。

---

# 10. Budget 修复不能改变语义 prompt

Stage E0 中禁止：

```text
修改 wording
增加 locality
增加 self-check
删除规则
加入 examples
```

否则无法判断：

> 上一轮失败究竟有多少来自 4096。

---

# 11. E0 最重要的输出

必须回答：

1. 4096 length failure 是否被更大 budget 大幅消除？
2. 历史 default configuration 的完成率是多少？
3. P1 在有充分 budget 后的真实 semantic-validity 是多少？
4. P5 在有充分 budget 后的真实 semantic-validity 是多少？
5. P5 上一轮的 `6/6 returned valid` 是不是 completion-selection artifact？
6. 是否仍存在模型无限 reasoning 直到 32k / default cap 的病例？

---

# 12. 如果提高 budget 后仍持续撞顶

如果出现：

```text
8192 → length
16384 → length
32768 → length
default → near 65535 / length
```

则不能继续单纯增加 token。

这说明：

\[
Prompt
\]

诱发了病态的 exhaustive reasoning。

将其分类：

```text
E-BUDGET-SPIRAL
```

然后进入 Prompt Simplification。

---

# 13. Stage N1 — 重新定义 ACT 阶段的问题

上一轮 P1 隐含要求：

\[
Q
\rightarrow decomposition
\]

\[
Q+Claims
\rightarrow complete\ coverage\ comparison
\]

\[
ResidualSet
\rightarrow selection
\]

\[
selection
\rightarrow safety\ check
\]

\[
\rightarrow Need
\]

这对于每一步 ACT 可能过重。

新的核心假设：

# ACT 和 STOP 应该是不对称的

继续研究时，只需要证明：

\[
\exists g:
Unresolved(g)\land Useful(g)
\]

即可 ACT。

不需要证明：

\[
\forall g
\]

的完整 coverage。

只有准备 STOP 时，才需要更严格的：

\[
\forall requirements,\ covered
\]

判断。

因此本轮：

> Primary 全部使用已知 unresolved states。

模型不需要判断 STOP。

也不需要完整审计所有剩余 requirement。

---

# 14. 新的最小控制目标

模型真正需要完成的只有：

\[
\boxed{
Belief
\rightarrow
one\ useful,\ independently\ answerable,\ unknown
}
\]

不是：

```text
enumerate all unresolved conditions
```

不是：

```text
identify the globally optimal frontier
```

不是：

```text
prove all other constraints are already resolved
```

---

# 15. Path B0 — Repaired historical baseline

重新测试上一轮：

```text
P1 Coverage-aware
```

唯一变化：

> 使用通过 E0 的 completion budget。

Prompt 一字不改。

目的：

> 测量 4096 confound 被移除后 P1 的真实表现。

---

# 16. Path B1 — Locality baseline

重新测试上一轮：

```text
P5 = P1 + independently-answerable locality rule
```

同样只换 completion budget。

Purpose：

> 判断上一轮 `6/6 returned valid` 是否能在充分输出条件下保持。

---

# 17. Path B2 — Minimal Existential Need

这是本轮最重要的新候选。

不要要求完整 coverage audit。

使用以下 system prompt：

```text
You are choosing one next research question.

Your task is NOT to audit the entire Original Question and NOT to list all remaining gaps.

Find any ONE independently answerable fact or relation that:

1. is not established by the Verified Claims; and
2. would materially reduce uncertainty about the Original Question.

Verified Claims are established facts.

The Working Hypothesis is provisional. You may ask a question that tests or refines it, but you must not assume it is true.

Choose one local unknown that can be investigated on its own.
Leave all other unresolved issues for later.

When no useful Working Hypothesis exists, choose one independently checkable clue, identity bridge, or factual relation whose answer could narrow the research direction. Do not ask which entity satisfies the entire Original Question.

You do not need to identify every unresolved issue.
You do not need to prove that this is the globally best next question.
Finding one valid, useful local unknown is sufficient.

Phrase uncertain relations as questions rather than assumptions.

Return only one JSON object:
{"decision":"research","need":"one natural-language research question"}

Do not output an explanation, plan, checklist, search query, confidence score, or list.
This experiment contains unresolved states. Do not return STOP.
```

这是 Primary candidate。

---

# 18. B2 的理论区别

P1：

```text
compare Original Question against Verified Claims
```

容易诱导：

\[
FullCoverageAudit
\]

B2：

```text
find any one useful unresolved local fact
```

只要求：

\[
ExistentialFrontierSearch
\]

因此理论上应：

- reasoning 更短；
- No-H 更容易；
- whole-question Need 更少；
- 保持 premise safety。

---

# 19. Path B3 — Minimal Two-Step Local Frontier

只有在 B2 仍然存在明显：

```text
broad frontier
```

时才运行。

不是默认必须执行。

第一调用只做：

\[
Belief\rightarrow local\ issue
\]

Prompt：

```text
Find one independently answerable fact or relation that remains unknown and would materially advance the Original Question.

Do not audit the whole question.
Do not list all unresolved issues.
Do not choose whether a candidate satisfies the full description.

Verified Claims are established facts.
The Working Hypothesis is provisional.

Choose exactly one local unknown.
If there is no useful Working Hypothesis, choose one independently checkable clue or identity relation that could narrow the research direction.

Finding one useful unknown is sufficient.

Return only one JSON object:
{"issue":"one independently answerable unresolved fact or relation"}

No explanation, list, plan, query, or confidence.
```

第二调用：

```text
Formulate the supplied unresolved issue as one natural-language research question.

Verified Claims are facts.
The Working Hypothesis is provisional.

Do not add another unresolved condition.
Do not assume the missing relation is already true.

Return only one JSON object:
{"decision":"research","need":"one natural-language research question"}
```

Ephemeral issue 仍然：

- 不持久化；
- 不进入 State；
- 每次重新计算。

---

# 20. Oracle diagnostic 保留

继续保留类似 P4：

```text
Gold local issue → Need
```

但：

- 仅 diagnostic；
- 不参与 production selection；
- 不用于“证明 Requirement Map 应持久化”。

它回答：

> 如果 local issue 已经正确选中，Need formulation 的上限如何？

---

# 21. 不再大规模测试 P0 / P2

历史已经显示：

### P0

明显弱。

### P2

self-check 增加 reasoning cost，

未显示稳定的边际收益。

本轮不继续消耗大量调用重复它们。

如果未来 bad case 明确表明：

```text
premise safety
```

重新成为主导问题，

才重新引入 self-check。

---

# 22. Need Primary Rubric 保持

一个 Need strict-valid 必须：

### Relevant

能推进 Q。

### Unresolved

Claims 尚未回答。

### Grounded

没有把 Q 中的描述或 H 偷渡为事实。

### Local

主要解决一个 independently answerable fact/relation。

### Actionable

可以合理通过研究获取答案。

---

# 23. 特别修改 Broadness 判定

以下不再算 local：

```text
Does candidate X satisfy all of the described conditions?
```

```text
Which entity matches all these clues?
```

```text
In which season did X simultaneously have rank Y, GD Z and equal points with another team?
```

当这些条件可以独立调查时。

允许必要的关系限定，例如：

```text
What was X's goal difference in the 2014 season?
```

这里 entity + season + relation 是一个独立事实。

---

# 24. No-H 是正式重点

上一轮：

```text
P0–P3 No-H dev = 0/7
P4 = 7/7
```

但大量 no-H 是 length failure。

因此 budget 修复后必须专门报告：

```text
No-H completion
No-H strict-valid
No-H broadness
No-H premise
```

B2 的目标是：

> 没有 H 时，不问整题答案，而选择一个独立 clue / bridge。

例如不要：

```text
Which club satisfies all these conditions?
```

而选择类似：

```text
Which club was described in the 2023 article as signing 13 players?
```

前提是这仍是当前未解决、可推进的局部问题。

---

# 25. Strong-H / One-Gap 仍然必须测

对于：

```text
strong H
+
one unresolved relation
```

需要确认：

> 模型不会因为 H 很强而停止；
> 也不会扩成整套候选验证。

目标：

```text
>=90% local-gap activation
```

但必须获得更多真实 one-gap states。

上一轮只有：

```text
1
```

个，不够。

---

# 26. Belief Delta 继续保留

Coverage pair：

State A：

```text
gap g unresolved
```

State B：

只新增一个 supported Claim 覆盖 g。

要求：

如果 A 选择 g，

B 必须退休 g。

但是：

> Pair correctness 不能仅因为 A/B 都选了其他 valid gap 就被解释成 strong causal evidence。

继续单独报告：

```text
A activated g
A activated g and was valid
B retired g
B remained strict valid
```

---

# 27. Fresh evidence 不足必须解决

上一轮只有：

```text
10 total historical qids
```

其中：

```text
5 challenge
5 less-exposed
```

无法满足：

```text
>=8 fresh qids
```

confirmation。

不能继续在现有五个 development qids 上调 prompt。

---

# 28. Stage D0 — Fresh Belief Acquisition

如果仓库现有自然历史不足，

允许创建新的 Belief 数据，

但必须与 Need policy 开发完全隔离。

从尚未进入 Need prompt 开发的 BC+ qids 中：

```text
>=10 new qids
```

创建新的自然 research histories。

---

# 29. Fresh state acquisition 原则

不得人工编造：

```text
Claims
Hypothesis
```

。

使用冻结的既有 Research Harness：

```text
Search/Find/Open
+
frozen U1 Writer
+
historical/base Actor policy
```

生成自然轨迹。

Need实验 prompt：

```text
B1/B2/B3
```

不得参与 state acquisition。

这样不会泄漏最终 policy。

---

# 30. 每个新 qid 尽量收集

### Initial state

```text
Q
Claims=[]
H=""
```

### Early discovery state

经过 1–2 个真实 evidence update。

### Hypothesis state

如果自然产生 H。

### Later coverage state

多个 Claims 已建立但仍未完成。

### Near-closure / one-gap

如果真实轨迹自然出现。

不能强造。

---

# 31. 所有新 Claims 必须有 provenance

每个 state 必须能追溯：

```text
Observation
source hash
Writer output
Claim
```

不能通过研究者手写 Claim 填补某个 stratum。

---

# 32. 新 qid 在 Need 实验前冻结

流程必须：

```text
Acquire trajectories
→ Freeze all QCH
→ Commit
→ Offline label unresolved gaps
→ Commit
→ THEN create/run Need prompts
```

不能看 B2 输出以后再选择 states。

---

# 33. Development / Confirmation 分开

新的 qids 至少拆：

```text
development >= 4 qids
confirmation >= 8 qids
```

如果资源允许：

```text
development 6–8 qids
confirmation 8–12 qids
```

同 qid 不能同时参与 prompt design 和 fresh confirmation。

---

# 34. Semantic Development Gate

在修复后的 completion configuration 下，

候选 policy 必须首先满足：

```text
Final JSON completion >=95%
STRICT_VALID >=85%
Premise error <=5%
Stale <=5%
Broad/whole-question <=10%
No-H strict-valid >=80%
Strong-H one-gap >=90% if denominator adequate
Coverage-delta retirement >=85%
```

否则进入 bad-case loop。

---

# 35. Bad-case loop

每轮只允许：

```text
一个主导语义机制
```

。

例如：

```text
No-H broadness
premise promotion
wrong granularity
candidate fixation
```

不能再把各种 guard 一次全部加入 prompt。

---

# 36. Prompt 简化优先于 Prompt 加法

如果出现错误：

优先问：

> 是否能把任务定义得更直接？

而不是：

> 再增加一条 Do not。

原则：

\[
\boxed{
positive task definition
>
accumulating negative guards
}
\]

避免重新产生 long reasoning。

---

# 37. 每轮必须监测 reasoning regression

一个 prompt 即使 semantic accuracy 提高，

如果：

```text
P90 reasoning tokens
```

大幅上涨，或者：

```text
length failures
```

重新出现，

也不能直接采用。

Need policy 的目标是：

> 简单、稳定、低成本地产生下一问题。

---

# 38. Fresh Confirmation

最终候选方案必须在：

```text
>=24 states
>=8 completely fresh qids
```

上确认。

门槛：

```text
Final JSON completion >=95%
STRICT_VALID >=90%
Premise <=5%
Stale <=5%
Broad <=5%
No-H >=85%
Strong-H one-gap >=90% where denominator adequate
Coverage-delta >=90%
```

不能使用：

- q580；
- q1094；
- 当前 development qids；

来替代 fresh confirmation。

---

# 39. PASS / NEAR_PASS

## PASS

满足全部 fresh gates。

## NEAR_PASS

至少：

```text
completion >=95%
strict >=85%
premise <=5%
stale <=7.5%
No-H >=80%
```

且剩余错误集中在一个明确长尾机制，

无系统性：

```text
whole-question collapse
hypothesis promotion
premature closure
```

。

---

# 40. Closure 仍然分开

本轮主要验证：

\[
UnresolvedBelief\rightarrow Need
\]

不要重新把 STOP 塞回来污染 ACT。

这是一个重要设计原则：

\[
\boxed{
ACT\ is\ existential;
STOP\ is\ universal.
}
\]

ACT：

> 找到一个有效 unresolved issue 即可继续。

STOP：

> 必须确认没有剩余 material unresolved issue。

后者下一阶段单独验证。

---

# 41. 不要在 ACT 时完整构造 Requirement Map

本轮明确测试：

\[
\exists g
\]

而不是：

\[
\{g_1,g_2,\ldots,g_n\}
\]

。

即：

> 只要找到一个局部未知即可。

不需要每一步都完整列出所有 requirement 再做 subtraction。

这既减少 reasoning cost，

也保持 Harness 通用性。

---

# 42. 最终希望得到的生产 prompt

除非实验否定，

优先收敛到类似：

```text
You are choosing one next research question.

Find any one independently answerable fact or relation that is still unknown and would materially advance the Original Question.

Verified Claims are established facts.

The Working Hypothesis is provisional: it may be tested or refined, but it is not evidence.

Choose one local unknown and leave other unresolved issues for later.

If no useful Working Hypothesis exists, choose one independently checkable clue or relation that could narrow the research direction rather than asking for the entire answer.

You do not need to audit every unresolved part or prove this is the globally best next question.

Return only one JSON object:
{"decision":"research","need":"one natural-language research question"}
```

最终是否采用，必须由 fresh confirmation 决定。

---

# 43. 最终报告必须回答

1. 历史实验为什么没有大量 4096 length failure？
2. 4096 cap 相比历史 provider-default 造成了多大 completion regression？
3. 修复预算后 P1 的真实 strict validity 是多少？
4. 修复预算后 P5 是否仍保持高 semantic precision？
5. B2 minimal existential prompt 是否降低 reasoning tokens？
6. B2 是否比 P1/P5 更少 broad Need？
7. No-H 失败究竟主要是 semantic 还是 budget？
8. local-frontier selection 是否仍是主瓶颈？
9. 两阶段 B3 是否真正值得额外调用？
10. Oracle issue → Need 是否仍维持约90%+？
11. 新鲜 qids 上结果能否复制？
12. 是否有任何结果要求改变 Persistent State？
13. 是否需要 Requirement Map？
14. 是否需要 separate verifier？
15. Belief → Need 最终是 FAIL / NEAR_PASS / PASS？
16. 是否有资格进入 Closure + end-to-end？

---

# 44. 最重要的解释约束

不能再次把：

```text
no final output
```

解释成：

```text
semantic Need failure
```

。

必须区分：

\[
P(Output)
\]

和：

\[
P(ValidNeed\mid Output)
\]

最终整体可靠性：

\[
P(ValidNeed)
=
P(Output)
\times
P(ValidNeed\mid Output)
\]

两项都必须高。

---

# 45. 最终研究目标

本轮不是为了：

> 调高一个 benchmark 分数。

而是要证明：

\[
\boxed{
(Q,C,H)
\rightarrow
one\ local\ useful\ unknown
\rightarrow
Need
}
\]

可以在：

- 足够执行预算；
- 不持久化 Requirement Map；
- 不结构化 Need；
- 不训练；
- 不增加 verifier；

的条件下稳定运行。

尤其验证新的核心假设：

\[
\boxed{
继续研究只需要找到一个有效缺口；
只有停止研究才需要证明所有缺口都消失。
}
\]

如果这个不对称设计成立，

Search-ESR 的最终控制结构可以进一步简化为：

\[
Belief
\rightarrow
one\ local\ Need
\rightarrow
Evidence
\rightarrow
Belief'
\]

而完整 coverage audit 只在：

\[
STOP
\]

候选出现时执行。

这才是本轮最终需要验证的修复方向。