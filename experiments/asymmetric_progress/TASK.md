你现在负责 Search-ESR 下一阶段核心实验：

# Asymmetric Research Progress:
# Single-Relation Blockers + Triggered Closure Audit

仓库：

`https://github.com/homulillew/Search-ESR`

当前研究基线分支：

`experiment/dynamic-progress-blockers`

开始前执行：

```bash
git fetch --all --prune
```

确认远程：

`origin/experiment/dynamic-progress-blockers`

最新 HEAD，并记录 exact SHA。

当前已知最新完成研究的 HEAD 应先核验，不得从本地旧状态假定。

创建新分支，例如：

`experiment/asymmetric-progress-closure-audit`

如已存在则添加明确 suffix。

继续使用当前：

`deepseek-flash`

当前 provider、JSON transport、retry=0、provider defaults 保持不变。

你作为 GPT-6 负责：

- 阅读前序实验；
- 做设计审计；
- 构建 fresh bank；
- 冻结请求；
- 实现；
- 真实模型调用；
- semantic review；
- 统计与成本分析；
- 完整性检查；
- commit / push；
- FINAL_CONCLUSION。

不要请求用户再次确认。

---

# 0. 开始前必须理解的当前结论

必须完整阅读最新：

```text
experiments/dynamic_progress/FINAL_CONCLUSION.md
experiments/dynamic_progress/p1_progress/RESULTS.md
experiments/dynamic_progress/decomposition_sensitivity/RESULTS.md
experiments/dynamic_progress/exploration/RESULTS.md
experiments/dynamic_progress/analysis/GATE.json
experiments/dynamic_progress/DESIGN_AUDIT.md
experiments/dynamic_progress/PROTOCOL.md
```

同时回看：

```text
experiments/frontier_generation/FINAL_CONCLUSION.md
experiments/deferred_recovery/FINAL_CONCLUSION.md
experiments/goal_residual_control_v3_1/FINAL_CONCLUSION.md
```

如果路径变化，先查仓库，不得跳过。

---

# 1. 当前已经得到的事实

最新 Dynamic Progress fresh primary：

```text
24 checkpoints
10 qids
48 B calls
```

Dynamic Blocker B：

```text
completion correct:
44/48

false closure:
4/42 = 9.5%

correct closure:
6/6

valid blocker presence:
36/42 = 85.7%

blocker precision:
76/103 = 73.8%
```

正式 P1 因：

```text
blocker precision < 90%
```

未通过。

P2/P3/P4 均未运行。

---

# 2. 当前不能简单解释成“Progress 失败”

详细错误显示：

Blocker precision 的主要损失来自：

```text
over-broad blocker
```

而不是大规模完全错误的 research gaps。

若仅做 post-hoc breadth sensitivity：

```text
96/103 = 93.2%
```

的 blocker units 没有其他内容错误。

这不是正式指标，不能覆盖 gate，但说明：

> gap granularity 是主要问题之一。

---

# 3. 单关系探索结果

唯一 bounded exploration 只增加：

> Each blocking gap must describe one missing or conflicting relation.

在12个 failure-enriched checkpoints：

```text
blocker precision:
61.1% → 88.0%

over-broad:
16/24 → 4/24

adequate output:
7/24 → 19/24

false closure:
0 → 0

unsupported premise:
0 → 0
```

但：

- 不是 fresh confirmation；
- precision 仍未达到原90%线；
- 没有包含主实验 false-closure P17/P19；
- 不能覆盖正式 gate。

因此本轮需要 fresh confirm：

> 单关系 blocker 是否能稳定改善 Progress 输出粒度。

---

# 4. 更重要的新问题：stable false closure

Fresh primary 的全部 false closure：

```text
4/42
```

全部来自 q580：

```text
P17 × 2
P19 × 2
```

而且两次 replicate 都稳定：

```text
resolved=true
```

这不是简单 sampling instability。

---

# 5. P17 的错误

当前 Claims 已有部分剧情证据，但没有建立：

```text
candidate series total number of seasons < 10
```

