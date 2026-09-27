# Search-ESR：Local Obligation Context Sufficiency Ablation

## 0. 实验目的

你正在继续 `homulillew/Search-ESR` 的 Research Control 研究。

本轮不是新的 Obligation prompt revision，也不是 Candidate Obligation decomposition。

本轮只验证：

> **当前 `Q + Verified Claims → Local Obligation` 表现差，是否部分因为 Verified Claims 只表达“现在知道什么”，却没有表达“研究刚刚如何推进到这里、当前 frontier 在哪里”？**

当前待检验的核心模型为：

\[
O_t=f(Q,C_t)
\]

对比：

\[
O_t=f(Q,C_t,P_t)
\]

其中：

- \(Q\)：Original Question；
- \(C_t\)：当前 Verified Claims；
- \(P_t\)：紧凑、机械、prefix-only 的 recent research-path context。

本轮尤其要区分：

\[
\boxed{
\text{Epistemic State}
\neq
\text{Frontier / Path Signal}
}
\]

即：

> Claims 可能已经足够告诉模型“什么成立/不成立”，但未必足够告诉模型“当前最自然应该继续哪一个 branch”。

---

# 1. 当前远程研究锚点

开始前必须：

```bash
git fetch origin --prune
git status
git branch --show-current

git rev-parse origin/main
git rev-parse origin/experiment/evidence-gap-gold-obligation
git rev-parse origin/experiment/dynamic-local-obligation

git log --oneline --decorate -20 \
  origin/experiment/dynamic-local-obligation
```

任务编写时最新状态：

```text
main
8021aca19a1ee5201730e40b338012c65ecd51cf

experiment/evidence-gap-gold-obligation
fb61da13d3be2511f37da590429ebea7f706bd0d

experiment/dynamic-local-obligation
8562c166326417e73be1eadb3b891b7c5769b0ad
```

其中最新研究提交：

```text
8562c166326417e73be1eadb3b891b7c5769b0ad
Report dynamic obligation failure, preserve scope diagnostics and close cascade gate
```

如果 fetch 后远程已经前移：

1. 先完整阅读新 commit；
2. 判断是否已经执行了本任务相同或冲突的 experiment；
3. 写入 `PRE_EXECUTION_AUDIT.md`；
4. 不允许忽略更新继续使用旧假设。

---

# 2. 新建独立实验分支

从真实最新：

```text
origin/experiment/dynamic-local-obligation
```

创建：

```bash
git switch -c experiment/obligation-context-sufficiency \
  origin/experiment/dynamic-local-obligation
```

新目录：

```text
experiments/obligation_context_sufficiency/
```

历史实验全部只读。

尤其不得修改：

```text
experiments/dynamic_local_obligation/
experiments/evidence_gap_gold_obligation/
experiments/need_premise_audit/
```

---

# 3. 为什么现在做这个实验

最近两轮已经形成：

\[
GoldO+C\rightarrow Gap
\]

开发阶段通过：

```text
Strict Gap Validity = 50/54 = 92.6%
```

而：

\[
Q+C\rightarrow O
\]

只有：

```text
Strict Obligation Validity = 29/54 = 53.7%
```

Dynamic O 的主要错误：

```text
whole-question / bundled broadness = 15/54 = 27.8%
downstream obligation              = 11/54 = 20.4%
wrong relation arguments           =  4/54 =  7.4%
already supported                  =  1/54 =  1.9%
```

同时：

```text
GoalGrounded = 54/54
Unresolved   = 53/54
Material     = 54/54
```

因此当前 evidence 支持：

> 模型基本知道 Q 在研究什么，也基本知道哪些内容仍未解决。

但是它不能稳定地：

> 从完整 Q 中选出当前合适的局部研究 focus。

当前存在两个仍未分离的解释：

### Explanation A — Frontier blindness

Claims 只保留 epistemic result：

```text
what is known
```

却丢失：

```text
what was just investigated
what just changed
which branch is currently active
```

因此模型每轮都像“半初始化”一样重新扫描整个 Q。

### Explanation B — Semantic projection bottleneck

即使 frontier 信息充分，

模型从全局 Q 压缩到自然语言 Local Obligation 时仍会：

```text
改 relation arguments
改变 object/date attachment
跳过依赖
重述整题
```

本实验只用于区分 A 与 B 的相对作用。

---

# 4. 本轮明确不是要证明什么

不要把本轮目标写成：

> “证明更多上下文能解决 Obligation generation。”

