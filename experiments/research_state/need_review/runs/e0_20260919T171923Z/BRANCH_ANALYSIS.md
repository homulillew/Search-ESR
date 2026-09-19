# 逐分支定性标注与成本

由 Codex 单评阅者完成；初评先于 private_key 揭示。人工复核尚未进行。原始 cards 与 first_pass 文件未改写。

计数口径：整体下一响应包含前导文字和全部工具调用；工具查询方向仅作补充描述。未查询外部答案、未读取 gold 或未来事件。

## qid_517_s21__A__r1 / card_0006

调用 1 次；报告总 token 18,263；调用耗时合计 7.24s；备忘注入 False；审查错误 `None`。

完整响应可接受：no；仅 Query 方向：no；相对匹配 A 退化：not_applicable。

- **assumption_grounded = not_applicable**：无 Reviewer，不适用。 依据：question, event:4:doc:46172, event:8:doc:82643

- **need_unresolved = not_applicable**：无需求，不适用。 依据：question, event:4:doc:46172, event:8:doc:82643

- **need_decision_relevant = not_applicable**：无需求，不适用。 依据：question, event:4:doc:46172, event:8:doc:82643

- **need_already_answered = not_applicable**：无需求，不适用。 依据：question, event:4:doc:46172, event:8:doc:82643

- **decision_effect_balanced = not_applicable**：无需求，不适用。 依据：question, event:4:doc:46172, event:8:doc:82643

- **action_responds_to_need = not_applicable**：无审查。 依据：question, event:4:doc:46172, event:8:doc:82643

- **original_constraint_preserved = no**：虽然尝试别的演员，最终仍用 born 1975 soldier mother nurse；1970s 被无依据压成 1975，医院工作又被当 nurse，未保留所期待的正常纠偏。 依据：question, event:4:doc:46172, event:8:doc:82643

- **action_acceptable = no**：虽然尝试别的演员，最终仍用 born 1975 soldier mother nurse；1970s 被无依据压成 1975，医院工作又被当 nurse，未保留所期待的正常纠偏。 依据：question, event:4:doc:46172, event:8:doc:82643

- **regression = not_applicable**：A 是匹配比较基线，不与自身判退化。 依据：question, event:4:doc:46172, event:8:doc:82643

- **new_errors = yes**：新增其他作品/演员经历的无依据断言，同时继承 1975 过滤。 依据：question, event:4:doc:46172, event:8:doc:82643

- **answer_vs_abstention = no_final_text**：这是工具决策批次，前导 content 即使说 the answer is 也不是终止提交；无 SDK refusal。 依据：question, event:4:doc:46172, event:8:doc:82643

引用语义：无 Reviewer 引用；仅评下一响应是否有来源支持。

517 回归检查：虽然尝试别的演员，最终仍用 born 1975 soldier mother nurse；1970s 被无依据压成 1975，医院工作又被当 nurse，未保留所期待的正常纠偏。

## qid_517_s21__B__r1 / card_0015

调用 2 次；报告总 token 39,096；调用耗时合计 18.47s；备忘注入 True；审查错误 `[]`。

完整响应可接受：no；仅 Query 方向：yes；相对匹配 A 退化：unknown。

- **assumption_grounded = no**：用 sources vary 和 main cast lists reviewed 包装 assistant 记忆，未识别 1975 硬绑定。 依据：question, event:4:doc:46172, event:8:doc:82643

- **need_unresolved = yes**：电影演员交集仍是合理未决问题，但备忘缺乏已见/自述区分。 依据：question, event:4:doc:46172, event:8:doc:82643

- **need_decision_relevant = yes**：电影演员交集仍是合理未决问题，但备忘缺乏已见/自述区分。 依据：question, event:4:doc:46172, event:8:doc:82643

- **need_already_answered = no**：仅可见关系局部已知，目标身份/比赛/角色关系未由可见原文回答；不是引用存在即已回答。 依据：question, event:4:doc:46172, event:8:doc:82643

- **decision_effect_balanced = unknown**：虽留不同解释，未明确用哪种新证据保留/修订；unknown。 依据：question, event:4:doc:46172, event:8:doc:82643

- **action_responds_to_need = no**：最终查询父亲 soldier/母亲 barracks hospital，未查备忘的电影交集。 依据：question, event:4:doc:46172, event:8:doc:82643

- **original_constraint_preserved = no**：工具 Query 很好地回到原题军营医院且撤去 1975，是局部正向；整体回答先断言 Idris 并补造 Mark Strong 等角色，故不接受整体。 依据：question, event:4:doc:46172, event:8:doc:82643

- **action_acceptable = no**：工具 Query 很好地回到原题军营医院且撤去 1975，是局部正向；整体回答先断言 Idris 并补造 Mark Strong 等角色，故不接受整体。 依据：question, event:4:doc:46172, event:8:doc:82643

- **regression = unknown**：相对A/r1查询方向更合理，但整条正文更强无证据身份断言；混合。 依据：question, event:4:doc:46172, event:8:doc:82643

- **new_errors = yes**：新增 intelligence officer 等角色细节，用身材/角色解释 soldier 背景无依据。 依据：question, event:4:doc:46172, event:8:doc:82643

- **answer_vs_abstention = no_final_text**：这是工具决策批次，前导 content 即使说 the answer is 也不是终止提交；无 SDK refusal。 依据：question, event:4:doc:46172, event:8:doc:82643

