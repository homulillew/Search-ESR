# Search-ESR — Stage 5-R: OneGap Recoverability

## 0. 本实验的研究位置

本实验从 **Stage 4：Stable Task Skeleton** 继续。

当前已经接受的基础是：

```text
Q — Original Question
R — Stable Task Skeleton
C — Verified Claims
H — Working Hypotheses
T — Mechanical Trace
```

长期状态记为：

\[
S_t=(Q,R,C,H,T)
\]

本实验不重新研究：

```text
Evidence → Claim Writer
Claim Admission
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

特别说明：

此前 `experiment/minimal-recoverable-loop` 中重新设计的 control-blind Writer + single-excerpt Admission 属于一次独立诊断实验。

保留它的历史代码、原始结果和结论，不删除、不修改。

但是：

```text
DO NOT use its E1 result as the prerequisite gate of this experiment.
DO NOT continue Writer v2 / Admission v2 from that branch.
DO NOT make Evidence→Claim the primary research question again.
```

本实验重新回到我们此前已经获得正向信号的设计：

```text
Current OneGap
+ existing C
+ new Observation
→ selective candidate Claims
→ grounded evidence verification
→ C
```

其中：

```text
OneGap controls relevance.
Evidence controls truth.
```

本轮实验本身不执行上述 Claim 写入链，只研究 OneGap / Actor / Recovery。

---

# 1. 核心研究问题

Stage 5 之前试图解决：

\[
R+C\rightarrow Supported/Partial/Full
\]

并进一步得到：

\[
Residual=R-Supported(C)
\]

这导致系统需要高度精确地判断：

- relation binding；
- qualifier；
- scope；
- partial support；
- semantic subtraction。

本实验不再要求这些局部判断一次正确。

新的研究问题是：

\[
\boxed{
Q,R,C,H,T
\rightarrow
OneGap
}
\]

在没有精确 Residual 的情况下：

1. 模型能否产生一个**足够有用、可执行**的 OneGap？
2. 当 OneGap 选错时，NoGain / Trace 是否能推动下一轮换方向？
3. 当 H 是错误候选时，Actor 是否把它当作待验证对象，而不是事实？
4. 当已有 promising source 时，Actor 是否会利用它，而不是机械重复 global Search？
5. 是否真的需要 persistent Residual 才能得到合理的下一步行动？

本实验验证的是：

\[
\boxed{
P(\text{recover}\mid\text{local control error})
}
\]

而不是：

\[
P(\text{OneGap exact})
\]

---

# 2. OneGap 的定义

OneGap 是：

> 当前这一轮最值得调查的一个问题。

它是 **ephemeral control object**。

它不是：

```text
State
Truth
Residual
Coverage
Requirement status
Closure result
```

明确：

\[
OneGap_t \neq R-Supported(C)
\]

也不要求：

```text
complete
unique
globally optimal
stable across repeated generations
```

只要求：

### A. Anchored

可以追溯到 Q 或某个 R。

### B. Not obviously solved

当前 C 没有直接、明确地已经建立它。

这里禁止要求严格证明：

\[
C\nmodels OneGap
\]

只判断是否“明显已经解决”。

### C. Actionable

可以转成一个实际的：

```text
SEARCH
FIND
OPEN
```

动作。

### D. Low commitment

如果涉及 H，只能表达为待验证问题。

允许：

```text
Verify whether the target book references Euler.
```

不允许：

```text
Find where the target book references Euler.
```

如果当前并没有证据证明它一定引用 Euler。

### E. Potentially informative

如果调查成功，至少可能带来以下之一：

```text
new useful Claim
hypothesis confirmation/rejection
candidate elimination
source localization
conflict resolution
```

---

# 3. OneGap 的权限

OneGap 只有：

```text
ACTION AUTHORITY
```

OneGap 没有：

```text
TRUTH AUTHORITY
STATE MUTATION AUTHORITY
REQUIREMENT CLOSURE AUTHORITY
STOP AUTHORITY
```

OneGap 不得：

```text
write C
rewrite R
rewrite Q
mark Requirement covered
remove unresolved semantics
trigger final answer directly
```

下一轮可以完全推翻上一轮 OneGap。

---

# 4. 当前 State 的职责

## Q

最高任务权威。

```text
immutable
```

---

## R

Stage 4 产生的 coarse、source-anchored Task Skeleton。

R 只描述：

> 原问题最终要求什么。

R 不描述：

> 当前研究进度。

禁止增加：

```text
supported = true
coverage = 0.7
residual = ...
scope = ...
```

---

## C

Verified Claims。

仅包含已经有 Evidence 支持的事实。

本实验直接复用历史已经确认的 Claims。

不要重新运行新的 Writer/Admission 来重建 C。

如果某个历史 Claim 的真实性存在明确争议：

```text
exclude the state
or
mark that Claim unavailable
```

不得为了组成实验状态人工修复 Claim。

---

## H

低权限候选/假设。

H 允许错误。

H 可以影响：

```text
what to investigate
```

H 不可以影响：

```text
what is true
```

---

## T / TraceView

只提供近期控制反馈。

建议给 Actor：

```text
recent 2–3 actions
recent OneGap
recent strategy/facet
Gain / NoGain
visited source refs
pending promising source refs
```

不提供完整历史 reasoning。

---

# 5. 本实验不使用 Writer / Admission

这是本轮非常重要的边界。

本实验阶段：

```text
NO Claim Writer calls
NO Admission calls
NO Search calls
NO Find calls
NO Open calls
NO Closure calls
```

第一轮只测试：

```text
Frozen State
→ Actor
→ OneGap + next Action
```

因此如果实验 FAIL，可以直接归因于：

```text
OneGap generation
Actor control
Trace / NoGain policy
H handling
```

而不是再混入：

```text
Writer
Admission
retrieval
evidence reading
closure
```

---

# 6. Git / 历史实验边界

执行前：

```bash
git fetch origin --prune
```

必须读取：

```text
experiment/ephemeral-obligation-decomposition
experiment/gap-evidence-claim-loop
experiment/skeleton-state-alignment
experiment/claim-requirement-support-alignment
experiment/minimal-recoverable-loop
```

目的：

- Stage 4 提供 Stable Skeleton；
- `gap-evidence-claim-loop` 提供已有 Claim extraction 结论；
- Stage 5 branches 提供自然 bad cases；
- `minimal-recoverable-loop` 只作为“不要继续使用的新 Writer/Admission 路径”的历史记录。

建议新分支：

```text
experiment/onegap-recovery-control
```

不要修改任何旧实验结果。

不要 cherry-pick `minimal-recoverable-loop` 的 Writer/Admission 实验逻辑作为本轮主路径。

如果工程需要复用公共 harness，可以复用纯机械代码，但不得改变本轮研究变量。

---

# 7. E0 — Frozen State Bank

目标：

建立自然、可复查的：

\[
Q,R,C,H,T
\]

状态。

优先使用历史真实状态，不人工编造语义状态。

建议：

```text
12–18 states
>= 6 qids
```

至少覆盖以下类型。

---

## Case A — Euler relation

历史问题：

```text
Euler biography is known
but target-book → Euler relation is not established
```

用于测试：

```text
related attribute ≠ target relation
```

---

## Case B — Book → Article

已有：

```text
book
book publication date
```

缺：

```text
later article
article-book temporal relation
```

---

## Case C — Teammate same-country

已有：

```text
Jerry nationality
teammate identities
```

缺：

```text
the other two teammates share a country
```

---

## Case D — DLC qualifier

已有部分：

```text
technology changes
religion/mechanics changes
Ottoman changes
```

仍有：

```text
specific playable European nation
```

类型的未决限定。

---

## Case E — Memo / Letter

已有：

```text
memorandum date
```

缺：

```text
actual letter date / required temporal relation
```

---

## Case F — q637 clinical

已有：

```text
candidate-local clinical facts
```

但：

```text
global candidate identity
```

仍然可能只属于 H。

---

## Case G — q228 / candidate branch

用于测试：

```text
candidate evolution
existing C
wrong H
```

---

## Case H — q546 / q1094

用于测试：

```text
repeated Search
NoGain
promising source
local verification opportunity
```

---

# 8. State Construction 原则

每个 frozen state：

```json
{
  "qid": "...",
  "Q": "...",
  "R": [...],
  "C": [...],
  "H": [...],
  "TraceView": [...]
}
```

要求：

### C

只能来自历史已经观察到并接受的 grounded facts。

不得为实验方便注入 false C。

### H

Normal state 使用自然历史候选。

Perturbation 可以加入：

```text
historically observed plausible but wrong candidate
```

不得人工发明明显荒谬 H。

### Trace

必须来自：

```text
真实历史 action
```

或明确标记：

```text
EXPERIMENTAL_PERTURBATION
```

不得让 reviewer 误以为扰动是自然历史。

---

# 9. Experimental Conditions

每个基础 State 根据适用性生成以下 paired conditions。

不要求每个 state 强行都有四个 condition。

---

## P0 — Normal

原始：

\[
Q,R,C,H,T
\]

目标：

观察自然生成的 OneGap。

---

## P1 — Wrong-H Injection

只修改 H。

加入：

```text
historically plausible but wrong / weak candidate
```

不修改：

```text
Q
R
C
```

测试：

> Actor 会不会把 H 当事实？

理想输出：

```text
verify whether H is correct
```

而不是：

```text
assume H and reason downstream
```

---

## P2 — Two-NoGain Recovery

在 Trace 中加入：

```text
same control family
two consecutive NoGain
```

family 第一版机械定义可以采用：

```text
(
  focus_requirement_id,
  semantic strategy,
  focused hypothesis IDs / candidate
)
```

但不要把 query wording 当 family identity。

测试：

\[
2\times NoGain
\rightarrow
\text{real strategy change}
\]

真正的 strategy change 至少改变一项：

```text
candidate
facet
source family
Requirement region
verification target
tool route when semantically meaningful
```

仅把：

```text
Euler biography
```

改写为：

```text
Euler early life
```

不算换方向。

---

## P3 — Promising Source Available

Trace 中加入：

```text
a previously discovered source looks promising
not locally inspected yet
```

重点：

```text
q546
q1094
```

测试：

> Actor 是否考虑利用已有 source 做 local verification？

允许：

```text
FIND
OPEN
```

也允许有充分理由重新 SEARCH。

本实验不硬编码：

```text
promising source → must FIND
```

只评价是否真正利用了新反馈。

---

# 10. Actor 的系统提示词

使用以下 Prompt，不加入 Residual、Support Mask、Gold Gap 或历史答案。

```text
You control the next evidence-acquisition step of a research task.

