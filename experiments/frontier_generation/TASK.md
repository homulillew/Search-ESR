你现在负责 Search-ESR 下一阶段的核心实验：

# Explicit Research State → Research Frontier Generation

仓库：

https://github.com/homulillew/Search-ESR

当前最新研究基线分支：

`experiment/deferred-recovery-global-vs-local`

运行模型继续使用：

`deepseek-flash`

你作为 GPT-6 负责：

- 阅读历史研究；
- 设计与冻结实验；
- 实现；
- 真实模型调用；
- 语义审核；
- 统计分析；
- 完整性检查；
- commit / push；
- 最终研究结论。

本轮不是重新研究 Search / Find / Claim Admission。

本轮核心问题是：

> 当 Persistent Research State 已经被压缩为 Original Question + Verified Claims + Working Hypothesis 后，模型能否仅依赖这个显式状态，稳定生成合理的下一研究前沿（Current Need），而不必每轮从完整 Research History 中重新重建“目前知道什么、还缺什么”？

---

# 0. 当前研究结论

开始前必须完整理解以下已经得到的结果。

## A. Claim 膨胀

v3.1 证明：

旧 State Updater 会大量保存 source-supported 但对研究没有持续决策价值的事实。

Uc → U1：

```text id="r09oip"
Incidental Claims:
44 → 2

Decision-relevant precision:
38.03% → 90%

State mutations:
37/55 → 15/55

New semantic chars:
6461 → 1823
```

因此：

```text id="gzhnjc"
source-supported
!=
state-worthy
```

已经有很强证据。

Persistent State 不应该试图保存所有已经观察的信息。

---

## B. Immediate Claim Recall 不等于最终系统 Recall

Selective Admission 会漏掉一部分当前不重要、未来可能需要的信息。

Deferred Recovery 实验表明：

当一个过去观察过但没有进入 Claim 的 requirement 后来真正成为 Current Need 时：

```text id="ai98ae"
Need
→ Global Search
→ Evidence
→ U1 Writer
→ Claim
```

这条链在现有 D3/D4 诊断案例中能够跑通。

Global Search 的小样本机制结果为：

```text id="fhk9ms"
5/5 evidence recovery
5/5 strict Claim recovery
```

但真正 fresh case 只有 1 个，因此不能把 5/5 当总体成功率。

目前只能认为：

```text id="eztw0b"
Deferred Recovery mechanism is plausible and operational.
```

不能认为已经完成泛化确认。

---

## C. Recovery 不需要成为新的 Tool

Runtime 仍然只有：

```text id="yuc1nb"
Search
Find
Open
```

Recovery 只是离线分析意义上的：

```text id="gq8jfr"
过去看过但没有持久化的信息，
未来重新因为 Need 被取得。
```

禁止本轮新增：

```text id="6vhsbv"
recover()
memory_search()
workspace_recall()
```

---

## D. Search / Find 当前定义

当前更合理的理解是：

```text id="a2v8sq"
Search = 全局范围的 Evidence Retrieval
Find   = 指定已知 Document 范围的 Evidence Retrieval
Open   = 已知 Window 的邻接扩展
```

而不是：

```text id="44iq79"
Search = 新文档发现
Find   = 旧文档恢复
```

v3a Search 在已经见过的 Document 再次被 Global Search 命中时，仍会按当前 query 重新生成 query-localized window。

本轮不得改 Search / Find / Open。

---

# 1. 当前最后一个核心问题

前面的 Research Loop 已经逐渐形成：

```text id="iwhr4r"
Current Need
    ↓
Search / Find / Open
    ↓
Observation
    ↓
Selective Belief Update
    ↓
Verified Claims / Working Hypothesis
```

目前真正没有被充分验证的是：

```text id="d3j7ej"
Original Question
+
Current Belief
    ↓
Next Research Need
```

完整闭环应该是：

```text id="9wguah"
Need_t
→ Evidence
→ Belief_{t+1}
→ Need_{t+1}
→ Evidence
→ ...
```

因此，本轮重点研究：

\[
\boxed{
Belief \rightarrow Need
}
\]

---

# 2. 核心理论假设

如果没有显式 Research State，

模型每一轮实际上必须隐式完成：

```text id="i1csu0"
Full History
    ↓
reconstruct current belief
    ↓
identify resolved requirements
    ↓
identify unresolved requirements
    ↓
select current research frontier
```

也就是把：

```text id="9j7l8y"
Belief Reconstruction
+
Frontier Generation
```

耦合在同一次模型推理中。

随着历史增长：

- irrelevant observations 增加；
- rejected candidates 留在 history；
- 重复 evidence 增加；
- 已解决 requirement 仍反复出现；
- 旧 focus 有路径惯性；
- 真正剩余 requirement 容易被长历史淹没。

---

显式 Research State 的理论作用不是替模型保存完整 Plan。

而是把：

```text id="6gebwa"
Evidence → Belief
```

和：

```text id="uscbwx"
Belief → Need
```

拆开。

Persistent semantic state 仍然只保持：

```text id="b9bu8u"
Original Question
Verified Claims
Working Hypothesis
```

