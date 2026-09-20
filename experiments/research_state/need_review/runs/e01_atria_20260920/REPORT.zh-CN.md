# Atria 重跑 C0/C1：下一动作有所改善，但512-token审查预算失配

**已完整重跑上一批：12个分支、24次真实模型调用、24个响应，零工具执行，未进入E1。** 模型替换为 `Atria-Dawn-Preview`，保持原三题、两组、两次重复和Reviewer512-token上限。

最重要的结果分为两层：

- **Reviewer：12/12都在推理阶段耗尽512 tokens，没有输出正文或可用JSON，全部按规则无备忘回退。** 因此来源归属正确率没有可评价分母，不能写成“来源判断0分”，也无法评价C0/C1的语义干预效果。
- **Actor：12次都是工具决策，11次Search、1次get_document，没有直接终答。** 单一Codex辅助评阅下，完整响应可接受7/12，上一批Qwen为1/12。两批实际备忘注入与推理计算不同，这只是本批行为更好的描述性信号，不是严格的模型能力排名或BC+正确率。

原始失败、推理内容、请求/响应、未知成本字段和所有标签均完整保留。没有从reasoning字段拼出审查JSON，没有改额度或重采样。

## Material Passport

- 执行基线：`6319c64cbff6995a879ed4fb8ceca095ec8d1b2a`，启动时工作区干净。
- 原历史源：`6d1be8d9b04972d8a55752449294abf12383f554`；546/s29、776/s53、517/s21，完整旧v000前缀。
- 提供商：`https://api.atria-asi.ai/v1`；Chat Completions；模型 `Atria-Dawn-Preview`，同时覆盖Reviewer和Actor。
- 真实执行：2026-09-20 05:44:47–05:53:18 UTC，北京时间13:44:47–13:53:18；首末事件跨度510.561秒。
- 对照批次：[上一批Qwen报告](../e01_source_20260920T0314Z/REPORT.zh-CN.md)。其原标签保留在 [prior_qwen_labels.json](preflight/prior_qwen_labels.json)，未重标或修改。
- 评阅：当前Codex辅助，已知历史输出、病例用途及稳定卡片顺序，不称独立人工金标或盲评；未以标准答案、未来观察或未见全文作为本批支持证据。
- 交付：[冻结计划](preflight/approved_plan.json)、[机械汇总](summary.json)、[逐分支分析](BRANCH_ANALYSIS.md)、[语义汇总](semantic_summary.json)、[完整性复核](verification.json)、[推理额度诊断](reasoning_diagnostics.json)。

## 1. 预检与冻结

135项 `test_need_review*.py` 离线测试通过。重新prepare到新目录，验证源日志blob、完整工具配对和引用；三个checkpoint与上一批逐字相同。实验实现、schema、提示词、legacy备忘及Actor原始历史未修改。

新计划 SHA256：

`6084415fdd2879dd53561bdd0896502ec2b99d1cb469461a8998fabbf376715a`

固定 `--comparison source_contract_pair --memo-mode legacy_text --repeats 2 --seed 20260919 --review-max-tokens 512 --sdk-max-retries 0`；唯一请求配置替换是模型名与端点。C0/C1 Reviewer仍只在system提示词上不同，user payload和其余参数相同。Actor保持捕获参数；原始请求没有显式输出cap，未为本轮另加。

