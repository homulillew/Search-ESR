# V3 最终结论：服务端完整 Schema 能力未通过，按 Gate 停止

## Material Passport

执行日期：2026-09-26。基线 `32de7c8`，分支 `experiment/goal-residual-control-v3-admission-structured`。本轮完成设计审计、离线验证及真实 provider capability 测试；未执行 Admission Replay / G4 / G5。这里的停止是任务书规定的能力 gate，不是因研究效果弱而中止。

## 已完成与停止原因

首个提交 `52f8911` 只包含 [V3_DESIGN_AUDIT.md](V3_DESIGN_AUDIT.md)，先核对两项混杂及前序 Gap-conditioned extraction 证据，再实现测试。39 个初始离线测试及两个 schema 等价测试通过。24 个历史 preflight 请求已机械选定并冻结，覆盖全部十种要求的输出形态，尚未发送。

实际完成 **13 次 capability probes**，同一 `deepseek-flash`、零重试、最多四并发。观察到两个关键反例：

- beta strict function calling 对合法的 `maxItems=2` schema 返回 `[1,2,3,4]`。
- Responses API 对 `minItems=3,maxItems=2` 的不可能 schema 返回 completed 状态和 `[1,2,3]`，没有拒绝或失败。

此外，测试过的完整 Actor schema 及等价 union 表达被服务端拒绝。部分简单 schema、编译后的 Updater schema、Goal schema 能返回合法对象，但不足以证明完整合同得到服务端保证。**本轮无法完成 Fix B，因而不能把后续实验建立在“serialization failure 已退出研究链”的假设上。**

没有自动降级 JSON mode/prompt-only，没有放宽 parser、修改数组上限、改输出对象、关闭 thinking、换模型或重采样。Fix A 完成设计审计，尚未实施或验证 U1 live admission；不能宣称 incidental rate 已下降。

详见 [完整能力报告](structured_output_preflight/CAPABILITY_REPORT.md)，其中区分简单正例、satisfiable schema 反例、故意不可能的负对照、API 错误以及 local semantic consistency。

## 对 17 个最终问题的回答

1. **Constrained generation 是否真正消除 serialization failure？** 未达到。当前测试无法确认完整 exact schema；strict function 出现直接数组越界反例。13 次诊断含不同 schema 和一个故意不可能的负对照，不能把 4 个 schema-valid 输出换算为研究节点有效率。
2. **是否改变明显语义行为？** 未测量普通研究请求的 paired semantic effect。24 个历史请求未发送；合成探针的语义冲突不能替代 Uc canary。编译 Updater 探针的空 `set` 仅说明 schema-valid 仍可能违反本地语义规则。
3. **Incidental rate 从多少降到多少？** v2 为 369/504＝73.21%；v3 未测量，没有下降幅度。
4. **Useful-fact admission recall 是否下降？** 未测量；没有 U1，不把零 admission 当作高 precision 或低 recall。
5. **State growth 是否减慢？** 未测量；v3 没有在线状态更新。
6. **Workspace→Claim 的关键事实遗漏是否减少？** 未测量。设计中明确纳入该指标，但尚无干预结果。
7. **Oracle vs Online 差距是否缩小？** 未测量；原 20 transitions 未重跑。
8. **Hypothesis rejection 是否影响下一行动？** 未测量；未执行 v3 Actor→Observation→Updater→Actor 链。
9. **L0/L1/L2 Resolution 各多少？** v3 均为未执行，不是 0/10。v2 的 1/10、1/10、1/10 继续保留，不能作为 v3 结果。
10. **Premature stop 各多少？** v3 未测量；v2 3/4/2 未被本轮更新。
11. **Evidence Progress 如何？** v3 未测量，真实研究工具调用数为零。
12. **成本如何？** 13 次诊断，6 次 HTTP 200 报告 3,183 total tokens，其中 1,002 input、2,181 output（含 2,064 reasoning）。7 次 HTTP 400 未报告 usage，不能证明其零成本。已报告 cache 命中为 0/1,002＝0%；没有研究阶段成本。
13. **Goal Residual 是 acquisition、stopping 还是无独立增益？** 本轮无新结论。v2 的停止信号与未证实最终收益继续有效，未被能力探针重新检验。
14. **Persistent Gap 危害是否观察到？** 本轮未测量，不支持新的有害性判断。
15. **Direct Replan 是否足够？** 本轮不能判断；不以 capability failure 推断 controller winner。
16. **Minimal semantic state 是否仍可保持 Claims + Working Hypothesis？** 设计保持这两个可变语义层，Original Question 始终不可变且 authoritative；Current Gap 只拟作为临时 admission context。这里是未改变的设计边界，不是新的端到端充分性证明。
17. **下一 dominant failure 是什么？** 当前执行阻塞是 provider 与所需完整输出 contract 的能力不匹配/未证实。不能跳过这一 gate，把 v3 的下一语义瓶颈宣布为 Actor、Retriever 或 Localizer。历史 admission 相关性问题仍值得修复，但效果需要在合格接口条件下另行测量。

## 冻结、失败与历史保护

| 阶段 | 状态 | 新请求 |
|---|---|---:|
| Design audit / offline tests | 完成 | 0 |
| Primary + strict fallback capability | 完成，保留失败 | 7 |
| 等价 schema / enforcement 诊断 | 完成，Gate 失败 | 6 |
| 24 历史请求 structured preflight | 已冻结，未执行 | 0 |
| Admission Replay U1 / Uc | 未执行，capability blocked | 0 |
| Transition Replay v3 | 未执行 | 0 |
| Three-round loop v3 | 未执行 | 0 |

两次 capability freeze 均在调用前提交；扩展诊断是新 ID、新协议和新 freeze，不替换初始失败。全部原始响应和错误保留；无失败删除、无重试、无模型输出修复。完整性核对通过：**519 个受保护历史文件无变化**，工具/模型/状态/horizon 未改。

本轮未达成最终干净 State substrate 上的 controller 重比较；达成的是一个可复核的停止决定。下一步需要先明确能满足完整 contract 的服务端机制或另行授权接口约束调整，不能把 JSON 合法性冒充完整 schema conformity。

## 产物

- [设计审计](V3_DESIGN_AUDIT.md)、[协议](PROTOCOL.md)、[原始冻结说明](FROZEN_STATE.md)。
- [能力报告](structured_output_preflight/CAPABILITY_REPORT.md)、[全部诊断指标](structured_output_preflight/CAPABILITY_METRICS.json)。
- [离线检查](structured_output_preflight/OFFLINE_REPORT.md)、[等价表达诊断协议](structured_output_preflight/equivalent_schema_probe/PROTOCOL.md)。
- [历史及冻结完整性](analysis/INTEGRITY.json)。各未执行 stage 的 `NOT_RUN.json` 明确记录原因。

官方能力说明引用已集中在能力报告；最终 gate 以本轮归档的真实响应为证据，不以产品文档或模型自行描述代替观测。
