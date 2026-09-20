# 六次pilot逐分支复核

全部6个计划分支均保留。这里只评价已交付正文和全部工具提议，不用reasoning替代正文。没有正式S0样本，也没有真实工具结果。

## qid_517_s21 / flat / r1 (card_0006)

[完整原始记录](branches/qid_517_s21__flat__r1/result.json) · [事件日志](branches/qid_517_s21__flat__r1/events.jsonl)

**原题限制 → 允许的下一动作**

同一演员；1970年代/羊；父亲军人、母亲军营医院；2005警察角色/Iracema导演；2013惊悚片/Kinsey导演；截至2023-12。

- 查2005候选影片的警察演员或角色表，不先锁定Idris。
- 核验电影—导演绑定；允许get_document读取已见导演条目的后续窗口，但不预先声称里面有答案。
- 用原题家庭稀有线索寻找候选或核查两片同一演员关系；这可合理但不一定使用当前角色调查目的。

**实际原文及固定笔记/任务 → 完整动作 → 未决内容**

1975来自历史猜测/影片年份，不能当演员事实。未见完整家庭角色链，不宜终答。未来要核查的片目或角色不能在正文先宣布成立。

三个Search分别查Constant Gardener警察演员、Fifth Estate演员表、含Meirelles的Constant Gardener警察角色。把影片作为检验入口，未断言已核实具体演员，未锁定Idris或1975，也未放宽policeman。前缀虽反复猜演员，但此前没有专查这组角色/跨影片关系，具体调查目的体现在请求中，整个批次合理。第一与第三个调用高度相近，可能冗余；增加导演名与police officer措辞可视为召回变体，尚无结果，不能仅凭相似字符串宣判无益。空正文不扣分，正文支持轴不适用。无新来源、无终答，家庭、生肖和同一演员链仍未知。

交付响应（全部选择及工具；未执行）：
```json
[
  {
    "finish_reason": "tool_calls",
    "message": {
      "content": null,
      "refusal": null,
      "role": "assistant",
      "tool_calls": [
        {
          "function": {
            "arguments": "{\"query\": \"The Constant Gardener 2005 cast policeman actor\"}",
            "name": "search"
          },
          "id": "chatcmpl-tool-85146cc79ec69c2c",
          "type": "function"
        },
        {
          "function": {
            "arguments": "{\"query\": \"The Fifth Estate 2013 full cast actor\"}",
            "name": "search"
          },
          "id": "chatcmpl-tool-b707c64695d32b82",
          "type": "function"
        },
        {
          "function": {
            "arguments": "{\"query\": \"Fernando Meirelles 2005 film The Constant Gardener cast police officer\"}",
            "name": "search"
          },
          "id": "chatcmpl-tool-bee53e7df9638960",
          "type": "function"
        }
      ]
    }
  }
]
```

已报告usage={"prompt_tokens": 20151, "completion_tokens": 305, "total_tokens": 20456}；未知usage请求=0；耗时=25.105秒。缺失不补零。

| 评价轴 | 标签 |
|---|---|
| `body_assertions_supported` | not_applicable |
| `complete_response_acceptable` | yes |
| `final_answer_supported` | not_applicable |
| `new_error_introduced` | no |
| `regression` | not_applicable |
| `relation_scope_preserved` | yes |
| `repetition_has_new_purpose` | yes |
| `source_attribution_correct` | yes |
| `task_used_in_decision` | yes |
| `tool_direction_reasonable` | yes |

配对归因：flat为同期基线，不与自身比较退化。

## qid_517_s21 / typed / r1 (card_0003)

[完整原始记录](branches/qid_517_s21__typed__r1/result.json) · [事件日志](branches/qid_517_s21__typed__r1/events.jsonl)

**原题限制 → 允许的下一动作**

同一演员；1970年代/羊；父亲军人、母亲军营医院；2005警察角色/Iracema导演；2013惊悚片/Kinsey导演；截至2023-12。

