# 定位消融：关键案例

A 原方案；B_pool3 扩大父块候选；C_scores 保留数字对。

## 517 / search 5 / docid 67431

Peter King actor The Constant Gardener role policeman

### A / [0, 1299)

````text
---
title: Peter Nzioki - Wikipedia
date: 2020-11-06
---
name: Peter King Nzioki Mwania
birth_date: 25 May 1978
birth_name: Peter King Nzioki Mwania
birth_place: Kenya
nationality: Kenyan
height: 1.8 m
years_active: 2000–present
spouse: Tess King
occupation: Actor

Peter King Nzioki Mwania (born 25 May 1978), popularly known as Peter King, is a Kenyan actor. He is best known for his roles in the films The Constant Gardener, The Fifth Estate and Sense8.

Personal life

Nzioki was born on 25 May 1978 in Nairobi, Kenya. His father Michael David Mwania, served in the Kenyan Army and his mother worked at the military hospital. At the age of six, he joined church productions at the Lang'ata Barracks. He completed his education from Lang'ata High School in Nairobi.

He is married to fellow actress Tess King.

Career

He made acting debut in 2000 at the Kenya National Theatre for three years under the guidance of Joab Kanuka. In theater, he played 'Iago' in the Phoenix Players production of the Shakespeare tragedy Othello. In 2005, he made his film debut with a minor role in The Constant Gardener directed by Fernando Meirelles. In the same year, he appeared as 'Barman' in the television movie Transit. In 2016, he appeared in the thriller film The CEO where he played the role of 'Jomo'. 
````

### B_pool3 / [1299, 2601)

````text
The film had its premier 10 July 2016, at the Eko Hotels & Suites, Victoria Island, Lagos and later received critical acclaim.

He made some notable appearances as 'Mkwajo' in award-winning musical Mo Faya directed by Eric Wainaina; scheming spouse in FaceBook and corrupt politician 'Mzito' in Ni Sisi. After several villainous roles, he received the role as stepfather in MTV series Shuga 2, then as an inspiring soccer coach in The Inside Story aired in Discovery Channel; and a preacher in The Knife Grinder's Tale.

In 2016, he was selected for the role as Kenyan crime lord 'Silas Kabaka' in the Netflix series Sense8. The role made him a popular television actor in Kenya.

Filmography

**Table 1**

| Year | Film | Role | Genre | Ref. |
|---|---|---|---|---|
| 2005 | The Constant Gardener | Policeman 1 | Film | |
| 2005 | Transit | Barman | TV movie | |
| 2007 | The Knife Grinder's Tale | Preacher | Short film | |
| 2007 | Makutano Junction | Albert Mukara | TV series | |
| 2010 | Ndoto Za Elibidi | Policeman 1 | Film | |
| 2013 | The Fifth Estate | Oscar Kamau Kingara | Film | |
| 2016 | The CEO | Jomo | Film | |
| 2016 | Kati Kati | King | Film | |
| 2016 | Sense8 | Silas Kabaka | TV series | |
| 2018 | Poacher | Kennedy | Short film | |

See also

* List of Black Sails characters

````

定位诊断：

```json
{
  "parents": [
    {
      "start": 0,
      "end": 1427,
      "score": 5.872427623439152,
      "matches": [
        "actor",
        "constant",
        "gardener",
        "king",
        "peter",
        "role",
        "the"
      ]
    },
    {
      "start": 1426,
      "end": 2634,
      "score": 4.927818373092642,
      "matches": [
        "actor",
        "constant",
        "gardener",
        "king",
        "policeman",
        "role",
        "the"
      ]
    }
  ],
  "anchors": [
    {
      "start": 2066,
      "end": 2122,
      "text": "| 2005 | The Constant Gardener | Policeman 1 | Film | |\n",
      "score": 10.303215051580123,
      "matches": [
        "constant",
        "gardener",
        "policeman",
        "the"
      ]
    },
    {
      "start": 266,
      "end": 361,
      "text": "Peter King Nzioki Mwania (born 25 May 1978), popularly known as Peter King, is a Kenyan actor. ",
      "score": 6.668023386224563,
      "matches": [
        "actor",
        "king",
        "peter"
      ]
    },
    {
      "start": 57,
      "end": 88,
      "text": "name: Peter King Nzioki Mwania\n",
      "score": 5.511672787144935,
      "matches": [
        "king",
        "peter"
      ]
    }
  ]
}
```

