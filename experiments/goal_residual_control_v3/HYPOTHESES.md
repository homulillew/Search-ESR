# Hypotheses and interpretation

- H-A：在相同已观察窗口及 pre-state 下，Current Actor Gap + admission 条件减少 incidental writes，而 useful admission recall、来源支持、时间/关系限定与候选反驳不恶化。
- H-B：同一 DeepSeek 模型的服务端完整 schema 约束消除纯 serialization failure；registry、semantic consistency、API/length failure 仍单独评估。
- H-C：更干净 online state 接近同批 oracle state；因 oracle 与 online 的来源事实组合不同，不能直接复制 closure label。
- H-D：在共同 Writer 上比较 L0/L1/L2，所有结果方向均可接受，不预设 L2 胜出。

采用设计审计中的六条解释规则。全体改善先归因于共同两项修复；L2 仅改善停止时解释为 closure 辅助；L0 相当或更好时不得宣称 persistent Gap 本身有害。低 resolution 不靠增加 State 字段补救。
