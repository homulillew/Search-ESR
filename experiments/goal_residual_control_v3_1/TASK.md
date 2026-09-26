你现在负责继续 Search-ESR 的 Research State / Harness 实验。

仓库：

https://github.com/homulillew/Search-ESR

---

# 0. 当前研究位置

本轮必须首先理解：我们不是重新设计 Harness，也不是重新研究 Search/Find。

当前已经完成：

`experiment/goal-residual-control-contract-v2-executed`

并得到 G1→G5 完整实验。

随后：

`experiment/goal-residual-control-v3-admission-structured`

尝试同时修复两个已知问题：

1. Online State Updater 不知道产生 Observation 的 Current Actor Gap，导致 Claim admission 退化为 source fact extraction；
2. DeepSeek 自由文本输出后再 JSON validate，仍存在少量纯 serialization failure。

v3 在 DeepSeek exact-schema capability gate 停止，没有运行 Admission Replay、G4 或 G5。

本轮不是继续研究 DeepSeek 是否完整实现 Draft JSON Schema。

本轮研究目标是：

**恢复已经有历史实验支持的 Goal-conditioned Claim Admission，然后重新验证在线 Research State 与 L0/L1/L2 controller。**

---

# 1. 首先读取并理解这些历史材料

必须先读取，不得根据文件名猜结论：

## 最新 v3

- `experiments/goal_residual_control_v3/V3_DESIGN_AUDIT.md`
- `experiments/goal_residual_control_v3/FINAL_CONCLUSION.md`
- `experiments/goal_residual_control_v3/structured_output_preflight/CAPABILITY_REPORT.md`
- `experiments/goal_residual_control_v3/structured_output_preflight/CAPABILITY_METRICS.json`

## 完整 v2

- `experiments/goal_residual_control/FINAL_CONCLUSION_V2.md`
- `experiments/goal_residual_control/SCORING_ERRATA_V2.md`
- `experiments/goal_residual_control/research_decision_v2/RESULTS.md`
- `experiments/goal_residual_control/one_step_acquisition_v2/RESULTS.md`
- `experiments/goal_residual_control/transition_replan_v2/RESULTS.md`
- `experiments/goal_residual_control/three_round_loop_v2/RESULTS.md`
- `experiments/goal_residual_control/three_round_loop_v2/EXECUTION_NOTES.md`
- `experiments/goal_residual_control/harness_v2/state_updater.md`
- `experiments/goal_residual_control/harness_v2/research_actor.md`
- `experiments/goal_residual_control/harness_v2/adaptive.py`

## 前序 Claim Admission 实验

- `experiments/gap_evidence_claim_loop/FINAL_CONCLUSION.md`
- `experiments/gap_evidence_claim_loop/single_gap_rollout/RESULTS.md`
- `experiments/minimal_research_loop/FINAL_CONCLUSION.md`
- `experiments/minimal_research_loop/prompts/reader.md`

必须明确写入设计文档：

历史实验已经得到：

- Observation-only 会抽取大量来源中真实、但与当前 Active Gap 无关的信息；
- Gap-conditioned extraction 大幅减少 irrelevant facts；
- Source-supported 并不是一个事实值得进入 Persistent Research State 的充分条件；
- Existing Claims 对 novelty / duplicate control 有价值；
- 最新 v2 删除 persistent Gap 时，同时让 State Updater 不再看到 Current Gap，这是旧 failure 回归的重要原因。

本轮不是重新证明“相关性很重要”这个概念。

本轮要验证：

**历史局部 Gap-conditioned admission 机制，在真实 online Observation 分布和完整闭环里是否仍然成立。**

---

# 2. 创建新分支，不覆盖 v3

先：

```bash
git fetch --all --prune
```

确认最新远程：

`origin/experiment/goal-residual-control-v3-admission-structured`

记录准确 HEAD。

从它创建新分支。

建议：

`experiment/goal-residual-control-v3-admission-replay`

如果远程已有同名分支，创建带明确后缀的新分支。

禁止：