### C_scores / [0, 1299)

````text
---
title: Peter Nzioki - Wikipedia
date: 2020-11-06
---
name: Peter King Nzioki Mwania
birth_date: 25 May 1978
birth_name: Peter King Nzioki Mwania
birth_place: Kenya
nationality: Kenyan
height: 1.8 m
years_active: 2000–present
spouse: Tess King
occupation: Actor

Peter King Nzioki Mwania (born 25 May 1978), popularly known as Peter King, is a Kenyan actor. He is best known for his roles in the films The Constant Gardener, The Fifth Estate and Sense8.

Personal life

Nzioki was born on 25 May 1978 in Nairobi, Kenya. His father Michael David Mwania, served in the Kenyan Army and his mother worked at the military hospital. At the age of six, he joined church productions at the Lang'ata Barracks. He completed his education from Lang'ata High School in Nairobi.

He is married to fellow actress Tess King.

Career

He made acting debut in 2000 at the Kenya National Theatre for three years under the guidance of Joab Kanuka. In theater, he played 'Iago' in the Phoenix Players production of the Shakespeare tragedy Othello. In 2005, he made his film debut with a minor role in The Constant Gardener directed by Fernando Meirelles. In the same year, he appeared as 'Barman' in the television movie Transit. In 2016, he appeared in the thriller film The CEO where he played the role of 'Jomo'. 
````

定位诊断：

```json
{
  "parents": [
    {
      "start": 0,
      "end": 1427,
      "score": 5.875614339075231,
      "matches": [
        "actor",
        "constant",
        "gardener",
        "king",
        "peter",
        "role",
        "the"
      ]
    }
  ],
  "anchors": [
    {
      "start": 266,
      "end": 361,
      "text": "Peter King Nzioki Mwania (born 25 May 1978), popularly known as Peter King, is a Kenyan actor. ",
      "score": 5.586232368700562,
      "matches": [
        "actor",
        "king",
        "peter"
      ]
    },
    {
      "start": 1031,
      "end": 1138,
      "text": "In 2005, he made his film debut with a minor role in The Constant Gardener directed by Fernando Meirelles. ",
      "score": 5.5456627951373765,
      "matches": [
        "constant",
        "gardener",
        "role",
        "the"
      ]
    },
    {
      "start": 361,
      "end": 457,
      "text": "He is best known for his roles in the films The Constant Gardener, The Fifth Estate and Sense8.\n",
      "score": 4.792979884211894,
      "matches": [
        "constant",
        "gardener",
        "the"
      ]
    }
  ]
}
```

## 546 / search 1 / docid 4975

snooker player decider game 2023 win 4-3 4-0 loss over 400 centuries

### A / [112237, 113090)

````text
| Winner | 19. | 2017 | Northern Ireland Open | | 9–8 | |
| Winner | 20. | 2018 | German Masters (2) | | 9–1 | |
| Winner | 21. | 2018 | | | 18–16 | |
| Winner | 22. | 2018 | World Open | | 10–9 | |
| Runner-up | 13. | 2019 | China Championship | | 9–10 | |
| Winner | 23. | 2021 | WST Pro Series | | | |
| Winner | 24. | 2021 | British Open (2) | | 6–4 | |
| Runner-up | 14. | 2022 | Snooker Shoot Out | | 0–1 | |
| Runner-up | 15. | 2023 | Championship League | | 0–3 | |
| Winner | 25. | 2023 | British Open (3) | | 10–7 | |
| Winner | 26. | 2024 | Tour Championship | | 10–5 | |
| Runner-up | 16. | 2024 | Saudi Arabia Snooker Masters | | 9–10 | |
| Runner-up | 17. | 2025 | World Snooker Championship (2) | | 12–18 | |

