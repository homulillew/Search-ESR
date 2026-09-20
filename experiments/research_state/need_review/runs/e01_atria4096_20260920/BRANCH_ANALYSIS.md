# 4096 上限 C0/C1 逐分支分析

先前缀、再 Reviewer、再 Actor，最后核对配对。单一 Codex 辅助评阅，已知旧输出和稳定卡片顺序，不是盲评或独立人工金标。保留所有计划分支，未知、不适用、失败分别记录。

完整响应指标保留对正文及全部工具调用的评价。工具方向可接受不代表检索有效；没有执行任何工具。超时请求没有收到的服务端输出与成本无法补造。

## qid_517_s21 / r1 / C0 (card_0008)

[原始记录](branches/qid_517_s21__C__r1__baseline/result.json) · [事件日志](branches/qid_517_s21__C__r1__baseline/events.jsonl)

Reviewer=`node_invalid`；memo_injected=False；Actor=tool_calls。已报告 token 下界 42,667，调用耗时合计 64.295 秒；未知成本另见原始记录和机械汇总。

**原题限定及事前允许的下一动作**

Born1970s/goat; father soldier, mother barracks hospital; policeman2005 film/director inspired by Iracema; same actor2013 thriller/director of Kinsey; as-ofDec2023.

Check policeman cast in2005 film; connect to2013 thriller cast; investigate family with broad1970s, not unsupported1975. Directors locally grounded, films and candidate family require checking.

**Reviewer 来源归属 → 信息需求**

Reviewer 用满 4096 个输出 token，全部为 reasoning，正文为空；不存在可评的交付审查。结构失败保留计划分母，语义轴不适用，不把缺失当成来源推理错误。

```json
null
```

**Actor 完整响应 → 仍未知内容**

最后查询 Idris Elba The Constant Gardener role，核验未证实的候选—影片—角色绑定，方向可接受，历史尚未专门查过这条关系。但完整交付正文含大段无可见依据的出生、家庭、电影角色及片目断言，并先后肯定/否定 Idris 参演，还称 Wikipedia says 而无相应观察。局部自我质疑不能把全部先前断言都变成有据假设。“policeman因为investigates”等被提出为可能解释但未作为最终替代答案；按最终取证方向仍保留原题任务，不据此忽略正文错误。

