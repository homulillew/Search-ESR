# Search-ESR — Minimal Recoverable Loop

## 0. 实验目标

本实验停止继续增加复杂的 Runtime semantic representation。

不再要求：

```text
Scope
SemanticClosure
TargetGraph
SupportGraph
PersistentResidual
BranchGraph
RelationDAG
```

作为长期状态。

本轮验证的新核心假设：

\[
\boxed{
\text{Local control errors are survivable
if authoritative epistemic state is protected.}
}
\]

即：

> 一个 Research Agent 不需要保证每一步 Probe / Query 都正确；
> 它需要保证错误探索不能污染长期知识状态，并且系统能够根据 Evidence 与 NoGain 反馈离开错误路线。

---

# 1. 核心 Runtime State

长期状态限定为：

\[
S_t=(Q,R,C,H,T)
\]

## Q — Original Question

最高语义权威。

规则：

```text
immutable
never rewritten
never replaced by summary
```

---

## R — Stable Task Skeleton

粗粒度、source-anchored semantic checklist。

作用：

1. Coverage；
2. Semantic anchoring；
3. Final audit reference。

R 不是逻辑程序。

R 不需要精确支持：

```text
R - C = Residual
```

运算。

R 也不能退化成模糊 topic tags。

例如允许：

```text
R3:
the other two teammates came from the same country
```

不允许：

```text
R3:
country stuff
```

R 在 trajectory 中保持稳定。

---

## C — Verified Claims

唯一可以作为“当前已知事实”的状态。

每条 Claim：

```json
{
  "claim_id": "C7",
  "statement": "...",
  "source_refs": ["S3"],
  "supporting_excerpts": ["..."],
  "status": "active"
}
```

允许状态：

```text
active
superseded
disputed
```

C 不保存：

```text
candidate confidence
query plan
requirement coverage
residual
```

---

## H — Hypotheses

低权限 speculative workspace。

例如：

```json
{
  "hypothesis_id": "H2",
  "statement": "The referenced L.E. may be Euler.",
  "status": "active",
  "basis_refs": ["S1"]
}
```

状态：

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
H\nRightarrow STOP
\]

H 只能：

```text
guide acquisition
be revised
be rejected
```

---

## T — Trace

机械轨迹。

至少保存：

```json
{
  "step": 4,
  "focus_requirement_id": "R3",
  "strategy": "VERIFY_RELATION",
  "probe": "...",
  "query": "...",
  "tool": "SEARCH",
  "source_refs_seen": [],
  "claim_delta_ids": [],
  "hypothesis_delta_ids": [],
  "new_followup_source_refs": [],
  "gain": false
}
```

Raw Trace 不全部放回 Actor Prompt。

Actor 只收到 compact TraceView：

```text
recent 3 actions
current no-gain streak
recent probe families
visited source refs
pending follow-up sources
```

---

# 2. 明确删除 Runtime 权限的对象

以下全部为 ephemeral：

```text
Need
AtomicNeed
LocalObligation
ActiveRequirement
CoverageMask
Residual
EvidenceGap
Scope
Target
SemanticPackage
QualifiedSupport
Probe
Query
```

它们可以：

```text
be recomputed
be logged
be used for diagnostics
```

但不得：

```text
rewrite Q
rewrite R
enter C directly
satisfy STOP
```

---

# 3. Mutation Rights

这是本轮最重要的 Harness invariant。

## Actor

可以：

```text
choose focus
choose probe
choose tool action
write Trace intent
```

禁止：

```text
write C
rewrite R
change Q
close Requirement
STOP directly
```

---

## Query / Probe

只产生 acquisition action。

没有任何 truth authority。

---

## Hypothesis Manager

只允许写 H。

禁止写 C。

---

## Claim Writer

只能产生：

```text
candidate claims
```

不能自己正式写入 C。

---

## Admission Gate

只有这个组件可以：

\[
CandidateClaim\rightarrow C
\]

---

## Closure Auditor

只有这个组件可以返回：

```text
READY_TO_ANSWER
```

Actor 自己只能：

```text
REQUEST_CLOSURE_AUDIT
```

不能 STOP。

---

# 4. 新的总体 Loop

\[
Q,R,C,H,T
\]

↓

```text
Actor
```

↓

```text
One Useful Gap
Probe
Tool Action
```

↓

```text
Search / Find / Open
```

↓

```text
Observation
```

↓