Research Need / Gap 不作为新增 persistent semantic field。

Need 是：

```text id="tqjpzs"
ephemeral control state
```

每轮根据最新 Belief 动态生成。

核心假设：

\[
\boxed{
Persist\ belief,\ derive\ control.
}
\]

---

# 3. 本轮必须回答的三个主要问题

## RQ1 — State Sufficiency

如果给模型：

```text id="1dk88y"
Original Question
+
Verified Claims
+
Working Hypothesis
```

不给完整历史，

它是否仍然能够生成与：

```text id="h7u8ah"
State + Full History
```

相当质量的下一研究 Need？

如果：

```text id="61w6y4"
StateOnly ≈ State+History
```

说明 Research State 已经保留了大部分对未来研究决策真正重要的信息。

---

## RQ2 — State Externalization Benefit

相比只给完整历史：

```text id="qsvqnq"
HistoryOnly
```

显式 State 是否：

- 减少错误研究方向；
- 减少已解决 requirement 重复研究；
- 减少长历史噪声影响；
- 降低 input tokens；
- 降低 reasoning tokens；
- 提高不同独立调用之间的稳定性？

即：

显式 State 是否把：

```text id="k6brmy"
“现在我们知道什么？”
```

这个问题从 Frontier Generator 的负担中拿掉了。

---

## RQ3 — Frontier Control Form

在显式 State 被证明足够以后：

下一研究 Need 最合理的生成方式是哪一种？

```text id="77wd0z"
P = Persistent / Prior Gap
D = Direct Replan
R = Goal Residual → Need
```

重点不再是 Search query quality。

重点是：

```text id="gak2ph"
哪个方法更能发现“当前 Claims 中仍然缺失的原问题要求”？
```

尤其是：

```text id="88nl5m"
之前因为 selective admission 被暂时压掉，
后来应该重新进入 focus 的 requirement。
```

---

# 4. 首先创建新分支

执行：

```bash id="41nnxd"
git fetch --all --prune
```

确认：

`origin/experiment/deferred-recovery-global-vs-local`

最新 HEAD。

记录 exact SHA。

创建：

`experiment/frontier-generation-state-sufficiency`

如果已有同名 branch，使用明确 suffix。

禁止：

- force push；
- overwrite；
- rebase 历史实验；
- 修改已有实验 raw artifacts。

新目录：

```text id="yd2uct"
experiments/frontier_generation/
```

---

# 5. 必须先阅读的历史材料

任何新增 prompt / code 前先阅读：

## Deferred Recovery

```text id="hxv1el"
experiments/deferred_recovery/FINAL_CONCLUSION.md
experiments/deferred_recovery/DESIGN_AUDIT.md
experiments/deferred_recovery/r1/RESULTS.md
experiments/deferred_recovery/r2/RESULTS.md
experiments/deferred_recovery/bank/RESULTS.md
experiments/deferred_recovery/EXPLORATION_DECISION.md
```

## v3.1 Claim Admission

```text id="pzgn4h"
experiments/goal_residual_control_v3_1/FINAL_CONCLUSION.md
experiments/goal_residual_control_v3_1/admission_replay/RESULTS.md
experiments/goal_residual_control_v3_1/admission_exploration/RESULTS.md
```

## Goal Residual v2

```text id="q4gkig"
experiments/goal_residual_control/FINAL_CONCLUSION_V2.md
experiments/goal_residual_control/goal_review/RESULTS.md
experiments/goal_residual_control/research_decision_v2/RESULTS.md
experiments/goal_residual_control/one_step_acquisition_v2/RESULTS.md
experiments/goal_residual_control/transition_replan_v2/RESULTS.md
experiments/goal_residual_control/three_round_loop_v2/RESULTS.md
```

同时读取当前：

- Actor prompt；
- Goal Reviewer prompt；
- State Updater；
- G4/G5 state/request construction；
- Workspace / Trace projection。

必须在 DESIGN_AUDIT 中说明这些历史结果如何导致本轮问题。

---

# 6. 任何真实调用前先写 DESIGN_AUDIT.md

创建：

```text id="6fb4sa"
experiments/frontier_generation/DESIGN_AUDIT.md
```

必须回答：

1. 为什么 Frontier Generation 是当前闭环剩余的主要机制问题？
2. 为什么 History-only 并不意味着“没有状态”，而是把状态重建负担交给模型？
3. 为什么 Research State 的目标不是保存 Plan？
4. 为什么 Current Need 仍然应该是动态控制变量？
5. 什么结果能够证明 State 接近一个足够的决策压缩？
6. 为什么不能给每个 checkpoint 规定唯一 gold Need？
7. HistoryOnly / StateOnly / State+History 如何构造才公平？
8. Trace / Workspace 与 semantic Research State 如何区分？
9. 如何评价一个 Need 是否合理？
10. 如何识别 stale focus / drift / premature stop？
11. 如何测试 deferred requirement reactivation？
12. 为什么这轮不能同时修改 Writer / Retriever / Search？
13. 什么结果允许进入后续 Controller-form 对比？
14. 什么结果说明当前 State 不充分？
15. 如果失败，GPT-6 有多少探索自由？

