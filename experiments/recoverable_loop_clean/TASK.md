# Search-ESR — Clean Recoverable Loop from Stage 4

## 0. 任务定位

本任务不是继续修复：

```text
experiment/minimal-recoverable-loop
experiment/onegap-recovery-control
```

也不是继续研究：

```text
Writer v2
Admission v2
Support Alignment
Residual
Scope
Target
SemanticPackage
QualifiedSupport
SupportGraph
BranchGraph
RelationDAG
```

这两轮后续实验保留为历史诊断结果，不删除、不修改、不覆盖。

本任务需要：

> **从干净的 Stage 4 基线重新建立一条最小、接口一致、可恢复的 Research Loop。**

推荐基线：

```text
experiment/ephemeral-obligation-decomposition
7fdb048e856545facd4acfb590e8cf28c46f1013
```

首先重新核对远程 HEAD。

如果远程该分支已经前移：

1. 阅读新增提交；
2. 判断是否仍然属于 Stage 4 Task Skeleton 路线；
3. 在 `DESIGN_AUDIT.md` 中说明；
4. 不静默继续使用旧 SHA。

建议新分支：

```bash
git fetch origin --prune

git switch -c \
  experiment/recoverable-loop-clean \
  7fdb048e856545facd4acfb590e8cf28c46f1013
```

如果仓库约定要求从远程 ref 创建，则使用对应的远程 Stage 4 ref。

---

# 1. 为什么重新从 Stage 4 实现

历史 Stage 5 / Stage 6 曾尝试：

```text
R + C
→ Supported / Partial / Full
→ Residual
→ Scope / Qualification
→ Semantic Package
```

这些实验暴露了大量 relation / binding / qualifier / context bad cases。

当前研究不再假定：

> 每一步必须精确知道“真正还剩什么”。

新的核心假设是：

\[
\boxed{
\text{Local control errors can be recoverable
if authoritative epistemic state remains grounded.}
}
\]

即：

> Research Agent 不需要每一步 OneGap、Query、Tool Choice 都完全正确。

它需要保证：

1. 错误探索不能直接污染长期事实；
2. 错误候选不能直接成为事实；
3. 无收益路线可以被反馈淘汰；
4. 错误的“我已经完成”判断必须经过独立 Closure；
5. 最终答案只能建立在 grounded Claims 上。

---

# 2. 当前已经接受的长期 State

长期状态限定为：

\[
S_t=(Q,R,C,H,T)
\]

不得因为某个 bad case 增加新的 persistent semantic state。

---

## Q — Original Question

最高任务权威。

规则：

```text
immutable
never rewritten
never replaced by summary
```

---

## R — Stable Task Skeleton

来自 Stage 4。

R 是：

> coarse、source-anchored、episode-stable 的任务结构。

R 只回答：

> 原问题最终要求我们建立哪些 material conditions？

R 不回答：

> 当前已经完成了多少？

禁止给 R 增加：

```text
supported
partial
full
coverage score
residual
scope
confidence
active flag
```

禁止假设：

\[
R-C=Residual
\]

必须可以追溯回 Original Question 的原始 source span。

---

## C — Verified Claims

C 是唯一的长期事实状态。

Claim 的核心语义是：

> 一个由实际 Observation 支持的、已经接受的事实。

推荐最小结构：

```json
{
  "claim_id": "C7",
  "statement": "...",
  "evidence_refs": ["W3"],
  "version": 1
}
```

如果现有可靠实现需要 source provenance / excerpt，可保留。

但不要在 Claim 中保存：

```text
supports_R
coverage
residual
semantic role
candidate confidence
next action
```

原则：

\[
C=\text{grounded facts}
\]

而不是：

\[
C=\text{research progress graph}
\]

---

## H — Hypotheses

H 是低权限候选空间。

例如：

```json
{
  "hypothesis_id": "H2",
  "statement": "The referenced L.E. may be Euler.",
  "status": "active",
  "basis_refs": ["W3"]
}
```

允许状态：

```text
active
deprioritized
rejected
```

硬规则：

\[
H\nRightarrow C
\]

\[
H\nRightarrow RequirementClosure
\]

