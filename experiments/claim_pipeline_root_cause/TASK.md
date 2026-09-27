# Search-ESR — Claim Pipeline Root-Cause Ablation

## 0. 本任务的研究目的

当前不要修 q435。

不要写：

```text
Be careful with temporal relations.
Do not infer album count from nearby dates.
```

不要把：

```text
67 albums
Forbes 2016
```

作为 prompt example。

本任务的目标不是让 q435 通过。

目标是验证一个更一般的结构性假说：

> 当前 Gap-conditioned Claim pipeline 为什么会把 source 中已经存在的局部事实，强化成 source 未明确承担的关系？

当前最新研究主线基于：

```text
experiment/recoverable-loop-h-continuation
dadf69f1c5fb96491f4fd3a34e0ece3418878de3
```

执行前重新：

```bash
git fetch origin --prune
```

确认远程 HEAD。

如果该分支已经前移，先审计新增 commit，不得静默使用旧 SHA。

建议新分支：

```text
experiment/claim-pipeline-root-cause
```

---

# 1. 现有结论：哪些东西已经不是本任务要重新验证的

不要重新质疑以下已经有较强实验依据的设计。

## 1.1 Claim selection 应该看 Gap / OneGap

历史 `gap-evidence-claim-loop`：

Observation-only：

```text
67 / 110 findings Gap-irrelevant
```

Gap-conditioned：

```text
1 / 46 Gap-irrelevant
```

Gap + existing Claims：

```text
0 / 38 Gap-irrelevant
```

因此保留：

\[
\boxed{
OneGap + C + Observation
\rightarrow
selective factual processing
}
\]

不要退回：

```text
Observation → enumerate facts
```

---

## 1.2 Existing C 对 novelty / dedup 有价值

已有实验显示：

```text
Gap + C
```

能减少 duplicate findings。

因此不能简单删除 C。

真正的问题是：

> C 应该在哪个阶段可见？

而不是：

> C 是否应该存在？

---

## 1.3 Candidate proposal 和 authoritative C mutation 必须分权

历史已经反复证明：

```text
model proposes a fact
```

不能直接：

```text
write C
```

因此仍然需要某种：

```text
proposal / extraction
→ epistemic admission
```

权限边界。

本任务不是把 Reader 和 Grounding 直接合并。

---

# 2. 当前重复出现的 failure mechanism

同一种错误至少已经在：

```text
gap-evidence-claim-loop F3
```

和：

```text
recoverable-loop H2
```

独立出现。

抽象形式：

Evidence 明确表达：

\[
A
\]

和：

\[
B
\]

Current Gap 需要：

\[
R(A,B)
\]

Reader 生成：

\[
R(A,B)
\]

Grounding 接受：

\[
R(A,B)
\]

最后：

\[
R(A,B)\rightarrow C
\]

但 source 实际没有明确承担这个关系。

这种错误可能表现为：

```text
temporal binding
identity binding
source/document binding
cross-entity relation
qualifier inheritance
conjunction completion
role binding
attribution/modality strengthening
```

不要把这些分别当作八个独立 prompt bug。

本任务测试它们是否共享一个结构性根因：

\[
\boxed{
Goal-conditioned semantic strengthening
}
\]

---

# 3. 三个待检验的根因假说

## H1 — C-visible Novelty Pressure

当前 Reader 看：

```text
OneGap
C
Observation
```

并被要求输出：

```text
NEW
Gap-useful
nonduplicate
Claim
```

如果 Observation 中的直接事实已经在 C 中，

模型为了产生：

```text
NEW + useful
```

可能倾向于合成一个 C 中没有的新关系。

例如抽象地：

\[
C=\{A,B\}
\]

而 Gap 需要：

\[
R(A,B)
\]

于是生成：

\[
R(A,B)
\]

H1：

\[
\boxed{
C\text{ 在 Claim formulation 阶段可见，会增加 unsupported relation synthesis。}
}
\]

