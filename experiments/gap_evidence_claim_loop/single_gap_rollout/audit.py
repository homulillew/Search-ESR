"""Read-only integrity audit for the frozen F3 trace and reviewer projection."""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVENTS = [json.loads(line) for line in (HERE / 'events.jsonl').open()]
PACKETS = json.loads((HERE / 'REVIEW_PACKETS.json').read_text())
REVIEWS = json.loads((HERE / 'REVIEWS.json').read_text())


def main():
    counts = Counter(e['kind'] for e in EVENTS)
    starts = [e['cell'] for e in EVENTS if e['kind'] == 'cell_start']
    ends = [e['cell'] for e in EVENTS if e['kind'] == 'cell_end']
    assert len(starts) == len(ends) == 12 and set(starts) == set(ends)
    assert len(PACKETS) == len(REVIEWS) == 12
    assert counts['observation'] == counts['reader_request'] == counts['reader_response'] == 147
    assert counts['verifier_request'] == counts['verifier_response'] == 25
    assert counts['gap_review_request'] == counts['gap_review_response'] + 1
    assert counts['gap_review_response'] == counts['gap_status'] == 146
    assert counts['cell_error'] == 1
    assert all(set(json.loads(e['request']['messages'][1]['content'])) ==
               {'raw_question', 'active_gap', 'relevant_committed_claims', 'latest_observation'}
               for e in EVENTS if e['kind'] == 'reader_request')
    assert all(set(json.loads(e['request']['messages'][1]['content'])) ==
               {'active_gap', 'finding', 'exact_observation', 'relevant_committed_claims'}
               for e in EVENTS if e['kind'] == 'verifier_request')
    assert all(len(p['observations']) == len(r['observations'])
               for p, r in zip(PACKETS, REVIEWS))
    out = {'cells_started': len(starts), 'cells_terminal': len(ends),
           'unique_cells': len(set(starts)), 'observations_read': 147,
           'verifier_calls': 25, 'gap_reviews_completed': 146,
           'unanswered_gap_review_requests': 1,
           'interrupted_cell': 'F3_177:R0',
           'reader_verifier_requests_without_query_or_review_labels': True,
           'all_W_reviewed': True,
           'event_counts': dict(counts)}
    (HERE / 'INPUT_AUDIT.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
