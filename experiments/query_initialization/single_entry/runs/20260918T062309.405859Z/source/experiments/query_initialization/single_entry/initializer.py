"""Single-entry variants; no retrieval, semantic judge, candidate state, or replanner."""
import json
from pathlib import Path
from experiments.query_initialization import initializer as previous
from .source_units import check_question, model_input

ARMS = ('v2', 'refs_goal', 'refs', 'minimal')


def system_prompt(arm):
    if arm == 'minimal':
        return Path(__file__).with_name('MINIMAL_PROMPT.txt').read_text()
    if arm not in {'refs_goal', 'refs'}:
        raise ValueError('No reference prompt for this arm')
    # Ablation: preserve the old selection/rewrite instructions, replace its quotation contract.
    text = previous.prompt()
    old = '- "source_clues": one to three nonempty, exact, contiguous quotations from the original question supporting this direction;'
    text = text.replace(old, '- "basis_refs": a nonempty list of distinct existing question-unit reference IDs supporting this direction;')
    begin = text.index('Copy source_clues exactly')
    end = text.index('Each goal must be', begin)
    text = text[:begin] + (
        'The full question and numbered original text units are provided. Units are text locations, not semantic constraints. '
        'Read the full context, including pronoun antecedents. Select the reference IDs supporting the query; '
        'one entry can use multiple units. Do not copy quotations or calculate offsets. '
        'Valid references do not prove that a query preserves meaning.\n\n') + text[end:]
    if arm == 'refs':
        text = text.replace('- "goal": one brief statement of the entity, source, or intermediate entity this search should help discover;\n', '')
        text = text.replace('in either goal or query', 'in the query')
        text = text.replace('in both goal and query', 'in the query')
        text = text.replace('Each goal must be at most 256 Unicode characters and each query', 'Each query')
    return text


def validate(value, question, arm):
    check_question(question)
    root = 'intents' if arm == 'minimal' else 'directions'
    if not isinstance(value, dict) or set(value) != {root}:
        return [f'Root must contain exactly {root}']
    intents = value[root]
    if not isinstance(intents, list) or len(intents) > 1:
        return ['Return a list with at most one intent']
    refs = {u['ref'] for u in question['units']}
    fields = {'basis_refs', 'query'} | ({'goal'} if arm == 'refs_goal' else set())
    errors = []
    for intent in intents:
        if not isinstance(intent, dict) or set(intent) != fields:
            errors.append('Intent fields must be exactly ' + ', '.join(sorted(fields)))
            continue
        q = intent['query']
        if not isinstance(q, str) or not q.strip() or len(q) > 512:
            errors.append('query must be nonempty text of at most 512 characters')
        if 'goal' in fields:
            goal = intent['goal']
            if not isinstance(goal, str) or not goal.strip() or len(goal) > 256:
                errors.append('goal must be nonempty text of at most 256 characters')
        basis = intent['basis_refs']
        if not isinstance(basis, list) or not basis or any(not isinstance(r, str) or r not in refs for r in basis):
            errors.append('basis_refs must be a nonempty list of existing reference IDs')
        elif len(basis) != len(set(basis)):
            errors.append('basis_refs must not contain duplicate IDs')
    return errors


def parse(content, question, arm):
    try:
        value = json.loads(content)
    except (ValueError, TypeError):
        return None, ['Response must be complete JSON, without Markdown fences']
    return value, validate(value, question, arm)


def response_text(response):
    if not response.choices or response.choices[0].finish_reason != 'stop':
        reason = response.choices[0].finish_reason if response.choices else 'no choices'
        raise ValueError('Incomplete initializer response: ' + str(reason))
    message = response.choices[0].message
    if getattr(message, 'tool_calls', None):
        raise ValueError('Initializer must not call tools')
    return message.content


def generate(client, config, question, arm='minimal'):
    check_question(question)
    if arm not in ARMS:
        raise ValueError('Unknown initializer arm')
    if arm == 'v2':
        old = previous.generate(client, config, question['text'], 'B')
        intents = []
        for direction in old['directions']:
            ranges = [(start, start + len(quote)) for quote, positions in
                      zip(direction['source_clues'], direction['clue_locations']) for start in positions]
            refs = [u['ref'] for u in question['units'] if any(a < u['end'] and u['start'] < b for a, b in ranges)]
            intents.append(dict(query=direction['query'], basis_refs=refs, goal=direction['goal']))
        return dict(status=old['status'], intents=intents, initial_valid=old['initial_valid'],
                    repairs=old['repairs'], raw_plan=old, question_sha256=question['sha256'],
                    basis_origin='runtime_mapped_exact_quotes')
    messages = [dict(role='system', content=system_prompt(arm)),
                dict(role='user', content=json.dumps(model_input(question), ensure_ascii=False))]
    options = dict(model=config.model, stream=False, max_tokens=1536, **config.request_options())
    content = response_text(client.chat.completions.create(**options, messages=messages))
    value, errors = parse(content, question, arm)
    initial_errors = list(errors)
    repairs = 0
    if errors:
        repairs = 1
        messages.extend([dict(role='assistant', content=content or ''), dict(role='user', content=json.dumps(dict(
            instruction='Correct only the listed contract errors using the original question and reference IDs. '
                        'Do not introduce guesses. Return only JSON under the same output contract. An empty list is allowed.',
            validation_errors=errors), ensure_ascii=False))])
        content = response_text(client.chat.completions.create(**options, messages=messages))
        value, errors = parse(content, question, arm)
    root = 'intents' if arm == 'minimal' else 'directions'
    intents = value[root] if not errors else []
    return dict(status='invalid' if errors else 'valid' if intents else 'no_direction', intents=intents,
                initial_valid=not initial_errors, repairs=repairs, initial_errors=initial_errors,
                errors=errors, raw_plan=value, question_sha256=question['sha256'], basis_origin='model_selected_refs')
