# 逐题分析：P0/P1 笔记对照

同题同 O1，仅 system 提示词不同（P1 追加保真 addendum）。每题先列交付状态，再按三轴分析。原文窗口见 `review_retry2/cards.json`。

## 517 — 无明确核心（no_clear_core=true）

O1 全为弱相关材料：Huang Yi 生平、生肖"羊"词义辨析、亚洲演员好莱坞经历。无窗口涉及警察角色、Iracema 导演或 Kinsey 导演条件。

- **P0**：invalid（2 条）。引文跨段合并，把两段并作一段，子串校验失败。
  - note 0：生肖术语辨析，来源支持 yes，相关性 unknown（通用术语，非身份关系）。
  - note 1：Zhao Wei 2005 三项最佳女主角，来源支持 yes，**相关性 no**——候选人生平，与原题条件无连接。
- **P1**：empty（0 条）。无据扩展 no，但放弃了唯一有支持的生肖术语关系。**空 notes 不能自动判成功**。
- 覆盖轴不适用（复核表声明无明确核心）。两组都未建立候选身份，符合声明。

**结论**：两组都未制造错误候选。P1 的空集不应计入收益。

## 546 — 四场赛程链不可见

O1 给出 O'Sullivan 破百里程碑、Williams 600+ 破百与三次满分、Selby 2023 决赛 147、2025 年 4 月事件。原题的 decider→4-3→4-0→再败链在任何窗口都不存在。

- **P0**：ok（3 条）。
  - O'Sullivan 第 1200 个破百（2023 世锦赛对 Vafaei），逐字忠实。
  - Williams 600+ 破百与三次满分；并保留 1992–93 转职业——**与原题"1995 至 2006"不一致，P0 未为此弯折来源**。
  - BBC 比分列表，但**丢了赛事与年份**，比分悬浮无时间范围。
  - 漏掉 Selby 2023 决赛 147 与 Williams 2025 最年长决赛选手（后者晚于截止日，属相关性而非伪造）。
- **P1**：invalid（3 条）。补上了 Selby 2023 决赛 147（P0 漏的核心）。**失败仅在 Williams 引文**：原文 `£8\xa0million` 的不可分空格被写成普通空格，子串校验失败。语义内容本身正确。
- 覆盖：P0 3/5、P1 4/5。

**结论**：两组都正确保留了 1992/93 与原题条件的张力，这是正向信号。P1 覆盖更好，但被机械失败挡在注入之外。

## 776 — 本轮最关键的对照

O1 给出 Jenness 1915 精确旅行、Wikipedia 小节标题 `Early life (1886–1910)`、Benedict 生平。

- **P0**：ok（3 条）。
  - note 0 **无据扩展**：statement 写 "Diamond Jenness **was born in 1886** and his early life period is noted as spanning until 1910"，而引文只有小节标题 `Early life (1886–1910)`。**标题区间不构成出生日期陈述**——这正是上一轮点名的失败，本轮原样复现。
  - note 1：1915 年 4 月 13 日至 11 月 8 日维多利亚岛南部旅行，逐字忠实，是本题唯一精确对应原题的关系。
  - note 2：Benedict 1940 年著作，来源支持 yes 但**相关性 no**（第三方人物）。
- **P1**：invalid（3 条）。
  - note 0 **改对**："A biographical section **labeled** 'Early life (1886–1910)' introduces Diamond Jenness as the second youngest son…"。标题保持标题，未声称出生日期。这正是 addendum 明文针对的机制。
  - note 1：1915 旅行，与 P0 同样忠实。
  - note 2：Benedict + Anne Singleton 笔名，两者都在窗口内，但引文用 `...` 跳过中间一句，子串校验失败。仍是第三方偏题。
  - 漏掉 Beuchat 与"加拿大人类学先驱"两条核心。
- 覆盖：P0 2/5、P1 3/5。

**结论**：**同一输入、同一目标关系，只有提示词不同，P1 把上一轮的扩展改对了。** 这是本轮可信度最高的单点证据。代价是整组机械无效。

## 519 — 上一轮的层级扩展未复现

O1 只有 Cyprus Mail 一篇相关：文章叙述 BBC 相遇，茶会引述明确归于 Kizilyurek 所著《Glafcos Clerides: The Path of a Country》。

- **P0**：ok（3 条）。
  - BBC 相遇按**文章叙述**归属，"immediately after World War II" 保留未补年。
  - 茶会："an event described in a book written by Niyazi Kizilyurek"——比"书中引述"略松，处于边界，标 unknown 而非干净通过。
  - Clerides 身份、RAF 职务、60 年婚姻，均忠实。
  - 漏掉女儿 Katy。
