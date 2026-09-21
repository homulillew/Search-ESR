# 逐分支完整响应复核

全部计划分支均保留。只评价已交付正文和全部工具提议，不用reasoning替代正文；没有真实工具结果。

## qid_517_s21 / flat / r1 (card_0011)

[完整原始记录](branches/qid_517_s21__flat__r1/result.json) · [事件日志](branches/qid_517_s21__flat__r1/events.jsonl)

**原题限制 → 允许的下一动作**

同一演员；1970年代/羊；父亲军人、母亲军营医院；2005警察角色/Iracema导演；2013惊悚片/Kinsey导演；截至2023-12。

- 查2005候选影片的警察演员或角色表，不先锁定Idris。
- 核验电影—导演绑定；允许get_document读取已见导演条目的后续窗口，但不预先声称里面有答案。
- 用原题家庭稀有线索寻找候选或核查两片同一演员关系；这可合理但不一定使用当前角色调查目的。

**实际原文及固定笔记/任务 → 完整动作 → 未决内容**

1975来自历史猜测/影片年份，不能当演员事实。未见完整家庭角色链，不宜终答。未来要核查的片目或角色不能在正文先宣布成立。

完整三调用：家庭+1970s/goat保留原题而撤回未经核实1975；Constant Gardener policeman直接落实当前角色发现；Bill Condon2013 cast从旧电影识别推进到演员表。可以互相核对同一演员，未认定最终身份。家庭查询虽与旧a4近似，但去除错误精确年份有具体目的，其他两条有角色/演员新关系。导演Iracema原文不能支持演员出生年，交付未作此越界断言。角色、家庭、生肖及2013同人仍需真实结果验证。

交付响应（全部选择及工具；未执行）：
```json
[
  {
    "finish_reason": "tool_calls",
    "message": {
      "content": "",
      "refusal": null,
      "role": "assistant",
      "tool_calls": [
        {
          "function": {
            "arguments": "{\"k\": 5, \"query\": \"\\\"father was a soldier\\\" AND \\\"mother\\\" AND \\\"hospital\\\" actor born 1970s goat\"}",
            "name": "search"
          },
          "id": "call_d2cea4d744524a6ca1b32fc7",
          "index": 0,
          "type": "function"
        },
        {
          "function": {
            "arguments": "{\"k\": 5, \"query\": \"Actor played policeman in The Constant Gardener\"}",
            "name": "search"
          },
          "id": "call_60c2d299b211446aaa080de4",
          "index": 1,
          "type": "function"
        },
        {
          "function": {
            "arguments": "{\"k\": 5, \"query\": \"Bill Condon 2013 film cast\"}",
            "name": "search"
          },
          "id": "call_05fd869d99da4ed29c0a19b0",
          "index": 2,
          "type": "function"
        }
      ]
    }
  }
]
```

已报告usage={"prompt_tokens": 21327, "completion_tokens": 4140, "total_tokens": 25467}；未知usage请求=0；耗时=58.781秒。缺失不补零。

| 评价轴 | 标签 |
|---|---|
| `body_assertions_supported` | not_applicable |
| `complete_response_acceptable` | yes |
| `final_answer_supported` | not_applicable |
| `new_error_introduced` | no |
| `regression` | not_applicable |
| `relation_scope_preserved` | yes |
| `repetition_has_new_purpose` | yes |
| `source_attribution_correct` | not_applicable |
| `task_used_in_decision` | yes |
| `tool_direction_reasonable` | yes |

配对归因：flat交付角色核验+家庭+2013演员表，typed只查两片共同演员。双方整体可接受，但typed未直接使用policeman当前任务，存在任务落实程度下降；这不是最终正确率下降，也不能据单次认定布局因果。

## qid_517_s21 / flat / r2 (card_0004)

[完整原始记录](branches/qid_517_s21__flat__r2/result.json) · [事件日志](branches/qid_517_s21__flat__r2/events.jsonl)

**原题限制 → 允许的下一动作**

同一演员；1970年代/羊；父亲军人、母亲军营医院；2005警察角色/Iracema导演；2013惊悚片/Kinsey导演；截至2023-12。

- 查2005候选影片的警察演员或角色表，不先锁定Idris。
- 核验电影—导演绑定；允许get_document读取已见导演条目的后续窗口，但不预先声称里面有答案。
- 用原题家庭稀有线索寻找候选或核查两片同一演员关系；这可合理但不一定使用当前角色调查目的。

**实际原文及固定笔记/任务 → 完整动作 → 未决内容**