Minor-ranking finals: 3 (2 titles)

**Table 6**

| Outcome | No. | Year | Championship | Opponent in the final | Score | Ref. |

````

### B_pool3 / [112237, 113090)

````text
| Winner | 19. | 2017 | Northern Ireland Open | | 9–8 | |
| Winner | 20. | 2018 | German Masters (2) | | 9–1 | |
| Winner | 21. | 2018 | | | 18–16 | |
| Winner | 22. | 2018 | World Open | | 10–9 | |
| Runner-up | 13. | 2019 | China Championship | | 9–10 | |
| Winner | 23. | 2021 | WST Pro Series | | | |
| Winner | 24. | 2021 | British Open (2) | | 6–4 | |
| Runner-up | 14. | 2022 | Snooker Shoot Out | | 0–1 | |
| Runner-up | 15. | 2023 | Championship League | | 0–3 | |
| Winner | 25. | 2023 | British Open (3) | | 10–7 | |
| Winner | 26. | 2024 | Tour Championship | | 10–5 | |
| Runner-up | 16. | 2024 | Saudi Arabia Snooker Masters | | 9–10 | |
| Runner-up | 17. | 2025 | World Snooker Championship (2) | | 12–18 | |

Minor-ranking finals: 3 (2 titles)

**Table 6**

| Outcome | No. | Year | Championship | Opponent in the final | Score | Ref. |

````

定位诊断：

```json
{
  "parents": [
    {
      "start": 112652,
      "end": 113468,
      "score": 21.200010604984655,
      "matches": [
        "0",
        "2023",
        "3",
        "4",
        "snooker"
      ]
    },
    {
      "start": 116136,
      "end": 117204,
      "score": 17.09845026592904,
      "matches": [
        "0",
        "3",
        "4",
        "snooker"
      ]
    },
    {
      "start": 114186,
      "end": 115068,
      "score": 16.746873946696873,
      "matches": [
        "0",
        "2023",
        "3",
        "4"
      ]
    }
  ],
  "anchors": [
    {
      "start": 112652,
      "end": 112711,
      "text": "| Runner-up | 15. | 2023 | Championship League | | 0–3 | |\n",
      "score": 5.1005044522147305,
      "matches": [
        "0",
        "2023",
        "3"
      ]
    },
    {
      "start": 116556,
      "end": 116591,
      "text": "| Winner | 4. | 1991 | | | 4–0 | |\n",
      "score": 4.702535750215777,
      "matches": [
        "0",
        "4"
      ]
    },
    {
      "start": 113412,
      "end": 113437,
      "text": "| Premier League (0–3) |\n",
      "score": 3.7992421421470017,
      "matches": [
        "0",
        "3"
      ]
    }
  ]
}
```

### C_scores / [112595, 113547)

````text
| Runner-up | 14. | 2022 | Snooker Shoot Out | | 0–1 | |
| Runner-up | 15. | 2023 | Championship League | | 0–3 | |
| Winner | 25. | 2023 | British Open (3) | | 10–7 | |
| Winner | 26. | 2024 | Tour Championship | | 10–5 | |
| Runner-up | 16. | 2024 | Saudi Arabia Snooker Masters | | 9–10 | |
| Runner-up | 17. | 2025 | World Snooker Championship (2) | | 12–18 | |

Minor-ranking finals: 3 (2 titles)

**Table 6**

| Outcome | No. | Year | Championship | Opponent in the final | Score | Ref. |
|---|---|---|---|---|---|---|
| Winner | 1. | 2010 | Players Tour Championship – Event 1 | | 4–0 | |
| Winner | 2. | 2013 | Rotterdam Open | | 4–3 | |
| Runner-up | 1. | 2015 | Gdynia Open | | 0–4 | |

Non-ranking finals: 25 (10 titles)

**Table 7**

| Legend |
|---|
| The Masters (2–2) |
| Champion of Champions (1–0) |
| Premier League (0–3) |
| Other (7–10) |

