# 完整 rollout 轨迹

API 请求是 SDK 调用参数；响应是 SDK 解析结果。未记录密钥或 HTTP 头。
仅记录 API 实际返回的内容，不推断未返回的内部推理。

## 1. control_query · 2026-09-18T06:45:21.375323+00:00

```json
{
  "seq": 1,
  "time": "2026-09-18T06:45:21.375323+00:00",
  "kind": "control_query",
  "arm": "delete",
  "query": "An author was born in 1964 and served as a lawmaker from 2004 to sometime before 2010."
}
```

## 2. query_finalized · 2026-09-18T06:45:21.375752+00:00

```json
{
  "seq": 2,
  "time": "2026-09-18T06:45:21.375752+00:00",
  "kind": "query_finalized",
  "plan": {
    "status": "valid",
    "query": "An author was born in 1964 and served as a lawmaker from 2004 to sometime before 2010.",
    "initial_valid": true,
    "repairs": 0,
    "origin": "preregistered_manual_control"
  }
}
```

## 3. search_start · 2026-09-18T06:45:21.376073+00:00

```json
{
  "seq": 3,
  "time": "2026-09-18T06:45:21.376073+00:00",
  "kind": "search_start",
  "arguments": {
    "query": "An author was born in 1964 and served as a lawmaker from 2004 to sometime before 2010.",
    "k": 6
  }
}
```

## 4. search_result · 2026-09-18T06:45:22.078794+00:00

