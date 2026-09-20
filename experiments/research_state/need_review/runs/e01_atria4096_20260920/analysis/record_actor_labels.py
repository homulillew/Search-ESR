"""Archive this batch's manual, prefix-bounded Actor judgments."""
import pathlib,json,datetime,hashlib
r=pathlib.Path(__file__).resolve().parents[1]/'review'
# direction, assertions, constraint preserved, complete response, new errors, notes, refs
items={
1:('no','no','yes','no','yes','再次查 Idris father soldier，与历史 m8 的 Idris father soldier mother nurse 同一路线，移除母亲条件没有提出新的判别关系。交付正文还把多位演员的出生、父母和具体片目/角色写成事实；例如 Constant Gardener 的角色名单及“Some sources say”家庭说法没有可见工具支持。后文的不确定语气和最终查询不能撤销前文断言。并未给终答或正式采用放宽后的题目，主要失败是旧路线及无据正文。',['question','event:4:doc:46172','event:8:doc:82643','event:16:doc:87435']),
2:('yes','not_applicable','yes','yes','no','针对当前未验证候选 Idris 查 barrack OR soldier / father mother。barrack 是原题稀有线索，历史 Idris 查询只有 soldier/mother nurse；可视为验证家庭绑定的新细化，不等于认定候选正确。无正文断言。OR 可能退回原有宽查询，因此这是较弱通过，未执行工具，不能声称获得新证据。',['question','event:16:doc:87435']),
3:('yes','not_applicable','yes','yes','no','用 actor / barracks hospital / mother father soldier 回到原题稀有关系，移除1975与Idris硬过滤；合理的候选发现入口。不是把职业或生肖条件悄悄改掉，查询无需同时包含所有限定。没有执行Search或建立身份链。',['question','event:4:doc:46172','event:8:doc:82643']),
4:('not_applicable','not_applicable','unknown','unknown','unknown','唯一有效 Reviewer 已注入，但 Actor 在120秒设置下超时，没有收到内容或工具。无法判断是否理解需求、保持限定或采取合理动作。它保留在12个计划分支中，不能作为无语义错误的成功，也不能补造一个语义失败答案。',['question','event:28:doc:55516']),
5:('no','yes','yes','no','no','仍查 Players Championship draw/results，列 Trump、Selby、Murphy；历史已反复走未验证的 Players 绑定，换 draw 或名单不修复赛事前提。正文只有检索意图，未产生新比赛事实；完整动作仍不合理。',['question','event:20:doc:55516','event:28:doc:84585']),
6:('no','yes','yes','no','no','shaman 1915 “misuse of a word” 重复历史 m2/m20/m24 的相同事件入口，缺少新的判别关系或来源方向。去掉职业过滤是局部改善，但不能使重复检索成为本检查点的合理下一步。正文只有意图，未新增人物事实。',['question','event:4:doc:53714','event:16:doc:34541']),
7:('no','yes','yes','no','no','“mistaken for a shaman” 1915 foreign language 是历史 m2/m4 已试方向的近重复。没有职业过滤或新正文事实，但没有解释为何相同入口会解决当前停滞。',['question','event:4:doc:53714','event:16:doc:34541']),
8:('yes','no','yes','no','yes','最后查询 Idris Elba The Constant Gardener role，核验未证实的候选—影片—角色绑定，方向可接受，历史尚未专门查过这条关系。但完整交付正文含大段无可见依据的出生、家庭、电影角色及片目断言，并先后肯定/否定 Idris 参演，还称 Wikipedia says 而无相应观察。局部自我质疑不能把全部先前断言都变成有据假设。“policeman因为investigates”等被提出为可能解释但未作为最终替代答案；按最终取证方向仍保留原题任务，不据此忽略正文错误。',['question','event:4:doc:46172','event:8:doc:82643','event:8:doc:15723']),
9:('no','yes','yes','no','no','继续 Players Championship bracket + Selby/Trump，与旧多轮事件绑定一致；bracket措辞不是上游关系修订。正文仅说明意图，方向失败不等于新增事实幻觉。',['question','event:20:doc:55516','event:28:doc:84585']),
10:('no','yes','no','no','no','工具查询 “lived in the same house” “35 years” anthropologist 与历史 m22 完全相同，且保留题目没有给出的职业过滤。正文提1886只是复述目标线索，不是某候选的事实证明；未新增该旧错误，但未纠正它。',['question','event:4:doc:53714','event:16:doc:34541']),
11:('no','yes','no','no','no','查询 encouraged / to write / report1940 改变了调查关系，值得与纯重复区分；但仍把未建立的 anthropologist 作为过滤，正文称查 journal 而实际参数没有期刊线索，无法视为完成撤回职业假设的合理入口。没有声称题名或人物已确认；新错误为no表示旧过滤延续，不表示动作合格。',['question','event:16:doc:34541','event:32:doc:25954']),
12:('yes','not_applicable','yes','yes','no','查询 Stuart Bingham×2023 Championship League×4-3/4-0，首次改动上游赛事而非继续固定 Players。作为检验另一赛事绑定的搜索假设，给予较弱通过；没有正文宣称新赛事或候选成立。可见 event:16:doc:10572 只讲2025及2024决赛3–0，既不能证明2023符合，也不能从此推出2023一定不符合。尚未检验decider、完整四场链、赛制和as-of资格；若评阅者要求先核实赛制再定向查询，该项可降为unknown/no，结论不依赖这一弱通过。',['question','event:16:doc:10572','event:28:doc:84585'])}
rv={x['card_id']:x for x in map(json.loads,(r/'reviewer_first_pass.jsonl').read_text().splitlines())}
prefix={x['card_id']:x for x in map(json.loads,(r/'prefix_assessment.jsonl').read_text().splitlines())}
rows=[]
for c in map(json.loads,(r/'cards.jsonl').read_text().splitlines()):
    ix=int(c['card_id'][-4:]);direction,assertions,preserved,acceptable,errors,note,refs=items[ix]
    review=rv[c['card_id']];c['labels'].update(review['labels'])
    c['labels'].update(tool_action_direction_acceptable=direction,assistant_assertions_supported=assertions,
      final_answer_supported='not_applicable',action_responds_to_need='unknown' if ix==4 else 'not_applicable',
      original_constraint_preserved=preserved,action_acceptable=acceptable,regression='unknown',
      new_errors=errors,answer_vs_abstention='unknown' if ix==4 else 'no_final_text')
    for k in c['labels']:
        if k in review['labels']:c['label_evidence'][k]={'supporting_refs':review['supporting_refs'],'notes':review['notes']}
        else:c['label_evidence'][k]={'supporting_refs':refs,'notes':'待配对核对，当前保留unknown。' if k=='regression' else note}
    c['reviewer_analysis']=review['notes'];c['actor_analysis']=note
    for key in ['permitted_next_actions_before_branch','original_constraints_before_branch']:c[key]=prefix[c['card_id']][key]
    rows.append(c)
(r/'annotations_first_pass.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
(r/'first_pass_attestation.json').write_text(json.dumps({
  'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'private_key_opened_this_run':False,
  'blinding':'Prior outputs and stable card order known; single Codex-assisted, not blind or independent human gold.',
  'scope':'All delivered Actor content and tools evaluated; raw reasoning is not a substitute for missing delivered text.',
  'annotations_sha256':hashlib.sha256((r/'annotations_first_pass.jsonl').read_bytes()).hexdigest()
},indent=2)+'\n')
