# Search-ESR：Dynamic Local Obligation Derivation

你正在继续 `homulillew/Search-ESR` 的 Research Control 研究。

本轮的核心目标只有一个：

> **验证模型能否根据 Original Question 与当前 Verified Claims，稳定地产生一个 scope 正确、仍未解决、粒度合适、可以驱动 Evidence Gap 计算的当前 Local Obligation。**

形式化：

\[
Q+C_t\rightarrow O_t
\]

上一轮已经获得开发阶段正向证据：

\[
GoldO_t+C_t\rightarrow Gap_t
\]

因此本轮**不得修改已经通过 Gate 的 Evidence Gap Generator**。

真正要测的是：

\[
\boxed{
\text{Dynamic }O_t
\text{ 是否能够接近人工 Gold }O_t
}
\]

以及当 Dynamic Obligation 送入已经冻结的 Gap Generator 后：

\[
\boxed{
Q+C
\rightarrow O
\rightarrow Gap
}
\]

会损失多少可靠性。

---

# 0. 当前远程锚点

开始前必须重新读取远程：

```bash
git fetch origin --prune
git status
git branch --show-current

git rev-parse origin/main
git rev-parse origin/experiment/need-premise-audit
git rev-parse origin/experiment/evidence-gap-gold-obligation

git log --oneline --decorate -15 \
  origin/experiment/evidence-gap-gold-obligation
```

任务编写时最新研究锚点：

```text
experiment/evidence-gap-gold-obligation
fb61da13d3be2511f37da590429ebea7f706bd0d
```

commit：

```text
Report gold-obligation gap gate pass with partial-state scope failures and H ablation
```

必须以实际 fetch 到的最新 remote 为准。

如果远程已有更新：

1. 先阅读；
2. 检查是否改变本实验前提；
3. 写入 `PRE_EXECUTION_AUDIT.md`；
4. 不得静默覆盖新结果。

---

# 1. 新建独立分支

从：

```text
origin/experiment/evidence-gap-gold-obligation
```

创建：

```bash
git switch -c experiment/dynamic-local-obligation \
  origin/experiment/evidence-gap-gold-obligation
```

新实验目录建议：

```text
experiments/dynamic_local_obligation/
```

历史实验全部只读。

尤其不得修改：

```text
experiments/evidence_gap_gold_obligation/
experiments/need_premise_audit/
experiments/minimal_need_multiquery/
```

---

# 2. 为什么现在研究 Obligation

当前实验历史已经形成一个很清楚的链条。

## Need 直接生成

```text
Q + C + H
→ Need
```

不稳定。

增加：

```text
premise closure
coherence
internal checking
```

仍然无法稳定改善。

---

## Premise Checker

```text
Candidate Need
→ target / subject / premise
```

能够较好重述 target，但不能稳定区分：

```text
正在研究的未知
```

与：

```text
必须事先支持的背景事实
```

并出现大量合法 Need 被错误拒绝。

---

## Gold Obligation → Evidence Gap

上一轮固定人工正确 Local Obligation 后：

```text
G0 = Gold O + Claims
```

得到：

```text
Strict Gap Validity      50/54 = 92.6%
Missing correctness      52/54 = 96.3%
Support binding          54/54 = 100%
Satisfied specificity    16/16 = 100%
Downstream jump          0/54
Target-as-prerequisite   0/54
Replicate semantic       24/27 = 88.9%
```

因此当前最合理的研究假设是：

> **Evidence Gap computation 本身有希望；当前剩余的主要瓶颈是如何从 Q 和当前 Claims 中产生正确的 Local Obligation。**

---

# 3. 当前长期架构假设

仍然保持：

```text
Persistent epistemic state:
Q + Verified Claims + Working Hypothesis

Ephemeral control:
Local Obligation
Local Evidence Gap

Mechanical state:
Workspace / Trace / attempts / D# / W#

Acquisition:
Gap + H + Workspace
→ Search / Find / Open
```

本轮只验证：

```text
Q + C
→ Local Obligation
```

以及 gated downstream：

```text
Dynamic O + C
→ frozen Gap Generator
```

不测试其他模块。

---

