# Search–Open阅读约定局部对照

两轮分别测试系统提示词和工具描述，生产代码均不变。每轮6个固定观察×2个实验组×3次重复，共36会话。原文观察固定，随后允许真实Search/Open，最多4轮后续工具机会。不是完整BC+评测或64轮rollout。

- `python experiments/prompt_contract/run.py --factor system`：只追加系统阅读约定。
- `python experiments/prompt_contract/run.py --factor tools`：只替换工具与参数description。
- `python experiments/prompt_contract/analyze.py <run_dir>`：核查原文、引用和实验输入，汇总机械指标。

[综合分析](../../全链路排查报告/Search-Open提示词与工具描述局部对照.md)与[描述准则](../../全链路排查报告/Search-Open工具描述与提示词准则.md)。首轮运行时脚本尚未增加factor参数，其原版在运行目录source中保留。

两轮未显示缺失细节取得率的稳定改善；不将候选版本自动部署。工具调用变化、核心答案依据和附加陈述可靠性分开评价。
