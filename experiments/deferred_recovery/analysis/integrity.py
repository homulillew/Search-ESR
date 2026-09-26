"""Read-only final audit of frozen inputs, real continuation, and one-attempt trace.

No model or research tool calls. Writes only this run's final audit artifacts.
"""
import copy
import hashlib
import json
import sqlite3
import subprocess
import sys
from collections import Counter
from pathlib import Path

TOP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOP))
from run import ROOT, actor_items, actor_view, initial, item, writer_view
from runtime import decode, digest, read, schema, usage, validate_object, write
from jsonschema import Draft202012Validator

BASE = '2544fbf0c5488d8b1c84f36577ea36f1beee2da2'
STAGE_HEAD = {'r1': '21afbd857d33214956298a6d07c8fa10c9a848c2',
              'r2': 'fd281cec00639db3ee589f7d10f533fcca1ced83'}


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def committed(head, path):
    rel = str(path.relative_to(ROOT))
    return subprocess.check_output(['git', 'show', head + ':' + rel])


def main():
    counters = Counter()
    historic = read(TOP / 'analysis/HISTORICAL_HASHES.json')
    base_paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', '-z', BASE]).decode().split('\0')
    assert set(historic) == set(filter(None, base_paths))
    for path, expected in historic.items():
        assert file_hash(ROOT / path) == expected, path
    counters['historical_files_unchanged'] = len(historic)
    freeze = read(TOP / 'freeze.json')
    assert committed(STAGE_HEAD['r1'], TOP / 'freeze.json') == (TOP / 'freeze.json').read_bytes()
    for path, expected in freeze['files'].items():
        assert file_hash(ROOT / path) == expected, path
    counters['frozen_files_unchanged'] = len(freeze['files'])
    for name, expected in freeze['binary_files'].items():
        path = Path(name)
        assert path.stat().st_size == expected['size'], name
        assert path.stat().st_mtime_ns == expected['mtime_ns'], name
        assert file_hash(path) == expected['sha256'], name
        print('verified binary', path.name, flush=True)
    counters['full_binary_hashes_unchanged'] = len(freeze['binary_files'])
    assert freeze['max_retries'] == 0 and freeze['k'] == 5
    assert (TOP / 'prompts/writer.md').read_bytes() == (ROOT / 'experiments/goal_residual_control_v3_1/prompts/state_updater_gap_conditioned.md').read_bytes()
    first = initial()
    assert actor_items(first, 0) == read(TOP / 'r1/requests.json')
    for cid in {c['case_id'] for c in first.values()}:
        g, h = (actor_view(first[cid + ':' + arm], 0) for arm in ['G', 'H'])
        for key in g:
            if key not in ['Tool schema', 'Response schema']:
                assert g[key] == h[key]
        assert g['New Observations'] == g['Recent Attempts'] == []
        assert all(set(d) == {'doc_ref', 'title', 'url'} for d in g['Historical Document Catalog'])
        assert set(g) == {'Original Question', 'Current Claims', 'Working Hypothesis',
                          'Current Recovery Need', 'Historical Document Catalog', 'Recent Attempts',
                          'New Observations', 'Budget', 'Tool schema', 'Response schema'}
    continuation = read(TOP / 'r2/continuation_freeze.json')
    assert file_hash(TOP / 'r1/post_writer_cells.json') == continuation['r1_cells_sha256']
    assert file_hash(TOP / 'r2/requests.json') == continuation['requests_sha256']
    for name in ['requests.json', 'continuation_freeze.json']:
        assert committed(STAGE_HEAD['r2'], TOP / 'r2' / name) == (TOP / 'r2' / name).read_bytes()
    assert actor_items(read(TOP / 'r1/post_writer_cells.json'), 1) == read(TOP / 'r2/requests.json')
    events = {}
    totals = Counter()
    for stage in ['r1', 'r2']:
        for path in sorted((TOP / stage).glob('*_events.jsonl')):
            if path.name == 'tool_events.jsonl':
                continue
            rows = [json.loads(line) for line in path.open()]
            starts = [x for x in rows if x['kind'] == 'request_started']
            ends = [x for x in rows if x['kind'] == 'completed']
            key = lambda x: (x['case_id'], x['arm'])
            assert len(starts) == len(ends) == len({key(x['item']) for x in starts})
            assert len(ends) == len({key(x['result']) for x in ends})
            start_by_key = {key(x['item']): x for x in starts}
            output = read(path.with_name(path.name.replace('_events.jsonl', '_outputs.json')))
            assert {key(r): r for r in output} == {key(e['result']): e['result'] for e in ends}
            for e in ends:
                ev, result = e['event'], e['result']
                start = start_by_key[key(result)]
                assert {k: ev[k] for k in ['item', 'started_utc', 'run_head']} == {k: start[k] for k in ['item', 'started_utc', 'run_head']}
                assert rows.index(start) < rows.index(e)
                it, raw = ev['item'], ev['response']
                assert ev['run_head'] == STAGE_HEAD[stage]
                assert it['request_sha256'] == result['request_sha256'] == digest(it['request'])
                assert ev['http_status'] == 200 and json.loads(ev['response_text']) == raw
                assert it['request']['model'] == raw['model'] == 'deepseek-flash'
                assert it['request']['response_format'] == {'type': 'json_object'}
                assert result['attempted'] and result['structural_valid'] and result['harness_valid']
                assert result['error'] is None
                out = decode(raw, it['mode'])
                assert out == ev['parsed_output'] == result['output']
                Draft202012Validator(schema(it['kind'])).validate(out)
                view = json.loads(it['request']['messages'][1]['content'])
                validate_object(out, it['kind'], {'known_documents': view.get('Historical Document Catalog', []),
                                                'observed_windows': view.get('New Observations', [])})
                u = usage(raw, it['mode'])
                assert u == result['usage'] and u['input'] == u['hit'] + u['miss']
                totals.update(u)
                tag = path.name.removesuffix('_events.jsonl')
                events[stage, tag, it['case_id'] + ':' + it['arm']] = e
                counters['actor_calls' if tag == 'actor' else 'writer_calls'] += 1
            counters['request_starts'] += len(starts)
            counters['request_completions'] += len(ends)
    db = sqlite3.connect(f"file:{ROOT / 'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite'}?mode=ro", uri=True)
    docs = {}

    def check_registry(c):
        docmap = {}
        for d in c['registry']['documents']:
            did = d['docid']
            if did not in docs:
                text, url = db.execute('select text,url from documents where docid=?', (did,)).fetchone()
                docs[did] = (text, url, hashlib.sha256(text.encode()).hexdigest())
            text, url, sha = docs[did]
            assert sha == d['document_sha256'] and url == d['url']
            docmap[d['doc_ref']] = text
        for w in c['registry']['windows']:
            assert docmap[w['doc_ref']][w['offset']:w['offset'] + len(w['text'])] == w['text']
            assert hashlib.sha256(w['text'].encode()).hexdigest() == w['text_sha256']
        assert all(set(d) == {'doc_ref', 'title', 'url'} for d in c['catalog'])

    for rnd, stage in enumerate(['r1', 'r2']):
        previous = first if rnd == 0 else read(TOP / 'r1/post_writer_cells.json')
        final = read(TOP / stage / 'post_writer_cells.json')
        posttool = read(TOP / stage / 'post_tool_cells.json')
        tool_events = [json.loads(line) for line in (TOP / stage / 'tool_events.jsonl').open()]
        starts = {e['cell']: e for e in tool_events if e['kind'] == 'started'}
        ends = {e['cell']: e for e in tool_events if e['kind'] == 'completed'}
        assert len(tool_events) == 2 * len(starts) == 2 * len(ends)
        for key, c in final.items():
            before = previous[key]
            assert c['decisions'][:-1] == before['decisions']
            assert c['updates'][:len(before['updates'])] == before['updates']
            assert c['claims'][:len(before['claims'])] == before['claims']
            assert c['registry']['documents'][:len(before['registry']['documents'])] == before['registry']['documents']
            assert len(c['decisions']) == rnd + 1
            actor = c['decisions'][-1]['actor']
            assert actor == events[stage, 'actor', key]['result']
            assert item(before, 'actor_' + c['arm'], actor_view(before, rnd)) == events[stage, 'actor', key]['event']['item']
            t = c['decisions'][-1]['tool']
            if actor['output']['decision'] == 'stop':
                assert t is None and key not in starts
                counters['actor_stops'] += 1
            else:
                assert t['error'] is None
                assert actor['output']['actions'] == [t['action']]
                assert starts[key]['action'] == t['action'] and ends[key]['record'] == t
                assert tool_events.index(starts[key]) < tool_events.index(ends[key])
                counters[t['action']['tool'] + '_calls'] += 1
                reg = {w['window_ref']: w for w in c['registry']['windows']}
                for w in t['observations']:
                    assert w == reg[w['window_ref']]
                if t['action']['tool'] == 'search':
                    assert t['action']['k'] == 5
                    assert [x['preview_ref'] for x in t['result']['results']] == [w['window_ref'] for w in t['observations']]
                    assert [x['preview'] for x in t['result']['results']] == [w['text'] for w in t['observations']]
                counters['new_observations'] += len(t['observations'])
            simulated = copy.deepcopy(posttool[key])
            updates = [u for u in c['updates'] if u['round'] == rnd]
            assert len(updates) == (len(t['observations']) if t else 0)
            for u in updates:
                assert u['pre_state'] == {'claims': simulated['claims'], 'hypothesis': simulated['hypothesis']}
                assert u['observation'] == t['observations'][u['wave']]
                ev = events[stage, 'writer' + str(u['wave']), key]
                assert u['proposal'] == ev['result']
                assert item(simulated, 'state_updater', writer_view(simulated, u['observation'])) == ev['event']['item']
                o, w = u['proposal']['output'], u['observation']
                assert len(o['claims_to_add']) <= 2
                for txt in o['claims_to_add']:
                    simulated['claims'].append({'statement': txt, 'support_refs': [w['window_ref']],
                        'source_text_hashes': [w['text_sha256']], 'first_seen_time': [{'round': rnd, 'wave': u['wave']}],
                        'admission': 'unrepaired online U1 proposal; semantic support evaluated offline'})
                h = o['hypothesis_update']
                if h['action'] == 'set':
                    simulated['hypothesis'] = h['statement']
                elif h['action'] == 'clear':
                    simulated['hypothesis'] = None
                assert u['post_state'] == {'claims': simulated['claims'], 'hypothesis': simulated['hypothesis']}
            assert simulated['claims'] == c['claims'] and simulated['hypothesis'] == c['hypothesis']
            check_registry(c)
    db.close()
    assert counters['actor_calls'] == 28 and counters['writer_calls'] == 72
    assert counters['request_starts'] == counters['request_completions'] == 100
    assert counters['search_calls'] == 13 and counters['find_calls'] == 8 and counters['open_calls'] == 0
    assert counters['new_observations'] == counters['writer_calls']
    report = {'status': 'PASS', 'scope': 'Mechanical integrity, not semantic-review independence or primary efficacy',
              'base': BASE, 'stage_heads': STAGE_HEAD, 'checks': dict(counters),
              'binary_bytes_rehashed': sum(v['size'] for v in freeze['binary_files'].values()),
              'distinct_corpus_documents_verified': len(docs), 'usage': dict(totals),
              'cache_hit_rate': totals['hit'] / totals['input'],
              'errors': {'transport_structural_failure': 0, 'harness_control_violation': 0,
                         'length/incomplete': 0, 'provider_failure': 0, 'tool_failure': 0},
              'no_retry_or_repair': True, 'historical_claims_append_only': True,
              'initial_context_is_metadata_only_catalog': True, 'private_truth_excluded_by_exact_view_reconstruction': True,
              'r1_preserved_into_r2': True, 'all_observations_grounded_in_frozen_corpus': True,
              'all_writer_proposals_applied_without_semantic_repair': True,
              'no_new_model_or_tool_calls_in_audit': True}
    write(TOP / 'analysis/FINAL_INTEGRITY.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
