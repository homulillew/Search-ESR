你现在负责 Search-ESR 下一阶段的 Deferred Recovery 实验。

仓库：

https://github.com/homulillew/Search-ESR

当前最新研究分支：

`experiment/goal-residual-control-v3-admission-replay`

本轮运行模型继续使用：

`deepseek-flash`

你作为 GPT-6 负责研究设计实现、冻结、运行、审计和分析。

---

# 0. 本轮研究位置

当前已经得到一个重要结果：

Persistent Claim Writer 如果只根据 Observation 做 source-supported fact extraction，会产生严重 Claim 膨胀。

v3.1 U1 通过 Current Gap-conditioned selective admission：

- Incidental Claims：44 → 2
- Decision-relevant precision：38.03% → 90%
- State mutation：37/55 → 15/55
- 新增 State characters：6461 → 1823

但 immediate useful-atom recall：

85.19% → 74.07%。

进一步分析表明，这些“遗漏”不是同一种失败。

至少存在：

1. 当前 Gap 直接相关但未写入；
2. 当前 Persistent Belief 的冲突信息未写入；
3. 原问题未来需要，但当前 research focus 暂时不在该 requirement；
4. 比已有 Claim 更精确的信息未立即更新；
5. 低边际或冗余证据；
6. 语义 Claim 已存在，只是增加新 provenance/support；
7. Claim 已持久化后真正丢失。

当前数据中没有发现第 7 类：
Verified Claims 是 append-only，这批 recall loss 主要发生在 Observation → Claim admission 阶段。

本轮重点研究第 3 类及部分第 4 类：

**以前已经观察到、但由于当时不是当前 focus 而没有持久化的信息，当未来真正成为 Current Need 时，是否可以可靠恢复。**

因此本轮不要求 State Writer 一次保存所有 Original Question 未来可能需要的事实。

研究的系统假设是：

```text
Write what matters now
+
Preserve recoverability
+
Recover when needed later
```

即：

\[
\boxed{
High\ Precision\ State
+
High\ Eventual\ System\ Recall
}
\]

而不是：

\[
Perfect\ Immediate\ Claim\ Recall
\]

---

# 1. Recovery 的定义

本轮定义：

\[
Recovery
=
重新获得一个过去已经观察过、
但当前 Persistent Claims 中不可用、
且现在已经成为 Current Need 的事实。
\]

Recovery 是一个评价意义上的信息事件。

它不是新的 Tool。

禁止增加：

```text
recover(...)
recall(...)
memory_search(...)
```

等工具。

Runtime Action Space 仍然只有：

```text
Search
Find
Open
```

如果一个旧事实通过普通 Search 重新出现：

这是 Recovery。

如果通过 Find 在旧 D 中重新定位：

也是 Recovery。

如果 Search 找到一个全新的 Source 来满足同一 Need：

同样视为成功解决当前 Need，但单独标记为 New-source Recovery。

---

# 2. 本轮明确禁止 Harness 做语义 Recovery 路由

不得实现：

```text
if Claims 没解决 Gap:
    搜 Workspace
if Workspace 不够:
    搜 Corpus
```

因为：

- “Claims 是否解决 Gap”是语义判断；
- “旧 W 是否相关”是语义判断；
- “旧来源是否足够”也是语义判断。

这些不能由纯 Harness 机械代码决定。

Harness 只能：

- 保存状态；
- 保存 D/W；
- 验证 handle；
- 验证预算；
- 执行模型选择的 tool；
- 记录 observation；
- 记录 provenance；
- 做机械 contract validation。

Research Actor 决定：

```text
当前 Need 是什么；
下一步 Search / Find / Open / Stop；
应该搜索什么 query；
应该 Find 哪个 D。
```

---

# 3. 两种需要比较的 Recovery Architecture

本轮主比较不是 Local-first Harness router。

而是：

## Arm G — Unified Global Rediscovery

Recovery 统一使用 Global Search。

Actor 当前只需要：

```text
Current Recovery Need
→ Search(query)
```

不需要判断：

```text
这是旧 Evidence 还是新 Evidence？
```

Search 对整个 corpus 排名。

旧 Document 与新 Document 公平竞争。

如果旧 Document 再次命中：

Search 必须按照当前 query 对该 Document 重新生成 query-localized preview。

