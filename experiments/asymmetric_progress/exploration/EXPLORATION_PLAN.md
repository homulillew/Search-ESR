# One bounded exploration: Audit materiality calibration

## Observed failure and scope

正式 primary 已完成：Audit false closure 0/38，但正确 closure 4/10；六次拒绝都因要求冗余身份/剧情位置/字面角色措辞，违反冻结 materiality。LA 正确停止 2/5，L/LL 为5/5。选择唯一 observed failure direction：**拒绝前判断缺失细节是否会实质改变答案**。

这是任务 §48 范围内的一次 Audit materiality 探索，不是 FULL。没有观察到需要系统穷尽条件扫描才能发现的 Audit false closure，故不触发 §47 FULL 条件。L0/L1、schema、provider、transport、failure policy 均不变。不改变任何正式标签或 gate，不进入 Frontier。

## Selection frozen before exploration calls

共12个 checkpoint，每个新 Audit prompt 两次，共24次。选择规则：全部5个 fresh resolved控制（A07/A08/A09/A18/A19），一个历史不同题型resolved控制S03；强制P17/P19（S01/S02），再加入quantity S09、temporal/source attribution S07、zodiac S08三个已冻结压力，以及主集出现event presupposition的A24。6 resolved +6 unresolved，5 qids。

这些是错误分析后选择的非fresh机制样本。各自原始Audit×2构成已存在的描述性配对baseline；不重跑baseline、不挑选好replicate。原始Q/Claims与标签保持字节内容，唯一干预为末尾追加的一个generic materiality段落。不得用结果称fresh确认或覆盖正式gate。

## Intervention

保留原Audit prompt，追加：在拒绝前做counterfactual materiality检验。若当前已观察的身份和最终关系足以区分答案，仅缺少冗余旁证或重复角色标签，不构成blocker。明确保护尚未建立的数量界限、请求日期/来源归属、参与者角色链接和真实冲突。无具体题名/答案/Claim索引例子，无oracle信息，无工具，无新persistent字段。

## Evaluation and stopping

报告固定12 resolved slots与12 unresolved slots的correct/false closure、有效blocker、precision、certificate、over-demand、unsupported premise、tokens。希望减少missed closure且不新增false closure；探索成功的描述性目标为correct closure≥11/12、false closure=0/12、certificate adequacy≥90%。逐qid/replica公开，样本少且同题重复，不称统计验证。

只有这一版追加prompt，不再调整、不做prompt sweep，不允许下一轮重采样。所有结果保留。运行前将plan、精确prompt、24请求、baseline hashes、标签与评分rubric写入manifest并commit；执行HEAD逐调用记录。