# 4. 本轮禁止新增的结构

不得实现：

```text
Requirement Map
OpenNeeds
Persistent Gap
Progress
Frontier
Dependency Graph
Binding Graph
typed requirement DAG
Need history
done_when lifecycle
priority queue
```

也不得实现完整：

```text
output_variables
local_variables
predicates
fixed_anchors
logical form
```

Binding 只允许作为：

```text
error-analysis vocabulary
```

不能成为 runtime state。

---

# 5. Local Obligation 的正式定义

一个 Local Obligation 是：

> **Original Question 当前仍要求被证据建立的一项局部、连贯、具有实质意义的答案义务。**

它回答：

> “为了最终回答 Q，现在有哪一件事情仍值得被建立？”

而不是：

> “下一条 Search Query 是什么？”

---

# 6. Local Obligation 必须满足的性质

一个合格的 Local Obligation 必须同时：

### Question-grounded

直接来自 Original Question。

不能由：

```text
Working Hypothesis
model memory
candidate guess
```

创造新的要求。

---

### Currently unresolved

当前 Claims 尚未充分建立它。

如果已被 Claims 满足，不应再次选它。

---

### Material

解决它会真实推进 Original Question。

不是无关 trivia。

---

### Local

只选择一个当前 research objective。

不是完整重述 Q。

---

### Coherent

可以包含多个互补条件，但它们必须共同服务于一个判断或一个待识别对象。

不要求逻辑原子化。

---

### Correctly scoped

不能跨过尚未识别/建立的对象、事件或关系直接追问 downstream attribute。

---

### Relation-faithful

必须保留 Original Question 中关系的实际 argument scope。

例如抽象地说：

```text
R(a,b)
```

不得改写成：

```text
R(a,c)
```

也不能因为：

```text
SameProperty(b,c)
```

就改写成：

```text
SameProperty(a,b,c)
```

---

### Evidence-resolvable

应该存在现实的证据类型能够推进或满足它。

不能要求推测作者心理、未陈述动机等不可验证内容。

---

# 7. 一个重要原则：未知本身可以是 Obligation 的输出

模型必须明确理解：

```text
unknown entity
unknown event
unknown relation
```

不意味着 Obligation 非法。

例如：

```text
Identify which DLC satisfies description D.
```

DLC identity 未知是合法的。

因为 DLC identity 本身就是 research output。

---

# 8. 一个同样重要的原则：不要跳到 downstream attribute

例如抽象形式：

当前尚未建立：

\[
R(x)
\]

则不要选择：

\[
Attribute(R(x))
\]

作为当前 obligation。

应该先选择：

\[
Establish/Identify\ R(x)
\]

或者：

\[
Determine\ whether\ R(x)\ holds
\]

具体形式取决于 Original Question。

---

# 9. Binding 的使用方式

本轮不输出 Binding schema。

只把下面两条写进语义规范：

> Information currently being discovered or verified does not need to be supported beforehand.

以及：

> A downstream property must not be selected before the entity/event/relation that gives that property a concrete referent is sufficiently established.

评审时可以使用：

```text
wrong_argument_binding
wrong_object_scope
unresolved_referent
downstream_jump
```

解释错误。

但不要要求模型输出这些字段。

---

# 10. E0：实验 bank

第一轮 development 直接复用上一轮：

```text
experiments/evidence_gap_gold_obligation/e0_reference/
```

中的 **27 个自然历史 snapshots**。

理由：

1. 已经存在人工 Gold Obligation；
2. 已经存在 Gold Gap；
3. 已经知道 Gold-O → Gap 的实际 ceiling；
4. 同一 bank 可以直接隔离 Obligation derivation loss。

这些状态：

```text
27 snapshots
10 question clusters
```

是 exposed development material。

绝不能称 fresh。

---

# 11. 不重新人工改 Gold Obligation

上一轮已经冻结的 Gold O：

```text
GOLD_OBLIGATIONS
```

作为本轮 reference。

不得为了适配新的模型输出修改。

如果发现历史 Gold O 本身确有严重错误：

1. 单独报告；
2. 停止该 case；
3. 不进行 post-hoc 改标后继续假装原 freeze 有效。

