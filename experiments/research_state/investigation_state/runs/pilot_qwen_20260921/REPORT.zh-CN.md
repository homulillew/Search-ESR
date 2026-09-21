# Qwen 状态视图交付 pilot（2026-09-21）

本批6/6交付成功、6/6 usage完整，准入通过；独立正式S0见[正式批报告](../s0_qwen_20260921/REPORT.zh-CN.md)。pilot不充当正式样本，也不以语义评分筛选正式题目。

## 冻结与准入

基于1581ba5550ece437881200be7ce63cec5485d512。离线60项state测试及135项need_review测试通过；真实归档检查无skip。逐项重新复核固定笔记，bundle与上一批Atria完全一致；无正文、夹具、工具或实现修改。仅模型/端点改为qwen3.7-flash及用户给定的阿里云兼容接口，保留8192/180、SDK retries=0，不加enable_thinking、reasoning_effort或采样覆盖。

计划SHA256：`d32f66bd967b7f4603a2cd1ad99f7fc944d935d756f8a5b7ac2c96f617ba9550`。bundle：`328e8324e44b4167b608248c9e2ab8f2c8139a97b81b5458d4698155e3384106`。6次Actor，0 Reviewer，0工具执行，0隐藏smoke或补采。真实gate在阅读本轮语义输出前记录，随后正式计划冻结并启动。

## 交付与成本

6请求、6响应、0失败、0未知usage；报告token合计215182（输入192681、输出22501，其中reasoning22020）。flat101895，typed113287。费用金额未知：没有账单/有效计费单价，usage完整不等于货币成本已知。原始usage与完整响应均保留，reasoning没有替代正文参加评分。

## 逐题结论（仅pilot）

- 517：flat保留未验证1975精确过滤，typed撤回到1970s；这是可观察的过滤改善。但双方都继续家庭入口，没有落实警察角色任务。
- 546：双方撤回Players绑定检索比分链；typed多拆分资格问题。尚无结果，额外调用不能算收益。
- 776：flat搜泛化报告短语，typed另加American Anthropologist 1940，较具体地使用候选期刊任务。未证明期刊或人物身份。

严格完整响应合理性：flat 2/3，typed 3/3。所有正文为空、全部为工具提议：来源身份断言轴/正文支持/最终答案均不适用，而非自动正确。没有把空正文当缺陷。此处评价者为单一Codex辅助复核、已知旧案例，非盲评/独立人工金标。相似query的收益未知处保留unknown。

[逐分支全文和标签](BRANCH_ANALYSIS.md)、[机器审计](summary.json)、[前缀先行记录](review/prefix_attestation.json)、[准入决策](gate_decision.json)、[离线验证](verification.json)。下一步已按授权进入独立12次正式S0；不执行S1、检索或状态更新。
