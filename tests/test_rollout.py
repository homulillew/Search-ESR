import json
from types import SimpleNamespace
import pytest
from experiments.run_rollout import Recorder, RecordedClient


def test_request_snapshot_survives_mutation_and_api_failure(tmp_path):
    def fail(**kwargs):
        raise RuntimeError('simulated transport failure')
    raw = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=fail)))
    recorder = Recorder(tmp_path)
    client = RecordedClient(raw, recorder)
    messages = [{'role': 'user', 'content': 'question'}]
    with pytest.raises(RuntimeError):
        client.create(messages=messages)
    messages.append({'role': 'assistant', 'content': 'later'})
    saved = [json.loads(line) for line in (tmp_path / 'events.jsonl').read_text().splitlines()]
    assert len(saved[0]['request']['messages']) == 1
    assert len(recorder.events[0]['request']['messages']) == 1
    assert saved[1]['kind'] == 'api_error'
    recorder.render()
    assert 'api_error' in (tmp_path / 'trajectory.md').read_text()


def test_shared_tools_keep_sqlite_on_one_thread_and_sessions_independent(monkeypatch):
    import threading
    from concurrent.futures import ThreadPoolExecutor
    import experiments.run_batch as batch
    created = []
    class FakeTools:
        def __init__(self):
            self.owner = threading.get_ident()
            self.closed = False
            created.append(self)
        def execute(self, name, arguments):
            assert threading.get_ident() == self.owner
            assert not self.closed
            return arguments['query']
        def close(self):
            assert threading.get_ident() == self.owner
            self.closed = True
    monkeypatch.setattr(batch, 'BCPlusTools', FakeTools)
    shared = batch.SharedTools()
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(shared.execute, 'search', {'query': str(i)}) for i in range(12)]
        assert [f.result() for f in futures] == [str(i) for i in range(12)]
    shared.close()
    assert shared.execute('search', {'query': 'still alive'}) == 'still alive'
    shared.shutdown()
    assert len(created) == 1 and created[0].closed
