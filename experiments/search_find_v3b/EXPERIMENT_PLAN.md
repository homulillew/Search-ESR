# v3b 实验计划

本计划在首个付费调用之前冻结。阶段 1 的执行参数（checkpoint 清单、arm 定义、
样本数、判定区间）一经 `FROZEN_STATE.md` 记录即不得在本批内修改。

与 v3a 的关系：**v3a 协议、四个 run、affordance probe、冻结文件、结果文档全部
不动**。v3b 只做两件事——读 v3a 的 run 记录来重建 checkpoint，以及把新实验的
输出写进 `experiments/search_find_v3b/` 自己的目录。

## 阶段 0：前置（已完成）

1. 最新仓库审计：`git fetch origin` 后
   `experiment/search-find-v3a` = `d06a5d40`，本地与远端一致。
   分支 `experiment/search-find-v3b` 自该 commit 创建；`main` 未动。
2. 旧结果复核：四个 run 的全部测量指标逐项独立复现。发现两处叙述性计数错误，
   已写 `../search_find_v3a/AUDIT_SECTION7A.md`（不改 RESULTS.md 正文，
   不推翻任何结论，不需要重跑任何 run）。按「先写审计再继续」执行完毕。
3. 10 个冻结 checkpoint 机械重建并复核（见审计文件末尾的表）。
4. 三个 hypothesis 正式预注册：`HYPOTHESES.md`。

## 阶段 1：Tool Competition Upper-Bound Probe（Experiment 1）

**目的**：在**不执行任何工具**的前提下，测「解除 Search 竞争」这一单项干预对
find 采用率的上界效应。这是 H1 的直接检验，也是唯一能零执行成本区分 H1/H2 的
实验。

### Checkpoint

沿用 v3a affordance probe 的 10 个（机械选取的最早重定位时刻，不按期望结果
人工挑选）：

| run | qid | seq |
|---|---|---|
| `v003a_search_find/qid_546/20260922T121742.932067Z` | 546 | 9, 17, 25, 33, 41 |
| `v003a_search_find/qid_1094/20260922T113202.256169Z` | 1094 | 23, 34, 45, 53, 61 |

重建方式：直接深拷贝原 run `events.jsonl` 里对应 `api_request` 的 `request`
字段。**不重放工具、不重建状态、不引入任何新文本**（Arm C 的 system 段除外，
见下），因此「history prefix 一致、已发现 D#/W# 不变、无 gold、无答案注入、
文档观测不变、无工具执行」这五项由构造保证，再由离线门禁逐条断言。

### Arm

| Arm | tools | system prompt | 说明 |
|---|---|---|---|
| **A**（`as_is`） | `search, find, open`（冻结 v3a schema 逐字） | 冻结 prompt 逐字 | 与原 run 逐字节一致的基线，也是噪声锚点。 |
| **B**（`search_hidden`） | `find, open`（其余一切不变） | 冻结 prompt 逐字（**不改**） | 单项干预：只把 search 从动作空间移除。Deliberately incoherent：prompt 仍描述 search，工具却没有——这正是 H1 要测的「压制解除」。 |
| **C**（`local_only_coherent`） | `find, open`（与 B **同一个 tools 对象**） | 冻结 prompt，**只替换一段** | B + 一处最小改动：把描述 search 的那一段换成「全局发现已完成、本步不再提供全局 Search」。这是**能力上界**，不是产品提案。 |

Arm C 替换的那一段（预注册全文，冻结后不得改）：

> 原文：
> `search(query) discovers candidate documents. Each result has a stable D# document handle and one short raw preview identified by a W# window handle. The preview is only one query-localized excerpt; absence from it does not establish absence from the document.`
>
> 换成：
> `Global document discovery for this question has already been done. The documents identified by the D# handles in this conversation are the candidate set, and this step offers no further global search. Use find and open on the D# / W# material already in the conversation.`

Arm C 的**禁令**（写入离线门禁逐条扫描）：不得指明该 find 哪个 D#；不得指明正确
候选；不得出现 gold；不得出现任何题目相关的外部证据；不得给出下一个本地 query；
不得出现 `docid` / `document_sha256`。上面这段文字不含上述任何一项——它只声明
「发现阶段结束、本步无全局检索」这一协议状态。

**同一性约束**：三个 Arm 的 `model` / `messages`（A、B）/ `stream` /
`tool_choice` 必须与记录的原请求一致；`tool_choice='auto'`，**绝不强制**。
记录的原请求**不含 temperature 与 max_tokens**（采样为 provider 默认），
任何 Arm 都不得新增这两个参数，否则违反「同一 thinking 配置、max tokens、
temperature」。

### Arm A 的样本来源（明确声明）

