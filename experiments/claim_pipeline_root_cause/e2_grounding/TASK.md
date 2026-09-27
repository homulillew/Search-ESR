# Search-ESR — E2 Grounding Candidate-Anchoring Diagnostic

## 0. 研究目的

当前不要再修改 Reader。

最新完整 E1 已经得到：

```text
experiment/claim-pipeline-contract-rerun
343b5a3d2ff4e05ec04302be9eb35534b71b86a1
```

结论：

```text
H1: not supported
H2: not supported
H3: untested
```

当前 A0 Reader：

```text
23 raw candidates
22/23 source-supported
FSSR = 1/23 = 4.35%
GRSR = 18/20 = 90%
```

因此本任务不再试图让 Reader 达到 100% 正确。

研究问题改为：

\[
\boxed{
\textbf{当 Reader 偶尔提出 plausible-but-unsupported Candidate 时，
Grounding 能否可靠阻止它进入 C？}
}
\]

本任务只测试：

\[
\boxed{H3:\ Candidate\ framing\ causes\ admission\ anchoring}
\]

---

# 1. 当前 Grounding 的结构

当前 production-style Grounding：

\[
Candidate + RawEvidence
\rightarrow supported/insufficient
\]

问题是：

> Candidate 已经提供了一个 source interpretation。

Grounding 再读 raw Evidence 时，可能从：

> “Evidence 自己明确说了什么？”

变成：

> “Evidence 能不能被解释成 Candidate 所说的意思？”

因此待检验：

\[
\boxed{
P(FalseAdmit\mid CandidateVisible)
>
P(FalseAdmit\mid EvidenceFirst)
}
\]

---

# 2. 本任务不测试什么

禁止修改或重新研究：

```text
Reader
OneGap
C visibility in Reader
A0/A1/A2 construction
Actor
Search
Find
Open
H
Gain
Closure
Finalizer
Task Skeleton R
persistent state schema
```

禁止新增：

```text
TemporalScope
RelationGraph
SemanticPackage
SupportGraph
ClaimType
```

本实验只测试：

\[
Candidate + Evidence \rightarrow C
\]

这道 authority boundary。

---

# 3. 起始分支

执行前：

```bash
git fetch origin --prune
```

确认：

```text
experiment/claim-pipeline-contract-rerun
```

远程最新 HEAD。

当前预期：

```text
343b5a3d2ff4e05ec04302be9eb35534b71b86a1
```

如果已经前移：

先审计新增 commit。

不要静默基于旧 SHA 执行。

建议新分支：

```text
experiment/grounding-candidate-anchoring
```

---

# 4. 当前用户授权范围

用户已明确要求：

> 测一下 Grounding。

本消息视为对本 E2 diagnostic 的新明确授权。

允许：

```text
DeepSeek Flash paid semantic calls
```

本次上限：

\[
\boxed{85\ calls}
\]

授权仅包含：

```text
E2 Grounding diagnostic
semantic review
analysis
```

不包含：

```text
E3
H-confirmation
Recovery rollout
production runtime modification
new retrieval
benchmark run
```

不得把 E1 未使用预算挪到其他阶段。

---

# 5. Candidate Bank 必须来自真实现有输出

不要人工编新的 hard negatives。

使用：

1. contract-corrected E1 `run002` 已审阅 Candidate；
2. 原协议中冻结的 10 个 actual historical Reader candidates。

应用已有：

```python
freeze_e2_candidates(...)
```

规则。

不修改规则。

不制造：

```text
synthetic negative
q435 paraphrase variants
new temporal traps
new attribution traps
```

---

# 6. deterministic bank selection

按原协议：

每个 split：

```text
D
H_diagnostic
```

分别最多：

```text
15 supported positives
15 strengthened negatives
```

使用 deterministic ascending pair hash。

保留所有：

```text
origin
qid
split
Candidate
Evidence
source review label
ambiguity label
```

---

# 7. 当前预计 bank

重新机械计算，不能直接硬编码以下数字。

目前仓库离线估计：

| Split | Supported | Strengthened negative |
|---|---:|---:|
| D | 15 | 3 |
| H-diagnostic | 15 | 2 |
| Total | 30 | 5 |

预计：

\[
35\ candidate/evidence\ pairs
\]

和：

\[
15\ distinct\ Evidence\ inventories
\]

如果重新计算结果不同：

