你现在负责 Search-ESR 下一阶段核心实验：

# Need → Evidence Access
# Retrieval Scope Selection & Local Relation Localization

仓库：

`https://github.com/homulillew/Search-ESR`

当前研究基线：

`experiment/bcplus-discovery-verification`

开始前必须：

```bash
git fetch --all --prune
```

核验：

`origin/experiment/bcplus-discovery-verification`

最新 HEAD。

当前已知研究完成时 HEAD 为：

`fcd195f0f0c6299f00f155c2a6ae37e915fa177e`

但必须以实际远程 HEAD 为准。

创建新分支，例如：

`experiment/evidence-scope-localization`

如果同名存在，增加明确 suffix。

继续使用：

- 同一个 `deepseek-flash`
- 当前 provider
- 当前 BC+ corpus
- 当前 v3a Search
- 当前 Find
- 当前 Open
- 当前 Workspace / D# / W#
- 当前 U1 Writer

本实验：

**不训练模型。**

**不修改 Persistent Research State。**

Persistent semantic state 继续只有：

```text
Original Question
Verified Claims
Working Hypothesis
```

不增加：

```text
Requirement Map
Source Plan
Persistent Need
Retrieval Mode
Confidence
Evidence Target fields
Candidate/Relation schema
```

---

# 0. 当前实验依据

最新 Candidate Discovery vs Constraint Verification 实验已经把上游变量大幅固定。

Verification 输入中，Candidate 与单个待验证条件均由实验预先给定。

因此这类失败不能再主要归因于：

```text
不知道候选是谁；
不知道当前缺什么；
Frontier 选错；
Closure 判断错。
```

正式 Verification：

```text
29 units / 10 qids
```

取得指定关系 Evidence：

```text
20/29 = 69.0%
```

取得指定关系 Evidence 后：

```text
valid target Claim:
19/20 = 95%
```

明确目标反证出现以后：

```text
Hypothesis clear:
6/6
```

任意明确 hard-constraint contradiction 出现以后：

```text
Hypothesis clear:
8/8
```

因此当前主要可观察断点为：

\[
Need
\rightarrow
ExactRelationEvidence
\]

而不是：

\[
Evidence
\rightarrow
Claim
\]

---

# 1. 当前 Retrieval 实际承担的三个判断

Actor 当前一次调用隐式完成：

\[
Need
\rightarrow
Scope
\rightarrow
Query
\rightarrow
Tool
\]

其中：

```text
Search
```

对应：

```text
global corpus scope
```

```text
Find(D#)
```

对应：

```text
known-document scope
```

```text
Open(W#)
```

对应：

```text
adjacent-window scope
```

本轮不新增显式 Scope 字段。

Scope 仍是 Actor 的内部决策。

---

# 2. 当前关键观察

最新 Verification 正式工具使用：

```text
Search: 37
Find:    2
Open:    0
```

部分失败满足：

```text
正确文档已经存在于 Workspace
+
当前 Need 已经明确
+
目标关系确实存在于该文档
+
visible window 尚未包含 exact relation
```

但 Actor 仍继续 Global Search。

唯一 bounded exploration 仅增加通用提示：

> 考虑当前已有文档是否适合验证缺失关系，必要时使用文档内检索或上下文扩展。

在 4 个失败选择病例：

```text
exact relation success:
0/4 → 2/4
```

VP06：

```text
repeat Search
→
Find D1
→
8x11 paper evidence
→
correct Claim
```

VP12：

```text
Search stops at filmography header
→
Find D1
→
Policeman 1 row
→
correct Claim
```

这是局部机制信号，不是正式总体确认。

---

# 3. 本轮核心问题

## RQ1

当正确来源已经存在于 Workspace 时：

> 当前 Actor 是否过度偏好 Global Search？

---

## RQ2

加入一个**通用的 retrieval-scope 策略提示**后：

> 能否更稳定利用已有文档，同时保持 Global Search fallback？