You receive:

Q:
the original question.

R:
a stable coarse checklist of what the original question ultimately requires.

C:
facts already supported by observed evidence.

H:
provisional hypotheses or candidates. H may be wrong.

TraceView:
recent investigation actions, Gain/NoGain feedback, visited sources,
and pending source opportunities.

Your job is to choose ONE useful next investigation target, called OneGap,
and one next evidence-acquisition action.

OneGap is NOT the exact residual task.

You do NOT need to determine everything that remains unresolved.

You do NOT need to produce the unique or optimal next step.

Choose one investigation that is:

1. grounded in Q or one Requirement in R;
2. not already directly established by C;
3. narrow enough to investigate;
4. likely to produce useful new evidence, eliminate a candidate,
   test a hypothesis, localize a source, or resolve a conflict.

H is NOT evidence.

If OneGap concerns a hypothesis, phrase the investigation as a test:

    verify whether ...
    determine whether ...
    check whether ...

Do not assume the hypothesis is already true.

Do not invent missing facts from Q, R, H, or Trace.

Prefer testing an unresolved relation over re-collecting an attribute
already clearly present in C.

If recent actions on the same route produced two consecutive NoGain outcomes,
choose a materially different route.
Changing only query wording is not a strategy change.

If TraceView contains a promising source that has not been locally inspected,
consider whether local verification of that source is more useful than
another global search.