\[
H\nRightarrow READY
\]

H 只能：

```text
guide investigation
be tested
be revised
be rejected
```

---

## T — Trace

T 是机械运行轨迹，不是真相。

保存：

```text
recent OneGap
actual tool action
observed handles
claim delta
hypothesis delta
Gain / NoGain
pending source opportunities
closure feedback
```

Actor 不需要看到完整历史。

设计一个：

```text
TraceView
```

只保留真正有助于下一轮控制的近期信息。

第一版优先简单。

---

# 3. OneGap 是本方案的核心临时控制量

每轮：

\[
Q,R,C,H,T
\rightarrow
OneGap_t
\]

OneGap 定义为：

> **当前这一轮值得调查的一个具体问题。**

OneGap 不是：

```text
Residual
complete unresolved set
Requirement status
truth
persistent state
```

明确：

\[
OneGap_t \neq R-Supported(C)
\]

OneGap 不要求：

```text
complete
unique
globally optimal
stable
exact
```

它只需要：

### 3.1 有任务锚点

能够追溯到 Q 或某个 R。

### 3.2 当前没有明显被 C 直接建立

不要要求严格逻辑证明：

\[
C\nmodels OneGap
\]

否则会重新走向 Residual。

### 3.3 可调查

OneGap 必须能够自然转成 acquisition。

### 3.4 低承诺

如果依赖 H：

必须表达成：

```text
verify whether ...
determine whether ...
check whether ...
```

不能把 H 中的条件偷偷变成已知事实。

### 3.5 有信息价值

如果成功，应至少可能：

```text
produce a useful Claim
reject/deprioritize a hypothesis
eliminate a candidate
localize a promising source
resolve a conflict
```

---

# 4. OneGap 只有 Action Authority

OneGap 可以影响：

```text
where to search
which source to inspect
which relation to verify
which hypothesis to test
```

OneGap 不可以：

```text
write C
change Q
change R
mark Requirement solved
delete unresolved semantics
authorize final answer
```

错误 OneGap 应该是：

> 一个可恢复的控制错误。

而不是：

> 一个长期 State corruption。

---

# 5. 不要继承旧 Writer / Admission 实验设计

明确禁止直接复用：

```text
experiment/minimal-recoverable-loop
```

中的：

```text
control-blind Writer
one-excerpt-only Admission
E1 Admission gate
```

作为新 Runtime 的默认 Claim 链。

这套实验保留历史结果，但不是当前主线。

不要继续做：

```text
Writer v2
Admission v2
excerpt package v2
```

---

# 6. Claim 链恢复到历史已有正向信号的设计

优先复用 / 重新实现：

```text
experiment/gap-evidence-claim-loop
```

中已经获得正向信号的核心思想：

\[
OneGap + C + Observation
\rightarrow
\text{selective candidate facts}
\]

这里：

```text
OneGap → relevance
C → novelty / dedup
Observation → truth
```

必须严格区分：

\[
\boxed{
OneGap\ decides\ what\ is\ worth\ extracting
}
\]

\[
\boxed{
Evidence\ decides\ what\ is\ true
}
\]

H 不应该直接成为 Claim extractor 的证据来源。

如果 H 需要被验证：

Actor 应先把它变成 OneGap。

---

# 7. Claim 提取不要重新变成网页通用事实抽取

禁止：

```text
Observation
→ enumerate every true fact
→ dump all into C
```

Claim extraction 的目标是：

> 从新 Observation 中提取 **对当前 OneGap 真正有新增价值的少量事实**。

第一版建议输出：

```text
0–3 candidate Claims
```

如果 historical implementation 已有合理限制，可复用。

如果 GPT-6 经过审计认为固定 0–3 会破坏已有已验证行为，可以提出替代，但必须：

1. 在 `DESIGN_AUDIT.md` 中解释；
2. 说明如何控制 Claim bloat；
3. 不得根据新实验结果事后修改。

---

# 8. Evidence → Claim 的 Truth Boundary

不要重新实现 single-excerpt-only Admission。

Claim 是否能进入 C，应依据：

> 实际 Observation 是否支持 Claim 的完整语义。

