# Belief → Need Convergence：最终结论

## 判定

**FAIL（本轮冻结配置）；EVIDENCE_EXHAUSTED（不能做合格 fresh confirmation）。**

本轮没有达到 NEAR_PASS，也没有获得进入真实多轮端到端实验的资格。
Coverage-aware prompt 相对历史风格 Direct 有正向信号；单纯增加 self-check
或 ephemeral Progress 未形成可靠收敛。局部化干预改善了已返回问题的质量，
但大量输出截断使执行可靠性不足。

这里必须限定结论：**4096-token 上限由本轮工程实现自行冻结，严重限制了模型
完成输出；当前分数不能证明这些 Need policies 在充足推理预算下仍然失败。**
此外，只有 5 个可用于较少暴露开发/后续保留的 qid，未满足确认所需的 8 个。
继续在这些材料上调 prompt 无法补足确认资格。

## 执行和材料

- 实际远程 base：`99202167ab1c693514ef87534ca9f346f0813638`。
- 分支：`experiment/belief-to-need-convergence`。
- 437 个不同历史 QCH，分布于 10 个 qid；五个指定历史 bad-case qid 进入 challenge。
- 开发：24 states / **5 qids**；challenge：10 states / 5 qids。
- Coverage Delta：12 对；Hypothesis Delta：4 对。诊断投影与自然历史状态分开。
- 去重后 55 个运行 Belief；各路径复用相同 QCH，各 state/path 一次采样。
- 只有 **1 个严格 one-gap 开发状态**，不足要求的 8 个。不能把其单次成功当稳定性。
- 保留 21 个未消耗 QC groups，仍只有 5 qids，且未完成确认级别审计；没有伪称 fresh confirmation。
- 部分历史 verification seeds 的 H 原本由研究者提供，部分 G4/G5 seeds 为来源支持的规范化状态；并非全部由自主轨迹自然发现。
- 模型始终为 `deepseek-flash`，temperature 0，max_tokens 4096，timeout 240s，max_retries 0。
- Primary 未执行 Search/Find/Open/Writer。持久语义状态、retriever、工具接口均未修改。

详见 [协议](PROTOCOL.md)、[冻结选择](bank/SELECTION.json)、[标签](bank/LABELS.json)
及 [来源审计](bank/CLAIM_SUPPORT_REVIEW.json)。同题状态及 Delta 共享端点不独立。
本轮是单 reviewer、非盲法的语义评审，不声称独立复核或统计显著性。

## 首轮结果

分母为相同的 24 个开发状态。无输出计 strict failure；P/W 等语义维度只标注
实际返回内容，不能将无输出当作“没有语义错误”。

| 路径 | Strict valid / 24 | 返回 Need | 返回条件下 valid | P | W | No-H / 7 | One-gap / 1 | Coverage pairs / 12 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| P0 历史风格 Direct | 1 | 11 | 1/11 | 4 | 7 | 0 | 0 | 0 |
| P1 Coverage-aware | 7 | 13 | 7/13 | 1 | 5 | 0 | 1 | 4 |
| P2 Internal self-check | 5 | 7 | 5/7 | 0 | 2 | 0 | 1 | 3 |
| P3 Ephemeral issue → Need，格式修正版 | 8 | 18 | 8/18 | 2 | 9 | 0 | 1 | 6 |
| P4 Oracle gap，非部署候选 | 22 | 24 | 22/24 | 2 | 0 | 7 | 1 | 10 |

开发集的 S 均为 0，但截断、宽泛输出及小样本使“不会 stale”的推断不成立。
完整 V/S/P/W/I/H/A、qid 分层及调用用量见 [首轮指标](round_0/METRICS.json)。
Challenge strict 分别为 **1/10、2/10、3/10、4/10、7/10**，不进入主 gate。

P3 初始 55 个请求因 P3-A 缺少字面词 `JSON` 被 API 拒绝。这是实现错误，
全部保留于 `round_0/`，初始 P3 intention-to-run 为 0/55。
[另行冻结的格式修正](P3_FORMAT_CORRECTION.md)只补该词，未改语义、预算或其他
路径。上表 P3 使用单列修正批次，不能与原失败混合成一次无瑕疵运行。
这是已披露的技术协议版本例外；没有对语义失败 best-of 或重采样。

P0/P1 同一状态双方均返回的 10 个 case：strict 为 1/10 → 7/10；
P1/P2 共同完成 5 个：3/5 → 3/5；P1/P3 共同完成 11 个：6/11 → 6/11。
这些是完成条件下的描述比较，仍有选择偏差，不能当作无偏效果估计。

## 有限 bad-case 循环

按冻结成本规则，P3 只比最佳单调用 P1 多 1/24（4.17pp），不足要求的至少
2/24（8.33pp），保留 P1 为开发基线。阅读 P1 的全部 17 个失败输入和输出：
11 个截断，5 个 B5 broad frontier，1 个未提供的生肖映射前提。
B5 跨 q177/q546/q1034，但 q546 贡献 3 个，题目依赖明确保留。