- force push；
- overwrite；
- rebase 历史实验；
- 修改任何 v1/v2/v3 raw artifact。

新目录：

`experiments/goal_residual_control_v3_1/`

历史目录全部视为 read-only evidence。

---

# 3. 本轮核心研究问题

本轮只研究两个层次。

## RQ-A：Belief Formation

给定：

- Original Question
- Existing Claims
- Working Hypothesis
- Current Actor Gap
- Current Observation

Agent 能否只持久化：

**可靠、当前决策相关、新颖、保留正确作用域的认知？**

核心链：

```text
Observation
    ↓
Claim Admission
    ↓
Persistent Belief
```

而不是：

```text
Observation
    ↓
Extract every true fact
    ↓
State bloat
```

---

## RQ-B：Controller

只有 Cleaner Online State 被验证后，才重新比较：

```text
L0 = Persistent/Cached Gap
L1 = Direct Replan from Current Belief
L2 = Derived Goal Residual
```

本轮不得预设 L2 应该获胜。

---

# 4. 本轮不允许改的东西

以下全部冻结：

- 模型：`deepseek-flash`
- provider/account
- Retriever
- Search
- Find
- Open
- window locator
- corpus/index
- Workspace 表示
- D#/W# 语义
- Original Question
- Claim persistent schema
- Working Hypothesis persistent schema
- 每 Observation 最多 2 条 Claim 的 Harness rule
- 每 Decision 最多 2 个独立 action 的 Harness rule
- G4 历史 transition cohort
- G5 原 10 qids
- G5 最多 3 个 decisions
- L2 batch-boundary Goal Review scheduling
- closure rubric
- q435 strict sensitivity
- source pool
- Progress rubric
- no retry
- no best-of
- no model-output repair
- failure preservation

禁止新增：

- Confidence
- Claim Graph
- Conflict Graph
- TestCard
- Persistent Frontier
- Hypothesis Set
- Verifier node
- Query optimizer
- Retrieval router
- 新 Planner
- 额外 State 字段

遇到新 failure：

**记录，不扩 schema。**

---

# 5. DeepSeek structured output：重新定义职责边界

当前 v3 证明的是：

DeepSeek hosted API 没有提供我们要求的“完整 JSON Schema language enforcement”。

尤其是 provider 不支持或不能可靠 enforce 某些完整 Draft Schema 约束。

这不再作为主实验 hard gate。

但是仍必须尽量使用 DeepSeek 能稳定支持的 constrained structured output 来保证：

- JSON 结构；
- required fields；
- primitive field type；
- enum；
- closed object；
- Search / Find / Open 不同字段形状；
- extra property rejection。

Harness 继续负责：

- `len(actions) <= 2`
- `len(claims_to_add) <= 2`
- STOP/ACT 跨字段一致性
- set/keep/clear 跨字段一致性
- D#/W# 是否真实存在
- 两 action 是否独立
- budget
- semantic support
- relevance
- closure

不要重新设计 fixed action slots。

保留自然内部形式：

```json
{
  "decision": "act",
  "gap": "...",
  "actions": [...]
}
```

和：

```json
{
  "claims_to_add": [...],
  "hypothesis_update": {
    "action": "keep",
    "statement": ""
  }
}
```

---

# 6. DeepSeek transport schema

优先继续使用 Responses API structured output。

但 transport schema 必须编译为 provider 支持的形式。

## Actor

顶层必须是：

```text
type = object
```

不能再用：

```text
root oneOf
root anyOf
```

顶层字段：

```text
decision
gap
actions
```

`decision`：

```text
enum = ["stop", "act"]
```

`gap`：

```text
string
```

`actions`：

```text
array
```

不要在 server schema 中要求 `minItems/maxItems`。

这些由 Harness deterministic validation。

`actions.items` 应尽可能使用 nested `anyOf`：

```text
Search object
Find object
Open object
```

每种 tool object：

- 明确 `tool` singleton enum；
- required fields；
- `additionalProperties=false`。

目标是保证：

Find branch 中不能合法出现 Search 的 `k`。

