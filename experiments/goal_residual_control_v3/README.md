# Goal Residual Control v3

基线：`32de7c8`；独立分支 `experiment/goal-residual-control-v3-admission-structured`。

仅测试两项修复：临时 Current Actor Gap 条件化 admission，以及同一模型的服务端完整 schema 约束。原问题、semantic state、工具、controller 与 horizon 不变。

执行次序：设计审计 → 离线检查 → 服务端 capability → 24 历史请求 preflight → Admission Replay → 原 20 transitions → 原 10 qids 三轮 loop。后续阶段有 gate；不可用时必须报告未执行。

入口：[V3_DESIGN_AUDIT.md](V3_DESIGN_AUDIT.md)、[PROTOCOL.md](PROTOCOL.md)、[FROZEN_STATE.md](FROZEN_STATE.md)。本文件创建时只完成离线检查，尚无 v3 模型结果。