注意：

> 如果 H1 成立，不代表 Selector 不应该看 C。

只意味着：

> C 的 novelty 信息不应该直接参与事实句子的自由生成。

---

## H2 — Relevance / Formulation Coupling

当前 Reader 同时负责：

### relevance

> 什么与 OneGap 有关？

以及：

### formulation

> 事实应该被写成什么 Claim？

H2：

\[
\boxed{
\text{让 Gap 同时参与 evidence selection 和 semantic formulation，
会增加 task-shaped semantic strengthening。}
}
\]

换句话说：

\[
Gap\rightarrow relevance
\]

是有用的。

但：

\[
Gap\rightarrow ClaimSentenceForm
\]

可能是危险的。

---

## H3 — Candidate Anchoring in Grounding

当前 Grounding 输入：

```text
CandidateClaim
Evidence
```

Candidate 已经提供一种解释。

Grounding 很可能从：

> Evidence 自己明确说了什么？

变成：

> Evidence 能不能被解释成这个 Candidate？

H3：

\[
\boxed{
\text{Candidate framing 会提高 ambiguous strengthened claims 的 false-admit rate。}
}
\]

---

# 4. 本任务不得预设 H1/H2/H3 正确

实验必须允许得到：

```text
H1 unsupported
H2 unsupported
H3 unsupported
```

如果消融不能支持这些机制：

不要修改生产 runtime。

不要为了使理论成立继续 patch prompt。

---

# 5. 研究阶段设计

整个实验分成：

```text
E0  Source/Bank Audit
E1  Claim Construction Ablation
E2  Grounding Anchoring Ablation
E3  Integrated Confirmation
```

E3 只有在 E1/E2 至少出现明确机制信号后才能执行。

---

# 6. E0 — 构建跨关系类型的自然 Evidence Bank

不要围绕 q435 建 bank。

从仓库历史真实 artifacts 中机械筛选：

```text
gap-evidence-claim-loop
research-state-v2
minimal-recoverable-loop
claim-requirement-support-alignment
contextual-subtraction-qualification
minimal-semantic-package
recoverable-loop-clean
recoverable-loop-h-continuation
```

优先使用：

```text
real observed W
real source metadata
real historical Candidate/Claim
real prefix C
real Gap/OneGap
```

不要改 source text。

---

# 7. Bank 必须同时包含正例和 relation traps

至少覆盖六类，不足则明确报告：

```text
temporal binding
identity / entity binding
source / document relation
cross-entity relation
qualifier / quantifier
conjunction / sequence
attribution / modality
role relation
```

不要求强行凑齐不存在的类别。

---

# 8. Primary Natural Bank 最低规模

目标：

```text
36–48 packets
>= 12 qids
<= 2 packets / qid
>= 6 semantic relation families
```

包含：

### Positive packets

source 明确支持完整关系。

### Ambiguous / negative packets

source 包含相关实体/事实，但不明确支持目标 relation。

### Duplicate/no-new-fact packets

Observation 与当前 Gap 有关，但没有超出 C 的新 source-supported fact。

这一类非常重要。

---

# 9. 不要只选历史 known bad cases

Bank 分两部分：

## D — Diagnostic Historical

允许包含已经分析过的 cases。

用途：

> 看实验是否能捕获已知 mechanism。

---

## H — Held-out Archived

从尚未用于本 root-cause 设计的 archived observations 中按机械规则选择。

要求：

```text
>= 12 packets
>= 6 qids
```

选择完成后先冻结。

不得看到新 arm 输出后再替换。

---

# 10. Bank selection 必须在模型调用前冻结

建议用 deterministic procedure：

```text
candidate inventory
→ eligibility filter
→ qid cap
→ relation-family stratification
→ deterministic hash ordering
→ D/H assignment
```

避免人为挑：

> 最适合当前理论的案例。

---

# 11. Bank review 不使用最终答案 Gold

Source-support 判断只使用：

