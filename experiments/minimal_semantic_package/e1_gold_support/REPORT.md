# E1 — Gold Package Support 最终报告

## 决定

**FAIL；停止E2/E3/E4。** 96次Verifier加35次Auditor均已完成并归档，所有调用合法返回，零重试。参考、Prompt、边界及计分规则保持冻结。

这次反向审计没有修复任何误支持，却拒绝了6个原本正确的支持。它在该冻结bank上的净作用为负；不是仅差一点门槛。

## Primary：所有48个Certificate × 2次重复

| 指标 | Verifier-only | Verifier + Auditor | 最终门槛 |
|---|---:|---:|---|
| TP / FP | 32 / 3 | 26 / 3 | — |
| TN / False OPEN | 51 / 10 | 51 / 16 | — |
| Support Precision（含引用witness） | 32/35 = 91.43% | 26/29 = 89.66% | ≥97%，FAIL |
| Support Recall | 32/42 = 76.19% | 26/42 = 61.90% | ≥90%，FAIL |
| False OPEN rate | 10/42 = 23.81% | 16/42 = 38.10% | 描述性 |
| Euler false support | 0/2 | 0/2 | 0，PASS |
| Book-only false support | 0/2 | 0/2 | 0，PASS |
| False-full-risk | 3/28 | 3/28 | 0，FAIL |
| q637 clinical recall | 0/6 | 0/6 | ≥90%，FAIL |
| Ding marriage recall | 2/2 | 1/2 | 100%，FAIL |
| Schema有效链 | 96/96 | 96/96 | ≥95%，PASS |
| 两次重复最终决定一致 | 45/48 | 45/48 | 描述性 |

Auditor自身schema35/35；无失败链，所有计划slot留在分母。False-full-risk是冻结的14个风险负例各2次的潜在控制风险，**不是E4的False FULLY_SUPPORTED**。没有执行任何Residual。

## 审计的实际净变化

- 35个被审计的Verifier支持：32真支持、3误支持。
- 32真支持中保留26，错误拒绝6；新增False OPEN率 **6/32=18.75%**。
- 3误支持全部放行，rescue **0/3**。
- 最终支持35→29；Precision下降1.77pp，Recall下降14.29pp。
- Verifier原有61个OPEN不能被该审计流程救回。因此最终Recall在审计前已最多76.19%；本次用户授权35次的目的明确为完成机制诊断。

“两次都同意”不能视作独立证据。两个组件使用同一模型，虽然Auditor任务方向不同、只看真实引用子集，但观测到的3个误支持均相关地保留。样本不足以估计通用错误相关系数。

### 新增6次False OPEN

| Certificate / replicate | 审计指出的缺口 | 实际可见材料及解释边界 |
|---|---|---|
| A07_CAND1 r2 | U2 `who, up to 2019,` | C5明示2019文章时已婚无子女；相同审计输入r1接受。 |
| A14_CAND1 r2、A14_CAND2 r2 | U3 `six years after` | C1/C3给2016与2022；按冻结出版年份政策为支持，日期精度解释存在争议。 |
| A20_CAND1 r2 | U3 `of the base game` | C3为DLC–EU4绑定，C4为宗教/技术变化；相同审计输入r1接受。 |
| A20_CAND4 r1/r2 | U3 `of the base game` | C3为绑定，C7为government/subjects变化；一般mechanics参考已预标歧义。 |

这些是输出直接定位的单位。JSON没有原因字段，不能断言内部拒绝理由。尤其DLC审计没有把未输入的European nation当作缺口。

### 保留的3次False Support

`A03_CAND3`两次都用孤立C5（`that paper`无可见前项）被两组件接受；`A24_CAND2 r2`只用C3提到Michael与Romania，也被两组件接受，未证明作者国家绑定。两类在调用前均标记参考歧义；按冻结Gold仍为误支持，不事后重标。

### Verifier原有10次False OPEN

- q637临床6次全部只标U1 `The first case`；症状单位没有列入缺口，country/history从未进入输入。
- DLC technology两次只标U2 `made changes to the mechanics`；C3+C6已按参考覆盖技术重做。
- Book/interval两个r1只标U3六年关系；两个r2随后也被审计拒绝，最终Book+Article时间关系支持0/4。

临床的候选分支支持政策与字面first-case身份要求仍可能冲突。源文本精确切分不能自动证明一个病例已绑定到该角色。因此结果定位到**固定Gold输入下的验证接口/语义契约**，不能声称已排除一切角色表示或参考定义问题。

## 正负控制及完整内容复核

单一、熟悉任务、未掩码的Codex复核覆盖全部96条链：35个实际Auditor子集与61个Verifier OPEN。仅查看Target/Context/Claims和content JSON，不看provider reasoning；此复核在机械计分之后，不能称独立评审或盲审。每条理由与单位检查见[CONTENT_REVIEW](../analysis/CONTENT_REVIEW.json)，实际包见[FINAL_DIAGNOSTICS](../analysis/FINAL_DIAGNOSTICS.json)。

