# Local Obligation Context Sufficiency：最终结论

## 决策

**存在选择稳定性信号，但没有形成更可靠的 Direct-O。下一阶段建议拆开 `Q → CandidateObligations` 与 `Candidates + C (+最小 recency) → ActiveO`，本轮不执行。**

CΔ 的总体稳定性提升达到冻结的机制门槛；C1/C2 的有效率收益很小，主要假说中的 broadness 下降没有出现。不能把本实验概括为“Context 完全无效”，也不能说“更多历史解决了 Obligation”。

## 主结果

| Context | Strict | Broad | Downstream | RelationArg | Scope | Stable |
|---|---:|---:|---:|---:|---:|---:|
| C0 | 25/54 (46.3%) | 13/54 (24.1%) | 10/54 (18.5%) | 2/54 (3.7%) | 40/54 (74.1%) | 6/27 (22.2%) |
| CΔ | 23/54 (42.6%) | 20/54 (37.0%) | 14/54 (25.9%) | 3/54 (5.6%) | 43/54 (79.6%) | 11/27 (40.7%) |
| C1 | 26/54 (48.1%) | 14/54 (25.9%) | 13/54 (24.1%) | 1/54 (1.9%) | 42/54 (77.8%) | 9/27 (33.3%) |
| C2 | 26/54 (48.1%) | 18/54 (33.3%) | 14/54 (25.9%) | 3/54 (5.6%) | 42/54 (77.8%) | 10/27 (37.0%) |

Broad/Downstream/RelationArg 越低越好；Scope/Strict/Stable 越高越好。Strict分母54，Stable分母27；2次提供方 length 失败完整保留在 C0 分母中。

| Contrast to C0 | Δ Strict | Δ Broad | Δ Downstream | Δ RelationArg | Δ Stable | Mechanism signal |
|---|---:|---:|---:|---:|---:|---|
| CΔ | -3.70 pp | +12.96 pp | +7.41 pp | +1.85 pp | +18.52 pp | True |
| C1 | +1.85 pp | +1.85 pp | +5.56 pp | -1.85 pp | +11.11 pp | False |
| C2 | +1.85 pp | +9.26 pp | +7.41 pp | +1.85 pp | +14.81 pp | False |

## 有上下文的匹配状态

17个状态有真实Delta和路径；15个有匹配原始观察。17个状态的结果：

| Context | Strict | Broad | Downstream | RelationArg | Scope | Stable |
|---|---:|---:|---:|---:|---:|---:|
| C0 | 16/34 (47.1%) | 6/34 (17.6%) | 8/34 (23.5%) | 1/34 (2.9%) | 23/34 (67.6%) | 3/17 (17.6%) |
| CΔ | 18/34 (52.9%) | 9/34 (26.5%) | 10/34 (29.4%) | 2/34 (5.9%) | 24/34 (70.6%) | 9/17 (52.9%) |
| C1 | 19/34 (55.9%) | 6/34 (17.6%) | 9/34 (26.5%) | 0/34 (0.0%) | 25/34 (73.5%) | 7/17 (41.2%) |
| C2 | 19/34 (55.9%) | 7/34 (20.6%) | 10/34 (29.4%) | 2/34 (5.9%) | 23/34 (67.6%) | 8/17 (47.1%) |

这里三种 context 都达到机制信号，来自稳定性提升。C1 的 strict只增加3/34（+8.82pp），broadness仍为6/34；CΔ稳定性最高，但有效率低于C1一个响应。所有臂、所有资格子集均未满足完整 Direct-O viability 条件。

## 回答任务的20个问题

1. **Concurrent C0 是否复制历史 failure？** 定性复制：25/54=46.3%，仍远低于75%。不等于精确复制旧29/54=53.7%；本轮统一提示词不同，提供方与评审的不确定性也存在。

2. **Delta 是否改善？** 改善了稳定选择：总体6→11/27，合格子集3→9/17。合格子集Strict16→18/34，但总体25→23/54，broadness13→20/54。是有代价的局部信号。

3. **仅知道新增Claims是否足够？** 足以获得本轮最大的稳定性收益；不足以产生合格的Direct-O。不能将“稳定”当成“正确”：CΔ同时有15/27个两次都无效的状态。

