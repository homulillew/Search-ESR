# Search–Open 观察管理协议

`ObservedAgentSession` 在原有工具循环外维护观察记录。Search/Open 的模型可见返回、系统提示词和工具描述保持原样。CLI 的 Agent 模式默认使用这一运行时；原始 `AgentSession` 保留给冻结基线实验。

## 记录对象与职责

一次 Search 可能返回多篇文档。观察管理逐个验证窗口，并将工具参数、原始返回和区间指标写入同一事件。窗口正文必须等于来源文档的 `[offset,end_char)` 原文，标题必须等于 `title_span` 指向的原文。引用按原协议校验，不根据答案生成。

覆盖范围以 `(docid, document_sha256)` 为键。不同版本的同一文档分别记账；标题与正文按区间并集统计，避免重复计数。这里的字符是 Python 字符串位置，既不是 UTF-8 字节，也不是模型 token。

|内部字段|含义|
|---|---|
|`window_ref`|本次返回的不可变窗口引用|
|`repeated_window`|该引用是否已在本会话的有效事件中出现|
|`source_ranges`|本次实际返回的正文和显式标题区间|
|`body_new_spans`|正文相对之前有效观察新增的原文区间|
|`title_new_spans`|标题相对之前观察及本次正文新增的区间|
|`new_chars`|本次新增正文和标题字符数|
|`body_overlap_chars`|正文中已经返回过的字符数|

不同窗口可能完全覆盖旧范围，所以 `repeated_window=false` 不保证 `new_chars>0`。新增原文也不保证包含新证据，重复原文也可能值得重新解读。这些指标提供事实，不决定研究进度、候选正确性或下一步动作。

## 来源保存与恢复

SQLite 中保存事件、窗口区间、来源全文及最后完成的对话检查点。全文按文档版本保存，供进程重启后的 Open 继续读取当时的来源；完整缓存不计入已观察范围，也不会自动发送给模型。

恢复引用前先检查它属于当前有效会话，再校验保存原文的 SHA-256，重新注册到窗口构造器。即使外部语料被替换，旧引用仍沿旧来源读取。未知引用、已清空会话的引用、损坏来源会报错，不静默跳转到新文本。

每个状态文件同时只允许一个运行时写入，使用 Linux `fcntl` 文件锁。不同会话使用不同 SQLite 文件。当前没有来源缓存回收或自动上下文压缩，长会话的磁盘占用及 API 历史长度仍会增长。

## 对话事务

工具执行时立即落盘，成功终答后保存 messages 与最后事件序号。请求失败或用户中断时恢复上一轮 messages，并将本轮事件标记为无效；记录仍可用于审计。进程意外退出后，下一次初始化按最后成功检查点排除未完成尾部。

恢复粒度是完整对话轮，当前不续跑中断位置的工具循环。`/clear` 清空有效观察和对话，保留历史事件。实验脚本直接调用工具形成的检查点后事件，也会在下一次恢复时被排除。

状态文件保存模型名、接口、窗口版本、系统提示词及工具协议哈希。恢复时这些配置必须一致。实现源码没有嵌入该兼容检查；跨实现修订的实验应新建状态文件，并保存运行源码清单。

## 使用

```bash
python chat.py --state-file chat_logs/observations/my-session.sqlite
python chat.py --window-variant table_entry_safe --state-file chat_logs/observations/safe-session.sqlite
```

第一条在新文件上使用 baseline，已有文件则恢复已保存的窗口版本。第二条启用保守表格入口候选：补齐首行时若会裁掉先前表格的数据行，则保持原窗口。原 `table_entry` 仍可用于历史对照。

```python
from llm_chat.client import Config
from llm_chat.observed_agent import ObservedAgentSession

session = ObservedAgentSession(Config.load(), state_path="chat_logs/observations/demo.sqlite")
try:
    answer = session.ask("请搜索相关文档并给出依据。")
    summary = session.observations.summary()
    active_events = session.observations.events(active_only=True)
finally:
    session.close()
```

观察指标暂不注入模型上下文，不据此省略重复文本、阻止提交或强制 Open。后续 research state 可以读取这些记录，再独立实验如何向模型提供观察摘要。
