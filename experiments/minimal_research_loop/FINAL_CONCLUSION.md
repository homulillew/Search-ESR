# Minimal Research Loop — 最终结论

基线：远程 `experiment/evidence-fidelity-loop`，`9cf044ddbfad022cb8e5c0a1e689b715b84421b3`。本轮使用 DeepSeek `deepseek-flash`、`max_retries=0`；历史实验目录未改写。每阶段请求前的 HEAD、数据、prompt、顺序、工具/索引及失败规则见各自 `freeze.json`。V1 的自然 Reader Finding 与逐条前缀审查在 Verify 调用之前分别冻结。所有失败和原始响应均保留。C1 是独立局部诊断，实际在 F1 工具执行之前完成；其选样、标签与决策没有使用 F1 结果。

## 阶段决定

| 阶段 | 主要结果 | 决定 |
| --- | --- | --- |
| V1 Verify Necessity | Direct 来源精度 53/55；Verify 53/54；完整 Claim 精度分别 47/55、47/54 | A/B 必要性判据处于灰区；两种 Claim-commit 策略均未达到 R1 入场标准 |
| F1 Frontier Control | Useful Evidence 15/24 → 16/24；A1 独赢 4、反向恶化 3、净增 1 | 不增加显式 Selector；保留 `gap_id` 作为可行但未证实有用的轻量表达 |
| C1 Gap Closure | Binary 40/40 判断正确；missing-first 39/40 有效、1 次格式失败 | 两者通过局部数值门槛，选择较简单的 Binary |
| R1 Single-Gap Loop | V1 无可部署 Claim-commit 策略 | 按预注册 gate 不运行；不报告集成收益 |

F1 使用 24 个真实历史 W 在同一语料中重建的**单窗口诊断前缀**，并非完整历史运行轨迹。C1 使用历史已接受且有 W 绑定的 Claim 组装**局部闭合诊断包**，并非原问题完整解答。每个 qid 的多个单元相关；所有比例是描述性结果，不能视为独立样本推断。

## 对 24 个问题的回答

