"""Post-unmask reporting only. Never changes frozen inputs, labels or metrics."""
from collections import Counter
from .common import *

def update_unfrozen(path,value,archive=None):
    assert rel(path) not in read(P/'FREEZE.json')['files']
    if archive is not None and path.exists():write(archive,read(path))
    path.write_text(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def main():
    metrics=read(P/'e1_alignment/METRICS.json');assert not metrics['joint_gate_pass']
    assert not metrics['arms']['A0']['gate']['pass'] and metrics['arms']['A1']['gate']['pass']
    assert not (P/'e2_selection/calls').exists() and not (P/'e2_selection/EXECUTION_SCHEDULE.json').exists()
    account=read(P/'e1_alignment/ACCOUNTING.json');audit=read(P/'analysis/e1_alignment_INTEGRITY.json')
    errors=read(P/'analysis/ERROR_LEDGER.json');seal=read(P/'e1_alignment/review/REVIEW_SEAL.json')
    write(P/'e2_selection/OUTCOME.json',{'status':'NOT_RUN_E1_A0_GATE_FAILED','conditional_planned_slots':108,'activated_slots':0,'sent':0,
      'prerequisite':'A0 PASS AND A1 PASS','observed_A0':'FAIL','observed_A1':'PASS','reason':'A0 support_precision, full_support_sufficiency and exact_state_mask fail frozen thresholds.',
      'selection_metrics':None,'no_new_api_calls':True,'no_replica_substitution_or_gate_relaxation':True})
    write(P/'e2_selection/REPORT.md','''# E2 — Not run

E1 A0 FAIL / A1 PASS does not satisfy the frozen conjunctive entry gate.
The108 conditional slots were not activated: zero sends, zero observations,
no S1 materialization and no selection metrics. This is not108 failed selector
responses. No requirement selection, Gap, Search/Find/Open, Writer or rollout ran.

The pre-call STATUS.json/SCHEDULE.json remain immutable preparation snapshots.
OUTCOME.json records the actual final stage status. No natural positive STOP
controls in the frozen bank; neither false nor missed STOP was evaluated here.
''')
    write(P/'STATUS.json',{'status':'COMPLETE_STOPPED_AT_E1_GATE','E1':'A0_FAIL_A1_PASS','E2':'NOT_RUN_E1_A0_GATE_FAILED',
      'paid_calls_authorized_maximum':216,'paid_calls_sent':108,'conditional_calls_not_activated':108,
      'current_report':'analysis/FINAL_CONCLUSION.md','preparation_snapshots':'README.md, e2_selection/STATUS.json, PRE_EXECUTION_AUDIT.md and FREEZE.json are preserved as frozen pre-call records.'})
    update_unfrozen(P/'analysis/EXECUTION_ACCOUNTING.json',{'status':'COMPLETE_STOPPED_AT_E1_GATE','E1':account,
      'E2':{'conditional_planned':108,'activated':0,'sent':0,'returned':0,'model_metrics':None,'cache_weighted_rate':None,'latency_seconds':None,'peak_concurrency':0,'reason':'E1 A0 gate failed'},
      'actual_calls':108,'actual_total_tokens':account['reported_partial_totals']['total'],'weighted_cache_hit_rate':account['cache_weighted_rate'],
      'reasoning_is_subset_of_completion':True,'currency_cost':None,'price_verified':False},P/'analysis/PREPARED_EXECUTION_ACCOUNTING.json')
    citation_extra={a:sum(len(r['extra_by_frozen_reference']) for r in errors['citation_contribution_disagreements'] if r['arm']==a) for a in ('A0','A1')}
    contribution_sensitivity={a:{'primary':metrics['arms'][a]['metrics']['support_precision'],
      'blind_judged_additional_contributions':citation_extra[a],
      'descriptive_precision_if_accepted':(metrics['arms'][a]['metrics']['support_precision']['numerator']+citation_extra[a])/metrics['arms'][a]['metrics']['support_precision']['denominator']} for a in ('A0','A1')}
    write(P/'analysis/REFERENCE_DISAGREEMENT.json',{'scope':'Post-unmask citation-reference audit, not preregistered gate modification',
      'blind_judgment_commit':seal['judgment_commit'],'status_disagreements':audit['blind_reference_status_disagreements'],
      'citation_contribution_disagreements':errors['citation_contribution_disagreements'],'descriptive_sensitivity':contribution_sensitivity,
      'primary_references_and_metrics_unchanged':True,'joint_gate_decision_unchanged':True,
      'interpretation':'The frozen contributing-Claim lists may be under-inclusive: C2 explicitly contributes the winning-year relation in host nodes (three responses) and actual thesis/game/year content in one thesis node. Even accepting all four leaves A0 below90% support precision; full-support and exact-mask failures are unaffected.'})
    ms={a:v['metrics'] for a,v in metrics['arms'].items()}
    def fmt(a,k):
        v=ms[a][k];return f"{v['numerator']}/{v['denominator']} ({v['value']:.2%})"
    table='| 指标 | A0 Oracle | A1 Runtime D2 |\n|---|---:|---:|\n'
    for k,label in [('node_status_accuracy','Node Status Accuracy'),('false_supported_rate','False-Supported Rate'),
       ('residual_recall','Residual Recall'),('residual_precision','Residual Precision'),('support_precision','Support Precision'),
       ('full_support_sufficiency','Full-Support Sufficiency'),('partial_support_validity','Partial-Support Validity'),
       ('exact_state_mask','Exact State Mask'),('both_replicates_exact','两次均 Exact 的状态'),('schema_validity','Schema Validity')]:
        table+=f'| {label} | {fmt("A0",k)} | {fmt("A1",k)} |\n'
    final='''# Skeleton–Claims Alignment：最终结论

## 结论与执行边界

**E1：A0 FAIL，A1 PASS；双门槛未通过，E2 未执行。**

有局部正向信号：节点状态准确率和 Residual Recall 较高，所有 Gold fully
supported 节点都被识别，空 Claims 也没有直接被问题前提填满。但完整 Mask、
引用贡献和细粒度语义蕴含还不够可靠。当前结果不能授权进入 Selection 或闭环。

这不是 DeepSeek 连通性/超时失败：108/108 返回，零 HTTP/格式错误、零重试。
用户明确授权后按冻结方案执行；未使用剩余108次条件预算来补采样或绕过门槛。

## Primary metrics（全部 planned slots 留在分母）

'''+table+'''
A0 未通过三项：Support Precision 86.58% <90%；Full-Support Sufficiency
86.27% <90%；Exact State Mask 70.37% <80%。其余 A0 门槛通过。
A1 达到自身较低的绝对门槛及相对损失门槛，但不能替代 A0 的进入条件。
False-Unresolved 为 A0 0/44、A1 0/36；不存在把已支持节点判为 unresolved 的观察。

## 状态分层与表示影响

10个空 Claims 状态 ×2 replicates 在每个 arm 均20/20 Exact。
17个非空 Claims 状态 ×2 replicates：

| 非空 Claims | A0 | A1 |
|---|---:|---:|
| Node Status Accuracy | 180/204 (88.24%) | 152/168 (90.48%) |
| Exact State Mask | 18/34 (52.94%) | 22/34 (64.71%) |

因此不能用总体约93%的节点准确率代替真实研究进展状态的可靠性。
按 qid/type/replicate 的全部指标见 e1_alignment/METRICS.json。
A1 两次 replicate 的 Exact 分别85.19%与70.37%；没有挑选较好一次重报。

AlignmentLoss=A0 Exact−A1 Exact=−7.41pp；Node Accuracy loss=−1.39pp。
没有观察到 D2 拖累这一组 alignment 指标，但不能据此证明它的控制表示更好：
E0 直接/连贯多节点可表达率 D1=23/27（85.19%）、D2=16/27（59.26%）；
D2 subnode-only=11/27（40.74%），触发冻结的粗粒度警告。

具体地，信件的 D2 节点同时包含 writing period 和 courier nickname。即使模型
误读日期，缺失 nickname 仍可能使整节点保留 P；Oracle 把日期/信件身份单独
拆出后，错误的 F 会显露。这是由输出和节点结构支持的解释，不能证明模型
在 D2 内部已经纠正了日期判断。更好的粗粒度 Mask 分数不等于更精确的控制。

## 误差形态

| Gold → predicted | A0 | A1 |
|---|---:|---:|
| unsupported → partial | 12 | 10 |
| partial → full | 7 | 3 |
| partial → unsupported | 5 | 3 |

最常见的是 **未建立关系绑定，却把相关背景提升为 partial**：Euler 出生信息
没有 book→Euler 引用关系；Harran 教授简介没有 target-paper→author 关系；
通用 SPS 症状没有两份特定病例的绑定；艺人名字没有 charity-name 关系；
队友名字没有 same-country 关系。22/40 个节点状态错误属于 U→P。

10个 false-full 节点集中在：

- 信件：4个 A0 响应把 covering memorandum 的1945日期当作 enclosed letter
  写作期依据；同一 prefix 尚未建立信件写作日期。
- 病例：4个响应把“接下来四年期间出现肿块”当作“四年后才出现肿块”。
- 论文/游戏：2个响应仅凭 Georgetown 名称就将 American-university 条件
  一并判 full。当前 Claims 未提供这个地理事实。

时间/地理条件过度提升可从可见输出确认；没有读取 provider reasoning，不能
判定究竟是外部记忆、问题前提投射还是语义误读。不能把这几种机制武断合并。
不存在空 Claims 直接产生 F 的观察，也没有把只有书的状态当作已有 later article。

8个 P→U 包括已有 official transmission 却因缺 nickname 判 U、已有两份病例
却因缺年份判 U，以及“五张数据表”与“六张总表”之间的 partial/unsupported
边界。最后一种属于预先标为 medium ambiguity 的标注约定，不能当作无争议的
模型事实错误。全部逐节点错误和理由见 analysis/ERROR_LEDGER.json。

## Review、参考限制与 sensitivity

Oracle 在81caa52先于当前 Claims/GoldO 构建冻结；Gold Mask 在4b8e9d8先于
GoldO 地址审查冻结。真实调用 run HEAD 为8980008。首轮只读取 masked packets，
108份逐节点判断在54bc77c提交后才读取映射键、Gold 和 aggregate。
同一输入的两个显示结果放在一组审阅以减少重复阅读，每个响应仍独立留标签；
未按结果择优。Reviewer 是熟悉仓库的单个 Codex，不是独立盲审员或无记忆审稿人。

首轮与冻结参考的 **状态判断无分歧**，但有4处引用贡献分歧：获胜年份 Claim
对 host-for-winning-year 节点的贡献（3次），以及 advisor Claim 同时重复提供
thesis/game/year 内容（1次）。这些 Claim 并非只有主题或名字重合。
冻结贡献集合可能漏列有效引用；原始标签和 primary 分数保持不变。
若描述性地接受这4处，Support Precision 为 A0 131/149=87.92%、
A1 122/137=89.05%。A0 仍未过90%，其余两个失败门槛完全不变。
详见 analysis/REFERENCE_DISAGREEMENT.json；这不是事后改门槛或改 Gold。

预注册 sensitivity：

- 排除 medium-ambiguity 节点后，Full-Support Sufficiency 为97.30%/96.77%，
  说明时间含义等边界会影响该指标；Support Precision 仍仅82.24%/83.33%。
- 逐一排除任意一个 qid，A0 在全部10种分析中仍 FAIL，A1 均 PASS。
- 更保守的 author-list / written-vs-published / partner-tribute 约定不改善
  primary gate。全部仅作描述，不能触发 E2。
- 若改成引用必须自带全部 antecedent context 的更强要求，充分性约51%；
  它不等于本轮允许整份当前 Claims 解析指代的 contextual-sufficiency 定义。

## Progress

预先排除两个 candidate/refinement pair 后，有15条 Claims-addition transition。
每个 arm ×2 replicates 共30对：A0 29对、A1 28对有至少一个上升节点；两者均无
状态下降或 F→U。单调性是描述性正向现象，但错误的 U→P 也会表现为“进展”，
因此它不能替代支持有效性。另两个 refinement pair 未混入该统计。

## 20个必答问题

1. **Control Addressability？** D1 direct10/27、direct+coherent23/27；D2
   direct12/27、direct+coherent16/27；两者 not-addressable 均0/27。
2. **D2 是否过粗？** 有明确警告：11/27 subnode-only。冻结 selection reference
   中 G04/G05 无可接受单节点，但也不是 STOP；结构上限25/27。E2未验证该上限。
3. **Oracle status accuracy？** 298/322=92.55%；非空 Claims 为88.24%。
4. **False-supported 是否受控？** 满足预注册总体比率：A0 7/278=2.52%，
   A1 3/228=1.32%；但 A0 预测 full 中7/51错误，不能据低总体比率宣称充分可靠。
5. **Requirement 再次被当事实？** 未看到空证据直接 F；观察到10次 P→F 的
   未证实条件补全。仅凭输出不能唯一归因于问题前提投射。
6. **Support precision？** 86.58%/87.59%；A0失败，引用集合还有上述4处争议。
7. **Residual recall？** 97.48%/98.68%，均通过；Residual precision 均100%。
8. **Exact Mask 可用吗？** A0 70.37%未过80%；A1 77.78%过其70%门槛。
   非空状态52.94%/64.71%，仍不足声称完整研究状态可靠。
9. **D2 alignment loss？** Exact为−7.41pp，node accuracy为−1.39pp；未观察到
   这两个指标下降，不构成细粒度 source/control 可用性的证明。
10. **主要错误来源？** 已观察到关系角色绑定和语义蕴含错误，尤其背景→partial、
    日期操作数移动、时间关系增强。粗节点还会遮蔽独立子条件错误；没有统一归因。
11. **随 Claims 增长合理 progress？** 符合描述性单调性，60对可评比较无下降；
    但部分上升本身是假支持，不能把单调当作有效进展。
12. **Oracle Mask selection？** 未评估，E2未运行。
13. **Downstream jump？** 未评估，不能从 E1 Mask 代替动作观察。
14. **Model Mask selection loss？** 未评估，无 S0/S1 调用。
15. **ID 显著减少 relation corruption？** 设计上移除了自由复述步骤；本轮没有
    执行 selector，也没有配对自然语言基线，不能作显著性/经验改善声明。
16. **需要 Recent Path？** 本轮没有证明其必要性或修复作用。
17. **需要 requires？** 没有这方面的新证据，不增加依赖结构。
18. **需要 Binding IR？** 关系绑定是实际问题，但这不证明新增 IR 是必要解法。
19. **进入4–8步 rollout？** 不具备本轮预注册资格：E1双门槛未过，E2未验证。
20. **当前瓶颈？** Task–Evidence Alignment 的完整状态/引用可靠性仍是阻塞项，
    同时有 D2 control-addressability 限制。Selection 未知，不能声称已转到 Acquisition。

## 用量与缓存

| 项目 | E1 实测 |
|---|---:|
| planned / sent / returned | 108 / 108 / 108 |
| HTTP / schema / timeout failures | 0 / 0 / 0 |
| input tokens | 121,892 |
| completion tokens | 259,559 |
| reasoning tokens（已含于 completion） | 246,939 |
| total tokens | 381,451 |
| cache hit / miss tokens | 89,579 / 32,313 |
| 加权缓存命中率 | 73.49% |
| latency median / P95 / max | 7.34 / 35.76 / 46.99 秒 |
| batch wall / peak concurrency | 158.59 秒 / 8 |

108份 usage 均完整且算术一致。没有验证价格，不报告货币费用。
E2条件预算108次未激活，实际调用为0；不是108个失败 selector 结果。
未运行 Gap、Search/Find/Open、Writer 或 rollout。历史18,598个已跟踪实验文件
哈希保持不变，冻结输入/提示词/参考/评分器未修改。

## 对后续研究的限定

当前证据支持继续研究 **Claims 是否真正绑定到 requirement 的角色、来源和
时间操作数，以及是否覆盖全部 material conditions**。它不支持直接把 Mask
写成 persistent truth，也不支持用新增 State 字段或架构层数代替这个问题。
本轮已依停止规则结束；任何修复或后续实验应单独预注册。

Q/Skeleton 保持 episode-stable，Claims 是持久证据；Mask、Residual、ActiveID
仍应是根据当前 Claims 重算的临时计算。最终目标是正确对齐与可靠控制，
不是在没有资格证据时持续推动后续阶段。
'''
    update_unfrozen(P/'analysis/FINAL_CONCLUSION.md',final)
    write(P/'RESULTS.md','''# Completed: E1 A0 FAIL / A1 PASS

E2 was not run because its frozen A0 AND A1 entry gate failed.108 real requests,
all returned, no retries or mechanical failures. Weighted cache hit rate73.49%.

| Metric | A0 | A1 |
|---|---:|---:|
| Node accuracy | 92.55% | 93.94% |
| Exact state mask | 70.37% | 77.78% |
| Support precision | 86.58% | 87.59% |
| Full-support sufficiency | 86.27% | 92.31% |
| Residual recall | 97.48% | 98.68% |

See [final conclusion and20 answers](analysis/FINAL_CONCLUSION.md),
[E1 gates](e1_alignment/REPORT.md), [E2 stopped outcome](e2_selection/REPORT.md),
[error ledger](analysis/ERROR_LEDGER.json), and [actual accounting](analysis/EXECUTION_ACCOUNTING.json).

README.md and e2_selection/STATUS.json are immutable pre-call preparation
snapshots covered by FREEZE.json. STATUS.json and this file record current status.
No frozen reference, prompt, schedule, scorer or historical experiment was edited.
''')
    paths=[p for p in (P/'e1_alignment').rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    write(P/'analysis/EXECUTED_FILES.json',{'stage':'e1_alignment','files':{rel(p):sha(p) for p in sorted(paths)},
      'review_commit':seal['judgment_commit'],'freeze_sha256':sha(P/'FREEZE.json')})
    update_unfrozen(P/'analysis/INTEGRITY.json',{'status':'COMPLETE_PASS','source_head':read(P/'FREEZE.json')['source_head'],
      'run_head':read(P/'e1_alignment/RUN.json')['head'],'review_commit':seal['judgment_commit'],
      'manifest_sha256':sha(P/'FREEZE.json'),'frozen_files_unchanged':True,'historical_files_unchanged':18598,
      'raw_requests_responses_metrics_accounting_replayed':True,'first_pass_before_unmask':True,
      'provider_reasoning_read_for_review':False,'actual_model_calls':108,'E2_calls':0,'zero_retries':True,
      'primary_gate':'A0_FAIL_A1_PASS_JOINT_FAIL','primary_references_unchanged':True,
      'single_familiar_reviewer':True,'status_disagreements':0,'citation_contribution_disagreements':4,
      'detail':'e1_alignment_INTEGRITY.json','executed_files_manifest':'EXECUTED_FILES.json'},P/'analysis/PREPARED_INTEGRITY.json')
    print('Final report written; E2 not activated; all frozen model/scoring inputs untouched.')

if __name__=='__main__':main()
