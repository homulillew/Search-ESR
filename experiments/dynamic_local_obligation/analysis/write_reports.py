"""Render results without changing frozen labels or gates."""
from experiments.dynamic_local_obligation.common import *

def main():
 m=read(P/'e1_obligation/METRICS.json');h=read(P/'e1_obligation/H_ABLATION.json');a=read(P/'e1_obligation/ACCOUNTING.json');d=read(P/'analysis/DIAGNOSTICS.json');s=read(P/'analysis/SENSITIVITY.json')
 fmt=lambda v:f"{v['n']}/{v['d']} ({v['rate']:.1%})" if v['rate'] is not None else '未测'
 table='| 指标 | O0：Q+C | O1：Q+C+H | O0门槛 |\n|---|---:|---:|---:|\n'
 for key,label,gate in [('strict','Strict Obligation Validity','≥80%'),('schema','Schema-valid','≥95%'),('stable_both_valid','两次都有效且同一/兼容目标','≥80%'),('raw_both_valid','两次都有效（含不同目标）','描述性'),('broadness','整题重述或捆绑目标','≤10%')]:
  table+=f"| {label} | {fmt(m['O0'][key])} | {fmt(m['O1'][key])} | {gate} |\n"
 for key,gate in [('GoalGrounded','≥90%'),('Unresolved','≥90%'),('Material','严格有效组成'),('Local','严格有效组成'),('Coherent','严格有效组成'),('ScopeFaithful','≥90%'),('NonDownstream','≥90%'),('EvidenceResolvable','严格有效组成')]:
  table+=f"| {key} | {fmt(m['O0']['dimensions'][key])} | {fmt(m['O1']['dimensions'][key])} | {gate} |\n"
 table+=f"| Wrong relation arguments | {fmt(m['O0']['errors']['wrong_relation_arguments'])} | {fmt(m['O1']['errors']['wrong_relation_arguments'])} | ≤5% |\n"
 errors='| 错误（可重叠） | O0 | O1 |\n|---|---:|---:|\n'
 for e in ('downstream_obligation','whole_question_restatement','bundled_objectives','relation_strengthening','wrong_relation_arguments','wrong_object_scope','already_supported','over_atomic','unresolved_referent'):
  errors+=f"| {e} | {fmt(m['O0']['errors'][e])} | {fmt(m['O1']['errors'][e])} |\n"
 selection='| 分类 | O0 | O1 |\n|---|---:|---:|\n'
 for k in ('gold_equivalent','alternate_valid','invalid'):selection+=f"| {k} | {fmt(m['O0']['gold_selection'][k])} | {fmt(m['O1']['gold_selection'][k])} |\n"
 report=f'''# E1 Dynamic Local Obligation — FAIL / STOP_E1

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

{table}

**O0未通过6项门槛：strict、scope、non-downstream、broadness、wrong-relation-arguments、稳定选择。** O1不能救回O0。所有54个planned slots与27个pairs均在分母。

GoalGrounded/Material按目标是否来自Q且对Q具有实质意义判定；具体角色/时间/附加约束错误另外计入ScopeFaithful，不因100%目标相关就说所有条件均grounded。一个任务现实中可查证也不等于它是正确的当前研究目标。

## Gold不能被当唯一正确目标

{selection}

O0的23条alternate-valid、O1的22条均已计入strict。8个旧Gold属于已满足局部对照，动态模型应选另一个未解决义务；重复已满足目标会失败。Gold-equivalent包括近似核心目标，4条近似项的限定条件增减单独记录；没有按字符串exact-match评分。若E2曾被允许，这些限定差异还需检查是否可直接继承Gap reference；本轮未进入该步骤。

## 失败机制

{errors}

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
'''
 write(P/'e1_obligation/REPORT.md',report)
 final='''# 最终结论：Dynamic Local Obligation Derivation

**E1 Gate：FAIL；STOP_E1。E2未执行。**

主臂O0（Q+C）strict **29/54=53.7%**，稳定选择 **11/27=40.7%**。O1（加H）为 **25/54=46.3%**、**5/27=18.5%**。主要失败是目标过宽、未建立事件的下游属性、关系参数范围改变。不能仅凭Gold-O→Gap曾通过，就认为模型已能动态生成可靠O。

## 任务要求的17个回答

1. **Q+C→O strict多高？** 29/54（53.7%），未达到80%；O1为25/54。9项gate中O0失败6项。
2. **经常选已支持目标吗？** 不经常：O0 1/54，O1 0/54。旧Gold的8个satisfied controls并未强制当作当前目标；合法alternate已计成功。
3. **仍有downstream jump吗？** 有：O0 11/54（20.4%）、O1 16/54（29.6%）。后续文章标题、未建立比赛的年份、未知gift/building的大学属性是主要模式。
4. **仍过度atomic吗？** 本次0条；没有证据表明需要把目标拆得更碎。多个互补条件共同识别一个对象可以合法。
5. **重新包装整个Q吗？** 是：whole-question O0 11/54、O1 12/54；并上bundled objectives后broadness为15/54、17/54。
6. **最常见relation-scope corruption？** 把两个独立“一名作者”角色强行合并/分开；还出现初始handoff officer→最终courier，以及其他两位队友彼此同国→与Jerry同国。wrong-argument两臂均4/54。原G23两臂选host所以该cell未触发国籍错误；该错误发生在同qid的下一快照F15_S02，且H为null。
7. **Gold-equivalent/alternate-valid比例？** O0为6/54（11.1%）与23/54（42.6%）；O1为3/54（5.6%）与22/54（40.7%）。二者均计入strict，不以Gold exact-match判错。近似等价的限定差异已单列记录。
8. **两次重复是否稳定？** O0同一/兼容11/27；仅“两次都合法”12/27。O1分别5/27、10/27；5对是不同但都合法的目标，未当单条语义失败。O0两次strict为14/27、15/27；O1为15/27、10/27。
9. **H是否改变scope？** 同期观察到选择和scope变化，O1较多downstream、较少稳定选择；配对O0胜7、O1胜3、平44。不能将全部差异因果归到H，尤其null-H子集也有差异。
10. **H是否造成candidate contamination？** 按内容判据标记2/54（非空H2/32）：H提出Euler可能是书中L.E.，O把此候选角色固定为要求。名字本身也在C，且O0同样会固定Euler；这是H一致的角色提升，不能证明由H造成。没有新增H-only名字/日期进入O的证据。
11. **Dynamic O送入frozen Gap后的strict？** 未测。E1失败，按预注册停止，没有Gap调用。
12. **同期Oracle/Dynamic差距？** 未测；没有重跑Oracle，也未拿旧92.6%代替同期比较。
13. **Pipeline失败主要在O还是Gap？** 当前明确失败在O阶段门槛；Gap对动态O的性能未知。固定rep1仅14/27合法，因此按invalid-O直接失败规则，即便Gap完美，纯算术端到端上界也为51.9%。这不是实测cascade或精确因果损失分解。
14. **需要requires/depends_on吗？** 尚无依据直接加入。先独立定位目标选择、实体/事件确立和属性抽取的边界；本轮没有做结构干预对照，不能宣称依赖字段可以修复。
15. **需要Binding IR吗？** 没有。关系参数错误值得独立机制测试，但不证明变量/谓词图/AST必要；本轮禁止且未实现。
16. **能进入fresh dynamic-obligation confirmation吗？** 不能。E1未过、E2未运行。应先另立development机制实验，不通过继续调本轮prompt获得表面PASS。
17. **是否仍支持最小persistent Q+C+H / ephemeral O+Gap？** 可保留为尚待检验的架构假设；本轮未给出可靠动态O管线证据，也未证明需要更多persistent fields。Gold-O Gap的有限正向证据仍保留，完整控制链尚未成立。

## 判断稳健性与限制

已暴露27快照/10问题簇；单reviewer，知道旧Gold，无法完全blind。第一轮技术上隐藏Gold/H/arm/replicate，标签提交后才揭盲、比较和汇总。Locality与identity/attribute边界存在语义判断，逐条reason和中等歧义标记保留。

即使事后忽略Local/Coherent，并把所有medium条目算成功，O0最多37/54=68.5%，仍不达80%。该分析不修改冻结标签或gate，也没有追加模型调用。

## 执行与交付

108个请求全部保留，108 HTTP200及schema成功；重试0，E2/检索/Writer调用0。Input79,500，completion452,664（reasoning446,273已包含），total532,164；cache hit/miss52,594/26,906，加权命中率**66.16%**。并发峰值8，批次281.29秒，usage缺失0；没有虚构货币成本。

Base `fb61da1`；预调用freeze `7c71fe6`；first-pass标签提交 `06f3133`。历史16,636个文件与旧Gap prompt未改；Gold/bank逐字继承。完整输出、评审、成本、敏感性与核验保存在本目录。

**允许结论：人工Gold O能支撑较好的Gap计算，但当前Q+C→O仍不能稳定地产生足够可靠的当前局部义务；本轮接受这一负结果并停止。**
'''
 write(P/'analysis/FINAL_CONCLUSION.md',final)
 write(P/'analysis/STATUS.json',{'status':'COMPLETED_STOP_E1','E1_gate':'FAIL','E1_calls':108,'E2_calls':0,'fresh_calls':0,'retrieval_calls':0,
  'prompt_revisions':0,'Gold_changes':0,'persistent_semantic_fields_added':0,'next_stage':'No automatic progression; independent development study required'})
if __name__=='__main__':main()
