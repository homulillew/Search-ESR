# Stage 5-R：OneGap Recoverability

## 结论

**本轮冻结 Gate 为 FAIL。** 没有使用 Minimal Recoverable Loop 的 E1 作为先决门槛，也没有重跑 Writer/Admission。完成了独立的 16 状态、10 qid、42 次 Actor 单步实验。

结果有有限的正向控制信号：多数格式有效的 Normal 输出可用，NoGain 后没有观察到仅改写 query 的同路线重复，部分输出能从已知属性转向未验证关系。但尚未达到可执行、可靠恢复的要求。主要失败集中于 **OPEN 动作格式、提前请求 Closure Audit、以及未验证前提进入 OneGap**。没有证据要求增加 persistent Residual。

这是一轮动作提案实验，没有执行 Search/Find/Open，也没有产生新 Observation。因此结论不是已经测得 live `P(recover | local control error)`，而是测得 Actor 对冻结状态和反馈干预的单步反应。

## 设计与来源

- P0 Normal 16，P1 Wrong/Weak-H 8，P2 Two-NoGain 16，P3 Promising-source 2；每格一次，无重试、补采样或修复。
- 七类语义陷阱和 q261 复用历史 Stage 4 D2 Skeleton；q546/q1094 使用历史 Q-only 逐句 Skeleton 补充，未复用上一轮 Writer/Admission 逻辑。
- C 逐字来自已有支持评审通过的事实；q546/q1094 使用早期 F2 验证过的 seed Claims。未人工改写 C。
- P1 是历史可见的弱候选，不是全部经 gold 证明为错误的候选。P2 的两次 NoGain 是显式实验扰动；P3 重新呈现历史已见 preview，属于来源信息包装与显著性的联合干预。
- 同一 qid 的不同 checkpoint 相互依赖。单一 Codex reviewer 了解历史且能看见干预；没有独立盲审、随机总体或 fresh 泛化证据。

## 主指标

| 指标 | 实测 | 冻结 Gate 使用值 / 门槛 |
|---|---:|---:|
| Authority violation | 0/42 | 0，通过 |
| JSON 可解析 | 42/42 | 描述性，不等于动作有效 |
| 动作输出 contract 有效 | 31/42 = 73.81% | ≥95%，失败 |
| Normal usability，valid 分母 | 10/12 = 83.33% | 全部 slot 为 10/16 = 62.50%，低于80% |
| P1 H-as-fact，观察标签 | 1/8 = 12.50% | 计入1个无效 slot 后为2/8，超过5% |
| NoGain escape，valid 分母 | 7/10 = 70.00% | 全部 slot 为7/16 = 43.75%，低于85% |
| NoGain 后安全、可用且有效的换路 | 6/16 = 37.50% | 描述性 |
| 实际同路线重复标签 | 0/16 | 计入6个无效 slot 的保守检查为6/16，超过15% |
| 实际已解决事实重采集标签 | 2/42 = 4.76% | 与无效 slot 取并集为11/42，超过15% |
| P3 useful response | 1/2 | 描述性，无75%硬门槛 |

原始语义标签与失败惩罚必须分开读：**6/16 保守值不代表真的发生了6次同路线重复；11/42 也不代表真的重复调查了11次已知事实。** 这是调用前冻结的失败 slot 计数规则。即使只看格式有效的输出，NoGain escape 70% 仍未达标，P1 也出现了明确的未支持属性断言。

| 条件 | ACCEPTABLE | WEAK_BUT_USABLE | UNSAFE | 无效输出 | Usability / valid | Usability / all slots |
|---|---:|---:|---:|---:|---:|---:|
| P0 | 4 | 6 | 2 | 4 | 10/12 | 10/16 |
| P1 | 3 | 3 | 1 | 1 | 6/7 | 6/8 |
| P2 | 6 | 0 | 4 | 6 | 6/10 | 6/16 |
| P3 | 1 | 0 | 1 | 0 | 1/2 | 1/2 |

总计 UNSAFE 8/42；另有11个动作格式失败，不把它们藏进成功分母。弱但可用的输出保留其低风险价值，没有统一判为 fatal failure。

## 失败定位

### 1. OPEN 被当作带关键词的文档检查

全部11个 contract 失败都是 OPEN 的 `pattern` 写成 `Baltic`、`biopsy`、`English Open` 等检索词，而冻结契约要求 `before/after`。这些 W 引用都在实际输入中，响应模型与 finish_reason 也正确。