交付正文：
```text
The searches aren't yielding a direct hit. Let's rethink the clues.

Clue 1: Born in the 1970s, father soldier, mother worked at barrack's hospital. Chinese zodiac = Goat.
Goat years: 1967, 1979, 1991, 2003. Wait, what about 1975?
Actually, 1975 is the Year of the Rabbit (Wood Rabbit).
Let's check: 1972 (Rat), 1973 (Ox), 1974 (Tiger), 1975 (Rabbit), 1976 (Dragon), 1977 (Snake), 1978 (Horse), 1979 (Goat).
So the person was born in **1979**.
If born in 1979, the zodiac is Goat.

Let's look for actors born in 1979 whose father was a soldier and mother worked at a barrack's hospital.
Actors born in 1979:
*   **Chris Pratt** (June 21, 1979) - Father was a miner/house remodeler.
*   **James McAvoy** (April 21, 1979) - Father was a psychiatric nurse. Mother was a nurse.
*   **John Krasinski** (Oct 20, 1979) - Father was an internist.
*   **Natalie Portman** (June 9, 1981) - No.
*   **Olivia Wilde** (March 10, 1984) - No.
*   **Rosamund Pike** (Jan 27, 1979) - Parents were musicians.
*   **Maggie Gyllenhaal** (1977).
*   **Rose Byrne** (1979) - Parents were statisticians.
*   **Aaron Paul** (1979) - Father was a Baptist minister.
*   **Lee Pace** (1979) - Father was an engineer.
*   **Adam Brody** (1979).
*   **Matt Bomer** (1977).
*   **Michael Fassbender** (1977).
*   **Tom Hardy** (1977) - Father was an author/comedian.
*   **Ryan Reynolds** (1976).
*   **Benedict Cumberbatch** (1976).
*   **Idris Elba** (1972? Wait, Idris Elba was born Sept 6, 1972? No, Sept 6, 1972? No, Sept 6, 1972 is wrong. Idris Elba was born September 6, 1972. Wait, let me check. Some sources say 1972, some say 1973.
Actually, Idris Elba was born September 6, 1972. 1972 is the Year of the Rat.
Wait, Wikipedia says: "Idrissa Akuna Elba OBE (/ˈɪdrɪs/; born 6 September 1972)". Wait, is it 1972 or 1973?
Most sources say 1972.
Wait, let's verify. Born 6 September 1972? Or 1973?
Some sources say 1972. Some say 1973.
If 1972, zodiac is Rat. If 1973, zodiac is Ox.
Neither is Goat.

Let's look at actors born in **1979**.
Who played a policeman in a 2005 film directed by Fernando Meirelles?
Cast of *The Constant Gardener* (2005):
*   Ralph Fiene (1962)
*   Rachel Weisz (1970)
*   Idris Elba (1972)
*   Danny Huston (1962)
*   Hubert Koundé (1955)
*   Bill Nighy (1949)
*   Tom Hollander (1967)
*   Paul Bettany (1971)
*   Mark Strong (1963)
*   **Pete Postlethwaite** (1946)
*   **John Sibi-Okumu** (1946)

None of these are born in 1979.

Let's reconsider the **2005 Film**.
Maybe the film is not *The Constant Gardener*.
Did Fernando Meirelles direct another film in 2005?
He directed **"Blindness"** (2008).
He directed **"The Two Popes"** (2019).
He directed **"360"** (2011).
He directed **"Maids"** (2001).
He directed **"City of God"** (2002).
He directed **"Dom"** (2003/2004)?
He directed a segment in **"Paris, je t'aime"** (2006).
He directed **"Lixo Extraordinário"** (2010)?

Wait, maybe the 2005 film is **"The Constant Gardener"** but the actor is someone else.
Or maybe the director of the 2005 film is NOT Fernando Meirelles.
Could someone else have been inspired by *Iracema*?
Maybe **Walter Salles**? He directed *The Motorcycle Diaries* (2004).
Maybe **José Padilha**? He directed *Elite Squad* (2007).
Maybe **Fernando Meirelles** is correct.

Let's re-read the 2005 film clue carefully: "acted as a policeman in a 2005 film directed by someone who decided to become a filmmaker after watching Iracema."
Maybe the actor is **John Krasinski**? No.
Maybe the actor is **James McAvoy**? In 2005, he was in *The Chronicles of Narnia* (Mr. Tumnus), *Becoming Jane* (2007).
Maybe the actor is **Chris Pratt**? In 2005, he was in TV.
Maybe the actor is **Aaron Paul**? In 2005, he was in TV.

What about **"The Constant Gardener"**? Who plays a policeman?
Actually, no one is explicitly a "policeman".

Let's look at the **2013 dramatic thriller** clue again.
"Directed by someone best known for directing and writing the critically acclaimed Kinsey."
Bill Condon.
Did Bill Condon direct a 2013 film?
*The Fifth Estate* (2013).
*Gods Behaving Badly* (2013).
Neither fits "actor born 1979, father soldier, mother barrack hospital worker".

Wait! Could the "2013 dramatic thriller" be **"The Fifth Estate"** and the actor be someone in it?
Who in *The Fifth Estate* was born in 1979?
Let's check the cast:
Benedict Cumberbatch (1976)
Daniel Brühl (1978)
Carice van Houten (1976)
David Thewlis (1963)
Alicia Vikander (1988)
Stanley Tucci (1960)
Brian Cox (1946)
Anthony Mackie (1978) - Wait, Anthony Mackie was in *The Fifth Estate*? No, he wasn't.
Actually, Anthony Mackie was in *The Fifth Estate*? No.
Let's check the full cast of *The Fifth Estate*.
Benedict Cumberbatch, Daniel Brühl, Carice van Houten, David Thewlis, Alicia Vikander, Stanley Tucci, Brian Cox, **Moritz Bleibtreu** (1971), **Alexander Beyer** (1973), **Anatole Taubman** (1970), **Peter Mensah** (1959).

No one born in 1979.

Maybe the 2013 film is **"Gods Behaving Badly"**? It's a comedy.
Cast: Gugu Mbatha-Raw (1983), Alison Pill (1985), John Benjamin Hickey (1963), Christopher Walken (1943), Sharon Stone (1958), Oliver Platt (1960).

Is it possible the director of *Kinsey* is someone else?
No.

Let's reconsider the **2013 Dramatic Thriller**.
Maybe it's **"Side Effects"** (2013) directed by Steven Soderbergh. Was Soderbergh known for *Kinsey*? No.
Maybe it's **"Prisoners"** (2013) directed by Denis Villeneuve. Known for *Incendies*, not *Kinsey*.
Maybe it's **"The Butler"** (2013) directed by Lee Daniels. Known for *Precious*.
Maybe it's **"The Wolf of Wall Street"** (2013)? Martin Scorsese.
Maybe it's **"Blue Jasmine"** (2013)? Woody Allen.
Maybe it's **"The Iceman"** (2012)?
Maybe it's **"The Place Beyond the Pines"** (2012)?

Wait, what if the director is **Bill Condon** and the film is **"The Fifth Estate"**, but the "dramatic thriller" description is just how the user describes it. And the actor is someone in it.
Who in *The Fifth Estate* has a father who was a soldier and a mother who worked at a barrack's hospital?
**Carice van Houten**? Mother was a nurse? No, her mother was a nurse? Actually, her mother was a nurse, but her father was a photographer.
**Daniel Brühl**? Father was an actor/director.
**Benedict Cumberbatch**? Parents were actors.
**David Thewlis**? Parents were shopkeepers.
**Stanley Tucci**? Parents were art teachers/writers.
**Brian Cox**? Father was a shopkeeper, mother was a spinner.
**Anatole Taubman**? Father was a doctor.
**Alexander Beyer**? No.
**Moritz Bleibtreu**? Parents were actors.

None fit.

Let's reconsider the **2005 Film**.
"Acted as a policeman in a 2005 film directed by [Fernando Meirelles]."
Is it possible the film is NOT *The Constant Gardener*?
Meirelles directed a segment for **"Paris, je t'aime"** (2006).
He directed **"8"** (2008)?
He directed **"Blindness"** (2008).

What if the director is NOT Fernando Meirelles?
Who else was inspired by *Iracema*?
Maybe **Walter Salles**? He directed *The Motorcycle Diaries* (2004), *Dark Water* (2005).
In *Dark Water* (2005), does someone play a policeman?
Cast of *Dark Water*: Jennifer Connelly, Tim Roth, John C. Reilly, Pete Postlethwaite, Dougray Scott, Camryn Manheim, Ariel Gade.
Was Walter Salles inspired by *Iracema*? Unlikely.

What if the director is **José Padilha**?
What if the director is **Fernando Meirelles** and the film is *The Constant Gardener*, and the actor is **Idris Elba** (born 1972, Rat).
The prompt says "Chinese zodiac sign is a goat". This is a strong constraint.

Let's search for actors born in 1979 who played a policeman in 2005.
Actually, let's look at the 2005 film **"Ladder 49"**? No, that's 2004.
2005 films with policemen:
*   **"The Constant Gardener"**
*   **"The Departed"** (2006)
*   **"Lucky Number Slevin"** (2006)
*   **"Dirty Harry"**?
*   **"Four Brothers"** (2005) - Mark Wahlberg plays a soldier? No.
*   **"The Island"** (2005) - Djimon Hounsou plays a mercenary.
*   **"War of the Worlds"** (2005)?
*   **"Batman Begins"** (2005)?
*   **"King Kong"** (2005)?
*   **"Pride & Prejudice"** (2005)?
*   **"Mr. & Mrs. Smith"** (2005)?
*   **"Sin City"** (2005)?
*   **"Star Wars: Episode III"** (2005)?
*   **"The Exorcism of Emily Rose"** (2005)?

Wait, let's look at **"The Constant Gardener"** again.
Idris Elba plays Tobias. He is not a policeman.
But maybe the user considers him a "policeman" because he investigates?
Or maybe the actor is **Paul Bettany**? He plays Justin Quayle's cousin? No, he plays **Tomas**? No, he plays **Justin's cousin**?
Actually, Paul Bettany plays **Tomas**, a diplomat? No, Paul Bettany plays **Tomas** in *The Da Vinci Code* (2006).
In *The Constant Gardener*, Paul Bettany plays **Tomas**? No.
Let's get the cast of *The Constant Gardener* right.
Ralph Fiene = Justin Quayle (diplomat)
Rachel Weisz = Tessa Quayle (activist)
Hubert Koundé = Dr. Arnold Bluhm
Danny Huston = Sandy Woodrow
Bill Nighy = Sir Bernard Pellegrin
Tom Hollander = Marcus Lorbeer
Richard McCabe = Tim Donohue
John Sibi-Okumu = Joshua Ngaba
Idris Elba = **Tobias**
Pete Postlethwaite = Marcus Lorbeer? No, that's Tom Hollander.

Wait, Idris Elba is NOT in *The Constant Gardener*!
I'm confusing it with something else.
Idris Elba was in **"The Constant Gardener"**? Let me check.
No! Idris Elba was NOT in *The Constant Gardener*.
Wait, who did Idris Elba play?
I'm thinking of **"The Constant Gardener"**... no.
Idris Elba was in **"Sometimes in April"** (2005).
He was in **"The Gospel"** (2005).
He was in **"Seven Seconds"**? No.
He was in **"Daddy's Little Girls"** (2007).
He was in **"28 Weeks Later"** (2007).
He was in **"This Christmas"** (2007).
He was in **"American Gangster"** (2007).
He was in **"RocknRolla"** (2008).

Wait, so Idris Elba was NOT in *The Constant Gardener*.
Who was the African actor in *The Constant Gardener*?
**Hubert Koundé** played Dr. Bluhm.
**John Sibi-Okumu** played Joshua Ngaba.

Let's reconsider the 2005 film directed by Fernando Meirelles.
It MUST be *The Constant Gardener*.
Who in *The Constant Gardener* played a policeman?
Maybe **Bill Nighy**? He plays Sir Bernard Pellegrin, a Foreign Office official.
Maybe **Ralph Fiene**? A diplomat.
Maybe **Danny Huston**? A diplomat.

Is there a policeman in *The Constant Gardener*?
There is a **Chief Inspector**? Or a **Police Commissioner**?
Actually, there is a character named **Police Chief**? Or **Sergeant**?
Let's search for the cast of *The Constant Gardener* to see if anyone is a policeman.
Actually, the prompt might be slightly wrong about "policeman".
Or maybe the 2005 film is NOT *The Constant Gardener*.

Let's re-read the 2005 clue: "acted as a policeman in a 2005 film directed by someone who decided to become a filmmaker after watching Iracema."
Maybe the director is **Fernando Meirelles**, and the film is *The Constant Gardener*, and the actor is **Idris Elba**?
Wait, I need to verify if Idris Elba was in *The Constant Gardener*.
Search: "Idris Elba The Constant Gardener".
```

