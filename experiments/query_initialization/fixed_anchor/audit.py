"""Mechanical checks plus fixed positive-reference coverage, not complete qrels."""
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from experiments.query_initialization.fixed_anchor.generate import payload, parse


def audit(run):
    run = Path(run)
    manifest = json.loads((run / 'manifest.json').read_text())
    for rel, digest in manifest['source_sha256'].items():
        assert hashlib.sha256((run / 'source' / rel).read_bytes()).hexdigest() == digest, rel
    cases = {c['qid']: c for c in json.loads((run / 'tasks.json').read_text())}
    annotations = json.loads((run / 'reference_annotations.json').read_text())['annotations']
    assert hashlib.sha256((run / 'reference_annotations.json').read_bytes()).hexdigest() == manifest['reference_annotations_sha256']
    reference = {(a['qid'], a['docid']): a for a in annotations}
    db = sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro', uri=True)
    cache, sessions, pool = {}, [], {}
    for folder in sorted(run.glob('qid_*')):
        r = json.loads((folder / 'result.json').read_text())
        s = json.loads((folder / 'summary.json').read_text())
        events = [json.loads(l) for l in (folder / 'events.jsonl').read_text().splitlines()]
        obs = json.loads((folder / 'observations.json').read_text())
        requests = [e for e in events if e['kind'] == 'api_request']
        if r['arm'] == 'model':
            for e in requests:
                assert json.loads(e['request']['messages'][1]['content']) == payload(cases[r['qid']])
                assert 'tools' not in e['request']
            if r['plan'] and r['plan']['status'] == 'valid':
                assert not parse(json.dumps({'query': r['plan']['query']}))[1]
        else:
            assert not requests
            assert r['plan']['query'] == cases[r['qid']][r['arm'] + '_query']
        starts = [e for e in events if e['kind'] == 'search_start']
        assert len(starts) <= 1
        if starts:
            end = next(e for e in events if e['kind'] == 'query_finalized')
            assert end['seq'] < starts[0]['seq']
            assert not requests or requests[-1]['seq'] < end['seq']
            assert starts[0]['arguments'] == dict(query=r['plan']['query'], k=6)
        assert [e['result'] for e in events if e['kind'] == 'search_result'] == [o['result'] for o in obs]
        if r['status'] == 'complete':
            assert r['result'] == obs[0]['result']
        ledger = sqlite3.connect(f'file:{folder}/observations.sqlite?mode=ro', uri=True)
        assert [json.loads(v) for (v,) in ledger.execute('select result from events where active=1 order by seq')] == [o['result'] for o in obs]
        ledger.close()
        assert len(r['result']) <= 6
        tokens, hits = 0, []
        for rank, w in enumerate(r['result'], 1):
            if w['docid'] not in cache:
                cache[w['docid']] = db.execute('select text,url from documents where docid=?', (w['docid'],)).fetchone()
            text, url = cache[w['docid']]
            digest = hashlib.sha256(text.encode()).hexdigest()
            assert w['document_sha256'] == digest and w['url'] == url
            assert w['text'] == text[w['offset']:w['end_char']]
            assert w['window_ref'] == 'w_' + hashlib.sha256(f"raw-v1:{w['docid']}:{digest}:{w['offset']}:{w['end_char']}".encode()).hexdigest()[:24]
            assert w['has_more_before'] == (w['offset'] > 0) and w['has_more_after'] == (w['end_char'] < len(text))
            if w['title_span']:
                a, b = w['title_span']
                assert w['title'] == text[a:b]
            size = w['text_tokens'] + w['title_tokens']
            assert size <= 400
            tokens += size
            key = (r['qid'], w['docid'])
            entry = pool.setdefault(key, dict(qid=r['qid'], docid=w['docid'], title=w['title'], url=w['url'], windows={}))
            entry['windows'][w['window_ref']] = w
            ann = reference.get(key)
            if ann:
                assert ann['document_sha256'] == digest
                ranges = [[w['offset'], w['end_char']]] + ([w['title_span']] if w['title_span'] else [])
                visible = any(all(any(any(lo <= a and b <= hi for lo, hi in ranges)
                                          for a, b in proof['source_spans']) for proof in option)
                              for option in ann['proof_alternatives'])
                hits.append(dict(docid=w['docid'], rank=rank, window_ref=w['window_ref'], reference_visible=visible, kind=ann['kind']))
        assert tokens <= 2400
        sessions.append(dict(**s, query=r['plan']['query'] if r['plan'] else None,
                             windows=len(r['result']), window_tokens=tokens,
                             confirmed_document=bool(hits), reference_visible=any(h['reference_visible'] for h in hits), hits=hits))
    scheduled = {(s['qid'], s['arm'], s['repeat']) for s in json.loads((run / 'schedule.json').read_text())}
    assert {(s['qid'], s['arm'], s['repeat']) for s in sessions} == scheduled
    aggregates = {}
    for arm in ['full', 'delete', 'model']:
        rs = [r for r in sessions if r['arm'] == arm]
        aggregates[arm] = dict(attempts=len(rs), complete=sum(r['status'] == 'complete' for r in rs),
            api_requests=sum(r['api_requests'] for r in rs), windows=sum(r['windows'] for r in rs),
            confirmed_document=sum(r['confirmed_document'] for r in rs), reference_visible=sum(r['reference_visible'] for r in rs),
            usage={key: sum(r['usage'][key] for r in rs) for key in ['prompt_tokens', 'completion_tokens', 'total_tokens']})
    result = dict(aggregates=aggregates, sessions=sessions,
                  note='Reference counts use pre-existing positive spans only. qid645 and qid786 have no positive annotations. Unmatched is unassessed. Controls once/question; model repeats clustered within question. No final accuracy or global recall.')
    (run / 'audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    for entry in pool.values():
        entry['windows'] = list(entry['windows'].values())
    (run / 'review_pool.json').write_text(json.dumps(list(pool.values()), ensure_ascii=False, indent=2))
    db.close()
    return result


if __name__ == '__main__':
    print(json.dumps(audit(sys.argv[1])['aggregates'], ensure_ascii=False, indent=2))
