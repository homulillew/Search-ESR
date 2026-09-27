# Search-ESR：Minimal Need → Multi-Query Research Control 实验任务

你正在继续一个已经进行了大量受控实验的研究项目 **Search-ESR**。

本任务不是重新设计一个通用 Deep Research Agent，也不是自由探索“怎样让 Agent 更强”。

你的任务是：

> **在不增加新的 persistent semantic state、不引入 Requirement Map / Dependency Graph / Planner / persistent Frontier 的前提下，验证一个极简 Research Harness 是否可以稳定地从 `Q + Verified Claims + Working Hypothesis` 派生一个正确的当前 Need，并允许该 Need 进一步 fan-out 成一条或多条检索动作。**

必须严格执行因果隔离、freshness、append-only、失败保留和阶段 Gate。

---

# 0. 开始前必须做的事情

首先检查实际远程仓库，不要根据本任务书中写出的旧 SHA 假定当前状态。

仓库：

```text
homulillew/Search-ESR
```

执行：

```bash
git fetch origin --prune
git status
git branch --show-current
git rev-parse HEAD
git rev-parse origin/main
git log --oneline --decorate -20 origin/main
```

当前编写任务书时最后一次确认的 `origin/main` 为：

```text
8021aca19a1ee5201730e40b338012c65ecd51cf
```

commit message：

```text
Add Evidence Pointer State v0 and authentication batch short-circuit
```

但这只是历史锚点。

**必须以你实际 fetch 到的远程最新内容为准。**

如果远程在此之后出现新的 Need / Research State / Query / Evidence Pointer 实验：

1. 先阅读；
2. 判断是否改变本任务的实验前提；
3. 在 `PRE_EXECUTION_AUDIT.md` 中说明；
4. 不得静默覆盖新结果。

---

# 1. 先理解研究历史，不要直接写代码

至少阅读以下历史实验及最终结论。

## Query / Search 层

```text
全链路排查报告/Search-Open节点排查与冻结报告.md
全链路排查报告/Query初始化首轮对照实验.md
全链路排查报告/Query单入口初始化落地与联调.md
全链路排查报告/Query固定线索表达对照与根因验证.md
全链路排查报告/Query通用原则提示词落地与对照实验.md
全链路排查报告/BasisPacket固定原文与保守编译对照实验.md
```

必须理解：

- Search 命中文档 ≠ Evidence 实际可见；
- Query 生成本身会发生主体错接、关系压缩、时间范围丢失；
- Query 是一次 retrieval action，不是 Belief；
- `basis_refs`、query、source guess 都不能自动升级成事实。

## Search / Find / Retrieval

阅读：

```text
experiments/search_find_v3a/RESULTS.md
experiments/search_find_v3b/RESULTS.md
experiments/unified_global_retrieval/FINAL_CONCLUSION.md
experiments/deferred_recovery/FINAL_CONCLUSION.md
experiments/evidence_scope_localization/FINAL_CONCLUSION.md
```

理解：

- Find 机械能力存在，但模型可能完全不使用；
- “更多 Find”不是目标；
- Global Search 对很多旧事实具有恢复能力；
- Find 适合作为 known-document local inspection / escape hatch；
- Search / Find / Open 当前不应 hard gate；
- Retrieval 尚有失败，但当前项目不能把所有控制失败重新归咎于 Retriever。

## Evidence → Claim

阅读：

```text
experiments/gap_evidence_claim_loop/FINAL_CONCLUSION.md
experiments/bcplus_verification/FINAL_CONCLUSION.md
```

理解：

- Evidence 与 Claim 必须分开；
- 有 exact useful evidence 时，Writer 对目标 Claim 的 admission 已有较强正向信号；
- contradiction 出现后清除 H 也有较强正向信号；
- 仍存在 scope strengthening，但当前不是唯一主瓶颈。

## Research State / Control

阅读：

