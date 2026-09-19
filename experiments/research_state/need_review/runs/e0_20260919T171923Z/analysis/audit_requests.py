import json,hashlib,collections
from pathlib import Path
from experiments.research_state.need_review.run import load_prompts
from experiments.research_state.need_review.node import build_actor_request,build_review_request
from experiments.research_state.need_review.checkpoint import digest
R=Path(__file__).resolve().parents[1];M=json.loads((R/'manifest.json').read_text());P={k:(R/'prompts'/f'{k}.txt').read_text() for k in ['generic_review','need_review','memo']};plan=json.loads((R/'preflight/plan.json').read_text())
assert all(M[k]==v for k,v in plan.items() if k!='schema_version')
rows=[];group={a:collections.Counter() for a in 'ABC'}
for item in M['schedule']:
 d=R/'branches'/item['sample_id'];r=json.loads((d/'result.json').read_text());cp=json.loads((R/'checkpoints'/(item['checkpoint_id']+'.json')).read_text());events=[json.loads(l) for l in (d/'events.jsonl').read_text().splitlines()]
 original=cp['request'];assert digest(original)==cp['request_sha256']==r['request_sha256']
 note=(r.get('review') or {}).get('raw_text') if r['memo_injected'] else None
 expected=build_actor_request(cp,note,P['memo'])
 assert r['actor']['request']==expected
 assert expected['messages'][:len(original['messages'])]==original['messages']
 assert {k:v for k,v in expected.items() if k!='messages'}=={k:v for k,v in original.items() if k!='messages'}
 reqs=[e for e in events if e['kind']=='request'];assert len(reqs)==r['logical_requests']
 for e in reqs:assert e['request']==r[e['stage']]['request']
 if item['arm']!='A':
  req=build_review_request(cp,item['arm'],P['generic_review' if item['arm']=='B' else 'need_review'],max_tokens=512)
  assert req==r['review']['request']
 a=r['actor'];cl=a.get('classification',{});g=group[item['arm']];g['branches']+=1;g['logical_calls']+=r['logical_requests'];g['actor_errors']+=a['status']!='ok';g['fallbacks']+=item['arm']!='A' and not r['memo_injected'];g['protocol_incompatible']+=cl.get('protocol_compatible') is False
 g['review_invalid']+=item['arm']!='A' and not (r.get('review') or {}).get('valid',False)
 rec={**item,'memo_injected':r['memo_injected'],'actor_classification':cl,'review_status':(r.get('review') or {}).get('status'),'review_errors':(r.get('review') or {}).get('errors'),'review_usage':(r.get('review') or {}).get('usage'),'actor_usage':a.get('usage'),'seconds':{},'prefix_match':True,'actor_parameter_diff':[],'actor_messages_added':len(expected['messages'])-len(original['messages'])}
 for stage in ['review','actor']:
  call=r.get(stage)
  if call:
   rec['seconds'][stage]=call.get('elapsed_seconds');g['seconds']+=call.get('elapsed_seconds',0)
   g[stage+'_calls']+=1
   g['api_errors']+=call['status']=='api_error'
   for key in ['prompt_tokens','completion_tokens','total_tokens']:g[stage+'_'+key]+=(call.get('usage') or {}).get(key,0)
 rows.append(rec)
report={'all_18_prefixes_exact':True,'all_actor_nonmessage_parameters_unchanged':True,'plan_matches_execution':True,'tool_executions':0,'groups':{k:dict(v) for k,v in group.items()},'rows':rows}
(R/'integrity_and_cost.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report['groups'],indent=2))