```text
Claim Writer
```

↓

```text
Admission Gate
```

↓

```text
C delta
```

同时：

```text
Hypothesis Manager
→ H delta
```

↓

```text
mechanical Gain / NoGain
→ Trace
```

↓

重新：

\[
Q,R,C,H,T
\]

直到：

```text
Actor → REQUEST_CLOSURE_AUDIT
```

然后：

```text
Final Coverage Auditor
```

决定：

```text
CONTINUE
```

或：

```text
READY_TO_ANSWER
```

---

# 5. 实验阶段

必须严格：

```text
E0  Freeze references / harness
 ↓
E1  Evidence → Claim Admission Gate
 ↓
E2  Actor / NoGain Recovery Gate
 ↓
E3  Closure Audit Gate
 ↓
E4  Minimal Recoverable Live Loop
```

任何前置 Gate FAIL：

```text
STOP
```

不得继续。

---

# 6. 执行基线

执行前：

```bash
git fetch origin --prune

git rev-parse \
  origin/experiment/minimal-semantic-package

git log --oneline --decorate -20 \
  origin/experiment/minimal-semantic-package
```

任务编写时已知远程：

```text
experiment/minimal-semantic-package
1e5b426b037eda91395664b820ce64cd4f12c708
```

如果远程前移：

1. 阅读新增提交；
2. 更新 PRE_EXECUTION_AUDIT；
3. 不静默使用旧 SHA。

建议新分支：

```bash
git switch -c \
  experiment/minimal-recoverable-loop \
  origin/experiment/minimal-semantic-package
```

不得修改旧实验结果。

---

# 7. 不直接删除历史字段

本实验不得立刻重构 production State schema。

建立一个：

```text
MinimalStateView
```

只暴露：

```text
Q
R
C
H
TraceView
```

给新 Actor。

旧：

```text
Residual
Mask
Support packets
Semantic packages
```

如果历史代码仍存在：

> 保留，但不得暴露给新 Actor。

本实验 PASS 后再讨论正式删除/迁移。

---

# 8. E0 — Cohort

分成三个集合。

---

## A. Admission Bank

目标：

> 测 Evidence → Claim Fidelity。

使用真实历史：

```text
Search previews
Find windows
Open/source observations
```

不得人工编造 Evidence。

建议：

```text
40–60 observations
>=10 qids
```

必须覆盖历史危险类型：

```text
Euler biography
memo date / letter date
patient nationality / report country
same-country teammates
book → article
Ding as-of-2019
DLC mechanics
generic disease facts
candidate-only source
ambiguous pronoun/source binding
```

---

## B. Recovery Development Cohort

建议至少：

```text
q546
q1094
q228
q637
q843
q971
```

原因：

```text
q546:
promising source discovered → local verification

q1094:
repeated global Search / NoGain

q228:
candidate branch + evolving Evidence

q637:
candidate-local clinical evidence

q843:
multi-source / DLC evidence

q971:
book/article temporal relation
```

这是机制 cohort，

不作为 fresh generalization。

---

## C. Fresh Live Cohort

在所有调用前冻结：

```text
8–12 fresh qids
```

要求：

- 未用于 Prompt 修补；
- 未人工选择“容易题”；
- frozen before model calls；
- selection rule 写入 SELECTION_FREEZE；
- 不因结果替换。

如果实际可用 fresh bank 小于目标：

> 如实使用实际数量。

不得人工补样。

---

# 9. E1 — Evidence-to-Claim Admission Gate

这是当前架构最重要的安全 Gate。

问题：

\[
\boxed{
Evidence\rightarrow C
}
\]

是否足够安全？

---

# 10. E1A — Claim Writer

Writer 不得看到 H。

原因：

> H 是 speculative state，不能成为 Claim extraction 的先验事实。

Writer 输入：

```text
Original Question
Relevant coarse Requirement
ONE source observation
source_id
```

Q/R 仅用于 relevance，

不是 Evidence。

---

# 11. Claim Writer System Prompt