因此 Arm G 必须使用：

`llm_chat/search_find_agent.py`

中 v3a Search 的语义。

不能使用：

`search_find_v3b_agent.py`

的 Orthogonal Search。

原因：

v3b 明确规定：

```text
old documents cannot be locally re-localized by Search
```

当 Search 命中已发现 Document 时，它只返回：

```text
status = already_discovered
existing_preview_ref
usage_hint = use Find
```

不会调用新的 local window search。

这种 Search 从定义上不能承担 unified Global Recovery。

---

## Arm H — Global Rediscovery + Opportunistic Local Reuse

使用与 Arm G 完全相同的 v3a Global Search。

额外允许 Actor：

```text
Find(D#, query)
Open(W#, direction)
```

Actor 可以：

- 直接 Search 全 corpus；
- 如果它明确知道某个历史 D 可能有用，则 Find；
- 对刚获得的 W 用 Open 补上下文。

没有 Local-first 强制顺序。

没有 Harness router。

没有：

```text
Workspace first
Corpus second
```

的机械策略。

因此：

\[
H = G + optional\ local\ action\ choices
\]

本轮核心问题之一就是：

**给 Actor 这些 local reuse 选择，是否真的带来足够的 Recovery / cost 收益，值得增加 policy complexity。**

---

# 4. 为什么不是直接比较 v3a vs v3b

不要把：

```text
v3a Search
```

直接对：

```text
v3b Search+Find
```

作为主实验。

因为这会同时改变：

- Search 对旧文档的语义；
- Action Space。

本轮更干净的比较是：

两组都使用 v3a unified Search。

差异只有：

```text
G: Search
H: Search + Find + Open
```

这样：

G vs H

真正回答：

**在 Global Rediscovery 已经可用的情况下，显式 Local Reuse 是否还有额外价值。**

v3b 可以保留为历史参考，不修改。

---

# 5. 创建新分支

先：

```bash
git fetch --all --prune
```

确认：

`origin/experiment/goal-residual-control-v3-admission-replay`

最新 HEAD。

从这个 HEAD 新建：

`experiment/deferred-recovery-global-vs-local`

如果远程已有同名分支，使用明确 suffix。

禁止：

- overwrite
- force push
- rebase 历史实验
- 修改任何旧实验 raw artifact。

创建：

```text
experiments/deferred_recovery/
```

---

# 6. 第一阶段：DESIGN_AUDIT

任何新模型调用前必须先创建：

`experiments/deferred_recovery/DESIGN_AUDIT.md`

至少回答：

1. Immediate Claim Recall 为什么不是最终系统 Recall？
2. 什么是 Deferred Recovery？
3. 哪些 v3.1 omission 属于 Deferred，而不是 immediate Writer failure？
4. 为什么 conflict with persistent belief 不应简单视为普通 deferred fact？
5. 为什么 Recovery 不是一个新 Tool？
6. 为什么 Harness 不做 Workspace→Corpus semantic routing？
7. 为什么当前 v3b Orthogonal Search 无法承担 Global Recovery？
8. 为什么 Global arm 必须使用 v3a Search semantics？
9. G 与 H 的唯一主要差别是什么？
10. 如何避免旧 Workspace raw text直接泄露目标 Evidence？
11. 如何定义 Recovery success，而不是 exact-old-window recall？
12. 如何区分 Retrieval failure 与 Writer re-admission failure？
13. 本轮允许 GPT-6 在什么情况下做一次 bounded exploration？

完成并 commit 后再继续。

---

# 7. Stage R0：建立 Recovery Bank

Recovery Bank 必须优先使用真实历史 Observation。

不能人工制造答案 Evidence。

候选来源：

1. v2 G5 的 372 个真实 Updater events；
2. v3.1 Admission Replay 中已经确认的 omission；
3. 其它已有真实 Search/Find/Open Observation，只要 provenance 完整。

---

# 8. Omission 先分类，不能所有 missed atom 一起使用

每个候选 omission 必须由 reviewer 在任何 Recovery 模型调用前归类为：

## D1 — Immediate Current-Need Miss

Observation 中的事实直接回答当时 Current Gap，但 Writer 没写。

这主要诊断 Writer。

不是 Primary Deferred Recovery。

---

