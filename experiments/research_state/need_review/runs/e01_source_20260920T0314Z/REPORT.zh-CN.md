# E0.1：来源归属 C0/C1 配对实验

本批已完成：3 个固定检查点 × 2 个合同 × 2 次重复，12 个分支、24 次真实模型调用、24 个响应、零工具执行。**新增来源合同未改善本批 Reviewer 来源归属：C0 为 3/6，C1 为 1/6。** 完整响应可接受 C0 0/6、C1 1/6，但 C1 唯一可接受动作来自无效审查后的原请求回退，不能归功于有效来源审查。未进入 E1。

这是三个已知开发病例上的单一 Codex 辅助定性标签，不是独立人工金标、严格盲评、统计显著性结论或 BC+ 准确率。两个重复不是两道独立题。C1 是新增来源规则的整体提示词处理，不能把其全部效果归因某一句规则。

## Material Passport

- 模式：experiment-agent/run，附离线完整性复核与本批描述性语义分析。
- 基线：`6e6222c773cedb07da96cc8385a7a9b0bc91c168`；开始时工作区干净；实验代码、提示词、历史轨迹和默认工具未改。
- 历史源提交：`6d1be8d9b04972d8a55752449294abf12383f554`；固定 546/s29、776/s53、517/s21，旧 v000 协议。
- 模型及提供商：原 `qwen3.7-flash`、原阿里云北京兼容接口；完整无凭证地址在冻结计划。无模型覆盖，thinking=false。
- 真正执行时间：2026-09-20 03:13:49–03:16:56 UTC（北京时间 11:13:49–11:16:56），首末事件跨度 187.424 秒。目录名只是本批标识，以事件时间为准。
- 评价者：当前 Codex；已知历史 E0 和审计，未使用独立人类评阅者。没有读取标准答案、原轨迹未来内容或未见全文作本批语义证据。
- 原始材料：[manifest](manifest.json)、[机械汇总](summary.json)、[逐分支记录](BRANCH_ANALYSIS.md)、[语义汇总](semantic_summary.json)、[完整性复核](verification.json)。

## 1. 预检与重新冻结

先阅读 `AUDIT_809DFEB_FOLLOWUP.md`，再按本版 `CODEX_TASK.md` 阅读计划、审计、选择清单与提示词。135 项 `test_need_review*.py` 离线测试通过，日志保存在 [preflight/tests.log](preflight/tests.log)。prepare 从新目录提取三个完整前缀，逐源验证固定 Git blob；没有重新拼装或截断。

新计划 [approved_plan.json](preflight/approved_plan.json) 的 SHA256：

`0b4a5b353ace6fdd303264f714174b14d4e86e21ca161bc3720ce692c90849b1`

计划绑定本提交的实现哈希、提示词、前缀、模型、提供商、调度与参数；execute 使用 `--plan-file` 强制匹配。未复用旧 E0 计划或绕过哈希检查。

固定 `source_contract_pair`、`legacy_text`、每组两次、调度 seed20260919、Reviewer 上限512、SDK retries0；Actor 保留捕获参数，原请求没有显式输出 cap，未另加预算。seed只控制本地顺序，不是远端采样种子。C0 原 `need_review.txt`，C1 `need_review_source_grounded.txt`；schema仍为四字段。

首次调用前逐题比较：两组 Reviewer 的 user payload、完整 messages/references 和其余请求参数完全相同，只改 system 来源合同。实际执行后再次逐配对核验。后续 Actor 的备忘内容由 Reviewer 输出产生，是处理结果；前缀、备忘包装和其他 Actor 参数保持一致。

提供商兼容性依据是同端点、模型、捕获参数和相同完整前缀在历史 E0 中的30次成功响应；本次不额外试跑。它不是当日服务商 SLA 或模型版本不变的证明。本批实际24次请求均返回，12条Actor响应都兼容旧协议。

## 2. 机械结果、失败和成本

| 项目 | C0 baseline | C1 source_grounded_v1 | 合计 |
|---|---:|---:|---:|
| 计划/完成分支 | 6/6 | 6/6 | 12/12 |
| 实际逻辑调用/响应 | 12/12 | 12/12 | 24/24 |
| 有效Reviewer | 6 | 5 | 11 |
| 无效Reviewer/无备忘回退 | 0 | 1 | 1 |
| API错误 / harness错误 | 0 / 0 | 0 / 0 | 0 / 0 |
| Actor Search决策 | 3 | 6 | 9 |
| Actor最终文本答案 | 3 | 0 | 3 |
| 协议兼容Actor | 6 | 6 | 12 |
| 执行工具数 | 0 | 0 | 0 |
| reported prompt tokens | 338,423 | 339,615 | 678,038 |
| reported completion tokens | 6,738 | 5,392 | 12,130 |
| reported total tokens | 345,161 | 345,007 | 690,168 |
| Reviewer调用耗时合计（秒） | 29.163 | 31.601 | 60.764 |
| Actor调用耗时合计（秒） | 68.767 | 55.279 | 124.046 |