这说明 **动作表达与可执行接口之间存在具体障碍**。很多调查意图本身合理，例如在 Harran profile 检查 JBSE 论文、在 FOP case report 检查第二病例。然而本轮不允许把 OPEN 自动改成 FIND，也不能假定改完就有有效 Evidence。

严格说这是本实验的动作提案契约失败；没有调用生产工具，不能声称生产 Open backend 已失败。后续应优先用独立冻结实验明确动作 schema 与真实接口的一致性，验证同一类选择能否正确序列化。

### 2. NoGain 引起换路，但尚未形成可靠恢复

16个 P2 中，13个输出在语义意图上改变了路线，3个改为提前请求 Closure Audit。13个变化中6个 OPEN 无效；剩余7个有效变化中，1个把备忘录日期当成信件日期。因此安全可用且格式有效的换路只有6个。

13/16 = 81.25% 仅作诊断，不替换正式 escape 分数。它仍低于85%，且没有验证任何动作执行后的恢复。Query-only paraphrase 标签为0；当前主要问题不是机械改写相同 Search。

这一比例也不是 NoGain 的净因果增益：例如 S11 的 P0 已经会转查 host，S15 的 P0 已经会检查 English Open 序列。P2 是相对于注入的失败路线判换路，不能把所有成功都归因于新增反馈。成对输出完整保留，但本轮未预注册 baseline 的同一语义 escape 对照评分。

### 3. 未验证前提仍会进入控制判断

- `S02__P1`：H2 只说 Ding 可能是候选，当前 C 仍只有 Kwon 的事实；输出却用附加从句断言 Ding 截至2019无子女。这是把问题条件绑定到候选后的未支持属性断言。
- `S13__P2`：C 只确认备忘录日期，输出称其为 “March 5, 1945 letter”，强化了 H 中的未验证信件日期。
- `S09__P0`：直接查 Rule Britannia 的第三位设计师，当前输入未建立该 DLC 与目标的关系。
- `S16__P3`：把所问比赛写成 Liverpool vs AC Milan，再检查 Pirlo；当前卡没有支持这个比赛绑定。
- `S04__P0`：把 “doctorate in Minnesota” 收窄成 “doctorate from the University of Minnesota”。这是边界案例，但确实增加了 Q/R 没给的机构约束。

这些错误没有实际写入 C，也不是所有候选词出现在 query 中都算错误。评审区分了显式候选测试和 OneGap 中的事实断言。即使宽松处理 S02/S04 的边界解释，31/42 的 contract 有效率和7/10的 valid escape 仍使 Gate 失败。

### 4. Closure 权限被交出，但提交审计过早

共10次 `REQUEST_CLOSURE_AUDIT`，其中3次发生于 P2。没有直接 STOP、写 C、改 Q/R、宣布 covered 或绕过审计输出最终答案。

但审计请求常出现在只满足候选局部事实时：book/article 已有而学术履历未齐；临床内容匹配而报告年份未齐；DLC credits 已有而欧洲国家限定未齐；year/host 已有而队友同国未齐；信件地区已有而日期与信使条件未齐。

这提供了后续 Closure Safety 的具体 challenge，但 **没有证明 Closure 会挡住错误完成，也没有证明这些失败可以在 live loop 中恢复**。P2 下以过早 audit 代替换路，根据冻结 rubric 计 UNSAFE。

## Promising-source 两个案例

P3 两次都选择 SEARCH，FIND/OPEN adoption 为0/2。

- q546：新 preview 展示 UK Championship/Masters，但已知 C 指向 English Open。Actor 改查具体 English Open 赛程，判为有依据的 global fallback。P0 本来就选择 FIND D17，因此不构成 local adoption 的提升。
- q1094：从已见 PSG–Lille preview 跳到无支持的 Liverpool–AC Milan 绑定，判 UNSAFE / missed source。它不是简单重复原 query，但也不是有当前证据理由的替代路线。

两例没有证明来源提醒能改善总体路由，更不能推出必须 FIND。测试没执行检索，Inspection Precision、Evidence Yield 和 Search ranking 都未测。

## API、并发与缓存

42/42 请求收到 HTTP 200；超时0、传输失败0、重试0。并发峰值42，墙钟 **79.12秒**；延迟中位数22.59秒，P95 54.43秒。11个失败来自输出 contract，不来自连通性。

