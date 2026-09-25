"""Frozen inputs and deterministic review helpers for this diagnostic cohort."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
U1 = ROOT / 'experiments/unified_global_retrieval/document_rediscovery'
DB = ROOT / 'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite'
INDEX = ROOT / 'BCPlus/indexes/qwen3-embedding-8b'


def read(path):
    return json.loads(Path(path).read_text())


def write(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def bank():
    cases = {x['case_id']: x for x in read(U1 / 'BANK.json')}
    truth = {x['case_id']: x for x in read(U1 / 'PRIVATE_TRUTH.json')}
    queries = {x['case_id']: x for x in read(U1 / 'QUERIES.json')}
    assert set(cases) == set(truth) == set(queries) and len(cases) == 40
    return [dict(cases[key], truth=truth[key], queries=queries[key]) for key in sorted(cases)]


def metrics(rows, hit_key='hit'):
    groups = {'overall': rows, 'A/B': [r for r in rows if r['primary_type'] in 'AB'],
              'C/D': [r for r in rows if r['primary_type'] in 'CD']}
    groups.update({t: [r for r in rows if r['primary_type'] == t] for t in 'ABCD'})
    return {name: {'hit': sum(bool(x[hit_key]) for x in items), 'n': len(items),
                   'rate': sum(bool(x[hit_key]) for x in items) / len(items) if items else None}
            for name, items in groups.items()}