也不要写成：

> “证明 history 越长越好。”

正确问题是：

\[
\boxed{
\text{Does compact research-path context improve local obligation projection
beyond the current evidence state?}
}
\]

中文：

> **在当前 Verified Claims 已经给定的情况下，增加紧凑、机械、非推测性的 recent-path signal，是否能够改善 Local Obligation 的局部性、选择稳定性和 scope fidelity？**

---

# 5. 本轮保持不变的所有东西

必须冻结：

```text
被测模型
temperature
JSON mode
max_tokens policy
retry policy
Obligation system instruction
output schema
27-state development bank
semantic rubric
error taxonomy
review procedure
```

本轮唯一 intervention：

```text
Recent Context block
```

不得同时：

- 改 Obligation prompt 原则；
- 新增 Candidate Obligations；
- 新增 Binding parser；
- 新增 depends_on；
- 改 Gold；
- 改评分标准；
- 调 Search；
- 改 Gap Generator。

---

# 6. 被测模型

继续：

```text
model = deepseek-flash
temperature = 0
JSON mode
max_retries = 0
omit max_tokens
```

Codex GPT-6 只负责：

```text
实验编排
reference construction
审阅
统计
Git 记录
```

不能替换被测模型。

---

# 7. 开发 bank

第一阶段直接复用上一轮：

```text
27 natural historical states
10 question clusters
```

即：

```text
experiments/dynamic_local_obligation/e0_reference/
```

对应完全相同的：

```text
Original Question
Verified Claims
historical state identity
Gold Obligation reference
```

不要重新抽样。

这样：

```text
C0 concurrent
```

可直接回答当前 branch 上 baseline 是否复制上一轮约 53.7%。

---

# 8. 为什么仍然需要 concurrent C0

不能只把旧：

```text
29/54 = 53.7%
```

作为 baseline。

已经多次观察到：

```text
temperature=0
```

仍有 run/provider variation。

所以四个 context arms 必须在同一 execution window 中混排。

旧 53.7% 只能作为：

```text
historical descriptive comparator
```

不能作为新实验的正式对照。

---

# 9. 首先构造 Prefix Source Map

任何模型调用之前，必须为 27 个 state 找到其**精确历史来源 prefix**。

生成：

```text
e0_context/
SOURCE_MAP.json
```

每条至少包含：

```json
{
  "case_id": "Gxx",
  "state_id": "Fxx_Sxx",

  "source_run": "...",
  "source_file": "...",
  "source_event_index": 123,

  "question_hash": "...",
  "claims_hash": "...",

  "prefix_start": "...",
  "prefix_end": "...",

  "has_previous_checkpoint": true,
  "has_recent_path": true,
  "has_recent_observation": true
}
```

必须验证：

```text
当前实验 Q
==
历史 prefix 当时真实 Q
```

以及：

```text
当前实验 Claims
==
该 prefix 当时已有 Claims
```

不得通过相似内容猜测映射。

---

# 10. Prefix-only 是硬约束

所有：

```text
Claim Delta
RecentPath
RecentEvidence
```

只能来自：

\[
\text{events before or at current state checkpoint}
\]

绝对禁止读取：

```text
future Search
future Open
future Claims
later Hypothesis
gold answer
later successful branch
future Writer output
future reviewer judgment
```

要自动写：

```text
PREFIX_LEAKAGE_AUDIT.json
```

至少检查时间/step index。

---

# 11. 四个实验 Arms

本轮采用嵌套 context ablation。

---

## C0 — Epistemic Baseline

输入：

\[
Q+C
\]

附加 Context block 保持存在，但三个字段全部为空：

```json
{
  "recent_context": {
    "recent_claim_delta": [],
    "recent_events": [],
    "recent_observations": []
  }
}
```

这就是 concurrent baseline。

---

## CΔ — Recent Claim Delta

输入：

\[
Q+C+\Delta C
\]

其中：

\[
\Delta C=C_t-C_{previous}
\]

只增加：

```text
最近一次状态推进新增了哪些 Claims
```

其他 context 为空。

例如：

```json
{
  "recent_context": {
    "recent_claim_delta": [
      {
        "claim_id": "C7",
        "statement": "..."
      }
    ],
    "recent_events": [],
    "recent_observations": []
  }
}
```

---

# 12. Recent Claim Delta 必须机械构造

不能由 reviewer 写：

```text
We just established X but still know nothing about Y.
```

因为这已经泄漏 frontier。

