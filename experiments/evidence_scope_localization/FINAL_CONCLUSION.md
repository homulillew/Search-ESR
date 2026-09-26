# Need → Evidence Access：最终结论

## 决策摘要

**通用 scope 提示改变了工具选择，但没有在 fresh K-bank 上提高 exact-evidence success。正式 scope gate 未通过。** 它在已分析过的 challenge 上有效，不能用来覆盖 fresh 结果。

| Bank | A0 自由策略 | A1 scope 提示 | A2 Search/Open | A3 正确 D 提示 |
|---|---:|---:|---:|---:|
| Fresh K：10 Need families / 5 qids | **9/10** | **8/10** | **10/10** | **9/10** |
| N：8 families / 8 qids | **6/8** | **6/8** | **6/8** | 不适用 |
| Challenge：5 cases | 3/5 | **5/5** | 3/5 | 3/5 |

A1 的 K 成功率达到 80%，相对 A0 却是 **−10 pp**，未达到冻结的至少 +2 个成功（本 bank 中 +20 pp）门槛。A0 的 90% 也形成了改善空间上限，但实际对照仍没有显示 A1 增益。N 的不退化及严格 local-lock 条件通过。

A3 fresh K = **9/10**，达到预注册可用线，故 **不运行 R2**；不运行额外 prompt sweep、Writer replay、Frontier 或 end-to-end。保持当前 Search/Find/Open 及 Q + Claims + Hypothesis。

## 可信范围与故障

K 实际只有 **10 cases / 5 qids**，低于目标 12 / 6；用了所有经审查符合条件的新 Need families，没有合成 source、重复 prefix 凑数或纳入旧 challenge。多例共享 qid/prefix，不能当作独立大样本。新的自然语言 Need 接口和两步预算也意味着不能直接与历史 37 Search / 2 Find 比例作因果比较。

本轮 **84 trajectories、156 次 API、100 次工具、312 个返回窗口、0 Writer**。全部 HTTP 200。保留了两次 schema failure，以及九次在第一步工具后发生的 harness failure：三个历史 Recent Attempts 是 provenance 字典，runner 误用 list.append。九例都已返回 exact evidence，按调用前冻结的 evidence-ever 规则仍计入证据成功；第二步行为和完整成本被截断，不能称为运行成功。

排除任一对照臂故障后的共同病例：K A1/A0 **7/8 vs 8/8**，A1/A2 **8/9 vs 9/9**；N 两种对照均 **4/6 vs 4/6**。这一敏感性没有逆转 fresh 结论。A3 的无故障 operational success 为 8/10，与正式 evidence 9/10 分开报告。故障、原始响应和未应用到 R1 的兼容修复见 [engineering/INCIDENT.md](engineering/INCIDENT.md)。没有重采样或隐藏失败。

## 逐项回答研究问题

### 1. 最新 Verification bad cases 主要是 Scope selection 还是 Localization？

**两者都存在，当前 bank 不支持归为单一瓶颈。** VP06 challenge 中 A0/A2 两次 Global Search 仍拿不到 paper relation，A1/A3 Find 成功，说明明确的 scope 机会。VP12 中 Find 后 Open 和直接 Open 都能取得 filmography row。另一方面，A3 已给正确 D，VN06 fresh 仍两次定位到错误内容；VN01/VN07 challenge 也失败。正确 source 并不能消除 query/occurrence/binding 问题。

Fresh A3 9/10 与 A1 8/10 的差距仅一例，且 A1 有 schema failure；不能将其描述为 A3≫A1，更不能据此认定 source routing 是压倒性原因。

### 2. 当前 Actor 是否过度偏好 Global Search？

**不是整个 fresh bank 的统一现象。** K A0 共 6 Search / 4 Find，9/10 成功。A1 变为 1 Search / 10 Find，但成功降到 8/10。A0 在第一步直接使用已有 exact source 为 4/10，A1 为 8/10；更多已有 source 利用没有转化为更好的证据结果。旧 challenge 中仍可看到无效重复 Global Search。

### 3. 通用 scope-aware prompt 能否 fresh-confirm bounded exploration？