You cannot:

- write or modify C;
- modify Q or R;
- mark a Requirement solved;
- produce a final answer;
- STOP the research task.

If the current evidence appears sufficient, output REQUEST_CLOSURE_AUDIT
instead of deciding completion yourself.

Return JSON only:

{
  "focus_requirement_id": "R3",
  "one_gap": "...",
  "strategy": "VERIFY_RELATION",
  "hypothesis_ids_under_test": ["H2"],
  "action": {
    "type": "SEARCH",
    "query": "...",
    "source_ref": null,
    "pattern": null
  }
}
```

---

# 11. Allowed Strategy

保持很小。

```text
LOCATE_SOURCE
IDENTIFY_CANDIDATE
VERIFY_RELATION
VERIFY_ATTRIBUTE
DISCRIMINATE_CANDIDATES
CROSS_CHECK_CONFLICT
LOCALIZE_IN_SOURCE
OTHER
```

Strategy 只是 Trace / analysis label。

它不是长期 State。

不要因为分类困难继续扩充 taxonomy。

---

# 12. OneGap Review Rubric

禁止建立唯一 Gold OneGap。

禁止 Exact Match。

Reviewer 对每个实际输出只判断：

```text
ACCEPTABLE
WEAK_BUT_USABLE
UNSAFE
```

---

## ACCEPTABLE

满足：

```text
anchored in Q/R
not obviously solved by C
actionable
does not harden H into fact
reasonable evidence value
```

不要求最优。

---

## WEAK_BUT_USABLE

例如：

```text
有一点重复
不是最优路径
过窄
没有利用最好的 source
```

但：

> 执行后仍可能产生有效信息，而且不会污染事实状态。

这种输出不能算 fatal failure。

这是 recovery architecture 的重要假设。

---

## UNSAFE

例如：

```text
treats H as established fact
contradicts visible C
focuses on something completely unrelated to Q/R
silently invents a relation
requires an unavailable tool
after explicit 2×NoGain merely paraphrases the same route
```

---

# 13. Secondary Error Tags

只用于分析。

不要用于 Runtime。

建议：

```text
H_AS_FACT
ALREADY_SOLVED_RECOLLECTION
UNRELATED_TO_REQUIREMENT
UNSUPPORTED_PREMISE
NON_ACTIONABLE
SAME_ROUTE_AFTER_NOGAIN
MISSED_PROMISING_SOURCE
QUERY_ONLY_PARAPHRASE
PREMATURE_CLOSURE_REQUEST
OTHER
```

不要再为每个 bad case 创建新的 Runtime semantic field。

---

# 14. Primary Metrics

## A. OneGap Usability

```text
(ACCEPTABLE + WEAK_BUT_USABLE) / all valid outputs
```

分别报告：

```text
Normal
Wrong-H
NoGain
Promising-source
```

---

## B. Unsafe OneGap Rate

```text
UNSAFE / all outputs
```

---

## C. H-as-Fact Rate

P1 中：

```text
H_AS_FACT / P1 outputs
```

---

## D. NoGain Escape Rate

P2 中：

```text
materially changed route
/
all valid P2 outputs
```

这是本实验最重要的指标之一。

---

## E. Same-route-after-NoGain

两次 NoGain 后仍重复相同语义路线的比例。

---

## F. Already-Solved Recollection

已有明确 C 的事实又被当成核心 OneGap 的比例。

重点检查：

```text
Jerry nationality
known biography attributes
already verified dates/attributes
```

---

## G. Promising-source Usage

P3 中：

```text
local verification chosen
OR
global action with materially justified alternative route
```

单独报告：

```text
FIND/OPEN adoption
global fallback
mechanical repeated Search
```

不要把“没有 Find”自动计错。

---

## H. Authority Violations

必须为：

```text
0
```

包括：

```text
writes C
rewrites R
rewrites Q
claims Requirement closure
produces final answer directly
```

---

# 15. Gate

第一轮机制实验建议采用：

```text
Authority violations = 0

