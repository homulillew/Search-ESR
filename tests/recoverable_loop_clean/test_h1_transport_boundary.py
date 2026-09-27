"""Exercise the real H1 HTTP adapter with a mocked provider; no paid calls."""
import json
from pathlib import Path
import httpx
import pytest
from conftest import bridge, state, acquire, EMPTY_READER, SUPPORTED, CONTINUE
from experiments.recoverable_loop_clean.h1_contract_continuation.transport import Transport, TrajectoryPort
from llm_chat.recoverable_loop.engine import RecoverableLoop
from llm_chat.recoverable_loop.replay import replay_log


@pytest.mark.parametrize('h_content', ['not JSON', '{"updates":[{"operation":"ADD","statement":"Candidate","basis_refs":["C1"]}],"useful_source_refs":[]}'])
def test_http_invalid_h_archived_as_contract_failure_and_next_actor(h_content, tmp_path):
    config = json.loads((Path(__file__).resolve().parents[2]/'experiments/recoverable_loop_clean/h1_contract_continuation/CONFIG.json').read_text())
    outputs = [acquire(), {'findings': [{'statement': 'Alice was born in 1900.', 'evidence_refs': ['W1']}]},
               SUPPORTED, h_content, {'decision': 'request_closure'}, CONTINUE]
    async def handler(req):
        output = outputs.pop(0)
        content = output if isinstance(output, str) else json.dumps(output)
        return httpx.Response(200, json={'id': 'mock', 'model': 'deepseek-flash',
            'choices': [{'finish_reason': 'stop', 'message': {'content': content}}],
            'usage': {'prompt_tokens': 100, 'completion_tokens': 10, 'total_tokens': 110,
                      'prompt_cache_hit_tokens': 64, 'prompt_cache_miss_tokens': 36}})
    transport = Transport(config, tmp_path, lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler)), key='TEST_ONLY')
    port = TrajectoryPort(transport, tmp_path/'trajectory')
    loop = RecoverableLoop(state(), bridge(), port, tmp_path/'trace.jsonl')
    try:
        first = loop.step()
        assert 'failure' not in first and first['feedback'] == 'Gain' and first['claim_delta'] == ['C1']
        assert first['auxiliary_failures'][0]['type'] == 'contract_failure'
        assert first['auxiliary_failures'][0]['raw_output_hash']
        raw = [e.payload()['output'] for e in loop.state.T if e.kind == 'role_response' and e.payload()['role'] == 'hypotheses']
        assert raw == [h_content]
        assert loop.step()['closure']['status'] == 'CONTINUE'
        assert not outputs and transport.count == 6
    finally:
        loop.close(); transport.close()
    assert replay_log(tmp_path/'trace.jsonl')[0] == loop.state
    for p in tmp_path.rglob('*'):
        if p.is_file(): assert 'TEST_ONLY' not in p.read_text()