使用实际冻结结果并解释差异。

---

# 8. E2 必须有可识别机会，否则停止

必须保证：

```text
D:
>=1 supported
>=1 strengthened negative

H_diagnostic:
>=1 supported
>=1 strengthened negative
```

否则：

```text
E2_STOP_INSUFFICIENT_NEGATIVE_OPPORTUNITY
```

不要补造 negatives。

---

# 9. 两个 Grounding arms

## G0 — Current Grounding

必须使用当前原始 Grounding prompt **byte-identical**：

```text
experiments/claim_pipeline_root_cause/prompts/g0_current_grounding.txt
```

内容保持不变，包括历史 baseline 中已经存在的 concrete examples。

不要删除。

不要增加新例子。

输入：

```json
{
  "candidate": {...},
  "Evidence": [...]
}
```

输出：

```json
{
  "verdict": "supported|insufficient",
  "reason": "..."
}
```

---

# 10. G0 的研究含义

G0 测：

\[
Candidate + RawEvidence
\rightarrow verdict
\]

Candidate 在 Grounding 阅读 Evidence **之前已经可见**。

这是 current baseline。

---

# 11. G1 — Evidence-First Grounding

G1 分成两步。

## Step 1：Source Commitment Inventory

输入只有：

```text
full public Evidence
visible source metadata
```

明确禁止：

```text
Candidate
OneGap
C
Q
R
H
Trace
evaluation labels
historical answer
future evidence
```

输出：

```text
0–32 minimal source commitments
```

使用现有：

```text
g1_evidence_inventory.txt
```

不要改 prompt。

---

# 12. G1 Inventory Prompt 保持 generic

当前 prompt：

```text
List the minimal factual commitments explicitly supported by the supplied full evidence and visible source metadata.
Preserve subjects, relations, scope, attribution, conditions and modality.
Do not introduce commitments using background knowledge.
Do not make a task-directed summary or guess a candidate claim.
...
```

保持 byte-identical。

禁止加入：

```text
67 albums
2016
memo date
letter date
Arinimaal
Rehbar
```

等实际 case。

---

# 13. Inventory schema

Inventory Claim refs 必须继续使用 contract-rerun 的 public W# rule。

Semantic Evidence 中不得出现：

```text
source_window_ref
docid
hash
offset
end_char
```

Inventory output：

```text
evidence_refs
```

只能引用当前 request 可见：

```text
W#
```

最好使用 request-specific dynamic enum。

并继续 runtime membership check。

不得 alias mapping。

---

# 14. 每份 Evidence 只构建一次 inventory

对完全相同：

```text
Evidence
model
prompt
schema
config
```

只调用一次：

\[
Evidence\rightarrow Inventory
\]

多个 Candidate 使用同一 Evidence 时复用 frozen inventory。

但是只允许在**本 E2 stage 内**复用。

不要复用旧 stage 的 inventory。

---

# 15. 先生成 Inventory，再做 Coverage

这一顺序必须物理保证。

不能：

```text
看了 Candidate
→ 再生成 inventory
```

Inventory request 在构造时不得包含 Candidate ID 或 Candidate text。

Harness private metadata 可以记录 linked pair IDs。

但 model input 不能看到。

---

# 16. Step 2：Candidate Coverage

输入：

```json
{
  "candidate": {...},
  "SourceCommitmentInventory": {...}
}
```

不提供：

```text
raw Evidence
Gap
C
Q
R
H
```

使用现有：

```text
g1_candidate_coverage.txt
```

保持 byte-identical。

核心判断：

> Candidate 的全部 factual commitment 是否已经由预先冻结的 source commitments 覆盖？

---

# 17. G1 的因果结构

G0：

\[
Candidate+Evidence\rightarrow verdict
\]

G1：

\[
Evidence\rightarrow Inventory
\]

先完成。

然后：

\[
Candidate+FrozenInventory\rightarrow verdict
\]

因此 Candidate 无法影响：

\[
Evidence\rightarrow SourceInterpretation
\]

这才是真正测试 Candidate anchoring。

---

# 18. 不能把 G1 理解成新的“更聪明 Verifier”

G1 改变的是：

\[
\boxed{\text{information order / visibility}}
\]

不是模型。

不是 temperature。

不是 reasoning budget。

不是专门增加 semantic rules。

如果 G1 更好，只能说：

> evidence-first commitment separation 有机制信号。

