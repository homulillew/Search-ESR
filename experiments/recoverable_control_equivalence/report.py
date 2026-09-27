"""Prepared-stage report: no unexecuted Selection metric is represented as zero."""
from .common import *
def fmt(m):
    return 'N/A' if m['value'] is None else f"{m['numerator']}/{m['denominator']} ({m['value']*100:.2f}%)"
def table(arms):
    names=[('three_way_node_accuracy','三分类节点正确率'),('binary_node_accuracy','二分类节点正确率'),('exact_three_way_mask','Exact 3-way Mask'),('exact_binary_mask','Exact Binary Mask'),('open_requirement_recall','OPEN Recall'),('open_requirement_precision','OPEN Precision'),('closure_precision','Closure Precision'),('false_close_rate','False Close Rate'),('false_empty_open_set','False Empty OpenSet'),('false_stop_hazard','Potential False STOP Hazard'),('lost_all_acceptable_frontier','Lost All Acceptable Frontier'),('still_has_recovery_frontier','Still Has Recovery Frontier'),('schema_validity','Source Schema')]
    return '| 指标 | A0 Oracle（诊断） | A1 D2（主评价） |\n|---|---:|---:|\n'+''.join(f'| {label} | {fmt(arms["A0"][k])} | {fmt(arms["A1"][k])} |\n' for k,label in names)
