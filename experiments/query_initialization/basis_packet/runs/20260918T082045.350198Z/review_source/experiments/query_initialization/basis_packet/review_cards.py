"""Prepare arm-hidden semantic review cards; never calls a model or retriever."""
import hashlib
import json
from pathlib import Path
import sys


def prepare(run):
    run = Path(run)
    tasks = {t['qid']: t for t in json.loads((run / 'tasks.json').read_text())}
    cards, mapping = [], {}
    for folder in sorted(run.glob('qid_*')):
        result = json.loads((folder / 'result.json').read_text())
        task = tasks[result['qid']]
        card_id = hashlib.sha256(('basis-review-v1:' + folder.name).encode()).hexdigest()[:12]
        mapping[card_id] = dict(session=folder.name, qid=result['qid'], arm=result['arm'], repeat=result['repeat'])
        cards.append(dict(card_id=card_id, qid=result['qid'],
                          original_question=task['question']['text'],
                          selected_texts=[s['text'] for s in task['packet']['segments']],
                          query=result['plan']['query'] if result['plan'] else None,
                          status=result['status']))
    cards.sort(key=lambda c: c['card_id'])
    (run / 'semantic_cards.json').write_text(json.dumps(cards, ensure_ascii=False, indent=2))
    (run / 'semantic_card_mapping.json').write_text(json.dumps(mapping, ensure_ascii=False, indent=2))
    return len(cards)


if __name__ == '__main__':
    print(prepare(sys.argv[1]))
