"""Mechanical input/ledger audit; semantic quality requires separate review.

All scheduled attempts remain denominators, including empty selection and errors.
No positive-source labels or answers are used by this audit.
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
from experiments.query_initialization.basis_packet.packet import check_packet, query_token_count, verbatim
from experiments.query_initialization.single_entry.source_units import check_question
from experiments.query_initialization.selector_verbatim.selector import build_messages, parse

ARMS = ('full_question', 'selector')
TOKEN_KEYS = ('prompt_tokens', 'completion_tokens', 'total_tokens')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def aggregate(rows):
    ratios = [r['token_ratio'] for r in rows if r['token_ratio'] is not None]
    unit_ratios = [r['source_unit_ratio'] for r in rows if r['source_unit_ratio'] is not None]
    char_ratios = [r['source_char_ratio'] for r in rows if r['source_char_ratio'] is not None]
    return dict(attempts=len(rows), status_counts=dict(Counter(r['status'] for r in rows)),
        complete=sum(r['status'] == 'complete' for r in rows),
        initial_valid=sum(r['initial_valid'] is True for r in rows),
        initial_invalid=sum(r['initial_valid'] is False for r in rows),
        all_selected=sum(r['all_selected'] for r in rows),
        forced_all_selected=sum(r['forced_all_selected'] for r in rows),
        discretionary_all_selected=sum(r['all_selected'] and not r['forced_all_selected'] for r in rows),
        no_basis=sum(r['status'] == 'no_basis' for r in rows),
        invalid=sum(r['status'] == 'invalid' for r in rows),
        packet_over_budget=sum(r['status'] == 'packet_over_budget' for r in rows),
        repairs=sum(r['repairs'] for r in rows), api_requests=sum(r['api_requests'] for r in rows),
        search_calls=sum(r['search_calls'] for r in rows), windows=sum(r['windows'] for r in rows),
        query_tokens_sum=sum(r['query_tokens'] or 0 for r in rows),
        mean_token_ratio=sum(ratios) / len(ratios) if ratios else None,
        mean_source_unit_ratio=sum(unit_ratios) / len(unit_ratios) if unit_ratios else None,
        mean_source_char_ratio=sum(char_ratios) / len(char_ratios) if char_ratios else None,
        elapsed_seconds_sum=sum(r['elapsed_seconds'] for r in rows),
        usage={key: sum(r['usage'][key] for r in rows) for key in TOKEN_KEYS})


def concurrency(intervals):
    """Observed wall-clock overlaps, not a speedup estimate."""
    points = []
    for start, finish in intervals:
        a, b = datetime.fromisoformat(start), datetime.fromisoformat(finish)
        assert a <= b
        if a < b:
            points.extend([(a, 1), (b, -1)])
    active = peak = 0
    for _, change in sorted(points):
        active += change
        peak = max(peak, active)
    return peak


def audit(run):
    run = Path(run).resolve()
    manifest = read(run / 'manifest.json')
    for rel, expected in manifest['source_sha256'].items():
        assert digest(run / 'source' / rel) == expected, ('snapshot', rel)
    assert digest(run / 'tasks.json') == manifest['tasks_sha256']
    assert digest(ROOT / 'BCPlus/data/bcplus/qa.jsonl') == manifest['dataset_sha256']
    assert digest(run / 'selection_lock.json') == manifest['selection_lock_sha256']
    lock = read(run / 'selection_lock.json')
    assert lock['dataset_sha256'] == manifest['dataset_sha256']
    assert lock['tasks_sha256'] == manifest['tasks_sha256']
    assert lock['arms'] == {'full_question': 1, 'selector': manifest['model_repeats']}
    tasks = read(run / 'tasks.json')
    cases = {str(t['qid']): t for t in tasks}
    assert len(cases) == len(tasks)
    assert [str(t['qid']) for t in tasks] == lock['qids']
    assert len(tasks) == lock['count']
    assert not set(cases) & set(lock['excluded_qids'])
    for task in tasks:
        check_question(task['question'])
        assert task['question']['sha256'] == lock['question_sha256'][str(task['qid'])]
    schedule = read(run / 'schedule.json')
    scheduled = {(str(s['qid']), s['arm'], s['repeat']) for s in schedule}
    expected = {(qid, arm, r) for qid in cases for arm in ARMS
                for r in range(1, 2 if arm == 'full_question' else manifest['model_repeats'] + 1)}
    assert len(scheduled) == len(schedule) and scheduled == expected
    tokenizer = AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B', local_files_only=True)
    prefix, budget = manifest['query_prefix'], manifest['query_max_tokens']
    preflight = read(run / 'retrieval_preflight.json')
    assert preflight['status'] == 'passed'
    assert preflight['replicas'] == manifest['retrieval_workers']
    assert len(preflight['probes']) == len(preflight['queries']) * preflight['replicas']
    worker_pids = {}
    for probe in preflight['probes']:
        index = probe['worker_index']
        assert 0 <= index < preflight['replicas']
        assert worker_pids.setdefault(index, probe['pid']) == probe['pid']
    assert len(worker_pids) == len(set(worker_pids.values())) == preflight['replicas']
    for index in range(len(preflight['queries'])):
        probes = [p for p in preflight['probes'] if p['query_index'] == index]
        assert len(probes) == preflight['replicas']
        reference = probes[0]
        for probe in probes[1:]:
            assert probe['docids'] == reference['docids']
            assert len(probe['scores']) == len(reference['scores'])
            assert all(abs(a - b) <= 1e-5 for a, b in zip(probe['scores'], reference['scores']))
    preflight_end = max(datetime.fromisoformat(p['finished_at']) for p in preflight['probes'])
    db = sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro', uri=True)
    sessions, pool, cache = [], {}, {}
    retrieval_intervals, api_intervals, retrieval_records = [], [], []
    try:
        for folder in sorted(run.glob('qid_*')):
            result, summary = read(folder / 'result.json'), read(folder / 'summary.json')
            task = cases[str(result['qid'])]
            question = task['question']
            all_refs = [u['ref'] for u in question['units']]
            full_query = '\n\n'.join(' '.join(u['text'].split()) for u in question['units'])
            full_tokens = query_token_count(full_query, tokenizer, prefix)
            assert read(folder / 'input.json') == task
            assert folder.name == result['session']
            for key in ('session', 'qid', 'arm', 'repeat', 'status'):
                assert result[key] == summary[key]
            plan, arm = result['plan'], result['arm']
            assert arm in ARMS
            packet = read(folder / 'packet.json') if (folder / 'packet.json').exists() else None
            events = [json.loads(line) for line in (folder / 'events.jsonl').read_text().splitlines()]
            requests = [e for e in events if e['kind'] == 'api_request']
            responses = [e for e in events if e['kind'] == 'api_response']
            terminals = [e for e in events if e['kind'] in {'api_response', 'api_error'}]
            assert len(terminals) == len(requests)
            for request, terminal in zip(requests, terminals):
                assert request['seq'] < terminal['seq']
                assert preflight_end <= datetime.fromisoformat(request['time'])
                api_intervals.append((request['time'], terminal['time']))
            assert summary['api_requests'] == len(requests)
            assert summary['usage'] == {key: sum(((e['response'].get('usage') or {}).get(key) or 0)
                                        for e in responses) for key in TOKEN_KEYS}
            if packet:
                check_packet(packet, question)
                assert not packet['context_refs'], 'No implicit context expansion'
            if arm == 'full_question':
                assert not requests and plan and packet
                assert packet['input_refs'] == all_refs
                assert plan['query'] == full_query == verbatim(packet)
            else:
                expected_messages = build_messages(question, budget)
                assert len(requests) <= 1 + manifest['repair_limit']
                parsed = []
                for index, event in enumerate(requests):
                    request = event['request']
                    assert request['messages'][:2] == expected_messages, (folder.name, 'model input')
                    assert len(request['messages']) == 2 + index * 2
                    assert 'tools' not in request and 'enable_search' not in request
                    assert request.get('stream') is False
                    assert request['model'] == manifest['model']
                    assert request['max_tokens'] == manifest['max_tokens']
                    for key, value in manifest['request_options'].items():
                        assert request[key] == value
                if plan:
                    assert len(responses) == len(requests) and responses
                    for event in responses:
                        choices = event['response']['choices']
                        assert choices and choices[0]['finish_reason'] == 'stop'
                        assert not choices[0]['message'].get('tool_calls')
                        parsed.append(parse(choices[0]['message']['content'], question))
                    first_errors, final_errors = parsed[0][1], parsed[-1][1]
                    assert plan['initial_errors'] == first_errors
                    assert plan['initial_valid'] == (not first_errors)
                    assert plan['repairs'] == len(requests) - 1 == int(bool(first_errors))
                    assert plan['selector_input_refs'] == all_refs
                    assert plan['question_sha256'] == question['sha256']
                    assert plan['raw_plan'] == parsed[-1][0]
                    if final_errors:
                        assert plan['errors'] == final_errors and plan['status'] == 'invalid'
                        assert plan['selected_units'] is None and packet is None
                    else:
                        selected = parsed[-1][0]['selected_units']
                        assert plan['selected_units'] == selected
                        if not selected:
                            assert plan['status'] == 'no_basis' and packet is None
                        else:
                            assert packet and set(packet['selected_refs']) == set(selected)
                            count = query_token_count(verbatim(packet), tokenizer, prefix)
                            assert plan['status'] == ('packet_over_budget' if count > budget else 'valid')
                            assert plan['errors'] == ([f'packet_over_budget: {count} > {budget}'] if count > budget else [])
                    assert plan['packet'] == packet
                for index, request_event in enumerate(requests[1:], 1):
                    previous = responses[index - 1]['response']['choices'][0]['message']['content']
                    errors = parse(previous, question)[1]
                    assert errors
                    repair = [dict(role='assistant', content=previous or ''), dict(role='user', content=json.dumps(dict(
                        instruction='Repair only the output contract using the same question and existing '
                                    'reference IDs. Return only selected_units. Do not write a query or '
                                    'introduce guesses. An empty list is allowed.',
                        validation_errors=errors), ensure_ascii=False))]
                    assert request_event['request']['messages'][2:] == repair
            count = None
            if plan:
                assert 0 <= plan['repairs'] <= manifest['repair_limit']
                assert plan['input_refs'] == (packet['input_refs'] if packet else [])
                if packet:
                    assert plan['query'] == verbatim(packet)
                    count = query_token_count(plan['query'], tokenizer, prefix)
                    assert plan['query_tokens'] == count
                    if plan['status'] == 'valid':
                        assert count <= budget
                    if packet['input_refs'] == all_refs:
                        assert plan['query'] == full_query, 'All-selection must equal full-question control'
                else:
                    assert plan['query'] is None and plan['query_tokens'] is None
            starts = [e for e in events if e['kind'] == 'search_start']
            searches = [e for e in events if e['kind'] == 'search_result']
            finalized = [e for e in events if e['kind'] == 'query_finalized']
            workers = [e for e in events if e['kind'] == 'retrieval_worker']
            observations = read(folder / 'observations.json')
            assert len(workers) <= len(starts)
            for worker in workers:
                assert worker_pids[worker['worker_index']] == worker['pid']
                assert preflight_end <= datetime.fromisoformat(worker['started_at'])
                assert starts[0]['seq'] < worker['seq']
                retrieval_intervals.append((worker['started_at'], worker['finished_at']))
                retrieval_records.append(dict(session=folder.name, **{
                    key: worker[key] for key in ('worker_index', 'pid', 'started_at', 'finished_at', 'elapsed_seconds')}))
            assert len(starts) <= 1 and summary['search_calls'] == len(starts)
            if starts:
                assert plan and plan['status'] == 'valid'
                assert len(finalized) == 1 and finalized[0]['plan'] == plan
                assert finalized[0]['seq'] < starts[0]['seq']
                assert not requests or requests[-1]['seq'] < finalized[0]['seq']
                assert starts[0]['arguments'] == dict(query=plan['query'], k=manifest['k'])
            assert [e['result'] for e in searches] == [o['result'] for o in observations]
            if result['status'] == 'complete':
                assert len(starts) == len(searches) == len(observations) == 1
                assert len(workers) == 1 and workers[0]['seq'] < searches[0]['seq']
                assert result['result'] == observations[0]['result']
            else:
                assert not result['result'] and not observations
            with sqlite3.connect(f'file:{folder}/observations.sqlite?mode=ro', uri=True) as ledger:
                assert [json.loads(v) for (v,) in ledger.execute(
                    'select result from events where active=1 order by seq')] == [o['result'] for o in observations]
            handoff = read(folder / 'handoff.json')
            assert handoff['schema_version'] == 'basis_packet_handoff_v1'
            assert handoff['original_question'] == question
            assert handoff['packet_id'] == (packet['packet_id'] if packet else None)
            assert handoff['status'] == result['status']
            assert len(handoff['search_attempts']) == len(starts)
            if starts:
                attempt = handoff['search_attempts'][0]
                assert attempt['attempt_id'] == run.name + '/' + folder.name
                assert attempt['packet_id'] == packet['packet_id']
                assert attempt['input_refs'] == plan['input_refs']
                assert attempt['method'] == arm and attempt['query'] == plan['query']
                assert attempt['arguments'] == starts[0]['arguments']
                assert attempt['status'] == result['status'] and attempt['result'] == result['result']
            assert len(result['result']) <= manifest['k']
            tokens = 0
            for rank, window in enumerate(result['result'], 1):
                if window['docid'] not in cache:
                    cache[window['docid']] = db.execute('select text,url from documents where docid=?',
                                                       (window['docid'],)).fetchone()
                text, url = cache[window['docid']]
                text_digest = hashlib.sha256(text.encode()).hexdigest()
                assert window['document_sha256'] == text_digest and window['url'] == url
                assert window['text'] == text[window['offset']:window['end_char']]
                expected_ref = 'w_' + hashlib.sha256(
                    f"raw-v1:{window['docid']}:{text_digest}:{window['offset']}:{window['end_char']}".encode()).hexdigest()[:24]
                assert window['window_ref'] == expected_ref
                assert window['has_more_before'] == (window['offset'] > 0)
                assert window['has_more_after'] == (window['end_char'] < len(text))
                if window['title_span']:
                    a, b = window['title_span']
                    assert window['title'] == text[a:b]
                size = window['text_tokens'] + window['title_tokens']
                assert size <= manifest['window_tokens']
                tokens += size
                key = (str(result['qid']), window['docid'])
                entry = pool.setdefault(key, dict(qid=result['qid'], docid=window['docid'], title=window['title'],
                                                  url=window['url'], windows={}, occurrences=[]))
                entry['windows'][window['window_ref']] = window
                entry['occurrences'].append(dict(session=result['session'], arm=arm, rank=rank,
                                                window_ref=window['window_ref']))
            assert tokens <= manifest['total_window_budget']
            selected_n = len(packet['input_refs']) if packet else 0
            selected_chars = sum(len(segment['text']) for segment in packet['segments']) if packet else 0
            sessions.append(dict(**summary, query=plan['query'] if plan else None, query_tokens=count,
                full_question_tokens=full_tokens, token_ratio=count / full_tokens if count is not None else None,
                selected_units=plan.get('selected_units') if plan else None,
                input_refs=packet['input_refs'] if packet else [], source_unit_count=len(all_refs),
                selected_unit_count=selected_n, source_unit_ratio=selected_n / len(all_refs) if plan else None,
                selected_source_chars=selected_chars, original_source_chars=len(question['text']),
                source_char_ratio=selected_chars / len(question['text']) if plan else None,
                all_selected=bool(packet and packet['input_refs'] == all_refs),
                forced_all_selected=bool(packet and len(all_refs) == 1),
                initial_valid=plan.get('initial_valid') if plan else None,
                repairs=plan.get('repairs', 0) if plan else max(0, len(requests) - 1),
                initial_errors=plan.get('initial_errors', []) if plan else [],
                windows=len(result['result']), window_tokens=tokens))
        assert {(str(s['qid']), s['arm'], s['repeat']) for s in sessions} == scheduled
        assert len(sessions) == len(scheduled)
    finally:
        db.close()
    output = dict(mechanical_checks='passed',
        concurrency=dict(api_peak_observed=concurrency(api_intervals),
            experimental_retrieval_peak_observed=concurrency(retrieval_intervals),
            experimental_retrieval_calls=len(retrieval_records),
            preflight_retrieval_calls=len(preflight['probes']),
            preflight_retrieval_peak_observed=concurrency([(p['started_at'], p['finished_at']) for p in preflight['probes']]),
            worker_pids=worker_pids, experimental_retrieval_records=retrieval_records,
            note='Preflight probes are separate from experiment Search counts. Peaks measure observed wall-clock overlap; no speedup claim.'),
        aggregates={arm: aggregate([s for s in sessions if s['arm'] == arm]) for arm in ARMS},
        per_qid={qid: {arm: aggregate([s for s in sessions if str(s['qid']) == qid and s['arm'] == arm])
                       for arm in ARMS} for qid in cases}, sessions=sessions,
        note='No semantic or retrieval-utility labels inferred from mechanical success. All scheduled attempts remain denominators. '
             'Full question once per qid; selector repeats are not independent questions. Token ratios include retrieval prefix/special tokens. '
             'Source-unit ratio is structural, not constraint coverage. Review pool has only actually visible windows.')
    dump(run / 'audit.json', output)
    for item in pool.values():
        item['windows'] = list(item['windows'].values())
    dump(run / 'review_pool.json', list(pool.values()))
    lines = ['# Selector and full-question queries', '', output['note'], '']
    for qid, case in cases.items():
        lines.extend([f'## qid {qid}', '', '```text', case['question']['text'], '```', ''])
        for row in [s for s in sessions if str(s['qid']) == qid]:
            lines.extend([f"### {row['arm']} r{row['repeat']}", '',
                f"Status: {row['status']}; query tokens: {row['query_tokens']}; selected units: {row['input_refs']}",
                '', '```text', row['query'] or '(no query)', '```', ''])
    (run / 'queries.md').write_text('\n'.join(lines), encoding='utf-8')
    return output


if __name__ == '__main__':
    print(json.dumps(audit(sys.argv[1])['aggregates'], ensure_ascii=False, indent=2))
