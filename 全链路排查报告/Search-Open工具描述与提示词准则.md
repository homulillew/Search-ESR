# Search–Open工具描述与提示词准则

Search已经能直接提供相关原文，但真实API验收表明，模型仍可能反复检索同一窗口，或在相关表格尚未展开时结束。接口描述需要让模型理解工具能取得什么信息、何时值得调用，以及返回范围能支持怎样的结论。描述本身不能保证模型遵守这些约定，因此每次改动都需要行为对照。

## 描述应覆盖哪些内容

用户提出的六项可以作为检查清单。信息应放在最合适的位置，不要求每个工具都写成六个长段落。

|检查项|Search–Open需要说明的内容|主要位置|
|功能|Search检索本地文档并返回查询相关的局部原文；Open沿已有窗口继续读取|工具description|
|典型场景|寻找其他文档用Search；检查已有相关文档的邻近正文用Open|工具description；跨工具取舍在系统提示词|
|边界与反模式|局部未见不等于全文没有；已有信息充分时无需为流程而Open；Open不会按新query重排|能力限制写工具description；结论原则写系统提示词|
|输入约束|query非空及长度、k默认和范围；window_ref来自本会话返回；direction的意义|JSON Schema及参数description；代码负责校验|
|输出约束|原文窗口、文档身份和来源、引用、范围及边界信号；返回可能不含答案|工具description解释重要字段；完整结构留接口文档|
|工具配合|发现文档后可沿window_ref继续读，读到足够信息可回答，需要其他来源仍可Search|说明可选路径，不规定Search后必须Open|

此外需要检查错误与终止状态：未知引用是调用错误；document_boundary表示该方向到达文档边界；document_complete表示已包含全文；no_expansion_within_budget表示当前预算内无法继续扩展，不能解读为没有更多正文。

## 几条需要遵守的准则

1. 描述与实现一致。不能承诺“最关键证据”“完整上下文”或“一次找到答案”；当前只返回一个查询定位窗口，定位可能不理想。
2. 优先写影响模型决策的信息。has_more表示位置上仍有正文，不表示那部分必然相关。around包含旧内容，新增范围不等于整次返回。不要把BM25参数、哈希算法等实现细节堆进模型可见描述。
3. 参数的机械约束放在Schema和代码。文字解释语义，例如window_ref应复制已有值，不能用docid代替。服务端未必严格执行Schema，运行时验证仍需保留。
4. 系统提示词负责全局原则与跨工具选择。工具description负责局部能力、输入输出和边界。避免把同一规则在两处反复强化，形成多个控制来源。
5. 描述“值得考虑的动作”，不把经验写成普遍强制。相关表头出现在窗口末端是续读理由，但无需规定每次检索必须Open。
6. 每条新增约定都应对应可观测行为与对照样本。增加读取时，也检查原本信息充分的样本是否多做无效调用。
7. 一次只改一个因素。先测试系统阅读约定，再独立测试工具描述；工具实现继续冻结。不根据一个失败样本持续追加专属例外。

工具描述能帮助模型选择动作，不能担任运行时保证。Harness记录实际观察、来源、预算与进展信号；模型判断缺失信息的语义、应读哪篇文档、是否换搜索方向。持续无进展的研究阶段控制留到统一状态机制，不在工具描述里模拟一套状态机。

## 当前实现的具体缺口

当前Search/Open描述已经有基本功能和相互引用，也已有“窗口未见不等于文档没有”的系统规则。主要不足是：

- Open参数没有解释引用来源和各方向的选择含义；
- 未解释has_more与边界状态；
- “需要上下文时Open”较抽象，尚未把“相关文档已找到、所问细节未展示”与续读联系起来。

这些是待验证的改进方向，不意味着文字补齐就能稳定解决问题。第一轮只测试最后一项：系统提示词追加一般阅读约定，TOOLS保持逐字不变。随后第二轮恢复原系统提示词，独立测试工具及参数description，类型与范围等Schema约束不变。两个候选版本均仅用于实验，尚未上线。

## 本轮唯一提示词改动

追加于现有系统提示词末尾：

```text
When a returned document is relevant but the requested detail is not in the current window, consider reading that document further before reformulating the search or concluding that the detail is unavailable. A relevant section heading, table header, or unfinished passage near a window boundary is a reason to inspect the adjacent source text with open. Use search when you need other documents or a different information target. If the visible text already supports the answer, answer without opening merely to satisfy a workflow. Distinguish a detail not seen in the current window from a detail absent from the document.
```

该段不包含实验答案或具体人名，未添加强制Open、引用强化、gap或重复搜索拦截。这样可以观察阅读约定本身的效果。完整计划见[固定观察对照方案](../experiments/prompt_contract/PLAN.md)。

## 依据与适用范围

Anthropic的[工具定义文档](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools)建议解释功能、适用及不适用情况、参数含义与限制。[工具工程文章](https://www.anthropic.com/engineering/writing-tools-for-agents)强调根据实际调用和评测迭代工具设计。这里采用这些一般设计原则，不将其当作Qwen3.7-flash效果保证；本仓库的结论以实际API对照为准。

实验结果见[两轮局部对照报告](Search-Open提示词与工具描述局部对照.md)。完整工具描述候选保存在[tools_candidate.json](../experiments/prompt_contract/tools_candidate.json)。两轮均未显示缺失细节取得率的稳定提升；描述准则不能替代行为验证。
