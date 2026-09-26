# Pre-call design audit

已核验远程 exact HEAD、阅读前序 Dynamic Progress 的 FINAL_CONCLUSION、P1、decomposition sensitivity、exploration、GATE、DESIGN_AUDIT、PROTOCOL，以及 Frontier Generation、Deferred Recovery、Goal Residual v3.1 结论。

前序证据：B 能减少 Direct 的 premature closure，但 primary precision 76/103；单关系探索 44/50=88% 仍未 formal-confirm。P17/P19 各两次 stable false closure，探索未包含它们。FULL 提高 precision 但 reasoning 成本约 2.52×，还存在 false/missed closure，不能用来每轮替代 Progress。

本轮将 unresolved 的单个有效反例，与 resolved 的全体 material support 区分；Audit 看不到 Light 建议。LL 对照隔离单纯第二样本的价值。模型/transport/tools 均固定。旧 JSON transport 缺少 literal JSON 的错误由 dummy canary 提前排查。

鲜样本库耗尽问题是真实限制：114 个 inventory 条目经 exact Q+Claims 排除与去重只剩 44 个，9 qids。所有 44 个均做 Q+Claims-only review。仅 5 个 fresh resolved，且 3 个音乐人+2 个电视剧；强 near-closure 仅 q435 的不同版本，多数受每 qid≤4 与保留全部控制限制，主集仅 1 个。主集 19 unresolved 不应被描述为 19 个 near-closure。材料冲突仅压力集有覆盖。这个设计可测 fresh single-relation precision，停止层泛化结论必须保守。

24 主样本和9压力样本共198次正式提交，另1次 dummy canary；探索若执行最多24次。未使用新输出、gold answer、source全文或 future 选 primary。模型可见边界通过请求 whitelist 固定。语义标签非穷尽，不按字面匹配评分。

用户已明确授权实现、真实调用、审查、commit/push；不再请求批准。无子代理，无额外模型 reviewer。本轮不修改生产 Retriever/State/Controller。