**Table 8**

| Outcome | No. | Year | Championship | Opponent in the final | Score | Ref. |

````

定位诊断：

```json
{
  "parents": [
    {
      "start": 112652,
      "end": 113468,
      "score": 17.18511522372495,
      "matches": [
        "2023",
        "scorepair4x0",
        "scorepair4x3",
        "snooker"
      ]
    }
  ],
  "anchors": [
    {
      "start": 113191,
      "end": 113241,
      "text": "| Winner | 2. | 2013 | Rotterdam Open | | 4–3 | |\n",
      "score": 2.4164214865947913,
      "matches": [
        "scorepair4x3"
      ]
    },
    {
      "start": 113120,
      "end": 113191,
      "text": "| Winner | 1. | 2010 | Players Tour Championship – Event 1 | | 4–0 | |\n",
      "score": 1.9291842949521003,
      "matches": [
        "scorepair4x0"
      ]
    },
    {
      "start": 112652,
      "end": 112711,
      "text": "| Runner-up | 15. | 2023 | Championship League | | 0–3 | |\n",
      "score": 1.8048473612974545,
      "matches": [
        "2023"
      ]
    }
  ]
}
```

## 546 / search 1 / docid 38231

snooker player decider game 2023 win 4-3 4-0 loss over 400 centuries

### A / [22000, 23325)

````text
Ding made a 132 break to level the match and a 70 in the decider to progress with a score of 13–12. He played Ronnie O'Sullivan in the quarter-finals. Despite a career-record ten losses and two wins prior to the match, Ding won 13–10. In his semi-final with Mark Selby, Ding made two consecutive centuries to end the third session at 12–12. He won two frames from 16 to 13 down but missed a blue in the next frame and lost 15–17. Ding said his game would continue to improve as he had played with more confidence and aggression throughout the event. He ended the season ranked world number four.

World Cup win (2017/2018)

At the 2017 World Cup, Ding and China's number-two player, Liang Wenbo, defeated the English pair, Judd Trump and Barry Hawkins, in a deciding frame, winning the event 4–3. Ding led the Chinese team at the CVB Snooker Challenge, losing 9–26 to the British team. He lost 1–6 to the captain of the British team, Ronnie O'Sullivan. He then participated in the second China Championship but was defeated in a 5–0 whitewash to Alan McManus in the last 32 in a rematch of the semi-finals of the 2015 World Championship. As the defending Six-red World Champion, Ding lost 1–6 to Marco Fu in the last 16. Ding won the World Open, beating Luca Brecel 6–4 in the semi-finals and Kyren Wilson 10–3 in the final.

````

### B_pool3 / [20746, 22151)

````text
His end-of-season world ranking was nine.

First Six-red World Championship (2016/2017)

Ding won the 2016 Six-red World Championship, beating Stuart Bingham on the final black in the final by 8–7. Ding won his second Shanghai Masters title, defeating Mark Selby 10–6 in the final. It was the 12th ranking-tournament win of his career and he also became the first player to win the event twice. Ding defeated John Higgins 6–2 and Judd Trump 9–4 to reach the final of the International Championship, where he made a high break of 47 but Mark Selby won the last seven frames to beat him 10–1. In the semi-finals of the 2016 Champion of Champions, Ding made four centuries but was beaten 6–5 by Higgins. He lost 2–6 to Jamie Jones in the third round of the UK Championship. In the first round of the Players Championship, Ding recovered from being 0–4 down to Higgins to win 5–4. He then defeated Anthony Hamilton 5–2. Ding was 5–3 up against Marco Fu in the semi-finals but lost the match 5–6.

Ding was eliminated from the China Open in the quarter-finals after losing 1–5 to Kyren Wilson. At the World Championship, Ding beat Zhou Yuelong in the first round by 10–5 and, after leading 6–2 and 9–7, Liang Wenbo was leading Ding 13–11 in the second round. Ding made a 132 break to level the match and a 70 in the decider to progress with a score of 13–12. He played Ronnie O'Sullivan in the quarter-finals. 
````

