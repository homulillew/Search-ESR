"""Extract only the frozen request prefix; stop reading before future events."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OLD = ROOT / 'experiments/search_find_v3b/orthogonal_search/freeze.json'
RUNS = {
    '546': ROOT / 'experiments/runs/v003a_search_find/qid_546/20260922T121742.932067Z/events.jsonl',
    '1094': ROOT / 'experiments/runs/v003a_search_find/qid_1094/20260922T113202.256169Z/events.jsonl',
}


def packet(qid, seq, digest):
    request = None
    with RUNS[qid].open() as stream:
        for line in stream:
            event = json.loads(line)
            if event['seq'] == seq:
                assert event['kind'] == 'api_request'
                request = event['request']
                break  # Do not read any later event.
    assert request is not None
    actual = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
    assert actual == digest
    messages = request['messages']
    question = next(x['content'] for x in messages if x['role'] == 'user')
    reasoning = [x.get('reasoning_content') or x.get('content') or ''
                 for x in messages if x['role'] == 'assistant']
    docs = {}
    for message in messages:
        if message['role'] != 'tool':
            continue
        try:
            result = json.loads(message['content'])
        except (ValueError, TypeError):
            continue
        if not isinstance(result, dict):
            continue
        for hit in result.get('results', []):
            if isinstance(hit, dict) and hit.get('doc_ref'):
                docs.setdefault(hit['doc_ref'], {'doc_ref': hit['doc_ref'],
                    'title': hit.get('title'), 'preview_ref': hit.get('preview_ref')})
    return {'qid': qid, 'seq': seq, 'checkpoint_request_sha256': digest,
            'question': question, 'last_visible_reasoning': reasoning[-1] if reasoning else '',
            'observed_documents': sorted(docs.values(),
                 key=lambda x: int(x['doc_ref'][1:])),
            'messages': messages}


def main():
    old = json.loads(OLD.read_text())
    out = HERE / 'PREFIX_ONLY_PACKETS.json'
    if out.exists():
        raise FileExistsError(out)
    packets = [packet(str(q), seq, old['checkpoint_request_sha256'][f'{q}:{seq}'])
               for cells in old['cohorts'].values() for q, seq in cells]
    out.write_text(json.dumps({'selection': '13 historical frozen checkpoints',
        'source_rule': 'read original events only through api_request seq, never future events',
        'packets': packets}, ensure_ascii=False, indent=2) + '\n')
    print(len(packets), out.stat().st_size)


if __name__ == '__main__':
    main()
