"""F2: predetermined Top1 and parallel Top2 Find using frozen ranking."""
import hashlib
import json
import sqlite3
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parents[2]))
from experiments.global_retrieval_robustness.common import DB, HERE, ROOT, U1, read, sha, write


def freeze_policy():
    oracle = read(BASE / 'freeze.json')
    assert (BASE / 'oracle_reviews.json').exists()
    k0 = read(HERE / 'rank_depth/summary.json')
    q1 = read(HERE / 'query_robustness/summary.json') if (HERE / 'query_robustness/summary.json').exists() else None
    if k0['single_query_10_pass']:
        source = 'single_query_10'; source_path = HERE / 'rank_depth/results.json'
        ranking = {r['case_id']: [h['docid'] for h in r['hits'][:2]] for r in read(source_path)['rows']}
        deployable = True
    elif q1 and q1['dual_pass']:
        source = 'dual_query_5_5_rrf'; source_path = HERE / 'query_robustness/retrieval_results.json'
        ranking = {r['case_id']: [h['docid'] for h in r['fused'][:2]] for r in read(source_path)['rows']}
        deployable = True
    else:
        source = 'U1_G_top5_diagnostic'; source_path = U1 / 'gpu_replication/retrieval_results.json'
        ranking = {r['case_id']: [h['docid'] for h in r['G'][:2]] for r in read(source_path)}
        deployable = False
    bank = read(BASE / 'BANK.json')
    cases = []
    for b in bank:
        docs = ranking[b['case_id']]
        assert len(docs) == 2 and docs[0] != docs[1]
        cases.append({'case_id': b['case_id'], 'qid': b['qid'], 'primary_type': b['primary_type'],
                      'rank1_docid': docs[0], 'rank2_docid': docs[1], 'find_query': b['find_query']})
    assert [x['case_id'] for x in cases] == oracle['case_order']
    write(BASE / 'policy_bank.json', cases)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    write(BASE / 'policy_freeze.json', {'git_head': head, 'ranking_source': source,
          'ranking_deployable': deployable, 'ranking_source_sha256': sha(source_path),
          'k0_summary_sha256': sha(HERE / 'rank_depth/summary.json'),
          'q1_summary_sha256': sha(HERE / 'query_robustness/summary.json'),
          'oracle_reviews_sha256': sha(BASE / 'oracle_reviews.json'),
          'policy_bank_sha256': sha(BASE / 'policy_bank.json'),
          'find_backend_sha256': oracle['find_backend_sha256'], 'tokenizer': oracle['tokenizer'],
          'search_budget_tokens': 400, 'case_order': oracle['case_order'],
          'arms': {'P1': 'rank1 Find', 'P2': 'rank1 and rank2 concurrent Find'},
          'max_parallel_finds': 2, 'P1_uses_same_rank1_call_as_P2': True,
          'selection_gate': {'useful_hit_gain_min_pp': 10, 'useful_per_call_loss_max_pp': 5},
          'review_rubric': oracle['review_rubric'], 'failure_policy': 'No retry, query rewrite, or adaptive second Find'})


def one(rank, docid, query, docs, tokenizer):
    from llm_chat.search_find_agent import SearchFindTools
    from llm_chat.raw_windows import RawWindowBuilder
    tools = SearchFindTools()
    tools.window_builder = RawWindowBuilder(tokenizer)
    handles = {}
    for d, text, url in docs:
        key = tools.window_builder.register(d, text, url)
        handles[d], _ = tools.handles.document(key)
    try:
        result = tools.execute('find', {'doc_ref': handles[docid], 'query': query})
        return {'rank': rank, 'docid': docid, 'result': result, 'audit': tools.audit_record(), 'error': None}
    except Exception as exc:
        return {'rank': rank, 'docid': docid, 'result': None, 'audit': None,
                'error': f'{type(exc).__name__}: {exc}'}


def run():
    from transformers import AutoTokenizer
    f = read(BASE / 'policy_freeze.json')
    assert f['policy_bank_sha256'] == sha(BASE / 'policy_bank.json')
    cases = read(BASE / 'policy_bank.json')
    assert [x['case_id'] for x in cases] == f['case_order']
    path = BASE / 'policy_find_events.jsonl'
    assert not path.exists()
    tokenizer = AutoTokenizer.from_pretrained(f['tokenizer'], local_files_only=True, use_fast=True)
    db = sqlite3.connect(f'{DB.as_uri()}?mode=ro', uri=True)
    with path.open('w') as out, ThreadPoolExecutor(max_workers=2) as pool:
        for c in cases:
            docs = []
            for docid in [c['rank1_docid'], c['rank2_docid']]:
                row = db.execute('SELECT text,url FROM documents WHERE docid=?', (docid,)).fetchone()
                if row is None:
                    raise ValueError(f'missing document {docid}')
                docs.append((docid, *row))
            f1 = pool.submit(one, 1, c['rank1_docid'], c['find_query'], docs, tokenizer)
            f2 = pool.submit(one, 2, c['rank2_docid'], c['find_query'], docs, tokenizer)
            calls = [f1.result(), f2.result()]
            out.write(json.dumps({'case_id': c['case_id'], 'qid': c['qid'],
                                  'primary_type': c['primary_type'], 'find_query': c['find_query'],
                                  'calls': calls}, ensure_ascii=False) + '\n')
            out.flush()
            print(c['case_id'], [(x['rank'], x['result']['status'] if x['result'] else x['error']) for x in calls], flush=True)
    db.close()


if __name__ == '__main__':
    if sys.argv[1:] == ['freeze']:
        freeze_policy()
    elif sys.argv[1:] == ['run']:
        run()
    else:
        raise SystemExit('Usage: run_policy.py freeze|run')