```text
exact Observation
source metadata visible at that point
```

不要用：

```text
later evidence
future windows
final historical answer
gold answer
```

因为研究目标是：

\[
Evidence\rightarrow Claim
\]

而不是最终答案正确性。

---

# 12. 冻结 review rubric

每个生成的 Candidate Claim 后续人工/离线 reviewer 只标：

```text
source_supported
semantic_strengthening
strengthening_type
gap_relevant
duplicate_with_C
gap_useful_if_supported
```

其中：

## semantic_strengthening

定义为：

> Candidate 引入 Evidence 本身没有明确承担的新 subject/object/relation/time/quantity/modality/condition/identity commitment。

不要因为 Candidate “听起来合理”就算 supported。

---

# 13. E1 — Claim Construction Root-Cause Ablation

E1 专门研究：

> unsupported strengthening 是在哪里生成的？

E1 不研究 Closure。

不研究 Actor。

不研究 Search/Find/Open。

每个 packet 固定：

```text
OneGap
C
Observation
```

不同 arm 只改变 Claim construction information flow。

---

# 14. E1-A0 — Current Fused Reader

保持当前 production Reader **完全不改 prompt**。

输入：

\[
OneGap+C+Observation
\]

输出：

\[
0\text{–}3\ CandidateClaims
\]

这是 Baseline。

不得针对历史失败补 prompt。

---

# 15. E1-A1 — Remove C from Formulation

输入：

\[
OneGap+Observation
\]

Reader 仍然直接写 CandidateClaims。

关键变化只有：

```text
C 不再进入生成阶段
```

不得额外增加 semantic safety rule。

Candidate 生成完以后：

```text
Harness deterministic/human dedup against C
```

也就是说：

\[
C
\]

从：

```text
generation context
```

移到：

```text
post-generation novelty filter
```

---

# 16. A0 vs A1 测试 H1

如果：

\[
FalseStrengthening(A1)
<
FalseStrengthening(A0)
\]

同时：

\[
GapRelevantSupportedRecall
\]

没有明显崩溃，

则支持：

\[
\boxed{
C-visible novelty pressure
}
\]

是根因之一。

如果没有改善：

不要继续宣称 novelty pressure 是根因。

---

# 17. E1-A2 — Hard-Separated Selection / Formulation

这是最重要的 arm。

分两步。

---

## A2-Step1 — Gap-conditioned Evidence Selector

输入：

\[
OneGap+C+Observation
\]

但禁止输出 Claim。

只允许输出：

```text
0–3 evidence selections
```

例如 schema：

```json
{
  "selections": [
    {
      "window_ref": "W3",
      "reason": "brief relevance reason"
    }
  ]
}
```

如果可以用 deterministic source span：

优先由 Harness 保存 exact span/offset。

不要要求模型复制长 quote。

Selector 只回答：

> 哪个已观察 Evidence 值得继续进入 Claim pipeline？

它不能回答：

> 这个 Evidence 证明了什么具体 relation？

---

# 18. A2-Step2 — Evidence-only Claim Formulator

输入只包含：

```text
selected full Evidence
source metadata
```

不包含：

```text
OneGap
Q
R
C
H
Trace
Selector reason
historical answer
```

输出：

```text
0–3 minimal source-entailed factual claims
```

Prompt 必须 generic。

不得出现：

```text
Euler
memo
letter
q435
albums
SPS
DLC
teammates
```

等历史 case example。

---

# 19. A2 的关键原则

A2 真正把：

\[
Gap\rightarrow relevance
\]

和：

\[
Evidence\rightarrow factual formulation
\]

放到不同信息域。

这不是 Observation-only Writer。

因为第一步仍然是：

\[
OneGap+C+Observation
\rightarrow Selection
\]

所以 Gap relevance 不会被放弃。

---

# 20. E1 Primary Metrics

分别对 raw Candidate 层统计：

## False Semantic Strengthening Rate

