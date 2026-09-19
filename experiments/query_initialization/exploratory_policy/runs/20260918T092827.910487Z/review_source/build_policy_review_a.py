import json,sqlite3,hashlib
from pathlib import Path
R=Path('/data/WSH/Search-ESR/experiments/query_initialization/exploratory_policy/runs/20260918T092827.910487Z')
P=Path('/data/WSH/Search-ESR/experiments/query_initialization/selector_verbatim/runs/20260918T085353.300461Z')
DB=sqlite3.connect('file:/data/WSH/Search-ESR/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
Q=['719','520','605','760','519','854','1000']
D={}
def doc(d):
 if d not in D:
  t,u=DB.execute('select text,url from documents where docid=?',(d,)).fetchone();D[d]=(t,u,hashlib.sha256(t.encode()).hexdigest())
 return D[d]
def proof(d,*quotes):
 t,_,_=doc(d);out=[]
 for quote in quotes:
  assert quote in t,(d,quote)
  a=t.index(quote);out.append({'quote':quote,'source_spans':[[a,a+len(quote)]]})
 return out
anns={}
for f in ['review_part_a.json','review_part_b.json']:
 for a in json.loads((P/f).read_text())['annotations']:
  if a['qid'] in Q:
   assert a['document_sha256']==doc(a['docid'])[2]
   a['kind']='confirmed_useful_source';anns[(a['qid'],a['docid'])]=a

def annotate(q,d,reason,action,*alternatives):
 t,u,h=doc(d)
 if (q,d) in anns:
  a=anns[q,d];a['proof_alternatives'].extend(alternatives);a['rationale']+=' 本轮补充：'+reason
 else:
  anns[q,d]={'qid':q,'docid':d,'kind':'confirmed_useful_source','document_sha256':h,'url':u,'rationale':reason,'next_action':action,'proof_alternatives':list(alternatives)}

clinic=proof('33294','After independence in 1957 Dr Barnor retired from the government service.','In 1958 he set up the Link Road clinic, Accra, which assumed hospital status in 1972.')
annotate('1000','33294','独立后1958开Link Road诊所与题设相连。','继续核对表彰书籍。',clinic)
track=proof('47140','| 6. |\n\nNothing According to Plan','release date: September 13th 2016')
annotate('605','47140','第6首与2016发行期提供已识别ReCore专辑的后续依据。','核实作曲者及电影提名。',track)
marriage=proof('3817','On 16 November 1818 he married Elizabeth von Backström in the Groote Kerk in Cape Town.','Thomas Charles John, his second son, would later join his father as apprentice road builder to one day become the builder of many more roads than his father.')
widow=proof('3817','His wife passed away after their relocation in 1857 and Bain married Theodora Kerr, a widow from Uitenhage one year later.')
annotate('854','3817','1818婚姻、父子修路与1857丧妻分别支持题内历史入口。','核对孤儿身世与事故道路。',marriage,widow)
orph=proof('71391','Both parents died when he was a child and he was brought up by an aunt who lived near Edinburgh.','In November 1818 he married Miss Elizabeth Maria von Backstrom, who bore him 11 children.','Elizabeth died in 1857, and he was then briefly married to Theodora Kerr.')
widow2=proof('71391','In November 1818 he married Miss Elizabeth Maria von Backstrom, who bore him 11 children.','Elizabeth died in 1857, and he was then briefly married to Theodora Kerr.')
annotate('854','71391','Bain童年父母双亡、1818结婚和1857丧妻的关联直接匹配题内历史条件。','与Bainskloof事故道路连接。',orph,widow2)
road=proof('46302','Bainskloof Pass () is a mountain pass on the R301 regional road between Wellington and Ceres in the Western Cape province of South Africa.','was constructed by road engineer Andrew Geddes Bain with the use of convict labour.')
annotate('854','46302','来源明确给出Bainskloof道路由Andrew Geddes Bain修建，连接事故来源与历史人物。','核对人物婚姻和道路总数。',road)
road2=proof('69065','Built circa 1849 by Andrew Geddes Bain, this pass was a tough nut to crack, working with convicts and raw, rough materials and methods.')
annotate('854','69065','全文有Bains Kloof由Andrew Geddes Bain修建的段落；当前返回仅路线参数，不能借全文计可见。','Open回到建造史段。',road2)
birthday=proof('32525','Professor Dr. Niyazi Kızılyürek was born on the 7th of December 1959 in Potamia a small bicommunal village in Cyprus.')
annotate('519','32525','明确给出Niyazi研究者身份与12月7日生日，可核对已识别传记作者。','继续验证博士年份和书年。',birthday)
bookyear=proof('73078','The book, Glafkos Clerides: The Path of a Country, is an important document for anyone who wants to understand the long-standing Cyprus problem and derive their own lessons for the future.','Year: 2008')
annotate('519','73078','书名、Clerides与Niyazi访谈关系及2008出版构成题内书籍关系。','结合作者生日/博士核对。',bookyear)
bookauthor=proof('6229','24) Glafkos Clerides: the Path of a Country, by Niyazi Kızılyürek')
annotate('519','6229','书评明确连接Clerides、传记书名与Niyazi作者身份。','继续核对研究者背景。',bookauthor)

cards=json.loads((R/'utility_cards.json').read_text());pool={}
for w in cards:
 if w['qid'] in Q:pool.setdefault((w['qid'],w['docid']),[]).append(w)
# All returned windows were read, combining overlapping spans to avoid duplicate review.
neg_reason={
'719':'已审阅的合作/年代名单或个人人物简介未建立1970年代出生者与1970年代成立乐队在1990年代两支单曲合作的特异关系；不将仅年代、乐队或首专词重合计作入口。',
'520':'窗口未建立作者首作年龄、作者与大使之女/子的配偶关系或题设年代内自演电影的具体关联；部分人物生卒、配偶身份已明显不符。',
'605':'其余窗口多为游戏音乐排行/获奖介绍/其它曲目表，未建立第21首tower与95–100分钟时长的组合，也未连接已识别ReCore作曲者和获提名电影。',
'760':'窗口的人物出生地/年代/死亡期与题设不符，或只给一般演艺经历，未建立母亲为舞台演员、1960年代离婚、学习与死亡同城或1950年代影片关系。',
'519':'未连接BBC初遇、Vienna Café、单子女/晚年教堂婚礼或特定传记作者背景；多数为其它政治人物、名人婚礼、学术简介或传记目录。',
'854':'其余窗口为一般动物交通/其它事故、野生动物介绍或其它历史人物，未把2017年2月事故与题设道路/修建者事实连接。',
'1000':'其它医生或殖民医学背景未建立Copacabana二战航行、独立次年开诊所或表彰书的特异链；部分人物留学/开诊所年代直接不符。'}
sources=[]
for (q,d),ws in sorted(pool.items()):
 status='confirmed_useful_source' if (q,d) in anns else 'no_confirmed_utility'
 reason=anns[q,d]['rationale'] if (q,d) in anns else neg_reason[q]
 if (q,d)==('519','27467'):
  status='plausible_unconfirmed';reason='全文807字符仅显示Niyazi社会研究者及PhD1990；独立初见尚缺生日或所著传记关系。若本会话已由62838识别传记作者，该文博士年份才构成可确认的新依据；不把跨会话知识借给current r2。'
 if (q,d)==('760','63016'):
  status='plausible_unconfirmed';reason='列表给Mary Twala(1939–2020)、Washington Xisolo(1934–2017)，是有根据的待查候选，但South African身份不等于非洲出生；尚无母亲、离婚、戏剧学习或影片关系。'
 if (q,d)==('520','11632'):
  status='plausible_unconfirmed';reason='导演2022死亡且全文列两段婚姻，但未明确两个离婚及作者自演电影的关系，仅保留待查导演。'
 if (q,d)==('519','72732'):
  status='plausible_unconfirmed';reason='总统身份、出生1919和Lila婚于1947可供核对已识别人物；窗口没有BBC/Vienna、晚年教堂婚礼或传记作者关联，不独立计强入口。'
 scope={'all_returned_window_cards':[w['card_id'] for w in ws],'body_spans':sorted({(w['offset'],w['end_char']) for w in ws}), 'title_reviewed':True,'full_document_review':d in {'47140','62838','33294','41381','27467'},'targeted_full_document_review':d in {'69065','11632','15991','54571','3817'}}
 s={'qid':q,'docid':d,'status':status,'review_scope':scope,'reason':reason}
 if (q,d) in {('760','63016'),('519','27467'),('520','11632'),('519','72732')}:s['sensitivity_candidate']=True
 sources.append(s)

# Behaviors are keyed by actual session; root mapping supplies the anonymized card id.
mapping=json.loads((R/'behavior_card_mapping.json').read_text())
print('mappingtype',type(mapping),'first',str(mapping)[:150])
if isinstance(mapping,dict):
 bysession={v['session']:k for k,v in mapping.items()}
else:bysession={v['session']:v['card_id'] for v in mapping}
beh=[]
def add(q,arm,r,ground,reason,unsupported=None,fidelity='acceptable',issues=None,new=None):
 sid=f'qid_{q}__{arm}__r{r}'
 beh.append({'card_id':bysession[sid],'session':sid,'qid':q,'first_query_fidelity':fidelity,'first_query_issues':issues or [],'second_action_grounding':ground,'reason':reason,'unsupported_claims':unsupported or [],'new_evidence':new or []})
def evidence(d,fact,link,p):
 return {'docid':d,'document_sha256':doc(d)[2],'fact':fact,'question_link':link,'proof_alternatives':[p]}
for arm in ['current','exploratory']:
 for r in [1,2]:
  add('605',arm,r,'observation_grounded','首搜忠实采用曲序和总时长；第二步content准确识别ReCore并列出尚未验证的发行期、作曲者与第6首，再发有来源基础的query。第二窗口新显示2016发行及第6首，而首窗口只从第11首开始。',new=[evidence('47140','ReCore于2016-09-13发行，第6首为Nothing According to Plan。','对应发行区间和待找第6首。',track)])
for r in [1,2]:
 add('519','current',r,'unsupported_premise','首query本身围绕题内研究者条件；但首content已武断认定Thatcher、编造BBC/Vienna故事并把one child或两人60岁条件归咎题目。第二步未获对应观察支持，仍以Thatcher'+('及John Campbell' if r==2 else '')+'作为确定搜索入口。',unsupported=[{'stage':'first_content','claim':'Based on the details provided, the political leader is **Margaret Thatcher**.','reason':'身份和BBC/Vienna初遇叙述没有题目或已见来源支持；甚至承认子女/年龄条件矛盾而迁就候选。'},{'stage':'second_action','claim':('John Campbell biographer Margaret Thatcher' if r==2 else 'biographer of Margaret Thatcher'),'reason':'首批观察没有建立该传记对象或作者关系。'}])
 phd=proof('27467','He graduated from the University of Bremen in Germany in 1983, where he also obtained his PhD in 1990.')
 add('519','exploratory',r,'observation_grounded','首content也曾将BBC/Vienna附会Thatcher，随后保留题内query；观察62838后明确切换到Clerides及Niyazi，第二步核实作者。博士事实的意义依赖本会话首步已确认Niyazi为该书作者，不能借给current r2首见该profile。',unsupported=[{'stage':'first_content','claim':'The meeting at the BBC and the Vienna Café is a famous anecdote regarding Margaret Thatcher' if r==1 else 'This narrative strongly matches **Margaret Thatcher**.','reason':'此具体附会未被原题/来源支持；模型随后质疑且检索后纠正，不能因此说它从未猜候选。'}],new=[evidence('32525','Niyazi出生于1959年12月7日。','验证原题研究者生日。',birthday),evidence('73078','该传记的出版年份为2008。','验证2010之前出版。',bookyear),evidence('27467','Niyazi于1990在Bremen取得PhD。','首步62838已确立其为传记作者；本步才取得博士年份。',phd)])

add('1000','current',1,'observation_grounded','首步取得Barnor与Copacabana/Edinburgh的关系，第二步据此核对诊所及书籍；返回新诊所1958依据。query的1990s把原题末20世纪进一步收窄，单列为范围问题。',unsupported=[{'stage':'second_query','claim':'book profiled 1990s','reason':'原题为20世纪末的闰年，没有限定1990年代；是未说明的范围收窄。'}],new=[evidence('33294','Barnor在加纳1957独立之后，于1958开设Link Road诊所。','验证独立次年开诊所。',clinic)])
died=proof('33294','Matthew Arnum Barnor, former family physician, president Ghana Medical Association, founding father Planned Parenthood Association Ghana, founder Link Road Hospital, Accra, Ghana (born 1917; q Edinburgh 1947; DTM&H), d 20 June 2005.')
add('1000','current',2,'observation_grounded','首搜已得关键航行和学医关系，Open(after)沿同一来源扩读，获得1958诊所与2005死亡；不是只靠Open次数计收益。',new=[evidence('33294','Barnor在独立次年1958开Link Road诊所。','诊所年份条件。',clinic),evidence('33294','Barnor于2005年6月20日去世。','早21世纪去世条件。',died)])
uni=proof('33294','Born in Accra, in the then Gold Coast, in 1917, he won a British government scholarship to study medicine and left for Edinburgh University on the Belgian ship Copacabana during the second world war.')
add('1000','exploratory',1,'observation_grounded','首步窗口2071之后已有Copacabana船队尾段及1958诊所。第二步识别Barnor并追查书籍；重搜定位到之前未见的1871句，新增明确Edinburgh University留学/政府奖学金关系，虽未取得书籍答案仍有相关新增。',unsupported=[{'stage':'first_content','claim':'Dr. Charles Odamtten Easmon ... He sailed on the Copacabana? Yes','reason':'首搜前把具体候选航行关系作肯定陈述，尚无来源；实际query未使用该候选。'},{'stage':'second_content','claim':'one of seven West African students','reason':'窗口原文是seven ships以及several west African students，数量主体混淆。'}],issues=['query使用clinic1958依赖一般历史知识将独立次年具体化；区别于题目逐字事实，不把这一可核算展开计为关系错误。'],new=[evidence('33294','Barnor获政府奖学金去Edinburgh University学医，并于二战乘Copacabana赴学。','本会话first仅展示Edinburgh临床工作和船队后文，second才显示大学留学的明确关系。',uni)])
add('1000','exploratory',2,'protocol_error','首步没有合法Search而直接给Easmon身份断言；按预算契约失败，没有窗口或可评query。',fidelity='not_evaluable',issues=['No executable first query.'],unsupported=[{'stage':'first_content','claim':'the biographical markers ... uniquely identify Charles Odamtten Easmon','reason':'没有任何检索观察，具体大学、诊所、去世年均来自未验证记忆/猜测。'}])

for r in [1,2]:
 add('520','current',r,'question_reanchor' if r==1 else 'observation_grounded','第二步改搜原题另一电影导演入口。' if r==1 else '由返回Carol Grace文中Saroyan名字提出待验证候选；并未声称已满足条件，但已见Carol生于1924与原题配偶1950年代出生冲突，应降低候选优先级。')
add('520','exploratory',1,'question_reanchor','首搜没有明确入口，第二步改用原题导演两次离婚/死亡期的另一约束。query丢失between，但可见content明确仍指2015–2023区间，记为表达含混而非肯定缩成两个年份。')
add('520','exploratory',2,'protocol_error','首搜后大量枚举记忆中的作者而耗尽输出预算，第二步finish=length，没有执行新工具。首步事实效用仍单独保留。',unsupported=[{'stage':'first_content','claim':'J.D. Salinger (alive); Philip Roth (alive)','reason':'与题目/已见来源无关的无来源具体生存断言；不据此计新增依据。'}])

add('719','current',1,'question_reanchor','第一轮无特异入口，第二轮以U2作为显式待检验乐队假设；U2不是来自已见窗口，不能称观察驱动，也不把猜测名称本身判为虚假事实。')
add('719','current',2,'unsupported_premise','第二步将Queen放入query，首content已知道Freddie Mercury去世与题目主唱仍活冲突；没有来源建立另一符合者，体现候选筛选不受已知约束约束。',unsupported=[{'stage':'second_query','claim':'collaborated with Queen','reason':'是未验证且与模型自己已指出主唱存活条件冲突的候选入口，未给出解决冲突的理由。'}])
add('719','exploratory',1,'protocol_error','首步长篇枚举乐队，finish=length，无完整query或Search。',fidelity='not_evaluable',issues=['No executable first query.'])
add('719','exploratory',2,'repeat_same_need','第二步基本重发同一类query，只附加首专词；content没有从返回片段取得新识别关系，仍持续枚举记忆候选。',unsupported=[{'stage':'first_content','claim':'Steven Tyler ... 22 years ... fits just short of two decades','reason':'把超过20年说成不足20年，属于可见分析中的关系错误；实际首query没有该年份关系。'}])

for arm in ['current','exploratory']:
 for r in [1,2]:
  ground='observation_grounded' if arm=='current' and r==1 else 'repeat_same_need'
  reason='首窗口候选列表给Mary Twala出生/死亡年代，第二步明确把她当待验证对象继续查母亲等条件；有观察来源但未建立强入口。' if ground=='observation_grounded' else '第二步仍围绕相同人物生平词改写，未形成来源支持的实体或关系；没有Open或独立新入口。'
  issues=['African actor（或African born简写）未明确保留“出生在非洲国家”；不能把国籍/族裔当出生地。']
  if arm=='exploratory' and r==2:issues.append('stage actress mother与person主体的绑定含混，下一轮又把未知性别限定为actress。')
  uns=[]
  if (arm,r) in [('current',2),('exploratory',1)]:uns=[{'stage':'second_query','claim':'died 2017 2018 2019' if arm=='current' else 'died 2017 2018 2019 2020 2021 2022','reason':'在声称保留原题2016–2023条件时，实际query遗漏部分边界年份；未说明是分批尝试。'}]
  add('760',arm,r,ground,reason,unsupported=uns,fidelity='ambiguous',issues=issues)

for r in [1,2]:
 ground='unsupported_premise' if r==1 else 'observation_grounded'
 reason='已经看到Bainskloof豹事故，却把BC+解释为British Columbia并排斥南非来源；第二query加BC无题内或来源依据。意外仍找回Bain1818婚姻，所以新增依据与行为缺陷分别计。' if r==1 else '首步取得Bainskloof豹事故，第二步据道路名称验证修建者身份，得到1818婚姻、孤儿/1857丧妻及父子道路数量等新历史关系。'
 uns=[{'stage':'first_and_second_content','claim':'Since the corpus is BC+; The Bainskloof incident is in South Africa, not BC.','reason':'把数据集名解读为地理范围并加入BC限制，原题没有这个限制。'}] if r==1 else []
 new=[evidence('3817','Bain于1818结婚，其子Thomas也随其修路。','验证事故年减199所指历史入口及家族修路关系。',marriage)]
 if r==2:
  new.append(evidence('71391','Bain童年失去双亲，1818婚姻的妻子于1857去世。','验证孤儿及晚1850年代丧偶。',orph))
  new.append(evidence('15991','Thomas与父亲分别修建24和8条主要山路。','总数32处在题目开放范围内。',proof('15991','Bain built 24 major mountain roads and passes in the second half of the 1800s. His father built eight during the first half of the same century.')))
 add('854','current',r,ground,reason,unsupported=uns,fidelity='ambiguous',issues=['把文章发表于2017年2月近似为事故发生日期；原题并未显式保证两者同月。'],new=new)
add('854','exploratory',1,'observation_grounded','首步Bain1818婚姻与父子修路形成历史入口；第二步准确针对孤儿/丧偶未决条件，取得1857丧妻的新原文。',fidelity='mutation',issues=['query把本人及家人合计more than28 less than40 roads压成road builder built28-40 roads，丢失共同主体和开放区间；1818还假设事故年即报道年。'],new=[evidence('3817','Bain妻子1857年去世，次年再婚。','验证晚1850年代丧偶。',widow)])
add('854','exploratory',2,'observation_grounded','首步历史入口将地点定位南非，第二步转向题内动物事故并得到Bainskloof豹、2017日期及37kg。query添加baboon/monkey作为可能动物的猜测，content同时虚构Bain死亡/丧偶年份；新增依据与此缺陷分别记录。',fidelity='mutation',issues=['query把家族合计道路数变成本人built28-40，并弱化晚1850年代；1818基于事故年=报道年的假设。'],unsupported=[{'stage':'second_content','claim':'Andrew died in 1863. His wife Elizabeth died in 1858.','reason':'这两个年份不在首步窗口；实际本地Bain原文为1864/1857。'}],new=[evidence('41381','2017年2月Bainskloof Pass汽车撞豹，事故后测得37kg。','直接连接事故月份/道路与待问动物体重。',proof('41381','On Thursday 16 Feb 2017, a leopard was hit by a car in Bainskloof Pass near Wellington.','He was quite large for a fynbos leopard, weighing in at 37kg and was estimated to be around 5 years old.'))])

assert len(beh)==28 and len({b['session'] for b in beh})==28
# Every retained new proof is entirely in its own second observation, including a separately returned title.
for b in beh:
 result=json.loads((R/b['session']/'result.json').read_text());steps=result['steps']
 if b['new_evidence']:
  vs=steps[1]['result'];vs=vs if isinstance(vs,list) else [vs]
  for e in b['new_evidence']:
   for alt in e['proof_alternatives']:
    for z in alt:
     ok=False
     for w in vs:
      if w['docid']!=e['docid']:continue
      intervals=[(w['offset'],w['end_char'])]
      if w.get('title_span'):intervals.append(tuple(w['title_span']))
      for a,c in z['source_spans']:
       if any(x<=a and c<=y for x,y in intervals):ok=True
     assert ok,(b['session'],e['docid'],z)
review={'method':'代理辅助、非人工金标准、非盲审；审阅者接触了arm/session和旧案例。仅审正式v002。全部本组返回窗口逐段筛查，重叠区间合并阅读；旧正例原文和hash复核、新正例逐条源文定位。来源全文所见不借给模型可见依据。边界候选保留plausible；未使用gold答案或额外API。','qids':Q,'annotations':[a for k,a in anns.items() if k in pool],'source_review':sources,'behavior':sorted(beh,key=lambda b:b['session'])}
(R/'review_part_a.json').write_text(json.dumps(review,ensure_ascii=False,indent=2))
print('wrote',len(review['annotations']),'annotations',len(sources),'sources',len(beh),'behaviors')