- 查2005候选影片的警察演员或角色表，不先锁定Idris。
- 核验电影—导演绑定；允许get_document读取已见导演条目的后续窗口，但不预先声称里面有答案。
- 用原题家庭稀有线索寻找候选或核查两片同一演员关系；这可合理但不一定使用当前角色调查目的。

**实际原文及固定笔记/任务 → 完整动作 → 未决内容**

1975来自历史猜测/影片年份，不能当演员事实。未见完整家庭角色链，不宜终答。未来要核查的片目或角色不能在正文先宣布成立。

三个调用分别核验Constant Gardener警察角色、Fifth Estate演员表及1979出生/家庭线索；前两个直接使用当前调查目的，第三个是辅助生平入口，整个工具批次作为探索合理。既有工具尚未查过角色/同一演员关系，不能因同电影词重复而判旧路线循环。正文把旧1975/Idris绑定称为suspect，正确保留其假设身份，没有假称导演原文证明演员。但它以确定语气补入1975=Rabbit、1979及early1980=Goat的历法断言，给定前缀和笔记没有此换算依据。本批严格的可见证据口径下正文支持=no、完整响应=no、新的未验证出生年限定=yes；这不等于证明生肖常识本身错误。early1980只是括号说明，实际query仍1979，未据此判它已经把目标改成1980年出生。若允许基础生肖常识作为外部背景，这项可改为通过；两种口径都不支持视图带来稳定收益。没有最终身份答案或工具结果。

交付响应（全部选择及工具；未执行）：
```json
[
  {
    "finish_reason": "tool_calls",
    "message": {
      "content": "I'll investigate the role clue in the 2005 film. Note: 1975 is actually a Rabbit year in the Chinese zodiac — Goat years in the 1970s are 1979 (and early 1980), so the earlier \"1975/Idris Elba\" binding is suspect. Let me gather cast evidence for both films.",
      "refusal": null,
      "role": "assistant",
      "tool_calls": [
        {
          "function": {
            "arguments": "{\"k\": 5, \"query\": \"The Constant Gardener 2005 cast policeman\"}",
            "name": "search"
          },
          "id": "chatcmpl-tool-b673eccf24fa05fa",
          "type": "function"
        },
        {
          "function": {
            "arguments": "{\"k\": 5, \"query\": \"The Fifth Estate 2013 film full cast Bill Condon\"}",
            "name": "search"
          },
          "id": "chatcmpl-tool-99cc5e0b3d648273",
          "type": "function"
        },
        {
          "function": {
            "arguments": "{\"k\": 5, \"query\": \"actor born 1979 father was a soldier mother worked at barracks hospital\"}",
            "name": "search"
          },
          "id": "chatcmpl-tool-b0a91d18ccb7c49a",
          "type": "function"
        }
      ]
    }
  }
]
```

已报告usage={"prompt_tokens": 20192, "completion_tokens": 6264, "total_tokens": 26456}；未知usage请求=0；耗时=131.023秒。缺失不补零。

| 评价轴 | 标签 |
|---|---|
| `body_assertions_supported` | no |
| `complete_response_acceptable` | no |
| `final_answer_supported` | not_applicable |
| `new_error_introduced` | yes |
| `regression` | yes |
| `relation_scope_preserved` | yes |
| `repetition_has_new_purpose` | yes |
| `source_attribution_correct` | yes |
| `task_used_in_decision` | yes |
| `tool_direction_reasonable` | yes |

配对归因：严格可见证据口径下，typed增加未经前缀支持的历法断言，完整响应低于flat；两组的角色/演员表方向均合理。若允许生肖背景常识，双方都可通过，此退化结论不稳健，不作视图劣势推断。

## qid_546_s29 / flat / r1 (card_0005)

[完整原始记录](branches/qid_546_s29__flat__r1/result.json) · [事件日志](branches/qid_546_s29__flat__r1/events.jsonl)

**原题限制 → 允许的下一动作**

2023 decider后另两胜4–3和4–0再输；首对手<250、末对手>400；目标>300破百、最高break>3；职业1995–2006；日期2025-01-30。原题无赛事名。