\[
FSSR=
\frac{\text{unsupported strengthened candidates}}
{\text{all factual candidates}}
\]

---

## Source-Supported Precision

\[
SSP=
\frac{\text{source-supported candidates}}
{\text{all candidates}}
\]

---

## Gap-Relevant Supported Recall

对于 frozen packet 中 Observation 确实包含的 Gap-useful supported atoms：

\[
GRSR
\]

---

## Correct Silence

对于：

```text
relevant evidence but no new supported fact
```

packet：

是否正确输出：

```text
[]
```

---

## Claim Bloat

每 packet Candidate 数。

---

# 21. E1 的因果判断

### 支持 H1

若 A1 相对 A0：

```text
FSSR 明显下降
```

而：

```text
GRSR 下降 <= 10 percentage points
```

。

---

### 支持 H2

若 A2 相对 A1：

```text
FSSR 再明显下降
```

且：

```text
Gap relevance / useful recall 没有明显崩溃
```

。

建议“明显下降”预注册为：

```text
>=30% relative reduction
```

并报告：

```text
paired packet changes
qid-clustered direction
```

不要只报 aggregate percentage。

---

# 22. 不用一次实验宣称总体规律

这些是机制诊断。

必须同时报告：

```text
Diagnostic bank
Held-out archived bank
```

如果只在已知 historical failure bank 上改善，

而 held-out 没有同方向，

不能称为 root cause confirmed。

---

# 23. E2 — Candidate Anchoring Ablation

E2 只研究：

\[
Grounding
\]

为什么会放过 Reader 的 strengthening。

---

# 24. 构建 E2 Candidate Bank

不要新造只针对 q435 的 negatives。

使用：

```text
E1 A0/A1/A2 实际生成的 Candidate
```

再加入：

```text
历史真实 supported Candidate
历史真实 unsupported Candidate
```

机械去重后形成 frozen candidate/evidence pairs。

要求正负都存在。

---

# 25. E2-G0 — Current Grounding

保持 production Grounding 不改。

输入：

```text
Candidate
Evidence
```

输出：

```text
supported / insufficient
```

。

---

# 26. E2-G1 — Evidence-first Grounding

不要先给 Candidate。

第一步：

\[
Evidence
\rightarrow
SourceCommitmentInventory
\]

输入只有：

```text
full Evidence
source metadata
```

输出：

```json
{
  "facts": [
    {
      "statement": "...",
      "evidence_refs": ["W3"]
    }
  ]
}
```

要求：

> 只列 source 自身可以安全承担的最小事实 commitment。

不看 Gap。

不看 C。

不看 Candidate。

---

# 27. G1 第二步 — Candidate Coverage

随后单独判断：

```text
Candidate
SourceCommitmentInventory
```

但**不给 raw Evidence**。

问：

> Candidate 是否完全包含在这些已经提前生成的 source commitments 中？

输出：

```text
supported / insufficient
```

这样 Candidate 不能再诱导模型重新解释 raw source。

---

# 28. 为什么 G1 能测试 Candidate Anchoring

G0：

\[
Candidate+RawEvidence
\rightarrow verdict
\]

Candidate 可以改变 raw text 的阅读方式。

G1：

先：

\[
RawEvidence
\rightarrow commitments
\]

此时 Candidate 不可见。

然后：

\[
Candidate+FrozenCommitments
\rightarrow coverage
\]

因此如果：

\[
FalseAdmit(G1)
<
FalseAdmit(G0)
\]

说明：

\[
\boxed{
Candidate anchoring
}
\]

确实是当前 Grounding failure 的重要来源之一。

---

# 29. E2 Metrics

重点：

## False Admit Rate

只看 frozen unsupported-strengthening candidates：

\[
FAR
\]

---

## True Positive Admit Recall

只看 source-explicit supported Candidates：

\[
TPR
\]

---

## Ambiguous Relation Admit Rate

单独报告 ambiguous cases。

---

## Candidate Anchoring Rescue

