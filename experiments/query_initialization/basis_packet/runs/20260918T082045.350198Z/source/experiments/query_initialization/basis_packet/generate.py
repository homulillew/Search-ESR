"""Isolated query compilation; caller records API requests with RecordedClient."""
import json
from pathlib import Path

from experiments.query_initialization.single_entry.initializer import response_text
from .packet import model_view, check_packet, budget_check, query_token_count

ARMS = ('conservative', 'expression_packet', 'expression_full_context')


def system_prompt(arm, max_query_tokens=1024):
    if arm not in ARMS:
        raise ValueError('Unknown compilation arm')
    name = 'COMPILER_PROMPT.txt' if arm == 'conservative' else 'EXPRESSION_PROMPT.txt'
    return Path(__file__).with_name(name).read_text() + (
        f'\nEngineering contract: the query plus retrieval prefix and special tokens must fit '
        f'{max_query_tokens} local embedding tokens. Do not truncate a relationship to fit. '
        'If necessary omit a whole condition while preserving the meaning of remaining facts, '
        'or return {"query": null}.\n')


def payload(packet, arm, question=None):
    if arm not in ARMS:
        raise ValueError('Unknown compilation arm')
    value = model_view(packet)
    if arm == 'expression_full_context':
        if question is None:
            raise ValueError('Full-context control requires the original question snapshot')
        check_packet(packet, question)
        value['question_context'] = question['text']
    # Even if a caller supplies a question to another arm, it never enters payload.
    return value


def build_messages(packet, arm, question=None, max_query_tokens=1024):
    return [dict(role='system', content=system_prompt(arm, max_query_tokens)),
            dict(role='user', content=json.dumps(payload(packet, arm, question), ensure_ascii=False))]


def parse(content, tokenizer, prefix, max_query_tokens=1024):
    try:
        value = json.loads(content)
    except (TypeError, ValueError):
        return None, ['Return a complete JSON object without Markdown fences']
    if not isinstance(value, dict) or set(value) != {'query'}:
        return None, ['Return exactly the query field']
    query = value['query']
    if query is None:
        return value, []
    if not isinstance(query, str) or not query.strip():
        return None, ['query must be nonempty text or null']
    count = query_token_count(query, tokenizer, prefix)
    if count > max_query_tokens:
        return value, [f'query uses {count} embedding tokens including prefix/special tokens; maximum is {max_query_tokens}']
    return value, []


def generate(client, config, packet, arm, tokenizer, prefix, question=None, max_query_tokens=1024):
    budget_check(packet, tokenizer, prefix, max_query_tokens)
    messages = build_messages(packet, arm, question, max_query_tokens)
    options = dict(model=config.model, stream=False, max_tokens=1536, **config.request_options())
    content = response_text(client.chat.completions.create(**options, messages=messages))
    value, errors = parse(content, tokenizer, prefix, max_query_tokens)
    initial_errors = list(errors)
    if errors:
        # Fresh list avoids mutating an already-recorded first request.
        messages = messages + [dict(role='assistant', content=content or ''), dict(role='user', content=json.dumps(dict(
            instruction='Repair only the output contract using the same supplied source text. Do not invent facts. '
                        'For a budget error omit whole conditions without changing retained facts, or return query null. Return only JSON.',
            validation_errors=errors), ensure_ascii=False))]
        content = response_text(client.chat.completions.create(**options, messages=messages))
        value, errors = parse(content, tokenizer, prefix, max_query_tokens)
    query = None if errors else value['query']
    input_refs = ([u['ref'] for u in question['units']] if arm == 'expression_full_context'
                  else list(packet['input_refs']))
    return dict(status='invalid' if errors else 'abstained' if query is None else 'valid',
                query=query, initial_valid=not initial_errors, repairs=int(bool(initial_errors)),
                initial_errors=initial_errors, errors=errors, input_refs=input_refs,
                query_tokens=None if query is None else query_token_count(query, tokenizer, prefix),
                origin=arm)
