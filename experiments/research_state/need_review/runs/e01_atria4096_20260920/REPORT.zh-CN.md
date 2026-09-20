# Atria Reviewer 上限 512→4096：仅一条审查有效，尚未形成可评价的审查—动作链

**已按冻结计划执行全部12个分支、24次真实调用尝试：收到20个响应，4次API超时；11个分支完成，1个Actor失败。零工具执行，未进入E1。** 本批唯一配置改动是 Reviewer `max_tokens=512→4096`，没有修改 Actor、提示词、State、Search/Open或Query初始化。

- **先看Reviewer：** 有效审查从上一批0/12变为1/12；8条仍在reasoning阶段用满4096、正文为空，3条超时。唯一有效审查来源归属合理，但其Actor随后超时。来源语义判断是可评样本1/1，不是全批“100%准确”。
- **再看Actor：** 11个已返回响应均提出Search；完整响应可接受3/12，不可接受8/12，1/12未知。两条长正文含无可见支持的事实，不能只看最后query。两个通过项较弱，敏感性分析降级后为1/12。
- **归因限制：** 11条可观察Actor全部来自无备忘回退，实际请求与上一批逐对象相同。上一批7/12与本批3/12不能解释为增大Reviewer预算导致Actor变差，也不能据C1高于C0宣称来源合同有效。当前仍在验证审查节点的可靠交付，不具备进入完整rollout的证据。

## 1. 预检、冻结与材料范围

基线提交 `ce8bb3d6517309c55b890ecba0391e0baf6063fb`；启动前工作区干净。135项离线 `test_need_review*.py` 通过；重新prepare，校验源blob、完整历史及引用。冻结时间为2026-09-20 06:08:38 UTC，早于首次调用。

历史源提交仍为 `6d1be8d9b04972d8a55752449294abf12383f554`；检查点546/s29、776/s53、517/s21。完整前缀、调度、实现哈希和提示词与[上一批Atria512](../e01_atria_20260920/REPORT.zh-CN.md)一致。新计划SHA256：

`46e3b5b4a9c8596e35b78c20d3b778e8c12e54b607bb97ee197acba58d5b0c7c`

固定模型 `Atria-Dawn-Preview`、端点 `https://api.atria-asi.ai/v1`、Chat Completions、两次重复、调度seed20260919、C0/C1交错、legacy_text备忘、SDK重试0、客户端timeout120秒。Actor原请求没有显式输出上限，本批未新增。没有额外smoke请求或择优补采样。

用户本次明确授权提高上限，故偏离旧CODEX_TASK示例的512仅此一项，并重新冻结。保留历史 `extra_body={"enable_thinking":false}`；实际usage证明推理仍然发生，不能据该字段声称关闭推理。未更换接口、推理参数或提示词。

实际首末事件：2026-09-20 **06:08:55–06:27:41 UTC**（北京时间14:08:55–14:27:41），跨度1126.448秒。实验命令退出2；外层记录命令成功结束不等于模型批次机械无错。

材料入口：[冻结计划](preflight/approved_plan.json)、[离线日志](preflight/tests.log)、[执行命令](preflight/commands.txt)、[机械汇总](summary.json)、[配置对照](budget_comparison.json)、[完整性复核](verification.json)、[预算诊断](reasoning_diagnostics.json)、[逐分支分析](BRANCH_ANALYSIS.md)、[语义汇总](semantic_summary.json)。所有收到的原始请求/响应、事件和失败保留；超时后未收到的服务端文本及usage无法补造。

## 2. 全分母执行与成本

| 项目 | C0 baseline | C1 source_grounded_v1 | 全批 |
|---|---:|---:|---:|
| 计划/已尝试分支 | 6/6 | 6/6 | 12/12 |
| completed / actor_error | 6 / 0 | 5 / 1 | 11 / 1 |
| 调用尝试 / 收到响应 | 12 / 11 | 12 / 9 | 24 / 20 |
| Reviewer有效 | 0 | 1 | 1 |
| Reviewer截断、正文为空 | 5 | 3 | 8 |
| Reviewer API超时 | 1 | 2 | 3 |
| Actor API超时 | 0 | 1 | 1 |
| 无备忘回退 | 6 | 5 | 11 |
| Actor提出Search | 6 | 5 | 11 |
| 已观察的直接终答 | 0 | 0 | 0 |
| 未知成本请求 | 1 | 3 | 4 |
| 已报告prompt tokens下界 | 282,912 | 211,554 | 494,466 |
| 已报告completion tokens下界 | 26,163 | 18,909 | 45,072 |
| 已报告total tokens下界 | 309,075 | 230,463 | 539,538 |
| Reviewer耗时合计（秒） | 372.442 | 443.684 | 816.126 |
| Actor耗时合计（秒） | 111.364 | 196.549 | 307.913 |