需要保留：

```text
subject
object
relation
time
quantity
modality
condition
identity binding
```

但不要重新增加 semantic package。

允许使用：

```text
full observed window
source title
real table header
adjacent raw context
existing source provenance
```

只要这些都是：

> 当前真实工具已经返回 / Harness 可确定恢复的 source context。

禁止使用：

```text
Q as evidence
R as evidence
H as evidence
OneGap as evidence
outside knowledge
future observations
```

---

# 9. 第一原则：Deterministic First

任何 Harness 已经知道的信息：

不要让 LLM 重写。

例如：

```text
doc_ref
window_ref
document hash
URL
offset
raw exact text
tool call id
attempt id
source provenance
```

如果可以机械恢复：

由 Python/Harness 负责。

LLM 只负责必要的语义选择。

---

# 10. 真实 Search / Find / Open 接口必须成为唯一工具合同

Stage 4 基线上已经有真实接口：

## search

```text
search(query, k=5)
```

用于：

> 全局发现候选文档。

返回：

```text
D# document handle
W# preview handle
```

---

## find

```text
find(doc_ref, query)
```

用于：

> 在一个已经发现的 D# 文档内部，根据关键词 / 局部语义定位目标事实。

---

## open

```text
open(window_ref, direction)
```

其中：

```text
direction ∈ {before, after, around}
```

作用：

> 展开一个已观察 W# 窗口的附近上下文。

---

# 11. 严禁重新发明另一套 Action API

不得重新出现：

```text
OPEN(source_ref, keyword)
pattern
source_ref with ambiguous D#/W#
custom tool meaning
```

等中间接口。

如果 Actor 输出工具动作：

必须和真实 `SearchFindTools` 1:1 对应。

例如：

```json
{
  "tool": "find",
  "doc_ref": "D7",
  "query": "Euler"
}
```

必须能够直接执行：

```python
SearchFindTools.execute(
    "find",
    {
        "doc_ref": "D7",
        "query": "Euler"
    }
)
```

不能再经过语义翻译：

```text
OPEN keyword → FIND
source_ref → doc_ref/window_ref guessing
pattern → direction/query guessing
```

---

# 12. GPT-6 可以自由决定 Action 接口的实现方式

这里允许 GPT-6 根据代码审计自行选择：

### 方案 A

直接使用真实 function calling schema。

### 方案 B

极薄的 Actor Decision schema，其中 Action 部分直接嵌入真实工具 schema。

### 方案 C

Actor 先输出语义 route，再由**完全机械、无语义判断**的 compiler 转成真实工具。

但如果选择 C：

必须证明 compiler：

```text
does not choose semantic content
does not infer missing handles
does not convert wrong intent into right intent
```

建议优先 A 或 B。

---

# 13. OneGap 和 Tool Action 必须分开评价

一个 OneGap 可以合理，但 Tool Action 可以选错。

例如：

```text
OneGap:
verify whether the target book references Euler
```

动作可能错误：

```text
SEARCH Euler biography
```

这属于：

```text
good control target
bad action choice
```

不要把两个错误混成一个指标。

后续实验分别记录：

```text
OneGap usability
Action validity
Action semantic suitability
Tool execution success
Evidence yield
```

---

# 14. Closure 不属于 Search/Find/Open Action Union

不要再把：

```text
SEARCH
FIND
OPEN
REQUEST_CLOSURE_AUDIT
```

塞成同一种工具动作。

Actor 应输出：

```json
{
  "decision": "acquire",
  ...
}
```

或者：

```json
{
  "decision": "request_closure"
}
```

例如：

```json
{
  "decision": "acquire",
  "focus_requirement_id": "R3",
  "one_gap": "Verify whether the target book references Euler.",
  "action": {
    "tool": "find",
    "doc_ref": "D7",
    "query": "Euler"
  }
}
```

Closure：

```json
{
  "decision": "request_closure"
}
```

不要强迫 closure request 填：

```text
one_gap
strategy
empty action args
```

---

# 15. 过早 Closure Request 不是安全失败

这是本次重构必须明确修正的地方。

Actor 可以随时：

