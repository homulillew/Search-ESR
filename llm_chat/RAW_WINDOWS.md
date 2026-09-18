# Search / Open 原文窗口协议 v002（机械修复）

当前默认 Agent 暴露 search 与 open，文档向量检索和 64 轮预算不变。Search 自动完成一次定向阅读，Open 只按位置继续读取。没有 focus、gap、强制阅读或阶段控制。

## Search

`search(query, k=5)` 继续使用 Qwen3-Embedding-8B 文档召回。文档内以原 400-token 块进行 BM25 定位，在命中块中选择句子或行作为锚点，再从完整文档扩展。展示窗口不受命中块边界限制。

每篇返回原文标题、URL、docid、document_sha256、连续原文、window_ref、offset/end_char、前后是否还有内容以及 token 数。标题仅从 `title:` 或 Markdown 一级标题提取，最多 48 tokens；没有可靠字段时为空。标题与正文合计最多 400 tokens，URL/JSON 等接口开销另计。内部字符位置仍保留在返回和日志中，但模型不需要构造 offset 参数。

窗口 builder 使用句子/行启发式；表格按行处理，不保证远处表头或完整比赛记录。全文原始结构未清洗，普通标题、HTML 和复杂表格可能处理不佳。不足预算的长单元允许截断。没有词面匹配时明确回退前缀。所有片段都是原文，不是已判定成立的证据。

## Open

`open(window_ref, direction)` 的 direction 必须为 before、after 或 around。

- before：读取旧窗口之前的相邻原文，新窗口末尾等于旧窗口起点。
- after：读取旧窗口之后的相邻原文，新窗口起点等于旧窗口末尾。
- around：包含旧窗口，并向两侧扩展；没有 query 排序。

before/after 不额外重复旧内容，默认标题加正文上限 1200 tokens。around 初次至少按 1200-token 总额度尝试，后续增加正文额度，标题加正文最多 2400 tokens。around 已覆盖全文时返回 document_complete；仍有原文但达到上限或附近单位放不下时，返回 no_expansion_within_budget；before/after 抵达所请求方向的文档端点返回 document_boundary。此时引用可能不变，避免把重复内容伪装成新观察。仍可使用 before/after 继续读取。

## 引用与生命周期

窗口的内部记录为冻结对象：docid、全文 SHA256、起止位置。ref 由版本、文档版本和范围确定；相同原文范围复用引用，不同范围产生新引用。调用展开不会修改旧记录。返回记录中的 parent_window_ref 记录本次展开来源，不属于窗口身份。

窗口与文档版本在当前工具实例生命周期内保留；批次共享串行工具实例。进程重启后不能仅凭引用恢复，原文与引用已写入完整工具轨迹。当前未做持久化注册表或缓存淘汰，长批次需要监控内存。

内部 get_document 字符分页继续保留，供历史离线实验与回读检查使用，不出现在当前模型工具 schema 中。

## 运行与验证

`python chat.py` 默认使用此协议。`python experiments/run_rollout.py --qid 517` 保存新版本到 runs/v002_raw_windows_mechanical，源码快照覆盖 builder、locator 和边界实现。

`python experiments/snippets/check_raw_windows.py` 在四篇真实文档上离线检查 Search、三个 Open 方向及翻页到末尾，不调用模型或重新召回。

本版本已经接入，但尚无新在线 rollout 的准确率或重复搜索改善结论。

## 机械修复记录

保留原 BM25 分块、父块与局部锚点排序。锚点选出后，从全文预识别的句子/行边界尝试补齐范围；若完整范围超过预算，则保留原锚点。Markdown 管道表格能明确识别分隔行时，尝试连同表头到命中行一起返回，仍必须是连续原文并满足预算。

空 title 字段不再跨行吸收正文。边界数组在文档注册时预存；token 计数采用每工具实例最多 256 项的 LRU 缓存。缓存只是计数加速，不淘汰原始文档或窗口引用。对预算内无法完整保留的超长单元仍不保证语义完整。

四篇固定文档的性能检查中，初始搜索窗口未变化，重复操作更快；最长约 115 万字符 HTML 的首次处理仍约 6 秒。详细结果在全链路排查报告第 18 节。未进行新 API rollout，未改变 research state 或模型字段组织。
