import copy, json
import pytest
from runtime import schema, validate, request, decode, TOP, ROOT
from jsonschema import Draft202012Validator

def test_historical_outputs_and_verbatim_context():
    rows=json.loads((ROOT/'experiments/goal_residual_control_v3/structured_output_preflight/HISTORICAL_REQUESTS.json').read_text())
    assert len(rows)==24
    for r in rows:
        out=r['old_output'];view=json.loads(r['old_request']['messages'][1]['content'])
        validate(out,r['kind'],view)
        for mode in ['responses_structured','json_mode_fallback']:
            req=request(r['old_request'],r['kind'],mode)
            assert req.get('input',req.get('messages'))==r['old_request']['messages']

@pytest.mark.parametrize('action',[
 {'tool':'find','doc_ref':'D1','query':'year','k':5},
 {'tool':'search','query':'year'},
 {'tool':'open','window_ref':'W1','direction':'invalid'},
 {'tool':'find','doc_ref':'D1','query':7}])
def test_branch_shape_rejected(action):
    with pytest.raises(Exception):Draft202012Validator(schema('research_actor')).validate({'decision':'act','gap':'year','actions':[action]})

@pytest.mark.parametrize('out,kind',[
 ({'decision':'act','gap':'year','actions':[{'tool':'search','query':'x','k':5}]*3},'research_actor'),
 ({'decision':'stop','gap':'year','actions':[]},'research_actor'),
 ({'claims_to_add':['a','b','c'],'hypothesis_update':{'action':'keep','statement':''}},'state_updater'),
 ({'claims_to_add':[],'hypothesis_update':{'action':'set','statement':''}},'state_updater'),
 ({'resolved':True,'residual':'missing year'},'goal_reviewer')])
def test_structural_success_is_not_harness_success(out,kind):
    Draft202012Validator(schema(kind)).validate(out)
    with pytest.raises(Exception):validate(out,kind,{})

def test_unknown_prebatch_handle():
    with pytest.raises(ValueError,match='unknown_prebatch_document'):
        validate({'decision':'act','gap':'year','actions':[{'tool':'find','doc_ref':'D2','query':'year'}]},'research_actor',
          {'Available Workspace':{'known_documents':[{'doc_ref':'D1'}],'observed_windows':[]}})

def test_no_repair_or_incomplete_acceptance():
    with pytest.raises(json.JSONDecodeError):decode({'choices':[{'finish_reason':'stop','message':{'content':'```json\n{}\n```'}}]},'json_mode_fallback')
    with pytest.raises(RuntimeError):decode({'status':'incomplete'},'responses_structured')
