# First Observation：真实资产预检阻塞报告

基于远程 `edcfb92dce6ec195fecc73f13b839cb92ce985da`，初始工作区干净。六题已锁定，真实采集入口在初始化阶段退出；本轮没有O1、来源笔记或语义效果结论。保留原始失败，不修改环境后偷偷继续。

## 为什么旧检索可用，这次却失败

metadata文件存在，但缺少`query_prefix`字段。实际本机`BCPlus/scripts/search_bcplus.py`直接用代码常量`PREFIX`拼接查询；旧`llm_chat/agent.py`直接调用该Searcher，不依赖metadata提供前缀。新提交的`first_observation/retrieval.py:28`要求该字段必须存在，因此在加载模型和执行Search之前抛出`ValueError: Missing frozen retrieval query_prefix`。这属于新实验适配器与本机资产合同未对齐，不是证明数据或模型丢失。

历史Search/Open和Query实验报告记录过真实检索；当前metadata明确标注“restored 2026-09-20; not the original frozen adapter”，不能把当前恢复版当作旧冻结检索器。最近Atria/Qwen S0使用已归档checkpoint，不执行真实Search，所以不会触发新读取要求。当前外部BCPlus目录不随这个提交版本化，无法仅凭git历史确定该字段何时丢失，也不能声称它曾经存在。

## 实际资产与配置核对

- 本地8B embedding模型、四个权重分片、tokenizer、四个向量分片及documents.sqlite存在；只查询数据库行数，100195行，未读取文档正文或答案。
- 实际前缀为`Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery:`，这里的`\n`表示一个换行。原题未改写。
- 实际脚本`truncation=False`，自身上限8192；实验保护线1024更严格，二者差异本身不是阻塞。两种实际tokenizer调用对六题的token ID完全一致，均低于1024。
- 新适配器资产清单只收集`indexes/bcplus-qwen3-8b`，实际FAISS载入的四个pkl在相邻`indexes/qwen3-embedding-8b`，没有被原清单覆盖。另存24个实际资产文件的SHA256/大小/时间，未改原代码。
- 默认设备为cuda:0，现场空闲约6023MiB；cuda:1约24180MiB。未加载8B模型，不能声称GPU验收通过；后续应核对足够显存的执行设备。
- 生成配置候选沿用已授权qwen3.7-flash及原阿里云定制端点，8192/180、无额外推理/采样覆盖；未将此前建议的300秒擅自启用。`profile.proposed.json`只做结构校验，不是已执行冻结模型计划；未加载API凭据或做额外兼容调用。

## 六题全分母

select只保存数据集query_id/query投影及数据集hash，不使用gold、旧答案、历史前缀或人工笔记。选择hash为`37468ad159d74693cad79927c3ec0c272e856c89e0e9150d5b2bdfb6a431a9ce`。

| 题号 | 原题字符 | 含实际前缀的token | Search | O1/笔记 |
|---|---:|---:|---|---|
|517|555|151|未执行|未产生|
|546|434|150|未执行|未产生|
|776|615|169|未执行|未产生|
|519|600|164|未执行|未产生|
|191|369|95|未执行|未产生|
|71|283|84|未执行|未产生|

六题均为开发题；评阅者已知先前案例。本轮无法分析原文支持、笔记越界或遗漏，各轴not_applicable；未产生笔记不等于模型返回合法空notes。实际Search=0、初始化生成=0、来源笔记生成=0、Actor=0、Open=0。没有API用量或未知API请求；本地测试/tokenizer/散列的计算费用未计量。一次collect初始化失败退出1，未创建capture目录或逐题Search请求，不能记作六次Search失败。

## 离线验证

42项first_observation、60项investigation_state、135项need_review与20项检索窗口/观察pytest均通过，共257项、0跳过。第一次用unittest读取pytest函数文件，以及错误的单个need_review文件匹配，均运行0项并退出5；这些日志保留，但不计入通过数，随后使用正确入口。没有跑全仓测试，也没有GPU检索/模型服务的本轮实时验收。

[初始化错误](preflight/collect_initialization.log)、[环境和长度核对](preflight/environment.json)、[资产散列](preflight/asset_manifest.json)、[原题选择](selection.json)、[全分母状态](status.json)均已保存。没有提交SQLite、索引、权重、密钥或.env。

## 暂停依据与下一步

本任务[CODEX_TASK.md](../../CODEX_TASK.md)第3项明确要求：“环境不兼容时报告并暂停，修改需另留版本。”因此本轮停在真实采集前，不冒充已完成来源笔记阶段。

下一修改应限定在**真实检索适配与资产声明节点**：另留版本，使metadata前缀与实际脚本常量核验一致，并将真正读取的向量分片纳入冻结清单；记录GPU设备。保持原题、检索排序、窗口与笔记提示词不变，再生成新的采集记录。本轮未实施修改，未启动A/B、后续工具或rollout。