def main():
    result=read(P/'e0_control_equivalence/METRICS.json');m={a:v['metrics'] for a,v in result['arms'].items()}
    nonempty={a:v['strata']['claims_empty']['False']['metrics'] for a,v in result['arms'].items()}
    report='''# E0：Control-Equivalent Reanalysis + Recoverability Audit

## Material Passport

来源：skeleton-state-alignment @ dd442dd；27 natural states / 10 qids / 108 historical responses。E0 新模型调用0。历史数据已暴露；此处是新问题的回顾性分析，不是独立确认实验。统计单位明确区分 response、requirement node、qid、eligible transition。

## 主结果：Runtime A1 E0 PASS

'''+table(m)+'''
两臂 Exact Binary Mask 都比旧 Exact 3-way 高 **16.67个百分点**。A0：24个三分类节点错误→7个二分类错误，折叠17个U/P错误；A1：16→3，折叠13个。合计40→10，30/40（75%）错误在本控制抽象下消失。剩下10个全是 False Close，False Open为0。每臂另有9个 response 从三分类不完全正确变为二分类完全正确。

旧实验 **A0 FAIL / A1 PASS / Joint FAIL / E2 NOT RUN** 原样成立。本次PASS指新任务书中以A1为主的二分类门槛；未反向修改任何阈值或历史结论。

## 非空 Claims（每臂34 responses）

'''+table(nonempty)+'''
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
'''
    for a,v in result['arms'].items():
        for q,sv in v['strata']['qid'].items():
            x=sv['metrics'];report+=f"| {a} | {q} | {fmt(x['binary_node_accuracy'])} | {fmt(x['exact_binary_mask'])} | {fmt(x['closure_precision'])} |\n"
    report+='\n| Arm | replicate | Binary node | Exact binary | Closure precision |\n|---|---|---:|---:|---:|\n'
    for a,v in result['arms'].items():
        for rep,sv in v['strata']['replicate'].items():
            x=sv['metrics'];report+=f"| {a} | {rep} | {fmt(x['binary_node_accuracy'])} | {fmt(x['exact_binary_mask'])} | {fmt(x['closure_precision'])} |\n"
    sensitivity=read(P/'analysis/SENSITIVITY.json')['leave_one_qid_out']['A1']['1259']['metrics']['closure_precision']
    report+=f'''
## 敏感性与边界

Leave-one-qid-out（仅描述）9/10保持A1门槛通过；去掉q1259时Closure Precision变为{fmt(sensitivity)}，低于90%。主门槛仍按冻结全bank计算；这表明闭合精度依赖题目构成，不能把PASS理解成普遍可靠性保证。不存在多次抽样挑最好replicate。

D2 direct+coherent addressability仍为16/27（59.26%），subnode-only为11/27（40.74%）。Binary状态更好不证明表示更细致或更适合局部控制。G04/G05保留，下一步Selection最高25/27=92.59%。

## 阶段结论

Control-equivalent projection qualified for Active-ID Selection on this exposed development bank.

可以按新任务书进入E1准备；Selection及真实纠错能力尚未验证。E1 paid108需TASK46要求的新授权。旧授权不继承；此处没有新增API支出。
'''
    write(P/'e0_control_equivalence/REPORT.md',report)
    rows=read(P/'e0_control_equivalence/CONTROL_EQUIVALENT_MASKS.json');errors=read(P/'analysis/ERROR_LEDGER.json');ev=read(P/'e0_control_equivalence/RECOVERABILITY.json')['events']
    known={q:{'errors':[e for e in errors if e['qid']==q],'temporal_events':[e for e in ev if e['qid']==q],
        'frontiers':[{k:r[k] for k in ('id','arm','case_id','predicted_open_ids','false_close_ids','remaining_acceptable_ids')} for r in rows if r['qid']==q]} for q in ('922','637','843','169','1259')}
    write(P/'analysis/KNOWN_BAD_CASES.json',known)
    conclusion='''# FINAL_CONCLUSION — E0完成 / E1已准备，待本轮授权

## Material Passport

本报告范围：零调用E0历史重分析，及尚未执行的E1冻结准备。基线dd442dd；27 states、10 qids、108旧输出。E0冻结后执行；E1请求、评分规则、预算和失败策略将在任何真实新调用前提交。没有新Gold、Alignment重采样、工具调用或rollout。

## 结论

**新E0 Runtime A1：PASS。** OPEN/CLOSED投影后，许多细粒度语义错误不改变可研究集合，已达到在这个exposed development bank上进入Active-ID Selection的最低条件。

**尚未证明动态可恢复。** A1的3次False Close全部缺少eligible后续状态。A0已有q922持续误关实例。现在不能授权跳到真实闭环。

**旧实验仍为A0 FAIL / A1 PASS / Joint FAIL / E2 NOT RUN。** 本次重新提出了评价问题，未修旧阈值、旧Gold或旧结果。

'''+table(m)+'''
## 逐一回答任务书20问

1. **多少三分类错误消失？** A0折叠17/24（70.83%）；A1折叠13/16（81.25%）；合计30/40（75%）。没有把这些错误从历史语义指标删除。
2. **Binary Node Accuracy？** A0 315/322=97.83%；A1 261/264=98.86%。
3. **Exact Binary是否更高？** A0 70.37%→87.04%，A1 77.78%→94.44%，各+16.67个百分点。是明显的描述性增幅；未声称统计显著，且是同一已暴露样本的确定性指标投影。
4. **OPEN Recall仍约98%？** 是：A0 97.48%、A1 98.68%；非空Claims分别95.63%、97.73%。
5. **Closure Precision？** A0 44/51=86.27%，A1 36/39=92.31%。它衡量被判CLOSED的风险，分母不同于3/228等False Close Rate，不能互换。A0诊断不足不触发本次新A1门槛。
6. **False close导致empty OpenSet？** 两臂均0/54；不是实测Selector没有STOP。
7. **所有acceptable frontier消失？** A1是0/50；G04/G05无合法ID是既有表示限制，独立4/54。A0无冻结相应ID参考，不能严谨量化这项。
8. **多数False Close仍有其它frontier？** A1全部3/3，有R1/R3或R3/R4。继续研究机会存在，但还没有证据证明能修复具体丢失的requirement。
9. **自然trajectory能否恢复？** 没有观察到恢复。A1可评估分母0；A0 0/2。两者均不足4，保持INSUFFICIENT_NATURAL_DENOMINATOR，不把0/0写成100%。
10. **是否persistent false close？** A0 q922 R1在G26→G27的两replicate均持续，最大观测长度2个状态。A1事件全部末端删失，无法判断持续性。
11. **U→P是否control-neutral？** 对本次只传二分类Mask的路径是：22个U→P及8个P→U都不改变OPEN集合。若未来消费partial引用或更强语义，该错误仍可能有代价；本轮未测试那条路径。
12. **哪些语义错误成为控制错误？** 全部10个剩余错误都是P→F：A0 7、A1 3。日期附件错绑、四年病程提升为四年后起病、American university条件外推，均使未完成节点从OpenSet消失。
13. **D2粗节点是否遮蔽内部错误？** 有结构性风险：q922 R1同时含信件时期、统治者关系、递送人与昵称；缺少昵称可让整体保持OPEN，即使内部日期判断仍错误。观测到D2 OPEN不能证明已纠正日期推理；本输出没有子条件诊断能力。
14. **粗节点实际阻塞Selection？** 还未调用Selector。冻结参考已显示G04/G05没有合法单ID，形成25/27上限；D2 addressability direct+coherent59.26%，subnode-only40.74%。不能在调用前报Selector失败分布。
15. **Gold OpenSet能否选择valid ID？** 未测；S0已冻结54个请求，待本轮授权。
16. **Model相对Gold的Selection loss？** 未测；S1固定A1 replicate1，54个请求已冻结。绝不挑replicate2、修Mask或回退Gold。
17. **Downstream jump仍存在？** 行为未测；冻结blocked/downstream参考保留，之后独立统计。E0其它OPEN节点的存在不自动表示它们都可合法选择。
18. **ID-only是否避免relation rewriting？** 输出契约仅允许selection=现有ID/STOP，从接口上移除自然语言重述通道；仍可能选错节点、选closed、跳prerequisite或STOP，不能预先称行为成功。
19. **False STOP？** E0潜在all-CLOSED hazard0；没有E1动作观测，实际False STOP为NOT_RUN而非0。整个bank也没有Gold合法STOP正控。
20. **够进入4–8步真实rollout吗？** 尚不够。E0通过只支持进入E1；必须S0、S1门槛均过，并为下一独立实验重新预注册，当前明确禁止闭环。

## Known bad cases追踪

| qid | 冻结观测 | 控制解释 |
|---|---|---|
| 922 letter / memorandum | A0 G26、G27的R1两replicate均False Close，2条persistent transition；A1没有节点状态错 | A0错误持续，仍有OPEN节点但无Oracle acceptable参考；D2 G26保留R1/R2/R3，G27保留R1/R2。粗R1仍OPEN不等于日期子条件已修复。 |
| 637 four-year course | G18 A0 R6、A1 R4两replicate均False Close | A1仍有R1/R3 acceptable；无eligible后续状态，不能判已恢复或absorbing。G17→G18原排除边不纳入恢复分母。 |
| 843 Georgetown / American university | G21两臂replicate2的R2 False Close | A1 R3/R4仍acceptable；均末端删失。可见结果不能区分参数知识、问题前提投射或蕴含错误的内部机制。 |
| 169 charity relation | 两臂各2次U→P，均位于R1 | 二分类OpenSet完全不受这些错误影响；A1三个状态的R1/R2/R3始终仍acceptable。 |
| 1259 teammate same-country | A1 G24 replicate2 R4发生U→P | 两replicate的R1/R4均OPEN且acceptable；同国关系仍未获证，未被误关。 |

## 不确定性和敏感性

- 本次只10个qid，state和replicate相关，所有数据历史上已暴露。没有总体置信保证、p-value门槛、fresh bank或最终答案Accuracy结论。
- 非空Claims A1 exact31/34（91.18%）仍高；10个空Claims状态不掩盖全部信号。
- Leave-one-qid-out 9/10保持门槛；去掉q1259后闭合精度低于90%。需要关注任务构成，不据此改主门槛。
- A1三个False Close全部右删失，**可恢复性没有被证明**。A0 q922的持续误关是实证警示，但本任务不引入Verifier、Reaudit或Lazy Reopen。
- A0 frozen selection reference缺失：N/A不等于安全、不等于危险。不能以D2相同编号冒充语义匹配。
- 旧引用贡献争议涉及citation，不修改本轮Gold status；二分类正确也不自动修复source entailment或citation precision。
- 未来CLOSED应是每轮重算的控制判断；持久边界仍为Q/Skeleton、Verified Claims/Hypothesis与机械Workspace/Trace。Mask/OpenSet/ActiveID/Gap保持ephemeral。

## E1执行准备与调用预算

108 calls（27×S0/S1×2），DeepSeek `deepseek-flash`，temperature0，JSON，省略max_tokens，max_retries0，最多8并发。请求只含Q、D2、OPEN/CLOSED Mask；无Claims、历史动作、GoldO或reasoning输入。所有失败留存；一次正式请求兼作canary，不额外采样。

输入估计87,022 tokens（cl100k_base代理，非provider精确计数）。沿用旧Alignment completion分布只作情景估计：总completion约172,908（每次历史中位数）至855,036（每次历史P95）；加输入约259,930或942,058总tokens。这不是Selection实测预测区间或费用上限，ID-only也可能有reasoning开销；reasoning包含在completion内。未核验价格，不编造金额。新缓存命中率未知，实际调用后记录hit/miss及加权率。

当前E0新增paid calls=0，E1 sent=0，无新cache rate。旧实验73.49%不是本轮实际缓存表现。

## 当前停止点

`PREPARED_FOR_E1_EXECUTION`。TASK第46节明确要求本新实验适用的调用授权，禁止自动沿用上一实验的“我授权”。已完成E0、E1 prompt/schema/reference/schedule/代码及离线preflight；待用户批准这108次新调用后执行。执行后无论结果如何均停止，不启动Gap、Search/Find/Open、Writer或rollout。
'''
    write(P/'analysis/FINAL_CONCLUSION.md',conclusion)
    write(P/'analysis/PREPARED_CONCLUSION.md',conclusion)
    write(P/'STATUS.json',{'status':'PREPARED_FOR_E1_EXECUTION','E0':'PASS','E1':'NOT_RUN_AWAITING_NEW_APPLICABLE_AUTHORIZATION','new_paid_calls':0})
    write(P/'analysis/OFFLINE_TESTS.json',{'command':'python -m unittest experiments.recoverable_control_equivalence.test_offline experiments.recoverable_control_equivalence.test_selection -v','passed':9,'failed':0,'scope':'projection/censoring/edge exclusion/run lengths, Gold-vs-input closure/STOP, parser schema, no inherited auth','network_calls':0})
    write(P/'analysis/INTERPRETATION_AUDIT.md','''# Descriptive interpretation audit

1. No p-value or significance claim. 2. Report numerators/denominators and effect sizes. 3. No108-independent-sample assumption: only10qids. 4. No causal claim from historical trajectory. 5. Gate chosen by new user task on exposed data, no fresh-confirmatory claim. 6. Nonempty and qid strata included. 7. No post-hoc label edits. 8. Selection NOT_RUN has no fabricated zero outcome. 9. Recovery0/0 is undefined with censoring. 10. Available frontier is not observed corrective evidence. 11. Addressability, alignment, selection and actual STOP remain separate. These checks cover inferential, denominator, causality and selective-reporting risks without claiming an independent review.
''')
if __name__=='__main__':main()