- 修改或核查person×event及赛制绑定，搜索完整多场序列。
- 读取已见BritishOpen赛果窗口的下文；把它当待检验入口而非已知答案。
- 搜索球员赛季记录或不同赛事作为假设；必须区分整个候选与局部事件失败。

**实际原文及固定笔记/任务 → 完整动作 → 未决内容**

不能把decider与后两胜合并成仅两胜链。当前BritishOpen窗口只显示决赛/半决赛，不能把未展示早轮写成观察。新赛事假设未证实不等于query不合理；重复路线要看是否有新的判别目的。

finish_reason=length，正文和工具提议均为空；原始响应有reasoning但未交付可消费决策。语义轴不适用，全分母记录为交付失败，不把reasoning当正文评分。

交付响应（全部选择及工具；未执行）：
```json
[
  {
    "finish_reason": "length",
    "message": {
      "content": null,
      "refusal": null,
      "role": "assistant",
      "tool_calls": null
    }
  }
]
```

已报告usage={"prompt_tokens": 27902, "completion_tokens": 8192, "total_tokens": 36094}；未知usage请求=0；耗时=120.340秒。缺失不补零。

| 评价轴 | 标签 |
|---|---|
| `body_assertions_supported` | not_applicable |
| `complete_response_acceptable` | not_applicable |
| `final_answer_supported` | not_applicable |
| `new_error_introduced` | not_applicable |
| `regression` | not_applicable |
| `relation_scope_preserved` | not_applicable |
| `repetition_has_new_purpose` | not_applicable |
| `source_attribution_correct` | not_applicable |
| `task_used_in_decision` | not_applicable |
| `tool_direction_reasonable` | not_applicable |

配对归因：flat为同期基线，不与自身比较退化。

## qid_546_s29 / typed / r1 (card_0004)

[完整原始记录](branches/qid_546_s29__typed__r1/result.json) · [事件日志](branches/qid_546_s29__typed__r1/events.jsonl)

**原题限制 → 允许的下一动作**

2023 decider后另两胜4–3和4–0再输；首对手<250、末对手>400；目标>300破百、最高break>3；职业1995–2006；日期2025-01-30。原题无赛事名。

- 修改或核查person×event及赛制绑定，搜索完整多场序列。
- 读取已见BritishOpen赛果窗口的下文；把它当待检验入口而非已知答案。
- 搜索球员赛季记录或不同赛事作为假设；必须区分整个候选与局部事件失败。

**实际原文及固定笔记/任务 → 完整动作 → 未决内容**

不能把decider与后两胜合并成仅两胜链。当前BritishOpen窗口只显示决赛/半决赛，不能把未展示早轮写成观察。新赛事假设未证实不等于query不合理；重复路线要看是否有新的判别目的。

finish_reason=length，正文和工具提议均为空；原始响应有reasoning但未交付可消费决策。语义轴不适用，全分母记录为交付失败，不把reasoning当正文评分。

交付响应（全部选择及工具；未执行）：
```json
[
  {
    "finish_reason": "length",
    "message": {
      "content": null,
      "refusal": null,
      "role": "assistant",
      "tool_calls": null
    }
  }
]
```

已报告usage={"prompt_tokens": 27944, "completion_tokens": 8192, "total_tokens": 36136}；未知usage请求=0；耗时=173.521秒。缺失不补零。

| 评价轴 | 标签 |
|---|---|
| `body_assertions_supported` | not_applicable |
| `complete_response_acceptable` | not_applicable |
| `final_answer_supported` | not_applicable |
| `new_error_introduced` | not_applicable |
| `regression` | unknown |
| `relation_scope_preserved` | not_applicable |
| `repetition_has_new_purpose` | not_applicable |
| `source_attribution_correct` | not_applicable |
| `task_used_in_decision` | not_applicable |
| `tool_direction_reasonable` | not_applicable |

配对归因：配对没有双方可消费动作，不能由截断/超时差异推断状态语义或具体决策退化。

## qid_776_s53 / flat / r1 (card_0002)

