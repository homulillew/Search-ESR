"""Audit fixed-packet inputs, runtime records, and frozen positive-source coverage.

Mechanical success is not semantic fidelity. Unannotated documents are unassessed.
Request reconstruction uses the sibling generation code and prompts.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from transformers import AutoTokenizer
from experiments.query_initialization.basis_packet.packet import (
    check_packet, verbatim, query_token_count)
from experiments.query_initialization.basis_packet.generate import build_messages, parse

ARMS = ['verbatim', 'conservative', 'expression_packet', 'expression_full_context']
TOKEN_KEYS = ['prompt_tokens', 'completion_tokens', 'total_tokens']


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def aggregate(rows):
    return dict(
        attempts=len(rows), status_counts=dict(Counter(r['status'] for r in rows)),
        complete=sum(r['status'] == 'complete' for r in rows),
        initial_valid=sum(r['initial_valid'] is True for r in rows),
        initial_invalid=sum(r['initial_valid'] is False for r in rows),
        repairs=sum(r['repairs'] for r in rows),
        api_requests=sum(r['api_requests'] for r in rows),
        search_calls=sum(r['search_calls'] for r in rows),
        windows=sum(r['windows'] for r in rows),
        confirmed_document=sum(r['confirmed_document'] for r in rows),
        reference_visible=sum(r['reference_visible'] for r in rows),
        selected_basis_document=sum(r['selected_basis_document'] for r in rows),
        selected_basis_visible=sum(r['selected_basis_visible'] for r in rows),
        elapsed_seconds_sum=sum(r['elapsed_seconds'] for r in rows),
        query_tokens_sum=sum(r['query_tokens'] or 0 for r in rows),
        usage={key: sum(r['usage'][key] for r in rows) for key in TOKEN_KEYS})


def audit(run):
    run = Path(run).resolve()
    manifest = read(run / 'manifest.json')
    for rel, expected in manifest['source_sha256'].items():
        assert digest(run / 'source' / rel) == expected, ('snapshot', rel)
    assert digest(run / 'tasks.json') == manifest['tasks_sha256']
    assert digest(run / 'reference_annotations.json') == manifest['reference_annotations_sha256']
    assert digest(ROOT / 'BCPlus/data/bcplus/qa.jsonl') == manifest['dataset_sha256']
    cases_list = read(run / 'tasks.json')
    cases = {c['qid']: c for c in cases_list}
    assert len(cases) == len(cases_list)
    for case in cases_list:
        check_packet(case['packet'], case['question'])
        assert case['packet']['selected_refs'] == case['basis_refs']
    annotations = read(run / 'reference_annotations.json')['annotations']
    reference = {(a['qid'], a['docid']): a for a in annotations}
    assert len(reference) == len(annotations)
    tokenizer = AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B', local_files_only=True)
    prefix, budget = manifest['query_prefix'], manifest['query_max_tokens']
    schedule = read(run / 'schedule.json')
    scheduled = {(s['qid'], s['arm'], s['repeat']) for s in schedule}
    expected_schedule = {(qid, arm, repeat) for qid in cases for arm in ARMS
                         for repeat in range(1, 2 if arm == 'verbatim' else manifest['model_repeats'] + 1)}
    assert len(scheduled) == len(schedule) and scheduled == expected_schedule
    db = sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro', uri=True)
    cache, sessions, pool = {}, [], {}
    try:
        for annotation in annotations:
            docid = annotation['docid']
            if docid not in cache:
                cache[docid] = db.execute('select text,url from documents where docid=?', (docid,)).fetchone()
            source, source_url = cache[docid]
            assert hashlib.sha256(source.encode()).hexdigest() == annotation['document_sha256']
            assert source_url == annotation['url']
            for option in annotation['proof_alternatives']:
                for proof in option:
                    assert proof['source_spans']
                    for a, b in proof['source_spans']:
                        assert source[a:b] == proof['quote'], (docid, 'annotation span')
        for folder in sorted(run.glob('qid_*')):
            result = read(folder / 'result.json')
            summary = read(folder / 'summary.json')
            case = cases[result['qid']]
            packet = read(folder / 'packet.json')
            assert read(folder / 'input.json') == case
            assert packet == case['packet']
            check_packet(packet, case['question'])
            assert folder.name == result['session']
            for key in ['session', 'qid', 'arm', 'repeat', 'status']:
                assert result[key] == summary[key]
            events = [json.loads(line) for line in (folder / 'events.jsonl').read_text().splitlines()]
            observations = read(folder / 'observations.json')
            requests = [e for e in events if e['kind'] == 'api_request']
            responses = [e for e in events if e['kind'] == 'api_response']
            plan = result['plan']
            arm = result['arm']
            assert arm in ARMS
            assert summary['api_requests'] == len(requests)
            assert summary['usage'] == {
                key: sum(((e['response'].get('usage') or {}).get(key) or 0) for e in responses)
                for key in TOKEN_KEYS}
            if arm == 'verbatim':
                assert not requests
                assert plan and plan['query'] == verbatim(packet)
            else:
                expected_messages = build_messages(
                    packet, arm, question=case['question'] if arm == 'expression_full_context' else None,
                    max_query_tokens=budget)
                assert len(expected_messages) == 2
                assert len(requests) <= 1 + manifest['repair_limit']
                for index, event in enumerate(requests):
                    request = event['request']
                    assert request['messages'][:2] == expected_messages, (folder.name, 'model input')
                    assert len(request['messages']) == 2 + index * 2, (folder.name, 'repair messages')
                    assert 'tools' not in request
                    assert request.get('stream') is False
                    assert 'enable_search' not in request
                    assert request['model'] == manifest['model']
                    assert request['max_tokens'] == manifest['max_tokens']
                    for key, value in manifest['request_options'].items():
                        assert request[key] == value
                if plan:
                    assert len(responses) == len(requests) and responses
                    parsed = []
                    for response in responses:
                        choices = response['response']['choices']
                        assert choices and choices[0]['finish_reason'] == 'stop'
                        assert not choices[0]['message'].get('tool_calls')
                        parsed.append(parse(choices[0]['message']['content'], tokenizer, prefix, budget))
                    first_errors, final_errors = parsed[0][1], parsed[-1][1]
                    assert plan['initial_errors'] == first_errors
                    assert plan['errors'] == final_errors
                    assert plan['initial_valid'] == (not first_errors)
                    assert plan['repairs'] == len(requests) - 1 == int(bool(first_errors))
                    assert plan['query'] == (None if final_errors else parsed[-1][0]['query'])
                    expected_status = ('invalid' if final_errors else
                                       'abstained' if plan['query'] is None else 'valid')
                    assert plan['status'] == expected_status
                for index, event in enumerate(requests[1:], 1):
                    previous = responses[index - 1]['response']['choices'][0]['message']['content']
                    previous_errors = parse(previous, tokenizer, prefix, budget)[1]
                    assert previous_errors
                    expected_repair = [dict(role='assistant', content=previous or ''),
                        dict(role='user', content=json.dumps(dict(
                            instruction='Repair only the output contract using the same supplied source text. Do not invent facts. '
                                        'For a budget error omit whole conditions without changing retained facts, or return query null. Return only JSON.',
                            validation_errors=previous_errors), ensure_ascii=False))]
                    assert event['request']['messages'][2:] == expected_repair
            expected_refs = ([u['ref'] for u in case['question']['units']]
                             if arm == 'expression_full_context' else packet['input_refs'])
            query_tokens = None
            if plan:
                assert plan['input_refs'] == expected_refs
                assert 0 <= plan['repairs'] <= manifest['repair_limit']
                if plan['query'] is not None:
                    query_tokens = query_token_count(plan['query'], tokenizer, prefix)
                    assert plan['query_tokens'] == query_tokens
                if plan['status'] == 'valid':
                    assert isinstance(plan['query'], str) and plan['query'].strip()
                    assert query_tokens <= budget
            starts = [e for e in events if e['kind'] == 'search_start']
            searches = [e for e in events if e['kind'] == 'search_result']
            finalized = [e for e in events if e['kind'] == 'query_finalized']
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
                assert result['result'] == observations[0]['result']
            else:
                assert not result['result'] and not observations
            with sqlite3.connect(f'file:{folder}/observations.sqlite?mode=ro', uri=True) as ledger:
                assert [json.loads(v) for (v,) in ledger.execute(
                    'select result from events where active=1 order by seq')] == [o['result'] for o in observations]
            handoff = read(folder / 'handoff.json')
            assert handoff['schema_version'] == 'basis_packet_handoff_v1'
            assert handoff['original_question'] == case['question']
            assert handoff['packet_id'] == packet['packet_id']
            assert handoff['status'] == result['status']
            assert len(handoff['search_attempts']) == len(starts)
            if starts:
                attempt = handoff['search_attempts'][0]
                assert attempt['attempt_id'] == run.name + '/' + folder.name
                assert attempt['packet_id'] == packet['packet_id']
                assert attempt['input_refs'] == expected_refs
                assert attempt['method'] == arm and attempt['query'] == plan['query']
                assert attempt['arguments'] == starts[0]['arguments']
                assert attempt['status'] == result['status'] and attempt['result'] == result['result']
            assert len(result['result']) <= manifest['k']
            tokens, hits = 0, []
            for rank, window in enumerate(result['result'], 1):
                if window['docid'] not in cache:
                    cache[window['docid']] = db.execute(
                        'select text,url from documents where docid=?', (window['docid'],)).fetchone()
                text, url = cache[window['docid']]
                text_digest = hashlib.sha256(text.encode()).hexdigest()
                assert window['document_sha256'] == text_digest and window['url'] == url
                assert window['text'] == text[window['offset']:window['end_char']]
                assert window['window_ref'] == 'w_' + hashlib.sha256(
                    f"raw-v1:{window['docid']}:{text_digest}:{window['offset']}:{window['end_char']}".encode()).hexdigest()[:24]
                assert window['has_more_before'] == (window['offset'] > 0)
                assert window['has_more_after'] == (window['end_char'] < len(text))
                if window['title_span']:
                    a, b = window['title_span']
                    assert window['title'] == text[a:b]
                size = window['text_tokens'] + window['title_tokens']
                assert size <= manifest['window_tokens']
                tokens += size
                key = (result['qid'], window['docid'])
                entry = pool.setdefault(key, dict(qid=result['qid'], docid=window['docid'],
                    title=window['title'], url=window['url'], windows={}, occurrences=[]))
                entry['windows'][window['window_ref']] = window
                entry['occurrences'].append(dict(session=result['session'], arm=arm, rank=rank,
                                                  window_ref=window['window_ref']))
                annotation = reference.get(key)
                if annotation:
                    assert annotation['document_sha256'] == text_digest
                    for option in annotation['proof_alternatives']:
                        for proof in option:
                            assert proof['source_spans']
                            for a, b in proof['source_spans']:
                                assert text[a:b] == proof['quote'], (key, 'annotation span')
                    ranges = [[window['offset'], window['end_char']]] + (
                        [window['title_span']] if window['title_span'] else [])
                    visible = any(all(any(any(lo <= a and b <= hi for lo, hi in ranges)
                                          for a, b in proof['source_spans']) for proof in option)
                                  for option in annotation['proof_alternatives'])
                    hits.append(dict(docid=window['docid'], rank=rank, window_ref=window['window_ref'],
                                     reference_visible=visible, kind=annotation['kind'],
                                     packet_alignment=annotation['packet_alignment']))
            assert tokens <= manifest['total_window_budget']
            selected_hits = [h for h in hits if h['packet_alignment'] == 'selected_basis']
            sessions.append(dict(**summary, query=plan['query'] if plan else None,
                query_tokens=query_tokens, initial_valid=plan.get('initial_valid') if plan else None,
                repairs=plan.get('repairs', 0) if plan else max(0, len(requests) - 1),
                initial_errors=plan.get('initial_errors', []) if plan else [],
                windows=len(result['result']), window_tokens=tokens,
                confirmed_document=bool(hits), reference_visible=any(h['reference_visible'] for h in hits),
                selected_basis_document=bool(selected_hits),
                selected_basis_visible=any(h['reference_visible'] for h in selected_hits), hits=hits))
        assert {(s['qid'], s['arm'], s['repeat']) for s in sessions} == scheduled
        assert len(sessions) == len(scheduled)
    finally:
        db.close()
    output = dict(
        mechanical_checks='passed', aggregates={arm: aggregate([s for s in sessions if s['arm'] == arm]) for arm in ARMS},
        per_qid={qid: {arm: aggregate([s for s in sessions if s['qid'] == qid and s['arm'] == arm])
                       for arm in ARMS} for qid in cases}, sessions=sessions,
        annotated_qids=sorted({a['qid'] for a in annotations}),
        note='Frozen positive-source pool, not complete qrels. Main packet utility uses selected_basis hits; outside_selected_basis is separate. Unmatched means unassessed. All scheduled attempts remain denominators, including failures and abstentions. Verbatim once per question; three model repetitions are not independent questions. Mechanical provenance does not establish semantic fidelity or final answer accuracy.')
    dump(run / 'audit.json', output)
    for entry in pool.values():
        entry['windows'] = list(entry['windows'].values())
    dump(run / 'review_pool.json', list(pool.values()))
    lines = ['# Fixed BasisPacket query listing', '', output['note'], '']
    for qid, case in cases.items():
        lines.extend([f'## qid {qid}', '', 'Selected refs: ' + ', '.join(case['basis_refs']), '',
                      'Original question:', '', '```text', case['question']['text'], '```', ''])
        for session in [s for s in sessions if s['qid'] == qid]:
            lines.extend([f"### {session['arm']} r{session['repeat']}", '',
                f"Status: {session['status']}; query tokens: {session['query_tokens']}; repairs: {session['repairs']}", '',
                '```text', session['query'] or '(no query)', '```', '',
                'Frozen positive hits: ' + json.dumps(session['hits'], ensure_ascii=False), ''])
    (run / 'queries.md').write_text('\n'.join(lines), encoding='utf-8')
    return output


if __name__ == '__main__':
    print(json.dumps(audit(sys.argv[1])['aggregates'], ensure_ascii=False, indent=2))