1. **自然 Reader 的 Evidence precision：**52 个真实 Observation 包、12 个 qid，经一次 Reader 调用得到 55 条 Finding，覆盖其中 10 个 qid。前缀审查判定 53/55（96.36%）有来源支持；真正同时有来源支持、与当前 Gap 相关且新颖的为 47/55（85.45%）。
2. **Verify 减少的真实错误：**两条不受 W 支持的自然 Finding 中拒绝一条，减少 1/2；另一条错误的时间绑定仍被接受。基线错误数仅 2，未达到预设 B 判据要求的至少 5 条。
3. **Verify 是否值得成本：**目前不值得部署为独立必经步骤。它增加 55 次调用、46,126 token 和 83.54 秒的响应时长总和；提供者报告的 prompt cache 命中为 768/33,502（2.29%）。它只把来源精度提高 1.79 个百分点，完整 Claim 精度仍低。
4. **删除 Verify 后 Claim 精度是否足够：**不足。Direct 的完整 Claim 精度为 47/55（85.45%），低于冻结的 95% R1 入场线；Verify 也只有 47/54（87.04%）。
5. **Verify 的主要错误：**一条 false accept、零条 false reject；另有六条来源支持但偏离当前 Gap 的 Finding 全被接受。后者不是来源判断错误，却仍会污染 Claim State。
6. **显式 Research Frontier 是否必要：**F1 没有证明必要。Selector 24/24 选出有效 open `gap_id`，与 reviewer preferred 标签一致 16/24，但没有跨过因果收益门槛。
7. **是否提高真实 Useful Evidence：**只从 A0 15/24 升到 A1 16/24。四对 A1 独赢，三对反向恶化，净增一对；所选 Frontier 真正得到推进仅 11/24。工具分布变化不能代替证据收益。
8. **Selector 是否值得额外调用：**否。增加 24 次模型调用；A1 Selector 加 Actor 共 193,475 token，比 A0 Actor 的 163,708 多 29,767 token。模型调用时长总和 A1 为 628.01 秒，A0 为 554.81 秒，而门槛要求净增至少 4 且反向恶化至多 1。
9. **Frontier 是否只需 `gap_id`：**模型能稳定输出并让 Harness 校验一个 open `gap_id`，无需额外持久控制字段。但这个表示的可行性不等于 Selector 有运行价值。
10. **Binary premature close 是否复现：**没有。在 C1 的 20 个 open 局部包上为 0/20；历史运行中 2/6 的 premature close 不能由这批组装的 Claim-only 诊断包推翻。
11. **Missing-first 是否改善 closure：**没有。C0 的 premature/missed 均为 0/20，C1 premature 0/20、missed 1/20。C1 对 20 个 open 包的 missing 描述均准确，但一次输出 `missing="None"` 与 `resolved` 冲突，被冻结的 Harness 规则拒绝。
12. **是否需要持久 `missing`：**不需要。即使临时 missing 描述准确，也没有超过 Binary 的闭合收益；临时推理输出不进入 State。
13. **Single-Gap Loop 的 Useful W→valid Claim 转化：**未测量；R1 因 V1 gate 未运行。不能用 V1 的 Finding 精度替代该集成指标。
14. **Claims 是否减少重复检索：**本轮未做 R1 连续动作，不能判断。
15. **pending-W-first 是否解决已有证据仍继续 Search：**未测量，不能声称解决。
16. **immediate stop 是否消除 resolved 后额外工具：**未测量。规则已定义，但没有 R1 运行证据。
17. **当前主要瓶颈：**首先是 Reader 输出能否成为当前 Gap 的 Claim：六条来源支持 Finding 偏离 Gap，来源 Verifier 无法识别。F1 同时显示 Query/Source selection 与局部定位制约 Useful Evidence；九次双工具 Actor 输出暴露动作格式问题。C1 的局部 Binary closure 不是本批主要瓶颈。
18. **极简 State 是否足够：**局部实验支持只保留 Question、来源绑定 Claims、语义 Gaps、可选 `gap_id` Frontier 与 Working Hypothesis 的设计边界；由于 R1 未运行，尚无端到端充分性证据。D#/W#/来源日期、边界、预算与 stop 仍归 Harness。
19. **是否需要恢复 persistent TestCard：**没有证据要求恢复。
20. **是否需要句子/字符级 Evidence Pointer：**没有证据要求。现有真实 W 单位足以揭示本轮的主要错误类型；更细 pointer 的收益未测。
21. **是否进入真正 multi-Gap Frontier runtime：**暂不进入。F1 非 ceiling，仍只有净增 1 对、反向恶化 3 对，未通过预设门槛；诊断前缀也不是完整轨迹。
22. **是否进入更长 rollout：**暂不进入。应先获得可靠的当前 Gap Claim-commit 方案，再验证四动作 R1。
23. **是否已有 ESR-GRPO 依据：**没有。当前机制和集成 gate 尚未打通。
24. **是否继续禁止 hard Search/Find/Open gating：**是。F1 没证明额外软 Frontier 稳定改善证据；没有资格把单一模型判断升级成工具硬屏蔽。

## 核心研究判断

模型判断有资格进入持久 Research State 的条件，至少包括：事实性 Claim 与当前 W 直接对应、与当前未闭合 Gap 有关、相对已有 Claim 新颖，且由 Harness 绑定来源与 ID。本轮来源 Verifier 对第一项有有限帮助，却完全不能保证第二、三项。`gap_id` 选择能表达当前方向，但只在后续行动确实取得新证据时才具有控制价值；F1 未给出足够收益。Binary closure 在本批稳定 Claim 包上可用，但不能弥补上游错误 Claim。

下一步应针对**Claim 的 Gap 相关性/新颖性与 Source 路由**做独立、预冻结的诊断，再判断是否可运行 R1。当前不恢复更多持久字段，也不引入硬工具门控。