---

# 12. Primary Arm：O0 = Q + C

Primary 输入：

```text
Original Question
Verified Claims with IDs
```

输出：

```json
{
  "obligation": "one natural-language Local Obligation"
}
```

不给：

```text
Gold O
Gold Gap
Historical Need
Premise audit
Search history
Workspace
H
```

---

# 13. Secondary Arm：O1 = Q + C + H

为了测试 Hypothesis 是否污染 Obligation selection，再设同期 arm：

```text
O1:
Q + C + Working Hypothesis
→ Local Obligation
```

其他所有条件相同。

Primary 仍然是 O0。

O1 不改变 O0 Gate。

---

# 14. 为什么现在需要 H ablation

Gold-O Gap 实验中：

```text
O+C
```

与：

```text
O+C+H
```

差异很小，没有观察到明显 H contamination。

但 Obligation derivation 是不同任务。

H 可能在这里更危险：

例如真实 obligation 是：

```text
identify championship winner
```

而 H 中有：

```text
Jerry Mao may be the winner
```

模型可能错误生成：

```text
determine the year Jerry Mao won
```

这正是过去的 candidate contamination。

因此这里 H ablation 非常有信息价值。

---

# 15. O0 Prompt

必须保持简单。

不要输出解释、分类、binding 或 plan。

建议使用：

```text
You derive one current Local Obligation for a research task.

You receive:
1. the Original Question;
2. the current Verified Claims.

Choose ONE unresolved Local Obligation that would materially advance answering the Original Question.

A Local Obligation states what information must still be established,
not how to search for it.

Requirements:

1. The obligation must come directly from the Original Question.

2. Use the Verified Claims only to determine what is already established.
Do not ask to establish something that the Claims already sufficiently support.

3. Choose one local coherent research objective.
It does not need to be logically atomic.
Several complementary conditions may remain together when they jointly
identify or verify one object, event, or relation.

4. Do not bundle independent research objectives merely because they
eventually contribute to the same final answer.

5. An unknown entity, event, relation, or value may itself be what the
obligation asks to discover or verify.
Do not require the current unknown to already be established.

6. Do not jump to a downstream attribute when the referenced entity,
event, relation, document, or source has not yet been sufficiently
identified or established by the Verified Claims.
In that case, choose the identifying/existence/relation obligation first.

7. Preserve relation scope exactly.
Do not change which entity, event, role, date, quantity, or argument
participates in a relation.
A relation between two entities must not be silently changed into a
relation involving another entity.

8. Do not use outside knowledge.

9. Do not output a search query, source preference, plan, hypothesis,
confidence, rationale, requirement list, or STOP decision.

Finding one useful unresolved obligation is sufficient.
Do not perform a complete coverage audit.

Return only JSON:

{
  "obligation": "one natural-language Local Obligation"
}
```

---

# 16. O1 Prompt

与 O0 完全相同，只追加：

```text
You also receive a Working Hypothesis.

The Working Hypothesis is provisional.
It may suggest a candidate that could later be tested,
but it is not evidence and must not create or redefine the Local Obligation.

Do not:
- turn a hypothesized candidate into the subject of a downstream attribute;
- assume a hypothesized event or relation occurred;
- replace a generic question requirement with a candidate-specific requirement;
- treat the hypothesis as satisfying any condition.

The Local Obligation must still be determined from
the Original Question and Verified Claims.
```

---

# 17. 输出 schema 保持只有一个字段

必须只有：

```json
{
  "obligation": "..."
}
```

不要增加：

```text
why
target
subject
mode
premises
depends_on
supported_by
missing
evidence_needed
priority
```

原因：

> 本轮只测 Obligation derivation。

不要再次因为方便评分增加新的 semantic parser。

---

# 18. Provider contract preflight

必须继承上一轮 JSON-mode 事故教训。

真实调用前自动验证：

- prompt 中包含 provider 所需 JSON literal；
- JSON schema；
- endpoint/model；
- authentication；
- max_tokens 未错误设置；
- retry=0；
- payload 可序列化；
- output path 唯一；
- 27 × 2 arms × replicates 完整；
- prohibited information 没进入 input。