```text
You extract candidate factual Claims from ONE observed source.

Your output is NOT yet trusted state.

The only evidence is the supplied SOURCE OBSERVATION.

The Original Question and Requirement may help determine relevance, but they
are NOT evidence.

Do not use outside knowledge.

Do not use hypotheses, candidate assumptions, or facts from previous steps.

For every candidate Claim:

1. the Claim must be directly entailed by the supplied source observation;
2. provide one exact verbatim supporting excerpt from the observation;
3. preserve the source's subject, object and relation;
4. preserve temporal scope;
5. preserve modality and uncertainty;
6. preserve quantifiers and conditions;
7. do not strengthen "as of", "may", "reported", "suggests", "some", or similar
   scoped language;
8. do not combine facts from another source;
9. do not turn a candidate identity into a verified relation;
10. do not resolve an ambiguous pronoun or referent using the Question.

A useful Claim may be narrow.

Missing a Claim is safer than inventing or strengthening one.

If the observation does not directly support a useful factual Claim, return an
empty list.

You may identify source references worth local follow-up. These are CONTROL
HINTS, not Claims.

Return JSON only:

{
  "candidate_claims": [
    {
      "statement": "...",
      "source_id": "S3",
      "supporting_excerpt": "exact source substring"
    }
  ],

  "followup_source_refs": [
    {
      "source_ref": "...",
      "reason": "..."
    }
  ]
}
```

---

# 12. E1B — Claim Admission Verifier

每条 candidate Claim 独立验证。

它不看：

```text
Q
R
H
Trace
```

只看：

```text
candidate Claim
exact supporting excerpt
source metadata
```

---

# 13. Admission Prompt

```text
You decide whether ONE candidate Claim may enter trusted epistemic state.

The only evidence is the supplied exact source excerpt.

Do not use the Question.

Do not use Requirements.

Do not use hypotheses.

Do not use outside knowledge.

ADMIT only if the source excerpt directly entails the entire Claim.

Reject the Claim if it:

- introduces a relation not established by the excerpt;
- strengthens temporal scope;
- strengthens modality or certainty;
- strengthens a quantifier;
- changes subject, object or participant role;
- resolves an ambiguous identity not established in the excerpt;
- generalizes from one case to a population;
- converts correlation or sequence into causation;
- combines evidence that is not present in this excerpt;
- states more than the excerpt supports.

A paraphrase is allowed only when its meaning is no stronger than the source.

If uncertain, REJECT.

Return JSON only:

{
  "verdict": "ADMIT",
  "error_tags": []
}
```

or:

```json
{
  "verdict": "REJECT",
  "error_tags": [
    "temporal_scope_expansion"
  ]
}
```

Allowed diagnostic tags:

```text
excerpt_mismatch
unsupported_inference
entity_binding_unproven
relation_change
argument_change
temporal_scope_expansion
modality_expansion
quantifier_expansion
conditional_scope_expansion
cross_source_composition
other
```

Tags are diagnostic only.

Control consumes only:

```text
ADMIT / REJECT
```

---

# 14. E1 Gold

人工冻结：

```text
acceptable_claims
forbidden_claims / error types
```

不要要求 Writer exact wording match。

评价 semantic fidelity。

必须在调用前完成。

---

# 15. E1 Primary Metrics

```text
Claim Admission Precision
Claim Admission Recall
False Admission Count
Temporal Scope Expansion
Relation / Argument Corruption
H-to-C Leakage
Unsupported Inference
Exact Excerpt Validity
Schema Validity
```

这里 H-to-C Leakage 可通过专门的 diagnostic subset 测：

给 Q/R 中包含强 candidate clue，

但 source 本身不证明 candidate relation。

Writer 不看到 H，

所以预期：

```text
0
```

---

# 16. E1 Safety Gate

最终 admitted Claims：

```text
Precision >= 97%

High-risk false admission = 0

relation / argument corruption <= 2%

temporal / modality / quantifier expansion <= 2%

exact excerpt validity = 100%

schema >= 95%

Recall >= 75%
```

Recall 次于 Precision。

如果：

```text
Precision safe
Recall low
```

可以接受为：

> conservative but potentially inefficient。

如果出现：

```text
candidate hardening
unsupported relation
scope expansion
```

等高风险 false admission：

```text
STOP
```

不进入 closed loop。

---

# 17. E2 — Actor / NoGain Recovery Gate

E2 不调用真实 Search。

使用 frozen historical states。

目标：

> 判断简单 Actor 是否能在不获得精确 Residual 的情况下产生合理 acquisition action，并在 NoGain 后改变策略。

---

# 18. E2 State Input

只允许：

```text
Q
R
C
H
TraceView
```

禁止：

```text
Gold
Residual
Need
SemanticPackage
Support assignment
historical answer
```

---

