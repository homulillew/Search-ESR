# Search-Find v3a 首轮结果

按 CLAUDE_NEXT.md 第 11 节输出。四轮 rollout 已按第 3 节固定交错调度全部完成
（546A → 1094B → 546B → 1094A），本文件回答七个规定问题，不只报 Accuracy。

**范围声明**：n = 2 题 × 2 协议，按第 2 节属开发/诊断轮次，**不支持任何推广性结论**。
两题都是历史 bad case，不是随机抽样。

## 结论先行

- `find` 在机制层面正确，但**一次都没被调用**（0/88 次工具调用）。
- 因此「Find 是否产生新窗口」「新窗口是否成为有效 Evidence」两个问题**无样本，不适用**。
- 重复 global Search **没有减少**：qid 546 两协议完全持平，qid 1094 上 v3a 反而是
  baseline 的 4 倍搜索量、6.6 倍 tokens。
- 但本批最重要的发现不是「Find 没用」：**定位缺口真实存在**，qid 546 的正确答案就在
  模型已经发现的某一篇文档里，只是落在 400-token preview 窗口之外，`find` 本可以
  逐字取回。瓶颈是工具采用（grounding 意愿），不是工具能力。
- 第 6 节的 Tool Affordance probe 已验证这一点：把「该用 find 的边界」写进工具
  description，find 采用率仍停在噪声水平（A 0/50 vs B 1/50）。缺的不是工具说明，
  是验证动机。
- 4/4 答案实体错误，0/4 abstain，4/4 解释无支撑。

## 第 4 节：机制明细

四轮全部 `natural_answer`，无 tool error，无 invalid ref。

| # | qid | 协议 | api_responses | search | find | open | err | rows | docs | ≥2次搜索 | 额外返回 | 全局重定位 | prompt tok | total tok | 耗时s | 答案字数 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 546 | baseline | 6 | 12 | – | 0 | 0 | 60 | 21 | 14 | 39 | 11 | 161 288 | 176 756 | 198.9 | 1223 |
| 2 | 1094 | v3a | 37 | 76 | **0** | 0 | 0 | 380 | 84 | 49 | 296 | 28 | 5 483 308 | 5 621 311 | 1275.1 | 1801 |
| 3 | 546 | v3a | 7 | 12 | **0** | 0 | 0 | 60 | 19 | 14 | 41 | 10 | 156 012 | 168 970 | 175.4 | 1146 |
| 4 | 1094 | baseline | 20 | 19 | 0 | 0 | 0 | 95 | 43 | 17 | 52 | 5 | 829 082 | 863 784 | 389.8 | 1098 |

- `search_result_rows` = 每次 search 返回的行数合计；`docs` = 出现过的不同文档身份
  （baseline 用 docid，v3a 用 D#）；`≥2次搜索` = 被多于一次全局 Search 返回的文档数；
  `额外返回` = 这些文档被重复返回的总次数减一；`全局重定位` = 同一文档被更晚的
  Search 以此前未出现过的 window 返回。
- 「Search 后第一次 Find 的时机」「Find 后是否仍立即围绕同一需求继续 global Search」：
  无 find 调用，两项均不适用。
- `find_no_match` = 0、`invalid_ref_calls` = 0、`local_find_relocation` = 0，全部因为
  find 从未进入候选动作（不是调用了失败）。

跨协议的重定位文档对照（D# 已折算为 docid）：

| qid | baseline 重定位 | v3a 重定位 | 两者交集 |
|---|---|---|---|
| 546 | 11 个 | 10 个 | **7 个**（16091, 1779, 42120, 4975, 55362, 60119, 64519） |
| 1094 | 5 个 | 28 个 | 3 个（26092, 40607, 67205） |

qid 546 上重定位压力在两协议间高度一致：同一批 7 篇文档被两次以上全局 Search
以不同窗口重复返回，v3a 一点都没有吸收掉。

qid 1094 上 v3a 的 76 次 search 里只有 42 个不同查询；query 58–76 退化为两个
近乎相同的字符串交替循环：