```json
{
  "seq": 4,
  "time": "2026-09-18T06:45:22.078794+00:00",
  "kind": "search_result",
  "arguments": {
    "query": "An author was born in 1964 and served as a lawmaker from 2004 to sometime before 2010.",
    "k": 6
  },
  "result": [
    {
      "docid": "6459",
      "url": "https://www.library.msstate.edu/grisham/writer",
      "title": "The John Grisham Room",
      "title_span": [
        11,
        32
      ],
      "document_sha256": "3c28d959d70027b0c185f85a4ccfdbd568a2533f0477dbbc11dd03ca05216373",
      "window_ref": "w_cf0799fd698c52f77c25c4da",
      "text": "By his second term, he was vice-chairman of the Apportionment and Elections Committee, and was a member of the Insurance, Judiciary A, and Military Affairs Committees. Yet Grisham was lonely without his family and frustrated with the slow pace of the state legislature. In his boredom, he began to come up with ways to pass the time; he once introduced a resolution commending singer Herbert Khaury (better known as Tiny Tim). Still, he held office until 1990.\n\nA new diversion presented itself in tragic circumstances in 1984 at the DeSoto County courthouse—Grisham witnessed the testimony of a twelve-year-old rape victim and decided to write about what might have happened had her father killed her attackers. A Time to Kill was published in June 1988. Despite publishers' lukewarm reception of this first novel, Grisham had already begun another novel, The Firm, the film rights to which sold to Paramount for $600,000. Suddenly, Grisham was on the map, and a new career as a writer was assured.\n\nSince A Time to Kill Grisham has published a new book each year. Each has become an international bestseller, and nine have been adapted for film (The Firm, The Pelican Brief, The Client, A Time to Kill, The Rainmaker, The Chamber, A Painted House, The Runaway Jury, and Skipping Christmas). At present, over 235 million John Grisham books are in print worldwide.\n\nJohn Grisham and his wife, Renee, have two children, Ty and Shea, and split their time between a Mississippi farm and a Virginia plantation.\n\nFor Posterity: The John Grisham Papers\n\nJohn Grisham, Jr., was born in Jonesboro, Arkansas, in 1955, the son of a cotton farmer. ",
      "offset": 987,
      "end_char": 2624,
      "text_tokens": 390,
      "title_tokens": 6,
      "has_more_before": true,
      "has_more_after": true,
      "parent_window_ref": null,
      "status": "ok",
      "score": 0.48970064520835876
    },
    {
      "docid": "98423",
      "url": "https://awpc.cattcenter.iastate.edu/directory/nancy-pelosi/",
      "title": "Nancy Pelosi",
      "title_span": [
        11,
        23
      ],
      "document_sha256": "62d158a2a462aed52b0e8df34c0abfdd6af7d91f8e47f7f866c57b5da9cb700b",
      "window_ref": "w_e50663700bbd5862f60bf3c5",
      "text": "| State: | California |\n\n| Party: | Democratic |\n\n| Education: | B.A., Trinity Washington University |\n\nNancy Pelosi assumed office in the U.S. House of Representatives in 1987. She has won every election since, including the 2024 election.\n\nShe served as speaker of the House from 2007-2011, and was elected to that position again in 2019 when the Democrats regained control of the House following the 2018 midterm elections, serving until 2023. In Congress, Pelosi was the first woman to lead a major political party, to serve as Democratic whip and to serve as speaker of the House, the highest elective office in the United States to be held by a woman prior to the election of Kamala Harris as vice president in 2020.\n\nPelosi was born March 26, 1940, in Baltimore, Maryland. She completed a Bachelor of Arts from Trinity College in 1962. Her father, Thomas D'Alesandro Jr., represented Maryland's 3rd congressional district in the U.S. House of Representatives from 1939-1947 and served as mayor of Baltimore from 1947-1959.\n\nPrior to serving in Congress, Pelosi served as chair of the California State Democratic Party from 1981-1983. From 1985-1986, she served as the finance chairman for the Democratic Senatorial Campaign Committee. She represented California's 5th District from 1988-1993, the 8th District from 1993-2013, the 12th District from 2013-2023, and the 11th since 2023.\n",
      "offset": 279,
      "end_char": 1671,
      "text_tokens": 391,
      "title_tokens": 3,
      "has_more_before": true,
      "has_more_after": true,
      "parent_window_ref": null,
      "status": "ok",
      "score": 0.4568512737751007
    },
    {
      "docid": "9378",
      "url": "https://www.businessinsider.com/youngest-congress-members-in-united-states-history",
      "title": "Maxwell Frost is the first Gen-Z member of Congress — here are 10 of the youngest Congress members in history",
      "title_span": [
        11,
        120
      ],
      "document_sha256": "ba149d03815df347d9250ea364ee54bc1c429e66198535b4b330b63f6cfa719b",
      "window_ref": "w_996a6077380fa8c8e6bb65b4",
      "text": "He also supported the effort to amend title VII of the Civil Rights Act of 1964 to make it illegal for employers to discriminate against Americans with disabilities.\n\nAfter serving two terms in Congress, Rowland became the youngest Connecticut governor in history at age 37. In this position, Rowland became the subject of \"Geargate,\" a political scandal in which a variety of equipment intended for the military (including sleeping bags, camouflage gear, and a bayonet) were gifted to his children and state police officers who served on his security detail. According to The Hartford Courant, Rowland described the misconduct as \"embarrassing, silly and stupid.\"\n\nFurther, Rowland was investigated for corruption and eventually resigned after reports emerged that he'd not paid state contractors for work on his home. In 2004, he pleaded guilty to conspiring to commit tax fraud and deprive taxpayers of his honest services, and he spent 10 months in prison. Then in 2014, he was found guilty on campaign corruption charges after he worked on two congressional campaigns while hiding payments from regulators, and he was sentenced to 30 months in prison.\n\nTennessee Democrat Rep. Jim Cooper, who first assumed office at 28, served in Congress for 32 years across two terms.\n\nBorn in Nashville, Tennessee, Jim Cooper represented Tennessee's fourth congressional district from 1983 to 1995, entering the role at the age of 28. He served in Congress again from 2003 to 2023, this time representing the fifth congressional district of Tennessee.\n\nAmong the committees Cooper served on during his time in office were the committees on Armed Services, Oversight and Government Reform, and Intelligence.\n",
      "offset": 8381,
      "end_char": 10080,
      "text_tokens": 358,
      "title_tokens": 24,
      "has_more_before": true,
      "has_more_after": true,
      "parent_window_ref": null,
      "status": "ok",
      "score": 0.4563846290111542
    },
    {
      "docid": "81937",
      "url": "https://succeed2gether.org/authors-may-2022/",
      "title": "2022 Authors",
      "title_span": [
        11,
        23
      ],
      "document_sha256": "51d2e1558cfc4186740aaf70dd33be769813b84444ae2595d14f0f118317cbfb",
      "window_ref": "w_8578433b4893177164b16f91",
      "text": "Her book reviews and articles have appeared in the Boston Globe, New York Times, Los Angeles Times, and Washington Post. Kate is part of a presentation with Montclair Public Library's Open Book, Open Mind program.\n\nElisabet Velasquez is a Boricua writer born in Bushwick, Brooklyn. Her work has been featured in Muzzle Magazine, Winter Tangerine, Latina Magazine, We Are Mitú, Tidal and more. She is a 2017 Poets House fellow and the 2017 winner of the Button Poetry Video Contest. Her work is featured in Martín Espada's anthology What Saves Us: Poems of Empathy and Outrage in the Age of Trump. Elisabet lives in Jersey City, New Jersey, and When We Make It is her debut novel. Photo: © Jonathan Rojas\n\nHelen Wan, author of The Partner Track, was born in California and raised in Virginia. She's a graduate of Amherst College and University of Virginia School of Law. She practiced law in NYC for many years before becoming a writer. The Partner Track is currently filming in NYC for a 10-part Netflix series starring actress Arden Cho as Ingrid Yun (Cho), an idealistic young lawyer who struggles with her moral compass and her passions as she fights to climb the partner track at an elite New York City law firm. Wan lives in Maplewood, NJ.\n\nStoryteller Sabina Wasonga-Gitau, born and raised in East Africa, and now a resident of Montclair, New Jersey, will be sharing stories inspired from her childhood years growing up both in Kenya and Uganda. Sabina, is a recipient of the New Jersey State council on the Arts (folk arts apprenticeship grant). She has spent the past year working under the mentorship of Samite Mulondo. ",
      "offset": 11974,
      "end_char": 13603,
      "text_tokens": 375,
      "title_tokens": 5,
      "has_more_before": true,
      "has_more_after": true,
      "parent_window_ref": null,
      "status": "ok",
      "score": 0.45142441987991333
    },
    {
      "docid": "17897",
      "url": "https://en.wikipedia.org/wiki/Steve_Martini",
      "title": "Steve Martini - Wikipedia",
      "title_span": [
        11,
        36
      ],
      "document_sha256": "af3b62710ae3f410bb2a71a91b69c07aa1822049063c38fecd4cb8686bad9e4c",
      "window_ref": "w_7ea55bc9ea30387b6322e6d1",
      "text": "Professional and legal career\n\nMartini's first career was in journalism. He worked as a newspaper reporter for the Los Angeles Daily Journal, the largest legal newspaper in the country covering the state, the local courts and the civic center beat. In 1970 he became the newspaper's first correspondent at the State Capitol in Sacramento and later its bureau chief. There he specialized in legal and political coverage. During this period he attended night law school and in 1974 took his J.D. degree from the University of the Pacific's McGeorge School of Law. He was admitted to the bar in January 1975.\n\nMartini has practiced law both privately as well as for public agencies, appearing in state and federal courts. During his legal career, in addition to other activities, he worked as a legislative representative for the California Department of Consumer Affairs, the State Bar of California, and served as special counsel to the California Victims of Violent Crimes Program. He has worked as an administrative hearing officer, a supervising hearing officer, an administrative law judge, and for a time served as Deputy Director of the State Office of Administrative Hearings. He is currently inactive with the State Bar of California, choosing writing instead as a full-time occupation.\n\nWriting career\n\nIn the mid-1980s Martini began his fiction-writing career. His first attempt at a novel, The Simeon Chamber, was represented by an agent and sold to the New York publisher D.I. Fine within two weeks of its submission. It was published in 1987. Compelling Evidence, his second novel, introduced his series character, attorney Paul Madriani, and was published by G.P. Putnam & Sons. A national bestseller, the novel earned Martini a critical and popular following. ",
      "offset": 1316,
      "end_char": 3090,
      "text_tokens": 367,
      "title_tokens": 5,
      "has_more_before": true,
      "has_more_after": true,
      "parent_window_ref": null,
      "status": "ok",
      "score": 0.45090949535369873
    },
    {
      "docid": "90657",
      "url": "https://nass.gov.ng/mps/single/600",
      "title": "Legislator",
      "title_span": [
        11,
        21
      ],
      "document_sha256": "5cdc32415bb9d704d3b542d4f96ee06c0f6778e59f5d21b76ca0eb9107b8b5e8",
      "window_ref": "w_81e09192126f7b4534c2f71d",
      "text": "---\ntitle: Legislator\nauthor: BA Law; History\ndate: 1999-01-01\n---\nSen. Ned Nwoko\n\nDelta North Senatorial DistrictPrince Ned Nwoko a lawyer, politician and veteran businessman, was born in December 21st, 1960 in Idumuje-Ugboko, Aniocha North LGA, Delta State.\n\nHe attended the University of Keele (England), where he obtained a BA (Hons) Law and History with subsidiary Subject of Biology and American Studies. He went to Kings College, University of London, LLM, where he majored in Insurance, Maritime, Company and Commercial Law, after which he proceeded to the prestigious Inn of Court School of Law-BL (Barrister at Law of Lincoln's Inn. London). He also attended the College of Law – London got the QLTT (Solicitor of the supreme court of England and Wales) and the Commonwealth University College, Belize, where he bagged the D.LITT (Doctor of Letters).\n\nHe represented Aniocha/Oshimili Federal Constituency in the House of Representatives between 1999 and 2003.\n\nHe is a man who has the qualities of leadership, with wide\n\nexperience in different sectors of life. \"He has contributed a lot to the\n\ndevelopment of mankind and to his people inclusively. He has dived into\n\ndifferent sectors to savage drowning and also to help upgrade and make life\n\nbetter.\n\nLegislative Interests\n\n- Education, - Health, - Sports, - Environment, - Youth Empowerment, - Tourism\n\nTarget Achievements\n\n- Education, - Sport, - Health, - Tourism.\n\nAwards & Honors\n\n-D.Sc. (Hon. Causa) Federal University of Petroleum\n\nResources, Effurun\n\n-The journal News – Golden excellence Award, the most\n",
      "offset": 0,
      "end_char": 1577,
      "text_tokens": 394,
      "title_tokens": 3,
      "has_more_before": false,
      "has_more_after": true,
      "parent_window_ref": null,
      "status": "ok",
      "score": 0.4497193992137909
    }
  ]
}
```
