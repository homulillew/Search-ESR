"""Mechanical observation context for an isolated ablation, not default runtime."""
import copy
import json

PREFIX = 'Harness observation bookkeeping (raw character ranges, not relevance, comprehension, or research progress):\n'


def build_summary(events, after_sequence, tokenizer, budget=1200):
    active = [e for e in events if e['active']]
    latest = [e for e in active if e['sequence'] > after_sequence]
    if not latest:
        return None
    windows = []
    calls = []
    for e in latest:
        views = e['result'] if isinstance(e['result'], list) else [e['result']]
        by_ref = {v['window_ref']: v for v in views if 'window_ref' in v}
        calls.append(dict(tool=e['tool'], returned_windows=len(e['observations']),
                          new_source_chars=sum(m['new_chars'] for m in e['observations'])))
        for m in e['observations']:
            v = by_ref[m['window_ref']]
            windows.append(dict(ref=m['window_ref'], docid=m['docid'],
                body=[v['offset'], v['end_char']], new_body=m['body_new_spans'],
                body_overlap_chars=m['body_overlap_chars'], repeated_window=m['repeated_window']))
    searches = [e for e in active if e['tool'] in {'search', 'seed_search'}][-3:]
    payload = dict(note='New means not previously returned in this active session. Counts include no unreturned cached text. Source totals include explicit titles; new_body lists only body ranges. No evidence or next-action judgment is made.',
        latest_calls=calls, recent_search_new_source_chars=[sum(m['new_chars'] for m in e['observations']) for e in searches],
        windows=windows, omitted_windows=0)
    while True:
        content = PREFIX + json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
        if len(tokenizer.encode(content, add_special_tokens=False)) <= budget:
            return {'role': 'user', 'content': content}
        if payload['windows']:
            payload['windows'].pop()
            payload['omitted_windows'] += 1
        else:
            raise ValueError('Summary aggregates exceed token budget')


def request_with_summary(request, summary):
    """Never mutate saved history or source tool messages."""
    request = copy.deepcopy(request)
    if summary is not None:
        request['messages'].append(summary)
    return request
