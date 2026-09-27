# E1 Dynamic Local Obligation — FAIL / STOP_E1

## Material Passport

27个自然历史快照，10个已暴露问题簇；单Codex reviewer；DeepSeek `deepseek-flash`。不声明fresh泛化或完整Agent成功。实验仅测试Q+C→O，O1增加原始H。历史Gap prompt与Gold引用均未改。

## 冻结、执行、审阅

- Remote/base：`fb61da13d3be2511f37da590429ebea7f706bd0d`，fetch后与任务一致。
- E1参考、输入、prompt、code、rubric、gate、schedule冻结：`7c71fe66a08af71528ca52d33ce38979e413ed45`。
- 两臂×27×2=108请求，首个正式请求充当唯一auth canary；并发峰值8，重试0。
- 108 HTTP200、108合法单字段schema，传输/格式失败0。原始响应、reasoning、请求、attempt与结果全部保留。
- first-pass只看Q/C/O，标签在`06f31332fa3fac1574cdaebdcaec55e69f180245`提交后才揭示Gold/H/臂/replicate，做Gold comparison、pair/H review与aggregate。
- Reviewer了解历史Gold，不能声称完全blind或独立评审。Locality、title/identity、referent边界有主观性；中等歧义判定及理由保留。

## 主门槛

| 指标 | O0：Q+C | O1：Q+C+H | O0门槛 |
|---|---:|---:|---:|
| Strict Obligation Validity | 29/54 (53.7%) | 25/54 (46.3%) | ≥80% |
| Schema-valid | 54/54 (100.0%) | 54/54 (100.0%) | ≥95% |
| 两次都有效且同一/兼容目标 | 11/27 (40.7%) | 5/27 (18.5%) | ≥80% |
| 两次都有效（含不同目标） | 12/27 (44.4%) | 10/27 (37.0%) | 描述性 |
| 整题重述或捆绑目标 | 15/54 (27.8%) | 17/54 (31.5%) | ≤10% |
| GoalGrounded | 54/54 (100.0%) | 54/54 (100.0%) | ≥90% |
| Unresolved | 53/54 (98.1%) | 54/54 (100.0%) | ≥90% |
| Material | 54/54 (100.0%) | 54/54 (100.0%) | 严格有效组成 |
| Local | 39/54 (72.2%) | 37/54 (68.5%) | 严格有效组成 |
| Coherent | 50/54 (92.6%) | 48/54 (88.9%) | 严格有效组成 |
| ScopeFaithful | 40/54 (74.1%) | 43/54 (79.6%) | ≥90% |
| NonDownstream | 43/54 (79.6%) | 38/54 (70.4%) | ≥90% |
| EvidenceResolvable | 54/54 (100.0%) | 54/54 (100.0%) | 严格有效组成 |
| Wrong relation arguments | 4/54 (7.4%) | 4/54 (7.4%) | ≤5% |


**O0未通过6项门槛：strict、scope、non-downstream、broadness、wrong-relation-arguments、稳定选择。** O1不能救回O0。所有54个planned slots与27个pairs均在分母。

GoalGrounded/Material按目标是否来自Q且对Q具有实质意义判定；具体角色/时间/附加约束错误另外计入ScopeFaithful，不因100%目标相关就说所有条件均grounded。一个任务现实中可查证也不等于它是正确的当前研究目标。

## Gold不能被当唯一正确目标

| 分类 | O0 | O1 |
|---|---:|---:|
| gold_equivalent | 6/54 (11.1%) | 3/54 (5.6%) |
| alternate_valid | 23/54 (42.6%) | 22/54 (40.7%) |
| invalid | 25/54 (46.3%) | 29/54 (53.7%) |


O0的23条alternate-valid、O1的22条均已计入strict。8个旧Gold属于已满足局部对照，动态模型应选另一个未解决义务；重复已满足目标会失败。Gold-equivalent包括近似核心目标，4条近似项的限定条件增减单独记录；没有按字符串exact-match评分。若E2曾被允许，这些限定差异还需检查是否可直接继承Gap reference；本轮未进入该步骤。

## 失败机制

| 错误（可重叠） | O0 | O1 |
|---|---:|---:|
| downstream_obligation | 11/54 (20.4%) | 16/54 (29.6%) |
| whole_question_restatement | 11/54 (20.4%) | 12/54 (22.2%) |
| bundled_objectives | 4/54 (7.4%) | 6/54 (11.1%) |
| relation_strengthening | 11/54 (20.4%) | 7/54 (13.0%) |
| wrong_relation_arguments | 4/54 (7.4%) | 4/54 (7.4%) |
| wrong_object_scope | 2/54 (3.7%) | 3/54 (5.6%) |
| already_supported | 1/54 (1.9%) | 0/54 (0.0%) |
| over_atomic | 0/54 (0.0%) | 0/54 (0.0%) |
| unresolved_referent | 7/54 (13.0%) | 13/54 (24.1%) |


