"""Offline ports; no model SDK, corpus encoder, or network may be used."""
import re
import socket
from copy import deepcopy
import pytest
from llm_chat.search_find_agent import SearchFindTools
from llm_chat.search_find_v3b_agent import OrthogonalSearchFindTools
from llm_chat.raw_windows import RawWindowBuilder
from llm_chat.recoverable_loop.tools import ToolBridge
from llm_chat.recoverable_loop.state import State, skeleton


@pytest.fixture(autouse=True)
def deny_network(monkeypatch):
    def denied(*args, **kwargs): raise AssertionError('Network forbidden in offline validation')
    monkeypatch.setattr(socket.socket, 'connect', denied)
    monkeypatch.setattr(socket.socket, 'connect_ex', denied)
    monkeypatch.setattr(socket, 'create_connection', denied)
    from llm_chat.client import Config
    monkeypatch.setattr(Config, 'load', denied)


class Tokenizer:
    """Whitespace test tokenizer; not claimed to reproduce model token budgets."""
    def encode(self, text, **kwargs): return list(range(len(re.findall(r'\S+', text))))
    def __call__(self, text, **kwargs):
        return {'offset_mapping': [(m.start(), m.end()) for m in re.finditer(r'\S+', text)]}


class Searcher:
    def __init__(self, hits): self.hits, self.calls = hits, []
    def search(self, query, k):
        self.calls.append((query, k))
        return deepcopy(self.hits[:k])


def bridge(text='title: Alpha\nAlice was born in 1900.', orthogonal=False, hits=None):
    tools = OrthogonalSearchFindTools() if orthogonal else SearchFindTools()
    tools.window_builder = RawWindowBuilder(Tokenizer())
    tools.searcher = Searcher(hits if hits is not None else [dict(docid='a', text=text, url='local:a', score=1)])
    return ToolBridge(tools)


def state(question='What was Alice’s birth year?'):
    return State(question, skeleton(question, [{'source_spans': [{'text': question}]}]))


def action(name='search', **arguments): return {'tool': name, 'arguments': arguments or {'query': 'Alice'}}


def acquire(one_gap='Verify Alice’s birth year.', act=None, strategy='VERIFY_ATTRIBUTE', hids=()):
    return dict(decision='acquire', focus_requirement_id='R1', one_gap=one_gap, strategy=strategy,
                hypothesis_ids_under_test=list(hids), action=act or action())


class Script:
    def __init__(self, *outputs): self.outputs, self.requests = list(outputs), []
    def complete(self, request):
        self.requests.append(request)
        assert self.outputs, 'Unexpected semantic call'
        role, value = self.outputs.pop(0)
        assert role == request.role
        if isinstance(value, Exception): raise value
        return value(request) if callable(value) else deepcopy(value)
    def done(self): assert not self.outputs


EMPTY_READER = {'findings': []}
EMPTY_H = {'updates': [], 'useful_source_refs': []}
SUPPORTED = {'verdict': 'supported', 'reason': 'Scripted: explicit raw source support.'}
CONTINUE = {'status': 'CONTINUE', 'missing': [{'requirement_id': 'R1', 'summary': 'Further relation evidence is needed.'}]}