如果 DeepSeek 对 nested action `anyOf` 仍拒绝或不能稳定约束，记录并进入 fallback，不继续无限探测 provider。

---

## State Updater

保持：

```text
claims_to_add: array[string]

hypothesis_update:
    action: enum["keep","set","clear"]
    statement: string
```

Server 不负责 `maxItems=2`。

Harness 检查：

```text
len(claims_to_add) <= 2
```

以及：

```text
action=set → statement non-empty
keep/clear → 按既有 invariant 检查
```

---

## Goal Reviewer

保持：

```text
resolved: boolean
residual: string
```

Harness 检查：

```text
resolved iff residual empty
```

---

# 7. 只做一次 Production-shape Transport Canary

禁止再做：

- impossible schema；
- minItems > maxItems；
- provider JSON Schema conformance benchmark；
- 大量 capability probe；
- fixed-slot workaround。

新建：

`structured_transport_canary/`

选择约 24 个真实历史 request：

覆盖：

- Actor STOP
- Actor Search
- Actor Find
- Actor Open
- two-action
- Updater keep
- Updater set
- Updater clear
- Goal resolved
- Goal unresolved

使用真实 production prompts/context。

重点检查：

### Structural validity

- valid JSON
- required fields
- field type
- enum
- tool branch shape
- no extra fields
- no Find+k
- no Search missing k

### Harness validity

另外单独记录：

- action 数量
- claim 数量
- D/W registry
- STOP/ACT consistency
- hypothesis consistency

不能把两者混成一个“schema valid”。

---

# 8. Canary 的决定规则

如果 production-shape constrained output 能稳定解决真实 serialization shape：

继续使用它。

不要要求 DeepSeek 完整实现所有 JSON Schema keyword。

如果仍然明显失败，例如：

- nested tool branch 不能表达；
- provider 经常返回 extra fields；
- Find/Search shape 仍明显混乱；

停止继续研究 structured output。

直接 fallback 到：

```text
Chat Completions
+ JSON mode
+ 原严格 Harness validator
```

并记录：

```text
transport_mode = json_mode_fallback
```

这不是最终生产 Harness 的理想约束实现，只是为了不让一个低比例基础设施问题继续阻塞本轮 Claim Admission 研究。

**无论 Canary 哪种结果，都不得因为它再次停止 Admission Replay。**

除非 API 根本无法返回可解析 JSON。

---

# 9. Admission Replay 是本轮第一核心实验

不要先跑 G4/G5。

从 v2 G5：

`three_round_loop_v2`

中的真实 Updater events 建立冻结 Admission Bank。

目标约 60 packets：

10 个 qid × 尽量 6 packets。

每个 packet 必须来自一个真实 Observation，并保留当时：

- Original Question
- pre-update Claims
- pre-update Working Hypothesis
- exact Observation
- exact source/window provenance
- 产生 Observation 的 Actor decision
- **该 decision 的 Current Actor Gap**

Current Gap 必须来自真实历史 Actor output。

不能：

- 用后续 Gap；
- 用 Goal Reviewer 后验 residual；
- 用人工重写 Gap；
- 根据 gold answer 修改 Gap。

同一个 Actor decision 的两个 independent actions 及其返回 windows，共享该 decision 的 Current Gap。

---

# 10. Admission Bank 的覆盖

使用现有 v2 review label 只用于确定性 stratified sampling 和 evaluation，不进入 model input。

尽量覆盖：

- incidental admission
- useful fact missed
- material qualifier omission
- hypothesis contradiction
- correct hypothesis rejection
- weak candidate promotion
- multi-fact page
- useful positive admission
- Observation 应该产生 no state change
- source-supported but task-irrelevant fact
- candidate evidence
- final-relation evidence

选择规则、hash ordering、qid cluster 在调用前冻结。

不能看到 U1 输出以后重新选择样本。

---

# 11. Admission Replay 必须有三个条件

这是本轮非常关键的因果设计。

## U0 — Archived v2

完全使用历史 v2 Updater output。

零新模型调用。

它代表：

