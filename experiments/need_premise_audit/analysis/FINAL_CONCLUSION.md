# Ephemeral Premise Audit / Need Type Checker：最终结论

## Material Passport

**当前状态：STOP_E1。** 已完成22条历史B0 Candidate Need的reference audit、88个计划请求及完整失败/语义记录。E2 Constrained Repair和E3 Fresh Confirmation均未运行。旧实验只读；本轮没有Need generation、Search/Find/Open、Writer、Closure或loop调用。

用户任务第40节明确授权本轮有界调用。模型保持DeepSeek `deepseek-flash`，temperature0，JSON mode，max_retries=0，省略max_tokens。新分支为 `experiment/need-premise-audit`，基于远程最新 `a12167e`；请求前冻结提交为 `ee6ab82`。

## 一、结果与执行缺陷分别是什么

### V1 绝对能力门槛没有通过

| 指标 | 实际结果 | 门槛 |
|---|---:|---:|
| 错误候选检出率 |16/22，**72.73%**|85%|
| 有效候选保留率 |10/22，**45.45%**|85%|
| 整条响应的支持绑定正确率 |30/44，68.18%|85%|
| target / premise 区分正确率 |28/44，63.64%|85%|
| 两次完整决策一致率 |16/22，72.73%|80%|
| V1 完整schema有效率 |43/44，97.73%|95%|

V1能够重述正在询问的target：43个schema有效响应中43个都正确。但它经常又把这个target的组成部分当作必须先有证据的前提，从而拒绝合法Need。例如：

- 直接问Kwon与配偶是否共同捐赠，却要求先证明配偶关系；
- 直接问Sophie伴侣采访是否发生，却要求先确认伴侣或完整候选身份；
- 已经在问“哪个DLC符合描述”，却因为DLC未识别而判定需先发现subject。

**显式抽出target，还不足以稳定区分哪些事实必须预先成立。** 这也是本轮最清楚的机制失败。两个replicate的错误检出分别6/11、10/11，有效候选保留均5/11；temperature0仍有变化，而且重复一致也可能是一致地误拒。

### V0 比较不可用，原因是执行前检查遗漏

V0的44条请求全部HTTP400。服务端要求JSON mode的提示文本包含“json”，任务提供的V0文本没有该字样；我没有在首次发送前补齐这一机械接口检查。**这是我的执行集成遗漏，不是V0模型能力失败。**

因此，本轮不能回答V1是否优于generic second-pass。原始METRICS保留失败计划槽位的零成功计数，但这些数值不能用作V0准确率，也不能据此宣称V1胜出。修正方案仅是在V0中把 `Return only:` 改为 `Return only JSON:`；已离线验证并增加只读输入预检查，原始请求/提示词未变，未重发任何请求。[执行问题与具体修正方案](FORMAT_INCIDENT.md)

这项执行缺陷损害了预定的相对比较，但V1自己的五个绝对语义/一致性指标均未过门槛。因此本轮仍须停止，不能为了补全报告继续Repair或Fresh，也不能把拒绝请求替换成新样本。

## 二、证据范围与敏感性

样本为22个candidate instances、12个状态、7个qid，来自两轮冻结B0输出；11个错误与11个有效对照，H/No-H均按10:1匹配。合法对照按哈希机械选取。Reference decisions为11 keep、6 lift_premise、5 discover_subject。相同QCH或相同Need跨历史run重复出现，不是独立新题。

Reference和响应均由单个Codex reviewer按prefix审阅。模型调用前已冻结reference；schema暴露实验臂，不能宣称盲审或独立gold。所有回复审阅完成并提交后才汇总指标。没有读取未来工具、gold或模型隐藏推理来决定语义标签。

排除全部medium/high reference歧义后，14个candidate instances、28个响应槽位仍只有：错误检出7/10，合法保留8/18。合法Need被拒绝的问题不依赖最有争议的clinical-report/accident/courier边界。支持绑定的个别判断有语义歧义，但即使把绑定项全部算对，也不能改变检出率、保留率和一致率不达标。[敏感性记录](SENSITIVITY.json)

该批为已暴露、重复、聚集的开发样本，不做fresh泛化或显著性声称。No-H仅2个candidate instances/4个响应，不能独立支撑No-H能力结论。

## 三、按任务顺序回答十五个问题