[Round 1](ROUND_1_DESIGN.md)只增加一条通用 locality rule：选择一个可独立回答
的事实/关系，discovery 也只取一个识别线索。没有增加状态字段、ontology、
verifier、工具或推理预算。

| 16 个已暴露 exploration 状态 | P1，复用 | P5，局部化 |
|---|---:|---:|
| Strict valid | 5/16 | 6/16 |
| 实际返回 | 11/16 | 6/16 |
| 返回条件下 strict | 5/11 | 6/6 |
| W | 5 | 0 |
| P | 1 | 0 |
| Length failure | 5 | 10 |

5 个 B5 目标只修复 **2/5**：N004 从联赛条件打包转为十五奖杯的来源归属问题；
N018 从整段比赛序列转为第二场比分问题。两者跨 2 个 qid。
5 个有效基线控制中 **3 个退化为无输出**。未达到预先冻结的 ≥3/5 修复、
最多 1 个控制回退要求。其余 3 个 B5 目标无输出，不能计为修复。

“6/6 已返回均有效”存在严重完成选择偏差。不能据此宣称收敛或部署 P5。
至此停止继续调参：合格 fresh bank 不足，且一次有限机制干预已完成。
详见 [Round 1 指标](round_1/METRICS.json)及 [逐例评审](round_1/REVIEW.json)。

## 预算与工程限制

总计 **391 次实际 HTTP 请求**，峰值并发 8；三个批次顺序运行，重试 0。

- 55 次初始 P3 HTTP400：提示格式实现错误，已另版修正并保留原始失败。
- **111 次 length 截断**：109 次为 4096 reasoning tokens 且最终内容为空；
  1 次为 4095 reasoning tokens 且为空；1 次仅返回 24 字符未完成内容。
- 没有观察到 timeout；不能用“API 超时”解释本轮截断。
- 输入 tokens：166,019；输出 tokens：772,315。
- 缓存命中：75,776 / 166,019 = **45.64%**；未命中 90,243。
  这是 token 加权比率，API 拒绝未报告 usage，未虚构其 token 用量。

P3 修正批次为 100 次调用，输入/输出 43,706 / 151,772 tokens；P1 为 55 次，
29,036 / 169,372。双调用的调用数更高，但本轮输出 tokens 更少，不能直接把
调用次数当货币费用。未作价格或成本金额推断。

下一轮首先需要解决并冻结**能完成输出的推理预算/接口配置**，随后补足新的
真实 qid，再评估同一 Need policy。当前严格分数同时测量了策略质量和预算下
的输出可用性，不能单独归因于 Belief→Need 的语义机制。

## 二十项研究回答

### 1. 旧 Direct Frontier 在严格语义下多差？

本轮“去掉 STOP 的历史风格 P0”仅 1/24 strict；11 个返回中 7 个 W、4 个 P
（维度可重叠），13 个被截断。它是当前模型/预算下重采样的控制，不是改写
历史轨迹的成绩，也不是充足预算下 Direct 的能力上限。

### 2. Coverage-aware one-call 是否改善？

有描述性的正向信号：1/24 → 7/24，共同返回子集也从 1/10 → 7/10。
但只有 5 个 qid、1 次采样且截断较多，未建立统计显著性或 fresh 可复制性。

### 3. Internal self-check 是否有边际价值？

没有观察到可部署的边际收益。P2 strict 为 5/24，低于 P1；共同完成子集
3/5 对 3/5。P2 返回内容较干净，但更多截断，不支持仅凭条件分数选它。

### 4. Ephemeral Progress → Need 是否更可靠？

完成率有所改善，但 dev strict 只到 8/24，未满足预注册的双调用收益门槛。
P3-A 的 45 个返回 issue 中 31 个为合格局部缺口；其中 **6 个在 P3-B 变成
不合格 Need**。13 个 issue 本身仍宽泛，另 1 个涉及别名绑定边界。
因此“显式写一个 missing issue”不能自动确保局部性和安全措辞。

### 5. Oracle gap → Need 上限是多少？

当前人工卡的实测结果为 dev **22/24**、全部异质诊断状态 **49/55**。
这只是该卡和单 reviewer 标注下的诊断参考，并非数学上限；部分卡仍宽泛，
且输出会重新加入未验证前提。P4 不能成为 production candidate。

### 6. 主要失败在 coverage detection 还是 phrasing？

两者都有。宽泛 identity issue 在 P3-A 已出现，说明“选一个局部缺口”本身
有问题；31 个合格 issue 中 6 个在 formulation 阶段退化，说明措辞也不可靠。
此外，大量推理截断阻断了语义观察，不能把所有无输出算 coverage failure。

### 7. Strong-H + one-gap 是否稳定激活？

唯一 one-gap 状态 N014 上 P1/P2/P3/P4/P5 均给出有效生肖核验问题；P0 识别到
相关矛盾但打包了修正出生年与找另一演员。只有一个题目状态，不足声称稳定。

### 8. 加入 covering Claim 后 Need 是否正确改变？

