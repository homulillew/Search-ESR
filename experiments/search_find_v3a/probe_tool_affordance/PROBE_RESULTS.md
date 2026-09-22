# Tool Affordance Probe 结果

按 CLAUDE_NEXT.md 第 6 节「两题都不调用 Find」分支执行。本文是**独立实验**：
不回写 v3a 首轮的四个 run 结果，不修改冻结协议，不改动被 replay 的 run 目录。

## 是什么

取 v3a 首轮两个 `natural_answer` run 里真实的 api_request 时刻，把「已经发现过的 D#
又被一次全局 Search 重复返回、而模型实际下一动作仍是 search」的最早若干时刻作为
checkpoint，原样重放整个对话（只换 `tools` 数组），问模型「下一步做什么」。
**全程不执行任何工具**，所以不存在工具结果反馈改变后续行为的问题。

- A：冻结的 v3a `SEARCH_FIND_TOOLS` 原文（sha256 `60de1d45…`，与 FROZEN_STATE.md 一致）。
- B：只改 `find` / `open` 的 description，强化通用边界「找同文档另一个事实用 Find；
  当前段落缺上下文才 Open」。工具名、顺序、参数 schema 全部不动，`search` 的
  description 逐字不动。

checkpoint 选择是机械的（每 run 最早 N 个，N=5），没有按期望结果人工挑选。
两个 run 各 5 个，共 10 个 checkpoint：

| run | qid | checkpoint seq |
|---|---|---|
| 20260922T121742.932067Z | 546 | 9, 17, 25, 33, 41 |
| 20260922T113202.256169Z | 1094 | 23, 34, 45, 53, 61 |

每个 (checkpoint, variant) 抽 5 个独立样本，共 10 × 2 × 5 = **100 次重放**。

冻结记录：`20260922T141730.317105Z/freeze.json`（任何付费调用之前写入，含两个
variant 的 tools sha256、checkpoint 清单、head/model/timeout）。离线门禁 30/30
PASS（含「A 与 SEARCH_FIND_TOOLS 逐字节一致」「A 与 B 只差 find/open 的
description」「每个 checkpoint 以 system 开头、以 tool 观测结尾」「replay 只改 tools」）。

## 结果

首个动作的分布（50 样本/variant）：

| variant | search | find | open | 停下作答 | 非 search 合计 |
|---|---|---|---|---|---|
| A（冻结说明） | 45/50 | **0/50** | 1/50 | 4/50 | 5/50 (10%) |
| B（强化边界） | 45/50 | **1/50** | 1/50 | 3/50 | 5/50 (10%) |

按题拆开：

| qid | seq | A (5 样本) | B (5 样本) |
|---|---|---|---|
| 546 | 9 | search×5 | search×5 |
| 546 | 17 | search×5 | search×5 |
| 546 | 25 | search×5 | search×5 |
| 546 | 33 | search×4, 停×1 | search×5 |
| 546 | 41 | search×4, 停×1 | search×2, 停×3 |
| 1094 | 23 | search×5 | search×5 |
| 1094 | 34 | search×5 | search×5 |
| 1094 | 45 | search×4, 停×1 | search×5 |
| 1094 | 53 | search×4, open×1 | search×4, **find×1** |
| 1094 | 61 | search×4, 停×1 | search×4, open×1 |

**与原 run 的差异**：35/100 次重放的下一动作与原 run 不同（A 18/50，B 17/50）。

## 怎么读这个结果

**关键的方法学锚点：variant A 与原 run 实际发送的 tools 逐字节相同。** 10 个
checkpoint 的原始 tools sha256 全部等于 `60de1d45…`，等于 variant A。因此 A 下
出现的一切偏离（1 次 open、4 次停下作答、18/35 的差异次数）**全部是模型采样
噪声**，不是变体效应。这直接给出本 probe 的噪声底：在这类 checkpoint 上，模型
本来就有约 10% 的概率做出非 search 动作。

在这个噪声底下：

- `find`：A 0/50 vs B 1/50。Fisher 精确检验双侧 p = 1.0。两者不可区分。
- 非 search 动作合计：A 5/50 vs B 5/50，完全相同。
- 单侧 95% 上界：0/50 的真实率可高至 **5.8%**，1/50 可高至 **9.1%**。也就是说，
  本 probe 的 n=50 只能排除「强化说明把 find 采用率提到 ~10% 以上」这档效应；
  低于这个量级的真实提升探测不到。这是本结果的能力上限，必须一并说明。