```text
旧 semantic prompt
+
旧 Chat Completion/free generation
+
No Current Gap
```

---

## Uc — Transport Control

使用：

- 与 v2 byte-equivalent 的 State Updater semantic instruction；
- 不提供 Current Gap；
- 使用本轮选定的 structured/JSON transport。

也就是说：

```text
旧语义
+
新 transport
```

U0 vs Uc 用于估计：

**API/transport 改变本身带来的行为差异。**

必须覆盖完整 Admission Bank，不只抽一个小 subset，除非成本/接口硬失败使完整调用不可能。

---

## U1 — Goal-conditioned Admission

使用：

```text
Question
+ Existing Claims
+ Working Hypothesis
+ Current Actor Gap
+ Observation
```

和新的 Admission Prompt。

Transport 与 Uc 完全相同。

因此真正核心因果比较是：

```text
U1 vs Uc
```

而不是：

```text
U1 vs U0
```

U0 是历史参照。

Uc 控制 API/structured-output surface change。

---

# 12. U1 State Updater Prompt

使用下面的语义作为主 Prompt。

不要额外加入 planner、reviewer 或 confidence。

---

You are updating the persistent Research Belief State from exactly one observed source.

The persistent semantic state contains:

1. Verified Claims:
   grounded factual beliefs that are worth retaining for future research decisions.

2. Working Hypothesis:
   a provisional candidate or interpretation that may guide exploration,
   but is not treated as verified fact and cannot by itself close the Original Question.

You are given:

- the Original Question,
- Existing Verified Claims,
- the current Working Hypothesis,
- the Current Research Gap that caused this Observation to be acquired,
- exactly one Observation.

The Current Research Gap is temporary decision context.
It is NOT evidence and must NOT be copied into persistent state.

Your job is NOT to summarize the source.

Your job is to decide whether this Observation contains new information that deserves to become durable research belief.

A new Verified Claim may be admitted only when ALL of the following are true:

1. SOURCE SUPPORT  
   The current Observation itself directly supports the statement.

2. NOVELTY  
   The information is not already adequately represented by Existing Verified Claims.

3. DECISION RELEVANCE  
   Retaining the fact would materially improve future research on the Original Question.

A fact is decision-relevant when it does at least one of the following:

- directly reduces the Current Research Gap;
- establishes another still-unresolved requirement of the Original Question;
- materially supports the current Working Hypothesis on a requirement that matters;
- materially contradicts the current Working Hypothesis;
- shows that the current research direction is wrong or stale;
- would materially change which candidate, relation, source, or question should be investigated next.

Do NOT persist a fact merely because:

- it is true;
- it appears in the source;
- it is about the same person, team, film, game, article, company, or topic;
- it is interesting background information;
- it might vaguely be useful someday;
- it restates information already present in Existing Claims.

If the Observation contains no new decision-relevant grounded fact, return no new Claims.

Empty admission is correct and expected.

Preserve the exact semantic scope supported by the Observation.

Do not:

- attach a date from one relation to another relation;
- turn an article date into an event date;
- turn a retrospective quantity into a quantity reported at an earlier event;
- join two independently true statements into a stronger unsupported relation;
- drop a material year, source, quantity, identity, ordering, or relationship qualifier;
- infer a full candidate identity from partial clue agreement.

The Original Question and Current Research Gap define relevance.
They are NOT evidence.

The model's previous query or action is NOT evidence.

Candidate handling:

If the Observation only makes a candidate more plausible:

- add only the directly supported factual Claim(s);
- optionally set or retain the candidate as Working Hypothesis.

Do NOT create a Verified Claim saying that the candidate is the answer unless the available grounded evidence actually establishes that task-level identification.

If the Observation materially contradicts the current Working Hypothesis:

- retain the directly supported contradictory fact when it is decision-relevant;
- clear the Working Hypothesis.

If the Observation directly supplies the requested final relation:

- admit that exact relation with its necessary scope.

Propose at most 2 new Verified Claims.

Do not output:

- Goal Residual;
- next Gap;
- query;
- plan;
- D#/W#/offset;
- source IDs;
- explanation outside the required object.

