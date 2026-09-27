# Minimal Semantic Package / Scoped Partial Evaluation — 最终结论

**E1 FAIL。实验按门槛停在Gold Package Support，E2/E3/E4未运行。**

完成96次Verifier + 35次Auditor，共131次调用。最终Precision **26/29=89.66%**、Recall **26/42=61.90%**。反向审计纠正误支持 **0/3**，新增False OPEN **6次**。这项审计在本次冻结bank上的效果为负；格式有效率100%不能替代语义可靠性。

## 任务书18个问题

1. **Gold Target已知时verifier是否可靠？** 不达到既定要求。Verifier-only为91.43% Precision/76.19% Recall，审计后进一步降至89.66%/61.90%；97%/90%门槛均失败。
2. **主要失败是verifier还是boundary recovery？** 在本轮冻结Gold契约下，验证链已经是前置瓶颈，尚不具备研究extractor的准入条件。但临床`The first case`与候选分支绑定、Book年份粒度仍有契约/表示问题，不能把失败全部归为与参考定义无关的模型推理能力。
3. **Parent+Locator能否恢复最小完整Target？** 未测量。E0构造了34个参考包、17个Parent、78个精确源片段；人工参考构造不是E2模型恢复能力证明。
4. **Under-inheritance是否压住？** 模型提取的under-inheritance未测量。Gold包保留必要关系后Euler与book-only都0/2误支持，只能说明这些具体控制通过。
5. **Over-inheritance是否仍集中于q637/paper/DLC？** E2分布未测量。临床失败单位为first-case，DLC为mechanics/base-game；被排除的country/history/nation未出现在输入，不能据此称为sibling over-inheritance。
6. **Target与interpretive context能否稳定区分？** 证据不足。34个参考包只有2个使用context；本次无context ID被作为gap输出，champion叙述context未阻塞，clinical仍被target角色阻塞。没有独立测试模型包分类稳定性。
7. **Euler是否不再false support？** 本bank中0/2；Verifier保留缺失的书籍引用关系。样本不支持普遍消除此错误。
8. **Book-only是否不再被视为solved relation operand？** 0/2误支持；单独book没有关闭article/六年关系。未测量book能否成为安全Residual binding。
9. **q637是否不再被country/history阻塞？** 两者从输入中移除，未被列为缺口；但临床召回仍0/6，唯一返回缺口是`The first case`。临床事实本身与角色身份判断不能混为一谈。
10. **Ding局部婚姻成立而gift不关闭？** Verifier局部支持2/2，Auditor误拒一次后仅1/2，未达到100%门槛；整个gift Parent保持OPEN 2/2。
11. **Predicted package相比Gold损失多少？** 未测量，E2/E3未运行；差值为null。
12. **已验证Support能否安全改变Residual？** 未测量。当前链还残留3个误支持，不足以授予更新资格。
13. **Book→Article是否完成partial evaluation？** 未运行E4，未生成或删除Residual；没有观察到安全派生ArticleDate的结果。
14. **是否出现False Shrink？** 未测量，不能报0。E1的3/28 false-full-risk是潜在风险，不是实际收缩或False FULLY_SUPPORTED。
15. **是否需要persistent graph？** 本结果没有提供必要性证据；新增持久图不能由这些验证错误推出。
16. **是否需要更细persistent Requirement nodes？** 没有必要性证据。78个源片段只是ephemeral参考，未新增持久节点。
17. **Q/R/C是否仍足够作为persistent semantic state？** 本轮维持Q/R/C、H不用，没有观察证明必须增字段；但因验证未过关，也不能宣称已经证明其对完整闭环充分。
18. **能否进入4–8step dynamic closedloop？** 不能。E1未通过，且任务书第36节即使E4通过也禁止本轮自动进入Search/rollout。

## 可支持的研究判断

必要关系进入Target后，一些危险的operand/identity误提升被拒绝；Gold范围本身仍不能保证正确验证。审计的3个已知误支持全部保留，却将Ding、Book时间关系与DLC关联的6个真支持改成OPEN。不能把多一次确认当作可靠控制状态的充分依据。

更合适的后续问题是：源片段中的角色、年份/时点与候选分支如何获得明确且可检验的支持契约，以及审计是否能定向发现真正未支持的关系。先做独立参考校准、保留未参与调整的新材料，再设计新实验；本轮不改Gold、不放宽门槛、不热修Prompt、不执行该建议。

## 限制与交付

这是9个问题上的相关历史bank、单一熟悉任务的参考作者与复核者，非独立评审；96次Verifier只有46种实际payload。3次误支持均集中在预标歧义证书，排除4个预标歧义证书后Precision100%、Recall68.42%，临床0/6与Ding1/2仍不达标。primary结果保持不变。

全部131次调用正常返回，max_retries=0、峰值并发8；总缓存命中率 **27,644/63,576=43.48%**。原21,632个历史实验文件及所有冻结材料保持原哈希。E2–E4有明确未执行决定及null指标。

详见[E1完整报告](e1_gold_support/REPORT.md)、[机器计分](e1_gold_support/METRICS.json)、[逐链内容复核](analysis/CONTENT_REVIEW.json)、[总调用账本](analysis/TOTAL_ACCOUNTING.json)。早期CURRENT_STATUS/EXECUTION_STATUS/VERIFIER_REPORT是冻结历史快照，最新状态见[FINAL_STATUS](FINAL_STATUS.md)。
