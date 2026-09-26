# Goal Residual Control：G1 有限信号，G2 完整性失败

## 实际完成范围

- 远程基线：`experiment/state-transition-feedback`，`2d0c55995badd14ab4bc8241ca9caa97a1eef3a1`；本轮分支：`experiment/goal-residual-control`。
- G0：40 个 Reviewer 归一化快照、20 个真实 Observation transition、10 个 qid；29 个带来源和哈希的窗口记录。不是 40 条独立自然轨迹。
- G1：40/40 响应有效。主口径 closure 正确 38/40；premature 2/33；missed 0/7。严格 q435 敏感性口径：正确 34/40，premature 6/37，missed 0/3。
- G2：120/120 API 返回成功，只有 75/120 符合冻结动作 JSON 契约（62.5%）。45 个格式失败完整保存。**动作契约有效率低于 80%，触发任务书的执行完整性停止条件。**
- G3、G4、G5 未运行；真实工具调用为 0。没有 Evidence Progress、在线 State Update 或三轮架构胜负结果。

### 失败责任和边界

Harness 请求提供了函数工具的参数 schema，却遗漏了任务书第 25 节明确的扁平动作对象示例。Actor prompt 第 26 节只有 `actions: [...]`，不能独自消除 `tool` / `type` / `name+arguments` 的歧义。冻结解析器要求 `tool`，38 个响应使用不兼容 discriminator/wrapper，7 个响应缺少扁平层的 query。**这是我构造请求时的接口契约遗漏，不能归因为研究架构失败。**

没有放宽 parser、改写响应、重采样或执行被拒绝的动作。已提供独立且未应用的完整响应 contract 和 7 项确定性检查；任何新调用都需要一个单独、可追溯的新冻结版本。本轮结果不被覆盖。

## 可保留的研究发现

1. 只给 Question+Claims，Goal Reviewer 仍可能提前关闭。q580 的 S4-only 状态被误判 resolved；另一个状态在季数尚未提交时被关闭。相同 Q+Claims 的两次调用还出现不同 closure 判断。
2. 没有发现把 retrospective 67 albums 拼接成 Forbes May feature count 的错误；但 3 个 residual 把尚未充分确立的音乐家身份说成已验证，2 个 residual 引入不必要的新要求。
3. G2 的有效样本中有 20 次提前 STOP。由于 action 格式失败在三个 arm 中不均衡，且 STOP 不需要动作对象，不能据此做 arm 优劣排序。
4. 7 个主口径 resolved 快照只来自 2 个 qid；其中 q435 的 4 个快照存在缺少精确访谈引语的歧义。不能将 95% 主口径准确率直接推广为生产可靠性。

## G2 诊断计数（不能当架构比较）

| Arm | 格式有效 / 计划 | Correct STOP / resolved | Premature STOP / open | 有效 act |
|---|---:|---:|---:|---:|
| A0 State-only | 29/40 | 7/7 | 10/33 | 12 |
| A1 Derived Residual | 21/40 | 7/7 | 3/33 | 11 |
| A2 Historical Gap | 25/40 | 7/7 | 7/33 | 11 |

这些分母保留全部计划快照。失败样本的语义结果未知，不能视为没有 drift，也不能简单删除后声称 A1 胜出。有效 act 中没有观察到 unrelated-goal pursuit；4 个 Gap 过度确立候选身份或 film binding。查询相关性不等于取得有用证据。

## 45 个问题逐项回答

