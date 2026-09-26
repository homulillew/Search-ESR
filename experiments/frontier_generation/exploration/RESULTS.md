# 唯一有界探索 A：较窄的 Need

9个失败条件筛选的checkpoint，跨5qid；18次新调用。A0为原提示的新对照，A1只追加 `Choose the smallest currently useful unresolved research question.`。没有改视图、模型、合同、Writer或工具。不是新cohort，不能覆盖F1。

| 指标 | A0原提示 | A1追加一句 |
|---|---:|---:|
| 有效决策 |0/9|3/9|
| Need过宽 |6/9|3/9|
| 关键前提错误 |4/9|5/9|
| 过早STOP |0/9|0/9|
| 传输/结构/长度失败 |0/9|0/9|

**有局部收窄信号，但未满足预先要求的“关键错误不增加”。** F02转为检验特定2023文章，F13转为下一段赛程，F18转为特定2020人物文章，三例有效。F20则从过宽的整场比赛资格问题变为带未验证95分钟事件前提的具体比赛提问；F21增加了未建立的socialite限定。更具体不等于更可靠。F22两组均引入新的、未获prefix支持的节目候选。

这个结果不解决主要STOP失败，也不能用三个局部改善推翻F1。唯一探索额度已使用；不继续prompt sweep，不进入F2–F4。

## 调用成本与缓存

| 指标 | A0 | A1 |
|---|---:|---:|
| 输入tokens |40148|40220|
| output tokens（含reasoning） |121161|139501|
| reasoning-token proxy |120475|138999|
| 平均elapsed秒 |64.04|75.37|
| 中位elapsed秒 |38.92|55.84|
| cache hit / input |38400/40148（95.65%）|1792/40220（4.46%）|

探索总cache token命中率40192/80368=50.01%。A0与先前请求的提示前缀相同，A1改变了system提示，缓存暖化明显不对称；这是对缓存差异的合理解释，不能把延迟差异全部归因于推理难度。两组都保留实际用量，没有额外暖缓存调用。

单审核员masked review，condition ID隐藏，但输入视图可识别；使用相同冻结coverage/rubric。完整paired结果、每个Need与reason见 `reviewed_outputs.json` / `summary.json`。失败条件选择、单次replicate及小样本限制泛化。