**结论：把通用边界写进工具 description，在本 probe 的分辨能力内没有提高 `find`
的采用率。** 不能说「完全没有」——只能说如果有效应，小于本 probe 能探测的量级。

另外，首轮单样本 probe（`20260922T140026.879255Z`，1 样本/格，20 次重放）里
唯一的 find 出现在 546 seq=9 的 B 下：`find(D5, "4-3")`。这次 5 样本重放在同一
checkpoint 的 B 下抽了 5 次，**0/5 再次出现 find**。那次单样本的 find 因此不能
归因于变体 B——正是加 `--samples` 的原因。

## 三个非 search 事件的定性观察

**(1) 唯一的 find（1094 seq=53，B，sample 0）**

```
find(D11, "Messi free-kick 95th minute")
```

这是一次**形态正确**的 find 调用：目标是已发现的文档，查询是文档内的事实定位，
不是全局召回。但 reasoning 显示调用动机是**确认既有结论**：

> "But 'On the 95th minute, a free-kick was taken' strongly points to the Messi
> event found in D11/D13/D15. … I will provide **Lionel Messi**."

模型在调用 find 之前已经锁定 Messi（错误答案）。即使 find 取回原文，也是被用来
加固先验，而不是用来检验替代候选。这与 RESULTS.md 第 7 节的判断一致：瓶颈是
grounding 意愿，不是工具能力。

**(2) 两次 open**

`open(W50, around)`（1094 seq=53，A）与 `open(W11, around)`（1094 seq=61，B），
都是「围绕已观察窗口读相邻文字」，符合 open 的设计语义，没有出现 find/open
误用。其中 A 下那次尤其说明问题：**冻结说明就能触发 open**，进一步证明这类
偶发动作是噪声而非变体效应。

**(3) 七次停下作答**

4（A）+ 3（B）次 `finish_reason=stop`，发生在 546 seq=33/41 与 1094 seq=45/61。
共同形态：reasoning 把参数记忆的约束匹配当成已验证，直接收尾。

- 546：`">300 centuries: Yes (~800+ by Jan 2025) … Answer: Judd Trump"`、
  `"I will state Mark Selby"`——与原 run 的错误答案相同。
- 1094：把「born out of discord」读成 PSG（合并纠纷）、「identity evolved」读成
  马赛，收尾 `"I will answer Lionel Messi"`。而正确解读（Inter、Pirlo）在原 run
  的 reasoning 里被明确写出过又被放弃。

这些是 RESULTS.md 第 7(b) 节「拿着正确线索丢弃」的直接复现，且在 A 下同样发生。

## 与首轮结论的关系

首轮发现：`find` 机制正确但 0/88 被调用，定位缺口真实存在（qid 546 的正确答案
就在已发现的 D17 里，落在 400-token preview 窗外）。本 probe 回答的是第 6 节
规定的下一个问题：**这是不是工具 description 的边界没讲清楚？**

答案：**不是（在本 probe 分辨能力内不是）**。把「需要同文档另一个事实就 find、
不要再去 global search」写进 description，采用率仍停在噪声水平（≤10% 上界）。
模型不缺「find 能干什么」的信息，缺的是在已有候选时去验证的动机。

## 能力与代价

- 100 次重放，2 870 230 prompt tokens / 3 071 838 total tokens，API 累计
  2083.5s。约为一个 1094B run（5.48M prompt tokens）的 52%。
- checkpoint 最大 prompt 约 48K tokens（1094 seq=61），全部远小于原 run 末段的
  数十万 token——因为 checkpoint 是重定位压力最早出现的时刻，这正是 find 本应
  介入的位置。
- 隐私边界保持：重放只发送原 run 已存在的 messages，不含 docid / document_sha256。
- 输出隔离在 `experiments/search_find_v3a/probe_tool_affordance/`，四个 v3a run
  目录与冻结协议源码未被修改。

## 目录说明

| 目录 | 内容 |
|---|---|
| `20260922T135046.536124Z` | 离线门禁试跑，仅 freeze.json，无任何付费调用 |
| `20260922T135428.162661Z` | 同上 |
| `20260922T140026.879255Z` | 首轮单样本 probe（1 样本/格，20 次重放） |
| `20260922T141730.317105Z` | **本文依据的多样本 probe（5 样本/格，100 次重放）** |

每个目录含 `freeze.json`；完成运行的另含 `events.jsonl`（checkpoint 与
probe_response 事件，含 reasoning 尾部、usage、耗时）与 `probe_results.json`。
