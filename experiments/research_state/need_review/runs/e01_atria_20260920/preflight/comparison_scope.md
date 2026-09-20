# 跨模型比较边界（运行期间补充说明）

本说明在批次运行期间整理，已观察到前三条审查的机械截断，尚未阅读本批语义输出；不冒充独立事前预注册。首次调用前的真实配置和预期见preflight.json、approved_plan.json及pre_output_baseline.json。

本轮按用户要求重跑上一批C0/C1，保持完整原题/历史、参考索引、两提示词、四字段schema、legacy备忘、重复数、调度seed、Reviewer512 cap、SDK重试0及零工具执行。仅模型名和API基础地址改变；不根据中间表现修改预算或提示词。

上一批基线：e01_source_20260920T0314Z（Qwen3.7-flash）。本轮Atria-Dawn-Preview：不是另一次来源分层输入实验，也不是E1。未加入当前Agent的stop工具执行兼容开关，原始finish_reason及旧协议分类仍按原E0规则保留。意图合理和旧协议可执行性分别统计。

请求中的历史enable_thinking=false逐字保留；Atria是否支持/遵循未知，不能把这个参数名当成实际无推理的证明。供应商默认采样、模型tokenizer、Actor无显式输出上限的服务端默认值也可能不同。响应reasoning_tokens、finish_reason、可用正文/JSON、实际memo注入需分别核对。

参考官方文档：https://api.atria-asi.ai/docs（2026-09-20查阅，Chat Completions，256K上下文，max_tokens或max_completion_tokens）。这不证明所有百炼扩展参数有效；完整上下文能力由正式调用记录另验。

如果Reviewer预算先被推理消耗而没有可用JSON，记录真实失败/成本，不人为从reasoning字段补造审查。此时来源归属标签没有完整可评价对象，不能把“未形成有效审查”写成“来源判断全部错误”，也不能用回退Actor的好动作证明审查生效。

本轮的“能力”结论仅限三个开发病例的一次下一决策，不能等同于BC+最终准确率或模型能力上限。与Qwen比较需展示每题每重复和有效/回退状态，不能忽略实际Actor有无收到备忘的差别。