1975来自历史猜测/影片年份，不能当演员事实。未见完整家庭角色链，不宜终答。未来要核查的片目或角色不能在正文先宣布成立。

三个家庭线索搜索分别撤回精确出生年份、增加barrack's hospital及mother worked at the barracks稀有短语；后两个比既有笼统mother/hospital更具体，可作为合理召回入口。没有落实当前警察角色调查，但任务是可质疑提案，不因此单独判错。未锁定Idris或1975；未证明任何演员/父母关系，跨影片与生肖仍未知。

交付响应（全部选择及工具；未执行）：
```json
[
  {
    "finish_reason": "tool_calls",
    "message": {
      "content": "",
      "refusal": null,
      "role": "assistant",
      "tool_calls": [
        {
          "function": {
            "arguments": "{\"query\": \"\\\"father was a soldier\\\" \\\"mother\\\" \\\"hospital\\\" actor\"}",
            "name": "search"
          },
          "id": "call_43da8c19ac764a649f5a77ae",
          "index": 0,
          "type": "function"
        },
        {
          "function": {
            "arguments": "{\"query\": \"\\\"barrack's hospital\\\" actor\"}",
            "name": "search"
          },
          "id": "call_ea68692fce474efdb0d80cf2",
          "index": 1,
          "type": "function"
        },
        {
          "function": {
            "arguments": "{\"query\": \"\\\"mother worked at the barracks\\\" actor\"}",
            "name": "search"
          },
          "id": "call_ebad579d37c74a8ab21b7bc7",
          "index": 2,
          "type": "function"
        }
      ]
    }
  }
]
```

已报告usage={"prompt_tokens": 21327, "completion_tokens": 3667, "total_tokens": 24994}；未知usage请求=0；耗时=50.860秒。缺失不补零。

| 评价轴 | 标签 |
|---|---|
| `body_assertions_supported` | not_applicable |
| `complete_response_acceptable` | yes |
| `final_answer_supported` | not_applicable |
| `new_error_introduced` | no |
| `regression` | not_applicable |
| `relation_scope_preserved` | yes |
| `repetition_has_new_purpose` | yes |
| `source_attribution_correct` | not_applicable |
| `task_used_in_decision` | no |
| `tool_direction_reasonable` | yes |

配对归因：flat交付合理家庭入口，typed超时，无可配对动作；失败不能解释为状态语义退化。

## qid_517_s21 / typed / r1 (card_0006)

[完整原始记录](branches/qid_517_s21__typed__r1/result.json) · [事件日志](branches/qid_517_s21__typed__r1/events.jsonl)

**原题限制 → 允许的下一动作**

同一演员；1970年代/羊；父亲军人、母亲军营医院；2005警察角色/Iracema导演；2013惊悚片/Kinsey导演；截至2023-12。

- 查2005候选影片的警察演员或角色表，不先锁定Idris。
- 核验电影—导演绑定；允许get_document读取已见导演条目的后续窗口，但不预先声称里面有答案。
- 用原题家庭稀有线索寻找候选或核查两片同一演员关系；这可合理但不一定使用当前角色调查目的。

**实际原文及固定笔记/任务 → 完整动作 → 未决内容**

1975来自历史猜测/影片年份，不能当演员事实。未见完整家庭角色链，不宜终答。未来要核查的片目或角色不能在正文先宣布成立。

检索Constant Gardener与Fifth Estate共同演员，使用同一人跨影片约束作为候选发现入口，未预先认定候选或家庭信息。相比旧传记猜测是新关系检验。没有policeman角色核验，故严格当前角色任务使用=no，但完整动作可接受；需后续核验影片绑定、警察角色及出生家庭。

交付响应（全部选择及工具；未执行）：
```json
[
  {
    "finish_reason": "tool_calls",
    "message": {
      "content": "",
      "refusal": null,
      "role": "assistant",
      "tool_calls": [
        {
          "function": {
            "arguments": "{\"query\": \"\\\"Constant Gardener\\\" AND \\\"Fifth Estate\\\" actor\"}",
            "name": "search"
          },
          "id": "call_dbb35a56cc77408180259329",
          "index": 0,
          "type": "function"
        }
      ]
    }
  }
]
```

已报告usage={"prompt_tokens": 21368, "completion_tokens": 8463, "total_tokens": 29831}；未知usage请求=0；耗时=109.657秒。缺失不补零。

