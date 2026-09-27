# Search-ESR：Recoverable Control Equivalence / Active Requirement Selection

## 0. 本轮研究目标

本轮不要继续追求每个 Task Requirement 的三分类状态都绝对正确。

上一实验已经观察到：

```text
unsupported ↔ partially_supported
```

是大量 Alignment 错误的来源，但这两种状态在控制意义上都应当保持：

```text
OPEN
```

因此本实验重新提出一个更贴近 Research Agent 最终闭环的研究问题：

> **即使中间的细粒度语义状态并不完美，只要真正未完成的 Requirement 仍然保持可见，错误不会形成不可逆闭合，并且后续 Agent 仍有继续研究和纠正它的机会，那么当前 Alignment 是否已经足以承担控制功能？**

核心原则：

\[
\boxed{
\textbf{Prefer recoverable imperfect control over brittle exact-looking state.}
}
\]

本轮严格区分：

```text
semantic exactness
```

和：

```text
control-equivalent correctness
```

---

# 1. 当前远程基线

开始前必须重新：

```bash
git fetch origin --prune
git status
git branch --show-current
git rev-parse origin/experiment/skeleton-state-alignment

git log --oneline --decorate -20 \
  origin/experiment/skeleton-state-alignment
```

任务编写时最新：

```text
experiment/skeleton-state-alignment
dd442dd62082e5923c98bd553b38fc4de3ad309d
```

latest commit：

```text
Report alignment reliability gap and stop conditional selection at frozen gate
```

若远程已前移：

1. 读取全部新增 commit；
2. 确认是否已经存在同类 recoverability / selection 实验；
3. 记录在 `PRE_EXECUTION_AUDIT.md`；
4. 不静默使用旧 SHA。

---

# 2. 上一实验结论必须原样保留

上一实验正式结果：

```text
E1:
A0 Oracle Skeleton = FAIL
A1 Runtime D2 = PASS
Joint Gate = FAIL

E2 Active Requirement Selection = NOT RUN
```

禁止把本实验的新评价目标反向用于：

```text
把旧 E1 改写为 PASS
修改旧 threshold
重新解释旧 preregistered gate
删除旧 Exact Mask failure
```

本实验是一个新的问题：

> **Control-equivalent Mask 是否已经足够可靠？**

不是旧实验的补考或事后修门槛。

---

# 3. 当前已有事实

上一实验主要结果：

```text
A0 Oracle
Node Status Accuracy       92.55%
Residual Recall            97.48%
Residual Precision         100%
Support Precision          86.58%
Full Support Sufficiency   86.27%
Exact 3-way Mask           70.37%

A1 Runtime D2
Node Status Accuracy       93.94%
Residual Recall            98.68%
Residual Precision         100%
Support Precision          87.59%
Full Support Sufficiency   92.31%
Exact 3-way Mask           77.78%
```

主要 status errors：

```text
unsupported -> partial
partial -> full
partial -> unsupported
```

其中最多的是：

```text
unsupported -> partial
```

这一类错误在控制意义上可能没有直接代价，因为两者都属于 OPEN。

---

# 4. 本轮核心假设

定义：

\[
ControlStatus(R_i)=
\begin{cases}
CLOSED,& status=fully\_supported\\
OPEN,& status=partial\ or\ unsupported
\end{cases}
\]

因此：

\[
\boxed{
P\leftrightarrow U
}
\]

不是 primary control error。

真正危险的是：

\[
\boxed{
Gold=OPEN,\ Predicted=CLOSED
}
\]

即：

```text
False Close
```

因为它可能导致：

```text
Requirement 从 frontier 消失
→ 不再被选择
→ 不再获取针对它的新证据
→ 提前 STOP
```

---

# 5. 本轮真正需要保护的 invariant

不是：

```text
every semantic status must be exactly right
```

而是：

\[
\boxed{
\textbf{Every materially unresolved requirement should retain a viable
future path back into active research.}
}
\]

换言之：

> 中间错误允许存在，但错误不能轻易变成不可恢复的控制承诺。

---

# 6. 推荐新分支

```bash
git switch -c experiment/recoverable-control-equivalence \
  origin/experiment/skeleton-state-alignment
```