1. **Q+Claims→resolved/residual 可靠吗？** 有限可用，尚不可靠。主口径 closure 38/40，完整 residual 30/40；同输入判断不稳定，且严格敏感性降为 34/40。
2. **Premature closure 率？** G1 主口径 2/33=6.1%；严格 q435 敏感性 6/37=16.2%。分母是 gold-open 快照。
3. **Missed closure 率？** 主口径 0/7；严格口径 0/3。resolved cohort 很小且集中。
4. **Unsupported join 仍出现吗？** G1 没有 observed lifetime-count→Forbes-count join；存在 3 次 partial identity 被表述为 verified。后者单独标注，不冒充数值 join。
5. **Reviewer 引入新目标吗？** 2/40：要求 Fifth Estate 的具体角色；要求 Game B 等于 Dust。这两项不是原题必要要求。
6. **排除 Hypothesis 后 closure 更稳吗？** 所有请求都确实隔离了 Hypothesis，但没有运行 hypothesis-visible 对照，不能声称因果改善；2 次提前关闭仍存在。
7. **State update 后 residual 正确缩小吗？** 多数冻结 oracle pre/post 保留正确方向；T13 出现错误空 residual 后重新打开，T14 的季数要求在 PRE 已被错误省略。在线 mutation 未测试。
8. **Residual 消除历史 stale Gap 吗？** G1 可从 Claims 省去已解决要求，但没有 G4/G5 的真实控制验证。不能声称消除路径持续。
9. **A1 比 A2 更少 Goal Drift 吗？** 不可判定。G2 完整性失败，有效样本中两者未见 unrelated-goal pursuit，不构成比较证据。
10. **A1 比 A0 更好吗？** 不可判定；提前停止诊断计数方向有差异，但 differential missingness 不允许归因。
11. **A0≈A1 是否说明额外 Reviewer 不值得？** 本轮未建立 A0≈A1。未来须用有效完整决策和真实 Evidence/Stop 收益比较额外成本。
12. **Resolved 中谁最容易正确 STOP？** 主口径有效诊断中三者均 7/7；严格口径均仅 3 个 resolved 快照。没有胜者。
13. **谁最容易 over-research？** 有效诊断中均未见；无可用架构排序，G4/G5 未运行。
14. **谁最容易继续已解决 Gap？** 有效 act 未见整个 Gap 已解决仍继续的案例；缺失严重，不能推广。
15. **Gap 需要持久化吗？** 未获实证结论。ephemeral Gap 仍是待验证设计。
16. **Frontier 应持久化吗？** 本轮没有支持增加持久 Frontier 的证据。
17. **Actor 能联合选择 gap+actions 吗？** 34 个格式有效 act 展示了这种能力，每个有 2 个独立动作；完整可执行率不足。没有执行后的效用证据。
18. **Hypothesis 能安全引导探索而不污染 closure 吗？** 请求层隔离可以实现；动作中存在合理候选探索，但安全性和闭环收益未证实。
19. **Online Updater Claim precision？** 未测；G4/G5 没有调用 updater，不能填写 0 或 100%。
20. **partial clue 被提升完整 binding 吗？** G1 residual 有 3 次身份过度确立，G2 有效 Gap 有 4 次 overcommit。它们不是在线 Updater 的统计。
21. **Hypothesis rejection 阻止 path lock 吗？** 部分有效决策放弃 Heart/Hijitus，属于诊断例；没有受控 transition 或三轮路径结果。
22. **Goal Review 后重规划修复 stale path 吗？** 未经 G4/G5 验证。
23. **G3 Derived Residual 提高 Evidence Progress 吗？** 未测，G3 未运行。
24. **Direct/Decision Progress 分别多少？** 未测，不能把查询或文档标题当取得的证据。
25. **Persistent Gap 更易 NoProgress 吗？** 未测，没有真实工具 Observation。
26. **L0/L1/L2 Original Goal Resolution 谁最高？** 未测，G5 未运行。
27. **谁 premature stop 最低？** 三轮指标未测；不能用不完整 G2 代替。
28. **谁 late stop/over-research 最低？** 三轮指标未测。
29. **谁 Goal Drift 最低？** 三轮指标未测。
30. **谁工具成本最低？** 未测。全轮 0 次工具调用是因停止，不代表任一架构高效。
31. **L1 已经足够吗？** 未得到证据。
32. **L2 explicit Residual 有独立增益吗？** 未得到证据。
33. **State 可最终固定 Q+Claims+Hypothesis 吗？** 可作为待验证最小接口；本轮不足以“最终固定”生产设计。
34. **Residual 应为 derived projection 吗？** 本轮遵守并验证了输入隔离，但未证明完整控制收益。保留为架构假说。
35. **Gap 应只是 ephemeral action goal 吗？** 合理待验设计，不能据本轮接口失败得出经验性结论。
36. **Frontier 是当前选择而非长期对象吗？** 未获反证，也未完成对照验证。
37. **需要独立 Frontier Selector 吗？** 没有新证据支持增加它。
38. **需要 Historical Recall 吗？** 本轮未测试，也没有证据支持增加。
39. **需要 old/new scope router 吗？** 未测试，不建议从当前失败推导新增组件。
40. **需要 persistent TestCard 吗？** 未测试，没有新支持。
41. **需要 finer Evidence pointer 吗？** Harness 已保存窗口/哈希 provenance；没有 localizer 执行证据支持细化生产 pointer。
42. **哪些 clean-State failures 支持改 Retriever？** 无。本轮没有检索执行，接口失败不支持改 Retriever。
43. **哪些支持改 Find/localizer？** 无；未执行 Find/Open。
44. **State/reward signal 足够考虑 ESR-GRPO 吗？** 不够。closure 仍不稳定，truth 有敏感性，动作契约未可靠执行，且无真实闭环 reward。
45. **下一阶段优化哪个组件？** 先修复并单独冻结动作输出 contract；这是 Harness 接口修复。研究组件中优先复查 Goal Reviewer 的 closure 一致性和 Research Actor 对未解决要求的停止纪律；当前不能依据本轮给 Updater/Retriever/Localizer 排优化顺序。

## 调用、缓存与完整性

共 160 次单次模型调用，160 个 API 响应；零重试、零修复、零工具执行。G1 40 个格式有效；G2 75 个格式有效、45 个失败。缓存命中率按 tokens 加权且包含格式失败的成本：G1 **47.85%**，G2 **60.84%**；详见 CACHE_USAGE.json。

15 项归档/隔离检查通过：bank 和历史来源哈希、冻结请求和代码、每请求恰一响应、Goal Reviewer 输入隔离、G2 公共上下文一致、历史 tracked 文件未修改、后续工具阶段未启动。这些检查不抵消 G2 的执行契约缺陷。

研究目标仍是：模型在当前证据支持的研究状态下，选择对 Original Question 的当前 Need 最合适的 Source 和动作。**本轮没有证据可把结论简化成“少 Search、多 Find”，也没有完成整个闭环架构的验证。**