引用语义：B 未显式给任何 ref 标识；可见来源并无完整演员名单，且把无名单误称已核阅。

517 回归检查：工具 Query 很好地回到原题军营医院且撤去 1975，是局部正向；整体回答先断言 Idris 并补造 Mark Strong 等角色，故不接受整体。

## qid_517_s21__C__r1 / card_0002

调用 2 次；报告总 token 38,895；调用耗时合计 14.29s；备忘注入 True；审查错误 `[]`。

完整响应可接受：no；仅 Query 方向：yes；相对匹配 A 退化：unknown。

- **assumption_grounded = yes**：确实识别 Idris 绑定，但把 1975=Goat 与父母医疗背景写成 match，未保持这些为 assistant 猜测。 依据：question, event:4:doc:46172, event:8:doc:82643

- **need_unresolved = yes**：两电影角色/出演关系尚未建立；可改变身份判断，但一次要求验证多关系。 依据：question, event:4:doc:46172, event:8:doc:82643

- **need_decision_relevant = yes**：两电影角色/出演关系尚未建立；可改变身份判断，但一次要求验证多关系。 依据：question, event:4:doc:46172, event:8:doc:82643

- **need_already_answered = no**：仅可见关系局部已知，目标身份/比赛/角色关系未由可见原文回答；不是引用存在即已回答。 依据：question, event:4:doc:46172, event:8:doc:82643

- **decision_effect_balanced = no**：仅两部电影关系满足就说 he is the answer，忽略父母与出生条件；link fails 未区分否定证据和未检索到。 依据：question, event:4:doc:46172, event:8:doc:82643

- **action_responds_to_need = no**：Actor 未查询所需电影交集，改搜 father soldier mother nurse goat；未完成合理关系需求的响应。 依据：question, event:4:doc:46172, event:8:doc:82643

- **original_constraint_preserved = no**：查询移除 1975 是局部正向，但整条响应先断言 Idris、补造军队背景并把 policeman 放宽为 authority/security；不接受整体。 依据：question, event:4:doc:46172, event:8:doc:82643

- **action_acceptable = no**：查询移除 1975 是局部正向，但整条响应先断言 Idris、补造军队背景并把 policeman 放宽为 authority/security；不接受整体。 依据：question, event:4:doc:46172, event:8:doc:82643

- **regression = unknown**：最终查询撤掉1975，但正文更强认定 Idris、放宽角色；局部得失混合，不能判整条改善或恶化。 依据：question, event:4:doc:46172, event:8:doc:82643

- **new_errors = yes**：新增 military bases/服役等细节及放宽角色要求。 依据：question, event:4:doc:46172, event:8:doc:82643

- **answer_vs_abstention = no_final_text**：这是工具决策批次，前导 content 即使说 the answer is 也不是终止提交；无 SDK refusal。 依据：question, event:4:doc:46172, event:8:doc:82643

引用语义：46172 只支持导演启蒙，82643 只支持 Condon 作品；没有支撑 Idris 生年/家庭/角色。

517 回归检查：查询移除 1975 是局部正向，但整条响应先断言 Idris、补造军队背景并把 policeman 放宽为 authority/security；不接受整体。

## qid_517_s21__A__r2 / card_0010

调用 1 次；报告总 token 18,406；调用耗时合计 7.48s；备忘注入 False；审查错误 `None`。

完整响应可接受：no；仅 Query 方向：no；相对匹配 A 退化：not_applicable。

- **assumption_grounded = not_applicable**：无 Reviewer，不适用。 依据：question, event:4:doc:46172, event:8:doc:82643

- **need_unresolved = not_applicable**：无需求，不适用。 依据：question, event:4:doc:46172, event:8:doc:82643

- **need_decision_relevant = not_applicable**：无需求，不适用。 依据：question, event:4:doc:46172, event:8:doc:82643

- **need_already_answered = not_applicable**：无需求，不适用。 依据：question, event:4:doc:46172, event:8:doc:82643

- **decision_effect_balanced = not_applicable**：无需求，不适用。 依据：question, event:4:doc:46172, event:8:doc:82643

- **action_responds_to_need = not_applicable**：无审查。 依据：question, event:4:doc:46172, event:8:doc:82643

- **original_constraint_preserved = no**：最后 Query 与 card0006 相同，仍固定 1975；正文又把自拟主角名单说成无交集并怀疑题目。 依据：question, event:4:doc:46172, event:8:doc:82643

- **action_acceptable = no**：最后 Query 与 card0006 相同，仍固定 1975；正文又把自拟主角名单说成无交集并怀疑题目。 依据：question, event:4:doc:46172, event:8:doc:82643

- **regression = not_applicable**：A 是匹配比较基线，不与自身判退化。 依据：question, event:4:doc:46172, event:8:doc:82643

- **new_errors = no**：主要复述前缀已有的角色/出生年/演员交集断言；继承错误不重复计成新增。 依据：question, event:4:doc:46172, event:8:doc:82643

- **answer_vs_abstention = no_final_text**：这是工具决策批次，前导 content 即使说 the answer is 也不是终止提交；无 SDK refusal。 依据：question, event:4:doc:46172, event:8:doc:82643

引用语义：无 Reviewer 引用；仅评下一响应是否有来源支持。