定位诊断：

```json
{
  "parents": [
    {
      "start": 21738,
      "end": 22624,
      "score": 11.387595643478171,
      "matches": [
        "centuries",
        "decider",
        "game",
        "win"
      ]
    },
    {
      "start": 14295,
      "end": 15695,
      "score": 11.211927586609843,
      "matches": [
        "0",
        "3",
        "4",
        "game",
        "player",
        "snooker",
        "win"
      ]
    },
    {
      "start": 20788,
      "end": 21739,
      "score": 11.164125922417398,
      "matches": [
        "0",
        "3",
        "4",
        "centuries",
        "player",
        "win"
      ]
    }
  ],
  "anchors": [
    {
      "start": 21517,
      "end": 21623,
      "text": "In the first round of the Players Championship, Ding recovered from being 0–4 down to Higgins to win 5–4. ",
      "score": 6.805745853838245,
      "matches": [
        "0",
        "4",
        "win"
      ]
    },
    {
      "start": 21028,
      "end": 21141,
      "text": "It was the 12th ranking-tournament win of his career and he also became the first player to win the event twice. ",
      "score": 4.32097457741515,
      "matches": [
        "player",
        "win"
      ]
    },
    {
      "start": 14942,
      "end": 15162,
      "text": "Following that, Ding played in the first Indian Open, defeating Aditya Mehta 5–0 in the final to become the first player to win back-to-back major-ranking event titles in the same season since Ronnie O'Sullivan in 2003. ",
      "score": 4.312343033174345,
      "matches": [
        "0",
        "player",
        "win"
      ]
    }
  ]
}
```

### C_scores / [22000, 23325)

````text
Ding made a 132 break to level the match and a 70 in the decider to progress with a score of 13–12. He played Ronnie O'Sullivan in the quarter-finals. Despite a career-record ten losses and two wins prior to the match, Ding won 13–10. In his semi-final with Mark Selby, Ding made two consecutive centuries to end the third session at 12–12. He won two frames from 16 to 13 down but missed a blue in the next frame and lost 15–17. Ding said his game would continue to improve as he had played with more confidence and aggression throughout the event. He ended the season ranked world number four.

World Cup win (2017/2018)

At the 2017 World Cup, Ding and China's number-two player, Liang Wenbo, defeated the English pair, Judd Trump and Barry Hawkins, in a deciding frame, winning the event 4–3. Ding led the Chinese team at the CVB Snooker Challenge, losing 9–26 to the British team. He lost 1–6 to the captain of the British team, Ronnie O'Sullivan. He then participated in the second China Championship but was defeated in a 5–0 whitewash to Alan McManus in the last 32 in a rematch of the semi-finals of the 2015 World Championship. As the defending Six-red World Champion, Ding lost 1–6 to Marco Fu in the last 16. Ding won the World Open, beating Luca Brecel 6–4 in the semi-finals and Kyren Wilson 10–3 in the final.

````

定位诊断：

```json
{
  "parents": [
    {
      "start": 21738,
      "end": 22624,
      "score": 11.53114828067714,
      "matches": [
        "centuries",
        "decider",
        "game",
        "win"
      ]
    }
  ],
  "anchors": [
    {
      "start": 22597,
      "end": 22623,
      "text": "World Cup win (2017/2018)\n",
      "score": 2.9063568307431824,
      "matches": [
        "win"
      ]
    },
    {
      "start": 22235,
      "end": 22341,
      "text": "In his semi-final with Mark Selby, Ding made two consecutive centuries to end the third session at 12–12. ",
      "score": 1.8707206297430665,
      "matches": [
        "centuries"
      ]
    },
    {
      "start": 22430,
      "end": 22550,
      "text": "Ding said his game would continue to improve as he had played with more confidence and aggression throughout the event. ",
      "score": 1.8242879610511538,
      "matches": [
        "game"
      ]
    }
  ]
}
```

## 546 / search 2 / docid 55362

snooker player "decider" 2023 "4-3" "4-0" loss

