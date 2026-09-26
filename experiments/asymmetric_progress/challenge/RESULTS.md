# Challenge Stress（单独分母）

9 个历史 checkpoint，8 unresolved + 1 resolved；每 arm 各 18 次。全部请求成功解析。它们不是 fresh 主集，不能补主集覆盖或推翻 gate。

| 指标 | L0 | L1 | Audit |
|---|---:|---:|---:|
| False closure | 2/16 | 0/16 | 0/16 |
| Correct closure | 0/2 | 1/2 | 0/2 |
| Valid blocker presence | 13/16 | 15/16 | 16/16 |
| Blocker precision | 24/39 | 31/42 | 16/18 |

## 强制 P17 / P19

| 原样本 | L0 ×2 | L1 ×2 | Audit ×2 | L / LL / LA |
|---|---|---|---|---|
| P17 → S01 | 都未闭合 | 都未闭合 | 都拒绝；均指出 total seasons 缺口 | 都继续 |
| P19 → S02 | 都错误闭合 | 都未闭合；指出 Edgar roommate 缺口 | 都拒绝；均指出同一 role 缺口 | 都继续 |

P19 重现了 historical strong-candidate false closure，L1 和 Audit 各自都修复 2/2。P17 的历史 2/2 错误在当前 L0 未重现，不能将当前正确拒绝归功于新 Audit。两次采样的所谓“稳定”仅指这两个实际输出，不是模型必然行为。

Audit 对日期/来源归属（S07）、zodiac（S08）、数量（S09）、动画角色（S05/S06）都产生有效拒绝。S04 的真实 material Claim conflict 保留在原样本中：Audit 分别选择 character-set 与 runtime 缺口；这验证至少一个反例的能力，不证明它识别了所有冲突。L1 一次明确指出 episode-count conflict。

S03 是历史 resolved 游戏控制。Audit 两次过度拒绝：一次要求额外公司命名/成立时点关系，并把 C4 中的实体称呼误读成成立时的法定名称；另一次要求解决 1992/1993 年差异，尽管两者均符合原问题的 early-1990s 范围。L0 也两次过度拒绝；L1 一次正确、一次拒绝。标签和 materiality 沿用历史冻结定义，未根据本轮输出改写。

## STOP policy

冻结 primary replica 下，L 为 false stop 0/8、correct stop 1/1；LL 和 LA 均为 0/8、0/1。唯一触发二次调用的是游戏 resolved 控制，因此二者都损失了一个正确停止。L1-primary 没有错误停止可供修复，不能据此声称 Audit 比同 prompt 第二次采样更有效。

独立 raw、每个 replica 的判断、review reason、策略配对与成本均保存在 challenge_outputs/events、metrics.json 与 analysis/diagnostics.json。