先 commit DESIGN_AUDIT。

之后才能实施。

---

# 7. Research Frontier 的定义

本轮把 Frontier / Need 定义为：

> 在当前已知研究状态下，下一步最值得解决的一个未决研究问题。

Need 不是：

- Search query；
- Tool action；
- 长期 Plan；
- 子问题列表；
- Goal Residual 全量摘要。

Need 应该是一个当前可行动的研究目标。

例如：

正确：

```text id="j3xuiu"
Does Ding Junhui satisfy the requirement of more than three career maximum breaks by 30 January 2025?
```

不够好：

```text id="x8pqv3"
Research Ding Junhui more.
```

也不应该：

```text id="tnyfb4"
Search Ding Junhui maximum breaks Wikipedia.
```

后者已经是 action/query。

---

# 8. Frontier 输出合同

Frontier probe 只输出：

```json id="s5u01s"
{
  "decision": "act",
  "need": "..."
}
```

或者：

```json id="nkotbo"
{
  "decision": "stop",
  "need": ""
}
```

不输出：

- query；
- tool；
- plan；
- confidence；
- list of needs；
- explanation；
- score。

只允许一个 Need。

这样可以直接评价：

```text id="t2jpqy"
Belief → Need
```

而不混入：

```text id="918ia9"
Need → Tool
```

---

# 9. 不要设计唯一 Gold Need

一个 checkpoint 往往有多个合理 frontier。

例如同时还有：

```text id="ehnr4d"
R2 unresolved
R4 unresolved
candidate identity unresolved
final relation unresolved
```

先研究哪一个可能都合理。

因此禁止评价：

```text id="ery81w"
model_need == gold_need
```

---

# 10. 预先建立 Original Question Requirement Map

在任何 Frontier model call 前，

对每个入选 qid 建立：

```text id="lmzz2h"
Requirement Map
```

例如：

```text id="5kq0ng"
R1
R2
R3
R4
Final relation
Candidate identity requirement
```

这些 requirement：

- 必须来自 Original Question；
- 不能根据模型输出事后新增；
- 不要过度拆成几十个微观 atom。

目标是判断：

> 当前 Need 对应哪个真正的未解决要求。

---

# 11. 每个 checkpoint 需要冻结三种 coverage

这是本轮非常关键的设计。

同一个 requirement \(R_i\)：

### State Coverage

当前 Verified Claims 是否已经充分覆盖。

```text id="8b81fm"
state_resolved(R_i)
```

### History Coverage

当前完整真实 research history 中是否已经存在充分 grounded evidence。

```text id="wmyuq3"
history_resolved(R_i)
```

### Combined Coverage

二者并集。

```text id="vo26uw"
combined_resolved(R_i)
```

为什么必须三种？

因为：

StateOnly 看不到 raw historical evidence。

如果某个 requirement：

```text id="nifw59"
history_resolved = true
state_resolved = false
```

那么 StateOnly 再次把它生成成 Need：

不是 stale failure。

这是：

```text id="2twcje"
deferred requirement reactivation
```

应该视为合理行为。

反过来 HistoryOnly 如果能够正确利用旧 evidence：

它可以不再研究这个 requirement。

因此不同 arm 的“已经解决”必须按照它实际可见的信息判断。

不能用一套 Claim-only gold 强行评价三组。

---

# 12. Stage F0：Checkpoint Bank

从已有真实 G4/G5/transition trajectories 中建立真实 checkpoint inventory。

要求：

- 每个 checkpoint 有完整 Original Question；
- exact State；
- exact Working Hypothesis；
- 可恢复 chronological history；
- 没有未来信息；
- provenance 完整。

目标：

```text id="1p5h40"
24 checkpoints
>= 8 qids
```

如果可以安全扩大：

最多 30。

不要为了达到数量制造 synthetic state。

---

# 13. Checkpoint 分层

尽量覆盖：

### A. Early / Many unresolved

当前只有少量 Claim。

---

### B. Mid-research

已有多个 requirement 解决，但仍有多个未解决。

---

### C. Deferred-reactivation risk

History 中曾看到某个 requirement 的 evidence，

但当前 State 没保存。

---

### D. Candidate contradiction / pivot

当前 candidate 已有冲突或刚被否定。

---

### E. Near closure

只剩一个 requirement。

---

### F. Resolved

Claims 已经足够支持停止。

必须有一定 resolved checkpoint，

否则无法测 premature/missed STOP。

---

# 14. History 长度也必须覆盖

按实际 History input tokens：

```text id="4nqgfv"
Q1
Q2
Q3
Q4
```

四分位报告结果。

不要人工添加噪声。

先利用真实历史自然增长。

这样可以观察：

> HistoryOnly 是否随着历史变长更容易生成错误 frontier。

---

# 15. 三个核心输入 Arm

对完全相同 checkpoint：

## H — History Only / Implicit State

输入：

```text id="qmc1de"
Original Question
+
Chronological Research History
+
minimal mechanical control context
```