完整提供商兼容性依靠前一任务的最小请求/工具往返记录和正式批次验证，没有增加本批smoke调用。官方接口文档标注256K上下文，支持Chat Completions及max_tokens；本批实际接受全部完整前缀。[Atria接口文档](https://api.atria-asi.ai/docs)

历史 `extra_body={"enable_thinking":false}` 原样保留。首次调用前已声明Atria对该扩展参数的支持/效果未知，不能据参数名字声称等计算或关闭了推理。实际响应显示推理没有被关闭。本轮没有擅自换成另一推理参数或在看到失败后加大预算。

现有Agent的 `OPENAI_ALLOW_TOOL_CALLS_WITH_STOP` 是独立运行时兼容开关，不改变本E0 runner。后者继续保存原始finish_reason并按旧协议分类；本批12条Actor均实际返回tool_calls，全部兼容，无需规范化。

## 2. 机械执行与成本

| 项目 | C0 baseline | C1 source_grounded_v1 | 总计 |
|---|---:|---:|---:|
| 分支完成/计划 | 6/6 | 6/6 | 12/12 |
| 逻辑调用/响应 | 12/12 | 12/12 | 24/24 |
| Reviewer有效 | 0 | 0 | 0 |
| Reviewer截断/回退 | 6 | 6 | 12 |
| API / harness错误 | 0 / 0 | 0 / 0 | 0 / 0 |
| Actor Search | 6 | 5 | 11 |
| Actor get_document | 0 | 1 | 1 |
| Actor最终答案 | 0 | 0 | 0 |
| 实际工具执行 | 0 | 0 | 0 |
| reported prompt tokens | 308,938 | 310,348 | 619,286 |
| reported completion tokens | 5,496 | 7,138 | 12,634 |
| reported total tokens | 314,434 | 317,486 | 631,920 |
| Reviewer耗时合计（秒） | 109.650 | 135.009 | 244.659 |
| Actor耗时合计（秒） | 80.428 | 183.011 | 263.439 |

Reviewer阶段：331,634 input +6,144 completion =337,778 tokens；全部6,144 completion被服务商标为reasoning。Actor阶段：287,652 input +6,490 completion =294,142 tokens，其中服务商报告reasoning6,141。直接记录供应商计数，不推断其对工具参数tokens的内部归类。

每条Reviewer的 `finish_reason=length`、`content=null`、`completion_tokens=reasoning_tokens=512`。校验错误都是“review must finish with stop”及“review must contain nonempty text”。退出码2，`mechanically_clean=false`；这是12条真实节点失败，不是遗漏调用或本地harness崩溃。

`cost_accounting_complete=true`；未知成本请求0，usage缺失0、不一致0，缺失字段映射为空，日志错误0。所有token恒等式成立。未知成本字段仍保留，未用0费用填补失败；本批失败是有完整usage的模型输出失败。货币费用未核验，仍未知。

631,920与上一批690,168只是各提供商的reported tokens；tokenizer、服务默认推理、缓存和Actor输出形式不同，不据此声称效率提高。Actor原无显式cap，服务端默认输出预算也不能视为跨模型等同。

## 3. 先评 Reviewer：输出合同没有成立

这次没有完整的四字段审查可供来源判断。所有Reviewer来源、假设、需求、决策作用标签为not_applicable；**可交付的有效审查为0/12，来源正确率为null而非0/12。** 既保留失败分母，也不把缺失输出伪装成来源推理错误。

12条reasoning内容和usage保留在原始response中，但未被harness验证或注入Actor。它们不能事后替代缺失的正式JSON。没有“合理需求未被Actor采纳”的证据，因为所有 `memo_injected=false`，需求响应标签全为not_applicable。

六对C0/C1的实际Actor请求已逐对象比较，完全相同：同一原前缀，仅模型名覆盖Atria。所谓C0和C1仍标识先前Reviewer调用的条件，但它们的输出没有形成Actor可见的差异。因此不能把C1动作计数高于C0解释为来源提示词收益。

## 4. 再评 Actor：表现更谨慎，但仍有路线问题

| 评价（每组全分母6） | C0 | C1 |
|---|---:|---:|
| 工具方向可接受 | 2/6 | 5/6 |
| **完整响应可接受** | **2/6** | **5/6** |
| 无支持的直接终答 | 0 | 0 |
| 非空正文仅说明行动意图 | 1 | 3 |
| 无正文，直接提出工具 | 5 | 3 |
| Reviewer需求实际注入 | 0 | 0 |

“完整响应”仍按原口径检查交付的assistant content和所有工具调用；未删除正文再打分。8条没有正文，正文支持轴为not_applicable；4条正文只是搜索/读取意图，没有无据事实断言。原始reasoning不作为缺失Reviewer的替代，也不把它和已交付正文混成同一指标；这限制了与上一批长正文的比较。无直接终答也不意味着之后必然答对或停得恰当。

| 题/重复 | C0下一动作 | C1下一动作 | 完整响应 C0/C1 |
|---|---|---|---|
| 517/r1 | 查barrack's hospital / actor mother | 相同稀有短语查询 | yes / yes |
| 517/r2 | 查mother worked at barracks hospital / actor | 查2005 Constant Gardener的policeman演员 | yes / yes |
| 546/r1 | Players bracket，加入多名候选 | Players draw，加入多名候选 | no / no |
| 546/r2 | 改查Neil Robertson，仍锁Players | get_document(55516, offset0, max_chars12000) | no / yes |
| 776/r1 | born1886 / three children / anthropologist | 1940 JAF report入口 | no / yes |
| 776/r2 | shaman1915 / anthropologist / misuse | 35years / three children / born1886 | no / yes |

517四条都移除了错误1975硬过滤，也没有把policeman解释为security后强行作答。这是最稳定的局部改进。546仍有三条固守Players，只换名字不修订赛事绑定；776两条仍带未证实职业过滤。

776/C1/r2是较弱的通过：它将已分别尝试过的生平线索作更具体的联合，没有职业过滤，因此本评阅者接受为一次细化尝试；这不保证新增召回。若另一评阅者把它判为近重复，总通过会是6/12而非7/12，主要限制与结论不变。首轮原标签不因此覆盖，也不利用“任一次成功”替代分母。

## 5. 与上一批Qwen的有限对照

| 全部12分支 | 上一批Qwen3.7-flash | 本批Atria |
|---|---:|---:|
| 有效Reviewer / 实际备忘注入 | 11 / 11 | 0 / 0 |
| 完整响应可接受 | 1/12 | 7/12 |
| 517可接受 | 0/4 | 4/4 |
| 546可接受 | 0/4 | 1/4 |
| 776可接受 | 1/4 | 2/4 |
| 无支持最终答案 | 3 | 0 |
| 实际工具执行 | 0 | 0 |

可支持的描述：**在当前配置、这三个已知前缀上，Atria交付的下一动作更少出现无依据终答，并在517上更愿意回到原题线索取证。** 不能推出“来源审查更准”，也不能推出全面模型优势。

主要混杂是Atria全部走原Actor回退，Qwen11条带备忘；两模型实际推理设置/预算、分词器与服务默认参数也不同。只有776/C1/r1两批同为无备忘回退，该局部比较仍只有一次，且两者都可接受（Qwen查AA，Atria查JAF）。更严格的Actor模型能力对照应另行固定两模型都不加备忘、明确推理配置和计算预算；本轮未执行该额外实验。

## 6. 三条代表性失败链路

### 1）Reviewer预算截断：这是本批最大的接口失配

[776/C1/r1原始记录](branches/qid_776_s53__C__r1__source_grounded_v1/result.json)是首个病例，其他11条相同机制。原题要求人物、1915语言误用、居住/子女、鼓励关系和1940官方报告。可见来源只有分散的期刊/人物资料，未建立完整链。

预期节点应交付未证实前提及一个信息需求；实际512tokens全部用于reasoning，`content=null`，没有next_need可注入。Actor精确回退后查询JAF/1940/report。查询合理与否独立评估；无论它后来是否能找到报告，都不能证明这条审查发挥了作用。未知的是在足够额度下Reviewer能否正确归属来源，而不是已经证明它必然误读。

### 2）546：换候选仍未修复未经证实的赛事绑定

[546/C0/r2](branches/qid_546_s29__C__r2__baseline/result.json)。原题未给赛事名，要求2023 decider、再两场4–3/4–0、然后输给>400 centuries者。`event:20:doc:55516`只提供Selby局部统计，`event:28:doc:84585`可见内容是British Open决赛/半决赛，不能支持Players完整路径。

没有有效Reviewer；Actor改查Neil Robertson，但仍把Players与4–3/4–0绑在一起。词面候选不同，没有解决“赛事绑定是否成立”。完整链仍未知，故方向不通过。与之对照，C1/r2开始读取已见Selby文档，可作为取证尝试通过；未执行读取，不能声称12000字符内真的有2023所需记录。

### 3）776：未证实的职业过滤仍在限定搜索

[776/C0/r2](branches/qid_776_s53__C__r2__baseline/result.json)。原题只给1886出生与旅行/家庭/报告关系，没有规定职业。`event:4:doc:53714`是Shamanism通用资料，`event:16:doc:34541`局部支持期刊起刊年份，均不能证明目标是anthropologist。

审查没有产出需求，Actor将shaman、1915、misuse、word、foreign language再组合，并保留anthropologist。历史第一条查询与后续职业查询已覆盖近似路线；缺少新的可区分入口。未知人物与官方题名不能靠职业假设补齐。同期C1/r2转向居住年数/子女/出生的联合查询是局部变化，但因为两者Actor输入相同，不能说是C1 Reviewer促成。

## 7. 下一轮建议：先只改 Reviewer 输出额度

要继续测试Atria的来源审查能力，首要问题已从“提示词是否更好”变为“它是否有机会输出正式审查”。**建议仅把Reviewer的输出上限从512提高到4096，两组同时提高；其他配置全部固定，再重新冻结一次C0/C1。** 这是预算适配实验，不是本批重试或补齐，不能与本批混算。

4096只是候选额度，不保证成功；届时仍保留reasoning和可用正文的成本，检查是否足以形成JSON。Actor预算、前缀、模型、来源提示词、legacy备忘、schema、重试数和工具版本不同时改变，也不在同轮增加来源分层/强制服从/停止器。先得到有效审查，才能评价来源规则、再判断是否需要来源分层。

没有自动执行该建议，没有E1、完整rollout、强制Open或State持久化。用户这次想测试模型能力，本批给出了Actor局部改善信号，也明确暴露了原512-token Reviewer设置不适合当前实际推理行为；未将它包装成完整能力评测。

## 8. 标注与复核记录

沿用上一批事前动作标准，首次调用前保存本批副本。导出后先读取prefix_cards，记录prefix_assessment，再检查Reviewer（全部无正文）并保存其标签，之后检查Actor content/工具并保存首轮标签，最后核对private_key，只有regression轴在配对后填写。模型推理原文始终保留在原始响应中，未拿来人工修补审查。

本评阅者已知历史内容和稳定卡片排序，因此步骤顺序不是盲评证明。所有标签完整保留在 `review/annotations_first_pass.jsonl` 与 `annotations_final.jsonl`，附时间和SHA。没有完整可评价审查的轴明确not_applicable，原始机械summary的semantic_evaluation保持not_evaluated，单独生成语义汇总。

[verification.json](verification.json)核验计划、源码/提示词哈希、实际请求和事件、原前缀/参数（仅model覆盖）、精确回退、成本与12张卡片；导出错误0。复核脚本还证明所有六对Actor请求相同及12条reasoning-only截断。模型、原始语料、密钥和环境文件不在提交范围。
