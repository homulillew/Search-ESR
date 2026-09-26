import itertools,copy
from jsonschema import Draft202012Validator
import capability as c
from capability_extension import compile_schema
from test_capability import negative_actors

def test_equivalent_language():
    rows=negative_actors()+[{'decision':'stop','gap':'','actions':[]}]
    actions=[{'tool':'search','query':'q','k':k} for k in [-1,0,1,5,10,11,'5']]
    actions += [{'tool':'find','doc_ref':d,'query':'q',**({'k':5} if extra else {})} for d,extra in itertools.product(['D1','D99','x'],[False,True])]
    actions += [{'tool':'open','window_ref':'W1','direction':d} for d in ['before','after','around','other']]
    for a in actions:
        for n in range(4):rows.append({'decision':'act','gap':'test','actions':[a]*n})
    old=Draft202012Validator(c.schema('research_actor'));new=Draft202012Validator(compile_schema(c.schema('research_actor')))
    assert all(old.is_valid(x)==new.is_valid(x) for x in rows)
    old=Draft202012Validator(c.schema('state_updater'));new=Draft202012Validator(compile_schema(c.schema('state_updater')))
    for action,claims in itertools.product(['keep','set','clear','other',1],[[],[''],[' '],['a'],['a','b'],['a','b','c']]):
        x={'claims_to_add':claims,'hypothesis_update':{'action':action,'statement':''}}
        assert old.is_valid(x)==new.is_valid(x)

def test_array_bounds_retained():
    s=compile_schema(c.schema('research_actor'))
    assert s['anyOf'][0]['properties']['actions']['maxItems']==0
    assert s['anyOf'][1]['properties']['actions']['minItems']==1
    assert s['anyOf'][1]['properties']['actions']['maxItems']==2
    assert compile_schema(c.schema('state_updater'))['properties']['claims_to_add']['maxItems']==2