不给：

- Verified Claims；
- Working Hypothesis；
- Goal Residual；
- Current Gap。

History 包含真实过去：

- Actor needs/gaps；
- Search/Find/Open actions；
- source observations。

不得包含：

- updater output；
- current Claim list；
- Goal Reviewer residual；
- offline labels。

这个 arm 模拟：

> 模型必须从研究历史自己重建“目前知道什么、还缺什么”。

---

## S — Explicit State Only

输入：

```text id="xtiy7b"
Original Question
+
Verified Claims
+
Working Hypothesis
+
same minimal mechanical control context
```

不给：

- raw source history；
- earlier observations；
- old gaps；
- full tool trace。

这是：

> 显式 Research State 驱动前沿。

---

## SH — State + History

输入：

```text id="zxtxj8"
Original Question
+
Verified Claims
+
Working Hypothesis
+
Chronological Research History
+
same minimal mechanical control context
```

这是最高信息量 comparator。

核心问题：

```text id="ugznmx"
StateOnly 相比 State+History 到底损失多少？
```

---

# 16. Minimal mechanical context

为了不把 machine-truth 问题混进 semantic State，

三个 arm 可以共同看到：

- 当前 round；
- remaining budget；
- 最近最多 2 次 tool attempt 的：
  - tool；
  - query；
  - status。

不要包含：

- source text；
- reviewer judgement；
- hidden gold；
- target requirement ID。

本轮没有真正执行 Tool，

所以 Workspace handles 不需要进入 Frontier-only probe。

---

# 17. F1 调用方式

每个 checkpoint：

```text id="el44bd"
H × 2 independent calls
S × 2 independent calls
SH × 2 independent calls
```

两个调用都必须：

- 预先冻结；
- 都进入 denominator；
- 不能 best-of；
- 不能选好的那个；
- 不能 retry。

如果 24 checkpoints：

总共：

```text id="cipwsr"
144 Frontier calls
```

这两个 replicate 用于测：

```text id="bvdpmx"
Frontier stability
```

不是为了选答案。

---

# 18. Frontier Prompt

核心 prompt 保持极简。

建议：

```text id="xcdbnp"
You are choosing the next research frontier.

Given the Original Question and the information available in this view,
decide whether the research is complete.

If it is not complete, output exactly one current research need:
the most useful unresolved question to investigate next.

A good need:
- serves the Original Question;
- is not already adequately resolved by the information available to you;
- can materially reduce uncertainty, distinguish candidates, resolve a conflict,
  establish a required condition, or obtain the final requested relation;
- is specific enough to guide the next research action;
- does not assume a provisional hypothesis is already true.

Do not output a search query, tool action, long-term plan, list of subquestions,
confidence score, or explanation.

If the available information is sufficient to answer the Original Question,
return stop.

Return only the required JSON object.
```

三组使用完全相同 semantic instruction。

只改变 input view。

---

# 19. F1 的核心评价

每个 Need 后验映射到 Requirement Map。

至少记录：

## Valid Frontier

是否针对一个当前合理未决问题。

---

## Stale Revisit

是否研究在该 arm 可见信息中已经充分解决的 requirement。

---

## Goal Drift

是否研究 Original Question 不需要的东西。

---

## Unsupported Premise

是否把 Working Hypothesis / 历史猜测当成已验证事实。

---

## Over-broad Frontier

例如：

```text id="gjhdmw"
Find the answer to the whole question.
```

没有形成可执行前沿。

---

## Premature Stop

仍有必要 unresolved requirement 却 Stop。

---

## Missed Stop

全部必要条件已经足够却继续研究。

---

## Deferred Requirement Reactivation

StateOnly 是否重新提出：

```text id="447abc"
history 中曾有 evidence
但 State 没保存
```

的 requirement。

这是一个正向指标。

---

# 20. State Reconstruction Error

这是证明“显式 State 是否减轻负担”的关键指标。

## HistoryOnly reconstruction error

例如：

History 明明已经有充分 evidence，

但模型还是把 requirement 当 unresolved。

或者：

历史只有猜测，

模型却当作 verified。

这些是：

```text id="pz12s5"
implicit belief reconstruction errors
```

---

## StateOnly state-use error

Claims 明明已经解决 requirement，

模型仍重新研究。

或者：

Hypothesis 被误当作 Claim。

---

## State+History integration error

State 和 history 同时存在却仍：

- 被旧 observation 带偏；
- 被旧 candidate 锚定；
- 忽视 authoritative Claims。

---

# 21. Frontier Stability

两个 replicate 的 Need：

映射到 Requirement ID。

记录：

```text id="4iq8ig"
same valid requirement
different but both valid
one valid / one invalid
both invalid
```

不要要求 wording 一样。

如果 StateOnly：

相比 HistoryOnly 有更高：

```text id="8swly0"
semantic decision stability
```

这是显式 State 降低重建负担的重要证据。

---

# 22. 负担 / 成本指标

必须报告：

```text id="2d08le"
input tokens
output tokens
reasoning tokens
provider elapsed time
```

reasoning tokens 只能称：

