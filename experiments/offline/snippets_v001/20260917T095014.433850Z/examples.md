# 关键片段对照

以下示例从完整结果中挑选用于人工诊断；选择算法未使用标准答案。每项的 A/B 原文完整保留。

## 可见性改善：从人物简介切换到 2023 年赛事经历

qid=546，搜索 5，docid=55516
Query: `"Mark Selby" 2023 Players Championship snooker results`
匹配词：['2023', 'championship', 'mark', 'selby', 'snooker']；BM25 分数：9.5659

**A：400 tokens，位置 [0, 1140)**

````text
---
title: Mark Selby - Wikipedia
date: 2006-01-29
---
name: Mark Selby
honorific_suffix: MBE
birth_date: 19 June 1983
birth_place: Leicester, England
professional: 1999–present
high ranking: 1 (Sep 2011–Nov 2012, Dec 2012–Feb 2013, Apr–Jun 2013, May–Jul 2014, Aug–Dec 2014, Feb 2015–Mar 2019, Aug–Oct 2021, Nov 2021–Apr 2022)
official maximums: 6
ranking wins: 24
minor wins: 7
world champ: 2014, 2016, 2017, 2021

Mark Anthony Selby (born 19 June 1983) is an English professional snooker player. Ranked world number one on multiple occasions, he has won a total of 24 ranking titles, placing him eighth on the all-time list of ranking tournament winners. He is a four-time World Snooker Champion, and has won the Masters three times and the UK Championship twice for a total of nine Triple Crown titles, putting him on a par with John Higgins, and behind only Ronnie O'Sullivan (23), Stephen Hendry (18) and Steve Davis (15).

After winning the England Under-15 Championship in 1998, Selby turned professional in 1999, aged 16. He made his Crucible debut in 2005, and reached his first World Championship final in 2007, when he was runner
````

**B：397 tokens，位置 [34885, 36261)**

````text

At the 2023 World Snooker Championship, Selby defeated Mark Allen 17–15 in a semi-final that lasted for over 13 and a half hours in total, with the final session ending at 12:48 a.m. In frame 16 of the final against Luca Brecel, Selby scored a maximum break, his first maximum at the Crucible, and the first ever compiled in a World Championship final. Trailing 16–10 at one point, Selby managed to close the gap to 16–15; however Brecel won the following two frames to win 18–15.

2023–24 season

At the start of the season, Selby was a semi-finalist in the 2023 European Masters and the 2023 Shanghai Masters, losing 4–6 to Barry Hawkins in the former, and 7–10 to Ronnie O'Sullivan in the latter tournament. Then he reached the final of the 2023 British Open, facing Mark Williams and eventually losing to him 10–7, despite coming back from 5–1 down to 8–7 throughout the match. Going that far in the tournament took its toll, as in the next event, the 2023 English Open, Selby won his held-over qualifying match, but then he lost 4–2 to world number 104 Martin O'Donnell in the last 64, having played nine matches in nine days altogether. He also exited in the last 64 round at the following 2023 Wuhan Open, losing 4–5 to Xu Si. His last notable result for the calendar year was reaching the quarter-finals of the 2023 UK Championship, where he lost 3–6 to Judd Trump.


````

## 偶然命中：Mark Selby 查询选中了 Mark Williams 对 Ding Junhui

qid=546，搜索 5，docid=84585
Query: `"Mark Selby" 2023 Players Championship snooker results`
匹配词：['2023', 'mark']；BM25 分数：4.2484

**A：400 tokens，位置 [0, 555)**

````text
---
title: 2023 British Open
date: 2023-08-14
---
2023 British Open

Final

Played on

2023-10-01

Referee

Frame scores

66-59; 131(110)-4; 100(55)-5; 30-102(58); 74(74)-39; 133(133)-0; 6-121(98); 0-79(73); 6-112(112); 66-1; 30-73; 97-51; 91-0; 36-82; 0-81(68); 69(69)-56; 59-54

Match progress

1-0, 2-0, 3-0, 3-1, 4-1, 5-1, 5-2, 5-3, 5-4, 6-4, 6-5, 7-5, 8-5, 8-6, 8-7, 9-7, 10-7

Williams

Selby

Total

50+ Breaks

133, 110, 74, 69, 55

