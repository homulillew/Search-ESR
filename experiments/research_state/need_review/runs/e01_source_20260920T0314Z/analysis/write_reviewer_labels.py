import json,pathlib,datetime,hashlib
r=pathlib.Path('experiments/research_state/need_review/runs/e01_source_20260920T0314Z/review')
notes={
1:('no','no','把历史assistant的父亲护士/母亲health advisor写成visible evidence；所引Meirelles/Condon窗口不支持该家庭关系。再把1975固定为Goat出生年。未找到候选不能据此修改原题父母条件。',['question','event:4:doc:46172','event:8:doc:15723']),
2:('no','no','与card0001同类：历史assistant的家庭说法升级为visible evidence；1975来自历史猜测。若未找到其他候选就重解释角色不构成平衡证据判断。',['question','event:4:doc:46172','event:8:doc:15723']),
3:('no','no','护士/health advisor不是已见tool对Idris的发现；Evaristo文章不支持Idris家庭。1975硬过滤及找不到别人就重解释policeman，保留了污染来源。',['question','event:4:doc:46172','event:8:doc:15723','event:16:doc:87435']),
4:('no','no','正确指出Selby×Players是假设，却规定该赛事不符就排除整个人选；把<250扩到多个对手，并无已见Trump/Bingham统计依据。这是关系支持范围错误。',['question','event:20:doc:55516','event:8:doc:4975']),
5:('no','no','当前赛事绑定未建立；Players结果不匹配最多否定该绑定，不能must reject Selby。局部Selby统计不建立赛事链。',['question','event:20:doc:55516']),
6:('no','no','无效引用event:4:doc:34541不在索引；仅event:16存在。原始文本仍可诊断：允许1887 close but not1886违反原题；Benedict窗口不支持出生1887。机械失败不冒充可用审查。',['question','event:16:doc:34541','event:32:doc:25954']),
7:('yes','yes','明确把两期刊绑定作为未建立前提，而非事实。1888起刊局部支持见34541，不证明具体报告；需求仍较宽，但允许查其他期刊、换传记线索，不改原题。',['question','event:4:doc:53714','event:16:doc:34541']),
8:('no','no','current_assumption正确描述历史的宽松解释，但next_need又把1975当Goat事实，并把两部影片的交集改成or。没有别的候选只保持弱假说，不提供充分的反证/条件检验。',['question','event:4:doc:46172','event:8:doc:82643']),
9:('no','no','Players绑定未证实却用其不匹配推断整个人选likely incorrect；将<250扩到连续多个对手，且称Trump/Bingham满足统计无窗口支持。',['question','event:20:doc:55516']),
10:('yes','no','正确识别anthropologist/folklorist只是历史搜索职业过滤，没有升级为来源发现；但无结果就修订shaman clue风险仍在，需求几乎重述人物链，缺少细粒度分岔。',['question','event:4:doc:53714','event:16:doc:34541','event:32:doc:25954']),
11:('yes','unknown','职业假设归属正确；需求未解决但很宽。若无此人存在才换解释并非直接把未检索到当不存在，不过没有给出如何建立不存在，decision_effect证据门槛不清。',['question','event:4:doc:53714','event:16:doc:34541','event:44:doc:28281']),
12:('yes','yes','解除Players预绑定，准确区分Selby局部统计与2023完整比赛链；允许验证或换其他人，未以未搜到直接排除。仍需保留首个对手<250及as-of统计，不能仅序列吻合就完整定案。',['question','event:20:doc:55516','event:28:doc:84585'])}
rows=[]
for n,(source,balanced,note,refs) in notes.items():
 rows.append({'card_id':f'card_{n:04d}','labels':{'review_source_attribution_correct':source,'assumption_grounded':'yes','need_unresolved':'yes','need_decision_relevant':'yes','need_already_answered':'no','decision_effect_balanced':balanced},'notes':note,'supporting_refs':refs,'scope':'raw review diagnostic; invalid review retained, not counted as valid success'})
(r/'reviewer_first_pass.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
(r/'reviewer_first_pass_attestation.json').write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actor_outputs_read':False,'private_key_opened':False,'reviewer':'single Codex-assisted; prior audits known; not blinded human gold','sha256':hashlib.sha256((r/'reviewer_first_pass.jsonl').read_bytes()).hexdigest()},indent=2)+'\n')
