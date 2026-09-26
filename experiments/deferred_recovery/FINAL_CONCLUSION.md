# Deferred Recovery：Global Rediscovery 与可选 Local Reuse

## 结论与研究门槛

**本轮有支持普通 Global Search 恢复遗漏事实的机制信号，但没有完成足够规模的新鲜样本确认。**

冻结的五个 D3/D4 诊断案例中，G（v3a Search only）全部重新取得证据并写入可用 Claim；H（相同 Search + 可选 Find/Open）严格口径恢复三个。H 少用 37.80% token，但恢复质量不相当，也没有增加独有成功。数据支持继续将普通 Global Search 作为下一次确认实验的简洁基线；尚不能宣称它已足够支撑普遍的 aggressive selective admission，也不能据此删除 Find/Open。

**Primary gate：`UNASSESSABLE_INSUFFICIENT_FRESH_BANK`。** 已冻结的 bank 只有 5 个 D3/D4 案例、4 个 qid，其中只有 1 个 fresh case；q311 占 2/5，亦超过 25% 分布目标。连混合诊断集都未达到 12 cases / 6 qids 的最低规模。另有 D2 safety 和 D1 immediate control 各一个，未混入 deferred 分母。该限制在模型调用前已提交，不能用漂亮的 5/5 覆盖。

本轮已完成 28 次 Actor、72 次 U1 Writer、21 次工具调用。无 retry、repair、best-of、接口失败或工具失败。R1 的真实结果原样延续至 R2；最多两个 decisions，无 gold 在线停止。未执行额外 exploration 或 G4/G5。

## 结果及口径

|Cohort|案例数 / qids|G 严格 Need Claim 恢复|H 严格恢复|H 放宽日期的 sensitivity|
|---|---:|---:|---:|---:|
|Fresh D3|1 / 1|1/1|1/1|1/1|
|Known D3/D4|4 / 4|4/4|2/4|3/4|
|D3/D4 混合诊断集|5 / 4|5/5|3/5|4/5|
|D2 belief conflict，单列|1 / 1|1/1|1/1|1/1|
|D1 immediate miss，单列|1 / 1|1/1|1/1|1/1|

Known 包括已分析 source/atom 的新历史 context、两个已知 U1 challenge，以及一个已知 reviewer-normalized Workspace omission。最后一类不冒充真实 U1 拒绝事件。372 个真实 G5 updates、289 个不同 `(qid, observed text)` 组曾进入机械 inventory；后续 semantic review 是定向筛查，不声称穷尽整个仓库后仅存在这些遗漏。

|D3/D4 两步指标|G|H|
|---|---:|---:|
|充分 Need Evidence 可见|5/5|4/5|
|严格 Evidence → Claim conversion|5/5 = 100%|3/4 = 75%|
|严格 Need Claim 恢复|5/5|3/5|
|原先遗漏的同一事实恢复|5/5|2/5|
|只放宽 DR04 日期要求|5/5|4/5|
|Actor calls|10|10|
|Tool calls|7|8|
|Search / Find / Open|7 / 0 / 0|2 / 6 / 0|
|Writer calls|35|15|
|Input + output tokens|163,728|101,836|
|输入 token 缓存命中率|55.54%|48.59%|

两个口径差异必须保留：

- **DR03 runtime：** H 写入了 5 分钟 / 21 分钟 specials 的来源证据，可用于反驳严格的 `<5 minutes` 条件。预先冻结的 protocol 允许这种 grounded refutation，所以计入 Need-information recovery；H 没有恢复原先 AlloCine 的 4 分钟事实。G 保留了 4 分钟及其他来源的 5/11/21 分钟信息，来源分歧仍未解决。二者都不等于完整节目资格已裁决，更不等于原问题已回答。
- **DR04 maximum breaks：** H 的新 Observation 含 2011 年第四次、2013 年第五次、2016 年第六次等日期，但 Writer 只保存了未限定日期的七次总数。冻结 rubric 要求 `by 2025-01-30`，不允许把当前未注明日期的总数自动倒推至截止日前。因此严格口径为 admission scope failure；只评估 `>3` 数量时则通过。这个 sensitivity 不替换主标签。

