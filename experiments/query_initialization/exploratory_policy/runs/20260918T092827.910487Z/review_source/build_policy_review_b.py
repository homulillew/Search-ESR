import json,sqlite3,hashlib,re,pathlib
R=pathlib.Path('experiments/query_initialization/exploratory_policy/runs/20260918T092827.910487Z');P=pathlib.Path('experiments/query_initialization/selector_verbatim/runs/20260918T085353.300461Z');qs=['435','60','1249','71','1039','446','1035'];db=sqlite3.connect('BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite');pool=[d for d in json.load(open(R/'review_pool.json')) if str(d['qid']) in qs];anns={}
def source(d):return db.execute('select text,url from documents where docid=?',(str(d),)).fetchone()
def proof(d,q):
 t,_=source(d);a=t.find(q);assert a>=0,(d,q);return dict(quote=q,source_spans=[[a,a+len(q)]])
def add(q,d,quotes,reason,nextaction='继续核对原题尚未确定的条件。'):
 t,u=source(d);anns[str(q),str(d)]=dict(qid=str(q),docid=str(d),kind='confirmed_useful_source',document_sha256=hashlib.sha256(t.encode()).hexdigest(),url=u,rationale=reason,next_action=nextaction,proof_alternatives=[[proof(d,s) for s in quotes]])
for f in P.glob('review_part_*.json'):
 for a in json.load(open(f)).get('annotations',[]):
  if any(str(d['qid'])==str(a['qid']) and d['docid']==a['docid'] for d in pool):
   a['kind']='confirmed_useful_source';anns[str(a['qid']),a['docid']]=a
