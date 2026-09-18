# 观察摘要对照结果：2026-09-18

40 次真实 API 会话：6 道新题与 4 类局部控制，两组各重复两次。33 次完整终答，7 次因 2048-token 输出上限截断失败。全部失败保留，无补跑覆盖。固定 baseline 窗口、工具协议，后台账本始终启用；仅 visible 组附加机械观察摘要。

|检查|hidden|visible|
|---|---:|---:|
|完全重复判断正确|1/2|2/2|
|部分新增摘录正确|2/2|2/2|
|前三类控制核心事实正确|6/6|6/6|
|仍需阅读的角色题取得证据并答对|2/2|0/2|
|自然题完整终答|7/12|10/12|
|自然题后续 Search|41|29|
|自然题零新增 Search|2/41|4/29|
|自然题正文重叠比例|40.2%|52.2%|

当前结论：后台记账可用；这版可见摘要不升级默认。局部重复判断的改善伴随阅读不足控制退化，自主轨迹重复率没有改善。四轮测试不作为 BC+ 完整准确率评测。

## 记录

- [manifest.json](manifest.json)：参数与运行源码哈希；源码副本位于 `source/`。
- [tasks.json](tasks.json)、[schedule.json](schedule.json)：预置原文窗口、问题和固定随机顺序。
- [controls.offline.json](controls.offline.json)：仅离线使用的核心事实及参考区间。
- [results.json](results.json)：40 次尝试状态与使用量。
- [audit.json](audit.json)：530 个窗口、摘要、原文及工具对象校验；逐会话统计、聚合与完整配对数据。
- [manual_controls.json](manual_controls.json)：16 次局部控制审阅及原因说明。
- [validation/tests.log](validation/tests.log)：51 项测试通过。
- [validation/frozen_hashes.json](validation/frozen_hashes.json)：原冻结文件未变。
- [validation/artifacts_manifest.json](validation/artifacts_manifest.json)：后处理脚本、报告和结果的哈希。

每个 `<task>__<arm>__r<repeat>` 目录保存 `events.jsonl`、`trajectory.md`、`observations.json`、`state.sqlite`、`summary.json`。成功尝试另有 `answer.md`。请求日志包含真实注入的摘要，原始工具对象未修改；没有记录密钥或 HTTP 头。

全部实际已报告 API 用量为 1,062,571 tokens。该数值为两组及控制合计，不作为计费金额或效率提升结论。摘要最长 833 个本地 tokenizer tokens，未触发明细省略。