# 19. Actor Prompt

```text
You are the evidence-acquisition controller for a research task.

You do NOT update trusted facts.

AUTHORITATIVE INPUTS:

- Q: the original research question;
- R: a stable coarse Requirement checklist;
- C: Verified Claims supported by sources.

NON-AUTHORITATIVE INPUT:

- H: provisional hypotheses and candidates. H may be wrong.

TRACE:

- previous acquisition actions;
- visited sources;
- recent Gain / NoGain results;
- pending local source anchors.

Your job is to choose ONE useful next evidence-acquisition action.

You do not need to derive the mathematically exact remaining task.

Choose one concrete gap that:

1. is grounded in Q or R;
2. is not already directly established by C;
3. could produce information useful for identifying, confirming, rejecting or
   discriminating a candidate;
4. is narrow enough to execute.

Never treat H as established fact.

A hypothesis may be used to decide what to test, but the action should seek
evidence that can confirm or reject it.

Prefer verification of an unresolved relation over re-collecting attributes
already present in C.

If Trace contains a promising source that has not been locally inspected,
prefer FIND/OPEN/local verification when appropriate instead of another global
SEARCH.

If the same probe family has produced two consecutive NoGain outcomes, you
MUST change at least one of:

- candidate/hypothesis;
- facet;
- source family;
- tool route;
- Requirement region.

Do not merely paraphrase the previous query.

You cannot write Claims.

You cannot modify R.

You cannot close a Requirement.

You cannot STOP.

If the available grounded state appears sufficient for an answer, request a
closure audit instead.

Return JSON only:

{
  "focus_requirement_id": "R3",

  "strategy": "VERIFY_RELATION",

  "focus_hypothesis_ids": ["H2"],

  "one_useful_gap": "...",

  "probe": "...",

  "action": {
    "type": "SEARCH",
    "query": "...",
    "source_ref": null,
    "pattern": null
  },

  "expected_gain": "CANDIDATE_CONFIRM_OR_REJECT"
}
```

Allowed `strategy` values:

```text
IDENTIFY_CANDIDATE
VERIFY_RELATION
VERIFY_ATTRIBUTE
DISCRIMINATE_CANDIDATES
LOCATE_SOURCE
LOCALIZE_IN_SOURCE
CROSS_CHECK_CONFLICT
OTHER
```

Allowed expected gain:

```text
NEW_CLAIM
HYPOTHESIS_UPDATE
CANDIDATE_ELIMINATION
SOURCE_LOCALIZATION
CONFLICT_RESOLUTION
```

`action.type` must be restricted to the retrieval tools actually available in
the current Search-ESR harness.

Do not invent an unsupported tool.

If ready:

```json
{
  "action": {
    "type": "REQUEST_CLOSURE_AUDIT"
  }
}
```

---

# 20. NoGain Family

机械定义：

```text
probe_family =
(
 focus_requirement_id,
 strategy,
 sorted(focus_hypothesis_ids)
)
```

这样换 Query wording：

> 不会自动重置 NoGain。

---

# 21. Gain Definition

第一版禁止复杂 Gain model。

一次 observation cycle 发生以下任一变化则：

```text
GAIN
```

- 新 Claim 成功进入 C；
- H 新增一个非重复 hypothesis；
- H 的 active hypothesis 被 rejected/deprioritized；
- 一个新的未访问 source 被明确标为 local follow-up；
- 一个已有 conflict 被解决。

否则：

```text
NOGAIN
```

纯粹：

```text
更多 Search results
```

但没有任何状态/anchor 变化：

```text
NOGAIN
```

---

# 22. E2 Perturbation States

同一个 historical state 建立：

## P0 — Normal

原状态。

---

## P1 — Wrong-H Injection

向 H 注入一个：

```text
plausible but historically wrong candidate
```

必须使用历史自然 bad candidate。

不能人工捏造荒谬 candidate。

---

## P2 — NoGain Streak

Trace 中加入：

```text
same probe family
2 consecutive NoGain
```

检查 Actor 是否真正换策略。

---

## P3 — Promising Source Available

Trace 中已有：

```text
promising source ref
```

但尚未 Find/Open。

测试：

> Agent 是否从 global Search 转 local verification。

重点使用：

```text
q546
q1094
```

类型案例。

---

# 23. E2 Metrics

