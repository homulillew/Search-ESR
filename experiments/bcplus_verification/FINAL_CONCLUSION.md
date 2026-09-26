# BC+ Candidate Discovery vs Constraint Verification：最终结论

## 结论与阶段决策

**本轮不支持直接宣布“发现难、验证易”，不进入 S4 / S5。** 有候选且拿到精确关系证据后，U1 通常能正确更新；但给出 Candidate + 单个 Constraint，并没有保证在两步内拿到该关系的证据。

正式实验完成 S0–S3。唯一一次 bounded exploration 完成 4 units / 12 API calls，观察到局部恢复信号；不替换正式结果，不重开 gate。Search / Find / Open、BC+ backend、localizer、U1、生产组件均未修改；持久语义仍为 Q + Claims + H。

研究基线为 fetch 后核实的 `453161c2d2335416d4f439f9419e85c2266658b5`。正式调用冻结 HEAD 为 `99f6fc430698cbfe27d6626a94c0aa17d872398b`；探索冻结 HEAD 为 `b8cb8c61182bf11fbf95d94dafae25c81a714ff3`。完整来源、选择和冻结信息见 [PROTOCOL](PROTOCOL.md)、[freeze.json](freeze.json)、[探索预注册](exploration/PREREGISTRATION.md)。

## 1. 正式结果

| 任务 | 样本 / qids | 语义目标达成 | 平均实际工具调用 | Search / Find / Open |
|---|---:|---:|---:|---:|
| V+：支持指定条件并正确入 Claim | 18 / 8 | **13/18，72.2%** | 1.17 | 20 / 1 / 0 |
| V−：反驳指定条件、入 Claim、clear H | 11 / 4 | **6/11，54.5%** | 1.64 | 17 / 1 / 0 |
| Verification 合计 | 29 / 10 | **19/29，65.5%** | 1.34 | 37 / 2 / 0 |
| Discovery：曾产生有来源支持的可验证候选 | 10 / 10 | **8/10，80.0%** | 2.70 | 26 / 1 / 0 |

Discovery 的 8 个有来源候选中，**7 个是 benchmark candidate**；D10 的 Léo Scienza 是真实但非 benchmark 的临时候选。D10 在第一步已发现该候选，第二次 Actor 生成触及长度上限而失败。因此同时报告：曾达成语义目标 8/10；按失败轨迹保守计失败的完整运行成功 7/10；benchmark candidate 曾被提出 7/10。这三个分母都保留全部 10 个病例。

正式整数 gate：V+ ≥15/18、V− ≥9/11、合格错误候选敏感性 ≥8/10、Discovery 有来源候选 ≤7/10，**均未通过**。实际工具成本与保守 restricted update cost 两项通过，不能补偿成功率和不对称性门槛失败。见 [GATES](analysis/GATES.json)。

### 不能隐藏的 bank 问题与敏感性

- V− 原目标 12，冻结前只找到 11 个有反证依据的条件，没有合成第十二个。又发现 **VN12** 的生日来源冲突：一个写 1978，另一个写 1979。因此它不能作为确定的“非 Goat”反例。冻结输入和全部调用保留，合格错误候选子集为 **6/10**；不能把这个病例的 H 变化归咎于确认偏误。
- **VP16** 的 reference 只说“截至当时展示了两位兄弟姐妹的照片”，不足以证明家庭总共三个孩子。预调用 bank 对可验证性的认证过强。原分母保留，排除此不合格正例为 **13/17**。
- VP03 的“一名离线玩家 → 只有单人模式”和 VP16 的“展示两个兄弟姐妹 → 总共两个”存在语义范围判断敏感性。若同时放宽这两个判断，V+ 为 **15/18**；V− 与 Discovery 门槛仍失败，阶段决策不变。
- 两个 bank 问题有独立 append-only 审计：[negative](bank/POSTFREEZE_ELIGIBILITY_AUDIT.json)、[positive](bank/POSTFREEZE_POSITIVE_ELIGIBILITY_AUDIT.json)。没有事后补样、替换或改写原 bank。

## 2. 六段条件分解

