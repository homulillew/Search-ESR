"""Actor action arguments are the actual SearchFindTools JSON schemas."""
from copy import deepcopy
import json
from jsonschema import Draft202012Validator
from llm_chat.search_find_agent import SEARCH_FIND_TOOLS

STRATEGIES = ('LOCATE_SOURCE', 'IDENTIFY_CANDIDATE', 'VERIFY_RELATION', 'VERIFY_ATTRIBUTE',
              'DISCRIMINATE_CANDIDATES', 'CROSS_CHECK_CONFLICT', 'LOCALIZE_IN_SOURCE', 'OTHER')


def object_schema(properties, required=None):
    return {'type': 'object', 'properties': properties, 'required': list(properties) if required is None else required,
            'additionalProperties': False}


TEXT = {'type': 'string', 'minLength': 1}
REFS = {'type': 'array', 'items': TEXT, 'uniqueItems': True}


def typed_refs(prefix):
    return {'type': 'array', 'items': {'type': 'string', 'pattern': f'^{prefix}[1-9][0-9]*$'},
            'uniqueItems': True}


# Separate domains for new contracts; legacy non-H role schemas stay unchanged.
WINDOW_REFS = typed_refs('W')
DOCUMENT_REFS = typed_refs('D')
HYPOTHESIS_REFS = typed_refs('H')


def action_schema():
    return {'oneOf': [object_schema({'tool': {'const': t['function']['name']},
                                    'arguments': deepcopy(t['function']['parameters'])}) for t in SEARCH_FIND_TOOLS]}


def decision_schema():
    return {'oneOf': [object_schema({'decision': {'const': 'request_closure'}}), object_schema({
        'decision': {'const': 'acquire'}, 'focus_requirement_id': TEXT, 'one_gap': TEXT,
        'strategy': {'enum': list(STRATEGIES)}, 'hypothesis_ids_under_test': REFS, 'action': action_schema()})]}


def check(value, schema):
    errors = list(Draft202012Validator(schema).iter_errors(value))
    if errors:
        # Do not repair invalid data; the caller archives the original payload.
        raise ValueError('schema: ' + errors[0].message)


def parse_json(text):
    def unique(pairs):
        out = {}
        for k, v in pairs:
            if k in out: raise ValueError('duplicate JSON key: ' + k)
            out[k] = v
        return out
    return json.loads(text, object_pairs_hook=unique, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def validate_action(action, handles):
    check(action, action_schema())
    name, args = action['tool'], action['arguments']
    if 'query' in args:
        q = args['query']
        if not q.strip() or len(q) > 16000: raise ValueError('invalid query length')
    if 'k' in args and type(args['k']) is not int: raise ValueError('k must be integer, not bool/float')
    if name == 'find': handles.resolve_document(args['doc_ref'])
    if name == 'open': handles.resolve_window(args['window_ref'])
    return deepcopy(action)


def validate_decision(value, state, handles):
    check(value, decision_schema())
    if value['decision'] == 'acquire':
        if not value['one_gap'].strip(): raise ValueError('empty OneGap')
        if value['focus_requirement_id'] not in {r.requirement_id for r in state.R}: raise ValueError('unknown R')
        if not set(value['hypothesis_ids_under_test']) <= {h.hypothesis_id for h in state.H}: raise ValueError('unknown H')
        validate_action(value['action'], handles)
    return deepcopy(value)