| 评价轴 | 标签 |
|---|---|
| `body_assertions_supported` | not_applicable |
| `complete_response_acceptable` | yes |
| `final_answer_supported` | not_applicable |
| `new_error_introduced` | no |
| `regression` | yes |
| `relation_scope_preserved` | yes |
| `repetition_has_new_purpose` | yes |
| `source_attribution_correct` | not_applicable |
| `task_used_in_decision` | no |
| `tool_direction_reasonable` | yes |

配对归因：flat交付角色核验+家庭+2013演员表，typed只查两片共同演员。双方整体可接受，但typed未直接使用policeman当前任务，存在任务落实程度下降；这不是最终正确率下降，也不能据单次认定布局因果。

## qid_517_s21 / typed / r2 (card_0002)

[完整原始记录](branches/qid_517_s21__typed__r2/result.json) · [事件日志](branches/qid_517_s21__typed__r2/events.jsonl)

**原题限制 → 允许的下一动作**

同一演员；1970年代/羊；父亲军人、母亲军营医院；2005警察角色/Iracema导演；2013惊悚片/Kinsey导演；截至2023-12。

- 查2005候选影片的警察演员或角色表，不先锁定Idris。
- 核验电影—导演绑定；允许get_document读取已见导演条目的后续窗口，但不预先声称里面有答案。
- 用原题家庭稀有线索寻找候选或核查两片同一演员关系；这可合理但不一定使用当前角色调查目的。

**实际原文及固定笔记/任务 → 完整动作 → 未决内容**

1975来自历史猜测/影片年份，不能当演员事实。未见完整家庭角色链，不宜终答。未来要核查的片目或角色不能在正文先宣布成立。

APITimeoutError，无收到的交付响应及usage。没有可评分的来源归属、动作或正文，不补造语义错误；保留12个计划分支分母和未知成本。

交付响应（全部选择及工具；未执行）：
```json
null
```

已报告usage={}；未知usage请求=1；耗时=180.146秒。缺失不补零。

| 评价轴 | 标签 |
|---|---|
| `body_assertions_supported` | not_applicable |
| `complete_response_acceptable` | unknown |
| `final_answer_supported` | not_applicable |
| `new_error_introduced` | not_applicable |
| `regression` | unknown |
| `relation_scope_preserved` | not_applicable |
| `repetition_has_new_purpose` | not_applicable |
| `source_attribution_correct` | not_applicable |
| `task_used_in_decision` | not_applicable |
| `tool_direction_reasonable` | not_applicable |

配对归因：flat交付合理家庭入口，typed超时，无可配对动作；失败不能解释为状态语义退化。

## qid_546_s29 / flat / r1 (card_0008)

[完整原始记录](branches/qid_546_s29__flat__r1/result.json) · [事件日志](branches/qid_546_s29__flat__r1/events.jsonl)

**原题限制 → 允许的下一动作**

2023 decider后另两胜4–3和4–0再输；首对手<250、末对手>400；目标>300破百、最高break>3；职业1995–2006；日期2025-01-30。原题无赛事名。

- 修改或核查person×event及赛制绑定，搜索完整多场序列。
- 读取已见BritishOpen赛果窗口的下文；把它当待检验入口而非已知答案。
- 搜索球员赛季记录或不同赛事作为假设；必须区分整个候选与局部事件失败。

**实际原文及固定笔记/任务 → 完整动作 → 未决内容**

不能把decider与后两胜合并成仅两胜链。当前BritishOpen窗口只显示决赛/半决赛，不能把未展示早轮写成观察。新赛事假设未证实不等于query不合理；重复路线要看是否有新的判别目的。

单条2023/decider/4–3/4–0查询撤回Players与Selby绑定，体现开放赛事的比赛序列调查目的。与旧a0/a1宽序列检索相近，缩短及加引号可能改变召回，尚无结果，新增信息价值未知；不能只按同词判坏，也不能认为已核实四场顺序。省略后续败者条件不等于确认不需要该条件，完整链、球员及2025资格待查。

交付响应（全部选择及工具；未执行）：
```json
[
  {
    "finish_reason": "tool_calls",
    "message": {
      "content": "",
      "refusal": null,
      "role": "assistant",
      "tool_calls": [
        {
          "function": {
            "arguments": "{\"query\": \"snooker 2023 \\\"4-3\\\" \\\"4-0\\\" decider\", \"k\": 5}",
            "name": "search"
          },
          "id": "call_5493d442e679471bbf083a30",
          "index": 0,
          "type": "function"
        }
      ]
    }
  }
]
```

