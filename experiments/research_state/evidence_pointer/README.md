# Evidence Pointer State v0

第一版 Research State。它只表达一件事：

> 哪些**已经实际看见**的原文，值得下一步研究继续保留。

## 为什么存在

上一轮 `statement + source_ref + quote` 接口（`first_observation`）要求模型重新
复打 Harness 已经持有的信息：`window_ref`、`docid`、`document_sha256`、`offset` 都
在传给模型的 observation payload 里，而校验器自己就能把引文定位到绝对字符坐标。
结果是 12 组交付里 5 组因纯机械复制失败而无效（ref 前缀截短、`\n\n`→空格、
NBSP→空格、`"`→`'`、`,`→`...`），零条语义失败被机械层捕获，50% 的笔记被浪费。

详见 `全链路排查报告/EvidencePointer前置职责边界审计.md`。

**Deterministic-first rule**：任何能由 Harness 从工具调用、Observation、已有 State
或程序日志中确定性恢复的信息，都不得要求 LLM 重新生成。

## 职责边界

| 由谁负责 | 内容 |
|---|---|
| **Reviewer（人工，第一轮）** | 只输出地址：`{window_ref, start, end}`，每题 0–2 个 |
| **Harness / Python** | exact text（切片）、docid、document_sha256、url、relative/absolute char range、evidence_id、attempt_id、全部校验 |
| **Actor（LLM）** | 只做下一个动作的语义判断，不输出任何 source metadata |

Reviewer 可以在 sealed artifact 里留 rationale，但 rationale **永远不会进入模型输入**。

## 数据流

```text
Question Q                          (immutable task)
   ↓
q0 = Q                              (attempt log, 零次 LLM 初始化调用)
   ↓
Search                              (first_observation.collect，一次真实检索)
   ↓
Raw Observation O1                  (冻结、sealed)
   ↓
reference Evidence Selection        (reviewer 只看 Q + q0 + O1)
   ↓
{pointers: [{window_ref, start, end}]}
   ↓
Harness materialize                 (Python 切片)
   ↓
Evidence Pointer State S1           (全部字段为程序派生)
   ↓
A/B next decision                   (不执行任何提出的工具)
```

## 地址与状态

Reviewer 的选择输入：

```json
{"pointers": [{"window_ref": "w_...", "start": 123, "end": 245}]}
```

约束：`0 <= start < end <= len(window.text)`；整数（bool 不行）；不跨 window；
window 必须在当前 observation 中可见；每题至多 2 个。`{"pointers": []}` 完全合法，
且**不等于** blocked / finished / answer-ready。

Harness materialize 后的 State（进入 B 组请求的唯一形式）：

```json
{"kind": "evidence_pointer_state", "evidence": [{
  "evidence_id": "E1",
  "attempt_id": "A0:517",
  "window_ref": "w_...",
  "docid": "...",
  "document_sha256": "...",
  "url": "...",
  "relative_start": 123,
  "relative_end": 245,
  "absolute_start": 9312,
  "absolute_end": 9434,
  "text": "<exact raw substring>"
}]}
```

`text` 永远是 `window['text'][start:end]`，逐字符等于源文本。

## A/B 设计

固定 `Q`、`q0`、`O1`。

- **A** = `Q + q0 + O1`（Raw Observation baseline）
- **B** = `Q + q0 + O1 + 显式选中的 exact evidence`

B 追加一条 user 消息，**不删除、不替换** Raw Observation。处理变量是"是否存在显式
Evidence State"。程序用对象级相等证明：B 去掉 treatment 消息后必须与 A 完全相同。

Actor 只交付 Search / Open / Final Answer 之一或一个合法完整 tool batch。
**不执行提议的工具**，不做 rollout，不做自动 State update。

## 关键性质

- `text` 由切片得到，五种历史机械失败模式在此路径中**结构性不存在**。
- pointer 的地址空间恰好是可见 window body，无法指向未展示的内容。
- 冻结后任何篡改（text / hash / offset / url / 窗口消失）都会在绑定时被拒绝。
- 空 Evidence State 合法。
- reviewer rationale、labels、pairwise 结果、gold、未来轨迹都不在 State 字段里。
- 失败分母完整保留：`api_error`、`blocked_by_auth`、`incomplete` 均计入。

## 使用

```bash
# 1. 冻结题号（在看到检索结果之前）
python -m experiments.research_state.first_observation.run select \
  --qids 517 546 ... --output sel.json

# 2. 一次真实原题检索（零 LLM 初始化调用）
python -m experiments.research_state.first_observation.run collect \
  --selection sel.json --output collection/

# 3. 生成 reviewer 模板（Q + q0 + O1 + char 偏移视图）
python -m experiments.research_state.evidence_pointer.run prepare-review \
  --collection collection/ --output review/

# 4. 人工填写 pointer（只看 Q + q0 + O1，不看 gold / 后续轨迹）
#    然后绑定：Python materialize
python -m experiments.research_state.evidence_pointer.run bind \
  --collection collection/ --selection pointers.json --output state/

# 5. 冻结 A/B 计划
python -m experiments.research_state.evidence_pointer.run plan \
  --collection collection/ --state state/evidence_state.json \
  --profile profile.json --output plan.json

# 6. 执行（复用唯一一条模型调用循环）
python -m experiments.research_state.first_observation.run execute \
  --plan plan.json --output run/
```

第 6 步会产生真实模型费用。**本仓库不自动执行它**；见 `CODEX_TASK.md`。

## 不做什么

- 不实现自动 Evidence Selector（第一轮用 reference pointer，正是为了把 selector
  的错误从 State 价值中剥离）。
- 不实现 statement / hypothesis / gap / next_need / confidence / candidate。
- 不做 rollout、不执行提出的工具、不自动更新 State。
- 不接管默认 Agent；`llm_chat/agent` 未被修改。
- 不修改、不重解释旧的 note 实验结果。

## 相关文件

- `contracts.py` — pointer 校验、materialize、provenance、tamper 检查
- `run.py` — reviewer 模板、绑定、A/B 计划、审计、导出
- `prompts/actor.txt` — A/B 共用 actor 契约
- `../first_observation/NOTE_FIDELITY_BRANCH_STATUS.md` — 旧分支为何暂停
