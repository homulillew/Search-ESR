"""K0: one Qwen3/FAISS top-50 retrieval per frozen U1 query."""
import json
import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parents[2]))
from experiments.global_retrieval_robustness.common import U1, bank, read, write, metrics


def main():
    freeze = read(BASE / 'freeze.json')
    cases = bank()
    assert freeze['case_order'] == [x['case_id'] for x in cases]
    assert freeze['k_values'] == [5, 10, 20, 50]
    os.environ['BCPLUS_DEVICE'] = freeze['device']
    from BCPlus.scripts.search_bcplus import BCPlusSearcher, PREFIX
    import torch
    searcher = BCPlusSearcher()
    baseline = {x['case_id']: x for x in read(U1 / 'gpu_replication/retrieval_results.json')}
    rows = []
    try:
        for case in cases:
            q = case['queries']['search_query']
            batch = searcher.tokenizer(PREFIX + q, return_tensors='pt', truncation=False)
            if batch['input_ids'].shape[1] > 8192:
                raise ValueError(f"oversize query {case['case_id']}")
            with torch.inference_mode():
                hidden = searcher.model(**batch.to(searcher.device)).last_hidden_state[:, -1]
                vector = torch.nn.functional.normalize(hidden, p=2, dim=1).float().cpu().numpy()
            scores, positions = searcher.index.search(vector, 50)
            hits = [{'rank': n, 'docid': searcher.docids[int(pos)], 'score': float(score)}
                    for n, (score, pos) in enumerate(zip(scores[0], positions[0]), 1)]
            old = baseline[case['case_id']]['G']
            assert [h['docid'] for h in hits[:5]] == [h['docid'] for h in old], case['case_id']
            target = set(case['truth']['sufficient_doc_ids'])
            first = next((h for h in hits if h['docid'] in target), None)
            rows.append({'case_id': case['case_id'], 'qid': case['qid'],
                         'primary_type': case['primary_type'],
                         'grounded_candidate': case['writer_input']['working_hypothesis'] is not None,
                         'sufficient_doc_ids': sorted(target), 'hits': hits,
                         'first_sufficient_rank': first['rank'] if first else None,
                         'first_sufficient_docid': first['docid'] if first else None})
            print(f"{case['case_id']} rank={rows[-1]['first_sufficient_rank']}", flush=True)
    finally:
        searcher.close()
    write(BASE / 'results.json', {'freeze': 'freeze.json', 'rows': rows})
    summary = {}
    for k in freeze['k_values']:
        rr = [dict(r, hit=r['first_sufficient_rank'] is not None and r['first_sufficient_rank'] <= k)
              for r in rows]
        summary[str(k)] = metrics(rr)
        for grounded in [True, False]:
            sub = [r for r in rr if r['grounded_candidate'] == grounded]
            summary[str(k)]['grounded' if grounded else 'ungrounded'] = metrics(sub)['overall']
    mrr = sum(1 / r['first_sufficient_rank'] for r in rows if r['first_sufficient_rank']) / len(rows)
    write(BASE / 'summary.json', {'recall': summary, 'MRR@50': mrr,
                                 'single_query_10_pass': summary['10']['A/B']['hit'] >= 19
                                 and summary['10']['C/D']['hit'] >= 18
                                 and summary['10']['overall']['hit'] >= 37})


if __name__ == '__main__':
    main()
