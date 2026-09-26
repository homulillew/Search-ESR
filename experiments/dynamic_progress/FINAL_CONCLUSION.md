# Dynamic Research Progress → Frontier：最终结论

## 结论与决策

**主实验未通过，停在 P1。** 显式 Progress 能指出真实缺口，但本轮没有证明它比旧 Residual 更可靠，也没有证明它足以控制 Frontier。一次“每个 blocker 一个关系”的有限探索有局部正向结果，仍不足以进入正式 P2–P4。

主集：24 个相对上一轮 F1 新的 Q+Claims checkpoint、10 个 qid，每 arm 两次；另保留24个旧 Challenge checkpoint。全部来自真实历史，未清理不利 Claims；不是新问题或新 U1 cohort。标签仅据 Q+Claims 在调用前冻结。研究者单人审查，schema可暴露条件，不能视为完全盲评或独立 gold truth。

## 主要结果

| 主集指标 | 旧 R（传输修正诊断） | B（原始调用） |
|---|---:|---:|
| 完成判断正确 |45/48|44/48|
| False closure |3/42（7.1%）|4/42（9.5%）|
| Correct closure |6/6|6/6|
| Valid blocker presence |38/42|36/42|
| Blocker precision |62/82（75.6%）|76/103（73.8%）|
| 过宽输出 |16/48|16/48|
| 无依据前提出现在输出中 |4/48|2/48|

B 满足冻结的 false closure、presence、correct closure 整数门槛，但 precision 未达到90%。B的4次false closure均来自q580的P17/P19；3个真实闭合控制仅覆盖2个qid。不能把这些相关重复样本当作独立大样本。

Challenge 上，B完成判断45/48，优于历史Direct的33/48；false closure从15/42降至0/42，但B有2次missed closure和1次未修复schema失败。这个非同期、已研究过题目的对照有价值，但不能覆盖新主集失败。

有限探索在12个选定checkpoint上，将precision从33/54（61.1%）提高到44/50（88.0%），过宽输出16/24→4/24，完成判断保持24/24；reasoning proxy增至1.89倍。它没有覆盖原来的false-closure checkpoint，不能证明闭合错误已修复，也不能覆盖正式gate。

## 必须披露的运行偏差

原冻结批次216次HTTP请求中，R的96次和FULL的24次因缺少JSON mode所要求的“JSON”字样被HTTP400拒绝。这是实现错误。全部120条原始失败保留，没有计为模型语义失败。

单独commit/freeze后，仅对这120个没有模型输出/usage的拒绝请求追加`Return JSON.`格式指令，进行了120次额外提交。Q+Claims和旧R系统prompt保持不变，已成功B输出不重采样。R/FULL比较因此是带格式和执行时序差异的修正诊断，不是无偏差完成的原始随机批次。原分母、修正批次和唯一24次语义探索分开保存。SDK重试为0，**额外HTTP提交确实发生过**。

总计360次HTTP提交：120次400、240次200。240个模型响应均报告deepseek-flash，其中1个B响应缺少必需字段而失败，不修复、不替换。没有Search/Find/Open、Writer、Frontier调用。全部usage记录的缓存命中率63.98%（160,886 / 251,448输入token）；reasoning-token proxy合计1,016,520，不等于真实推理质量或计费核算。

## 对17个研究问题的回答

