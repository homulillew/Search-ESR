# V3 Design Audit — 两项混杂修复与重验证

## Material Passport

- 日期：2026-09-26；阶段：代码修改与真实调用前的设计审计。
- 远程稳定基线：`origin/experiment/goal-residual-control-contract-v2-executed`，`32de7c8c7fb3ff197b16632079e43a33c52f372e`。
- 新分支：`experiment/goal-residual-control-v3-admission-structured`。创建前已检查远程，无同名分支。
- 数据：仓库中冻结的 v2 请求、来源窗口、状态和输出；单 Codex reviewer。没有独立人工复核，也不声称 reviewer 之间独立。
- 本文是本轮第一个新增文件；尚未修改执行代码，尚未发出模型调用。后续只有 capability / preflight 通过后才允许 Admission Replay。

## 1. 两项已识别混杂

**Admission context 缺失。** v2 `harness_v2/adaptive.py:update_view` 只传 Original Question、Verified Claims、Working Hypothesis、当前 Observation，没有产生该 Observation 的 Actor Gap。原 prompt 要求来源支持和最多两条 Claim，却没有完整的决策相关性与相对现有 Claims 新颖性标准。G5 的 503/504 来源支持率与 369/504 incidental admission 同时成立；不能把前者当成合格持久状态的充分条件。

**接口是事后验证。** v2 `runtime.py` 使用 Chat Completions 自由文本，再做 JSON 解析、固定 schema 验证和 registry 检查。G2/G4/G5 仍有 Find 多余 `k` 和 trailing comma。另有一次 Updater 达到输出长度上限；这种 incomplete failure 必须与纯格式错误分别保留，不能承诺 schema 会消除所有失败。

v2 不是“没有贡献”：显式 prompt contract 已使 G2 有效率从 75/120 提升为 118/120。这里不修改历史 parser 或重新解释历史 invalid。

## 2. 已有实验依据及边界

已阅读指定的 v2 总结、勘误、provenance、G2/G3/G4/G5 报告，以及 `harness_v2` 的源代码、prompt、schema、合同审计与离线记录。

已阅读四份指定前序材料：

- `gap_evidence_claim_loop/FINAL_CONCLUSION.md`：F1 Observation-only 产生 67/110 无关 Findings；加入 Gap 后为 1/46，加入既有 Claims 后为 0/38，并得到 29/32 必要事实召回。严格审计有一例额外推断，因此不把 curated 结果称为普遍保证。
- `gap_evidence_claim_loop/single_gap_rollout/RESULTS.md`：真实短 rollout 两组均只有 1/6 Claim-based closure；有漏读直接 Forbes 窗口、时间绑定错误和来源身份丢失。更多有用原始窗口没有自动转为闭合。
- `minimal_research_loop/FINAL_CONCLUSION.md`：自然 Reader 53/55 有来源支持，但同时满足支持、相关、新颖的只有 47/55；来源 Verifier 没有解决六条 Gap 无关 Findings，集成 gate 未通过。
- `minimal_research_loop/prompts/reader.md`：Question/Gap 定义相关性而不是证据；已有 Claims 用于去重；没有新且相关的事实时应返回空列表。

这些结果支持修复已有 admission 边界，不支持新建 ontology、Verifier 或更多持久字段。历史 Reader 的 0–3 Findings 上限不带入本轮；Updater 保留 v2 的每 Observation 最多两条。

## 3. Fix A 的精确定义

所有 controller 使用相同 Writer：

`Question + Existing Claims + Working Hypothesis + Current Actor Gap + Observation → Claims / keep|set|clear`

Current Actor Gap 来自生成这批真实 Observation 的 Actor output，两个独立动作及其所有窗口共享该决策的 Gap。它只进入当前 Updater request，不能新增到 committed semantic state。L0 原有 prior-focus 保存仍保留；它是既有 controller treatment，不是新增 semantic-state 字段。L1/L2 不额外持久化 Gap。

本轮追加的 admission 条件是：直接支持、相对现有 Claims 新颖、当前决策有实质价值。允许原问题其它未闭合必要条件、支持/反驳候选、以及改变研究方向的事实。不能收窄为逐字回答 Gap。空 Claims 是预期输出。Gap、query、问题中的猜测不能填补 Observation 中缺失的实体、时间、数量或关系。

