# BC+ Agent Search 实验

## 目录约定

```text
experiments/
  run_rollout.py
  runs/
    v000_baseline/                 # 历史原始 Agent 策略
      qid_186/
        <UTC时间戳>/               # 每次运行独立保存，不覆盖
          manifest.json            # 配置、预算、源码哈希、数据哈希
          input.json               # 原题，不含标准答案
          retrieval_metadata.json  # 检索配置
          source/                  # 本次执行源码快照
          events.jsonl             # 逐事件保存，失败时也保留
          trajectory.md            # 完整轨迹的可读版本
          answer.md                # 成功返回的最终回答
          summary.json             # 用量、工具次数、结束原因
```

运行：`python experiments/run_rollout.py --qid 186`

v000 保持原始 system prompt、工具及 Agent 循环，默认 64 轮工具调用；达到上限后额外一次 API 请求禁用工具以收尾，因此最多 65 次 API 请求（不计 SDK 内部重试）。历史 12 轮运行保留原配置，以各次 manifest 为准。自然回答与预算强制回答分开记录。当前脚本运行 v002_raw_windows_mechanical，使用统一 Search/Open；历史 v000 轨迹和源码快照保留。新运行位于 runs/v002_raw_windows_mechanical/。

API 请求记录 SDK 调用参数，响应记录 SDK 解析的完整响应；不记录 API key、HTTP 头或未返回的内部推理。SDK 内部最多重试 2 次，当前不分别记录 HTTP 重试。工具结果记录模型可见全文及片段哈希；参数错误的模型可见结果也能从后续请求中复核。标准答案仅用于独立离线评估，不注入运行上下文。

所有时间戳使用 UTC。每次运行均从空会话开始。`events.jsonl` 是原始轨迹；`trajectory.md` 重复展示完整请求上下文，文件较大属于预期行为。评估结果另存于对应运行目录，明确区分人工判断与自动评分。

## 批量运行

`python experiments/run_batch.py --qids 311 776 324 546 517 1094`

该入口默认并行 API、串行共享检索，详见下一节；新轨迹存于 `runs/v002_raw_windows_mechanical/qid_<ID>/<UTC时间戳>/`。

## 并行批次

`python experiments/run_batch.py --qids 311 776 324 546 517 1094 --workers 6`

每题独立 API 会话并行执行；本地检索通过单独工作线程串行执行，共享一份模型和索引，避免显存重复占用。文档数据库也由该线程访问。工具耗时包含排队时间，不能与单题运行直接比较延迟。批次入口位于 `experiments/batches/<UTC时间戳>/batch.json`，指向各题原有版本目录下的运行。每题 manifest 保存 batch_id 和本次 runner 源码快照；工具版本为 v002_raw_windows_mechanical，研究状态与强制阅读机制未加入。

## 离线片段实验

见 [片段选择原型与运行方法](snippets/README.md)。v001–v005 片段实验均为离线分析。当前另行接入统一原文窗口工具，协议见 [RAW_WINDOWS.md](../llm_chat/RAW_WINDOWS.md)。

## 新题边界与观察管理

见 [实验方法与记录](observation_state/README.md)。本轮扩展了新题的 Search–Open 呈现边界检查，并接入可恢复的观察账本；原有 rollout 入口保持冻结基线，`chat.py` 的 Agent 模式使用新观察运行时。

观察账本是否应对模型可见，见 [观察摘要最小对照](observation_summary/README.md)。该实验候选保持独立，默认运行时不注入摘要。

## Query 初始化

见 [Query 初始化节点](query_initialization/README.md)。已实现单/双方向局部对照，完成两批开发共 24 次及 20 道留出题共 120 次真实 API 尝试。执行可靠性提高，但入口改善尚不稳定；候选保持独立，未替换默认 Agent。完整轨迹、原文标注和报告见该目录。
