# E0：一次审查没有稳定修复下一动作，证据读取与传递各有失效

## 执行结论

本批按冻结计划完整执行 **3 题 × 3 组 × 2 次 = 18 个分支，18 次 Actor + 12 次 Reviewer = 30 次逻辑模型调用**，收到 30 次响应。没有额外试跑、SDK 重试、人工在线修复或补成功样本。**工具执行数为 0**；没有加载检索模型，没有 E1、完整 rollout、持久 Research State 或停止器实验。

没有 API/Actor 请求错误；C 在 776/r1 的 Reviewer 达到 512-token 上限，JSON 截断，按规则回退到原 Actor。所有失败原文、请求、响应、校验结果、耗时与用量均保留。15 条 Actor 响应提出 search（各一条调用），3 条为最终人名答案；没有 get_document、SDK refusal 或语义弃答。18 条响应都兼容原运行时协议，没有 `tool_calls_with_stop`。

本轮不能支持 B 或 C 稳定优于 A。严格评价**整条下一响应**时，三组均没有通过的分支；这不等于所有 Query 都毫无价值：B 的 517/r1、C 的 517/r1 与 546/r1 有局部放宽绑定的查询方向，但同一响应仍包含无依据的确定性叙述。不能只取最后一条 Query，把正文问题藏掉。三条最终回答均缺少关键关系的已见支持，属于证据不足的提前作答，**并非以 gold 评分出的答案错误率**。

下一轮优先只改 **C Reviewer 的证据读取合同**，不增加字段或工具、不改 Actor/备忘注入/预算。原因是审查多次把历史 assistant 猜测写成已见事实；应先减少错误备忘，再判断下游不服从。本轮也有“审查指出合理限制、Actor 仍忽略”的清晰病例，保留为后续传递合同诊断，不同时修改。

## Material Passport

- 阶段：已完成 E0 固定前缀实验与 Codex 定性分析；没有独立人类复核。
- 材料：固定检查点消息、实际 30 次请求响应、匿名卡片、初评与揭示分组后的标注。
- 范围：三个已分析开发病例、每组两次；不作 BC+ 总体准确率或统计显著性结论。
- 禁止混入材料：gold、检查点之后事件、未见全文、额外工具结果。语义评阅未使用这些材料。
- ARS 使用：academic-research-suite 的执行监控与留痕原则；用户提供的 CODEX_TASK/EXPERIMENT_PLAN 为实验权威，用户已授权真实调用，无重复批准环节。

## 版本、配置与离线冻结

| 项目 | 本批值 |
|---|---|
| 运行 ID | `e0_20260919T171923Z`（UTC） |
| 代码/实验配置提交 | `0193fc072c31554284c9459bac62f436e9f7ba64` |
| 原始轨迹固定提交 | `6d1be8d9b04972d8a55752449294abf12383f554` |
| 检查点 | 546 seq29；776 seq53；517 seq21 |
| 模型 | 全部 `qwen3.7-flash`；无 `--model` 覆盖 |
| 工具语义 | 捕获的 `v000_baseline`，search/get_document；不替换为当前 Search/Open |
| 重复/调度 seed | 2 / 20260919（仅调度，不是服务采样 seed） |
| Reviewer 输出上限 | 512 tokens，B/C 相同 |
| Actor 参数 | 与捕获请求相同；没有新增 max_tokens/temperature/seed |
| 思考/流式 | 捕获的 `enable_thinking=false`、`stream=false` |
| SDK 重试 | 0 |
| 执行墙钟时间 | 218.78 秒（实际调用耗时合计 217.83 秒） |

首个真实调用前完成 62 项 `test_need_review*.py` 测试，全部通过，未修实验实现、提示词或检查点。三个源文件 Git blob SHA 全部匹配；检查点与提示词 SHA-256 见 [freeze.json](preflight/freeze.json)、[manifest.json](manifest.json) 和 [prepare.log](preflight/prepare.log)。A 的完整请求精确等于检查点；B/C Reviewer 输入仅为 messages/references 且相同；实际所有 Actor 前缀精确一致、非 messages 参数无变化。完整机械复核见 [integrity_and_cost.json](integrity_and_cost.json)。

任务开始时 `git status --short` 为空。预检 `initial_worktree_status.txt` 中只有刚创建的本批 `initial_git_head.txt`，不是既有用户改动。未读取/打印 `.env` 内容、API key 或认证头；execute 经既有 Config.load 加载凭证。前轮创建的本地 BCPlus 资源没有进入实验模型请求或本次提交。