```text id="cju10h"
inference-burden proxy
```

不能声称等于模型真实认知负担。

核心比较：

```text id="3u5793"
H vs S vs SH
```

特别看：

```text id="e1szg1"
StateOnly
```

是否在 Frontier 质量不下降时显著减少：

- input；
- reasoning；
- latency。

---

# 23. 长历史敏感性

按照 History token quartile：

分别报告 H/S/SH 的：

- Valid Frontier；
- stale revisit；
- drift；
- premature stop；
- instability。

重点观察：

```text id="bb6y2s"
HistoryOnly 的错误是否随着历史增长上升，
而 StateOnly 相对稳定。
```

这是非常重要的机制证据。

---

# 24. F1 State Sufficiency Gate

不要仅凭一个总准确率。

进入下一阶段至少要求：

### A. StateOnly frontier quality

```text id="gmo7k7"
Valid Frontier >= 85%
```

---

### B. StateOnly vs State+History

StateOnly 的 Valid Frontier 不应低超过约：

```text id="ndcnh5"
5 percentage points
```

并且不得新增：

```text id="9vx041"
>=3 个关键失败
```

且这些失败跨 ≥2 qids。

关键失败包括：

- premature stop；
- goal drift；
- unresolved blocking requirement 长期漏掉；
- unsupported candidate premise。

---

### C. State compression

即使 S 与 H 质量相当，

如果：

```text id="7u76a8"
S input context 大幅更小
```

并且 reasoning 没有明显增加，

仍然可以认为显式 State 有系统价值。

---

### D. State+History 的额外价值

如果 SH 相比 S：

```text id="b2dw05"
+ >=10 percentage points Valid Frontier
```

或：

```text id="rwrra2"
额外修复 >=3 个关键case，跨>=2 qids
```

则不能声称当前 State 已经足够。

必须分析：

> History 中哪类信息没有被 State 表达。

不要马上扩 State schema。

---

# 25. 结果解释

## 情况 1

```text id="bh5m8n"
S ≈ SH > H
```

同时 S context/reasoning 更低：

强支持：

```text id="hnc7bp"
显式 Research State 把 belief reconstruction 从 frontier generation 中解耦出来。
```

---

## 情况 2

```text id="o7ac23"
S ≈ H ≈ SH
```

但 S 显著更便宜：

Research State 仍然有价值，

但优势主要是：

```text id="0y5xa4"
compression / efficiency
```

不是 frontier accuracy。

---

## 情况 3

```text id="f7e0vy"
SH > S
```

History 仍有显著 decision-critical 信息没有进入 State。

不要立即增加字段。

先分类：

- omitted evidence；
- conflict；
- recent observation；
- candidate history；
- provenance；
- search-failure history。

---

## 情况 4

```text id="ogorur"
H > S
```

说明当前 explicit State 压缩损失过大，

不能直接把 State 当成充分控制表示。

---

## 情况 5

```text id="1yw19x"
S > SH
```

说明额外 History 反而造成明显干扰。

这是：

```text id="h9uib0"
history noise / anchoring
```

的强证据。

---

# 26. Stage F2：Frontier Transition Test

F1 Gate 通过后执行。

目标：

不是只看静态 checkpoint。

而是测试：

```text id="m1qgqf"
Belief发生变化以后，
Frontier会不会合理变化。
```

---

# 27. Transition Bank

选择：

```text id="q0j2mp"
12 real transitions
>=6 qids
```

每个 transition 有：

```text id="ni29mi"
pre-state
real Observation
post-state
```

必须是真实历史 mutation。

优先覆盖：

### T1 — Current requirement resolved

新 Claim 解决当前 focus。

---

### T2 — Candidate contradicted

新 Claim 否定当前 Working Hypothesis 或重要 candidate。

---

### T3 — New independent requirement evidence

某个未解决 Original Question 条件刚获得 Claim。

---

### T4 — Closure reached

最后必要 requirement 被解决。

---

# 28. 对每个 Transition

分别在：

```text id="z7tt1k"
pre
post
```

状态运行：

```text id="an5tzo"
H
S
SH
```

每个只跑一次即可。

因此如果 12 transitions：

```text id="p4skz2"
72 calls
```

HistoryOnly 的 post 输入必须真实加入这次 Observation。

StateOnly 的 post 输入必须只反映真实 post Claims/Hypothesis。

SH 两者都有。

---

# 29. F2 评价

## Appropriate Shift

当前 requirement 被解决后：

下一 Need 是否转向另一个合理未解决 requirement。

---

## Stale-focus Persistence

post-state 仍继续研究已经解决的旧 focus。

---

## Candidate Recovery

candidate 被 contradicted 后：

是否停止围绕该 candidate 继续研究。

---

## Deferred Requirement Reactivation

旧 focus 被解决后：

是否重新激活一个此前没有持久化、但 Original Question 仍需要的 requirement。

---

## Correct Stop Transition

最后 blocking requirement 解决后：

是否从 ACT 转成 STOP。

---

# 30. F2 Gate

StateOnly 至少应满足：

```text id="iurizn"
>=80% transitions
```

