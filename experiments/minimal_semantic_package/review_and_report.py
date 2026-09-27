"""Offline, post-score content review and final reports. Never calls a provider.

The manually authored explanations below do not change any frozen reference.
All output paths are exclusive; this is an archival writer, not a rerun command.
"""
from collections import Counter
from .common import *
from .inputs import references


# Reviewed against the actual content-only packets, including every cited subset.
REASONS = {
    'A01_CAND1': '教授身份不证明两人共同署名；U1缺口成立。',
    'A02_CAND1': 'C2明确给出同一论文的两位作者，满足局部署名条件。',
    'A02_CAND2': 'C2已足够；Auditor收到的实际子集只有C2，没有借用未引用C1。',
    'A02_CAND3': '主题分类及表格内容不提供作者数量。',
    'A03_CAND1': '实际引用C4+C5建立该论文表格与13.53%的关联。',
    'A03_CAND2': 'C4为C5的that paper提供可见前项，表格、情绪、比例共同成立。',
    'A03_CAND3': '孤立C5的that paper没有可见前项；按冻结绑定政策为OPEN。两次审计均未标缺口。已预标参考歧义：存在性表格读法会宽于该政策。',
    'A04_CAND1': '创办公司及毕业院校未覆盖游戏发行部门/年份、最高营收及大学创立年份。',
    'A05_CAND1': '创办公司和学位没有婚姻、2019时点、无子女证据。',
    'A06_CAND1': '人取得大学学位不能替代建筑属于大学的关系及2019时点。',
    'A07_CAND1': 'C5明确说2019文章时已婚无子女；两次Verifier均接受，相同证据的Auditor r2却将U2时间框架列为缺口。',
    'A07_CAND2': '2025分居及两个孩子不建立2019婚姻无子女状态；不能从后来的状态倒推2019。r1额外标记U1，分居对曾有配偶有间接支持，但不解决目标时点。',
    'A07_CAND3': 'C5支持局部婚姻，未提供gift、建筑及complex；两次正确保留U4/U5/U6。',
    'A08_CAND1': '创办人、个人学位及婚姻均未建立建筑身份、开放计划或所属大学。',
    'A09_CAND1': '艺人身份已给出，但没有慈善机构名字及共享名字关系。',
    'A10_CAND1': '死亡城市已给出，缺少航空事故地点/最严重条件及20–30英里距离关系。',
    'A11_CAND1': '伴侣与悼念引语不支持艺人身份和慈善机构名字关系的完整目标。',
    'A12_CAND1': '加拿大PhD经历有证据，但没有伊朗导师及指导关系。',
    'A13_CAND1': 'C1只建立book出版；后续article和六年关系U1/U3均缺失。',
    'A14_CAND1': 'C1+C3给出同作者book2016/article2022；冻结参考按出版年份接受。r1在Verifier、r2在Auditor均标U3六年间隔。精确到日的读法可产生争议，但JSON没有原因，不能确定内部解释。',
    'A14_CAND2': '与A14_CAND1实际payload相同，U3被两条调用链拒绝；此证书在调用前预标出版年份/日期精度歧义。',
    'A14_CAND3': '同作者book与article的数学/Vipassana主题均可见，局部主题关系不要求兄弟六年条件。',
    'A14_CAND4': '只有article，缺book及六年比较U4/U3；r2还将已由C3明确给出的U1文章发表列为缺口，属正确OPEN中的额外错误缺口。',
    'A15_CAND1': '传记不能建立书籍引用Euler的U1关系；没有可见well-known或中欧地理分类，不能调用外部知识补足。',
    'A16_CAND1': '一般SPS症状不能证明具体病例有半年的病史。引用一般症状仍不构成病例支持。',
    'A17_CAND1': 'C7覆盖病史及症状，唯一返回缺口U1=The first case。按冻结候选分支政策是假OPEN；字面序数/角色绑定并未单独表示，仍有语义契约限制。country/history未出现在输入。',
    'A17_CAND2': '局部半年病史已有C7；唯一缺口是first-case角色U1，非country/history。冻结候选分支政策与字面身份要求须区分。',
    'A17_CAND3': 'walking/shoulder及加重已有C7；U6只作痛感前项的context，模型未将其列为额外目标。唯一缺口U1角色，按冻结政策是假OPEN。',
    'A17_CAND4': '患者Pakistani国籍不建立报告地点国家及建国历史资格。r2未标U2报告国家缺口，属于正确OPEN但缺口列表不完整；U3仍实质未支持。',
    'A17_CAND5': 'FOP分子机制和一般创伤风险不证明具体病例半年病史。',
    'A18_CAND1': '论文及导师背景没有DLC发行、策略类型和时间关系证据。',
    'A19_CAND1': 'C3+C5建立DLC/base-game与2016相对2013超过三年；两个2013日期版本均满足超过三年。',
    'A19_CAND2': '与A19_CAND1实际payload相同；两出版/发行时点及DLC关系共同覆盖间隔。',
    'A19_CAND3': 'C3+C5共同覆盖DLC与策略游戏的关系，不需要兄弟三年间隔。',
    'A19_CAND4': '只有DLC发行，不提供策略类型及base-game发行时间，U3/U4未支持。',
    'A20_CAND1': 'C3建立Rights of Man–EU4，C4给技术及宗教机制变化；冻结参考接受。相同引用子集Auditor r2把U3 base-game列为缺口，r1接受。',
    'A20_CAND2': 'C3+C6建立DLC/game及技术重做，冻结参考接受；两次Verifier却只标U2 mechanics-change。nation/religion兄弟条件没有进入输入。',
    'A20_CAND3': 'C3+C4足够且实际另引用C6，机制及DLC/game绑定均有材料，审计两次接受。',
    'A20_CAND4': 'C3绑定DLC/game，C7给government/subjects改变，冻结参考接受一般mechanics。Auditor两次只标U3 base-game。参考已预标一般mechanics与列举子条件边界歧义。',
    'A20_CAND5': '有机制变化但没有完整playable European nation资格；U8缺口成立。',
    'A20_CAND6': '整个目标仍缺U8 qualified nation；r2另标U3，按冻结DLC/game关联政策这是额外错误缺口，OPEN本身正确。',
    'A21_CAND1': 'C1+C2联合建立澳大利亚程序员、团队成员与冠军；叙述者I discovered仅为context，没有被要求另证。',
    'A21_CAND2': 'C1+C2明确建立nationality、成员与championship关系。',
    'A21_CAND3': '个人国籍和IOI奖牌未建立该团队及冠军成员关系，U2/U4缺失。',
    'A22_CAND1': 'C2给队友姓名但无两位队友同国证据；不能由姓名或Jerry国籍推断。',
    'A23_CAND1': '备忘录传递日期不是信件写作与作者上台的六个月关系，尤其U2/U3缺失。',
    'A24_CAND1': 'C1的King Michael of Romania绑定作者国家，C3提供信中收回地区陈述；引用子集足够。',
    'A24_CAND2': 'C2/C3不明示Romania是作者国家。r1正确标U3，r2只引用C3并被Auditor放行。调用前已改为OPEN并预标歧义，未借用未提供C1。',
}


