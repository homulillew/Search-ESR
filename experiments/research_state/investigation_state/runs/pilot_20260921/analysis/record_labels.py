"""Record single-Codex judgments before opening the current pairing map."""
import pathlib,json,datetime,hashlib
r=pathlib.Path(__file__).resolve().parents[1]/'review'
prefix={c['card_id']:c for c in map(json.loads,(r/'prefix_assessment.jsonl').read_text().splitlines())}
rows=[]
for c in map(json.loads,(r/'cards.jsonl').read_text().splitlines()):
    labels={k:'not_applicable' for k in c['labels']};labels['regression']='unknown';refs=['question']
    if c['delivered_response'] is None:
        labels['complete_response_acceptable']='unknown'
        note='API超时，没有收到交付响应或usage。来源、任务使用、工具方向等没有可评对象，保留计划分母及未知成本，不补造模型语义错误。'
    elif not c['execution']['semantic_eligible']:
        assert all(not x['message'].get('content') and not x['message'].get('tool_calls') for x in c['delivered_response'])
        note='finish_reason=length，正文和工具提议均为空；原始响应有reasoning但未交付可消费决策。语义轴不适用，全分母记录为交付失败，不把reasoning当正文评分。'
    elif c['card_id']=='card_0003':
        labels.update(complete_response_acceptable='no',source_attribution_correct='yes',relation_scope_preserved='yes',
          task_used_in_decision='yes',tool_direction_reasonable='yes',repetition_has_new_purpose='yes',
          body_assertions_supported='no',new_error_introduced='yes')
        refs=['question','event:4:doc:46172','event:8:doc:82643','m2','task']
        note=('三个调用分别核验Constant Gardener警察角色、Fifth Estate演员表及1979出生/家庭线索；前两个直接使用当前调查目的，第三个是辅助生平入口，整个工具批次作为探索合理。既有工具尚未查过角色/同一演员关系，不能因同电影词重复而判旧路线循环。正文把旧1975/Idris绑定称为suspect，正确保留其假设身份，没有假称导演原文证明演员。'
              '但它以确定语气补入1975=Rabbit、1979及early1980=Goat的历法断言，给定前缀和笔记没有此换算依据。本批严格的可见证据口径下正文支持=no、完整响应=no、新的未验证出生年限定=yes；这不等于证明生肖常识本身错误。early1980只是括号说明，实际query仍1979，未据此判它已经把目标改成1980年出生。若允许基础生肖常识作为外部背景，这项可改为通过；两种口径都不支持视图带来稳定收益。没有最终身份答案或工具结果。')
    elif c['card_id']=='card_0006':
        labels.update(complete_response_acceptable='yes',source_attribution_correct='yes',relation_scope_preserved='yes',
          task_used_in_decision='yes',tool_direction_reasonable='yes',repetition_has_new_purpose='yes',new_error_introduced='no')
        refs=['question','event:4:doc:46172','event:8:doc:82643','task']
        note=('三个Search分别查Constant Gardener警察演员、Fifth Estate演员表、含Meirelles的Constant Gardener警察角色。把影片作为检验入口，未断言已核实具体演员，未锁定Idris或1975，也未放宽policeman。前缀虽反复猜演员，但此前没有专查这组角色/跨影片关系，具体调查目的体现在请求中，整个批次合理。第一与第三个调用高度相近，可能冗余；增加导演名与police officer措辞可视为召回变体，尚无结果，不能仅凭相似字符串宣判无益。空正文不扣分，正文支持轴不适用。无新来源、无终答，家庭、生肖和同一演员链仍未知。')
    else:raise AssertionError('Unexpected delivered card; inspect manually before labeling')
    c['labels']=labels;c['analysis']=note
    for key in labels:c['label_evidence'][key]={'refs':refs,'notes':'待独立标签完成后配对，当前unknown。' if key=='regression' else note}
    for key in ['permitted_next_actions_before_output','original_constraints','evidence_boundaries']:c[key]=prefix[c['card_id']][key]
    rows.append(c)
(r/'annotations_first_pass.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in rows))
(r/'first_pass_attestation.json').write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'private_key_opened_this_run':False,'view_mechanical_status_already_known':True,
  'evaluator':'single Codex-assisted; fixture authors/old cases known, not blind or independent human gold',
  'scope':'Full delivered content and all tool proposals; no private reasoning substituted; external calendar lookup not used to retroactively support the response.',
  'sha256':hashlib.sha256((r/'annotations_first_pass.jsonl').read_bytes()).hexdigest()},indent=2)+'\n')