已报告usage={"prompt_tokens": 31259, "completion_tokens": 1031, "total_tokens": 32290}；未知usage请求=0；耗时=15.368秒。缺失不补零。

| 评价轴 | 标签 |
|---|---|
| `body_assertions_supported` | not_applicable |
| `complete_response_acceptable` | yes |
| `final_answer_supported` | not_applicable |
| `new_error_introduced` | no |
| `regression` | not_applicable |
| `relation_scope_preserved` | yes |
| `repetition_has_new_purpose` | unknown |
| `source_attribution_correct` | not_applicable |
| `task_used_in_decision` | yes |
| `tool_direction_reasonable` | yes |

配对归因：两组解码后的工具名称和参数完全一致，均为snooker 2023 "4-3" "4-0" decider、k=5；没有可观察的动作改变。

## qid_546_s29 / flat / r2 (card_0012)

[完整原始记录](branches/qid_546_s29__flat__r2/result.json) · [事件日志](branches/qid_546_s29__flat__r2/events.jsonl)

**原题限制 → 允许的下一动作**

2023 decider后另两胜4–3和4–0再输；首对手<250、末对手>400；目标>300破百、最高break>3；职业1995–2006；日期2025-01-30。原题无赛事名。

- 修改或核查person×event及赛制绑定，搜索完整多场序列。
- 读取已见BritishOpen赛果窗口的下文；把它当待检验入口而非已知答案。
- 搜索球员赛季记录或不同赛事作为假设；必须区分整个候选与局部事件失败。

**实际原文及固定笔记/任务 → 完整动作 → 未决内容**

不能把decider与后两胜合并成仅两胜链。当前BritishOpen窗口只显示决赛/半决赛，不能把未展示早轮写成观察。新赛事假设未证实不等于query不合理；重复路线要看是否有新的判别目的。

单条2023/decider/4–3/4–0查询撤回Players与Selby绑定，体现开放赛事的比赛序列调查目的。与旧a0/a1宽序列检索相近，缩短及加引号可能改变召回，尚无结果，新增信息价值未知；不能只按同词判坏，也不能认为已核实四场顺序。省略后续败者条件不等于确认不需要该条件，完整链、球员及2025资格待查。

交付响应（全部选择及工具；未执行）：
```json
[
  {
    "finish_reason": "tool_calls",
    "message": {
      "content": "",
      "refusal": null,
      "role": "assistant",
      "tool_calls": [
        {
          "function": {
            "arguments": "{\"query\": \"snooker 2023 \\\"decider\\\" \\\"4-3\\\" \\\"4-0\\\"\"}",
            "name": "search"
          },
          "id": "call_6bc6d1a9f18a4cb09a68188b",
          "index": 0,
          "type": "function"
        }
      ]
    }
  }
]
```

已报告usage={"prompt_tokens": 31259, "completion_tokens": 2383, "total_tokens": 33642}；未知usage请求=0；耗时=36.771秒。缺失不补零。

| 评价轴 | 标签 |
|---|---|
| `body_assertions_supported` | not_applicable |
| `complete_response_acceptable` | yes |
| `final_answer_supported` | not_applicable |
| `new_error_introduced` | no |
| `regression` | not_applicable |
| `relation_scope_preserved` | yes |
| `repetition_has_new_purpose` | unknown |
| `source_attribution_correct` | not_applicable |
| `task_used_in_decision` | yes |
| `tool_direction_reasonable` | yes |

配对归因：flat继续宽比分链，typed新增European Tour假设。动作发生变化，但该假设没有新结果验证，无法判断改善或退化，不能把换赛事词当状态收益。

## qid_546_s29 / typed / r1 (card_0007)

[完整原始记录](branches/qid_546_s29__typed__r1/result.json) · [事件日志](branches/qid_546_s29__typed__r1/events.jsonl)

**原题限制 → 允许的下一动作**

2023 decider后另两胜4–3和4–0再输；首对手<250、末对手>400；目标>300破百、最高break>3；职业1995–2006；日期2025-01-30。原题无赛事名。

- 修改或核查person×event及赛制绑定，搜索完整多场序列。
- 读取已见BritishOpen赛果窗口的下文；把它当待检验入口而非已知答案。
- 搜索球员赛季记录或不同赛事作为假设；必须区分整个候选与局部事件失败。

**实际原文及固定笔记/任务 → 完整动作 → 未决内容**

不能把decider与后两胜合并成仅两胜链。当前BritishOpen窗口只显示决赛/半决赛，不能把未展示早轮写成观察。新赛事假设未证实不等于query不合理；重复路线要看是否有新的判别目的。