不能说：

> 已经证明 LLM 心理意义上的 anchoring。

---

# 19. Same-model control

所有 calls 使用和 E1 相同：

```text
provider: DeepSeek
model: deepseek-flash
temperature: 0
thinking: enabled
reasoning_effort: high
max_tokens: 32768
stream: false
max_retries: 0
```

不得：

```text
换模型
best-of
majority vote
retry
temperature sampling
```

---

# 20. Call budget

根据当前估计：

### G0

\[
35
\]

### G1 inventory

\[
15
\]

### G1 coverage

\[
35
\]

总计：

\[
\boxed{85}
\]

执行前必须根据冻结 candidate bank 重算 exact count。

如果不是 85：

记录真实值。

但：

\[
\boxed{不得超过85}
\]

---

# 21. 并发策略

第一批独立：

```text
35 G0
+
15 Inventory
=
50
```

可并行。

Coverage 必须等待对应 Inventory 成功。

建议最大 pool：

```text
70
```

但实际 initial concurrency 不超过：

```text
50
```

不做额外付费 load test。

---

# 22. Failure Policy

任何：

```text
transport failure
schema failure
ref failure
model mismatch
finish failure
parse failure
inventory contract failure
```

发生：

1. halt 未发送请求；
2. in-flight 允许完成；
3. 全部保留；
4. 0 retry；
5. 0 replacement；
6. 0 output repair；
7. 0 resume。

如果产生 selective missingness：

\[
H3=\text{inconclusive}
\]

不要只分析 surviving pairs。

---

# 23. Ground Truth 只使用冻结 source-relative labels

Candidate truth 标签：

```text
source_supported
semantic_strengthening
ambiguous_relation
```

必须来自 E1 已冻结 reviewer labels / historical frozen reviews。

不要重新根据 G0/G1 输出修改 truth label。

不要看最终 benchmark answer。

不要看 future evidence。

---

# 24. Primary negative

Primary negative 定义：

```text
source_supported = false
semantic_strengthening = true
```

不是：

```text
“最终答案其实可能是假的”
```

也不是：

```text
“这句话不相关”
```

研究的是：

\[
\boxed{
source-relative unsupported strengthening
}
\]

---

# 25. Primary positive

Positive：

```text
source_supported = true
```

Grounding 不需要 Candidate 对 Gap useful。

Grounding只判断：

> source 是否支持。

因此：

```text
irrelevant but source-supported claim
```

在 Grounding 任务里仍然是 positive。

不要把 relevance 混进去。

---

# 26. Primary Metrics

## G0 False Admit Rate

\[
FAR_{G0}
=
\frac{unsupported\ strengthened\ candidates\ admitted}
{all\ unsupported\ strengthened\ candidates}
\]

---

## G1 False Admit Rate

\[
FAR_{G1}
\]

同样定义。

---

## True Positive Admit Recall

\[
TPR=
\frac{supported\ candidates\ admitted}
{all\ supported\ candidates}
\]

分别统计 G0/G1。

---

# 27. Candidate Anchoring Rescue

定义：

```text
Gold = unsupported strengthening
G0 = supported
G1 = insufficient
```

统计：

\[
RescueCount
\]

每个 rescue 必须保存：

```text
Candidate
Evidence
Inventory
G0 reason
G1 reason
qid
relation family
ambiguity
```

---

# 28. Harm case

也必须统计：

```text
Gold = source-supported
G0 = supported
G1 = insufficient
```

即：

\[
\boxed{
G1\ recall\ damage
}
\]

不能只看 rescue。

---

# 29. Inventory 自己必须单独审查

G1 不是免费正确。

Inventory 可能：

- omission；
- strengthening；
- attribution loss；
- relation loss；
- modality loss。

因此对每个 inventory fact 标：

```text
source_supported: bool
```

并记录：

```text
omitted_observed_commitments
```

---

# 30. Inventory review 不能被 Candidate 污染

审查某 inventory 时只看：

```text
Evidence
Inventory
```

不要显示 linked Candidate。

否则 reviewer 又会被 Candidate framing。

---

# 31. H3 冻结 Gate

保持原 gate：

\[
\boxed{
FAR\ relative\ reduction \ge 50\%
}
\]

同时：

\[
\boxed{
G1\ TPR \ge 85\%
}
\]

并要求：

