"""Reporting only after sealed review, frozen scoring, and raw-result replay."""
from collections import Counter
from .common import *
from .score import assert_review
from .run import load_rows

def fmt(metric):
    return 'N/A' if metric['value'] is None else f"{metric['numerator']}/{metric['denominator']} ({metric['value']*100:.2f}%)"
def metric_table(m):
    rows=[('valid_selection','Valid Selection'),('selected_closed','Selected Gold CLOSED'),('selected_input_closed','Selected Input CLOSED'),
      ('downstream_selection','Downstream Selection'),('false_stop','False STOP'),('input_mask_false_stop','Input-Mask False STOP'),('schema_validity','Valid schema/completion')]
    return '| 指标 | S0 Gold Control Mask | S1 Model Control Mask |\n|---|---:|---:|\n'+''.join(f'| {label} | {fmt(m["arms"]["S0"]["metrics"][key])} | {fmt(m["arms"]["S1"]["metrics"][key])} |\n' for key,label in rows)
def main():
    assert_review();m=read(P/'e1_selection/METRICS.json');acc=read(P/'e1_selection/ACCOUNTING.json')
    integrity=read(P/'analysis/E1_INTEGRITY.json');assert integrity['status']=='PASS' and not m['joint_gate_pass']
    assert m['arms']['S0']['metrics']['valid_selection']['numerator']==41 and m['arms']['S1']['metrics']['valid_selection']['numerator']==40
    outcome={'status':'COMPLETE_STOPPED_AT_E1_GATE','E0':'PASS','S0':'FAIL','S1':'FAIL','E1_joint':'FAIL','interpretation_case':'B',
      'reason':'Gold OpenSet selection already below frozen85% threshold; Model below80%.',
      'paid_calls':108,'valid_outputs':104,'failures':{'length':4},'retries':0,
      'next_rollout':'NOT_RUN_NOT_QUALIFIED','next_gap_tool_writer_calls':0}
    write(P/'e1_selection/OUTCOME.json',outcome)
    # Preserve the prior mutable preparation snapshots before lifecycle updates.
    write(P/'analysis/PRE_EXECUTION_ACCOUNTING.json',(P/'analysis/EXECUTION_ACCOUNTING.json').read_text())
    write(P/'analysis/PRE_EXECUTION_INTEGRITY.json',(P/'analysis/INTEGRITY.json').read_text())
    def replace(path,value):path.write_text(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    replace(P/'STATUS.json',outcome);replace(P/'e1_selection/STATUS.json',outcome)
    replace(P/'analysis/EXECUTION_ACCOUNTING.json',{'new_model_calls':108,'new_paid_calls':108,'E0_new_calls':0,'E1':acc,
      'max_retries':0,'Search_Find_Open_Writer_Gap_calls':0,'currency_estimate':None,'reasoning_note':'Reasoning tokens already included in completion, never added twice.'})
    replace(P/'analysis/INTEGRITY.json',{'status':'PASS','phase':'COMPLETE_STOPPED_AT_E1_GATE','execution':integrity,
      'authorization_sha256':sha(P/'AUTHORIZATION.json'),'freeze_sha256':sha(P/'FREEZE.json'),
      'source_history_unchanged':19111,'blind_review_commit':read(P/'e1_selection/review/REVIEW_SEAL.json')['judgment_commit'],
      'new_paid_calls':108,'remaining_authorized_calls':0})
    report='''# E1 Active Requirement ID Selection — FAIL

## Material Passport

108 frozen calls =27 states×S0/S1×2，DeepSeek deepseek-flash。所有尝试保留，单次完成要求，零重试；仅Q/Skeleton/二分类Mask输入。单个熟悉历史bank的Codex reviewer，18种可见输入分组，108份独立记录的first-pass judgments（非108独立评审）；提交后揭盲。主评分完全继承旧冻结selection reference。

'''+metric_table(m)+'''
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
'''
    for label in ('directly_addressable','coherently_multi_addressable','subnode_only'):
        report+=f"| {label} | {fmt(m['arms']['S0']['strata']['addressability'][label]['metrics']['valid_selection'])} | {fmt(m['arms']['S1']['strata']['addressability'][label]['metrics']['valid_selection'])} |\n"
    report+='''
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
'''
    # Frozen scorer REPORT.md is an executed summary; detailed report is appended separately.
    write(P/'e1_selection/DETAILED_REPORT.md',report)
    conclusion='''# FINAL_CONCLUSION — E0 PASS；E1 S0/S1 FAIL

## Material Passport / provenance

本轮Recoverable Control Equivalence / Active Requirement Selection，基线`dd442dd`，分支`experiment/recoverable-control-equivalence`。27历史states/10qid；E0复用108旧Alignment outputs，E1真实108调用。代码和请求在授权前冻结，用户明确授权后执行。旧实验仍为 **A0 FAIL / A1 PASS / Joint FAIL / E2 NOT RUN**；任何新指标都没有覆盖旧结果。

**结论：OPEN/CLOSED抽象确实消除了大量与控制无关的语义误差，但“正确OpenSet→合法局部Requirement ID”仍未过关。当前不能进入4–8步真实闭环。**

## E0保持通过

| 指标 | A0 Oracle（诊断） | A1 Runtime D2（主评价） |
|---|---:|---:|
| Binary Node Accuracy |315/322（97.83%）|261/264（98.86%）|
| Exact 3-way Mask |38/54（70.37%）|42/54（77.78%）|
| Exact Binary Mask |47/54（87.04%）|51/54（94.44%）|
| OPEN Recall |271/278（97.48%）|225/228（98.68%）|
| OPEN Precision |271/271（100%）|225/225（100%）|
| Closure Precision |44/51（86.27%）|36/39（92.31%）|
| False Close Rate |7/278（2.52%）|3/228（1.32%）|
| False Empty OpenSet |0/54|0/54|
| Lost All Acceptable Frontier |N/A：无Oracle-ID冻结参考|0/50|
| False-close仍有acceptable frontier |N/A|3/3|

40个三分类节点错误折叠掉30个，剩10个False Close（A0 7、A1 3）；False Open为0。两臂Exact Mask各增加16.67pp。非空Claims A1 binary exact31/34=91.18%，OPEN recall129/132=97.73%。

A1所有3个False Close都缺少eligible后续状态，**恢复分母0，不能证明recoverable**。A0 q922两条replicate在G26→G27持续误关（0/2 safe resolution），最大观测连续长度2。两臂均INSUFFICIENT_NATURAL_DENOMINATOR；按任务书不自动阻断Selection，不能据此跳过动态验证。

## E1正式结果

'''+metric_table(m)+'''
S0 **75.93%<85%：FAIL**；S1 **74.07%<80%：FAIL**。Joint FAIL。SelectionLoss=1.85pp通过其限制，但绝对有效选择率未过门槛。4次length（每臂2次）不删除；schema/completion validity每臂96.30%，仍过95%门槛。全部其它动作约束指标通过。

### 错误集中于局部地址能力

23个可解析但不合法的ID：q228复合R1共12次、q637复合R3共8次、q122复合R2共3次。另4次length均为q169。所有23个语义选择错误都位于历史`subnode_only`状态。

- direct+coherent合并有效率62/64=96.88%。
- subnode-only合并19/44=43.18%。
- D2旧addressability仍为direct+coherent16/27=59.26%、subnode-only11/27=40.74%。
- G04/G05本来没有合法单D2 ID，保留全部8个跨臂responses；单臂上限仍25/27=92.59%，没有删题提高成绩。
- G06已有合法R2，但两臂都选R1；G16/G17有合法其它目标，却选了混合临床史和国家史的R3。因此失败不只来自两例不可表示case。

### Mask错误传播证据的实际范围

S0/S1仅G18的Mask不同；两臂四次都选冻结参考允许的R3。可以说这一局部实例保留并使用了替代frontier；不能说误关的R4已恢复，因为没有行动或新证据。

其余26个状态输入相同。整体1.85pp差异来自q122的重复采样差异，不能归因于模型Mask错误。虽然temperature0，返回行为仍不完全相同；不做best-of或替换。

### 盲审分歧与信息缺口

所有108判断先提交于`1c377fc`再揭盲。4条分歧都是G18 R3：可见Mask不展示临床/国家哪一部分未完成，reviewer判粗；冻结参考依据已有Claims判为局部有效。主计分坚持冻结参考，首轮判断完整保留。单熟悉bank的reviewer不构成独立验证。

同一输入还覆盖G04/G05/G06（acceptable空/空/{R2}），以及G10/G11（后者可选集合多R5）。二分类Mask保留OPEN不等于传递了复合节点的可操作残差；这是真实表示问题的线索，但非所有任务不可识别的普遍定理。

## 逐一回答任务书20问

1. **三分类错误多少消失？** A0 17/24，A1 13/16，合计30/40=75%。原语义错误未被删除。
2. **Binary Node Accuracy多高？** A0 97.83%，A1 98.86%。
3. **Exact Binary是否明显更高？** 两臂均+16.67pp；这是描述性增益，没有统计显著或独立确认的声称。
4. **OPEN Recall是否仍约98%？** 是：97.48%/98.68%；非空Claims为95.63%/97.73%。
5. **Closure Precision？** A0 86.27%，A1 92.31%。去掉q1259时A1为22/25=88%，主PASS对题目构成有敏感性，未修改全bank门槛。
6. **False Close是否产生空OpenSet？** E0两臂均无；这是控制状态检查。
7. **是否失去全部acceptable frontier？** A1 0/50；G04/G05另标表示限制，A0缺少相应冻结参考记N/A。
8. **多数False Close仍有其它frontier？** A1 3/3；G18实际Selector也选到其它合法R3。仍未证明可获取修正该错误的证据。
9. **natural trajectory可以恢复吗？** 本次未观察到恢复；A1可评估分母0，A0为0/2，不宣称100% recoverable。
10. **persistent False Close？** A0 q922两replicate持续，最长观测2states；A1末端删失不能判无持续风险。
11. **U→P基本control-neutral？** 对本次只消费二分类状态的接口是。22次U→P、8次P→U均不改变OpenSet，但不表示被引用的语义内容可信。
12. **哪些semantic error成为control error？** P→F的日期错绑、病程增强和地理条件补全。OPEN→CLOSED才使当前可选集合真正丢节点。
13. **D2 coarse node遮蔽内部错误？** 可能；q922粗节点仍因缺少昵称保持OPEN，不能由此推断日期子条件已修复。当前Mask没有子条件解析能力。
14. **coarse node实际阻塞Active-ID Selection？** 有描述性支持：所有23个语义选择错误处于subnode-only，含无可选ID以及选错粗ID两类。未操纵D1/D2作本轮因果对比，不能排除Selector自身能力不足。
15. **Gold OpenSet能选valid ID？** 部分可以：41/54=75.93%，未达到85%。即使OpenSet正确，Frontier Selection仍是独立瓶颈。
16. **Model相对Gold损失？** 1/54=1.85pp；Model40/54=74.07%，未达80%。实际不同Mask只有G18且两臂都valid，不能把全局loss解释为Alignment导致。
17. **downstream jump？** 冻结指标0/54每臂；失败主要是非局部复合目标和length，而非已注册的downstream ID。
18. **ID-only避免重写吗？** 104个有效输出均只返回已有ID，没有重新生成Obligation/relation文本；接口防住改写通道，却没有解决选错节点或节点本身过粗。4次length没有可用输出。
19. **false STOP？** 没有观测到STOP或false STOP，且没选Gold/Input CLOSED。4次无输出单独保留；没有Gold合法STOP正控，不能宣称停止能力已完整验证。
20. **是否够进入4–8步闭环？** 不够；E0通过而S0/S1均失败，属于Case B。按规则停止，不运行Gap/工具/Writer/rollout。

## Known bad cases追踪

| qid | E0问题 | E1观测及边界 |
|---|---|---|
|922 letter/memorandum|A0日期误关持续；D2粗R1仍OPEN|两臂所有6/6均选可接受R1。避免丢失frontier的局部正向证据，不等于日期推理已纠正。|
|637 four-year course|G18 D2 R4误关，两replicate末端删失|G18两臂均选合法R3；早期G16/G17同样选R3却不合法，因当时需同时解决临床与国家条件。|
|843 Georgetown/American|G21 replicate2 R2误关|S1固定replicate1，不含该错误；两臂6/6valid，不能用它证明该误关在Selection被恢复。|
|169 charity relation|U→P不改变二分类Mask|两臂各4/6valid，剩余各2次length；没有把U→P记为False Close，也未因输出失败挑更好replicate。|
|1259 teammate country|U→P仍OPEN|两臂6/6valid；G24均选R4验证同国关系，已知姓名未被当成该关系已完成。|

## 缓存、调用和验证

- 108/108真实请求返回；104有效，4length，HTTP错误/网络错误/timeout0，retries0，峰值并发8。
- input93,656；completion695,973，其中reasoning695,223已包含；total789,629。usage108/108完整。
- cache hit66,944、miss26,712；加权命中率**71.48%**。这是本轮实测，不沿用旧实验73.49%。
- 4个length各65536completion，总262,144，占completion37.67%；失败开销计入总账。省略max_tokens仍遵循冻结配置，不事后调整采样。
- wall471.29s；latency median6.80s、P95177.10s、max261.40s。240s配置为HTTP inactivity，非wall deadline；未伪报timeout。
- 108 raw request/response重放、输出contract重验、冻结metrics和账目重算完全一致；19,111个历史实验文件SHA未变化。未用provider reasoning判断失败原因。
- 不报告未经价格验证的货币成本；不因schema/length失败填造动作。无新搜索、检索、Writer调用。

## 研究判断和下一步边界

本轮支持“细粒度语义错误并非全部都有控制代价”，也给出了“一处False Close仍能选到替代合法目标”的小范围实例。它不支持“Alignment solved”或“自然纠错已经可靠”。

**当前主要瓶颈是：D2复合Requirement作为单一局部目标的地址能力，以及Selector在这些节点间的选择。** OPEN集合保存下来是必要线索，却不足以保证所选ID能成为一个可执行的当前研究目标。边界清晰的direct/coherent状态表现好，是值得保留的正向信号。

下一独立实验可按任务书方向比较 **D1-like局部控制节点+D2 source-span authority**；应保持本轮case与失败记录，避免同时修改表示、Alignment、Selector。这里只提出方向，不新增层级、Verifier、hard gating或State字段，不重调本轮prompt，不运行闭环。

Persistent boundary不变：Q/Skeleton稳定；Verified Claims/Hypothesis持续保存；Workspace/Trace机械记录；Control Mask/OpenSet/ActiveID/Gap每轮重算。CLOSED不能永久写进task semantics。

最终状态：`COMPLETE_STOPPED_AT_E1_GATE`。用户授权的108次调用已用完；本轮按冻结停止规则完成。准备阶段的PREPARED_CONCLUSION、E0 REPORT和FREEZE中的待授权说明是历史快照；当前状态以本报告、STATUS和e1_selection/OUTCOME为准。
'''
    replace(P/'analysis/FINAL_CONCLUSION.md',conclusion)
    write(P/'RESULTS.md','''# Results

E0 Runtime A1 PASS. E1 S0 FAIL (41/54,75.93%<85%); S1 FAIL (40/54,74.07%<80%). SelectionLoss1.85pp. Stop at E1; no rollout.

108 calls,104 valid outputs,4 length failures,0 retries. Cache weighted71.48%. All frozen/historical inputs retained.

See analysis/FINAL_CONCLUSION.md and e1_selection/DETAILED_REPORT.md. Source E0 and preparation reports are immutable chronological snapshots; current STATUS.json supersedes prepared lifecycle status.
''')
    print('Final report and lifecycle accounting written; no new requests.')
if __name__=='__main__':main()