提出但未执行的全部工具：
```json
[
  {
    "arguments": "{\"query\": \"Idris Elba The Constant Gardener role\"}",
    "name": "search"
  }
]
```

证据界限：尚无同一演员的出生/生肖、父母、2005 警察角色和 2013 影片关系链。

| 评价轴 | 标签 |
|---|---|
| `review_source_attribution_correct` | not_applicable |
| `tool_action_direction_acceptable` | yes |
| `assistant_assertions_supported` | no |
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
| `new_errors` | yes |
| `answer_vs_abstention` | no_final_text |

配对比较：同期C0不对自身作退化判断。

引用定位见同卡 `reference_index`；逐轴依据见 [annotations_final.jsonl](review/annotations_final.jsonl)。

## qid_517_s21 / r1 / C1 (card_0003)

[原始记录](branches/qid_517_s21__C__r1__source_grounded_v1/result.json) · [事件日志](branches/qid_517_s21__C__r1__source_grounded_v1/events.jsonl)

Reviewer=`node_invalid`；memo_injected=False；Actor=tool_calls。已报告 token 下界 40,969，调用耗时合计 77.664 秒；未知成本另见原始记录和机械汇总。

**原题限定及事前允许的下一动作**

Born1970s/goat; father soldier, mother barracks hospital; policeman2005 film/director inspired by Iracema; same actor2013 thriller/director of Kinsey; as-ofDec2023.

Check policeman cast in2005 film; connect to2013 thriller cast; investigate family with broad1970s, not unsupported1975. Directors locally grounded, films and candidate family require checking.

**Reviewer 来源归属 → 信息需求**

