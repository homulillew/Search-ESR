import json
from types import SimpleNamespace
from experiments.query_initialization.initializer import validate,parse,normalize,generate


def direction(query='person studied art',clue='studied art'):
    return dict(goal='Find the person',source_clues=[clue],query=query)


def test_exact_source_and_relationships_are_not_guessed_by_validator():
    q='Her mother studied art. Her father was a teacher.'
    assert validate({'directions':[direction()]},q,1)==[]
    assert validate({'directions':[direction(clue='her mother studied art')]},q,1)
    assert validate({'directions':[direction(query='father studied art')]},q,1)==[]  # Semantic fidelity is separately reviewed.


def test_empty_and_underfilled_are_allowed_but_extra_directions_are_not():
    assert validate({'directions':[]},'studied art',2)==[]
    assert validate({'directions':[direction()]},'studied art',2)==[]
    assert validate({'directions':[direction(),direction('person taught art')]},'studied art',1)


def test_duplicate_normalization_does_not_remove_negation_or_digits():
    ds=[direction('  ART  2012 '),direction('art 2012')]
    assert validate({'directions':ds},'studied art',2)
    assert normalize('not art 2012')!=normalize('art 2012')
    assert normalize('art 2013')!=normalize('art 2012')


def test_invalid_types_and_partial_json_fail_without_salvage():
    assert parse('```json\n{}\n```','q',1)[1]
    assert parse('{"directions":[','q',1)[1]
    assert validate({'directions':[dict(goal='g',query='x'*513,source_clues=['q'])]},'q',1)


class FakeClient:
    def __init__(self,contents):self.contents=iter(contents);self.requests=[];self.chat=SimpleNamespace(completions=self)
    def create(self,**kwargs):
        self.requests.append(json.loads(json.dumps(kwargs)))
        return SimpleNamespace(choices=[SimpleNamespace(finish_reason='stop',message=SimpleNamespace(content=next(self.contents),tool_calls=None))])


def test_only_one_repair_and_no_retrieval_feedback():
    cfg=SimpleNamespace(model='fake',request_options=lambda:{})
    c=FakeClient(['not json',json.dumps({'directions':[direction()]})])
    result=generate(c,cfg,'A person studied art.','C')
    assert result['status']=='underfilled' and result['repairs']==1 and len(c.requests)==2
    assert 'validation_errors' in c.requests[1]['messages'][-1]['content']
    c=FakeClient(['not json','still not json']);assert generate(c,cfg,'q','B')['status']=='invalid'


def test_zero_directions_never_forces_repair():
    cfg=SimpleNamespace(model='fake',request_options=lambda:{})
    c=FakeClient(['{"directions":[]}']);r=generate(c,cfg,'q','C')
    assert r['status']=='no_direction' and r['repairs']==0 and len(c.requests)==1
