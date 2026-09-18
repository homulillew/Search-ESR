# Search-ESR

通过 OpenAI 兼容 API 与大模型对话，并使用 BC+ 本地检索工具。

## 当前配置

已配置阿里云百炼北京工作空间的 OpenAI 兼容接口，模型为 `qwen3.7-flash`。
密钥通过 `DASHSCOPE_API_KEY` 读取，已保存在受 Git 忽略且权限为 600 的 `.env`。
也支持 `OPENAI_API_KEY`。程序优先读取非空环境变量，再读取 `.env`。

`DASHSCOPE_ENABLE_THINKING=false` 通过 `extra_body` 传递，当前关闭思考模式。
可设为 `true` 启用；普通对话只展示回答正文，不展示 reasoning_content。
其他服务商可将该配置留空以省略此参数。

## 配置与启动

当前环境已安装对话所需依赖。新环境先运行：

```bash
python -m pip install -r requirements-chat.txt
```

编辑仓库根目录的 `.env`（已创建，文件权限为 600），填写：

```dotenv
OPENAI_BASE_URL=https://你的服务商地址/v1
OPENAI_MODEL=你的模型名称
OPENAI_API_KEY=你的密钥
```

地址填写服务商提供的 API 基础路径，不要包含 `/chat/completions`。
阿里云密钥也可配置为 `DASHSCOPE_API_KEY`。
模型需要支持 Chat Completions 的 `tools` / function calling。
环境变量优先于 `.env`；也可通过 `--env-file` 指定其他配置。

从仓库根目录启动：

```bash
python chat.py
```

默认是 **BC+ 检索 Agent**。模型可自主调用：

- `search(query, k)`：检索文档，返回原文标题、定向原文窗口和不可变的 `window_ref`。每篇标题与正文合计最多 400 tokens。
- `open(window_ref, direction)`：以 `before`、`after`、`around` 继续读取，不重新排序。前后读取不重叠，around 保留旧窗口并扩展。详见 [窗口协议](llm_chat/RAW_WINDOWS.md)。

每轮对话最多调用工具 64 轮，达到上限后要求模型直接回答；可用
`--max-tool-rounds` 修改。回答提示词要求提供文档 ID 和 URL，并说明证据不足的情况。
首次调用 search 会加载 `/data/model/Qwen3-Embedding-8B`，约需 15 GB 显存，
可能耗时约两分钟；同一进程后续查询复用模型。模型只在需要搜索时加载。
对话请求和检索出的文档片段会发送给配置的 API 服务商。

Agent 模式逐轮请求工具，最终回答完整输出。普通对话模式默认流式输出：

```bash
python chat.py --plain
python chat.py --plain --no-stream
```

发送单条问题后退出：

```bash
python chat.py --prompt "请搜索文档，介绍青霉素的发现过程，并引用来源。"
```

对话内命令：`/clear` 清空上下文，`/save` 保存记录到 `chat_logs/`，`/exit` 退出。
Agent 模式自动将观察和最后完成的对话轮保存到 `chat_logs/observations/` 的独立 SQLite 文件。
工具返回内容不增加观察管理字段，系统提示词和工具描述不变。普通对话仍不自动保存。
`/save` 另行导出 JSON 对话记录，包含工具调用和文档片段。
历史记录随每次请求发送；长对话超过服务商上下文限制时请用 `/clear` 重新开始。
请求失败或用户中断时，本轮不会写入对话历史。

恢复之前的 Agent 会话，继续使用原来的窗口引用：

```bash
python chat.py --state-file chat_logs/observations/my-session.sqlite
```

文件不存在时创建新会话，存在时恢复最后一个成功完成的对话轮。原文按文档版本保存，
恢复后 Open 使用当时的原文；失败轮记录保留用于审计，但不计入有效观察。
`/clear` 同时清空有效观察和对话，保留历史审计记录。

默认仍使用冻结的 baseline 窗口。表格入口修复可在新会话中独立启用：

```bash
python chat.py --window-variant table_entry_safe --state-file chat_logs/observations/table-test.sqlite
```

`table_entry_safe` 在补齐表格入口时保留已经展示的其他表格记录；旧 `table_entry` 保留用于历史实验对照。
恢复时自动沿用保存的窗口版本，不能在同一状态文件中切换模型、接口、提示词或窗口版本。
观察管理只记录重复、重叠和新增原文范围，不判断语义进展，也不强制 Open。
详见 [观察管理协议](llm_chat/OBSERVATIONS.md)。

## 代码调用

```python
from llm_chat.client import Config
from llm_chat.observed_agent import ObservedAgentSession

session = ObservedAgentSession(Config.load(), state_path="chat_logs/observations/example.sqlite")
try:
    print(session.ask("请搜索并解释青霉素是如何被发现的。"))
    print(session.ask("相关文档还提到了哪些人物？"))
finally:
    session.close()
```

原始 `llm_chat.agent.AgentSession` 仍保留用于冻结基线实验；
普通 API 对话可使用 `llm_chat.client.ChatSession`。

## 目录

- `chat.py`：命令行入口。
- `llm_chat/`：API 客户端、对话历史与 BC+ Agent 工具循环。
- `.env.example`：配置模板；`.env` 和对话记录已加入 Git 忽略规则。
- `BCPlus/`：BC+ 数据、模型检索脚本、索引与文档，见 [BC+ 说明](BCPlus/README.md)。

## 验证

```bash
python -m pytest -q tests/test_chat.py
```

测试通过模拟 HTTP 验证 API 请求格式、流式响应、多轮上下文、错误处理、工具调用循环，
并使用真实 BC+ 文档库验证分页读取。真实 API 联调结果见 `chat_logs/dashscope_agent_check.log`。

接口依据：[OpenAI Chat Completions 官方文档](https://developers.openai.com/api/reference/python/resources/chat/subresources/completions/methods/create)。

百炼模型能力参考：[qwen3.7-flash 官方说明](https://help.aliyun.com/zh/model-studio/qwen3-7-flash)。

## Rollout 实验

单题运行与轨迹目录约定见 [experiments/README.md](experiments/README.md)。运行 `python experiments/run_rollout.py --qid 186`，按方案版本、题目 ID 和 UTC 运行时间分别归档。
