# 最终结论：Gold Obligation → Evidence Gap

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