保留的局部支持包括署名4/4、带绑定的表格4/4、book/article同主题2/2、DLC发行/类型6/6、带championship成员证据4/4、带作者国家绑定的letter2/2。Ding1/2，DLC机制正例3/8，临床0/6，六年间隔0/4。

Euler0/2、book-only0/2、DLC nation0/4、generic SPS0/2、generic FOP0/2、患者国籍/报告国家0/2、memo/letter0/2、同国队友0/2、alma-mater/building0/4、nationality-only/champion0/2均无误支持。Ding整体gift Parent两次均OPEN，没有被局部婚姻关闭。

正确OPEN也不保证缺口列表每一项准确：A14_CAND4 r2额外标记已有证据的article U1；A20_CAND6 r2额外标记按绑定政策已有支持的base-game U3；A17_CAND4 r2未指出患者国籍不能证明report-country的U2缺口。主判定仍因其它真实缺口而正确。这些诊断不改Gold和计分。

## 重复及分层

| replicate | TP / FP / False OPEN | Precision | Recall |
|---|---:|---:|---:|
| r1 | 14 / 1 / 7 | 14/15 = 93.33% | 14/21 = 66.67% |
| r2 | 12 / 2 / 9 | 12/14 = 85.71% | 12/21 = 57.14% |

| qid | 计划链 | TP | FP | False OPEN |
|---|---:|---:|---:|---:|
| 1259 | 8 | 4 | 0 | 0 |
| 169 | 6 | 0 | 0 | 0 |
| 228 | 14 | 1 | 0 | 1 |
| 261 | 14 | 8 | 2 | 0 |
| 538 | 2 | 0 | 0 | 0 |
| 637 | 12 | 0 | 0 | 6 |
| 843 | 22 | 9 | 0 | 5 |
| 922 | 6 | 2 | 1 | 0 |
| 971 | 12 | 2 | 0 | 4 |

这是相关的历史机制bank：24 cells、16 snapshots、9 qids、48 certificates；96次Verifier只有46种实际请求payload。Book两个locator、DLC发行两个locator在Gold包后具有相同payload，不是额外独立案例。主要分母未去重。temperature0未保证重复一致；不做投票。

## 歧义与历史参考

预注册4个歧义证书全部保留primary。仅描述性排除后：Precision **26/26=100%**，Recall **26/38=68.42%**，临床仍0/6，Ding仍1/2；不能改判PASS。该排除后审计仍新增3次False OPEN。Book两个实际相同输入均有年份/日期解释风险，但只有A14_CAND2在证书层面预标AMBIGUOUS_REFERENCE；A14_CAND1未事后追加排除。

历史[Q0/Q1原报告](../../contextual_subtraction_qualification/e1_qualification/REPORT.md)原样复用：Q0 Precision44/54=81.48%、Recall44/44=100%；Q1 Precision32/35=91.43%、Recall32/44=72.73%。本轮Gold正例由22变21（A24_CAND2调用前改为OPEN）、输入不再含siblings、加入审计、评分含引用witness。因此这些只是描述性背景，不能把差值归因于单一分割干预，也不能把改变分母称为改善。

## 调用和缓存

| 项目 | Verifier | Auditor | 总计 |
|---|---:|---:|---:|
| 实际调用 / 合法返回 | 96 / 96 | 35 / 35 | 131 / 131 |
| 失败 / 重试 | 0 / 0 | 0 / 0 | 0 / 0 |
| Input tokens | 51,556 | 12,020 | 63,576 |
| Output tokens | 99,924 | 72,884 | 172,808 |
| 其中reported reasoning | 96,799 | 72,516 | 169,315 |
| Total tokens | 151,480 | 84,904 | 236,384 |
| Cache hit / miss | 24,188 / 27,368 | 3,456 / 8,564 | 27,644 / 35,932 |
| Token加权缓存命中率 | 46.92% | 28.75% | **43.48%** |
| 峰值并发 | 8 | 8 | 8 |
| 批次活跃耗时 | 76.36秒 | 62.45秒 | 138.81秒 |

usage完整131/131，hit+miss=input；合计命中率不是两个百分比平均。reasoning为output子集，不重复相加、未用于复核。金额未知保留null；活跃耗时不含准备及等待新授权。E2/E3/E4与检索调用均0。

## 结论

固定范围能保留某些必要关系，Euler/book-only等控制表现符合预期，但整个验证链仍不可靠。额外反向审计在本bank上没有带来安全收益。按照冻结规则停止，不开始package extractor或Residual阶段。后续如另立实验，应先独立校准候选角色绑定与时间粒度契约，并在新冻结材料上同时测rescue与误拒；这只是研究建议，本轮没有改Prompt或追加调用。
