# 阶段 1 打标与判定：Tool Competition Upper-Bound Probe

probe_id: `20260922T174605.704525Z`
脚本：`../tool_competition_probe.py`
样本：10 checkpoint × 3 arm × 5 样本 = 150 条（B、C 各 50 条为**新调用**共 100 次；
A 50 条**复用** v3a affordance probe `20260922T141730.317105Z`，未重新采样）。
**未执行任何工具**（probe 只调用 `chat.completions.create`）。

---

## 1. 主指标：首个动作（按 arm）

| 分类 | Arm A `as_is` | Arm B `search_hidden` | Arm C `local_only_coherent` |
|---|---|---|---|
| `search`（真实工具调用） | **45/50** | — | — |
| `search`（free-text / 未声明工具） | — | **41/50** | **36/50** |
| `find` | **0/50** | 2/50 | 4/50 |
| `open` | 1/50 | 1/50 | 3/50 |
| `answer-stop` | 4/50 | 6/50 | 7/50 |
| `invalid` | 0/50 | 0/50 | 0/50 |
| `other` | 0/50 | 0/50 | 0/50 |

按 HYPOTHESES.md 的要求，Arm B/C 的 `search` 类**单列**：那不是工具调用——
`search` 不在 B/C 的 tools schema 里。它是模型对一个**未被声明的工具名**发出的
function call（见 §4，这是本批次最重要的单一观测）。

Arm A 的 45/50 是真实 search 调用，与 v3a 原始 run 的行为一致，作为噪声锚点。

### 逐 checkpoint（find 计数 / 样本数）

| qid | seq | A | B | C |
|---|---|---|---|---|
| 546 | 9 | 0/5 | 1/5 | **2/5** |
| 546 | 17 | 0/5 | 0/5 | 0/5 |
| 546 | 25 | 0/5 | 0/5 | 0/5 |
| 546 | 33 | 0/5 | 0/5 | 0/5 |
| 546 | 41 | 0/5 | 0/5 | 0/5 |
| 1094 | 23 | 0/5 | 0/5 | 0/5 |
| 1094 | 34 | 0/5 | 0/5 | 0/5 |
| 1094 | 45 | 0/5 | 1/5 | **1/5** |
| 1094 | 53 | 0/5 | 0/5 | **1/5** |
| 1094 | 61 | 0/5 | 0/5 | 0/5 |

Arm C 的 find 只落在 **3/10** 个 checkpoint（546:9、1094:45、1094:53），
**不满足**「强」信号要求的 ≥5/10 checkpoint 分布。

---

## 2. find 的二分：exploratory vs confirmation

判定依据 = reasoning 尾部 + find 的 query（**不含 gold**）。
共 6 次 find（B 2 次、C 4 次）。**6/6 全部为 exploratory_find，0 次 confirmation_find。**

> 判定规则（HYPOTHESES.md）：`exploratory_find` = 调用时候选/约束**尚未**定盘；
> `confirmation_find` = 答案**已经**锁定，find 只是在确认先验。

### ① arm=B 546 seq=9 sample=2 — find(D5, "2023")

reasoning 尾部逐字（节选）：

> Among these, those with >3 147s: Williams (4), Bingham (4), Selby (5), Trump (7).
> Let's search within D5 for "2023" to see his match history.
> Also, let's search for "less than 250 centuries" in general. …
> Let's try finding the exact phrase in D5 first.

**判定：exploratory。** 候选仍是 7 人清单（Bingham/Williams/Selby/Trump/Murphy/Robertson/Carter），
find 用来在 D5 内部**区分**尚未锁定的候选，不是确认某个已定答案。

### ② arm=C 546 seq=9 sample=2 — find(D5, "2023 4-3 4-0")

> Also, I should check if there's another player who fits better. "turned professional
> between 1995 and 2006". Mark Williams (1995), Stuart Bingham (1995), Mark Selby (2003),
> Judd Trump (2005). … Let's find Mark Williams' 2023 record in D5.

**判定：exploratory。** 原文明说 "check if there's another player who fits better"——
find 是在**比较**替代候选。

### ③ arm=C 546 seq=9 sample=4 — find(D5, "4-3 4-0 2023")

> So it's definitely Selby, Trump, Bingham, or Williams. Let's check their 2023 runs
> in the **WST Pro Series** or **Championship League**. …
> Let's try finding within D5 (Mark Williams) for "4-3" or "decider".