---

## RQ3

当前 v3a Global Search 已经支持旧文档重新定位。

因此：

> 单纯使用统一 Global Search，是否已经足够？

还是：

> Find 在 known-source 情况下确实提供额外价值？

---

## RQ4

如果直接给定正确 document scope：

> 当前 Find/Open 能否稳定取得 exact relation？

这用于区分：

```text
scope-selection failure
```

与：

```text
within-document localization failure
```

---

## RQ5

当前失败到底主要来自：

```text
wrong scope
wrong query
localizer/window
```

哪一层？

---

# 4. 统一概念

本轮理论上把：

```text
Search
Find
Open
```

统一理解为：

\[
Retrieve(Need,Scope)
\]

但 Runtime 工具接口保持不变。

```text
Search = global scope
Find   = known-document scope
Open   = adjacent scope
```

本轮绝不新增：

```text
retrieve()
scope_router()
query_planner()
```

工具。

实验只研究：

> 同一个 Actor 如何使用现有工具。

---

# 5. Need 保持自然语言

本轮不使用生产式结构化：

```json
{
  "candidate": "...",
  "relation": "...",
  "constraint": "..."
}
```

作为 Actor 接口。

实验从上一轮 Oracle Candidate + Constraint 构造一个冻结的自然语言 Current Need。

例如：

```text
What role did Peter Nzioki play in The Constant Gardener?
```

```text
How many seasons did You're the Worst run for?
```

```text
Did company X use the required former name when first established?
```

所有 arm 接收完全相同的 Need。

Need 在模型调用前冻结。

不得根据某 arm 输出改写。

这保持最终 Harness 的通用性：

\[
Need=\text{one natural-language research question}
\]

---

# 6. Stage R0：构建 Evidence-Scope Bank

构建两个主 bank。

---

# 7. K-bank：Known-source cases

目标状态：

```text
Need明确；
Workspace已经包含至少一个高度相关文档D；
gold exact relation确实存在于该D；
当前visible windows不包含完整目标关系。
```

必须通过 corpus-level source audit 确认：

```text
gold document
exact supporting/refuting span
document hash
offset
```

这些只用于离线评价。

绝不能给普通 Actor。

---

# 8. K-bank freshness

Primary K-bank 排除：

```text
VP06
VP12
VN01
VN07
```

因为这些已进入上一轮 bounded exploration。

它们作为 Challenge Set 保留。

从：

```text
上一轮正式 Verification
+
其他真实历史 Workspace states
```

机械提取所有新的 eligible states。

目标：

```text
K >= 12
>= 6 qids
```

如不足：

使用全部真实 eligible cases，并明确报告不足。

禁止 synthetic source insertion。

---

# 9. K-bank 类型覆盖

尽量覆盖：

```text
prose relation
table row
date/scope relation
quantity
role
career fact
company/release relation
event relation
```

记录 document 结构：

```text
prose
table
list
mixed
```

用于 failure decomposition。

---

# 10. N-bank：No-known-source controls

为了防止 Scope-aware policy 退化成：

> “只要 Workspace 有文档就死磕本地”

还必须构建 N-bank。

满足：

```text
Need明确；
Workspace存在一些已知文档；
但这些文档均不包含目标 exact relation；
正确 evidence 必须通过新的 Global Search 获取。
```

目标：

```text
N >= 8
>= 5 qids
```

这些 case 用来测试：

> scope-aware policy 是否造成错误 local lock-in。

---

# 11. Challenge Bank

单独保留：

```text
VP06
VP12
VN01
VN07
```

以及其他已经明确分析过的 known-source failures。

不能进入 fresh Primary Gate。

只用于机制复现。

---

# 12. Stage R1：四个 Retrieval Arms

所有 arm：

- 同一个 natural-language Need；
- 同一个 Workspace；
- 同一个 Recent Attempts；
- 同一个 budget；
- 同一个 model/provider；
- 不调用 Writer；
- 不修改 Claims/Hypothesis；
- 最多 2 个 tool decisions；
- 每 decision 最多 1 action。

