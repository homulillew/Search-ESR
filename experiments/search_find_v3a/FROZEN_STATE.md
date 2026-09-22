# Search-Find v3a 首轮冻结状态

按 CLAUDE_NEXT.md 第 0 节，在首次真实模型调用前记录。此后在本批内不得修改 prompt、tool
description 或 usage hint。

| 项目 | 值 |
|---|---|
| HEAD | `9cc7dff033169e5fd1d82e5a2a75b23b03ba3535` |
| branch | `experiment/search-find-v3a` |
| model | `qwen3.7-flash` |
| base_url host | `llm-p0vhlut44muxw0h2.cn-beijing.maas.aliyuncs.com` |
| timeout | 180.0 |
| OPENAI_ALLOW_TOOL_CALLS_WITH_STOP | false（env 与 .env 一致） |
| python | 3.12.2 |
| openai SDK | 1.109.1 |
| max_tool_rounds | 64（run_rollout 默认） |
| max_tool_calls_per_round | 8 |
| sdk_max_retries | 2 |

## 哈希

- qa.jsonl: `44b80cc9fcd9dd5a44aa09292c2165364b0c0e9df26c9cd6c11846165a0916b7`
- index_validation.json: `aed6224a68ba4b6bf7187e08206f3e8467c8671cc78daa2c25743cb085721058`
- v3a tool schema: `60de1d45580c0dcd1fab666fbb97052122259f14c7f92bafab59825f3e7662ba`
- v3a agent prompt: `b93952826c95fcb4c5ba050012cdcb8f275de94445af724949bcdd74809342ca`
- baseline tool schema: `2470dab030a55eb5b98ad21f1d89f805c9769338b973c41c6a1fdef16f19773b`
- baseline agent prompt: `3b701fc9293b06dc57b747dfb06d07293d61b699b56a73ec465712caa6b2b102`

源码（短哈希前 16 位）：`llm_chat/agent.py` e129a97b82388116 · `llm_chat/search_find_agent.py`
7abd1c4414a38bce · `llm_chat/raw_windows.py` b72948cf78cdf15d · `llm_chat/window_locator.py`
f9805b2976b7dac4 · `llm_chat/window_units.py` 06aac46abd434450 · `experiments/run_rollout.py`
9f1fbf8ccdb7b5c3 · `BCPlus/scripts/search_bcplus.py` b8c27504231b094c

## 检索后端

- 索引：`BCPlus/indexes/qwen3-embedding-8b`，`index_validation.json` 报告 100195 文档、4096 维。
- Embedding 模型：`/data/model/Qwen3-Embedding-8B`。
- GPU：2× RTX 4090 D。

## 门禁结果（第 1 节）

- `python -m pytest -q tests/test_chat.py`：20 passed。
- `python -m pytest -q tests/`：393 passed。
  （仓库根 `python -m pytest -q` 收集到 19 个 collection error，全部来自 `experiments/`
  归档 run 快照里的测试模块缺少 `test_snippets` 依赖，与本 PR 无关，是 main 上既有的。）
- `python experiments/run_rollout.py --help`：正常，`--agent-protocol` 参数存在。
- `python experiments/search_find_v3a/offline_gate.py`：43/43 passed。

## 固定交错调度（第 3 节）

1. 546 A（baseline）
2. 1094 B（search_find_v3a）
3. 546 B（search_find_v3a）
4. 1094 A（baseline）

在看到前两个结果后不得修改协议。

## 批次执行日志

冻结后唯一改动的文件是 `analyze_mechanism.py`（第 4 节离线分析工具，不属于协议：
不在 manifest 的 `source_sha256` 清单内）。上表六个协议源码哈希在每次 rollout
前都复核过，逐项一致。

| # | 调度 | qid | 协议 | run_id | 状态 | search | find | open | 备注 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 546 A | 546 | baseline | 20260922T105706.100542Z | natural_answer | 12 | – | 0 | 198.9s，161 288 prompt tokens |
| 1b | (546 A 重试) | 546 | baseline | 20260922T105026.926765Z | error | 1 | – | 0 | cuda:1 OOM（他人进程占用 9.6 GiB），改用 cuda:0 重跑 |
| 2 | 1094 B | 1094 | search_find_v3a | 20260922T113202.256169Z | natural_answer | 76 | **0** | 0 | 1275.1s，5 483 308 prompt tokens，无 find 调用 |
| 3 | 546 B | 546 | search_find_v3a | 20260922T121742.932067Z | natural_answer | 12 | **0** | 0 | 175.4s，156 012 prompt tokens，无 find 调用 |
| 3b | (546 B 重试) | 546 | search_find_v3a | 20260922T120722.543923Z | error | 1 | – | 0 | cuda:0 OOM（另一用户进程临时占用 8.4 GiB，该进程随后自行退出），重跑成功 |
| 4 | 1094 A | 1094 | baseline | 20260922T122337.338934Z | natural_answer | 19 | – | 0 | 389.8s，829 082 prompt tokens |

四个计入统计的 run 全部 `natural_answer`，无 tool error，无 invalid ref。
两次 OOM 重试产生的 `status=error` run 目录已保留未删，未计入任何统计。
结论见 `RESULTS.md`。

GPU：两卡都有其他用户的进程，必须显式 `BCPLUS_DEVICE=cuda:0`；cuda:1 被占用且不得
杀死。

## 第 6 节：Tool Affordance probe（独立实验）

在四个 rollout 全部结束后、按第 6 节既定动作执行。不修改任何协议源码，不回写
四个 run 的结果，输出只落在 `probe_tool_affordance/` 下自己的目录。

| probe_id | 样本/格 | 重放数 | 说明 |
|---|---|---|---|
| 20260922T135046.536124Z | – | 0 | 离线门禁试跑，仅 freeze.json，无付费调用 |
| 20260922T135428.162661Z | – | 0 | 同上 |
| 20260922T140026.879255Z | 1 | 20 | 单样本 probe（find(D5,"4-3") 出现 1 次，后证为噪声） |
| 20260922T141730.317105Z | 5 | 100 | 多样本 probe，2 870 230 prompt tokens，结论依据 |

checkpoint 为每 run 最早 5 个「重定位时刻」（546: seq 9/17/25/33/41；1094:
seq 23/34/45/53/61），机械选取。离线门禁 30/30 PASS（含「A 与冻结
SEARCH_FIND_TOOLS 逐字节一致」「A 与 B 只差 find/open 的 description」）。
结论见 `probe_tool_affordance/PROBE_RESULTS.md`：强化工具边界未提高 find
采用率（A 0/50 vs B 1/50，Fisher p=1.0）。