Return only the required structured object.

---

# 13. U1 评价不能只看 source precision

v2 已经有接近 100% source-supported precision。

所以本轮 Admission evaluation 至少需要下面这些维度：

## A. Source Support Precision

Claim 是否被当前 Observation 直接支持。

---

## B. Decision-Relevant Admission Precision

所有 admitted Claims 中：

真正值得长期保存的比例。

定义不能是 topic relevance。

必须能够说明：

该 Claim 如何影响 Original Question / Current Gap / Hypothesis / next decision。

---

## C. Novelty Precision

是否只是已有 Claim 的重复或语义改写。

---

## D. Useful Fact / Admission Recall

对每个 packet，在调用前冻结：

```text
decision-relevant factual atoms visible in this Observation
```

然后计算：

```text
被 Claim 或正确 Hypothesis update 捕获的比例
```

不能为了提高 precision，把 State Writer 训练成永远输出空。

---

## E. Scope Preservation

检查：

- year
- date
- source relation
- quantity relation
- subject/object identity
- event binding
- sequence/order

有没有损失。

---

## F. Hypothesis Control

分别记录：

- correct set
- correct keep
- correct clear
- missed clear
- spurious clear
- contradicted candidate reintroduced
- weak candidate overcommit

---

## G. No-change correctness

Observation 没有值得持久化的事实时：

```text
claims_to_add=[]
```

是否正确。

---

# 14. Admission 主要比较

主比较：

```text
U1 vs Uc
```

辅助比较：

```text
Uc vs U0
U1 vs U0
```

重点回答：

```text
Current Gap conditioning
```

到底减少了多少：

```text
source-supported but decision-irrelevant admission
```

以及有没有损害：

```text
useful fact recall
```

---

# 15. Admission Gate

Gate 不允许只用一个漂亮的 absolute threshold。

必须综合 paired 结果。

进入 G4 至少需要：

- U1 的 incidental / irrelevant admission 相比 Uc 明显下降；
- Source Support 不出现实质恶化；
- Useful Fact Recall 不出现明显下降；
- qualifier/scope preservation 不恶化；
- Hypothesis control 不恶化；
- no-change 行为更加合理或至少不更差。

如果 U1 只是：

```text
写得更少
```

但：

```text
关键事实也大量漏掉
```

则 FAIL。

如果 FAIL：

停止进入 G4/G5。

分析 Admission 边界为什么失败。

禁止通过新增更多持久 State 字段救实验。

---

# 16. 必须单独计算 Counterfactual State Growth

使用 U0/Uc/U1 输出，在相同 pre-state 上机械构造 counterfactual post-state。

测量：

- new claims per Observation
- State mutation rate
- semantic characters
- relevant state characters
- incidental state characters
- no-change update rate

这是局部 replay，不声称等同于完整 rollout。

目的：

回答 v2 的 State bloat 有多少来自 goal-blind admission。

---

# 17. Stage B：G4 v3.1

Admission Gate 通过后才运行。

使用原 20 个 transition。

关键是 Current Gap provenance。

对于每个 transition：

优先寻找：

**真正产生这些 historical Observation 的 Actor Gap。**

必须建立：

```text
transition_id
→ source observation
→ producing decision
→ exact current gap
```

如果某个 historical transition 没有可恢复的 exact generating gap：

不能人工猜一个。

允许使用明确标记的：

```text
historical normalized focus
```

但必须与 exact Actor Gap 分开报告。

如果可追溯的 transition 太少，要在结果中限制结论，不得制造数据。

---

# 18. G4 重新比较

保持：

```text
R0 = cleaner online post-state + historical persisted gap
R1 = cleaner online post-state only
R2 = frozen oracle post-state + residual
R3 = cleaner online post-state + residual
```

其中 R0/R1/R3 使用同一个 U1 Writer。

R2 仍然是 oracle comparator。

重点不是先宣布谁赢。

重点看：

```text
Online State → Oracle State gap
```

是否缩小。

测量：

