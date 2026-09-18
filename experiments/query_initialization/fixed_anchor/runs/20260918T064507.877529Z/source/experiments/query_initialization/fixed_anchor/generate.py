"""Fixed-entry expression probe; model never receives the manual control queries."""
import json
from pathlib import Path
from experiments.query_initialization.single_entry.initializer import response_text
from experiments.query_initialization.single_entry.source_units import check_question


def payload(case):
    check_question(case['question'])
    units = case['question']['units']
    refs = case['basis_refs']
    if not refs or not set(refs) <= {u['ref'] for u in units}:
        raise ValueError('Invalid fixed basis')
    return dict(question=case['question']['text'], fixed_target=case['fixed_target'],
                selected_clues=[dict(ref=u['ref'], text=u['text']) for u in units if u['ref'] in refs])


def parse(text):
    try:
        value = json.loads(text)
    except (TypeError, ValueError):
        return None, ['Return a complete JSON object']
    if not isinstance(value, dict) or set(value) != {'query'}:
        return None, ['Return exactly the query field']
    q = value['query']
    if not isinstance(q, str) or not q.strip() or len(q) > 512:
        return None, ['query must be nonempty text <=512 Unicode characters']
    return value, []


def generate(client, config, case):
    messages = [dict(role='system', content=Path(__file__).with_name('PROMPT.txt').read_text()),
                dict(role='user', content=json.dumps(payload(case), ensure_ascii=False))]
    options = dict(model=config.model, stream=False, max_tokens=1536, **config.request_options())
    text = response_text(client.chat.completions.create(**options, messages=messages))
    value, errors = parse(text)
    initial_errors = list(errors)
    if errors:
        messages.extend([dict(role='assistant', content=text or ''), dict(role='user', content=json.dumps(dict(
            instruction='Repair only the output contract using the same fixed clues and target. Do not invent facts. Return only JSON.',
            validation_errors=errors), ensure_ascii=False))])
        value, errors = parse(response_text(client.chat.completions.create(**options, messages=messages)))
    return dict(status='invalid' if errors else 'valid', query=None if errors else value['query'],
                initial_valid=not initial_errors, repairs=int(bool(initial_errors)),
                initial_errors=initial_errors, errors=errors)
