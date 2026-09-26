# Bounded materiality exploration

执行前 plan/prompt/24 请求及已存在 baseline 在 `b9a5936` 提交冻结。只有这一版追加 prompt，未做 FULL、未重采样、未进行第二次探索。

12 个错误分析后选择的 checkpoint，5 qids，6 resolved + 6 unresolved；每个两次。非 fresh、非随机，不替代主实验。

| 指标 | 原 Audit（复用） | Materiality Audit |
|---|---:|---:|
| 有效输出 |24/24|24/24|
| False closure |0/12|1/12|
| Correct closure |4/12|9/12|
| Valid blocker presence |11/12|9/12|
| Blocker precision |11/20 (55.0%)|9/14 (64.3%)|
| Certificate adequacy |4/4|8/10|
| Over-demand 输出 |8|4|
| Reasoning tokens |182,084|142,273|

音乐人控制 A07/A08/A09 均恢复闭合；电视剧 A18 恢复，两次 A19 只有一次恢复。S03 游戏控制仍两次被额外公司成立/开发时点要求挡住。降低过度拒绝并未普遍解决 materiality 判断。

**P17/S01 新增一次错误闭合**：只用 episode page 与一个 plot match 作为 certificate，缺少 total seasons 和 roommate-sacrifice 关系；certificate 还将未注明 season 的事件写成 season four。另一 replica 虽拒绝，但解释中也把该事件称为已观察的 season-four 事件，因此按冻结 prefix-only rubric 无完整有效 blocker 信用。

P19/S02 两次仍正确指出 roommate 关系；日期归属 S07 和 zodiac S08 也保留两次有效拒绝。S09 一次正确指出 total seasons，另一次选择冗余的 literal male-lead label。A24 两次都明确拒绝 fixture/event join，未再预设具体比赛已有 95th-minute 事件。

A18 一次 certificate 虽正确闭合，却把观测到的 S3E13/S4E7 描述成 final/midpoint。冻结规则允许它们足以识别剧集，同时仍要求 certificate 不把未观测的相对位置写成既定事实；该 certificate 因此不充分。另一次 certificate 只保留已观察 episode index，合格。

预定探索目标（correct closure≥11/12、false closure=0/12、certificate≥90%）全部未满足。不能部署该追加 prompt，不能改写 C1/C2/C3 或进入 Frontier。结果支持一个有限诊断：materiality 放宽能减少部分 missed closure，但会重新引入 strong-candidate false closure；需要同时校准两端，单纯要求更严格或更宽松均未解决。
