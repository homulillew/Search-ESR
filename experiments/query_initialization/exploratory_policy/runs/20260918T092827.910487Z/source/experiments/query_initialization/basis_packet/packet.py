"""Exact source packets. Provenance records input, not semantic entailment."""
import hashlib
import json
import uuid

from experiments.query_initialization.single_entry.source_units import check_question

SCHEMA_VERSION = 'basis_packet_v1'
NORMALIZATION_VERSION = 'whitespace_per_segment_v1'


def _serialize(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def model_view(packet):
    return dict(selected_texts=[s['text'] for s in packet['segments'] if s['role'] == 'selected'],
                context_texts=[s['text'] for s in packet['segments'] if s['role'] == 'context'])


def validate_selection(value, question):
    check_question(question)
    if not isinstance(value, dict) or set(value) != {'selected_units'}:
        return ['Return exactly the selected_units field']
    refs = value['selected_units']
    valid = {u['ref'] for u in question['units']}
    if not isinstance(refs, list) or any(not isinstance(r, str) or r not in valid for r in refs):
        return ['selected_units must be a list of existing IDs from this request']
    if len(refs) != len(set(refs)):
        return ['selected_units must not contain duplicate IDs']
    return []


def build_packet(question, refs, context_refs=()):
    errors = validate_selection({'selected_units': refs}, question)
    errors += validate_selection({'selected_units': list(context_refs)}, question)
    if errors:
        raise ValueError('; '.join(errors))
    if not refs:
        raise ValueError('no_basis: empty selection')
    if set(refs) & set(context_refs):
        raise ValueError('Selected and context references must be disjoint')
    selected, context = set(refs), set(context_refs)
    segments = [dict(u, role='selected' if u['ref'] in selected else 'context')
                for u in question['units'] if u['ref'] in selected | context]
    packet = dict(schema_version=SCHEMA_VERSION, packet_id=str(uuid.uuid4()),
                  source_version=question['sha256'],
                  selected_refs=[s['ref'] for s in segments if s['role'] == 'selected'],
                  context_refs=[s['ref'] for s in segments if s['role'] == 'context'],
                  input_refs=[s['ref'] for s in segments], segments=segments,
                  normalization_version=NORMALIZATION_VERSION)
    packet['compiler_input_sha256'] = hashlib.sha256(_serialize(model_view(packet)).encode()).hexdigest()
    check_packet(packet, question)
    return packet


def check_packet(packet, question):
    check_question(question)
    if packet['schema_version'] != SCHEMA_VERSION or packet['source_version'] != question['sha256']:
        raise ValueError('Packet source/schema version mismatch')
    if not isinstance(packet['packet_id'], str) or not packet['packet_id']:
        raise ValueError('Missing packet ID')
    for field in ('selected_refs', 'context_refs'):
        errors = validate_selection({'selected_units': packet[field]}, question)
        if errors:
            raise ValueError('; '.join(errors))
    selected, context = set(packet['selected_refs']), set(packet['context_refs'])
    if not selected or selected & context:
        raise ValueError('Invalid packet selection/context')
    expected = [dict(u, role='selected' if u['ref'] in selected else 'context')
                for u in question['units'] if u['ref'] in selected | context]
    if packet['segments'] != expected or packet['input_refs'] != [u['ref'] for u in expected]:
        raise ValueError('Packet excerpts or source order mismatch')
    for role, field in [('selected', 'selected_refs'), ('context', 'context_refs')]:
        if packet[field] != [u['ref'] for u in expected if u['role'] == role]:
            raise ValueError('Packet reference order mismatch')
    digest = hashlib.sha256(_serialize(model_view(packet)).encode()).hexdigest()
    if packet['compiler_input_sha256'] != digest:
        raise ValueError('Packet model view checksum mismatch')
    if packet['normalization_version'] != NORMALIZATION_VERSION:
        raise ValueError('Unknown normalization policy')


def verbatim(packet):
    return '\n\n'.join(' '.join(s['text'].split()) for s in packet['segments'])


def query_token_count(query, tokenizer, prefix):
    # Mirror retrieval's default special tokens, explicitly disable truncation.
    ids = tokenizer(prefix + query, add_special_tokens=True, truncation=False)['input_ids']
    if ids and isinstance(ids[0], list):
        raise ValueError('Expected an unbatched tokenizer result')
    return len(ids)


def budget_check(packet, tokenizer, prefix, max_query_tokens=1024):
    count = query_token_count(verbatim(packet), tokenizer, prefix)
    if count > max_query_tokens:
        raise ValueError(f'packet_over_budget: {count} > {max_query_tokens}')
    return count