1. **Q+Claims能否可靠判断material blocker？** 能识别许多缺口，但尚未达到预注册的整体可靠性。B的完成判断44/48、presence36/42；precision73.8%，严格加入status/ref/witness后仅16/48输出充分合格。
2. **False closure到底多少？** 主集B4/42=9.5%，全部集中在q580；Challenge B0/42，但另有1个无有效输出的失败，不能算作安全判断。不能仅凭Challenge零false closure宣称可靠。
3. **Dynamic Blocker比旧Residual更可靠吗？** 主集没有：B44/48 vs R45/48，precision73.8% vs75.6%；两者充分合格输出均23/48。Challenge B有局部提升，但R/FULL还存在上述技术修正限制。
4. **完整decomposition有额外价值吗？** 有局部精度收益：同12个checkpoint上FULL168/177=94.9%，BLOCKER42/53=79.2%。但完成判断同为22/24；FULL少1次false closure、多1次missed closure，双次完成判断一致10/12 vs12/12，reasoning proxy为2.52倍。没有支持持久Requirement Map的证据。
5. **容易发明requirement吗？** B主集3/48、Challenge6/48输出有此问题；FULL4/24。常见于要求额外的别名、精确背景措辞或冗余年代佐证。materiality必须区别真正身份/最终关系缺口与附加佐证。
6. **会把question constraint偷渡成candidate fact吗？** 会。B主集2/48有无依据前提，其中P24把Liverpool–Milan的进球顺序证据升级成95分钟任意球事件；P14从出生日期引入Claims没有提供的生肖映射。不能把输出gap直接当作已成立候选事实。
7. **正确blocker后Selector能稳定产Need吗？** 未测，P2未运行。
8. **Oracle和Generated Blocker差多少？** 未测，不能用P1precision代替Selector因果对照。
9. **Direct与Progress-assisted Frontier差多少？** 新鲜Need级对照未测。Challenge只比较历史Direct的完成判断，不是两阶段Frontier质量。
10. **Claims mutation后blocker会合理消失/出现吗？** 未测，P3未运行，没有构造人工post-state替代真实transition。
11. **H变化但Claims不变需要重算吗？** 实现按本轮假设不重算；代码检查通过。没有新的语义证据支持增加触发器，也未通过真实transition证明充分性。
12. **Q+Claims hash缓存成立吗？** 机械复用、Claim变更失效、Q变更失效及H/Workspace/attempt不触发均已检查；语义充分性仍未验证。这个操作缓存不把Progress变成persistent Research State。
13. **减少premature STOP吗？** 相对历史Challenge Direct有明显描述性信号（15→0），但主集B比R多1次false closure。尚不能推广为一般改善。
14. **减少whole-question Need吗？** Need未生成，不能回答。原B与R主集过宽输出均16/48；唯一探索把选定样本的过宽blocker从16/24降至4/24。blocker变化不等于Need变化。
15. **减少unsupported premise吗？** 主集B2/48 vsR4/48是小样本方向信号，尚不足以断言稳定减少；B仍存在清楚的错误证据升级。探索样本原本就没有此类错误，不能据0→0宣称修复。
16. **提升deferred requirement自主重新激活吗？** 未测，P4未运行。没有声称完成Progress→Need→检索→Observation→U1 Claim闭环。
17. **主要瓶颈在哪里？** 当前可观察瓶颈在Progress：gap粒度、materiality、缺失关系绑定、status和closure witness。Frontier、Retrieval、Admission在本轮均未接受新的因果测试，不能据此归责或改造。

## 机制解释与研究边界

“知道还没完成”与“提供可用于后续控制的理由”需要分别验证。B的完成判断可以正确，同时输出多个冗余或过宽gap；它也可能稳定重复同一个错误闭合。有效Claim索引不是语义支持验证。

按预先冻结的rubric，过宽unit不能计入precision。事后仅移除这一项惩罚，B有96/103（93.2%）unit没有其他内容错误。这是解释失败来源的敏感性结果，不是重设gate；仍有false closure、无依据前提以及9个status错误和不完整closure witness。

一次窄化指令能改善gap粒度，说明有可继续验证的方向。但它仍未达到原precision门槛，而且成本上升，未覆盖停止错误。下一轮若继续，应在新bank上验证停止判断与单关系blocker，保留真实闭合控制；本轮不再追加prompt sweep或跨gate运行完整系统。

Persistent语义State继续只有Original Question、Verified Claims、Working Hypothesis。Progress仍是基于当前Claims的派生判断，尚无资格作为未经验证的停止或动作权威。本轮没有引入固定问题拆解、hard gating、额外State字段或新的工具。

## 完整性与复现

基线为远程`experiment/frontier-generation-state-sufficiency`的`fafe06019326cef35aa40f6e6092bbb5c725306f`；新分支`experiment/dynamic-progress-blockers`。设计e24798c，原始冻结e91216f，传输修正冻结c386274，唯一探索冻结391b951。执行期间有仅增加审查/记录的commit；每请求记录实际HEAD，冻结runtime/输入hash始终一致。

审计确认10,478个历史tracked文件字节未变；48个State与历史库存完全一致；360个请求及审查全部可追踪。旧实验标签/结果未改写；用户既有未跟踪目录未动。详见[完整性审计](analysis/INTEGRITY_AUDIT.json)、[主实验](p1_progress/RESULTS.md)、[FULL敏感性](decomposition_sensitivity/RESULTS.md)、[有限探索](exploration/RESULTS.md)及[Gate记录](analysis/GATE.json)。