517 回归检查：最后 Query 与 card0006 相同，仍固定 1975；正文又把自拟主角名单说成无交集并怀疑题目。

## qid_517_s21__B__r2 / card_0014

调用 2 次；报告总 token 39,140；调用耗时合计 18.56s；备忘注入 True；审查错误 `[]`。

完整响应可接受：no；仅 Query 方向：no；相对匹配 A 退化：unknown。

- **assumption_grounded = no**：把父亲 nurse 冲突写成 sources cite，把演员无交集写成事实；可见工具来源不支持这些。 依据：question, event:4:doc:46172, event:8:doc:82643

- **need_unresolved = yes**：电影角色/演员交集尚未解决且有关，但备忘将修订原题/电影作为主要出口。 依据：question, event:4:doc:46172, event:8:doc:82643

- **need_decision_relevant = yes**：电影角色/演员交集尚未解决且有关，但备忘将修订原题/电影作为主要出口。 依据：question, event:4:doc:46172, event:8:doc:82643

- **need_already_answered = no**：仅可见关系局部已知，目标身份/比赛/角色关系未由可见原文回答；不是引用存在即已回答。 依据：question, event:4:doc:46172, event:8:doc:82643

- **decision_effect_balanced = no**：倾向重新解释电影或导演而非核实候选；未保持题目约束。 依据：question, event:4:doc:46172, event:8:doc:82643

- **action_responds_to_need = no**：Actor 继续围绕 Idris 2013 thriller，略去已建立的 Condon 条件；明说 assume Idris despite discrepancy。 依据：question, event:4:doc:46172, event:8:doc:82643

- **original_constraint_preserved = no**：进一步固化候选并用 military context/security 替代 soldier/policeman，查询虽可作单点核验，整体不接受。 依据：question, event:4:doc:46172, event:8:doc:82643

- **action_acceptable = no**：进一步固化候选并用 military context/security 替代 soldier/policeman，查询虽可作单点核验，整体不接受。 依据：question, event:4:doc:46172, event:8:doc:82643

- **regression = unknown**：相对A/r2从无依据1975过滤改回显式Idris确认；都差，不能可靠量化孰差。 依据：question, event:4:doc:46172, event:8:doc:82643

- **new_errors = yes**：新增服役/基地生活等家庭叙事。 依据：question, event:4:doc:46172, event:8:doc:82643

- **answer_vs_abstention = no_final_text**：这是工具决策批次，前导 content 即使说 the answer is 也不是终止提交；无 SDK refusal。 依据：question, event:4:doc:46172, event:8:doc:82643

引用语义：46172 支持启蒙；不能顺带证明电影唯一、演员角色或家庭职业。

517 回归检查：进一步固化候选并用 military context/security 替代 soldier/policeman，查询虽可作单点核验，整体不接受。

## qid_517_s21__C__r2 / card_0017

调用 2 次；报告总 token 40,161；调用耗时合计 25.55s；备忘注入 True；审查错误 `[]`。

完整响应可接受：no；仅 Query 方向：not_applicable；相对匹配 A 退化：yes。

- **assumption_grounded = yes**：识别 Idris 绑定，但基于未核实的家庭/电影角色搭建候选确认路线。 依据：question, event:4:doc:46172, event:8:doc:15723, event:8:doc:2650

- **need_unresolved = yes**：家庭和角色关系未决且相关；同时允许另查候选，本身不是必须最终回答。 依据：question, event:4:doc:46172, event:8:doc:15723, event:8:doc:2650

- **need_decision_relevant = yes**：家庭和角色关系未决且相关；同时允许另查候选，本身不是必须最终回答。 依据：question, event:4:doc:46172, event:8:doc:15723, event:8:doc:2650

- **need_already_answered = no**：仅可见关系局部已知，目标身份/比赛/角色关系未由可见原文回答；不是引用存在即已回答。 依据：question, event:4:doc:46172, event:8:doc:15723, event:8:doc:2650

- **decision_effect_balanced = no**：允许 policeman 解释为 loose role，降低原条件；若否则 must pivot，又未规定负证据强度。 依据：question, event:4:doc:46172, event:8:doc:15723, event:8:doc:2650

- **action_responds_to_need = no**：未查证，重复说 Elba 最合适后直接交答案，未落实验证需求。 依据：question, event:4:doc:46172, event:8:doc:15723, event:8:doc:2650

- **original_constraint_preserved = no**：最终提交 Idris，承认缺 2013 关系仍指责题目混淆，并造 Captain Typho 角色；提前结束且忽略原条件。 依据：question, event:4:doc:46172, event:8:doc:15723, event:8:doc:2650

- **action_acceptable = no**：最终提交 Idris，承认缺 2013 关系仍指责题目混淆，并造 Captain Typho 角色；提前结束且忽略原条件。 依据：question, event:4:doc:46172, event:8:doc:15723, event:8:doc:2650

- **regression = yes**：相对A/r2，工具仍可用却直接最终提交未证实的Idris，纠偏转成提前结束。 依据：question, event:4:doc:46172, event:8:doc:15723, event:8:doc:2650

- **new_errors = yes**：新增 Star Wars/Captain Typho 关系等大量无来源断言。 依据：question, event:4:doc:46172, event:8:doc:15723, event:8:doc:2650