**判定：exploratory（本批最接近边界的一例）。** "definitely … or" 是一个 **4 元析取**，
不是锁定单一答案；query 针对的是 4 人中的 Williams，目的仍是区分。按预注册定义
（"答案已经锁定"指单一候选定盘），4 选 1 未定盘 → exploratory。
**边界情形如实记录**：若把"候选集收窄到 4 人"算作锁定，这一条会移入 confirmation，
Arm C exploratory_find 变为 3/50，结论（弱信号）不变。

### ④ arm=B 1094 seq=45 sample=3 — find(D14, "95th minute free-kick")

> Is there another famous 95th minute free kick?
> Maybe **Totti**? Maybe **Crosas**? Maybe **Zlatan Ibrahimovic**?
> … D14 (Last-minute goal) has a list. Let's check D14 more carefully.

**判定：exploratory。** reasoning 明确在**列举替代解释**，find 用来检验它们。

### ⑤ arm=C 1094 seq=45 sample=3 — find(D40, "discord OR free-kick OR 95th minute OR iterations")

> This might be the source of the riddle if it's there. Let me check the content of D40
> or search within it for "discord" or "95th minute".

**判定：exploratory。** "might be … if it's there" 是一个**未经检验的假设**，
find 就是去检验它。

### ⑥ arm=C 1094 seq=53 sample=1 — find(D37, "split caused by internal disagreements over the signing of foreign players")

> "Born out of discord among two parties" -> **Inter Milan** (founded after a schism
> with AC Milan). … Let's consider **Totti**. Let's consider **Crosas**?
> Let's consider **Liberatore**? Let's consider **Pirlo**?
> … Let's use find on D37 (AC Milan - Wikipedia) which mentions the split that formed Inter.

**判定：exploratory（六例中最需论证的一例）。** "Inter Milan" 是**子线索的假设**，
不是题目答案；题目问的是「哪场早期 21 世纪比赛 / 谁罚的 95 分钟任意球」，而
reasoning 在 find 前后一直在 Totti / Crosas / Liberatore / Pirlo 之间循环，**完全未锁定**。
find 在这里的作用是检验「D37 是否真的支持 1908 分裂这一读法」——这是**验证假设**，
不是确认已定答案。值得注意的是这正是 v3a 首轮被明确放弃的那条正确解读路径
（`../search_find_v3a/RESULTS.md` §7(b)），在本批里它**以 exploratory find 的形态回来了**，
但只在 1/50 条样本里出现。

### 二分小结

| | B | C | 合计 |
|---|---|---|---|
| exploratory_find | 2/50 | **4/50** | 6/100 |
| confirmation_find | 0/50 | 0/50 | 0/100 |

---

## 3. 统计（允许报告，不替代机制解释）

| 比较 | Fisher 双侧 p |
|---|---|
| A(0/50) vs C(4/50) find | 0.1175 |
| A(0/50) vs B(2/50) find | 0.4949 |
| B(2/50) vs C(4/50) find | 0.678 |
| A(0/50) vs B+C(6/100) find | 0.179 |
| A(45/50) vs C(36/50) 未声明 search | **0.0395** |
| A(45/50) vs B(41/50) 未声明 search | 0.3881 |

- Arm C exploratory_find = 4/50，Clopper-Pearson 精确 95% 上界 = **17.4%**。
- Arm B find = 2/50，95% 上界 = 12.1%。
- 本批 100 次新调用：输入 2,852,830（其中命中缓存 2,402,944）+ 输出 199,405。
  按 ¥0.02/M（缓存输入）、¥1/M（未缓存输入）、¥4/M（输出）≈ **¥1.30**。

**显著性说明**：唯一 p < 0.05 的比较不是 find，而是「未声明 search 调用」
（A→C）。按 HYPOTHESES.md 的规定，p 值不得替代机制解释；§4 给出机制读法。

---

## 4. 本批最重要的观测：模型对「未声明的工具」发出 search 调用

Arm B/C 的 41/50 与 36/50 首个动作是 **function call，name = `search`**，
而 `search` **不在它们的 tools schema 里**。原始 events 里的实际名字计数：

| arm | 返回的 tool_call 名字 | 次数 |
|---|---|---|
| B | `search` / `find` / `open` | 80 / 3 / 1 |
| C | `search` / `find` / `open` | 79 / 4 / 4 |

（上表是全部 action，含非首个动作；首个动作口径见 §1。）

provider 接受了未声明的函数名，返回 `finish_reason=tool_calls`，所以这些调用
**没有**进入 `invalid` 类（invalid = 0/50，未触发「invalid ≥10/50 则实验作废」的规则）。

几个例子（arm=B, seq=9，逐字）：

- search({"query": "snooker \"4-3\" \"4-0\" 2023"})
- search({"query": "snooker \"over 400 centuries\""})
- search({"query": "Mark Selby 2023 \"4-3\" \"4-0\" \"decider\""})

