# Claude Code：Search–Find v3a 下一步测试和实验计划

## 目标

不要继续扩功能。先回答：

> 增加文档内 find(D#, query) 后，模型是否会把一部分“重复全局 Search”转换为“在已发现文档中的局部重新定位”，并因此获得新的有效原文或改善最终判断？

本轮不研究 Query 初始化、不研究 Research State、不改 Retriever。

## 0. 首次调用前冻结

记录 HEAD commit、model、无凭据 endpoint、OPENAI_ALLOW_TOOL_CALLS_WITH_STOP、检索 metadata hash、工具协议 hash、max tool rounds、Python/SDK 版本。

看到本轮模型输出后，不允许修改 prompt、tool description 或 usage hint 后继续把结果算进同一批。

## 1. 离线工程门禁

先运行：

    python -m pytest -q tests/test_chat.py
    python -m pytest -q
    python experiments/run_rollout.py --help

至少验证：

- 同一 (docid, sha) 永远复用同一 D#；
- 同一 canonical raw window 永远复用同一 W#；
- 未知 D/W 严格报错，不 fuzzy repair；
- baseline 行为未改变；
- v3a global Search backend 与 baseline 相同；
- Find 只操作 Search 已发现文档；
- 相同 (D#, query) deterministic；
- lexical miss 返回 no_match，绝不 prefix fallback；
- W# 能映射回 canonical raw window 并正常 Open。

任何一项失败就停止真实 API 实验。

## 2. 首轮只做两个历史 bad case

### qid 546

历史 v001：
- 最终错误：reference Ding Junhui，旧 rollout 回答 Judd Trump；
- 3 次 Search，0 次 Open；
- doc 11927 在不同 Search 中从 [775,2314) 重新定位到 [0,1416)；
- doc 1779 从 [5526,6806) 重新定位到 [10694,12019)。

这是“重新全局 Search 使同一文档换局部窗口”的直接病例。

### qid 1094

历史 v001：
- 最终 abstained；
- 7 次 Search，1 次 Open；
- doc 40496 在不同 Search 中分别出现 [79448,80884) 与 [58521,59559)，之后又 Search 回前一个窗口；
- doc 39918 多次被全局 Search 重复返回同一短窗口，最后才 Open。

这是更强的 repeated discovery / local relocation 候选。

两题都已经是 development/diagnostic case，不宣称泛化。

## 3. 第一批 A/B：总共四个 rollout

每题只做：
- A：当前 baseline；
- B：search_find_v3a。

先保存固定交错 schedule，例如：
- 546 A
- 1094 B
- 546 B
- 1094 A

不要看到前两个结果后修改协议。

示例命令：

    python experiments/run_rollout.py --qid 546 --agent-protocol baseline
    python experiments/run_rollout.py --qid 546 --agent-protocol search_find_v3a
    python experiments/run_rollout.py --qid 1094 --agent-protocol baseline
    python experiments/run_rollout.py --qid 1094 --agent-protocol search_find_v3a

两组保持同一 model、endpoint、budget、corpus/index 和 SDK retry。Gold 不进入在线过程。

## 4. 第一轮先评价机制，不先评价总分

逐题报告：
- search_calls
- find_calls
- open_calls
- invalid_ref_calls
- find_no_match
- Search 中重复 D# 次数
- global_same_doc_relocation：同一 D# 因不同全局 Search 返回不同 W#
- local_find_relocation：Find 在已有 D# 上返回此前未观察 W#
- Search 后第一次 Find 的时机
- Find 后是否仍立即围绕同一需求继续 global Search

### 认为存在“行为改变”的最低条件

至少一个病例满足以下任一项：
1. baseline/historical 通过重复 global Search 重定位的文档，在 v3a 中改为 Find；
2. Find 产生新的 W# 且对后续判断有用；
3. v3a 减少同文档重复 global Search，而不是简单提前停止；
4. Find 暴露此前 Search preview 没显示的关键原文。

第一轮不要求必须把最终答案修对。

## 5. 离线语义审阅

Rollout 结束后才能看 reference/gold。

对每个 Find 新窗口标注：
- 是否包含题目约束相关事实；
- 是否只是重复已有原文；
- 是否改变候选或判断；
- 是否解决历史 repeated Search 想解决的同一信息需求。

new window 不等于 useful evidence。

同时报告 exact entity correctness、abstain、unsupported explanation、tokens、API responses 和 elapsed time。

## 6. 根据结果分支

### 两题都不调用 Find

不要立刻判 Find 无用。先检查 repeated global Search 是否仍存在。

若 repeated Search 仍明显而 Find 从未使用，做一个固定 checkpoint 的 Tool Affordance probe：
- A：当前 v3a 工具说明；
- B：只强化通用边界“找同文档另一个事实用 Find；当前段落缺上下文才 Open”；
- 不执行工具，只比较下一动作。

这是独立实验，不回写原 v3a 结果。

### Find 被调用但大量 no_match

先分析 local query 与原文：
- 同义表达问题？
- 实体/年份词缺失？
- 表格/HTML？
- chunk 边界？
- 文档本来没有信息？

只有确认 localizer 是瓶颈后，才研究 top-2、query expansion、dense chunk 或 hybrid。当前批不要修改 localizer。

### Find 找到新窗口但最终仍错

这是有价值结果：说明 discovery→localization 改善，而 failure 已转移到 evidence recognition、belief update、state retention 或 stop。停止继续扩 Search/Find，转 Research State。

### Find 替代重复 Search，并改善或维持结果

进入 10–20 题批量验证。

## 7. 10–20 题 cohort 必须机械冻结

不要人工挑“Find 会赢”的题。

从候选协议运行前已经存在的历史 trajectory 机械筛：
1. search_calls >= 3
2. open_calls <= 1
3. 至少一个 docid 在两次以上 Search 返回
4. 该重复 doc 至少一次对应不同 raw window_ref/source range
5. 优先 incorrect / abstained / unsupported
6. 排除 API/harness error 主导轨迹
7. 排除 546、1094，因为它们已经用于开发

如果 10–20 条就全部使用；>20 用固定 seed 抽 20；<10 时只放宽第 5 条，不放宽 1–4。

在跑 v3a 前保存 qid 列表、筛选脚本和 seed。

## 8. 批量前的工程边界

当前 run_batch.py 共享一个 BCPlusTools，但 D/W Registry 必须 episode-local。

禁止把一个 SearchFindTools 实例跨题共享。

若要并行，应拆成：
- SharedRetrievalBackend：共享 embedding model/index/document DB，串行 GPU 访问；
- Episode SearchFindTools：每题独立 D/W registry，调用共享 backend。

如果不想先重构，可以顺序跑 10–20 题。

## 9. 批量主要指标

- same-doc global re-search rate
- local find relocation rate
- useful-new-window rate
- global search calls
- total tool calls
- find no-match
- invalid D/W handles
- Open usage after Find
- Accuracy / abstain
- tokens / cost

不要按 best-of 选结果，不删除失败。

## 10. 暂时不要改 Open

即使 v3a 成功，也不要马上删除 Open 或改名 Read。

后续独立比较：
- Search + Find
- Search + Find + Open/Read

评价的是“已经定位正确位置但上下文不足时，连续阅读是否产生 rescue”，不是 Open 总使用率。

## 11. 最终输出

生成 experiments/search_find_v3a/RESULTS.md，必须分别回答：
1. Tool capability 是否机械正确；
2. 模型是否实际选择 Find；
3. Find 是否产生新窗口；
4. 新窗口是否形成有效 Evidence；
5. 是否减少重复 global Search；
6. 最终答案是否变化；
7. 新的主要 failure 是什么。

不要只汇报 Accuracy。