任一失败：

```text
STOP_BEFORE_PAID_CALL
```

---

# 19. 被测模型配置

沿用：

```text
deepseek-flash
temperature = 0
JSON mode
max_retries = 0
omit max_tokens
```

Codex GPT-6 是实验执行者。

不要把被测模型改成 GPT-6。

---

# 20. Replicates

每个：

```text
case × arm
```

执行：

```text
2 independent responses
```

所以：

```text
27 × 2 × 2 = 108
```

个 Obligation calls。

两次全部保留。

不能：

- best-of；
- semantic retry；
- 用第二次替换第一次；
- 只选择较好结果进入下游。

---

# 21. E1 Obligation 评分维度

每条 Obligation 至少评：

### Goal Grounding

是否真实来自 Q。

---

### Unresolvedness

是否尚未被当前 Claims 充分支持。

---

### Materiality

是否解决后真实推进最终答案。

---

### Locality

是否是一个当前局部 research objective，而非整题重述。

---

### Coherence

是否只有一个主要研究目标。

---

### Scope Fidelity

实体、事件、关系、时间、角色、比较范围是否忠实于 Q。

---

### Non-Downstream

是否避免跳过尚未建立的 referent/event/relation 去追属性。

---

### Evidence Resolvability

是否现实中存在可获得证据能够解决它。

---

# 22. Strict Obligation Validity

只有全部满足：

```text
GoalGrounded
AND
Unresolved
AND
Material
AND
Local
AND
Coherent
AND
ScopeFaithful
AND
NonDownstream
AND
EvidenceResolvable
AND
valid schema
```

才算 strict-valid。

---

# 23. 与 Gold Obligation 的比较不能只做 exact match

这点非常重要。

Human Gold O 只是一个 reference active obligation。

如果模型生成另一个同样合法的 unresolved Local Obligation：

不要因为“不等于 Gold O”就判错。

每条模型 O 分类为：

```text
gold_equivalent
alternate_valid
invalid
```

其中：

### gold_equivalent

语义上与 Gold O 相同或近似。

### alternate_valid

不是当前人工 Gold O，但依然是：

- Q-grounded；
- unresolved；
- material；
- local；
- correctly scoped。

### invalid

违反 strict obligation rubric。

Primary strict：

```text
gold_equivalent + alternate_valid
```

都算成功。

---

# 24. 额外报告 Gold-selection agreement

虽然 alternate valid 可通过，但仍应报告：

```text
gold-equivalent rate
alternate-valid rate
```

这样可以观察：

> 模型是否稳定选择相同局部目标，

而不把 selection diversity 错判成错误。

---

# 25. Obligation error taxonomy

必须记录：

### Downstream obligation

应该先 establish/identify X，却直接选择 X 的属性。

---

### Already supported

Claims 已经建立 obligation。

---

### Whole-question restatement

把多个独立 final requirements 全塞进去。

---

### Over-atomic

将一个合理的 coherent evidence objective 拆得过细。

---

### Invented requirement

Q 中没有该条件。

---

### Hypothesis contamination

只有 H 中存在的候选事实进入 O。

---

### Wrong object scope

属性、时间、事件被绑定到错误对象。

---

### Wrong relation arguments

关系中的参与者发生变化。

例如抽象地：

```text
R(a,b)
```

被变成：

```text
R(a,c)
```

---

### Relation strengthening

Q 只要求：

```text
A related to B
```

却变成更强关系。

---

### Irrelevant / low-value

虽然和领域有关，但不能实质推进 Q。

---

# 26. G23 类错误必须特别统计

上一轮唯一稳定跨四个输出出现的失败是：

> 原关系是“两名其他队友彼此同国”，模型却重新绑定成“与 Jerry/Australia 同国”。

因此本轮要单独统计：

```text
argument-scope corruption
```

但：

不要给 prompt 加 Jerry、Australia、teammate 等 case-specific patch。

只能使用通用 relation-scope invariant。

---

# 27. Replicate stability

对同一个：

```text
state × arm
```

两条 Obligation 分类：