**未能。** Fresh 正式 gate 失败。四个原探索病例 VP06/VP12/VN01/VN07 单列为 A0 **2/4**、A1 **4/4**、A2 **2/4**、A3 **2/4**；加入已分析过的 VN03 后分别 3/5、5/5、3/5、3/5。这里重采样的 baseline、Need 和预算与历史探索不同，不能写成一次严格配对的“历史 0/4 → 当前 4/4”。

### 4. Scope-aware policy 是否造成 local lock-in？

按冻结的 S3 定义，N A1 **0/8**：没有连续两次死磕同一个不含关系的文档。N 总成功率也未下降。但是 N_VP03 一次本地检查只看到 one offline player 后就 STOP；A2 更是直接 STOP。这属于不完整证据的解释/提前停止问题，不能因为 S3=0 就说 fallback 已可靠。

K_VP14 A1 两次完全相同 Find 返回 WPBSA 表格开头。D4 实际有需要的 Ding 记录，因此是**正确来源的重复定位失败 S6**，不是错误来源 local lock。

### 5. v3a Unified Global Search 是否足以替代 Find？

**Fresh bank 中表现很强，尚不能全局替代。** A2 K=10/10、N=6/8，优于或持平 A1；但 A2 challenge=3/5，遗漏 paper 等已知来源关系，A1=5/5。每组样本很小，不能据此声称等效、支配或直接删除 Find。

### 6. Find 是否有真实边际价值？

**有局部价值，未证明总体增益。** Paper challenge 提供了直接机制证据；filmography 可以通过 Find+Open 或 Open 完成。Fresh A2 的成功表明许多关系可由 Global Search 对旧文档重新定位，Find 的价值取决于具体关系和窗口，而非只取决于文档是否已经发现。

### 7. 正确 source 给定时 Find/Open 成功率是多少？

Fresh **9/10=90%**；全部通过 Find 返回证据的九例均在第一步成功。唯一语义失败 K_VN06：在 Williams 文档内寻找 Ronnie 职业起点，查询落到 Williams 自己的职业段和两人比赛段，未返回 Class-of-92 绑定句。Challenge **3/5**。A3 是受工具限制的 document-scope 诊断，单次随机生成的表现不必逐例高于自由策略，不是数学上的最优上界。

按冻结规则不启动 top-3 local Find；challenge 和 operational 敏感性均不覆盖这个正式决定，见 [r2/DECISION.json](r2/DECISION.json)。

### 8. Table / prose / list 是否有明显差异？

Fresh relation-region 分层：

| 类型 | A0 | A1 | A2 | A3 |
|---|---:|---:|---:|---:|
| Prose，6例 | 6/6 | 6/6 | 6/6 | 5/6 |
| Mixed，3例 | 2/3 | 2/3 | 3/3 | 3/3 |
| List，1例 | 1/1 | 0/1 | 1/1 | 1/1 |

List 的 A1 失败是 schema，不是检索。没有满足 freshness 的纯 table 主样本；challenge 有三例 table/infobox，但不能作为新结构结论。可以定位具体 table 截断，也有 prose 关系绑定失败；**不足以归因于 table 或启动结构化 parser**。

### 9. Global query 还是 local query failure 更突出？

没有一个可靠的统一排序。Fresh Global Search 在返回多个窗口时通常能得到至少一个成功窗口；local query 的 wrong occurrence 在 K_VP14/A1 和 K_VN06/A3 中具体可见。旧 challenge 的 Global Search 又更容易重复不合适的 preview。这里只记录冻结的 entity/relation 词命中、原始 query、重复和 rediscovery，不用事后改写的“理想 query”打分。

### 10. Search 命中正确文档但 window 错的比例？

两种不同分母必须区分：

- 已返回至少一个经核实 exact source 的 Search action 中，**11/48=22.9%** 的所有返回窗口都未取得 exact relation。
- 从这些 exact sources 返回的单个窗口中，**19/69=27.5%** 缺少关系；同一次 Search 的其他窗口可能成功。

Fresh K action 层为 **0/16**，但单窗口层仍为 **6/25**；N action 层 **1/19**；challenge 为 **10/13**。N_VN05/A2 曾命中含 Brum 的完整列表，preview 却从 Brum 行之后开始，属于可定位的 source-hit/window-miss。Source 层按核实的关系来源计，不能把相关页面算成 exact source，也不声称穷尽了 corpus 的所有等价来源。

