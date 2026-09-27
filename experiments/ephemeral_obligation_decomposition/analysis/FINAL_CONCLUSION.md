# Source-Anchored Task Skeleton：最终结论

## Material Passport

研究范围：仅 `Q → Task Skeleton`。22 个 unique questions；108 次 DeepSeek
`deepseek-flash` 正式调用；每题每 arm 两次重复。单一 Codex reviewer，先提交隐藏
arm 的语义标注，再进行 provenance review。无额外模型评审、重试或替换样本。

基线：`fc0746930edc4ad8aad4c8a04a5f2a138d1b5082`。
冻结提交：`0ddd897`；E1 首轮 review：`f598e02`；E1 gate：`338a6be`；
E2 首轮 review：`4117df1`。所有历史实验文件保持原样。

## 结论与停止位置

**E1 PASS；E2 完整 gate FAIL，实验按协议停止。**

本轮支持：在这些问题和冻结评价标准下，模型可以生成覆盖充分、关系保真、允许
合理不同分组的 Q-only Task Skeleton。D2 在开发集及 fresh bank 共 44/44 个
response strict-valid。

本轮尚未证明：extractive grouping 在 fresh 问题上优于自由改写。E2 的 D0 和
D2 都是 24/24 strict-valid，结构错误均为零。预注册比较要求
`corruption(D2) < corruption(D0)`，因此零对零不满足条件。绝对可用性指标通过，
比较优势没有得到确认；不能把两者合并写成“E2 通过”。

没有执行 `R+C → Supported/Unresolved`、ActiveO、Gap、Search/Find/Open 或 Writer。

## 主结果

Coverage 为按 critical=2、material=1 加权后对 response 取平均；两次重复固定，
等价于每个 qid 等权。Stability 要求两次都 strict-valid 且结构相同或兼容。
所有 planned slots 均保留在分母。

| 阶段 | Arm | Strict | Coverage | RelationErr | RoleErr | TemporalErr | DependencyRecall | Severe broad | Stability |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| E1 exposed dev | D0 | 18/20（90%） | 97.78% | 1/20（5%） | 0 | 0 | 100% | 0 | 8/10（80%） |
| E1 exposed dev | D1 | 20/20（100%） | 100% | 0 | 0 | 0 | 100% | 0 | 10/10（100%） |
| E1 exposed dev | D2 | 20/20（100%） | 100% | 0 | 0 | 0 | 100% | 0 | 10/10（100%） |
| E2 fresh | D0 | 24/24（100%） | 100% | 0 | 0 | 0 | 100% | 0 | 12/12（100%） |
| E2 fresh | D2 | 24/24（100%） | 100% | 0 | 0 | 0 | 100% | 0 | 12/12（100%） |

E1 D0 critical coverage：macro 97.50%、micro 97.06%；material micro 97.80%。
其余各组 critical/material coverage 的 macro、micro 均为 100%。依赖 recall 的
macro、micro 均为 100%。逐条分子、分母见各阶段 `METRICS.json`。

| 补充指标 | E1 D0 | E1 D1 | E1 D2 | E2 D0 | E2 D2 |
|---|---:|---:|---:|---:|---:|
| Invented semantics | 1/20 | 0/20 | 0/20 | 0/24 | 0/24 |
| Schema valid | 20/20 | 20/20 | 20/20 | 24/24 | 24/24 |
| Exact anchor valid | 不适用 | 20/20 | 20/20 | 不适用 | 24/24 |
| Harmful merge / split | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| 两次均 strict-valid 的 qids | 8/10 | 10/10 | 10/10 | 12/12 | 12/12 |
| 平均节点数 | 6.65 | 8.15 | 4.90 | 6.13 | 5.29 |

D1 的 163 个 prose nodes 在原题上下文中均获 `fully_supported` 判定。
部分短 anchor 含代词或省略主语，需要保留 Q/Source Unit 地址才能解释；这里没有
认证它们脱离原题后仍能独立表达完整关系。D2 的精确复制也不等于跨节点指代已消除。

## 门槛解释

E1 D2 通过全部绝对条件，比较条件通过的是“绝对结构错误率 ≤5%”这一分支。
实际相对 D0 的结构错误下降为 5pp，并未达到另一分支要求的 10pp。

E2 D2 全部绝对条件通过。唯一失败项是严格比较方向：D0=0、D2=0。
不增加样本、不修改 prompt、不放宽 gate，也不把敏感性结果替换主结果。

## 关键判例与敏感性