- **P1**：invalid（3 条）。
  - BBC 相遇同样按文章归属。
  - 茶会："Clerides recounted … in a book"，与原文 "quoted as saying in a book" 对应，归属正确。
  - 补上女儿 Katy。
  - **失败仅在引号字符**：原文用 `"`，模型写 `'`，子串校验失败。
- 覆盖：P0 3/5、P1 4/5。

**结论**：**两组都未把 BBC 相遇写成书中内容**——上一轮的核心失败本轮未复现。按方案第 9 节，这是小样本不确定，不能算 P0 改善，也不能算 P1 收益。

## 191 — 跨窗身份混淆未发生

O1 给出 Tim Ellis（魔术师）与 Justin Hamilton（2025 主持、TV producer）两个不同人物。

- **P0**：invalid（3 条）。
  - note 0：**Hamilton** 的主持与 TV producer 身份，归属正确——不是并入 Ellis，而是"另选了一个人"。
  - note 1：Ellis 1992 年购入 Bernard's Magic Shop，逐字忠实。
  - note 2：Pinder Prize。**双重问题**：`source_ref` 截短 4 个字符（`w_eb79e233ddb35ebb` 而非 `w_eb79e233ddb35ebb6cd02553`），指向不存在的窗口；内容也与本题无关。
- **P1**：ok（3 条）。三条全给 Ellis：performer/author/lecturer、1992 购店、Australian Magic Monthly 100 期，全部逐字忠实。**完全不提 Hamilton**，通过"不选"规避跨窗混淆。
- 覆盖：两组 3/5。P0 的覆盖含 Hamilton 那条；P1 全在 Ellis。P1 的 Melbourne 出生与魔术套装起源两组都漏。

**结论**：上一轮的失败是"把 Hamilton 的 TV producer 身份并入 Ellis"。本轮两组都没犯——P0 用正确归属另一人，P1 用不选。两条都是可接受路径。

## 71 — 单一来源升级是唯一差异

O1 给出 Talbot 酒店页（Ballast Bank 人造岛、压舱物、1905）与 Wikipedia 页（19 世纪末煤场）。

- **P0**：ok（3 条）。四条核心全部覆盖，含跨窗张力。
  - note 0：人造岛 + 压舱物 + 稳定无货船 + 酒店酒吧命名，忠实。
  - note 1："**One source asserts** that … 1905"——正确把建造年限定为单一酒店来源，未当作共识。
  - note 2 **来源层级升级**："**Historical records indicate** that by the late 19th century…"——把单一 Wikipedia 条目升级为多份历史记载。事实本身逐字忠实，只有来源称谓被抬高。
- **P1**：ok（3 条）。同样四条核心全覆盖。
  - 人造岛与压舱物忠实；"erected **around** 1905" 把原文确定的 "constructed in 1905" 弱化——是**松化**而非升级，标 unknown。
  - 煤场关系直接陈述，**未做来源层级升级**。
  - note 1 选了 Ice House Hotel（1859 冰库，另一建筑），引文与归属正确，纯选材错位。
- 覆盖：两组 4/4。

**结论**：P0 的扩展是"来源层级提升"，P1 消除了它。P1 另有选材错位与一处弱化，均非扩展。

## 费用与失败汇总

| 题号 | P0 状态 | P0 in/out/total token | P0 秒 | P1 状态 | P1 in/out/total token | P1 秒 |
|---|---|---|---|---|---|---|
| 517 | invalid | 3644/2607/6251 | 30.8 | empty | 3833/1350/5183 | 19.4 |
| 546 | ok | 3724/3791/7515 | 46.5 | invalid | 3913/3878/7791 | 43.7 |
| 776 | ok | 3715/3732/7447 | 42.0 | invalid | 3904/4624/8528 | 51.7 |
| 519 | ok | 3755/3814/7569 | 43.1 | invalid | 3944/3559/7503 | 43.5 |
| 191 | invalid | 3702/2657/6359 | 31.5 | ok | 3891/2631/6522 | 31.2 |
| 71 | ok | 3481/3097/6578 | 35.0 | ok | 3670/4603/8273 | 57.6 |
| **合计** | 4ok/2inv | 22021/19698/41719 | 228.9 | 2ok/3inv/1empty | 23155/20645/43800 | 247.1 |

- provider 报告 reasoning 合计 35,422，含于 40,343 输出 token 内，不重复相加。
- P1 输入高 1,134 token（+5.1%），与追加段落长度相符，不宣称等成本。
- 货币成本未知：无账单、未核实单价；本地检索与散列的 I/O 未计量。
- 三批历史失败完整保留：`model/` 12 次 AuthenticationError、`model_retry_071500Z` 12 次 AuthenticationError，均 `cost_accounting_complete=false`、未知用量 12，未从任何分母删除。
