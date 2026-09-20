import json
import httpx
import pytest
from openai import OpenAI, AuthenticationError
from llm_chat.client import Config, ChatSession
from llm_chat.agent import AgentSession, BCPlusTools


def config():
    return Config('test-key', 'https://example.test/v1', 'test-model')


def reply(content='你好', calls=None):
    msg = {'role': 'assistant', 'content': content}
    if calls:
        msg['tool_calls'] = calls
    return {'id': 'chatcmpl-test', 'object': 'chat.completion', 'created': 0, 'model': 'test-model',
            'choices': [{'index': 0, 'finish_reason': 'tool_calls' if calls else 'stop', 'message': msg}]}


def client(handler):
    return OpenAI(api_key='test-key', base_url='https://example.test/v1', max_retries=0,
                  http_client=httpx.Client(transport=httpx.MockTransport(handler)))


def test_plain_multiturn_and_reset():
    requests = []
    def handler(request):
        assert request.url.path == '/v1/chat/completions'
        assert request.headers['authorization'] == 'Bearer test-key'
        requests.append(json.loads(request.content))
        return httpx.Response(200, json=reply())
    chat = ChatSession(config(), client(handler))
    assert chat.ask('你好', stream=False) == '你好'
    chat.ask('继续', stream=False)
    assert [m['role'] for m in requests[1]['messages']] == ['system', 'user', 'assistant', 'user']
    chat.reset()
    assert len(chat.messages) == 1
    chat.close()


def test_stream_and_failure_rollback():
    chunks = [{'id': 'x', 'object': 'chat.completion.chunk', 'created': 0, 'model': 'test-model',
               'choices': [{'index': 0, 'delta': {'content': t}, 'finish_reason': finish}]}
              for t, finish in [('你', None), ('好', None), ('', 'stop')]]
    body = ''.join('data: ' + json.dumps(c) + '\n\n' for c in chunks) + 'data: [DONE]\n\n'
    calls = []
    def handler(request):
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(200, text=body, headers={'content-type': 'text/event-stream'})
        return httpx.Response(401, json={'error': {'message': 'Invalid key', 'type': 'authentication_error'}})
    chat = ChatSession(config(), client(handler))
    output = []
    assert chat.ask('hi', on_text=output.append) == '你好'
    before = list(chat.messages)
    with pytest.raises(AuthenticationError):
        chat.ask('again')
    assert chat.messages == before
    assert output == ['你', '好']
    chat.close()


def test_agent_search_read_answer_and_followup():
    requests = []
    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        n = len(requests)
        if n <= 2:
            name, args = ('search', {'query': 'penicillin'}) if n == 1 else ('open', {'window_ref': 'w_test', 'direction': 'around'})
            return httpx.Response(200, json=reply(None, [{'id': f'call{n}', 'type': 'function',
                'function': {'name': name, 'arguments': json.dumps(args)}}]))
        return httpx.Response(200, json=reply('Fleming [42]'))
    class FakeTools:
        def execute(self, name, args):
            return {'docid': '42', 'text': 'Fleming discovered penicillin.'}
        def close(self):
            pass
    chat = AgentSession(config(), client(handler), FakeTools())
    assert chat.ask('谁发现了青霉素？') == 'Fleming [42]'
    assert [m['role'] for m in chat.messages] == ['system', 'user', 'assistant', 'tool', 'assistant', 'tool', 'assistant']
    assert requests[2]['messages'][-1]['tool_call_id'] == 'call2'
    chat.ask('继续解释')
    assert requests[3]['messages'][-2]['content'] == 'Fleming [42]'
    chat.close()


def test_agent_bad_tool_args_and_limit():
    requests = []
    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        if len(requests) == 1:
            return httpx.Response(200, json=reply(None, [{'id': 'bad', 'type': 'function',
                'function': {'name': 'search', 'arguments': '{bad json'}}]))
        assert body['tool_choice'] == 'none'
        assert 'error' in json.loads(body['messages'][-1]['content'])
        return httpx.Response(200, json=reply('无法确认。'))
    chat = AgentSession(config(), client(handler), max_rounds=1)
    assert chat.ask('问题') == '无法确认。'
    chat.close()


def test_config_file_and_override(tmp_path, monkeypatch):
    for key in ['DASHSCOPE_API_KEY', 'DASHSCOPE_ENABLE_THINKING', 'OPENAI_API_KEY', 'OPENAI_MODEL', 'OPENAI_BASE_URL', 'OPENAI_TIMEOUT', 'CHAT_SYSTEM_PROMPT']:
        monkeypatch.delenv(key, raising=False)
    env = tmp_path / '.env'
    env.write_text('OPENAI_API_KEY=secret\nOPENAI_MODEL=demo\nOPENAI_BASE_URL=https://example.test/v1\n')
    cfg = Config.load(env)
    assert cfg.model == 'demo' and 'secret' not in repr(cfg)
    monkeypatch.setenv('OPENAI_MODEL', 'override')
    assert Config.load(env).model == 'override'
    with pytest.raises(ValueError):
        Config.load(env, base_url='https://example.test/v1/chat/completions')


