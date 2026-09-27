# State-Conditioned Residualization / Bootstrap-to-Residual：最终结论

## 结论

**存在正向机制信号，但尚不足以宣称 Q+R+C 已成为稳定可靠的闭环控制状态。**

- E1 整体 R0/R1/R2 均 FAIL；P 组 R0、R1 均 6/6，通过预注册的 E2 入口。这个入口在调用前按 TASK28 Case C / TASK29 冻结，并非看到整体失败后临时放宽。
- E2 **预注册数值门槛 PASS**：P1 新材料机会 7/11，P0 3/11，差值 +36.36 pp；配对 5 胜、1 负、5 平。
- E2 的通过依赖 4 个有歧义的桥接判断，且 5 个 P1 查询违反 objective-only 生成规则。它不是干净、稳健的机制资格确认。
- E2B 固定 Parent 口径救回 0/2。Oracle 诊断 2/2 在 rank 1 返回有用来源，支持这两个案例存在查询/锚点瓶颈。
- 本轮完成后停止；没有自动运行短闭环、Writer、最终答案或新增持久状态字段。

## 执行概况

基线 `1f5536d54bc963e27583368dbed1d8356e012ee9`，分支 `experiment/state-conditioned-residualization`。E0 冻结 19 states / 10 qids：全部 11 个历史 subnode-only states + 8 个机械匹配对照；P=3，Z=16。

|阶段|规模|主要结果|
|---|---|---|
|E1|19 × 3 arms × 2 = 114 调用|整体 FAIL；P 入口 PASS|
|可检索性审计|全部 16 个 Z states|11 accessible / 6 qids；5 uncertain；0 known_unavailable|
|E2|22 计划槽位，20 调用，19 Search|P1 7/11，P0 3/11；数值 PASS，敏感性不稳健|
|E2B|2 cases，4 调用，2 Search|固定 Parent 救回 0/2|
|Oracle 诊断|2 Search + 2 已知文档预览，0 模型调用|2/2 已知来源 rank 1，预览有新材料|

合计 **138 次 DeepSeek API 调用**，21 次主实验 Search，2 次独立 Oracle Search；0 Find/Open、0 Writer、0 retries。全部 138 次请求返回，0 HTTP 错误；4 次输出格式失败保留。另外 2 个 P1 依赖槽位未发送，仍保留分母。

## 20 个研究问题

### 1. Full Current Claims 是否足以动态 residualize coarse R？

在部分支持的三个状态中有正向证据：R0 P 组 6/6 严格有效，且没有重复研究已支持内容。但整体 R0 29/38=76.32%，没有达到 85%。只能支持局部 subtraction 能力，不能泛化为整体可靠。

### 2. Gold relevant Claims 是否更稳定？

R1 整体 31/38=81.58%，比 R0 高 5.26 pp，但未达 90%；P 同为 6/6。模式正确率 R1 37/38，R0 28/38，说明剔除仅用于绑定的背景 Claims 有助于区分 substantive support。仍不足以宣布 evidence routing 已解决整体问题。

### 3. Frozen model supported_by packet 是否足够？

R2 30/38=78.95%，未达 80%；R0−R2=-2.63 pp。旧 packet 没有产生明显总体压缩损失，但 Euler biography 被当作书中引用关系的依据，说明它仍会错误提升局部事实。不能把压缩 packet 当作稳定的语义支持接口。

### 4. q228 G04/G05/G06 是否被正确区分？

R0 G04 聚焦 gift/building；G05 replicate1 聚焦 spouse/2019 childlessness；G06 两次都聚焦 Ding 的 gift/building，未重问已知婚育条件。G05→G06 replicate1 是清晰的必要切换；replicate2 的前态仍把多个缺口捆在一起，不能算成功转换。

### 5. q637 G16/G17/G18 是否随 Claims 改变 residual？

R0 G16 聚焦临床史，G17 已转向报告国家条件，G18 保留国家条件，并把已知临床史用于定位。国家条件始终未解决，故 G17→G18 的不变是合理保留，不是额外的因果“切换”证据。没有把病人国籍自动等同于报告国家。

### 6. 已支持内容是否仍被重复研究？

E1 三 arms supported-content leakage 均 0/38。E2B G20 却重新获取已有 thesis/game/advisor 内容；它按任务模板没有收到 Current Claims，故这是输入投影边界问题，不能归因于模型忽略了它未收到的 Claims。

### 7. coarse R 是否继续产生 broad residual？

R0 1/38，R1/R2 0/38。大范围捆绑已不常见；更突出的是把完整关系缩成较弱片段，以及混淆实体线索与 substantive support。

### 8. direct/coherent controls 是否被过度拆解？

是。R0/R1 各 6/16，R2 7/16，超过 10% 门槛。若描述性地接受“忠实但较窄的发现 facet”，严格率可变成 R0 35/38、R1 37/38、R2 36/38。该敏感性不改主标签或 gate，说明评估高度依赖“完整关系 residual”与“探索 facet”的范围边界。

### 9. 历史 subnode-only 的 actionable addressability 提高多少？

R0/R1/R2 均 21/22=95.45% 形成有效局部目标。这是从既定 subnode-only whole-parent 标签到局部目标的描述性转换。历史 ID Selection 的 19/44=43.18% 属于不同输出任务，不能直接减出同口径提升或宣称闭环成功。

### 10. Z state 能否产生 faithful、low-commitment probe？

不够稳定。Z strict：R0 23/32、R1 25/32、R2 24/32；R0 Z mode 正确率 22/32。候选实体、书名或背景有时被称为 substantive support，导致错误使用 residual 模式。语义目标有效也不保证满足 probe 的执行接口。

### 11. Probe 是否获得新 material evidence？

