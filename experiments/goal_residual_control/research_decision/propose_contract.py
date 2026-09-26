"""Unexecuted future request contract. Never rewrites frozen requests/results."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
from jsonschema import Draft202012Validator

action_schemas=[]
for tool,args in SCHEMAS.items():
    action_schemas.append({'type':'object','properties':{'tool':{'const':tool},**args['properties']},
      'required':['tool']+args['required'],'additionalProperties':False})
schema={'$schema':'https://json-schema.org/draft/2020-12/schema','type':'object',
  'properties':{'decision':{'enum':['stop','act']},'gap':{'type':'string'},
    'actions':{'type':'array','maxItems':2,'items':{'oneOf':action_schemas}}},
  'required':['decision','gap','actions'],'additionalProperties':False,
  'allOf':[{'if':{'properties':{'decision':{'const':'stop'}}},
    'then':{'properties':{'gap':{'const':''},'actions':{'maxItems':0}}},
    'else':{'properties':{'gap':{'minLength':1},'actions':{'minItems':1}}}}]}
validator=Draft202012Validator(schema)
cases=[
 ({'decision':'stop','gap':'','actions':[]},True),
 ({'decision':'act','gap':'g','actions':[{'tool':'search','query':'q'}]},True),
 ({'decision':'act','gap':'g','actions':[{'tool':'find','doc_ref':'D1','query':'q'},{'tool':'open','window_ref':'W1','direction':'around'}]},True),
 ({'decision':'act','gap':'g','actions':[{'type':'search','query':'q'}]},False),
 ({'decision':'act','gap':'g','actions':[{'tool':'search','arguments':{'query':'q'}}]},False),
 ({'decision':'stop','gap':'','actions':[{'tool':'search','query':'q'}]},False),
 ({'decision':'act','gap':'g','actions':[{'tool':'search','query':'q'}]*3},False),
]
for obj,valid in cases:assert validator.is_valid(obj)==valid
write(TOP/'research_decision/PROPOSED_ACTION_SCHEMA.json',schema)
write(TOP/'research_decision/CONTRACT_CHECKS.json',{'new_model_calls':0,'applied_to_current_requests':False,
 'checks':[{'value':x,'expected_valid':v,'actual_valid':validator.is_valid(x)} for x,v in cases]})
print('7 deterministic proposed-contract checks passed; zero model calls; frozen parser unchanged')