Coverage pair correctness 为 0/12、4/12、3/12、6/12、10/12。
更强的“前态确实选中 g 且有效”子集：P1 仅 1 对、P3 仅 2 对，均转向有效
新问题；P4 为 8 对，8 对都不再重问 g，但只有 7 对的后态 Need 仍严格有效。
不能把没选过 g 的 pair correctness 当作 causal switching。

泛化动画 credit 并不覆盖 intro/end credit；base city 也不覆盖 capital-city
scope。[配对评审](analysis/PAIR_REVIEW.json)按精确局部关系判断，未误判这些
合理后续问题为 stale。

### 9. H 是否导致 unsupported premise？

有个别配对信号，但证据有限。双方均有输出的 H pairs：P0 的 P 从 1/2→2/2，
P1 为 0/2→0/2，P3 为 0/3→1/3，P4 为 0/4→1/4；P2 没有双方都完成的配对。
新增 premise 主要涉及演员 credit-name 变体的未明确绑定，对别名解释较敏感。
放宽别名推断后该效果减弱；P3 从局部 join 转成全套 biography 的 W 回退仍存在。
因此不能宣称已稳健证明 H 必然污染 coverage。

### 10. 无 H 时 discovery 是否有效？

P0–P3 的 dev No-H 都是 **0/7**；返回内容分别只有 1、2、1、4 个，且均宽泛。
P4 为 7/7。P5 exploration 为 1/4，其余 3 个截断。当前证据不支持可靠 No-H
discovery；缺口选择和输出完成都需要解决。

### 11. 是否仍有 whole-question Need？

有。P1 的 5/24、P3 的 9/24 开发输出被标 W；典型是完整比分序列，或
“是否匹配所有文章细节”。单个问号不等于一个局部研究问题。

### 12. 是否仍重复 already-covered Need？

本轮没有严格成立的整题 stale Need；所有可观察的 Delta 后态也未重问已覆盖
的精确 g。样本小、很多请求无输出，且部分输出仍打包已知与未知内容，不能
推断已解决 stale。查新的日期/角色绑定不算重复查已知值。

### 13. Bad-case exploration 找到了什么机制？

B5 locality 有有限可重复的同状态改进：2 个跨 qid 失败修复。
但其余 B5 状态无输出、3 个有效控制截断，因此未通过探索规则。
B11 输出不可用在本轮成为必要的独立工程分类；不能称作 Find/coverage failure。

### 14. 哪个 intervention 在 fresh confirmation 复现？

**没有。** 未运行合格 fresh confirmation。21 个保留 groups 仍仅 5 qid，
少于至少 8 个；challenge 和 design failures 没有被重新命名为 fresh。

### 15. 最佳方案 one-call 还是 two-call？

开发基线保留 **one-call P1**。P5 是未通过可靠性要求的局部化探索；P3 未达到
双调用增益门槛。没有任何方案被批准为已验证的最终部署 policy。

### 16. 是否需要新增 persistent state？

没有证据支持新增。保留 Q + Verified Claims + provisional H。
本轮问题发生在从这些信息派生一个局部、可完成输出的 Need 的过程。

### 17. 是否需要 Requirement Map？

没有证据支持。离线覆盖标签能诊断错误，但 Oracle 优势不等于应持久化一套
Requirement Map；本轮未检验其成本、错误积累和迁移性。

### 18. 是否需要 separate verifier？

未建立必要性。P2 的内部检查未获得执行收益；P3 也未可靠消除问题。
应先校准输出预算及局部问题选择，再考虑是否需要独立验证器的机制实验。

### 19. 达到 FAIL / NEAR_PASS / PASS 哪级？

**FAIL，附 EVIDENCE_EXHAUSTED。** 数值门槛、No-H 和 Delta 均未满足，确认
qid 覆盖也不足。结论限于本轮配置，不等于断言通用 Belief→Need 不可行。

### 20. 是否有资格进入最终 held-out end-to-end？

**没有。** Closure controls、offline autonomous transition simulation 和真实
多轮 Search loop 均未执行。Need generation 尚未验证，最终 closure 也未验证。
先获得可完成输出的固定配置及足够新的真实研究状态，再做 held-out 机制确认。

## 评审边界与完整性

[敏感性分析](analysis/SENSITIVITY.json)保留原判，同时报告别名推断、生肖常识
和历史 multiplayer 覆盖规则的替代解释。别名放宽使 P4 dev 22→23；生肖常识
放宽使 P1 7→8、P0 1→2；都不能通过 gate。没有为了过门槛改写冻结标签。

[完整性检查](analysis/INTEGRITY_REPORT.json)验证了 11,491 个历史实验文件
字节不变、391 个请求 QCH 一致、三批调用前 commit/freeze、工具列表为空、
卡片信息隔离、review 完整及凭据未进入产物。所有原始响应和失败均保留。

当前支持的最小架构判断仍是：**保留认识状态，按当前 Claims 派生一个局部
研究问题。** 本轮尚未证明该派生过程足够可靠，也未证明增加持久字段能修复它。