Reviewer已报告229,306 input +35,118 completion =264,424 tokens，其中reasoning34,940；Actor已报告265,160 input +9,954 completion =275,114 tokens，其中reasoning4,990。这些均不含超时请求的未知消耗，**不是完整成本，也不是货币费用**。未核验账单，金额未知。不能将539,538小于上一批631,920解释为本轮更便宜。

四次超时均原样保留为 `APITimeoutError`：776/C1/r1 Reviewer、546/C0/r1 Reviewer、776/C1/r2 Reviewer、546/C1/r1 Actor。SDK无自动重试；没有人工重跑失败分支。

所有20个响应usage完整且加和一致；`responses_missing_usage=0`、`responses_inconsistent_usage=0`，不意味着超时请求成本已知。`cost_accounting_complete=false`、`mechanically_clean=false`，日志/请求审计错误0，导出错误0，本地harness错误0。11个Actor工具批次均按原始finish_reason为`tool_calls`且旧协议兼容；未规范化stop或执行工具。

## 3. Reviewer：只有一条可评价的来源归属

8条截断审查的共同模式是 `finish_reason=length`、`content=null`、`completion_tokens=reasoning_tokens=4096`。保存其原始reasoning，但不据此拼出四字段JSON或冒充已传给Actor。另3条API超时无交付内容。以上11条语义审查轴均为not_applicable，同时全部保留在12个计划分母中。

唯一有效者为[546/C1/r1](branches/qid_546_s29__C__r1__source_grounded_v1/result.json)，2350个completion tokens，其中2172个reasoning。它把可见Selby页面的1999转职业、>800杆破百、6次满分，与未证实的2023比赛链明确分开。

引用 `event:28:doc:55516` 的1600字符窗口确实支持上述局部人物事实；它没有将assistant早先的Players赛制/对阵推测升级为来源事实，也没有引用未见全文。需求保留“decider后**另两胜**4–3、4–0，再负于>400破百对手”，没有预先绑定某赛事。decision_effect允许保留Selby、修改候选或继续澄清关系，并明确“没有检索到”不能直接反证Selby。

因此来源归属、实际路线前提、需求未解决、需求相关、双向决策作用均通过；need_already_answered=no。资料窗口未证明2025-01-30的所有资格，审查也未声称这些日期条件已全部满足，仍留待后续核验。

| Reviewer评价 | C0 | C1 |
|---|---:|---:|
| 有效且来源合理 / 计划 | 0/6 | 1/6 |
| 来源合理 / 可评审查 | 不适用（0条） | 1/1（仅一例） |
| 实际备忘注入 | 0 | 1 |
| 有效审查后的可观察Actor | 0 | 0 |

这条备忘确已加入Actor请求，但Actor超时。`action_responds_to_need=unknown`，不能记成“需求被使用”“需求没有影响动作”或审查闭环成功。其他11条无备忘，需求响应为not_applicable。

## 4. Actor：必须同时检查工具方向和正文

| 全计划分母评价 | C0（6条） | C1（6条） | 总计（12条） |
|---|---:|---:|---:|
| 工具方向可接受 | 2 | 2 | 4 |
| **完整响应可接受** | **1** | **2** | **3** |
| 完整响应不可接受 | 5 | 3 | 8 |
| 完整响应未知（API失败） | 0 | 1 | 1 |
| 正文有无支持的事实断言 | 2 | 0 | 2 |
| 空正文但有工具 | 1 | 2 | 3 |
| 正文仅检索意图 | 3 | 3 | 6 |