- source-supported Claims
- decision-relevant Claims
- useful fact recall
- incidental admission
- qualifier omission
- state growth
- correct hypothesis rejection
- rejected-path continuation
- premature STOP
- correct STOP
- Evidence Progress
- tool cost

---

# 19. G4 最重要的机制问题

必须回答：

1. Cleaner Updater 是否把 Observation 中真正有用的信息更稳定地写入 State？
2. Cleaner Updater 是否减少 State bloat？
3. R3 是否比 v2 更接近 R2？
4. correct hypothesis clear 后，Actor 是否还继续研究被否定 candidate？
5. Residual 是否仍会因为错误 Claim 而被错误缩窄？
6. source-visible closure 和 claim-visible closure 的差距是否缩小？

---

# 20. Stage C：G5 v3.1

G4 没有暴露严重完整性问题后进入。

继续原 10 qid。

不换 cohort。

比较：

```text
L0 Persistent/Cached Gap
L1 State-only Direct Replan
L2 Derived Goal Residual
```

---

# 21. 三个 arm 必须共享同一个 State Writer

这是硬要求。

不管 L0/L1/L2：

每次 Actor `decision=act` 都产生：

```text
Current Actor Gap
```

本 decision 获取的所有 Observation 都使用这个 Gap 作为 Updater 临时条件。

即：

```text
Actor
  ↓
CurrentGap + Actions
  ↓
Observation(s)
  ↓
Updater(Q, Claims, Hypothesis, CurrentGap, Observation)
```

Update 完成后：

- Claims/Hypothesis 持久化；
- Current Gap 本身不因 State Update 自动持久化。

只有：

### L0

将 Actor Gap 作为下一轮 prior/persisted focus 保存。

### L1

下一轮不继承 authoritative Gap。

### L2

下一轮不继承 authoritative Gap，而是从 Q+Claims 重新 Goal Review。

这样 State Writer 对三个 arm 完全一致。

---

# 22. 不改变 L2 scheduling

为了与 v2 可比：

仍然保持：

```text
tool batch
→ sequential Observation updates
→ batch-boundary Goal Review
```

不要这次顺手改成 per-window Review。

这仍然记录为 known limitation。

如果 cleaner admission 导致：

```text
fewer state mutations
```

那么 Goal Reviewer 调用减少应被视为真实机制结果。

---

# 23. G5 核心指标

继续报告：

- Original Goal Resolution
- Correct STOP
- Premature STOP
- Late research
- Goal drift
- Evidence Progress
- NoProgress decisions
- Tool calls
- Search/Find/Open
- token cost
- interface failure
- horizon exhausted

另外必须新增或重点报告：

## Admission

- total admitted Claims
- decision-relevant Claims
- incidental Claims
- missed useful atoms
- qualifier omissions
- unsupported joins

## State Growth

- claim count by round
- state characters by round
- useful/relevant state density
- state mutation count
- no-change updates

## Evidence → Belief

- useful fact visible in Workspace
- useful fact admitted to State
- source-visible resolution
- claim-visible resolution
- source-visible minus claim-visible gap

## Hypothesis

- set
- retain
- reject
- reintroduction after rejection
- Actor continues rejected path

## Recovery

- wrong candidate recovery
- wrong direction recovery
- stale focus continuation
- alternative candidate exploration

---

# 24. 特别关注 v2 已经发现的 case

至少重新检查：

## q580

此前关键 five-season evidence 已经存在于 Workspace，但没有进入 Claims。

观察 v3.1 是否：

```text
Observation
→ relevant Claim
→ correct closure
```

---

## q435

关注：

- May 2017 relation
- album count
- retrospective count
- source/date binding

防止重新出现 temporal join。

---

## q517

关注：

- candidate identity
- Goat zodiac
- 1978 birthday conflict
- premature closure

---

## q311

关注：

- runtime 等已经观察到但被遗漏的关键事实
- title/director/writer facts
- Updater 是否只保留有控制价值的信息

---

## q1094

关注：

- weak candidate replacement
- speculative fixture
- candidate churn
- contradiction-driven rejection