配对结果：严格口径为 3 both-success、2 G-only、0 H-only、0 both-fail。放宽 DR04 日期后为 4 both-success、1 G-only。相同 qid 的案例有关联，每个 arm 只有一次采样；不作独立样本 p-value 或总体稳定性宣称。

## 逐例机制

|Case|G 路径与结果|H 路径与结果|解释|
|---|---|---|---|
|DR01 教育目的，fresh|Search 首步恢复并写入；第二次 Search 无额外教育证据|Find 无匹配 → Search 恢复并写入|普通 Global fallback 有效；首个英文 source 本身未必错误，局部 query 没命中|
|DR02 Game B 年份|Search 恢复 1998 年，另有新来源日期支持 → Stop|Search 恢复 1998 年 → Stop|H 也选择 Global Search，没有 local 独有收益|
|DR03 时长 refinement|Search 恢复 4 分钟并保留反向来源 → 再 Search 获得季别信息|Find 获得 5/21 分钟反证 → Find 另一语言 Wiki 再证实，Writer 空更新|H 恢复有用 Need 信息，未恢复原 4 分钟 atom；第二次是语义重复佐证|
|DR04 截止日前满分杆次数|Search → 带 2016 年第六次等日期的 Claim → Stop|Find → 未限定日期的七次 Claim → Stop|证据取得成功；H 的 persistent Claim 遗失必要时间范围|
|DR05 总季数|Search 直接返回 `num_seasons: 5` → 写入 → Stop|两次 Find 同一正确 D，均返回演员表，只支持至少五季|local query/window failure；Writer 的上界 Hypothesis 无依据，但第二步 Actor 没有接受它|
|DR06 1992/1993 冲突，D2|首步 Search 即保留 1993 与已有 1992 的分歧|Find 仅佐证已知 1992 → Search 才写入 1993|冲突能恢复，不证明延迟冲突信息安全|
|DR07 文章日期，D1|Search 恢复 July 24 与电脑配置关系 → Stop|Find 恢复同一关系 → Stop|当前 Need 聚焦后可重写，属于 immediate Writer control|

DR05 H 的 Claim “至少五季”有支持；Hypothesis “可能少于十季，因为演员表列到第五季”缺少上界依据。它是 Hypothesis 的不当提升，不能记作有效 Claim Recovery。第二步 Actor 明确指出总季数尚不确定，继续检索，最终受两步 horizon 限制。DR03 G 曾在时长反证后清除 candidate，又基于名称关系重建 candidate；Claim 没有删除，但 candidate persistence 仍需审慎解释。

## 任务书要求的 20 个回答

### 1. Deferred omission 有多少通过普通 Search 恢复？

五个 D3/D4 诊断案例，G 全部在第一个 decision 取得充分证据并写入必要 Claim，原先遗漏的事实亦恢复。唯一 fresh case 为 1/1；其余四个有历史熟悉度，不能合并解释成新鲜泛化验证。

### 2. Global Search 能否稳定重新发现 old source？

本轮观察到持续命中，但规模不足以确认普遍稳定性。三份真实文档的预调用 audit 证明：固定 Global hit 条件下，v3a 会用当前 query 重新定位旧 D；v3b 仍保持 metadata-only 语义。这项 audit 不是 corpus recall 测试。真实恢复调用另外验证了 corpus 排名与局部窗口表现，两者不能混同。

### 3. OldDocRecall@5 是多少？

G：D3/D4 首步 5/5；两步所有 Search 调用 7/7。加入单列 controls 后是 10/10。H 的实际 Global Search 为 D3/D4 2/2、全诊断 3/3。H 首步五个 deferred decisions 只有一个 Search，不能把该条件分母解释成五个首步均成功。Rank 6–10 未测量。

### 4. Old Evidence Visibility@5 是多少？

