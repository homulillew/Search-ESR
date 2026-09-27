# Contextual Subtraction Qualification：最终结论

## 本轮回答

**完整上下文能修复部分错误接受，但当前 verifier 尚不能稳定判断“这部分是否可以从 unresolved 中减掉”。E1 FAIL，E2/E3未运行。**

192次真实调用全部完成。Q1 Precision为**32/35=91.43%**，高于Q0的44/54=81.48%；Q1 Recall为**32/44=72.73%**，低于Q0的44/44=100%。7次误接受被修复，同时增加12次漏接受。这个结果有局部机制收益，不能视作合格的subtraction控制器。

## 1. Governing context是否有效？

有效，但收益有边界。Euler错误接受2/2→0/2，alma-mater→building角色错配2/2→0/2，nationality-only→champion membership错误2/2→0/2。说明原来只验证短片段确实会漏掉必要关系。

Book-only→later-article关系仍错误接受1/2，孤立表格指代仍接受2/2。**局部属性脱离governing relation的错误没有被消除。** 两种重复间Q1 verdict一致率仅41/48=85.42%。

## 2. ClaimSet能否建立联合支持？

能在部分例子上做到。加入champion membership后nationality Certificate由拒绝0/2接受变为接受2/2；book+article、DLC+base release均能提供比较两端；Ding绑定+2019婚姻事实保留2/2正例。Binding Claim可以作为联合证据的一部分，不能据此把每个成员都单独升为substantive support。

Table对照不支持稳定的联合绑定能力：孤立指代被接受，加入具名table上下文反而触发一次拒绝。新增上下文同时暴露全局线索冲突，限制了该对照的纯度。

## 3. 保留局部支持与继承必要依赖能否兼得？

当前不能稳定兼得。Ding婚姻和DLC religion/technology正例保持良好，但q637真实C7临床支持只接受4/6；论文共作者、table等局部事实还会被要求先确定最终目标。

主要困难是**确定当前条件真正依赖什么**：必要关系缺失时仍会漏放；独立未解条件尚存时又可能拒绝已成立的候选局部事实。单纯扩大上下文在这两端之间移动，未形成稳定边界。

## 4. 这是否只是Gold争议？

Gold选择确实影响结果，必须公开。冻结政策允许候选分支内的局部支持；某些模型要求先确认最终目标。论文5张表与问题6张表的冲突是真实观察，严格拒绝有语义依据。临床正例、Ding婚姻正例则来自任务明确要求，不能执行后取消。

排除调用前3个歧义Certificate后，Q1 Precision=96.875%、Recall=77.50%，仍FAIL。再排除复核发现的letter作者国家绑定争议后，为96.77%/78.95%，仍FAIL。Book-only误接受和临床漏接受均仍存在。因此失败不只由孤立table标签造成；这些分析也不能彻底解决更广的候选身份契约争议。

## 5. 是否值得进入E2/E3？

本轮门槛不允许。Q1未通过Precision、Recall、binding false acceptance、book→article零误接受、false-full-risk零接受及相对Recall要求。E2单独授权的前提E1 PASS没有满足。

E2候选提议召回、cascade支持精度/召回、E3 strict residual、false subtraction、false FULLY_SUPPORTED、state discrimination均为**未测量**，不能写成0错误或已解决。历史S0/S1原始结果保持不变，未重跑；其Claim-level指标不能直接与本轮Certificate-level指标比较。

因此尚未建立完整的：

`Claims → CandidateEvidence → ContextualQualification → QualifiedSupport → Residual`

因果链。本轮只检验了固定候选的Qualification。

## 6. 后续值得探索什么？

下一步首先需要厘清评估契约：在某候选分支内被证实的条件，何时可记录为局部已支持；哪些关系必须实际被ClaimSet建立；何时“目标已唯一确定”才是必要条件。应让相同原则同时覆盖paper、clinical、Ding、book/article等案例，并保留明确的困难负例。

在新的独立冻结实验中，可以考虑让模型临时表述locator在Parent中的完整依赖，再对该临时语义对象检验entailment，观察能否同时降低关系漏放和范围扩大。这个方向尚未实现、尚未调用API、也没有效果证据。它不要求增加persistent graph或persistent finer Requirement nodes。

当前资格输出仍应作为**待审的ephemeral判断**，不具备自动永久删除unresolved内容的依据。State继续保持Q/R/C/H；没有写入持久Certificate、SupportGraph或RelationDAG。

## 可复核材料

- [完整指标、门槛和敏感性](e1_qualification/REPORT.md)
- [九类bad cases](analysis/CASE_REPORT.md)
- [冻结Gold政策](e0_reference/REFERENCE_POLICY.md)
- [逐项原始结果与语义复核](analysis/DIAGNOSTICS.json)
- [审计](analysis/POST_EXECUTION_AUDIT.md)：20,796个历史实验文件哈希不变，原始响应重解析、计分回放和usage回放一致。

使用DeepSeek `deepseek-flash`，192次请求、最多8并发、零重试，批次耗时126.41秒，缓存命中率**55.91%**。没有检索调用或后续阶段费用。