- **answer_vs_abstention = answer**：有明确人名最终答案，犹疑与自行反驳不等于弃答；SDK refusal=null。 依据：question, event:4:doc:46172, event:8:doc:15723, event:8:doc:2650

引用语义：15723/2650 只给 Condon 生涯，46172 只给 Meirelles 启蒙；不支持该演员身份、出生或家庭。

517 回归检查：最终提交 Idris，承认缺 2013 关系仍指责题目混淆，并造 Captain Typho 角色；提前结束且忽略原条件。

## qid_546_s29__A__r1 / card_0005

调用 1 次；报告总 token 26,582；调用耗时合计 9.46s；备忘注入 False；审查错误 `None`。

完整响应可接受：no；仅 Query 方向：no；相对匹配 A 退化：not_applicable。

- **assumption_grounded = not_applicable**：无 Reviewer，不适用。 依据：question, event:20:doc:55516

- **need_unresolved = not_applicable**：无需求，不适用。 依据：question, event:20:doc:55516

- **need_decision_relevant = not_applicable**：无需求，不适用。 依据：question, event:20:doc:55516

- **need_already_answered = not_applicable**：无需求，不适用。 依据：question, event:20:doc:55516

- **decision_effect_balanced = not_applicable**：无需求，不适用。 依据：question, event:20:doc:55516

- **action_responds_to_need = not_applicable**：无审查。 依据：question, event:20:doc:55516

- **original_constraint_preserved = no**：Selby+Players 保留原错误赛事绑定，并增加 Highfield/Lisowski 为未见对手过滤；重复取证。 依据：question, event:20:doc:55516

- **action_acceptable = no**：Selby+Players 保留原错误赛事绑定，并增加 Highfield/Lisowski 为未见对手过滤；重复取证。 依据：question, event:20:doc:55516

- **regression = not_applicable**：A 是匹配比较基线，不与自身判退化。 依据：question, event:20:doc:55516

- **new_errors = yes**：新增并多次改写未见赛果，按所谓 records 口吻呈现。 依据：question, event:20:doc:55516

- **answer_vs_abstention = no_final_text**：这是工具决策批次，前导 content 即使说 the answer is 也不是终止提交；无 SDK refusal。 依据：question, event:20:doc:55516

引用语义：无 Reviewer 引用；仅评下一响应是否有来源支持。

517 回归检查：not_applicable

## qid_546_s29__B__r1 / card_0003

调用 2 次；报告总 token 57,456；调用耗时合计 25.32s；备忘注入 True；审查错误 `[]`。

完整响应可接受：no；仅 Query 方向：no；相对匹配 A 退化：unknown。

- **assumption_grounded = yes**：识别赛事/比分是 hypothesis、具体赛程未证实；但将泛统计称 strong candidate，候选池和赛果仍混入 assistant 记忆。 依据：question, event:20:doc:55516

- **need_unresolved = yes**：2023 四场顺序仍未建立，直接影响身份；不应把当前统计或其他赛事末轮当同一证据。 依据：question, event:20:doc:55516

- **need_decision_relevant = yes**：2023 四场顺序仍未建立，直接影响身份；不应把当前统计或其他赛事末轮当同一证据。 依据：question, event:20:doc:55516

- **need_already_answered = no**：仅可见关系局部已知，目标身份/比赛/角色关系未由可见原文回答；不是引用存在即已回答。 依据：question, event:20:doc:55516

- **decision_effect_balanced = unknown**：指出不确定性且容纳其他人，但未给支持/反证对应的决策规则，且偏向 Selby/Players。 依据：question, event:20:doc:55516

- **action_responds_to_need = no**：转成 Judd Trump lost to Mark Allen + Players，既未建立新对手也未解除赛事绑定。 依据：question, event:20:doc:55516

- **original_constraint_preserved = no**：编出 Liam Highfield 等赛果、断言 Selby，继而以无依据 Trump/Allen 关系作为过滤；不能算需求驱动改善。 依据：question, event:20:doc:55516

- **action_acceptable = no**：编出 Liam Highfield 等赛果、断言 Selby，继而以无依据 Trump/Allen 关系作为过滤；不能算需求驱动改善。 依据：question, event:20:doc:55516

- **regression = unknown**：A/r1也编造赛程；B继续错误赛事并换未经证实对手，不能从一次响应确定相对严重度。 依据：question, event:20:doc:55516

- **new_errors = yes**：新造 Highfield/Gilbert/Allen 等比赛关系，将日期稍有偏差作为容错，违反原题。 依据：question, event:20:doc:55516

- **answer_vs_abstention = no_final_text**：这是工具决策批次，前导 content 即使说 the answer is 也不是终止提交；无 SDK refusal。 依据：question, event:20:doc:55516

引用语义：55516 支持 1999 与通用统计，不支持题设截止日期及 2023 路线；British Open 原文 m7 /3 是 Williams–Vafaei 6–3，不能读成 Selby 两场 6–0、6–4。

517 回归检查：not_applicable

## qid_546_s29__C__r1 / card_0007

调用 2 次；报告总 token 57,803；调用耗时合计 25.36s；备忘注入 True；审查错误 `[]`。

完整响应可接受：no；仅 Query 方向：yes；相对匹配 A 退化：unknown。

- **assumption_grounded = yes**：正确把 Selby+Players 路线称未证实假设，但未把人物与赛事拆开。 依据：question, event:20:doc:55516