```text
experiments/variable_preserving_state/FINAL_CONCLUSION.md
experiments/research_state_v2/FINAL_CONCLUSION.md
experiments/research_state_plan_handoff/FINAL_CONCLUSION.md
experiments/research_state_qualification/FINAL_CONCLUSION.md
experiments/research_state_projection/FINAL_CONCLUSION.md
experiments/research_progress_frontier/FINAL_CONCLUSION.md
experiments/dynamic_progress/FINAL_CONCLUSION.md
experiments/asymmetric_progress/FINAL_CONCLUSION.md
experiments/goal_residual_control/FINAL_CONCLUSION_V2.md
```

理解：

- 更丰富 State 可以局部改变行为，但没有稳定证明应该升级为 persistent control truth；
- Plan / target / source status 可能因为显式出现而放大错误 salience；
- Requirement Map、persistent Frontier、persistent Gap、mandatory Reviewer 尚无充分证据；
- `Q + Verified Claims + provisional H` 仍是当前最合理的 minimal semantic core；
- mechanical Workspace / provenance / trace 不属于 semantic state。

## 当前 Need 实验

必须重点阅读：

```text
experiments/belief_need_convergence/FINAL_CONCLUSION.md
experiments/belief_need_budget_locality_repair/FINAL_CONCLUSION.md
```

理解以下真实结果：

```text
B5 development:
15/16 strict-valid

B5 fresh confirmation:
16/27 strict-valid = 59.26%

valid JSON:
26/27

主要错误：
P = 4
W = 5
A = 1
另有 1 个 reasoning length failure
```

其中：

- P：unsupported presupposition；
- W：多个独立研究目标被打包；
- A：用于定位问题的 referent 自身未 grounded。

不要把历史 `4096 max_tokens` 的 bug 误认为历史真实配置。

历史请求通常省略 `max_tokens`。

当前 Need 正式配置必须沿用已经校准过的可完成输出配置，不允许重新人为加 4096 token 上限。

---

# 2. 当前研究结论必须冻结

本任务开始时采用以下工作假设。

## Persistent semantic state

仍然只有：

```text
Original Question Q
Verified Claims C
Working Hypothesis H
```

形式化：

```text
Belief_t = (Q, C_t, H_t)
```

其中：

### Q
原始问题及其 hard constraints。

### Claims
已经由真实 Observation / Evidence 支持的事实。

### H
候选、猜测、解释方向、可能答案。

H 可以告诉模型：

```text
what is worth testing
```

但不能：

```text
supply a fact
cover a hard constraint
justify STOP
```

---

# 3. 本任务明确禁止增加的 Persistent State

不得为了让实验“更容易成功”而增加：

```text
Requirement Map
OpenNeeds
Dependency Graph
Persistent Need
Persistent Gap
Persistent Frontier
Progress table
Need history
Priority score
done_when state
confidence state
source preference state
candidate schema
relation graph
semantic router state
```

如果你认为某个字段绝对必要：

1. 不要直接实现；
2. 先把它记录成 failure-driven hypothesis；
3. 必须由当前 minimal design 的受控失败支持；
4. 只有在对应 Gate 失败后，才允许设计后续最小干预实验。

---

# 4. 新 Need 的正式定义

不再使用：

```text
Need = one atomic unknown
```

也不要要求：

```text
UnknownCount == 1
```

新的定义是：

> **Need = one coherent, premise-closed, unresolved information objective.**

中文：

> Need 表示当前 Belief 下最值得解决的一个连贯信息缺口。它应足够具体，可以指导下一轮取证；它可以需要一条或多条 Search / Find / Open 动作，但这些动作必须共同服务于同一个研究目标。

Need 必须满足：

```text
Relevant
Unresolved
Grounded
PremiseClosed
Coherent
Actionable
```

---

# 5. PremiseClosed 的定义

这是本任务最重要的机制之一。

Need 中除了真正待调查的未知部分之外，其余用于：

```text
identify the subject
identify the event
bind the relation
locate the target
```

的事实，必须已经由：

```text
Original Question
or
Verified Claims
```

建立。

不能由：

```text
Working Hypothesis
model memory
query guess
candidate speculation
```

提供。

---

## 典型错误

错误：

```text
What year did Jerry Mao win the target championship?
```