G5 必须逐项保存 `cell + round + actor_request_hash + exact_gap + observation_hash` 的绑定。Admission Replay 从该绑定恢复 Current Gap，不能使用下一轮 Gap、Residual、后验正确答案或人工改好的焦点。G4 在调用前须沿 transition 的历史 source_path 追溯其产生观察时的冻结研究焦点；若历史记录只有归一化 prior focus，将明确记录来源，不伪称为自然 Actor 输出，也不生成一个新的替代 Gap。不可追溯的输入构成阶段设计缺口，不能静默补造。

## 4. Fix B：拟采用机制与证据标准

优先尝试同一 `https://api.deepseek.com`、同一 `deepseek-flash` 的 **Responses API `text.format.type=json_schema`**，完整 Actor / Updater / Reviewer schema 作为请求参数传给服务端。保留原 system/user 文本及角色顺序，只映射 API envelope；不借机改 Actor/Reviewer prompt。研究请求继续省略 v2 未显式设定的采样参数，记录 endpoint 默认行为这一潜在混杂。

官方 [Responses API reference](https://api-docs.deepseek.com/api/create-response/) 描述了 JSON Schema 输出；[兼容性指南](https://api-docs.deepseek.com/guides/responses_api/) 说明 `text.format` 支持、部分其它参数会被忽略。文档不等于已验证当前账户、模型及所需全部关键词有效。**截至本审计，能力仍未确认。**

所需约束包括封闭对象、必填键、enum/const、Actor 根及动作的 oneOf、数组长度、Search k 的整数范围、Find 无 k。保留运行时 D#/W# registry、非空语义字符串和 resolved/residual 一致性检查；分别记录 JSON syntax、schema、registry/semantic validity。

普通 JSON mode 不是替代品。将做不依赖研究结论的 schema 能力检查：相互冲突的合成输出指令、必填/额外键/枚举/边界/oneOf 负例、完整生产 schema。离线 validator 能拒绝负例只证明本地检查正确，不证明服务端约束。HTTP 200 或少量合法输出也不能独立证明 strict capability。

如 Responses 不支持完整合同，评估官方 [strict function calling](https://api-docs.deepseek.com/guides/tool_calls/)；只能以同一完整返回对象作为单一 response function 的 arguments，不把 Search/Find/Open 改为新的工具执行路径。任何 schema 等价编译必须证明接受集合不变，不能放宽一项约束来“通过”。若 strict 也不能可靠实现完整 schema，则输出 capability report，停止正式 Admission/G4/G5，禁止 prompt-only 降级或换模型。

## 5. 不变变量

| 项目 | 保持方式 |
|---|---|
| v1/v2 artifacts | 只读；基线 tracked 文件逐一 hash，结束时复核 |
| 模型及凭据来源 | 复用 provider 配置，仅公开非密钥元数据 |
| 重试、并发、timeout | `max_retries=0`，最多四并发，240 秒；认证失败复用既有短路 |
| 原始问题 / Claims / Hypothesis schema | 不新增 semantic fields，不改 candidate schema |
| Writer 数量上限 | 每 Observation 最多两条 Claim |
| Actor / Goal Reviewer 语义 prompt | 与 v2 字节相同 |
| Search/Find/Open / Retriever / localizer | 原 schema、实现、索引和恢复逻辑不变 |
| G4 cohort | 原 20 transitions、pre-state 和真实观察窗口 |
| G5 cohort / budget | 原 10 qids、三个 arm、最多三 Actor decisions、每次两独立动作 |
| L2 scheduling | 沿用 v2 batch boundary 和最终 Review；不改 per-window |
| truth / closure / Progress rubric | 沿用冻结主判据、strict/source-visible sensitivities 和 source pool |
| 输出处置 | 不 repair、normalize、retry、best-of、删除失败或补齐返回对象 |

## 6. Structured preflight 与 canary

在研究阶段之前冻结 **24 个历史请求**：12 Actor、8 Updater、4 Goal Reviewer。按历史输出形态分层机械抽取，覆盖 STOP/Search/Find/Open/双动作、keep/set/clear、resolved/unresolved；历史 category 只是覆盖依据，不强制新输出重复旧语义选择。记录 qid cluster、原请求/输出 hashes、语义 prompt identity、schema hash、转换后的确切请求和 API surface。

离线先验证原 schema 正反例、运行时 registry 单独拒绝未知 D/W、原文保留、凭据不进入留档、零重试与失败保留。服务端 capability probes 独立于这 24 个历史请求，使用新的冻结 diagnostic IDs，不伪装成历史样本。

结构 invalid 目标为零；incomplete/API/registry failures 单独报告，不从分母剔除。小 preflight 的零错误不等于普遍 100% 保证。若 API surface 引起明显异常语义变化，先运行冻结的小 paired Uc canary，不直接展开 rollout。

## 7. Admission Bank：先选样、标注、冻结，再调用

计划从 v2 G5 的 372 个 Updater events 建立 **60 个 packet**，每 qid 六个，保留真实 pre-state、Observation、Actor Gap 与 source provenance。机械排序采用固定 hash；同一 qid 内优先覆盖既有标注的 missed useful fact、qualifier omission、material contradiction/rejection、weak/overpromotion trap、incidental、多事实页面、有效 admission 和 empty/no-change。优先标签允许重叠；先选覆盖，再用确定性排序补足。若某 qid 不足六个可用真实窗口，不造例、不复制，记录实际数量及缺口。

新模型调用前，逐包冻结应保留的 decision-relevant fact atoms、必要限定、允许的 Hypothesis 操作及理由。Reviewer 只看该 packet 的 Q/Gap/pre-state/current Observation；不使用未来 trajectory 或 gold answer。历史 U0 的失败仍保留，unknown 不自动当错或对。这样 recall 分母来自观察中应承认的事实，而不是 U1 恰好输出的事实。

- U0：归档 v2 输出，零重请求。
- U1：同一历史 pre-state/Observation 加真实 Current Gap 与 admission 指令，constrained output；最多 60 新调用。
- Uc：从同 bank 机械选取最多 12 个 packet，旧 v2 prompt + constrained output，用于 API-surface attribution；不扩展为整 bank 第三 arm。

主要比较 U1–U0，Uc 提供小型拆分证据，不把联合修复效果全部归因于 Gap。按 qid 报告 paired 差值、方向一致性与未知/失败，而不把多窗口当独立问题。precision 的分母是 admitted claims；recall 的分母是预先标定的 useful atoms。Claim 或恰当 Hypothesis 更新承认同一 atom 只计一次。

## 8. Admission gate 与后续因果比较

通过要求 paired incidental 下降、来源支持无恶化、useful recall 无实质下降、限定丢失不增加、Hypothesis control 不恶化。冻结逐项判定方式和实例级原因，不用结果后新造的单一绝对阈值。存在不确定或权衡时明确给出 gate 的理由，不能仅凭精度提升自动通过。失败则停止 B/C，保留全部数据。

Stage B：20 个相同历史观察 transition，由统一 U1 生成 cleaner online state；比较 R0 prior Gap、R1 State-only、R2 原 oracle+Residual、R3 cleaner online+Residual。所有输出 constrained。R2 与其它 arm 的状态不同；R3–R2 差距缩小不能单独归因于 Residual。v2→v3 联合改变 admission 和 API surface，Uc 只提供有限拆分。用真实源判断 online closure，不复制 oracle label。

Stage C：B 没有严重完整性/语义问题才执行原十 qids。L0/L1/L2 使用同一 Writer，唯一控制差异保持 v2 定义。每轮评估 relevant/incidental state growth、Useful Observation→admitted fact→next decision、source-visible/claim-visible closure、候选修正、重复方向和原问题解决率。相同 wording/工具数不是 Progress，重写 query 仍可能返回已知文档。

## 9. 预注册解释边界

- Cleaner State 改善但 controller 相当：优先简单 L1，Residual 作诊断/停止 comparator。
- L2 仅减少 premature STOP：解释为 closure 辅助，不宣称 acquisition 胜出。
- 只有 L1≈L2>L0 才支持有害 persistent focus；L0 相当或更好则放弃其本身有害的强假设。
- 三组相对 v2 都改善：首先归于共同 admission/interface 修复，不宣布一个 controller 胜出。
- 修复后仍低 Resolution：依据真实 failure 转向 candidate control/source selection/search policy；不增加 State 字段救当前实验。

本轮明确授权实现与真实调用，因此不需要额外用户签字。所有调用前提交冻结；看到结果后不在同一 freeze 修改 prompt。每阶段失败、成本、cache hit/miss 和未知均留档。若服务端 exact schema 不可用，未执行的研究问题必须答“未测量”，不能借历史结果填充 v3 结论。
