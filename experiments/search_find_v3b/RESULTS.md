# Search–Find v3b 结果

**只写实际跑过的阶段。** 本文件目前只覆盖阶段 1（Tool Competition
Upper-Bound Probe）。阶段 2/3/4 未跑，不写结果。

---

## 阶段 1：Tool Competition Upper-Bound Probe（已完成）

- probe_id：`competition_probe/20260922T174605.704525Z`
- 冻结参数与门禁：`FROZEN_STATE.md`；门禁 123/123 PASS（dry-run
  `20260922T173041.831538Z`，零付费调用）。
- 样本：10 checkpoint × 3 arm × 5 = 150 条；**新调用 100 次**（arm B、C）；
  arm A **复用** v3a affordance probe 的 50 条（理由见 `EXPERIMENT_PLAN.md`）。
- **未执行任何工具**（probe 只允许 `chat.completions.create`）。
- 成本：100 次新调用 ≈ **¥1.30**（输入 2.85M，其中缓存 2.40M；输出 0.20M）。

### 主指标：首个动作

| 分类 | A `as_is` | B `search_hidden` | C `local_only` |
|---|---|---|---|
| `search`（真实调用） | **45/50** | — | — |
| `search`（对**未声明**工具发调用） | — | **41/50** | **36/50** |
| `find` | 0/50 | 2/50 | 4/50 |
| `open` | 1/50 | 1/50 | 3/50 |
| `answer-stop` | 4/50 | 6/50 | 7/50 |
| `invalid` / `other` | 0/50 | 0/50 | 0/50 |

find 二分：**6/6 全部为 exploratory_find，0 次 confirmation_find**。
Arm C exploratory_find = **4/50**，分布在 3/10 个 checkpoint。

逐条判定依据、reasoning 尾部逐字引用、边界情形讨论见
[SCORING.md](competition_probe/20260922T174605.704525Z/SCORING.md)。

### 判定：**弱信号** → Experiment 3

按 HYPOTHESES.md 的预注册区间，Arm C exploratory_find ≤ 4/50 判为弱信号。
四个预注册的边界读法（B 高 C 低 / 增量是 confirmation / 增量是 answer-stop /
invalid ≥10）**没有一个触发**。下一步：**Experiment 3（Verification State Probe）**。

### 三个必须随结论一起读的限定

1. **4/50 卡在弱/中边界。** Clopper-Pearson 95% 上界 = 17.4%，跨进中区间。
   判「弱」是按预注册规则对观测计数施加判据，**不是**对真实率的证明。
   Fisher 双侧 A vs C（find）p = 0.1175，未达显著。
2. **「移除工具」没有真正移除动作。** arm B/C 的 41/50 与 36/50 是对
   **不在 schema 里的 `search`** 发出的 function call——provider 不拦截未声明函数名，
   返回 `finish_reason=tool_calls`。所以本 probe 测的是「search **不被声明**时模型做什么」，
   而不是「search **不可用**时模型做什么」。这是本批最重要的单一观测，
   它把 H1 的供给面机制推向一个不利于 H1 的方向：下一步动作策略对 tools 菜单
   几乎不敏感，对 search 的偏向在策略层先验（被 prefix 里大量成功的
   search→preview 循环强化），而不在「可选工具里有更好的」这一层。
3. **6/6 exploratory 这个事实本身不支持 H2 的典型形态。** H2 预测 find 出现时
   主要是 confirmation（加固先验）；实测 0 次 confirmation。但 n=6 太小，
   只能作为弱观察，不能反过来判 H2 不成立。

### 与 v3a 首轮的衔接

v3a 首轮：find 0/88；把边界写进 description 的 affordance probe A 0/50 vs B 1/50
（Fisher p=1.0）。本轮把干预从「改 description」推进到「把 search 从动作空间移除」，
find 仍然停在弱区间（C 4/50，p=0.1175）。三轮干预——讲清楚、移除声明——
都没让 find 起飞。

一个正面观察：1094 seq=53 sample=1 里，arm C 的模型用 exploratory find
回到 D37 查「1908 因外援签约分歧的分裂」——这正是 v3a 首轮被模型在 reasoning 里
写出又明确放弃的正确解读路径。1/50 的样本不足以支撑任何结论，
但它说明**正确路径在本地工具下可以被重新进入**，这是 Experiment 3 的直接动机。

### 下一步（Experiment 3）的范围

按 `EXPERIMENT_PLAN.md` 阶段 3：最小 Verification Card，只含
「当前未解决的需求 + 有希望的已有文档 / 候选 D#」两项；禁令清单
（claim graph / 置信度 / 计划 / 打分 / verify 状态 / 证据摘要 / gold）逐条执行；
Card 只能由 checkpoint prefix 信息推出，第一版手搓但必须标注 `diagnostic_oracle`；
arm S0（v3b，无 card）vs S1（同 prefix + card），tools 完全相同。

**同时保留**：若 Experiment 3 也给出弱信号，阶段 2 的 orthogonal search
（命中已发现文档 → `already_discovered`，无新 W#、无新原文）是唯一还没被排除的
H1 检验形态，必须补做——理由见 SCORING.md §5 第 2 点。