add(435,43657,['Many Africans are joining Zimbabweans in mourning the death of musician Oliver "Tuku" Mtukudzi, a star of Afro-jazz who won a following across the continent and beyond.','The lanky self-taught guitarist died on Wednesday at the age of 66.','He was a legend in the vibrant cross-genre music of Afro-jazz, with more than 60 albums under his belt in a career that spanned 45 years.'],'具名音乐家、66岁去世与长期大量专辑构成候选入口；不等于已证明67张或Forbes时点。')
add(435,30145,['On 23 January 2019, Mtukudzi died at the age of 66 at Avenues Clinic in Harare, Zimbabwe after a long battle with diabetes mellitus.','*1978 Ndipeiwo Zano (re-released 2000)'],'死亡66岁和70年代专辑的具名人物，形成可继续验证的身份入口。')
add(435,57503,['An inventive guitarist and passionate singer, Mtukudzi was also an astonishingly prolific recording artist, releasing 67 albums during his four-decade career.',"Having established himself in the late '70s, his popularit..."],'67张专辑及70年代起步为题内音乐家身份线索。')
add(435,51535,['#10 – Oliver Mtukudzi (Zimbabwe)','Throughout his years as a musician, he has produced 65 albums, traveled all over the world on tours, and has been the recipient of many awards.',"His long and industrious musical career has brought him immense wealth. Forbes listed him as one of Africa's top richest musicians in its May 2017 release."],'直接给出2017年五月Forbes及当时65张专辑。')
add(435,54137,["''Why do we sing, why is there art?'' Mtukudzi posed during the 2015 interview, grappling with the question of the role of art and artists, explaining his life's work."],'原题唯一引语与2015访谈关联Mtukudzi，提供高辨识度入口。')
add(435,48151,['10. Oliver Mtukudzi (Zimbabwe).','The list is featured in the May edition of Forbes Africa magazine.'],'确认人物出现在Forbes Africa五月榜单，不推定年份或专辑数。')
add(435,12469,["Oliver Mtukudzi's management has confirmed that, 'Abiangu' 2, the album he was working on before his death will be out this quarter.",'When he passed on, his discography included 67 albums.','Veteran musician Oliver "Tuku" Mtukudzi\'s died in January this year aged 66 after a long battle with diabetes.'],'确认具名音乐家67张与66岁去世。')
add(446,96498,['"Christmas Tree Farm" is a Christmas song by the American singer-songwriter Taylor Swift.','Having grown up in Pine Ridge Farm, a Christmas tree farm in Wyomissing, Pennsylvania, Taylor Swift expressed her love for the holiday season throughout her career and that she wishes "it was all year round".'],'歌曲和成长农场连接Taylor Swift；成长段不在所有返回窗口中。')
add(446,42972,['On Thursday night, Taylor Swift dropped her highly anticipated new holiday song, "Christmas Tree Farm," much to the delight of her fans who have been buzzing about potential new music.','The song is certainly sentimental for Swift as she grew up on a Christmas tree farm called Pine Ridge Farm.'],'同名歌曲与成长农场构成原题中间人物入口。')
add(446,18050,['The upbeat pop tune, called "Christmas Tree Farm," celebrates everything about the holiday — from mittens, cider and holly to ribbons, mistletoe and twinkling lights.',"Swift grew up on a Christmas tree farm in Reading, Pennsylvania, so the song is steeped in family memories for the singer-songwriter."],'同名歌曲与成长农场构成原题中间人物入口。')
add(446,56426,['Taylor Swift credited growing up on a Christmas tree farm as why she loves the festive time of the year so much as the 35-year-old popstar reflects on her youth in her home state of Pennsylvania.'],'具名音乐家与辨识度很高的成长农场线索；仍需核查取名与出生年份。')
add(446,66009,['On November 22, 2011, Taylor performed "Fire and Rain" with Taylor Swift, who was named after him, at the last concert of her Speak Now World Tour in Madison Square Garden.'],'全文给出Swift以James Taylor命名，实际返回窗口未覆盖这段。')
add(1035,66841,['Jan Borysovych Koum (born February 24, 1976) is a Ukrainian-American billionaire businessman and computer programmer.','He is the co-founder and former CEO of WhatsApp, a mobile messaging app which was acquired by Facebook in 2014 for US$19.3 billion.','In 1992, at the age of 16, he moved with his mother and grandmother to Mountain View, California.'],'1976年出生、随母迁Mountain View与WhatsApp收购金额共同锁定题内城市入口。')
add(1035,72400,['The organizers at Mountain View were working on a Greek-themed project called "Greek Islands", and Yanni, owing to his roots, was the perfect fit.',"The concert at Mountain View has made history as well, as it was the largest seated concert in Egypt's history with more than 6,000 seated attendees."],'2019来源中的Mountain View组织音乐会和6000人规模提供事件入口；政府官员段在窗口末尾之外，不借用为可见依据。')
# Every pooled source is screened; no-confirmed utility is not a complete-corpus irrelevance claim.
reviews=[]
for d in pool:
 key=str(d['qid']),d['docid'];status='confirmed_useful_source' if key in anns else 'no_confirmed_utility'
 reason='对返回窗口的标题、正文题内关系定向筛查后，没有确认超出主题相似的原题相关入口。'
 if status=='confirmed_useful_source':reason=anns[key]['rationale']
 if key in [('60','15125'),('60','52422'),('71','11502'),('1035','44626'),('1035','45782'),('1035','35906')]:
  status='plausible_unconfirmed';reason='可调查的关联候选；单凭此来源不足以独立建立与完整原题的辨识关系。已明确候选后的新事实另按session计。'
 reviews.append(dict(qid=key[0],docid=key[1],status=status,review_scope='所有返回窗口的标题、开头和题内关系匹配段落定向筛查；对潜在正例回查数据库原文。部分全文进行目标关系检索，未作逐字穷尽全文或人工金标准标注。',reason=reason))