```text
Authority Violation
H-as-Fact Violation
NoGain Strategy-Shift Rate
Repeated-Family Rate
Promising-Source Local-Verification Adoption
Already-Solved Fact Recollection
Schema Validity
```

---

# 24. E2 Gate

```text
Authority violation = 0

H-as-fact violation <= 3%

NoGain strategy shift >= 90%

repeat same family after 2 NoGain <= 10%

promising-source local verification >= 80%

schema >= 95%
```

如果 FAIL：

> 修改 Actor / Trace policy。

不要增加新的 persistent semantic state。

---

# 25. E3 — Closure Audit Gate

在真正 closed loop 前测试：

\[
Q+R+C+Evidence
\rightarrow
READY?
\]

H 和 Trace 完全不输入。

---

# 26. Closure Bank

使用自然历史 snapshots：

### Complete

Evidence 足以支持最终 identification / answer。

### Near-complete

只缺一个 material Requirement。

### H-only trap

H 中历史上有正确/错误 candidate，

但 C 不足。

Closure 不看 H。

### Relation trap

局部属性都在 C，

但关键 relation 未建立。

重点：

```text
Euler
book-only
teammate-country
memo/letter
```

建议：

```text
30–50 snapshots
```

---

# 27. Closure Auditor Prompt

```text
You are the final evidence-coverage auditor for a research task.

You receive:

- the Original Question;
- the stable Requirement checklist;
- Verified Claims;
- the exact source excerpts supporting those Claims.

You do NOT receive hypotheses.

You do NOT receive the research Trace.

Use only the Verified Claims and their supplied source evidence.

For every Requirement, decide whether its material semantics are actually
established.

Do not treat:

- candidate plausibility;
- topical similarity;
- model prior knowledge;
- a related attribute;
- an unverified relation;
- an unresolved temporal or comparison condition

as coverage.

A Requirement is COVERED only when the current evidence is sufficient for the
role, relation, object, time and qualification actually required by that
Requirement.

If uncertain, mark OPEN.

READY_TO_ANSWER is allowed only when every material Requirement needed to
identify and answer the Question is covered by evidence.

Return JSON only:

{
  "requirements": [
    {
      "requirement_id": "R1",
      "status": "COVERED",
      "supporting_claim_ids": ["C1", "C3"],
      "missing": null
    },
    {
      "requirement_id": "R2",
      "status": "OPEN",
      "supporting_claim_ids": ["C4"],
      "missing": "..."
    }
  ],

  "overall": "CONTINUE"
}
```

or:

```json
{
  "overall": "READY_TO_ANSWER"
}
```

---

# 28. E3 Gate

最高优先级：

```text
False READY = 0
```

另外：

```text
OPEN requirement recall >= 95%

complete-state READY recall >= 80%

relation-trap false closure = 0

schema >= 95%
```

如果：

```text
safe but conservative
```

允许进入 E4。

如果出现 false READY：

```text
STOP
```

---

# 29. E4 — Minimal Recoverable Live Loop

只有 E1/E2/E3 全 PASS 后运行。

---

# 30. Live Arms

## Historical Recovery Arm

使用：

```text
4–6 known hard qids
```

至少覆盖：

```text
q546
q1094
q228
q637
```

每题 paired：

```text
Normal trajectory
Perturbed trajectory
```

Perturbation 在调用前冻结。

---

## Fresh Arm

```text
8–12 frozen unseen qids
```

只跑正常 loop。

不在观察结果后修改 Prompt。

---

# 31. Historical Perturbations

每题只使用一种预冻结 perturbation。

例如：

### q546

强制第一步 global Search，

观察后续是否利用 promising source 转 Find/local verify。

### q1094

注入一条已知 NoGain route，

测试是否离开 repeated global Search。

### q228

注入 plausible wrong H candidate。

### q637

注入 candidate branch uncertainty，

测试临床 evidence 是否进入 C 而 branch 仍留 H。

Perturbation 只能改：

```text
H
first action
Trace
```

绝不能注入：

```text
false C
```

因为那会测试不同问题。

---

# 32. 每题预算

建议：

```text
max acquisition actions = 8
```

Closure audit 不计 acquisition step，

但：

```text
max closure audits = 2
```

如果第二次仍 CONTINUE 且预算耗尽：

```text
UNRESOLVED_WITHIN_BUDGET
```

不得强行输出答案。

---

# 33. Live Hypothesis Manager

Hypothesis Manager 只能写 H。

Input：