G：D3/D4 首步 5/5；两步所有 Search 为 6/7 = 85.71%；含 controls 为 9/10 = 90%。差别来自 DR01 已恢复后的第二次 Search：仍命中目标旧 D，但新局部窗口只讲角色，没有教育目的。H 的实际 Search 为 D3/D4 2/2、全诊断 3/3。文档命中不自动等于所需证据可见。

### 5. Recovery 来自旧 Source 还是新 Source？

G 五个 deferred case 的首次 Claim 恢复都来自旧来源重新发现。H 三个严格成功中，两个来自 Search 重新发现旧来源，一个来自旧 D 的 Find。G 在 DR02、DR04 还获得新来源的额外支持，但没有案例只能靠新来源成功；exclusive New-source Recovery 为 0。不能把两个补充来源计成两个新来源独有恢复。

### 6. Need 成为 Current Gap 后，U1 能重新写入吗？

可以，本轮 G 的五个案例均重新写入。U1 prompt 与历史版本字节相同，Current Research Gap 明确设为冻结 Recovery Need。H 暴露了必要日期范围被省略的反例。因此“现在聚焦后可以重写”有实例证据，“所有合理遗漏都能可靠恢复”尚未验证。

### 7. Evidence → Claim conversion 是多少？

D3/D4：G 5/5，H 3/4。若只评估数量而忽略 DR04 日期，H 为 4/4；严格语义主口径保留 3/4。包括不同性质 controls 的混合描述值是 G 7/7、H 5/6，不能替代 deferred 指标。

### 8. Global-only recovery success 是多少？

严格 Need-information recovery 为 5/5，fresh 单列 1/1。该结果达到数值参考线，但 bank 完整性不达标，不能据此把 Reference-design gate 写为 PASS。

### 9. Hybrid recovery success 是多少？

严格为 3/5；放宽日期要求为 4/5；只计原先遗漏的同一事实为 2/5。差异分别来自 DR04 的日期范围和 DR03 的反证替代。单列 fresh 为 1/1，发生在第二步 Global Search。

### 10. Find/Open 增加多少独有成功？

H-only 为 0。Need-bearing Find 为 3/6，其中一次只是对已持久化时长的第二来源佐证；排除该重复信息，首次充分 local-evidence yield 为 2/6。含 controls 分别为 4/8 与 3/8。Open 没被选择，不能推断 Open 的成功率或必要性。

### 11. Local reuse 是否降低 cost/latency？

Token 有明显描述性下降：H 101,836 vs G 163,728，减少 37.80%；恢复质量同时下降。工具数 H 8 vs G 7，没有动作成本优势。G 全部首步取得证据/Claim；H 的 DR01 需第二步，DR05 未恢复，DR04 严格 Claim 未恢复。没有观察到 decision latency 优势。Search 通常产生五个 Writer 输入、Find 通常一个，这解释了成本差的一大部分。并发请求耗时之和不等于端到端墙钟时间。

### 12. 是否出现 source lock-in？

按配对操作性定义，有一个两步 local-path regression：DR05 H 连续 Find 同一 D 未恢复，G 成功。首步 local 未取得新必要证据而 G 成功的还有 DR01、D2 DR06。这里没有证明“必须换新 source 才能解决”的强 lock-in；DR05 的正确旧文档本来就含总季数，直接失效层是 query/window。此区分保留在逐例报告。

### 13. 哪些 omission 是真正 Immediate Writer failure？

DR07 的文章日期在当时 Current Gap 中已明确需要，却未写入，是 D1。冲突证据 D2 也有即时 belief revision 价值，应另列。反过来，已有 1982 年冠军足以满足 1973–83 年赢过赛事时，未保存额外 1974 年 double 不能自动算失败；“第一次 147”单独也不足以证明 `>3`。

### 14. 哪些 omission 可以安全 deferred？

