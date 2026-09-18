"""Create arm-hidden semantic and observation review cards, without API calls.

Arm identity may still be inferable from complete-question selections; do not call
this fully blind review. Identity maps and search ranks are written separately.
"""
import hashlib
import json
from pathlib import Path
import sys


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def prepare(run):
    run = Path(run)
    tasks = {str(t['qid']): t for t in read(run / 'tasks.json')}
    cards, mapping = [], {}
    for folder in sorted(run.glob('qid_*')):
        result = read(folder / 'result.json')
        task = tasks[str(result['qid'])]
        packet = read(folder / 'packet.json') if (folder / 'packet.json').exists() else None
        card_id = hashlib.sha256(('selector-semantic-v1:' + folder.name).encode()).hexdigest()[:12]
        mapping[card_id] = dict(session=folder.name, qid=result['qid'], arm=result['arm'], repeat=result['repeat'])
        cards.append(dict(card_id=card_id, qid=result['qid'], original_question=task['question']['text'],
                          selected_texts=[s['text'] for s in packet['segments']] if packet else [],
                          query=result['plan']['query'] if result['plan'] else None, status=result['status']))
    cards.sort(key=lambda c: c['card_id'])
    dump(run / 'semantic_cards.json', cards)
    dump(run / 'semantic_card_mapping.json', mapping)
    utility, utility_map = [], {}
    pool_path = run / 'review_pool.json'
    if pool_path.exists():
        for item in read(pool_path):
            # Each distinct visible observation is reviewed once; occurrence maps
            # retain the exact arm/window pairing for later deterministic scoring.
            for window in item['windows']:
                card_id = hashlib.sha256(('selector-utility-v1:' + str(item['qid']) + ':' +
                                          window['window_ref']).encode()).hexdigest()[:12]
                occurrences = [o for o in item['occurrences'] if o['window_ref'] == window['window_ref']]
                utility_map[card_id] = dict(qid=item['qid'], docid=item['docid'],
                                            window_ref=window['window_ref'], occurrences=occurrences)
                utility.append(dict(card_id=card_id, qid=item['qid'],
                    original_question=tasks[str(item['qid'])]['question']['text'],
                    docid=window['docid'], title=window['title'], url=window['url'],
                    text=window['text'], offset=window['offset'], end_char=window['end_char'],
                    has_more_before=window['has_more_before'], has_more_after=window['has_more_after']))
        utility.sort(key=lambda c: c['card_id'])
        dump(run / 'utility_cards.json', utility)
        dump(run / 'utility_card_mapping.json', utility_map)
    return dict(semantic_cards=len(cards), utility_cards=len(utility))


if __name__ == '__main__':
    print(json.dumps(prepare(sys.argv[1])))