只允许：

```text
Current claims - previous checkpoint claims
```

按 exact statement identity 或已有 canonical claim identity 计算。

如果没有 previous checkpoint：

```json
"recent_claim_delta": []
```

同时标：

```text
delta_context_available = false
```

不得人工补一句解释。

---

# 13. CΔ 真正测试什么

它测试的不是 history。

而是：

\[
\boxed{
\text{是否只需要一个 recency/state-transition signal}
}
\]

例如：

> 模型是不是只要知道“C7 是刚刚新得到的”，就更容易理解研究现在推进到了哪里。

如果 CΔ 已经达到 C1 效果：

就没有理由维护更复杂 Path。

---

# 14. C1 — Compact Mechanical Recent Path

输入：

\[
Q+C+\Delta C+P
\]

在 CΔ 基础上增加：

```text
最近最多 4 个 research-control events
```

必须来自真实历史。

建议 event 类型只允许：

```text
Search
Find
Open
Verify       # 如果真实历史存在
WriterUpdate # 如果真实历史存在
```

不要加入：

```text
LLM reasoning
rationale
chain of thought
manual reviewer note
```

---

# 15. RecentPath 的结构

建议统一：

```json
{
  "step_offset": -2,
  "event_type": "Search",
  "argument": {
    "query": "..."
  },
  "observed_refs": ["D14", "D19"],
  "claim_delta": []
}
```

或者：

```json
{
  "step_offset": -1,
  "event_type": "Open",
  "argument": {
    "document": "D14"
  },
  "observed_refs": ["W8"],
  "claim_delta": ["C7"]
}
```

只保存真实 Harness 字段。

---

# 16. 不允许把 Path 变成 semantic summary

禁止：

```text
The previous search failed to find Marwaha's later article.
```

除非这是历史系统已经有的明确机械状态。

默认只允许：

```text
Search(query X)
returned D1,D2
claim delta = none
```

不要从：

```text
claim_delta = none
```

人工推导：

> “证明了没有 later article”。

---

# 17. Past Action 永远不是 Evidence

System prompt 必须明确：

> Recent Context describes previous control actions and observations.  
> Past queries, opened documents, search arguments and prior attempted directions are NOT verified facts.

也就是说：

\[
Query_{past}\notin Evidence
\]

\[
DocumentSeen\not\Rightarrow ClaimSupported
\]

只有：

```text
Verified Claims
```

具有 epistemic support status。

---

# 18. C2 — Recent Path + Raw Local Observation Context

输入：

\[
Q+C+\Delta C+P+E_{recent}
\]

C2 在 C1 基础上加入最近局部 Observation。

目的：

> 测试 Claims 压缩后是否丢失了对当前对象/来源/关系 continuity 有价值的局部文本。

---

# 19. Recent Observation 不允许人工总结

不要加入：

```text
D18 does not establish a later article.
```

除非这本来就是可验证的 Claim。

应该加入：

```json
{
  "observation_ref": "W8",
  "source_ref": "D14",
  "text": "<exact historical visible observation text>"
}
```

必须是 prefix 中模型当时真实可见的内容。

不得：

- paraphrase；
- reviewer summarize；
- 加结论；
- 补上下文；
- 使用以后打开到的页面。

---

# 20. Recent Observation 的选择必须完全机械

最多取：

```text
最近 2 个 observation blocks
```

选择顺序：

```text
most recent first
```

只取与最近 Path 中：

```text
Search / Find / Open
```

真实对应的 observation。

不要按：

```text
哪个更相关
哪个后来证明有用
哪个与 Gold O 接近
```

做人工筛选。

---

# 21. Context 大小限制

本轮不是 long-context 实验。

建议：

```text
recent events <= 4
recent observation blocks <= 2
```

Recent observation 使用历史已经显示给 Actor 的原始 bounded text。

如果某 observation 异常大：

使用在历史 Actor 输入中的**实际可见版本**，

不要重新读取全文。

目标：

\[
\boxed{
compact\ local\ path
}
\]

不是：

\[
full\ trajectory
\]

---

# 22. Context availability 分层

并非每个 state 都一定有：

```text
previous checkpoint
recent event
recent observation
```

不能因此删除 state。

所有 27 states 必须保留。

另外机械报告：

```text
delta-eligible states
path-eligible states
observation-eligible states
```

Primary overall：

```text
all 27
```

同时分别报告 matched eligible subsets。

这样避免：

> 很多空 context 把真实 Path effect 稀释掉。