也没有完整建立：

```text
season-one date setup
+
season-three roommate sacrifice
```

是否属于同一候选 series。

模型两次仍：

```text
resolved=true
```

这是：

```text
strong candidate recognition
→ implicit completion
```

而不是证据闭合。

---

# 6. P19 的错误

Claims 支持：

```text
Edgar performed the sacrifice
```

以及相关季节/事件信息，

但没有直接建立：

```text
Edgar = male lead's roommate
```

模型仍两次：

```text
resolved=true
```

说明 Closure reasoning 中发生了：

```text
supported event
+
strong candidate context
→ unsupported role binding
```

这是隐式 stronger-relation join。

---

# 7. 当前最重要的理论结论

必须显式区分：

```text
Candidate confidence
```

和：

```text
Evidence closure
```

普通模型容易：

```text
candidate highly likely
→ answer probably right
→ stop
```

Research Agent 要求：

```text
material relations entailed by Verified Claims
→ justified closure
```

因此：

\[
\boxed{
high candidate confidence
\neq
research completion
}
\]

---

# 8. 更深层的非对称性

判断：

```text
研究还没有完成
```

只需要找到一个 material blocker：

\[
\exists g:\ g\text{ unresolved}
\]

即可。

但是判断：

```text
研究已经完成
```

实际上需要确信：

\[
\not\exists g:\ g\text{ material and unresolved}
\]

所以：

```text
find one blocker
```

与：

```text
prove no blocker remains
```

不是同难度问题。

当前 Light Progress 把两者放在同一个调用里。

本轮核心假设：

> Light Progress 适合发现 blocker，但不应该拥有未经二次认证的最终 STOP 权。

---

# 9. 本轮架构假设

Persistent semantic state 仍然只有：

```text
Original Question
Verified Claims
Working Hypothesis
```

Progress 仍然是：

```text
ephemeral derived state
```

不增加：

```text
Persistent Requirement Map
Persistent Goal Graph
Persistent Progress Table
Persistent Gap
Confidence
Priority
Plan Graph
```

---

# 10. Proposed Runtime Structure

定义：

\[
L_t = LightProgress(Q,C_t)
\]

如果：

```text
L_t.resolved = false
```

则正常输出：

```text
1–3 single-relation blockers
```

然后进入 Frontier Selection。

如果：

```text
L_t.resolved = true
```

Harness 不允许立即 STOP。

机械触发：

\[
A_t = ClosureAudit(Q,C_t)
\]

如果：

```text
A_t.confirmed = true
```

才允许最终 STOP。

如果：

```text
A_t.confirmed = false
```

则 Audit 返回一个 material blocker，

系统继续研究。

---

# 11. 重要：Closure Audit 不是新 Action

Runtime research actions 仍然只有：

```text
Search
Find
Open
```

不能增加：

```text
verify()
closure_check()
recover()
```

Closure Audit 是 Harness 调度的语义计算。

Actor 无权决定是否调用。

---

# 12. Harness 的职责

Harness 只能机械判断：

```text
Claims hash changed?
Light Progress cache stale?
Light Progress returned resolved=true?
Audit schema valid?
Claim index exists?
Budget exhausted?
```

Harness 不判断：

```text
某个 blocker 是否真的 material
某个 Claim 是否真的支持 closure
某个候选是否已经成立
```

---

# 13. Closure Audit 使用同一个模型

仍然：

`deepseek-flash`

不是：

- 新模型；
- Judge model；
- 第二个 autonomous Agent。

只是同一模型的一次独立调用：

\[
M_{audit}(Q,C)
\]

---

# 14. Closure Audit 不看 Light Progress 输出

虽然 Harness 因：

```text
Light Progress → resolved=true
```

触发 Audit，

但 Audit 请求本身只看：

```text
Original Question
Verified Claims
```

不要把：

```text
Light Progress said resolved=true
```

传给 Audit。

这样避免 confirmation anchoring。

---

# 15. Closure Audit 也不看