进程退出码 **2**，`mechanically_clean=false`；这是保留的一条模型节点无效输出，并非批次漏跑或日志损坏。C1/776/r1 引用了不存在的 `event:4:doc:34541`，真实可用的是 `event:16:doc:34541`。原始响应 `finish_reason=stop`，不是上批的512-token截断问题。没有修复引用、增加额度或重试。Actor请求逐字等于原捕获请求，`memo_injected=false`。

全部原始请求/响应及失败保留在 `branches/*/{events.jsonl,result.json}`。导出12张卡片，`cards_with_export_errors=0`；逐分支实际请求与事件复核、引用定位及源/提示词哈希校验通过。

成本边界：`cost_accounting_complete=true`；`failed_requests_with_unknown_cost=0`、`responses_missing_usage=0`、`responses_inconsistent_usage=0`；`missing_usage_fields_by_stage` 两阶段均空；24条usage的三个非负整数计数与总数恒等式均通过。未知成本字段没有被删除或用零成本补齐；本批这些异常的实际计数确实为0。690,168 是服务商报告tokens，不是货币费用；缓存/账单价格与实际计费额未核验，货币费用未知。

## 3. 标注顺序与规则

1. 在查看本批输出前，根据固定前缀写 [pre_output_baseline.json](preflight/pre_output_baseline.json)。导出后先读 `prefix_cards.jsonl`，逐卡保存 [prefix_assessment.jsonl](review/prefix_assessment.jsonl) 和时间/哈希凭据。
2. 只看 Reviewer 输出与可见来源，保存 [reviewer_first_pass.jsonl](review/reviewer_first_pass.jsonl)；当时尚未查看 Actor 输出。
3. 查看 Actor 全响应，包括正文与整个工具批次，保存 [annotations_first_pass.jsonl](review/annotations_first_pass.jsonl)，回归标签仍unknown。
4. 最后打开 private_key 映射；仅修改配对regression标签/说明，保留其余标签，另写 [annotations_final.jsonl](review/annotations_final.jsonl)。对应时间及SHA凭据均保留。没有以揭示组别后的判断覆盖首轮。

格式和历史内容可能暴露条件；本评阅者也已读历史报告，所以只称元数据遮蔽和顺序约束，不称严格盲评。标注脚本记录人工式判断，不是自动语义分类器，不得重跑脚本来伪造首评时间。

来源轴检查所有保留命题的来源、关系范围和限定，不仅看引用ID合法。C1/776/r1原始无效文本可做失败诊断，但不能算有效审查成功。`assumption_grounded=yes`只表示确实存在该历史搜索前提，不证明假设为真。需求与原题相关、尚未解决，也不代表其粒度或决策作用正确。

`action_responds_to_need=yes`采用较窄语义：所提查询回应需求主题。它不等于使用了合理纠偏理由，更不等于检索有进展。回退分支为not_applicable。重复查询、未证实硬过滤、无来源正文和提前终答仍使完整响应不通过；一个Query方向看似相关不能替正文免责。

## 4. 首先看 Reviewer 来源归属

| 评价 | C0（全分母6） | C1（全分母6） |
|---|---:|---:|
| 来源归属合格 | 3/6 | 1/6 |
| 有效审查子集中的来源合格 | 3/6 | 1/5 |
| 识别到确实未建立的搜索前提（原始文本诊断） | 6/6 | 6/6，含无效文本1条 |
| 决策作用平衡 | 2/6 | 0/6，另unknown1条 |

C0来源合格：776/r1、776/r2、546/r2。C1来源合格：776/r2。C0→C1在6个配对中，来源轴为1对yes→yes、2对yes→no（其中1对C1机械无效）、3对no→no，没有no→yes。这是本批标签计数，不是总体效应估计。