**复用 v3a affordance probe 已有的 50 个 A 样本**，不重新采样。理由与依据：

- 该 probe 的 variant A 与原 run 实际发送的 tools **逐字节一致**（sha256
  `60de1d45…`，probe 的 freeze 与门禁都校验过），checkpoint 也完全是同一批
  10 个、同一 model、同一请求字段、同一 provider 默认采样。
- 因此那 50 条与本轮若重新采样的 A 属于**同一条件**，重采只是花钱买噪声。
- 每条记录都带 `reasoning_tail`（尾部 1200 字符），本轮的
  exploratory_find / confirmation_find 二分可以照着它重新打标，不需要新调用。

复用方式（满足「单独存放、可追溯」）：把这 50 条**拷贝**进本轮 probe 目录的
`arm_a_reused_from_v3a_probe.json`，并保留原 probe 目录里的原件不动。拷贝件里
每条带来源 probe_id 与原 seq/sample 编号。本轮的任何统计都从拷贝件读，原
probe 目录只读不写。

（若复核时发现那 50 条的 checkpoint 集合与本轮 10 个不完全对齐，则改为
**重新采样** A 并单独存 `arm_a_resampled.json`，同时在 `FROZEN_STATE.md` 里
记下这个变更与原因。这是唯一允许的偏离，且必须在付费前决定。）

### 样本数

10 checkpoint × 2 **新** Arm（B、C）× 5 样本 = **100 次新的真实模型调用**。
A 复用 50 条，不产生新调用。

不采用「成本受限时先 3 样本」的豁免：v3a 全批（四次 rollout + 一次 100 次
probe）总成本约 ¥3.61，本轮 100 次重放的量级与那次 probe 相当（约 ¥0.8–1.0），
没有成本约束。因此**一开始就按 5 样本**，避免「先 3 后补」引入的任何选择性。

### 分类（预注册，见 HYPOTHESES.md）

首个动作：`search` / `find` / `open` / `answer-stop` / `invalid` / `other`。
`search` 类在 B/C 下只能是 free-text search attempt，**单列**。
`find` 二分为 exploratory_find / confirmation_find，判定区间只施加于前者。

判定区间：强 ≥15/50 且 ≥5/10 checkpoint；中 5–14/50；弱 ≤4/50。
Arm B 高而 C 低、增量全是 confirmation_find、增量全是 answer-stop、
invalid ≥10/50 的读法见 `HYPOTHESES.md`。

### 离线门禁（任何付费调用之前必须全过）

在 v3a probe 30 项门禁的基础上追加：

1. 输出目录不在任何被重放 run 目录之内。
2. 10 个 checkpoint 的 seq 与冻结清单**逐项相等**。
3. 每个 checkpoint 的 `messages` 与原 run 记录的 `request['messages']`
   **深相等**（A、B 两 arm；C arm 只允许 system 那一段不同）。
4. 每个 checkpoint 末条 message 的 role == `tool`。
5. Arm A 的 tools sha256 == `60de1d45…`（等价于冻结的 `SEARCH_FIND_TOOLS`）。
6. Arm B 的 tools == Arm A 去掉 search 后保持原序；剩下的 find/open 的
   **参数 schema 与 description 与 A 逐字节相同**（B 只做减法，不改描述）。
7. Arm C 的 tools **对象**与 Arm B 相同（同一个 sha256）。
8. Arm B 的 system message 与冻结 `SEARCH_FIND_PROMPT` **逐字节相同**。
9. Arm C 的 system message 与冻结 prompt **恰好一段不同**，且不同的一段的
   index 就是描述 search 的那一段；其余段（含 user question）逐字节相同。
10. 三个 Arm 的 `model` / `stream` / `tool_choice` 与原记录相同；
    `tool_choice == 'auto'`。
11. 三个 Arm 的请求都**不含** `temperature` 与 `max_tokens`（保持 provider
    默认，与原 run 一致）。
12. 任何 Arm 的任何 message 里**不得出现** `docid` / `document_sha256` /
    gold 实体串。
13. Arm C 新增的那段文本不得包含：任何具体 D# 编号、任何候选实体名、gold、
    任何题目相关外部事实、任何建议的本地 query。（门禁里维护一份禁词/禁模式
    清单，逐条扫描。）
14. **不执行任何工具**：probe 只允许调用 `chat.completions.create`，代码路径
    上不得构造任何 tool executor（不得 import / 实例化 `SearchFindTools`
    或 `BCPlusTools` 的执行端）。
15. Arm A 复用的 50 条：来源 probe_id 已记录；每条的 tools sha256 与 checkpoint
    seq 都在本轮冻结清单内；**原件未被修改**（比对原 probe 目录的文件哈希）。