```text
Working Hypothesis
History
Workspace
Recent Attempts
Old Gap
Frontier
Light blocker list
```

Closure 必须只由：

```text
Q + Verified Claims
```

决定。

---

# 16. 为什么要增加 Same-Prompt Confirmation 对照

如果：

```text
Light → resolved
```

之后再调用一次模型，

即使使用完全相同的 prompt，

可能也会因为第二次采样而修复部分 false closure。

因此必须区分：

```text
second independent sample effect
```

和：

```text
specialized closure audit effect
```

---

# 17. 三种策略

本轮必须能离线构造三种 STOP policy。

## L — Light only

```text
stop iff LightProgress.resolved
```

---

## LL — Light + same-prompt confirmation

```text
stop iff:
Light1.resolved
AND
Light2.resolved
```

Light2：

- 同一个 Light Progress prompt；
- 同样 Q+Claims；
- 独立模型调用。

这测：

> 仅仅增加一个独立样本是否足够。

---

## LA — Light + Closure Audit

```text
stop iff:
Light1.resolved
AND
ClosureAudit.confirmed
```

这测：

> 专门的 closure semantics 是否有额外价值。

---

# 18. 为避免 output-driven sampling 偏差

Primary experiment 中：

对每个 checkpoint 预先运行：

```text
Light original × 2
Light single-relation × 2
Closure Audit × 2
```

即使 Light 没有提议 closure，也照样运行 Audit。

这样：

- Audit quality 可以在全部 frozen states 上评价；
- 不因 Light 输出决定是否产生研究数据；
- Conditional runtime cost 可在分析时按真实触发率模拟。

真实最终架构当然只在 proposed STOP 时触发 Audit。

---

# 19. Light 两个版本

## L0 — current frozen Dynamic Blocker

使用最新主实验 `prompts/blocker.md` 语义。

不修改。

---

## L1 — single-relation blocker

只增加已经探索过的一条约束：

> Each blocking gap must describe one missing or conflicting relation. Do not combine several independent conditions into one blocker.

其余：

- completion semantics；
- status；
- Claims input；
- schema；

全部保持一致。

这用于 fresh confirmation granularity effect。

---

# 20. Primary Bank

必须建立新的 fresh bank。

禁止直接把：

```text
P17/P19
```

放进 primary denominator。

它们作为 Challenge Stress Set。

---

# 21. Freshness

从已有真实 checkpoint inventory 中选择 exact：

```text
Q + Claim statements
```

key 从未进入：

- Frontier F1 primary；
- Dynamic Progress primary；
- Dynamic Progress semantic exploration。

同一个 qid 可以出现，

但 exact Q+Claims 不得复用。

如果无法满足规模：

不得制造 synthetic State。

直接降低样本并报告不足。

---

# 22. Primary target

目标：

```text
24 checkpoints
>=8 qids
max 4 checkpoints / qid
```

优先：

```text
18 unresolved
6 resolved
```

如果 held-out resolved 状态不足：

使用所有真实可用 resolved controls，并明确 small resolved stratum。

不要人工删除 Claim 来制造 near-closure。

---

# 23. Unresolved stratification

Fresh unresolved 应尽量覆盖：

```text
missing quantity
missing temporal scope
missing role binding
missing candidate→event binding
missing source/date attribution
candidate identity incomplete
material Claim conflict
near closure with one subtle missing relation
mid-research with multiple blockers
```

其中 near-closure unresolved 至少：

```text
10–12 cases
>=5 qids
```

如果真实数据不足，报告实际数量。

---

# 24. Resolved controls

优先覆盖：

```text
clear identity + final relation
quantity-bound closure
date/scope closure
role-binding closure
event-binding closure
```

不要只选一种 resolved pattern。

---

# 25. Challenge Stress Set

单独运行但不进入 fresh primary gate。

必须包括：

```text
P17
P19
```

以及前序研究中其他已知：

```text
strong-candidate false closure
role/date/quantity binding false closure
```

如有 provenance-complete exact state。

Challenge 只能用于机制验证。

