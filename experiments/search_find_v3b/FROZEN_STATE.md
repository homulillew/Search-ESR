# Search-Find v3b 冻结状态

在 v3b 批次的**首个真实模型调用之前**记录。此后在本批内不得修改预注册的
hypothesis、判定区间、arm 定义、checkpoint 清单或样本数。

| 项目 | 值 |
|---|---|
| HEAD（创建分支处） | `d06a5d40ab3c48ed987a354f32470cd226866131` |
| 分支 | `experiment/search-find-v3b`（自 `experiment/search-find-v3a` 创建） |
| model | `qwen3.7-flash` |
| base_url host | `llm-p0vhlut44muxw0h2.cn-beijing.maas.aliyuncs.com` |
| timeout | 180.0 |
| python | 3.12.2 |
| openai SDK | 1.109.1 |
| 采样 | provider 默认（记录的请求不含 temperature / max_tokens，重放同样不设） |

## 冻结的协议哈希（来自 v3a，用于证明本轮没动 v3a）

- v3a tool schema `SEARCH_FIND_TOOLS`：`60de1d45580c0dcd1fab666fbb97052122259f14c7f92bafab59825f3e7662ba`
- v3a agent prompt `SEARCH_FIND_PROMPT`：`b93952826c95fcb4c5ba050012cdcb8f275de94445af724949bcdd74809342ca`
- baseline tool schema `TOOLS`：`2470dab030a55eb5b98ad21f1d89f805c9769338b973c41c6a1fdef16f19773b`
- baseline agent prompt `AGENT_PROMPT`：`3b701fc9293b06dc57b747dfb06d07293d61b699b56a73ec465712caa6b2b102`

本轮 probe 的门禁逐项比对了两个被重放 run 的 `manifest.json` 里全部 9 个
`source_sha256` 与当前文件，全部一致 → **v3a 协议源码自 run 以来未被改动**。

## 阶段 1：Tool Competition Upper-Bound Probe（冻结参数）

| 项目 | 值 |
|---|---|
| checkpoint | 10 个（546: seq 9/17/25/33/41；1094: seq 23/34/45/53/61），机械选取 |
| arm A `as_is` | tools = `60de1d45…`；prompt = `b9395282…`（均逐字） |
| arm B `search_hidden` | tools = A 去掉 search 后保持原序（find/open 逐字节不变）；prompt 逐字不动 |
| arm C `local_only` | tools 与 B 同一对象；prompt 只替换第 1 段（search 那一段） |
| 新调用 | 10 checkpoint × 2 arm（B、C）× 5 样本 = **100** |
| arm A 样本来源 | **复用** v3a probe `20260922T141730.317105Z` 的 50 条（不重新采样） |
| 执行工具 | **不执行任何工具**（probe 只允许 `chat.completions.create`） |
| `tool_choice` | `auto`，绝不强制 |
| 主指标 | 首个动作：search / find / open / answer-stop / invalid / other |
| find 二分 | exploratory_find / confirmation_find（后者不计为同等成功） |
| 判定区间 | 强 ≥15/50 且 ≥5/10 checkpoint；中 5–14/50；弱 ≤4/50（对 Arm C 的 exploratory_find 施加） |

Arm C 替换进 prompt 的那段（冻结全文）：

> Global document discovery for this question has already been done. The
> documents identified by the D# handles in this conversation are the candidate
> set, and this step offers no further global search. Use find and open on the
> D# / W# material already in the conversation.

Arm C 的禁令（门禁逐条扫描）：不含任何具体 D#、不含任何候选实体名、不含 gold、
不含题目相关外部事实、不含建议的本地 query、不含 `docid` / `document_sha256`。

## 批次执行日志

| # | 实验 | 目录 | 新调用 | 状态 |
|---|---|---|---|---|
| 0 | 最新仓库审计 + 旧结果复核 | `../search_find_v3a/AUDIT_SECTION7A.md` | 0 | 完成，两处叙述性计数错误已立审计，无结论翻转 |
| 0b | 阶段 1 离线门禁 dry-run | `competition_probe/20260922T173041.831538Z` | 0 | 完成，123/123 PASS，0 FAIL |
| 1 | 阶段 1 Tool Competition Probe | `competition_probe/20260922T174605.704525Z` | 100 | 完成，未执行任何工具。判定：**弱信号**（Arm C exploratory_find 4/50，3/10 checkpoint）。下一步 Experiment 3 |

（dry-run 目录只含 `freeze.json` 与 `gate.txt`，无任何付费调用。两次调试中间产物
已删。）

阶段 1 结论（详见 `RESULTS.md` 与 `competition_probe/20260922T174605.704525Z/SCORING.md`）：
把 `search` 从 tools schema 移除，find 仍停在弱区间；而模型的首个动作有
41/50（B）/ 36/50（C）变成了**对未声明工具的 `search` 调用**——provider 不拦截
未声明函数名，所以「移除工具」没有真正移除动作。**冻结的判定区间按字面施加，
未做事后解释**；4/50 落在弱区间（≤4/50），95% 上界 17.4% 进入中区间，这一限定
已写入 SCORING.md。

GPU 沿用 v3a：两卡均有其他用户进程。本阶段只调用 LLM 推理，不跑 embedding，
不需要 `BCPLUS_DEVICE`。
