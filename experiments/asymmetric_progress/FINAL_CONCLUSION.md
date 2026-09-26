# Asymmetric Research Progress：最终结论

## 本轮判断

**单关系 instruction 有明显方向性收益，但尚未达到控制接口门槛；当前 Closure Audit 过度拒绝真实闭合，LA 没有优于 LL。一次有界 materiality 探索减少了部分过度拒绝，同时重新引入错误闭合。正式 C1/C2/C3 全部失败，不进入 Frontier。**

远程基线已 fetch 核验：`origin/experiment/dynamic-progress-blockers`，HEAD `094b87382668fa21e68290eed3050d5f8e5f979a`。新分支：`experiment/asymmetric-progress-closure-audit`。标签/机械 canary 冻结于 `716f2b0`；198 次正式请求运行于 `bf1932d`；24 次唯一探索运行于 `b9a5936`。每次 exact HEAD、请求、响应、失败和 usage 均保留在各阶段 journal。

## 证据与适用范围

主集 24 个 exact Q+Claims 未使用 checkpoint、9 qids、每 qid≤4；19 unresolved + 5 resolved。排除历史 Frontier F1、Dynamic Progress primary/exploration 输入，原 Claims 不增删改写。剩余 44 个状态中只有这 5 个 fresh resolved，集中在 2 qids；严格 near-closure 主集只有 1 个/1 qid，没有达到期望的 10–12 个/5 qids；material inter-Claim conflict 仅压力集覆盖。

这是对未使用状态的目的抽样，且有同题相近轨迹，不能把 replicas 当独立样本。全部标签在任何本轮调用前冻结，review 由单一 Codex 依据 Q+Claims 执行，没有第二 reviewer；opaque IDs 不等于完全盲审。尤其 over-demand 的结论以预先冻结、沿用历史的 materiality 定义为准。

| 主实验指标 | L0 | L1 | Audit |
|---|---:|---:|---:|
| 有效输出 |46/48|48/48|48/48|
| False closure |0/38|0/38|0/38|
| Correct closure |7/10|10/10|4/10|
| 有效 blocker presence |34/38|38/38|37/38|
| Blocker precision |60/111 = 54.1%|90/109 = 82.6%|37/44 = 84.1%|
| 充分 closure certificate |7/7|8/10|4/4|

L1 相对同 replica L0 只有一次新增 critical regression：引入 Claims 外的 zodiac Horse 判断；未触发“≥3 次/≥2 qids”回退门槛。C1 失败于 precision。C2 失败于 correct closure 和 blocker precision。C3 失败于正确停止、decision accuracy 及对 LL 的非劣要求。`analysis/GATE.json` 保留全部检查。

| 主集 STOP policy | False stop | Correct stop | Missed stop | 有效 decision accuracy |
|---|---:|---:|---:|---:|
| L |0/19|5/5|0/5|24/24|
| LL |0/19|5/5|0/5|24/24|
| LA |0/19|2/5|3/5|21/24|

## 对任务书 20 个问题的回答

1. **Single-relation instruction 是否 fresh-confirm？** 方向性改善得到 fresh bank 支持：precision 从 54.1% 到 82.6%，有效 blocker presence 38/38，correct closure 10/10。但未通过 90% precision gate，不能称完整确认。

2. **L1 precision 是否达到下游控制水平？** 未达到冻结门槛。仍有 14 个 broad units、3 个冗余要求，以及 unsupported/已支持关系被写成缺口等错误。把 status/ref fidelity 一并计入时为 74/109=67.9%。事后若只宽免 breadth 错误，上界可达 104/109=95.4%，但这是敏感性诊断，不能替换单关系 rubric 或改变 gate。

3. **False closure 是否仍集中在 strong-candidate states？** fresh 主集各 arm 均为 0，无法估计其分布；独立压力集 L0 两次 false closure 都在 P19，支持这一局部诊断。唯一探索新错误发生在 P17，也是用一个强 plot match 提前闭合。不能据此作总体频率结论。

4. **Audit false closure 是多少？** 正式主集 0/38；独立压力集 0/16。materiality 探索为 1/12，单独报告，不混入正式分母。

5. **能否稳定发现 quantity / role / temporal / event-binding blocker？** 在这些样本中，正式 Audit 对 P17 的 total seasons、P19 的 roommate、S07 的 count-to-feature、S05/S06 的动画角色均为有效拒绝 2/2。fixture/event binding 有一次 A24 unsupported presupposition，因此不能称全面稳定。有限 qids 和两次 replicas 限制结论。

6. **Audit 是否更容易 over-demand？** 主集 Audit 6/48，L1 3/48，L0 7/48；相对 L1 更严重，相对 L0 并非更多。Audit 的 6 次全部落在 10 个真实闭合控制上，直接损害停止。压力集游戏控制 Audit 也拒绝 2/2。

7. **Audit correct closure rate？** 主集 4/10=40%；压力集 0/2。不能用 0 false closure 掩盖这一损失。

8. **Certificate 是否充分？** 正式主集 4 个确认的 certificate 均充分（4/4），压力集无确认，分母为 0，不记 100%。这只反映它选择确认的少量样本。探索只有 8/10 充分：一条遗漏 material relations 而 false close，一条在正确闭合时仍强化了未观察的 episode 相对位置。

9. **LL 修复多少 false closure？** 按冻结配对，主集和压力集 L1-primary 都没有 false stop，LL 修复 0，不能判断其修错收益。主集保留 5/5 true stops；压力集把唯一正确停止变成 missed stop。

