import json,sqlite3,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
D=sqlite3.connect('file:/data/WSH/Search-ESR/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
Q={'1147','124','978','191','134','692'}
cards=[c for c in json.loads((P/'utility_cards.json').read_text()) if str(c['qid']) in Q]
bs=[c for c in json.loads((P/'behavior_cards.json').read_text()) if str(c['qid']) in Q]
mp=json.loads((P/'behavior_card_mapping.json').read_text())
def doc(i):return D.execute('select text,url from documents where docid=?',(str(i),)).fetchone()
def proof(i,qs):
 t,u=doc(i);o=[]
 for q in qs:
  a=t.index(q);o.append(dict(quote=q,source_spans=[[a,a+len(q)]]))
 return o
def ann(q,i,qs,why,next_action):
 t,u=doc(i)
 return dict(qid=str(q),docid=str(i),kind='confirmed_useful_source',document_sha256=hashlib.sha256(t.encode()).hexdigest(),url=u,rationale=why,next_action=next_action,proof_alternatives=[proof(i,qs)])
A=[]
A.append(ann(978,70422,['Tatsuya Endo is perhaps the most well-known on the list as he is the author of the massively successful Spy X Family. He initially worked as an assistant for Blue Exorcist, Attack on Titan, and Fire Punch.'],'明确作品作者与先前助手系列的关系，可形成待核验入口；不宣称时间/rehabilitation/第十篇章已确认。','继续核验作者家庭、rehabilitation与第十篇章。'))
A.append(ann(978,5794,['His family consists of one parent and one elder brother.','His hobbies, special skills, pride include skiing, basketball, racket-based ball games, repeated side-steps, doing nothing, getting stomatitis, and health destruction.[1]','Endo worked as an assistant for the manga series Blue Exorcist, Fire Punch[2], and Attack on Titan[3].'],'Endo家庭结构、运动爱好及助手经历构成多个题内关系的具体入口。','核验个人康复创作表述、作品及第十篇章。'))
A.append(ann(191,86746,['Tim Ellis (magician) - Wikipedia',"In 1992 he bought Australia's oldest magic shop, 'Bernard's Magic Shop' which he owned for several years."],'标题身份与1992购店关系明确；不把刊物编辑当成TV训练。','查电视训练、盲驾及MICF演出。'))
A.append(ann(191,48963,['Tim Ellis','To promote Magic Week 87, Tim drove a $100,000 Mercedes Benz while blindfolded.'],'同一历史来源列Tim Ellis和Tim盲驾事件；结合购店候选提供具体核验关系。','核验其TV训练与MICF。'))
# Choose occurrence of Tim Ellis within delivered paragraph, not the earlier full-source occurrence.
A[-1]['proof_alternatives'][0][0]=dict(quote='Tim Ellis',source_spans=[[doc('48963')[0].index('Tim Ellis',726),doc('48963')[0].index('Tim Ellis',726)+len('Tim Ellis')]])
A.append(ann(191,74394,['Tim Ellis','His life has been a roller coaster ride of magical adventures. Tim has been buried alive, escaped from a wooden crate at the bottom of the Yarra River, freed himself from straitjackets hundreds of feet above city streets, and driven a $100,000 sports car while blindfolded.'],'Tim身份与盲驾相连，另在窗口描述电视制作及购店；可以核验候选。','查训练而不只查是否曾制作节目。'))
A.append(ann(191,80098,['TIM ELLIS has been buried alive, driven sports cars blindfolded, escaped straitjackets high above city streets and been thrown into the Yarra River in a locked wooden trunk.','Tim has acted as magic consultant on several plays, movies and TV series and co-produced \'The Catchpenny Club\' for Channel 31 and \'Magical Mystery Tour Downunder\' for NHKTV Japan.'],'明确Tim盲驾及具体电视制作节目，是题内背景核验来源，尚未确认受训。','查其正式电视制作与编辑训练。'))
A.append(ann(191,85951,["Ellis spent his youth in Melbourne's libraries, hunting down tips on card tricks and rare illusions. He was a regular of Bernard's Magic Shop on Elizabeth Street (which is now closed), where he connected with other lovers of the craft. He would later own and manage Bernard's for a period in the early '90s."],'明确Ellis经营Bernard店及90年代，支持已有购店身份关系。','交叉核验1992与训练。'))
A.append(ann(191,28646,['TIM ELLIS','EDUCATION Swinburne University – Film & Television School Film & Television Production 1981'],'离线查阅全文头部可确认电视训练，当前返回尾窗不含该事实，不能给模型可见依据借用。','Open before/around向简历教育开头阅读。'))
positive={(a['qid'],a['docid']) for a in A}
S=[]
reason_by_q={
'1147':'返回的是旧代rapper欺凌、泛真名名单、歌词或占位页，未建立2000–2010出生、最小孩子与2017突破的题内辨识联系。',
'124':'纸牌泛历史/玩家、其他作者或2018颁奖名单，未连接艾美得主所写2018纸牌起源文章与2020 KW童书引用。',
'978':'泛漫画/助手/康复/编辑主题，未建立题中家庭、个人rehabilitation或特定助手与作品关系的可确认入口。',
'191':'泛喜剧节节目、他人履历或Bird Box盲驾事故/占位页，未连接1992购店与表演者训练等辨识关系。',
'134':'纳米/工程/督导/院校泛材料，未建立特定论文作者与贵族同姓及导师评价联系。',
'692':'动物写作、医学、迁徙或导演/作者泛材料，未连接2010–2015个人迁徙物种文章与2017诊断诊所主任身份。'}
for q,i in sorted({(str(c['qid']),str(c['docid'])) for c in cards}):
 cc=[c for c in cards if str(c['qid'])==q and str(c['docid'])==i]
 pos=(q,i) in positive
 why=next((a['rationale'] for a in A if a['qid']==q and a['docid']==i),reason_by_q[q])
 status='confirmed_useful_source' if pos else ('plausible_unconfirmed' if (q,i) in {('1147','98951'),('978','27679'),('978','244'),('978','29427')} else 'no_confirmed_utility')
 S.append(dict(qid=q,docid=i,status=status,review_scope=dict(all_returned_windows=[[c['offset'],c['end_char']] for c in cc],window_card_ids=[c['card_id'] for c in cc],outside_window_reads=[[0,1900]] if i=='28646' else [],full_document_negative_claim=False),reason=why+' 只报告已审范围内未确认，非全文不存在结论。' if not pos else why))
def new(i,qs,fact,link):
 t,u=doc(i);return dict(docid=str(i),document_sha256=hashlib.sha256(t.encode()).hexdigest(),fact=fact,question_link=link,proof_alternatives=[proof(i,qs)])
B=[]
for c in bs:
 m=mp[c['card_id']];session=m['session'];q=str(c['qid']);steps=c['steps']
 b=dict(card_id=c['card_id'],session=session,qid=q,first_query_fidelity='acceptable',first_query_issues=[],second_action_grounding='repeat_same_need',reason='',unsupported_claims=[],new_evidence=[])
 if q=='1147':
  b['reason']='第二次仍搜索同组出生年代、欺凌、最小孩子和2017线索，未利用具体候选或改变信息需求；没有新题相关事实。'
  if session.endswith('exploratory__r2'):
   b['second_action_grounding']='unobservable';b['query_narrowing']='birth 2000–2010 -> 2005';b['reason']='第二次query把2000–2010收窄成born 2005。首步Young Poppa在2016年11岁可支持约2004/2005候选；content为空，无法判断是尝试候选还是无依据收窄，不计确定unsupported断言。未取得新题相关依据。'
 elif q=='124':
  b['first_query_fidelity']='ambiguous';b['first_query_issues']=['关键词排列未清楚绑定2018为文章年份，实际召回颁奖名单；不是显式把获奖时间改成2018。']
  b['second_action_grounding']='observation_grounded';b['reason']='content准确指出首步为2018颁奖名单而非艾美得主撰写文章，并调整作者关系表达；未取得题内可确认来源，行为修正与效用分开。'
 elif q=='978':
  b['reason']='围绕personal rehabilitation/助手线索继续搜索；增加原题家庭、编辑或许可条件属于题内调整，不可仅凭发生于观察后声称依赖具体观察。'
  b['second_action_grounding']='question_reanchor' if 'exploratory' in session else 'repeat_same_need'
  if session.endswith('current__r1'):
   b['new_evidence']=[new('70422',['Tatsuya Endo is perhaps the most well-known on the list as he is the author of the massively successful Spy X Family. He initially worked as an assistant for Blue Exorcist, Attack on Titan, and Fire Punch.'],'首次可见Endo是Spy X Family作者并曾为Blue Exorcist等担任助手。','作者与先前助手作品的关系为题内具体候选入口。')]
  if session.endswith('current__r2'):
   b['second_action_grounding']='repeat_same_need';b['reason']+=' 第二query加入VIZ Media但未断言许可关系已成立，可以是记忆候选探索；仍沿rehabilitation/助手主线重复搜索。';b['unsupported_claims']=['首步content在检索前断言Komi、Tomohito Oda、Gege助手及rehabilitation及well-documented第三次编辑合作，后有自我质疑；这些先前断言没有原题或来源依据。首query本身未写这些实体。']
  if session.endswith('exploratory__r1'):
   b['new_evidence']=[new('5794',['His family consists of one parent and one elder brother.','His hobbies, special skills, pride include skiing, basketball, racket-based ball games, repeated side-steps, doing nothing, getting stomatitis, and health destruction.[1]'],'Endo家庭一名家长一个哥哥，爱好含篮球及持拍球类。','首步已显示Endo与Spy X Family/助手关系，第二步新家庭和运动属性对应原题尚未核验条件。')]
 elif q=='191':
  if 'current' in session:
   b['second_action_grounding']='observation_grounded';b['reason']='首步已见Tim Ellis购店及盲驾关系，第二query使用此候选查TV与MICF，属于有观察依据的核验；未把训练视为已确认。'
   b['new_evidence']=[new('80098',["Tim has acted as magic consultant on several plays, movies and TV series and co-produced 'The Catchpenny Club' for Channel 31 and 'Magical Mystery Tour Downunder' for NHKTV Japan."],'Tim共同制作具体电视节目。','首步仅刊物制作/编辑、Magic Week宣传与购店，未呈现具体电视制作经历；新事实能推进TV背景核验，仍不等于训练已确认。')]
  elif session.endswith('r1'):
   b['second_action_grounding']='observation_grounded';b['reason']='content承认Tim已满足购店、其余待核验，改搜盲驾与电视背景；行动有观察动机但去掉姓名后返回他人事故，无新目标相关依据。'
  else:
   b['second_action_grounding']='repeat_same_need';b['reason']='去掉购店、给盲驾加引号继续原线索，未显式利用Tim候选，返回大多旧来源；更多旧人物背景不构成新题相关条件。'
 elif q=='134':
  b['reason']='content长篇枚举院校贵族候选并称要换方向，实际第二query仍围绕原engineering phrase，未出现新题相关依据。'
  if session.endswith('current__r1') or session.endswith('exploratory__r2'):
   b['unsupported_claims']=['content把原题according to an article改说supervisor wrote an article，原题没有说明导师就是作者。实际query尚未指定文章作者。']
  if session.endswith('exploratory__r2'):
   b['reason']+=' 首步content提出Yoseph Bar-Cohen为候选但未进入query；仅提出待验证候选，不额外计无依据断言。'
 elif q=='692':
  b['reason']='第二query仍重排或加引号同一诊所/迁徙/宿命线索，无具体来源提取或新目标关系。'
  if session.endswith('current__r2'):
   b['first_query_fidelity']='ambiguous';b['first_query_issues']=['关键词缺少主谓，diagnostic clinic与个人文章关系较含混，但未明确置换。']
   b['reason']+=' 第二次将animal缩为birds可由首步多数鸟类材料启发，但未证实目标物种；只是探索方向，不直接计错误前提。'
 B.append(b)
R=dict(method='代理辅助审阅，非human gold、非双盲；预先复核旧source标注并查看实际session，未使用gold或追加API。所有155个去重返回窗口逐一阅读；正例原文精确校验，其他文档未读全文不宣称全局无用。',qids=sorted(Q),annotations=A,source_review=S,behavior=B)
(P/'review_part_c.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n')
print(len(cards),len(S),len(B),len(A))