目录：

```text
experiments/recoverable_control_equivalence/
```

历史实验目录保持完全只读。

---

# 7. 本轮阶段

本实验分两个阶段。

## E0 — Control-Equivalent Reanalysis + Recoverability Audit

**零新模型调用。**

只重新分析上一实验已经存在的：

```text
108 E1 Alignment outputs
27 natural states
10 qids
A0 / A1
2 replicates
Gold Masks
chronological state structure
frozen selection references
```

回答：

> 三分类 Mask 虽然不完美，但 OPEN/CLOSED 控制状态到底有多可靠？

以及：

> 已经出现的 false close 是否会在后续自然状态中恢复，还是成为 sticky / absorbing error？

---

## E1 — Active Requirement ID Selection

只有 E0 的 Runtime A1 control-equivalent gate 通过后才运行。

测试：

\[
OpenSet\rightarrow ActiveRequirementID
\]

不生成自然语言 Obligation。

不执行 Gap。

不执行 Search/Find/Open。

不执行 Writer。

不执行完整 rollout。

---

# 8. 为什么先做 E0，而不是重新调用 Alignment

已有 Alignment 输出已经足够回答一个新的、此前没有统计的问题：

> 很多三分类错误是否其实属于 control-equivalent error？

因此不得为了得到更好结果重新跑 Alignment。

首先最大化已有证据的信息价值。

---

# 9. E0：Binary Control Projection

对上一实验所有有效 Mask：

```text
fully_supported      -> CLOSED
partially_supported  -> OPEN
unsupported          -> OPEN
```

Gold Mask 同样投影。

生成：

```text
CONTROL_EQUIVALENT_MASKS.json
```

原始三分类永远保留。

不得覆盖旧数据。

---

# 10. E0 Primary Metrics

## 10.1 Binary Node Accuracy

每个 Requirement：

```text
Gold OPEN/CLOSED
vs
Predicted OPEN/CLOSED
```

---

## 10.2 Open Requirement Recall

\[
\frac{
Gold\ OPEN\ 且\ Predicted\ OPEN
}{
Gold\ OPEN
}
\]

这是 primary safety metric。

---

## 10.3 Open Requirement Precision

\[
\frac{
Gold\ OPEN\ 且\ Predicted\ OPEN
}{
Predicted\ OPEN
}
\]

---

## 10.4 Closure Precision

所有模型判：

```text
CLOSED
```

的节点中，

真正 Gold CLOSED 的比例。

注意：

这比上一实验：

```text
false_supported_rate / all Gold P/U
```

更接近 runtime risk。

---

## 10.5 False Close Rate

\[
\frac{
Gold\ OPEN,\ Predicted\ CLOSED
}{
Gold\ OPEN
}
\]

---

## 10.6 Exact Binary Mask

一个 response 中所有 Requirement 的：

```text
OPEN/CLOSED
```

全部正确才算 exact。

这个指标与上一实验的：

```text
Exact 3-way Mask
```

必须并列报告。

不得替换旧指标。

---

# 11. 计算 Control-Equivalent Gain

定义：

\[
ControlEquivalentGain
=
ExactBinaryMask-Exact3WayMask
\]

目的不是证明旧评价错误，

而是回答：

> 多少原先的 semantic Mask error 对控制状态其实没有影响？

同时报告：

```text
3-way status errors
binary control errors
U<->P errors collapsed
remaining false-close errors
remaining false-open errors
```

---

# 12. Absorbing Error Audit

这是 E0 最重要的新分析。

对于每个 predicted Mask：

机械产生：

\[
OpenSet=\{R_i\mid status_i=OPEN\}
\]

然后判断：

### false_empty_open_set

Gold 仍存在 OPEN Requirement，

但模型：

```text
OpenSet = empty
```

这相当于潜在 premature STOP。

---

### lost_all_acceptable_frontier

利用上一实验已经冻结的：

```text
SELECTION_REFERENCE
```

判断：

> Gold 存在至少一个 acceptable active requirement，
> 但 predicted OpenSet 中一个 acceptable ID 都没有。

这是比单节点 false close 更危险的错误。

---

### still_has_recovery_frontier

