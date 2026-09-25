"""Equal-budget Q1 vs Q1+Q2 retrieval, after committed Query2 outputs."""
import json
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parents[2]))
from experiments.global_retrieval_robustness.common import HERE, ROOT, bank, metrics, read, sha, write


def freeze_retrieval():
    q = read(BASE / 'QUERY2.json')
    f = read(BASE / 'freeze.json')
    assert [x['case_id'] for x in q] == f['case_order']
    assert not (BASE / 'retrieval_freeze.json').exists()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    changed = subprocess.check_output(['git', 'status', '--porcelain', '--', str(BASE / 'QUERY2.json'),
                                       str(BASE / 'query2_events.jsonl')], cwd=ROOT, text=True)
    assert not changed, 'Query2 outputs must be committed before retrieval'
    prior = read(HERE / 'rank_depth/freeze.json')
    write(BASE / 'retrieval_freeze.json', {'git_head': head, 'query2_sha256': sha(BASE / 'QUERY2.json'),
          'query2_events_sha256': sha(BASE / 'query2_events.jsonl'), 'query1_top50_sha256': sha(HERE / 'rank_depth/results.json'),
          'index_sha256': prior['index_sha256'], 'retriever_sha256': prior['retriever_sha256'],
          'case_order': f['case_order'], 'device': 'cuda:1', 'q2_k': 5,
          'rrf_constant': 60, 'tie_break': 'docid ascending', 'failure_policy': 'Invalid Query2 is a miss; no retry'} )


def run():
    f = read(BASE / 'retrieval_freeze.json')
    assert f['query2_sha256'] == sha(BASE / 'QUERY2.json')
    assert f['query1_top50_sha256'] == sha(HERE / 'rank_depth/results.json')
    assert not (BASE / 'retrieval_results.json').exists()
    q = {x['case_id']: x for x in read(BASE / 'QUERY2.json')}
    old = {x['case_id']: x for x in read(HERE / 'rank_depth/results.json')['rows']}
    cases = bank()
    os.environ['BCPLUS_DEVICE'] = f['device']
    from BCPlus.scripts.search_bcplus import BCPlusSearcher
    searcher = BCPlusSearcher()
    rows = []
    try:
        for c in cases:
            cid = c['case_id']; q1 = old[cid]['hits'][:5]; q2 = q[cid]
            if q2['search_query']:
                raw = searcher.search(q2['search_query'], 5)
                h2 = [{'rank': i, 'docid': h['docid'], 'score': h['score']}
                      for i, h in enumerate(raw, 1)]
            else:
                h2 = []
            ranks = {}
            for label, hits in [('q1', q1), ('q2', h2)]:
                for h in hits:
                    ranks.setdefault(h['docid'], {})[label] = h['rank']
            fused = [{'docid': docid, 'rrf_score': sum(1 / (60 + n) for n in r.values()),
                      'rank_q1': r.get('q1'), 'rank_q2': r.get('q2')}
                     for docid, r in ranks.items()]
            fused.sort(key=lambda x: (-x['rrf_score'], x['docid']))
            for i, h in enumerate(fused, 1):
                h['rank'] = i
            truth = set(c['truth']['sufficient_doc_ids'])
            s10 = any(h['docid'] in truth for h in old[cid]['hits'][:10])
            d10 = any(h['docid'] in truth for h in fused)
            f5 = any(h['docid'] in truth for h in fused[:5])
            set1 = {h['docid'] for h in q1}; set2 = {h['docid'] for h in h2}
            rows.append({'case_id': cid, 'qid': c['qid'], 'primary_type': c['primary_type'],
                         'q2_error': q2['error'], 'q1_top5': q1, 'q2_top5': h2, 'fused': fused,
                         'S10_hit': s10, 'D5_5_hit': d10, 'fused5_hit': f5,
                         'jaccard': len(set1 & set2) / len(set1 | set2) if set1 | set2 else None})
            print(cid, 'S10', int(s10), 'D5+5', int(d10), flush=True)
    finally:
        searcher.close()
    write(BASE / 'retrieval_results.json', {'rows': rows, 'freeze': 'retrieval_freeze.json'})
    rescue = [r['case_id'] for r in rows if not r['S10_hit'] and r['D5_5_hit']]
    regress = [r['case_id'] for r in rows if r['S10_hit'] and not r['D5_5_hit']]
    summary = {'S10': metrics([dict(r, hit=r['S10_hit']) for r in rows]),
               'D5_5': metrics([dict(r, hit=r['D5_5_hit']) for r in rows]),
               'fused5': metrics([dict(r, hit=r['fused5_hit']) for r in rows]),
               'rescue': rescue, 'regression': regress, 'net_paired_rescue': len(rescue) - len(regress),
               'mean_jaccard': sum(r['jaccard'] for r in rows if r['jaccard'] is not None) /
                               sum(r['jaccard'] is not None for r in rows),
               'qid_breadth': {str(qid): {'n': sum(r['qid'] == qid for r in rows),
                    'S10_hit': sum(r['qid'] == qid and r['S10_hit'] for r in rows),
                    'D5_5_hit': sum(r['qid'] == qid and r['D5_5_hit'] for r in rows)}
                    for qid in sorted({r['qid'] for r in rows})}}
    d = summary['D5_5']
    summary['dual_pass'] = (d['A/B']['hit'] >= 19 and d['C/D']['hit'] >= 18 and
                            d['overall']['hit'] >= 37 and summary['net_paired_rescue'] >= 2 and
                            len(regress) <= 1)
    write(BASE / 'summary.json', summary)


if __name__ == '__main__':
    if sys.argv[1:] == ['freeze']:
        freeze_retrieval()
    elif sys.argv[1:] == ['run']:
        run()
    else:
        raise SystemExit('Usage: retrieve.py freeze|run')