- **need_unresolved = yes**：Selby 在指定赛事的对手与赛果仍未被看到，作为局部核验可有用，不能穷尽所有 2023 赛事。 依据：question, event:20:doc:55516

- **need_decision_relevant = yes**：Selby 在指定赛事的对手与赛果仍未被看到，作为局部核验可有用，不能穷尽所有 2023 赛事。 依据：question, event:20:doc:55516

- **need_already_answered = no**：仅可见关系局部已知，目标身份/比赛/角色关系未由可见原文回答；不是引用存在即已回答。 依据：question, event:20:doc:55516

- **decision_effect_balanced = no**：某一赛事不匹配就淘汰整个 Selby 候选，是过强排除；仍可为赛事绑定错误。 依据：question, event:20:doc:55516

- **action_responds_to_need = no**：最终搜索泛 4–3/4–0 snooker 2023，而不是确认 Selby 在指定赛事的真实记录；期间自己编造记录并无依据换 Bingham。 依据：question, event:20:doc:55516

- **original_constraint_preserved = no**：最终 Query 解除人名/赛事锁定，是方向改进；整条响应长篇捏造赛程并称 Bingham fits perfectly，因此整体不接受。 依据：question, event:20:doc:55516

- **action_acceptable = no**：最终 Query 解除人名/赛事锁定，是方向改进；整条响应长篇捏造赛程并称 Bingham fits perfectly，因此整体不接受。 依据：question, event:20:doc:55516

- **regression = unknown**：查询解除绑定，但冗长无证据赛程更多；不同质量轴混合。 依据：question, event:20:doc:55516

- **new_errors = yes**：新造 Selby–Liang 与 Bingham–Highfield/Jones/Higgins 链，三胜被两胜替代后又反复摇摆。 依据：question, event:20:doc:55516

- **answer_vs_abstention = no_final_text**：这是工具决策批次，前导 content 即使说 the answer is 也不是终止提交；无 SDK refusal。 依据：question, event:20:doc:55516

引用语义：55516 不含具体比赛，不能授权淘汰或替代候选。

517 回归检查：not_applicable

## qid_546_s29__A__r2 / card_0011

调用 1 次；报告总 token 25,753；调用耗时合计 1.70s；备忘注入 False；审查错误 `None`。

完整响应可接受：no；仅 Query 方向：no；相对匹配 A 退化：not_applicable。

- **assumption_grounded = not_applicable**：无 Reviewer，不适用。 依据：question, event:20:doc:55516

- **need_unresolved = not_applicable**：无需求，不适用。 依据：question, event:20:doc:55516

- **need_decision_relevant = not_applicable**：无需求，不适用。 依据：question, event:20:doc:55516

- **need_already_answered = not_applicable**：无需求，不适用。 依据：question, event:20:doc:55516

- **decision_effect_balanced = not_applicable**：无需求，不适用。 依据：question, event:20:doc:55516

- **action_responds_to_need = not_applicable**：无审查。 依据：question, event:20:doc:55516

- **original_constraint_preserved = yes**：以 let us try 换为 Trump 是探索而非确定认定；但没有新证据支持锁定 Players，继续同一赛事路线，按预定标准不算可接受推进。 依据：question, event:20:doc:55516

- **action_acceptable = no**：以 let us try 换为 Trump 是探索而非确定认定；但没有新证据支持锁定 Players，继续同一赛事路线，按预定标准不算可接受推进。 依据：question, event:20:doc:55516

- **regression = not_applicable**：A 是匹配比较基线，不与自身判退化。 依据：question, event:20:doc:55516

- **new_errors = no**：没有新确证性断言；“换候选”本身不标回归或新增事实错。 依据：question, event:20:doc:55516

- **answer_vs_abstention = no_final_text**：这是工具决策批次，前导 content 即使说 the answer is 也不是终止提交；无 SDK refusal。 依据：question, event:20:doc:55516

引用语义：无 Reviewer 引用；仅评下一响应是否有来源支持。

517 回归检查：not_applicable

## qid_546_s29__B__r2 / card_0018

调用 2 次；报告总 token 57,273；调用耗时合计 23.32s；备忘注入 True；审查错误 `[]`。

完整响应可接受：no；仅 Query 方向：not_applicable；相对匹配 A 退化：yes。

- **assumption_grounded = yes**：承认具体赛事是假设，统计满足不等于身份确认；仍把 Selby 称 strong candidate。 依据：question, event:20:doc:55516

- **need_unresolved = yes**：未确认 2023 顺序是合理且未解决需求，也留其他候选。 依据：question, event:20:doc:55516

- **need_decision_relevant = yes**：未确认 2023 顺序是合理且未解决需求，也留其他候选。 依据：question, event:20:doc:55516

- **need_already_answered = no**：仅可见关系局部已知，目标身份/比赛/角色关系未由可见原文回答；不是引用存在即已回答。 依据：question, event:20:doc:55516

- **decision_effect_balanced = unknown**：列出不确定项但未给多向判断规则；unknown。 依据：question, event:20:doc:55516

- **action_responds_to_need = no**：没检索新证据，直接自拟记录，再从 Selby 转 Trump。 依据：question, event:20:doc:55516

