"""Offline mechanical audit and arm-hidden review material for a two-action probe.

This code never infers usefulness, entailment, or research progress from bytes,
overlap, API success, or a model's own explanation. Failed scheduled sessions stay
in the denominator. Sources are checked against the frozen local corpus.
"""
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from transformers import AutoTokenizer
from experiments.query_initialization.basis_packet.packet import query_token_count
from llm_chat.observations import merge_ranges, subtract_ranges

ARMS = ('current', 'exploratory')
TOKEN_KEYS = ('prompt_tokens', 'completion_tokens', 'total_tokens')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def concurrency(intervals):
    points = []
    for start, finish in intervals:
        a, b = datetime.fromisoformat(start), datetime.fromisoformat(finish)
        assert a <= b, (start, finish)
        if a < b:
            points.extend([(a, 1), (b, -1)])
    active = peak = 0
    for _, change in sorted(points):
        active += change
        peak = max(peak, active)
    assert active == 0
    return peak


def window_views(result):
    if isinstance(result, list):
        return result
    if isinstance(result, dict) and 'window_ref' in result:
        return [result]
    return []


def audit_window(window, corpus, cache, tokenizer, cap):
    did = window['docid']
    if did not in cache:
        cache[did] = corpus.execute('select text,url from documents where docid=?', (did,)).fetchone()
    assert cache[did] is not None, ('missing source', did)
    text, url = cache[did]
    sha = hashlib.sha256(text.encode()).hexdigest()
    assert window['document_sha256'] == sha and window['url'] == url
    a, z = window['offset'], window['end_char']
    assert type(a) is int and type(z) is int and 0 <= a <= z <= len(text)
    assert window['text'] == text[a:z]
    ref = 'w_' + hashlib.sha256(f'raw-v1:{did}:{sha}:{a}:{z}'.encode()).hexdigest()[:24]
    assert window['window_ref'] == ref
    assert window['has_more_before'] == (a > 0)
    assert window['has_more_after'] == (z < len(text))
    if window['title_span'] is not None:
        ta, tz = window['title_span']
        assert 0 <= ta <= tz <= len(text)
        assert window['title'] == text[ta:tz]
    else:
        assert window['title'] == ''
    for label in ('text', 'title'):
        count = len(tokenizer(window[label], add_special_tokens=False)['input_ids'])
        assert window[f'{label}_tokens'] == count, (did, label, count)
    assert window['text_tokens'] + window['title_tokens'] <= cap
    return text, url


def expected_metrics(views, coverage, seen):
    """Recompute bookkeeping in emission order, including title/body overlap."""
    metrics = []
    for v in views:
        key = v['docid'], v['document_sha256']
        a, z = v['offset'], v['end_char']
        old = coverage.get(key, [])
        body_new = subtract_ranges(a, z, old)
        spans = [[a, z]]
        current = merge_ranges(old + spans)
        title_new = []
        if v.get('title_span'):
            ta, tz = v['title_span']
            title_new = subtract_ranges(ta, tz, current)
            spans.append([ta, tz])
            current = merge_ranges(current + [[ta, tz]])
        if v.get('parent_window_ref'):
            assert v['parent_window_ref'] in seen
        metrics.append(dict(docid=v['docid'], document_sha256=v['document_sha256'],
            window_ref=v['window_ref'], repeated_window=v['window_ref'] in seen,
            source_ranges=spans, body_new_spans=body_new, title_new_spans=title_new,
            new_chars=sum(y-x for x,y in body_new + title_new),
            body_overlap_chars=z-a-sum(y-x for x,y in body_new)))
        coverage[key] = current
        seen.add(v['window_ref'])
    return metrics