单条2023/decider/4–3/4–0查询撤回Players与Selby绑定，体现开放赛事的比赛序列调查目的。与旧a0/a1宽序列检索相近，缩短及加引号可能改变召回，尚无结果，新增信息价值未知；不能只按同词判坏，也不能认为已核实四场顺序。省略后续败者条件不等于确认不需要该条件，完整链、球员及2025资格待查。

交付响应（全部选择及工具；未执行）：
```json
[
  {
    "finish_reason": "tool_calls",
    "message": {
      "content": "",
      "refusal": null,
      "role": "assistant",
      "tool_calls": [
        {
          "function": {
            "arguments": "{\"query\": \"snooker 2023 \\\"4-3\\\" \\\"4-0\\\" decider\", \"k\": 5}",
            "name": "search"
          },
          "id": "call_d566ef79a4b546ee834153cf",
          "index": 0,
          "type": "function"
        }
      ]
    }
  }
]
```

已报告usage={"prompt_tokens": 31301, "completion_tokens": 1986, "total_tokens": 33287}；未知usage请求=0；耗时=30.546秒。缺失不补零。

| 评价轴 | 标签 |
|---|---|
| `body_assertions_supported` | not_applicable |
| `complete_response_acceptable` | yes |
| `final_answer_supported` | not_applicable |
| `new_error_introduced` | no |
| `regression` | no |
| `relation_scope_preserved` | yes |
| `repetition_has_new_purpose` | unknown |
| `source_attribution_correct` | not_applicable |
| `task_used_in_decision` | yes |
| `tool_direction_reasonable` | yes |

配对归因：两组解码后的工具名称和参数完全一致，均为snooker 2023 "4-3" "4-0" decider、k=5；没有可观察的动作改变。

## qid_546_s29 / typed / r2 (card_0005)

[完整原始记录](branches/qid_546_s29__typed__r2/result.json) · [事件日志](branches/qid_546_s29__typed__r2/events.jsonl)

**原题限制 → 允许的下一动作**

2023 decider后另两胜4–3和4–0再输；首对手<250、末对手>400；目标>300破百、最高break>3；职业1995–2006；日期2025-01-30。原题无赛事名。

- 修改或核查person×event及赛制绑定，搜索完整多场序列。
- 读取已见BritishOpen赛果窗口的下文；把它当待检验入口而非已知答案。
- 搜索球员赛季记录或不同赛事作为假设；必须区分整个候选与局部事件失败。

**实际原文及固定笔记/任务 → 完整动作 → 未决内容**

不能把decider与后两胜合并成仅两胜链。当前BritishOpen窗口只显示决赛/半决赛，不能把未展示早轮写成观察。新赛事假设未证实不等于query不合理；重复路线要看是否有新的判别目的。

单条检索以European Tour作为新的赛事探索入口，包含2023及4–3/4–0；撤回旧Players/Selby绑定，是核查其他person×event关系的一种选择。可见前缀没有证明该赛事存在/符合题意，query也未宣称其已成立，因此不能把未证实的检索假设直接判为事实幻觉。decider/后续败者尚待核验，省略词不等于放宽原题。实际召回、完整四场链和日期资格未知。

交付响应（全部选择及工具；未执行）：
```json
[
  {
    "finish_reason": "tool_calls",
    "message": {
      "content": "",
      "refusal": null,
      "role": "assistant",
      "tool_calls": [
        {
          "function": {
            "arguments": "{\"query\": \"snooker 2023 European Tour \\\"4-3\\\" \\\"4-0\\\" results\", \"k\": 5}",
            "name": "search"
          },
          "id": "call_661e5427c2a545fe9058682b",
          "index": 0,
          "type": "function"
        }
      ]
    }
  }
]
```

已报告usage={"prompt_tokens": 31301, "completion_tokens": 1683, "total_tokens": 32984}；未知usage请求=0；耗时=24.853秒。缺失不补零。

| 评价轴 | 标签 |
|---|---|
| `body_assertions_supported` | not_applicable |
| `complete_response_acceptable` | yes |
| `final_answer_supported` | not_applicable |
| `new_error_introduced` | no |
| `regression` | unknown |
| `relation_scope_preserved` | yes |
| `repetition_has_new_purpose` | yes |
| `source_attribution_correct` | not_applicable |
| `task_used_in_decision` | yes |
| `tool_direction_reasonable` | yes |