- **original_constraint_preserved = no**：以 placeholders 和未经支持对手链作最终 Trump 答案，无文档/URL引用；提前作答。 依据：question, event:20:doc:55516

- **action_acceptable = no**：以 placeholders 和未经支持对手链作最终 Trump 答案，无文档/URL引用；提前作答。 依据：question, event:20:doc:55516

- **regression = yes**：相对A/r2，未取新证据直接给Trump最终答案。 依据：question, event:20:doc:55516

- **new_errors = yes**：新增 Selby Group B、Trump–Burden/O’Sullivan 等关系，题目各条件靠猜测补齐。 依据：question, event:20:doc:55516

- **answer_vs_abstention = answer**：有明确人名最终答案，犹疑与自行反驳不等于弃答；SDK refusal=null。 依据：question, event:20:doc:55516

引用语义：55516 只给生涯简介；没有所谓 Players 的分组或 Burden/O’Sullivan 比赛证据。

517 回归检查：not_applicable

## qid_546_s29__C__r2 / card_0012

调用 2 次；报告总 token 56,144；调用耗时合计 11.66s；备忘注入 True；审查错误 `[]`。

完整响应可接受：no；仅 Query 方向：not_applicable；相对匹配 A 退化：yes。

- **assumption_grounded = yes**：正确指出 Selby+Players 是假设。 依据：question, event:20:doc:55516

- **need_unresolved = yes**：具体比赛序列未见且有关，但这个单一赛事仅是一个待检验分支。 依据：question, event:20:doc:55516

- **need_decision_relevant = yes**：具体比赛序列未见且有关，但这个单一赛事仅是一个待检验分支。 依据：question, event:20:doc:55516

- **need_already_answered = no**：仅可见关系局部已知，目标身份/比赛/角色关系未由可见原文回答；不是引用存在即已回答。 依据：question, event:20:doc:55516

- **decision_effect_balanced = no**：该赛事记录不符便淘汰整个人，不允许只修订赛事。 依据：question, event:20:doc:55516

- **action_responds_to_need = no**：没有新查证；直接将需求写成已满足，先 Selby 后 Bingham。 依据：question, event:20:doc:55516

- **original_constraint_preserved = no**：最终提交 Bingham，原题三胜后负变成两胜后负，无可见比赛证据且无引用，属证据不足的提前作答。 依据：question, event:20:doc:55516

- **action_acceptable = no**：最终提交 Bingham，原题三胜后负变成两胜后负，无可见比赛证据且无引用，属证据不足的提前作答。 依据：question, event:20:doc:55516

- **regression = yes**：A/r2继续检索，本分支无新证据便提交 Bingham，且漏一场胜利。 依据：question, event:20:doc:55516

- **new_errors = yes**：新增整条赛程与候选替换；混用截止日期统计。 依据：question, event:20:doc:55516

- **answer_vs_abstention = answer**：有明确人名最终答案，犹疑与自行反驳不等于弃答；SDK refusal=null。 依据：question, event:20:doc:55516

引用语义：引用只给生涯概况，不支持 Highfield/Carter/Liang/Lisowski/Robertson 比赛链。

517 回归检查：not_applicable

## qid_776_s53__A__r1 / card_0016

调用 1 次；报告总 token 35,917；调用耗时合计 1.06s；备忘注入 False；审查错误 `None`。

完整响应可接受：no；仅 Query 方向：no；相对匹配 A 退化：not_applicable。

- **assumption_grounded = not_applicable**：无 Reviewer，不适用。 依据：question

- **need_unresolved = not_applicable**：无需求，不适用。 依据：question

- **need_decision_relevant = not_applicable**：无需求，不适用。 依据：question

- **need_already_answered = not_applicable**：无需求，不适用。 依据：question

- **decision_effect_balanced = not_applicable**：无需求，不适用。 依据：question

- **action_responds_to_need = not_applicable**：无审查。 依据：question

- **original_constraint_preserved = yes**：shaman 1915 trip 与多次旧查询相比只换普通关键词，无新信息辨别关系；未加错误职业限定，但仍属重复取证。 依据：question

- **action_acceptable = no**：shaman 1915 trip 与多次旧查询相比只换普通关键词，无新信息辨别关系；未加错误职业限定，但仍属重复取证。 依据：question

- **regression = not_applicable**：A 是匹配比较基线，不与自身判退化。 依据：question

- **new_errors = no**：没有新的确定错误。 依据：question

- **answer_vs_abstention = no_final_text**：这是工具决策批次，前导 content 即使说 the answer is 也不是终止提交；无 SDK refusal。 依据：question

引用语义：无 Reviewer 引用；仅评下一响应是否有来源支持。

517 回归检查：not_applicable

## qid_776_s53__B__r1 / card_0008

调用 2 次；报告总 token 77,238；调用耗时合计 9.29s；备忘注入 True；审查错误 `[]`。

完整响应可接受：no；仅 Query 方向：no；相对匹配 A 退化：yes。

- **assumption_grounded = no**：把 journal established 和作者 identified 写成已建立；原文只给 AA 创办年，人物身份并未确定，职业也无来源。 依据：question, event:16:doc:34541, event:20:doc:46003, event:20:doc:69609

- **need_unresolved = yes**：寻找 Person A 仍未解决且相关，但依附于被错误宣告确定的期刊/作者背景。 依据：question, event:16:doc:34541, event:20:doc:46003, event:20:doc:69609