如果当前 Claims 只证明：

```text
Jerry Mao won IOI medals
```

而没有证明：

```text
Jerry Mao won the target championship
```

那么 Need 偷渡了：

```text
Won(JerryMao, TargetChampionship)
```

这个未验证关系。

正确当前 Need 应先成为：

```text
Did Jerry Mao win the target championship?
```

---

## 一般规则

如果候选 Need 是：

```text
Attribute(R)?
```

而：

```text
R
```

尚未由 Q / Claims 建立，

则不要问 Attribute。

先问：

```text
Does R hold?
```

这叫：

```text
presupposition closure
```

但不要构造 persistent dependency graph。

这是 one-step local check。

---

# 6. Coherent 的定义

一个 Need 可以包含多个 atomic facts。

不要仅因为：

```text
UnknownCount > 1
```

就判失败。

真正要问的是：

> 这些子问题是否共同服务于同一个主要 research objective / resolution judgment？

---

## 合法 multi-query Need 示例

```text
Did X receive both a bachelor's and a master's degree from University Y?
```

它可能需要：

```text
query 1 -> bachelor's
query 2 -> master's
```

但仍然共同服务于：

```text
EducationCondition(X,Y)?
```

这是一个 coherent Need。

---

## 非法 broad Need 示例

```text
Identify X and verify X's education, spouse, birthplace and promotion history.
```

这里包含多个可以独立完成、独立失败的 research objectives。

这是：

```text
W_independent
```

应判失败。

---

# 7. Need 与 Query 必须严格分层

必须冻结：

```text
Need is semantic.
Query is operational.
```

Need 回答：

```text
What information is currently worth establishing?
```

Query / Action 回答：

```text
What concrete tool call should we make to obtain evidence for that Need?
```

不允许 Need 退化成：

```text
Jerry Mao championship results 2023
```

这只是 Query。

Need 应类似：

```text
Determine whether Jerry Mao won the championship described in the question.
```

---

# 8. 一个 Need 可以产生多条 Query

新的 runtime hypothesis：

```text
Belief
  ↓
Need
  ↓
1..k Search / Find / Open actions
  ↓
Evidence
  ↓
Belief'
```

而不是：

```text
Need
  ↓
one query only
```

多个 Action 必须：

```text
serve the same Need
```

---

## 并行规则

如果：

```text
q1
q2
q3
```

可以在不知道其他 query 结果的情况下正确生成：

```text
q1 || q2 || q3
```

可以同轮 fan-out。

---

## 依赖规则

如果：

```text
q2 = f(answer(q1))
```

则禁止提前实例化 q2。

必须：

```text
q1
→ Evidence
→ Belief'
→ regenerate Need / action
```

不要建立 dependency DAG。

通过执行顺序体现依赖。

---

# 9. 不引入 Need lifecycle

不要增加：

```text
need_status
need_resolved
need_progress
done_when
criterion_status
```

Observation 后：

```text
Evidence → Writer → Claims'/H'
```

然后重新执行：

```text
Q + Claims' + H' → Need'
```

如果原 Need 仍未解决：

- 新 Need 可以保持相同；
- 或变得更窄。

如果已解决：

- 新 Need 应自然转向另一个 unresolved gap。

Claims 本身承担“已经知道什么”的作用。

不要重复存储。

---

# 10. 实验总体结构

实验必须分阶段执行。

不能直接跑完整 end-to-end。

阶段：

```text
E0 旧 W 重新审阅
E1 Belief → Need
E2 Need → Multi-Query Evidence
E3 Reactivation + Closure
E4 final held-out closed loop
```

每一阶段都必须 Gate。

失败后停止，不允许为了“把完整实验跑完”跨 Gate。

---

# 11. E0：重新审阅历史 W

这是 offline、zero-model-cost。

使用 B5 fresh confirmation 中历史标记为：

```text
W = 5
```

的 case。

不要调用模型。

对每个 W 增加以下标签：

```text
objective_count
has_dependency
single_resolution_judgment
multiquery_sufficient
new_label
```

其中：