即使有一个 Requirement 被误关，

Predicted OpenSet 中仍然存在至少一个：

```text
acceptable_active_id
```

那么系统至少仍有：

> 继续研究 → 获得新 Claims → 下轮重算

的机会。

---

# 13. 不允许把 D2 无法表达的状态算成 Alignment 错误

上一实验已经冻结：

```text
G04
G05
```

在严格 D2 locality interpretation 下：

```text
没有合法单一 active ID
```

这种 failure 必须分别标：

```text
representation_addressability_limit
```

不能混进：

```text
false_close
```

也不能因为没有 ID 就允许 STOP。

---

# 14. Temporal Recoverability Audit

使用上一实验预先认定的 natural Claims-addition trajectories。

之前已经排除：

```text
G05 -> G06
G17 -> G18
```

这两个 candidate/refinement pair。

保留原来 eligible 的 literal Claims-addition transitions。

对于：

```text
qid
requirement_id
replicate
```

如果在状态 \(t\)：

```text
Gold = OPEN
Predicted = CLOSED
```

则检查下一个 eligible state。

分成：

### recovered_open

下一个 state：

```text
Gold = OPEN
Predicted = OPEN
```

说明之前的 false close 没有持续。

---

### became_justified

下一个 state：

```text
Gold = CLOSED
Predicted = CLOSED
```

说明后续 evidence 已经真正补足 Requirement。

这不是“模型纠错”，但之前的控制风险已自然消失。

---

### persistent_false_close

下一个 state：

```text
Gold = OPEN
Predicted = CLOSED
```

这是最危险的。

---

### reopened_incorrectly

若：

```text
Gold = CLOSED
Predicted = OPEN
```

单独报告。

---

# 15. Safe Resolution Rate

对于能够继续观察的 prior false-close：

\[
SafeResolutionRate=
\frac{
recovered\_open+became\_justified
}{
evaluable\ prior\ false\ closes
}
\]

另外报告：

```text
persistent false-close count
maximum consecutive false-close length
median recovery steps
```

如果 natural false-close denominator：

```text
< 4
```

则该指标只作：

```text
DESCRIPTIVE / UNDERPOWERED
```

不得因为 denominator 太小自动判 100% recoverable。

不得人为制造更多“自然病例”补分母。

---

# 16. False Close 是否真的阻断研究？

对每个 false-close state 再判断：

```text
A. 仍有其它 acceptable OPEN requirement
B. 只有 downstream / blocked OPEN requirement
C. 已无任何 acceptable frontier
D. OpenSet 完全为空
```

这一步非常重要。

因为：

\[
FalseClose\neq AutomaticallyFatal
\]

真正危险的是：

\[
\boxed{
FalseClose
+
NoAlternativeFrontier
}
\]

---

# 17. E0 Primary Runtime Arm

Primary：

```text
A1 Runtime D2
```

因为这是上一实验实际候选 runtime representation。

A0 Oracle：

```text
diagnostic only
```

A0 不再作为 E1 Selection 的自动双门槛。

这是一个**新实验目标**。

必须明确：

> 这不改变旧实验 A0 FAIL / Joint FAIL。

---

# 18. E0 Gate

Runtime A1 必须满足全部：

```text
Binary Node Accuracy >= 95%

Open Requirement Recall >= 97%

Closure Precision >= 90%

Exact Binary Mask >= 85%

False Empty OpenSet = 0

False STOP Hazard = 0

Schema-valid source masks = 100%
```

另外：

```text
Lost-All-Acceptable-Frontier Rate <= 10%
```

---

# 19. Recoverability 不作为硬 Gate 的条件

如果 natural false-close transition denominator：

```text
>= 4
```

则额外要求：

```text
Safe Resolution Rate >= 75%
```

如果：

```text
< 4
```

则：

```text
Recoverability = INSUFFICIENT_NATURAL_DENOMINATOR
```

不允许凭此宣布“已证明 recoverable”。

但也不自动阻止 E1 Selection。

原因：

> E1 测试的是当前 OpenSet 是否足以支持 selection；
> 真正 longitudinal recoverability 将留到后续 closed-loop rollout。

必须在最终报告中明确保留这个 uncertainty。