```text
request_closure
```

如果当前证据不足：

Closure 返回：

```text
CONTINUE
```

以及必要的：

```text
open Requirement IDs
brief missing evidence summaries
```

这些只进入：

```text
TraceView
```

不能写入：

```text
R
C
```

因此：

\[
PrematureClosureRequest
\]

优先视为：

```text
efficiency cost
```

而不是：

```text
safety violation
```

真正的安全错误是：

\[
FalseREADY
\]

---

# 16. Closure 是恢复机制的一部分

恢复不只依赖 NoGain。

明确实现三条恢复通道：

## A. Evidence correction

\[
WrongH
\rightarrow Evidence
\rightarrow H\ rejected/deprioritized
\]

---

## B. NoGain correction

\[
BadOneGap
\rightarrow 2\times NoGain
\rightarrow NewOneGap
\]

---

## C. Closure correction

\[
FalseCompletionBelief
\rightarrow ClosureRequest
\rightarrow CONTINUE
\rightarrow NewOneGap
\]

后续实验必须实际跑 C。

不能只在 Actor 单步阶段猜：

> Closure request 是否过早。

---

# 17. NoGain 第一版保持简单

Gain 第一版只在发生以下之一时成立：

```text
new useful Claim entered C
new nonduplicate H added
active H rejected/deprioritized
new uninspected useful source opportunity discovered
known conflict resolved
```

否则：

```text
NoGain
```

但必须额外审计一种风险：

> 错误路线持续产生大量“真实但无关”的新 Claim，从而机械上一直 Gain。

如果出现：

```text
Claim bloat masking failed exploration
```

先记录为 failure mechanism。

不要立刻增加 SupportGraph / Residual。

---

# 18. OneGap 的 premise hardening

当前已观察到：

```text
Ding candidate
→ Ding who had no children...
```

以及：

```text
memo date
→ 1945 letter
```

这种问题。

第一版通过 Prompt / contract 约束：

> 如果一个 relation / attribute 仅存在于 H、Q/R condition 或推测中，而没有 C 支持，OneGap 必须表达为待验证问题。

允许：

```text
Verify whether Ding also satisfies the 2019 childlessness condition.
```

不允许：

```text
Verify the gift made by Ding, who had no children as of 2019.
```

允许：

```text
Verify the actual date of the enclosed letter.
```

不允许：

```text
Inspect the March 5, 1945 letter.
```

但不要为此增加新的长期字段或独立 Semantic Verifier。

---

# 19. Actor 第一版输入

只允许：

```text
Q
R
C
H
TraceView
available source handles
```

禁止：

```text
Residual
Support Mask
Need
AtomicNeed
Scope
Target
SemanticPackage
Gold
historical answer
future source evidence
```

---

# 20. Actor 的基本 Prompt

第一版核心指令：

```text
You choose the next research investigation.

Q and R describe what the task ultimately requires.

C contains verified facts.

H contains provisional hypotheses that may be wrong.

TraceView describes recent attempts, feedback, and source opportunities.

Choose ONE useful investigation target: OneGap.

OneGap is not an exact residual and does not need to describe everything still missing.

Use H only as something to test.
Never phrase an unverified H condition as an established fact.

If the same investigation route repeatedly produced NoGain, choose a materially different investigation.

If the evidence might already be sufficient, request Closure instead of deciding completion yourself.

You cannot modify Q, R, or C.
You cannot mark a Requirement solved.
You cannot answer the original question directly.
```

具体字段 / schema 允许 GPT-6 根据真实工具接口优化。

---

# 21. Claim Reader 恢复旧方案思想

真实 Observation 返回后：

输入：

```text
OneGap
existing C
Observation
```

任务：

> 只提取 Observation 中对当前 OneGap 有新价值的 grounded facts。

不要让 H 作为事实输入。

可以给 Q/R 少量上下文用于 disambiguation，但必须明确：

```text
Q/R are not evidence
```

如果 GPT-6 通过代码审计认为历史 `gap-evidence-claim-loop` 有可以直接复用的 prompt/schema，应优先复用，而不是重新设计。