配对归因：flat继续宽比分链，typed新增European Tour假设。动作发生变化，但该假设没有新结果验证，无法判断改善或退化，不能把换赛事词当状态收益。

## qid_776_s53 / flat / r1 (card_0003)

[完整原始记录](branches/qid_776_s53__flat__r1/result.json) · [事件日志](branches/qid_776_s53__flat__r1/events.jsonl)

**原题限制 → 允许的下一动作**

1886人物；1915年4–11月旅行语言误用；同屋35年3孩子；鼓励1936–1940；作者英国早1910年代出生；1940报告、1888创刊季度期刊及官方题名。

- 将AmericanAnthropologist作为候选期刊，查1940目录/文章条目或其官方记录。
- 更换传记或报告入口并撤回anthropologist/固定1912过滤；若不使用当前期刊任务，分别标注而非自动判错。
- 读取已见期刊指南更多内容以辨认候选/入口；不得冒充官方1940全文。

**实际原文及固定笔记/任务 → 完整动作 → 未决内容**

34541是期刊指南列举项，不是1940目标报告。重复query是否合理看新目的，不能单靠字符串。未证职业不能充当必须条件；无完整人物—作者—题名链，不宜终答。

四个调用必须整体评价：前两个与历史a1（mistaken for a shaman 1915）和a2（born in1886/three children/same house）参数query完全相同，前缀已有返回且未交付新的核验理由。第三个是更精确的report on cultural discoveries 1940短语；第四个American Anthropologist 1940 report使用候选期刊入口，正确撤回职业预设，作为探索合理。后两个不能抵销前两个无新增目的的直接重跑，故严格完整批次=no，工具批次方向=no，task_used=yes。这是继承旧搜索循环，不是新事实错误；没有把期刊指南断言为官方记录。目标报告、作者及鼓励者仍未知。

交付响应（全部选择及工具；未执行）：
```json
[
  {
    "finish_reason": "tool_calls",
    "message": {
      "content": "",
      "refusal": null,
      "role": "assistant",
      "tool_calls": [
        {
          "function": {
            "arguments": "{\"query\": \"\\\"mistaken for a shaman\\\" 1915\"}",
            "name": "search"
          },
          "id": "call_9c99783f06b9499a9f692ec6",
          "index": 0,
          "type": "function"
        },
        {
          "function": {
            "arguments": "{\"query\": \"\\\"born in 1886\\\" \\\"three children\\\" \\\"same house\\\"\"}",
            "name": "search"
          },
          "id": "call_ab0a5a2bc75d4382b123fbb2",
          "index": 1,
          "type": "function"
        },
        {
          "function": {
            "arguments": "{\"query\": \"\\\"report on cultural discoveries\\\" 1940\"}",
            "name": "search"
          },
          "id": "call_d07ab7854b4a481087d1b304",
          "index": 2,
          "type": "function"
        },
        {
          "function": {
            "arguments": "{\"query\": \"\\\"American Anthropologist\\\" 1940 report\"}",
            "name": "search"
          },
          "id": "call_3616eeeb88b046f9a0d2c207",
          "index": 3,
          "type": "function"
        }
      ]
    }
  }
]
```

已报告usage={"prompt_tokens": 43693, "completion_tokens": 3378, "total_tokens": 47071}；未知usage请求=0；耗时=23.610秒。缺失不补零。

| 评价轴 | 标签 |
|---|---|
| `body_assertions_supported` | not_applicable |
| `complete_response_acceptable` | no |
| `final_answer_supported` | not_applicable |
| `new_error_introduced` | no |
| `regression` | not_applicable |
| `relation_scope_preserved` | yes |
| `repetition_has_new_purpose` | no |
| `source_attribution_correct` | not_applicable |
| `task_used_in_decision` | yes |
| `tool_direction_reasonable` | no |

配对归因：flat批次有候选期刊入口也有两个无新目的的精确重跑；typed超时，没有配对动作，不能归因布局。

## qid_776_s53 / flat / r2 (card_0009)

[完整原始记录](branches/qid_776_s53__flat__r2/result.json) · [事件日志](branches/qid_776_s53__flat__r2/events.jsonl)

**原题限制 → 允许的下一动作**

1886人物；1915年4–11月旅行语言误用；同屋35年3孩子；鼓励1936–1940；作者英国早1910年代出生；1940报告、1888创刊季度期刊及官方题名。

- 将AmericanAnthropologist作为候选期刊，查1940目录/文章条目或其官方记录。
- 更换传记或报告入口并撤回anthropologist/固定1912过滤；若不使用当前期刊任务，分别标注而非自动判错。
- 读取已见期刊指南更多内容以辨认候选/入口；不得冒充官方1940全文。

