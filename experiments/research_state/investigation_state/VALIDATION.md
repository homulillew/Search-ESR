# 本次交付的离线验证

基于远程 `396592c3ed371a6be260ca0a40434d1f6afc821f` 的接口实现，2026-09-21完成本地检查。本次只新增调查状态实验包、测试和设计文档；不修改默认Agent、Search/Open、Query或Need Review。

## 实际执行

```bash
python -m unittest discover -s tests -p 'test_investigation_state.py' -v
python -m experiments.research_state.investigation_state.run --help
python -m compileall -q experiments/research_state/investigation_state
```

60个测试方法：**59通过，1跳过**。完整三题、两视图、两重复的合成前缀模拟执行通过：12次mock Actor调用，完整保留每次的两个工具提议，导出12张卡片；0 Reviewer，0真实模型调用，0工具执行。

覆盖：flat/typed无损还原及序列化后分组顺序；来源身份与quote；问题不作为候选事实；assistant不能作为observed_finding；同doc不同窗口不合并；重复window_ref排名分数变化；冲突引用拒绝；同参数/可见原文关联；可空task不触发停止；profile端点/预算/超时保护；SDK/源码/计划漂移；篡改请求/响应检测；多工具；超时未知成本；reasoning-only不伪装正文；坏日志连续前缀；中断分母；mock不能验收正式运行；usage缺失和算术异常；空人工标签导出。

## 不能冒充完成的检查

本地不能直接clone完整仓库，也没有完整三份归档checkpoint。`test_builtin_real_checkpoints_and_quotes` 因此明确skip。虽然通过GitHub读取了检查点元数据和关键原文片段，**没有在本地完成三个完整真实JSON的prepare**。Codex在完整checkout必须运行该测试及prepare，quote/blob不符即停止，不跳过以继续付费。

完整旧test_need_review和全仓测试未在本次重跑。只复用了下列三个原模块，并核对本地字节的Git blob与远端一致：

| 文件 | Git blob |
|---|---|
| need_review/checkpoint.py | `600b089e3ee353d029edb007aa608dd9c32e7a85` |
| need_review/node.py | `a8b117e5f08839398c80627731c0cfdfb5194db0` |
| need_review/accounting.py | `740e4b72f73cf46609b9b84249d93238dd2daebe` |

新增测试在真实的这三个模块上执行，不用伪造分类器替代它们。这些本地副本不属于本次提交变更。

模型profile只是待验收候选，未验证新API、实际推理控制或任务性能。没有真实实验结果，不能把mock调用称为模型测试通过。
