# E1V — Gold Package Verifier中期报告

## 执行范围

用户“好的，我授权”对应前一条明确请求的96次Verifier调用。实际执行96/96，全部有效格式返回，零失败和重试。所有输入、Gold和程序均按原Verifier freeze执行，21,632个历史实验文件保持原哈希。

Auditor未运行。35次SUPPORTED分别生成一条实际审计请求，编译规则和两个Prompt均在Verifier调用前冻结。没有根据Gold或本节分析选择、删除或修补审计案例。61次OPEN按冻结流程不进入Auditor。

## Verifier-only结果

| 指标 | 结果 |
|---|---:|
| 正例 / 负例slots | 42 / 54 |
| TP / FP / TN / False OPEN | 32 / 3 / 51 / 10 |
| 引用Witness对应的Support Precision | 32/35 = 91.43% |
| 引用Witness对应的Support Recall | 32/42 = 76.19% |
| 仅verdict的Precision / Recall | 91.43% / 76.19% |
| Schema有效率 | 96/96 = 100% |
| 两次重复的verdict一致率 | 45/48 = 93.75% |

本次不存在“Gold正例被判SUPPORTED，但引用集合不充分”这一额外情况，因此witness与verdict分数相同。复核不使用provider reasoning，输出只包含verdict和IDs，不能从中读出完整推理原因。

### 召回上界与后续范围

Auditor是单向拒绝器：最终真支持集合必然是现有32个真支持的子集。即使35次审计保留全部32个真支持、拒绝全部3个误接受，最终Precision可达100%，**Recall仍只能到32/42=76.19%**，低于90%。临床正例已全部OPEN，Auditor无法恢复这6个slot。

因此本轮E1不能满足全部冻结Gate，不能进入E2。完整E1指标仍等待必要Auditor结果；不把尚未执行的审计rescue、额外误拒或最终Precision记成0或已通过。35次审计的用途是完成反向审计机制诊断，不是争取E2准入。

## 错误的内容级检查

以下13个错误输出已按实际Target/Context/ClaimSet及冻结Gold检查；这是单一、熟悉任务且未掩码的诊断审阅，不是独立评审。全部96条Primary判定为机械比较，不改Gold。

### False Support：3次

1. `A03_CAND3`，2/2：孤立C5说`that paper`，模型仍接受完整table/emotion/percentage Target。冻结参考要求可见的paper/table antecedent；该参考已预标歧义。
2. `A24_CAND2`，1/2：只引用C3，接受`In it / the author refers to / their country having regained a region`。C3只是King Michael在信中提到Romania收回North Transylvania，未显式证明Romania是其国家。该参考已预标歧义，本轮调用前已改为OPEN；历史Gold未改。

这3次都进入35条Auditor请求。尚不知Auditor能否找出缺口。

### False OPEN：10次

- **临床6次**：`A17_CAND1–3`两次重复全部返回OPEN，引用C7，并唯一标记`U1: The first case`未覆盖。所选临床事实并未被列为缺口；country/history完全不在输入中。观察直接支持“阻塞点位于first-case角色单位”，不能声称模型仍在要求看不到的country/history sibling。
- **DLC technology 2次**：`A20_CAND2`两次都引用C3+C6，但标记`U2: made changes to the mechanics`未覆盖。它们没有把Europe/nation或religion当额外Target。冻结参考接受DLC绑定加manual的technology-redone内容；输出未解释为何不接受U2，不能断言内部原因。
- **Book+article interval 2次**：`A14_CAND1`r1、`A14_CAND2`r1都只标记`U3: six years after`缺失，仍引用C1+C3。冻结Gold采用2016→2022出版年份；日期精度可能是解释，但本次JSON没有理由字段，因此该解释保持为假说。

临床结果不能干净地归因为模型不会理解临床事实。Gold采用“观察到的候选病例可以填入first-described-case槽位”的局部支持契约，而输入保留了字面`The first case`，没有额外的槽位绑定对象。模型把这个单位判为未覆盖。参考契约、角色表示和验证器的解释仍可能交互。Gold Package已固定不等于Gold语义契约已由独立证据证明无歧义；本轮保持原Gold，不热修Prompt、不重试。