def cards(run, tasks, sessions, pool):
    """Hide policy/rank labels, not a guarantee of complete reviewer blinding."""
    utility, utility_map, behavior, behavior_map = [], {}, [], {}
    for item in pool:
        for window in item['windows']:
            card_id = hashlib.sha256(('exploratory-utility-v1:' + str(item['qid']) + ':' +
                                      window['window_ref']).encode()).hexdigest()[:12]
            utility_map[card_id] = dict(qid=item['qid'], docid=item['docid'],
                window_ref=window['window_ref'], occurrences=[o for o in item['occurrences']
                                                           if o['window_ref'] == window['window_ref']])
            utility.append(dict(card_id=card_id, qid=item['qid'],
                original_question=tasks[str(item['qid'])]['question'],
                **{k: window[k] for k in ('docid', 'title', 'url', 'text', 'offset', 'end_char',
                                         'has_more_before', 'has_more_after')}))
    for session in sessions:
        result = read(run / session['session'] / 'result.json')
        card_id = hashlib.sha256(('exploratory-behavior-v1:' + session['session']).encode()).hexdigest()[:12]
        behavior_map[card_id] = {k: session[k] for k in ('session', 'qid', 'arm', 'repeat')}
        behavior.append(dict(card_id=card_id, qid=session['qid'],
            original_question=tasks[str(session['qid'])]['question'],
            status=result['status'], steps=result['steps']))
    for name, values in [('utility', utility), ('behavior', behavior)]:
        values.sort(key=lambda c: c['card_id'])
        dump(run / f'{name}_cards.json', values)
    dump(run / 'utility_card_mapping.json', utility_map)
    dump(run / 'behavior_card_mapping.json', behavior_map)
    return dict(utility_cards=len(utility), behavior_cards=len(behavior))


def aggregate(rows):
    return dict(sessions=len(rows), status_counts=dict(Counter(r['status'] for r in rows)),
        api_requests=sum(r['api_requests'] for r in rows),
        search_calls=sum(r['search_calls'] for r in rows), open_calls=sum(r['open_calls'] for r in rows),
        returned_windows=sum(r['returned_windows'] for r in rows),
        second_action_counts=dict(Counter(r['second_action'] for r in rows)),
        repeated_windows=sum(r['repeated_windows'] for r in rows),
        new_source_chars=sum(r['new_source_chars'] for r in rows),
        usage={k:sum(r['usage'][k] for r in rows) for k in TOKEN_KEYS})


def without_none(value):
    if isinstance(value, dict):
        return {k: without_none(v) for k,v in value.items() if v is not None}
    if isinstance(value, list):
        return [without_none(v) for v in value]
    return value


def audit_api(events, result, manifest, expected_system, task, tool_schema):
    requests = [e for e in events if e['kind'] == 'api_request']
    terminals = [e for e in events if e['kind'] in ('api_response', 'api_error')]
    responses = [e for e in terminals if e['kind'] == 'api_response']
    assert 1 <= len(requests) <= 2 and len(requests) == len(terminals)
    expected_history = [dict(role='system', content=expected_system),
                        dict(role='user', content=task['question'])]
    intervals = []
    for i, (request, terminal) in enumerate(zip(requests, terminals)):
        assert request['seq'] < terminal['seq']
        if i:
            assert terminals[i-1]['seq'] < request['seq']
        payload = request['request']
        assert payload['messages'] == expected_history, (result['session'], i+1, 'input boundary')
        assert payload['model'] == manifest['model']
        assert payload['max_tokens'] == manifest['max_tokens']
        assert payload['stream'] is False and payload['tools'] == tool_schema
        assert payload['tool_choice'] == ({'type':'function', 'function':{'name':'search'}} if i == 0 else 'auto')
        assert payload.get('parallel_tool_calls') is False
        assert 'enable_search' not in payload
        for key, value in manifest['request_options'].items():
            assert payload[key] == value
        intervals.append((request['time'], terminal['time']))
        if terminal['kind'] == 'api_error':
            assert i == len(requests)-1
            continue
        choice = terminal['response'].get('choices', [])
        if not choice:
            assert i == len(requests)-1
            continue
        step = result['steps'][i]
        assert step['step'] == i+1
        assert without_none(step['assistant_message']) == without_none(choice[0]['message'])
        assert step['finish_reason'] == choice[0]['finish_reason']
        action = step.get('action')
        calls = step['assistant_message'].get('tool_calls') or []
        if action:
            assert len(calls) == 1
            call = calls[0]
            assert action['name'] == call['function']['name']
            assert action['requested_arguments'] == json.loads(call['function']['arguments'])
            if action.get('arguments') is not None:
                args = action['arguments']
                if action['name'] == 'search':
                    expected = dict(action['requested_arguments'])
                    expected.setdefault('k', manifest['k'])
                    assert args == expected, 'Only documented default k may be filled'
                else:
                    assert args == action['requested_arguments']
        if i < len(requests)-1:
            assert len(calls) == 1 and action and step['status'] == 'complete'
            expected_history.extend([step['assistant_message'], dict(role='tool', tool_call_id=calls[0]['id'],
                                      content=json.dumps(step['result'], ensure_ascii=False))])
    usage = {key:sum((e['response'].get('usage') or {}).get(key) or 0 for e in responses) for key in TOKEN_KEYS}
    return requests, responses, usage, intervals


