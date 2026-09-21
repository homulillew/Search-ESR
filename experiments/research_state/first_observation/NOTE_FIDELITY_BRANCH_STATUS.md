# Note Fidelity 分支状态：暂停

适用范围：`prompts/note.txt` + `prompts/note_fidelity_addendum.txt` + `contracts.note_result`
+ `fidelity.py` 所定义的 `statement + source_ref + quote` 实验线。

## 状态

**暂停。** 不再新增 P2/P3/P4 fidelity 提示词，不再向 `note.txt` 或 addendum 追加任何
针对具体病例的细则，不做 quote fuzzy repair，不把旧 invalid 改判为成功。

## 暂停理由

不是"semantic note 已被证明无用"。是以下三条**测量层面**的理由：

1. **机械噪声压倒语义信号。** 交付批次 12 组中 5 组 invalid，五条失败全部是字符
   复制失手（ref 前缀截短、`\n\n`→空格、NBSP→空格、`"`→`'`、`,`→`...`），零条
   语义失败。all-or-nothing 把这 5 条放大成 16/32 条笔记浪费（50%）。
2. **接口违反 deterministic-first。** `window_ref` / `docid` / `document_sha256` /
   `offset` / `end_char` 全部已在传给模型的 observation payload 中；校验器自己就能
   把引文定位到绝对字符坐标。要求模型重新复打这些字段，是在校验一个 Harness 已持
   有且能自行恢复的性质。
3. **已出现 case-specific patching。** addendum 的三条核心规则分别对应 776 / 519 /
   71 三道固定开发题的上一轮失败。这是 bad case 逐条修补，不是泛化保真原则。

详见 `全链路排查报告/EvidencePointer前置职责边界审计.md`。

## 保留用途

旧实验**原样保留**，不删除、不修改、不重解释：

- `runs/notes_qwen_20260921/`、`runs/note_fidelity_20260921T064837Z/`（含三批执行记录，
  两批 AuthenticationError 完整保留在分母中）；
- pointer contract 的 **regression / bad-case reference**：`contracts.note_result`
  的五种机械失败模式被固化为新 contract 的反向测试用例；
- `fidelity.py` 的 sealed-plan 复核流程（`validate_fidelity_plan` 重建整个 plan 并
  逐对象比对漂移）被新实验继承。

## 明确禁止

- 删除旧实验目录或旧 response；
- 修改旧标签、旧报告或旧 collection 以制造更好结果；
- 把旧 invalid 通过 fuzzy matching 或宽松校验重新解释为成功；
- 在 `note.txt` 中继续追加病例细则；
- 让默认 Agent 自动走这条分支。

## 新路线

`experiments/research_state/evidence_pointer/`：第一版 Research State 只表达
"哪些已实际看见的原文值得下一步保留"，由 reference reviewer 选 0–2 个 span，Python
从 observation 切片 materialize，模型不输出任何 source metadata。

判断标准从"怎样让 LLM 更准确地写 citation"改为"Harness 已经知道这些 citation，
为什么还要让 LLM 重写"。