**实际原文及固定笔记/任务 → 完整动作 → 未决内容**

34541是期刊指南列举项，不是1940目标报告。重复query是否合理看新目的，不能单靠字符串。未证职业不能充当必须条件；无完整人物—作者—题名链，不宜终答。

四条分别查cultural discoveries1940报告、1886/三孩子/house、inadvertent misuse/foreign language、shaman/travel。撤回职业与部分过窄短语，第三条把外语误用作为入口、第四条旅行语境可扩召回；都属于待验证假设，不是已证实人物事实。未查候选期刊官方1940记录，task_used=no。多条与旧检索主题相近，净新增价值未知，但并非完全相同参数重跑，整体保守接受。报告标题、三个人物关系仍未定。

交付响应（全部选择及工具；未执行）：
```json
[
  {
    "finish_reason": "tool_calls",
    "message": {
      "content": "",
      "refusal": null,
      "role": "assistant",
      "tool_calls": [
        {
          "function": {
            "arguments": "{\"query\": \"\\\"cultural discoveries\\\" 1940 report\"}",
            "name": "search"
          },
          "id": "call_27b86267980e4189b068abd7",
          "index": 0,
          "type": "function"
        },
        {
          "function": {
            "arguments": "{\"query\": \"\\\"born in 1886\\\" \\\"three children\\\" \\\"house\\\"\"}",
            "name": "search"
          },
          "id": "call_bd2cc59d0d4f468f857d5eef",
          "index": 1,
          "type": "function"
        },
        {
          "function": {
            "arguments": "{\"query\": \"\\\"inadvertent misuse\\\" word \\\"foreign language\\\"\"}",
            "name": "search"
          },
          "id": "call_a62f0da70dcc4782b9de7f0a",
          "index": 2,
          "type": "function"
        },
        {
          "function": {
            "arguments": "{\"query\": \"\\\"mistaken for a shaman\\\" travel\"}",
            "name": "search"
          },
          "id": "call_c69495d7a9064fbca0b081ed",
          "index": 3,
          "type": "function"
        }
      ]
    }
  }
]
```

已报告usage={"prompt_tokens": 43693, "completion_tokens": 1586, "total_tokens": 45279}；未知usage请求=0；耗时=10.995秒。缺失不补零。

| 评价轴 | 标签 |
|---|---|
| `body_assertions_supported` | not_applicable |
| `complete_response_acceptable` | yes |
| `final_answer_supported` | not_applicable |
| `new_error_introduced` | no |
| `regression` | not_applicable |
| `relation_scope_preserved` | yes |
| `repetition_has_new_purpose` | unknown |
| `source_attribution_correct` | not_applicable |
| `task_used_in_decision` | no |
| `tool_direction_reasonable` | yes |

配对归因：flat混合报告和传记短语，typed以shaman/house变体继续旧路线。双方均未采用候选期刊官方条目任务；typed完整合理性unknown，不能确认退化或布局收益。

## qid_776_s53 / typed / r1 (card_0001)

[完整原始记录](branches/qid_776_s53__typed__r1/result.json) · [事件日志](branches/qid_776_s53__typed__r1/events.jsonl)

**原题限制 → 允许的下一动作**

1886人物；1915年4–11月旅行语言误用；同屋35年3孩子；鼓励1936–1940；作者英国早1910年代出生；1940报告、1888创刊季度期刊及官方题名。

- 将AmericanAnthropologist作为候选期刊，查1940目录/文章条目或其官方记录。
- 更换传记或报告入口并撤回anthropologist/固定1912过滤；若不使用当前期刊任务，分别标注而非自动判错。
- 读取已见期刊指南更多内容以辨认候选/入口；不得冒充官方1940全文。

**实际原文及固定笔记/任务 → 完整动作 → 未决内容**

34541是期刊指南列举项，不是1940目标报告。重复query是否合理看新目的，不能单靠字符串。未证职业不能充当必须条件；无完整人物—作者—题名链，不宜终答。

APITimeoutError，无收到的交付响应及usage。没有可评分的来源归属、动作或正文，不补造语义错误；保留12个计划分支分母和未知成本。

交付响应（全部选择及工具；未执行）：
```json
null
```

已报告usage={}；未知usage请求=1；耗时=180.048秒。缺失不补零。