这些是 diagnostic cases，不允许针对它们单独改 prompt。

---

# 25. 结果解释提前冻结

## 情况 A

Cleaner State 明显改善，但：

```text
L0 ≈ L1 ≈ L2
```

结论：

Controller representation 不是当前主要瓶颈。

优先考虑简单 L1。

Residual 保留为 diagnostic / stopping comparator。

---

## 情况 B

L2：

```text
premature stop ↓
```

但：

```text
resolution ≈
evidence progress ≈
```

结论：

Goal Residual 主要提供 closure/stopping value，而不是 acquisition/control advantage。

未来可研究 conditional Goal Review，而不是 mandatory per-round node。

---

## 情况 C

```text
L1 ≈ L2 > L0
```

才支持：

Persistent/Cached Gap 存在有害路径惯性。

---

## 情况 D

```text
L0 ≈ or > L1/L2
```

必须放弃：

```text
Persistent Gap 本身有害
```

这一强假设。

更合理结论可能是：

Gap 可以作为 cached prior focus，
只要它不能覆盖 Original Question 和 current grounded belief。

---

## 情况 E

三个 arm 都相对 v2 大幅改善。

首先归因于：

```text
Goal-conditioned Admission
```

这个共同 substrate 修复。

不能宣布某个 controller 因此获胜。

---

## 情况 F

Cleaner State 后仍然整体 resolution 很低。

才把下一 dominant failure 转向：

- candidate control
- source selection
- query formation
- retrieval/localization

不能再次通过增加 State schema 救实验。

---

# 26. DeepSeek 接口错误怎么计

必须把 failure 分类：

```text
transport_structural_failure
harness_control_violation
semantic_failure
provider/API failure
length/incomplete failure
tool failure
```

不能再把它们统称为：

```text
invalid
```

例如：

### Transport structural

- malformed JSON
- missing required field
- wrong type
- wrong enum
- illegal tool field

### Harness control

- 3 actions
- 3 Claims
- unknown D/W
- dependent Search→Find batch
- STOP 携带动作
- set hypothesis with empty statement

### Semantic

- wrong STOP
- irrelevant Claim
- unsupported Claim
- bad candidate
- bad query

这样即使 DeepSeek constrained output 不完美，也不会污染我们对研究 failure 的理解。

---

# 27. 冻结与执行规则

每个 live stage 必须：

1. 先 commit protocol / prompt / schema / selection / code；
2. 记录 HEAD；
3. freeze exact requests 或 deterministic request builder；
4. 检查历史 protected hashes；
5. 再调用模型；
6. zero retry；
7. 不 repair；
8. 不重新采样失败；
9. raw request/response 全部保存；
10. 后验人工 review 与生产路径隔离。

如果模型/工具 failure：

保留在 planned denominator。

不能“补跑一个替代样本”。

---

# 28. 推荐目录

```text
experiments/goal_residual_control_v3_1/
    README.md
    HYPOTHESES.md
    PROTOCOL.md
    PROTOCOL_AMENDMENT.md
    FROZEN_STATE.md
    FINAL_CONCLUSION.md

    prompts/
        state_updater_v2_control.md
        state_updater_gap_conditioned.md

    schemas/
        actor_transport.json
        updater_transport.json
        goal_transport.json

    structured_transport_canary/
        PROTOCOL.md
        freeze.json
        requests.json
        events.jsonl
        outputs.json
        RESULTS.md

    admission_replay/
        PROTOCOL.md
        BANK.json
        GOLD_ADMISSION_ATOMS.json
        freeze.json
        U0_ARCHIVED.json
        Uc_events.jsonl
        Uc_outputs.json
        U1_events.jsonl
        U1_outputs.json
        REVIEWS.json
        metrics.json
        RESULTS.md

    transition_replan/
        ...

    three_round_loop/
        ...

    analysis/
        ...
```

---

# 29. 第一批代码修改前必须先写设计审计

先创建：

`experiments/goal_residual_control_v3_1/DESIGN_AUDIT.md`