Reviewer 用满 4096 个输出 token，全部为 reasoning，正文为空；不存在可评的交付审查。结构失败保留计划分母，语义轴不适用，不把缺失当成来源推理错误。

```json
null
```

**Actor 完整响应 → 仍未知内容**

用 actor / barracks hospital / mother father soldier 回到原题稀有关系，移除1975与Idris硬过滤；合理的候选发现入口。不是把职业或生肖条件悄悄改掉，查询无需同时包含所有限定。没有执行Search或建立身份链。

交付正文：
```text
(empty)
```

提出但未执行的全部工具：
```json
[
  {
    "arguments": "{\"query\": \"actor \\\"barracks hospital\\\" mother father soldier\"}",
    "name": "search"
  }
]
```

证据界限：尚无同一演员的出生/生肖、父母、2005 警察角色和 2013 影片关系链。

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

配对比较：按完整响应标签，本批C1没有比配对C0更差。双方都无备忘回退，实际Actor请求相同；行为差异不能归因于来源合同。

引用定位见同卡 `reference_index`；逐轴依据见 [annotations_final.jsonl](review/annotations_final.jsonl)。

## qid_517_s21 / r2 / C0 (card_0001)

[原始记录](branches/qid_517_s21__C__r2__baseline/result.json) · [事件日志](branches/qid_517_s21__C__r2__baseline/events.jsonl)

Reviewer=`node_invalid`；memo_injected=False；Actor=tool_calls。已报告 token 下界 40,229，调用耗时合计 64.814 秒；未知成本另见原始记录和机械汇总。

**原题限定及事前允许的下一动作**

Born1970s/goat; father soldier, mother barracks hospital; policeman2005 film/director inspired by Iracema; same actor2013 thriller/director of Kinsey; as-ofDec2023.

Check policeman cast in2005 film; connect to2013 thriller cast; investigate family with broad1970s, not unsupported1975. Directors locally grounded, films and candidate family require checking.

**Reviewer 来源归属 → 信息需求**

Reviewer 用满 4096 个输出 token，全部为 reasoning，正文为空；不存在可评的交付审查。结构失败保留计划分母，语义轴不适用，不把缺失当成来源推理错误。

```json
null
```

**Actor 完整响应 → 仍未知内容**

再次查 Idris father soldier，与历史 m8 的 Idris father soldier mother nurse 同一路线，移除母亲条件没有提出新的判别关系。交付正文还把多位演员的出生、父母和具体片目/角色写成事实；例如 Constant Gardener 的角色名单及“Some sources say”家庭说法没有可见工具支持。后文的不确定语气和最终查询不能撤销前文断言。并未给终答或正式采用放宽后的题目，主要失败是旧路线及无据正文。

交付正文：
```text
The generic searches aren't working. Let's use the strongest constraint: **"2013 dramatic thriller directed by Bill Condon"**.
Wait, I should double-check Bill Condon's filmography. Is there any other film?
What if the director is not Bill Condon?
"Directed by someone best known for directing and writing the critically acclaimed Kinsey."
This is definitely Bill Condon.
Bill Condon directed:
*   Sister, Sister (1987)
*   Murder 101 (1991)
*   Candyman: Farewell to the Flesh (1995)
*   Gods and Monsters (1998)
*   Kinsey (2004)
*   Dreamgirls (2006)
*   Twilight: Breaking Dawn – Part 1 (2011)
*   Twilight: Breaking Dawn – Part 2 (2012)
*   **The Fifth Estate (2013)**
*   Mr. Holmes (2015)

So the 2013 film is **The Fifth Estate**.
Who acted in *The Fifth Estate*?
Benedict Cumberbatch, Daniel Brühl, Carice van Houten, Alicia Vikander, Stanley Tucci, David Thewlis, Brian Cox, Anthony Mackie.

Let's check **Anthony Mackie**:
*   Born 1978 (Horse? 1978 is Horse).
*   Father was a carpenter.

Let's check **Carice van Houten**:
*   Born 1976 (Dragon).

Let's check **Benedict Cumberbatch**:
*   Born 1976 (Dragon).

None fit.

Is it possible the question refers to a **2013 film** that is a "dramatic thriller" but NOT *The Fifth Estate*?
Could Bill Condon have directed an episode of a TV show in 2013? No.
Could the film be **"Gods Behaving Badly"**? It's a comedy.

Let's reconsider the **2005 film**.
"Acted as a policeman in a 2005 film directed by someone who decided to become a filmmaker after watching Iracema."
Fernando Meirelles.
2005 film: *The Constant Gardener*.
Who acted as a policeman in *The Constant Gardener*?
Actually, let's look at the cast list for *The Constant Gardener*.
Ralph Fiene (Justin Quayle)
Rachel Weisz (Tessa Quayle)
Hubert Koundé (Dr. Arnold Bluhm)
Danny Huston (Tedmond Arundel)
**Idris Elba (Tobias)**
Bill Nighy (Sir Bernard Pellegrin)
Tom Hollander (Justin's friend)
Paul Bettany (Justin's friend)
Mark Strong (Justin's friend)

Maybe **Idris Elba** IS the answer, and the "2013 dramatic thriller directed by Bill Condon" clue is wrong or I'm missing something.
Did Idris Elba star in a 2013 thriller?
Idris Elba starred in:
*   **Pacific Rim** (2013) - Sci-Fi action.
*   **Mandela: Long Walk to Freedom** (2013) - Biographical drama.
*   **Thor: The Dark World** (2013) - Fantasy action.
*   **No Good Deed** (2014) - Thriller.
*   **The Gunman** (2015) - Action thriller.
*   **Beasts of No Nation** (2015).

None of these are directed by Bill Condon.

Let's re-read the first clue very carefully.
"born sometime in the 1970s to a father who was a soldier and a mother who worked at the barrack's hospital"
This is a very specific biographical detail.
Could this be **Chiwetel Ejiofor**?
Born 1977 (Snake).
Father: Arinze Ejiofor, a doctor? Actually, his father was a pharmacist? No, his father was a doctor? His parents were Nigerian immigrants. His father was a doctor? No, his father was a "pharmacist"? Actually, his father was a doctor and his mother was a pharmacist? Let me check.
Actually, Chiwetel Ejiofor's father was a doctor? No, his father was a **musician**? No.
Wikipedia: "His parents, Arinze and Obiajulu Ejiofor, were Nigerian Igbo... His father was a pharmacist and his mother was a doctor." Wait, I'm not sure.

Let's check **David Oyelowo**:
Born 1976 (Dragon).
Father worked for an airline.

Let's check **John Boyega**:
Born 1992.

Let's check **Idris Elba** again.
Is it possible Idris Elba's father was a soldier?
Some sources say: "His father, George, was a nurse from Sierra Leone, and his mother, Irene, was a health advisor from Ghana."
However, there might be a source saying his father was a soldier. Let's search specifically for "Idris Elba" "soldier" father.
```