```
58 'match "born out of discord" OR "born of discord"'
59 '"born out of discord" OR "born of discord" OR "created out of discord" sport'
60 'match "born out of discord" OR "born of discord"'
...（交替到 76）
```

## 第 11 节：七个问题

### 1. Tool capability 是否机械正确 —— 是

- `offline_gate.py` 43/43 通过；`tests/test_chat.py` 20 passed；`tests/` 393 passed；
  `run_rollout.py --help` 正常（冻结记录见 FROZEN_STATE.md）。
- 已核对 1094B 的首个 api_request：`tools` 数组为 `['search', 'find', 'open']`，
  `find` 的 description 与参数 schema 与冻结哈希 `60de1d45…` 一致，没有被削减。
- 88 次 v3a 工具调用 0 次 `tool_error`。
- D# 注册表稳定：1094B 的 84 个 D# 各自唯一映射到 `(docid, document_sha256)`；
  546B 的 19 个 D# 同理。同一 docid 在不同查询下复用同一 D#（如 1094B 中
  docid 40496 始终是 D3）。
- 隐私边界保持：`docid` / `document_sha256` 从未出现在模型可见的 result JSON 里，
  只在 `tool_internal` 的 audit 中。

### 2. 模型是否实际选择 Find —— 否，一次都没有

- 1094B：0/76；546B：0/12。合计 **0/88**。
- `find` 在每个 request payload 中都存在（第 1 点已核对），所以不是工具没被暴露。
- `find_no_match` = 0 且 `tool_error` = 0：不是「调了但失败」，而是从未进入候选动作。
- 模型的动作分布与 baseline 完全同构：只 search，不 open，不 find。

### 3. Find 是否产生新窗口 —— 不适用（无）

- `local_find_relocation` = 0，按构造如此（find 未被调用）。
- 546B 的 41 个 W#、1094B 的 120 个 W# **全部来自 search preview**。
- 没有任何一个 W# 是 find 创建的。

### 4. 新窗口是否形成有效 Evidence —— 不适用（无样本）

第 5 节要求的四项标注（是否含题目约束事实 / 是否只是重复已有原文 / 是否改变候选或
判断 / 是否解决历史 repeated Search 想解决的同一信息需求）**没有可标注对象**。

### 5. 是否减少重复 global Search —— 否，两个方向都是负结果

- **qid 546（持平）**：两协议都是 12 次 search、60 行结果、14 个文档被多次返回。
  额外返回 41（v3a）vs 39（baseline）。7 个文档在两协议下都被全局重定位。
- **qid 1094（变差）**：v3a 76 次 search vs baseline 19 次（4.0×）；唯一查询
  42/76；query 58–76 退化为双字符串交替循环；额外返回 296 vs 52（5.7×）；
  prompt tokens 5.48M vs 0.83M（6.6×）；耗时 1275s vs 390s（3.3×）。
- find 吸收的重定位压力 = 0。
- 注意方向：加 find 之后搜索量反而上升，与「工具可用导致提前停止」或「工具可用
  导致改用 find」都不符；最接近的解读是 find 对模型的策略完全不可见（见问题 7）。

### 6. 最终答案是否变化 —— 变了，但没有变对

| run | 答案 | gold | 实体正确 | abstain | 解释无支撑 |
|---|---|---|---|---|---|
| 546 A（baseline） | Judd Trump | Ding Junhui | ✗ | 否 | 是 |
| 1094 B（v3a） | Selçuk İnan | Andrea Pirlo | ✗ | 否 | 是 |
| 546 B（v3a） | Neil Robertson | Ding Junhui | ✗ | 否 | 是 |
| 1094 A（baseline） | Lionel Messi | Andrea Pirlo | ✗ | 否 | 是 |

- 4/4 实体错误，0/4 abstain，4/4 解释无支撑。答案在两协议间确实变了
  （546: Trump→Robertson；1094: Messi→İnan），但都离开 gold 更远而非更近。
- 不能据此说 find 改善或损害了正确率：n=2/协议，且两题的正确检索路径在两协议下
  都不完全可达（见问题 7c）。

