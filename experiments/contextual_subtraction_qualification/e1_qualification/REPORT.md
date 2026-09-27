# E1 — Contextual Subtraction Qualification

## 决定

**FAIL。停止 E2/E3。** Q1 的完整上下文改善了部分 governing-relation 判断，但没有达到可安全用于 subtraction 的资格门槛。

本结论使用调用前冻结的 Gold 与门槛。129组相同内容/输出的语义复核覆盖全部192条输出，复核封存并提交后才解盲计分。语义说明不参与重标 Gold。

## 设计与实际执行

- 复用24个 Parent–State cells、16个自然历史 snapshots、9个 qids。
- 48个 Certificate：22正例，26负例；负例含15 binding missing、6 qualifier incomplete、5 background/irrelevant。
- Q0只收到 locator 和选定 Claims；Q1额外收到 Original Q、完整 Parent，并使用任务书原定 contextual prompt。两组都只用同一个选定 ClaimSet。
- 每组48 × 2重复 = 96请求，共192。没有 majority vote、择优或丢弃重复。
- DeepSeek `deepseek-flash`，temperature0，JSON mode，最多8并发，retries0；所有请求均正常返回且格式有效。
- E1只有资格判断，没有执行 subtraction、Parent closure 或后续工具。

Q0/Q1同时改变上下文可见性及解释指令，因而估计的是任务规定的整个干预包；不能把差异全部归因于单独增加 Parent 文本。

## Primary metrics

| 指标 | Q0 | Q1 | Q1门槛 | 结果 |
|---|---:|---:|---:|---|
| Precision | 44/54 = 81.48% | 32/35 = 91.43% | ≥97% | FAIL |
| Recall | 44/44 = 100% | 32/44 = 72.73% | ≥90% | FAIL |
| Hard-negative rejection | 42/52 = 80.77% | 49/52 = 94.23% | 描述性 | 改善 |
| Hard-negative false acceptance | 10/52 = 19.23% | 3/52 = 5.77% | 描述性 | 下降 |
| Binding-missing false acceptance | 10/30 = 33.33% | 3/30 = 10% | ≤3% | FAIL |
| Qualifier-incomplete false acceptance | 0/12 | 0/12 | ≤5% | PASS |
| Euler false acceptance | 2/2 | 0/2 | 0次 | PASS |
| Book→article负例 false acceptance | 2/4 | 1/4 | 0次 | FAIL |
| False-full-risk acceptance | 4/26 | 2/26 | 0次 | FAIL |
| Schema validity | 96/96 | 96/96 | ≥95% | PASS |
| Replicate verdict agreement | 48/48 = 100% | 41/48 = 85.42% | 描述性 | 下降 |
| Exact reference verdict | 86/96 = 89.58% | 81/96 = 84.38% | 描述性 | 下降 |

Book→article门槛分母4包括book-only两次和article-only两次；其中核心 **book-only误接受是Q0 2/2、Q1 1/2**。避免把1/4理解为book-only错误率。

Precision比较通过：91.43% ≥81.48%。Recall比较失败：72.73% <100%−5pp。全部门槛须同时满足，因此没有进入E2的资格。

False-full-risk是调用前标注的13个负例上的接受风险。Q1两次均来自孤立的`that paper`表格Claim。它们是潜在覆盖风险，**并非实际运行Residual后出现两次FULLY_SUPPORTED**。

## 配对变化与错误机制

按同一Certificate、同一replicate比较96对结果：74对两组都正确，7对Q1修正Q0错误，12对Q1新增错误，3对两组都错。7次改进全部是负例拒绝；12次退步全部是正例漏接受。

Q1的3次误接受：

1. `A03_CAND3`两次：单独C5中的`that paper`没有提供前文锚点，仍被接受。这是调用前已声明的指代歧义。
2. `A13_CAND1`一次：只有book publication而无后续article，仍把`publishing the book`作为可减去片段。此项不依赖表格指代歧义。

Q1的12次漏接受：

- 6次要求先确定最终目标论文：两种coauthor Certificate各2次，两种有绑定的table Certificate各1次。
- 2次将country/history绑定要求带入任务指定为正例的C7临床局部条件。
- 2次将religion/technology等具体条件带入一般mechanics-change片段；该参考边界预先声明为歧义。
- 1次要求精确到日的六年间隔，而冻结参考使用出版年份；预先声明为歧义。
- 1次要求明确的King Michael–Romania统治关系；所选两条Claim确实没有显式写明，属于复核后发现的参考边界争议。

错误taxonomy：Q0为10次`semantic_binding_missing`；Q1为3次`semantic_binding_missing`、1次`qualifier_or_scope_missing`、11次`other`。`other`细分为10次把局部资格扩大为更多全局条件、1次作者国家绑定争议；不将这些统一称作binding false promotion。