517四条审查均未通过：三个写了“visible evidence stating his father was a nurse and mother a health advisor”，但该命题只在历史assistant文本中出现；已见tool的护士信息涉及其他人物，Meirelles/Condon窗口不证明Idris家庭。另一个虽把宽松职业/角色解释叫作假设，仍在需求中把1975当已确定Goat出生年，并用两部影片的“or”替代原题同一演员关系。两组均未解决此来源污染。

546的C0/r1、C1/r1、C1/r2仍把Selby×Players绑定的不匹配推成排除Selby本人。原题没有给定赛事：否定某个假定关系并不否定所有可能赛事。C0/r2反而解除Players预绑定，只要求核对2023完整序列；来源轴合格，但“序列符合即可答案”的措辞仍需完整对手统计/as-of条件检验，不能当所有审查维度满分。

776两组r2都能识别职业过滤没有证据；需求仍宽。C1/r1另出现无效引用及允许1887“close but not1886”的条件放宽，说明新增规则没有保证约束保持。

## 5. 再看 Actor 与逐题逐重复结果

| 辅助/主指标 | C0 | C1 |
|---|---:|---:|
| 工具方向可接受（全分母） | 0/6（另3条无工具） | 1/6 |
| 工具方向可接受（仅工具决策） | 0/3 | 1/6 |
| 正文事实有据或明确作为未证假设 | 1/6 | 2/6 |
| 最终答案获可见证据支持 | 0/3 | 无最终答案，not_applicable |
| **完整响应可接受（主指标）** | **0/6** | **1/6** |
| 有效审查之后的完整响应可接受 | 0/6 | 0/5 |

C1少了本批C0的三次无支持最终作答，但这不等于提高正确率；C1仍有错误来源、重复检索及无据正文。唯一主指标通过来自回退，不能把它记为“合理gap被采用”。

| 题/重复 | C0 Reviewer → Actor | C1 Reviewer → Actor | 解释 |
|---|---|---|---|
| 517/r1 | 来源不合格；直接答Idris | 来源不合格；查David Thewlis父母 | C1正文自己称1963出生却原题1970s，Search不自动优于终答；配对regression unknown |
| 517/r2 | 来源不合格；直接答Idris | 来源不合格；查父soldier/母nurse/1975 | 保留错误1975和无据家庭/角色正文，无完整改善 |
| 546/r1 | 来源不合格；重复Selby×Players | 来源不合格；Players比分查询、正文补造对阵 | C1虽去候选名，仍锁赛事；相对C0短正文增加无据断言，regression=yes |
| 546/r2 | 来源合格；无观察补出全链并答Selby | 来源不合格；重复Selby×Players结果表 | C1避免终答，但来源轴变差且工具方向仍重复 |
| 776/r1 | 来源合格；精确重复职业查询并确定JAF | 审查无效未注入；改查1940 American Anthropologist报告 | C1动作可接受来自原Actor回退，不是审查传递成功 |
| 776/r2 | 来源合格；继续anthropologist biography | 来源合格；shaman+word近重复 | C1去职业过滤是局部变化，仍无实质新入口；正文出生断言无可见支持 |

全部12条四字段原文、实际下一动作、15轴标签、成本及未知关系见 [BRANCH_ANALYSIS.md](BRANCH_ANALYSIS.md)。没有挑任一次成功替代两次重复的总体分母。

## 6. 三个最有说明力的 bad case

### 517：来源规则存在，仍把assistant回忆当作tool证据

对照 [C0/r2](branches/qid_517_s21__C__r2__baseline/result.json) 与 [C1/r2](branches/qid_517_s21__C__r2__source_grounded_v1/result.json)。原题要求1970s/Goat、父亲soldier/母亲barracks hospital、2005警察角色、2013另一影片，必须绑定同一演员。

已见 `event:4:doc:46172` 只支持Meirelles受Iracema启发；`event:8:doc:82643` 和 `15723` 支持Condon局部作品/生平。父亲nurse/母亲health advisor只出现在assistant消息2、6、8，不是tool的Idris传记。C1 Reviewer仍称其为visible evidence，并把1975写进next_need。

Actor因此没有得到可靠的来源纠偏：C0/r2无工具终答Idris；C1/r2继续Search，却搜 `"father was a soldier" "mother" "nurse" actor born 1975`，并先认定Idris、补家庭与cast关系。仍未知的是准确出生/生肖、父母、角色及跨片交集；不能用电影导演局部证据补全人物链，也不能把unsupported直接当成我们已按gold判定答案姓名错误。

### 546：上游较合理不保证下游证据使用；新增合同也没有阻止关系作用域错误

