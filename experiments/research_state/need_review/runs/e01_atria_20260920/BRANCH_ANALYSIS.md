# C0/C1 逐分支分析

单一 Codex 辅助标注；先前缀、再 Reviewer、再 Actor，最后核对配对。已知历史输出及稳定卡片顺序，不是独立人工金标或盲评。全部 12 分支保留，未知/不适用分别标记。

主指标 action_acceptable 保留完整响应评价；检索方向是辅助轴。action_responds_to_need=yes 仅表示所提查询在语义上回应需求主题，不证明正确使用了审查的纠偏理由、需求合理或检索有收益。未执行工具。

## qid_517_s21 / r1 / C0 (card_0008)

[完整原始记录](branches/qid_517_s21__C__r1__baseline/result.json) · [事件日志](branches/qid_517_s21__C__r1__baseline/events.jsonl)

审查状态 `node_invalid`；memo_injected=False；Actor=tool_calls；reported tokens=36,387；调用耗时合计=24.904s。

**Reviewer 来源归属 → 需求**

没有输出可用Reviewer正文/四字段JSON，来源归属与需求没有可评价对象；节点失败保留全分母，不从reasoning内容补造审查，不记为语义错误或需求传递失败。

```json
null
```

**Actor 动作 → 尚未知内容**

用barracks hospital短语查actor mother，未固定1975、Idris或把警察解释为security。与另一独立分支查询相同不算同一历史内重复；两分支互不可见。

实际提出的工具（未执行）：
```json
[
  {
    "arguments": "{\"query\": \"\\\"barrack's hospital\\\" actor mother\"}",
    "name": "search"
  }
]
```

证据界限：仍无同一演员的父母、出生/生肖、2005警察角色与2013影片完整关系链。

| 评价轴 | 标签 |
|---|---|
| `review_source_attribution_correct` | not_applicable |
| `tool_action_direction_acceptable` | yes |
| `assistant_assertions_supported` | not_applicable |
| `final_answer_supported` | not_applicable |
| `assumption_grounded` | not_applicable |
| `need_unresolved` | not_applicable |
| `need_decision_relevant` | not_applicable |
| `need_already_answered` | not_applicable |
| `decision_effect_balanced` | not_applicable |
| `action_responds_to_need` | not_applicable |
| `original_constraint_preserved` | yes |
| `action_acceptable` | yes |
| `regression` | not_applicable |
| `new_errors` | no |
| `answer_vs_abstention` | no_final_text |

配对比较：同期C0对照不对自身做退化判断。

依据索引：。精确 message_index/path 见同卡 reference_index。

## qid_517_s21 / r1 / C1 (card_0003)

[完整原始记录](branches/qid_517_s21__C__r1__source_grounded_v1/result.json) · [事件日志](branches/qid_517_s21__C__r1__source_grounded_v1/events.jsonl)

审查状态 `node_invalid`；memo_injected=False；Actor=tool_calls；reported tokens=37,722；调用耗时合计=153.866s。

**Reviewer 来源归属 → 需求**

没有输出可用Reviewer正文/四字段JSON，来源归属与需求没有可评价对象；节点失败保留全分母，不从reasoning内容补造审查，不记为语义错误或需求传递失败。

```json
null
```

**Actor 动作 → 尚未知内容**

查barracks hospital/actor/mother原题线索，取消历史1975硬过滤；精准措辞可能漏召回，但此时是合理新入口，不能把尚未运行的召回结果当成成功。

实际提出的工具（未执行）：
```json
[
  {
    "arguments": "{\"query\": \"\\\"barrack's hospital\\\" actor mother\"}",
    "name": "search"
  }
]
```

证据界限：仍无同一演员的父母、出生/生肖、2005警察角色与2013影片完整关系链。

| 评价轴 | 标签 |
|---|---|
| `review_source_attribution_correct` | not_applicable |
| `tool_action_direction_acceptable` | yes |
| `assistant_assertions_supported` | not_applicable |
| `final_answer_supported` | not_applicable |
| `assumption_grounded` | not_applicable |
| `need_unresolved` | not_applicable |
| `need_decision_relevant` | not_applicable |
| `need_already_answered` | not_applicable |
| `decision_effect_balanced` | not_applicable |
| `action_responds_to_need` | not_applicable |
| `original_constraint_preserved` | yes |
| `action_acceptable` | yes |
| `regression` | no |
| `new_errors` | no |
| `answer_vs_abstention` | no_final_text |