1. **明确改坏的关系：E1 Q1259，D0R1 / R017。** 原题要求另两名队友彼此同国籍，
   输出变成与澳大利亚 coder 同国籍。记录 relation-argument corruption 和 invented
   equality；没有把它泛化成所有多实体问题都会失败。
2. **歧义覆盖判例：E1 Q922，D0R2 / R050。** `another party` 在冻结参考的
   ruler-recipient 解读下丢失角色限制。若接受更宽的原文省略解读，D0 strict
   从 18/20 升至 19/20，stability 从 8/10 升至 9/10；E1 gate 不变。
3. **代词判例：E1 Q169。** `artist's songs` 被解释为原文自然的归属指代，未被
   当成“artist 创作了歌曲”的新增事实。更严格要求保留代词歧义的反事实结果单列。
4. **时间判例：E2 Q548，D0 的两次响应。** `a few years after 2021` 被接受为
   对紧邻上一句时间的自然解析，未确定具体 launch year。若把这种解析判为越界
   绑定，D0 会有 2/24 temporal corruption，E2 比较 gate 会通过。这个反事实说明
   结论对语义边界的敏感性；不能据此追认 PASS。主标签与主 FAIL 保持不变。
5. **粒度判例：E1 Q228 / R018、E2 Q523 / R036。** 一个人的多个身份线索可以
   合并，目标 building 或 series 链仍单列。若改用更严格的宽度标准，前者使 D2
   strict 变为 19/20，仍过 E1；后者降低 E2 D0 strict，仍不能满足结构错误比较条件。

这些都是明确标出的 reviewer-boundary counterfactuals，不是补充采样。
未修改冻结 reference 或首轮标注，未删除有歧义问题。完整结果见 `SENSITIVITY.json`。

## 对任务书 20 个问题的回答

1. **Free-form strict validity 多高？** 开发集 90%，fresh 100%。两组不能合并成
   无曝光问题上的一个泛化率。
2. **Source anchoring 是否减少 corruption？** 开发集从 1/20 降到 0/20，有小样本
   正向信号，支持点仅一个 qid；接受信件歧义不会改变这项结构错误计数。
3. **Extractive grouping 是否进一步减少？** 未观察到：E1 D1/D2 都是零；E2
   D0/D2 也都是零，D1 按协议未运行。
4. **D2 是否牺牲 coverage？** 未观察到；两阶段 critical/material coverage 都为
   100%。节点更少不能直接推断之后的 Claims 对齐会更容易。
5. **Relation-argument error 出现在哪类 Q？** 唯一明确实例是多人物的国籍比较
   关系，参与者被改写。没有足够事件数建立可靠的题型风险排序。
6. **Role identity uncertainty 能否保留？** 本轮 paper 的 JBSE/Harran 作者和
   fresh 的 first/corresponding-author 角色均未被强制等同或区分。归属代词的边界
   仍需要明确评价约定。
7. **Temporal attachment 稳定吗？** 主评估未见 critical temporal corruption。
   日期密集的疫苗/年报题及两篇文章题保留了对象归属；Q548 的相对时间有歧义，
   不应把零错误理解为所有时间绑定问题已解决。
8. **Downstream prerequisite 是否保留？** 各组 recall 均 100%，later article、
   interview/song、gift building 等描述性 referent 都保留了。这里只判断任务中
   是否表达该目标，并未判断当前研究是否已建立它。
9. **主要失败是 merge 还是 split？** 主评估两者均零，无法排序；看到的是粒度
   差异和少量边界判例，不能把“节点数多”直接算成 split failure。
10. **D2 错误是否从 rewriting 转成 grouping？** 没有观察到 D2 的 primary failure，
    因而没有证据确认错误发生了这种转移。只能说输出形式消除了自由 prose 改写，
    grouping 与指代风险依然可能存在。
11. **两次生成稳定吗？** 注册语义稳定性为 E1 的 80%/100%/100%，E2 两组均
    100%。若只认可 `same_structure`，E1 分别 30%/30%/70%，E2 分别 25%/66.7%。
    “稳定”依赖允许兼容细分，不能宣称节点边界完全固定。
12. **需要唯一 Gold grouping 吗？** 本轮不需要。D2 开发集 3/10、fresh 4/12 对
    重复是兼容的不同分组，仍各自有效。合理替代结构确实存在。
13. **Dev/fresh 方向一致吗？** 可用性方向一致；比较优势没有复制，fresh 出现
    错误率为零的基线下限，不能确认 D2 降低错误。
14. **Source anchoring 值得成为正式 runtime representation 吗？** 值得保留为可
    审计的候选表示，能够机械检查原文来源；本轮不足以证明它必须成为默认控制
    表示。应保留 Q/原文地址，不能把正确引用当作已完成状态对齐。
