# Minimal Need → Multi-Query：当前交付结论

## Material Passport

- Status: **PREPARED_FOR_REAL_RUN**.
- Scope: E0 单 reviewer 离线复审 + E1 开发阶段设计、实现、输入冻结和离线验证。
- New paid model / Search / Find / Open / Writer calls: **0**.
- Source: 历史 B5 自然 QCH、原始请求/响应、Claim 来源记录；历史文件未改。
- Model policy: DeepSeek `deepseek-flash`, temperature 0, JSON mode, max_retries=0, omit max_tokens。

## 已观察与审阅结果

E0 五个旧 W 中，**2 个仍为 W_independent，3 个为合法 W_multiquery**。三个重分类涉及两道题，其中 DLC 的两条是同题不同状态。出版内容特征和 DLC 发布特征可以共同服务一个判断；捐赠+婚姻、晋升+教育仍是独立目标捆绑。这是有歧义的单人 rubric correction，没有改写历史 16/27 或 FAIL。

E1 已准备 **18 个自然状态 / 9 个 qid / 8 个 No-H，四臂共 72 次调用**。包含旧四个 P、一个 A、五个 W 和八个有效控制。B0 原样复用 B5 请求；其余臂只追加任务指定规则。29 条去重 Claim 继承已归档来源支持审计，18 份已观察来源保留机械核验；H 均保留自然 Writer 轨迹来源和 provisional 地位。

离线测试与 dry run 检查请求隔离、零重试、失败保留、授权守卫、完整分母和缓存账目。它们证明执行合同可用，不能证明 Need 策略有效。具体提交、测试与历史哈希检查见 [完整性记录](analysis/FINAL_INTEGRITY.json)。

## 诊断解释和下一步

新定义减少了旧 W 中的过度惩罚，但本轮尚未测量 Premise Closure 或 Coherence 指令是否改变模型。B2/B3 的追加规则与旧 B5 单关系表述存在张力；它被显式保留以满足原样基线及 append-only 消融要求。若行为机制不能分离，应先分析，最多一次单独冻结修订，不能直接宣布完整架构失败或进入 fresh。

任务书 §35 要求当前任务明确授权真实付费调用；此次消息没有附带该授权。因此停在准备完成。首个可运行批次为 72 次 E1 调用，最多八路并发。按所选历史 B5 用量乘四，输出约 **378,420 tokens**，输入至少约 **37,956 tokens 加新增 prompt**，仅为预算代理；缓存及推理长度可能改变实际费用。历史逐调用极长推理已纳入估算，不重新加 4096 限额。无当前核验单价，不虚构金额。

## 任务的十五项问题

| # | 问题 | 当前回答与证据类型 |
|---:|---|---|
| 1 | 旧 W 有多少合法 multi-query Need？ | **3/5**，单 reviewer 离线标签；另 2/5 独立目标。 |
| 2 | Premise Closure 定向减少 P/A？ | **未测**，B1 待调用。 |
| 3 | Coherence 定向减少真正 W？ | **未测**，不能把 E0 重分类当 prompt 效果。 |
| 4 | Combined 在 completely fresh QCH 复制？ | **未测**；现有 18 条全部已暴露。 |
| 5 | Need 能保留一个自然语言字段？ | **工程上已准备**；仅 `need` 为可变语义字段，固定 research 标签保证 B0 不变；可靠性未证。 |
| 6 | 等预算 fan-out 提高 useful evidence？ | **未测**，E2 gate 未开。 |
| 7 | 增加漂移或重复检索？ | **未测**，协议已要求单列。 |
| 8 | 需要 Probe / NeedSpec / ResolutionCriterion？ | **没有新增必要性证据**；当前未增加。 |
| 9 | 需要 persistent dependency graph？ | **没有新增必要性证据**；保留顺序执行依赖的假设。 |
| 10 | Q+C+H 足以重新激活 deferred constraints？ | **未测**，E3 缺合格自然 bank。 |
| 11 | 强 H 仍引起 premature closure？ | **本轮未测**；历史风险不能变成本轮频率。 |
| 12 | Strict Closure 在 fresh near-closure 工作？ | **未测**。 |
| 13 | 完全 held-out minimal loop 能运行？ | **未测**，E4 未采样或运行。 |
| 14 | 若失败，在哪层？ | **本轮无新模型失败可归因**；旧 P/A 与真正 W 是待检验机制，rubric 问题已确认存在于复审。 |
| 15 | 哪些结构被 failure-driven evidence 要求？ | **本轮没有证据要求增加结构**。未来必须由对应 gate 的真实失败推动。 |

## 工程建议

授权后先运行已冻结 E1 开发批次，做完整语义审阅并检查机制分离；满足条件才另行冻结新 qid 的确认实验。E2–E4 目前仅保留阶段协议，没有伪造输入、raw outputs 或成功指标。持久语义继续只有 Q + Verified Claims + provisional H。

---

# 授权后执行更新（当前结论）

上述 PREPARED 部分保留授权前历史。本轮已执行108次真实API调用。E1 v1及唯一修订均未通过；修订同期B0为10/18，B3为2/18，按任务Gate停止。Fresh confirmation与E2–E4均未运行。缓存加权命中率51.32%，保留1个length failure且零重试。完整执行结论与证据见 [EXECUTION_CONCLUSION.md](EXECUTION_CONCLUSION.md)。

## 执行后的十五项回答

| # | 研究问题 | 当前回答 |
|---:|---|---|
|1|旧W有多少是合法multi-query？|**3/5**，来自2个qid；单人离线复审，保留歧义。|
|2|Premise Closure定向减少P/A？|**没有**。v1 B1的P+A为5，B0为4；修订B3仍有多个明确的候选事件偷渡。|
|3|Coherence定向减少真正W？|**没有证据支持**。v1 B0为0、B2为1；修订B3为6。地板效应阻止原预期效应的识别。|
|4|组合策略在完全fresh QCH复制？|**未测**。开发门槛未过，没有采集或调用fresh样本。|
|5|Need能否只用一个自然语言字段？|**输出接口可行，稳定语义可靠性未成立**。107/108输出符合原双键信封，唯一可变语义字段仍是need；这不等于strict有效。|
|6|等预算多Query提高useful evidence？|**未测**，E2未运行。|
|7|多Query增加漂移或重复？|**未测**，本轮没有生成或执行Query。|
|8|需要Probe/NeedSpec/ResolutionCriterion？|**没有足够证据证明必要**；本轮失败发生在QCH→Need，尚未隔离Need→Action。|
|9|需要persistent dependency graph？|**没有**。局部前提失败不足以支持持久图结构。|
|10|Q+C+H能重新激活deferred约束？|**未测E3**。两个stale Need说明存在选择问题，但不能据此证明状态表达不足。|
|11|强H仍造成premature closure？|**本轮未测closure**；固定research输出没有STOP。No-H修订也失败，不能把全部问题归因于H。|
|12|Strict Closure在fresh near-closure工作？|**未测**。|
|13|完全held-out最小闭环能运行？|**未测**，E4没有启动。|
|14|失败发生在哪层？|**主要是QCH→Need选择/前提绑定/目标范围/未解决性**；另有1次provider length failure。没有本轮Retrieval/Writer/Closure归因证据。|
|15|哪些额外结构被failure evidence要求？|**没有结构被证明为必需**。证据支持下一次诊断短暂premise extraction及小型临时分解的合理性；不支持persistent Frontier、Requirement Map或Dependency Graph。|
