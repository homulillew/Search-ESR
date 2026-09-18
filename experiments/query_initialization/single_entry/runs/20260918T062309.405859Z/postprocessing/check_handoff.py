"""Offline restart/Open probe on copied ledgers; never mutates archived sessions."""
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from transformers import AutoTokenizer
from llm_chat.observations import ObservationStore
from llm_chat.observed_agent import ObservedTools
from llm_chat.raw_windows import RawWindowBuilder


def check(run):
    run = Path(run)
    tokenizer = AutoTokenizer.from_pretrained('/data/model/Qwen3-Embedding-8B', local_files_only=True)
    rows = []
    for directory in sorted(run.glob('qid_*__minimal__r*')):
        handoff = json.loads((directory / 'handoff.json').read_text())
        if handoff['status'] != 'complete':
            continue
        original = sqlite3.connect(f'file:{directory}/observations.sqlite?mode=ro', uri=True)
        before = original.execute('select count(*) from events').fetchone()[0]
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / 'observations.sqlite'
            destination = sqlite3.connect(copied)
            original.backup(destination)
            destination.close()
            store = ObservationStore(copied)
            tools = ObservedTools(store)
            tools.window_builder = RawWindowBuilder(tokenizer)
            try:
                view = handoff['search_attempts'][0]['result'][0]
                assert view['window_ref'] not in tools.window_builder.windows
                restored = tools.execute('open', dict(window_ref=view['window_ref'], direction='around'))
                assert restored['docid'] == view['docid']
                assert restored['document_sha256'] == view['document_sha256']
                text = store.db.execute('select text from documents where docid=? and digest=?',
                                        (view['docid'], view['document_sha256'])).fetchone()[0]
                assert restored['text'] == text[restored['offset']:restored['end_char']]
                assert store.sequence == before + 1
                rows.append(dict(session=directory.name, source_ref=view['window_ref'],
                                 result_ref=restored['window_ref'], source_sha256=view['document_sha256'],
                                 status='restored_and_opened'))
            finally:
                tools.close()
                store.close()
        assert original.execute('select count(*) from events').fetchone()[0] == before
        original.close()
    result = dict(probes=rows, api_requests=0, method='Separate process, temporary ledger copies, Open around on first result; archived ledgers unchanged.')
    (run / 'handoff_verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    check(sys.argv[1])
