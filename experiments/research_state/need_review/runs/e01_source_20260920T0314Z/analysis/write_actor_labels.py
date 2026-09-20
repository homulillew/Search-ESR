import json,pathlib,datetime,hashlib
r=pathlib.Path('experiments/research_state/need_review/runs/e01_source_20260920T0314Z/review')
# Recorded qualitative judgments, not an automatic semantic evaluator.
# action direction, assertions, final support, response-to-need, constraint preserved, full acceptable, new error, note
N='not_applicable'
data={
1:(N,'no','no','no','no','no','yes','未检索而最终答Idris；承认2013关系缺失后解释用户记错，扩展policeman为security。家庭、出生、完整cast与no overlap均无已见窗口支持。'),
2:('no','no',N,'yes','no','no','yes','搜索父亲soldier/母亲nurse/1975，语义回应家庭需求，但仍把1975硬过滤且正文先确定Idris、编造家庭及cast。请求不是最终答案；开头认定实体仍属于正文断言错误。'),
3:('no','no',N,'no','no','no','yes','改搜David Thewlis父母；正文自己称其1963却原题要求1970s，且把1963/1975当Goat无依据。角色/家庭来自无来源断言，未合理完成需求。'),
4:('no','no',N,'yes','no','no','yes','Query移除Selby但仍锁Players/4-3/4-0；没有纠正赛事绑定且正文补出Liang/Brecel等对阵。对需求主题有响应不等于获得新证据或修正前提。'),
5:('no','yes',N,'yes','yes','no','no','短正文仅要求验证，没有造新事实；但results table与前缀三次Selby×Players查询近重复，未解释为何再查可区分关系，不满足预先合理方向标准。'),
6:('yes','yes',N,N,'yes','yes','no','无效Reviewer未注入，Actor原请求回退后改查1940 American Anthropologist report。该期刊1888起刊有局部来源，查询作为候选探索而非已确定事实；较既往泛journal查询有具体入口。此可接受动作不能归功无效备忘。'),
7:('no','no',N,'yes','no','no','yes','下一查询逐字重复历史message18的anthropologist查询。虽然主题回应找人物需求，但未采用期刊/生平替代入口，正文从候选升为The journal is JAF，来源未建立。'),
8:(N,'no','no','no','no','no','yes','无新观察直接最终答Idris；将policeman、2013导演关系解释为用户混淆，家庭military-adjacent解释无来源。'),
9:('no','yes',N,'yes','yes','no','no','正文仅请求检查，无无据事实；first round opponent score与历史message12基本同方向，继续Selby×Players，没有新关系区分。'),
10:('no','no',N,'yes','no','no','no','Reviewer提醒职业未证实，Actor仍anthropologist biography；主题找人物虽回应，但职业前提未撤回。历史已有类似职业搜索，新增biography没有充分新分岔；人物出生断言沿用未观察内容。'),
11:('no','no',N,'yes','yes','no','no','查询去除anthropologist但仍是历史shaman+word的近重复，仅去掉1915；正文沿旧候选列举及未经来源支持的出生信息。保留题目条件也不等于方向有新价值。'),
12:(N,'no','no','no','yes','no','yes','审查要求验证赛事链，Actor未得新证据即最终答Selby，补出Highfield→Milkins→OConnor→Trump及比分；已见Selby简介只支持局部统计，84585只展示British Open后段，不能支持Players全链。')}
review={x['card_id']:x for x in map(json.loads,(r/'reviewer_first_pass.jsonl').read_text().splitlines())};prefix={x['card_id']:x for x in map(json.loads,(r/'prefix_assessment.jsonl').read_text().splitlines())};out=[]
for c in map(json.loads,(r/'cards.jsonl').read_text().splitlines()):
 n=int(c['card_id'][-4:]); direction,assertions,final,responds,preserved,acceptable,new,note=data[n];rv=review[c['card_id']]
 c['labels'].update(rv['labels']);c['labels'].update(tool_action_direction_acceptable=direction,assistant_assertions_supported=assertions,final_answer_supported=final,action_responds_to_need=responds,original_constraint_preserved=preserved,action_acceptable=acceptable,regression='unknown',new_errors=new,answer_vs_abstention='answer' if final!=N else 'no_final_text')
 for k in c['label_evidence']:
  c['label_evidence'][k]={'supporting_refs':rv['supporting_refs'],'notes':rv['notes'] if k in rv['labels'] else ('待揭示配对后评价。' if k=='regression' else note)}
 c['permitted_next_actions_before_branch']=prefix[c['card_id']]['permitted_next_actions_before_branch'];c['original_constraints_before_branch']=prefix[c['card_id']]['original_constraints_before_branch'];c['reviewer_analysis']=rv['notes'];c['actor_analysis']=note
 assert all(v is not None for v in c['labels'].values());assert c['execution_status']['memo_injected'] or responds==N
 out.append(c)
(r/'annotations_first_pass.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in out))
(r/'first_pass_attestation.json').write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'private_key_opened':False,'reviewer':'single Codex-assisted; metadata masked, not strict blind, prior audits known','annotations_sha256':hashlib.sha256((r/'annotations_first_pass.jsonl').read_bytes()).hexdigest()},indent=2)+'\n')
print('12 cards annotated; group mapping not opened.')