- **need_decision_relevant = yes**：寻找 Person A 仍未解决且相关，但依附于被错误宣告确定的期刊/作者背景。 依据：question, event:16:doc:34541, event:20:doc:46003, event:20:doc:69609

- **need_already_answered = no**：仅可见关系局部已知，目标身份/比赛/角色关系未由可见原文回答；不是引用存在即已回答。 依据：question, event:16:doc:34541, event:20:doc:46003, event:20:doc:69609

- **decision_effect_balanced = no**：没有重新考虑职业/期刊的分支，偏单路确认。 依据：question, event:16:doc:34541, event:20:doc:46003, event:20:doc:69609

- **action_responds_to_need = no**：只给旧 same house 35 years anthropologist 查询添加 biography；并未解决职业限定。 依据：question, event:16:doc:34541, event:20:doc:46003, event:20:doc:69609

- **original_constraint_preserved = no**：继续原过滤和重复语义，不接受。 依据：question, event:16:doc:34541, event:20:doc:46003, event:20:doc:69609

- **action_acceptable = no**：继续原过滤和重复语义，不接受。 依据：question, event:16:doc:34541, event:20:doc:46003, event:20:doc:69609

- **regression = yes**：A/r1尚未加职业过滤到本次Query；B/r1新增确定期刊/作者断言并把 anthropologist 加入Query。 依据：question, event:16:doc:34541, event:20:doc:46003, event:20:doc:69609

- **new_errors = yes**：Reviewer 新增已确定期刊/作者的认识状态错误；Actor 加入无证据俄语词联想，但未当正式结果。 依据：question, event:16:doc:34541, event:20:doc:46003, event:20:doc:69609

- **answer_vs_abstention = no_final_text**：这是工具决策批次，前导 content 即使说 the answer is 也不是终止提交；无 SDK refusal。 依据：question, event:16:doc:34541, event:20:doc:46003, event:20:doc:69609

引用语义：34541 只证明 AA 1888-present，不证明目标报告属于 AA；生日名单无身份匹配。

517 回归检查：not_applicable

## qid_776_s53__C__r1 / card_0013

调用 2 次；报告总 token 77,044；调用耗时合计 9.35s；备忘注入 False；审查错误 `['review must finish with stop', 'review is not a single strict JSON object: Expecting value: line 29 column 1 (char 1198)']`。

完整响应可接受：no；仅 Query 方向：no；相对匹配 A 退化：no。

- **assumption_grounded = yes**：原始截断文本识别职业假设；虽可读到语义，不能把它当成功节点。 依据：question

- **need_unresolved = yes**：身份/旅行/家庭仍未解决且相关；本条未通过结构/结束校验。 依据：question

- **need_decision_relevant = yes**：身份/旅行/家庭仍未解决且相关；本条未通过结构/结束校验。 依据：question

- **need_already_answered = no**：仅可见关系局部已知，目标身份/比赛/角色关系未由可见原文回答；不是引用存在即已回答。 依据：question

- **decision_effect_balanced = no**：仅描述找到后再找作者，缺乏不匹配如何更新的决策方向。 依据：question

- **action_responds_to_need = not_applicable**：memo_injected=false，Actor 未收到这段审查，不评价传递成功。 依据：question

- **original_constraint_preserved = yes**：与 m14 完全相同 same house 35 years born1886；原条件未改，但未产生新的下一步，不接受重复。 依据：question

- **action_acceptable = no**：与 m14 完全相同 same house 35 years born1886；原条件未改，但未产生新的下一步，不接受重复。 依据：question

- **regression = no**：回退分支和A/r1都在重复已有检索；不是审查传递成功。 依据：question

- **new_errors = no**：没有新错误；失败与重复在分母中保留。 依据：question

- **answer_vs_abstention = no_final_text**：这是工具决策批次，前导 content 即使说 the answer is 也不是终止提交；无 SDK refusal。 依据：question

引用语义：长串 references 来自可见索引，但罗列大量无关文档不构成支持；只在离线评阅截断文本，不修复 JSON。

517 回归检查：not_applicable

## qid_776_s53__A__r2 / card_0009

调用 1 次；报告总 token 35,922；调用耗时合计 0.78s；备忘注入 False；审查错误 `None`。

完整响应可接受：no；仅 Query 方向：no；相对匹配 A 退化：not_applicable。

- **assumption_grounded = not_applicable**：无 Reviewer，不适用。 依据：question

- **need_unresolved = not_applicable**：无需求，不适用。 依据：question

- **need_decision_relevant = not_applicable**：无需求，不适用。 依据：question

- **need_already_answered = not_applicable**：无需求，不适用。 依据：question

- **decision_effect_balanced = not_applicable**：无需求，不适用。 依据：question

- **action_responds_to_need = not_applicable**：无审查。 依据：question

- **original_constraint_preserved = no**：born1886 three children anthropologist 仍擅自限制职业；与历史无结果的职业路线同义，不接受。 依据：question

- **action_acceptable = no**：born1886 three children anthropologist 仍擅自限制职业；与历史无结果的职业路线同义，不接受。 依据：question

- **regression = not_applicable**：A 是匹配比较基线，不与自身判退化。 依据：question

- **new_errors = no**：继承职业限制，未见新的确定事实错误。 依据：question

