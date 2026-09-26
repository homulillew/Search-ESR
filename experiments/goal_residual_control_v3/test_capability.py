import copy,json
import pytest
from jsonschema import Draft202012Validator,ValidationError
import capability as c

@pytest.mark.parametrize('obj',[
 {'decision':'stop','gap':'','actions':[]},
 {'decision':'act','gap':'test','actions':[{'tool':'search','query':'x','k':5}]},
 {'decision':'act','gap':'test','actions':[{'tool':'find','doc_ref':'D1','query':'x'}]},
 {'decision':'act','gap':'test','actions':[{'tool':'open','window_ref':'W1','direction':'around'}]},
 {'decision':'act','gap':'test','actions':[{'tool':'search','query':'x','k':1},{'tool':'search','query':'y','k':10}]},
])
def test_valid_actor(obj):
 Draft202012Validator(c.schema('research_actor')).validate(obj)
 Draft202012Validator(c.transport_equivalent(c.schema('research_actor'))).validate(obj)

def negative_actors():
 good={'decision':'act','gap':'test','actions':[{'tool':'search','query':'x','k':5}]}
 rows=[]
 for key in ['decision','gap','actions']:
  o=copy.deepcopy(good);del o[key];rows.append(o)
 for k in [0,11,1.5,True,'5']:
  o=copy.deepcopy(good);o['actions'][0]['k']=k;rows.append(o)
 for patch in [{'extra':1},{'decision':'invent'},{'gap':''},{'actions':[]},{'actions':[good['actions'][0]]*3},{'decision':'stop'}]:rows.append(good|patch)
 rows.extend([good|{'actions':[{'tool':'find','doc_ref':'D1','query':'x','k':5}]},
 good|{'actions':[{'tool':'find','doc_ref':'invalid','query':'x'}]},
 good|{'actions':[{'tool':'open','window_ref':'W1','direction':'sideways'}]},
 good|{'actions':[{'name':'search','arguments':{'query':'x','k':5}}]},
 {'decision':'stop','gap':'test','actions':[]}])
 return rows

@pytest.mark.parametrize('obj',negative_actors())
def test_reject_and_equivalent_actor(obj):
 for s in [c.schema('research_actor'),c.transport_equivalent(c.schema('research_actor'))]:
  with pytest.raises(ValidationError):Draft202012Validator(s).validate(obj)

@pytest.mark.parametrize('action',['keep','set','clear'])
def test_updater_valid(action):
 Draft202012Validator(c.schema('state_updater')).validate({'claims_to_add':[],'hypothesis_update':{'action':action,'statement':'candidate' if action=='set' else ''}})

@pytest.mark.parametrize('patch',[{'claims_to_add':['a','b','c']},{'claims_to_add':[' ']},{'extra':1},{'hypothesis_update':{'action':'invent','statement':''}}])
def test_updater_invalid(patch):
 with pytest.raises(ValidationError):Draft202012Validator(c.schema('state_updater')).validate({'claims_to_add':[],'hypothesis_update':{'action':'keep','statement':''}}|patch)

def test_registry_separate():
 from experiments.goal_residual_control.harness_v2.contracts import validate_object
 obj={'decision':'act','gap':'test','actions':[{'tool':'find','doc_ref':'D99','query':'x'}]}
 Draft202012Validator(c.schema('research_actor')).validate(obj)
 with pytest.raises(ValueError,match='unknown_prebatch_document'):validate_object(obj,'research_actor',{'known_documents':[],'observed_windows':[]})

def test_historical_coverage_and_mapping():
 rows=c.select_history();assert len(rows)==24
 assert len({r['id'] for r in rows})==24
 cats={cat for r in rows for cat in r['categories']}
 assert cats=={'actor_stop','actor_search','actor_find','actor_open','actor_two','updater_keep','updater_set','updater_clear','goal_true','goal_false'}
 for r in rows:
  req=c.responses_request(r['old_request'],c.schema(r['kind']),r['kind'])
  assert req['input']==r['old_request']['messages']
  assert req['model']==r['old_request']['model']=='deepseek-flash'
  assert req['text']['format']['schema']==c.schema(r['kind'])
  assert 'temperature' not in req and 'reasoning' not in req and 'max_output_tokens' not in req

def test_no_repair():
 with pytest.raises(json.JSONDecodeError):c.decode({'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':'{"x":1,}'}]}]},'responses')
 with pytest.raises(ValueError,match='incomplete'):c.decode({'status':'incomplete','output':[]},'responses')

@pytest.mark.parametrize('obj',[{'resolved':True,'residual':''},{'resolved':False,'residual':'need'}])
def test_goal_valid(obj):Draft202012Validator(c.schema('goal_reviewer')).validate(obj)

@pytest.mark.parametrize('obj',[{'resolved':'true','residual':''},{'resolved':True},{'resolved':True,'residual':'','extra':1}])
def test_goal_invalid(obj):
 with pytest.raises(ValidationError):Draft202012Validator(c.schema('goal_reviewer')).validate(obj)