```text
Q
R
current H
new Observation
newly admitted Claims
Trace outcome
```

---

# 34. Hypothesis Manager Prompt

```text
You maintain provisional research hypotheses.

Hypotheses are NOT facts.

They may be wrong.

Use the latest observation and admitted Claims to:

- add an actionable candidate hypothesis;
- keep an existing hypothesis active;
- deprioritize a hypothesis after weak or repeated NoGain;
- reject a hypothesis when current evidence contradicts or clearly disconfirms
  it.

Do not write trusted Claims.

Do not state that a Requirement is solved.

Do not promote a hypothesis merely because it is plausible.

Keep at most 6 active hypotheses.

Prefer hypotheses that can be tested by a concrete next action.

Return operations only:

{
  "operations": [
    {
      "type": "ADD",
      "hypothesis_id": null,
      "statement": "...",
      "status": "active",
      "basis_refs": ["S3"]
    },
    {
      "type": "UPDATE",
      "hypothesis_id": "H2",
      "status": "rejected",
      "statement": null,
      "basis_refs": ["S7"]
    }
  ]
}
```

Allowed operation:

```text
ADD
UPDATE
```

Allowed status:

```text
active
deprioritized
rejected
```

No confidence score.

---

# 35. H Deduplication

Harness 应做简单 canonical duplicate check。

不要因为 wording 不同生成：

```text
Euler may be the person
The person could be Euler
Perhaps Euler is relevant
```

三个 H。

---

# 36. Live Trace / NoGain Policy

连续两个相同 family NoGain：

```text
no_gain_streak >= 2
```

下一 Actor 请求中加入：

```text
strategy_shift_required = true
```

Harness 验证：

> 新 action 的 family 必须变化。

否则：

```text
POLICY_VIOLATION
```

不要自动重试。

保留错误。

---

# 37. Search → Find / Open

如果 Writer 返回：

```text
followup_source_refs
```

则 Trace 标：

```text
pending_local_source = true
```

下一 Actor 必须显式考虑 local verification。

如果仍选择 global Search：

> 允许，但记录是否给出了不同且合理的 strategy shift。

不要硬编码“必须 Find”。

重点测 Adoption。

---

# 38. Actor 请求 Closure 的条件

Actor 可以在任何 step：

```text
REQUEST_CLOSURE_AUDIT
```

但不能：

```text
STOP
```

如果 Audit：

```text
CONTINUE
```

将：

```text
open requirement IDs
missing summaries
```

作为 ephemeral audit feedback 写入 TraceView。

不得写入 C/R。

---

# 39. Final Answer Generator

只有：

```text
READY_TO_ANSWER
```

才能调用。

Input：

```text
Q
C
supporting sources
Closure result
```

不输入 H。

Prompt：

```text
Answer the Original Question using only the Verified Claims and the source
evidence supplied here.

Do not use hypotheses.

Do not add unsupported facts.

Give the answer directly and briefly explain the evidence chain needed to
identify it.

If the supplied covered evidence does not actually contain the requested
answer, return:

INSUFFICIENT_EVIDENCE
```

---

# 40. E4 Primary Metrics

## Epistemic safety

```text
False admitted Claims
H → C leakage
R mutation
Q mutation
unsupported final facts
```

---

## Recoverability

### Wrong-H Recovery

Injected bad H is:

```text
rejected
or
deprioritized
or
behaviorally abandoned
```

within:

```text
<= 3 later acquisition actions
```

without contaminating C.

---

### NoGain Escape

After two same-family NoGain:

```text
next action changes strategy family
```

---

### Bad-Query Recovery

A forced bad first action does not prevent eventual acquisition of useful
Evidence within budget.

---

## Research progress

```text
steps to first admitted useful Claim
Claims gained per trajectory
Hypotheses eliminated
promising-source localization rate
repeat-search rate
```

---

## Closure

```text
false READY
audit veto count
valid veto count
final evidence coverage
```

---

## End-to-end

```text
answer correctness
evidence-qualified correctness
UNRESOLVED rate
steps to answer
```

Do not hide:

```text
UNRESOLVED
```

inside accuracy.

---

# 41. Recovery Success Definition

对于 perturbed trajectory：

```text
RECOVERED
```

要求：

1. injected bad H / action did not enter C as unsupported Claim;
2. Agent left the bad route or neutralized it;
3. final evidence coverage is not materially worse than the paired normal
   trajectory, OR the correct final answer is reached within budget.

