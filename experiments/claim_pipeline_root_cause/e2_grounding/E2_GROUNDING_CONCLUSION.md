# E2 Grounding Candidate-Anchoring Diagnostic

## Material Passport

Source base: `343b5a3d2ff4e05ec04302be9eb35534b71b86a1`. Branch: `experiment/grounding-candidate-anchoring`. Scope: frozen corrected E1 + historical actual Candidates; E2 only. Execution freeze commit: `69fde98d`; raw run commit: `56bd5b02`. Verification: 101 offline tests; complete 85-call run; single-reviewer source-only inventory review followed by separately marked outcome-informed case audit.

## 结论

**H3_NOT_SUPPORTED：完整门槛未通过。** FAR 从 4/5 降到 2/5，相对下降恰为 50%；但 G1 TPR 只有 22/30（73.33%），低于 85%。H_diagnostic FAR 仍为 2/2，TPR 降至 10/15（66.67%），没有严格同方向改善。

这次不能据此正式更换 Grounding。两个 rescue 来自同一个 q435 Inventory，而该 Inventory 整体遗漏了未定时的“67 albums”陈述。因此无法把拒绝归因于正确保留前提后识别了缺失的时间关系。q673 中，candidate-free Inventory 自身也把截断争议引文中的两条断言提升为无条件事实，Coverage 随后正常匹配并放行了它们。

## 固定输入与运行完整性

- 原 `freeze_e2_candidates` 未改动；实际重算与先前估计一致：35 pairs、15 distinct Evidence、85 calls。
- D：15 positive、3 negative；H_diagnostic：15 positive、2 negative。5 个负例仅来自 2 个 qids，且全部 ambiguous。源相对 truth 标签未根据本轮输出修改；不相关但 source-supported 仍是 positive。
- G0 35 次、Inventory 15 次、Coverage 35 次；全部 HTTP 200，schema/ref/model/finish/parse/transport failure 为 0，无重试、替换、修补或补采样。
- 每个 Inventory 为本阶段新建；仅向模型提供完整 public Evidence，物理落盘并绑定 hash 后才发送相应 Coverage。后者只见 Candidate + frozen Inventory。三个原语义 prompt byte-identical。
- thinking enabled，reasoning_effort high，temperature 0，max_tokens 32768，stream false，max_retries 0。
- 峰值并发 50；墙钟 69.02 秒；请求延迟 p50 1.62 秒、p95 35.27 秒、最大 54.19 秒。独立请求并行，依赖不越序。
- 85/85 usage 完整一致：input 91,089，output 173,109，total 264,198；cache hit 0，miss 91,089，**缓存命中率 0%**。缺失/不一致记录 0；未轮换 key 或 user_id。

## 主要结果

| Split | G0 FAR | G1 FAR | G0 TPR | G1 TPR |
|---|---:|---:|---:|---:|
| Pooled | 4/5 = 80% | 2/5 = 40% | 30/30 = 100% | 22/30 = 73.33% |
| D | 2/3 = 66.67% | 0/3 = 0% | 15/15 = 100% | 12/15 = 80% |
| H_diagnostic | 2/2 = 100% | 2/2 = 100% | 15/15 = 100% | 10/15 = 66.67% |

Pooled negative paired admission delta 为 −2/5 = −0.4。按 negative qid 等权：q435 为 −2/3，q673 为 0，平均 −1/3；两个 pooled 方向均有利。H_diagnostic 的 paired/qid delta 均为 0，相对 FAR reduction 为 0。未降低任何门槛。

Ambiguous-only FAR 与全部负例 FAR 相同：G0 4/5、G1 2/5。Nonambiguous-negative denominator 为 0，FAR **undefined**。这里的 80%/40% 是经过富集的五个歧义负例上的条件率，不能解释为实际工作负载中的总体错误率。

## Rescue 与 recall harm