提出但未执行的全部工具：
```json
[
  {
    "arguments": "{\"query\": \"Idris Elba \\\"father\\\" \\\"soldier\\\"\"}",
    "name": "search"
  }
]
```

证据界限：尚无同一演员的出生/生肖、父母、2005 警察角色和 2013 影片关系链。

| 评价轴 | 标签 |
|---|---|
| `review_source_attribution_correct` | not_applicable |
| `tool_action_direction_acceptable` | no |
| `assistant_assertions_supported` | no |
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
| `new_errors` | yes |
| `answer_vs_abstention` | no_final_text |

配对比较：同期C0不对自身作退化判断。

引用定位见同卡 `reference_index`；逐轴依据见 [annotations_final.jsonl](review/annotations_final.jsonl)。

## qid_517_s21 / r2 / C1 (card_0002)

[原始记录](branches/qid_517_s21__C__r2__source_grounded_v1/result.json) · [事件日志](branches/qid_517_s21__C__r2__source_grounded_v1/events.jsonl)

Reviewer=`node_invalid`；memo_injected=False；Actor=tool_calls。已报告 token 下界 40,750，调用耗时合计 82.157 秒；未知成本另见原始记录和机械汇总。

**原题限定及事前允许的下一动作**

Born1970s/goat; father soldier, mother barracks hospital; policeman2005 film/director inspired by Iracema; same actor2013 thriller/director of Kinsey; as-ofDec2023.

Check policeman cast in2005 film; connect to2013 thriller cast; investigate family with broad1970s, not unsupported1975. Directors locally grounded, films and candidate family require checking.

**Reviewer 来源归属 → 信息需求**

Reviewer 用满 4096 个输出 token，全部为 reasoning，正文为空；不存在可评的交付审查。结构失败保留计划分母，语义轴不适用，不把缺失当成来源推理错误。

```json
null
```

**Actor 完整响应 → 仍未知内容**

针对当前未验证候选 Idris 查 barrack OR soldier / father mother。barrack 是原题稀有线索，历史 Idris 查询只有 soldier/mother nurse；可视为验证家庭绑定的新细化，不等于认定候选正确。无正文断言。OR 可能退回原有宽查询，因此这是较弱通过，未执行工具，不能声称获得新证据。

交付正文：
```text
(empty)
```

提出但未执行的全部工具：
```json
[
  {
    "arguments": "{\"query\": \"\\\"Idris Elba\\\" \\\"barrack\\\" OR \\\"soldier\\\" father mother\"}",
    "name": "search"
  }
]
```

证据界限：尚无同一演员的出生/生肖、父母、2005 警察角色和 2013 影片关系链。

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

配对比较：按完整响应标签，本批C1没有比配对C0更差。双方都无备忘回退，实际Actor请求相同；行为差异不能归因于来源合同。

引用定位见同卡 `reference_index`；逐轴依据见 [annotations_final.jsonl](review/annotations_final.jsonl)。

## qid_546_s29 / r1 / C0 (card_0009)

[原始记录](branches/qid_546_s29__C__r1__baseline/result.json) · [事件日志](branches/qid_546_s29__C__r1__baseline/events.jsonl)

Reviewer=`api_error`；memo_injected=False；Actor=tool_calls。已报告 token 下界 22,581，调用耗时合计 149.276 秒；未知成本另见原始记录和机械汇总。

**原题限定及事前允许的下一动作**

As of 2025-01-30: >300 centuries, highest break >3 times; pro 1995–2006; 2023 decider against <250 centuries, then two further wins 4–3 and 4–0, then loss to >400 centuries. Do not bind unnamed tournament by assumption.

Check 2023 match sequence at tournament/round level, or read already seen relevant match source beyond current window using available get_document; treat Selby/Players as unproven binding. Keep candidate if only event binding fails.

**Reviewer 来源归属 → 信息需求**

Reviewer API 超时，没有收到审查正文或 usage，成本未知；不从其他分支或 reasoning 补造来源/需求判断。

```json
null
```

**Actor 完整响应 → 仍未知内容**

继续 Players Championship bracket + Selby/Trump，与旧多轮事件绑定一致；bracket措辞不是上游关系修订。正文仅说明意图，方向失败不等于新增事实幻觉。

交付正文：
```text
Let's search specifically for the 2023 Players Championship bracket.
```

提出但未执行的全部工具：
```json
[
  {
    "arguments": "{\"query\": \"2023 Players Championship snooker draw bracket Selby Trump\"}",
    "name": "search"
  }
]
```