### W_independent

多个真正独立 research objectives。

### W_multiquery

多个小事实，但共同服务于一个 coherent objective，通过一个 Need + 多 Query 可以合理解决。

输出：

```text
experiments/<new_experiment>/e0_w_reaudit/REVIEW.json
experiments/<new_experiment>/e0_w_reaudit/REPORT.md
```

必须保留旧 label。

不能覆盖历史审阅。

报告必须明确：

```text
旧 W 中有多少真正是 W_independent
有多少按新 rubric 应改判为 valid coherent multi-query Need
```

这是 rubric correction，不是修改历史实验。

---

# 12. E1：Need mechanism ablation

E1 不调用：

```text
Search
Find
Open
Writer
```

只测试：

```text
Q + Claims + H → Need
```

---

## 12.1 Development bank

使用已经暴露的历史 bad cases：

```text
P = 4
A = 1
W cases
```

加一组历史 strict-valid controls。

建议：

```text
16–20 natural states
```

必须覆盖至少多个 qid。

不要把同 qid 多 state 当成独立问题样本。

开发集只用于机制探索。

不得宣称 fresh confirmation。

---

## 12.2 Arms

### B0 — Current B5 baseline

原有：

```text
one unresolved relation
```

不得偷偷更新 prompt。

---

### B1 — Premise Closure only

只加入通用规则：

```text
Do not treat an unverified identity, event, relationship, or candidate-specific fact as a premise of the next question.

If an attribute question would require assuming an unverified event or relation first, investigate whether that event or relation holds before asking for its attribute.

The Working Hypothesis may identify what to test, but it cannot supply a fact.
```

不要加入 coherence / multi-query 规则。

目标：

```text
P ↓
A ↓
```

---

### B2 — Coherent Need only

只加入：

```text
Choose one coherent unresolved research objective.

The objective may require several complementary retrieval queries if they all serve the same research judgment.

Do not bundle independent research objectives that could be resolved separately.
```

不要加入新的 premise closure 文本。

目标：

```text
W_independent ↓
```

---

### B3 — Combined

同时使用 B1 + B2。

这是最终 candidate policy。

---

# 13. E1 输出格式

为了减少 schema confound，输出尽量简单。

建议：

```json
{
  "need": "one natural-language research need"
}
```

不要要求模型输出：

```text
premises
dependency
why
priority
done_when
subquestions
confidence
```

这些可以在 offline reviewer 中分析。

不要为了机械评分让模型显式生成复杂语义结构。

---

# 14. E1 模型配置

沿用 Belief Need Budget Locality Repair 已校准的配置：

```text
temperature = 0
JSON mode
max_retries = 0
omit max_tokens
```

不要人为加回 4096 completion limit。

记录：

```text
input tokens
output tokens
reasoning tokens
finish_reason
latency
cache hit/miss
```

失败保留。

不 retry semantic failure。

---

# 15. E1 rubric

Primary strict validity：

```text
Relevant
Unresolved
Grounded
PremiseClosed
Coherent
Actionable
valid output
```

一个 Need 只有全部满足才 strict-valid。

---

## Diagnostic labels

```text
P = unsupported presupposition
A = ungrounded referent
W = independent research objectives bundled
Q = need collapsed into query-like keywords
S = already-supported / stale need
R = unrelated / invented target
X = execution failure
```

注意：

```text
multiple atomic facts
```

本身不再自动算 W。

Reviewer 必须先判断：

```text
single coherent resolution objective?
```

---

# 16. E1 development 的机制判定

希望看到的模式：

```text
B1:
P/A 明显下降
W 基本不变

B2:
W 明显下降
P/A 基本不变

B3:
两者同时下降
```

如果不是这个模式，不要急着 fresh-confirm。

必须先分析：

```text
机制是否真的分离
prompt 是否同时影响多个维度
旧 rubric 是否不适用
```

只允许一次 bounded development revision。

不能无限 prompt sweep。

---

# 17. E1 Fresh Confirmation

Development 冻结后：

必须使用：

```text
12–15 completely new qids
30–40 natural QCH states
```