def audit_ledger(folder, executed, corpus, cache, tokenizer, manifest, pool, identity):
    observations = read(folder / 'observations.json')
    assert len(observations) == len(executed), (folder.name, 'ledger count')
    coverage, seen, history, summary = {}, set(), {}, []
    with sqlite3.connect(f'file:{folder}/observations.sqlite?mode=ro', uri=True) as ledger:
        rows = list(ledger.execute('select seq,active,tool,arguments,result,metrics from events order by seq'))
        assert len(rows) == len(observations)
        for obs, step, row in zip(observations, executed, rows):
            seq, active, tool, arguments, value, metrics = row
            args, value, metrics = json.loads(arguments), json.loads(value), json.loads(metrics)
            assert active == 1 and seq == obs['sequence'] and obs['active'] is True
            assert tool == obs['tool'] == step['action']['name']
            assert args == obs['arguments'] == step['action']['arguments']
            assert value == obs['result'] == step['result']
            views = window_views(value)
            assert views, (folder.name, step['step'], 'successful tool without windows')
            if tool == 'search':
                assert len(views) <= manifest['k'] and isinstance(value, list)
                cap = manifest['window_tokens']
            else:
                assert tool == 'open' and len(views) == 1
                cap = manifest['max_around_budget'] if args['direction'] == 'around' else manifest['open_budget']
                assert args['window_ref'] in seen
                parent, child = history[args['window_ref']], views[0]
                assert child['parent_window_ref'] == args['window_ref']
                assert (child['docid'], child['document_sha256']) == (parent['docid'], parent['document_sha256'])
                unchanged = (child['offset'], child['end_char']) == (parent['offset'], parent['end_char'])
                if args['direction'] == 'around':
                    assert child['offset'] <= parent['offset'] <= parent['end_char'] <= child['end_char']
                elif args['direction'] == 'after' and not unchanged:
                    assert child['offset'] == parent['end_char']
                elif args['direction'] == 'before' and not unchanged:
                    assert child['end_char'] == parent['offset']
                else:
                    assert args['direction'] in ('before', 'after')
            tokens, wire_tokens = 0, len(tokenizer(json.dumps(value, ensure_ascii=False), add_special_tokens=False)['input_ids'])
            for rank, v in enumerate(views, 1):
                text, url = audit_window(v, corpus, cache, tokenizer, cap)
                tokens += v['text_tokens'] + v['title_tokens']
                pin = ledger.execute('select text,url from documents where docid=? and digest=?',
                                     (v['docid'], v['document_sha256'])).fetchone()
                assert pin == (text, url)
                stored = ledger.execute('select docid,digest,start,end from windows where ref=?',
                                        (v['window_ref'],)).fetchone()
                assert stored == (v['docid'], v['document_sha256'], v['offset'], v['end_char'])
                key = str(identity['qid']), v['docid']
                item = pool.setdefault(key, dict(qid=identity['qid'], docid=v['docid'], title=v['title'],
                    url=v['url'], windows={}, occurrences=[]))
                item['windows'][v['window_ref']] = v
                item['occurrences'].append(dict(**identity, step=step['step'], tool=tool, rank=rank,
                                               window_ref=v['window_ref']))
                history[v['window_ref']] = v
            assert tokens <= manifest['total_window_budget']
            expected = expected_metrics(views, coverage, seen)
            assert metrics == obs['observations'] == expected
            summary.append(dict(step=step['step'], tool=tool, windows=len(views), window_tokens=tokens,
                serialized_result_tokens=wire_tokens,
                new_source_chars=sum(m['new_chars'] for m in metrics),
                body_chars=sum(v['end_char']-v['offset'] for v in views),
                body_overlap_chars=sum(m['body_overlap_chars'] for m in metrics),
                repeated_windows=sum(m['repeated_window'] for m in metrics)))
    return summary


