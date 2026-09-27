# Search-ESR — Claim Pipeline Root-Cause E1 Contract Repair & Full Rerun

## 0. 任务定位

本任务不是修改 Claim semantics。

不是修 q435。

不是增加 temporal / relation / identity 等 prompt 规则。

不是重新设计 Reader/Grounding。

本任务只解决上一轮 `claim-pipeline-root-cause` E1 暴露的一个机械接口问题：

\[
\boxed{
\text{model-public W\# identity}
\neq
\text{harness-internal source-window identity}
}
\]

然后在**完全不改变原 E1 语义实验设计**的前提下，从头完整重跑 E1。

---

# 1. 起始远程状态

执行前：

```bash
git fetch origin --prune
```

确认远程：

```text
experiment/claim-pipeline-root-cause
```

最新 HEAD。

当前已知最新基准：

```text
99fbe47b9a6fa1bcfe628cb801cbd8e1ebcb29c5
Archive authorized E1 calls and stop causal gates on reference namespace failures
```

如果远程 HEAD 已经前移：

1. 阅读新增 commits；
2. 判断是否已经修复本任务问题；
3. 在审计报告中说明；
4. 不得静默覆盖新工作。

建议基于最新：

```text
experiment/claim-pipeline-root-cause
```

新建：

```text
experiment/claim-pipeline-contract-rerun
```

或者等价独立分支。

---

# 2. 旧 E1 run001 必须永久保留

以下结果是历史实验事实：

```text
E1 run001
85 attempted calls
85 HTTP 200
8 reference-contract failures
1 unsent dependency
A0 complete 24/24
A1 complete 22/24
A2 complete 17/24
```

正式结论保持：

```text
H1 inconclusive
H2 inconclusive
H3 not tested
```

不得：

- 修旧输出；
- 把 `w_*` 自动映射成 `W#` 后重算；
- 补跑旧失败的九个 packet；
- 用 surviving samples 做 semantic comparison；
- 改写 `ROOT_CAUSE_CONCLUSION.md` 里的历史结论。

旧 run001 的意义是：

> **reference namespace contract diagnostic**

不是失败的语义实验。

---

# 3. 已确认的机械根因

当前 evidence object 同时向模型暴露：

```json
{
  "window_ref": "W12",
  "source_window_ref": "w_507e1a8c396e80440dd42c00",
  "doc_ref": "D4",
  "docid": "...",
  "document_sha256": "...",
  "text_sha256": "...",
  "offset": 123,
  "end_char": 456,
  "title": "...",
  "url": "...",
  "text": "..."
}
```

但是 runtime 只允许：

```text
evidence_refs = ["W12"]
```

不能接受：

```text
evidence_refs = ["w_507e..."]
```

与此同时，原：

```text
a0_current_reader.json
a1_no_c_reader.json
a2_evidence_formulator.json
```

中的 `evidence_refs.items` 只是：

```json
{
  "type": "string",
  "minLength": 1
}
```

所以：

\[
\boxed{
SchemaContract \neq RuntimeContract
}
\]

并且模型同时看见两个具有明显 ref 语义的字段：

```text
window_ref
source_window_ref
```

造成：

\[
\boxed{
VisibleReferenceNamespaceConfusion
}
\]

这不是 semantic hallucination。

失败的 `w_*` 全部来自真实输入。

---

# 4. 本次修复的核心原则

新增明确原则：

\[
\boxed{
\textbf{One semantic role, one public reference namespace.}
}
\]

对于 Evidence Window：

模型只允许看到：

```text
W#
```

Harness 可以继续内部保存：

```text
source_window_ref
docid
hash
offset
end_char
```

但这些不属于 semantic model 的 decision surface。

---

# 5. 不修改 Internal Evidence

不要删除 production/internal provenance。

内部完整 Evidence record 仍应保留：

```text
window_ref
doc_ref
source_window_ref
docid
document_sha256
text
text_sha256
title
url
offset
end_char
```

这些仍然用于：

```text
integrity
replay
source hashing
exact raw span validation
audit
provenance
```

---

# 6. 新增 Semantic Evidence View

在**实验 diagnostic harness 内**实现一个明确 allowlist view。

例如：

```python
def semantic_evidence_view(window):
    return {
        "window_ref": window["window_ref"],
        "doc_ref": window["doc_ref"],
        "title": window["title"],
        "url": window["url"],
        "text": window["text"],
    }
```

具体命名可调整。

但原则不能变。

---

# 7. Semantic Model 不得再看到以下字段

至少隐藏：

```text
source_window_ref
docid
document_sha256
text_sha256
offset
end_char
```

除非你在代码审计中发现某字段对当前实验中的 source semantics 是不可替代的。

如果确有必要保留某 metadata：

必须在设计审计中逐项说明为什么它是：

```text
semantic evidence
```

而不是：

```text
mechanical provenance
```

默认不要保留。

---

# 8. 保留 title / url / doc_ref

不要为了 namespace repair 把 source identity 相关信息也全部删除。

以下字段可继续提供：

```text
window_ref
doc_ref
title
url
text
```

因为它们可能参与：

```text
document identity
publisher/source identity
table/page context
attribution
```

本实验不是 source-metadata ablation。

---

# 9. 所有 E1 arms 使用同一 Semantic Evidence View

这点非常重要。

A0：

```text
OneGap
C
SemanticObservation
```

A1：

```text
OneGap
SemanticObservation
```

A2 Selector：

```text
OneGap
C
SemanticObservation
```

A2 Formulator：

```text
Selected SemanticEvidence only
```

不得：

```text
A0 sees full internal evidence
A2 sees cleaned evidence
```

否则会产生新的 treatment confound。

---

# 10. Schema 必须和 runtime contract 对齐

修改本 experiment 的 Claim-producing schemas。

原：

```json
"evidence_refs": {
  "type": "array",
  "items": {
    "type": "string",
    "minLength": 1
  }
}
```

至少改为：

```json
"evidence_refs": {
  "type": "array",
  "items": {
    "type": "string",
    "pattern": "^W[1-9][0-9]*$"
  },
  "uniqueItems": true,
  "minItems": 1
}
```

至少覆盖：

```text
a0_current_reader
a1_no_c_reader
a2_evidence_formulator
g1_evidence_inventory
```

即所有会输出 Evidence refs 的 diagnostic semantic roles。

---

# 11. A2 Selector 继续使用 W-only schema

当前：

```json
"window_ref": {
  "pattern": "^W[1-9][0-9]*$"
}
```

已经正确。

保持。

---

# 12. Runtime membership validation 必须继续存在

Regex 只能证明：

```text
W-like
```

不能证明：

```text
observed in this request
```

因此仍要机械检查：

```python
returned_ref in available_window_refs
```

不能只依赖 schema。

---

# 13. 如果实现方便，优先使用动态 enum

对于一个 request，如果合法 refs 是：

```text
["W3"]
```

可以动态生成：

```json
{
  "enum": ["W3"]
}
```

如果是：

```text
["W3", "W4", "W7"]
```

则：

```json
{
  "enum": ["W3", "W4", "W7"]
}
```

这种方式优于：

```text
regex only
```

因为模型 contract 与实际 available set 完全一致。

但是：

- 不得改变 semantic role 的其他 schema；
- 不得让动态 schema 泄露 evaluation labels；
- 如果动态 enum 引入较大实验代码复杂度，W-pattern + membership validation 也可接受。

必须在报告中说明最终选择。

---

# 14. 禁止任何 post-hoc ref mapping

如果模型仍返回：

```text
w_abc
```

不能自动：

```text
w_abc → W3
```

即使 Harness 明确知道它们对应。

也不能：

```text
docid → D#
source_window_ref → W#
```

模型违反 contract：

```text
record failure
```

而不是：

```text
repair output
```

---

# 15. 本次不得修改任何 E1 semantic prompt

必须保证以下 prompt 与上一轮 freeze **字节一致**：

```text
a0_current_reader.txt
a1_no_c_reader.txt
a2_selector.txt
a2_evidence_formulator.txt
```

特别禁止新增：

```text
Use W# only
Do not use source_window_ref
```

到 semantic prompt。

因为 namespace 应由：

```text
representation + schema
```

解决。

不是靠 prompt 提醒。

---

# 16. 更不能加入任何 semantic bad-case rule

禁止添加：

```text
67 albums
2016
memo date
letter date
Euler
SPS
DLC
teammates
patient nationality
publication country
```

等 case-specific example。

本次修复是：

```text
contract / representation repair
```

不是：

```text
semantic tuning
```

---

# 17. 原 E1 bank 必须 byte-identical

必须保留：

```text
36 packets
20 qids
8 relation families
```

尤其 E1 使用的：

```text
D + H_diagnostic
= 24 packets
```

不得：

- 替换 qid；
- 删除困难 packet；
- 补新 packet；
- 调整 split；
- 修改 OneGap；
- 修改 C；
- 修改 Observation source text；
- 修改 frozen atom；
- 修改 review strata。

---

# 18. H-confirmation 必须继续保持未打开状态

本次只执行：

```text
E1
```

不要执行 E3。

也不要为了看结果提前调用：

```text
H_confirmation
```

H-confirmation 仍作为未来确认集。

---

# 19. Review Rubric 必须保持不变

保留原：

```text
source_supported
semantic_strengthening
strengthening_type
gap_relevant
duplicate_with_C
gap_useful_if_supported
ambiguous_relation
covered_atom_ids
```

定义。

不得因为看到 run001 raw outputs 修改 reviewer 标准。

---

# 20. H1/H2 阈值保持不变

继续使用冻结标准。

## H1

A1 vs A0：

```text
FSSR relative reduction >= 30%
GRSR drop <= 10 percentage points
paired packet direction < 0
qid-weighted direction < 0
same direction on H-diagnostic
```

---

## H2

A2 vs A1：

```text
FSSR relative reduction >= 30%
GRSR drop <= 10pp
Gap-relevance precision drop <= 10pp
paired direction
qid direction
same direction on H-diagnostic
```

不得因为结果不好调整 threshold。

---

# 21. 第一步：先写 Contract Repair Audit

在修改代码前创建：

```text
experiments/claim_pipeline_root_cause/contract_rerun/CONTRACT_REPAIR_AUDIT.md
```

至少回答：

1. `window_ref` 的职责是什么？
2. `source_window_ref` 的职责是什么？
3. 为什么两个都进入 semantic payload？
4. 为什么 A2 Selector 没有失败？
5. 为什么 A1/A2 Formulator 会失败？
6. Schema 与 runtime contract 哪里不一致？
7. 8 个 run001 failure 是否全部来自可见 alias confusion？
8. 是否存在任何真正 invented ref？
9. 哪些 Evidence 字段属于 semantic model 必要信息？
10. 哪些字段纯属 mechanical provenance？
11. 为什么不能 post-hoc alias mapping？
12. 为什么需要完整重跑，而不能只补 9 个失败 chain？
13. 本修复是否改变 H1/H2 semantic intervention？
14. 是否修改 production runtime？
15. 是否增加 persistent semantic state？

Audit commit 后再写代码。

---

# 22. 本任务默认不修改 production recoverable loop

当前目标是：

> 让 root-cause experiment 可解释。

因此默认只修改：

```text
experiments/claim_pipeline_root_cause/
```

中的 diagnostic harness。

不要修改：

```text
llm_chat/recoverable_loop/engine.py
llm_chat/recoverable_loop/roles.py
llm_chat/recoverable_loop/state.py
llm_chat/recoverable_loop/tools.py
```

如果代码复用必须触碰 production 文件：

停止并在报告中解释。

不要顺手改 production。

正式 Runtime repair 应该在实验确认后另开任务。

---

# 23. 新增离线测试

至少覆盖以下机械 contract。

### Public view

1. Semantic view 包含 `window_ref`；
2. 包含 `doc_ref`；
3. 包含 `title`；
4. 包含 `url`；
5. 包含 `text`；
6. 不包含 `source_window_ref`；
7. 不包含 `docid`；
8. 不包含 SHA；
9. 不包含 offset/end。

---

### Ref schema

10. `["W1"]` valid；
11. `["W12"]` valid；
12. `["w_abc"]` invalid；
13. `["D1"]` invalid；
14. `["C3"]` invalid；
15. `["R1"]` invalid；
16. `["W0"]` invalid；
17. `["W01"]` invalid；
18. unobserved `W999` rejected by runtime membership。

---

### Arm isolation

19. A0 sees C；
20. A1 does not see C；
21. A2 Selector sees OneGap+C；
22. A2 Formulator sees neither OneGap nor C；
23. A2 Formulator does not see Selector reason；
24. all three see the same cleaned Evidence representation.

---

### Freeze integrity

25. E1 bank byte-identical；
26. all E1 semantic prompts byte-identical；
27. review rubric byte-identical；
28. H1/H2 thresholds byte-identical；
29. run001 immutable；
30. H-confirmation not used。

---

# 24. 对旧 run001 做 contract replay

不重新调用模型。

读取旧 8 个 invalid raw outputs。

验证：

```text
old raw output
→ new schema/runtime
→ still rejected
```

因为：

```text
w_* still invalid
```

这是正常的。

不要自动修。

另外验证旧对应 input 经过新 SemanticEvidenceView 后：

```text
source_window_ref
```

不会再出现在 model-visible payload。

这说明：

> 新设计消除了诱因。

而不是：

> 新 validator 放宽了错误。

---

# 25. 新 freeze 必须在付费调用前提交

建议目录：

```text
experiments/claim_pipeline_root_cause/contract_rerun/
```

至少包含：

```text
CONTRACT_REPAIR_AUDIT.md
OFFLINE_VALIDATION.md
FREEZE_V2.json
REQUEST_HASHES_V2.json
CALL_ESTIMATE_V2.json
EXECUTION_PREFLIGHT.json
```

所有：

```text
bank
prompts
schemas
harness
config
review rubric
thresholds
```

hash 固定后再执行模型调用。

---

# 26. 本消息授权范围

用户当前明确要求：

> 修复后重跑。

因此本任务授权：

\[
\boxed{\text{contract-fixed E1 full rerun}}
\]

允许：

```text
DeepSeek Flash semantic calls for corrected E1
```

调用上限继续：

```text
96 calls
```

不得超出。

---

# 27. 当前授权不包含 E2 / E3

即使新 E1 成功并 H1/H2 gate PASS：

本任务只允许：

```text
E1 execution
E1 semantic review
E1 analysis
```

然后停止。

不得自动执行：

```text
E2
E3
new Recovery rollout
production runtime test
```

这些等待新的明确授权。

---

# 28. 模型配置保持上一轮完全一致

继续使用冻结配置：

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

不得换模型。

不得调整 temperature。

不得增加 retry。

---

# 29. 完整 E1 从头重新执行

E1 packets：

```text
24
```

Arms：

```text
A0
A1
A2
```

初始独立 calls：

```text
24 * 3 = 72
```

A2 selected Evidence 后最多再：

```text
24 formulator calls
```

因此：

```text
max = 96 semantic calls
```

不要为了用满 96 而强制 A2 formulation。

如果：

```text
A2 selector = []
```

则合法 skip。

---

# 30. 不只补失败 packet

绝对禁止：

```text
reuse old A0
reuse successful old A1
reuse successful old A2
rerun only failures
```

新结果必须是一个完整、统一 contract 下的 paired experiment：

\[
24\times(A0,A1,A2)
\]

全部属于同一次新 freeze。

---

# 31. 并发

可以继续 dependency-safe parallelism。

上一轮：

```text
peak concurrency = 72
```

已经稳定。

无需提高。

推荐：

```text
initial independent calls = 72
```

A2 Formulator 等 Selector dependency 完成后再执行。

不要通过提高并发改变实验。

---

# 32. Failure Policy 保持严格

任何：

```text
schema failure
ref failure
transport failure
finish_reason failure
model mismatch
incomplete response
```

：

1. 保留；
2. halt unsent requests；
3. 已经 in-flight 的允许结束并记录；
4. 不 retry；
5. 不 replacement；
6. 不 repair；
7. 不 resume。

如果新 run 仍发生 reference contract failure：

立即停止并调查。

不要继续 semantic scoring。

---

# 33. 新 E1 必须满足完整执行门槛

只有：

```text
A0 24/24
A1 24/24
A2 24/24 valid packet chains
```

或 A2 合法 `selection=[] → formulation skipped` 的完整 chain，

才能进入正式 comparative semantic review。

任何 selective missingness：

```text
E1_INCOMPLETE
```

H1/H2：

```text
INCONCLUSIVE
```

。

---

# 34. 执行完成后进行盲式 semantic review

继续使用原 review export。

Reviewer 不应看到：

```text
arm
H1/H2 hypothesis
other-arm output
historical final answer
future evidence
```

Source-support review只看：

```text
Candidate
cited exact Observation
```

Relevance review才看：

```text
Candidate
Observation
OneGap
C
```

不要混在一起。

---

# 35. 必须分别报告 Raw Candidate 和 Post-dedup

不要只报告最终 kept Claims。

首先评估：

\[
Reader/Formulator
\]

本身有没有 strengthening。

因此：

```text
Primary FSSR
Primary Source-Supported Precision
```

基于：

```text
raw generated candidates
```

然后另报：

```text
exact deterministic dedup
semantic dedup sensitivity
```

。

---

# 36. 重点指标

## False Semantic Strengthening Rate

\[
FSSR=
\frac{unsupported\ strengthened\ candidates}
{all\ factual\ candidates}
\]

---

## Source Supported Precision

\[
SSP=
\frac{source\ supported}
{all\ candidates}
\]

---

## Gap Relevant Supported Recall

继续使用 frozen atoms：

\[
GRSR
\]

---

## Gap Relevant Precision

尤其比较 A2。

---

## Correct Silence

对 frozen：

```text
duplicate/no-new
relevant/no-new
```

packet：

是否正确输出空或 post-dedup 无新增。

---

## Claim Bloat

每 packet raw candidate 数。

---

# 37. H1 的核心比较

\[
A0:
OneGap+C+Observation\rightarrow Claim
\]

vs

\[
A1:
OneGap+Observation\rightarrow Claim
\]

如果 A1：

```text
FSSR relative reduction >= 30%
```

同时：

```text
GRSR drop <= 10pp
```

并满足 paired/qid/H-diagnostic direction：

支持 H1。

否则：

```text
H1 unsupported / inconclusive
```

按冻结规则。

---

# 38. 特别审查 q435，但不能让它决定结论

旧 run001 已经给出一个非正式线索：

A1 在看不到 C 时仍生成：

```text
Oliver Mtukudzi spoke to Forbes Africa in 2016,
at which point he had 67 albums.
```

因此 q435 单 case 暗示：

```text
C-visible novelty pressure
```

可能不是充分解释。

新 E1 必须如实保留 q435 的结果。

但：

```text
q435 pass/fail
```

绝对不能成为 H1 gate。

---

# 39. H2 是当前更关键的比较

\[
A1:
OneGap+Observation
\rightarrow Claim
\]

vs

\[
A2:
OneGap+C+Observation
\rightarrow EvidenceSelection
\]

然后：

\[
SelectedEvidenceOnly
\rightarrow Claim
\]

最关键的问题：

> 当 Formulator 完全看不到 OneGap 和 C 时，semantic strengthening 是否下降？

特别是：

> q435 Evidence-only Formulator 会不会仍然生成 `67 albums by 2016`？

这是 diagnostic sanity check。

但正式结论必须来自：

```text
cross-qid
cross-relation-family
H-diagnostic
paired metrics
```

。

---

# 40. 如果 A2 仍然大量 strengthening

那不要继续改 Reader prompt。

这会说明我们的根因需要进一步下沉：

\[
\boxed{
EvidenceOnly
\rightarrow
NaturalLanguageClaim
}
\]

本身可能就会发生：

```text
plausible discourse inference
→ stronger factual commitment
```

那下一研究问题才应该是：

> source-relative fact normalization / entailment 本身的可靠性。

而不是：

> 再把 Gap 隔离得更多。

---

# 41. 如果 A2 明显改善

才有资格认为：

\[
\boxed{
Gap-conditioned selection
+
Evidence-only formulation
}
\]

是一个有实证支持的结构性改进。

仍然不能立即修改 production。

下一步应该是：

```text
E2 Grounding anchoring ablation
```

。

---

# 42. 不执行 E2

本次完成 E1 后即使：

```text
H1 PASS
H2 PASS
```

也只输出：

```text
E1_RERUN_CONCLUSION.md
```

和未来：

```text
E2_NEXT_PLAN.md
```

不要发任何 E2 paid calls。

---

# 43. 建议 Commit 顺序

### Commit 1

```text
Audit public/internal evidence reference leakage before E1 rerun
```

只提交 Contract Audit。

---

### Commit 2

```text
Isolate semantic evidence view and align W-reference schemas
```

实现 mechanical repair + tests。

---

### Commit 3

```text
Freeze contract-corrected E1 rerun with unchanged semantic treatments
```

冻结所有 input/hash。

---

### Commit 4

```text
Record complete contract-corrected E1 root-cause rerun
```

原始 live outputs。

---

### Commit 5

```text
Review E1 construction ablation and report H1/H2 root-cause evidence
```

semantic review 和结论。

不要 squash。

---

# 44. 最终报告必须明确区分三种结论

## Contract conclusion

是否实现：

\[
\boxed{
One semantic role\rightarrow One public evidence namespace
}
\]

---

## H1 conclusion

是否有证据支持：

\[
C-visible novelty pressure
\]

。

---

## H2 conclusion

是否有证据支持：

\[
selection/formulation coupling
\]

。

不要混成一句：

> “新 pipeline 更好。”

---

# 45. 最终必须回答

1. 新 SemanticEvidenceView 暴露哪些字段？
2. 哪些 internal provenance 被隐藏？
3. 为什么这些字段不再需要模型处理？
4. `evidence_refs` schema 是否和 runtime 对齐？
5. 是否仍存在任何双 reference namespace？
6. 是否发生自动 alias mapping？
7. 原 run001 是否保持 byte-identical？
8. bank 是否保持 byte-identical？
9. prompts 是否保持 byte-identical？
10. H1/H2 thresholds 是否保持不变？
11. 新 E1 是否 24×3 全部完整？
12. contract failure 是否降为 0？
13. A0 raw candidate count / FSSR / SSP？
14. A1 raw candidate count / FSSR / SSP？
15. A2 raw candidate count / FSSR / SSP？
16. H1 是否通过完整 gate？
17. H2 是否通过完整 gate？
18. H-diagnostic direction 是否一致？
19. A1 是否减少 q435 strengthening？
20. A2 Evidence-only Formulator 如何处理 q435？
21. strengthening 是否跨 relation family 减少？
22. GRSR 是否出现 recall collapse？
23. Correct Silence 是否改善？
24. A2 是否导致 fact bloat？
25. 当前根因假说应该接受、部分接受还是拒绝？
26. 下一步是否值得进入 E2？
27. 是否执行了 E2/E3？答案必须是 No。
28. 是否修改 production runtime？答案必须是 No。

---

# 46. 最终研究纪律

此次重跑的目标不是：

```text
make q435 pass
```

而是：

\[
\boxed{
\textbf{
在消除机械 reference ambiguity 后，
重新获得一个完整、可比较、无 selective missingness 的
A0/A1/A2 Claim-construction causal diagnostic。
}
}
\]

我们真正要回答：

\[
\boxed{
\textbf{
False semantic strengthening
主要来自 C-visible novelty pressure，
还是来自 Gap 与 Claim formulation 的耦合，
还是二者都不是？
}
}
\]

只有这个问题被干净回答后，才能进入下一阶段。

---

# 47. 本次最重要的工程原则

把这条写进实验报告：

\[
\boxed{
\textbf{
Mechanical provenance must stay in the Harness.
Semantic models should operate only on stable public handles.
}
}
\]

以及：

\[
\boxed{
\textbf{
Do not ask a language model to choose between two machine identities
when the Harness already knows they are aliases.
}
}
\]

修掉 namespace ambiguity 后，才有资格继续研究真正的语义根因。