这里只测：

\[
Need+Workspace\rightarrow Evidence
\]

避免 Writer 再次混入因果链。

---

# 13. Arm A0：Current Free Policy

使用当前 Verification Actor retrieval semantics。

Tools：

```text
Search
Find
Open
```

不增加 scope 提示。

代表：

> 当前行为。

---

# 14. Arm A1：Scope-Aware Policy

Tools 完全相同：

```text
Search
Find
Open
```

只在 Actor prompt 加一个**通用**策略段。

建议冻结：

```text
Before choosing a retrieval action, consider the narrowest evidence scope justified by the current Workspace.

If an already discovered document is plausibly about the exact subject and relation needed for the Current Research Need, consider searching within that document before globally retrieving the corpus.

If no known document is a strong candidate source, or local inspection fails to provide the needed relation, use global Search.

Do not remain locked to a known document merely because it is topically related.

Choose the retrieval scope first, then formulate a query appropriate to that scope.

A global Search query should contain enough entity and relation context to retrieve the right source.

A document-local Find query should focus on the missing relation or distinctive wording inside that document and need not repeat context already fixed by the document itself.

Open is for adjacent context around an already relevant visible passage, not for searching the whole document.
```

注意：

不出现：

```text
BC+
candidate constraint
D1 is correct
local-first
```

等 task-specific / oracle 提示。

这是一个通用 Research Retrieval policy。

---

# 15. Arm A2：Unified Global Retrieval

用于直接回答：

> v3a 的统一 Search 是否已经足够？

移除 Find。

保留：

```text
Search
Open
```

Search 使用当前 v3a：

- 全 corpus ranking；
- 命中旧文档时仍可产生新的 query-conditioned localized preview。

Actor 可重复 Search，不允许 Find。

Open 仍可读取当前 Search 返回窗口邻近内容。

这代表：

\[
\boxed{
GlobalSearch作为统一重新定位接口
}
\]

的最强可用 baseline。

不得改 Retriever/localizer。

---

# 16. Arm A3：Oracle Document Scope

只用于 K-bank。

给 Actor 一个额外实验事实：

```text
For this diagnostic only, the required evidence is located somewhere in document Dk.
```

不告诉：

- exact wording；
- offset；
- window；
- value；
- answer；
- query。

禁止 Global Search。

只允许：

```text
Find(Dk,...)
Open(...)
```

这是 diagnostic upper bound。

用于测：

\[
Need+CorrectDocument
\rightarrow
ExactEvidence
\]

而不是部署方案。

---

# 17. 为什么 A3 很关键

如果：

```text
A3很高
A1较低
```

说明：

\[
ScopeSelection
\]

是主要问题。

如果：

```text
A3仍然低
```

说明：

\[
Find/Localization
\]

本身仍有问题。

如果：

```text
A1≈A3≫A0
```

说明：

> 一个通用 scope-aware prompt 基本足够，不需要 Harness hard router。

---

# 18. Query 不单独结构化

Actor 仍直接输出：

```text
tool + arguments
```

不增加：

```text
scope
query_plan
target_entity
relation
```

字段。

但是分析时从动作中离线推断：

```text
global/local/adjacent
```

Scope 是评估变量，不是运行时状态。

---

# 19. Primary Outcome

每个 case 的主要结果：

\[
ExactEvidenceFoundWithin2Actions
\]

必须是真正支持或反驳当前 Need 的 exact relation。

只找到：

- candidate page；
- same-topic document；
- related clue；
- generic entity information；

都不算成功。

---

# 20. Secondary Outcomes

记录：

### Source-level

```text
correct source selected/discovered
```

### Window-level

```text
exact relation visible
```

### First-action success

```text
exact evidence after action 1
```

### Second-action recovery

```text
failed action1 but succeeds action2
```

### Tool distribution