不能代替 fresh confirmation。

---

# 26. Offline labels

每个 checkpoint 在任何新模型调用前冻结：

```text
gold_resolved: true / false
```

若 unresolved：

记录若干：

```text
acceptable_single_relation_blockers
```

不要求穷举。

并记录：

```text
known_invalid_joins
known_unsupported_assumptions
```

例如：

```text
episode plot ≠ total seasons
event actor ≠ roommate role
article date + count ≠ date-scoped attribution
scoring pattern ≠ 95-minute event
```

---

# 27. Resolved checkpoint labels

记录：

```text
minimal_closure_support_families
```

不是固定 runtime Requirement Map。

只是离线说明：

> 为什么这个状态确实可以结束。

例如：

```text
candidate identity binding
requested final relation
explicit quantity/date/scope relation if material
```

这些离线标签不能进入模型。

---

# 28. Light Progress L1 Prompt

基于当前 blocker prompt。

只允许一个新变化：

```text
Each blocking gap must describe exactly one material missing or conflicting relation.

Do not combine several independent conditions, clue families, or the whole identity problem into one blocker.

A blocker may include the minimal scope, date, role, quantity, or endpoint binding necessary to define that one relation.

You do not need to fill all blocker slots or cover every unresolved clue.
One valid material blocker is sufficient to establish that research is unresolved.
```

禁止其他 prompt tuning。

---

# 29. Closure Audit 的任务定义

Closure Audit 不是：

> 再问一次“你觉得做完了吗？”

它的任务是：

> **主动尝试推翻 closure。**

首先寻找：

> 是否仍有任意 material relation 未被 Verified Claims 建立。

如果找到一个：

```text
confirmed = false
```

并返回最强的一个 blocker。

只有在无法找到任何 material blocker，且 Claims 构成合理 closure support chain 时：

```text
confirmed = true
```

---

# 30. Closure Audit Prompt

建议冻结为：

```text
You are auditing whether the research is truly complete.

The Original Question is the authoritative goal.

Verified Claims are the only facts that may be treated as established.

Do not use outside knowledge.
Do not infer a missing relation merely because a candidate appears highly likely.
Do not treat a plausible identity, likely answer, or strong clue match as proof of closure.

Your first responsibility is to try to REFUTE closure.

Look for any material relation required for a justified answer that is still:
- unsupported,
- only partially bound,
- scoped to the wrong date/quantity/role/entity,
- contradicted by another Verified Claim,
- or implicitly assumed rather than established.

Pay particular attention to relation joins.

Examples:
- an episode event does not establish the character's required role;
- an appearance in season five does not establish the total number of seasons;
- an article date and a separate count do not establish that the article stated that count;
- a scoring pattern does not establish that the same fixture contains the required 95th-minute event;
- identifying a likely candidate does not establish every explicit quantity, date, role, or requested final relation.

Do NOT create a permanent checklist or plan.

If you can identify even one material blocker:
return confirmed=false and exactly one strongest blocker.

The blocker must describe one relation only.

If and only if you cannot identify any material blocker and the Verified Claims jointly establish:
1. the discriminative answer/candidate identity when identity is required,
2. the user's requested final relation,
3. any explicit quantity, date, role, scope, event, or relation whose failure could materially change the answer,
then return confirmed=true.

When confirming closure, provide a concise closure support certificate:
list only the main relations necessary to justify closure and the Claim indices supporting each.

Do not demand redundant corroboration or a separate Claim for every incidental wording detail.

Return only the required JSON object.
```

---

# 31. Closure Audit Schema

建议：

```json
{
  "confirmed": false,
  "blocking_gap": {
    "gap": "The candidate series' total number of seasons is not established.",
    "claim_refs": []
  },
  "closure_support": []
}
```

或：

```json
{
  "confirmed": true,
  "blocking_gap": null,
  "closure_support": [
    {
      "relation": "The candidate identity is established.",
      "claim_refs": [1, 3, 5]
    },
    {
      "relation": "The requested final relation is established.",
      "claim_refs": [7]
    }
  ]
}
```