### 11. 当前 Workspace 足够吗，是否需要修改内容？

Workspace 已能承载解决 K/挑战病例所需的文档和原文位置，A3 及 A2 都证明现有访问路径可用。但 Actor 仍可能重复同一窗口或过早停止。当前没有受控证据要求扩展 Workspace 内容或添加 relevance summary；先在现有目录和窗口上验证决策与访问可靠性。

### 12. 是否有证据要求修改 Persistent State？

**没有。** 本轮失败发生在冻结正确 Need 与真实证据访问之间，且没有 Writer 更新。增加 persistent source、scope、Need、constraint 或 confidence 字段不能由这些结果推出。继续保留 Q + Claims + H。

### 13. U1 是否保存 off-Need 但 Original-Question-relevant 的事实？

**会，但不完整。** 对历史全部 318 窗口和 U1 输出离线审计，Verification 中其他 hard condition 的完整支持/反驳立即保存 **30/38=78.9%**，只看正文 **29/37=78.4%**；包含直接支持的条件组成事实则为 **67/89=75.3%**。按 case/fact 去重并允许后续观察补记为 **67/77=87.0%**。Discovery 单列 7/9，不混入 V 主分母。

### 14. Claim Admission 是否实现 Need OR Original Question relevance？

**行为上已实现，召回与保真仍有限。** 有跨 Need 保存 birth/parent/network/album 等事实的实例，也漏掉 No Multiplayer 和明确的 first-break-year。不能把部分条件保存当成完整条件闭合。

历史 140 条新增 Claims，本轮发现 **5 条 unsupported strengthening**，其中 4 条延续旧判定，新增发现 VP10 在窗口中没有 67 albums 时写入该数量。保留旧 label，新增审计修正，不改写历史。Whole-Claim duplicates **0/140**，但存在部分事实重复。详见 [writer_audit/REPORT.md](writer_audit/REPORT.md)。本轮不修改 U1；如后续研究 admission recall，应另行隔离实验。

### 15. 下一瓶颈应该进入 Frontier 还是继续 Retrieval？

**继续验证 RetrievalPolicy / exact relation access 与停止条件。** 优先修复已证实的工程兼容问题，再在新冻结病例上区分“看到部分证据就停”“正确文档内重复错误位置”“Global preview 遗漏相邻关系”。这些是后续研究建议，本轮没有自行增加干预。A3 gate 未触发，当前不扩展 localizer。

### 16. 是否有资格运行 held-out end-to-end loop？

**本轮证据不足。** Scope formal gate 未通过，K 覆盖不足，N 仍只有75% exact success，并有明确的提前 STOP 与 source-hit/window-miss。工程失败也限制了 operational reliability。先补足独立 fresh retrieval 验证，再判断自主 Need 是否能达到同样质量；现在不把 Frontier uncertainty 混入。

## 执行与复核

使用原 provider `https://api.deepseek.com` / `deepseek-flash`，max_retries=0。
八个独立轨迹 worker，并行 API/CPU 工具；每条轨迹顺序执行，GPU1 embedding
forward 保持锁内单 query 计算。日志测得 API 峰值 **8**、工具峰值 **5**。
运行 wall time **126.71s**；并发的模型时间总和290.53s、工具时间总和234.22s，
不能相加当作 wall time。

Input **643,859**、output **40,550**（含 reasoning **31,573**）；缓存命中
**135,808 / 643,859 = 21.09%**，151/156 请求有非零缓存命中。
无 Writer、无重试、无 R2 或额外模型探索。

完整表格和逐案例结果：[analysis/RESULTS_REPORT.md](analysis/RESULTS_REPORT.md)。
哈希与因果输入检查：[analysis/INTEGRITY.json](analysis/INTEGRITY.json)：
10,803 个历史文件、37 个冻结输入、23 个 prefix 哈希通过；605 次 registry
窗口原文字节检查、112 个完整文档哈希通过，所有请求均先冻结后发送。
Corpus/index/model 二进制只验证冻结 size/mtime，不声称做过全量二进制哈希。

**最终应优化的是：给定当前 Need 和已有 Workspace，稳定取得真正支持或反驳该关系的证据。工具次数和 State 字段数量都不能替代这个目标。**
