"""Project the immutable event log into arm-masked W and action review packets."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
BANK = {x['case_id']: x for x in json.loads((HERE / 'BANK.json').read_text())}


def build():
    if (HERE / 'REVIEW_PACKETS.json').exists():
        raise FileExistsError('REVIEW_PACKETS.json')
    events = [json.loads(line) for line in (HERE / 'events.jsonl').open()]
    rows = defaultdict(lambda: {'actions': [], 'observations': [], 'claims': [], 'gap_status': []})
    for e in events:
        cell = e['cell']
        row = rows[cell]
        if e['kind'] == 'tool_result':
            row['actions'].append({'decision': e['decision'], 'name': e['name'],
                                   'arguments': e['arguments'], 'result': e['result']})
        elif e['kind'] == 'observation':
            row['observations'].append({'decision': e['decision'],
                                        'action_index': len(row['actions']) - 1,
                                        **e['observation']})
        elif e['kind'] == 'claim_commit':
            row['claims'].append({'action_index': len(row['actions']) - 1,
                                  **e['claim']})
        elif e['kind'] == 'gap_status':
            row['gap_status'].append({'decision': e['decision'],
                                      'action_index': len(row['actions']) - 1,
                                      'observation_ref': e['observation_ref'],
                                      'review': e['review']})
        elif e['kind'] == 'actor_response' and not e['parsed_calls']:
            row['natural_stop_text'] = e['response']['choices'][0]['message'].get('content')
        elif e['kind'] == 'cell_end':
            row['status'] = e['status']
    packets = []
    mapping = {}
    for cell, row in sorted(rows.items(), key=lambda item: hashlib.sha256(item[0].encode()).hexdigest()):
        if 'status' not in row:
            raise ValueError(f'incomplete cell: {cell}')
        caseid, _ = cell.split(':')
        case = BANK[caseid]
        review_id = f'P{len(packets)+1:02d}'
        mapping[review_id] = cell
        packets.append({'review_id': review_id,
                        'qid': case['qid'],
                        'raw_question': case['raw_question'],
                        'active_gap': case['active_gap'],
                        'seed_claims': case['initial_claims'], **row})
    (HERE / 'REVIEW_PACKETS.json').write_text(json.dumps(packets, ensure_ascii=False, indent=2) + '\n')
    (HERE / 'PRIVATE_MAPPING.json').write_text(json.dumps(mapping, indent=2) + '\n')


if __name__ == '__main__':
    build()