4. **Path在Delta之外有价值吗？** 有有限混合证据：总体C1比CΔ少6个broad输出，满足增量机制门槛；但其中3个差异来自输入完全相同的空context状态。17个path-eligible状态中Strict仅多1/34，broad少3/34、stable反而少2/17，增量门槛未过。15个observation-eligible子集的broad下降恰为10pp，过增量门槛。不能据此认定Path必要或没有任何作用。

5. **Recent Observation改善还是干扰？** 未见稳定的增益。15个匹配状态上C2相对C1：Strict18→17/30，Scope24→21/30，RelationArg0→2/30，Stable同为7/15。是小幅负向诊断，尚不足以证明raw text造成语义干扰。

6. **哪个context最能降低broadness？** 没有任何增强臂优于concurrent C0。总体C0最低13/54；C1为14/54，且17个合格状态上与C0同为6/34。C1优于CΔ不等于优于baseline。

7. **哪个最有利于稳定性？** CΔ：总体40.7%、合格子集52.9%，均为最高。raw both-valid为C0 9/27，其余各11/27；稳定增益一部分来自减少不同但均有效的分支选择。

8. **Downstream是否改善？** 没有。总体C0/CΔ/C1/C2为10/14/13/14（/54）；合格子集8/10/9/10（/34）。Marwaha后续文章、未识别病例报告、候选捐赠事件等依赖仍被跳过。

9. **Relation arguments是否改善？** C1从C0的2/54降到1/54；合格子集1/34降到0/34，但只是一个错误的差别。CΔ/C2均3/54。没有大幅修复证据，且此错误类型基率很低。

10. **Object scope是否改善？** 总体wrong_object_scope为0/0/2/0（/54）；C1出现“memo日期→letter日期”和“base-game thesis→DLC描述”误附着，其中后者来自空context输入，前者来自没有raw observation的状态。不能归因于原始文本。

11. **Stale是否存在floor effect？** 是。C0仅3/54，CΔ/C1各1/54，C2为0；最多只有几个响应的改进空间。G21的Delta有助于从已完成的设计者/游戏线索转到advisor，但不能掩盖其他失败。

12. **Path是否产生新的事实提升？** 观察到6个与query绑定相符的未验证关系固化标签（C1、C2各3），但未识别出context独有的新事实提升。这些名字已在C中，类似错误也出现在无Path臂，不能称为6个由Path造成的新错误。

13. **Raw observation被当成verified evidence吗？** 最终Obligation中没有发现可明确归于raw-only内容的事实前提，`observation_overreach=0`。这只是可观察输出结论，不保证内部推理没有受影响。

14. **旧Query candidate是否被harden？** 有与此相符的输出：SOPHIE的未验证interview/song-reference绑定，以及Euler与目标书引用的绑定。6条内容匹配标签均保留因果来源不确定性。Melbourne查询候选则没有被固化为ICPC host。

15. **Eligible与overall一致吗？** 不完全。合格子集Strict有+5.88/+8.82/+8.82pp，而总体为−3.70/+1.85/+1.85pp。10个空context状态完全相同输入，却得到45%/25%/35%/35%有效率，说明本轮总体差异受随机波动影响，必须同时报告匹配子集。

16. **最低复杂度且最值得保留的intervention？** Delta作为可重算的recency信号最值得后续保留：稳定性收益最大，不需要完整Path。但它不是已经合格的单阶段Obligation方案。

17. **Claims足以表示frontier吗？** 不能证明充分。给同样Claims增加“刚新增哪些”的标签后，选择稳定性改变，说明epistemic result与recency不是同一信息。但没有证据表明持久Path是必需的，也没有证明目前的主要失败由缺少Path主导。

18. **有必要研究Candidate Obligation decomposition吗？** 值得。四臂Strict仅42.6–48.1%；即完全忽略Local/Coherent，仍只有59.3–68.5%通过其余维度和schema。结构与依赖失败持续存在，不宜继续单纯加上下文。

19. **需要persistent Path state吗？** 不需要作出这种架构升级。已有trace/Workspace足以机械重建Delta和短路径；本轮未增加任何persistent字段。维持PersistentSemantic=Q+C+H，control临时重算。

20. **下一阶段走哪条路线？** 建议独立分支 `experiment/ephemeral-obligation-decomposition`，先检验问题理解产生的候选目标是否保留关系/日期/角色，再用C与可选最小recency做选择。本轮没有运行候选生成、Gap cascade、Search/Find/Open、Writer或新循环。