| 分解项 | 观察值 | 范围 |
|---|---:|---|
| P(candidate discovered) | **8/10** | 有来源、值得继续验证的真实候选；benchmark 为 7/10 |
| P(evidence found ∣ candidate, constraint) | **20/29** | 正例支持或反例反驳所指定的关系；合格 bank 敏感性 20/27 |
| P(valid target Claim admitted ∣ useful evidence) | **19/20** | VP03 的事实先于充分证据被强化入库，后续未修复其 admission provenance |
| P(H cleared ∣ target contradiction) | **6/6** | 限合格负例，精确指定条件的直接反证 |
| P(correct verification frontier ∣ candidate) | **未测** | S1 的 Constraint 是 oracle 输入，不能冒充 Frontier 能力；S4 未运行 |
| P(correct resolved ∣ full coverage) | **未测** | 重审的历史 resolved controls 没有 strict full coverage；S5 未运行 |

### S3：没有观察到主要由“拒绝接受已见反证”造成的失败

合格负例中，6 个取得指定条件反证的病例全部正确 admission + clear。另有 VN01、VN03 先取得了**其他显式条件**的反证并 clear H，虽不满足“验证本次指定关系”的主指标，却是有用的候选排除。按任意明确 HARD_CONSTRAINT failure 排除候选，描述性结果为 **8/10**，其中 clear 为 **8/8**。

这个宽口径不能替换 frozen 指定条件 gate。它说明负例主指标低，主要不是已获得反证后仍然保留错误 H。未见反证的 VN05 继续保留 Brum，不算确认偏误；VN07 从 Higgins 转为有来源支持的 Selby，属于“未先证伪就替换候选”，不能算 Higgins 被正确验证或清除。有效反证已出现但原错误候选在最终 H 被保留的病例为 **0**。

负例集中在 q311、q546；同一 Hijitus 的四个条件共享来源。合格负例仅六个不同候选：至少一个指定条件验证成功的是 4/6，全部受测条件都成功的是 3/6。不是十个独立的失败机制样本。

## 3. 证据效率与成本

| 指标 | V+ | V− | Verification 合计 | Discovery |
|---|---:|---:|---:|---:|
| 取得目标证据的 Search / 全部 Search | 14/20 | 6/17 | 20/37 | 14/26 |
| 有用目标窗口 / Search | 24/20 | 11/17 | 35/37 | 33/26 |
| 对当前任务无关或仅支持其他 Need 的窗口 | 54/101 | 63/86 | **117/187，62.6%** | **76/131，58.0%** |
| 单位内去重后的对应比例 | 51/96 | 57/75 | 108/171，63.2% | 75/121，62.0% |
| 成功病例到有效状态更新的平均 action | 1.00 | 1.17 | 1.05 | 1.86（完整运行成功子集） |
| 保守 restricted update cost | 1.56 | 2.00 | 1.72 | 2.50 |

Verification 的无关窗口比例没有总体下降。V+ 略好，V− 明显较差；Search 产生目标证据的比例合计约 54%，与 Discovery 接近。不能写成“candidate-conditioned query 已显著提高检索精度”。这里 relevance 按任务定义：V 只要求指定关系，D 允许支持任意有区分力的候选线索；23 个 V 窗口支持其他问题线索，不能称为毫无研究价值。完整逐窗口判定见 [WINDOW_REVIEW](analysis/WINDOW_REVIEW.json)。

实际成本存在结构性混杂：S1 有 oracle 候选与单条件，预算两步；S2 无候选，预算三步。Discovery 在首次候选形成后又执行了 7 次工具调用，Verification 在首次目标成功后又执行 2 次。总平均调用差不能直接等同于“发现本身更难”。如果将 D10 已实现的候选发现保留为成功，Discovery restricted cost 为 **2.20**，与 Verification 的差 **0.476**，还不到 0.5；保守失败规则下才是 0.776。均为预算相关描述量，不作 IID 显著性或无偏速度提升结论。

### DeepSeek 用量与缓存

| 阶段 | API calls（Actor / Writer） | Input | Output（含 reasoning） | Reasoning | Cache hit / miss | hit / input |
|---|---:|---:|---:|---:|---:|---:|
| 正式实验 | **404（86 / 318）** | 818,980 | 862,350 | 844,444 | 382,976 / 436,004 | **46.76%** |
| 唯一探索 | **12（4 / 8）** | 30,324 | 15,577 | 15,037 | 11,392 / 18,932 | **37.57%** |

正式实验 399/404 请求报告非零 cache hit（98.76%）；探索 12/12。请求命中占比不能替代按输入 token 加权的命中率。Output 已包含 reasoning，不能重复相加。正式模型调用 elapsed 累加 4,045.24 秒，因四路并发和分阶段执行，实际 wall time 为 1,498.00 秒；工具执行累加 31.38 秒，另有初始化开销。探索模型 elapsed 累加 79.50 秒。