本轮支持“部分 off-focus 原问题 requirement / material refinement 具有可恢复性”：教育目的、游戏年份、节目时长、截止日前满分杆次数等。安全性仍有条件：当前不需要立即修订的事实、真实来源仍可访问、Need 后来正确激活、检索与 Writer 能保留必要范围。当前仅测试外部冻结的 Recovery Need，没有测试 Actor 是否会自主重新激活所有遗漏 requirement；因此还不能确认系统级安全 deferred。

### 15. Belief conflict 应为 Immediate Admission exception 吗？

建议保留这一原则。DR06 两组后来均能恢复 1993 与 1992 的来源分歧，H 晚一步。本小样本未观察到恢复前错误行动或过早结束，但没有足够 rollout 排除即时错误 belief 的影响。不要用 later recoverable 推导 conflict omission safe；本轮未裁决哪个年份是真实最终答案。

### 16. Provenance-only update 应计入 Claim Recall 吗？

不应要求 duplicate semantic Claim。D6 1992 corroboration 被从普通恢复分母排除；DR06 H 的首个 Find 新窗口仍保存在 Workspace、registry 与 trace，即使 U1 空更新仍可追溯。现有 schema 未给同一 Claim 自动合并 support_ref，本轮也未新增合并逻辑或 Claim graph。记录到证据和合并进 Claim provenance 是两回事。

### 17. Global Rediscovery 足以支撑 aggressive selective admission 吗？

已有局部机制支持，尚无充分总体证据。数值上 G 5/5 恢复、5/5 conversion，但 fresh 只有一个，且 Need 由实验冻结；没有 end-to-end eventual recall、大规模多样需求或自主重激活确认。还需区分 U1 会丢失哪些不可安全延迟的范围和冲突事实。

### 18. Reference Harness 需要专门 Recovery policy 吗？

本轮没有支持新增 Recovery tool、semantic Workspace→Corpus router 或 local-first policy。普通 v3a Search 已实现全部诊断恢复。H 的 token 优势值得留作成本问题，但没有满足“相当成功率且成本下降”的采用条件。由于 fresh bank 不足且 H 确有成本下降，也不把 G 数值表现直接解释为完整 Reference-design 规则已通过。

### 19. 仍需区分 old/new source scope 吗？

离线评估和 provenance 需要区分，以辨认 rediscovery、local reuse 与新来源支持。本轮没有证据要求 Runtime 先做 old/new 的语义路由决策。统一 Global Search 让两类文档参与同一排名，机械 registry 继续保存来源身份即可。

### 20. 下一步能否进入 cleaner State 的 G4/G5 controller comparison？

**本轮不进入。** 先补充真实、未用于前序机制分析的新鲜 D3/D4 omission，冻结满足分布要求的确认 bank，再验证 scoped Claim recovery。当前失败并未证明允许的 A–E remedy 能修复主要限制，因此未使用一次探索额度；理由见 [EXPLORATION_DECISION.md](EXPLORATION_DECISION.md)。不以扩大实验阶段替代缺失的恢复性证据。

## 成本、完整性与可复核边界

全部 100 次请求共 232,294 input、129,771 output tokens；其中缓存命中 123,134、未命中 109,160，加权命中率 **53.01%**。所有请求均返回 usage；完整分 arm、case、stage 的数据见 [COSTS.md](analysis/COSTS.md)。缓存按实际 usage 记录，未用推定价格计算美元成本。

10,318 个历史文件、36 个冻结输入文件、17 个大型资源/配置文件核验通过；大型资源合计重新哈希 20,121,459,507 bytes。72 个新 Observation 都能对应冻结 corpus 原始 substring，72 个 U1 proposals 均机械原样应用，没有根据 reviewer 改写 State。原始结果、单次失败记录结构、历史 registry 和两步 trace 全部保留。详见 [FINAL_INTEGRITY.md](FINAL_INTEGRITY.md)。

Semantic labels 是单 reviewer Codex 审核，未声称盲评或独立复核。完整性 PASS 只证明记录和执行约束一致，不证明标签无误，也不替代不足的 primary cohort。当前目标仍是：当一个 requirement 真正成为 Need 时，系统取得适当来源证据，并把保留必要范围的事实重新写成可用 Claim。