```text
same_obligation
compatible_obligation
different_but_valid
one_valid_one_invalid
both_invalid
```

Primary stability Gate：

两条必须：

- 都 strict-valid；
- 并且属于 same 或 compatible Local Obligation。

`different_but_valid` 单独报告，不一定视为 semantic failure，但不计“稳定选择”。

---

# 28. O0 Primary Gate

建议全部同时满足：

```text
Strict Obligation Validity >= 80%

Goal grounding >= 90%

Unresolvedness >= 90%

Scope fidelity >= 90%

Non-downstream >= 90%

Whole-question/broadness error <= 10%

Wrong-relation-argument error <= 5%

Schema-valid >= 95%

Both-valid replicate rate >= 80%
```

工程 Gate，不声称统计显著性。

---

# 29. O1 H ablation

重点报告：

```text
O0 strict
O1 strict

O0 downstream
O1 downstream

O0 scope errors
O1 scope errors

O1 H contamination

O0 better
O1 better
tie
```

如果：

```text
O1 < O0
```

且差异主要来自 candidate-specific downstream obligations：

支持：

```text
Hypothesis should not participate in obligation derivation.
```

---

# 30. 如果 E1 FAIL

立即停止。

不要：

- 改 prompt；
- 新增 binding schema；
- 增加 requires；
- 调整 Gold O；
- 跑 Gap cascade；
- 跑 Search。

只分析：

```text
downstream error?
scope corruption?
broadness?
stale selection?
H contamination?
run variance?
```

下一实验另立。

---

# 31. 如果 E1 PASS：进入 E2 Cascade

E2 只回答：

> 一个模型动态生成的合法 Obligation，送进已经冻结的 Evidence Gap Generator 后，会损失多少性能？

这一步不能修改上一轮通过的：

```text
g0_gap_no_h.txt
```

必须逐字复用其 frozen prompt。

---

# 32. E2 选择哪个 Dynamic O

预注册：

使用：

```text
O0 replicate 1
```

作为正式 Dynamic Obligation。

永远不用：

```text
replicate 2
```

替换 replicate 1。

如果 replicate 1 invalid：

该 Dynamic path 在 end-to-end 分母中直接失败。

不能选更好的 replicate。

---

# 33. E2 前先构造 Dynamic-O Reference

这是非常重要的实验纪律。

如果：

```text
O0 replicate 1
```

是：

```text
gold_equivalent
```

可以直接继承对应 Gold Gap reference。

如果是：

```text
alternate_valid
```

必须在看到任何 E2 Gap output 之前，由 reviewer 根据：

```text
Q
C
Dynamic O
```

冻结：

```text
Dynamic-O reference gap
```

包括：

```text
support groups
reference missing
reference evidence_needed
ambiguity
```

然后 commit。

只有之后才能调用 Gap Generator。

---

# 34. E2 两条并行路径

同一 state：

## Oracle Path

```text
Gold O + C
→ frozen Gap Generator
```

## Dynamic Path

```text
Model O(rep1) + C
→ exact same frozen Gap Generator
```

两个路径使用：

```text
same model
same gap prompt
same config
same Claims
same execution period
```

只有 Obligation 不同。

---

# 35. 为什么要并发重新跑 Oracle Path

不要仅拿上一轮 92.6% 做历史 comparator。

因为已经观察到：

```text
temperature=0
```

也有运行波动。

同期 Oracle Path 可以控制：

- provider timing；
- model run variance；
- current execution environment。

---

# 36. E2 Replicate

建议每条路径：

```text
2 gap replicates
```

如果 27 cases：

```text
27 × 2 paths × 2 reps
= 108 gap calls
```

因此整个实验最多：

```text
108 obligation calls
+
108 gap calls
=
216 calls
```

但 E2 只有 E1 PASS 后执行。

---

# 37. E2 Primary Metrics

分别报告：

```text
Oracle Gap strict
Dynamic Gap strict conditional on valid O
Dynamic end-to-end strict over all states
```

其中：

### Conditional

只看 valid Dynamic O。

回答：

> 如果 Obligation 是合法的，Gap Generator 是否仍保持性能？

### End-to-end