两个 rescue 都在 q435：`E2_7da9dd0481c347fbad316074`、`E2_b50747a23a1e1241121dcbf6`。G0 的 reason 明确将相邻的“67 albums later”和 2016 采访绑定。G1 reason 表示 Inventory 未包含相应数量/日期主张。源审查在看 verdict 前已记录：Inventory 只有 2016 引语，完全遗漏了 album count。另一个 q435 负例被 G0/G1 同时拒绝；G0 在该表述上已明确指出 retrospective count 不必属于 2016。

q673 的两个负例均为 G0 supported → G1 supported。W11 的截断引文里没有可见的外层说话者名称，但有闭引号及争议上下文；不能补看 W12 来修复这个请求。Inventory facts 1、2 丢掉引文范围，Coverage 的 reason 是与 inventory 直接匹配。另一个独立 W12 完整来源 Inventory 保留了 Toshakhani attribution；这是可见上下文差异的描述，不是配对消融结论。

8 个 source-supported positives 出现 G1 recall harm：

| 数量 | Case / 问题 | 逐案解释 |
|---:|---|---|
| 3 | q261，D10 bibliographic claims | Inventory 留下 title/authors/citation，却没有保留 public W12 → D10 标识关系；Coverage 仅因 D10 未出现而拒绝。 |
| 2 | q186，DOS credits | 来源明确有 `Credits (DOS version)`，Inventory 拆出角色/姓名并保留 DOS release，却遗漏 credits 的版本限定。 |
| 1 | q637，病种标题 | 完整标题和病例事实仍在；Coverage 把“titled as FOP”解释成“标题精确等于短病名”。 |
| 1 | q922，Donovan memorandum | Inventory 正确保留 footnote states；Coverage 要求普通文献出处表述也进入 Candidate，拒绝了冻结标签认可的事实转述。 |
| 1 | q637，病程复合转述 | Coverage 质疑拆开后的 biopsy-site 关系，以及 progressively/subsequently 的转述。既有关系分拆也有措辞争议，不能简单归为纯遗漏；冻结 positive 标签保持原样。 |

每个 rescue、harm 和其他 negative 的完整 Candidate、Evidence、Inventory、两个 reason、qid、family、ambiguity 均在 `review/ERROR_CATALOG.json`。解释另存 `review/CASE_INTERPRETATION.json`。

## Inventory 独立审查与审查局限

15 份来源包共 365 facts。冻结的 source-only review 标记 **3/365 unsupported facts**：W11 两条 quoted proof/assertion 的 attribution/modality 提升；AC Milan 一条脱离例外条件的“无国内冠军”断言。Milan 的例外保存在紧接的下一 fact，故 inventory 整体可以恢复限定，但单条 universal 仍过强。

冻结审查在 5/15 Inventories 记录遗漏。其中 4 份涉及事实或范围的实质遗漏，另 1 份仅漏掉推广口号：争议引文范围、论文后半段条件/关系、完整文学评论的开头质疑、Mtukudzi 的 album count 等陈述。没有系统空输出或无法解释的全局退化，所以最终结论是 gate 不通过，而非因不可解释而改成 inconclusive。

**审查本身有遗漏，已如实保留并追加说明。** outcome-informed case audit 另识别了 DOS-credit header scope 和 D10 metadata binding 丢失。原 source-only labels 未覆盖这两项，也未事后改写。把这部分单列后，至少 **5/15 distinct Evidence 有实质遗漏**：原 4 份，加 DOS credits 1 份；D10 属于已有论文 Evidence。任意遗漏的并集为 6/15。这些计数的出处和区分见 `review/POST_OUTCOME_INVENTORY_AUDIT.json`，不能把事后发现冒称为先前盲审结果。完整病例的 same-site 联系问题仍按关系/转述争议记录，未为了提高遗漏数再加一个确定遗漏。

这说明 source-only 分离既可能损失来源陈述，也可能重复强化错误。事实支持率较高本身不能保证 Coverage 的 admission recall。单个 Codex reviewer 已知历史例子，packet 隔离不等于独立人工盲审，当前结果不提供独立 reviewer 一致性估计。