---

# 23. 四个 Arms 的输入必须完全同 schema

不要让 prompt surface 产生额外 confound。

所有 user payload 均为：

```json
{
  "Original Question": "...",

  "Verified Claims": [
    {
      "claim_id": "C1",
      "statement": "..."
    }
  ],

  "Recent Context": {
    "recent_claim_delta": [],
    "recent_events": [],
    "recent_observations": []
  }
}
```

区别只在数组内容。

---

# 24. 不向模型暴露 arm 名

绝对不能出现：

```text
C0
Cdelta
C1
C2
baseline
path condition
evidence condition
```

模型只看：

```text
Recent Context
```

为空或非空。

---

# 25. 全部 arms 使用完全相同的 System Prompt

不要像上一轮 O0/O1 一样为不同 arm 加额外 instruction。

本轮唯一变量必须是 context 内容。

使用下面统一 prompt。

---

# 26. Unified Obligation Prompt

```text
You derive one current Local Obligation for a research task.

You receive:

1. the Original Question;
2. the current Verified Claims;
3. optional Recent Context describing recent research activity.

Choose ONE unresolved Local Obligation that would materially advance
answering the Original Question.

A Local Obligation states what information must still be established,
not how to search for it.

The Recent Context may help you understand where the research has
recently focused or changed.

IMPORTANT:
Recent Context is NOT evidence.

Past searches, query wording, opened documents, attempted directions,
and raw observations must not be treated as established facts merely
because they appear in Recent Context.

Only Verified Claims determine what is already established.

The Original Question determines what the research is required to answer.

Requirements:

1. The obligation must come directly from the Original Question.

2. Use the Verified Claims to determine what is already established.
Do not ask to establish something that the Claims already sufficiently support.

3. Use Recent Context only as a frontier/locality signal.
It may help identify what branch has just been investigated,
but it must not create a new requirement or establish a fact.

4. Choose one local coherent research objective.
It does not need to be logically atomic.
Several complementary conditions may remain together when they jointly
identify or verify one object, event, or relation.

5. Do not bundle independent research objectives merely because they
eventually contribute to the same final answer.

6. An unknown entity, event, relation, or value may itself be what the
obligation asks to discover or verify.
Do not require the current unknown to already be established.

7. Do not jump to a downstream attribute when the referenced entity,
event, relation, document, or source has not yet been sufficiently
identified or established by the Verified Claims.

In that case, choose the identifying, existence, or relation obligation first.

8. Preserve relation scope exactly.

Do not change:
- which entity participates in a relation;
- which event a date belongs to;
- which person has a role;
- which two entities are being compared;
- which object owns an attribute.

Do not silently merge or split two roles unless the Original Question
or Verified Claims establishes that relation.

9. Do not use outside knowledge.

10. Do not output a search query, source preference, plan, hypothesis,
confidence, rationale, requirement list, coverage audit, or STOP decision.

Finding one useful unresolved obligation is sufficient.

Return only JSON:

{
  "obligation": "one natural-language Local Obligation"
}
```

---

# 27. 不给 H

四个 arms 都不输入：

```text
Working Hypothesis
```

原因：

本轮 intervention 只有：

```text
Recent Context
```

不要重新引入 H confound。

H 仍然保留在长期架构假设中：

```text
Gap + H + Workspace → Action
```

但不参与本轮实验。

---

# 28. 输出 schema

严格只有：

```json
{
  "obligation": "..."
}
```

不能多：

```text
basis_refs
reason
target
mode
depends_on
confidence
```

因为本轮仍然是在测与上一实验完全相同的 Obligation output。

---

# 29. 调用规模

如果：

```text
27 states
4 arms
2 independent replicates
```

则：

\[
27\times4\times2=216
\]

个真实 model calls。

全部混合在一个 deterministic shuffled schedule 中。

建议：

```text
max concurrency = 8
```

与历史保持可比。

---

# 30. 真实调用前必须先准备但不默认执行

用户要求的任务书本身不自动构成无限网络付费授权。

先完成：

```text
reference/context reconstruction
prefix audit
prompt freeze
schema tests
schedule
estimated call/tokens
dry run
provider preflight
```

生成：

```text
PREPARED_FOR_EXECUTION
```

如果当前任务环境已经有明确、适用、仍有效的用户 API 授权，按现有项目规则执行。

否则在真实 paid calls 前停止并记录。

---

# 31. Provider preflight

必须检查：