在 state change 后做合理：

```text id="zjxmzv"
shift or stop
```

并且：

```text id="56f27i"
stale-focus persistence <=10%
```

如果样本整数导致阈值不整，

保留 case-level解释，不机械追求百分比。

同时 S 不应明显差于 SH。

---

# 31. Stage F3：Frontier Control Form

F1/F2 通过后，

再回答我们之前 L0/L1/L2 的真正问题。

这里暂时不执行 Tools。

只比较 Need。

---

# 32. 三种 Frontier 生成方式

使用同一组 post-state checkpoint。

## P — Prior/Persistent Gap

输入：

```text id="c3e05n"
Original Question
Claims
Hypothesis
previous Gap
```

Previous Gap 使用真实历史值。

不人工改写。

这代表：

```text id="65ygd2"
cached focus
```

---

## D — Direct Replan

输入：

```text id="74bumc"
Original Question
Claims
Hypothesis
```

直接生成：

```text id="dyk22p"
Next Need
```

这是最简单方案。

---

## R — Goal Residual Assisted

第一调用：

```text id="rxm076"
GoalReviewer(
    Original Question,
    Verified Claims
)
→ Residual
```

Reviewer 不看 Hypothesis。

第二调用：

```text id="nc41u0"
Original Question
Claims
Hypothesis
Residual
→ Next Need
```

Residual 不持久化。

---

# 33. F3 的真正评价问题

不是：

> 哪个 Need wording 更漂亮？

而是：

### Need Coverage

是否指向一个真正未解决 requirement。

### Deferred Reactivation

是否更容易重新发现当前 Claims 没覆盖的要求。

### Stale Focus

是否继续旧 Gap。

### Premature Stop

是否错误停止。

### Unnecessary Whole-goal Review

Residual 是否引入已经解决或根本不存在的新要求。

### Cost

R 多一个 model call。

它必须有足够控制收益才能证明额外复杂度合理。

---

# 34. F3 的解释规则

## D ≈ R > P

支持：

```text id="sjh3dq"
Persistent Gap 有路径惯性；
Direct Replan 已经足够。
```

优先 D。

---

## R > D

如果 R：

- 明显减少 premature stop；
- 明显增加 deferred requirement reactivation；
- 没有增加 drift；

则 Goal Residual 的真正价值可能是：

```text id="w8kpvt"
帮助系统重新看到 Original Question 尚未覆盖的部分
```

而不是提升 Search acquisition。

---

## D ≈ R

没有理由为了极小收益增加 Reviewer call。

Goal Residual 可以保留：

```text id="fxfvcb"
diagnostic / occasional closure review
```

而不是 mandatory node。

---

## P ≈ or > D/R

必须放弃：

```text id="iv8wvl"
Persistent Gap 本身有害
```

这个强假设。

---

# 35. Stage F4：Autonomous Reactivation Mini-loop

如果 F1/F2 表明：

```text id="arxncs"
Explicit State 足够生成合理 Frontier
```

则进行一个小型真正闭环。

---

# 36. F4 Bank

使用：

```text id="fru95o"
8–12 held-out cases
>=6 qids
```

这些 case 必须满足：

- Original Question 有一个当前 Claims 尚未覆盖的 requirement；
- 这个 requirement 过去可能已有 Evidence 但未持久化；
- 不把 Recovery Need 人工提供给模型；
- source 仍在 corpus；
- 不与 F1/F2 reviewer prompt tuning 重叠。

---

# 37. F4 不再给 Recovery Need

Actor 只看到：

```text id="x13k24"
Original Question
Claims
Hypothesis
Workspace metadata
Recent Attempts
Budget
```

然后自己输出：

```text id="tb0bbf"
gap
+
Search/Find/Open action
```

这是真正测试：

```text id="ahygjq"
Belief
→ Need
→ Search
→ Evidence
→ Claim
```

完整链条。

---

# 38. F4 Controller Arms

根据 F3 预注册结果规则：

至少运行：

```text id="to3vya"
D
R
```

如果 P 在 F3 没有明显劣势，

也保留 P。

禁止根据单个 case 临时删除 arm。

---

# 39. F4 Budget

每 case：

```text id="6drziv"
最多 3 decisions
每 decision 最多 1 action
```

使用当前：

```text id="8lmuiq"
Search
Find
Open
U1 Writer
```

全部冻结。

不修改：

- Retriever；
- Find；
- Open；
- Writer；
- State schema。

---

# 40. F4 核心成功链

分别记录：

## Need Reactivated

模型是否自己重新提出缺失 requirement。

## Evidence Recovered

是否获得支持当前 Need 的 Evidence。

## Claim Recovered

是否重新写入 scoped Claim。

最终：

```text id="zhdkgu"
Autonomous Recovery Success
```

要求三步完整：

```text id="pgb6q2"
Need
→ Evidence
→ Claim
```

---

# 41. F4 Failure 分层

必须区分：

```text id="a62n23"
Need generation failure
Retrieval failure
Localization failure
Admission failure
Hypothesis/control failure
Premature stop
Horizon exhaustion
```

