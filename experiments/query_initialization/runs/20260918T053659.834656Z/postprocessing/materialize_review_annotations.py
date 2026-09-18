import json,sqlite3,re,pathlib,hashlib
p=pathlib.Path('experiments/query_initialization/runs/20260918T053659.834656Z')
c=sqlite3.connect('file:BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
# Each alternative is a set of exact source snippets; all snippets in a set must be visible.
specs=[
('985','50013','target_linked','thesis_author','学位论文记录包含教父姓名、Montanism 和作者，提供论文及作者入口。', [['Larson, Brice Andrew, "Lost Prophets: Tertullian, Eusebius, Epiphanius, and Early Montanism"']]),
('591','37403','target_linked','campus_anniversary','GUC 海外校区十周年活动的时间、校名与地点。', [['2022','The German University in Cairo and the GUC-Berlin will be celebrating their combined "20th GUC – 10th GUC Berlin Anniversary"']]),
('591','86424','target_linked','founder','创始人、董事会主席和科学家身份同时出现。', [['Prof.Dr. Ashraf Mansour is the Founder & Chairman of Board of Trustees of German University in Cairo (GUC).','He is s an Egyptian Scientist']]),
('183','90095','target_linked','teaching_blog','二十年教学文章与多条具体教学观点吻合，入口是博客文章而非最终答案。', [["Lessons I've learned from teaching 20 years of IT",'Listening is the most important part of any communication.'],["Lessons I've learned from teaching 20 years of IT",'Leverage it in the classroom','Never be afraid to say "No"']]),
('183','61300','target_linked','park_blog','三镇合并、铁路公司和公园开放年份组合。', [['The city was formed when 3 smaller towns (Hespeler, Preston and Galt) amalgamated in 1973','the railway only opened the park between 1899 and 1916']]),
('551','37025','target_linked','substitution_2011','2011 年 Paul Rachubka 被半场换下的具体比赛，后续仍需查失误细节。', [['Paul Rachubka who was substituted at half-time in the 5-0 loss to Blackpool in 2011']]),
('810','9043','target_linked','architect_family','建筑师、诗人弟弟关系及四个孩子支持继续核查。', [['Edgar Irving Williams','younger brother of the poet William Carlos Williams','had four daughters']]),
('1072','69382','target_linked','author_thesis','作者出生年、议员任期和国际组织论文相互连接。', [['Aminzadeh was born in 1964','the United Nations and international peace and security: a legal and practical analysis','as a lawmaker from 2004 to 2008']]),
('1072','21375','bridge','museum_year','博物馆及 1997 年开馆提供独立年份入口，不能确认作者。', [['Getty Center','Los Angeles','opened with great publicity in 1997']]),
('583','996','target_linked','artist_interview','2012 年艺术家采访；别名、童年和圆形图案可交叉核查。', [['Cuore','Circles often appear in Carolina\'s artworks']]),
('478','47437','target_linked','book_stadium','指定书评来源、夫妇养熊及体育场。', [['Pro Wrestling Books','Eldorado Stadium in Edinburgh','wife Maggie','Hercules']]),
('478','24964','target_linked','obituary_date','指定报刊讣告、相识时间、养熊年数和日期。', [['2019-12-06','Andy and Maggie met 46 years ago','grizzly with for 25 years']]),
('558','20026','target_linked','museum_founder','Tom Rice 纪念文包含逝世日，全文另含 1973 年博物馆和长期杂志出版。', [['Remembering Tom Rice 1939-2022','passed away in Thailand on January 8']]),
('558','69043','target_linked','family_obituary','父亲 Frank 的讣告列出 Tom 和 Steve，提供家庭关系入口。', [['Frank E. Rice','Rice is survived by his sons Tom Rice of Pawai Beach, Thailand, Steve']]),
('1117','8000','bridge','journal_owner','1828 年接手刊物的姓名可供核查，尚未验证军衔和婚姻关系。', [['In 1828, T. Perronet Thompson took over the Westminster Review']]),
('638','38269','bridge','bestselling_album','识别销量最高专辑这一中间实体；未要求同一窗口已经呈现发行年。', [['Thriller remains the best-selling album of all time'],['By 1984, Thriller had sold 32 million copies worldwide, making it the best-selling album of all time']]),
('638','18046','bridge','bestselling_album','专辑销量列表最高行提供 Thriller 和 1982 年，继续核查品牌仍必需。', [['List of best-selling albums','Michael Jackson\tThriller\t1982','70\t[30][31][32]']]),
('638','15261','bridge','bestselling_album','全文明确销量最高专辑身份；部分窗口仅呈现历年表，不能据此计入已见参考片段。', [["Michael Jackson's Thriller, estimated to have sold 70 million copies worldwide, is the best-selling album ever."]]),
]
anns=[]
for q,d,kind,clue,note,alternatives in specs:
 text,url=c.execute('select text,url from documents where docid=?',(d,)).fetchone()
 proofs=[]
 for alt in alternatives:
  proof=[]
  for quote in alt:
   spans=[[m.start(),m.end()] for m in re.finditer(re.escape(quote),text)]
   assert spans,(d,quote)
   proof.append({'quote':quote,'source_spans':spans})
  proofs.append(proof)
 anns.append(dict(qid=q,docid=d,kind=kind,clue=clue,rationale=note,url=url,document_sha256=hashlib.sha256(text.encode()).hexdigest(),proof_alternatives=proofs))
out={'method':'Single-reviewer source-grounded positive pool. Offline gold available for review only; no LLM judge. Not blind or exhaustive qrels. Unannotated sources remain unverified, not negative. A reference span miss is not proof that the window has no useful information.','annotations':anns}
(p/'evidence_annotations.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
# Explicit deviations flagged while reading every accepted direction. This is a screen, not an independent semantic certification.
flags={}
def flag(q,a,r,d,field,kind,note):flags.setdefault((f'qid_{q}__{a}__r{r}',d),[]).append(dict(field=field,kind=kind,note=note))
flag(985,'A',2,1,'query','unsupported_entity','原题没有明确给出 Montanism；未经检索先具体化教派。')
for r in [1,2]:flag(638,'A',r,1,'query','unsupported_entity','原题没有直接给出 1982；r1 同时加入 Thriller。可能知识正确，但此处未验证。')
flag(558,'A',2,1,'query','range_narrowing','将 2021—2023 区间收窄到 2021。')
flag(1072,'A',2,1,'query','range_ambiguity','before 2010 改为 2009，可能被读成确定任期终点；保留为歧义。')
for a in ['B','C']:flag(786,a,1,1,'goal_and_query','relation_reassignment','将目标演员和侄子拍短片的线索接到另一部长片的导演。')
flag(786,'C',2,1,'goal','work_type_change','将目标人物出演的 91 分钟电影称为 short film。')
flag(23,'C',1,1,'goal_and_query','relation_reassignment','原题是某角色受警察启发阻止骗局；改写使警察直接成为阻止骗局的主体。')
flag(23,'C',1,2,'goal','relation_reassignment','将书的故事概括为骗局由警察阻止，未保持原角色关系。')
flag(551,'B',1,1,'goal_and_query','range_ambiguity','as of 2020 retired 改成 career ending around 2020 / retired 2020。')
flag(551,'C',1,1,'query','range_ambiguity','goal 保留 by 2020，但 query 写 retired 2020。')
flag(551,'C',2,1,'goal_and_query','range_narrowing','原题截至 2020 已退役，goal 明确改成 retired in 2020。')
for r in [1,2]:flag(285,'C',r,2,'goal' if r==1 else 'goal_and_query','unsupported_relation','原题只说科学家任 dean；未明确他是研究中心的 dean。')
flag(1117,'B',1,1,'goal','relation_ambiguity','将 Major 的配偶之兄弟姐妹描述为 married to or related by elopement to Major，配偶关系不清。')
flag(1072,'C',2,1,'query','range_narrowing','before 2010 改为 served 2004 to 2010。')
for r in [1,2]:flag(867,'C',r,1,'query','range_narrowing','列举年份 2020—2024，遗漏原区间允许的 2025；goal 仍到 2025。')
for r in [1,2]:flag(1209,'C',r,1,'goal','unsupported_intent','uncovering the truth 改成 avenging / seeking revenge，增加复仇动机；query 未加。')
for r in [1,2]:flag(558,'B',r,1,'goal','relation_ambiguity','one parent named Frank 改成 parents named Frank；query 未继承这一复数改写。')
rows=[]
for d in sorted(p.glob('qid_*')):
 if not (d/'plan.json').exists():continue
 pl=json.loads((d/'plan.json').read_text())
 for i,x in enumerate(pl.get('directions',[]),1):rows.append(dict(session=d.name,direction=i,goal=x['goal'],query=x['query'],flags=flags.get((d.name,i),[]),screen='flagged' if (d.name,i) in flags else 'no_explicit_issue_flagged'))
(p/'query_review.json').write_text(json.dumps({'method':'All accepted goals and queries read against original questions by one reviewer. Flags distinguish explicit changes and ambiguities; no flag is not proof of semantic correctness. Failed outputs excluded from direction review but retained in attempt metrics.','directions':rows},ensure_ascii=False,indent=2))
print('annotations',len(anns),'directions',len(rows),'flagged',sum(bool(x['flags']) for x in rows))
