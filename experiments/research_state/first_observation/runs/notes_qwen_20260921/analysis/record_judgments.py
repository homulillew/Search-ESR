from pathlib import Path
import json,datetime,hashlib
r=Path('experiments/research_state/first_observation/runs/notes_qwen_20260921')
cards=json.loads((r/'notes-review/cards.json').read_text());baseline=json.loads((r/'review/observation_first_assessment.json').read_text())
# Entries: source support, subject/relation/scope, concrete-clue relevance, analysis.
J={
'card_1':{'case':'546','notes':[
('yes','yes','yes','同窗连续上下文明示O\'Sullivan第1200次century发生于2023世锦赛第二轮对Vafaei；主体由该窗前文恢复，不借题目绑定，年份保留。支持带主体破百背景，不证明目标球员或完整四场比赛链。'),
('yes','yes','yes','同窗Williams上下文明确Class of92成员、三人及199293赛季转职业；保留原文缺横线写法，不擅自改数值。可用于检验题目1995–2006条件，但笔记没有把Williams认定为目标。'),
('yes','yes','no','来源明确2025年4月14日Page双maximum及147000奖金；statement忠实且保留April2025，因此不是把截止后成绩伪称截止前。问题在选材：晚于2025-01-30，也未连接2023比赛链，却占一条笔记。')],
'coverage':'yes','omissions':'核心破百背景与职业年份已记录。未收Williams超过600centuries/three maximums，属于可改善的资格内容选择，不把未建立的2023四场链算笔记遗漏。第三条可让位给更贴合原题的同窗资格关系。','whole':'no'},
'card_2':{'case':'517','notes':[
('yes','yes','unknown','引用句支持多数中国人/民俗专家倾向Goat；statement增加的Han饲养、邮票及铜像依据来自同一可见窗口后续段，合同允许同窗上下文，不因quote短于statement就判无据。仍只是术语背景，不给出生年份或演员身份，具体用处较弱。'),
('yes','yes','yes','同窗Huang Yi主体、1977上海出生和父母离异后随祖父母成长均明确。属于1970s条件部分重合，不能升级为目标候选已确认。页面日期2024晚于题目截至2023；笔记没有声称当时已知，但后续若使用须复核时间口径。'),
('yes','yes','unknown','Zhao2005凭A Time to Love获三奖的原句完整支持；没有替她补警察角色、父母或生肖。与2005电影只部分同年，离具体角色/导演关系仍远，不能因有年份就证明调查价值。')],
'coverage':'not_applicable','omissions':'本批窗口没有家庭军营医院、2005警察、Iracema导演或2013电影的明确连接；未出现的信息不算笔记遗漏。Huang出生年代及生肖术语已记录，无发现明确关键局部关系被漏掉。整体检索关联偏弱。','whole':'unknown'},
'card_3':{'case':'71','notes':[
('yes','yes','yes','同窗明确Ballast Bank人造岛、装卸ballast及其稳定无货船的用途；statement没有把受稳定对象改为港口/岛，主体与功能关系保留。'),
('unknown','unknown','yes','1905数值及Bank/Hotel双方主体有直接来源。问题是把单一酒店页面称Historical accounts，并用adjacent替代opposite；未明确宣称独立多源验证，不能断言硬性捏造多份史料，但历史来源范围含混。严格保真保留unknown；若accounts只是泛称该页面，本条核心事实可判yes。不是判1905为假，也没有用另一窗替换年份。'),
('unknown','unknown','yes','名称与命名原因可由该同窗前面的name one...after...支持，不能只因所选quote只提warehouse而判命名无据。风险在operates at the site：可指旧bonded warehouse/bar场址，也可被读成结构岛上；页面仅说岛在酒店对面，没证明餐吧在岛上。不强行选错读，位置范围记unknown；若site指仓库，主体/关系可以接受。')],
'coverage':'yes','omissions':'用途、1905说法、命名关联三个核心均保留。另一窗晚19世纪已改作煤储存的时间张力未被记录，作为跨来源冲突的次级遗漏提示；3条上限不要求每个条件，且该窗没有明确19世纪建造年份，不能补成确定日期。','whole':'unknown'},
'card_4':{'case':'519','notes':[
('no','no','yes','作者—书名—Vienna Café喝茶回忆由引用句直接支持，相遇地点BBC由同窗文章叙述支持。但statement将BBC相遇也嵌入which contains...这个书内容归属中；窗口只明确茶/蛋糕那段引自该书，没有明确BBC相遇叙述来自书中。严格来源层级口径下多走了一步，source_support=no；不是说作者/书名错误，也不是禁止利用同窗解析人物。若将此句宽读成整篇文章所述经历，核心线索仍有用，但书内容归属不能据此证明。')],
'coverage':'yes','omissions':'核心书名/作者及茶会关系已保存。一女Katy、Lila在BBC工作未单独列出，属于次级可选补充；英国civil/教堂婚礼、作者生日PhD和2010前出版不在窗口，不能记为遗漏。','whole':'no'},
'card_5':{'case':'776','notes':[
('no','unknown','yes','quote仅为正文中的小节标题Early life(1886–1910)。模型说early life began in1886，并没有直接写born in1886，不能夸大成明确出生断言。但它把标题时期改为生平起点，缺少叙述句支持；按本轮titles-alone不足的严格合同，来源支持=no、时间范围unknown。若允许仅复述小节起始年，本条可放宽为yes；不据此断言真实出生年错误。'),
('yes','yes','yes','引用明确1915年4月13日至11月8日Jenness在southern Victoria Island旅行，diary背景也在同一窗口。只写Jenness而未借另一窗拼全名，保留日期/主体/地点，是原题旅行线索的强支持；没有补shaman或鼓励关系。'),
('yes','yes','no','同窗Benedict姓名、Regarded by many...与Patterns of Culture1934支持statement。原题无职业限定，本条未连接1886/1915/鼓励关系/1940报告；只是邻近文化主题人物，选材价值弱，不是来源事实错误。')],
'coverage':'yes','omissions':'核心Jenness精确旅行关系已保留。Copper Inuit同行者、1922/1928书名可辅助后续但不要求穷尽；误用词、35年同屋、三孩子、1940目标标题均不在本批窗口。','whole':'no'},
'card_6':{'case':'191','notes':[
('yes','yes','yes','同窗明确Tim Ellis performer/author/lecturer inmagic，主体职业忠实，不把其他人的职业移给他。'),
('yes','yes','yes','同窗Ellis代词可由正文解析；1992购买Bernard\'s Magic Shop和持有数年均明确，是原题购店条件的强支持，未宣布他满足全题。'),
('yes','unknown','unknown','Justin Hamilton职业串和某晚host由窗口支持，没有把属性拼给Ellis，也没有说Hamilton接受TV producer/editor训练。但来源明确是2025 Roadshow，statement省略2025，容易被放进题目截至2023的资格判断。因未明确作as-of2023断言，不算已证实时间造假，必要时间范围/实际相关性记unknown。')],
'coverage':'yes','omissions':'Ellis购店与performer核心已保留。Australian Magic Monthly编辑关系没选，不应冒充TV训练；蒙眼驾驶及Ellis喜剧节主持未见，不算遗漏。','whole':'unknown'}
}
rows=[]
for c in cards:
 j=J[c['card_id']];notes=json.loads(c['delivered'][0]['message']['content'])['notes'];assert len(notes)==len(j['notes'])
 assessments=[]
 for i,(note,(support,scope,relevance,analysis)) in enumerate(zip(notes,j['notes']),1):
  w=next(w for w in c['observation'] if w['window_ref']==note['source_ref']);assert note['quote'] in w['text']
  assessments.append({'index':i,'note':note,'source_support':support,'subject_relation_scope':scope,'concrete_clue_relevance':relevance,'analysis':analysis,'window_ref':w['window_ref'],'quote_is_body_substring':True})
 def aggregate(axis):
  vals=[x[axis] for x in assessments]
  return 'no' if 'no' in vals else 'unknown' if 'unknown' in vals else 'yes'
 c['labels'].update(source_support=aggregate('source_support'),subject_relation_scope=aggregate('subject_relation_scope'),useful_information_coverage=j['coverage'],next_action_uses_observation='not_applicable',new_unsupported_claim='yes' if aggregate('source_support')=='no' else 'unknown' if aggregate('subject_relation_scope')=='unknown' else 'no',whole_action_reasonable='not_applicable')
 c.update(case_id=j['case'],note_assessments=assessments,whole_note_set_acceptable=j['whole'],omission_analysis=j['omissions'],observation_first_assessment=baseline['cases'][j['case']])
 c['evidence']=[{'source_ref':n['note']['source_ref'],'quote':n['note']['quote'],'notes':n['analysis']} for n in assessments];rows.append(c)
(r/'review/annotations_first_pass.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
(r/'review/first_pass_attestation.json').write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'evaluator':'single Codex-assisted, known development cases, not blind/human gold','preceding_observation_review':baseline['created_at'],'mapping_opened':False,'scope':'All16 delivered notes, full30 visible windows; no private reasoning or unseen source used. Strict title-only and source-layer attribution judgments include explicit sensitivity.','sha256':hashlib.sha256((r/'review/annotations_first_pass.json').read_bytes()).hexdigest()},indent=2)+'\n')
