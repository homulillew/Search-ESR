"""Render final descriptive reports from immutable results and review artifacts."""
from experiments.evidence_gap_gold_obligation.common import *

def main():
 m=read(P/'e1_gap/METRICS.json');a=read(P/'e1_gap/ACCOUNTING.json');d=read(P/'analysis/DIAGNOSTICS.json');h=read(P/'analysis/H_ABLATION.json')
 fmt=lambda v:f"{v['n']}/{v['d']} ({v['rate']:.1%})" if v['rate'] is not None else 'n/a'
 table='| 指标 | G0：O+C | G1：O+C+H | G0 门槛 |\n|---|---:|---:|---:|\n'
 for key,label,threshold in [('strict','Strict Gap Validity','≥80%'),('missing','Missing correctness','≥85%'),('support','Response-level support','≥85%'),('satisfied_specificity','Satisfied-control specificity','≥85%'),('schema','Schema valid','≥95%'),('replicate_semantic','有效语义重复一致率','≥80%'),('evidence_needed','Evidence-needed correctness','描述性'),('evidence_level','保持 evidence-level','描述性')]:
  table+=f"| {label} | {fmt(m['G0'][key])} | {fmt(m['G1'][key])} | {threshold} |\n"
 for key,label in [('downstream_jump','Downstream jump'),('target_as_prerequisite','Target as prerequisite')]:table+=f"| {label} | {fmt(m['G0']['errors'][key])} | {fmt(m['G1']['errors'][key])} | ≤10% |\n"
 strata='| Reference 状态 | G0 strict | G1 strict |\n|---|---:|---:|\n'
 for key in ('unsupported','partial','satisfied','empty_claims','nonempty_claims'):
  strata+=f"| {key} | {fmt(d['G0']['strict_by_stratum'][key])} | {fmt(d['G1']['strict_by_stratum'][key])} |\n"
 report=f'''# E1 Gold Obligation → Evidence Gap：PASS，STOP_E1

## Material Passport

27 个已暴露的自然历史 QCH，10 个问题簇；人工 Gold O，单 Codex reviewer；被测模型 DeepSeek `deepseek-flash`。原始任务和协议见 TASK.md / PROTOCOL.md。没有 fresh/generalization 或完整 Agent 成功声明。

## 执行与盲审顺序

- Base: `a37a1bd1afbd366dc35bc1e0c951aa5c2befbd96`。
- Bank、Gold、prompt、provider 预检、schedule、gate/code freeze: `a7f458f36b1b8f0373144d0363b3b108cf44eff9`。
- 108 请求 = 27×2 arms×2 replicates；真实调用全部发生在 freeze commit 后。
- 全部 first-pass semantic labels 在 `af43b4fb5e20b37e081256adddd3b7e30c69293d` 提交，之后才揭示 KEY/H、做 replicate/H second pass 和 aggregate。
- Reviewer 不看 provider reasoning、H、臂名或重复编号进行 first pass；知道旧研究和参考构造，不能声称独立 reviewer 或完美 blind。
- 108/108 HTTP200、合法 schema；0 transport/format failure，全部调用保留。6 条 strict semantic failure 仍在分母。

## Frozen primary gate

{table}

**G0 八项全部通过。** 有效重复一致率要求同一语义缺口、两条 missing/evidence 均正确且 schema 有效；两次一致地错不会得分。G1 只作为消融，不能改变 G0 gate。

## 必须同时看的分层

{strata}

每臂 20/54 输出来自空 Claims，16/54 来自 satisfied controls；两者均全对，会提高 aggregate。最直接测试部分证据差分的 7 个 partial cases，G0 只有 **10/14=71.4%**。这是明确的机制局限，不能把总体通过解释为所有研究中间状态都已可靠。分层是描述性诊断，不事后修改 frozen gate。非空 Claims 的 G0 strict 为 30/34=88.2%。

Support micro：G0 {fmt(m['G0']['support_micro'])}，G1 {fmt(m['G1']['support_micro'])}。每臂仅 32 条输出实际引用 Claim；空列表不进入 micro 分母。非空 Claims 的 response support 均为 34/34。这里允许相关实体定位引用，不把定位信息当未观察关系的证据；详见每条 reason。R031/R091 的额外 C3 被接受，因为它明确支持同一论文的 emotion 分类，未被当成 13.53% 的证明。

## 失败定位

- G23 / F15_S01，两臂四条：把“两名其他队友彼此同国”扩成或替换为“与 Jerry/Australia 同国”。这是 relation/referent scope 错误，不是未识别 Claim ID。
- G0 G08 replicate 2 / R077：missing 正确，但 evidence_needed 把成为歌曲指代的人由 Sophie 换成 partner。
- G0 G14 replicate 2 / R068：missing 保留书未识别，但 evidence_needed 将 L. E. 固定为 Euler；当前 C 只支持候选出生信息，未建立该书的 referent。此 case 事前标为 medium ambiguity，删除它的描述性敏感性结果为 G0 49/52=94.2%，不改变 gate。

错误标签可重叠：G0 false_requirement 3/54、wrong_referent 2/54；G1 分别 2/54、1/54。未观察到 downstream_jump、target_as_prerequisite、memo→letter scope transfer、Claim over-strengthening 或 stale_gap。零观测不是零风险保证。

## 重复与 H

G0：both strict-valid 24 对、exactly one 2 对、both invalid 1 对；same/compatible/different gap=24/1/2。G1：26/0/1；same/compatible/different=26/1/0。G0 单次重复 strict 为 26/27 和 24/27；G1 两次均 26/27。temperature=0 仍不等于确定性。

G1 H contamination = **0/54**，其中 32 条来自非空 H，22 条来自原始 null H。已检查 H 的坏日期、候选书、SPS、song、host hint，未发现 H 独有内容改变 gap。G0 better 0、G1 better 2、tie 52；2 条差异不足以证明 H 有效。G1 数值更高，不能说无 H 更稳定，也不能说 H 必须进入 Gap。G0 的 Euler 固定错误本身发生在没有 H 的 arm。

## 成本与完整性

planned/sent/returned=108/108/108；peak concurrency=8；wall={a['wall_seconds']:.2f}s；单请求 latency median={d['execution']['latency_seconds']['median']:.2f}s、P95={d['execution']['latency_seconds']['p95']:.2f}s、max={d['execution']['latency_seconds']['max']:.2f}s。timeout/retry=0/0。

Input 75,406；completion 80,175（含 reasoning 70,422）；total 155,581。Cache hit 45,436、miss 29,970，加权命中率 **60.26%**。108 条 usage 完整，unknown usage=0；没有重复加 reasoning，也没有虚构货币成本。实际 completion median=463、P95=1,792、max=5,136，低于历史长尾，但不提供未来上限保证。

16,148 个历史实验文件哈希未变；27 个 QCH 与原始 snapshots 逐字核对；108 个 raw response 独立重解析与 result 一致；accounting 可重算。INTEGRITY 中 zero_network_calls 指审计函数本身不联网；本实验实际 sent 明确为108。

## 研究结论与停止

本 development bank 支持：**给定人工正确 scoped O，O+C→Gap 是有希望的控制计算，并通过事前工程门槛。** 尤其避免了旧 Premise Checker 将正在调查的关系误当已成立前提的问题。旧 checker 的 28/44 distinction、30/44 whole-support 仅为描述性背景：任务、bank、prompt/runtime 不同，不能把差值称作 randomized causal improvement。

部分证据条件下仍有明显 scope/证据表达脆弱性。允许建议下一次独立研究 Q→Local Obligation，同时继续隔离 Gold-O Gap 诊断；本轮已停止，未执行该建议。没有依据添加 requires/depends_on、完整 Binding graph、persistent Gap 或检索闭环。
'''
 write(P/'e1_gap/REPORT.md',report)
 conclusion='''# 最终结论：Gold Obligation → Evidence Gap

**Frozen G0 Gate：PASS。执行状态：STOP_E1。**

在人工先固定 Local Obligation 的前提下，G0 Strict Gap Validity 为 **50/54（92.6%）**，8 项门槛全部满足。有资格提出下一次独立的 `Q → Local Obligation` 实验；本轮没有执行它。

最重要的限制：27 个快照仅来自 10 个已暴露问题，单 reviewer；10 个空 Claims 快照和 8 个 satisfied control 较容易。7 个 partial-support 快照的 G0 strict 仅 **10/14（71.4%）**，中间研究状态仍有明显问题。整体通过不等于完整架构成立。

## 任务要求的 15 个回答

1. **Gold O 固定后能否稳定做 Required−Supported？** 在本 development bank 上通过工程门槛：strict 50/54，missing 52/54，正确语义重复一致 24/27。支持继续独立研究；不能外推未知任务或所有 partial states。
2. **最常见 Gap 错误？** 错误的关系范围/新增条件。G0 false_requirement 3/54；wrong_referent 2/54（重叠）。队友“彼此同国”被改成“都与 Jerry 同国”是最稳定失败，四条跨臂输出均错。
3. **Target 仍被当 prerequisite 吗？** 本轮 0/54 G0、0/54 G1。把未知 spouse/donation/interview 列为待查证据，未要求它们事先成立，不应误标为前提错误。
4. **还有 downstream jump 吗？** 两臂均 0/54；未知 article、book、DLC 和 letter 保持 identification/existence gap。Euler 固定错误单列为 candidate-specific false requirement，未混称下游跳跃。
5. **Claim support scope 仍是主要瓶颈吗？** 本轮未表现为首要问题；错误集中在 missing/evidence_needed 的 relation/referent 表达。Gold O 和短、已整理 C 降低了难度；Claim支持评估也允许明确相关的实体定位引用。
6. **supported_by 整条可靠性？** 两臂均 54/54；非空 Claims 子集均 34/34。Micro 分别 59/59、56/56；每臂 32 条实际引用了 Claims。空引用与容易对照会抬高整体，需要保留分层解释。
7. **missing 比此前 legality 更稳定吗？** 当前 missing 两臂均 52/54，描述性表现较好；历史 premise distinction 28/44、whole-support 30/44。任务、样本、prompt/runtime 不同，没有 randomized 直接比较，不能宣称因果提升。
8. **evidence_needed 保持证据层面吗？** 两臂均 54/54 没退化为 query 或指定网站；但语义正确分别只有 50/54、52/54。Sophie/partner 主体互换说明格式和“证据类型”正确仍可验证错对象。
9. **Satisfied 上会制造假 Gap 吗？** 本轮未观察到：两臂均 16/16 返回成对 null。仅说明局部 obligation 已满足，不代表 Q 全局完成。
10. **两次重复稳定性？** G0 both-valid/exactly-one/both-invalid=24/2/1；G1=26/0/1。有效 same-gap 一致率分别 24/27、26/27。两次一致地错不算通过；temperature=0 仍有语义波动。
11. **H 污染 Gap 吗？** 未观察到 H 独有内容污染：0/54；非空 H 子集0/32。坏的 memo→letter 日期 H 也未被采纳。样本小、H多与O/C重复，不能证明永远安全。
12. **没有 H 明显更稳定吗？** 不支持。G1 strict 52/54，高于G0 50/54；配对 G0胜0、G1胜2、平52。差异小且仅两次重复；既不能认为必须删除H，也不能认为H必须参与Gap。
13. **需要 requires/depends_on 的证据？** 没有。失败不是 unresolved external dependency，增加依赖字段没有本轮经验依据。
14. **需要完整 Binding representation 的证据？** 没有。确有局部关系/指代错误，但这不能直接推出需要变量、谓词或图。当前最小输出结构即可承载正确解；不升级表示复杂度。
15. **有资格进入 Q→Local Obligation 吗？** 按冻结 development Gate，有资格设计下一次独立实验。其核心应单独评价 O 的 scope/来源，并保留 Gold-O 对照以隔离 Gap 错误。**未自动执行、未加 prompt revision、未做 Search/Writer/closure。**

## 交付与成本

108 请求全部保留，HTTP/schema成功108；strict语义失败6条均在分母。无重试，无额外canary或下游调用。Input 75,406，completion 80,175（reasoning 70,422已包含），total155,581；cache hit/miss=45,436/29,970，加权命中率 **60.26%**；并发峰值8，批次60.56秒，usage无缺失。未估算货币费用。

参考与代码冻结 `a7f458f`；遮蔽臂别第一轮标签提交 `af43b4f`，之后才揭盲和汇总。旧实验16,148文件哈希全部未变。详细指标、逐条失败、重复与H审阅、原始响应见本目录的 `e1_gap/` 和 `analysis/`。

**允许结论：Gold O 给定时，Evidence Difference 是一个有希望的控制计算。尚未证明动态 O、动作选择、证据获取或完整 Evidence-Gap architecture 成功。**
'''
 write(P/'analysis/FINAL_CONCLUSION.md',conclusion)
 write(P/'analysis/STATUS.json',{'status':'COMPLETED_STOP_E1','G0_gate':m['gate']['status'],'real_calls':108,'further_calls':0,'Q_to_O_executed':False,'retrieval_executed':False,'prompt_revisions':0,'next_stage':'Recommendation only; independent Q→Local Obligation experiment'})
if __name__=='__main__':main()