| # | 问题 | 当前回答 |
|---:|---|---|
|1|最常见隐藏前提是什么？|Reference错误中，**未绑定具体来源/事件5/11**；另有错误的letter日期绑定、未经证实的article/SPS事件、候选letter内容和courier角色。类型可重叠。|
|2|能稳定区分target与presupposition吗？|**不能**。Target重述43/44成功，但真正区分仅28/44；准确复述不等于知道它无需预先证实。|
|3|能发现未绑定subject/source/event吗？|**有局部能力，不稳定**。能发现部分book/accident缺口，也会把Q描述当作具体source或仅关注Euler而漏掉book。整体subject判断27/44。|
|4|会把真正target错判为必须已支持吗？|**会，15个有效响应出现此类错误**，尤其参与人关系、DLC discovery和复合历史条件。|
|5|能正确绑定Q/exact Claim吗？|**机械ref合法不等于语义成立**。整条响应全部绑定正确30/44；逐slot为178/204（87.25%），后者不是冻结gate指标。|
|6|V1优于generic verifier吗？|**无法判断**：V0接口拒绝，没有模型输出。不得把失败分母中的0当作模型准确率。|
|7|两次重复一致性如何？|完整三分类16/22（72.73%）；二分类18/22（81.82%）。主门槛用前者，两次失败不计一致。|
|8|Oracle audit下Repair可靠吗？|**未测**，E1失败后按规则未运行E2。|
|9|Model与Oracle audit repair差距？|**未测**，不能把本轮结果归因于Repair。|
|10|Repair保留局部性吗？|**未测**。Checker额外要求完整候选身份提示可能存在扩散风险，但不是已测Repair drift。|
|11|Repair引入broadness/stale/hallucination吗？|**未测**。Checker的false premise与wrong anchor已单独记录，不能替代Repair指标。|
|12|Fresh QCH复制开发结果吗？|**未测**，没有fresh采样/调用。|
|13|足以支持Generate→Check→Repair吗？|**不够**。Checker绝对可靠性与合法Need保留门槛均失败，Repair尚未测试。|
|14|需要增加persistent state吗？|**没有证据**。当前定位为checker计算/类型边界错误，加上V0接口集成问题；不能推出Q+C+H不足。|
|15|能重新打开Need→Multi-Query吗？|**不能**。本轮E1未通过，E2/E3未运行；Query收益仍未测。|

## 四、失败分类与解释

在43个schema有效V1响应中，可重叠计数为：false premise21、subject error16、target/premise confusion15、wrong anchor13、missed premise8。另1个V1响应因为多出top-level `type`字段而schema失败；44个V0是接口拒绝，不编造语义错误标签。

**已观察**：Checker会增加原Candidate不需要的前提，要求验证候选是否满足整道Q，或者把正在发现的实体当作必须先识别的背景。也能在部分例子中正确发现memorandum与letter日期差异。它不是完全没有检查能力，而是还不能可靠保护合法target。

**诊断解释**：当前类型规则没有稳定处理“目标内部的存在性成分”和“为了询问下游属性必须建立的背景”之间的边界。结构化字段增加了可审计性，但字段存在不等于判断可靠。

**未验证假设**：更明确地测试这两种作用域，可能减少过度保守。该想法没有在本轮形成新prompt或付费修订，不能报告为解决方案已有效。通用第二遍检查的相对效果仍需要一个执行有效的对照实验。

## 五、成本、缓存与保存

总计88个请求尝试，全部保留请求、响应和结果。仅44个V1响应有完整usage：输入46,184 tokens；输出248,746，其中reasoning238,692已包含在输出内；可报告总量294,930。缓存hit31,104、miss15,080，**已报告usage的加权命中率67.35%**。44个被拒V0无usage，不能推断其账单为零，也不把缺失usage混成已测零成本。

墙钟155.22秒，峰值并发8。没有超时/length失败、重试或工具调用；保留44个HTTP400与1个schema失败。未查询价格，不虚构金额。[账目](EXECUTION_ACCOUNTING.json)

机械完整性核验检查所有冻结文件、15,799个历史文件、88份真实发送/返回记录及评分重算。机械PASS表示记录一致，不代表V0实验执行成功或V1门槛通过。[完整性记录](INTEGRITY.json)

当前研究决策：保持Q+C+H持久状态；不部署该Checker为强制前置检查；不进入Repair/Fresh/Multi-Query。下一项独立实验若继续，必须先采用已验证的JSON-mode输入检查，并单独解决误拒合法target的问题。本轮结果和失败不重写。