有些模型拒绝理由在全局层面是合理的。例如D10观察到5张表，而问题要求6张表。它没有编造这个冲突。冻结Gold允许在候选分支上确认局部条件；模型有时改用“已证明是最终目标”的标准。本实验测到了这个控制契约的不一致，不能把全部漏接受都解释为模型不理解事实。

## 重复与分层

| 重复 | Q0 Precision / Recall | Q1 Precision / Recall |
|---|---:|---:|
| r1 | 22/27 = 81.48% / 22/22 = 100% | 15/16 = 93.75% / 15/22 = 68.18% |
| r2 | 22/27 = 81.48% / 22/22 = 100% | 17/19 = 89.47% / 17/22 = 77.27% |

Q1有7/48个Certificate在两次重复间改变verdict。temperature0并未保证一致性。这里保留两次观察，不做投票或择优。

| qid | 每组请求数 | Q0 TP / FP / FN | Q1 TP / FP / FN |
|---|---:|---:|---:|
| 1259 | 8 | 4 / 2 / 0 | 4 / 0 / 0 |
| 169 | 6 | 0 / 0 / 0 | 0 / 0 / 0 |
| 228 | 14 | 2 / 2 / 0 | 2 / 0 / 0 |
| 261 | 14 | 8 / 2 / 0 | 2 / 2 / 6 |
| 538 | 2 | 0 / 2 / 0 | 0 / 0 / 0 |
| 637 | 12 | 6 / 0 / 0 | 4 / 0 / 2 |
| 843 | 22 | 14 / 0 / 0 | 12 / 0 / 2 |
| 922 | 6 | 4 / 0 / 0 | 3 / 0 / 1 |
| 971 | 12 | 6 / 2 / 0 | 5 / 1 / 1 |

有些qid没有正例，Precision/Recall零分母在机器文件中为null，不能报成0%或100%。分层为描述性结果，不代表9个等权独立试验。全部Certificate结果见[DIAGNOSTICS](../analysis/DIAGNOSTICS.json)。

## 歧义敏感性

| 参考集合 | Q0 Precision / Recall | Q1 Precision / Recall | 解释 |
|---|---:|---:|---|
| 全部48个，primary | 81.48% / 100% | 91.43% / 72.73% | 正式FAIL |
| 排除调用前声明的3个歧义Certificate | 40/48 = 83.33% / 40/40 = 100% | 31/32 = 96.875% / 31/40 = 77.50% | 仍FAIL |
| 再排除复核发现的`A24_CAND2` | 38/46 = 82.61% / 38/38 = 100% | 30/31 = 96.77% / 30/38 = 78.95% | 事后敏感性，仍FAIL |

第一次排除后Q1 false-full-risk为0/24，但book-only误接受仍存在，binding false acceptance=1/28=3.57%，Recall仍低。96.875%精度不可四舍五入成达到97%门槛。

这些排除都不替换primary结果；没有重标或删除原始实验记录。候选论文是否必须先证明最终身份这一更广的语义选择，仍是参考政策局限，不能由这两次敏感性分析彻底消除。

## 调用与缓存

| 项目 | 实际值 |
|---|---:|
| 发送 / 返回 / 有效 | 192 / 192 / 192 |
| HTTP、格式、超时、重试失败 | 全部0 |
| 峰值并发 | 8 |
| 批次耗时 | 126.41秒 |
| 中位 / p95 / 最大延迟 | 1.95 / 23.34 / 49.17秒 |
| Input tokens | 115,146 |
| Output tokens | 176,433 |
| 其中reported reasoning tokens | 168,717 |
| Total tokens | 291,579 |
| Cache hit / miss tokens | 64,379 / 50,767 |
| 加权缓存命中率 | **55.91%** |

命中率为sum(hit)/sum(input)，usage覆盖192/192，hit+miss与input一致。reasoning是output子集，不重复计费量相加；审核未使用provider reasoning内容。未核实货币单价，金额保留null。

## 限制与后续决定

这是熟悉历史bank上的机制诊断；48个Certificate来自9个问题，多个locator/ClaimSet重用同一观察。没有fresh generalization、独立评审者一致性或大样本置信声明。输出掩码不能完全遮蔽模型是否看过上下文。

E1测量的是Certificate资格，历史S0/S1测量的是Claim角色/支持集合，不能直接把两轮Precision拼在同一排行榜。E1也没有测量proposer recall、cascade support或Residual质量。

**E2/E3调用0；各项下游机制指标未测量。** 当前结果支持继续研究“必要语义依赖与独立未解条件的边界”，不足以让这个Q1 verifier获得实际subtraction控制权。