## D2 — Belief-Conflict Miss

Observation 与当前 Persistent Claim 存在 material contradiction：

例如：

```text
1992
vs
1993
```

这种信息原则上有即时 Belief Revision 价值。

单独作为 Safety cohort。

不能用“以后可以恢复”来证明这种 omission 是安全的。

---

## D3 — Deferred Original-Requirement Fact

事实：

- 与 Original Question 的某个 requirement 明确相关；
- 当前 Current Gap 暂时在研究别的 requirement；
- 当时不写入可以解释为 selective compression；
- 未来 requirement 变成 Current Need 时应该能够恢复。

这是 Primary Recovery cohort。

典型：

```text
q311:
当前研究 Argentinian name / cast
Observation 出现 exact 4-minute runtime
```

以及：

```text
q546:
当前研究 2023 match sequence
Observation 出现 fifth career 147
```

---

## D4 — Refinement Miss

Persistent Claim 已有粗信息：

```text
runtime = 4–10
```

新 Observation：

```text
runtime = 4
```

属于更精确信息。

如果当前 focus 不需要精度升级，可以允许延迟。

进入 Primary/Sensitivity，单独标记。

---

## D5 — Low-Marginal / Redundant

例如：

已经有足够的历史-success Claim，

Observation 又提供另一条同方向弱证据。

不应因为 Writer 没保存就自动视为系统失败。

不进入 Primary Recovery success denominator。

可以作为 negative/control。

---

## D6 — Evidence/Provenance Augmentation

Semantic Claim 已经存在，

只是新来源增加：

```text
support_ref
corroboration
source-specific evidence
```

不要自动要求生成新 semantic Claim。

这类不进入普通 Claim Recovery denominator。

单独分析 Evidence binding。

---

# 9. Primary Recovery Bank

Primary cohort 只包含：

```text
D3 Deferred Original-Requirement
+
D4 material Refinement
```

目标：

约 20–30 cases。

尽量：

- ≥ 6 qids；
- 同一 qid 不超过总样本 25%；
- provenance 完整；
- 原始 source 仍存在 corpus；
- 当前 Claims 尚未解决 future Need；
- 原始 Observation 确实足以支持 Need。

如果没有 20 个：

不要制造。

最低完整性：

```text
>=12 cases
>=6 qids
```

若不足，报告 bank limitation，不扩 synthetic case。

---

# 10. Challenge / Anchor Set

v3.1 已知 omission：

例如：

- q311 exact 4-minute runtime
- q546 fifth career 147
- q186 release-year conflict
- q177 1974 double
- q546 first 147

可以保留为：

`KNOWN_CHALLENGE_SET`

但由于这些 case 已经参与前序分析，不作为 fresh generalization 的唯一依据。

Primary report 必须将：

```text
fresh recovery cohort
```

和：

```text
known challenge cases
```

分开。

---

# 11. 每个 Recovery Case 的冻结结构

每个 case 至少保存：

```json
{
  "case_id": "...",
  "qid": "...",

  "original_question": "...",

  "claims_at_recovery_start": [...],

  "working_hypothesis": "...",

  "recovery_need": "...",

  "historical_document_catalog": [...],

  "private_recovery_truth": {
    "requirement": "...",
    "historical_support_doc": "...",
    "historical_support_window": "...",
    "support_hash": "...",
    "acceptable_relation": "..."
  },

  "category": "D3 | D4 | ..."
}
```

其中：

`private_recovery_truth`

绝不能进入 production model input。

---

# 12. Recovery Need 的构造

Recovery Need 必须：

- 来自 Original Question 中尚未解决的 requirement；
- 不包含答案；
- 不包含目标 source；
- 不告诉模型“以前看过这个”；
- 不告诉模型 exact old W；
- 不使用未来 trajectory 的答案信息。

例如：

不要：

```text
Find the old page where Ding's fifth 147 appeared.
```

应该：

```text
Does Ding Junhui satisfy the requirement of having made more than three career maximum breaks by the relevant date?
```

不要：

```text
Re-read AlloCine for the 4 minute runtime.
```

应该：

```text
Does the candidate program satisfy the requirement that its episodes run for less than five minutes?
```

---

# 13. Recovery success 的定义

Primary success 不是：

```text
重新找到 exact old W
```