## 任务书 32 问

| # | 回答 |
|---:|---|
| 1 | 35 Candidate–Evidence pairs。 |
| 2 | D：15 positive / 3 negative；H_diagnostic：15 / 2。 |
| 3 | 2 个 negative qids：435、673。 |
| 4 | temporal 3；attribution_modality 2。 |
| 5 | 15 distinct Evidence。 |
| 6 | 85 calls：35 G0 + 15 Inventory + 35 Coverage。 |
| 7 | 是，所有列出的 transport/output contract failures 均为 0；语义错误另计。 |
| 8 | G0 FAR = 4/5 = 80%。 |
| 9 | G1 FAR = 2/5 = 40%。 |
| 10 | G0 TPR = 30/30 = 100%。 |
| 11 | G1 TPR = 22/30 = 73.33%。 |
| 12 | Pooled FAR relative reduction = 50%。 |
| 13 | Pooled paired-negative delta = −0.4，有改善。 |
| 14 | 等权 negative-qid delta = −1/3，有改善；仅两个 qids。 |
| 15 | 否。H_diagnostic FAR 2/2 → 2/2，paired/qid delta 0，TPR 10/15。 |
| 16 | 否。Pooled recall guard 和 H_diagnostic reduction/recall guards 均失败。 |
| 17 | 是。q435 三个负例中 G0 false-admit 2 个。 |
| 18 | 是。G1 拒绝 q435 3/3，但 Inventory 完全丢掉了 67 count。 |
| 19 | q673 两个负例，G0/G1 都放行 2/2。 |
| 20 | 不完全。完整 W12 保留多层 attribution，截断 W11 两条失去 quoted-account scope；并非 candidate-free 就可靠。 |
| 21 | source-only review：3/365 unsupported facts，涉及 2/15 Inventories。 |
| 22 | 至少 5/15 Evidence 有实质遗漏：4 份在冻结审查中识别，另 1 份由事后 case audit 识别；两种审查不混称。任意遗漏含口号为 6/15。 |
| 23 | 不是全拒绝：G1 仍接纳 22/30 positives。但召回损失过大，且两个 rescue 都与同一数量陈述遗漏相伴。 |
| 24 | 2 个 rescue，共用同一 q435 Evidence/Inventory。 |
| 25 | 8 个 recall-harm，分布于 q637、q922、q186、q261。 |
| 26 | Ambiguous-only FAR：G0 4/5、G1 2/5。 |
| 27 | 无；nonambiguous-negative denominator = 0，FAR undefined。 |
| 28 | 已观察到真实 source-relative false admission 和 G0 对相邻子句的关系补足；但当前消融无法把它独立归因于 Candidate framing，也未证明心理意义 anchoring。 |
| 29 | 不足以正式改变 Grounding；G1 recall guard 失败且不能防住已观察的 attribution errors。 |
| 30 | 不应按原 repaired-pipeline gate 进入 E3；H1/H2/H3 均未支持。未来可另行决定小规模现有系统 E2E 测实际 False C，属于新协议。 |
| 31 | **No**，E3 calls = 0；H_confirmation 保持未执行。 |
| 32 | **No**，production 与历史实验未修改。 |

## 停止位置与可支持的研究判断

本轮完成 bank freeze → G0/G1 → source-only inventory review → H3 analysis → conclusion，**STOP_AFTER_E2**。不增加 verifier，不调整三个 prompt，不修 Reader，不执行 Recovery 或 benchmark。

Grounding 的 authority boundary 确有 source-relative residual noise。这里观察到的是：**evidence-first commitment separation 降低了部分错误接纳，同时引入显著的信息保留和正常接纳问题，未形成通过门槛的替换方案。** 值得下一次决策的问题是这些残余错误在完整系统里实际形成多少 False C；当前富集 bank 无法回答其自然发生率。