任何改动必须在 `DESIGN_AUDIT.md` 中说明：

```text
what is reused
what is changed
why
```

---

# 22. Hypothesis Manager

H Manager 只能：

```text
ADD hypothesis
KEEP
DEPRIORITIZE
REJECT
```

它不能：

```text
write C
mark R solved
request final answer directly
```

输入可包括：

```text
Q
R
current H
new Observation
new Claims
Trace outcome
```

保持最多少量 active H。

第一版建议：

```text
<= 6
```

不要 confidence score。

---

# 23. Closure

输入：

```text
Q
R
C
Evidence supporting C
```

不要输入：

```text
H
OneGap
Trace
Residual
Mask
```

输出：

```text
READY
```

或：

```text
CONTINUE
```

若 CONTINUE：

可以提供：

```text
open requirement IDs
brief missing summaries
```

但这些只进 Trace。

最高安全要求：

\[
FalseREADY=0
\]

---

# 24. 最终答案生成

只有：

```text
Closure = READY
```

才能调用。

输入：

```text
Q
C
supporting Evidence
Closure result
```

不输入 H。

---

# 25. 先做 DESIGN_AUDIT，禁止立即写大段代码

新分支建立后，第一项交付：

```text
experiments/recoverable_loop_clean/DESIGN_AUDIT.md
```

必须回答：

1. Stage 4 当前真实 Search/Find/Open 实现在哪里？
2. D#/W# handle 生命周期是什么？
3. `SearchFindTools.execute()` 的真实参数合同是什么？
4. 最新 onegap experiment 为什么出现 11 个 OPEN mismatch？
5. 哪些旧代码可以直接复用？
6. 哪些 `minimal-recoverable-loop` / `onegap-recovery-control` 代码不应该带回来？
7. 历史 `gap-evidence-claim-loop` 哪部分 Claim 提取逻辑值得复用？
8. 新 loop 每一步的输入/输出/权限是什么？
9. OneGap、Action、Claim、H、Closure 的职责是否完全分离？
10. 哪些信息可机械确定，必须由 Harness 而不是 LLM 处理？
11. 如何保证真实 Action 与工具 schema 1:1？
12. 如何避免 premise hardening？
13. 如何处理 premature Closure request？
14. Gain/NoGain 最小定义是什么？
15. 哪些 invariant 可以完全离线测试？

完成 Audit 后再进入实现。

---

# 26. 实现阶段必须逐层完成

## Phase A — Tool Contract

实现 / 验证：

```text
Search
Find
Open
D#/W# registry
action schema
action validation
execution
observation normalization
```

所有测试：

```text
offline
no paid API
```

必须覆盖：

```text
valid search
valid find
valid open before
valid open after
valid open around
unknown D#
unknown W#
wrong action shape
wrong handle type
```

---

## Phase B — Minimal State

实现：

```text
Q/R/C/H/T
TraceView
```

只做数据结构和权限。

不调模型。

---

## Phase C — OneGap Actor

实现：

```text
StateView
→ decision
→ OneGap + real Action
```

先用静态 mock outputs / fixtures 测接口。

---

## Phase D — Claim Chain

把已有：

```text
OneGap-conditioned evidence reading
```

接回。

不要导入旧 control-blind Writer。

---

## Phase E — H + Gain/NoGain

接入：

```text
Hypothesis update
Trace
Gain / NoGain
strategy shift signal
```

---

## Phase F — Closure

接入：

```text
REQUEST_CLOSURE
CONTINUE
READY
```

并确保：

```text
CONTINUE → feedback only
READY → only final-answer gate
```

---

# 27. 必须建立离线 regression suite

至少覆盖历史 bad cases：

```text
Euler biography
book-only → later article
memo date → letter date
patient nationality → report country
teammate same-country
DLC qualifier
q637 clinical-local vs global candidate
Ding 2019
q546 promising source
q1094 repeated Search
```

离线 regression 的目标不是要求：

```text
exact OneGap
```

而是检查：

```text
no unauthorized C mutation
no H→C direct leakage
valid action schema
no invented source handles
premise remains tentative
Closure authority separation
NoGain policy can be represented
```

