import json
import httpx
import pytest
from openai import OpenAI, AuthenticationError
from llm_chat.client import Config, ChatSession
from llm_chat.agent import AgentSession, BCPlusTools
from llm_chat.search_find_agent import HandleRegistry, SearchFindAgentSession
from llm_chat.raw_windows import RawWindowBuilder


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


def test_short_handle_registry_is_stable_and_typed():
    registry = HandleRegistry()
    d1, new1 = registry.document(('42', 'abc'))
    d1_again, new_again = registry.document(('42', 'abc'))
    d2, new2 = registry.document(('43', 'def'))
    w1, _ = registry.window('w_source_a')
    w1_again, _ = registry.window('w_source_a')
    w2, _ = registry.window('w_source_b')
    assert (d1, d1_again, d2) == ('D1', 'D1', 'D2')
    assert (new1, new_again, new2) == (True, False, True)
    assert (w1, w1_again, w2) == ('W1', 'W1', 'W2')
    assert registry.resolve_document('D1') == ('42', 'abc')
    assert registry.resolve_window('W2') == 'w_source_b'
    with pytest.raises(ValueError):
        registry.resolve_document('D99')
    with pytest.raises(ValueError):
        registry.resolve_window('W99')


def test_search_find_agent_exposes_find_without_changing_core_loop():
    requests = []
    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        if len(requests) == 1:
            return httpx.Response(200, json=reply(None, [{
                'id': 'search1', 'type': 'function',
                'function': {'name': 'search', 'arguments': '{"query":"target"}'}
            }]))
        if len(requests) == 2:
            return httpx.Response(200, json=reply(None, [{
                'id': 'find1', 'type': 'function',
                'function': {'name': 'find', 'arguments': '{"doc_ref":"D1","query":"father"}'}
            }]))
        return httpx.Response(200, json=reply('answer [W2]'))

    class FakeTools:
        def execute(self, name, args):
            if name == 'search':
                return {'status': 'ok', 'results': [{'doc_ref': 'D1', 'preview_ref': 'W1',
                         'preview': 'candidate'}], 'usage_hint': 'preview'}
            if name == 'find':
                return {'status': 'ok', 'doc_ref': 'D1',
                        'matches': [{'window_ref': 'W2', 'text': 'father evidence'}],
                        'usage_hint': 'localized'}
            raise AssertionError(name)
        def close(self): pass

    agent = SearchFindAgentSession(config(), client(handler), tools=FakeTools())
    try:
        assert agent.ask('question') == 'answer [W2]'
        names = {t['function']['name'] for t in requests[0]['tools']}
        assert names == {'search', 'find', 'open'}
        assert requests[2]['messages'][-1]['tool_call_id'] == 'find1'
    finally:
        agent.close()


def test_local_find_has_explicit_no_match_without_prefix_fallback():
    class CharTokenizer:
        def encode(self, text, add_special_tokens=False):
            return list(range(len(text)))
        def __call__(self, text, add_special_tokens=False, return_offsets_mapping=False):
            result = {}
            if return_offsets_mapping:
                result['offset_mapping'] = [(i, i + 1) for i in range(len(text))]
            return result

    builder = RawWindowBuilder(CharTokenizer())
    key = builder.register('doc', 'Alpha paragraph.\n\nThe father was Bob.\n', 'https://example.test')
    match, _ = builder.find(key, 'father')
    missing, meta = builder.find(key, 'nonexistentterm')
    assert match is not None and 'father was Bob' in match['text']
    assert missing is None
    assert meta['fallback'] == 'no_lexical_match'