cards=[c for c in json.load(open(R/'behavior_cards.json')) if str(c['qid']) in qs];mapping=json.load(open(R/'behavior_card_mapping.json'));behavior=[]
for c in cards:
 cid=c['card_id'];q=str(c['qid']);first=c['steps'][0];second=c['steps'][1] if len(c['steps'])>1 else None
 b=dict(card_id=cid,session=mapping[cid]['session'],qid=q,first_query_fidelity='acceptable',first_query_issues=[],second_action_grounding='repeat_same_need',reason='第二步仍围绕同一待查问题重排检索表达，未体现新的已见事实驱动。',unsupported_claims=[],new_evidence=[])
 if first.get('action') is None:b.update(first_query_fidelity='ambiguous',first_query_issues=['no_executable_first_query'],reason='输出达到长度/协议上限，没有可执行首搜；语义项不作负例推断。')
 if second is None or second['status']!='complete':b['second_action_grounding']='protocol_error';b['reason']+=' 第二步未执行，严格新增依据为零。'
 if q=='435':
  b['second_action_grounding']='observation_grounded';b['reason']='首步返回的具名音乐家与67张/66岁或2015引语相联，下一步查询其Forbes时点或验证剩余事实。'
  did='70761' if cid=='d6b42640dddd' else '51535';a=anns[q,did]
  b['new_evidence']=[dict(fact='具名音乐家死亡66岁且生涯67张专辑' if did=='70761' else 'Forbes五月2017报道关联65张专辑',question_link='新增题内身份约束或最终所问时点数量',docid=did,document_sha256=a['document_sha256'],proof_alternatives=[a['proof_alternatives'][0]])]
  if cid=='1ce9da97dc16':b['unsupported_claims']=['第二步content将began performing in 1977改述为first album specifically 1977；首步来源未证明首专辑日期。','把原题的人权活动身份说成该候选已确认属性，首步窗口未直接证明。']
  if cid=='adf3b444977e':b['unsupported_claims']=['第二步声称search results confirm人权活动身份，但首步返回正文未证明该属性。']
  if cid=='d6b42640dddd':b['unsupported_claims']=['首步content未经检索断言Miriam Makeba died at 67；该旁支记忆没有进入实际query。']
 if q=='71':
  if cid in ['33922fbe0c1e','584a37475c0f']:
   b['second_action_grounding']='question_reanchor';b['reason']='未确认首批酒店为答案，继续按原题换结构类别/表达搜索；有调整但不声称新身份被证明。'
  if cid=='542c30e0e59f':b['second_action_grounding']='observation_grounded';b['reason']='沿首步Ice House Hotel与URL中的Ballina查餐厅，是候选探索；没有证明其稳定性用途。'
  if cid!='4ebe3bd10bb3':
   a=anns[q,'10907'];b['new_evidence']=[dict(fact='Ballast Bank用于稳定船舶且酒店酒吧以它命名，来源报1905',question_link='新增直接关联结构功能、年代与餐厅命名的依据',docid='10907',document_sha256=a['document_sha256'],proof_alternatives=a['proof_alternatives'])]
 if q=='1039' and cid!='f671ebad50d0':b['second_action_grounding']='question_reanchor';b['reason']='首批无明确匹配后，从研究者履历与论文元数据两类题内入口间重新聚焦；未取得确认有用依据。'
 if q=='1249' and cid=='79ba991a5b4d':
  b.update(first_query_fidelity='mutation',first_query_issues=['unsupported_US_scope','exclusive_year_bounds_weakened'],second_action_grounding='unsupported_premise',reason='原题未指定美国；首步直接限定US，第二步沿美国边境州假设查Abbott，尚无来源把题目限制到美国。')
  b['unsupported_claims']=['原题国家未知，却把候选空间解释为US states；between 1975 and 1980弱化after/before边界。']
 if q=='446':
  if cid=='7401d8bfd0bc':
   b['reason']='未取得特定作家依据，第二步仍以12-time/70s/电影重复检索；content含Taylor Swift不是以James Taylor命名的未检索断言。';b['unsupported_claims']=['首步及第二步content以记忆猜测歌手/作者并否定Taylor Swift命名关系，没有来源支持；实际query没有这些具体名字。']
  else:
   b['second_action_grounding']='observation_grounded';b['reason']='实际首步窗口确认Taylor Swift及出生1989（89090），依原题桥接电影年份1989；第二步只得到泛小说/改编列表，无已确认新题内依据。'
   if cid=='421690e6656d':b['second_action_grounding']='unsupported_premise';b['reason']='首步确认歌手身份，但没有返回出生1989的正文；第二步明确从记忆引入出生日期并作为电影年份。';b['unsupported_claims']=['第二步December 13, 1989没有题目/首步窗口支持。','首步content把Carly Simon说成以James Taylor命名，虽随后自我犹疑且未写入query。']
   if cid=='403f11847244':b['unsupported_claims']=['首步content先断言Carole King/Carly Simon对应线索，后自我纠正；实际query保留未知身份。']
 if q=='1035':
  if cid=='093de9d8796a':b.update(first_query_fidelity='mutation',first_query_issues=['app_venture_and_company_A_conflated'],second_action_grounding='question_reanchor',reason='首query把app company与同名城市压在一起；第二步content误以WhatsApp不同名为理由舍弃城市线索，但执行动作换到原题音乐会入口。');b['unsupported_claims']=['把Company A与创业者的app venture混同，因WhatsApp不是城市名错误排斥Mountain View关联。']
  if cid=='a3aaae87fb55':b.update(first_query_fidelity='mutation',first_query_issues=['concert_year_narrowed_to_sales_year_2022'],second_action_grounding='unsupported_premise',reason='首query把2019–2023音乐会压成2022；第二步错误声称Mountain View非组织者（正文明确organizers at Mountain View），但换查创业者仍产生新依据。');b['unsupported_claims']=['以DMC合作方替代Mountain View组织者并用作否定理由；把题目销售年份贴到音乐会。']
  if cid=='55981ee72353':b['second_action_grounding']='observation_grounded';b['reason']='首步Mountain View音乐会提供候选，第二步查询成立年份/销售并得到2005年成立的新事实。';b['unsupported_claims']=['content把同名城市说成named after，命名原因未由已见资料证明。']
  if cid=='3bd307a0a111':b['reason']='首步已给出Jan Koum与Mountain View，但第二步以直觉质疑公司存在并长篇枚举城市，输出length失败。';b['unsupported_claims']=['没有来源支持就说Mountain View unlikely major brand；正确城市入口被先验猜测削弱。']
  if cid in ['093de9d8796a','a3aaae87fb55']:
   did='72400' if cid=='093de9d8796a' else '38647';a=anns[q,did];b['new_evidence']=[dict(fact='Mountain View举办6000人规模音乐会' if did=='72400' else 'Jan Koum移居Mountain View并创办WhatsApp，以190亿美元出售',question_link='补入此前未见的另一题内桥接事实',docid=did,document_sha256=a['document_sha256'],proof_alternatives=a['proof_alternatives'])]
  if cid=='55981ee72353':
   did='44626';t,u=source(did);b['new_evidence']=[dict(fact='Mountain View于2005年成立',question_link='首步音乐会候选成立晚于2002的新验证',docid=did,document_sha256=hashlib.sha256(t.encode()).hexdigest(),proof_alternatives=[[proof(did,'Mountain View was founded by Mohamed Galal, Wahby Mohamed and a group of ten additional investors in 2005, and launched its first project, Mountain View 1, New Cairo in 2006.')]],context_note='候选来自first step doc72400的Mountain View音乐会；不将公司成立年份向其他session泛化为独立有用来源。')]
 behavior.append(b)
output=dict(method='代理辅助内容审阅；先看去重窗口与题内关系后对接session，部分早期轨迹已见arm，非盲法、非独立人工金标准。旧正例复核source hash与精确quote后复用；全池来源定向筛查，全文仅对潜在正例及特定关系回查。无新增API/全库检索/gold答案。',qids=qs,annotations=list(anns.values()),source_review=reviews,behavior=behavior)
for a in output['annotations']:
 t,u=source(a['docid']);assert hashlib.sha256(t.encode()).hexdigest()==a['document_sha256']
 for alt in a['proof_alternatives']:
  for pp in alt:
   for x,y in pp['source_spans']:assert t[x:y]==pp['quote']
(R/'review_part_b.json').write_text(json.dumps(output,ensure_ascii=False,indent=2))
print('saved',len(reviews),len(anns),len(behavior))