15. **需要 Lazy Expansion 吗？** 当前没有以 severe broadness 为依据的需求。
    合并条件能否支持精细 Claims masking，需另一个实验回答。
16. **需要 explicit `requires` 吗？** 没有；无需该字段即可保留本轮依赖 checkpoint。
    未来是否发生 downstream selection jump 尚未测试。
17. **需要 Binding IR 吗？** 没有证据支持现在增加。一次自由改写的关系错误不足以
    证明必须引入 IR；D1/D2 在本轮保存了该关系。
18. **值得 episode-stable reuse 吗？** 作为下一研究假设有价值。只应因明确的原题
    分解缺陷做显式版本修订，不能因候选失败或 Search 结果改变原题含义；runtime
    复用的控制效果尚未验证。
19. **现在有资格进入 `R+C → Supported/Unresolved` 吗？** 按本任务预注册的完整
    E2 gate，**没有自动进入资格**。绝对可用性结果使该方向有工程研究价值，但应
    在另一个明确授权、预注册的任务中处理“可用性”与“比较优势”的区别。本轮停止。
20. **仍需要 Direct `Q+C→O` 路线吗？** 本轮没有再测试它，不能宣告已替代它。
    Task semantics 与状态对齐分离是可继续验证的架构假设；两种路线的闭环效果
    仍缺少直接比较。

## 可解释范围

- 这是 single-reviewer、允许语义兼容分组的小样本研究，无独立第二 reviewer 或
  inter-rater reliability。Extractive 文风可能暴露 arm，masking 仅为部分隐藏。
- 开发题已多次曝光。Fresh 只指在保守的 repository 文本曝光审计中未进入历史
  实验；不是 foundation-model-unseen。审计扫描 17,063 个文本文件，排除 229 个
  qid，从 567 个机械合格问题按固定种子取 12 个。未使用答案选题。
- D0 也获得相同 Source Units 和完整的语义保持 prompt。它不是无结构提示的裸 Q
  baseline。结构化输入和任务变简单都可能使本轮出现高分。
- 与历史 `Q+C→O` 不同，本轮允许同时保留全部题目条件，不需要选择一个当前
  obligation。因此不能把 90–100% 与历史 46–54% 作直接因果提升比较，也不能
  据此断言旧瓶颈已经定位到某一个组件。
- 原题内容成为 task requirement，不代表实际 evidence 已支持它。没有 Claims
  输入、没有 evidence promotion 或检索收益方面的新证据。

## 执行成本与完整性

| 指标 | E1 | E2 | 合计 |
|---|---:|---:|---:|
| Planned / sent / returned | 60 / 60 / 60 | 48 / 48 / 48 | 108 / 108 / 108 |
| Input tokens | 47,500 | 39,296 | 86,796 |
| Completion tokens | 366,516 | 172,793 | 539,309 |
| 其中 reasoning | 346,192 | 162,863 | 509,055 |
| Total tokens | 414,016 | 212,089 | 626,105 |
| Cache hit tokens | 23,165 | 20,860 | 44,025 |
| Cache miss tokens | 24,335 | 18,436 | 42,771 |
| 加权 cache hit rate | 48.77% | 53.08% | **50.72%** |
| Median / P95 / max latency (s) | 23.62 / 43.81 / 47.54 | 14.15 / 29.04 / 45.24 | 见分阶段 |
| Peak concurrency | 8 | 8 | 8 |
| 调用窗口 wall time (s) | 242.41 | 144.67 | 387.08 |

HTTP、transport、JSON/schema、anchor、length 失败均为 0；usage 缺失为 0；
retry、repair、replacement 为 0。Reasoning 已包含在 completion 中，没有重复
计入 total。未核验供应商单价，不报告推测的货币金额。

E1 D2 completion 为 116,464 tokens，高于 D0 的 80,985；“少生成”指少生成
authoritative prose，不意味着更少的总推理 token。E2 D2/D0 completion 分别为
84,567/88,226；不能把单次窗口的成本差异当作稳定性能优势。

34 个冻结文件、18,076 个历史文件哈希核验通过；请求、原始响应解析、usage 和
语义算术均可回放。首轮标注保持 commit 时的字节。详见 `INTEGRITY.json`、
`FINAL_VALIDATION.json`、`EXECUTION_ACCOUNTING.json` 和各阶段 review artifacts。

**当前可支持的判断：Q-only canonicalization 可行；fresh comparative superiority
尚未得到确认。研究在此停止，保留这个区别。**
