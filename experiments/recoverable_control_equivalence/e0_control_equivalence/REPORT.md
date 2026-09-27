# E0：Control-Equivalent Reanalysis + Recoverability Audit

## Material Passport

来源：skeleton-state-alignment @ dd442dd；27 natural states / 10 qids / 108 historical responses。E0 新模型调用0。历史数据已暴露；此处是新问题的回顾性分析，不是独立确认实验。统计单位明确区分 response、requirement node、qid、eligible transition。

## 主结果：Runtime A1 E0 PASS

| 指标 | A0 Oracle（诊断） | A1 D2（主评价） |
|---|---:|---:|
| 三分类节点正确率 | 298/322 (92.55%) | 248/264 (93.94%) |
| 二分类节点正确率 | 315/322 (97.83%) | 261/264 (98.86%) |
| Exact 3-way Mask | 38/54 (70.37%) | 42/54 (77.78%) |
| Exact Binary Mask | 47/54 (87.04%) | 51/54 (94.44%) |
| OPEN Recall | 271/278 (97.48%) | 225/228 (98.68%) |
| OPEN Precision | 271/271 (100.00%) | 225/225 (100.00%) |
| Closure Precision | 44/51 (86.27%) | 36/39 (92.31%) |
| False Close Rate | 7/278 (2.52%) | 3/228 (1.32%) |
| False Empty OpenSet | 0/54 (0.00%) | 0/54 (0.00%) |
| Potential False STOP Hazard | 0/54 (0.00%) | 0/54 (0.00%) |
| Lost All Acceptable Frontier | N/A | 0/50 (0.00%) |
| Still Has Recovery Frontier | N/A | 3/3 (100.00%) |
| Source Schema | 54/54 (100.00%) | 54/54 (100.00%) |

两臂 Exact Binary Mask 都比旧 Exact 3-way 高 **16.67个百分点**。A0：24个三分类节点错误→7个二分类错误，折叠17个U/P错误；A1：16→3，折叠13个。合计40→10，30/40（75%）错误在本控制抽象下消失。剩下10个全是 False Close，False Open为0。每臂另有9个 response 从三分类不完全正确变为二分类完全正确。

旧实验 **A0 FAIL / A1 PASS / Joint FAIL / E2 NOT RUN** 原样成立。本次PASS指新任务书中以A1为主的二分类门槛；未反向修改任何阈值或历史结论。

## 非空 Claims（每臂34 responses）

| 指标 | A0 Oracle（诊断） | A1 D2（主评价） |
|---|---:|---:|
| 三分类节点正确率 | 180/204 (88.24%) | 152/168 (90.48%) |
| 二分类节点正确率 | 197/204 (96.57%) | 165/168 (98.21%) |
| Exact 3-way Mask | 18/34 (52.94%) | 22/34 (64.71%) |
| Exact Binary Mask | 27/34 (79.41%) | 31/34 (91.18%) |
| OPEN Recall | 153/160 (95.62%) | 129/132 (97.73%) |
| OPEN Precision | 153/153 (100.00%) | 129/129 (100.00%) |
| Closure Precision | 44/51 (86.27%) | 36/39 (92.31%) |
| False Close Rate | 7/160 (4.38%) | 3/132 (2.27%) |
| False Empty OpenSet | 0/34 (0.00%) | 0/34 (0.00%) |
| Potential False STOP Hazard | 0/34 (0.00%) | 0/34 (0.00%) |
| Lost All Acceptable Frontier | N/A | 0/32 (0.00%) |
| Still Has Recovery Frontier | N/A | 3/3 (100.00%) |
| Source Schema | 34/34 (100.00%) | 34/34 (100.00%) |

10个空Claims状态每臂20/20 exact。非空Claims下A1二分类exact仍为31/34（91.18%），OPEN recall129/132（97.73%）。因此整体正向信号不完全依赖空状态，但数据仍是小型且已暴露的历史bank。

## Frontier / absorbing risk

- A1三个false-close response全部保留其它acceptable OPEN ID：3/3。G18两replicate丢失R4，但R1/R3仍可选；G21 replicate2丢失R2，但R3/R4仍可选。
- Lost-all-acceptable为0/50。分母只含冻结参考存在至少一个acceptable ID的response；全54个response中事件数同样为0。
- G04/G05两状态、各两replicate共4/54是既有 `representation_addressability_limit`。它们不是被Alignment误关的frontier；它们仍不允许STOP，并继续进入Selection总分母。
- 三个false-close response的互斥类别都是A（仍有acceptable frontier）；B/C/D均0。这只说明有可选研究机会，不能证明该机会会提供修复被误关节点的新证据。
- A0没有冻结的Oracle-ID selection reference；不能将D2的R#按编号移植。A0的acceptable-frontier和A/B/C表记为N/A，而非伪造0。两臂Gold/predicted OPEN集合均完整保存，可确认A0也没有空OpenSet。
- 未执行Selector，所以这里是潜在STOP条件，不是观测到的STOP动作。该bank没有Gold全CLOSED正控，无法评价正确STOP能力。

## Temporal recoverability