### 7. 新的主要 failure —— grounding（证据识别/信念更新），不是工具能力

分三层。

**(a) 定位缺口真实存在 —— 这是本批最重要的发现**

qid 546：docid 38231（Ding Junhui - Wikipedia，75 871 字符）在**两协议下都被发现**
（546B 中为 D17，被返回过 4 次）。该文档中一段相邻文字同时覆盖题目三条关键约束：

> In 2003, Ding turned professional at the age of 16. … During his career, he
> has compiled more than 600 century breaks, including seven maximum breaks,
> in professional play.

- 「1995–2006 之间转职业」→ 2003 ✓
- 「more than 300 centuries」→ 600+ ✓
- 「highest break more than 3 times」→ 7 次满分 ✓

但 400-token preview 从未覆盖这段（该文档的 4 个 preview 窗口里，「centur」只
出现 1 次，「turned professional」0 次）。**`find(D17, ...)` 本可以逐字取回这段**。

qid 1094：模型两轮合计看到的 43 个文档中，docid 5400（List of Inter Milan records
and statistics）与 26092 的**全文**含 Pirlo，但 preview 窗口从未覆盖。同样是
「文档已发现、事实在窗外」。

→ 工具要补的缺口确实在；问题不在「该不该做 find」，而在「模型不去用」。

**(b) 模型拿着正确线索丢弃**

- qid 546：preview 中 "Ding Junhui" 出现 16 次（A）/ 11 次（B），reasoning 中也
  反复出现。546A 的丢弃理由是「Trump is English and the 'less than 250 centuries'
  phrasing is common in English Wiki pages discussing English/Aus/Welsh players」
  ——纯语言学偏见；546B 的 reasoning 以「No hallucination. Uses provided
  constraints logically.」收尾，然后给出错误答案。
- qid 1094：模型在 reasoning 中数十次正确判定「born out of discord」= Inter
  （seq 118 明确引用 D37 的 1908 分裂记载：「D37 mentions 'In 1908, Milan
  experienced a split caused by internal disagreements… forming…
  Internazionale.' So Inter fits」），并把 **Andrea Pirlo 列为候选约 15 次**。
  但它从未用 find/open 回到 D37 或任何 Inter 文档验证任何候选，最后转向参数记忆
  编造的 Fenerbahçe/Galatasaray 2011 德比叙事，以「This fits all clues
  precisely.」收尾。正确解读被明确写出过，又被明确放弃。

**(c) 检索侧另有缺口（本轮按边界不可动）**

- docid 54472（Andrea Pirlo - Wikipedia，63 397 字符，「known for his vision,
  technique, creativity, passing and free kick ability」）在语料库中，但 380 行
  检索结果里从未出现。
- 「born out of discord」在全部 100 195 篇文档中 **0 命中**——题目措辞是合成的，
  不能靠字面召回，必须先识别隐喻再定位。

**综合**：主要 failure 是 grounding。模型把参数记忆里冒出来的候选当作证据，而不是
把已发现文档里的原文当作证据。`find` 改变的是「能不能移到文档内别处」，真正的瓶颈
是「模型想不想去验证」。这与第 6 节的「两题都不调用 Find」分支完全对应。

## 第 6 节：分支判定

命中 **「两题都不调用 Find」**。按计划先排除「Find 其实没用」的误判：重复 global
Search 仍然显著存在（qid 546 上 7 个文档在两协议下都被全局重定位；qid 1094 上
v3a 干脆 76 次 search）。结论：**不是没有重定位压力，是压力没有被工具吸收**。

按第 6 节的既定动作，做了**固定 checkpoint 的 Tool Affordance probe**：

- A：当前 v3a 工具说明；
- B：只强化通用边界「找同文档另一个事实用 Find；当前段落缺上下文才 Open」；
- 不执行工具，只比较下一动作。

已完成。10 个 checkpoint（每 run 最早 5 个）× 2 variant × 5 独立样本 = 100 次重放，
结果与结论见 `probe_tool_affordance/PROBE_RESULTS.md`。摘要：

