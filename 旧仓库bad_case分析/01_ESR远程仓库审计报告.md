# ESR 远程仓库审计报告

审计日期：2026-09-17。目标：为当前 `qwen3.7-flash API + BC+ + pure forward harness` 研究确定可验证的起点。

审计对象：[homulillew/ESR-GRPO-Code-L](https://github.com/homulillew/ESR-GRPO-Code-L)，固定提交 **`253beb48865ffa14cd9b0861e83fef0f45b7cd67`**。下文源码链接均固定至该版本。

## 1. 结论

原型讨论中的方向值得继续：外部工作记忆、可追溯证据、无进展触发重新规划、验证后自动停止。但旧仓库的实验不足以证明这四项机制已经有效，也不足以将主要失败统一归为弱模型能力不足。

本次最重要的发现是：

1. **旧 baseline 存在实质性工具缺陷。** 100 条归档中 447 次 `read_evidence` 全部非法；baseline 没有 `update_state`，而读取又要求先在 TaskState 登记。旧 ESR 与 baseline 的差异不能直接解释为记忆或验证机制的收益。
2. **离线重放的观测记录与真实 verifier 输入不一致。** 脚本构建、保存了 chunk 视图，却将全文 Evidence 传给 verifier。不能依据该输出中的 `view_evidence` 判断验证器“看到了哪些文本”。
3. **在线同视图机制也有边界漏洞。** 同一文档由不同 query 重复打开时复用 evidence_id，但新 open 用新 query，verify 仍用首次 query 重建视图。不可变全文不等于不可变观察。
4. **格式错误会进入语义 Gap，确有代码和原始轨迹证据。** 100 条 ESR 中 30 次验证记录标记 unparseable，涉及 19 个 episode。
5. **120、186、324 是不同层次的诊断题。** 120 有精确可复核的长文档可见性问题；186 涉及证据组合、指代消歧和解析失败；324 涉及目标实体与中间线索实体混淆。不要将其压成单一“收敛能力”解释。

因此，下一步应先建立工具正确、输入可审计的当前强 API 基线，再验证“文档前缀 vs 查询相关 chunk”的单因素改动。暂不移植旧 ESR 的整套状态门禁与 recovery guidance。

## 2. 审计范围与证据等级

已阅读核心 `environment.py / rollout.py / retrieval.py / verification.py / models.py / store.py`、`tests/test_environment.py`、主要分析报告、迭代日志、强策略驱动和重放脚本；扫描归档 batch 的 SQLite actions/state/metadata，重点检查 120、186、324、170、416、533、1044；检查两个 12 题 JSON 结果集。

证据按以下层次区分：

- **A：本次复核。** 源码直接支持、SQLite 直接计数，或本次合成输入复现。
- **B：归档日志支持。** 有当时的结果/解释，但缺少完整请求快照、版本绑定或对照条件。
- **C：待检验假设。** 对失败原因或新设计收益的解释。

本次未运行旧模型服务，未重跑真实 BC+ benchmark，未重新判定 100 条答案的正确性。只运行了原仓库 14 个环境单元测试和 9 个离线诊断 probe，均无需远程 API。Probe 是复现缺陷或边界的检查，不是九项“功能通过”。

仓库 [README](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/README.md) 明确说明它是复制形成的归档快照；源代码与历史运行产物不能假定对应同一个运行版本。引用旧日志中的修复前现象时，不能用当前 HEAD 的实现反推当时行为。

## 3. 真实 forward 调用链

```text
AgentRunner.run
  ├─ 保留 messages
  ├─ environment.render_context(mode)
  │    └─ TaskState + 所有 evidence_sources + next_step_guidance
  ├─ OpenAIChatPolicy.next_turn(messages, context)
  │    └─ API：system prompt + 历史 + 当前状态 + tools
  ├─ 解析 function arguments → ToolCall
  ├─ execute_tool / execute_parallel
  │    ├─ search → EchoRetrievalClient → 外部 BM25 检索服务
  │    ├─ open_page → 全文入库 + query-ranked chunk 视图
  │    ├─ update_state → coverage / visible-original / support 门禁
  │    ├─ verify_answer → 重建 supporting Evidence 视图 → 独立 verifier API
  │    └─ submit_answer → 门禁通过后写 submitted_answer
  ├─ 追加工具结果和 recovery 提示
  ├─ 消息过长时裁剪历史
  └─ 已提交 / 回合上限 / 无工具输出重试耗尽等条件结束
```

来源：[AgentRunner](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/src/esr_grpo/rollout.py#L359)、[工具环境](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/src/esr_grpo/environment.py#L91)。

### 3.1 模型承担的工作

模型除了选择 query、文档和候选，还要填写 `search_action_id`、Evidence ID、finding、supporting_evidence，选择何时更新、验证和提交。

提示词要求按流程推进，环境同时生成 next_step_guidance，runner 又处理重复验证等特殊情况。多处控制同一流程确实存在，但 `_search_open_break` 本身是**返回引导文本**，并不直接执行 top-1 open。旧文档中的“强制 open”要区分提示语气与运行时强制。

### 3.2 两种“记忆”仍然混在一起

TaskState 的 `evidence_directory` 要覆盖所有已归档 Evidence；`update_state` 实际是 `old_directory + patch` 合并，**不是每次必须重发全部旧 finding**。真正的负担是：每篇新打开的材料最终都必须登记，包括无关材料，且没有从工作目录删除的路径。

`_visible_evidence_inputs` 在 update/verify 后清空。旧 evidence_id 通常仍然存在；“stale”更多表示修改 finding 的可见性前提不满足，而非 ID 失效。提示词若把它描述为“必须用新 ID”，可能使模型误解对象生命周期。

来源：[update_state](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/src/esr_grpo/environment.py#L334)。

### 3.3 已有压缩，但没有有界工作状态保证

`_maybe_compact` 超过约 28,000 序列化字符后，保留 system、原问题、压缩提示和最后 5 条消息。它不是语义摘要，也没有限制不断增长的 TaskState/evidence_sources；动态 context 在 API 请求前另行拼入，不计入该压缩触发阈值。

尾部按消息条数裁剪还可能留下没有对应 assistant tool_calls 的 tool 消息，已在本次 probe 复现。不能把“有 compact 函数”视为长程上下文问题已经解决。

来源：[压缩实现](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/src/esr_grpo/rollout.py#L537)。

## 4. 原始统计复核

统计对象仅为 `results/exp1/exp100_merged_{baseline,esr}/stores`，各 100 个 SQLite。**次数是 actions 表中的动作尝试数，含非法动作，不是模型 API 调用数，也不是成功执行数。**

| 指标 | Baseline | ESR |
|---|---:|---:|
| episode | 100 | 100 |
| 已提交 | 100 | 19 |
| 未提交 | 0 | 81 |
| search 尝试 | 1208 | 1067 |
| open_page 尝试 | 182 | 279 |
| open_page 非法 | 64 | 7 |
| read_evidence 尝试 | 447 | 150 |
| read_evidence 非法 | **447** | 95 |
| update_state 尝试 / 非法 | — | 340 / 111 |
| verify_answer 尝试 / 非法 | — | 232 / 48 |
| 全部动作平均数 | 19.37 | 20.87 |
| 从未尝试 open 的 episode | **41** | 0 |
| 未提交且尝试过 verify | — | 78 |
| 曾 supported 但最终未提交 | — | **0** |

复算见 [复核结果.json](复核结果.json)。ESR 共 261 个非法动作。30 个合法 verify 动作的 rationale 标记 `unparseable`，涉及 19 个 episode；**legal=True 只表示状态转换成功，不能说明验证器返回了有效语义判断**。

### 4.1 哪些旧统计可以保留

19/100 提交、81 未提交、其中 78 尝试验证，与旧报告一致。旧报告列出的 15/100 ExactMatch、17/100 人工语义复核，以及 baseline 17/100，可作为作者报告引用，本次没有独立重判这些正确性数字。

### 4.2 哪些解释需要降级

- 17/19 的提交内正确率与 baseline 17/100 是不同条件分母。前者体现选择性提交，不能说整体准确率提高了五倍。
- “未提交但尝试过 verify”不等于“证据齐备、仅差收尾”；空候选、错材料、解析错误也进入该集合。
- 全量 100 条中没有 supported 后未提交，故 auto-stop 的收益不能从这批直接推断；其他 retry 批次确实存在此类案例。
- 旧文档 baseline 无 open 写为 49 条，本次对应归档为 41 条。过程语言错误的数量在不同文档中又出现 30 与 53 两种口径，不能直接合并使用。
- `_gap` 以文本匹配复用 ID；改写描述时旧 ID 消失、新 ID 出现，会被记为旧 gap resolved。**resolved_gap_ids 不是语义问题已解决的可靠标签。**

来源：[原 ESR 报告](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/analysis-L/BADCASE_ESR_100.md)、[Gap 更新逻辑](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/src/esr_grpo/environment.py#L520)。

## 5. 关键实现问题

### F1. Baseline 的 read_evidence 无法正常使用【A，历史频率已计数】

Baseline tools 包含 read_evidence，不包含 update_state。环境的 read_evidence 却要求 TaskState 已存在且 ID 在 directory 中。正常 baseline 没有建立该状态的工具，因此打开文档后重读仍被拒。

本次合成调用复现，历史 447 次 read 全部非法。它会影响长文阅读、历史压缩后的恢复和预算使用。不能据此把 baseline 的阅读失败主要归为模型能力不足。

来源：[baseline tools](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/src/esr_grpo/rollout.py#L193)、[读取门禁](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/src/esr_grpo/environment.py#L198)。

### F2. schema 仍声明已删除的 offset【A，接口不一致】

rollout 中 ESR 和 baseline 的 read_evidence schema 都仍带 offset；environment 的签名和局部 ESR_TOOL_SCHEMAS 已移除。系统提示又仍称 open 返回头部截断。调用者按公开 schema 生成 offset 会被拒，不能把这类错误全算模型格式能力问题。

原有 14 个环境测试全部通过，但测试只检查 Python 方法签名，未核对对外 OPENAI_TOOLS。

来源：[对外 schema](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/src/esr_grpo/rollout.py#L120)、[环境测试](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/tests/test_environment.py#L247)。

### F3. 同一 Evidence ID 可以对应不同实际观察【A，合成复现】

第一次 query A 打开 d1，建立 e1，绑定 A；第二次 query B 打开同一全文，去重复用 e1，但向模型返回 B 的 chunks。verify/read 根据 e1 初始 search_action_id 重建 A 的 chunks。

本次 probe：最后 open 显示 `beta fact`，verifier 收到 `alpha fact`。两个视图都可能在历史上被看过，但模型当前 claim 对应的观察与审核输入已脱节。外部 chunk 服务波动或 fallback 切换还可能引入未曾展示的文本，后者是代码路径风险，未做历史频率统计。

应固定每次展示的 immutable chunks/hash，再让 citation 指向该文本。不能依赖“以后重新跑同一个检索请求”保证输入一致。

来源：[open 去重及观察构造](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/src/esr_grpo/environment.py#L151)、[verify 重建视图](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/src/esr_grpo/environment.py#L471)。

### F4. 离线 replay 记录 chunk，实际验证全文【A，合成复现】

`replay_shortboardA.py` 先生成 view_evidence，但真正调用的是：

```python
verifier.verify(question, answer, [store.get_evidence(e) for e in support])
```

本次 probe 的日志视图只有 alpha，verifier 输入却同时含 alpha 与 beta。该脚本不能证明“仅将验证观察改成 chunks”的效果。现有 JSON 缺少真实请求 body，不能确定它由哪个脚本版本生成，因此结论应为**当前可执行重放路径有错，历史结果的输入口径待核实**。

来源：[replay_case](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/analysis-L/replay_shortboardA.py#L73)。

### F5. 格式、上下文与语义失败混合【A】

Verifier JSON 无法解析时，返回 needs_revision，并生成“整理答案和证据”的 Gap；超过字符预算同样返回语义修订。它们随后被写入研究状态，可能诱发无意义补证。

HTTP 等异常在 environment 中不会直接修改语义状态，这是已有改进；但所有异常被笼统描述为瞬时故障并要求模型重试，持久配置错误也可能反复消耗研究动作。需分别表示 FORMAT / CONTEXT / INFRA / SEMANTIC_REPAIR，前三者由 runtime 处理。

来源：[verification.py](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/src/esr_grpo/verification.py#L62)。

### F6. 提交控制与运行时边界【A，部分未证实历史触发】

- supported 后不会自动停止，仍需 model-facing submit，已复现。
- 无语义变化的 update_state 也会生成新版本并恢复 unverified，能够绕过“同一状态不重复验证”的意图，已复现。
- `execute_tool` 使用 getattr，ESR 模式没有工具白名单；`render_context` 的 allowed_actions 还包含 FINISH。即使 OPENAI_TOOLS 不声明 finish，若输出该调用，仍能无验证提交，已复现。**未发现这里已被用来解释某个历史失败/成功，属于协议保证缺口。**
- baseline 预算结束会从 assistant 文本提取答案强制 finish，ESR 没有等价出口。提交率 100% 与 19% 部分来自不同终止协议。

来源：[dispatch](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/src/esr_grpo/environment.py#L646)、[runner 终止处理](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/src/esr_grpo/rollout.py#L472)。

### F7. 预算单位不统一【A，代码风险】

AgentRunner 限制的是 policy turn，一个 turn 可以含多个工具；soft deadline 计算的却是 actions 数，二者不能直接设成同一个“轮数”。verifier API 以及网络重试的成本也不由动作总数完整表达。另有一次响应超过 max_parallel_calls 时，assistant 中保留所有 tool_calls、只执行前几项的消息配对风险。

来源：[runner](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/src/esr_grpo/rollout.py#L410)、[soft deadline](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/src/esr_grpo/environment.py#L891)。

## 6. 对复用的判断

| 旧组件 | 处理建议 | 原因 |
|---|---|---|
| append-only store、全文 hash、动作审计思想 | 保留思想，简化实现 | 可用于可追溯实验，不必携带训练 token_span |
| EvidenceSource、KnownFact 类数据结构 | 小范围改造 | citation 应绑定 immutable chunk，而非动态文档视图 |
| 检索协议与 get_doc_chunks 思路 | adapter 化 | 当前已具备 Qwen3 向量检索和本地 SQLite，无需回迁旧 BM25 服务 |
| verifier 的独立 context | 保留 | 必须改输入快照、错误类型和报告结构 |
| 全目录 coverage、visible-original 时序门禁 | 不直接移植 | 把归档规模变成模型记账负担 |
| next_step_guidance 与多个 breaker | 不直接移植 | 当前强模型是否需要，需重新实测 |
| verify/submit 两个 model-facing 工具 | 在新 harness 中内部化 | 作为设计假设单独测量，不提前宣称提升准确率 |
| 旧 baseline runner 和历史总体对比 | 保留为历史资料 | 已有工具缺陷与终止协议混杂，不作新的公平对照 |
| 训练、GRPO、credit assignment 结构 | 本研究不纳入 | 与纯 forward 研究目标无关 |

## 7. 本次交付与下一步

- [02_典型bad_case与证据边界.md](02_典型bad_case与证据边界.md)：逐题、逐版本分析。
- [03_当前项目的最小实验路线.md](03_当前项目的最小实验路线.md)：第一轮如何控制变量。
- [复核脚本.py](复核脚本.py)、[复核结果.json](复核结果.json)：本次原始计数和合成 probe。

复核命令：

```bash
git clone --depth 1 https://github.com/homulillew/ESR-GRPO-Code-L.git /tmp/esr-audit
# 如远程 HEAD 已变化，应先 checkout 本报告固定的 commit。
python 旧仓库bad_case分析/复核脚本.py /tmp/esr-audit
PYTHONPATH=/tmp/esr-audit/src python -m pytest -q /tmp/esr-audit/tests/test_environment.py
```

本次只新增审计资料，没有修改当前聊天/检索实现，没有训练，也没有调用任何远程模型。