原本：

```text
G0 = supported
Gold/source review = insufficient
```

而：

```text
G1 = insufficient
```

的数量。

---

# 30. H3 Gate

支持 Candidate Anchoring 假说的预注册条件建议：

```text
false-admit relative reduction >= 50%
```

同时：

```text
true-positive admit recall >= 85%
```

如果 G1 只是：

> 什么都拒绝，

不能算成功。

---

# 31. E3 — Integrated Root-Cause Confirmation

只有以下至少一个成立：

```text
H1 supported
H2 supported
H3 supported
```

才进入 E3。

否则停止。

---

# 32. E3 不跑 full Research Loop

只跑 Claim pipeline。

比较：

## Current

```text
OneGap + C + Observation
→ current Reader
→ current Grounding
→ candidate C
```

和：

## Root-cause-repaired

如果 H2/H3 被支持，则例如：

```text
OneGap + C + Observation
→ Evidence Selector
→ Evidence-only Claim Formulator
→ evidence-first admission
→ deterministic dedup
→ candidate C
```

具体采用哪些组件必须由 E1/E2 结果决定。

不要提前固定。

---

# 33. E3 必须用 Held-out Bank

不要用：

```text
q435
Euler
memo/letter
```

等作为唯一验证。

使用 E0 中冻结的 held-out archived packets。

如果 held-out bank 太小：

停止并报告：

```text
INSUFFICIENT_HELDOUT_BANK
```

不要补挑漂亮样本。

---

# 34. E3 Gate

最高优先级：

\[
FalseAuthoritativeClaim
\]

目标：

```text
0 observed false authoritative C
```

同时避免 trivial empty system。

建议最低：

```text
source-supported precision >= 95%
gap-useful supported recall >= 80%
correct-silence >= 80%
```

样本很小时只作为扩展 Gate，不声称总体置信率。

---

# 35. 一个特别重要的实验约束：不要改生产 Runtime

E0/E1/E2 阶段：

禁止修改：

```text
llm_chat/recoverable_loop/engine.py
llm_chat/recoverable_loop/state.py
Search/Find/Open
Actor
H
Closure
Finalizer
```

只允许在：

```text
experiments/claim_pipeline_root_cause/
```

建立独立 diagnostic harness。

原因：

> 本任务首先是验证根因，不是实现我们喜欢的方案。

---

# 36. Prompt 不得包含历史 case-specific 规则

实验 prompt 禁止出现：

```text
memo date is not letter date
patient nationality is not publication country
Euler biography...
67 albums...
SPS...
DLC...
teammate...
```

否则又变成 prompt patch。

Prompt 只允许抽象职责描述。

例如：

```text
Do not introduce factual commitments that are not explicitly supported by the supplied evidence.
```

这种 generic rule 可以存在。

---

# 37. 不允许 semantic tuning

一旦：

```text
bank
prompts
schemas
rubric
arm definitions
```

冻结并 commit，

开始 semantic calls 后不得：

```text
rewrite prompt
add examples
change thresholds
drop hard cases
retry
best-of
replace sample
```

Schema/transport bug 如果出现：

保留并停止相应 gate。

不得把 semantic fix 冒充 engineering fix。

---

# 38. 使用同一模型，避免模型能力 confound

第一轮所有 arm 使用完全相同：

```text
provider
model
thinking mode
temperature
token cap
```

建议继续当前：

```text
DeepSeek Flash
temperature 0
thinking enabled/high
max_retries 0
```

具体参数读取当前 frozen config，并重新 freeze。

不要同时换模型。

否则不能归因于信息流。

---

# 39. 必须保存 raw reasoning/output

每次 call 保存：

```text
request
response
reasoning content
usage
latency
request hash
source hashes
arm
packet ID
```

Reviewer packet 去掉：

```text
arm name
hypothesis name
```

尽量盲评。

---

# 40. Review 纪律

Reviewer 只能看到：

