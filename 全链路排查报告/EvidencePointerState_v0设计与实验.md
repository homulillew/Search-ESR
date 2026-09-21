# EvidencePointer State v0：设计与实验

配套代码：`experiments/research_state/evidence_pointer/`
配套审计：`全链路排查报告/EvidencePointer前置职责边界审计.md`

---

## 1. `750257d` 暴露了什么

直接重跑 `contracts.note_result` 于原始 events（不读报告数字）：

- 12 组交付，**5 组 invalid**（41.7%），1 组 empty，6 组 ok；
- 32 条笔记中仅 **5 条**引文机械失败（15.6%），但 all-or-nothing 使其连带丢弃
  **11 条逐字合法的笔记**，总浪费 **16/32 = 50%**；
- 五种失败全部定位到码点：ref 前缀截短（18 vs 26 字符）、`\n\n`→U+0020、
  NBSP U+00A0→U+0020、`"`→`'`、`,`→`...`；
- **被判 invalid 的笔记里，0 条语义错误**；
- **被判 ok 的笔记里，恰恰有 2 条语义扩展**（776 标题→出生日期、71 单一来源→
  "Historical records indicate"）。

即：字符级校验既抓不到语义错误，其失败也不代表语义错误。它在校验一个与目标
正交的性质，同时把噪声放大到 50%。

## 2. 为什么这不是简单 prompt 问题

三条独立证据：

1. **失败落在重复职责上。** observation payload 已携带 `window_ref` / `docid` /
   `document_sha256` / `offset` / `end_char`；校验器自己算出
   `absolute_starts`。模型被要求复打的信息，Harness 全部持有。
2. **addendum 已呈 case-specific 形态。** 三条核心规则分别对应 776 / 519 / 71
   三道固定开发题的上一轮失败。本轮 776 扩展被消除，但同组因省略号机械失败而
   整体无效——收益在注入层不可见。
3. **新机械失败无法被 prompt 规则预防。** 字符复制失手与语义指令正交；且 776 P1
   的 131 字符多段引用精确包含 `\n\n`，证明模型**有能力**复制，失手是任务形态问题。

另外 `empty` 合法而"有瑕疵"致命，构成系统性保守偏置（517 P1 已出现）。任何
fidelity 分支都必须显式处理它，而它不是 prompt 层面能解决的。

## 3. 什么是 deterministic-first

> 任何能够由 Harness 从工具调用、Observation、已有 State 或程序日志中确定性恢复
> 的信息，都不得要求 LLM 重新生成。

**Harness / Python 负责**：exact query、attempt id、tool call id、window_ref、
docid、document hash、URL、window offset / end_char、source span 的 relative /
absolute char range、exact source text、State ID、provenance、State version、
hash / dedup / 机械相等、pointer 合法性与边界检查。

**LLM 只负责**：从实际可见 Observation 中判断哪些原文值得下一步研究继续保留。

**本任务不让 LLM 输出**：window_ref、exact quote、char offset、document hash、
candidate、hypothesis、gap、next_need、confidence、final answer state。

## 4. Observation / Attempt / Research State 的边界

```text
Q                      immutable Task（不可改写）
q0 / tool / result     Attempt Log（含 q0 == Q 的逐字约束）
O1                     Raw Observation（冻结、sealed、完整保留）
S1 = Evidence Pointer  Research State（本轮唯一的新研究对象）
```

前两层在本设计中**都不是** State：它们是输入。State 从 O1 之后才产生。这样划分的
目的是让"State 有没有价值"这个问题可测，而不是与"检索是否召回"混淆。

## 5. 为什么 first Research State 是 Evidence Selection

三个理由：

1. 它是**唯一在 Q 与下一步动作之间必然存在**的中间量。无论后续路线是 Actor、
   还是长程 memory，都必须先决定"哪些已看见的东西要留着"。
2. 它**语义上必要、机械上可完全确定性化**。选择是语义判断（需要 LLM 或人），
   但选中之后的 provenance 全部可切片恢复。这两半可以干净分开。
3. 它是上一轮失败的实际位置。`statement` 是语义扩张的载体且无机械约束；
   `source_ref` / `quote` 是机械复制的载体且无语义价值。**Selection 恰好是这两半
   之间唯一真正需要语义、又不需要复制的位置。**

## 6. 为什么第一轮使用 reference pointer

要证明的是：

> **Evidence Pointer State 本身有没有价值。**

而不是"LLM 能不能自动写 Evidence State"。

若一上来就用 LLM selector：