这些 qid 不能出现在：

```text
B5 development
B5 confirmation
本轮 E1 development
Need Review
相关 prompt 调参材料
```

需要在请求前 freeze：

```text
qid list
QCH
Claim support audit
H origin
rubric
prompts
model config
request schedule
```

然后 commit。

---

## Fresh 必须覆盖

尽量包含：

```text
candidate known / relation unknown
relation unknown / downstream attribute tempting
identity unknown / property tempting
No-H discovery
legitimate coherent multi-query Need
true multi-objective broad Need
strong-H but uncovered constraint
```

不要人工写 Claims 补足样本。

优先使用真实历史/自然采集的 QCH。

---

# 18. E1 Fresh Gate

这些是工程研究 Gate，不称统计显著性。

B3 至少满足：

```text
strict-valid >= 80%
```

同时：

```text
P + A <= 5%
W_independent <= 10%
```

且相对 B0：

```text
strict-valid improvement >= 15 percentage points
```

No-H 单独报告。

如果 B3 不满足：

```text
STOP
```

不得进入 E2 autonomous connection。

可以继续分析失败原因，但不要跑最终 closed loop。

---

# 19. E2：Need → Query Fan-out

只有 E1 Gate 通过才执行。

E2 必须隔离：

```text
Need → Query / Evidence
```

因此：

**不要让 E2 使用模型自己生成的 Need。**

使用冻结并人工审核为 strict-valid 的 Need。

---

# 20. E2 Need bank

建议：

```text
20–30 Needs
```

覆盖：

### Type S — single-facet

一条 query 可能足够。

### Type M — coherent multi-facet

多个 complementary query 可能合理。

例如：

```text
Does X satisfy both education conditions A and B?
```

不要放真正 broad multi-objective Need。

---

# 21. E2 Query arms

第一轮只测试 Search。

不要一开始就混入 Find/Open。

---

### Q0 — single query

模型输入：

```text
Need
```

输出：

```text
one search query
```

执行：

```text
Search top6
```

---

### Q1 — multi-query

模型输入完全相同 Need。

允许最多：

```text
3 queries
```

但保持等预算：

```text
3 × top2
```

总 result slots：

```text
6
```

与 Q0：

```text
1 × top6
```

相同。

不得因为 Q1 多执行 3 倍 retrieval budget 而获得虚假收益。

---

# 22. E2 Query prompt 原则

Query generator 只负责：

```text
operational retrieval expression
```

允许：

```text
paraphrase
synonyms
source vocabulary
different lexical entry points
complementary query formulations
```

不允许：

```text
change subject
change relation direction
invent a fixed year from a range
promote H into fact
add unrelated original-question constraints
turn a speculative term into a Claim
```

---

# 23. E2 主要指标

Primary：

```text
UsefulEvidence@FixedBudget
```

定义：

> 相同 retrieval/display budget 下，是否取得足以支持或反驳当前 Need 的真实 Evidence。

同时记录：

```text
Need fidelity
Query semantic drift
Evidence coverage
Unique useful sources
Query redundancy
Result overlap
Unsupported assumption added in query
API tokens
retrieval cost
latency
```

multi-query 本身不是成功。

只有 Evidence yield / coverage 提升才算成功。

---

# 24. E2 Gate

工程参考线：

在 Type M 上：

```text
Q1 UsefulEvidence 至少比 Q0 提高 15pp
```

且：

```text
semantic drift 不明显增加
```

Type S 上：

```text
不得出现明显退化
```

如果 multi-query 没有稳定收益：

```text
不要保留 fan-out
```

回到：

```text
Need → one action → Evidence → replan
```

简单方案优先。

---

# 25. E2 第二阶段：真实 ActionBatch

只有 Search-only fan-out 有正信号后才运行。

Actor 输入：

```text
Need
Workspace directory / available D#/W#
Recent mechanical attempts
```

不要重新给它完整 Q + Claims + H 去解释一次任务。

允许输出：

```text
1..k Search / Find / Open actions
```

合同：