内容必须回答：

1. 为什么 v3 停止？
2. 为什么不继续研究完整 JSON Schema conformance？
3. DeepSeek constrained output 本轮负责什么？
4. Harness validation 负责什么？
5. 为什么仍保留自然 `actions[]`，不使用 fixed slots？
6. 为什么 `Current Actor Gap` 是 ephemeral conditioning，而不是重新引入 persistent Gap？
7. 哪些历史实验已经支持 Gap-conditioned admission？
8. 为什么 Uc 是必要的？
9. Admission Bank 如何从真实 G5 Observation 恢复 Current Gap？
10. 哪些变量从 v2 完全冻结？
11. 什么条件下 Admission Replay 才允许进入 G4？
12. 什么情况下本轮必须停止？

写完并 commit 后再实施。

---

# 30. 不要再次在 capability 上陷入无限循环

Structured transport 最多做：

```text
一次 production-shape schema implementation
+
一次冻结 canary
```

如果 provider 仍然不能稳定支持：

记录。

使用：

```text
JSON mode + strict deterministic Harness validator
```

继续 Admission Replay。

不要：

- 换模型；
- 关 thinking；
- fixed slots；
- invent another API encoding；
- 继续 20 个 capability probes；
- 再把 Admission 实验停掉。

本轮 Research Question 是 Claim Admission，不是 DeepSeek API compliance。

---

# 31. 最终必须回答的问题

最终报告至少明确回答：

1. DeepSeek production-shape constrained transport 实际可用到什么程度？
2. 剩余 structural failure rate 是多少？
3. Uc 相比 U0 是否说明 API/transport surface 改变了语义行为？
4. U1 相比 Uc，incidental admission 降了多少？
5. Useful Fact Recall 是否保持？
6. Scope/qualifier retention 是否改善？
7. No-change rate 是否提高？
8. State Growth 是否降低？
9. q580 类 Workspace→Claim 漏失是否减少？
10. Online State 与 Oracle State 差距是否缩小？
11. Hypothesis contradiction 是否更稳定改变下一行动？
12. G4 Evidence Progress 是否变化？
13. L0/L1/L2 Original Goal Resolution 分别是多少？
14. L0/L1/L2 premature stop 分别是多少？
15. L0/L1/L2 State Growth 分别是多少？
16. L2 的 Goal Reviewer 调用是否因 cleaner semantic mutations 而下降？
17. Goal Residual 是否仍主要是 stopping signal？
18. Persistent Gap 是否终于表现出有害性？
19. Direct Replan 是否已经足够？
20. 当前最小语义 State 是否仍有理由保持：
   `Committed Claims + Working Hypothesis`？
21. 如果仍失败，新的 dominant failure 到底位于：
   Admission、Candidate Control、Actor、Search、Retriever 还是 Localizer？

---

# 32. 本轮最重要的研究原则

不要为了证明 Goal Residual 而运行实验。

不要为了证明 Minimal State 而运行实验。

不要为了证明 Persistent Gap 有害而运行实验。

目标是让数据决定：

```text
Observation
    ↓
Selective Belief Formation
    ↓
Current Belief
    ↓
Research Control
```

到底哪一环真正限制 BC+ 长程 Agent Search。

当前优先假设只是：

```text
source-supported
≠
state-worthy
```

以及：

```text
Gap 不需要持久化
≠
Gap 不应该参与 State Admission
```

本轮首先验证这个区别。

---

现在开始。

第一步：

1. fetch 最新远程；
2. 确认 v3 最新 HEAD；
3. 创建新分支；
4. 完整阅读指定历史材料；
5. 写 `DESIGN_AUDIT.md`；
6. commit；
7. 才开始 production-shape structured transport canary；
8. 无论 constrained transport 最终是否完美，只要 API 可正常返回 JSON，就继续 Admission Replay；
9. Admission Gate 通过后才执行 G4；
10. G4 没有严重完整性问题后才执行 G5。

不要请求用户再次确认。
不要在后台等待。
按阶段完成、保存、提交并报告真实结果。