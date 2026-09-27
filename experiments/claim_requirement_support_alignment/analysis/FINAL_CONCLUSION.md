# 最终结论：E1 完成，安全门槛未通过，E2 不执行

## 核心结果

本轮完成已授权的96次 DeepSeek 调用。S1 typed + scope 提高了真支持召回，但未把错误支持压到门槛以内。

| 优先指标 | S0 Binary | S1 Typed + Scope |
|---|---:|---:|
| Support Precision | 27/27 =100% | **35/38 =92.11%**，低于95% |
| Hard-negative false promotion | 0/128 | 3/128 =2.34% |
| Support Recall | 27/36 =75.00% | 35/36 =97.22% |
| False-full assignment hazard | ID-only 输出无法判断 | **2次**，门槛要求0 |
| 实际 False Subtraction | 未测 | 未测 |
| 实际 False FULLY_SUPPORTED | 未测 | 未测 |

错误集中在：Euler biography→target-book reference 的关系缺失、book-only anchor→article relation 的升级，以及 DLC 局部变化→完整 playable-European-nation 条件的范围扩大。最后两类涉及预先声明的歧义参考；排除全部六个歧义单元后，S1 precision仍为21/23=91.30%，仍未过门槛。

按任务书第24节 Case D、第25节及冻结入口规则，**停止进入 E2**。没有发送 E2 请求，也没有进行检索、Writer、Bootstrap 或闭环。

## 对任务书18个问题的回答

1. **能否可靠区分相关性与实质支持？** 当前未达到安全要求。S1 precision92.11%，仍有3条绑定上下文被升级为实质支持。S0在本 bank 未出现错误支持，但 recall仅75%，不能称为完整可靠方案。
2. **False Support 的主要来源？** 不是事实本身虚假，而是遗漏其所需的主导关系或事件绑定：人物属性未建立书中引用；一本书未建立后续文章关系。另有真支持 Claim 的 scope 超出证据所建立的限定条件。
3. **Candidate anchor 是否经常被提升？** S1对56个 Gold binding Claim-slots有3次升级（5.36%），占全部3次 false promotion。样本小且定向采样，不能外推总体频率；Euler两个重复均犯错，book-only一次犯错。
4. **Generic background 是否经常被提升？** 本轮S1背景→支持为0/66；S0也无false promotion。SPS背景未冒充具体病例。背景和binding/irrelevant之间仍不稳定，但这与实质支持误判是不同问题。
5. **Relation argument / temporal / object binding 是否稳定？** 部分典型转移被避免：国籍未变成报告国家，memo日期未变成letter日期，coder国籍未变成队友关系，Kwon/Ding未合并。仍有3/48个输出丢失必要关系/来源绑定，超过3%阈值，不能判定整体稳定。
6. **S1是否优于简单binary？** 有明确召回收益：75%→97.22%；P组11/20→20/20。但precision100%→92.11%，false promotion0→2.34%，因此未证明在本轮最优先的安全目标上更优。两个arm同时改变role分类与scope输出，不能分离各自的作用。
7. **Support scope能否正确定位？** 正确选中的支持Claim中32/35=91.43%，达到局部scope门槛；所有56个输出片段均为字面精确子串。但3个Claim-slots在DLC国家限定上越界，并构成2次全Parent覆盖风险。字面复制正确不等于语义支持正确；该指标也不是完整scope召回率。
8. **Gold typed Support是否足以稳定产生Residual？** 未测。D3属于E2，本轮入口失败，不能从历史研究或本轮E1填补这个结论。
9. **Model typed与Gold typed差多少？** 下游Residual差距未测。E1的已知差别是3次false support、1次missed support及scope/context差异，不能将它们换算成D2−D3表现。
10. **Raw all-Claims与typed packet谁更可靠？** 未测。S0是binary assignment，不是E2的D0 raw residual baseline；不可混同。
11. **False subtraction主要来自alignment还是residualizer？** 实际subtraction未运行，无法做因果归因。当前已定位到足以阻止下游的alignment风险；不能据此声称residualizer已经犯错或一定无错。
12. **是否观察到false-full-support hazard？** 是，A20两个S1重复均将局部机制变化扩成完整国家限定。是assignment的覆盖风险，不是实际FULLY_SUPPORTED或STOP。A20预先标为歧义参考，排除它后hazard消失；precision失败仍存在。
13. **q228/q637 trajectory是否正确区分？** E1层面正确：G05→G06从空支持变为Ding C5，G17→G18从空支持变为临床C7，两个arm各4/4匹配重复的支持集变化正确。E2 Residual State Discrimination未测，不能将E1变化冒充下游收敛证据。
14. **历史bad cases是否重现？** Euler在S1两个重复重现、S0未重现；generic SPS、letter-date、teammate-country在本轮均未重现。国籍/报告国家、alma mater/building、artist/charity也未发生实质支持升级。详见E1报告逐案表。
15. **是否需要新的persistent State field？** 没有本轮证据支持。可见Claim及Parent已足以揭示多数错误；当前失败在支持关系的判断，而非已证实缺少一个长期字段。
16. **是否需要finer persistent Requirement nodes？** 尚无足够证据。D3能力上限未测试，不能把alignment失败直接归因为coarse Parent不能residualize。此次没有新增子节点。
17. **Claims→Support→Residual是否足够可靠？** 尚未成立。第一段未达到安全门槛，第二段本轮未测。P组召回改善是有价值的能力信号，不能替代全链条的安全证据。
18. **是否有资格进入Zero-Support Evidence Bootstrap？** 按本轮注册规则，没有。当前只完成E1并触发安全停止；不自动扩展新的控制路径或付费实验。

## 研究判断与边界

最有用的正向信号是：typed/scoped提示使模型更愿意识别尚未完全成立Parent中的真实部分支持。最关键的负向信号是：相同机制也可能把候选属性从其主导关系中截取出来，误当成可减去的条件。

因此当前应保留的结论是：**支持判断必须同时保留“什么事实成立”和“它通过哪一个已观察的关系属于这个Requirement”。** 本轮尚未证明这些判断有资格直接控制语义减法或关闭任务。后续若另行注册，应先验证这一关系绑定边界；本轮未进行prompt修补、补样或新实验。

限制：24个Parent–State单元、16个自然snapshot、9个qid；两次重复并非独立问题样本；任务定向历史bank；单一熟悉任务的reviewer；输出格式使完全盲法不可能。预标歧义保留在主评分，未事后改标签。总体结论是机制诊断，不是新cohort泛化。

## 执行与完整性

96/96调用返回；8并发；耗时133.03秒；超时0、HTTP错误0、schema failure0、重试0。输入79,812 tokens，输出224,626，总计304,438。DeepSeek缓存命中43,904/79,812 = **55.01%**，全部96条usage完整且一致。

历史20,343文件不变；请求、Gold、prompt、rubric不变；raw响应重新解析、usage核算和封存评分重放一致。E2各项实际结果标为未测，不记为0错误。细节见[阶段报告](../e1_support_alignment/REPORT.md)、[指标](../e1_support_alignment/METRICS.json)、[执行核算](EXECUTION_ACCOUNTING.json)、[实际完整性核验](E1_INTEGRITY.json)。