10. **LA 修复多少？** 同样修复 0 个 L1-primary false stop。主集额外损失 3 个 true stops，压力集损失 1 个。不能拿 L0 的错误当成 LA 相对 L1 的增益。

11. **Audit 收益是否超出第二次采样？** 没有观察到。主集 LA 比 LL 更差，压力集 LA=LL。两者触发率相同，Audit reasoning 成本更高。L1-primary 没有错误停止也造成安全收益的 floor effect。

12. **P17/P19 是否稳定修复？** 正式 Audit 两者都有效拒绝 2/2。P19 的 L0 仍 false close 2/2，而 L1 已独立修复 2/2。P17 当前 L0 也正确拒绝 2/2，历史失败没有重现，不能归因于 Audit；探索又在 P17 false close 1/2，因此不支持跨 prompt 的稳定解决。

13. **Audit blocker 能否直接作为 Frontier 输入？** 只有内容和支持关系合格的单个 blocker 才是候选。本轮正式主集 precision 84.1%，尚有 over-demand 与 unsupported fixture premise；直接无筛选传入不可靠。Blocker→Need 没有运行，不声称 downstream 收益。

14. **FULL 是否仍只适合 closure 边界？** 不支持每轮 FULL。其 closure 边界用途也只是候选；正式 Audit 未出现 false closure，主要失败是过度拒绝，未满足任务规定的 FULL 扫描不足触发条件。本轮未运行 FULL，不能声称其能解决当前问题。

15. **额外调用率和成本？** 主集 LL/LA 都在 5/24=20.8% decisions 触发，平均 1.208 calls/decision。L、LL、LA 的平均 reasoning tokens 分别为 5609.83、5995.79、7587.46；LA 相对 L 增加 1977.63/decision，LL 增加 385.96。压力集触发 1/9。实际离线调用数与这些逻辑路径成本不同，见下节。

16. **当前最佳 STOP policy？** 对部署选择 **none yet**。本次固定样本上 L1-only 最好，但 unresolved 主集大多远离闭合，resolved 类型窄，不能据此把它提升为可靠生产 STOP 规则。现有证据尤其不支持默认增加当前 Audit。

17. **是否有资格进入 Blocker→Need？** 没有。C1/C2/C3 全失败，D/O/G、Search、Retrieval、Writer、P3/P4 均未运行。探索不覆盖 formal gate。

18. **是否需要扩大 persistent State？** 没有新证据。仍保留 Q + Verified Claims + Working Hypothesis；Light/Audit 及证书都是 ephemeral。Q/Claims hash 改变使两类 cache 同时失效，Hypothesis/Workspace/attempts 单独变化不失效；拒绝结果不能被同状态反复重采样直到通过。

19. **是否需要不同模型 Audit？** 本轮没有跨模型证据，不能作此要求或保证。当前同模型能发现真实缺口，也会误判 materiality；换模型是否解决需要另行受控比较，本轮没有调用第二模型。

20. **Dominant bottleneck 是否已转移到 Frontier？** 尚不能这么判断。closure 的 materiality 校准仍是主要障碍，Progress 粒度/status 也未完全可靠。Frontier 未进入，不能把未测试阶段称为已经定位的新瓶颈。

## 唯一 bounded exploration

12 个非 fresh、失败分析后选定状态，6 resolved + 6 unresolved，各两次。只追加 generic materiality 判断，未增加 requirement table、State 字段或 FULL 扫描。复用原 Audit baseline：correct closure 4/12→9/12，但 false closure 0/12→1/12，有效 blocker presence 11/12→9/12，certificate adequacy 4/4→8/10。探索预定目标未满足，不采用追加 prompt。

这揭示了具体问题：更加严格地搜寻“未被逐字写明的关系”会增加过度拒绝；更宽松地接受强身份匹配，又可能遗漏 material quantity/role。需要可靠地区分这两类缺口，增加判断字段或重复采样本身没有解决它。

## 成本、失败与完整性

共 **223 次真实 HTTP 提交**：1 dummy canary + 144 primary + 54 challenge + 24 exploration。客户端 retry=0，无 repair/best-of/补采样。全部 HTTP 成功；2 个 L0 schema failures 因缺少 `closure_claim_refs` 保留，未删除或重跑。

- Input：259,378 tokens；其中 cache hit 186,224、miss 73,154，token-weighted 命中率 **71.80%**。
- Output：1,276,550 tokens；其中 reasoning 为 1,244,096（已含在 output 内，不重复相加）。
- 所有用量均为 provider 实测；未估算未经核验的货币价格。
- 历史 10,505 个 tracked experiment 文件进行字节哈希保护；完整性结果见 `analysis/INTEGRITY.json`。
- 模型请求只有 Q 与原 Claim statements；没有 Workspace、Hypothesis、先前 Light 输出、标签、source 全文或 gold answer。
- 未修改 Search/Find/Retriever、persistent State 或生产 Controller；缓存只做离线机械原型与 contract checks。

## 当前可保留的研究结论

一个真实 material blocker 足以否定 closure；它不需要穷尽问题。但发现“某句话没有对应 Claim”不自动构成 material blocker，找到强候选也不自动构成 closure。当前最值得保留的是已观察事实及其显式关系绑定；模型生成的 Progress/Audit 判断仍应接受资格检验，不能因格式正确或被缓存就成为持久控制事实。

目标仍是：模型依据当前证据支持的研究状态，选择能解决当前 Need 的下一步。此次没有获得把这个判断可靠地交给默认 Closure Audit 的证据。