重点 [C0/r2](branches/qid_546_s29__C__r2__baseline/result.json)。原题未指明赛事，要求decider后**两场**4–3、4–0，再输给>400 centuries者。`event:20:doc:55516`支持Selby转职业1999、>800 centuries、6 maxima等局部资料；`event:28:doc:84585`可见窗口是British Open决赛/半决赛，截到quarter-final标题，不能推断未见后文。

C0 Reviewer要求检查Selby的2023比赛序列，没有锁死Players。Actor却无新观察就以“Based on the detailed match history”起头，补出Players的Highfield→Milkins→O'Connor→Trump及比分后最终答Selby。原题序列形状保留了，证据链仍是补造：这比只看最终姓名更能定位Actor的证据使用失败。

同期C1/r2提出验证性Search、没有终答，但Reviewer仍写“Players不匹配就must reject”。另外C1/r1相对C0/r1短正文新增Liang/Brecel等无据断言。尚不能确定正确候选或赛事；现在既有上游来源/关系范围问题，也有下游越过需求补全问题，不能归为单一故障。

### 776：无效引用的代价与回退中的偶然好动作必须分开

重点 [C1/r1](branches/qid_776_s53__C__r1__source_grounded_v1/result.json)。原题1886出生、1915语言误用、35年同屋/3子女、1936–1940鼓励、1940官方报告题名。`event:16:doc:34541`局部支持American Anthropologist从1888起刊；`event:32:doc:25954`支持Benedict研究/任职及编辑JAF，但没有建立题目人物或报告，也不支持1887出生信息。

Reviewer引用不存在的event4/34541，被正确拒绝；它还提出1887“close but not1886”。Actor没有看到这条备忘，原请求回退后提出1940 American Anthropologist report的候选探索查询，相比此前泛journal入口更具体、正文不造事实，因而主指标通过。相对C0/r1重复旧职业查询确实有行为差异，但不能将该差异解释为新合同通过合理需求驱动Actor。

r2则是另一类链路：C0和C1都正确指出职业未证实，C0仍保留anthropologist过滤，C1仅回到近重复shaman+word。主题相关不等于纠偏完成。仍未知人物、作者及官方题名，没有执行工具取得新报告内容。

## 7. 下一轮只改一个节点：Reviewer读取输入的来源分层

**建议下一轮只比较 Reviewer 的来源分层视图，暂不改Actor交接或停止逻辑。** 理由是C1未先稳定改善来源归属，517直接复现assistant→evidence污染，546继续错误扩大关系作用域；目前不足以把首要问题归为“正确需求已经稳定产生、仅未传递”。

具体候选：在同一完整证据库存下，Reviewer user payload显式区分原题、原始tool观察、历史assistant假设/查询，并保留原message_index/path及逐字内容。不加入人工事实清单、gold、未见全文、额外字段或生成摘要；不删除任何原文。以本轮C1提示词作为两臂共同固定合同，仅改Reviewer输入的来源组织这一处，重新离线验证和冻结。

其余固定：同模型/thinking、三检查点、schema四字段、512 cap、retries0、legacy_text、Actor原历史与参数、同样24调用规模和全部失败分母。来源分层会改变位置/注意力与输入token，属于整个输入呈现处理，不可声称仅某个标签字符串的因果效应。

首先检验517家庭职业和1975是否仍被错误归属，再看546是否把赛事绑定失败推成整个人选淘汰；分别记录来源轴和decision_effect，防止只看引用格式。若Reviewer可靠后Actor仍越权补全，才另立一次只改Actor证据使用或交接的实验。当前不增State字段、不同时修引用/升额度、不要求无条件服从、不自动进入E1。本建议尚未实现或执行。

## 8. 交付与限制

原始机械summary保留 `semantic_evaluation=not_evaluated`，语义标签独立保存在semantic_summary及review文件中，不改原始事实。源快照、冻结计划、全部请求/响应、失败与成本、逐卡标签、分组映射、中文报告均在此新目录；历史E0未覆盖。

本批只能评价固定旧v000前缀后的**下一决策**。没有新检索结果，没有BC+准确率、命中率、持续状态收益或当前Search/Open端到端效果。没有模型能力上限结论。抽样小、开发病例选择、单模型别名可能漂移、单一辅助评阅与提示词长度变化均限制外推。

复核执行方式见 [commands.txt](preflight/commands.txt) 和 [analysis/README.md](analysis/README.md)。本批原始失败没有重采样，也没有执行下一轮或E1。