```text
Observation
Candidate
必要的 C/Gap（仅用于 relevance/duplicate 标签）
```

判断 source support 时：

必须屏蔽：

```text
final historical answer
future evidence
later windows
other arm output
```

---

# 41. 不要只报告最终 C precision

必须分别定位：

```text
Reader generated strengthening?
Grounding accepted strengthening?
```

也就是分别报告：

\[
P(ReaderStrengthening)
\]

以及：

\[
P(FalseAdmit\mid StrengthenedCandidate)
\]

否则仍然不知道 failure 在哪一层。

---

# 42. Root-Cause Decision Table

最终结论必须按如下逻辑：

### A1 改善，A2 无额外改善

说明：

```text
主要根因 = C-visible novelty pressure
```

---

### A1 无改善，A2 明显改善

说明：

```text
主要根因 = Gap-conditioned semantic formulation coupling
```

---

### A0/A1/A2 都相似，但 G1 改善

说明：

```text
主要根因 = admission candidate anchoring
```

---

### A2 + G1 才明显改善

说明：

```text
两个 mechanism 存在 interaction
```

---

### 全部无改善

则：

```text
当前 root-cause hypothesis rejected
```

下一研究问题应转向：

> evidence-only natural-language entailment 本身是否不可靠。

不要继续 patch。

---

# 43. q435 应该怎么使用

q435 可以进入：

```text
Diagnostic Historical Bank
```

作为 sanity check。

但：

```text
q435 PASS
```

绝对不能作为实验成功条件。

成功必须来自：

```text
cross-relation
multi-qid
held-out direction
```

。

---

# 44. 不要新增 Persistent State

无论结果如何，本实验禁止新增：

```text
TemporalScope
RelationType
ClaimGraph
SupportGraph
SemanticPackage
CoverageMask
Residual
Target
```

这是 Claim pipeline 机制实验。

不是 State schema 实验。

---

# 45. 不要立即修改 Grounding Prompt

尤其不要因为某个 false admission：

```text
add another negative example
```

先完成 E1/E2。

如果结构性假说成立：

优先改信息流。

只有证明：

```text
same information flow
but generic instruction is the actual missing factor
```

后才讨论 prompt。

---

# 46. 关于 Gain

本任务不要同时修改：

```text
new H → Gain
```

问题。

Gain misclassification 是另一个已知 issue。

但与 False C admission 不同。

本轮只研究 Claim pipeline。

否则无法归因。

---

# 47. 关于 Local Navigation

Find/Open yield 低的问题也暂不修改。

所有 E1/E2 packet 使用冻结 Observation。

不执行新 retrieval。

这样：

\[
RetrievalQuality
\]

不会混入：

\[
ClaimAdmissionQuality
\]

。

---

# 48. 建议目录

```text
experiments/claim_pipeline_root_cause/
    DESIGN_AUDIT.md
    HYPOTHESES.md
    PROTOCOL.md
    BANK_PROTOCOL.md
    REVIEW_RUBRIC.md
    CALL_ESTIMATE.json

    bank/
        inventory.json
        diagnostic.json
        heldout.json
        manifest.json

    prompts/
        a0_current_reader.txt
        a1_no_c_reader.txt
        a2_selector.txt
        a2_evidence_formulator.txt
        g0_current_grounding.txt
        g1_evidence_inventory.txt
        g1_candidate_coverage.txt

    schemas/
    tests/
    e1/
    e2/
    e3/
```

---

# 49. Git commit discipline

建议：

### Commit 1

```text
Audit repeated Claim-strengthening failures and preregister root-cause hypotheses
```

只写 Audit/Hypotheses。

---

### Commit 2

```text
Freeze cross-relation Claim pipeline bank and blinded review protocol
```

冻结 bank。

---

### Commit 3

```text
Implement Claim construction and grounding ablation harness with offline contract tests
```

只实现 diagnostic harness。

---

之后停止。

---

# 50. 未经新授权禁止付费调用