```text
LLM selector → pointer → Actor
```

失败后无法区分是 State 没价值，还是 selector 选错了。**这是混淆处理变量与
测量对象。** 因此第一轮的 selector 是人工 reviewer，其选择质量在事后被单独审计
（"Evidence State 输入质量"轴），不与 Actor 表现混计。

reviewer 的信息边界：只看 `Q + q0 + O1`。不看 gold、后续 Search/Open、最终
trajectory、历史最终答案、之后 Actor 输出。

## 7. 为什么还不实现自动 selector

因为 selector 的错误会污染 State 价值的结论。只有当 reference 路径证明
"B > A"之后，才有意义去比较：

```text
Reference Evidence Pointer   vs   Model-selected Evidence Pointer
```

那时 LLM 的输出应当尽可能只是"选 Harness 提供的地址"，例如
`{"selected_units": ["W2:S3", "W2:S4"]}`，再由程序恢复 ref / text / range /
provenance。本轮只在 contract 里为此预留了空间，**不实现它**。

## 8. 为什么还不实现 statement

`750257d` 的证据是直接的：

- statement 可以在**引文完全合法**的情况下扩展来源含义（776 P0 note 0、71 P0 note 2）；
- 程序只能校验 `quote in text`（可见性），**无法校验蕴含**；
- 反过来，引文失败时 statement 往往是对的（546 P1、519 P1）。

也就是说 statement 既没有机械约束，也不是机械失败的保护对象。把它放进 State，
等于把上一轮的混淆重新引入。等 Evidence Pointer 的价值被 A/B 证明之后，再决定
statement 是否以"派生注释"而非"模型输出"的形式加入。

## 9. A/B 能证明什么

固定 `Q`、`q0`、`O1`，同一模型、同一 system prompt、同一采样、同一 token 上限、
同一 tool 定义、同一 budget、平衡的组内顺序。

- **A** = `Q + q0 + O1`
- **B** = `Q + q0 + O1 + 显式选中的 exact evidence`（追加一条 user 消息，
  **不删除 Raw Observation**）

处理变量是**是否存在显式 Evidence State**。

第一轮**不是** `A = raw` 对 `B = summary replaces raw`——那会把"压缩"和
"显式选择"两个变量混在一起。

Actor 只交付 Search / Open / Final Answer 之一或一个合法完整 tool batch，
**不执行提议的工具**，不做 rollout，不做自动 State update。

## 10. 不能证明什么

即使 B > A，也只能证明：**一个正确、显式的 Evidence Pointer State 对下一动作
有价值。**

不能证明：
- 自动 selector 已经有效
- semantic statement 有价值
- 长程 memory 有价值
- hypothesis / binding / gap 必须存在
- 最终 BC+ accuracy 提升

这是 **State utility test**，不是 selector test，也不是 accuracy test。

## 11. 下一步进入自动 selector 的 gate

1. A/B 在 12–20 个**新**题上显示 B > A（不是固定开发题）；
2. reference State 的输入审计通过（pointer 来自当前 O1、无系统性偏题、无同等级
   关键 span 漏选、`evidence=[]` 的题确实无可用信息）；
3. 上述结论在 `cost_accounting_complete=true` 的批次上成立（失败批次保留但不
   计入结论）。

满足后，下一实验比较 reference pointer 与 model-selected pointer，LLM 输出
限制为选地址。**只有这一步成功，才讨论 statement / long-horizon memory。**

---

## 实现状态

| 交付 | 位置 |
|---|---|
| 前置职责边界审计 | `全链路排查报告/EvidencePointer前置职责边界审计.md` |
| 本设计报告 | 本文 |
| note 分支暂停说明 | `experiments/research_state/first_observation/NOTE_FIDELITY_BRANCH_STATUS.md` |
| 新实验代码 | `experiments/research_state/evidence_pointer/` |
| pointer materialization 测试 | `tests/test_evidence_pointer_materialization.py`（28） |
| A/B plan 测试 | `tests/test_evidence_pointer_ab.py`（19） |
| 旧路径 regression 测试 | `tests/test_evidence_pointer_regression.py`（10） |
| VALIDATION | `experiments/research_state/evidence_pointer/VALIDATION.md` |
| 下一执行 Agent 的 CODEX_TASK | `experiments/research_state/evidence_pointer/CODEX_TASK.md` |
| 认证失败短路修复（独立归因） | `全链路排查报告/认证失败批处理短路修复.md` |

**未执行**：真实 Evidence Pointer A/B（无授权，不产生费用）。
