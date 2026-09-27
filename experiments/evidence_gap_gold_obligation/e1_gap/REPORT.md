# E1 Gold Obligation → Evidence Gap：PASS，STOP_E1

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

| 指标 | G0：O+C | G1：O+C+H | G0 门槛 |
|---|---:|---:|---:|
| Strict Gap Validity | 50/54 (92.6%) | 52/54 (96.3%) | ≥80% |
| Missing correctness | 52/54 (96.3%) | 52/54 (96.3%) | ≥85% |
| Response-level support | 54/54 (100.0%) | 54/54 (100.0%) | ≥85% |
| Satisfied-control specificity | 16/16 (100.0%) | 16/16 (100.0%) | ≥85% |
| Schema valid | 54/54 (100.0%) | 54/54 (100.0%) | ≥95% |
| 有效语义重复一致率 | 24/27 (88.9%) | 26/27 (96.3%) | ≥80% |
| Evidence-needed correctness | 50/54 (92.6%) | 52/54 (96.3%) | 描述性 |
| 保持 evidence-level | 54/54 (100.0%) | 54/54 (100.0%) | 描述性 |
| Downstream jump | 0/54 (0.0%) | 0/54 (0.0%) | ≤10% |
| Target as prerequisite | 0/54 (0.0%) | 0/54 (0.0%) | ≤10% |


**G0 八项全部通过。** 有效重复一致率要求同一语义缺口、两条 missing/evidence 均正确且 schema 有效；两次一致地错不会得分。G1 只作为消融，不能改变 G0 gate。

## 必须同时看的分层

| Reference 状态 | G0 strict | G1 strict |
|---|---:|---:|
| unsupported | 24/24 (100.0%) | 24/24 (100.0%) |
| partial | 10/14 (71.4%) | 12/14 (85.7%) |
| satisfied | 16/16 (100.0%) | 16/16 (100.0%) |
| empty_claims | 20/20 (100.0%) | 20/20 (100.0%) |
| nonempty_claims | 30/34 (88.2%) | 32/34 (94.1%) |


每臂 20/54 输出来自空 Claims，16/54 来自 satisfied controls；两者均全对，会提高 aggregate。最直接测试部分证据差分的 7 个 partial cases，G0 只有 **10/14=71.4%**。这是明确的机制局限，不能把总体通过解释为所有研究中间状态都已可靠。分层是描述性诊断，不事后修改 frozen gate。非空 Claims 的 G0 strict 为 30/34=88.2%。

Support micro：G0 59/59 (100.0%)，G1 56/56 (100.0%)。每臂仅 32 条输出实际引用 Claim；空列表不进入 micro 分母。非空 Claims 的 response support 均为 34/34。这里允许相关实体定位引用，不把定位信息当未观察关系的证据；详见每条 reason。R031/R091 的额外 C3 被接受，因为它明确支持同一论文的 emotion 分类，未被当成 13.53% 的证明。

## 失败定位

- G23 / F15_S01，两臂四条：把“两名其他队友彼此同国”扩成或替换为“与 Jerry/Australia 同国”。这是 relation/referent scope 错误，不是未识别 Claim ID。
- G0 G08 replicate 2 / R077：missing 正确，但 evidence_needed 把成为歌曲指代的人由 Sophie 换成 partner。
- G0 G14 replicate 2 / R068：missing 保留书未识别，但 evidence_needed 将 L. E. 固定为 Euler；当前 C 只支持候选出生信息，未建立该书的 referent。此 case 事前标为 medium ambiguity，删除它的描述性敏感性结果为 G0 49/52=94.2%，不改变 gate。

错误标签可重叠：G0 false_requirement 3/54、wrong_referent 2/54；G1 分别 2/54、1/54。未观察到 downstream_jump、target_as_prerequisite、memo→letter scope transfer、Claim over-strengthening 或 stale_gap。零观测不是零风险保证。

## 重复与 H

G0：both strict-valid 24 对、exactly one 2 对、both invalid 1 对；same/compatible/different gap=24/1/2。G1：26/0/1；same/compatible/different=26/1/0。G0 单次重复 strict 为 26/27 和 24/27；G1 两次均 26/27。temperature=0 仍不等于确定性。

G1 H contamination = **0/54**，其中 32 条来自非空 H，22 条来自原始 null H。已检查 H 的坏日期、候选书、SPS、song、host hint，未发现 H 独有内容改变 gap。G0 better 0、G1 better 2、tie 52；2 条差异不足以证明 H 有效。G1 数值更高，不能说无 H 更稳定，也不能说 H 必须进入 Gap。G0 的 Euler 固定错误本身发生在没有 H 的 arm。

## 成本与完整性

planned/sent/returned=108/108/108；peak concurrency=8；wall=60.56s；单请求 latency median=2.73s、P95=8.73s、max=24.63s。timeout/retry=0/0。

Input 75,406；completion 80,175（含 reasoning 70,422）；total 155,581。Cache hit 45,436、miss 29,970，加权命中率 **60.26%**。108 条 usage 完整，unknown usage=0；没有重复加 reasoning，也没有虚构货币成本。实际 completion median=463、P95=1,792、max=5,136，低于历史长尾，但不提供未来上限保证。

16,148 个历史实验文件哈希未变；27 个 QCH 与原始 snapshots 逐字核对；108 个 raw response 独立重解析与 result 一致；accounting 可重算。INTEGRITY 中 zero_network_calls 指审计函数本身不联网；本实验实际 sent 明确为108。

## 研究结论与停止

本 development bank 支持：**给定人工正确 scoped O，O+C→Gap 是有希望的控制计算，并通过事前工程门槛。** 尤其避免了旧 Premise Checker 将正在调查的关系误当已成立前提的问题。旧 checker 的 28/44 distinction、30/44 whole-support 仅为描述性背景：任务、bank、prompt/runtime 不同，不能把差值称作 randomized causal improvement。

部分证据条件下仍有明显 scope/证据表达脆弱性。允许建议下一次独立研究 Q→Local Obligation，同时继续隔离 Gold-O Gap 诊断；本轮已停止，未执行该建议。没有依据添加 requires/depends_on、完整 Binding graph、persistent Gap 或检索闭环。
