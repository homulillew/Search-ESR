# Explicit Research State → Research Frontier：结论

## 结论先行

**F1 未通过；当前结果不足以把 Explicit State 视为已合格的独立 Frontier 控制表示。** 24 个真实归档 checkpoint、10 个 qid、144 次独立调用：H18/48（37.5%），S18/48（37.5%），SH19/48（39.6%）。S 与 SH 总体差距仅2.08pp，但绝对质量远低于85%，并命中预注册的关键失败条件。F2–F4 不执行。

State 的输入压缩是明确的：相对 H 少84.80%，相对 SH 少85.72%。但不能据此宣布“推理更简单”：S 的 reasoning-token proxy 比 H **多13.31%**，平均延迟也更高。三组大量共同失败，主要是过早 STOP、过宽的 Need 和未验证前提。**这是 Frontier/停止判断尚未合格的结果，不是增加 State 字段的证据。**

唯一一次 A 类有界探索在9个失败条件筛选的checkpoint上追加18次新调用：过宽6/9→3/9，有效0/9→3/9，但关键前提错误4/9→5/9。它提供局部收窄信号，未满足“关键错误不增加”的预声明要求；不能改写主门槛。详见 [exploration/RESULTS.md](exploration/RESULTS.md)。

## 实验边界

- 同一 checkpoint 的 H/S/SH 使用同一提示、模型、机械上下文和合同；唯一主干预是信息视图。每组两次独立提交，全部计入分母，不选优、不重试、不执行工具。
- 所有 Requirement Map、State/History/Combined coverage、判分规则与144请求先冻结并提交。Requirement Map 从未进入生产请求。ACT 按实际视图做 masked single-reviewer 语义审核；STOP 机械应用预先人工审核的 closure 标签。
- reviewer 可从输入格式推断 treatment，所以这不是完全盲评或独立多审核员结果。相同 qid 的 checkpoint/replicate 有关联，不作 IID 显著性宣称。
- History 是**完整归档 replay episode**，从当时真实暴露的 seed source 开始；更早的祖先研究时序不能完整恢复。State 是实际归档 State，包含历史 reviewer-normalized 起点和旧 Writer 后续 Claims。没有清洗或补写，但它也**不是新 U1 产生的 fresh minimal-State cohort**。
- 主 closure 要求原问题的实质条件与最终关系共同成立。模型可能凭强身份线索就给出正确的最终名称，但这不自动满足本轮研究状态充分性标准。该标准影响绝对有效率；没有事后放宽。唯一预注册的 F24 身份+直接关系敏感性，使 H/S/SH 分别变为20/48、20/48、21/48，仍远未合格。

## 主要结果

| 指标 | H | S | SH |
|---|---:|---:|---:|
| 有效决策（含正确 STOP） |18/48|18/48|19/48|
| 有效 ACT / 全部 ACT |10/23|14/27|11/26|
| 正确 STOP / 全部 STOP |8/24|4/21|8/21|
| 过早 STOP |16/48|17/48|13/48|
| unsupported premise |7/48|9/48|7/48|
| Need 过宽 |9/48|6/48|11/48|
| stale / goal drift / missed STOP |0/0/0|0/0/0|0/0/0|
| 长度失败 |1|0|1|

错误标记可以重叠，不能把每列标记相加当作独立失败数。142个响应满足本地结构合同；2个响应 `finish_reason=length`，均保留。两个长度失败位于F22（q311）的H和SH，provider报告65536completion/reasoning tokens；不是超长History引起的输入截断。HTTP timeout240s限制网络操作等待，实际整次墙钟可更长（约263/265s）；没有重试或调整预算。

### 关键失败门槛的含义

S关键失败且SH两次均有效的4个checkpoint：F06(q311)、F13(q546)、F15/F16(q580)。跨3qid，触发预注册条件。

- **F06：行为不同。** S两次STOP；SH两次检验仍缺失的角色组合。两边本来都没有充分的角色证据，因此这可能是呈现/显著性与整合效应；不能只凭两次采样定位某个唯一缺失字段。
- **F13：一个replicate的前提错误。** S一次加入没有可见截止日计数依据的JohnHiggins从句，另一次有效；SH两次均为合理赛程检验。这里不是稳定的两次S失败。
- **F15/F16：输出相同、可见依据不同。** S和SH都STOP；SH有五季的原始证据，S的Claims没有总季数。它们是视图相对的合法性差异，**不是看到History后Actor改变动作**。两例同属q580，也不是两个独立问题的复现。

所以既不能用总率“37.5≈39.6”宣告充分，也不能把4个标签修复都称为4次行为因果修复。原始门槛保持失败，机制解释保留这些差异。

### 输入、reasoning proxy、延迟与缓存

| 指标 | H | S | SH |
|---|---:|---:|---:|
| input tokens 总计 |244214|37128|259934|
| input / call 均值 |5087.8|773.5|5415.3|
| output tokens 总计（含reasoning） |383763|434453|398596|
| reasoning tokens 总计 |381945|432768|396576|
| reasoning / call 中位数 |4055|4231.5|4308|
| elapsed / call 均值秒 |36.65|42.77|39.07|
| elapsed / call 中位数秒 |20.44|20.92|22.06|
| prompt-cache token命中率 |52.9%|53.8%|53.3%|

F1总缓存命中率 **287608/541276=53.14%**。reasoning只称inference-burden proxy，不等于真实认知负担；output含reasoning，二者不可相加重复计费。并发、缓存暖化、网络和长尾影响墙钟；没有预注册价格，因此不估计金额。