不能统称：

```text id="hasroc"
failed
```

这会直接告诉我们：

当前最后 bottleneck 到底在哪里。

---

# 42. 为什么 F4 非常重要

Deferred Recovery 之前已经测试：

```text id="fwhdte"
Given the correct Need,
can Search recover?
```

F4 第一次测试：

```text id="wjnoc7"
Without giving the Need,
can the system itself realize the requirement is still unresolved,
then recover it?
```

这才是真正的：

```text id="cu3usv"
Selective State + Recovery
```

闭环。

---

# 43. DeepSeek transport

沿用当前稳定方案：

```text id="v4v4n9"
JSON mode
+
strict deterministic Harness validation
```

本轮禁止继续研究：

- structured output；
- strict schema；
- function calling capability。

所有错误分类仍保持：

```text id="5sf7qe"
transport failure
Harness violation
semantic failure
length/incomplete
provider failure
```

零 retry。

---

# 44. 不允许改的组件

本轮冻结：

- model；
- provider；
- Search；
- Find；
- Open；
- Retriever；
- localizer；
- U1 Writer；
- Claim schema；
- Working Hypothesis schema；
- Workspace；
- corpus；
- question set；
- source truth；
- no retry；
- no best-of。

禁止增加：

- Confidence；
- Frontier list；
- Plan graph；
- Requirement graph 作为 runtime State；
- Conflict graph；
- Recovery tool；
- memory router；
- query optimizer；
- new persistent fields。

Requirement Map 只用于离线 evaluation。

不能进入生产模型输入。

---

# 45. GPT-6 的有限探索自由

如果某个主要 Gate 失败，

允许：

```text id="tl3xm3"
一次且仅一次 bounded exploration
```

不能多轮 prompt sweep。

必须先写：

```text id="5he1lr"
EXPLORATION_PLAN.md
```

并 commit/freeze。

---

# 46. 允许探索的方向

只能选择一个最符合 observed failure 的方向。

## A. Frontier 太宽 / 不可行动

如果大量输出类似：

```text id="31i8qc"
figure out the whole answer
```

允许增加一句：

```text id="l0224j"
Choose the smallest currently useful unresolved research question.
```

做小样本验证。

---

## B. Hypothesis 导致 unsupported premise

如果很多 Need 因 Hypothesis 被当事实而错误：

允许小样本：

```text id="znz37u"
ClaimsOnly
vs
Claims+Hypothesis
```

诊断 Working Hypothesis 是否帮助或伤害 Frontier。

不得直接删除 Hypothesis。

---

## C. StateOnly 明显输给 State+History

如果差异集中于：

```text id="c9lvq9"
刚刚看到但尚未形成Claim的最新Evidence
```

允许测试：

```text id="vi8hrf"
State
+
one ephemeral Recent Observation
```

作为诊断。

这不是新的 persistent State field。

不能因此直接改正式架构。

---

## D. Direct Replan 漏 requirement，而 Residual 明显帮助

允许一次小型 Residual prompt clarification。

不得增加第三个 Reviewer 或 plan node。

---

## E. HistoryOnly 在长 History 主要因重复/格式噪声失败

允许一个**机械、非语义**的 chronological compression sensitivity：

例如去重完全相同 tool events。

不能用模型提前总结 History。

否则已经等价于创建另一种 State。

---

# 47. Exploration 预算

最多：

```text id="932z75"
12 checkpoints
<=24 Frontier model calls
```

或：

```text id="uy22c5"
<=8 mini-rollout cells
```

只能一次。

探索结果只能标：

```text id="68qb1m"
exploratory
```

不能覆盖原 Gate。

---

# 48. 最终必须回答的问题

最终报告至少明确回答：

1. HistoryOnly 的 Valid Frontier rate 是多少？
2. StateOnly 是多少？
3. State+History 是多少？
4. StateOnly 是否接近 State+History？
5. Full History 在已有 State 后还有多少额外控制价值？
6. StateOnly 相比 HistoryOnly 是否减少 stale revisit？
7. 是否减少 goal drift？
8. 是否减少 premature stop？
9. 是否减少 unsupported candidate premise？
10. 长 History 是否显著伤害 HistoryOnly？
11. StateOnly 对 History length 是否更稳健？
12. 三组 input token 差多少？
13. reasoning-token proxy 差多少？
14. Frontier replicate stability 如何？
15. StateOnly 能否重新激活 deferred requirement？
16. Belief mutation 后 Frontier 是否及时切换？
17. candidate contradiction 后是否停止旧 candidate 路径？
18. closure 后是否正确 Stop？
19. Persistent Gap 是否导致更多 stale focus？
20. Direct Replan 是否已经足够？
21. Goal Residual 是否显著提升 requirement reactivation？
22. Residual 的收益是否值得额外一个 model call？
23. F4 中 Autonomous Need Reactivation 成功率多少？
24. Need 生成正确后 Search recovery 是否仍稳定？
25. Evidence 出现后 U1 是否重新形成 Claim？
26. 最终 dominant failure 在：
   - State sufficiency
   - Need generation
   - Retrieval
   - Admission
   - Hypothesis
   - Stop
   哪一层？
