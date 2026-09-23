"""Mechanical summaries of the frozen P0/P1 partial continuation events."""

from collections import Counter, defaultdict
import json
from pathlib import Path

from run_partial import COHORTS, HERE, checkpoint


def analyze():
    events = [json.loads(line) for line in (HERE / 'events.jsonl').open()]
    by_cell = defaultdict(list)
    for event in events:
        if 'cell' in event:
            by_cell[event['cell']].append(event)
    expected = {f'{q}:{seq}:{arm}' for cells in COHORTS.values()
                for q, seq in cells for arm in ('P0', 'P1')}
    rows = []
    for cell in sorted(by_cell, key=lambda s: (int(s.split(':')[0]), int(s.split(':')[1]), s.split(':')[2])):
        parts = by_cell[cell]
        start = next((x for x in parts if x['kind'] == 'cell_start'), None)
        end = next((x for x in parts if x['kind'] == 'cell_end'), None)
        if start is None or end is None:
            continue
        qid, seq, arm = cell.split(':')
        request, prior, _ = checkpoint(qid, int(seq))
        last_audit = [x['audit'] for x in prior if x['kind'] == 'tool_internal'][-1]
        seen = {x['window_ref'] for x in last_audit['handles']['windows']}
        tools = [x for x in parts if x['kind'] == 'tool_start']
        results = {(x['decision'], x['call_index']): x for x in parts if x['kind'] == 'tool_result'}
        actions = [(x['decision'], x['call_index'], x['name']) for x in tools]
        find_steps = [d for d, _, n in actions if n == 'find']
        first_search = next((i for i, (_, _, n) in enumerate(actions) if n == 'search'), None)
        first_find = next((i for i, (_, _, n) in enumerate(actions) if n == 'find'), None)
        find_before_search = first_find is not None and (first_search is None or first_find < first_search)
        no_gain = []
        old_hits = new_docs = old_new_windows = useful_unknown = 0
        raw_chars = old_preview_chars = find_chars = 0
        find_new_windows = 0
        for action in tools:
            d, i, name = action['decision'], action['call_index'], action['name']
            item = results.get((d, i))
            if not item:
                continue
            result = item['result']
            if name == 'search':
                hits = result.get('results', [])
                old_in_call = 0
                new_raw_in_call = 0
                for hit in hits:
                    if hit.get('status') == 'already_discovered' or hit.get('previously_discovered'):
                        old_in_call += 1
                        old_hits += 1
                    else:
                        new_docs += 1
                    preview = hit.get('preview')
                    if preview is not None:
                        new_raw_in_call += 1
                        raw_chars += len(preview)
                        if hit.get('previously_discovered'):
                            old_preview_chars += len(preview)
                            if hit.get('preview_ref') not in seen:
                                old_new_windows += 1
                        if hit.get('preview_ref'):
                            seen.add(hit['preview_ref'])
                if hits and old_in_call > len(hits)/2 and new_raw_in_call == 0:
                    no_gain.append((d, i))
            elif name == 'find':
                for match in result.get('matches', []):
                    raw_chars += len(match.get('text', ''))
                    find_chars += len(match.get('text', ''))
                    if match.get('window_ref') not in seen:
                        find_new_windows += 1
                    seen.add(match.get('window_ref'))
            elif name == 'open':
                raw_chars += len(result.get('text', ''))
                if result.get('window_ref'):
                    seen.add(result['window_ref'])
        after_no_gain_find2 = any(any(d < fd <= d+2 for fd in find_steps) for d, _ in no_gain)
        after_no_gain_search = any(any((sd, si) > (d, i) and n == 'search'
                                      for sd, si, n in actions) for d, i in no_gain)
        premature_stop = end['status'] == 'natural_stop' and not find_steps
        rows.append({
            'cell': cell, 'qid': qid, 'seq': int(seq), 'arm': arm,
            'cohort': start['cohort'], 'status': end['status'],
            'decisions': len([x for x in parts if x['kind'] == 'api_response']),
            'actions': [n for _, _, n in actions], 'find_before_next_search': find_before_search,
            'find_within_1': any(d <= 1 for d in find_steps),
            'find_within_2': any(d <= 2 for d in find_steps),
            'find_within_3': any(d <= 3 for d in find_steps),
            'find_any': bool(find_steps), 'no_gain_searches': len(no_gain),
            'find_within_2_after_no_gain': after_no_gain_find2,
            'search_again_after_no_gain': after_no_gain_search,
            'new_documents': new_docs, 'old_document_hits': old_hits,
            'old_document_new_search_windows': old_new_windows,
            'find_new_windows': find_new_windows,
            'raw_chars': raw_chars, 'old_preview_chars': old_preview_chars,
            'find_chars': find_chars, 'premature_stop_candidate': premature_stop,
            'prompt_tokens': end['prompt_tokens'], 'total_tokens': end['total_tokens'],
            'elapsed_seconds': end['elapsed_seconds'],
            'undeclared_tool_calls': sum(x['kind'] == 'undeclared_tool_call' for x in parts),
            'tool_errors': sum(x['kind'] == 'tool_error' for x in parts),
        })
    aggregates = {}
    for cohort in ('broad_relocation', 'local_verification', 'all'):
        for arm in ('P0', 'P1'):
            group = [r for r in rows if r['arm'] == arm and (cohort == 'all' or r['cohort'] == cohort)]
            sums = Counter()
            for r in group:
                for key in ('find_before_next_search', 'find_within_1', 'find_within_2',
                            'find_within_3', 'find_any', 'no_gain_searches',
                            'find_within_2_after_no_gain', 'search_again_after_no_gain',
                            'new_documents', 'old_document_hits', 'old_document_new_search_windows',
                            'find_new_windows', 'raw_chars', 'old_preview_chars', 'find_chars',
                            'premature_stop_candidate', 'prompt_tokens', 'total_tokens',
                            'undeclared_tool_calls', 'tool_errors'):
                    sums[key] += r[key]
            aggregates[f'{cohort}:{arm}'] = {'n': len(group), 'status': dict(Counter(r['status'] for r in group)),
                                            **dict(sums)}
    output = {'expected_cells': len(expected), 'completed_cells': len(rows),
              'missing_cells': sorted(expected - {r['cell'] for r in rows}),
              'rows': rows, 'aggregates': aggregates}
    (HERE / 'mechanical_summary.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print('completed',len(rows),'/',len(expected))
    for key, value in aggregates.items():
        print(key, value)


if __name__ == '__main__':
    analyze()