所有 416 次 HTTP 返回 200。正式保留两次输出失败：VP09 多出 `type` 键而违反 schema；D10 `finish_reason=length`、65,535 completion/reasoning tokens，没有可解析动作。后者不是网络超时。所有请求 max_retries=0，没有修复或重采样失败。原始 usage、耗时、失败均在 [CALL_AUDIT](analysis/CALL_AUDIT.json) 和各阶段 events 中。

## 4. 瓶颈与唯一探索

正式 10 个 Verification 失败中：5 个是已发现合适来源但没有取到所需关系窗口；1 个没有找回目标文档；1 个为目标 Claim 强化；2 个存在 bank 资格问题（其中一个同时有 Writer 强化）；1 个为 Actor schema 错误。主导观察是**关系证据访问失败**。这次不能继续无条件沿用“Search / Find 已不是主要瓶颈”的总体判断；必须区分 Actor 的来源范围选择与选对文档后的 localizer/局部 query 失配。

### Bounded exploration：相同第一步后前缀，替换第二步 Actor 的一段提示

机械选择正式失败且首轮已经见到 reference 文档的病例，每 qid 最多一个，得到 4 units / 4 qids。唯一变化是一段通用提示：考虑已有文档是否适合验证缺失关系，必要时使用文档搜索或窗口扩展。没有注入 D#、答案、offset、人工 Claim 或来源优先级，所有工具仍可用。对照复用正式第二步，探索最多增加一个决定，**从初始点算仍各两步**。

| 病例 | 对照 | 探索 | 结果 |
|---|---|---|---|
| VP06：Dodrill 的纸张动画设置 | Search 重复截断片段 | Find D1 | 取得 8x11 纸张陈述，正确入 Claim |
| VP12：Peter 的 2005 policeman 角色 | Search 停在电影表头 | Find D1 | 取得电影表格确切行，正确入 Claim |
| VN01：Hijitus 制作人员数量 | Find 命中角色描述 | Find D1 命中剧情 | 仍缺制作人员关系 |
| VN07：Higgins 转职业年份 | Search | 相同 Search | 仍未取得 Higgins 年份 |

精确关系成功 **0/4 → 2/4**；inspection 1/4 → 3/4，新增检查中有实际证据收益，非单纯工具数量增加。探索共 12 calls，低于 24 上限，零失败。完整新窗口与 Claim 已独立审阅，见 [REVIEW](exploration/REVIEW.json)。

这是失败选择后的、单次样本的可恢复性信号；没有重采样无提示对照，不能排除随机波动，也不能声称总体 50% 增益。两个反例均未被这个提示补救。它值得作为后续“候选条件化的来源/关系检查策略”研究依据，不足以支持完整 held-out loop。

## 5. 历史 closure 的重新解释

Q-only S0 标注覆盖 20 个真实 Q / 20 qids。**12 个历史 resolved 标注出现次数、11 个独立 Q+Claims 状态，strict-all-constraints 下保留 0 个。**

历史 Dynamic 的 29 个旧正确 closure 输出改判 premature，3 个旧 missed closure 改判正确拒绝；Asymmetric 分别为 31 和 17。合计是重复状态、多个阶段/arm 的 80 个输出映射，不是 80 个独立新病例。

曾标为 invented requirement 的 75 个需求，经复核有 44 个是真正未覆盖 hard constraint，14 个仍有阈值歧义，7 个为无依据的不相容推断，5 个为额外精确年份要求，3 个为已覆盖的普通名称共指，另有过时候选追问和捏造地理范围各 1 个。正式 S0 第一版粗判为 51 个真实缺口；新调用开始后复读**历史 packets**发现九处错误，以修订文件保留差异和时间，没有改写旧实验、当前条件或 gate。

Asymmetric primary Audit 的六次旧“over-demand”拒绝中，五次实际指出 hard gap，一次是含糊的剧集位置。正确拒绝并不保证理由正确。q435 的首专/退休/引语、q580 的敏感假设及主角关系、q186 的创立时名称绑定都不能由“答案很像”替代；q311 不能额外要求原播出发生在阿根廷；q1094 的一个 95 分钟事件不能覆盖球队历史与整场进球模式。完整逐案例说明见 [REINTERPRETATION](constraint_audit/REINTERPRETATION.md)。

## 6. 任务书的二十个问题

