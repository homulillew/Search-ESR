# H1 / H2 / H3 正式预注册

本文件在**任何新的真实模型调用之前**写定，是本轮（v3b）实验的预注册依据。
三个 hypothesis 的措辞、可观测预测、判定规则一经冻结即不得改动；若后续要改，
必须另写一个 hypothesis 文件并声明替换关系，不得回头修改本文件。

## 待解释的现象

`search_find_v3a` 首轮（`RESULTS.md`，已复核，见
`../search_find_v3a/AUDIT_SECTION7A.md`）：

- `find` 机制层面正确（offline gate 43/43；对 docid 38231 实际执行
  `find('turned professional')` 返回 [642, 2157)，覆盖题目三条约束），但
  **88 次工具调用里 0 次被选用**。
- 定位缺口真实存在：qid 546 的正确答案就在已发现的文档里，落在 400-token
  preview 窗口之外；qid 1094 的 docid 5400 / 26092 全文含 Pirlo，但 preview
  从未覆盖。
- 把「该用 find 的边界」写进工具 description（v3a 第 6 节 affordance probe，
  variant B），find 采用率仍停在噪声水平（A 0/50 vs B 1/50，Fisher p=1.0）。
  该 probe 的噪声底由 variant A 与原 run 逐字节一致这一锚点定为约 10% 非 search。

所以问题不是「find 坏了」或「没讲清楚 find 能干嘛」，而是「模型为什么不选用」。
三个竞争解释如下。

---

## H1：Tool Competition / Action Dominance

**陈述**：模型**有能力**用 Find，但 Search 在动作空间里的即时回报更大、功能覆盖
更广，因此 Search 压制了 Find。

**机制（本仓库里可检验的具体形式）**：v3a 的 Search 并非纯全局召回。读
`llm_chat/raw_windows.py` 可见 `search()` 的管线是「全局检索 → 逐文档 chunk
本地定位 → `_repair_anchor` → `_expand` → 400-token preview」；`find()` 走的是
**同一条**本地定位管线，只是输入从「query + 语料」换成「query + 已知文档」。
也就是说在 v3a 里 **Search ⊃ Find**：Search 的返回里已经内含一次 query-localized
的文档内定位（preview W#）。对「下一步该做什么」这个决策点，Find 在功能上被
Search 严格包含，只在「已经知道是哪篇文档、且只想换一段」时才有边际价值——
而这个边际情境恰好被「再搜一次」近似覆盖了。

**可观测预测（P1）**：把 Search 从动作空间里移除、其余一切不变，Find 会**显著**
进入分布。极端形式：即使 Find 是唯一能拿到新信息的工具，模型也会大量改用 Find。

**反预测（P1⁻）**：移除 Search 后模型不是改用 Find，而是（a）直接用参数记忆
作答（answer-stop 上升），或（b）在 free text 里反复表达「想 search 但没有」
却不去 find，或（c）find 采用率仍落在噪声区间。

**H1 不预测什么**：H1 不预测 Find 拿到的窗口有没有用。H1 只管「采用」。
「移除搜索后 find 起飞但拿回的是垃圾」与 H1 相容，与 H2 也相容——这正是
Experiment 2（而非 Experiment 1）要分开测的东西。

---

## H2：Verification State 缺失

**陈述**：即使解除 Search 的竞争，模型仍然极少用 Find，因为它缺少从
「Candidate Discovery」切换到「Candidate Verification」所需的**控制状态**。
模型不是不知道有 find，而是在它当前的推理状态里，根本没有「我现在该去验证
某个已有候选」这一格位置可以放 find 这个动作。

**机制（首轮证据）**：`RESULTS.md` 第 7(b) 节——模型在 reasoning 里**明确写出过
正确解读又明确放弃**（qid 1094：引用 D37 的 1908 分裂记载判定 "Inter fits"，
把 Andrea Pirlo 列为候选约 15 次，然后转向编造的 Fenerbahçe/Galatasaray 叙事，
以 "This fits all clues precisely." 收尾）。这不是「没找到线索」，是拿着线索
不验证。affordance probe 里唯一的 find（`find(D11, "Messi free-kick 95th minute")`）
形态正确，但 reasoning 显示是在**锁定错误答案之后用来确认先验**，不是用来检验
替代候选——即「验证」这个动作即使出现，动机也是加固而非检验。

**可观测预测（P2）**：解除 Search 竞争**不足以**让 Find 进入分布；Find 采用率
仍落在噪声或低区间。补上最小 Verification State（只有「当前未解决的需求 +
有希望的已有文档/候选 D#」两项）后，Find 采用率才上升，且上升的 Find 主要是
exploratory_find 而非 confirmation_find。

