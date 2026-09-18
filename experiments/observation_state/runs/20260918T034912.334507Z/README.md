# 新题边界与观察管理：2026-09-18

本目录固定预选 12 道未用于此前七题讨论的 BC+ 题目。模型为 qwen3.7-flash，thinking 关闭，原系统提示词与工具描述保持不变。仅评估局部工具链，未做 gold 答案评分。

|材料|内容与结果|
|---|---|
|[protocol.json](protocol.json)、[tasks.json](tasks.json)|实验范围、随机种子 919、预选 12 题|
|[queries.json](queries.json)|真实首轮 query；各 `qid_*` 目录有请求响应与两版窗口|
|[observations.json](observations.json)|60 个不同文档的自然首轮窗口；两版无变化|
|[边界汇总](boundary_audit/summary.json)|180 个方向读取、60 个重复记账检查通过；10 个人工截断压力样本通过|
|[初次 API 结果](live/results.json)、[审计](live/audit.json)|12 次尝试，11 次成功，1 次最终请求 BadRequestError；260 个已生成窗口原文、传递一致性通过|
|[独立重试](live_retry_20260918T040012Z/results.json)、[审计](live_retry_20260918T040012Z/audit.json)|qid=905 / table_entry 重试成功；25 个窗口；重启恢复检查通过|
|[新结构风险](live/qid_905__table_entry/structural_changes.json)|文档 40817 的两处左侧表格记录被旧候选裁掉|
|[安全候选回归](safe_check.json)|旧局部 16/19 → 17/19，无退化；60 个新首轮窗口不变；两处风险被拦住|
|[安全候选新题尝试](live_retry_20260918T040449Z/results.json)、[审计](live_retry_20260918T040449Z/audit.json)|qid=905 / table_entry_safe；四次后续 Search 后最终请求超时，保留失败|
|[CLI 恢复验证](cli_resume/validation.json)、[日志](cli_resume/cli.log)|实际 API 成功 Open 旧引用；模型称为新增的内容实际 `new_chars=0`|
|[安全候选 CLI 日志](safe_smoke.log)|两次 Search、一次 Open，回答 Policeman 1；状态保存在 safe_smoke.sqlite|
|[自动化测试](validation/tests.log)|49 passed|
|[冻结文件校验](validation/frozen_hashes.json)|原冻结文件及 tokenizer 哈希保持一致|
|[最终实现清单](validation/runtime_manifest.json)|本轮最终运行时、脚本、文档与测试的哈希；源码副本在 final_source|

每个 live 会话目录保存 `events.jsonl`、`trajectory.md`、`observations.json`、`observations.sqlite` 和 `summary.json`。成功会话另有 `answer.md` 和 `recovery.json`。失败轮观察会保留但标为 inactive；原始生成窗口数与有效覆盖统计不可混用。

首批 11 个成功会话与独立重试共 12 次恢复检查均通过。恢复检查直接调用工具，与模型主动 Open 的行为评估不同。4 轮短轨迹中多次达到强制终答，不能由此推断完整题目已解决。不同运行源码以各自 `manifest.json` 与 `source/` 为准；最终测试还包含随后增加的安全限制和文件锁。

`boundary_audit_reused_excluded` 是复用了观察状态的中间运行，已排除，不计入正式表格。