## Frontier不足与结构投影失败各占多少？

本实验不能给出因果百分比分解。可以报告冻结标签的交集：

| 输出类别（/54） | C0 | CΔ | C1 | C2 |
|---|---:|---:|---:|---:|
| 有效 |25|23|26|26|
| 仅局部性失败 |7|12|11|10|
| 仅Scope/依赖失败 |11|10|13|10|
| 两者同时失败 |6|8|3|8|
| 其他语义失败（已支持） |3|1|1|0|
| 机械失败 |2|0|0|0|

因此可观察的正向信号主要是**重复选择更一致**，并没有减少总体局部性失败。结构/依赖错误并集为17/18/16/18条，仍约占全部输出三分之一。交集不是独立原因，不能相加解释成“多少错误由Path造成”。

G03的Path使两次都聚焦于真实未决的总表数，这是局部正例；G08的Path却让两次都跳到未建立interview的歌曲标题，是反例。G27仅Delta便可避免角色混淆。这些例子支持继续分离“知道什么”“刚发生什么”和“如何保持关系结构”三件事。

## 阈值、审阅与外推边界

冻结机制规则是OR：Strict+10pp、Broad−10pp或Stable+15pp，且RelationArg恶化不超过5pp。CΔ总体确实达标，不能改写为没过；它的Strict下降与Broad上升也必须一起看。C2总体Stable+14.81pp不能四舍五入到15pp算通过。Direct-O需要六项同时通过；所有臂只有RelationArg这一项通过，其余五项均未通过。

第一轮216条Q/C/O盲审已先提交，再揭示arm/context。单一reviewer知道既往bank并参与前缀重建，不声称完全失忆式盲法或独立评审。边界争议标为medium；低歧义子集是不同输出组成，不能用于补救主门槛。留一question后Strict差值可变号，也不支持稳定总体优势。

最后4个事件包括真实Writer更新；2个状态因此没有Search/Find/Open观察块。一个tool batch内部按原始数组下标降序选择最近块，很多文本与当前need无关。这是调用前冻结的机械规则，不能把结果外推成所有Path表示都无效。中间Writer checkpoint没有实际Actor调用；文本取自当时可供actor_view读取的精确bounded buffer，未读取未来Actor输入。

本轮是已暴露的27-state/10-question开发实验，不是最终准确率、生产部署或闭环成功证明。不依据gold/future重选状态，不改历史结果，不做事后提示词修订。

## 成本与交付

- Freeze：`0cc6d11`；第一轮评分提交：`3834417`。
- 216 planned/sent/returned，HTTP失败0，解析后schema失败0，length失败2；214条合规输出。重试0，额外canary0，新增retrieval0。
- input226,770；completion1,082,725，其中reasoning1,069,759；total1,309,495。reasoning已包含在completion，未重复相加。
- cache hit168,060；miss58,710；加权命中率 **74.11%**，216条usage均完整。
- latency median12.87s、P95 53.32s、max244.04s；max concurrency8，批次wall785.31s。240s是HTTP inactivity timeout，不是总耗时限制。
- 未验证价格，不报告货币费用。15项离线测试通过，216原始响应重解析与评分重算一致，17,128个历史文件hash保持不变。

完整结果见 `e1_context/REPORT.md`；逐条标签、pair/context评审、matched subsets、leave-one-question-out、失败与cache accounting均保留。

**最终目标仍是：在当前证据支持的状态下，选择合适的局部研究目标；更稳定地输出一个未经验证的目标，不是研究控制能力提升。**

## 额外事后稳健性诊断（不改主结果）

总体Delta的机制门槛对一个pair的语义分类敏感：若将C0 G12的“导师身份”与“包含导师的作者学术profile”假设改为compatible，C0稳定数会由6变7，Delta提升由18.52变14.81pp，总体机制门槛将不再通过。主分类保留different_but_valid，因两者选择的目标不同；这里只披露边界敏感性。17个eligible状态的三臂机制信号在这一扰动下仍成立。

仅在有合规输出的响应中，C0 strict为25/52=48.08%，与C1/C2的48.15%几乎相同。将发生机械失败的G07/G14从所有臂共同移除，得到25/23/26/25（/50）。这是事后敏感性描述，不能替换预注册的54分母。它进一步说明：不要把本轮总体约1.85pp的Strict变化当作稳健增益。