```text
Search / Find / Open
```

### Known-source utilization

K-bank 中：

```text
first action uses existing relevant D
```

比例。

注意：

不用它替代 final evidence success。

---

# 21. Scope error taxonomy

每个失败必须归类。

## S1：unnecessary-global

Known relevant document exists，

但 Actor Global Search，

且未获得目标证据。

## S2：wrong-local-source

Actor 进入一个 Workspace 文档，

但该文档并不包含目标 relation。

## S3：local-lock

第一次 local inspection 无果后，

第二次仍在错误 local source，

没有使用 global fallback。

## S4：global-source-miss

需要 global Search，

但正确 source 没进入返回结果。

## S5：source-hit-window-miss

正确 source 已获取，

但 target relation 未进入 visible window。

## S6：query-localization-miss

正确 source + local Find，

但 query 定位到错误 occurrence/section。

## S7：adjacent-context-miss

已出现接近 target 的 passage，

但没有 Open 获得完整关系。

## S8：actor-stop

证据尚未取得即 STOP。

---

# 22. Query Analysis

不要用研究者主观“好 query / 坏 query”作为 Primary。

只记录可审计属性：

```text
tool
scope
query string
repeated query
same-document rediscovery
relation keywords present
candidate/entity terms present
```

最终根据 evidence outcome 解释。

不能看到失败后再人为重写“理想 query”作为正式指标。

---

# 23. R1 Gate：Scope-Aware policy

Primary K-bank：

建议预注册：

```text
A1 exact-evidence success >= 80%
```

并且相对 A0：

```text
absolute improvement >= 15 pp
```

如果样本整数过小，冻结 bank 后转换成整数门槛。

Primary N-bank：

A1 不得比 A0 的 exact-evidence success 下降超过：

```text
10 pp
```

同时 local-lock：

```text
<=10%
```

目标：

> 提高已知来源利用率，但不把策略变成 local-first hard rule。

---

# 24. R1 对 Unified Search 的判定

比较：

```text
A1 vs A2
```

尤其 K-bank。

如果：

```text
A2 ≈ A1
```

且成本相近，

说明：

> 当前 v3a Global Search 的旧文档 re-localization 已经足够，可以考虑简化 Find。

如果：

```text
A1明显高于A2
```

说明：

> document scope control 确实有实际价值，Find 不只是接口冗余。

这个结果直接回答当前架构争议。

---

# 25. Oracle Scope 判定

如果：

```text
A3 >= 90%
```

则当前 Find/Open 在 gold source 已知时基本可用。

当前主要问题：

```text
Scope selection / policy
```

如果：

```text
A3 < 80%
```

则不能只靠 prompt policy。

进入 Stage R2。

80–90% 为灰区，结合错误类型判断，但不得事后改变 primary gate。

---

# 26. Stage R2：Within-Document Localization

仅当 A3 明显失败时运行。

不得因为想“把实验做完整”无条件运行。

此阶段不测试 Search。

输入固定：

```text
Need
gold D#
```

---

# 27. R2 Arm F0

当前：

```text
Find(D, query)
```

single localized window。

Actor 最多两步：

```text
Find
Open/Find
```

---

# 28. R2 Arm F1：Top-k Local Find

唯一 Harness-level intervention：

将 Find 从：

```text
one best local match
```

扩为：

```text
top 3 non-overlapping local matches
```

保持：

- 同一文档；
- 同一 lexical/local locator 基础；
- 不使用新 embedding model；
- 不训练；
- 不改变 corpus；
- 每个 match 独立 W#；
- 总 token budget控制在与现有 Search top-k 可比较范围。

不要同时加入 semantic Find / table parser。

这样只测试：

> single local maximum 是否导致 relation miss。

---

# 29. R2 Primary

比较：

```text
F0 vs F1
```

exact relation evidence。

同时按：

```text
prose
table
list
mixed
```

报告。

如果 table cases 改善尤其明显：