不要：

```text
confidence
score
requirement_id
priority
next_action
query
source
```

---

# 32. Audit blocker 不需要 status

第一版 Closure Audit 的失败输出只需要：

```text
gap
claim_refs
```

不要再增加：

```text
missing / partial / conflict
```

理由：

当前 Dynamic Progress 已出现多次 status error。

Closure Audit 的核心任务只是：

> 能否找到一个真正阻止 closure 的 relation。

避免把 status fidelity 混入 closure safety。

---

# 33. Light Progress 仍保留原 status

因为本轮仍需要确认：

> L1 是否改善 blocker granularity。

不要同时修改 Light schema。

---

# 34. Calls

如果 primary=24：

每个 state：

```text
L0 × 2
L1 × 2
Audit × 2
```

共：

```text
24 × 6 = 144 calls
```

Challenge 单独计数。

全部：

- frozen before calls；
- both replicates retained；
- no retry；
- no best-of；
- no semantic repair。

---

# 35. Transport

必须在 freeze 前做一次纯机械 contract / serialization canary。

重点避免上一轮：

```text
JSON mode prompt missing literal JSON
```

错误。

Canary 只允许：

- schema；
- transport；
- response_format；

验证。

不得用研究 bank prompt/output做语义调试。

如果 transport canary失败：

先修 transport 再冻结正式 calls。

不要先跑正式批次。

---

# 36. Stage C1 — Fresh Single-Relation Confirmation

比较：

```text
L0 vs L1
```

主要指标：

```text
completion accuracy
false closure
correct closure
valid blocker presence
blocker precision
over-broad blocker
invented requirement
unsupported premise
status error
semantic ref error
reasoning proxy
```

---

# 37. L1 参考 Gate

建议：

```text
false closure <= 10%
valid blocker presence >= 90%
blocker precision >= 90%
correct closure >= 90%
```

并且不得出现：

```text
>=3 new critical semantic regressions across >=2 qids
```

相对 L0。

这部分回答：

> one-relation blocker exploration 是否能 fresh-confirm。

---

# 38. Stage C2 — Closure Audit Standalone Quality

Audit 在所有 primary checkpoint 上独立运行。

核心指标：

## Unresolved rejection rate

真实 unresolved：

```text
confirmed=false
```

比例。

对应 Audit false closure：

```text
confirmed=true
on unresolved
```

必须非常低。

---

## Correct closure

真实 resolved：

```text
confirmed=true
```

比例。

---

## Audit blocker precision

Audit 拒绝 closure 时：

返回 blocker 是否真实、material、single-relation。

---

## Closure support adequacy

Audit confirmed=true 时：

support certificate 是否足以支撑：

```text
identity
+
requested final relation
+
material explicit bindings
```

---

## Invented requirement / over-demand

Audit 是否因为过度保守而提出：

> 用户其实不需要的额外 requirement。

---

# 39. Audit Gate

因为 Audit 是停止安全层，门槛应比普通 Progress 更严格。

如果 primary unresolved slots ≥30，建议：

```text
false closure <= 1 slot
```

或近似：

```text
<=3%
```

取更适合冻结整数分母的规则。

Correct closure：

```text
>=90%
```

Closure support adequacy：

```text
>=90%
```

Audit blocker precision：

```text
>=90%
```

不能通过简单“永远说未完成”获得高分。

Resolved controls必须进入主 gate。

---

# 40. Stage C3 — Distinguish Re-Sampling from Audit Semantics

使用预先冻结的 replicate 配对构造：

## Policy L

```text
stop iff L1-primary.resolved
```

## Policy LL

```text
stop iff:
L1-primary.resolved
AND
L1-confirm.resolved
```

其中 confirm 是同 Prompt 的另一次独立调用。

## Policy LA

```text
stop iff:
L1-primary.resolved
AND
Audit-primary.confirmed
```

---

# 41. Primary/confirm replicate assignment

在模型调用前用 deterministic hash：

```text
hash(case_id)
```

决定：