[完整原始记录](branches/qid_776_s53__flat__r1/result.json) · [事件日志](branches/qid_776_s53__flat__r1/events.jsonl)

**原题限制 → 允许的下一动作**

1886人物；1915年4–11月旅行语言误用；同屋35年3孩子；鼓励1936–1940；作者英国早1910年代出生；1940报告、1888创刊季度期刊及官方题名。

- 将AmericanAnthropologist作为候选期刊，查1940目录/文章条目或其官方记录。
- 更换传记或报告入口并撤回anthropologist/固定1912过滤；若不使用当前期刊任务，分别标注而非自动判错。
- 读取已见期刊指南更多内容以辨认候选/入口；不得冒充官方1940全文。

**实际原文及固定笔记/任务 → 完整动作 → 未决内容**

34541是期刊指南列举项，不是1940目标报告。重复query是否合理看新目的，不能单靠字符串。未证职业不能充当必须条件；无完整人物—作者—题名链，不宜终答。

API超时，没有收到交付响应或usage。来源、任务使用、工具方向等没有可评对象，保留计划分母及未知成本，不补造模型语义错误。

交付响应（全部选择及工具；未执行）：
```json
null
```

已报告usage={}；未知usage请求=1；耗时=180.114秒。缺失不补零。

| 评价轴 | 标签 |
|---|---|
| `body_assertions_supported` | not_applicable |
| `complete_response_acceptable` | unknown |
| `final_answer_supported` | not_applicable |
| `new_error_introduced` | not_applicable |
| `regression` | not_applicable |
| `relation_scope_preserved` | not_applicable |
| `repetition_has_new_purpose` | not_applicable |
| `source_attribution_correct` | not_applicable |
| `task_used_in_decision` | not_applicable |
| `tool_direction_reasonable` | not_applicable |

配对归因：flat为同期基线，不与自身比较退化。

## qid_776_s53 / typed / r1 (card_0001)

[完整原始记录](branches/qid_776_s53__typed__r1/result.json) · [事件日志](branches/qid_776_s53__typed__r1/events.jsonl)

**原题限制 → 允许的下一动作**

1886人物；1915年4–11月旅行语言误用；同屋35年3孩子；鼓励1936–1940；作者英国早1910年代出生；1940报告、1888创刊季度期刊及官方题名。

- 将AmericanAnthropologist作为候选期刊，查1940目录/文章条目或其官方记录。
- 更换传记或报告入口并撤回anthropologist/固定1912过滤；若不使用当前期刊任务，分别标注而非自动判错。
- 读取已见期刊指南更多内容以辨认候选/入口；不得冒充官方1940全文。

**实际原文及固定笔记/任务 → 完整动作 → 未决内容**

34541是期刊指南列举项，不是1940目标报告。重复query是否合理看新目的，不能单靠字符串。未证职业不能充当必须条件；无完整人物—作者—题名链，不宜终答。

finish_reason=length，正文和工具提议均为空；原始响应有reasoning但未交付可消费决策。语义轴不适用，全分母记录为交付失败，不把reasoning当正文评分。

交付响应（全部选择及工具；未执行）：
```json
[
  {
    "finish_reason": "length",
    "message": {
      "content": null,
      "refusal": null,
      "role": "assistant",
      "tool_calls": null
    }
  }
]
```

已报告usage={"prompt_tokens": 40549, "completion_tokens": 8192, "total_tokens": 48741}；未知usage请求=0；耗时=175.370秒。缺失不补零。

| 评价轴 | 标签 |
|---|---|
| `body_assertions_supported` | not_applicable |
| `complete_response_acceptable` | not_applicable |
| `final_answer_supported` | not_applicable |
| `new_error_introduced` | not_applicable |
| `regression` | unknown |
| `relation_scope_preserved` | not_applicable |
| `repetition_has_new_purpose` | not_applicable |
| `source_attribution_correct` | not_applicable |
| `task_used_in_decision` | not_applicable |
| `tool_direction_reasonable` | not_applicable |

配对归因：配对没有双方可消费动作，不能由截断/超时差异推断状态语义或具体决策退化。