配对比较：按本批完整响应标签未比配对C0更差；但双方都回退，Actor输入相同，差异不能归因来源合同。

依据索引：。精确 message_index/path 见同卡 reference_index。

## qid_517_s21 / r2 / C0 (card_0001)

[完整原始记录](branches/qid_517_s21__C__r2__baseline/result.json) · [事件日志](branches/qid_517_s21__C__r2__baseline/events.jsonl)

审查状态 `node_invalid`；memo_injected=False；Actor=tool_calls；reported tokens=35,573；调用耗时合计=23.579s。

**Reviewer 来源归属 → 需求**

没有输出可用Reviewer正文/四字段JSON，来源归属与需求没有可评价对象；节点失败保留全分母，不从reasoning内容补造审查，不记为语义错误或需求传递失败。

```json
null
```

**Actor 动作 → 尚未知内容**

针对母亲barracks hospital原题稀有短语寻找演员，不再把1975或Idris当硬过滤。比历史多条件猜测查询更集中，方向可接受；没有执行Search，家庭链仍未建立。

实际提出的工具（未执行）：
```json
[
  {
    "arguments": "{\"query\": \"\\\"mother worked at the barracks hospital\\\" actor\"}",
    "name": "search"
  }
]
```

证据界限：仍无同一演员的父母、出生/生肖、2005警察角色与2013影片完整关系链。

| 评价轴 | 标签 |
|---|---|
| `review_source_attribution_correct` | not_applicable |
| `tool_action_direction_acceptable` | yes |
| `assistant_assertions_supported` | not_applicable |
| `final_answer_supported` | not_applicable |
| `assumption_grounded` | not_applicable |
| `need_unresolved` | not_applicable |
| `need_decision_relevant` | not_applicable |
| `need_already_answered` | not_applicable |
| `decision_effect_balanced` | not_applicable |
| `action_responds_to_need` | not_applicable |
| `original_constraint_preserved` | yes |
| `action_acceptable` | yes |
| `regression` | not_applicable |
| `new_errors` | no |
| `answer_vs_abstention` | no_final_text |

配对比较：同期C0对照不对自身做退化判断。

依据索引：。精确 message_index/path 见同卡 reference_index。

## qid_517_s21 / r2 / C1 (card_0002)

[完整原始记录](branches/qid_517_s21__C__r2__source_grounded_v1/result.json) · [事件日志](branches/qid_517_s21__C__r2__source_grounded_v1/events.jsonl)

审查状态 `node_invalid`；memo_injected=False；Actor=tool_calls；reported tokens=36,577；调用耗时合计=20.919s。

**Reviewer 来源归属 → 需求**

没有输出可用Reviewer正文/四字段JSON，来源归属与需求没有可评价对象；节点失败保留全分母，不从reasoning内容补造审查，不记为语义错误或需求传递失败。

```json
null
```

**Actor 动作 → 尚未知内容**

查The Constant Gardener的policeman演员，是核查角色关系的入口，不预先选Idris、也不放宽policeman。电影绑定仍是待检验搜索假设，不能作为已确认事实或最终答案。

实际提出的工具（未执行）：
```json
[
  {
    "arguments": "{\"query\": \"The Constant Gardener 2005 policeman actor\"}",
    "name": "search"
  }
]
```

证据界限：仍无同一演员的父母、出生/生肖、2005警察角色与2013影片完整关系链。

| 评价轴 | 标签 |
|---|---|
| `review_source_attribution_correct` | not_applicable |
| `tool_action_direction_acceptable` | yes |
| `assistant_assertions_supported` | not_applicable |
| `final_answer_supported` | not_applicable |
| `assumption_grounded` | not_applicable |
| `need_unresolved` | not_applicable |
| `need_decision_relevant` | not_applicable |
| `need_already_answered` | not_applicable |
| `decision_effect_balanced` | not_applicable |
| `action_responds_to_need` | not_applicable |
| `original_constraint_preserved` | yes |
| `action_acceptable` | yes |
| `regression` | no |
| `new_errors` | no |
| `answer_vs_abstention` | no_final_text |