27. 当前最小 Persistent Research State 是否仍可保持：

```text id="bh93x1"
Original Question
+
Verified Claims
+
Working Hypothesis
```

28. Current Need 是否仍应该保持 ephemeral？
29. 是否还需要 mandatory Goal Reviewer？
30. 是否已经有足够机制证据进入最终大规模 G4/G5 controller validation？

---

# 49. 最重要的最终解释原则

不要为了证明 Research State 有用而解释结果。

允许出现：

```text id="bvph4q"
HistoryOnly >= StateOnly
```

如果发生，

就说明当前 State 还没有成为充分的决策表示。

---

不要为了证明 Goal Residual 有用而解释结果。

如果：

```text id="gm5kfi"
Direct Replan ≈ Goal Residual
```

优先简单架构。

---

不要因为某个 deferred requirement 没有被立即提出就自动判失败。

Frontier 可以有多个合理方向。

真正的问题是：

> 系统是否长期遗漏 blocking requirements，还是只是在合理排序它们。

---

不要要求一次 Need 生成覆盖所有 unresolved requirements。

Research Frontier 本来就是：

```text id="wrqn5n"
one active focus
```

我们关心的是：

```text id="s20pfj"
随着Belief变化，
合理未决问题能否逐步重新进入focus。
```

---

# 50. 本轮真正的理论检验

如果最终观察到：

```text id="vr11wb"
StateOnly ≈ State+History
```

同时：

```text id="x7awds"
StateOnly context << HistoryOnly context
```

并且：

```text id="mrfpqz"
Need quality / stability >= HistoryOnly
```

那么可以较强地支持：

> 显式 Research State 的主要价值，不是替模型保存一个长期计划，而是把“从历史重建当前认知状态”和“决定下一步研究什么”这两个任务解耦。

这意味着：

```text id="m40q36"
Evidence → Belief
```

可以独立维护，

然后：

```text id="319xl9"
Belief → Need
```

每轮动态重新计算。

---

如果 F4 最终还能跑通：

```text id="zvs0pr"
Selective Claim omission
→ Future Need reactivation
→ Global Search
→ Evidence recovery
→ Claim re-admission
```

那么当前 Research Loop 的核心闭环就基本形成：

\[
\boxed{
Need
\rightarrow
Evidence
\rightarrow
Belief
\rightarrow
Need
}
\]

到这一步以后，

下一阶段才应该回到较大规模的：

```text id="w42gl4"
G4 / G5 end-to-end controller validation
```

而不是继续增加新的 State ontology。

---

# 51. 推荐目录

```text id="5y9j8t"
experiments/frontier_generation/
    README.md
    DESIGN_AUDIT.md
    HYPOTHESES.md
    PROTOCOL.md
    FROZEN_STATE.md
    FINAL_CONCLUSION.md
    COMPLETION.json

    bank/
        CHECKPOINT_INVENTORY.json
        REQUIREMENT_MAP.json
        CHECKPOINT_BANK.json
        TRANSITION_BANK.json
        REACTIVATION_BANK.json
        SELECTION.json
        RESULTS.md

    prompts/
        frontier.md
        goal_reviewer.md

    schemas/
        frontier.json

    f1_state_sufficiency/
        requests.json
        freeze.json
        events.jsonl
        outputs.json
        reviews.json
        metrics.json
        RESULTS.md

    f2_transitions/
        ...
        RESULTS.md

    f3_controller_form/
        ...
        RESULTS.md

    f4_autonomous_reactivation/
        ...
        RESULTS.md

    analysis/
        PER_CASE.json
        PER_QID.json
        HISTORY_LENGTH_SENSITIVITY.json
        COSTS.json
        INTEGRITY.json

    exploration/
        EXPLORATION_PLAN.md
        ...
```

---

# 52. 执行顺序

严格执行：

1. fetch 最新远程；
2. 创建新 branch；
3. 阅读指定历史材料；
4. 写 DESIGN_AUDIT；
5. commit；
6. 构建 Requirement Map；
7. 构建 checkpoint inventory；
8. 冻结 F1 bank；
9. 冻结全部 F1 requests；
10. 运行 H/S/SH；
11. blind/masked semantic review；
12. F1 analysis；
13. Gate；
14. 如通过，构建并冻结 F2 transition bank；
15. 运行 F2；
16. Gate；
17. 运行 F3 P/D/R；
18. 如机制足够稳定，运行 held-out F4 autonomous reactivation；
19. 如任一主要 Gate 失败，只允许一次 bounded exploration；
20. 完整性检查；
21. FINAL_CONCLUSION；
22. push remote。

不要请求用户再次确认。

不要修改旧实验结果。

不要用漂亮的单 case 推翻 frozen aggregate result。

不要因为 History 很长就事后删掉不利 History。

不要把 Requirement Map 暴露给生产模型。

让数据回答：

\[
\boxed{
Explicit\ Research\ State
是否真的让“下一步该研究什么”
变得更简单、更稳定、更可恢复。
}
\]