| 指标 | A0 | A1 |
|---|---:|---:|
| Natural false-close节点事件 | 7 | 3 |
| 有eligible successor的prior false-close | 2 | 0 |
| recovered_open | 0 | 0 |
| became_justified | 0 | 0 |
| persistent_false_close transition | 2 | 0（无可评估transition） |
| reopened_incorrectly | 0 | 0 |
| right-censored | 5 | 3 |
| Safe Resolution Rate | 0/2（0%，仅描述） | 0/0（N/A） |
| 最大观测连续false-close状态数 | 2 | 1（右删失） |
| Median recovery steps | N/A | N/A |

两臂均为 `INSUFFICIENT_NATURAL_DENOMINATOR`。原冻结15条literal Claims-addition边被完整复用；G05→G06、G17→G18继续排除，未跨越跳到更远状态。A0 q922的G26→G27在两个replicate均持续误关；不是两个独立问题。A1的3个false close都位于末端，既不能说已恢复，也不能说会永远持续。没有观察到recovered_open或became_justified。

即使历史后续状态存在，也属于外生历史Claims演进；本轮不证明被误关后的实际Agent仍会走到该后续状态。因此 **E0 PASS不等于recoverability已证明**。A1分母0时，任务书允许进入Selection，不启用>=4才适用的75%恢复门槛。

## qid / replicate 分层

完整分母及所有主指标：METRICS.json的arms.*.strata。下面列出二分类accuracy / exact / closure：

| Arm | qid | Binary node | Exact binary | Closure precision |
|---|---|---:|---:|---:|
| A0 | 122 | 10/10 (100.00%) | 2/2 (100.00%) | N/A |
| A0 | 1259 | 36/36 (100.00%) | 6/6 (100.00%) | 14/14 (100.00%) |
| A0 | 169 | 36/36 (100.00%) | 6/6 (100.00%) | N/A |
| A0 | 228 | 36/36 (100.00%) | 6/6 (100.00%) | 2/2 (100.00%) |
| A0 | 261 | 42/42 (100.00%) | 6/6 (100.00%) | 8/8 (100.00%) |
| A0 | 538 | 24/24 (100.00%) | 4/4 (100.00%) | N/A |
| A0 | 637 | 40/42 (95.24%) | 4/6 (66.67%) | 8/10 (80.00%) |
| A0 | 843 | 29/30 (96.67%) | 5/6 (83.33%) | 4/5 (80.00%) |
| A0 | 922 | 26/30 (86.67%) | 2/6 (33.33%) | 4/8 (50.00%) |
| A0 | 971 | 36/36 (100.00%) | 6/6 (100.00%) | 4/4 (100.00%) |
| A1 | 122 | 8/8 (100.00%) | 2/2 (100.00%) | N/A |
| A1 | 1259 | 36/36 (100.00%) | 6/6 (100.00%) | 14/14 (100.00%) |
| A1 | 169 | 24/24 (100.00%) | 6/6 (100.00%) | N/A |
| A1 | 228 | 24/24 (100.00%) | 6/6 (100.00%) | N/A |
| A1 | 261 | 36/36 (100.00%) | 6/6 (100.00%) | 6/6 (100.00%) |
| A1 | 538 | 16/16 (100.00%) | 4/4 (100.00%) | N/A |
| A1 | 637 | 28/30 (93.33%) | 4/6 (66.67%) | 4/6 (66.67%) |
| A1 | 843 | 29/30 (96.67%) | 5/6 (83.33%) | 4/5 (80.00%) |
| A1 | 922 | 24/24 (100.00%) | 6/6 (100.00%) | 4/4 (100.00%) |
| A1 | 971 | 36/36 (100.00%) | 6/6 (100.00%) | 4/4 (100.00%) |

| Arm | replicate | Binary node | Exact binary | Closure precision |
|---|---|---:|---:|---:|
| A0 | 1 | 158/161 (98.14%) | 24/27 (88.89%) | 22/25 (88.00%) |
| A0 | 2 | 157/161 (97.52%) | 23/27 (85.19%) | 22/26 (84.62%) |
| A1 | 1 | 131/132 (99.24%) | 26/27 (96.30%) | 18/19 (94.74%) |
| A1 | 2 | 130/132 (98.48%) | 25/27 (92.59%) | 18/20 (90.00%) |

## 敏感性与边界

Leave-one-qid-out（仅描述）9/10保持A1门槛通过；去掉q1259时Closure Precision变为22/25 (88.00%)，低于90%。主门槛仍按冻结全bank计算；这表明闭合精度依赖题目构成，不能把PASS理解成普遍可靠性保证。不存在多次抽样挑最好replicate。

D2 direct+coherent addressability仍为16/27（59.26%），subnode-only为11/27（40.74%）。Binary状态更好不证明表示更细致或更适合局部控制。G04/G05保留，下一步Selection最高25/27=92.59%。

## 阶段结论

Control-equivalent projection qualified for Active-ID Selection on this exposed development bank.

可以按新任务书进入E1准备；Selection及真实纠错能力尚未验证。E1 paid108需TASK46要求的新授权。旧授权不继承；此处没有新增API支出。