---

# 20. 如果 E0 FAIL

立即停止。

不得运行新模型 Selection calls。

结论必须定位：

### 如果 Open Recall 失败

```text
Alignment 仍会丢失未完成 Requirement。
```

### 如果 Closure Precision 失败

```text
错误 CLOSED 仍过多。
```

### 如果 false-empty / no-frontier 出现

```text
错误已经具有 absorbing-control risk。
```

这时才有经验依据研究：

```text
Closure Verification
Periodic Reaudit
Lazy Reopen
```

但本轮不实施。

---

# 21. 如果 E0 PASS

说明：

> 虽然三分类语义状态不完美，但在 OPEN/CLOSED 控制抽象下，现有 Alignment 已达到预注册的最低可用性门槛。

注意：

不得写：

> Alignment problem solved.

只能写：

> Control-equivalent projection qualified for Active-ID Selection on this exposed development bank.

---

# 22. E1 — Active Requirement Selection

只有 E0 PASS 才运行新模型调用。

目标：

\[
\boxed{
OpenSet\rightarrow ActiveRequirementID
}
\]

---

# 23. E1 的两个 Arms

## S0 — Gold Control Mask

输入：

```text
Original Q
Runtime D2 Skeleton
Gold OPEN/CLOSED Mask
```

目的：

> 隔离 Selection 本身。

---

## S1 — Model Control Mask

固定使用上一实验：

```text
A1 replicate 1
```

然后投影：

```text
F -> CLOSED
P/U -> OPEN
```

绝不：

```text
best-of two replicates
人工修复
挑 better mask
fallback to Gold
```

目的：

> 测真实 Alignment error 传到 Selection 后损失多少。

---

# 24. 为什么继续用 D2

不是因为 D2 已证明是最佳控制表示。

而是为了：

1. 保持与上一实验 runtime candidate 一致；
2. 不同时更改 Representation + Alignment + Selector；
3. 保留 E0 已观察到的 addressability warning。

最终报告必须继续明确：

```text
D2 direct + coherent addressability = 59.26%
D2 subnode-only = 40.74%
```

如果 Selection 失败明显集中在 coarse-node case，

下一实验才研究：

```text
D1-like control node
+
D2 source-span authority
```

本轮不偷偷切换。

---

# 25. E1 Selection Reference

继承上一实验已经冻结的：

```text
acceptable_active_ids
invalid_supported_ids
blocked_or_downstream_ids
stop_allowed
```

不得因为本轮输出修改 reference。

G04/G05：

```text
没有合法单 D2 ID
```

继续保留在 denominator。

它们构成 representation ceiling。

---

# 26. E1 Input

只允许：

```text
Original Question
Task Skeleton
Control Mask
```

Control Mask 格式：

```json
{
  "R1": "CLOSED",
  "R2": "OPEN",
  "R3": "OPEN"
}
```

不输入：

```text
Claims
H
Recent Delta
Path
Workspace
GoldO
Gap
provider reasoning
historical next action
```

原因：

> 本轮只测试知道 OpenSet 后能否选择一个合法 frontier。

---

# 27. E1 Selection Prompt

统一使用以下 system prompt：

```text
You select one current research requirement from a fixed Task Skeleton.

You receive:

1. the Original Question;
2. a fixed Task Skeleton;
3. the current control status of every Task Requirement.

Each Task Requirement has exactly one control status:

- OPEN
- CLOSED

OPEN means that this requirement is not yet sufficiently established and may
still require research.

CLOSED means that the current evidence state is considered sufficient for this
requirement at this control step.

The Task Skeleton defines the task semantics.
Do not rewrite, merge, split, add, delete, or reinterpret requirements.

Choose exactly ONE OPEN requirement_id that is appropriate to work on next.

A valid active requirement should:

1. be OPEN;

2. materially advance answering the Original Question;

3. be sufficiently local to serve as one current research objective;

4. not skip an unresolved prerequisite merely to request a downstream
   property;

5. be allowed to identify or establish an entity, event, relation, document,
   source, or attribute that is itself still unknown;

6. not be rejected merely because its answer is not yet known;

7. preserve the original participant roles, relation arguments, object scope,
   ownership, and temporal attachment encoded by the fixed Task Skeleton.

If multiple OPEN requirements are equally legitimate current objectives,
choose any one.

Do not globally re-plan the whole problem.
Finding one useful current requirement is sufficient.

Return STOP only if every material Task Requirement is CLOSED.

Do not output:
- a rewritten obligation;
- a search query;
- an explanation;
- a source preference;
- a hypothesis;
- a confidence score;
- an evidence gap;
- a plan.

Return JSON only:

{
  "selection": "R3"
}

or:

{
  "selection": "STOP"
}
```