517/C0/r1和r2分别交付10,966与3,744字符正文。服务商把这两条reasoning_tokens报告为0；这些文本实际位于`message.content`，不能当作隐藏推理删掉再评分。两条含未经可见来源支持的演员出生、家庭、片目、角色和“Some sources/Wikipedia says”等归属。517/C0/r1最后验证Idris—影片—角色的query方向合理，但不足以挽救整条响应。

| 题/重复 | C0实际动作 | C1实际动作 | 完整响应C0/C1 |
|---|---|---|---|
| 517/r1 | 长篇无据正文后查Idris的Constant Gardener角色 | 原题barracks hospital家庭关系 | no / yes |
| 517/r2 | 无据片目/家庭正文后重查Idris父亲soldier | Idris + barrack OR soldier + parents | no / yes（弱） |
| 546/r1 | 继续Players bracket + Selby/Trump | 有效审查注入后Actor超时 | no / unknown |
| 546/r2 | 改查Bingham×Championship League×比分 | 继续Players draw +候选名单 | yes（弱） / no |
| 776/r1 | 再查mistaken for shaman/1915/foreign language | 再查shaman/1915/misuse | no / no |
| 776/r2 | 与历史完全相同的same house35years/anthropologist | encouragement/report1940，但仍加anthropologist | no / no |

三题仍分别缺同一演员的完整身份链、同一球员的完整赛果/资格链、人物—作者—报告官方题名链。本实验无任何新工具结果，不报告检索命中率、BC+正确率或最终任务成功率。

**边界判断透明保留：** 517/C1/r2加入barrack是原题稀有细化，但OR可能回到旧路线；546/C0/r2首次修改赛事绑定而非只换名字，因此接受为另一赛事假设的尝试。但可见Championship League资料仅涉及2025/2024的3–0决赛，不能证明2023赛制或题目链。更严格评阅可以先要求查赛制。两项都降级时通过数为1/12；原始首轮标签不覆盖，主要交付失败和归因结论不变。

## 5. 配对及与512上限的有限比较

本批五对C0/C1都是精确回退，Actor请求完全相同。第六对546/r1仅C1加入有效备忘，但其Actor未返回。因此没有一对具备“有/无有效来源干预且双方动作均可见”的证据。

配对regression：C1四条no、一条yes（546/r2，以C0弱通过为基准）、一条unknown（546/r1超时）。这些是本批响应差异，不是合同因果效果。若546/C0/r2弱通过降级，该退化标签也不再成立。

| 全批指标 | Atria512上一批 | Atria4096本批 |
|---|---:|---:|
| 计划分支 / 调用尝试 | 12 / 24 | 12 / 24 |
| 收到响应 | 24 | 20 |
| 有效Reviewer | 0 | 1 |
| reasoning-only截断Reviewer | 12 | 8 |
| Reviewer / Actor API超时 | 0 / 0 | 3 / 1 |
| 完整动作可接受 | 7/12 | 3/12 |
| 动作未知 | 0 | 1 |
| 无据正文响应 | 0 | 2 |
| 可观察的审查后Actor | 0 | 0 |

逐请求核对确认：Reviewer请求只改512→4096；当前11条已返回Actor请求与上批完全相同。它们的标签转移是yes→no五条、no→yes一条、yes→yes两条、no→no三条。两批差异显示同输入下行为不稳定，不能将所有变化归因到上限；调度seed只固定顺序，不构成固定模型采样种子。调用时段、服务状态和默认采样的影响未受严格控制。

这仍是三个已反复使用的发展病例、每条件两次重复，且单一Codex辅助标注。没有独立人工金标、盲评或泛化准确率证据。先验判断标准在调用前冻结；完成后先核对prefix，再保存Reviewer判断，再看Actor，最后打开分组映射；所有阶段保留时间及SHA256。已知历史输出和卡片顺序，程序性先后不构成盲评。

## 6. 三条有说明力的bad case链

### A. 517/C0/r1：最后的合理query不能抵消前面的无据事实

[原始响应](branches/qid_517_s21__C__r1__baseline/result.json) · [事件](branches/qid_517_s21__C__r1__baseline/events.jsonl)