def review():
    diagnostics = read(P/'analysis/FINAL_DIAGNOSTICS.json')
    refs = references()
    assert set(REASONS) == set(refs)
    rows = []
    for r in diagnostics['review_records']:
        cid = r['certificate_id']
        audited = r['auditor_id'] is not None
        out = r['auditor_output'] if audited else r['verifier_output']
        payload = r['actual_last_call_input']
        target = {u['unit_id']: u['text'] for u in payload['target_semantics']}
        context = {u['unit_id']: u['text'] for u in payload['interpretive_context']}
        gaps = out['uncovered_target_unit_ids']
        unit_reviews = []
        for uid in gaps:
            assessment = 'material_not_established'
            if r['gold_support'] == 'SUPPORTED':
                assessment = 'supported_under_frozen_reference'
                if cid.startswith('A17_') or cid in ('A14_CAND1', 'A14_CAND2', 'A20_CAND4'):
                    assessment = 'reference_policy_disagreement'
            elif (cid == 'A14_CAND4' and uid == 'U1') or (cid == 'A20_CAND6' and uid == 'U3'):
                assessment = 'extra_gap_despite_support_under_frozen_reference'
            elif cid == 'A07_CAND2' and uid == 'U1':
                assessment = 'partial_spouse_evidence_but_target_time_unestablished'
            unit_reviews.append({'unit_id': uid, 'text': target[uid], 'assessment': assessment})
        rows.append({
            'verifier_id': r['verifier_id'], 'auditor_id': r['auditor_id'],
            'certificate_id': cid, 'replicate': r['replicate'],
            'category': r['category'], 'reviewed_call': 'auditor' if audited else 'verifier',
            'content_packet_sha256': digest(payload),
            'asserted_support_has_frozen_sufficient_witness': r['witness_sufficient'] if r['verifier_accepted'] else None,
            'all_reported_gap_ids_are_real_target_ids': all(u in target for u in gaps),
            'reported_context_ids_as_target_gaps': [u for u in gaps if u in context],
            'unit_gap_review': unit_reviews,
            'gap_omission_observed': ['U2: patient nationality does not establish report country'] if cid == 'A17_CAND4' and r['replicate'] == 2 else [],
            'missing_gap_list_not_required_exhaustive_by_schema': True,
            'material_reason': REASONS[cid],
            'precall_ambiguity': refs[cid]['ambiguity_reason'],
            'semantic_context_expansion_evidence': 'none identifiable from content; absence of evidence is not proof of internal reasoning',
            'primary_gold_changed': False,
        })
    data = {
        'reviewer': 'single task-familiar Codex reviewer; unmasked after mechanical scoring; not independent or blind',
        'review_material': 'all96 content-only chain packets, including all35 actual auditor evidence subsets; provider reasoning excluded',
        'rubric': 'e1_gold_support/REVIEW_RUBRIC.md',
        'rubric_sha256': sha(P/'e1_gold_support/REVIEW_RUBRIC.md'),
        'primary_scoring_unchanged': True,
        'coverage': {'chains': len(rows), 'audited_chains': sum(r['auditor_id'] is not None for r in rows),
                     'verifier_open_chains': sum(r['auditor_id'] is None for r in rows)},
        'categories': dict(Counter(r['category'] for r in rows)),
        'records': rows,
    }
    write(P/'analysis/CONTENT_REVIEW.json', data)


