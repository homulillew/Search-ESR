# VALIDATION — Evidence Pointer v0

## 离线测试结果（本机实际执行）

### 任务指定的两个 glob

```bash
python -m unittest discover -s tests -p 'test_first_observation*.py' -v
python -m unittest discover -s tests -p 'test_evidence_pointer*.py' -v
```

| glob | 运行数 | pass | fail | skip |
|---|---|---|---|---|
| `test_first_observation*.py` | 83 | 83 | 0 | 0 |
| `test_evidence_pointer*.py` | 57 | 57 | 0 | 0 |

`test_first_observation*.py` 的 83 = 44（原 44 题 suite）+ 39（fidelity suite）。
**`ActualArchiveTests.test_pinned_archive_prepares_offline` 实际运行并通过，未被
skip。**

### 完整离线 suite

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

| 运行数 | pass | fail | skip |
|---|---|---|---|
| 335 | 335 | 0 | **0** |

**skip 数为 0，没有需要解释的 skip 原因。**

仓库另有 4 个 pytest 风格模块（`test_chat`、`test_locator_probe`、`test_rollout`、
`test_snippets`）不被 `unittest discover` 收集，它们用 `@pytest.fixture` 且依赖
本机 `/data/model/Qwen3-Embedding-8B` tokenizer。用 pytest 补跑：

```bash
python -m pytest tests/ -q
```

| 运行数 | pass | fail | skip |
|---|---|---|---|
| 390 | 390 | 0 | 0 |

390 = 335（unittest 收集）+ 55（pytest 额外收集）。本机 tokenizer 可用，这些测试
**能**跑，只是不走 unittest discover。

### 被修改模块的旧测试

`first_observation/run.py` 与 `artifacts.py` 被修改。相关旧 suite：

| 模块 | 运行数 | 结果 |
|---|---|---|
| `test_first_observation.py` | 44 | OK |
| `test_first_observation_fidelity.py` | 39 | OK |
| `test_evidence_pointer_regression.py`（新增，覆盖旧路径） | 10 | OK |

其中 `test_evidence_pointer_regression.py` 明确断言旧 note / actor stage 的行为未变：
计划数、arm 分布、status 分布、`initial_model_calls=0`、`tool_executions=0`、
`source_files()` 默认 root 仍是 `first_observation`、未知 stage 仍被拒绝。

## 真实环境调用统计

| 项 | 数量 |
|---|---|
| 真实模型调用（本次任务全程） | **0** |
| 真实 Search | **0** |
| 真实 Open | **0** |
| 检索 / 向量 / 数据库访问 | **0**（检索适配器未导入；`LocalSearch` 未实例化） |
| Mock 客户端调用（测试内） | 全部在测试内存中，不出网 |

所有 evidence_pointer 测试都用合成 window 与内存 fake client。**没有任何 mock
测试被称作 BC+ 效果实验**——本任务交付的是 harness 与 contract，不是效果结论。

## 测试覆盖的契约

### Pointer range（28 项，`test_evidence_pointer_materialization.py`）

- `start=0` 与 `end=len(text)` 允许
- 空 range / 负数 / 反转 / 越界 拒绝
- bool 不能冒充 int；float 拒绝
- 单 pointer 不能跨 window
- 不可见 window 拒绝；重复 pointer 拒绝；>2 个拒绝
- 指针多带字段（如 `quote`）拒绝
- rationale 只能在 case 层，不能进 pointer
- 地址无法指向未展示文本

### Exact source recovery

- `\n\n` 段落分隔符（历史失败点）
- NBSP `£8\xa0million`（历史失败点）
- smart quotes `“…”`（历史失败点）
- 省略号 `…`、制表符、`\xa0`
- Unicode / emoji 🎉 / 中文 / 西里尔
- 重复相同 substring 时取到请求的那一个
- `absolute == offset + relative` 逐字符一致
- provenance 全部由 Harness 采集，reviewer 只给地址
- evidence 对象字段封闭，多字段拒绝