### A / [696, 1782)

````text
Then in the evening, Gilbert and Milkins playing to a finish and Si Jiahui v Jak Jones playing the middle session of 3.

DRAWORDER OF PLAYFriday 26th of April 10amDavid Gilbert 5-3 Robert Milkins

Milkins leads 7-4Jak Jones v Si Jiahui

Jones leads 2-12.30pmStephen Maguire v Shaun Murphy

Tied at 14-14Judd Trump 6-2 Tom Ford

Trump leads 13-6 7pm**David Gilbert v Robert Milkins

Milkins leads 7-4Jak Jones v Si Jiahui

Jones leads 2-1** Denotes Final Session of a Match

-

Wildey

- Posts: 66177

- Joined: 02 October 2009

- Location: North Wales

- Snooker Idol: Mark Selby

- Highest Break: 25

- Walk-On: the one and only

by Andre147 » 25 Apr 2024 Read

Maguire v Murphy one of the ties of the round for sure, will keep an eye on that.

-

Andre147

- Posts: 42912

- Joined: 09 October 2011

- Snooker Idol: Ronnie and Luca

- Highest Break: 27

- Walk-On: Spies - Coldplay

by McManusFan » 25 Apr 2024 Read

Andre147 wrote:Maguire v Murphy one of the ties of the round for sure, will keep an eye on that.

Yes, that looks like a tasty one. They both seem to be playing well.

````

### B_pool3 / [7214, 8299)

````text
2021 =39

2020 =38

Good. The bags certainly aren't the buckets they have been in recent years.

POCKETS!

-

McManusFan

- Posts: 9219

- Joined: 03 October 2018

- Snooker Idol: Alan McManus

- Highest Break: 8

by Pedro147 » 26 Apr 2024 Read

Wilson v O'Connor has all the hallmarks of an absolute stinker of a match. Could go close and that will be the only way excitement is created. Expecting 25+ seconds ASTs for both players.

Looking forward to Bingham v Lisowski and Maguire v Murphy.

-

Pedro147

- Posts: 530

- Joined: 14 January 2015

by Dan-cat » 26 Apr 2024 Read

Prop wrote:Wildey wrote:1st Round Centuries

2024 =25

2023 =39

2022 =44

2021 =39

2020 =38

Good. The bags certainly aren't the buckets they have been in recent years.

Agreed this should be celebrated

-

Dan-cat

- Posts: 32906

- Joined: 20 August 2013

- Location: Shoreditch, London

- Snooker Idol: The Rocket + The Nugget

- Highest Break: 53

- Walk-On: 

-

by Prop » 26 Apr 2024 Read

It makes a frame-winning clearance or a steal even better to watch. There's more jeopardy. More pressure. 
````

定位诊断：

```json
{
  "parents": [
    {
      "start": 0,
      "end": 1298,
      "score": 4.734821503231965,
      "matches": [
        "2023",
        "3",
        "4",
        "snooker"
      ]
    },
    {
      "start": 8661,
      "end": 9848,
      "score": 2.0346736888668575,
      "matches": [
        "2023",
        "player",
        "snooker"
      ]
    },
    {
      "start": 7459,
      "end": 8736,
      "score": 1.946867104355701,
      "matches": [
        "2023",
        "player",
        "snooker"
      ]
    }
  ],
  "anchors": [
    {
      "start": 7850,
      "end": 7859,
      "text": "2023 =39\n",
      "score": 4.851726221049953,
      "matches": [
        "2023"
      ]
    },
    {
      "start": 8872,
      "end": 8881,
      "text": "2023 =39\n",
      "score": 4.851726221049953,
      "matches": [
        "2023"
      ]
    },
    {
      "start": 1249,
      "end": 1276,
      "text": "- Snooker Idol: Mark Selby\n",
      "score": 4.062715109495467,
      "matches": [
        "snooker"
      ]
    }
  ]
}
```

### C_scores / [8087, 9261)

````text
- Snooker Idol: The Rocket + The Nugget

- Highest Break: 53

- Walk-On: 