def blocked_stages():
    metrics = {
        'E2': ['target_under_inheritance', 'sibling_over_inheritance', 'interpretive_context_confusion', 'safe_package', 'exact_target_set', 'replicate_stability', 'unitization_insufficient', 'schema_validity'],
        'E3': ['support_precision', 'support_recall', 'gold_minus_predicted_precision', 'gold_minus_predicted_recall', 'false_support_increase', 'false_open_increase', 'Euler_false_support_count', 'false_full_risk_count'],
        'E4': ['false_shrink', 'false_FULLY_SUPPORTED_count', 'residual_recall', 'governing_relation_retention', 'known_binding_correctness', 'derived_constraint_correctness', 'state_discrimination', 'state_pair_monotonicity', 'schema_validity'],
    }
    for stage, dirname in [('E2', 'e2_boundary_recovery'), ('E3', 'e3_predicted_support'), ('E4', 'e4_residual_view')]:
        decision = {'stage': stage, 'status': 'NOT_RUN_E1_GATE_FAILED', 'actual_requests': 0,
                    'root_gate': '../e1_gold_support/METRICS.json', 'E1_PASS': False,
                    'metrics_measured': False, 'gate_pass': None,
                    'reason': 'TASK3/13: E1 FAIL prohibits every later stage; not waiting for approval'}
        write(P/dirname/'DECISION.json', decision)
        write(P/dirname/'METRICS.json', {**decision, 'metrics': dict.fromkeys(metrics[stage])})
        write(P/dirname/'REPORT.md', f'''# {stage} — 未执行

状态：`NOT_RUN_E1_GATE_FAILED`。实际调用 **0**。

[E1最终结果](../e1_gold_support/REPORT.md)未通过冻结门槛。按任务书第3/13节，后续阶段停止；没有待授权的本阶段调用。

本阶段所有机制指标均为 **未测量 / null**，不能解释为0错误或PASS。原`STATUS.json`为调用前冻结快照，保留原样；最终决定见本目录`DECISION.json`。
''')


def report():
    scored = read(P/'e1_gold_support/METRICS.json')
    m, sensitivity = scored['primary'], scored['ambiguous_reference_exclusion_descriptive_only']
    ds = read(P/'analysis/FINAL_DIAGNOSTICS.json')
    assert scored['gate']['status'] == 'FAIL'
    qrows = '\n'.join(f"| {qid} | {r['planned']} | {r['TP']} | {r['FP']} | {r['false_open_count']} |" for qid, r in ds['by_qid'].items())
    write(P/'e1_gold_support/REPORT.md', f'''# E1 — Gold Package Support 最终报告

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
{qrows}

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
''')


def conclusion():
    write(P/'FINAL_CONCLUSION.md', '''# Minimal Semantic Package / Scoped Partial Evaluation — 最终结论

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
''')
    write(P/'FINAL_STATUS.md', '''# 最终状态

**COMPLETE_E1_FAIL — STOP。** E0参考构造完成；E1的96次Verifier与35次Auditor全部完成；E2/E3/E4为`NOT_RUN_E1_GATE_FAILED`，没有等待授权的后续批次。

最终结论见[FINAL_CONCLUSION](FINAL_CONCLUSION.md)，门槛见[E1 METRICS](e1_gold_support/METRICS.json)。完整性结果见[FINAL_INTEGRITY](analysis/FINAL_INTEGRITY.json)，交付文件哈希见[RESULTS_SEAL](RESULTS_SEAL.json)。

先前README、CURRENT_STATUS、EXECUTION_STATUS、FROZEN_STATE、VERIFIER_REPORT及各阶段STATUS.json均为调用前/中期已冻结快照，保留原样。本文件及各阶段DECISION.json给出执行完成后的状态。
''')


if __name__ == '__main__':
    review()
    blocked_stages()
    report()
    conclusion()
    print('Wrote complete96-chain content review, final E1 report,18 answers, and explicit unmeasured later stages. No model calls.')
