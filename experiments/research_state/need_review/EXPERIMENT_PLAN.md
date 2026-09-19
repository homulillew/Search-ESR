# E0 实验计划（e0_audit_v1）

本次依据809dfeb真实结果，保持“一次审查 → 一次原 Actor 决策”的研究范围，不增加持久 Research State、触发器或停止器。源检查点和原审查提示词不变；详细历史设计保存在 [0193fc0 原计划](https://github.com/homulillew/Search-ESR/blob/0193fc072c31554284c9459bac62f436e9f7ba64/experiments/research_state/need_review/EXPERIMENT_PLAN.md)。该旧版本命令不能替代本版冻结计划要求。

## 下一轮优先：C0/C1来源合同配对

使用 `--comparison source_contract_pair --memo-mode legacy_text`，程序在每题每重复中交错运行C0 baseline和C1 source_grounded_v1，各自一次Reviewer再一次Actor。3题×2重复×2合同=12分支、24次逻辑调用，不额外重跑A/B。唯一语义输入差异是C Reviewer system提示词中的来源归属规则；Actor原参数/备忘/schema/512输出上限不变。实际审查输出和后续Actor输入因干预而变化，这是观察对象。

计划固定每样本的review_contract和顺序；summary按by_contract报告，private_key保留条件。禁止同时启用indexed交接。先看来源归属是否正确，再看需求与动作，所有无效审查回退仍归入原条件分母。效果不能由跨批次旧C对比新C单独得出，故保留同批新采样C0。

新增人工分轴：review_source_attribution_correct、tool_action_direction_acceptable、assistant_assertions_supported、final_answer_supported，保留旧action_acceptable为完整响应指标。没有独立人类复核时明确写代理辅助标签，不称金标。

## 保留的ABC基线模式

H0：在同一已见材料下，检查未证实前提并提出一个会改变判断的信息需求，比直接继续或一般进度审查，更容易产生有价值的下一动作。

| Arm | 干预 | 逻辑请求 |
|---|---|---:|
| A | 原捕获请求原样继续一次 | 1 |
| B | 普通自由文本审查，再继续一次 | 2 |
| C | 四字段 Need Review，再继续一次 | 2 |

3 个检查点 × 3 组 × 2 次 = 18 个分支、30 次逻辑模型调用。调度 seed20260919 只固定调度，不等于远端采样 seed。审查上限512 tokens，Actor 保留捕获预算；模型覆盖必须同时作用于 Reviewer 与 Actor，且写入冻结计划。

## 首次调用前冻结

按照 [CODEX_TASK.md](CODEX_TASK.md) 保存 plan 文件，固定源清单/前缀、模型、API 基础地址、额度、重试数、提示词、交接模式和实现哈希；execute 必须逐项匹配。不能看到某题结果后改提示词、换模型或增加该组重试。错误分支不删除，实际调用、用量、耗时与未知成本都保留。

默认legacy_text保留既有Actor备忘；indexed_json_v1为独立交接实验候选，可向B/C Actor交付同一已见引用索引。没有标准答案、未来事件、未见全文或人工改好的需求。审查仍然可能错，Actor 可以不采纳。legacy_text 只用于独立交接消融，不与 indexed 结果混合。

## 审查合同

```json
{
  "current_assumption": null,
  "next_need": "一个尚未解决、会影响原题或中间关系判断的问题",
  "decision_effect": "可观察记录如何支持或修订判断",
  "basis_refs": ["question"]
}
```

只允许上述四字段。前三个为非空字符串或 null；next_need 与 decision_effect 同时为 null 或同时为非空字符串。basis_refs 只能引用已见索引且不可重复。代码验证格式/成员资格，不验证语义真值，允许全 null；不能把全 null 直接当作提交许可。Reviewer 不写 Query、不执行工具、不选终答。未搜到不是反证，候选未被排除与当前路线值得继续是两回事。

## 评价分层

先检查实际请求/响应/备忘与冻结数据一致；完整性异常属于 harness/data 问题，不能算模型语义失败。原始分母始终保留，再分别报告 API、节点格式、协议、语义与中断状态。

只根据前缀预先列出合理动作，再评价：假设是否真的未建立、需求是否未解决且决定性、是否容纳反证/上游修订、引用实际支持什么、Actor 是否语义上响应合理需求、是否保留原题限定、是否破坏517正常纠偏。新 Query 词面不同不代表新策略；执行了合理需求也不等于已获得有用证据，E0 尚未执行工具。

C 相对 A 的变化包含额外推理和备忘；C 相对 B 只检验整个定向审查包，不单独识别 JSON、gap 字段或结构化状态的效应。无效审查回退按原 arm 计入主分析；可另列有效子集但不能删失败后宣称收益。两个重复不是两道独立题。

## 一次只改一处

审查误读 → 只改读取合同；确认式 gap → 只改需求定义；合理需求未影响 Actor → 固定证据做需求替换；B/C相近 → 优先简单B；动作合理 → 才进入真实工具 E1；后续忘记目的 → 再引入 last_attempt。停止单独选疑似充分的新检查点做作答探针。本版没有自动执行这些后续实验。

当前检查点全为历史 v000，517只作行为回归对照，不是完美答案金标。当前 Search/Open 下旧症状消失就记为解决；不能把旧工具缺陷重建进新协议制造效果。详细归因与修复边界见 [审计报告](AUDIT_20260920.md)。