典型证据：

1. **未建立事件→直接标题**：F10_S01四条均问Marwaha后来文章标题；C只建立作者/书，未建立后续文章事件。不是因为未知文章身份不合法，而是输出将候选发表事件当作已发生后追属性。
2. **目标过宽**：论文、书、人物案例常把原题几乎全部独立条件重新塞进O；单个对象名未自动构成locality。也接受多个互补条件共同识别一个DLC、采访事件或作者profile，未要求逻辑原子化。
3. **论元腐坏**：Q说“一名作者有另一篇论文”“一名作者在Harran”，没有给出两者相同或不同；输出有时强制合并，有时强制成为不同coauthor。O0四条wrong-argument中三条属此类，另一条把初始接收OSS officer代成最终courier。O1四条包括作者角色合并两条、死亡城市所在国→artist国家一条（中等歧义）、队友国籍关系一条。
4. **G23类的具体追踪**：在原G23/F15_S01，两臂0/2argument错误，因为都合理选择已知比赛的未知host，未选择国籍义务。相同qid的F15_S02，O1 replicate2/R054出现“其他两人彼此同国→都与Jerry同国”。这里H是null，因此不能归因于H。
5. **Stale少、over-atomic未观察到**：仅O0 R079重复已被C7/C9支持的共同疾病名；0条over_atomic。不能把本轮诊断写成“需要更少条件”——核心是局部目标、真实referent和关系范围。

## 重复稳定性与H

O0：same9、compatible2、different-but-valid1、one-valid-one-invalid5、both-invalid10。稳定选择11/27；即使只要求两次都有效、不要求同目标，也只有12/27。O1：same4、compatible1、different-but-valid5、one-valid-one-invalid5、both-invalid12。不同但合法不记为单条语义失败，单独降低稳定选择。

O0两次strict=14/27、15/27；O1=15/27、10/27。O0 better7、O1 better3、tie44。O1数值更差，且5对都合法但切换目标；不能据此证明H导致全部退化。Null-H子集O0=11/22、O1=9/22，说明指令差异/运行波动也存在。

H contamination按“仅H提出的候选角色/关系被变成要求”标记2/54（非空H为2/32）：G14把Euler固定为书中L.E.。Euler名字本身在C中，未将“出现名字”当污染；未观察到新增的H-only名字/日期进入O。这两条是**与H一致的候选角色提升**，O0也出现同类错误，不能主张H具有已识别的因果效应。其余错误不硬归入H污染。

## 歧义与敏感性

O0低歧义子集17/38=44.7%。忽略Local/Coherent两维，O0最多35/54=64.8%；进一步把所有medium条目都算成功，仍只有37/54=68.5%，低于80%。O1对应32/54与35/54。以上为事后描述性宽松上界，不改原标签或gate。失败结论不依赖严格的broadness边界。

历史Gold状态分层：O0 unsupported11/24、partial7/14、satisfied11/16；O1分别11/24、5/14、9/16。这里状态是**旧Gold的状态**，不表示动态O已满足。

## E2严格停止

E2未准备Dynamic-O Gap references、未冻结schedule、未调用Oracle或Dynamic Gap。Concurrent Oracle strict、Dynamic|valid-O、Dynamic end-to-end、实际Loss均**未测**，不能填0或拿旧92.6%当同期结果。

预注册O0 replicate1有14/27合法；在invalid-O直接失败的规则下，即使下游Gap全对，端到端纯算术上界也只有51.9%。这是E1标签导出的上界，**不是实测cascade**。不运行E2符合任务停止规则，且不会因下游成功掩盖O失败。

## 成本与完整性

Planned/sent/returned=108/108/108；E2=0。Input79,500；completion452,664（含reasoning446,273）；total532,164。Cache hit52,594/miss26,906，加权命中率**66.16%**；usage未知0。无价格验证，不报告货币成本。

Wall281.29秒；单请求median13.33秒、P95 44.31秒、max150.67秒；completion median2,722、P95 10,192、max33,623。未触发timeout，max_tokens仍按任务省略，没有重试。

16,636个历史文件哈希未变；27个原始QCH和3个复制Gold/bank文件字节一致；108条raw重新解析与result一致，accounting重算一致。旧Gap prompt逐字保持原样。

## 解释

E1支持“模型经常找到Q相关且未解决的内容”，不支持“可以稳定选出正确局部O”。当前已直接观察到的瓶颈是O选择/表达，具体为范围、下游顺序与参数角色。Gap在动态合法O下的鲁棒性仍未测，不能从本轮外推。

保持停止；下一次独立实验应先隔离这些失败，而非直接fresh确认或加requires/Binding IR。没有prompt revision、Gold改标、检索或persistent state增加。