## 指定Case观察

| Case | Verifier结果 | 当前可说什么 |
|---|---|---|
| Euler | 错误支持0/2 | 本次固定Target保留了reference edge，两个verdict均OPEN。 |
| Book-only | 错误支持0/2 | 未将单独book publication升级为已建立的article comparison。 |
| q637 clinical | 正确支持0/6 | 三种局部Scope都被first-case角色单位阻塞。 |
| Ding marriage | 正确支持2/2 | 局部婚姻条件保留；整个gift Parent仍OPEN。 |
| DLC nation qualifier | 错误支持0/4 | 未完成qualified nation条件时保持OPEN。 |
| DLC technology | 正确支持0/2 | 具体失败单位是general mechanics-change predicate。 |
| Generic SPS | 错误支持0/2 | 一般疾病描述未被提升为具体病史。 |
| Patient nationality/report country | 错误支持0/2 | 两次都未建立report-country/history Target。 |
| Memo/letter date | 错误支持0/2 | 未建立letter/accession时间关系。 |
| Teammate same-country | 错误支持0/2 | 姓名和Jerry国籍未替代另两位同国关系。 |
| Alma-mater/building | 错误支持0/2 | 未将person-degree关系当building-university关系。 |
| Nationality-only/champion | 错误支持0/2 | 无championship membership时保持OPEN。 |

这些均为Verifier-only结果，尚不是经过Uncovered Auditor的Qualified Support。

## 歧义、重复和解释限制

排除调用前标记的4个歧义证书，仅作描述性敏感性：Precision=29/29=100%，Recall=29/38=76.32%。临床0/6不变，召回门槛仍不可达。说明本轮primary误接受集中于已声明的参考争议，召回不足另有稳定来源；不能因此把Primary改成PASS。

96次调用对应46种不同Verifier请求payload。原48个证书中，Book两种locator在固定Package后得到相同payload，DLC release的两种locator也得到相同payload。因此一些错误或正确结果属于同一输入的重复观察，不是新的独立证据。既定48×2分母保持不变。

关于Book日期，两个相同payload都受出版年份/精确日期解释影响。原支持参考只把`A14_CAND2`标为AMBIGUOUS_REFERENCE，Package级政策已披露该日期解释。`A14_CAND1`没有被事后追加到预注册排除集合；报告如实保留这个参考标记粒度限制。

上一轮Q1恰好也为32/35 Precision，但Recall分母是44，本轮为42，且目标范围、参考标签和引用Witness评分发生变化。不能把两个91.43%当作严格相同条件的因果对照，也不能把Recall分母变化当作改善证据。

## 调用与缓存

| 项目 | 实际 |
|---|---:|
| 发送 / 返回 / schema有效 | 96 / 96 / 96 |
| 失败 / 重试 | 0 / 0 |
| 峰值并发 | 8 |
| 批次耗时 | 76.36秒 |
| 中位 / p95 / 最大延迟 | 2.33 / 18.42 / 28.70秒 |
| Input / Output / Total tokens | 51,556 / 99,924 / 151,480 |
| Output中reported reasoning tokens | 96,799 |
| Cache hit / miss | 24,188 / 27,368 |
| 缓存命中率 | **46.92%** |

usage覆盖96/96，hit+miss与input完全一致。reasoning是output子集，未重复相加，未用于语义审阅。金额未知，不推算货币成本。Auditor真实调用0，E2–E4真实调用0。

## 下一步授权对象

35条实际Auditor请求已由冻结编译器生成，包含模型实际引用的证据子集，不含Gold/verdict/reasoning。保留全部35条，包括预计正确的支持，以同时测量rescue与新增false OPEN。任务书第33节要求对这批冻结后的准确数量重新授权。授权范围仅E1A，后续阶段不在其范围内。