- **answer_vs_abstention = no_final_text**：这是工具决策批次，前导 content 即使说 the answer is 也不是终止提交；无 SDK refusal。 依据：question

引用语义：无 Reviewer 引用；仅评下一响应是否有来源支持。

517 回归检查：not_applicable

## qid_776_s53__B__r2 / card_0004

调用 2 次；报告总 token 76,963；调用耗时合计 4.20s；备忘注入 True；审查错误 `[]`。

完整响应可接受：no；仅 Query 方向：no；相对匹配 A 退化：no。

- **assumption_grounded = yes**：明确职业假设无已见支持，并承认两本候选期刊均未确定。 依据：question, event:16:doc:34541

- **need_unresolved = yes**：人物和报告尚未找到；需求与问题相关，但未压缩成能区分下一步的关系问题。 依据：question, event:16:doc:34541

- **need_decision_relevant = yes**：人物和报告尚未找到；需求与问题相关，但未压缩成能区分下一步的关系问题。 依据：question, event:16:doc:34541

- **need_already_answered = no**：仅可见关系局部已知，目标身份/比赛/角色关系未由可见原文回答；不是引用存在即已回答。 依据：question, event:16:doc:34541

- **decision_effect_balanced = unknown**：保留两期刊和未知身份，未明确列决策分支；标 unknown，不因自由文本格式自动扣为 no。 依据：question, event:16:doc:34541

- **action_responds_to_need = no**：再次执行 m18 完全相同的 shaman 1915 anthropologist 查询，直接保留已被指出的职业过滤。 依据：question, event:16:doc:34541

- **original_constraint_preserved = no**：审查读对限制，但 Actor 既重用职业限定又重跑原 Query；不接受。 依据：question, event:16:doc:34541

- **action_acceptable = no**：审查读对限制，但 Actor 既重用职业限定又重跑原 Query；不接受。 依据：question, event:16:doc:34541

- **regression = no**：与A/r2同样保留职业过滤；未见改善，也不足判更差。 依据：question, event:16:doc:34541

- **new_errors = no**：主要延续旧职业过滤和期刊猜测，未观察到新的确定错误。 依据：question, event:16:doc:34541

- **answer_vs_abstention = no_final_text**：这是工具决策批次，前导 content 即使说 the answer is 也不是终止提交；无 SDK refusal。 依据：question, event:16:doc:34541

引用语义：无显式 ref 标识，未遵守 B 引用要求但入口未机械拒绝；语义判断可由 m9 /1 与原题支持，缺引用需单列。

517 回归检查：not_applicable

## qid_776_s53__C__r2 / card_0001

调用 2 次；报告总 token 77,504；调用耗时合计 4.74s；备忘注入 True；审查错误 `[]`。

完整响应可接受：no；仅 Query 方向：no；相对匹配 A 退化：no。

- **assumption_grounded = yes**：正确指出路线擅自限定 anthropologist/folklorist；前缀 m12/m18/m22 的查询可直接核对。 依据：question, event:16:doc:34541, event:20:doc:46003

- **need_unresolved = yes**：识别 1886 人物及旅行/家庭关系仍未解决且影响作者链；但把整套上游谜题重述为一个需求，粒度较粗。 依据：question, event:16:doc:34541, event:20:doc:46003

- **need_decision_relevant = yes**：识别 1886 人物及旅行/家庭关系仍未解决且影响作者链；但把整套上游谜题重述为一个需求，粒度较粗。 依据：question, event:16:doc:34541, event:20:doc:46003

- **need_already_answered = no**：仅可见关系局部已知，目标身份/比赛/角色关系未由可见原文回答；不是引用存在即已回答。 依据：question, event:16:doc:34541, event:20:doc:46003

- **decision_effect_balanced = unknown**：有匹配/不匹配分支，但 no such person exists 缺少可操作的证据标准；未直接说没检索到即不存在，故不武断判为明确反证错误。 依据：question, event:16:doc:34541, event:20:doc:46003

- **action_responds_to_need = no**：Actor 仍枚举前缀已反复排除的人类学家，并将 m24 的 shaman+1915+word 改成 shaman+word；未形成新的关系辨别入口。 依据：question, event:16:doc:34541, event:20:doc:46003

- **original_constraint_preserved = yes**：仅删除年份、保留重复短语，未执行有效撤销职业路径的动作；按预定重复取证标准不接受。 依据：question, event:16:doc:34541, event:20:doc:46003

- **action_acceptable = no**：仅删除年份、保留重复短语，未执行有效撤销职业路径的动作；按预定重复取证标准不接受。 依据：question, event:16:doc:34541, event:20:doc:46003

- **regression = no**：相比同题 A/r2，未观察到额外明确退化，但仍无有效推进。 依据：question, event:16:doc:34541, event:20:doc:46003

- **new_errors = no**：未见本条引入新的确定错误；旧错与低效仍在。 依据：question, event:16:doc:34541, event:20:doc:46003

- **answer_vs_abstention = no_final_text**：这是工具决策批次，前导 content 即使说 the answer is 也不是终止提交；无 SDK refusal。 依据：question, event:16:doc:34541, event:20:doc:46003

引用语义：引用存在；一般萨满页面和生日名单仅表明此前取证缺乏匹配，不能支持具体人物身份。职业限定的直接依据是 assistant 历史。

517 回归检查：not_applicable