## 对任务书30个问题的回答

1. **H有效率？** 18/48，37.5%。
2. **S？** 18/48，37.5%。
3. **SH？** 19/48，39.6%。
4. **S接近SH吗？** 总率差2.08pp，接近；绝对质量和关键失败门槛均不合格，不能称充分。
5. **已有State后History额外价值？** 本归档episode比较净增1/48有效决策；四个关键checkpoint的标签差异如上。存在可见但未持久化的证据价值，也存在呈现/采样效应。完整祖先History的增益未测量。
6. **减少stale？** 三组均0/48，不能主张减少；大量过早STOP使“少重复”并非成功信号。
7. **减少drift？** 三组严格goal-drift均0/48；unsupported premise和过宽Need另计，不能混称drift。
8. **减少premature STOP？** 没有，H16、S17、SH13。
9. **减少unsupported premise？** 没有，H7、S9、SH7。
10. **长History显著伤害H？** 无此证据。H四分位有效数为4/12、2/12、7/12、5/12，不单调；qid/阶段/closure混杂，不作显著性结论。
11. **S对History长度更稳健？** 未支持。对应有效数7/12、4/12、2/12、5/12；也无单调优势。它没有读取History，但不同组的任务难度仍不同。
12. **input差距？** S相对H减少84.80%，相对SH减少85.72%；均值见表。
13. **reasoning proxy差距？** S比H增加13.31%，比SH增加9.13%；没有证明压缩降低推理负担。中位数差异较小，长尾明显。
14. **replicate稳定性？** H/S/SH两次同一有效requirement或正确STOP：7/24、7/24、8/24；一对中仅一个有效：4/24、4/24、3/24；两次均无效各13/24。未观察到“不同但都有效”的requirement对。宽复合R可能含不同子事实，已保存窄focus供检查。
15. **S重新激活deferred requirement？** 6个有完整requirement遗漏机会的S调用中观察到0次；另有子关系机会也未观察到有效重激活。q546选择另一个未决赛程是允许的，不能算长期遗漏；q580四次STOP确实没有请求缺失总季数。无工具恢复链证据。
16. **Belief mutation后及时切换？** F2未执行，未测量。静态早/晚checkpoint不能冒充受控transition结果。
17. **contradiction后停止旧候选路径？** 部分输出绕开已冲突的Heart/Hijitus，转向别的约束；但也出现未经验证的新国家/电视台/比赛前提和整题重述。不能宣称可靠的动态pivot，F2仍未测量。
18. **closure后正确STOP？** 所有按各自可见信息完整的视图都STOP：H8/8、S4/4、SH8/8；missedSTOP为0。与此同时不完整视图大量STOP，说明不能只用已完成控制组来评价停止能力。
19. **Persistent Gap导致更多stale？** F3未运行，未测量；本轮未操纵旧Gap。
20. **Direct Replan足够？** 当前直接Frontier生成未达到质量门槛；没有P/D/R比较，不能选定最终Controller。
21. **Goal Residual提升reactivation？** 未测量。
22. **值得多一个Reviewer调用？** 未测量；不能由本轮失败直接推出mandatory Reviewer。
23. **F4自主Need reactivation成功率？** 未运行，未测量，不写0%。
24. **正确Need后Search recovery稳定？** 本轮没有检索，未测量；历史供应Need的结果不能替代自主链条。
25. **Evidence后U1重新形成Claim？** 本轮未执行Writer，未测量。
26. **dominant failure层？** 本轮可测部分以STOP/Need generation为主；候选/日期/事件前提提升也明显。State遗漏在季数等例子中可见，但H和SH也普遍失败。Retrieval和Admission未测试，不能归责它们。
27. **最小Persistent State仍可保持Q+Claims+Hypothesis？** 可以继续作为简洁架构候选；尚未获得决策充分性资格。没有根据本轮结果增加ontology/持久字段，Hypothesis是否应删除也未单独干预。
28. **Need仍应ephemeral？** 维持当前设计合理；本轮不能证明persistentGap更差。Need是当前控制输出，不能因失败就存成长期Plan。
29. **需要mandatory Goal Reviewer？** 未证明。优先明确证据充分性与STOP判定，再做已授权阶段的因果比较；不自动加组件。
30. **可以进入最终大规模G4/G5 validation？** 不可以据本轮宣告机制就绪。F1门槛失败，F2–F4尚未合格。

## 下一步的研究含义

当前应先解决：在保留强候选、最终关系已经可猜的情况下，Frontier如何识别仍未被证据覆盖的必要条件，并在这些条件上选择一个有用的问题。其次是候选前提和时间/角色范围的忠实表达。不能把目标简化成“多生成Need”或“少STOP”，也不能因为输入变短就称系统已经学会可靠地从Belief产生Need。

本轮没有改Search/Find/Open、Retriever、localizer、U1、Claim/Hypothesis schema、Workspace、corpus；没有增加任何persistent字段。所有失败、原始请求和输出保留；历史实验完整性检查见 [analysis/INTEGRITY.json](analysis/INTEGRITY.json)。

## 执行汇总

共162次真实模型提交（F1 144 + 唯一探索18），0次工具调用，0次Writer调用，0次重试。F1缓存53.14%，探索50.01%，全轮缓存327800/621644=52.73%。探索的A0/A1缓存暖化明显不对称，不能用其延迟作干净的推理难度比较。完整逐例、逐qid、History四分位与成本文件位于analysis/；所有未进入阶段均写明未测量。
