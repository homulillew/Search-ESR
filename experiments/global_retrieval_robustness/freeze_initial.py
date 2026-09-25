"""Prepare K0/F1 preregistration without performing retrieval or Find calls."""
import hashlib
import sqlite3
import subprocess
from pathlib import Path
from common import HERE, ROOT, U1, DB, INDEX, bank, read, sha, write


def main():
    cases = bank()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    common = {'base_head': head, 'case_order': [x['case_id'] for x in cases],
              'input_sha256': {str(p.relative_to(ROOT)): sha(p) for p in
                               [U1 / 'BANK.json', U1 / 'PRIVATE_TRUTH.json', U1 / 'QUERIES.json']},
              'failure_policy': 'No retry, repair, query edit, or case replacement'}
    index = {str(p.relative_to(ROOT)): sha(p) for p in sorted(INDEX.glob('*.pkl'))}
    k0 = dict(common, retriever_sha256=sha(ROOT / 'BCPlus/scripts/search_bcplus.py'),
              index_sha256=index, sqlite_sha256=sha(DB), model='/data/model/Qwen3-Embedding-8B',
              device='cuda:1', k_values=[5, 10, 20, 50],
              old_top5_sha256=sha(U1 / 'gpu_replication/retrieval_results.json'),
              gates={'A/B': 19, 'C/D': 18, 'overall': 37})
    write(HERE / 'rank_depth/freeze.json', k0)
    db = sqlite3.connect(f'{DB.as_uri()}?mode=ro', uri=True)
    selected = []
    for c in cases:
        t = c['truth']; docid = t['evidence_location']['doc_id']
        row = db.execute('SELECT text,url FROM documents WHERE docid=?', (docid,)).fetchone()
        assert row, (c['case_id'], docid)
        text, url = row
        source_sha = hashlib.sha256(text.encode()).hexdigest()
        assert source_sha == t['evidence_location']['source_text_sha256'], c['case_id']
        anchor = t['evidence_location']['anchor']
        assert anchor in text, c['case_id']
        selected.append({'case_id': c['case_id'], 'qid': c['qid'],
                         'primary_type': c['primary_type'], 'docid': docid,
                         'document_sha256': source_sha, 'anchor': anchor,
                         'anchor_offset': t['evidence_location']['anchor_offset'],
                         'find_query': c['queries']['find_query'],
                         'find_query_sha256': hashlib.sha256(c['queries']['find_query'].encode()).hexdigest()})
    db.close()
    write(HERE / 'find_recovery/BANK.json', selected)
    f1 = dict(common, bank_sha256=sha(HERE / 'find_recovery/BANK.json'),
              find_backend_sha256={str(p.relative_to(ROOT)): sha(p) for p in
                                   [ROOT / 'llm_chat/search_find_agent.py', ROOT / 'llm_chat/raw_windows.py',
                                    ROOT / 'llm_chat/window_locator.py', ROOT / 'llm_chat/window_units.py']},
              tokenizer='/data/model/Qwen3-Embedding-8B', search_budget_tokens=400,
              calls_per_case=1, max_retries=0,
              review_rubric={'useful': 'Returned W provides new support, contradiction, or effective exclusion for current Gap',
                             'fully_sufficient': 'Returned W alone answers current Gap with adequate source context',
                             'partial': 'Some relevant fact but not enough to answer Gap',
                             'no_gain': 'No substantive progress for current Gap',
                             'anchor_hit': 'Exact frozen anchor substring appears in returned W; auxiliary only'})
    write(HERE / 'find_recovery/freeze.json', f1)


if __name__ == '__main__':
    main()