按冻结机会口径，P1 7/11，P0 3/11；指可形成新 Claim 的可见机会，没有实际 Writer admission。P1 的 3 个直接增益来自婚育事实与临床病例，另外 4 个是桥接线索。它们都没有被宣布为最终正确候选。

### 12. 是否获得新 entity/relation binding？

P1 7/11，P0 3/11。桥接包括 professor/publication、游戏创办者的建筑捐赠线索、航空事故的国家/事件/日期。两个教授结果来自同一 qid 的不同 checkpoint，不是独立复现；同样不证明完整作者关系或航空事故与艺人的关系。

### 13. Probe 是否优于直接 coarse R 搜索？

冻结主指标 +36.36 pp，数值门槛通过。但排除 medium-ambiguity 增益后，P1 与 P0 都是 3/11。只保留遵守 objective-only 规则的查询，P1 2/11、P0 1/11，也无法通过。任务提供的 Q 被生成器用于补回 objective 没有的约束，因此不能把效果全部归于局部 probe 本身。

这些扩展来自已经提供的 Q，不是 future/Gold 泄漏，也没有插入外部具体候选；依照冻结区分，单列为生成规则偏离，而非不兼容的语义关系改写。数值 PASS 与协议遵从性不足同时报告。

### 14. NoGain 后正交 probe 救回多少？

固定 Parent 口径 0/2。两次 probe/query 都不是近重复，8/10 文档是相对累计 P1 workspace 的新文档，但目标关系没有新支持。G10 得到一个相邻问题中的有力导师候选；若采用较宽的 Q-level 口径，可描述为 1/2 潜在线索，不能补写为 Parent rescue。

### 15. Starvation 来自哪里？

全部 16 Z：7 个 bootstrap-success（其中 4 个桥接有歧义），2 个 query-limited，2 个上游格式/mode 阻断无法归因，5 个 accessibility uncertain 未进入主检索。没有依据把后两类写成 corpus 不存在。

G10/G20 的两次模型 probe 未获得 Parent gain；冻结 Oracle 查询均把已知有用来源放在 rank 1，原 localizer 也显示有用段落。这支持它们存在查询/源锚点瓶颈，不支持“检索器普遍可靠”。Oracle 带入未来已知实体/来源，不能当现实可用策略。没有运行 Writer，因此 evidence-recognition-limited 在本实验中不可识别。

### 16. 是否出现 candidate hardening？

E1 有 1 个 R2 输出把 Euler 生平线索提升成书中引用对象。另有 1 个 R0 输出把程序员本人的 Australia 条件附加到另外两位队友。E2 可执行查询未发现外部具体候选硬化；但 Q-context 扩展和 bridge 被过度解释的风险必须分别处理。

### 17. 是否需要 finer persistent control nodes？

目前没有足够依据直接增加。P subtraction 有效，subnode 局部目标也明显可寻址；主要未解决的是 coherent-control 范围、冷启动锚点和探测边界。若后续严格的范围定义仍导致 R0/R1 同时失败，再比较 finer nodes + source-span authority。

### 18. 是否需要新的 persistent State field？

本轮没有提供这种证据。未新增字段。应先保证已有 Q、固定 R、可追溯 Claims 在需要的临时控制视图中保留；不要把新增残差树当作信息投影问题的默认修复。

### 19. Q+R+C 是否已是足够的最小 persistent semantic state？

它是有希望的候选，尚未证明“足够”或“最小”。P 的证据支持当前 Claims 帮助减去已知部分；E2 只测了一次检索机会，且存在桥接/规则敏感性，没有验证 Evidence→Claim→next residual 的连续更新。residual/probe/support packet 继续保持 ephemeral。

### 20. 是否有资格进入独立 4–8 decision rollout？

按本轮预注册数值组合，P 入口与 E2 gate 都通过，允许另行注册小规模探索性闭环。但不应称为已稳定达标或直接运行确认性大 cohort。下一轮应先明确 bridge 的计分边界、Q context 在 query 中的权限，以及 E2B 是否需要当前 Claims 以避免 stale 回访；不必先加 State 字段。

本轮严格停止。下一轮若开展，必须独立 preregister `experiment/bootstrap-residual-research-loop`；此处没有执行任何闭环。

## 缓存、失败与完整性

|阶段|实际 API 调用|输入 tokens|cache hit tokens|加权命中率|
|---|---:|---:|---:|---:|
|E1|114|89,380|63,611|71.17%|
|E2|20|8,015|2,048|25.55%|
|E2B probe|2|1,121|0|0%|
|E2B query|2|783|384|49.04%|
|合计|138|99,299|66,043|**66.51%**|

总 tokens 289,947；completion 190,648，其中 reasoning 182,344 已包含在 completion 内，不重复相加。没有推测货币费用。

`INTEGRITY.json`：19,619 个历史受保护文件未变；全部阶段冻结文件不变；检索代码不变；模型、向量、语料资产完整 SHA256 复核；138 次 raw response/解析/usage 重放一致；105 个主实验窗口的原文跨度、hash 与 400-token 预算通过。所有失败保留，没有 retry、repair、best-of 或失败换样。

局限：single familiar reviewer、部分盲审、复用题目与相关 checkpoint、小 P 样本、单次 query、对桥接/范围定义敏感。不能用数值 PASS 替代这些边界。

## 可复核入口

- [E1 报告](../e1_residualization/REPORT.md)
- [E2 报告](../e2_bootstrap/REPORT.md)
- [E2B 报告](../e2b_escalation/REPORT.md)
- [逐状态 starvation 诊断](STARVATION_DIAGNOSTICS.json)
- [全部执行与缓存账目](EXECUTION_ACCOUNTING.json)
- [完整性审计](INTEGRITY.json)