**机制读法**：把 `search` 从 tools schema 里移除，**并没有把它从模型的动作分布里移除**。
首个动作分布几乎没动——A 真实 search 45/50 → B 未声明 search 41/50 → C 未声明 search 36/50。
也就是说，这个 probe 实际测的是「当 search **不被声明**时模型做什么」，
而不是「当 search **不可用**时模型做什么」。provider 层不拦截未声明函数名，
所以「移除工具」这一干预在行为层面被绕过了。

这对 H1 的供给面机制是一个**直接的、方向不利于 H1 的证据**：如果 next-action 选择是
在**已声明**工具之间的理性竞争，移除 search 应该迫使流量重分布到 find / open / answer-stop。
实测是重分布到「对不存在的工具发调用」。模型的下一步动作策略对 tools 菜单
**几乎不敏感**——它对 search 的偏向不在「可选工具里有更好的」这一层，
而在策略层先验（这部分先验明显由 checkpoint prefix 里大量成功的 search→preview 循环强化）。

---

## 5. 应用预注册的判定区间

主判据（HYPOTHESES.md）：**Arm C 的 exploratory_find 计数**。

| 信号强度 | 条件 | 本批实际 |
|---|---|---|
| 强 | ≥15/50 且 ≥5/10 checkpoint | 否（4/50，3/10） |
| 中 | 5–14/50 | 否（4/50） |
| **弱** | **≤4/50** | **是：4/50** |

预注册的边界读法逐条核对：

| 边界情形 | 本批是否触发 | 结论 |
|---|---|---|
| Arm B 高、Arm C 低 | 否（B 2/50 < C 4/50，方向相反） | 不适用 |
| 增量主要变成 confirmation_find | 否（6/6 全为 exploratory，0 次 confirmation） | 不适用 |
| 增量主要变成 answer-stop | 否（A→C：find +4 > answer-stop +3 > open +2） | 不适用 |
| invalid ≥ 10/50 | 否（0/50） | 不适用 |

**判定：弱信号。** 按预注册的下一步：**停止把低采用率归因于 Search dominance，
跳到 Experiment 3（Verification State Probe）。**

### 必须如实记录的两个限定

1. **4/50 卡在弱/中边界上。** Clopper-Pearson 95% 上界 17.4%，区间跨进「中」
   甚至触及「强」的下沿。数据与 0% 到约 17% 之间的任何真实率都相容，
   **不能**证明真实率 ≤4%。这里判「弱」是**按预注册规则对观测计数施加判据**，
   不是对真实率的证明。若后续实验要引用本结论，应引用「点估计落在弱区间，
   上界进入中区间」这一完整表述。

2. **§4 的观测削弱了本 probe 对 H1 的检验力，但不推翻它。** 「移除声明工具」
   并未真正移除动作，所以本 probe 测的是**声明菜单**层面的竞争，不是**可达性**层面的竞争。
   真正能让 search「不产生回报」的干预是阶段 2 的 orthogonal search
   （命中已发现文档 → `already_discovered` + 无新 W#、无新原文）。
   因此**存在一个预注册之外的论证**支持「下一步本应是 Experiment 2」。
   本批按预注册走 Experiment 3；但 §4 的这个论证应当随结果一起保留，
   若 Experiment 3 也给出弱信号，阶段 2 的 orthogonal search 就是唯一还没被
   排除的 H1 检验形态，到时必须补做。

---

## 6. 阶段 1 的净结论

1. `find` 采用率在解除 search 声明后**没有离开弱区间**（C exploratory 4/50，
   3/10 checkpoint）。
2. 解除声明的**主要效果不是**转向本地工具，而是转向**对未声明工具的 search 调用**
   （B 41/50、C 36/50）。这是 H1 反预测 P1⁻ 的一个比预注册措辞更强的形态：
   模型不是在 free text 里「表达想 search」，而是**直接发出对不存在工具的调用**。
3. 出现的 6 次 find **全部是 exploratory**，0 次 confirmation——这一点**不支持**
   H2 所描述的「find 只被用来加固」的形态，反而说明一旦 find 出现，它的动机是检验。
   但 6/100 的基数太小，只能作为弱观察，不能反过来判 H2 不成立。
4. 唯一在 Arm C 里出现的 D37「1908 分裂」exploratory find（1094 seq=53，sample 1）
   是 v3a 首轮被明确放弃的正确解读路径。它是 1/50，但说明**正确路径在本地工具下
   可以被重新进入**——这是 Experiment 3（Verification State）值得做的直接理由。

**下一步：Experiment 3（Verification State Probe）。**