```text
JSON literal present
endpoint
model
temperature
response_format
omit max_tokens
retry = 0
payload serialization
all 216 IDs unique
all output paths unique
no arm leakage
no H leakage
no Gold leakage
prefix-only context
```

任何失败：

```text
STOP_BEFORE_PAID_CALL
```

---

# 32. First-pass review 完全沿用上一轮 rubric

不要为了适配 Context 结果重新定义“好 Obligation”。

继续使用八维：

```text
GoalGrounded
Unresolved
Material
Local
Coherent
ScopeFaithful
NonDownstream
EvidenceResolvable
```

Strict：

```text
all 8 true + schema valid
```

---

# 33. Error taxonomy 也冻结沿用

至少保持：

```text
downstream_obligation
already_supported
whole_question_restatement
over_atomic
invented_requirement
wrong_object_scope
wrong_relation_arguments
relation_strengthening
irrelevant_low_value
unresolved_referent
bundled_objectives
outside_knowledge
```

不要在看到结果后重新定义类别。

---

# 34. 新增的 context-specific labels 只做 second pass

第一次 semantic review 时：

Reviewer 只看：

```text
Q
Claims
Generated Obligation
```

不要看：

```text
arm
Recent Context
replicate
historical Gold
aggregate metrics
```

完成 strict/error labels 并 commit。

之后才揭示 Recent Context，并做第二轮 context audit。

---

# 35. Second-pass 新增 Context Contamination 标签

只在揭盲后检查：

### path_fact_promotion

Obligation 把：

```text
past query / path event / raw observation
```

中的内容当成已建立事实。

---

### path_created_requirement

Recent Context 中出现的内容：

```text
不属于 Q requirement
```

却进入了 Obligation。

---

### path_candidate_hardening

过去 Search query 中的候选值被升级成：

```text
固定 subject / event / relation
```

而 Q/C 没有支持。

---

### observation_overreach

raw observation 中未经 Writer/Claims 接纳的内容被当成事实使用。

---

# 36. Primary metrics 不只看 Strict

每个 arm 必须报告：

```text
Strict Obligation Validity
GoalGrounded
Unresolved
Local
Coherent
ScopeFaithful
NonDownstream
EvidenceResolvable
Schema Validity
Stable both-valid same/compatible
```

以及 errors：

```text
Broadness union
Downstream
Wrong relation arguments
Wrong object scope
Relation strengthening
Already-supported
Unresolved referent
```

---

# 37. Primary 表必须长这样

```text
| Context | Strict | Broad | Downstream | RelationArg | Scope | Stable |
|---------|--------|-------|------------|-------------|-------|--------|
| C0      |        |       |            |             |       |        |
| CΔ      |        |       |            |             |       |        |
| C1      |        |       |            |             |       |        |
| C2      |        |       |            |             |       |        |
```

这个表比单独一个总准确率更重要。

---

# 38. Replicate 分析

每个：

```text
state × arm
```

两次输出分类：

```text
same_obligation
compatible_obligation
different_but_valid
one_valid_one_invalid
both_invalid
```

继续沿用上一轮。

特别报告：

```text
both strict valid
stable same/compatible
```

Path 如果真的帮助 frontier localization：

应该主要表现为：

\[
stable\ selection\uparrow
\]

---

# 39. Primary Hypothesis H1 — Frontier Localization

预注册：

\[
\boxed{
Compact\ path\ context
\rightarrow
lower\ broadness
}
\]

具体预测：

```text
C1 broadness < concurrent C0 broadness
```

并希望：

```text
C1 stable-selection > C0
```

这是真正最核心的 Path hypothesis。

---

# 40. H2 — Delta Sufficiency

测试：

\[
C_\Delta
\]

是否已经获得 C1 大部分收益。

如果：

```text
CΔ ≈ C1
```

说明系统可能不需要 Pathway Memory。

只需要：

```text
recent state transition signal
```

这会是更简单、更优先的工程方案。

---

# 41. H3 — Downstream Error

预注册不做过强预测。

当前假设：

```text
Path may improve downstream jump modestly,
but large improvement is not expected.
```

因为 Marwaha 类状态：

```text
Claims
```

本身已经告诉模型 later article 尚未建立。

所以 downstream failure 不完全是 path blindness。

---

# 42. H4 — Relation Fidelity Negative Prediction

预注册：

\[
\boxed{
Path\ context\ does\ not\ substantially\ repair
relation-argument corruption
}
\]

也就是预计：