**H2 与 H1 的关系**：两者不互斥。H1 说的是动作空间的**供给侧**竞争，H2 说的是
**需求侧**缺失。可能两者都真：Search 压制了 Find，同时即使解除压制也缺验证动机。
预注册的判定规则（下文）必须能把「两个都真」这个结果读出来，而不是逼着选一个。

---

## H3：Find 的名称 / API 形态 / 模型先验

**陈述**：问题在 Find 这个工具的**呈现**本身——名字、参数形态（`find(D#, query)`）、
或模型对这类工具的先验习惯——而不是动作空间竞争，也不是验证状态。

**本轮明确置后**：H3 **只在 H1 与 H2 都检验完之后**才允许动（见
`EXPERIMENT_PLAN.md` 阶段 4 的 `scoped_search`）。理由：H1/H2 是机制假设，可以用
既有 checkpoint 零成本检验；H3 的检验要么改工具名（破坏与冻结 v3a 的可比性），
要么加 `scope` 参数（属于协议变更），代价与污染风险都高。在 H1/H2 未定之前
动 H3，会把「工具形态」与「动作空间/验证状态」三个变量混进同一批结果。

---

## 判定规则（预注册）

Experiment 1（Tool Competition Upper-Bound Probe）的主指标是**首个动作**，
分类为 `search` / `find` / `open` / `answer-stop` / `invalid` / `other`。
Search 类必须**单列**「free-text search attempt」：Arm B/C 不提供 search 工具，
所以这一类只能是模型用文字表达全局检索意图（含调用一个不存在的工具名、或在
reasoning 里声明要 search），要单独计数，不得与真正的 search 调用混同。

`find` 必须二分（分类依据 = reasoning 尾部 + find 的 query，不含 gold）：

- **exploratory_find**：调用时候选/约束**尚未**定盘——find 用来检验、比较、
  或定位一个还没被锁定的信息。
- **confirmation_find**：调用时答案**已经**锁定，find 只是在确认先验。

> **confirmation_find 不得计为同等成功。** 它是「加固」不是「验证」，与 H2
> 描述的现象同源。所有判定区间只对 exploratory_find 施加。

以 **Arm C 的 exploratory_find 计数**（10 checkpoint × 5 样本 = 50）为准，
Arm A 保持在 0 附近：

| 信号强度 | 条件 | 预注册的下一步 |
|---|---|---|
| **强** | Arm C exploratory_find ≥ 15/50，且分布在 ≥ 5/10 个 checkpoint 上 | H1 成立：Search 确实在压制 Find。进入 **Experiment 2**（v3b orthogonal search）。 |
| **中** | Arm C exploratory_find 5–14/50 | 证据不足以判 H1 成立，但不足以排除。进入 **Experiment 2**，同时**保留 H2**（Verification State）作为并行的待检假设。 |
| **弱** | Arm C exploratory_find ≤ 4/50 | 停止把低采用率归因于 Search dominance。跳到 **Experiment 3**（Verification State）。 |

边界情形与额外读法（同样预注册，避免事后解释）：

- **Arm B 高、Arm C 低**：说明缺的不是动机而是「知不知道 search 没了」——
  这既不是纯 H1 也不是纯 H2，归为 H1 的弱形式 + 信息可见性问题，按「中」信号
  处理（进 Experiment 2），并在结果里明确记为 Arm B/C 分离。
- **Arm C 的增量主要变成 confirmation_find**：即使 find 计数高，只要
  exploratory_find 仍 ≤ 4/50，判为**弱**信号——这正是 H2 所预测的形态，
  不是 H1。
- **Arm B/C 的增量主要变成 answer-stop**：解除搜索没有让模型转向本地工具，
  而是转向参数记忆。这是 H1⁻ 的直接观测，判为**弱**信号，跳 Experiment 3。
- **invalid 类 ≥ 10/50**：说明协议边界本身在 B/C 下不成立（例如模型大量尝试
  调用不存在的 search 导致 API 报错），**实验作废**，先修协议边界再重跑，
  不得把 invalid 计入任何一侧。
- Fisher 精确检验与置信区间**允许**报告，但 p 值不得替代机制解释；任何结论
  必须能用 reasoning 尾部复述出来。

---

## 与首轮结论的衔接

首轮 affordance probe 回答的是「description 讲得不够清楚吗」，答案是不是。
本预注册把问题往前推一格：**在 description 已经讲清楚的情况下，是动作空间里
有更强的 Search（H1），还是根本没有「该验证了」这个状态格（H2）**。

H1 的 Supply-side 机制有一个首轮没有直接检验的强预测可以现在就说清：
因为 v3a 里 Search ⊃ Find，**Arm B/C 下模型如果真的想「再搜一次」，它没有等价
动作可做**——这正是 H1 所说的压制被解除的形态。若此时 find 仍不起来，压制就
不是主因。
