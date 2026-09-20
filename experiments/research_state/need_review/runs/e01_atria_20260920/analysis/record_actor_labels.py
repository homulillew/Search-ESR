"""Archive single-Codex qualitative judgments; not an automatic evaluator."""
import pathlib,json,datetime,hashlib
r=pathlib.Path(__file__).resolve().parents[1]/'review'
# direction, constraint preservation, note, supporting prefix refs
items={
1:('yes','yes','针对母亲barracks hospital原题稀有短语寻找演员，不再把1975或Idris当硬过滤。比历史多条件猜测查询更集中，方向可接受；没有执行Search，家庭链仍未建立。',['question','event:4:doc:46172','event:8:doc:82643']),
2:('yes','yes','查The Constant Gardener的policeman演员，是核查角色关系的入口，不预先选Idris、也不放宽policeman。电影绑定仍是待检验搜索假设，不能作为已确认事实或最终答案。',['question','event:4:doc:46172','event:8:doc:82643']),
3:('yes','yes','查barracks hospital/actor/mother原题线索，取消历史1975硬过滤；精准措辞可能漏召回，但此时是合理新入口，不能把尚未运行的召回结果当成成功。',['question','event:4:doc:46172','event:8:doc:15723']),
4:('no','yes','仍在Players事件绑定下并列此前Selby/Trump/Bingham，draw results与多次旧结果查询近重复，未说明可区分的新关系。正文只有搜索意图，没有造比赛事实；未推进不等于命题错误。',['question','event:20:doc:55516','event:28:doc:84585']),
5:('yes','yes','首次提出get_document读取已见55516，从offset0扩到12000字符；该人物页面现只展示1600字符，继续核查2023关系是合理取证尝试。尚不知道前12000字符是否含相关赛事，不能假称已获得新事实。',['question','event:20:doc:55516']),
6:('yes','yes','转向1940年JAF报告入口；期刊仍只是探索候选，查询未断言已经锁定。较既往泛journal/1888组合更具体，是允许的报告侧反向取证；官方题名仍未知。',['question','event:16:doc:34541','event:32:doc:25954']),
7:('no','no','出生1886和3children都来自原题，但继续用未证实anthropologist过滤；历史已试人物家庭组合与职业路线，此查询没有撤回限制。无新正文断言，评价的是方向/约束而非姓名正确性。',['question','event:4:doc:53714','event:16:doc:34541']),
8:('yes','yes','用barracks hospital短语查actor mother，未固定1975、Idris或把警察解释为security。与另一独立分支查询相同不算同一历史内重复；两分支互不可见。',['question','event:4:doc:46172','event:8:doc:82643']),
9:('no','yes','仍在Players绑定下并列Selby/Trump/Bingham/Murphy，bracket results未纠正未经证实赛事；与旧多轮该赛事结果路线近重复。没有伴随正文事实，不能标为新事实幻觉。',['question','event:20:doc:55516','event:28:doc:84585']),
10:('no','no','shaman/1915/misuse/word/foreign language接近历史第一条需求，又加旧anthropologist过滤；只是同一路线重组，没有合理的新分岔。正文只是查询意图，不是人物事实。',['question','event:4:doc:53714','event:16:doc:34541']),
11:('yes','yes','改用原题35years、3children、born1886三项联合，不带职业。历史分别查过部分组合，本次把具体居住年数和子女数联合起来，作为传记入口的细化可以接受；边界判断较弱，不能保证新召回。',['question','event:4:doc:53714','event:20:doc:46003']),
12:('no','yes','改查Neil Robertson但保留Players/4-3/4-0绑定，候选变化本身不足以修复上游赛事前提。仅探索姓名不算新错误事实，仍不满足本批合理方向标准。',['question','event:20:doc:55516','event:28:doc:84585'])}
rv={c['card_id']:c for c in map(json.loads,(r/'reviewer_first_pass.jsonl').read_text().splitlines())};prefix={c['card_id']:c for c in map(json.loads,(r/'prefix_assessment.jsonl').read_text().splitlines())};out=[]
for c in map(json.loads,(r/'cards.jsonl').read_text().splitlines()):
 d,p,note,refs=items[int(c['card_id'][-4:])];msg=c['actor_response']['choices'][0]['message'];assert msg.get('tool_calls');assert not c['execution_status']['memo_injected']
 c['labels'].update(rv[c['card_id']]['labels']);c['labels'].update(tool_action_direction_acceptable=d,assistant_assertions_supported='yes' if msg.get('content') else 'not_applicable',final_answer_supported='not_applicable',action_responds_to_need='not_applicable',original_constraint_preserved=p,action_acceptable=d,regression='unknown',new_errors='no',answer_vs_abstention='no_final_text')
 for k in c['labels']:
  c['label_evidence'][k]={'supporting_refs':[] if k in rv[c['card_id']]['labels'] else refs,'notes':rv[c['card_id']]['notes'] if k in rv[c['card_id']]['labels'] else ('待配对核对；不把回退间差异归因Reviewer。' if k=='regression' else note)}
 c['reviewer_analysis']=rv[c['card_id']]['notes'];c['actor_analysis']=note
 c['permitted_next_actions_before_branch']=prefix[c['card_id']]['permitted_next_actions_before_branch'];c['original_constraints_before_branch']=prefix[c['card_id']]['original_constraints_before_branch'];out.append(c)
(r/'annotations_first_pass.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in out));(r/'first_pass_attestation.json').write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'private_key_opened_this_run':False,'blinding':'Not blinded: prior output, task purposes and stable card order known; labels are single-Codex assistance.','evaluation_scope':'Actor content and proposed tools; reasoning preserved raw, not substituted for an absent delivered Reviewer JSON or user-visible assertions.','annotations_sha256':hashlib.sha256((r/'annotations_first_pass.jsonl').read_bytes()).hexdigest()},indent=2)+'\n')
