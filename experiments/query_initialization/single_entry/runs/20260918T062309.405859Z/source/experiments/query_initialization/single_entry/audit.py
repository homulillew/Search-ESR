"""Verify saved handoffs, raw observations, source versions, budgets and ordering."""
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from experiments.query_initialization.single_entry.source_units import check_question
from experiments.query_initialization.single_entry.initializer import validate
from experiments.query_initialization.initializer import validate as validate_v2


def audit(path):
    path = Path(path)
    manifest = json.loads((path / 'manifest.json').read_text())
    for name, digest in manifest['source_sha256'].items():
        assert hashlib.sha256((path / 'source' / name).read_bytes()).hexdigest() == digest, name
    db = sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro', uri=True)
    cache, rows = {}, []
    tasks = {t['qid']: t['question'] for t in json.loads((path / 'tasks.json').read_text())}
    for folder in sorted(path.glob('qid_*')):
        summary = json.loads((folder / 'summary.json').read_text())
        handoff = json.loads((folder / 'handoff.json').read_text())
        events = [json.loads(line) for line in (folder / 'events.jsonl').read_text().splitlines()]
        obs = json.loads((folder / 'observations.json').read_text())
        ledger = sqlite3.connect(f'file:{folder}/observations.sqlite?mode=ro', uri=True)
        ledger_results = [json.loads(raw) for (raw,) in ledger.execute('select result from events where active=1 order by seq')]
        assert handoff['question'] == tasks[summary['qid']]
        assert handoff['status'] == summary['status']
        check_question(handoff['question'])
        plan = handoff['plan']
        if plan:
            assert plan['question_sha256'] == handoff['question']['sha256']
            if plan['status'] in {'valid', 'no_direction'}:
                if summary['arm'] == 'v2':
                    clean = {'directions': [{k: d[k] for k in ['goal', 'source_clues', 'query']}
                                            for d in plan['raw_plan']['directions']]}
                    assert not validate_v2(clean, handoff['question']['text'], 1)
                else:
                    assert not validate(plan['raw_plan'], handoff['question'], summary['arm'])
            assert len(plan['intents']) <= 1
        starts = [e for e in events if e['kind'] == 'search_start']
        assert len(starts) <= 1
        if starts:
            final = next(e for e in events if e['kind'] == 'plan_finalized')
            assert max(e['seq'] for e in events if e['kind'] == 'api_request') < final['seq'] < starts[0]['seq']
        results = [a['result'] for a in handoff['search_attempts'] if a['status'] == 'complete']
        assert results == [e['result'] for e in events if e['kind'] == 'search_result']
        assert results == [e['result'] for e in obs] == ledger_results
        window_tokens, windows = 0, 0
        for attempt in handoff['search_attempts']:
            assert plan and plan['status'] == 'valid'
            assert attempt['intent'] == plan['intents'][0]
            assert attempt['question_sha256'] == handoff['question']['sha256']
            assert attempt['arguments'] == dict(query=attempt['intent']['query'], k=6)
            assert set(attempt['intent']['basis_refs']) <= {u['ref'] for u in handoff['question']['units']}
            assert attempt['window_refs'] == [w['window_ref'] for w in attempt['result']]
            assert len(attempt['result']) <= 6
            for w in attempt['result']:
                if w['docid'] not in cache:
                    cache[w['docid']] = db.execute('select text,url from documents where docid=?', (w['docid'],)).fetchone()
                text, url = cache[w['docid']]
                assert text[w['offset']:w['end_char']] == w['text'] and w['url'] == url
                assert hashlib.sha256(text.encode()).hexdigest() == w['document_sha256']
                assert w['has_more_before'] == (w['offset'] > 0)
                assert w['has_more_after'] == (w['end_char'] < len(text))
                if w['title_span']:
                    a, b = w['title_span']
                    assert w['title'] == text[a:b]
                assert w['text_tokens'] + w['title_tokens'] <= 400
                window_tokens += w['text_tokens'] + w['title_tokens']
                windows += 1
                stored = ledger.execute('select docid,digest,start,end from windows where ref=?', (w['window_ref'],)).fetchone()
                assert stored == (w['docid'], w['document_sha256'], w['offset'], w['end_char'])
        assert window_tokens <= 2400
        rows.append(dict(**summary, raw_checks_passed=True, window_tokens=window_tokens, windows=windows))
        ledger.close()
    expected = {(s['qid'], s['arm'], s['repeat']) for s in json.loads((path / 'schedule.json').read_text())}
    assert {(s['qid'], s['arm'], s['repeat']) for s in rows} == expected
    aggregates = {}
    for arm in sorted({r['arm'] for r in rows}):
        rs = [r for r in rows if r['arm'] == arm]
        aggregates[arm] = dict(attempts=len(rs), first_valid=sum(r['initial_valid'] for r in rs),
            complete=sum(r['status'] == 'complete' for r in rs), api_requests=sum(r['api_requests'] for r in rs),
            repair_requests=sum(max(0, r['api_requests'] - 1) for r in rs),
            search_calls=sum(r['search_calls'] for r in rs), windows=sum(r['windows'] for r in rs),
            window_tokens=sum(r['window_tokens'] for r in rs),
            usage={key: sum(r['usage'][key] for r in rs) for key in ['prompt_tokens', 'completion_tokens', 'total_tokens']})
    db.close()
    result = dict(aggregates=aggregates, sessions=rows, semantic_success='not inferred from mechanical checks')
    (path / 'audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == '__main__':
    print(json.dumps(audit(sys.argv[1])['aggregates'], ensure_ascii=False, indent=2))