配对比较：按本批完整响应标签未比配对C0更差；但双方都回退，Actor输入相同，差异不能归因来源合同。

依据索引：。精确 message_index/path 见同卡 reference_index。

## qid_546_s29 / r1 / C0 (card_0009)

[完整原始记录](branches/qid_546_s29__C__r1__baseline/result.json) · [事件日志](branches/qid_546_s29__C__r1__baseline/events.jsonl)

审查状态 `node_invalid`；memo_injected=False；Actor=tool_calls；reported tokens=49,904；调用耗时合计=17.436s。

**Reviewer 来源归属 → 需求**

没有输出可用Reviewer正文/四字段JSON，来源归属与需求没有可评价对象；节点失败保留全分母，不从reasoning内容补造审查，不记为语义错误或需求传递失败。

```json
null
```

**Actor 动作 → 尚未知内容**

仍在Players绑定下并列Selby/Trump/Bingham/Murphy，bracket results未纠正未经证实赛事；与旧多轮该赛事结果路线近重复。没有伴随正文事实，不能标为新事实幻觉。

实际提出的工具（未执行）：
```json
[
  {
    "arguments": "{\"query\": \"2023 Players Championship snooker bracket results Mark Selby Judd Trump Stuart Bingham Shaun Murphy\"}",
    "name": "search"
  }
]
```

证据界限：仍无与题目一致的完整赛事/对手/比分及as-of统计链。

| 评价轴 | 标签 |
|---|---|
| `review_source_attribution_correct` | not_applicable |
| `tool_action_direction_acceptable` | no |
| `assistant_assertions_supported` | not_applicable |
| `final_answer_supported` | not_applicable |
| `assumption_grounded` | not_applicable |
| `need_unresolved` | not_applicable |
| `need_decision_relevant` | not_applicable |
| `need_already_answered` | not_applicable |
| `decision_effect_balanced` | not_applicable |
| `action_responds_to_need` | not_applicable |
| `original_constraint_preserved` | yes |
| `action_acceptable` | no |
| `regression` | not_applicable |
| `new_errors` | no |
| `answer_vs_abstention` | no_final_text |

配对比较：同期C0对照不对自身做退化判断。

依据索引：。精确 message_index/path 见同卡 reference_index。

## qid_546_s29 / r1 / C1 (card_0004)

[完整原始记录](branches/qid_546_s29__C__r1__source_grounded_v1/result.json) · [事件日志](branches/qid_546_s29__C__r1__source_grounded_v1/events.jsonl)

审查状态 `node_invalid`；memo_injected=False；Actor=tool_calls；reported tokens=49,968；调用耗时合计=63.052s。

**Reviewer 来源归属 → 需求**

没有输出可用Reviewer正文/四字段JSON，来源归属与需求没有可评价对象；节点失败保留全分母，不从reasoning内容补造审查，不记为语义错误或需求传递失败。

```json
null
```

**Actor 动作 → 尚未知内容**

仍在Players事件绑定下并列此前Selby/Trump/Bingham，draw results与多次旧结果查询近重复，未说明可区分的新关系。正文只有搜索意图，没有造比赛事实；未推进不等于命题错误。

实际提出的工具（未执行）：
```json
[
  {
    "arguments": "{\"query\": \"2023 Players Championship snooker draw results Judd Trump Mark Selby Stuart Bingham\"}",
    "name": "search"
  }
]
```

证据界限：仍无与题目一致的完整赛事/对手/比分及as-of统计链。

| 评价轴 | 标签 |
|---|---|
| `review_source_attribution_correct` | not_applicable |
| `tool_action_direction_acceptable` | no |
| `assistant_assertions_supported` | yes |
| `final_answer_supported` | not_applicable |
| `assumption_grounded` | not_applicable |
| `need_unresolved` | not_applicable |
| `need_decision_relevant` | not_applicable |
| `need_already_answered` | not_applicable |
| `decision_effect_balanced` | not_applicable |
| `action_responds_to_need` | not_applicable |
| `original_constraint_preserved` | yes |
| `action_acceptable` | no |
| `regression` | no |
| `new_errors` | no |
| `answer_vs_abstention` | no_final_text |