下一轮才值得研究结构感知 localizer。

---

# 30. R2 不允许继续 prompt sweep

只有：

```text
single-window
vs
top-k local windows
```

一个变量。

不要同轮再测试：

```text
semantic Find
table-aware Find
heading-aware Find
query expansion
```

否则无法归因。

---

# 31. Writer 暂时冻结

本轮正式 Primary R1/R2 不运行 Writer。

原因：

上一轮已经观察：

\[
P(validTargetClaim\mid usefulEvidence)=19/20
\]

当前问题应隔离 retrieval。

如果最终 exact evidence success 显著提高，

可在阶段末仅做一个 replay：

```text
same frozen U1
```

验证新 Evidence 不导致明显 Claim regression。

这个 replay 不能改变 retrieval gate。

---

# 32. Secondary Offline Audit：当前 Claim Admission 是否已经覆盖“第三种策略”

不需要新 Search。

使用上一轮正式 318 个窗口与 U1 输出。

对 Observation 离线增加一个标签：

```text
contains direct evidence for another Original-Question hard constraint,
different from the Current Need?
```

如果有：

检查 U1 是否保存。

计算：

\[
P(admit\ offNeedQuestionConstraint
\mid
directSupport)
\]

同时统计：

```text
新增Claims数量
unsupported strengthening
duplicate
```

---

# 33. 这个 Secondary Audit 回答 Claim 设计问题

我们现在区分三种策略：

### All evidence

已否定。

### Current Need only

理论上过窄。

### Current Need OR Original Question constraint relevance

当前 U1 prompt 已明确允许：

```text
establishes another still-unresolved requirement of the Original Question
```

本轮只验证它**实际是否做到**。

如果 off-Need hard-constraint evidence admission 很高：

> 不需要改 Writer。

如果很低：

下一轮再单独研究 Admission Recall。

不要本轮同时修改 Writer。

---

# 34. 本轮不改变 State Schema

无论 R1/R2 结果如何，都不得因此增加：

```text
source preference
active document
retrieval scope
constraint IDs
need fields
```

到 Persistent State。

正确分层仍然是：

```text
Research State:
Q + Claims + Hypothesis

Workspace:
D# / W# / observed source locations

Need:
temporary natural-language research question

Action:
Search / Find / Open
```

---

# 35. 本轮理论模型

可以正式写成：

\[
B_t=(Q,C_t,H_t)
\]

派生：

\[
N_t=Frontier(B_t)
\]

然后：

\[
a_t=
RetrievalPolicy(N_t,W_t,A_t)
\]

其中内部隐含：

\[
N_t
\rightarrow
Scope_t
\rightarrow
Query_t
\rightarrow
Tool_t
\]

但：

```text
Scope
Query
```

不持久化。

执行：

\[
O_t=Execute(a_t)
\]

再：

\[
B_{t+1}=Update(B_t,N_t,O_t)
\]

---

# 36. 本轮最重要的原则

不要因为 retrieval failure 增大 Semantic State。

不要因为一个 known-source success 就 hard-code local-first。

不要因为 v3a Search 能恢复旧事实就假设 Find 永远无价值。

不要因为 Find 存在就假设 Actor 会正确使用它。

不要把实验中的 Oracle Source 变成 Runtime routing rule。

---

# 37. 结果解释矩阵

## 情况 A

```text
A1 ≫ A0
A1 ≈ A3
A1 > A2
```

结论：

> Find 本身有价值，主要缺的是一个通用 scope-selection policy。

保留 Search/Find/Open。

只改 Actor prompt/control contract。

---

## 情况 B

```text
A2 ≈ A1 ≈ A3
```

结论：

> v3a Unified Global Search 已经足够。

Find 可能没有足够边际价值。

可以进一步研究简化 action space。

---

## 情况 C

```text
A3 ≫ A1
```

结论：

> Find/localizer 可用，但 Actor 不会选正确 source scope。

