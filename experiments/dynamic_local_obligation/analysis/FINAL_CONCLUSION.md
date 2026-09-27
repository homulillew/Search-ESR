# 最终结论：Dynamic Local Obligation Derivation

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
