# 审计：RESULTS.md 第 7(a) 节两处叙述性计数错误

按本轮指令「Section 二（旧结果复核）」执行。复核方法：不读 RESULTS.md 的数字，
而是从四个 run 的 `events.jsonl` 与 `documents.sqlite` 重新独立计算，再与报告比对。

本文只是**审计记录**。RESULTS.md 与 FROZEN_STATE.md 的正文没有被改动，四个 run
目录、probe 目录、冻结协议源码也没有被改动。

## 结论

四个 run 的全部测量指标（工具计数、rows/docs/重定位、token、耗时、W# 注册表、
probe 采用率）**逐项精确复现**。唯一两处错误都在第 7(a) 节的**叙述性计数**里，
属于把两个 run 的数字写混/数错，不影响任何 §4 表格中的指标，也不推翻结论。

两处错误的**方向一致且值得注意**：都把模型实际看到的东西**往少里写**——
真实情况是模型在 546A 里看到的「centur」线索比报告声称的多一倍。因此若要说，
这两处错误让第 7(a) 的论证**略微偏乐观**，而不是偏悲观。

## 错误 1：把 546A 的「返回 4 次」归给了 546B

**报告原文**（RESULTS.md:127）：

> docid 38231（Ding Junhui - Wikipedia，75 871 字符）在**两协议下都被发现**
> （546B 中为 D17，被返回过 4 次）。

**实际**（从 `tool_result` / `tool_internal` 重新计数）：

| run | docid 38231 被返回次数 | 折算句柄 | preview 窗口 |
|---|---|---|---|
| 546 A（baseline） | **4 次** | docid 直接可见 | 4 个不同 W# |
| 546 B（v3a） | **1 次** | D17 | 1 个 W#（W31） |

「被返回过 4 次」是 546A 的事实，被写进了 546B 的括号里。546B 里 D17 只被返回
1 次，preview 只有 W31 一个窗口。

未受影响的部分：38231 **在两协议下都被发现**——这一点是对的，只是返回次数
写错了归属。

## 错误 2：「centur」出现次数数错

**报告原文**（RESULTS.md:138）：

> 但 400-token preview 从未覆盖这段（该文档的 4 个 preview 窗口里，「centur」只
> 出现 1 次，「turned professional」0 次）。

**实际**（对 38231 的每个 preview 窗口原文做子串计数）：

| run | 38231 的 preview 窗口 | 含 "centur" 的窗口数 | 含 "turned professional" |
|---|---|---|---|
| 546 A | 4 个 | **2 个**（不是 1） | 0 |
| 546 B | 1 个（W31） | **0 个** | 0 |

「4 个 preview 窗口」属于 546A，其中 "centur" 出现在 2 个窗口里，不是 1 个。
546B 只有 1 个 preview 窗口（W31），两个子串都是 0。

## 不受影响的核心论证（已重新机械验证）

第 7(a) 节的实质主张是「定位缺口真实存在」：qid 546 的正确答案在模型已经发现的
文档里，但落在 400-token preview 窗口之外，`find` 本可以逐字取回。复核：

题目三条约束在 docid 38231 全文中的位置（`documents.sqlite` 原文偏移）：

- "turned professional" @ 1375
- "more than 600 century breaks" @ 1646
- "seven maximum breaks" @ 1682

即关键段落大致在 **[1300, 1900)**。

| run | 38231 的 preview 区间 | 是否覆盖 [1300, 1900) |
|---|---|---|
| 546 A | [21739,23138)、[0,1032)、[18490,20065)、[14942,16542) | 4 个全部**不覆盖** |
| 546 B | [28085,29547)（W31） | **不覆盖** |

并且**实际执行** `find`（真实文档、真实 BM25 本地定位器，非模拟）：

- `find(38231, 'turned professional')` → 窗口 **[642, 2157)**，同时含上述三条事实
- `find(38231, 'more than 600 century breaks')` → [729, 2296)
- `find(38231, 'seven maximum breaks')` → [29230, 30670)（只命中 "maximum" 那个词，
  属局部定位器的正常行为，不影响前两条）

