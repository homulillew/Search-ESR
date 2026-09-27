# E1A 冻结记录（调用前快照）

- Base：`1e5b426b037eda91395664b820ce64cd4f12c708`（已核实远程 `experiment/minimal-semantic-package`）。
- 新分支：`experiment/minimal-recoverable-loop`。
- 本批：53 个真实 observation × 2 replicates = **106 个 Writer 请求**，20 qid，56 个召回项 / 112 个计分 slot。
- Provider/model：DeepSeek / `deepseek-flash`；temperature 0，JSON mode，max_retries 0，并发最多 8。
- 完整请求 SHA-256：`2b54f44622fb501f53365d654e0a1a465b84f8a8dfae4c657e7ca96e5b40646c`。
- 原任务书 SHA-256：`eaa9d3fe69395cfc0918c24feddd39b1eb50acb7de4e57d6a54596411380cd17`。
- Selection/参考/全部 Prompt/Schema/计分/失败政策提交后，由 `e1_admission/WRITER_FREEZE.json` 记录 request commit 和逐文件 SHA；该 manifest 再独立提交。
- `PREPARATION_VALIDATION.json` 记录实际离线检查；`analysis/POST_FREEZE_VALIDATION.json` 记录提交后重验及无授权拒绝测试。
- 保护历史实验文件 **22,238** 个；本轮不改历史结果。

本快照时 API 调用 **0**、检索调用 **0**。离线检查不代表 E1 语义门槛通过。

授权依任务书第47节：上述请求 commit/hash 完成后，另行取得本轮明确授权，才可发送。旧实验授权无效。本批授权范围仅 106 次 Writer；Admission 需等待实际候选，单独 review/commit/hash/估算/授权。

10 个 Fresh 问题已在任何模型调用前冻结。Recovery/Closure 来源 ID 已冻结，后续语义 Gold 与资格审查尚待前置 PASS。未来 E4 的精确 payload 随 Observation 才能确定，当前仅给出 Search 上限 176，不把预算上限当作付费授权。

严格采用全部数值门槛。安全但低召回仅作描述，不自动继续；若用户在调用前修改此规则，记录前瞻修订后重新冻结。各阶段实测结果另立不可变文件，本文件不回填成实验结论。