所有 planned state 都进入分母。

如果 O invalid：

整个：

```text
Q+C → O → Gap
```

判失败。

这才是真正的 pipeline reliability。

---

# 38. Obligation Derivation Loss

定义描述性：

\[
Loss_{O}
=
OracleGapStrict
-
DynamicEndToEndStrict
\]

不要称精确 causal decomposition，除非 paired design 支持。

同时报告：

```text
fail due to O
fail due to Gap | valid O
fail in both
```

这样能真正定位瓶颈。

---

# 39. E2 Gate

建议：

```text
Concurrent Oracle Gap strict >= 80%

Dynamic Gap | valid O >= 80%

Dynamic end-to-end strict >= 75%

No downstream-jump explosion

No target-as-prerequisite explosion

Dynamic-vs-Oracle loss <= 15pp
```

这只是 development engineering Gate。

不做泛化声称。

---

# 40. 如果 E2 PASS

停止。

允许提出下一次独立：

```text
fresh dynamic obligation confirmation
```

但本轮不执行。

更不能进入：

```text
Query
Search
Multi-Query
Writer
Closure
full loop
```

---

# 41. 如果 E2 FAIL

根据失败来源决定后续。

### 如果主要 O invalid

继续研究：

```text
Q+C → O
```

不要改 Gap。

### 如果 O valid，但 Gap 明显退化

说明：

```text
Gold-O bank
```

低估了真实 Dynamic-O 对 Gap 的难度。

下一步研究：

```text
Gap robustness under diverse valid obligations
```

而不是立刻加 Planner。

---

# 42. 不允许提前增加 `requires`

即使 Dynamic O 出现 downstream 错误，也不要在本轮 adaptive 增加：

```text
requires
depends_on
```

先报告失败。

只有新的独立实验才能比较：

```text
plain O
vs
O + requires
```

---

# 43. 不允许完整 Binding IR

本轮任何结果都不能直接触发：

```text
variables
predicate graph
AST
logical form
typed operators
```

必须先证明简单自然语言 O 无法达到需要的可靠性，并且错误集中在某个可由最小结构修复的机制上。

---

# 44. Provider preflight

真实调用前必须自动检查：

```text
JSON mode prompt contains required literal
schema
model/endpoint
credential availability
request serialization
max-token policy
retry=0
complete schedule
unique outputs
no Gold leakage
no H leakage into O0
no arm leakage
```

preflight 不通过：

```text
STOP_BEFORE_PAID_CALL
```

---

# 45. Freeze 纪律

E1 调用前冻结并 commit：

```text
branch/base
27-case bank
Gold O
Q/C/H input projection
O0/O1 prompts
schemas
review rubric
error taxonomy
replicates
schedule
gates
provider config
preflight
```

E1 完成后：

1. first-pass obligation review；
2. commit；
3. aggregate；
4. Gate；
5. PASS 才允许准备 E2。

E2 又必须独立 freeze + commit。

---

# 46. Review masking

第一次 semantic review 尽量隐藏：

```text
arm
replicate
H
historical Gold O text
aggregate results
```

Reviewer看到：

```text
Q
Claims
generated Obligation
```

然后按照 rubric 独立判断。

判断后才对照 Gold O 分类：

```text
gold_equivalent
alternate_valid
invalid
```

如果技术上无法完全盲：

明确披露。

---

# 47. 成本与失败

全部保留：

```text
HTTP failure
schema invalid
timeout
length
empty output
auth error
provider rejection
```

不得 retry 或 sample replacement。

记录：

```text
planned
sent
returned
input
completion
reasoning
cache hit/miss
latency
peak concurrency
unknown usage
```

reasoning 已属于 completion 时不能重复加总。

---

# 48. 建议目录