证据界限：尚无题目要求的完整赛事、对手、比分及 as-of 统计链。

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
| `regression` | not_applicable |
| `new_errors` | no |
| `answer_vs_abstention` | no_final_text |

配对比较：同期C0不对自身作退化判断。

引用定位见同卡 `reference_index`；逐轴依据见 [annotations_final.jsonl](review/annotations_final.jsonl)。

## qid_546_s29 / r1 / C1 (card_0004)

[原始记录](branches/qid_546_s29__C__r1__source_grounded_v1/result.json) · [事件日志](branches/qid_546_s29__C__r1__source_grounded_v1/events.jsonl)

Reviewer=`ok`；memo_injected=True；Actor=None。已报告 token 下界 28,611，调用耗时合计 155.487 秒；未知成本另见原始记录和机械汇总。

**原题限定及事前允许的下一动作**

As of 2025-01-30: >300 centuries, highest break >3 times; pro 1995–2006; 2023 decider against <250 centuries, then two further wins 4–3 and 4–0, then loss to >400 centuries. Do not bind unnamed tournament by assumption.

Check 2023 match sequence at tournament/round level, or read already seen relevant match source beyond current window using available get_document; treat Selby/Players as unproven binding. Keep candidate if only event binding fails.

**Reviewer 来源归属 → 信息需求**

引用 event:28:doc:55516 的可见 1600 字符窗口确有 professional 1999–present、>800 centuries、six maximums。审查只把这些归于来源，没有把题目比分链或早先 assistant 的 Players 赛制判断升级为观察。历史 m10/m12/m14 确实围绕 Selby×Players，故未建立的候选绑定是实际路线前提。需求完整保留 decider 后另两胜 4–3、4–0 和对手门槛，不预设赛事；此前工具没有回答完整链。作用允许支持 Selby、换符合条件者或重新理解关系，明确检索失败不等于反证。未声称可见当下统计已证明 2025-01-30 的全部门槛；日期、候选其他资格仍须后续核查。仅这一条可评语义审查，不能外推来源准确率。

```json
{"current_assumption":"The route treats Mark Selby as the likely target even though the visible sources establish only his 1999 professional debut, more than 800 career centuries, and six official maximum breaks—not the decisive 2023 match sequence.","next_need":"Which player’s 2023 match record contains a deciding-frame win over an opponent with fewer than 250 centuries, followed by 4-3 and 4-0 wins, and then a loss to an opponent with more than 400 centuries?","decision_effect":"Finding that exact sequence for Selby would support him as the answer; finding it for another eligible player would change the candidate; finding no exact sequence would require revisiting the meaning of “decider game” before concluding. A retrieval failure alone would not refute Selby.","basis_refs":["question","event:28:doc:55516"]}
```

**Actor 完整响应 → 仍未知内容**

唯一有效 Reviewer 已注入，但 Actor 在120秒设置下超时，没有收到内容或工具。无法判断是否理解需求、保持限定或采取合理动作。它保留在12个计划分支中，不能作为无语义错误的成功，也不能补造一个语义失败答案。

Actor API 失败，未收到响应；不能补造工具方向或终答，也不能判断需求实际被使用。

证据界限：尚无题目要求的完整赛事、对手、比分及 as-of 统计链。

| 评价轴 | 标签 |
|---|---|
| `review_source_attribution_correct` | yes |
| `tool_action_direction_acceptable` | not_applicable |
| `assistant_assertions_supported` | not_applicable |
| `final_answer_supported` | not_applicable |
| `assumption_grounded` | yes |
| `need_unresolved` | yes |
| `need_decision_relevant` | yes |
| `need_already_answered` | no |
| `decision_effect_balanced` | yes |
| `action_responds_to_need` | unknown |
| `original_constraint_preserved` | unknown |
| `action_acceptable` | unknown |
| `regression` | unknown |
| `new_errors` | unknown |
| `answer_vs_abstention` | unknown |

配对比较：C1 Actor超时，不能比较语义动作好坏；运行可靠性失败另行保留。C1有memo、C0无memo，无法补造反事实动作。

引用定位见同卡 `reference_index`；逐轴依据见 [annotations_final.jsonl](review/annotations_final.jsonl)。

## qid_546_s29 / r2 / C0 (card_0012)

[原始记录](branches/qid_546_s29__C__r2__baseline/result.json) · [事件日志](branches/qid_546_s29__C__r2__baseline/events.jsonl)

Reviewer=`node_invalid`；memo_injected=False；Actor=tool_calls。已报告 token 下界 53,488，调用耗时合计 99.834 秒；未知成本另见原始记录和机械汇总。

**原题限定及事前允许的下一动作**

As of 2025-01-30: >300 centuries, highest break >3 times; pro 1995–2006; 2023 decider against <250 centuries, then two further wins 4–3 and 4–0, then loss to >400 centuries. Do not bind unnamed tournament by assumption.

Check 2023 match sequence at tournament/round level, or read already seen relevant match source beyond current window using available get_document; treat Selby/Players as unproven binding. Keep candidate if only event binding fails.

**Reviewer 来源归属 → 信息需求**

Reviewer 用满 4096 个输出 token，全部为 reasoning，正文为空；不存在可评的交付审查。结构失败保留计划分母，语义轴不适用，不把缺失当成来源推理错误。

```json
null
```

**Actor 完整响应 → 仍未知内容**

查询 Stuart Bingham×2023 Championship League×4-3/4-0，首次改动上游赛事而非继续固定 Players。作为检验另一赛事绑定的搜索假设，给予较弱通过；没有正文宣称新赛事或候选成立。可见 event:16:doc:10572 只讲2025及2024决赛3–0，既不能证明2023符合，也不能从此推出2023一定不符合。尚未检验decider、完整四场链、赛制和as-of资格；若评阅者要求先核实赛制再定向查询，该项可降为unknown/no，结论不依赖这一弱通过。

