# CODEX_TASK — Evidence Pointer State v0 的下一步执行

## 前置条件（本任务已完成，不要重做）

- [x] 前置职责边界审计（`全链路排查报告/EvidencePointer前置职责边界审计.md`）
- [x] note fidelity 分支暂停说明（`../first_observation/NOTE_FIDELITY_BRANCH_STATUS.md`）
- [x] `contracts.py` / `run.py` / `prompts/actor.txt`
- [x] pointer materialization 测试（28）
- [x] A/B plan 测试（19）
- [x] 旧路径 regression 测试（10）
- [x] `VALIDATION.md`（335 unittest + 390 pytest，0 skip）
- [x] 认证失败短路修复（`first_observation/run.py`，含 regression 测试）

## 你的任务：执行一次真实的 reference-pointer A/B

**只在获得明确授权后执行。** 本任务会产生真实模型费用。

### 规模

- 题数：12–20 个**新** BC+ question（不是 517/546/776/519/191/71）
- 每题 1 次真实原题 Search（`q0 == Q` 逐字）
- 每题 2 次 Actor 调用（A + B）
- **总模型调用 = 2 × 题数**（24–40 次），`initial_model_calls = 0`
- 提出的工具：0 次执行

12–20 不是硬编码上限；CLI 接收任意冻结的 selection artifact。题数由你冻结的
`--qids` 决定。

### 硬性顺序（违反则作废）

1. **在看到任何 Search 结果之前**冻结 qid 并写 `selection.json`。
2. 执行 `collect`。**不得**根据结果重新选题、换题、加题。
3. 生成 reviewer 模板。
4. 人工标 pointer：**只看 Q + q0 + O1**。
   - 不得看 BC+ gold answer
   - 不得看后续 Search / Open
   - 不得看最终 trajectory
   - 不得看历史最终答案
   - 不得看 Actor 输出
5. `bind` → `plan` → `execute`。

### reviewer 只能写

```json
{"pointers": [{"window_ref": "<visible window>", "start": 123, "end": 245}]}
```

每题 0–2 个。不写 candidate、statement、next query、gap、confidence。
rationale 可写进 sealed artifact 供审计，**绝不能进入模型输入**。

### 允许的结果

- Search 无有用结果 → 记录，不换题
- `evidence: []` → 完全合法，不等于失败
- Actor 返回 Search / Open / Final Answer 任一皆可
- **不执行**任何提议的 Search / Open

### 必须保留的失败

API timeout / truncation / 认证失败 / 本地 harness 错误 / 中断 / 非法协议，
全部保留在分母里。`blocked_by_auth` 是新支持的合法状态，表示"凭证已失效，
剩余请求未发送"——不要把它们改成 `ok`，也不要重发。

若 `cost_accounting_complete=false`，退出码为 2，这是**交付不完整**的正确语义，
不要通过补发或 JSON 修复把它变成 0。

### 评价（事后）

先看 Q / q0 / O1 / reference evidence，**事前**记录多种合理下一动作。然后：

**1. Evidence State 输入质量**（不是模型性能）

- pointer 是否来自当前实际 O1
- pointer 是否确实值得当前任务继续使用
- 是否明显偏题
- 是否漏掉一个同等级关键 span
- `evidence=[]` 是否合理

**2. Actor 行为**

- 是否正确利用已有 Observation
- 是否无理由重复已解决的查询
- 是否沿真实 intermediate entity 继续
- 是否把部分支持升级成候选确认
- 上下文不足时是否选合理 Open
- 是否新增无依据事实
- 是否过早 final answer
- 整个下一动作是否合理

**3. Pairwise**：只给 `B better / A better / tie / unclear` + 理由。

**不要**一开始就设计综合分数。

### 结论能说什么、不能说什么

若 B > A，只能证明：**一个正确、显式的 Evidence Pointer State 对下一动作有价值**。

**不能**证明：
- 自动 selector 已有效
- semantic statement 有价值
- 长程 memory 有价值
- hypothesis / binding / gap 必须存在
- BC+ accuracy 提升

### 交付物

1. 冻结的 selection / collection / reviewer 模板 / pointer 选择 / evidence state
2. A/B plan（含 sha256）
3. 执行批次（含 usage 与失败）
4. 逐题评价卡（labels + pairwise）
5. 一份报告：说明题数、调用数、失败数、未知成本、A/B 结果

### 禁止

- 删除 / 修改旧实验、旧 response、旧标签
- 把 `evidence=[]` 的题从分母里删掉
- 让 reviewer rationale 进任何模型请求
- 自动实现 selector（那是**下一轮**的事）
- 修改 `prompts/actor.txt` 以外的任何 prompt
- 修改默认 Agent、Search/Open 实现
- 提交 `.env` / API key / 数据库 / 索引 / 权重