问题主要在 Retrieval Policy。

---

## 情况 D

```text
A3也低
```

结论：

> 即使 source 已知，局部定位仍失败。

进入 R2。

问题主要在 Find/localization。

---

## 情况 E

```text
A1提高K
但N显著下降
```

结论：

> Scope-aware prompt 过度 localize。

不能作为通用 policy。

需要保持更强 global escape 条件。

---

# 38. Challenge 机制验证

VP06 / VP12 / VN01 / VN07 单列。

特别报告：

```text
A0
A1
A2
A3
```

但不能用这四个病例覆盖 fresh Primary Gate。

---

# 39. 成本

报告：

```text
mean tool actions
Search calls
Find calls
Open calls
input tokens
output tokens
reasoning tokens
elapsed
```

更重要的是：

```text
actions to exact evidence
```

而不是只比较总 token。

---

# 40. 一次 bounded exploration

如果正式 gate 失败，允许一次：

```text
<=12 cases
<=24 model calls
```

只能针对一个已观察机制。

例如：

```text
A3低且table集中失败
```

才允许探索 table-sensitive local retrieval。

或者：

```text
A1仍重复Global Search
```

才允许微调 generic scope instruction。

不能同时做两件事。

---

# 41. 不运行 Frontier / end-to-end 的条件

本轮 Need 是冻结正确的自然语言 Need。

如果：

\[
Need\rightarrow Evidence
\]

仍未达到可靠水平，

不要继续增加 Frontier uncertainty。

只有 Retrieval 层通过以后，

下一阶段才重新测试：

\[
Q+Claims+H
\rightarrow
Need
\]

是否可以自主生成同质量 Need。

---

# 42. 最终报告必须回答

1. 最新 Verification bad cases 主要是 Scope selection 还是 Localization？
2. 当前 Actor 是否过度偏好 Global Search？
3. 一个通用 scope-aware prompt 能否 fresh-confirm bounded exploration 信号？
4. Scope-aware policy 是否造成 local lock-in？
5. v3a Unified Global Search 是否已经足以替代 Find？
6. Find 在 known-source cases 是否有真实边际价值？
7. 如果正确 source 直接给定，当前 Find/Open 成功率是多少？
8. table / prose / list 是否有明显差异？
9. 当前 query failure 是 global query 还是 local query 更突出？
10. Search 命中正确文档但 window 错的比例是多少？
11. 当前 Workspace 是否已经足够，还是需要修改内容？
12. 是否有任何证据要求修改 Persistent State？
13. U1 是否实际保存 off-Need 但 Original-Question-relevant 的事实？
14. 当前 Claim Admission 是否已经实现“Need OR Original Question relevance”？
15. 下一瓶颈应该进入 Frontier 还是继续 Retrieval？
16. 是否有资格运行 held-out end-to-end loop？

---

# 43. 最终目标

本轮不是为了证明：

```text
Search好
```

或：

```text
Find好
```

而是判断更一般的问题：

\[
\boxed{
当Need已经明确时，
一个通用Research Agent
是否能根据已有Workspace
选择合适的证据范围，
并稳定取得exact evidence？
}
\]

最终希望保留的通用 Harness 仍然是：

\[
\boxed{
Q + Claims + Hypothesis
}
\]

产生自然语言：

\[
\boxed{
Need
}
\]

然后：

\[
\boxed{
Need + Workspace
\rightarrow
Search/Find/Open
}
\]

证据返回以后：

\[
\boxed{
Evidence + Need + OriginalQuestion
\rightarrow
SelectiveClaims
}
\]

其中：

- Claims 缓存“已经证明什么”；
- Workspace 缓存“证据可能在哪里”；
- Search/Find/Open 只是不同 evidence scope 的访问方式；
- Harness 不理解候选、约束或关系；
- 所有语义仍由模型完成。

让本轮实验回答：

> 当前最后主要缺的是 Retrieval Policy，还是底层 Local Evidence Access。