```text
beneficial paired direction
beneficial qid-weighted direction
H_diagnostic strict same error-reduction direction
H_diagnostic TPR guard
```

不得降低门槛。

---

# 32. 特殊情况：G0 没有 false admit

如果：

\[
FAR_{G0}=0
\]

不能说：

> Current Grounding 已证明完美。

只能：

```text
H3_INCONCLUSIVE_NO_BASELINE_FALSE_ADMISSION
```

因为没有 anchoring opportunity。

此时不要执行 E3。

---

# 33. 特殊情况：G1 全拒绝

例如：

\[
FAR_{G1}=0
\]

但：

\[
TPR_{G1}=30\%
\]

不能通过。

这是：

\[
\boxed{
universal conservatism
}
\]

不是可靠 Grounding。

---

# 34. 特殊情况：Inventory 本身不可靠

如果 inventory 出现明显：

```text
unsupported facts
systematic source commitments omission
attribution stripping
```

必须单独报告。

若严重到 G1 verdict 无法解释：

H3 不通过或标为 inconclusive。

不要把 inventory bottleneck 当成 Grounding 胜利。

---

# 35. Ambiguous stratum 单独报告

当前 negatives 高度集中于 ambiguous cases。

至少单独报告：

```text
all negatives FAR
ambiguous-only FAR
nonambiguous FAR
```

如果 nonambiguous denominator 为 0：

明确写：

```text
undefined
```

不要声称跨全部 relation 类型泛化。

---

# 36. q435 / q673 的用途

可以作为 mechanism trace。

但不能成为 gate。

特别观察：

### q435

Candidate：

```text
67 albums at/by 2016 Forbes feature
```

问题：

```text
temporal binding
```

### q673

问题：

```text
attribution/modality scope
```

分析：

> G0 为什么支持/拒绝？

> G1 Inventory 是否保留 source attribution？

> Coverage 如何判断？

但：

```text
q435 PASS
```

绝不等于 H3 PASS。

---

# 37. 不允许增加新 Grounding rules

不要因为看到 q435 就新增：

```text
Do not infer dates from adjacent clauses
```

不要因为 q673 新增：

```text
Preserve quoted authorship claims
```

G0 必须 byte-identical。

G1 也保持现有 generic prompt。

本轮测架构，不调 prompt。

---

# 38. 不允许第三个 verifier

禁止：

```text
G0
→ G1
→ Temporal Auditor
→ Attribution Auditor
```

本实验只比较：

```text
candidate-visible verification
```

和：

```text
evidence-first commitment separation
```

。

---

# 39. 不修改 Reader

尤其禁止看到某个 negative 后：

```text
回头修 A0 Reader
```

Reader 在本实验完全冻结。

Candidate 是实验输入。

---

# 40. 不执行 H-confirmation

当前：

```text
H_confirmation
```

继续密封。

E2 只使用：

```text
D
H_diagnostic
```

。

不因为 H3 结果好看就提前打开 confirmation。

---

# 41. 不执行 E3

即使 H3 PASS：

本任务也必须：

```text
STOP_AFTER_E2
```

输出：

```text
E2_GROUNDING_CONCLUSION.md
E3_RECOMMENDATION.md
```

不得发送 E3 calls。

---

# 42. 建议文件结构

```text
experiments/claim_pipeline_root_cause/e2_grounding/
    DESIGN_AUDIT.md
    PROTOCOL.md
    CANDIDATE_BANK.json
    BANK_FREEZE.json
    CALL_ESTIMATE.json
    EXECUTION_PREFLIGHT.json

    run001/
        calls/
        inventories/
        RESULTS.json
        TRANSPORT_SUMMARY.json

    review/
        inventory_source/
        inventory_labels.json
        E2_METRICS.json
        ERROR_CATALOG.json

    E2_GROUNDING_CONCLUSION.md
    E3_RECOMMENDATION.md
```

---

# 43. Commit discipline

建议：

### Commit 1

```text
Freeze actual E2 Grounding bank and candidate-anchoring protocol
```

---

### Commit 2

```text
Validate evidence-first Grounding contracts and execution freeze
```

---

### Commit 3

```text
Record authorized E2 Grounding candidate-anchoring run
```

---

### Commit 4

```text
Review Grounding admission behavior and report H3 evidence
```

不要 squash。

---

# 44. 执行前必须输出 exact freeze

至少记录：

