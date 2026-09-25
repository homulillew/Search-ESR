"""Run one unchanged SearchFindTools.find against each frozen oracle D."""
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parents[2]))
from experiments.global_retrieval_robustness.common import DB, read
from llm_chat.search_find_agent import SearchFindTools


def main():
    from transformers import AutoTokenizer
    from llm_chat.raw_windows import RawWindowBuilder
    freeze = read(BASE / 'freeze.json')
    cases = read(BASE / 'BANK.json')
    assert [x['case_id'] for x in cases] == freeze['case_order']
    tokenizer = AutoTokenizer.from_pretrained(freeze['tokenizer'], local_files_only=True, use_fast=True)
    db = sqlite3.connect(f'{DB.as_uri()}?mode=ro', uri=True)
    path = BASE / 'oracle_find_events.jsonl'
    assert not path.exists(), 'Events already exist; no rerun without a new frozen run'
    with path.open('w') as output:
        for c in cases:
            event = {'case_id': c['case_id'], 'qid': c['qid'], 'primary_type': c['primary_type'],
                     'docid': c['docid'], 'find_query': c['find_query']}
            try:
                row = db.execute('SELECT text,url FROM documents WHERE docid=?', (c['docid'],)).fetchone()
                if row is None:
                    raise ValueError('canonical document absent')
                text, url = row
                assert hashlib.sha256(text.encode()).hexdigest() == c['document_sha256']
                tools = SearchFindTools()
                tools.window_builder = RawWindowBuilder(tokenizer)
                key = tools.window_builder.register(c['docid'], text, url)
                doc_ref, _ = tools.handles.document(key)
                event['result'] = tools.execute('find', {'doc_ref': doc_ref, 'query': c['find_query']})
                event['audit'] = tools.audit_record()
                event['error'] = None
            except Exception as exc:
                event['result'] = None
                event['audit'] = None
                event['error'] = f'{type(exc).__name__}: {exc}'
            output.write(json.dumps(event, ensure_ascii=False) + '\n')
            output.flush()
            print(c['case_id'], event['result']['status'] if event['result'] else event['error'], flush=True)
    db.close()


if __name__ == '__main__':
    main()