- 哪个 L1 replicate 是 primary；
- 哪个 L1 replicate 是 confirmation；
- 哪个 Audit replicate 是 primary；
- 哪个是 stability replicate。

禁止看输出后配对。

---

# 42. Policy metrics

对 L / LL / LA 比较：

```text
False Stop
Correct Stop
Missed Stop
Overall completion decision accuracy
Conditional second-call rate
Expected model calls / decision
Input/output/reasoning-token cost
```

---

# 43. 最关键的因果解释

如果：

```text
LL ≈ LA
```

说明：

> 第二次独立判断本身可能已经足够，专门 Audit 语义未产生明显额外价值。

如果：

```text
LA >> LL
```

尤其 false closure 明显更低，

说明：

> 专门的“主动寻找 closure 反例”语义确实有效，而不仅是多采样一次。

这是本轮最重要的因果比较之一。

---

# 44. Challenge Stress Set

P17/P19 必须单独报告：

对于每个 prior stable false closure：

```text
L0
L1
Audit
LL
LA
```

结果。

特别看：

```text
P17:
missing total-season quantity

P19:
missing Edgar→roommate role binding
```

Audit 是否能稳定识别。

---

# 45. Challenge 参考机制目标

希望：

```text
Audit rejects P17 2/2
Audit rejects P19 2/2
```

但即使4/4成功：

也不能覆盖 fresh primary。

只是 mechanism confirmation。

---

# 46. FULL 不作为正式 Runtime Arm

上一轮 FULL 已经显示：

```text
higher local precision
but ~2.5x reasoning cost
and closure instability remains
```

所以本轮不要默认：

```text
FULL every turn
```

---

# 47. 允许的 FULL follow-up 条件

只有当：

```text
Audit false closure仍明显存在
```

且 failure audit 显示：

> Audit 主要因为没系统扫描问题条件而漏 blocker，

才允许一次 bounded exploration：

```text
temporary FULL-style audit at closure only
```

不是 full Progress every turn。

必须先：

```text
EXPLORATION_PLAN.md
```

commit/freeze。

---

# 48. 一次 bounded exploration 上限

最多：

```text
12 checkpoints
<=24 calls
```

只能选择一个 observed failure direction。

不能 prompt sweep。

Primary gate 不因 exploration 改写。

---

# 49. 如果 C1 + C2 + C3 通过

才恢复之前被阻塞的 Frontier P2。

不要直接跑 Search。

---

# 50. Stage F1 — Blocker → Need

使用 fresh unresolved states。

比较：

## D

当前 Direct：

```text
Q + Claims + Hypothesis
→ Need / Stop
```

## O

Oracle blocker：

```text
known-valid single-relation blocker
+ Claims
+ Hypothesis
+ Attempts
→ Need
```

不允许 STOP。

## G

实际 L1 Generated blocker：

```text
generated blocker
+ Claims
+ Hypothesis
+ Attempts
→ Need
```

不允许 STOP。

---

# 51. Frontier 主要问题

验证：

```text
Given a valid blocker,
can the model produce a bounded Need
without unsupported candidate assumptions?
```

核心指标：

```text
Valid Need
Need matches blocker
Unsupported premise
Over-broad Need
Goal drift
Stale Need
```

---

# 52. F1 最关键结果模式

如果：

```text
Oracle high
Generated high
Direct low
```

支持：

```text
Progress → Frontier
```

解耦。

如果：

```text
Oracle high
Generated low
```

Progress blocker 仍是瓶颈。

如果：

```text
Oracle low
```

Frontier Selector 有独立问题。

---

# 53. 本轮禁止跨 Gate

如果 closure 主实验不通过：

```text
不要运行Frontier
不要运行Search
不要运行Writer
不要运行P3/P4
```

先解决 closure。

---

# 54. Runtime 架构候选

只有实验支持后，才考虑正式：