```text
wrong_relation_arguments
```

不会因为 C1/C2 明显下降。

这是有价值的负预测。

---

# 43. H5 — Recent Evidence

C2 是 exploratory-diagnostic，但同样冻结。

可能出现：

### Benefit

recent observation 保留局部 referent continuity，

减少 broadness 或 unresolved referent。

### Harm

增加 entity salience，

导致：

```text
wrong attachment
candidate hardening
relation corruption
```

不要预设方向。

---

# 44. Overall Primary Comparison

正式 baseline：

```text
concurrent C0
```

不要拿历史 53.7% 直接算 improvement。

报告：

\[
\Delta Strict(C_x-C_0)
\]

\[
\Delta Broad(C_x-C_0)
\]

\[
\Delta Downstream(C_x-C_0)
\]

\[
\Delta RelationArg(C_x-C_0)
\]

\[
\Delta Stability(C_x-C_0)
\]

---

# 45. Eligibility subset metrics

除了全部 27 states，还必须报告：

### Δ-eligible

有真实 previous checkpoint / nonempty mechanically derived delta 的 states。

### Path-eligible

至少有 1 个合法 prefix path event。

### Observation-eligible

至少有 1 个 prefix observation block。

例如：

```text
C1 vs C0 on path-eligible states
```

才是真正衡量 Path。

不能因为大量：

```text
empty Recent Context
```

把效应稀释后得出：

> Path 无效。

---

# 46. 但 eligibility 规则必须调用前冻结

不能看到结果以后再：

```text
“这些状态路径比较完整，所以只看这些。”
```

资格必须完全机械：

```text
has event before state checkpoint?
has observation before state checkpoint?
```

调用前 freeze。

---

# 47. 本轮不以单一 PASS/FAIL 掩盖诊断

这是一个 mechanism experiment。

因此不要只输出：

```text
PASS
FAIL
```

至少给出两个层次。

---

# 48. Mechanism Signal

建议预注册：

Context 被认为具有有意义的 frontier signal，如果满足至少：

```text
Strict improvement >= 10 percentage points
OR
Broadness reduction >= 10 percentage points
OR
Stable-selection improvement >= 15 percentage points
```

并且：

```text
Wrong-relation-argument error
不得恶化 > 5 percentage points
```

这些只是 engineering thresholds，不是统计显著性声明。

---

# 49. Direct-O Viability Signal

如果某个 compact-context arm 同时达到大致：

```text
Strict >= 75%

Broadness <= 15%

Downstream <= 15%

ScopeFaithful >= 85%

Stable same/compatible >= 65%

Wrong relation arguments <= 7.5%
```

可以将：

```text
Q + C + compact path → one O
```

视为一个“值得继续工程验证”的方案。

不要求完美 90–100%。

---

# 50. 为什么这里可以低于过去 80% Gate

本轮不是生产部署。

而且用户明确不要求完美。

Local Obligation 是可重算的 ephemeral control。

因此一个：

```text
75–80%
```

左右、且重大 structural error 受控的方案，

可能已经值得进入更真实的小 loop。

但这只是 future qualification signal。

本轮仍只完成 context mechanism 分析。

---

# 51. Decision Rule A — CΔ 已经够用

如果：

```text
CΔ 明显改善 C0
```

而：

```text
C1 ≈ CΔ
C2 ≈ C1
```

则结论：

> 缺失的不是 full research history，而主要是 state-transition recency signal。

下一阶段优先测试：

```text
Q + C + recent_claim_delta
→ Local Obligation
```

不要维护完整 Path。

---

# 52. Decision Rule B — Path 有独立价值

如果：

```text
C1 > CΔ > C0
```

尤其：

```text
Broadness ↓
Stability ↑
```

则支持：

\[
\boxed{
Claims\ are\ not\ sufficient\ frontier\ state
}
\]

未来可以使用：

```text
Q + C + CompactRecentPath
→ O
```

但 Path 保留在 mechanical Workspace，

不是 semantic belief。

---

# 53. Decision Rule C — Path 只修 Broadness

如果：

```text
Broadness 明显下降
```

但：

```text
Downstream ≈
Relation argument errors ≈
Scope errors remain high
```

则结论：

> Path context 修复 frontier localization，但不能修复 structure-preserving semantic projection。

下一独立实验应该进入：

\[
Q\rightarrow CandidateObligations
\]

再：

\[
Candidates+C(+P)\rightarrow ActiveO
\]

---