def test_real_document_paging_without_gpu():
    tools = BCPlusTools()
    doc = tools.execute('get_document', {'docid': '98474', 'max_chars': 100})
    assert len(doc['text']) == 100 and doc['truncated'] and doc['next_offset'] == 100
    next_page = tools.execute('get_document', {'docid': '98474', 'offset': 100, 'max_chars': 100})
    assert next_page['offset'] == 100 and len(next_page['text']) == 100
    assert tools.searcher is None
    with pytest.raises(ValueError):
        tools.execute('search', {'query': 'x', 'k': 1000})
    tools.close()


def test_dashscope_key_and_thinking_option(tmp_path, monkeypatch):
    for key in ['OPENAI_API_KEY', 'DASHSCOPE_API_KEY', 'OPENAI_MODEL', 'OPENAI_BASE_URL', 'OPENAI_TIMEOUT', 'DASHSCOPE_ENABLE_THINKING']:
        monkeypatch.delenv(key, raising=False)
    env = tmp_path / '.env'
    env.write_text('DASHSCOPE_API_KEY=dashscope-test\nOPENAI_API_KEY=\nOPENAI_MODEL=qwen3.7-flash\nOPENAI_BASE_URL=https://example.test/v1\nDASHSCOPE_ENABLE_THINKING=false\n')
    cfg = Config.load(env)
    assert cfg.api_key == 'dashscope-test'
    assert cfg.request_options() == {'extra_body': {'enable_thinking': False}}
    monkeypatch.setenv('DASHSCOPE_API_KEY', 'env-test')
    assert Config.load(env).api_key == 'env-test'
    requests = []
    def handler(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json=reply('ok'))
    chat = ChatSession(cfg, client(handler))
    assert chat.ask('hi', stream=False) == 'ok'
    assert requests[-1]['enable_thinking'] is False
    chat.close()
    agent = AgentSession(cfg, client(handler))
    assert agent.ask('hi') == 'ok'
    assert requests[-1]['enable_thinking'] is False
    agent.close()


@pytest.mark.parametrize('enabled,finish,accepted', [
    (False, 'stop', False), (True, 'stop', True),
    (True, 'length', False), (False, 'tool_calls', True),
])
def test_stop_tool_calls_require_explicit_compatibility(enabled, finish, accepted):
    calls = [{'id': 'c1', 'type': 'function',
              'function': {'name': 'search', 'arguments': '{"query":"test"}'}}]
    raw = reply(None, calls)
    raw['choices'][0]['finish_reason'] = finish
    requests, executed, statuses = [], [], []
    def handler(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json=raw if len(requests) == 1 else reply('done'))
    class Tools:
        def execute(self, name, args):
            executed.append((name, args))
            return {'text': 'observed'}
        def close(self): pass
    cfg = config()
    cfg.allow_tool_calls_with_stop = enabled
    agent = AgentSession(cfg, client(handler), Tools(), on_status=statuses.append)
    try:
        if accepted:
            assert agent.ask('test') == 'done'
            assert executed == [('search', {'query': 'test'})]
            assert requests[1]['messages'][-1]['tool_call_id'] == 'c1'
            assert any('finish_reason=stop' in s for s in statuses) == (finish == 'stop')
        else:
            with pytest.raises(ValueError): agent.ask('test')
            assert not executed and len(agent.messages) == 1
        assert raw['choices'][0]['finish_reason'] == finish
    finally:
        agent.close()


@pytest.mark.parametrize('bad_args,bad_id,bad_name', [
    ('{', 'c2', 'search'), ('[]', 'c2', 'search'),
    ('{}', 'c1', 'search'), ('{}', '', 'search'), ('{}', 'c2', 'unknown'),
])
def test_stop_tool_batch_rejected_before_any_execution(bad_args, bad_id, bad_name):
    raw = reply(None, [
        {'id': 'c1', 'type': 'function', 'function': {'name': 'search', 'arguments': '{"query":"ok"}'}},
        {'id': bad_id, 'type': 'function', 'function': {'name': bad_name, 'arguments': bad_args}},
    ])
    raw['choices'][0]['finish_reason'] = 'stop'
    class Tools:
        def execute(self, *args): pytest.fail('Invalid batch must not execute even its first call')
        def close(self): pass
    cfg = config()
    cfg.allow_tool_calls_with_stop = True
    agent = AgentSession(cfg, client(lambda r: httpx.Response(200, json=raw)), Tools())
    try:
        with pytest.raises(ValueError): agent.ask('test')
        assert len(agent.messages) == 1
    finally:
        agent.close()


def test_stop_tool_config_and_responses_url(tmp_path, monkeypatch):
    monkeypatch.delenv('OPENAI_ALLOW_TOOL_CALLS_WITH_STOP', raising=False)
    env = tmp_path / '.env'
    env.write_text('OPENAI_API_KEY=test\nOPENAI_BASE_URL=https://example.test/v1\nOPENAI_MODEL=test\nOPENAI_ALLOW_TOOL_CALLS_WITH_STOP=true\n')
    assert Config.load(env).allow_tool_calls_with_stop
    with pytest.raises(ValueError, match='基础地址'):
        Config.load(env, base_url='https://example.test/v1/responses')
    monkeypatch.setenv('OPENAI_ALLOW_TOOL_CALLS_WITH_STOP', 'false')
    assert not Config.load(env).allow_tool_calls_with_stop
    monkeypatch.setenv('OPENAI_ALLOW_TOOL_CALLS_WITH_STOP', 'invalid')
    with pytest.raises(ValueError, match='OPENAI_ALLOW_TOOL_CALLS_WITH_STOP'):
        Config.load(env)