H-as-fact <= 5%

Normal usability >= 80%

NoGain escape >= 85%

same-route after 2×NoGain <= 15%

already-solved recollection <= 15%

schema validity >= 95%
```

Promising-source 指标第一轮建议描述性报告。

如果自然样本足够，可预注册：

```text
useful response to promising source >= 75%
```

不要要求：

```text
OneGap exact accuracy >= X
```

不存在这个指标。

---

# 16. Replicates

第一轮优先：

```text
1 response per condition
```

避免用重复采样制造：

```text
best-of
majority vote
```

如果需要稳定性实验，必须另行注册。

同一 State 的两个不同 ACCEPTABLE OneGap：

```text
不算 instability failure
```

因为 OneGap 本来允许多解。

---

# 17. 本轮特别禁止

```text
Gold Residual
Gold OneGap exact string
Support Mask
semantic subtraction
Target/Context package
QualifiedSupport
persistent ActiveRequirement
persistent OneGap
OneGap confidence score
OneGap → C
OneGap → closure
automatic repair
retry
best-of
majority vote
```

特别禁止：

> 因为 Euler / DLC / book-article 某一个 case 失败，就新增 persistent semantic field。

---

# 18. 旧 Writer / Admission 的处理

此前：

```text
experiment/minimal-recoverable-loop
```

的：

```text
Writer
single-excerpt Admission
E1 Gate
```

不得作为本实验 prerequisite。

其结果保持：

```text
historical diagnostic
```

不要删除。

但本轮不：

```text
continue
repair
rerun
optimize
```

这条路径。

未来进入真实 live loop 时，Claim extraction 恢复此前已经得到正向结果的方向：

```text
OneGap + existing C + Observation
→ selective candidate Claims
```

Candidate Claim 的 truth 只能由真实 Observation 支持。

不要使用：

```text
control-blind broad fact extraction
```

作为默认生产 Writer。

---

# 19. 本实验不回答的问题

本轮不声称验证：

```text
Evidence→Claim end-to-end safety
Closure safety
full research accuracy
fresh end-to-end accuracy
Search ranking quality
Find superiority
final answer correctness
```

它只回答：

\[
\boxed{
Q,R,C,H,T
}
\]

是否足以产生一个：

\[
\boxed{
useful\ OneGap
}
\]

以及：

\[
\boxed{
bad\ local\ control
\rightarrow
feedback
\rightarrow
strategy\ shift
}
\]

是否成立。

---

# 20. 如果本实验 PASS

下一实验：

```text
Stage 5-C — Closure Safety
```

重点：

```text
Euler biography trap
book-only → article trap
memo → letter trap
teammate-country trap
DLC qualifier trap
q637 partial-local evidence
true complete states
```

最高优先：

```text
False READY = 0
```

之后才进入：

```text
Stage 5-L — Minimal Live Recovery Loop
```

把：

```text
OneGap
Search/Find/Open
existing gap-conditioned Claim extraction
C/H update
NoGain
Closure
```

真正串起来。

---

# 21. 如果本实验 FAIL

先定位：

```text
OneGap cannot use C?
H hardening?
Trace insufficient?
NoGain representation ineffective?
R too coarse for action?
promising-source information not usable?
```

只有当出现明确证据：

> 在 Q/R/C/H/T 下，同一类不可恢复失败持续发生，并且缺少某种信息正是失败的必要原因，

才考虑新增长期 State。

不得因为单个 semantic bad case 重新引入：

```text
Residual
Scope
Target
SupportGraph
SemanticPackage
```

---

# 22. 执行纪律

沿用：

```text
temperature = 0
max_retries = 0
no best-of
no failed-output replacement
all failures stay in denominator
freeze inputs before model calls
freeze rubric before model calls
do not change Gold/review rules after results
```

本轮没有检索调用。

在实际模型调用前：

1. 冻结全部 State packets；
2. 冻结全部 P0/P1/P2/P3 变体；
3. 冻结 reviewer rubric；
4. 生成完整 request set；
5. commit；
6. hash；
7. 输出精确 CALL_ESTIMATE；
8. **重新请求用户明确授权后才允许付费调用。**

---

# 23. 最终必须回答的问题

1. 不提供 Residual 时，Q/R/C/H/T 能否产生可用 OneGap？
2. OneGap 是否经常重复 C 已经确认的事实？
3. H 是否会被 Actor 当成事实？
4. Wrong H 是否主要诱导“验证动作”，还是诱导下游事实假设？
5. 两次同方向 NoGain 后，模型是否真正换路线？
6. Query 改写是否会伪装成 strategy shift？
7. Promising source 是否会影响下一步选择？
8. Stage 5 的 Euler 型错误，在 OneGap 层主要表现为什么？
9. Stage 5 的 P→U 错误是否主要转化为低成本重复调查？
10. Stage 5 的 false-full 类型是否已经从 Actor 控制问题迁移为 Closure 问题？
11. OneGap 是否真的需要精确表示完整剩余任务？
12. 当前是否仍有证据支持 persistent Residual？
13. 当前最主要的不可恢复控制失败是什么？
14. 是否有资格进入 Closure Safety 实验？
15. 是否有资格进入最小 live recovery loop？

---

# 24. 本实验最终要验证的核心假设

\[
\boxed{
\textbf{
OneGap does not need to be an exact residual.
It only needs to be a useful, revisable control decision.
}
}
\]

进一步：

\[
\boxed{
\textbf{
If grounded facts remain protected,
a locally wrong OneGap should be recoverable through
Evidence, NoGain feedback, and later Closure audit,
without introducing a persistent semantic residual state.
}
}
\]

中文：

> **OneGap 不需要精确描述“真正还剩什么”。它只需要作为当前一轮一个有价值、可执行、可被下一轮推翻的调查决策。只要 C 保持 grounded、H 不拥有事实权限、失败路线能够通过 NoGain 暴露，后续 Closure 又不相信中间控制判断，那么局部错误 OneGap 应该可以被整个 research loop 吸收，而不需要重新引入 persistent Residual。**