```text
if claims_hash changed:
    invalidate LightProgress
    invalidate ClosureAudit

if LightProgress stale:
    LightProgress = evaluate(Q, Claims)

if LightProgress.resolved == false:
    Need = select_frontier(
        blockers,
        Claims,
        Hypothesis,
        RecentAttempts
    )

else:
    Audit = closure_audit(Q, Claims)

    if Audit.confirmed:
        STOP
    else:
        Need = select_frontier(
            [Audit.blocking_gap],
            Claims,
            Hypothesis,
            RecentAttempts
        )
```

---

# 55. Closure Audit cache

同一个：

```text
Hash(Q,Claims)
```

Audit 结果可以机械缓存。

如果 Claims 不变：

不得反复调用 Audit 直到出现想要答案。

禁止 best-of closure。

---

# 56. Claims mutation

一旦 Verified Claims 改变：

```text
LightProgress cache invalid
ClosureAudit cache invalid
```

Working Hypothesis 改变：

不 invalidate Progress/Audit。

Workspace / Attempts 改变：

不 invalidate Progress/Audit。

它们只影响 Frontier / Action。

---

# 57. 本轮仍然冻结

```text
Persistent semantic State:
Q + Claims + Hypothesis
```

不新增：

```text
persistent progress
persistent requirements
persistent blocker IDs
persistent closure certificate
```

Audit output 只对当前：

```text
Q + Claims hash
```

有效。

---

# 58. 最终必须回答的问题

最终报告至少明确回答：

1. Single-relation instruction 是否 fresh-confirm？
2. L1 blocker precision 是否达到可用于下游控制的水平？
3. Progress false closure 是否仍集中在 strong-candidate states？
4. Audit 的 false closure 是多少？
5. Audit 能否稳定发现 quantity / role / temporal / event-binding blocker？
6. Audit 是否比 Light Progress 更容易 over-demand？
7. Audit 正确 closure rate 是多少？
8. Audit closure certificate 是否真的充分？
9. `Light + same prompt confirmation` 能修复多少 false closure？
10. `Light + Audit` 能修复多少？
11. Audit 的收益是否超出单纯第二次采样？
12. P17/P19 是否被稳定修复？
13. Audit blocker 是否能直接作为后续 Frontier 输入？
14. FULL 是否仍然只适合 closure 边界，而不适合每轮？
15. 额外 Audit 的平均调用率和 token 成本是多少？
16. 当前最合理的 STOP policy 是：
    - Light only
    - double Light
    - Light + Audit
    - none yet
17. 是否已有资格进入 Blocker→Need 实验？
18. 是否仍有证据要求扩大 Persistent Research State？
19. 是否需要不同模型做 Audit？
20. 当前 Research Loop 的 dominant bottleneck 是否已经从：
    - Progress
    转移到：
    - Frontier
    或仍然是 closure？

---

# 59. 最重要的理论判断

本轮不应试图证明：

> “模型能不能猜出答案。”

真正测试：

\[
\boxed{
Research Agent能否区分
“答案已经很可能是X”
和
“Claims已经足以证明X并支持用户要求的最终关系”
}
\]

---

# 60. 最终可能的架构结论

只有当数据支持时，才允许写：

\[
\boxed{
Persistent\ Belief
\rightarrow
Light\ Progress
\rightarrow
Frontier
}
\]

并在 STOP 边界：

\[
\boxed{
Proposed\ Closure
\rightarrow
Triggered\ Closure\ Audit
}
\]

即：

```text
日常进度判断：
寻找至少一个 blocker。

最终停止：
需要独立 closure certificate。
```

---

# 61. 最核心原则

不要把：

```text
absence of a detected blocker
```

直接当成：

```text
proof that no blocker exists
```

不要因为候选很强就停止。

不要为了安全又把完整 Requirement Table 持久化。

不要让 Harness 理解语义。

不要让 Actor 自己选择是否接受 closure audit。

让 Harness 只根据：

```text
proposed resolved=true
```

机械触发 Audit。

让实验回答：

\[
\boxed{
“轻量发现缺口 + 停止时严格审计”
是否能成为长程 Research Agent
可靠的收敛机制。
}
\]