配对比较：按本批完整响应标签未比配对C0更差；但双方都回退，Actor输入相同，差异不能归因来源合同。

依据索引：。精确 message_index/path 见同卡 reference_index。

## qid_546_s29 / r2 / C0 (card_0012)

[完整原始记录](branches/qid_546_s29__C__r2__baseline/result.json) · [事件日志](branches/qid_546_s29__C__r2__baseline/events.jsonl)

审查状态 `node_invalid`；memo_injected=False；Actor=tool_calls；reported tokens=49,283；调用耗时合计=23.184s。

**Reviewer 来源归属 → 需求**

没有输出可用Reviewer正文/四字段JSON，来源归属与需求没有可评价对象；节点失败保留全分母，不从reasoning内容补造审查，不记为语义错误或需求传递失败。

```json
null
```

**Actor 动作 → 尚未知内容**

改查Neil Robertson但保留Players/4-3/4-0绑定，候选变化本身不足以修复上游赛事前提。仅探索姓名不算新错误事实，仍不满足本批合理方向标准。

实际提出的工具（未执行）：
```json
[
  {
    "arguments": "{\"query\": \"\\\"Neil Robertson\\\" 2023 Players Championship snooker results 4-3 4-0\"}",
    "name": "search"
  }
]
```

证据界限：仍无与题目一致的完整赛事/对手/比分及as-of统计链。

| 评价轴 | 标签 |
|---|---|
| `review_source_attribution_correct` | not_applicable |
| `tool_action_direction_acceptable` | no |
| `assistant_assertions_supported` | not_applicable |
| `final_answer_supported` | not_applicable |
| `assumption_grounded` | not_applicable |
| `need_unresolved` | not_applicable |
| `need_decision_relevant` | not_applicable |
| `need_already_answered` | not_applicable |
| `decision_effect_balanced` | not_applicable |
| `action_responds_to_need` | not_applicable |
| `original_constraint_preserved` | yes |
| `action_acceptable` | no |
| `regression` | not_applicable |
| `new_errors` | no |
| `answer_vs_abstention` | no_final_text |

配对比较：同期C0对照不对自身做退化判断。

依据索引：。精确 message_index/path 见同卡 reference_index。

## qid_546_s29 / r2 / C1 (card_0005)

[完整原始记录](branches/qid_546_s29__C__r2__source_grounded_v1/result.json) · [事件日志](branches/qid_546_s29__C__r2__source_grounded_v1/events.jsonl)

审查状态 `node_invalid`；memo_injected=False；Actor=tool_calls；reported tokens=49,330；调用耗时合计=11.054s。

**Reviewer 来源归属 → 需求**

没有输出可用Reviewer正文/四字段JSON，来源归属与需求没有可评价对象；节点失败保留全分母，不从reasoning内容补造审查，不记为语义错误或需求传递失败。

```json
null
```

**Actor 动作 → 尚未知内容**

首次提出get_document读取已见55516，从offset0扩到12000字符；该人物页面现只展示1600字符，继续核查2023关系是合理取证尝试。尚不知道前12000字符是否含相关赛事，不能假称已获得新事实。

实际提出的工具（未执行）：
```json
[
  {
    "arguments": "{\"docid\": \"55516\", \"max_chars\": 12000, \"offset\": 0}",
    "name": "get_document"
  }
]
```

证据界限：仍无与题目一致的完整赛事/对手/比分及as-of统计链。

| 评价轴 | 标签 |
|---|---|
| `review_source_attribution_correct` | not_applicable |
| `tool_action_direction_acceptable` | yes |
| `assistant_assertions_supported` | yes |
| `final_answer_supported` | not_applicable |
| `assumption_grounded` | not_applicable |
| `need_unresolved` | not_applicable |
| `need_decision_relevant` | not_applicable |
| `need_already_answered` | not_applicable |
| `decision_effect_balanced` | not_applicable |
| `action_responds_to_need` | not_applicable |
| `original_constraint_preserved` | yes |
| `action_acceptable` | yes |
| `regression` | no |
| `new_errors` | no |
| `answer_vs_abstention` | no_final_text |