1. **Hard constraints 容易识别吗？** 人工 Q-only 复核大多可明确识别；相对时间、主角定义、资本城市范围仍需保留歧义。未测模型抽取准确率，不能据此称模型可靠。
2. **历史 resolved labels 保留多少？** 0/12 occurrences，0/11 unique states。
3. **是否支持 hard to discover, easier to verify？** 未充分支持。成功更新成本较低，但精确验证成功率不高于候选发现，尤其负例取证不足。
4. **V+ 成功率？** 主分析 13/18；有效 bank 敏感性 13/17；双范围放宽敏感性 15/18。
5. **V− 成功率？** 指定条件 6/11；合格错误候选 6/10。任意 hard failure 排除候选为 8/10，单列而不换主指标。
6. **Verification 平均 Search/Find/Open？** 37/29、2/29、0，共 1.34 次。
7. **Discovery 平均？** 26/10、1/10、0，共 2.70 次；包括发现候选后的继续研究。
8. **候选条件化是否显著减少无关证据？** 没有总体证据；V+ 略低、V− 较高，合并比例反而高于 D。不做显著性声称。
9. **U1 能正确写验证 Claim 吗？** 取得指定证据后为 19/20；全部新 Claim 中 136/140 有当前观察或既有 Claims 支持。4 个范围强化集中于两类机制，不能称完全可靠。
10. **反证能稳定 clear H 吗？** 这批有效指定条件反证 6/6 clear；任意明确 hard failure 8/8。样本集中且小，仅支持条件性正向信号。
11. **有候选后 Frontier 能稳定选 uncovered constraint 吗？** 未测，S4 gated off。Oracle Need 不证明该能力。
12. **还有 whole-question Need 吗？** 有。D04 首步串起 Game A、Game B、动画师和 PC；D02、D07、D09 仍出现多独立线索捆绑。少数 D 后续自然转入验证，不能据此量化 S4 成功率。
13. **还有 Q constraint 偷渡成 candidate fact 吗？** 有：“只有单人模式”的排他性、两位已展示兄弟姐妹被解释为总数。后者也暴露研究者 bank 认证错误；其他案例（如 Ding 的单场 4–3）没有被 U1 强化为整串比赛。
14. **Strict closure 消除了 q580 式 premature stop 吗？** 新评价会正确识别其缺口；没有运行新的 strict closure 控制闭环，不能声称消除了行为。D08 的 stop 是候选发现 probe 结束，也不是全题完成。
15. **Strict closure 成本不可接受吗？** 未测全部约束闭合的成本；当前仅测单条件。两步均值和探索恢复不能外推完整研究成本。
16. **需要 Persistent Requirement Map 吗？** 没有证据表明需要。离线标注服务评价，不进入 runtime。
17. **需要 Closure Verifier 吗？** 没有新证据。应先修正 closure oracle；旧 over-refusal 结论需重解。
18. **需要 Harness semantic router 吗？** 没有证据。当前机械 Harness 保持不变；探索的软提示已能恢复部分病例。
19. **Dominant bottleneck 是哪一层？** 本批 oracle verification 主要是精确关系的证据访问：Actor 的检查范围选择和局部 query/window。Discovery 的宽查询也造成失败；Writer 总体条件性良好但仍会过度强化；Frontier 尚未测。
20. **可以运行完整 held-out loop 吗？** **不可以。** 正式成功率/不对称性 gates 未过，S4 未测，且 bank 质量和来源冲突仍需处理。唯一探索已用完，不继续增加调用。

## 7. 可复现性与下一步判断

正式逐窗口 318 条、逐 Claim 140 条均已审阅；探索新窗口 8 条、Claim 4 条另行审阅。所有 request/response、工具结果、状态版本与失败保留。10,640 个历史文件、55 个正式冻结文件、17 个二进制身份和 13 个探索冻结文件通过完整性检查；所有注册窗口与实际语料 offset/text/hash 对齐；四个探索 pair 的 user payload、工具/schema、预算完全相同，system prompt 仅多预注册段落。见 [INTEGRITY_CHECK](analysis/INTEGRITY_CHECK.json)。

下一步研究依据是：**检验已有候选时，如何选对来源范围并取出缺失关系，再让 U1 保存精确事实。** 同时需要确保 answerability bank 的证据范围与冲突审计可靠。当前没有理由增加持久 Requirement Map、Closure Verifier、语义 router 或 hard gating。

工作目标仍是：**以最低成本验证当前候选尚未被证据覆盖的显式约束；候选被反证时撤销；全部 hard constraints 与最终关系都有支持才闭合。** 本轮证明了部分环节可行，也明确了完整结构尚未通过的环节。