### Provenance / tamper

- window text 改动 → 拒绝
- `document_sha256` 改动 → 拒绝
- `offset` 改动 → 拒绝
- `url` 改动 → 拒绝
- 窗口消失 → 拒绝
- 未篡改 → 通过

### A/B plan（19 项，`test_evidence_pointer_ab.py`）

- 12 job、A/B 各 6、同 case 配对
- **B 去掉 treatment 消息后必须对象级等于 A**
- `validate_ab_plan` 重建整个 plan 并比对漂移；plan 被改 → 拒绝
- treatment 不含 reviewer rationale / 空集理由 / 任何 label 词汇
- treatment 只含 `{kind, evidence}`，evidence 字段封闭
- A 臂不含 `evidence_pointer_state`
- 空集 case 合法且能过校验
- 来自别的 collection 的选择 → 拒绝
- 请求字节上限守卫
- `planned_tool_executions=0`、`max_model_calls=12`

### 执行与失败分母

- 复用唯一一条模型调用循环；`tool_executions=0`，`proposed_tools` 被记录
- 多工具批次**完整保留**，不只留第一条
- B 请求实际携带 evidence，NBSP 端到端不归一化
- source snapshot 与 fingerprint 一致
- **认证失败短路**：1 次请求后剩余 7 个 `blocked_by_auth`，`attempts=1`
- 非 auth 的 API 错误仍逐个重试（行为不变）
- blocked job 不计入 attempts，不产生虚假 usage
- 那次确实发出的请求 usage 未知，`cost_accounting_complete=false`，退出码 2
- 编程 bug（非 API 异常）立即停止批次，不记为模型失败
- 无隐式 resume：原地重跑已存在目录 → `FileExistsError`

## 代码审查清单

| 检查项 | 结果 |
|---|---|
| 新代码没有引入另一个 note paraphraser | ✅ 不存在 statement 概念 |
| LLM 不输出 ref / quote / offset / hash | ✅ Actor 只回 tool batch 或 final text；evidence 全部程序派生 |
| Harness exact source recovery 是确定性的 | ✅ `window['text'][start:end]`，无 fuzzy |
| pointer 不会授权未见全文 | ✅ 地址空间 == 可见 window body |
| `window_ref + span` 只允许当前 Observation | ✅ `check_pointer_selection` 对冻结 case 逐条校验 |
| Raw Observation 完整保留 | ✅ A/B 的 payload 字段级相同 |
| B 没有替代原文 | ✅ B 只追加一条 user 消息 |
| review rationale 没泄漏 | ✅ 结构性不在 State 字段中，并有断言 |
| 旧实验和旧报告没被改写 | ✅ `git diff --name-only` 只含 `run.py`、`artifacts.py` |
| 默认 Agent 没被接管 | ✅ `llm_chat/` 未改 |
| 没有秘密 / `.env` / 数据库 / 权重 / 索引进 commit | ✅ 见下 |

### 提交边界扫描

提交前检查：归档目录不含 `*.sqlite`、`*.pkl`、`*.safetensors`、`*.bin`、
`.env`、`*key*`、`*token*`。

## 已知限制

- `prepare-review` 把完整 observation 写进 reviewer 模板；模板本身是明文 artifact，
  不含 gold，但"reviewer 只看 Q+q0+O1"是流程约束，不是技术强制。
- reviewer 的"不看未来轨迹"同样是流程约束。模板里没有放任何未来信息。
- 空集与"偏题"在输入审计层需要人工判断；程序只校验地址合法性。
- `show_window` 的 100 字符切宽是 UI 常数，不参与任何校验或 State。
- Actor 的 `allow_tool_calls_with_stop` 沿用 profile 设置；本任务未改采样语义。
- 未实现自动 selector（设计决策，见 `README.md` "不做什么"）。