而是：

\[
\boxed{
Current Recovery Need
被新获得的grounded evidence支持，
并重新成为可用Persistent Claim
}
\]

因此以下都算成功：

### Old-source Rediscovery

Global Search 重新找到历史 Document 并产生新 query-localized W。

### Local Reuse

Find 在已知 D 中重新定位 Evidence。

### New-source Recovery

Global Search 找到一个以前没见过的新 Source，
但同样可靠地解决 Recovery Need。

分别记录 path。

---

# 14. Stage R0.5：验证 Global Search 的 Recovery 语义

在任何研究 Actor 调用前做 deterministic tool audit。

必须证明 v3a：

`SearchFindTools`

在：

1. 某 Document 已经注册为 known D；
2. 新 query 再次命中同一 Document；

时仍然：

- 调用当前 query 的 local window search；
- 返回 query-localized preview；
- 可以产生新的/对应的 W；
- 不只是 `already_discovered` metadata。

至少使用 3 个真实历史 Document 做 offline/integration check。

同时证明 v3b：

`OrthogonalSearchFindTools`

仍保持历史语义不变。

不要修改 v3b。

如果 v3a 当前实现无法完成这种 relocalization：

允许修复**实现 bug**，

但不能改变 Retriever、ranking 或 localizer algorithm。

修复后重新 freeze。

---

# 15. Context Projection：模拟“以前见过，但现在不在活跃上下文”

Recovery 实验不能把旧 raw W text直接放回 Actor Context。

否则没有 Recovery 问题。

两个 arm 都看到完全相同的：

`Historical Document Catalog`

内容只包含机械 metadata：

```text
D#
title
url
```

不要包含：

- old window text；
- target passage；
- private relevance label；
- target rank；
- old answer；
- reviewer judgement。