---

# 28. 不要自动执行真实实验

本任务第一阶段只允许：

```text
repository analysis
code implementation
offline tests
historical fixture replay
mock tool execution
```

禁止未经新授权：

```text
DeepSeek API
OpenAI API
Search API with paid cost
new live BC+ model rollout
```

在所有离线实现完成后：

生成：

```text
IMPLEMENTATION_REPORT.md
OFFLINE_VALIDATION.md
NEXT_EXPERIMENT_PLAN.md
CALL_ESTIMATE.json
```

然后停止。

等待用户明确授权后，才能进行任何新的付费模型实验。

---

# 29. GPT-6 的自由度

允许 GPT-6 自主：

```text
refactor code structure
choose clean module names
reuse trustworthy historical utilities
delete unnecessary intermediate wrappers in the new branch
choose function-calling vs thin action schema
design TraceView serialization
improve offline tests
identify hidden interface bugs
propose simpler implementations
```

如果发现：

> 当前任务书某个工程约束会制造明显接口问题，

允许修改实现方案。

但必须：

1. 在 `DESIGN_AUDIT.md` 记录原约束；
2. 说明为什么不合理；
3. 给出更简单替代；
4. 不改变下面的核心研究 invariant。

---

# 30. 不允许 GPT-6 自主改变的研究 invariant

不得自行新增：

```text
persistent Residual
persistent Scope
persistent Target
SupportGraph
BranchGraph
RelationDAG
SemanticPackage
persistent Coverage Mask
persistent OneGap
```

不得改变：

```text
Q immutable
R stable task skeleton
C grounded facts
H low authority
OneGap ephemeral
Actor cannot write C
Actor cannot STOP/final answer
Closure exclusively controls READY
Evidence controls truth
NoGain is feedback, not truth
```

如果 GPT-6 认为某个新长期字段真的不可避免：

不要直接实现。

必须在报告中写：

```text
PROPOSED_STATE_EXTENSION
failure being solved
why Q/R/C/H/T cannot recover
counterexample
minimal proposed field
alternative without field
```

然后停止等待用户决策。

---

# 31. 代码实现质量要求

所有新模块必须：

```text
small
explicit
testable
replayable
no hidden global semantic mutation
```

优先：

```text
pure functions
typed structures
deterministic mechanical transforms
append-only logs
```

避免：

```text
generic update_state()
model-generated state patches
implicit mutation
silent repair
fallback that changes semantic intent
```

---

# 32. Tool interface 的关键 invariant

必须添加类似测试：

```python
for every valid Actor acquisition action:
    SearchFindTools.execute(
        action["tool"],
        action["arguments"]
    )
```

在已知 handle 合法时：

```text
must pass structural validation
```

不要等真实模型调用后才发现：

```text
OPEN keyword should have been FIND
```

这种问题。

---

# 33. OneGap premise safety 的离线测试

构造真实历史 fixture：

### Euler

H：

```text
Euler may be L.E.
```

允许：

```text
verify whether the book references Euler
```

拒绝作为“事实式 premise”的：

```text
locate where the book references Euler
```

如果 context 中还没有引用关系。

---

### Memo / Letter

C：

```text
memo dated 1945
```

H：

```text
letter may also date to 1945
```

允许：

```text
verify the letter's actual date
```

不允许：

```text
inspect the 1945 letter
```

---

### Ding

H：

```text
Ding may be the founder candidate
```

允许：

```text
test whether Ding satisfies the 2019 childlessness condition
```

不要把：

```text
Ding, who had no children...
```

当成既定前提。

---

# 34. Closure regression

至少准备：

### Euler trap

只有 Euler biography。

应：

```text
CONTINUE
```

### Book-only trap

只有 book/date，无 article。

应：

```text
CONTINUE
```

### Memo trap

只有 memo date，无 letter date。

应：

```text
CONTINUE
```

### DLC trap

部分 mechanics 有证据，关键 qualifier 缺失。

应：

```text
CONTINUE
```

### q637

local clinical facts 成立，但 global candidate identification 未完成。

应：

```text
CONTINUE
```

同时不能否认已有 local Claims。

