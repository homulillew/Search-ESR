# E1 Active Requirement ID Selection — FAIL

## Material Passport

108 frozen calls =27 states×S0/S1×2，DeepSeek deepseek-flash。所有尝试保留，单次完成要求，零重试；仅Q/Skeleton/二分类Mask输入。单个熟悉历史bank的Codex reviewer，18种可见输入分组，108份独立记录的first-pass judgments（非108独立评审）；提交后揭盲。主评分完全继承旧冻结selection reference。

| 指标 | S0 Gold Control Mask | S1 Model Control Mask |
|---|---:|---:|
| Valid Selection | 41/54 (75.93%) | 40/54 (74.07%) |
| Selected Gold CLOSED | 0/54 (0.00%) | 0/54 (0.00%) |
| Selected Input CLOSED | 0/54 (0.00%) | 0/54 (0.00%) |
| Downstream Selection | 0/54 (0.00%) | 0/54 (0.00%) |
| False STOP | 0/54 (0.00%) | 0/54 (0.00%) |
| Input-Mask False STOP | 0/54 (0.00%) | 0/54 (0.00%) |
| Valid schema/completion | 52/54 (96.30%) | 52/54 (96.30%) |

S0有效选择75.93%<85%；S1有效选择74.07%<80%。其它门槛均过。SelectionLoss=S0−S1=1/54=**1.85个百分点**，低于10pp限制，但不能替代两个绝对门槛。**E1 Joint FAIL，停止。**

零违规动作率包含所有54planned slots；4次length（每臂2次）仍计入总分母，是没有可用动作，不是合法选择。仅看完成响应，S0 41/52=78.85%、S1 40/52=76.92%，也不足以解释为长度失败单独造成主失败；这些条件率仅描述，主门槛不变。没有Gold合法STOP正控，因此未测正确停止能力。

## 失败分解（不删任何case）

| 来源 | S0失败数 | S1失败数 | 说明 |
|---|---:|---:|---|
| q228 G04/G05 | 4 | 4 | 冻结D2表示无合法单ID；选择R1。继续保留分母。 |
| q228 G06 | 2 | 2 | 有合法R2但仍选复合R1。 |
| q637 G16/G17 | 4 | 4 | 选R3，把国家/宗教历史与临床史合成当前目标。 |
| q122 G15 | 1 | 2 | 选R2，把出生人物条件与城镇人口条件捆在一起；S0另一rep选择合法R3。 |
| q169 G07/G08/G09 length | 2 | 2 | 每次completion65536；无可用selection。 |
| 合计 | 13 | 14 | 全部保留，未补样、未repair。 |

## Addressability strata

| 历史D2地址能力 | S0 valid | S1 valid |
|---|---:|---:|
| directly_addressable | 23/24 (95.83%) | 24/24 (100.00%) |
| coherently_multi_addressable | 7/8 (87.50%) | 8/8 (100.00%) |
| subnode_only | 11/22 (50.00%) | 8/22 (36.36%) |

合并direct+coherent为62/64（96.88%）；subnode-only为19/44（43.18%）。**23个有合法JSON但不合法的ID选择，全部处于subnode-only状态**。27个总体失败中25个落在subnode-only（另2个为其它stratum中的length）。这是有力的描述性集中，不是随机操纵表示粒度后的因果比较；历史addressability标签针对旧GoldO而非对所有可能ID逐一评分。

## 稳定性

| 类别（27 state pairs） | S0 | S1 |
|---|---:|---:|
| same valid ID | 14 | 15 |
| different but both valid | 5 | 5 |
| one valid / one invalid | 3 | 0 |
| both invalid | 5 | 7 |

不同但都valid不判失败；相同但都invalid也不因一致性获益。S0 replicate1/2分别21/27、20/27；S1均20/27。非空Claims状态S0 27/34、S1 26/34；空Claims均14/20。qid、replicate、empty和addressability完整指标见METRICS.json。

## 真正Mask差异与重复输入

S1严格固定旧A1 replicate1，只G18与S0 Mask不同：R4被误关；另外26/27 states输入完全相同。G18两臂四次均选择R3，冻结reference均判valid，展示一次“某节点误关，但另一个可用目标仍被选择”的局部实例；未执行工具或获取纠错证据，不能视为恢复证明。

整体1.85pp loss全部来自输入完全相同的q122：S0一次选R3而S1两次选R2。不能将这1.85pp解释成Alignment误差的因果影响；固定错误Mask的实质对照只有一个状态。

## 盲审与冻结参考分歧

4个分歧全部是G18 R3。仅见二分类Mask的reviewer认为该ID仍捆绑国家条件与临床条件，缺少局部残差信息；冻结参考使用旧Claims知道临床部分已成立，仅国家条件残留，所以记valid。保留全部首轮判断并按冻结reference计分，无调分。分歧说明两个评估口径信息量不同，也暴露二分类Mask不显示“复合节点哪部分仍未解决”；不是独立复审证明。

两个输入碰撞：G04/G05/G06输入完全相同，但acceptable集合分别空/空/{R2}；G10/G11输入相同，G11新增可选R5，仍共享R1/R2/R4。前者包含两例本来不可表示状态，不应外推为所有可表示状态都无解。它说明二分类变化并不总能表达局部残差的变化。

## 执行账目

108/108发送并返回（HTTP200）；104有效、4length；timeout/transport/HTTP errors0，零重试，峰值并发8。4个失败各65536completion tokens，合计262144，约占总completion的37.67%。保留raw响应和usage，未读reasoning解释模型内因。

输入93,656；completion695,973（其中reasoning695,223，已包含）；total789,629。缓存hit66,944、miss26,712，加权命中率**71.48%**。usage108/108完整，hit+miss=input。

壁钟471.29秒；请求latency median6.80秒、P95 177.10秒、max261.40秒。配置240秒是HTTP inactivity timeout，非总wall deadline；不存在把261.4秒完成误记为未遵守总超时的问题。没有新价格核验或货币成本声称。

## 判断与停止

Case B：control-equivalent Alignment通过最低门槛，但正确OpenSet下的Current Frontier Selection仍失败。瓶颈主要与复合D2节点的局部可选性有关；不是多Search/少Find问题，也不是只补一个closure checker可以解决的证据。

下一独立实验可考虑任务书提出的D1-like局部控制节点+D2 source-span authority，并保留相同cases以区分表示粒度与Selector能力；本轮不实现、不调prompt、不新增State。禁止进入Gap/工具/Writer/rollout。