交付正文：
```text
(empty)
```

提出但未执行的全部工具：
```json
[
  {
    "arguments": "{\"query\": \"\\\"Stuart Bingham\\\" 2023 Championship League results 4-3 4-0\"}",
    "name": "search"
  }
]
```

证据界限：尚无题目要求的完整赛事、对手、比分及 as-of 统计链。

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

配对比较：同期C0不对自身作退化判断。

引用定位见同卡 `reference_index`；逐轴依据见 [annotations_final.jsonl](review/annotations_final.jsonl)。

## qid_546_s29 / r2 / C1 (card_0005)

[原始记录](branches/qid_546_s29__C__r2__source_grounded_v1/result.json) · [事件日志](branches/qid_546_s29__C__r2__source_grounded_v1/events.jsonl)

Reviewer=`node_invalid`；memo_injected=False；Actor=tool_calls。已报告 token 下界 53,765，调用耗时合计 57.978 秒；未知成本另见原始记录和机械汇总。

**原题限定及事前允许的下一动作**

As of 2025-01-30: >300 centuries, highest break >3 times; pro 1995–2006; 2023 decider against <250 centuries, then two further wins 4–3 and 4–0, then loss to >400 centuries. Do not bind unnamed tournament by assumption.

Check 2023 match sequence at tournament/round level, or read already seen relevant match source beyond current window using available get_document; treat Selby/Players as unproven binding. Keep candidate if only event binding fails.

**Reviewer 来源归属 → 信息需求**

Reviewer 用满 4096 个输出 token，全部为 reasoning，正文为空；不存在可评的交付审查。结构失败保留计划分母，语义轴不适用，不把缺失当成来源推理错误。

```json
null
```

**Actor 完整响应 → 仍未知内容**

仍查 Players Championship draw/results，列 Trump、Selby、Murphy；历史已反复走未验证的 Players 绑定，换 draw 或名单不修复赛事前提。正文只有检索意图，未产生新比赛事实；完整动作仍不合理。

交付正文：
```text
Let's look at the 2023 Players Championship draw directly.
```

提出但未执行的全部工具：
```json
[
  {
    "arguments": "{\"query\": \"2023 Players Championship snooker draw results Judd Trump Mark Selby Shaun Murphy\"}",
    "name": "search"
  }
]
```

证据界限：尚无题目要求的完整赛事、对手、比分及 as-of 统计链。

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
| `regression` | yes |
| `new_errors` | no |
| `answer_vs_abstention` | no_final_text |

配对比较：本批C1完整动作不合格，配对C0为较弱通过，因此本口径出现退化；C0若降级则不成立。双方都无备忘回退，实际Actor请求相同；行为差异不能归因于来源合同。

引用定位见同卡 `reference_index`；逐轴依据见 [annotations_final.jsonl](review/annotations_final.jsonl)。

## qid_776_s53 / r1 / C0 (card_0007)

[原始记录](branches/qid_776_s53__C__r1__baseline/result.json) · [事件日志](branches/qid_776_s53__C__r1__baseline/events.jsonl)

Reviewer=`node_invalid`；memo_injected=False；Actor=tool_calls。已报告 token 下界 75,056，调用耗时合计 57.566 秒；未知成本另见原始记录和机械汇总。

**原题限定及事前允许的下一动作**

Born1886; travel April–November1915, foreign-language slip mistaken for shaman; same house35years,3children; encouragement1936–1940; author England early1910s; report1940 in quarterly founded1888; exact official title.

Change investigative axis to official 1940 journal records or linked biography; query anecdote with a genuinely different entry, remove unsupported profession/exact birth1912. Potential journals must remain candidates. Do not repeat same exhausted query without a reason.

**Reviewer 来源归属 → 信息需求**

Reviewer 用满 4096 个输出 token，全部为 reasoning，正文为空；不存在可评的交付审查。结构失败保留计划分母，语义轴不适用，不把缺失当成来源推理错误。

```json
null
```

**Actor 完整响应 → 仍未知内容**

“mistaken for a shaman” 1915 foreign language 是历史 m2/m4 已试方向的近重复。没有职业过滤或新正文事实，但没有解释为何相同入口会解决当前停滞。

交付正文：
```text
Let's try searching for the specific phrase "mistaken for a shaman" and "1915" with "foreign language".
```

提出但未执行的全部工具：
```json
[
  {
    "arguments": "{\"query\": \"\\\"mistaken for a shaman\\\" 1915 foreign language\"}",
    "name": "search"
  }
]
```

证据界限：尚无人物—语言误用—作者—1940 报告官方题名的完整链。

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
| `regression` | not_applicable |
| `new_errors` | no |
| `answer_vs_abstention` | no_final_text |

配对比较：同期C0不对自身作退化判断。

引用定位见同卡 `reference_index`；逐轴依据见 [annotations_final.jsonl](review/annotations_final.jsonl)。

## qid_776_s53 / r1 / C1 (card_0006)

[原始记录](branches/qid_776_s53__C__r1__source_grounded_v1/result.json) · [事件日志](branches/qid_776_s53__C__r1__source_grounded_v1/events.jsonl)

Reviewer=`api_error`；memo_injected=False；Actor=tool_calls。已报告 token 下界 33,326，调用耗时合计 132.233 秒；未知成本另见原始记录和机械汇总。

**原题限定及事前允许的下一动作**

Born1886; travel April–November1915, foreign-language slip mistaken for shaman; same house35years,3children; encouragement1936–1940; author England early1910s; report1940 in quarterly founded1888; exact official title.