---

# 28. 为什么不再生成自然语言 O

Task Skeleton 已经承担稳定 task semantics。

所以：

\[
\boxed{
ActiveO=RequirementID
}
\]

避免：

```text
R3
→ natural-language paraphrase
→ relation/date/role corruption
```

本轮只测 ID selection。

---

# 29. E1 调用规模

```text
27 states
× 2 arms
× 2 replicates
= 108 calls
```

模型配置保持历史一致：

```text
DeepSeek deepseek-flash
temperature = 0
JSON mode
omit max_tokens
max_retries = 0
concurrency <= 8
```

不得重试、repair、replacement。

---

# 30. E1 Metrics

## Valid Selection

输出属于：

```text
acceptable_active_ids
```

---

## Selected Closed

选择 Gold CLOSED requirement。

---

## Selected Input-Closed

选择输入 Mask 中标 CLOSED 的 requirement。

这两个必须分开。

因为 S1 Mask 本身可能错误。

---

## Downstream Selection

选择：

```text
blocked_or_downstream_ids
```

---

## False STOP

Gold 仍有可研究 material requirement，

却输出：

```text
STOP
```

---

## Input-Mask False STOP

输入 Mask 中仍有 OPEN，

模型却 STOP。

---

## Selection Stability

两 replicate：

```text
same valid ID
different but both valid
one valid one invalid
both invalid
```

不同但都 valid 不算失败。

---

# 31. S0 Gate

Gold Control Mask：

```text
Valid Selection >= 85%

Selected Closed <= 5%

Downstream Selection <= 10%

False STOP <= 5%

Schema >= 95%
```

若 S0 FAIL：

停止。

结论：

> 即使 OpenSet 正确，Current Frontier Selection 仍是独立瓶颈。

---

# 32. S1 Gate

Model Control Mask：

```text
Valid Selection >= 80%

Selected Closed <= 7.5%

Downstream <= 10%

False STOP <= 7.5%

Schema >= 95%
```

并定义：

\[
SelectionLoss
=
S0Valid-S1Valid
\]

要求：

```text
SelectionLoss <= 10 percentage points
```

---

# 33. 如果 E1 PASS

立即停止本实验。

不要继续调用：

```text
Gap
Search
Find
Open
Writer
full rollout
```

结论只能写：

> Control-equivalent Alignment plus ID-only frontier selection is sufficiently promising on the exposed historical bank to justify a separately preregistered short closed-loop rollout.

---

# 34. 下一独立实验

只有 E0 + E1 PASS 后，

建议创建：

```text
experiment/recoverable-skeleton-loop
```

第一次真正运行：

```text
Skeleton
→ recompute OPEN/CLOSED
→ ActiveRequirementID
→ Local Gap
→ Search/Find/Open
→ Writer
→ Claims update
→ recompute OPEN/CLOSED
```

每题限制：

```text
4–8 control decisions
```

---

# 35. 下一 closed-loop experiment 的 primary 指标

未来不要只看 final answer。

必须重点记录：

### transient_false_close

某轮错误 CLOSED。

---

### persistent_false_close

同一 Requirement 在后续证据更新后仍错误 CLOSED。

---

### reopened_requirement

之前 CLOSED，后来重新变 OPEN。

注意：

这在新架构中必须允许。

---

### recovery_after_new_evidence

错误状态是否被新 Claims 修正。

---

### false_stop

是否在 Gold residual 存在时结束。

---

### recovery_frontier_available

即使某 Requirement 被误关，

是否仍有其它有效 Active Requirement 让 Agent 继续运行。

---

# 36. 不允许实现不可逆 CLOSED