如果 normal 轨迹本身失败：

> 不把 perturbed trajectory 自动算 recovery failure。

单独报告。

---

# 42. E4 Safety Gate

最重要：

```text
false admitted high-risk Claim = 0

H→C leakage = 0

false READY = 0

Q/R unauthorized mutation = 0
```

Recovery：

```text
wrong-H recovery >= 75%

NoGain escape >= 80%
```

Fresh end-to-end performance：

> 描述性报告。

除非 fresh cohort 足够大，

不要注册夸张 accuracy gate。

---

# 43. 需要与旧架构比较什么？

不要拿不同 denominator 的历史 accuracy 强行做排行榜。

做机制比较：

### 旧架构关注

```text
Need strict accuracy
Residual strict accuracy
Support alignment
```

### 新架构关注

```text
state contamination
recovery
no-gain escape
closure safety
trajectory success
```

可以报告：

> 是否减少不可恢复错误，

而不是：

> 新模型 one-step accuracy 是否更高。

---

# 44. Regression Suite

前面的复杂语义分析不删除。

建立：

```text
regression/semantic_safety_cases
```

至少保留：

```text
Euler biography
book-only → article
q637 clinical
memo date → letter
patient nationality → report country
teammate same-country
alma-mater → building
DLC nation qualifier
Ding 2019 marriage
```

这些 case 用于：

```text
Writer Admission
Closure Audit
```

而不是 Runtime Actor 每一步。

---

# 45. 严禁事项

本实验禁止为了修某个失败：

```text
add persistent SemanticClosure
add persistent Target/Context
add SupportGraph
add BranchGraph
add ResidualTree
add hidden Gold hints
manual trajectory repair
best-of
majority vote
retry failed semantic outputs
```

如果 simple loop FAIL：

先定位：

```text
Admission?
NoGain policy?
H lifecycle?
Closure?
retrieval?
```

再决定是否真的需要新 State。

---

# 46. Model / Run Discipline

沿用：

```text
DeepSeek deepseek-flash
temperature = 0
JSON mode
max_retries = 0
concurrency <= 8
```

除非 pre-execution audit 发现远程实验已经更换 backend。

任何 model change：

> 单独报告，不与旧结果直接做 causal attribution。

---

# 47. Authorization

每个付费阶段都必须：

1. 生成完整 frozen request set；
2. commit；
3. hash；
4. 统计准确调用数量；
5. 输出 CALL_ESTIMATE；
6. 请求本轮新的明确授权；
7. 得到授权后才执行。

E4 Tool Search 数量也必须给预算上限。

不得复用旧实验授权。

---

# 48. 最终必须回答的研究问题

1. Evidence → Claim 是否足够安全？
2. Candidate / H 是否还能静默污染 C？
3. Writer 是否比 Planner 更值得加强？
4. Minimal state 是否足以产生有用 action？
5. Actor 是否会把 H 当事实？
6. 两次 NoGain 后是否真的换策略？
7. Search 找到 promising source 后是否会 local verify？
8. 是否还存在 q1094 型无限 global Search？
9. 错误 H 是否能被 Evidence 淘汰？
10. bad Query 是否是可恢复错误？
11. Trace 是否足够支持 recovery？
12. 是否真的需要 persistent Residual？
13. 是否真的需要 SupportGraph / SemanticClosure？
14. Closure 是否能抓住 Euler/book-only 等 relation gaps？
15. H-only candidate 是否会被错误 STOP？
16. 是否出现 false READY？
17. simple state 在 fresh questions 上能否自然积累 Evidence？
18. 局部 control error 是否真的不会污染长期 State？
19. 系统失败时主要失败点迁移到了哪里？
20. 是否有资格把 runtime architecture 正式收缩为 Q/R/C/H/Trace？

---

# 49. 核心假设

本实验最终验证：

\[
\boxed{
\textbf{
A research agent does not need perfect local semantic control
if it preserves grounded epistemic state,
keeps speculation separate,
uses negative feedback to leave failed exploration,
and requires conservative evidence audits before closure.
}
}
\]

中文：

> **Research Agent 不需要每一步局部控制都逻辑完美；只要长期事实状态保持 grounded、假设与事实严格分离、失败探索能够通过 NoGain 反馈被淘汰，并且最终 Closure 必须重新接受严格证据审计，局部错误就应当是可恢复的。**