Change investigative axis to official 1940 journal records or linked biography; query anecdote with a genuinely different entry, remove unsupported profession/exact birth1912. Potential journals must remain candidates. Do not repeat same exhausted query without a reason.

**Reviewer 来源归属 → 信息需求**

Reviewer API 超时，没有收到审查正文或 usage，成本未知；不从其他分支或 reasoning 补造来源/需求判断。

```json
null
```

**Actor 完整响应 → 仍未知内容**

shaman 1915 “misuse of a word” 重复历史 m2/m20/m24 的相同事件入口，缺少新的判别关系或来源方向。去掉职业过滤是局部改善，但不能使重复检索成为本检查点的合理下一步。正文只有意图，未新增人物事实。

交付正文：
```text
Let's search for "shaman" "1915" "misuse of a word".
```

提出但未执行的全部工具：
```json
[
  {
    "arguments": "{\"query\": \"shaman 1915 \\\"misuse of a word\\\"\"}",
    "name": "search"
  }
]
```

证据界限：尚无人物—语言误用—作者—1940 报告官方题名的完整链。

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

配对比较：按完整响应标签，本批C1没有比配对C0更差。双方都无备忘回退，实际Actor请求相同；行为差异不能归因于来源合同。

引用定位见同卡 `reference_index`；逐轴依据见 [annotations_final.jsonl](review/annotations_final.jsonl)。

## qid_776_s53 / r2 / C0 (card_0010)

[原始记录](branches/qid_776_s53__C__r2__baseline/result.json) · [事件日志](branches/qid_776_s53__C__r2__baseline/events.jsonl)

Reviewer=`node_invalid`；memo_injected=False；Actor=tool_calls。已报告 token 下界 75,054，调用耗时合计 48.021 秒；未知成本另见原始记录和机械汇总。

**原题限定及事前允许的下一动作**

Born1886; travel April–November1915, foreign-language slip mistaken for shaman; same house35years,3children; encouragement1936–1940; author England early1910s; report1940 in quarterly founded1888; exact official title.

Change investigative axis to official 1940 journal records or linked biography; query anecdote with a genuinely different entry, remove unsupported profession/exact birth1912. Potential journals must remain candidates. Do not repeat same exhausted query without a reason.

**Reviewer 来源归属 → 信息需求**

Reviewer 用满 4096 个输出 token，全部为 reasoning，正文为空；不存在可评的交付审查。结构失败保留计划分母，语义轴不适用，不把缺失当成来源推理错误。

```json
null
```

**Actor 完整响应 → 仍未知内容**

工具查询 “lived in the same house” “35 years” anthropologist 与历史 m22 完全相同，且保留题目没有给出的职业过滤。正文提1886只是复述目标线索，不是某候选的事实证明；未新增该旧错误，但未纠正它。

交付正文：
```text
Let's try searching for the person who was born in 1886 and lived in the same house for 35 years.
```

提出但未执行的全部工具：
```json
[
  {
    "arguments": "{\"query\": \"\\\"lived in the same house\\\" \\\"35 years\\\" anthropologist\"}",
    "name": "search"
  }
]
```

证据界限：尚无人物—语言误用—作者—1940 报告官方题名的完整链。

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

配对比较：同期C0不对自身作退化判断。

引用定位见同卡 `reference_index`；逐轴依据见 [annotations_final.jsonl](review/annotations_final.jsonl)。

## qid_776_s53 / r2 / C1 (card_0011)

[原始记录](branches/qid_776_s53__C__r2__source_grounded_v1/result.json) · [事件日志](branches/qid_776_s53__C__r2__source_grounded_v1/events.jsonl)

Reviewer=`api_error`；memo_injected=False；Actor=tool_calls。已报告 token 下界 33,042，调用耗时合计 134.715 秒；未知成本另见原始记录和机械汇总。

**原题限定及事前允许的下一动作**

Born1886; travel April–November1915, foreign-language slip mistaken for shaman; same house35years,3children; encouragement1936–1940; author England early1910s; report1940 in quarterly founded1888; exact official title.

Change investigative axis to official 1940 journal records or linked biography; query anecdote with a genuinely different entry, remove unsupported profession/exact birth1912. Potential journals must remain candidates. Do not repeat same exhausted query without a reason.

**Reviewer 来源归属 → 信息需求**

Reviewer API 超时，没有收到审查正文或 usage，成本未知；不从其他分支或 reasoning 补造来源/需求判断。

```json
null
```

**Actor 完整响应 → 仍未知内容**

查询 encouraged / to write / report1940 改变了调查关系，值得与纯重复区分；但仍把未建立的 anthropologist 作为过滤，正文称查 journal 而实际参数没有期刊线索，无法视为完成撤回职业假设的合理入口。没有声称题名或人物已确认；新错误为no表示旧过滤延续，不表示动作合格。

交付正文：
```text
Let's try searching for "encouraged" "to write" "report" 1940 journal.
```

提出但未执行的全部工具：
```json
[
  {
    "arguments": "{\"query\": \"\\\"encouraged\\\" \\\"to write\\\" report 1940 anthropologist\"}",
    "name": "search"
  }
]
```

证据界限：尚无人物—语言误用—作者—1940 报告官方题名的完整链。

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
| `regression` | no |
| `new_errors` | no |
| `answer_vs_abstention` | no_final_text |

配对比较：按完整响应标签，本批C1没有比配对C0更差。双方都无备忘回退，实际Actor请求相同；行为差异不能归因于来源合同。

引用定位见同卡 `reference_index`；逐轴依据见 [annotations_final.jsonl](review/annotations_final.jsonl)。