-

by Prop » 26 Apr 2024 Read

It makes a frame-winning clearance or a steal even better to watch. There's more jeopardy. More pressure. And also the dynamics of the game and how it's handled by the very best players - they'll suss out early on whether a table is taking them easily down the cushions, for example - and they're capable of adapting their game to suit. And when a player is making 80, ton, 90, it's because they're in the zone, not because the table has afforded them a bit of slack.

-

Prop

- Posts: 30839

- Joined: 16 December 2015

- Highest Break: 65

- Walk-On: Papua New Guinea - FSOL

by Prop » 26 Apr 2024 Read

McManusFan wrote:Prop wrote:Wildey wrote:1st Round Centuries

2024 =25

2023 =39

2022 =44

2021 =39

2020 =38

Good. The bags certainly aren't the buckets they have been in recent years.

POCKETS!

-

Prop

- Posts: 30839

- Joined: 16 December 2015

- Highest Break: 65

- Walk-On: Papua New Guinea - FSOL

by SnookerEd25 » 26 Apr 2024 Read

Prop wrote:It makes a frame-winning clearance or a steal even better to watch. There's more jeopardy. More pressure. 
````

定位诊断：

```json
{
  "parents": [
    {
      "start": 8661,
      "end": 9848,
      "score": 2.027190572814368,
      "matches": [
        "2023",
        "player",
        "snooker"
      ]
    }
  ],
  "anchors": [
    {
      "start": 8872,
      "end": 8881,
      "text": "2023 =39\n",
      "score": 4.545149984990839,
      "matches": [
        "2023"
      ]
    },
    {
      "start": 9724,
      "end": 9753,
      "text": "- Snooker Idol: Cliff Wilson\n",
      "score": 3.6870537692211087,
      "matches": [
        "snooker"
      ]
    },
    {
      "start": 9492,
      "end": 9623,
      "text": "And when a player is making 80, ton, 90, it's because they're in the zone, not because the table has afforded them a bit of slack.\n",
      "score": 1.129084253730714,
      "matches": [
        "player"
      ]
    }
  ]
}
```

## 546 / search 2 / docid 60119

snooker player "decider" 2023 "4-3" "4-0" loss

### A / [17521, 18181)

````text
 114–11 (114), 77–0 |
| 114 | Highest break | 69 |
| 2 | Century breaks | 0 |
| 8 | 50+ breaks | 2 |

Century breaks

There were 26 century breaks made during the tournament. The highest was a 139 made by Bingham in his first round loss to Wilson.

* 139, 132 Stuart Bingham
* 135, 101, 101 Judd Trump
* 130, 119, 119, 114, 105, 102 Neil Robertson
* 128 Zhao Xintong
* 127, 126, 104, 100 John Higgins
* 127, 125, 102 Ronnie O'Sullivan
* 124, 103 Barry Hawkins
* 122 Yan Bingtao
* 116, 104 Mark Williams
* 115 Anthony McGill
* 104 Jack Lisowski

References

External links

* 

Category:2022 in snooker
Category:2022 in sport in London
Masters
2022
Masters 2022
````

### B_pool3 / [239, 1636)

````text
organisation: World Snooker Tour
format: Non-ranking event
total prize fund: £725, 000
winners_share: £250, 000
highest_break: Stuart Bingham ENG (139)
winner: Neil Robertson AUS
runner_up: Barry Hawkins ENG
score: 10–4
previous: 2021
next: 2023

The 2022 Masters (officially the 2022 Cazoo Masters) was a professional non-ranking snooker tournament that took place from 9 to 16 January 2022 at Alexandra Palace in London, England. It was the 48th staging of the Masters tournament, which was first held in 1975, and the second of three Triple Crown events in the 2021–22 snooker season, following the 2021 UK Championship and preceding the 2022 World Snooker Championship. Broadcast by the BBC and Eurosport in Europe, it was sponsored for the first time by car retailer Cazoo.