本任务当前允许：

```text
repository audit
bank construction
historical artifact extraction
offline tests
freeze
call estimate
```

不要执行：

```text
DeepSeek API
OpenAI API
new semantic calls
```

即使仓库历史里存在 standing authorization，本任务也必须等待当前用户对这次实验的新授权。

完成上述准备后输出：

```text
READY_FOR_AUTHORIZATION.md
CALL_ESTIMATE.json
```

并停止。

---

# 51. CALL_ESTIMATE 必须分阶段

分别估算：

```text
E1 calls
E2 calls
E3 conditional calls
```

不要把 conditional E3 当成一定会发生。

建议控制：

```text
E1 <= ~150 semantic calls
E2 <= ~180 semantic calls
```

具体值按最终 packet 数和 candidate 数机械计算。

不允许为了用满预算而补调用。

---

# 52. 实验成功并不等于马上换 Runtime

如果 E1/E2 支持 H1/H2/H3：

先提交：

```text
ROOT_CAUSE_CONCLUSION.md
```

明确：

```text
what mechanism was supported
what mechanism was rejected
effect on held-out packets
recall cost
known limitations
```

然后另开实现任务。

不要在同一个实验 branch：

```text
observe result
→ patch production
→ rerun
```

。

---

# 53. 最终必须回答的问题

1. 当前 false Claim strengthening 是否在多个 relation 类型复现？
2. 它是否集中于 Gap-relevant relation completion？
3. C 在 generation context 中是否增加 strengthening？
4. 把 C 移到 post-generation dedup 后是否改善？
5. Gap-conditioned selection 是否仍然保持 relevance？
6. Gap 从 Claim formulation 中移除是否减少 strengthening？
7. A2 是否重新产生 Observation-only Claim bloat？
8. Correct Silence 是否提高？
9. Candidate anchoring 是否显著提高 Grounding false-admit？
10. Evidence-first grounding 是否只是更保守、导致 recall collapse？
11. 哪个 mechanism 在 held-out bank 上仍有同方向信号？
12. 是否存在 interaction？
13. 是否需要改变正式 Reader？
14. 是否需要改变正式 Grounding？
15. 是否有任何证据支持新增 persistent semantic state？
16. 是否值得继续完整 Recovery rollout？
17. 当前 root-cause hypothesis 应接受、部分接受还是拒绝？

---

# 54. 本任务最重要的科研纪律

不要做：

```text
failure case
→ add prompt rule
→ rerun same failure
→ declare solved
```

必须做：

\[
\boxed{
Failure
\rightarrow
mechanism hypothesis
\rightarrow
cross-case causal ablation
\rightarrow
held-out confirmation
\rightarrow
architecture change
}
\]

---

# 55. 最终希望验证的不是 q435

我们真正想知道：

\[
\boxed{
\textbf{
当前 False C 是否主要来自：
Gap/C 参与 Claim sentence 生成所造成的 semantic strengthening，
以及 Candidate 对后续 Grounding 的 anchoring。
}
}
\]

如果是：

修信息流。

如果不是：

推翻这个解释。

不要继续围绕历史样本写规则。

---

# 56. 当前阶段的停止条件

在以下任一情况发生时停止：

```text
bank 无法满足多 qid / 多 relation-family 要求
held-out bank 太小
source provenance 无法完整恢复
schema/transport contract 存在歧义
review rubric 无法冻结
```

不要用更多模型调用弥补实验设计问题。

---

# 57. 最终研究原则

这次实验要真正检验：

\[
\boxed{
OneGap\rightarrow Relevance
}
\]

是否可以和：

\[
\boxed{
Evidence\rightarrow Truth
}
\]

在**信息流层面**分离，

而不仅仅是在 prompt 里告诉模型：

> “Gap is not evidence.”

如果 hard separation 能跨 relation 类型降低 false strengthening，同时保留 Gap usefulness：

这才是值得修改 Runtime 的根因级证据。