```text
All actions must serve the current Need.

Independent actions may be issued together.

If one action requires another action's result, do not issue the dependent action yet.
```

Search 始终可用。

Find/Open 不 hard gate。

---

# 26. E3：Reactivation + Closure

只有：

```text
E1 PASS
E2 PASS
```

后执行。

这一阶段专门测试 minimal state 是否真的足够长期控制。

---

## 核心状态类型

需要大量：

```text
strong candidate H
most hard constraints covered
exactly one or very few material constraints still uncovered
```

也就是 near-closure / strong-H one-gap states。

当前历史这类样本不足，所以必须重新收集。

---

## E3 测试两个问题

### Reactivation

一个之前暂时没有研究的 hard constraint：

是否能从：

```text
Q + Claims + H
```

重新被派生为 Need？

---

### Closure

强候选存在时：

系统是否仍然拒绝 premature STOP？

STOP 必须满足：

```text
all material hard constraints supported by Claims
+
final requested relation supported or strictly entailed
```

H 不算 coverage。

---

# 27. ACT / STOP 必须分离

ACT：

```text
只需要找到一个有用 unresolved issue
```

形式：

```text
exists useful unresolved gap
```

STOP：

```text
必须全局 closure
```

形式：

```text
forall material requirements, covered
```

不要把完整 closure audit 塞进每一次 Need 生成。

---

# 28. E4：Final Held-Out Loop

只有前三个 Gate 全部通过后才运行。

使用：

```text
10–15 completely held-out qids
```

执行：

```text
Q
→ Need
→ 1..k Actions
→ Evidence
→ Writer
→ Claims/H update
→ rederive Need
→ ...
→ strict closure
→ final answer
```

---

# 29. Final metrics

不要只报 Accuracy。

至少：

```text
Strict final resolution
Final answer correctness
Premature STOP
Missed STOP
Need strict-valid rate
Unsupported Claim rate
Hypothesis promotion rate
Useful Evidence / tool call
Repeated Need
Repeated Search
Query redundancy
Total model calls
Total tool calls
Input/output/reasoning tokens
Cache hit/miss
Wall-clock
Execution failures
```

---

# 30. Failure-driven escalation rule

如果 minimal design 失败，才允许考虑更复杂结构。

---

## 如果 Premise Closure 仍失败

才允许设计：

```text
ephemeral premise extraction
```

但不要直接做 dependency graph。

---

## 如果 Coherence 仍失败

才允许测试：

```text
tiny ephemeral subquestion decomposition
```

但不要持久化 Frontier。

---

## 如果 E2 fan-out 无收益

删除 multi-query。

---

## 如果 E3 reactivation 失败

这才是第一个真正支持：

```text
Q + Claims 不足以恢复 deferred requirements
```

的证据。

到那时才允许讨论：

```text
OpenNeeds
Requirement representation
```

---

## 如果 Closure 失败

单独研究 Closure。

不要因此给每轮 Need 加 Full Requirement Map。

---

# 31. 代码与目录要求

创建独立新实验目录。

建议：

```text
experiments/minimal_need_multiquery/
```

至少：

```text
README.md
TASK.md
PROTOCOL.md
HYPOTHESES.md
FROZEN_STATE.md
CONFIG.json

prompts/
  b0.txt
  b1_premise.txt
  b2_coherent.txt
  b3_combined.txt
  query_single.txt
  query_multi.txt

e0_w_reaudit/
e1_need/
e2_query/
e3_closure/
e4_loop/

analysis/
```

历史目录只读。

不要修改旧实验结果。

---

# 32. Freeze 纪律

每个真实模型调用阶段之前：

1. 写 Protocol；
2. 写 Hypotheses；
3. 锁定 bank；
4. 锁定 prompt；
5. 锁定 rubric；
6. 锁定 config；
7. 锁定 schedule；
8. commit；
9. 记录 exact HEAD；
10. 才允许发送调用。

调用开始后：

```text
no prompt editing
no sample replacement
no cherry-picking
no hidden retry
no best-of
no silent repair
```

格式 transport repair 如必须发生：

必须：