配对比较：按本批完整响应标签未比配对C0更差；但双方都回退，Actor输入相同，差异不能归因来源合同。

依据索引：。精确 message_index/path 见同卡 reference_index。

## qid_776_s53 / r1 / C0 (card_0007)

[完整原始记录](branches/qid_776_s53__C__r1__baseline/result.json) · [事件日志](branches/qid_776_s53__C__r1__baseline/events.jsonl)

审查状态 `node_invalid`；memo_injected=False；Actor=tool_calls；reported tokens=71,818；调用耗时合计=87.788s。

**Reviewer 来源归属 → 需求**

没有输出可用Reviewer正文/四字段JSON，来源归属与需求没有可评价对象；节点失败保留全分母，不从reasoning内容补造审查，不记为语义错误或需求传递失败。

```json
null
```

**Actor 动作 → 尚未知内容**

出生1886和3children都来自原题，但继续用未证实anthropologist过滤；历史已试人物家庭组合与职业路线，此查询没有撤回限制。无新正文断言，评价的是方向/约束而非姓名正确性。

实际提出的工具（未执行）：
```json
[
  {
    "arguments": "{\"query\": \"\\\"born in 1886\\\" \\\"three children\\\" anthropologist\"}",
    "name": "search"
  }
]
```

证据界限：仍无人物—语言误用事件—作者—1940报告官方题名的完整关系链。

| 评价轴 | 标签 |
|---|---|
| `review_source_attribution_correct` | not_applicable |
| `tool_action_direction_acceptable` | no |
| `assistant_assertions_supported` | not_applicable |
| `final_answer_supported` | not_applicable |
| `assumption_grounded` | not_applicable |
| `need_unresolved` | not_applicable |
| `need_decision_relevant` | not_applicable |
| `need_already_answered` | not_applicable |
| `decision_effect_balanced` | not_applicable |
| `action_responds_to_need` | not_applicable |
| `original_constraint_preserved` | no |
| `action_acceptable` | no |
| `regression` | not_applicable |
| `new_errors` | no |
| `answer_vs_abstention` | no_final_text |

配对比较：同期C0对照不对自身做退化判断。

依据索引：。精确 message_index/path 见同卡 reference_index。

## qid_776_s53 / r1 / C1 (card_0006)

[完整原始记录](branches/qid_776_s53__C__r1__source_grounded_v1/result.json) · [事件日志](branches/qid_776_s53__C__r1__source_grounded_v1/events.jsonl)

审查状态 `node_invalid`；memo_injected=False；Actor=tool_calls；reported tokens=72,183；调用耗时合计=54.938s。

**Reviewer 来源归属 → 需求**

没有输出可用Reviewer正文/四字段JSON，来源归属与需求没有可评价对象；节点失败保留全分母，不从reasoning内容补造审查，不记为语义错误或需求传递失败。

```json
null
```

**Actor 动作 → 尚未知内容**

转向1940年JAF报告入口；期刊仍只是探索候选，查询未断言已经锁定。较既往泛journal/1888组合更具体，是允许的报告侧反向取证；官方题名仍未知。

实际提出的工具（未执行）：
```json
[
  {
    "arguments": "{\"query\": \"\\\"Journal of American Folklore\\\" 1940 report discoveries\"}",
    "name": "search"
  }
]
```

证据界限：仍无人物—语言误用事件—作者—1940报告官方题名的完整关系链。

| 评价轴 | 标签 |
|---|---|
| `review_source_attribution_correct` | not_applicable |
| `tool_action_direction_acceptable` | yes |
| `assistant_assertions_supported` | not_applicable |
| `final_answer_supported` | not_applicable |
| `assumption_grounded` | not_applicable |
| `need_unresolved` | not_applicable |
| `need_decision_relevant` | not_applicable |
| `need_already_answered` | not_applicable |
| `decision_effect_balanced` | not_applicable |
| `action_responds_to_need` | not_applicable |
| `original_constraint_preserved` | yes |
| `action_acceptable` | yes |
| `regression` | no |
| `new_errors` | no |
| `answer_vs_abstention` | no_final_text |

配对比较：按本批完整响应标签未比配对C0更差；但双方都回退，Actor输入相同，差异不能归因来源合同。