所以：**两协议的 preview 都没覆盖关键段落，而 `find` 一次调用就能取回**。
第 7(a) 节的定位缺口论证成立，`find` 的能力主张成立。

qid 1094 那侧的对应主张也复核过并成立：docid 5400 与 26092 全文含 "Pirlo"，
但两协议所有 preview 窗口里 "pirlo" 命中 **0** 次；docid 54472（Pirlo 本人的
Wikipedia 页）从未出现在任何一次检索结果里；"born out of discord" 在全部
100 195 篇文档中 0 命中。

## 为何不改动 RESULTS.md

按保护规则，既有 run / probe / 冻结文件 / 结果文档视为不可修改的实验记录。本审计
是「另写的审计记录」，正是规则为机械错误指定的补救方式。RESULTS.md 正文保持原样，
本文作为它的勘误存在。任何引用第 7(a) 节计数的地方应以本文为准。

## 不构成「把旧失败标记为无效」

这两处是**叙述里的计数/归属错误**，不是 run 被污染、prompt 被改、或指标算错：
四个 run 的机制指标没有一项变化，`find` 0/88 这个被解释的对象没有变化。
因此不存在「旧结果失效」的问题，也不需要重跑任何 run。

## 复核中顺带确认的其余数字（供后续实验继承）

- 工具计数：546A search=12 / 1094B search=76 / 546B search=12 / 1094A search=19；
  `find` = 0（合计 **0/88**）；`open` = 0；`tool_error` = 0；四轮全部
  `natural_answer`。
- §4 指标：rows 60/380/60/95；不同文档 21/84/19/43；被 ≥2 次搜索命中的文档
  14/49/17/14；额外返回 39/296/41/52；多窗口文档 11/28/10/5；prompt tokens
  161 288 / 5 483 308 / 156 012 / 829 082。
- 跨协议重定位交集：546 = 7 个（16091, 1779, 42120, 4975, 55362, 60119, 64519）；
  1094 = 3 个（26092, 40607, 67205）。（baseline 的 `tool_result` 以 docid 为键、
  v3a 以 D# 为键，必须先从**全部** `tool_internal` 事件建 D#→docid 映射再比对；
  `tool_internal` 在其 `tool_result` **之后**发出，不能单遍顺序扫描。）
- probe（5 样本/格，100 次重放）：A 停下 4、open 1、search 45、**find 0**；
  B 停下 3、open 1、search 45、**find 1**。唯一的 find 是
  `find(D11, "Messi free-kick 95th minute")`（1094 seq=53，B，sample 0）。
- 10 个冻结 checkpoint 全部可从原 run 机械重建（见下），tools 的 sha256 与
  `60de1d45…` 一致。

## 10 个 checkpoint 的机械复核（供本轮 Tool Competition Probe 直接继承）

| qid | seq | history msgs | 末条 role | 末条中被重发现的 D# | 原 run 实际下一动作 |
|---|---|---|---|---|---|
| 546 | 9 | 5 | tool | D1, D2, D5, D4 | search, search |
| 546 | 17 | 8 | tool | D1, D2, D7 | search, search |
| 546 | 25 | 11 | tool | D7, D9, D8 | search, search |
| 546 | 33 | 14 | tool | D1, D2, D5, D13, D4 | search, search |
| 546 | 41 | 17 | tool | D1, D2, D7, D13, D12 | search, search |
| 1094 | 23 | 10 | tool | D1 | search, search, search |
| 1094 | 34 | 14 | tool | D7, D19 | search, search, search |
| 1094 | 45 | 18 | tool | D3, D39, D2 | search, search |
| 1094 | 53 | 21 | tool | D14, D36, D11, D38 | search, search |
| 1094 | 61 | 24 | tool | D8 | search, search |

记录的 `api_request` 只含 `messages / model / stream / tool_choice / tools` 五个
字段，**没有 temperature 或 max_tokens**——采样为 provider 默认。任何重放都不得
新增这两个参数，否则违反「同一 thinking 配置、max tokens、temperature」的约束。