def audit(run):
    run = Path(run).resolve()
    manifest = read(run / 'manifest.json')
    for rel, expected in manifest['source_sha256'].items():
        assert digest(run / 'source' / rel) == expected, ('snapshot', rel)
    assert digest(run / 'tasks.json') == manifest['tasks_sha256']
    assert digest(ROOT / 'BCPlus/data/bcplus/qa.jsonl') == manifest['dataset_sha256']
    prior = ROOT / manifest['prior_run']
    assert digest(prior / 'tasks.json') == manifest['prior_tasks_sha256']
    original = read(prior / 'tasks.json')
    tasks_list = read(run / 'tasks.json')
    assert tasks_list == [dict(qid=t['qid'], question=t['question']['text']) for t in original]
    tasks = {str(t['qid']):t for t in tasks_list}
    assert len(tasks) == len(tasks_list) == 20
    assert manifest['system_prompts']['exploratory'] == manifest['system_prompts']['current'] + '\n\n' + manifest['guidance']
    assert manifest['system_prompts']['current'].endswith(manifest['shared_probe'])
    assert manifest['request_options'] == {'extra_body': {'enable_thinking': False}}
    assert manifest['sdk_retries'] == manifest['repair_limit'] == 0
    assert manifest['max_actions'] == 2 and manifest['model_repeats'] == 2
    schedule = read(run / 'schedule.json')
    scheduled = {(str(s['qid']),s['arm'],s['repeat']) for s in schedule}
    expected = {(qid,arm,r) for qid in tasks for arm in ARMS for r in (1,2)}
    assert len(schedule) == len(scheduled) == 80 and scheduled == expected
    preflight = read(run / 'retrieval_preflight.json')
    assert preflight['status'] == 'passed' and preflight['replicas'] == manifest['retrieval_workers']
    assert len(preflight['probes']) == len(preflight['queries']) * preflight['replicas']
    worker_pids = {}
    for p in preflight['probes']:
        assert worker_pids.setdefault(p['worker_index'], p['pid']) == p['pid']
    assert len(worker_pids) == len(set(worker_pids.values())) == preflight['replicas']
    for i in range(len(preflight['queries'])):
        probes = [p for p in preflight['probes'] if p['query_index'] == i]
        assert len(probes) == preflight['replicas']
        for p in probes[1:]:
            assert p['docids'] == probes[0]['docids']
            assert len(p['scores']) == len(probes[0]['scores'])
            assert all(abs(a-b)<=1e-5 for a,b in zip(p['scores'],probes[0]['scores']))
    preflight_end = max(datetime.fromisoformat(p['finished_at']) for p in preflight['probes'])
    tokenizer = AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B', local_files_only=True)
    api_intervals, retrieval_intervals, retrieval_records = [], [], []
    pool, cache, sessions = {}, {}, []
    with sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro', uri=True) as corpus:
        for folder in sorted(run.glob('qid_*')):
            result, summary = read(folder/'result.json'), read(folder/'summary.json')
            task = tasks[str(result['qid'])]
            assert read(folder/'input.json') == task
            assert folder.name == result['session'] == f"qid_{result['qid']}__{result['arm']}__r{result['repeat']}"
            for key in ('session','qid','arm','repeat','status'):
                assert result[key] == summary[key]
            events = [json.loads(line) for line in (folder/'events.jsonl').read_text().splitlines()]
            assert [e['seq'] for e in events] == list(range(1,len(events)+1))
            requests, responses, usage, intervals = audit_api(events,result,manifest,
                manifest['system_prompts'][result['arm']],task,manifest['tools'])
            assert summary['api_requests'] == len(requests) and summary['usage'] == usage
            assert all(preflight_end <= datetime.fromisoformat(a) for a,_ in intervals)
            api_intervals += intervals
            assert len(result['steps']) == len(requests)
            final_messages = [dict(role='system',content=manifest['system_prompts'][result['arm']]),
                              dict(role='user',content=task['question'])]
            executed = []
            for step in result['steps']:
                if 'action' in step:
                    final_messages.append(step['assistant_message'])
                action = step.get('action')
                if action and action['name'] == 'search':
                    count = query_token_count(action['arguments']['query'], tokenizer, manifest['query_prefix'])
                    assert step['query_tokens'] == count
                    if step['status'] == 'complete':
                        assert count <= manifest['query_max_tokens'] and action['arguments']['k'] == manifest['k']
                if step['status'] == 'complete':
                    assert step['finish_reason'] in ('tool_calls', 'stop')
                    assert step.get('compatibility_stop_toolcall', False) == (step['finish_reason'] == 'stop')
                    executed.append(step)
                    final_messages.append(dict(role='tool',tool_call_id=action['tool_call_id'],
                        content=json.dumps(step['result'],ensure_ascii=False)))
            assert read(folder/'messages.json') == final_messages
            starts = [e for e in events if e['kind'] == 'tool_start']
            finishes = [e for e in events if e['kind'] == 'tool_result']
            assert len(finishes) == len(executed) <= len(starts) <= 2
            assert summary['search_calls'] == sum(e['name']=='search' for e in starts)
            assert summary['open_calls'] == sum(e['name']=='open' for e in starts)
            for e,step in zip(finishes,executed):
                assert e['step'] == step['step'] and e['name'] == step['action']['name'] and e['result'] == step['result']
                start = next(s for s in starts if s['step'] == step['step'])
                assert start['seq'] < e['seq']
                assert start['name'] == e['name'] and start['arguments'] == step['action']['arguments']
            workers = [e for e in events if e['kind'] == 'retrieval_worker']
            assert len(workers) <= summary['search_calls']
            for worker in workers:
                assert worker_pids[worker['worker_index']] == worker['pid']
                assert preflight_end <= datetime.fromisoformat(worker['started_at'])
                retrieval_intervals.append((worker['started_at'],worker['finished_at']))
                retrieval_records.append(dict(session=folder.name,**{k:worker[k] for k in
                    ('worker_index','pid','started_at','finished_at','elapsed_seconds')}))
            identity = {k:result[k] for k in ('session','qid','arm','repeat')}
            ledger = audit_ledger(folder,executed,corpus,cache,tokenizer,manifest,pool,identity)
            for step,row in zip(executed,ledger):
                assert step['observation_tokens'] == row['window_tokens']
            assert sum(s['window_tokens'] for s in ledger) <= manifest['session_observation_budget']
            handoff = read(folder/'handoff.json')
            assert handoff['schema_version'] == 'two_action_probe_v1'
            assert handoff['original_question'] == task and handoff['status'] == result['status']
            assert handoff['messages_file'] == 'messages.json' and handoff['observation_ledger'] == 'observations.sqlite'
            assert handoff['observed_window_refs'] == sorted({w['window_ref'] for s in executed for w in window_views(s['result'])})
            first = next((s for s in executed if s['step']==1), None)
            second = next((s for s in result['steps'] if s['step']==2), None)
            first_docs = {w['docid'] for w in window_views(first['result'])} if first else set()
            second_views = window_views(second.get('result')) if second else []
            queries = [s['action']['arguments']['query'] for s in executed if s['action']['name']=='search']
            sessions.append(dict(**summary, steps=ledger,
                second_action=(second.get('action') or {}).get('name',second['status']) if second else 'not_reached',
                returned_windows=sum(s['windows'] for s in ledger),
                repeated_windows=sum(s['repeated_windows'] for s in ledger),
                new_source_chars=sum(s['new_source_chars'] for s in ledger),
                second_repeated_docids=sum(w['docid'] in first_docs for w in second_views),
                exact_repeated_query=len(queries)==2 and queries[0]==queries[1],
                normalized_repeated_query=len(queries)==2 and ' '.join(queries[0].casefold().split())==' '.join(queries[1].casefold().split())))
    assert {(str(s['qid']),s['arm'],s['repeat']) for s in sessions} == scheduled
    assert len(sessions) == 80
    results = read(run/'results.json')
    assert sorted(results,key=lambda s:s['session']) == [read(run/s['session']/'summary.json') for s in sessions]
    output = dict(mechanical_checks='passed',
        concurrency=dict(api_peak_observed=concurrency(api_intervals),
            experimental_retrieval_peak_observed=concurrency(retrieval_intervals),
            experimental_retrieval_calls=len(retrieval_records),preflight_retrieval_calls=len(preflight['probes']),
            worker_pids=worker_pids,experimental_retrieval_records=retrieval_records),
        aggregates={arm:aggregate([s for s in sessions if s['arm']==arm]) for arm in ARMS},
        per_qid={qid:{arm:aggregate([s for s in sessions if str(s['qid'])==qid and s['arm']==arm]) for arm in ARMS} for qid in tasks},
        sessions=sessions,
        note='Mechanical success, byte novelty, and repeated-window counts do not establish semantic utility. All scheduled sessions retained. Two repeats per question are not independent questions. Concurrency is overlap, not a speedup estimate.')
    dump(run/'audit.json',output)
    pool_list = []
    for item in pool.values():
        item['windows'] = list(item['windows'].values())
        pool_list.append(item)
    dump(run/'review_pool.json',pool_list)
    output['review_cards'] = cards(run,tasks,sessions,pool_list)
    dump(run/'audit.json',output)
    return output


if __name__ == '__main__':
    output = audit(sys.argv[1])
    print(json.dumps(dict(status=output['mechanical_checks'],aggregates=output['aggregates'],
        review_cards=output['review_cards']),ensure_ascii=False,indent=2))