```text
单独版本
单独 freeze
单独报告
```

---

# 33. Freshness 纪律

一旦查看过模型输出并用于：

```text
设计 prompt
修改 rubric
选择机制
解释 bad case
```

该 case：

```text
永远不再属于 fresh confirmation
```

不能因为换了模型或换了 prompt 就重新称 fresh。

---

# 34. 失败必须保留

保留：

```text
HTTP errors
schema errors
length failures
timeouts
empty outputs
invalid JSON
tool errors
reasoning exhaustion
auth errors
```

不能从 denominator 删除。

---

# 35. 真实付费调用授权

如果当前用户任务没有明确授权真实付费模型调用：

你必须先完成：

```text
design
implementation
offline tests
bank freeze
prompt freeze
dry run
cost/call-count estimate
```

然后停在：

```text
PREPARED_FOR_REAL_RUN
```

不要擅自发送真实外部 API 调用。

如果用户已在当前任务中明确授权真实调用，则按 Gate 执行。

---

# 36. 不要追求“把所有阶段跑完”

这是本任务最重要的执行纪律之一。

如果：

```text
E1 FAIL
```

就停。

不要为了完整报告继续跑 E2/E3/E4。

如果：

```text
E2 FAIL
```

就停。

这是 gated research，不是 benchmark marathon。

---

# 37. 最终需要回答的研究问题

最终报告必须明确回答：

1. 旧 B5 的 W 中有多少其实是 legitimate multi-query Need？
2. Premise Closure 是否定向减少 P/A？
3. Coherent Need 是否定向减少真正的 W？
4. 两者结合是否在 completely fresh QCH 上复制？
5. Need 是否可以保持一个自然语言字段，而不增加 persistent semantic state？
6. 一个 Need fan-out 到多 Query 是否在等预算下提高 useful evidence？
7. multi-query 是否增加 semantic drift 或重复检索？
8. Need→Action 是否需要 Probe / NeedSpec / ResolutionCriterion？
9. 是否出现证据要求 persistent dependency graph？
10. Q + Claims + H 是否足以重新激活 deferred hard constraints？
11. 强 H 是否仍导致 premature closure？
12. strict Closure 能否在 near-closure fresh states 上工作？
13. 最小闭环是否能在完全 held-out qids 上运行？
14. 如果失败，失败发生在哪一层？
15. 哪些额外结构是真正被 failure-driven evidence 要求的？

---

# 38. 当前目标架构

除非实验明确推翻，最终目标仍是：

```text
PERSISTENT SEMANTIC STATE
─────────────────────────
Original Question
Verified Claims
Working Hypothesis


EPHEMERAL CONTROL
─────────────────────────
Current Need


ACTION LAYER
─────────────────────────
1..k Search / Find / Open


MECHANICAL HARNESS
─────────────────────────
D# / W#
Evidence Pointer
provenance
offsets
Workspace
Trace
attempt history
budget
schema
execution reliability
```

核心闭环：

```text
Belief(Q,C,H)
→ Need
→ Evidence Acquisition
→ Writer
→ Belief'
→ Need'
→ ...
→ Strict Closure
```

---

# 39. 设计哲学

始终遵守：

> **Strong structured control, weak structured semantics.**

Harness 应该强管理：

```text
execution
provenance
addressing
budget
trace
schema
recovery
```

模型应该负责：

```text
understanding Q
interpreting Claims
maintaining provisional H
choosing current Need
deciding useful research direction
```

不要把模型的语义判断过早冻结成 Harness truth。

---

# 40. 完成标准

你的工作不是“实现了代码”就结束。

每阶段必须产生：

```text
protocol
frozen inputs
raw outputs
machine-readable metrics
semantic review
integrity audit
cost/accounting
failure taxonomy
final gated conclusion
```

最终结论必须区分：

```text
observed fact
diagnostic interpretation
hypothesis
engineering recommendation
unmeasured question
```

不要因为一个机制“看起来合理”就宣布成功。

不要因为某个复杂组件“理论上有用”就实现。

**只让真实 failure 推动架构增加复杂度。**