```text
source HEAD
candidate pair hashes
Evidence hashes
split
qid
positive/negative counts
distinct inventories
G0 prompt hash
G1 prompt hashes
schema hashes
model config
exact call count
failure policy
H3 thresholds
authorization provenance
```

freeze 后不得修改。

---

# 45. 最终必须回答的问题

1. 最终 E2 bank 有多少 pairs？
2. D/H-diagnostic 各有多少 positive/negative？
3. negatives 来自多少 qids？
4. negatives 覆盖哪些 strengthening family？
5. distinct Evidence 数是多少？
6. 实际 call 数是多少？
7. contract failures 是否为 0？
8. G0 FAR 是多少？
9. G1 FAR 是多少？
10. G0 TPR 是多少？
11. G1 TPR 是多少？
12. FAR relative reduction 是多少？
13. paired direction 是否改善？
14. qid-weighted direction 是否改善？
15. H-diagnostic 是否同方向？
16. H3 full gate 是否通过？
17. G0 是否再次 false-admit q435？
18. G1 是否拒绝 q435？
19. q673 在 G0/G1 中如何？
20. Inventory 是否保留 attribution/modality？
21. Inventory 有多少 unsupported facts？
22. 有多少 Evidence 出现 material omissions？
23. G1 的 improvement 是否只是 universal rejection？
24. 有多少 CandidateAnchoringRescue？
25. 有多少 G1 recall-harm cases？
26. ambiguous-only FAR 是多少？
27. nonambiguous FAR 是否有 denominator？
28. 是否有证据支持 Candidate framing 是真实 admission risk？
29. 是否有证据支持正式改变 Grounding？
30. 是否应该进入 E3？
31. 是否执行了 E3？必须回答 No。
32. 是否修改了 production？必须回答 No。

---

# 46. Root-cause Decision

## 情况 A

若：

```text
G0 FAR > 0
G1 FAR relative reduction >= 50%
G1 TPR >= 85%
paired/qid direction beneficial
H_diagnostic same direction
```

则：

\[
\boxed{H3\ supported}
\]

结论只能写：

> evidence-first commitment separation reduces false admission on this frozen diagnostic bank.

不要写：

> Grounding problem solved.

---

## 情况 B

如果：

```text
G0 FAR = 0
```

则：

\[
\boxed{H3\ inconclusive}
\]

说明当前样本没有触发 baseline anchoring error。

---

## 情况 C

如果：

```text
G1 FAR improves
but TPR < 85%
```

则：

\[
\boxed{H3\ intervention\ fails}
\]

原因：

> improvement purchased by excessive conservatism / inventory bottleneck.

---

## 情况 D

如果：

```text
G1 FAR ~= G0 FAR
```

则：

\[
\boxed{H3\ not\ supported}
\]

不要再加 verifier。

---

# 47. 无论结果如何都停止 Grounding micro-tuning

这是本任务非常重要的停止规则。

完成 E2 后：

不要自动提出：

```text
G2
G3
relation auditor
temporal auditor
multi-agent voting
```

。

如果 H3 PASS：

下一步是考虑一次 integrated diagnostic / small E2E。

如果 H3 FAIL：

接受：

> strict natural-language entailment 有 residual noise。

然后考虑以整个 end-to-end system 观察实际 False C rate。

不要无限继续拆 verifier。

---

# 48. 本实验真正要验证的东西

不是：

> 哪个 prompt 更严格？

而是：

\[
\boxed{
\textbf{
Grounding 在看到 Candidate 之前先独立确定 source commitments，
是否能降低 plausible semantic strengthening 的 false admission，
同时不破坏正常 Claim 的 admission recall。
}
}
\]

这才是 H3。

---

# 49. 架构原则

Reader 是 proposal layer：

\[
Reader\rightarrow Candidate
\]

允许偶尔出错。

Grounding 是 authority layer：

\[
Grounding\rightarrow C
\]

所以我们真正要求的不是：

\[
P(ReaderError)=0
\]

而是：

\[
\boxed{
P(FalseC\mid ReaderError)\text{ 足够低}
}
\]

本实验直接测这一点。

---

# 50. 最终停止位置

本任务完成：

```text
E2 bank freeze
→ G0/G1 execution
→ inventory review
→ H3 metrics
→ conclusion
```

以后立即停止。

不要：

```text
E3
Recovery
H-confirmation
production patch
benchmark
```

等待新的明确用户决策。