未来 runtime 中：

```text
CLOSED
```

只是：

> 当前 control cycle 的判断。

不得永久写进 persistent task semantics。

禁止：

```text
R3.closed = true forever
```

正确形式：

\[
Mask_t=Align(R,C_t)
\]

下一轮：

\[
Mask_{t+1}=Align(R,C_{t+1})
\]

重新计算。

---

# 37. Persistent Boundary

继续保持：

## Episode-stable

```text
Original Q
Task Skeleton
```

## Persistent epistemic

```text
Verified Claims
Hypothesis
```

## Mechanical

```text
Workspace
Trace
D#
W#
```

## Ephemeral / recomputed

```text
Control Mask
OpenSet
ActiveRequirementID
Gap
```

---

# 38. 不新增 Closure Verifier

本实验明确禁止增加：

```text
second LLM verifier
majority vote
closure checker
persistent progress table
dependency DAG
Binding IR
confidence threshold
```

原因：

> 当前还没有证明现有 false-close 会在动态控制中形成不可恢复错误。

只有 E0 或后续真实 rollout 观察到：

```text
persistent false close
false empty OpenSet
premature STOP
no remaining recovery frontier
```

才有经验依据增加 Closure Verification。

---

# 39. 不新增 Lazy Expansion

D2 coarse-node warning 已经真实存在，

但本轮先通过 Selection error distribution 判断它是否真的阻塞控制。

如果 Selection failure 显著集中于：

```text
subnode_only
```

下一实验才研究：

```text
D1-like finer control nodes
+
D2 source anchors
```

不得现在直接增加 hierarchy。

---

# 40. E0 必须输出的关键表

至少包含：

```text
3-way exact mask
binary exact mask
control-equivalent gain

open recall
open precision
closure precision
false close rate

false empty OpenSet
lost all acceptable frontier
still has valid recovery frontier

natural false-close count
recovered open
became justified
persistent false close
safe resolution rate
```

分别报告：

```text
A0
A1
non-empty Claims only
qid strata
replicate strata
```

---

# 41. 特别分析上一轮 known bad cases

必须逐一追踪：

### q922 letter / memorandum date

看错误 CLOSED 是否：

```text
持续
恢复
被其它 open frontier 绕过
```

---

### q637 four-year course

看：

```text
duration
```

被增强成：

```text
four-years-later onset
```

是否形成 absorbing false close。

---

### q843 Georgetown / American university

看 parametric/geographic completion 是否导致节点过早 CLOSED。

---

### q169 charity relation

这是主要 U→P case。

由于：

```text
U/P 都是 OPEN
```

检查它是否在 binary control 中完全无影响。

---

### q1259 teammate same-country

检查已知 teammate identity：

```text
→ partial
```

的错误是否影响 OpenSet。

---

# 42. 研究问题必须最终回答

1. 三分类错误中有多少在 OPEN/CLOSED 投影后消失？
2. Binary Node Accuracy 多高？
3. Exact Binary Mask 是否显著高于 Exact 3-way Mask？
4. Open Requirement Recall 是否仍约98%？
5. Closure Precision 到底多高？
6. false close 是否产生 false empty OpenSet？
7. false close 是否会让所有 acceptable frontier 消失？
8. 多数 false close 是否仍有其它 research frontier？
9. natural trajectory 中 false close 能否恢复？
10. 是否观察到 persistent false close？
11. U→P 是否基本属于 control-neutral error？
12. 哪些 semantic error 真正变成 control error？
13. D2 coarse node 是否遮蔽内部错误？
14. D2 coarse node 是否实际阻塞 Active-ID Selection？
15. Gold OpenSet 下 selector 能否选择 valid ID？
16. Model OpenSet 相对 Gold OpenSet 损失多大？
17. downstream jump 是否仍存在？
18. ID-only output 是否避免重新引入 relation rewriting？
19. 是否出现 false STOP？
20. 是否已经有资格进入4–8步真实 closed-loop rollout？

---

# 43. 结果解释矩阵

## Case A

E0 FAIL。

结论：

```text
当前 Alignment 错误已经具有控制层危险，
不能仅靠后续自纠错假设进入 Selection。
```