16. 被重放的 v3a run 目录与 v3a 冻结协议源码**未被改动**：比对
    `manifest.json` 里 `source_sha256` 的每一项与当前文件。

### 输出

全部落在 `experiments/search_find_v3b/competition_probe/<probe_id>/`：

- `freeze.json`（首个付费调用之前写入）
- `gate.txt`（逐项 PASS/FAIL）
- `events.jsonl`（checkpoint 与 probe_response，含 reasoning 尾部、usage、耗时）
- `probe_results.json`（B、C 的新结果）
- `arm_a_reused_from_v3a_probe.json`（复用的 50 条 + 来源标注）
- `SCORING.md`（分类与二分的结果表，含每条的判定依据）

## 阶段 2：Checkpoint Partial Rollout（Experiment 2，仅阶段 1 给出 ≥ 中信号时）

**协议 `search_find_v3b`：orthogonal search。** 只改一处机制：全局 Search 命中
**已发现**文档时，返回 `status: already_discovered` + title + url +
`existing_preview_ref`，**不生成新 W#、不产生任何新原文给模型**，并注入一条
固定的 harness hint。私有 trace 里仍记 rank/score。

必须**真的阻断重定位**：不跑本地 BM25、不开新 Window、不扩覆盖、不给模型新文本。
否则「find 吸收了重定位压力」就是假的。

**其余一律不改**：retriever、top-k、preview 算法、400-token 预算、find 的
BM25/top-k、open、query 策略、上下文策略、状态、停止策略、citation 策略。

从同一批 checkpoint prefix 起，P0 = 当前 v3a、P1 = v3b，最多 4–6 个新的工具
决策轮，**不强制最终答案**。首轮 10 checkpoint × 2 arm × 1 rollout = 20；
方向混杂则**均匀**扩到 40。

指标：`find_any_within_horizon`、**`find_before_next_search`（最重要）**、
`find_returns_new_window`、useful evidence、search pressure、tokens、
premature stop。

成功判据：find 采用率明显上升；≥2 个 checkpoint 通过 Find 拿到语义上有价值的
新窗口；Search 不再做同文档重定位；Search 下降不是被 premature stop 解释掉的；
D/W 身份无错乱。

## 阶段 3：Verification State Probe（Experiment 3）

触发条件：阶段 1 给出**弱**信号；或阶段 2 证明 v3b 正交但采用率仍低。

最小 Verification Card，只含两项：
**(当前未解决的需求，有希望的已有文档 / 候选 D#)**。

**禁令**：claim graph、置信度、计划、候选打分、verify 状态、证据摘要、gold。
Card 只能由 checkpoint prefix 的信息推出；第一版允许手搓，但**必须标注
`diagnostic_oracle`**。

Arm S0（v3b，无 card）vs S1（同 prefix + card），tools 完全相同。

## 阶段 4：scoped_search（仅 H1 与 H2 都检验完之后）

`scope="corpus"` vs `scope="document"`，检验 H3（工具名 / API 形态 / 先验）。
在此之前**禁止**动工具名或加 scope 参数。

## 本轮禁止做的事（Section 二十三）

10–20 题基准、multi-query、dense chunk index、hybrid localizer、top-2 find、
preview 压缩、Open→Read 重构、claim graph、ESR-GRPO、process reward、自动
verifier、强制的 find-after-search、全局搜索硬上限、「IMPORTANT ALWAYS USE
FIND」式的 prompt 补丁。

## 本轮禁止触碰的东西

- `experiment/search-find-v3a` 分支上的任何既有文件（`RESULTS.md`、
  `FROZEN_STATE.md`、`PROBE_RESULTS.md`、`offline_gate.py`、
  `tool_affordance_probe.py` 除外——这两个脚本**只读不写**）。
- 四个计入统计的 run 目录与两个 OOM error run 目录（只读）。
- `probe_tool_affordance/` 的四个 probe 目录（只读；Arm A 复用时只拷出不写回）。
- `llm_chat/` 下被 v3a manifest 记录哈希的协议源码（在阶段 2 开始前一律不动；
  阶段 2 只允许新增 `llm_chat/search_find_v3b_agent.py` 之类的**新文件**，
  不得改既有文件）。
- `main` 分支。

## 需要产出的文件（Section 二十七）

`experiments/search_find_v3b/`：`README.md`、`HYPOTHESES.md`、
`EXPERIMENT_PLAN.md`、`FROZEN_STATE.md`、`competition_probe/`、
`checkpoint_rollout/`、`verification_state_probe/`、`RESULTS.md`、
`FINAL_CONCLUSION.md`。

**未跑的阶段一律不得写结果**，目录可以先建空，但 `RESULTS.md` /
`FINAL_CONCLUSION.md` 只写实际执行过的部分。