# 54. Decision Rule D — Path 几乎无效

如果：

```text
CΔ/C1/C2
```

相对 C0 几乎没有有意义改善，

则可以更强地支持：

> 当前 Q+C→O 失败不是由 path blindness 主导。

下一阶段直接拆：

```text
Question understanding
```

和：

```text
state-conditioned selection
```

即：

\[
Q\rightarrow \{R_i\}
\]

然后：

\[
\{R_i\}+C\rightarrow O_t
\]

---

# 55. Decision Rule E — Recent Evidence 反而变差

如果：

```text
C2 < C1
```

尤其增加：

```text
wrong_relation_arguments
wrong_object_scope
candidate hardening
```

则：

> raw/recent evidence context 正在造成 salience interference。

未来不应将 observation text 放进 Obligation planner。

保留：

```text
Claims + compact path
```

即可。

---

# 56. 不允许 post-result prompt revision

无论结果是什么：

本分支只运行一套 frozen prompt。

不得：

```text
看到 C1 broadness 后补一句 locality rule
看到 C2 argument error 后删 observation
看到某 case 后加 case-specific example
```

任何修订另开实验。

---

# 57. 不运行 Candidate Obligations

即使 C1 FAIL：

本轮也停止。

只在最终报告中建议下一分支：

```text
experiment/ephemeral-obligation-decomposition
```

不得在同一分支追加：

```text
Q → candidates
```

否则无法区分 path intervention 与 decomposition intervention。

---

# 58. 不运行 Evidence Gap cascade

上一轮已经：

```text
Gold O + C → Gap
```

通过 development gate。

本轮只研究：

```text
Context → O
```

不要：

```text
O → Gap
Search
Find
Open
Writer
Closure
```

否则实验过宽。

---

# 59. 不增加 persistent state

即使 Path 有帮助：

不得立刻把它加入：

```text
ResearchState
```

正确解释应是：

```text
RecentPath is mechanical / ephemeral control context.
```

Persistent semantic hypothesis 仍保持：

\[
Q+C+H
\]

除非以后单独实验要求改变。

---

# 60. 建议目录

```text
experiments/obligation_context_sufficiency/
├── README.md
├── TASK.md
├── HYPOTHESES.md
├── PROTOCOL.md
├── PRE_EXECUTION_AUDIT.md
├── CONFIG.json
├── FREEZE.json
│
├── e0_context/
│   ├── SOURCE_MAP.json
│   ├── CONTEXT_C0.json
│   ├── CONTEXT_CDELTA.json
│   ├── CONTEXT_C1.json
│   ├── CONTEXT_C2.json
│   ├── AVAILABILITY.json
│   └── REPORT.md
│
├── prompts/
│   └── obligation_context_unified.txt
│
├── e1_context/
│   ├── SCHEDULE.json
│   ├── RUN.json
│   ├── calls/
│   ├── review/
│   │   ├── PACKETS.json
│   │   ├── FIRST_PASS.json
│   │   ├── FIRST_PASS_ATTESTATION.json
│   │   ├── CONTEXT_REVIEW.json
│   │   └── PAIR_REVIEW.json
│   ├── METRICS.json
│   └── REPORT.md
│
└── analysis/
    ├── PROVIDER_PREFLIGHT.json
    ├── PREFIX_LEAKAGE_AUDIT.json
    ├── CONTEXT_AVAILABILITY.json
    ├── DIAGNOSTICS.json
    ├── SENSITIVITY.json
    ├── EXECUTION_ACCOUNTING.json
    ├── INTEGRITY.json
    └── FINAL_CONCLUSION.md
```

---

# 61. Freeze discipline

在任何真实调用前 freeze：

```text
base SHA
27 states
source mapping
all four context payloads
context construction algorithm
availability rules
prompt bytes
schema
model config
schedule
replicates
rubric
error taxonomy
mechanism thresholds
decision rules
failure policy
```

然后 commit。

所有 paid calls 必须发生在该 freeze commit 之后。

---

# 62. Context Construction 本身要做 unit tests

至少测试：

### Future leakage

任何 context event：

```text
event_index <= state_checkpoint
```

---

### Q/C identity

必须与原 state byte-compatible 或 canonical-equal。

---

### Delta

只能来源于：

```text
current C - previous prefix C
```

---

### RecentPath

必须是最后 K 个允许的真实事件。

---

### RecentObservation

必须来自 RecentPath 对应真实 observation。

---

### No Gold leakage

context 内不能出现：