下一步才考虑 Closure / Reaudit。

---

## Case B

E0 PASS，S0 FAIL。

结论：

```text
Alignment 在控制等价层面足够，
但 Frontier Selection 是当前瓶颈。
```

---

## Case C

E0 PASS，S0 PASS，S1 FAIL。

结论：

```text
Selection 本身可行，
但 Model Mask error 传播后仍损害控制。
```

---

## Case D

E0 + S0 + S1 全 PASS。

结论：

```text
Plan–Monitor–Select bridge 已获得开发阶段正向证据。
下一步应进入短 closed-loop rollout。
```

---

# 44. Review Discipline

E0 是纯离线分析。

不得修改旧 Gold。

不得读取 final answer 来重写状态。

E1 first-pass review 隐藏：

```text
arm
replicate
Gold acceptable IDs
historical GoldO
aggregate metrics
provider reasoning
```

Reviewer 只看：

```text
Q
Skeleton
visible OPEN/CLOSED Mask
selection
```

先提交 judgment，

再揭盲汇总。

---

# 45. E1 结果不能因为 coarse ceiling 做事后删除

G04/G05 等无单 ID 状态：

继续保留。

如果因此 S0 最大只能达到：

```text
25/27 = 92.59%
```

这是表示真实约束。

不能删掉这两个状态再提高准确率。

---

# 46. 调用授权

E0：

```text
0 paid calls
```

可以直接执行。

如果 E0 PASS 后需要 E1 的108次 paid calls：

只有当前上下文存在对本新实验明确适用的授权时才能执行。

否则：

1. 完成全部 E0；
2. 冻结 E1 prompt/schema/reference/schedule；
3. 完成 preflight；
4. 输出 call/token estimate；
5. 停在：

```text
PREPARED_FOR_E1_EXECUTION
```

不得把旧实验授权自动延伸到本轮。

---

# 47. 建议目录

```text
experiments/recoverable_control_equivalence/
├── README.md
├── TASK.md
├── HYPOTHESES.md
├── PROTOCOL.md
├── CONFIG.json
├── GATES.json
├── FREEZE.json
├── PRE_EXECUTION_AUDIT.md
│
├── e0_control_equivalence/
│   ├── SOURCE_MANIFEST.json
│   ├── CONTROL_EQUIVALENT_MASKS.json
│   ├── METRICS.json
│   ├── RECOVERABILITY.json
│   ├── ABSORBING_ERROR_AUDIT.json
│   └── REPORT.md
│
├── e1_selection/
│   ├── STATUS.json
│   ├── SELECTION_REFERENCE.json
│   ├── SCHEDULE.json
│   ├── calls/
│   ├── review/
│   ├── METRICS.json
│   └── REPORT.md
│
└── analysis/
    ├── ERROR_LEDGER.json
    ├── SENSITIVITY.json
    ├── EXECUTION_ACCOUNTING.json
    ├── INTEGRITY.json
    └── FINAL_CONCLUSION.md
```

---

# 48. 最终研究哲学

本轮最重要的不是把：

```text
93% node status accuracy
```

提高成：

```text
97%
```

而是回答：

\[
\boxed{
\textbf{
Do imperfect intermediate judgments actually destroy future research
opportunities, or can the agent remain recoverable?
}
}
\]

如果：

```text
OPEN requirements remain visible
false close rarely eliminates the entire frontier
Mask is recomputed rather than persisted
STOP remains conservative
```

那么系统可能并不需要每个 intermediate semantic label 都完美。

---

# 49. 最终停止纪律

不要因为我们“感觉闭环已经很近”而直接运行 full loop。

本轮顺序必须是：

```text
existing Alignment outputs
↓
Control-equivalent offline audit
↓
E0 gate
↓
Active-ID Selection
↓
E1 gate
↓
STOP
```

只有下一独立实验才允许：

```text
Selection
→ Gap
→ Action
→ Evidence
→ Claims
→ Recompute
```

---

# 50. 本轮一句话目标

\[
\boxed{
\textbf{
不是证明 Agent 每一步都判断正确，
而是证明它即使偶尔判断错误，也不会轻易失去继续纠错的机会。
}
}
\]