```text
experiments/dynamic_local_obligation/
├── README.md
├── TASK.md
├── PRE_EXECUTION_AUDIT.md
├── HYPOTHESES.md
├── PROTOCOL.md
├── CONFIG.json
├── FREEZE.json
│
├── prompts/
│   ├── o0_no_h.txt
│   └── o1_with_h.txt
│
├── e0_reference/
│   ├── CASES.json
│   ├── GOLD_OBLIGATIONS.json
│   └── REPORT.md
│
├── e1_obligation/
│   ├── SCHEDULE.json
│   ├── calls/
│   ├── review/
│   ├── METRICS.json
│   ├── H_ABLATION.json
│   └── REPORT.md
│
├── e2_cascade/
│   ├── DYNAMIC_OBLIGATION_REFERENCES.json
│   ├── FREEZE.json
│   ├── SCHEDULE.json
│   ├── calls/
│   ├── review/
│   ├── METRICS.json
│   └── REPORT.md
│
└── analysis/
    ├── PROVIDER_PREFLIGHT.json
    ├── EXECUTION_ACCOUNTING.json
    ├── INTEGRITY.json
    └── FINAL_CONCLUSION.md
```

---

# 49. 本轮预注册 Hypotheses

## H1

给定 Q+C，模型可以稳定产生一个：

```text
question-grounded
unresolved
material
local
coherent
scope-faithful
```

的 Obligation。

---

## H2

主要失败若发生，将集中在：

```text
downstream selection
relation-argument scope
broadness
```

而不是格式。

---

## H3

H 若进入 Obligation derivation，可能增加 candidate-specific downstream selection。

但这是待测假设，不预设结果。

---

## H4

在 Dynamic O 合法的条件下，上一轮通过的 frozen Gap Generator 应大体保持性能。

---

## H5

如果 end-to-end 性能明显低于 Oracle-O path，主要损失应能够归因到 Obligation derivation，而不是需要新增 persistent semantic state。

---

# 50. 最终报告必须回答

1. `Q+C → Local Obligation` 的 strict validity 多高？
2. 模型是否经常选择已被 Claims 支持的 obligation？
3. 是否仍出现 downstream jump？
4. 是否仍过度 atomic？
5. 是否会重新把整个 Q 包成一个 obligation？
6. 最常见 relation-scope corruption 是什么？
7. Gold-equivalent 与 alternate-valid 比例分别多少？
8. 两次 replicate 是否稳定选到兼容 Obligation？
9. H 是否改变 Obligation scope？
10. H 是否造成 candidate contamination？
11. Dynamic O 输入 frozen Gap Generator 后，Gap strict 多少？
12. Oracle-O 与 Dynamic-O 的同期差距多大？
13. Pipeline 失败主要发生在 O 还是 Gap？
14. 是否有证据要求 `requires/depends_on`？
15. 是否有证据要求 Binding IR？
16. 是否有资格进入 fresh dynamic-obligation confirmation？
17. 当前是否仍支持 persistent `Q+C+H` / ephemeral `O+Gap` 的最小架构？

---

# 51. 允许的结论边界

如果 E1/E2 均 PASS，可以说：

> 在 exposed development states 上，动态 Local Obligation 加 frozen Evidence Gap computation 是一个有希望的控制 pipeline。

不能说：

> Evidence-Gap Agent 已经闭环成功。

因为仍未验证：

```text
fresh generalization
Action planning
Query generation
Search evidence yield
Writer interaction
reactivation
global closure
end-to-end loop
```

---

# 52. 当前研究方向的核心表述

如果实验成功，当前控制链可以暂时写成：

\[
\boxed{
Q+C_t
\rightarrow
O_t
\rightarrow
G_t
}
\]

其中：

\[
O_t=
\text{one current Local Obligation}
\]

\[
G_t=
Required(O_t)-Supported(C_t)
\]

之后未来再研究：

\[
G_t+H_t+Workspace_t
\rightarrow Action_t
\]

Persistent semantics 仍然保持：

\[
\boxed{Q+C+H}
\]

而：

\[
O,\ G
\]

均为 ephemeral。

---

# 53. 最重要的研究纪律

本轮不要试图证明整个架构。

只回答：

\[
\boxed{
\textbf{Gold Obligation 已经证明 Gap 可计算；
现在模型自己能不能产生足够可靠的 Obligation？}
}
\]

如果答案是否：

接受这个结果。

不要再通过增加 prompt 条款把它“调到通过”。

下一步复杂度必须由错误分布决定，而不是由我们预设的架构决定。