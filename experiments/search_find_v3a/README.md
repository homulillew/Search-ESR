# Search–Find v3a：文档发现与局部定位解耦实验

本目录记录 experiment/search-find-v3a 分支上的候选协议。它不是默认 Harness 的升级结论，而是一个最小机制实验：

> 当前 Agent 是否因为缺少“已发现文档内的定向查找”能力，而用重复的全局 Search 来完成局部重新定位？

## 本轮核心机制

保持当前全局检索器、Search 的 400-token 定向预览和 Open 的位置扩展语义不变，新增 find(doc_ref, query)。

find 只允许操作本轮 Search 已发现的文档，并复用当前 RawWindowBuilder 的文档内 BM25 定位能力。词面无匹配时显式返回 no_match，不回退文档前缀。

同时加入 episode-local 短句柄：

- D#：已发现文档；
- W#：已观察原文窗口。

底层真实 docid、document_sha256、raw window_ref 和 offset 仍由 Harness 保存，模型不需要复制这些机器标识。

## 当前刻意不改的东西

为了第一轮归因，本轮不修改 Qwen3-Embedding-8B 全局 Retriever，不缩短 Search preview，不把 Open 改名 Read，不删除 around，不改 Open budget，不加入 top-2 find，不加入 chunk embedding，不加入 Research State，也不强制 Find/Open。

因此本轮首先回答“Document-level local relocation 是否有行为价值”，不是最终 Search/Find/Read 协议优劣。

## 工具语义

Search：发现候选文档，继续返回当前 400-token query-localized preview。模型看到稳定 D# 和预览 W#。提示明确 preview 不是全文，缺少信息不代表文档没有该信息。

Find：find(D3, "father parents family")。只操作已发现 D#；使用当前文档内 BM25；返回一个 exact raw-text W#；相同输入 deterministic；无匹配返回 no_match。

Open：保持当前 before/after/around。只用于已经定位窗口的相邻上下文，不负责寻找文档其它位置。

## 运行

Baseline：

    python experiments/run_rollout.py --qid 546

v3a：

    python experiments/run_rollout.py --qid 546 --agent-protocol search_find_v3a

v3a 输出进入 experiments/runs/v003a_search_find/qid_<QID>/<UTC>/。

events.jsonl 除模型可见 tool_result 外，还保存 tool_internal，其中包含 D/W 到 canonical source 的映射、原始 docid/SHA/raw window ref 与 Find locator 元数据。这些字段不发送给模型。

## 当前限制

1. D/W Registry 目前只在一次 rollout 进程内存在，尚未接入 ObservationStore 的重启恢复。
2. run_batch.py 仍只适用于 baseline 共享工具；SearchFindTools 不能跨题共享。
3. Find 当前 top-1；是否改 top-2 要先做离线 recall/token 对照。
4. Search preview 仍为当前 400-token 窗口；缩短 preview 属于后续独立消融。
5. 本分支尚未产生新的真实 API 实验结论。

下一步严格按 CLAUDE_NEXT.md 执行。