底层 tool session 仍恢复真实 Handle Registry，
因此 H arm 的 Find(D#) 可以执行。

两个 arm 的 catalog 完全相同。

---

# 16. Stage R1：One-step Recovery Decision

同一个 case 做 paired comparison。

Actor input：

```text
Original Question
Current Claims
Working Hypothesis
Current Recovery Need
Historical Document Catalog
Recent Attempts
Budget
Tool schema
```

不提供 Goal Residual node。

本轮 Recovery Need 已经是冻结的当前 Gap。

---

# 17. Arm G — Global only

只暴露：

```text
Search
```

每次最多：

```text
1 action
```

Search 使用 v3a unified semantics。

目标：

测试：

\[
Need
\rightarrow
Query
\rightarrow
GlobalCorpus
\]

本身是否足以恢复历史 Evidence。

---

# 18. Arm H — Opportunistic local reuse

暴露：

```text
Search
Find
Open
```

但第一 decision 最多一个 action。

Actor 自己判断：

- Search；
- Find 某个已知 D。

Harness 不推荐 Local-first。

Harness 不告诉哪个 D 正确。

如果 first action 产生新 W，
第二 decision 可以 Open/Find/Search。

---

# 19. 为什么每 decision 只允许一个 action

Recovery Probe 中暂时不用历史的 max-two independent actions。

原因：

本轮要清楚观察：

```text
Need
→ first action choice
→ Evidence
```

避免：

```text
一个 decision 同时 Search + Find
```

后无法判断哪个动作真正负责 Recovery。

这是 Recovery probe 的实验预算，不是生产 Harness 架构修改。

---

# 20. Stage R1 评价

每个 first action 必须标注：

### Tool choice

```text
Search
Find
Open
Stop
```

### Source outcome

```text
old_source
new_source
wrong_old_source
no_useful_source
```

### Evidence outcome

```text
direct_need_support
decision_progress
no_progress
```

### Old source rediscovery

Search 时记录：

```text
historical target doc rank
returned or not
query-localized target evidence visible or not
```

### Local source lock

H 如果选择 old D：

记录：

```text
Find 是否取得 Progress
```

如果 H 在 old D 中浪费 action，
但 paired G 成功找到 evidence：

标记：

```text
local_source_lock
```

---

# 21. Stage R2：Two-decision End-to-End Recovery

R1 的真实 first decision/result 原样成为 R2 prefix。

不重新运行第一步。

最多再允许：

```text
1 second Actor decision
1 action
```

因此总 budget：

```text
2 decisions
2 sequential actions
```

这允许：

```text
Search → Find
Find → Open
Search → Open
Search → Search
```

但必须跨 decision 顺序执行。

---

# 22. 每次新 Observation 后使用 Selective Writer 重新物化 Claim

使用 v3.1 U1 的 selective Writer 语义。

但：

```text
Current Research Gap
```

设置为：

```text
Recovery Need
```

因为现在这个 requirement 已经真正成为当前 focus。

不得使用 U2 eager-global-coverage prompt。

本轮恰恰要验证：

**一个当初因为 off-focus 被 U1 合理压掉的事实，当它后来成为 Current Gap 后，U1 是否能够重新 admission。**

---

# 23. Recovery Loop 不使用 Gold 在线停止

Private truth 不能进入生产控制。

不要：

```text
if recovered:
    stop
```

这种 gold-triggered runtime。

最多运行两个 decisions。

Actor 可以自己输出 Stop。

后验 reviewer 判断：

- 是否已经 recovered；
- Actor stop 是否 premature。

---

# 24. 分解两个 failure layer

Primary end-to-end failure 必须拆成：

## Retrieval Failure

两个 decision 中：

没有任何 Observation 支持 Recovery Need。

---

## Admission Failure

Observation 已经出现充分 Evidence，

但 U1 Writer 没有形成必要 Claim。

---

## Actor Control Failure

合适 D/Source 已经明显可用，
但 Actor 选择无效路径或 premature stop。

---

## Local Lock-in

H 反复利用旧 D，
而新的 global source 才能解决 Need。

---

# 25. Primary Metrics

必须至少报告：

## Recovery

```text
Need Recovery Success / planned
```

最终 Claims 是否重新拥有解决 Need 的 grounded information。

---

## Evidence Visibility

```text
Useful Evidence Visible / planned
```

不要求已经进入 Claim。

---

## Evidence → Claim Conversion

```text
Recovered Claim / Evidence-visible cases
```

这个指标直接测试：

当 fact 成为 Current Gap 后，
Selective Writer 能否重新物化它。

---

## Old-source Rediscovery

Global Search 中：

```text
OldDocRecall@5
OldEvidenceVisibility@5
```

---

## New-source Recovery

Global Search 是否通过新 source 解决 Need。

---

## Local Reuse Yield

```text
Useful Find / Find calls
Useful Open / Open calls
```

---

## Source Lock-in

H 的 local action 导致失败，而 G 同 case 成功。

---

## Cost

```text
Actor calls
Tool calls
Updater calls
input tokens
output tokens
cache usage
```

---

## Latency

```text
decisions to Evidence
decisions to Claim Recovery
```

---

## Premature Stop

Actor 在 Need 未恢复时 Stop。

---

# 26. Paired comparison

每 case 比较：

```text
G vs H
```

记录：

```text
G only success
H only success
both success
both fail
```

以及：

```text
G cheaper
H cheaper
tie
```

同 qid case 相关。

不做独立样本 p-value 宣称。

---

# 27. Reference-design decision rules

不要求强行选 winner。

## Global Rediscovery 足够

如果：

```text
G recovery success >= 75%
```

并且：

```text
Evidence-visible → Claim conversion >= 85%
```

同时 H 相对 G：

```text
净增加 recovery < 3 cases
```

且没有明显成本优势，

则结论倾向：

\[
\boxed{
Unified\ Global\ Rediscovery
作为默认Recovery机制已经足够
}
\]

Find/Open 保留普通工具，但不需要为了 Recovery 建立特殊 local policy。

---

## Opportunistic Local Reuse 有独立价值

如果 H：

- 相对 G 净增加 ≥3 个 Recovery success；
- 且覆盖至少 2 个 qid；

或者：

- Recovery success 相当；
- 但 tool/token cost 降低 ≥25%；

且：

- 没有 >1 个新增 local-source-lock regression；

则支持：

\[
\boxed{
GlobalSearch
+
optional\ Find/Open
}
\]

作为 Reference Harness。

仍然不增加 Harness semantic router。

---

## Global 明显不足

如果：

```text
G recovery success < 60%
```

重点诊断：

- Query；
- document rank；
- old doc rediscovery；
- initial localization；
- writer conversion。

不能直接得出：

```text
Selective State 不可行
```

---

# 28. Safety cohort：Belief Conflict

D2 conflict cases 不进入 Deferred Recovery primary success。

单独报告。

问题：

如果一个 Observation：

```text
directly contradicts Persistent Claim
```

而 Writer 没写，

是否应该允许它像普通 future fact 一样延迟到以后 Recovery？

默认假设：

\[
\boxed{
No
}
\]

因为错误/冲突 Belief 会立即影响后续 decision。

测试：

- conflict later recoverable?
- 在 recovery 前是否会造成 incorrect action / premature closure？

本轮不需要大规模 rollout。

只做小型诊断。

最终回答：

是否应该把：

```text
Belief-contradicting evidence
```

作为 Immediate Admission exception。

---

# 29. Provenance-only cases

D6 单独报告：

如果 Semantic Claim 已存在：

不要求生成 duplicate Claim。

检查 Harness 是否可以：

```text
append support_ref
```

或至少保持 source evidence 可追溯。

不要用这种 case 惩罚 Claim Recall。

本轮不得因此新增复杂 Claim graph。

---

# 30. Recovery Bank 不能泄漏旧 Evidence

Production Actor input 绝不能包含：

```text
target old W
target source label
private need truth
old evidence text
```

Historical Document Catalog 只是：

```text
D#
title
url
```

两个 arm 完全相同。

所有 reviewer labels、target refs、acceptable facts 都只在 offline evaluation。

---

# 31. DeepSeek 输出

沿用当前 v3.1 结论。

不继续研究 structured output。

使用当前稳定的：

```text
JSON mode
+
strict Harness validation
```

记录：

```text
transport_structural_failure
harness_control_violation
semantic_failure
length/incomplete
provider failure
tool failure
```

零 retry、零 repair、零 best-of。

---

# 32. 不允许改的组件

冻结：

- DeepSeek model/provider
- corpus
- retriever
- embedding
- ranking
- localizer
- Search k 默认值
- Find implementation
- Open implementation
- U1 Writer prompt
- State schema
- Claim max 2
- Hypothesis schema
- source truth
- no retry
- no best-of

唯一特殊点：

Global Search 必须使用现有 v3a semantics，
因为这正是被测试的 unified recovery capability。

不要修改 v3b 历史实现。

---

# 33. Bounded Exploration：给 GPT-6 的有限自由

如果 Primary Recovery 结果没有达到门槛，
你可以进行**一次且仅一次** bounded exploratory follow-up。

必须先创建：

`EXPLORATION_PLAN.md`

说明：

1. Primary failure 位于哪个 layer；
2. 为什么所选 remedy 针对这个 layer；
3. 为什么不改变研究问题；
4. 最大额外调用数；
5. 成功/失败如何解释。

然后 commit/freeze 后执行。

---

# 34. 允许 GPT-6 从下面方向中选择一个

只能选择一个。

## A. Query formulation exploration

仅当：

```text
target doc rank低 / Search query明显表达不充分
```

允许改 Recovery Actor 的 query instruction。

不能改 Retriever。

---

## B. k sensitivity

仅当：

```text
target old docs 经常 rank 6–10
```

允许固定：

```text
k=10
```

做小样本 sensitivity。

不能动态调 k。

---

## C. Historical Document Catalog projection

仅当 H 明显因为 catalog 过长/混乱导致错误 Find。

允许做一个更紧凑但**机械产生**的 catalog representation。

不能用语义模型提前筛选正确 D。

---

## D. Unified Search implementation repair

仅当 audit 证明：

v3a Search 理论上命中 old doc，
但实现未返回新的 query-localized W。

允许修复 implementation bug。

不能改变 Retriever/localizer算法。

---

## E. Writer recovery focus

仅当：

```text
Evidence Visibility 高
但 Evidence→Claim conversion 明显低
```

允许一个非常窄的 Writer clarification：

“Current Recovery Need is now the active focus.”

不得扩大为 U2 式全 Original Question eager scan。

---

# 35. Exploration 限制

最多：

```text
12 cases
<=24 new Actor model calls
```

或等量小规模 Writer calls。

只能一轮。

禁止：

```text
U3
U4
多个 prompt sweep
新 State fields
新 Router
换模型
新 Retriever
新 memory tool
```

Exploration 不能覆盖 Primary result。

必须标：

```text
exploratory
```

如果探索有正信号：

只能建议 future fresh confirmation。

不能直接把 Primary gate 改成 PASS。

---

# 36. 最终报告必须回答

至少回答：

1. Deferred omission 有多少可以通过普通 Search 恢复？
2. Global Search 能否稳定重新发现 old source？
3. OldDocRecall@5 是多少？
4. Old Evidence Visibility@5 是多少？
5. Recovery 有多少来自旧 Source，有多少来自新 Source？
6. 当 Need 成为 Current Gap 后，U1 Writer 能否重新写入此前漏掉的事实？
7. Evidence→Claim conversion 是多少？
8. Global-only recovery success 是多少？
9. Hybrid recovery success 是多少？
10. Find/Open 增加了多少独有成功？
11. Local reuse 是否显著降低 cost/latency？
12. 是否出现 source lock-in？
13. 哪些 omission 是真正 Immediate Writer failure？
14. 哪些 omission 可以安全 deferred？
15. Belief conflict 是否应该成为 Immediate Admission exception？
16. Provenance-only update 是否不应计入 Claim Recall？
17. Global Rediscovery 是否足以支撑 aggressive selective admission？
18. Reference Harness 是否需要专门的 Recovery policy？
19. 是否仍需要区分 old/new source scope？
20. 下一步是否可以进入 cleaner State 下的 G4/G5 controller comparison？

---

# 37. 预注册解释

如果：

```text
G ≈ H
且两者 Recovery 高
```

优先选择：

\[
\boxed{
Global\ Rediscovery
}
\]

因为它控制逻辑更简单。

---

如果：

```text
H > G
```

且差距来自 Find 对明确旧 D 的稳定收益，

则保留：

\[
\boxed{
GlobalSearch + OpportunisticFind/Open
}
\]

但仍不增加 Harness Router。

---

如果：

```text
G低，H高
```

说明：

Global Rediscovery 的 Query/Retriever 不足以单独承担 Recovery，

Selective State 需要保留一定 known-source reuse 能力。

---

如果：

```text
G和H都低
```

先定位：

```text
Query
Retriever
Localization
Writer re-admission
```

哪一层失败。

不能简单回到：

```text
把更多事实永久写进Claims
```

---

如果：

```text
Evidence visibility高
但Claim recovery低
```

说明：

问题仍然在 Admission Writer，

不是 Retrieval Architecture。

---

如果：

```text
Global能够通过新Source解决Need
```

即使没找回 exact old Source，

也应算 Recovery 成功。

这会直接支持：

\[
Old/New\ source\ distinction
\]

在 runtime 中没有必要。

---

# 38. 本轮最核心的理论问题

最终不要只回答：

“Search 还是 Find 更好？”

真正的问题是：

\[
\boxed{
一个高压缩、有损的Persistent Research State，
能否依赖普通未来搜索恢复被暂时省略的信息？
}
\]

如果答案是 Yes：

我们可以接受：

```text
Immediate Claim Recall < 100%
```

因为真正需要的是：

\[
\boxed{
Eventual System Recall
}
\]

而不是：

\[
One-shot Writer Recall
\]

这将直接决定：

Research State 到底可以压缩到多小。

---

# 39. 实施顺序

严格按照：

1. fetch 最新远程；
2. 创建新 branch；
3. 阅读当前 v3.1 全部相关报告；
4. 写 DESIGN_AUDIT；
5. commit；
6. 构建并冻结 omission taxonomy；
7. 构建并冻结 Recovery Bank；
8. tool-level audit v3a old-doc relocalization；
9. freeze R1 paired requests；
10. 执行 G/H first decision；
11. review Evidence；
12. 用真实 prefix 继续 second decision；
13. U1 Writer re-admission；
14. final paired analysis；
15. 如未达门槛，只允许一次 bounded exploration；
16. final integrity；
17. FINAL_CONCLUSION.md；
18. push remote。

不要请求用户再次确认。

不要修改历史结果。

不要因为某个 case 漂亮就临时增加新机制。

让 Recovery 数据决定：

\[
Global\ Rediscovery
\]

是否真的足以支撑：

\[
Selective\ Minimal\ Research\ State.
\]