原模型已在此前用户授权的链路测试中可用，本批没有再做挑选模型的试跑。官方[模型能力页](https://help.aliyun.com/zh/model-studio/qwen3-7-flash)预检给出 1M 上下文和 Function Calling；本批实际最大 prompt 为 **40,606 tokens**，完整前缀均被服务接受。`compatibility.md` 的“约140 KB”是粗略量级，精确最大 Reviewer JSON 为 147,075 UTF-8 bytes，见 input_audit。服务端模型别名没有固定权重快照；不能声称远端采样可完全复现。

## 成本与失败：先给完整分母

| 组 | 分支 | Actor / Reviewer 调用 | API / Actor 错误 | 审查无效/回退 | Actor 输入/输出 tokens | Reviewer 输入/输出 tokens | 总 tokens | 调用秒数合计 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 6 | 6 / 0 | 0 / 0 | 不适用 | 158,246 / 2,597 | 0 / 0 | 160,843 | 27.72 |
| B | 6 | 6 / 6 | 0 / 0 | 0 / 0 | 160,764 / 7,336 | 176,768 / 2,298 | 347,166 | 99.16 |
| C | 6 | 6 / 6 | 0 / 0 | 1 / 1 | 159,894 / 7,317 | 178,382 / 1,958 | 347,551 | 90.95 |

总计 **855,560 tokens**（834,054 输入、21,506 输出）；所有响应都有 usage，无缺失用量。这里报告服务端 tokens 与调用耗时，**不是实际账单金额**；缓存、账户折扣及计价应以账单为准。B/C 相比 A 不仅多一次审查，也出现更长 Actor 输出，不能把差异只归因于 gap 内容。

| 组 | 整条响应可接受 | 仅 Query 方向局部正向* | 最终回答/缺关键证据 | 语义弃答 | 协议不兼容 | 相对匹配 A 明确退化 / 不确定 |
|---|---:|---:|---:|---:|---:|---:|
| A | 0/6 | 0/6 | 0/6 | 0/6 | 0/6 | 不适用 |
| B | 0/6 | 1/6 | 1/6 | 0/6 | 0/6 | 2/6 / 3/6 |
| C | 0/6 | 2/6 | 2/6 | 0/6 | 0/6 | 2/6 / 2/6 |

*补充描述轴，不替代主评价，也不是检索命中率。没有工具执行，不能知道这些查询实际能否取到新证据。三组全为 0 的整体口径包含：重复已失败查询、未撤销错误硬过滤、无依据确定性正文、提前提交。详见每卡依据，而非机械指标代替语义。

## 逐题、逐重复

详细 11 维标签、实际引用、审查语义及 517 检查见 [BRANCH_ANALYSIS.md](BRANCH_ANALYSIS.md)。以下每行包括全部响应中的调用；本批每个工具响应恰有一次 search，并未挑选其中某个调用。

| 题/重复 | A | B | C |
|---|---|---|---|
| 546/r1 | card0005：Selby + Players + 新造 Highfield/Lisowski，仍锁赛事 | card0003：Trump lost to Allen + Players，无来源换关系 | card0007：最终回到 4–3/4–0 + 2023 泛赛事查询，局部改善；正文自造赛程并转 Bingham |
| 546/r2 | card0011：try Trump + Players；候选换了，赛事没松开 | card0018：未新查证，最终给 Trump，对手链含占位/猜测 | card0012：未新查证，最终从 Selby 转 Bingham；三胜变两胜 |
| 776/r1 | card0016：shaman + 1915 + trip，近重复 | card0008：误称期刊/作者已确定，再搜同屋35年 + anthropologist + biography | card0013：Reviewer length/JSON 无效回退；Actor 完全重复旧 same house 35 years born1886 |
| 776/r2 | card0009：born1886 + three children + anthropologist，仍职业锁定 | card0004：Reviewer 明确职业假设无支持；Actor 仍完全重复 shaman1915anthropologist | card0001：Reviewer 识别职业假设；Actor 继续枚举旧人类学家，仅改 shaman+word |
| 517/r1 | card0006：仍固定 born1975 + father soldier + mother nurse | card0015：最后回到 soldier/barracks hospital，局部改善；正文仍认定 Idris 并补角色 | card0002：最后去掉1975搜军人父母/Goat，局部改善；未处理提出的电影关系且放宽 policeman |
| 517/r2 | card0010：与 A/r1 完全同一 Query，1975 未解除 | card0014：回到 Idris 2013 thriller，省去 Condon 限制并强化候选 | card0017：无新证据直接最终 Idris；承认不符仍替题目找解释 |

### 546：人物统计不等于赛事路径

m11 /0、`event:20:doc:55516` 只给 Selby 的 1999 转职业和生涯概况，没有题目四场序列。m7 /3、`event:12:doc:84585` 是 British Open 的有限入口，且其中 4–3 是比赛进程，不能自动转成题设某一场终场比分。B/C 都知道具体比赛没证实，但 C 两次把“Selby 在 Players 不匹配”升级成“Selby 应淘汰”，遗漏“赛事绑定错、人物仍可能”的解释。

C/r1 的末尾查询是正向反例：人物/赛事绑定确有松动；但正文把 Selby、Bingham 与一连串对手关系说成记录，未经工具证实，不能给整条通过。r2 的 B/C 都从审查“尚待验证”直接跳到答案。不存在审查后新的工具观察来支撑这个跳跃。

### 776：有合理提醒，也可能没有合理动作

整个前缀没有确定 A、B 或报告。`event:16:doc:34541`/m9 /1 只支持 American Anthropologist 创办于1888；这不够确认为目标季刊，更不确定作者的职业。

B/r1 却写 journal established、author identified，并在动作中继续 anthropologist。B/r2 更有区分力：它正确指出职业假设无支持，Actor 却把前缀 m18 的 Query 原样重复。C/r2 也指出职业假设，但泛化成“找出这个人及全部传记条件”，没有给出足以脱离旧路径的信息分岔。不能把字符串不含 anthropologist 的 C/r2 查询直接视为真正摆脱职业路径：其前导文字仍枚举同一批旧人物，Query 与历史萨满短语近重复。

C/r1 是机械失败：Reviewer `finish_reason=length`、输出512 tokens，原文在 basis_refs 长列表尾部截断。校验错误包括未正常 stop 与非完整 JSON；Actor 输入精确回退原请求。该 Actor 重复旧查询不能计作“服从了审查”，也不删除此分支后报告 C 的有效样本成绩。完整记录见该分支 events seq1–5 与 result.json。

### 517：本批基线并没有稳定纠偏

两个 A 的最后 Query 完全相同，均保留未被原文支持的 1975 过滤。历史选点“之后能解除绑定”是选点背景，**不是本批 A 已实现的结果**。因此不能声称 C 破坏了本批一个已成功的 A；可以说 C/r2 相对仍在搜索的 A/r2 出现证据不足的最终提交。

已见工具文本证实的只是 Meirelles 的 Iracema 启蒙（m3 /0）与 Condon 的 Kinsey/The Fifth Estate 关系（m5 /0、m5 /3）。它们没有支撑 Idris 的生年、父母、角色或演员名单交集。B/C 多次把 assistant 记忆写为 sources cite、sources vary、main cast lists reviewed，这就是证据来源混淆。最后搜军营医院的 B/r1 值得保留为局部正向，但不能掩盖前导正文的确定性认定。

## 最有说明力的三个 bad case

### 1. 776/B/r2：正确识别职业假设，Actor 原样重跑旧 Query

- 分支：`branches/qid_776_s53__B__r2/`，card0004。
- Reviewer（events seq2）明确说职业假设不被可见观察支持；期刊仍是候选。
- Actor（events seq5）却调用 `"mistaken for a shaman" 1915 anthropologist`，与可见前缀 m18 相同。
- 这不是引用失效或 API 失败，也不是 tool_calls/stop 混淆。它说明合理提醒未落实为下一动作，存在备忘到 Actor 的传递问题。
- 限制：B 的提醒较泛，未给单个有区分力的信息问题；不能由此证明只改包装就能解决。

### 2. 546/C/r2：单一赛事假设变成人物淘汰规则，最后凭空提交

- 分支：`branches/qid_546_s29__C__r2/`，card0012。
- Reviewer（seq2）用 `event:20:doc:55516` 支持检查 Selby 在 Players 的记录，并规定不符即拒绝该候选。该来源只有生涯资料。
- Actor（seq5）不调用工具，先说 Selby，后编写 Bingham 两胜一负并最终回答 Bingham；没有覆盖题目的三次胜利。
- 失效跨两处：审查错误绑定了人物与赛事，Actor 又把未决需求变成答案叙述。不能把改人名当纠偏。
- 限制：没有执行工具或 gold 评分；结论是当前证据链不足，不借真正赛果反推唯一正确 Query。

### 3. 517/C/r2：审查允许放宽角色，Actor 用猜测解释不匹配后提交

- 分支：`branches/qid_517_s21__C__r2/`，card0017。
- Reviewer（seq2）允许 policeman 被解释为 loose role，列举的引用只涉及两位导演，不提供 Idris 家庭/角色证据。
- Actor（seq5）承认没有已支持的2013出演关系，仍给最终 Idris；新造家庭军事背景和其他角色来填空，没有引用完整证据链。
- 这不是 null need 导致的程序停止：Reviewer next_need 非 null，Actor 工具仍可用，却自行结束。也不是拒答。
- 限制：匹配 A/r2 也保留1975误绑定，所以只能确认“由搜索变为无支持提交”的退化，不能说它从本批稳定正确轨道被拉坏。

## 下一轮：只改 C Reviewer 的证据读取合同

建议另立 E0.1，**仅修改 `prompts/need_review.txt` 的来源归属规则**，保留现有四字段 schema、输入、512-token 上限、B 提示词、Actor、memo、注入位置、模型和调度。此建议未在本批应用，也未启动下一轮。

具体单点改动：在审查把某项关系写为 established/confirmed/source says 之前，必须在当前可见 question/tool 文本中找到对应的最小支持；若只在历史 assistant 中出现，只能在现有字段内写为“assistant 假设，原题/已见观察尚未支持”，不能改写成 sources vary 或 confirmed。`basis_refs` 必须对应实际支持的那部分断言，不把“引用某篇人物页”当作授权其未见全文。没有必要新加字段或读取全文，也不注入本批人名/赛事的答案提示。

这一修改针对的是审查节点读取来源，而不是同时修改 next_need 定义、Actor 服从要求或停止机制。评估时先看备忘是否仍把出生年、亲属职业、演员交集、目标期刊当已知，再看 Actor 行为；保留 A/B 与全部失败分母。C/r1 的截断另作为可靠性观察，不在这轮同时改 token 上限或做 JSON 修复。

为什么暂不选传递合同：776/B/r2 是真实的下游失效，但 546/517 与 776/B/r1 已表明上游备忘本身常带污染。直接强化 Actor 服从可能放大错误；先验证证据读取合同能否产出可信需求，再用固定的合理需求做另标传递诊断。若以后 B/C 改善相近，优先选择简单 B；本轮不据三条局部 Query 宣称结构化 gap 必需。

为什么不做 E1：尚未稳定得到“需求有据且整条下一动作合理”的组合；本轮没有实际新观察，无法推断检索或答案收益。停止充分性也未被这三题验证，应另选当前协议的合适检查点。

## 评阅与复核边界

[pre_output_assessment.md](preflight/pre_output_assessment.md) 在首次真实调用前写下允许动作。先读 cards/rubric 并完成 [annotations_first_pass.jsonl](review/annotations_first_pass.jsonl)，保存 [first_pass_attestation.json](review/first_pass_attestation.json)，然后才读取 private_key。最后只补 regression 和分组/成本，保留初评不改；见 [annotations_final.jsonl](review/annotations_final.jsonl) 与 [unmask_attestation.json](review/unmask_attestation.json)。

这只是组名等元数据遮蔽：评阅者知道选点机制、实验设计和调用计划，JSON/自由文本/无审查本身也会暴露组别，不宣称严格盲评。语义标签由当前 Codex 单评阅者给出，没有额外远端 Reviewer 调用或独立人类复核。引用存在由入口检查；语义支持逐卡看已见文本，不能由引用存在自动判真。

开发题选择与两次重复高度相关；不计算显著性、不报告 BC+ 准确率提升、不单字段归因、不以更多 tokens 代表更深研究。A/B/C 的温度、seed 未额外设置；调度 seed 不控制服务端随机性。全部分支及无效审查均留在分母。报告中的 new_errors 特指相对前缀新出现的无依据断言；旧错误即使很严重，也不重复计为新增。

## 文件导航与提交边界

- `manifest.json`：冻结计划、版本、请求/提示词哈希、传输配置（不含认证信息）。
- `checkpoints/`、`prompts/`、`source/`：本批使用的精确输入与源代码快照。
- `branches/*/events.jsonl`、`result.json`：完整实际请求、响应、机械验证、usage、耗时。
- `summary.json`：原入口的机械汇总，`semantic_evaluation=not_evaluated` 保持原样；语义评价在另存的 `semantic_summary.json`，不篡改机器记录。
- `preflight/`：离线测试、源哈希、预输出基线、冻结配置和执行日志。
- `review/`：18 卡原件、rubric、映射、初评及最终评价。
- `BRANCH_ANALYSIS.md`：18 分支逐项依据、成本、失败和回退。
- `integrity_and_cost.json`、`verification.json`：机械完整性和提交前复核。

只形成本地可复核提交，未授权推送，因此不推送。实验源码、默认 Search/Open、Query 初始化和 Actor 提示词均未改动。