The participants were invited to the tournament based on the world rankings as they stood after the UK Championship. Some players took issue with the cut-off date, noting that the in-form Luca Brecel, who had entered the top 16 by winning the 2021 Scottish Open in December, did not qualify as the event took place after the UK Championship. Ding Junhui, who had made 15 consecutive Masters appearances between 2007 and 2021, fell out of the top 16 after the UK Championship and failed to qualify. Zhao Xintong, who entered the top 16 for the first time by winning the UK Championship, was the only Masters debutant. 
````

定位诊断：

```json
{
  "parents": [
    {
      "start": 17521,
      "end": 18181,
      "score": 6.714982693443085,
      "matches": [
        "0",
        "loss",
        "snooker"
      ]
    },
    {
      "start": 0,
      "end": 1019,
      "score": 5.16200094890937,
      "matches": [
        "2023",
        "4",
        "snooker"
      ]
    },
    {
      "start": 17013,
      "end": 17521,
      "score": 4.617446806154697,
      "matches": [
        "0",
        "4"
      ]
    }
  ],
  "anchors": [
    {
      "start": 474,
      "end": 485,
      "text": "next: 2023\n",
      "score": 5.318188407738061,
      "matches": [
        "2023"
      ]
    },
    {
      "start": 447,
      "end": 459,
      "text": "score: 10–4\n",
      "score": 4.180913108121517,
      "matches": [
        "4"
      ]
    },
    {
      "start": 17507,
      "end": 17521,
      "text": "0 (68), 62–16,",
      "score": 3.119354404245829,
      "matches": [
        "0"
      ]
    }
  ]
}
```

### C_scores / [7964, 9467)

````text
In the evening, reigning world champion and three-time winner Mark Selby played Stephen Maguire. Selby won the 45-minute opening frame, and the players traded frames until the midsession interval, tying the scores at 2–2. The momentum shifted after the interval, with Selby winning four of the last five frames for a 6–3 victory.

The last two first-round matches both went to a . The 2019 champion Judd Trump, who had missed the previous year's event after testing positive for COVID-19, played the 2018 champion Mark Allen. Both players scored heavily in the opening frames, with Trump making two 101 breaks and Allen a 92. The match was tied at 2–2 at the midsession interval. After play resumed, Trump took the lead with a break of 88, but Allen won the next two frames to go 4–3 in front and looked like extending his lead in frame eight, as Trump with one red remaining. However, Allen failed to escape from a snooker and went , allowing Trump to clear the table and level at 4–4. A 135 break in the ninth frame gave Trump the lead once more, but Allen won an error-filled tenth frame to force the decider. In the final frame, Allen was on a break of 23 before committing a as he bridged over the with the rest. Trump came from 25 points behind to win the match 6–5 with a break of 62.

Kyren Wilson faced the 2020 champion Stuart Bingham. Wilson won four of the first five frames to lead 4–1. In frame six, Wilson declared a foul on himself after the cue ball, allowing Bingham to win the frame. 
````

定位诊断：

```json
{
  "parents": [
    {
      "start": 8294,
      "end": 9257,
      "score": 4.920152429498385,
      "matches": [
        "decider",
        "scorepair4x3",
        "snooker"
      ]
    }
  ],
  "anchors": [
    {
      "start": 8841,
      "end": 8951,
      "text": "However, Allen failed to escape from a snooker and went , allowing Trump to clear the table and level at 4–4. ",
      "score": 1.920477139282561,
      "matches": [
        "snooker"
      ]
    },
    {
      "start": 8951,
      "end": 9077,
      "text": "A 135 break in the ninth frame gave Trump the lead once more, but Allen won an error-filled tenth frame to force the decider. ",
      "score": 1.7289024492802367,
      "matches": [
        "decider"
      ]
    },
    {
      "start": 8644,
      "end": 8841,
      "text": "After play resumed, Trump took the lead with a break of 88, but Allen won the next two frames to go 4–3 in front and looked like extending his lead in frame eight, as Trump with one red remaining. ",
      "score": 1.3514331813780827,
      "matches": [
        "scorepair4x3"
      ]
    }
  ]
}
```