| 评价轴 | 标签 |
|---|---|
| `body_assertions_supported` | not_applicable |
| `complete_response_acceptable` | unknown |
| `final_answer_supported` | not_applicable |
| `new_error_introduced` | not_applicable |
| `regression` | unknown |
| `relation_scope_preserved` | not_applicable |
| `repetition_has_new_purpose` | not_applicable |
| `source_attribution_correct` | not_applicable |
| `task_used_in_decision` | not_applicable |
| `tool_direction_reasonable` | not_applicable |

配对归因：flat批次有候选期刊入口也有两个无新目的的精确重跑；typed超时，没有配对动作，不能归因布局。

## qid_776_s53 / typed / r2 (card_0010)

[完整原始记录](branches/qid_776_s53__typed__r2/result.json) · [事件日志](branches/qid_776_s53__typed__r2/events.jsonl)

**原题限制 → 允许的下一动作**

1886人物；1915年4–11月旅行语言误用；同屋35年3孩子；鼓励1936–1940；作者英国早1910年代出生；1940报告、1888创刊季度期刊及官方题名。

- 将AmericanAnthropologist作为候选期刊，查1940目录/文章条目或其官方记录。
- 更换传记或报告入口并撤回anthropologist/固定1912过滤；若不使用当前期刊任务，分别标注而非自动判错。
- 读取已见期刊指南更多内容以辨认候选/入口；不得冒充官方1940全文。

**实际原文及固定笔记/任务 → 完整动作 → 未决内容**

34541是期刊指南列举项，不是1940目标报告。重复query是否合理看新目的，不能单靠字符串。未证职业不能充当必须条件；无完整人物—作者—题名链，不宜终答。

四条搜索为shaman误认的四种人称OR变体、word误用变体、1886/three children/same house、same house/35 years/1886。前两条可解释为扩大原文措辞覆盖，后两条与a2/a6近似；没有新增来源、主体关系或期刊入口，也未说明为何回到已反复搜索的路线。因为语言变体可能合理，不能仅凭字符串相似判失败；保留完整合理性和重复新目的为unknown，而非挑选其中一条判成功。未采用当前1940官方条目任务，也没有误加anthropologist职业。

交付响应（全部选择及工具；未执行）：
```json
[
  {
    "finish_reason": "tool_calls",
    "message": {
      "content": "",
      "refusal": null,
      "role": "assistant",
      "tool_calls": [
        {
          "function": {
            "arguments": "{\"k\": 5, \"query\": \"\\\"mistaken for a shaman\\\" OR \\\"mistook me for a shaman\\\" OR \\\"mistook him for a shaman\\\" OR \\\"mistook her for a shaman\\\"\"}",
            "name": "search"
          },
          "id": "call_64cab846ff8a4366a053bfe1",
          "index": 0,
          "type": "function"
        },
        {
          "function": {
            "arguments": "{\"k\": 5, \"query\": \"\\\"misuse of a word\\\" shaman OR \\\"misused a word\\\" shaman\"}",
            "name": "search"
          },
          "id": "call_96a0a4ac76654287b16e5aff",
          "index": 1,
          "type": "function"
        },
        {
          "function": {
            "arguments": "{\"k\": 5, \"query\": \"born 1886 \\\"three children\\\" \\\"same house\\\"\"}",
            "name": "search"
          },
          "id": "call_84a034a6b8e94ae5a93a47a8",
          "index": 2,
          "type": "function"
        },
        {
          "function": {
            "arguments": "{\"k\": 5, \"query\": \"\\\"same house\\\" \\\"35 years\\\" born 1886\"}",
            "name": "search"
          },
          "id": "call_29d8b93cf00e4921aaf06c80",
          "index": 3,
          "type": "function"
        }
      ]
    }
  }
]
```

已报告usage={"prompt_tokens": 43733, "completion_tokens": 3316, "total_tokens": 47049}；未知usage请求=0；耗时=25.639秒。缺失不补零。

| 评价轴 | 标签 |
|---|---|
| `body_assertions_supported` | not_applicable |
| `complete_response_acceptable` | unknown |
| `final_answer_supported` | not_applicable |
| `new_error_introduced` | no |
| `regression` | unknown |
| `relation_scope_preserved` | yes |
| `repetition_has_new_purpose` | unknown |
| `source_attribution_correct` | not_applicable |
| `task_used_in_decision` | no |
| `tool_direction_reasonable` | unknown |

配对归因：flat混合报告和传记短语，typed以shaman/house变体继续旧路线。双方均未采用候选期刊官方条目任务；typed完整合理性unknown，不能确认退化或布局收益。