---

# 35. 下一轮真正的实验目标

离线实现完成后，不要重新跑单步 OneGap accuracy。

下一轮应该设计：

\[
\boxed{
2\text{–}3\ step\ Micro\ Recovery
}
\]

验证三类轨迹：

---

## R1 — Bad OneGap Recovery

人为冻结一个次优第一动作。

观察：

```text
action
→ Observation / NoGain
→ next OneGap
```

测试：

> 是否真的离开错误路线。

---

## R2 — Wrong-H Recovery

加入自然历史弱候选。

运行真实 acquisition。

测试：

```text
H
→ evidence
→ reject/deprioritize/behaviorally abandon
```

并检查：

```text
no false C
```

---

## R3 — Premature Closure Recovery

让 Actor 有机会：

```text
request_closure
```

Closure 若：

```text
CONTINUE
```

将 missing feedback 放回 Trace。

然后再跑下一 Actor step。

测试：

\[
ClosureVeto
\rightarrow
NewOneGap
\]

这才是完整 recovery。

---

# 36. 下一轮实验评价重点

不要再主要看：

```text
OneGap exact accuracy
```

重点：

```text
valid executable action rate
premise hardening rate
NoGain route escape
wrong-H recovery
closure veto usefulness
false C
false READY
steps to useful new evidence
```

其中最高风险仍是：

```text
false high-risk Claim in C
false READY
```

---

# 37. 严禁事项

禁止为了修接口问题：

```text
add Residual
add Scope
add Target
add SemanticPackage
add SupportGraph
```

禁止为了提高实验分数：

```text
retry
best-of
majority vote
manual trajectory repair
post-hoc Gold change
delete failures
auto-correct model actions before scoring
```

Harness 可以拒绝非法 action。

但：

> 非法 action 必须保留为真实失败。

离线开发阶段可以修接口设计；

一旦新实验冻结，不得运行中热修。

---

# 38. 最终交付

在任何新付费调用之前，必须提交：

```text
experiments/recoverable_loop_clean/DESIGN_AUDIT.md
experiments/recoverable_loop_clean/ARCHITECTURE.md
experiments/recoverable_loop_clean/INTERFACE_CONTRACTS.md
experiments/recoverable_loop_clean/OFFLINE_VALIDATION.md
experiments/recoverable_loop_clean/NEXT_EXPERIMENT_PLAN.md
experiments/recoverable_loop_clean/CALL_ESTIMATE.json
```

以及：

```text
all new source code
all unit tests
all regression fixtures
```

最终报告必须明确回答：

1. 是否真正从 Stage 4 干净分支实现？
2. 是否导入了旧 Writer/Admission 逻辑？
3. 新 OneGap 是否仍为 ephemeral？
4. Actor action 是否和真实 Search/Find/Open 1:1 对齐？
5. OPEN/FIND 是否还存在语义重叠或参数歧义？
6. Claim 链是否恢复 Gap-conditioned relevance？
7. Evidence 是否仍是 Claim truth 的唯一依据？
8. H 是否仍无 truth authority？
9. NoGain 如何实现？
10. Closure 是否成为真实恢复通道？
11. premature closure 是否只产生 CONTINUE，而不是安全失败？
12. Stage 5 历史 bad cases 是否都已有对应 regression？
13. 当前还有哪些已知接口风险？
14. 当前还有哪些真正的方案级风险？
15. 是否已经具备冻结 2–3 step Micro-Recovery 实验的资格？

---

# 39. 核心判断原则

实现过程中始终遵守：

\[
\boxed{
\text{Persist epistemic state; derive control state.}
}
\]

\[
\boxed{
\text{Control may be approximate; facts must be grounded.}
}
\]

\[
\boxed{
\text{Wrong action should be recoverable.}
}
\]

\[
\boxed{
\text{Wrong Claim and false READY are the high-risk failures.}
}
\]

最终目标不是：

> 让每一步 OneGap 都非常聪明。

而是：

\[
\boxed{
\textbf{
构建一个接口正确、事实状态受保护、
允许局部控制犯错、并能通过反馈真正恢复的 Research Loop。
}
}
\]