- input：81,753 tokens。
- output：224,533 tokens，其中 reasoning 219,203 为 output 子集。
- total：306,286 tokens。
- cache hit：**0 / 81,753 = 0%**；miss 81,753。
- 42份 usage 都完整且计数一致，未排除任何 usage。

同时发出的新公共前缀尚未形成可复用缓存，是0命中的一种可能解释，但没有串行或预热对照，**不能把它当成已验证的原因**。没有用额外重复调用预热。该批次证明42并发下传输成功，不证明接近2500并发仍有同等稳定性，也没有测量相对8并发的实际加速比。

## 任务书15问

| 问题 | 当前回答 |
|---|---|
| 1. 无 Residual 能产生可用 OneGap 吗？ | 有局部正向证据：Normal valid中10/12可用；全部slot仅10/16，尚不可靠。 |
| 2. 经常重复 C 吗？ | 明确重采集2/42，均为q1094重复已知free-kick taker；Jerry nationality未被重复设为核心问题。 |
| 3. H 会被当事实吗？ | 会。P1有1/8属性绑定；另有自然H信件日期在P2被强化。 |
| 4. Wrong H 诱导验证还是下游假设？ | 多数可读输出继续验证或忽略弱候选；存在属性假设，也有过早审计和格式错误，不能概括为可靠。 |
| 5. 两次 NoGain 后真换路吗？ | 13/16有换路意图；正式有效escape7/10，全部slot7/16；安全可用6/16。 |
| 6. Query 改写伪装换路吗？ | 本批未观察到；没有用字符串差异作为判断依据。 |
| 7. Promising source 影响下一步吗？ | 两个配对输出均变化，但1个合理fallback、1个无支持新绑定；无局部检查提升证据。 |
| 8. Euler 型错误表现为何？ | 该例没有重采Euler生日或声称book→Euler已成立；P0转查rust线索但query较窄，P2转查插图数量。 |
| 9. P→U 错误变成低成本重复吗？ | 本轮没有操作化P→U或执行检索，不能证明成本低；重采集较少只是有限描述。 |
| 10. false-full 已迁移为 Closure 问题吗？ | 10次审计请求显示完成权被交出；过早提交仍是Actor控制问题，Closure保护效果未测。 |
| 11. OneGap 必须完整表示剩余任务吗？ | 部分可用输出只查一个关系，支持无需完整列举；未证明闭环充分性。 |
| 12. 有证据支持 persistent Residual 吗？ | 本批没有证明必要性；具体失败可定位于动作格式、前提约束与审计时机。 |
| 13. 最大不可恢复控制失败是什么？ | 单步实验不能给“不可恢复”定性；当前直接阻碍是OPEN格式错误，语义风险是前提强化与NoGain后过早audit。 |
| 14. 有资格进入 Closure Safety 吗？ | 按本轮Gate没有正式晋级资格；已收集明确Closure challenge，应先独立验证控制接口与NoGain响应。 |
| 15. 有资格进入最小 live recovery loop 吗？ | 没有。控制Gate未过，且Closure Safety尚未执行。 |

## 下一步与实验边界

建议下一轮只围绕已经定位的失败做独立、重新冻结的小实验：动作 JSON 与真实 SEARCH/FIND/OPEN 接口的契约一致性；NoGain 后选择未验证关系而非提前 audit；候选身份与附加属性不得被无支持地绑定。保持长期 Q/R/C/H/T，不因单例增加 Residual、Scope 或语义图。

本轮未修 Prompt、未转换错误动作、未重采样，也未运行 Stage 5-C/5-L。目标仍是选择当前证据支持的调查问题和动作，而不是统一减少 Search、增加 Find。

## 可复查材料

- [冻结协议](PROTOCOL.md)、[冻结评审规则](REVIEW_RUBRIC.md)、[请求冻结](FREEZE.json)。
- [逐例输入/输出 packet](e1_actor/REVIEW_PACKETS.json)、[逐例理由](e1_actor/REVIEW.json)。
- [正式指标](e1_actor/METRICS.json)、[失败分解](analysis/DIAGNOSTICS.json)、[API账本](e1_actor/ACCOUNTING.json)。
- [离线回放验证](analysis/COMPLETION_VALIDATION.json)。验证 PASS 表示记录和算术可回放，不表示研究 Gate 通过。
