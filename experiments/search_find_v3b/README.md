# Search–Find v3b：Tool Competition vs Verification State

本分支回答 v3a 首轮留下的核心问题：`find` 机制正确却 0/88 被调用，**为什么**。

三个竞争解释（正式预注册见 [HYPOTHESES.md](HYPOTHESES.md)）：

- **H1 Tool Competition / Action Dominance**：模型会用 find，但 v3a 里
  Search ⊃ Find——`search()` 的管线是「全局检索 → 逐文档 chunk 本地定位 →
  `_repair_anchor` → `_expand` → 400-token preview」，`find()` 走的是**同一条**
  本地定位管线。所以对「下一步做什么」这个决策点，find 在功能上被 search 严格
  包含。解除这个竞争，find 应该起飞。
- **H2 Verification State 缺失**：解除竞争也不够，模型缺的是从
  「Candidate Discovery」切到「Candidate Verification」的控制状态。首轮证据：
  模型在 reasoning 里**写出过正确解读又明确放弃**（qid 1094：引用 D37 的 1908
  分裂记载判定 "Inter fits"，把 Pirlo 列为候选约 15 次，然后转向编造的
  Fenerbahçe/Galatasaray 叙事）。
- **H3 工具名称 / API 形态 / 先验**：本轮**置后**，只在 H1 与 H2 都检验完之后
  才允许动。

## 工作流

`Failure → Hypothesis → Minimal Intervention → Mechanism Experiment → Decision`。
禁止 upfront 设计完整 Harness；每个阶段只做一个最小干预，测一个机制。

## 目录

| 路径 | 内容 |
|---|---|
| [HYPOTHESES.md](HYPOTHESES.md) | H1/H2/H3 正式预注册：措辞、可观测预测、反预测、判定区间 |
| [EXPERIMENT_PLAN.md](EXPERIMENT_PLAN.md) | 阶段 0–4 的计划、禁令、离线门禁清单、产出文件 |
| [FROZEN_STATE.md](FROZEN_STATE.md) | 首个真实模型调用之前冻结的状态 |
| `competition_probe/` | 阶段 1：Tool Competition Upper-Bound Probe |
| `checkpoint_rollout/` | 阶段 2：Checkpoint Partial Rollout（v3b orthogonal search） |
| `verification_state_probe/` | 阶段 3：Verification State Probe |
| [RESULTS.md](RESULTS.md) | 只写实际跑过的阶段 |
| [FINAL_CONCLUSION.md](FINAL_CONCLUSION.md) | 回答 10 个规定问题 |

**未跑的阶段不写结果**，目录可以为空。

## 当前状态

| 阶段 | 状态 |
|---|---|
| 1 Tool Competition Upper-Bound Probe | **完成**，判定 **弱信号**（Arm C exploratory_find 4/50，3/10 checkpoint）→ 下一步 Experiment 3 |
| 2 Checkpoint Partial Rollout | 未跑 |
| 3 Verification State Probe | 待跑（阶段 1 的预注册下一步） |
| 4 scoped_search | 未跑（H1/H2 都检验完之前禁止） |

详见 [RESULTS.md](RESULTS.md) 与
[competition_probe/20260922T174605.704525Z/SCORING.md](competition_probe/20260922T174605.704525Z/SCORING.md)。

## 不可触碰的东西

- `experiment/search-find-v3a` 上的全部既有文件与 run 目录（只读）。
- `probe_tool_affordance/` 的四个 probe 目录（只读；Arm A 复用时只拷出不写回）。
- `main` 分支。

## 与 v3a 的关系

v3a 首轮结论（`../search_find_v3a/RESULTS.md`，已复核）：`find` 机制正确但 0/88
被调用；定位缺口真实存在（qid 546 的正确答案在已发现的 docid 38231 里，落在
preview 窗外，`find('turned professional')` 机械返回 [642, 2157) 覆盖题目三条
约束）；把边界写进工具 description 不能提高采用率（A 0/50 vs B 1/50，
Fisher p=1.0）。复核发现两处叙述性计数错误，见
`../search_find_v3a/AUDIT_SECTION7A.md`——不改 RESULTS.md 正文，不推翻结论，
不需要重跑。