```text
Gold O
Gold Gap
review reason
error labels
reference status
```

---

### No H

四臂均不得输入 H。

---

# 63. 调用失败处理

全部 planned slots 都保留。

不得：

```text
retry
repair
best-of
replace state
replace replicate
resume partial outputs
```

HTTP / schema failure 都在分母。

Contract/access 类 provider error：

按现有项目规则停止未发送队列。

---

# 64. Cost accounting

必须报告：

```text
planned calls = 216
sent
returned
HTTP failures
schema failures
input tokens
completion tokens
reasoning tokens
cache hit
cache miss
weighted cache rate
median latency
P95 latency
max latency
peak concurrency
```

reasoning 已包含于 completion 时：

不得重复加到 total。

不验证价格就不报告货币费用。

---

# 65. 最终报告必须回答的核心问题

1. Concurrent C0 是否复制历史 Dynamic-O failure？
2. `Recent Claim Delta` 是否改善 Obligation？
3. 仅知道“刚新增了哪些 Claims”是否已经足够？
4. Compact RecentPath 是否在 Delta 之外增加价值？
5. Recent Observation 是否进一步改善或反而干扰？
6. 哪种 context 对 broadness 最有效？
7. 哪种 context 对 replicate stability 最有效？
8. downstream jump 是否受 path context 影响？
9. wrong-relation-argument 是否受 path context 影响？
10. wrong-object-scope 是否受 context 影响？
11. stale/repeated obligations 是否存在 floor effect？
12. Path context 是否产生新的事实提升错误？
13. raw observations 是否被错误当成 verified evidence？
14. 是否出现旧 Query candidate 被 harden 成事实？
15. path-eligible subset 的结果与 overall 是否一致？
16. CΔ/C1/C2 哪个是最低复杂度且最有价值的 intervention？
17. 当前证据是否支持 Claims 足以表示 frontier？
18. 是否有必要进入 Candidate Obligation decomposition？
19. 是否有任何证据要求 persistent Path state？
20. 下一阶段应该是 Direct-O + compact path，还是 `Q → CandidateObligations`？

---

# 66. 最终解释边界

如果 C1/C2 明显更好：

只能说：

> compact recent-path context improves local obligation projection on this exposed development bank.

不能说：

> 完整 history 解决 decomposition。

---

如果 broadness 改善但 relation errors 不动：

应明确写：

> path context improves frontier localization but does not solve structural semantic fidelity.

---

如果四臂差异很小：

应写：

> current evidence does not support path blindness as the dominant cause of Dynamic Obligation failure.

---

如果 C2 更差：

应写：

> adding local observation text can increase semantic interference; more context is not monotonically beneficial.

---

# 67. 本轮最重要的理论输出

最后必须回答：

\[
\boxed{
\text{当前 Dynamic Obligation failure 中，
究竟有多少看起来像“frontier 不足”，
有多少仍然是“structure-preserving projection failure”？}
}
\]

不要试图用一个总准确率替代这个机制结论。

---

# 68. 本轮之后的决策

只有本实验完成后，才能选择下一条路线。

### 路线 A

如果 compact path 足够好：

\[
Q+C+P_{compact}
\rightarrow O
\]

继续做小规模动态 O → Gap cascade。

### 路线 B

如果 path 只修 locality：

\[
Q
\rightarrow
CandidateObligations
\]

然后：

\[
Candidates+C+P
\rightarrow ActiveO
\]

### 路线 C

如果 observation context 有害：

只保留：

```text
Claims + compact mechanical path
```

不要向 control planner 暴露最近原始文本。

---

# 69. 当前架构假设仍保持最小

在本轮结果出来之前，继续保持：

\[
\boxed{
PersistentSemantic = Q+C+H
}
\]

\[
\boxed{
MechanicalWorkspace = Trace+RecentPath+D/W+attempts
}
\]

\[
\boxed{
EphemeralControl = O+Gap
}
\]

RecentPath 即使证明有用，

也优先从 Workspace 临时投影给 planner，

而不是永久写入 semantic ResearchState。

---

# 70. 最后一句实验纪律

本轮不是寻找一个“更强提示词”。

本轮要回答的是：

\[
\boxed{
\textbf{
When current evidence is already known,
does compact recent research-path information materially improve
where the model places the next local research focus?
}
}
\]

如果答案是否：

接受结果。

然后再把：

```text
question decomposition
```

与：

```text
state-conditioned selection
```

正式拆开研究。