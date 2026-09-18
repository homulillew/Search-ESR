"""Select original units; the runtime constructs an exact-source retrieval query.

No compiler, semantic repair, retrieval feedback, or silent fallback is used.
"""
import json
from pathlib import Path

from experiments.query_initialization.single_entry.source_units import check_question
from experiments.query_initialization.single_entry.initializer import response_text
from experiments.query_initialization.basis_packet.packet import (
    build_packet, query_token_count, validate_selection, verbatim,
)


def system_prompt(max_query_tokens=1024):
    if not isinstance(max_query_tokens, int) or isinstance(max_query_tokens, bool) or max_query_tokens < 1:
        raise ValueError('max_query_tokens must be a positive integer')
    return Path(__file__).with_name('SELECTOR_PROMPT.txt').read_text() + (
        '\nEngineering contract: the runtime will concatenate the selected original units '
        'in source order, normalize whitespace within each unit, and search that text directly. '
        f'The resulting query plus retrieval prefix and special tokens must fit {max_query_tokens} '
        'local embedding tokens. Do not calculate token counts or rewrite the text.\n'
    )


def build_messages(question, max_query_tokens=1024):
    check_question(question)
    payload = dict(question=question['text'], question_units=[
        dict(ref=unit['ref'], text=unit['text']) for unit in question['units']])
    return [dict(role='system', content=system_prompt(max_query_tokens)),
            dict(role='user', content=json.dumps(payload, ensure_ascii=False))]


def parse(content, question):
    try:
        value = json.loads(content)
    except (ValueError, TypeError):
        return None, ['Return a complete JSON object without Markdown fences']
    return value, validate_selection(value, question)


def generate(client, config, question, tokenizer, prefix, max_query_tokens=1024):
    messages = build_messages(question, max_query_tokens)
    options = dict(model=config.model, stream=False, max_tokens=1536, **config.request_options())
    content = response_text(client.chat.completions.create(**options, messages=messages))
    value, errors = parse(content, question)
    initial_errors = list(errors)
    if errors:
        # Fresh list preserves the first request in clients/recorders holding references.
        messages = messages + [dict(role='assistant', content=content or ''), dict(
            role='user', content=json.dumps(dict(
                instruction='Repair only the output contract using the same question and existing '
                            'reference IDs. Return only selected_units. Do not write a query or '
                            'introduce guesses. An empty list is allowed.',
                validation_errors=errors), ensure_ascii=False))]
        content = response_text(client.chat.completions.create(**options, messages=messages))
        value, errors = parse(content, question)
    result = dict(status='invalid' if errors else 'no_basis', selected_units=None,
                  packet=None, query=None, initial_valid=not initial_errors,
                  repairs=int(bool(initial_errors)), initial_errors=initial_errors,
                  errors=list(errors), query_tokens=None, input_refs=[],
                  selector_input_refs=[unit['ref'] for unit in question['units']],
                  question_sha256=question['sha256'], raw_plan=value,
                  origin='selector_verbatim')
    if errors:
        return result
    result['selected_units'] = list(value['selected_units'])
    if not result['selected_units']:
        return result
    packet = build_packet(question, result['selected_units'])
    query = verbatim(packet)
    count = query_token_count(query, tokenizer, prefix)
    result.update(packet=packet, query=query, query_tokens=count,
                  input_refs=list(packet['input_refs']), status='valid')
    if count > max_query_tokens:
        result.update(status='packet_over_budget', errors=[
            f'packet_over_budget: {count} > {max_query_tokens}'])
    return result