依据索引：。精确 message_index/path 见同卡 reference_index。

## qid_776_s53 / r2 / C0 (card_0010)

[完整原始记录](branches/qid_776_s53__C__r2__baseline/result.json) · [事件日志](branches/qid_776_s53__C__r2__baseline/events.jsonl)

审查状态 `node_invalid`；memo_injected=False；Actor=tool_calls；reported tokens=71,469；调用耗时合计=13.187s。

**Reviewer 来源归属 → 需求**

没有输出可用Reviewer正文/四字段JSON，来源归属与需求没有可评价对象；节点失败保留全分母，不从reasoning内容补造审查，不记为语义错误或需求传递失败。

```json
null
```

**Actor 动作 → 尚未知内容**

shaman/1915/misuse/word/foreign language接近历史第一条需求，又加旧anthropologist过滤；只是同一路线重组，没有合理的新分岔。正文只是查询意图，不是人物事实。

实际提出的工具（未执行）：
```json
[
  {
    "arguments": "{\"query\": \"shaman 1915 anthropologist misuse word foreign language\"}",
    "name": "search"
  }
]
```

证据界限：仍无人物—语言误用事件—作者—1940报告官方题名的完整关系链。

| 评价轴 | 标签 |
|---|---|
| `review_source_attribution_correct` | not_applicable |
| `tool_action_direction_acceptable` | no |
| `assistant_assertions_supported` | yes |
| `final_answer_supported` | not_applicable |
| `assumption_grounded` | not_applicable |
| `need_unresolved` | not_applicable |
| `need_decision_relevant` | not_applicable |
| `need_already_answered` | not_applicable |
| `decision_effect_balanced` | not_applicable |
| `action_responds_to_need` | not_applicable |
| `original_constraint_preserved` | no |
| `action_acceptable` | no |
| `regression` | not_applicable |
| `new_errors` | no |
| `answer_vs_abstention` | no_final_text |

配对比较：同期C0对照不对自身做退化判断。

依据索引：。精确 message_index/path 见同卡 reference_index。

## qid_776_s53 / r2 / C1 (card_0011)

[完整原始记录](branches/qid_776_s53__C__r2__source_grounded_v1/result.json) · [事件日志](branches/qid_776_s53__C__r2__source_grounded_v1/events.jsonl)

审查状态 `node_invalid`；memo_injected=False；Actor=tool_calls；reported tokens=71,706；调用耗时合计=14.191s。

**Reviewer 来源归属 → 需求**

没有输出可用Reviewer正文/四字段JSON，来源归属与需求没有可评价对象；节点失败保留全分母，不从reasoning内容补造审查，不记为语义错误或需求传递失败。

```json
null
```

**Actor 动作 → 尚未知内容**

改用原题35years、3children、born1886三项联合，不带职业。历史分别查过部分组合，本次把具体居住年数和子女数联合起来，作为传记入口的细化可以接受；边界判断较弱，不能保证新召回。

实际提出的工具（未执行）：
```json
[
  {
    "arguments": "{\"query\": \"\\\"35 years\\\" \\\"three children\\\" \\\"born in 1886\\\"\"}",
    "name": "search"
  }
]
```

证据界限：仍无人物—语言误用事件—作者—1940报告官方题名的完整关系链。

| 评价轴 | 标签 |
|---|---|
| `review_source_attribution_correct` | not_applicable |
| `tool_action_direction_acceptable` | yes |
| `assistant_assertions_supported` | yes |
| `final_answer_supported` | not_applicable |
| `assumption_grounded` | not_applicable |
| `need_unresolved` | not_applicable |
| `need_decision_relevant` | not_applicable |
| `need_already_answered` | not_applicable |
| `decision_effect_balanced` | not_applicable |
| `action_responds_to_need` | not_applicable |
| `original_constraint_preserved` | yes |
| `action_acceptable` | yes |
| `regression` | no |
| `new_errors` | no |
| `answer_vs_abstention` | no_final_text |

配对比较：按本批完整响应标签未比配对C0更差；但双方都回退，Actor输入相同，差异不能归因来源合同。

依据索引：。精确 message_index/path 见同卡 reference_index。