112, 98, 73, 68, 58

Points Scored

994

919

1913

Avg. points/frame

58.47

54.06

112.53

Breaks

| 50s | 60s |
````

**B：331 tokens，位置 [52080, 52592)**

````text
Breaks
50s	60s	70s	80s	90s	100s	Total
Junhui	2	-	-	-	-	-	2



Last 16
Wales Mark Williams
4(7)2
China Ding Junhui
View head-to-head
Played on
2023-09-28
Referee
Belgium Olivier Marteel
Frame scores
29-87(66); 0-132(123); 58-17; 77-39; 60(52)-5; 99(99)-0
Match progress
0-1, 0-2, 1-2, 2-2, 3-2, 4-2
Williams
Junhui
Total
50+ Breaks
99, 52
123, 66
Points Scored
323
280
603
Avg. points/frame
53.83
46.67
100.5
Breaks
50s	60s	70s	80s	90s	100s	Total
Williams	1	-	-	-	1	-	2
Junhui	-	1	-	-	-	1	2
© 2011-2025 Ron Florax
````

## 词面相关但时间不符：95th minute 查询选中了加时赛末尾任意球

qid=1094，搜索 2，docid=23800
Query: `Champions League final 95th minute free kick`
匹配词：['free', 'kick', 'minute']；BM25 分数：6.9986

**A：400 tokens，位置 [0, 1350)**

````text
---
title: 2005 UEFA Champions League final - Wikipedia
date: 2006-04-23
---
title: 2005 UEFA Champions League final
image_size: 200
event: 2004–05 UEFA Champions League
team1: Milan
team1association: ITA 2003 30px
team1score: 3
team2: Liverpool
team2association: ENG 30px
team2score: 3
details: After extra time Liverpool won 3–2 on penalties
date: 25 May 2005
stadium: Atatürk Olympic Stadium
city: Istanbul
man_of_the_match1a: Steven Gerrard (Liverpool)2015 2. Finals UEFA Champions League Statistics Handbook 2014/15 Union of European Football Associations 10 12 July 2015
referee: Manuel Mejuto González (Spain)
attendance: 69, 000
weather: Clear night18 °C °F78% humidity
previous: 2004
next: 2006

The 2005 UEFA Champions League final was the final match of the 2004–05 UEFA Champions League, Europe's primary club football competition. The showpiece event was contested between Liverpool of England and AC Milan of Italy at the Atatürk Olympic Stadium in Istanbul, Turkey on 25 May 2005. Liverpool, who had won the competition four times, were appearing in their sixth final, and their first since 1985. Milan, who had won the competition six times, were appearing in their second final in three years and tenth overall.

Each club needed to progress through the group stage and knockout rounds to reach the final, playing 12 matches in total
````

**B：122 tokens，位置 [16139, 16659)**

````text

The best chance of the second half of extra time came in the 117th minute (three minutes from penalties) when Shevchenko shot at goal. Dudek saved, only for it to rebound back out to Shevchenko, who again shot from under , which Dudek saved again, pushing the shot over the bar. Liverpool had one last chance at the end of extra time, but John Arne Riise's free kick was blocked, and following this the referee signalled the end of extra time, which meant a penalty shoot-out would decide the championship.

Penalties


````

## 信息取舍：选出角色表格，但不包含人物开头简介

qid=517，搜索 6，docid=67431
Query: `actor played policeman in The Constant Gardener 2005`
匹配词：['2005', 'actor', 'constant', 'gardener', 'in', 'policeman', 'the']；BM25 分数：5.3062

**A：400 tokens，位置 [0, 1434)**

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

He made acting debut in 2000 at the Kenya National Theatre for three years under the guidance of Joab Kanuka. In theater, he played 'Iago' in the Phoenix Players production of the Shakespeare tragedy Othello. In 2005, he made his film debut with a minor role in The Constant Gardener directed by Fernando Meirelles. In the same year, he appeared as 'Barman' in the television movie Transit. In 2016, he appeared in the thriller film The CEO where he played the role of 'Jomo'. The film had its premier 10 July 2016, at the Eko Hotels & Suites, Victoria Island, Lagos and later received critical acclaim.

He made
````

**B：368 tokens，位置 [1426, 2634)**

````text

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

References

External links

* 


````