原题限定1970年代/羊、父亲军人、母亲军营医院、2005警察角色、2013惊悚片。可见工具支持导演与Iracema/Kinsey等局部关系，未建立Idris或其他演员的全链。Reviewer本次4096全用于reasoning，正式审查为空，Actor精确回退。

Actor交付超过一万字符的出生、父母、片目、角色陈述，先后肯定与否定Idris参演，并把未观察的Wikipedia/其他来源说法写入正文；随后提出 `Idris Elba The Constant Gardener role`。这个query确实尝试核验候选绑定，工具方向可接受，但正文断言缺证，完整动作不合格。尚未知该角色及同一演员的家庭、生肖和两部影片关系。此例定位的是**完整输出的证据约束**，不能用较好query隐藏正文问题，也不能归因未交付的Reviewer。

### B. 776/C0/r2：多给推理预算，回退动作仍完全重复

[原始响应](branches/qid_776_s53__C__r2__baseline/result.json) · [事件](branches/qid_776_s53__C__r2__baseline/events.jsonl)

原题有1886、1915语言误用、同屋35年/3孩子、鼓励1936–1940、1940年官方报告题名，**没有给anthropologist职业**。可见工具只是一般shaman、期刊和零散人物资料，没有完整人物—报告链。Reviewer再次耗尽4096 reasoning，未形成需求。

Actor提出 `"lived in the same house" "35 years" anthropologist`，与历史m22工具参数完全相同。不是“新的词序略有相似”，而是精确重复，并延续未证实职业过滤。正文只是意图，故没有新的事实断言错误；完整动作仍不合理。仍缺人物身份、鼓励关系和官方题名。此例显示即使无终答幻觉，下一动作仍可能没有进展。

### C. 546/C1/r1：来源审查合理，真实交接效果仍被超时截断

[原始响应](branches/qid_546_s29__C__r1__source_grounded_v1/result.json) · [事件](branches/qid_546_s29__C__r1__source_grounded_v1/events.jsonl)

原题没有指定Players赛事，要求decider后另两胜及随后失利，并附对手破百门槛。可见Selby窗口只支持部分个人统计；此前assistant反复绑定Selby×Players没有来源证明。

Reviewer成功指出这种局部支持与完整链之间的缺口，提出不固定赛事的精确比赛序列需求，允许保留候选而不因检索失败就反证。memo已注入实际Actor请求，但Actor超时；没有实际下一动作可分析。仍未知审查会否改善检索，也未知完整赛果链及该请求的服务端成本。此例是**交付链失败**，不是来源判断失败或需求未被采纳的证据。

## 7. 下一轮只改一个节点的建议

**建议仍停留在Reviewer交付验证，仅将Reviewer `max_tokens` 从4096提高到8192，重新冻结同一12分支计划。** 不修改来源合同、JSON schema、legacy memo、Actor、timeout、重试、Search/Open、Query或State字段，也不自动进入E1。本报告只提出建议，没有执行8192请求。

理由是本批8/12 Reviewer被明确的reasoning额度截断，这是当前最多的、可直接观察的阻塞；唯一完整JSON已经显示合理来源归属，尚不足以优先归咎于来源合同。8192是否足够未知，固定120秒超时下甚至可能增加超时风险，应如实保留，不能承诺扩大上限就能解决。

下一批首先看有效JSON/计划分母、截断与超时的分解，再看来源语义，最后才看有备忘后的Actor。新增有效审查不等于需求交接有效；若仍无可观察的审查后动作，就继续将交接效果标未知。当前两条Actor无据正文也不能由这个预算实验自动修复，先保留为独立故障证据，避免同时调整多个节点失去归因。

## 8. 复核与交付界限

原始 `summary.json` 保持runner的机械汇总及 `semantic_evaluation=not_evaluated`；人工辅助语义判断另存 `semantic_summary.json` 和全部12条标注，不改写原始记录。完整性脚本核对源/提示词哈希、计划、请求/事件、回退、usage、首轮标注SHA256、引用合法性及配对后仅regression变化。凭证/环境文件/权重未进入本批产物。

测试和机械审计通过，意味着实验记录可复核；**不表示模型调用全成功或动作全正确**。本批未追加失败重试、未执行Search/get_document、未查看标准答案或未来观察、未建立持久State、未进入E1。报告和原始产物按已有授权提交并推送。