| variant | search | find | open | 停下作答 |
|---|---|---|---|---|
| A（冻结说明） | 45/50 | **0/50** | 1/50 | 4/50 |
| B（强化边界） | 45/50 | **1/50** | 1/50 | 3/50 |

- **强化工具说明没有提高 find 采用率**（Fisher 精确 p = 1.0；0/50 的单侧 95% 上界
  为 5.8%，1/50 为 9.1%，故只排除「提到 ~10% 以上」这档效应）。
- 方法学锚点：variant A 与原 run 实际发送的 tools 逐字节相同，因此 A 下的 1 次
  open、4 次停下作答全部是采样噪声——本 probe 的噪声底就是约 10% 非 search。
- 唯一的 find（`find(D11, "Messi free-kick 95th minute")`）形态正确，但 reasoning
  显示是在**锁定错误答案之后用来确认先验**，不是用来检验替代候选。
- 首轮单样本 probe 里那个 `find(D5, "4-3")` 在同一 checkpoint 的 5 次 B 样本中
  0/5 复现，不能归因于变体。

这是独立实验，不回写本批 v3a 结果。本批的四个 run 目录保持原样，冻结协议源码
未改动。

## 第 5 节：离线语义审阅汇总

（gold 仅在四轮 rollout 全部结束后查阅；查阅范围为 `qa.jsonl` 的 `answer` 字段
与 `documents.sqlite` 的原文。）

| run | 实体正确 | abstain | 解释无支撑 | prompt tok | api_responses | 耗时s |
|---|---|---|---|---|---|---|
| 546 A | ✗ Judd Trump | 否 | 是 | 161 288 | 6 | 198.9 |
| 1094 B | ✗ Selçuk İnan | 否 | 是 | 5 483 308 | 37 | 1275.1 |
| 546 B | ✗ Neil Robertson | 否 | 是 | 156 012 | 7 | 175.4 |
| 1094 A | ✗ Lionel Messi | 否 | 是 | 829 082 | 20 | 389.8 |

无支撑解释的具体形态：

- 546A 编造了 Championship League 分组赛程与对手，且自己用「such as Luca Brecel
  or David Gilbert」「such as John Higgins or Neil Robertson」的模糊措辞暴露猜测。
- 546B 编造了「2023 Championship League (Ranking) Stage 1, Group 2，决胜局胜
  Jak Jones」以及 4 次满分的年份（2006/2012/2015/2023）。
- 1094B 编造了 2011-12-04 Fenerbahçe 2–2 Galatasaray 的完整叙事、进球者和
  95 分钟任意球归属。
- 1094A 编造了 PSG vs Lille 的比赛细节。它甚至在 reasoning 里承认过 Inter Milan
  这个正确解读，随后以「the specific detail … points directly to Lionel Messi」放弃。

四轮答案都给出了确定的主张，没有一轮 abstain；没有一轮引用了任何 preview 里
真正存在的原文作为依据。

## 工程记录

- GPU：两卡均有其他用户进程，必须显式 `BCPLUS_DEVICE=cuda:0`。546A 首次在
  cuda:1 上 OOM（他人进程占 9.6 GiB，未杀死），改到 cuda:0 重跑成功；546B
  首次在 cuda:0 上 OOM（另一用户进程临时占用 8.4 GiB，该进程随后自行退出），
  重跑成功。两次 OOM 各产生一个 `status=error` 的 run 目录，已保留未删，
  未计入任何统计。
- 冻结后唯一改动的文件是 `analyze_mechanism.py`（第 4 节离线分析工具，不属于
  协议，不在 manifest 的 `source_sha256` 清单内）。改动内容是修两个解析 bug：
  baseline 的 search 结果是行列表而非 dict；`tool_internal` 有独立 seq、必须与
  `tool_result` 按顺序配对。每次 rollout 前都复核了六个协议源码哈希，逐项一致。
- 协议输入（prompt / tool description / usage hint）在本批内**未做任何修改**，
  符合第 0 节与第 3 节的约束。
