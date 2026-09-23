"""Mechanism checks for Orthogonal Search, independent of the live retriever."""

import hashlib

from llm_chat.search_find_v3b_agent import OrthogonalSearchFindTools
from llm_chat.scoped_search_agent import ScopedSearchTools
from llm_chat.search_document_alias_agent import SearchDocumentAliasTools, ALIAS_TOOLS


class FakeSearcher:
    def __init__(self, hits):
        self.hits = hits
        self.calls = []

    def search(self, query, k):
        self.calls.append((query, k))
        return self.hits[:k]


class FakeBuilder:
    def __init__(self):
        self.documents = {}
        self.windows = {}
        self.calls = []

    def search(self, docid, text, url, query):
        self.calls.append((docid, query))
        key = (docid, hashlib.sha256(text.encode()).hexdigest())
        self.documents[key] = {'title': f'Title {docid}', 'url': url}
        ref = f'w_{docid}'
        self.windows[ref] = object()
        return {'docid': docid, 'document_sha256': key[1],
                'window_ref': ref, 'title': f'Title {docid}', 'url': url,
                'text': f'PREVIEW {docid}', 'has_more_before': False,
                'has_more_after': True, 'status': 'ok'}

    def find(self, key, query):
        ref = f'w_local_{key[0]}'
        self.windows[ref] = object()
        return ({'docid': key[0], 'document_sha256': key[1],
                 'window_ref': ref, 'text': 'LOCAL PASSAGE',
                 'has_more_before': False, 'has_more_after': True},
                {'locator': 'fake'})


def test_old_hit_does_not_call_localizer_or_create_window():
    old_text, new_text = 'old full text', 'new full text'
    hits = [dict(docid='1', text=old_text, url='old-url', score=.9),
            dict(docid='2', text=new_text, url='new-url', score=.8)]
    tool = OrthogonalSearchFindTools()
    builder = FakeBuilder()
    tool.window_builder = builder
    tool.searcher = FakeSearcher(hits)
    old_key = ('1', hashlib.sha256(old_text.encode()).hexdigest())
    doc_ref, _ = tool.handles.document(old_key)
    builder.documents[old_key] = {'title': 'Old title', 'url': 'old-url'}
    tool.discovery_previews[doc_ref] = 'W1'
    result = tool.execute('search', {'query': 'different query', 'k': 2})
    assert tool.searcher.calls == [('different query', 2)]
    assert builder.calls == [('2', 'different query')]
    assert len(builder.windows) == 1
    assert len(result['results']) == 2  # no refill and original rank retained
    old, new = result['results']
    assert old['status'] == 'already_discovered'
    assert old['existing_preview_ref'] == 'W1'
    assert 'preview' not in old and 'preview_ref' not in old
    assert 'score' not in old and 'rank' not in old
    assert old_text not in str(result)
    assert new['preview'] == 'PREVIEW 2'
    assert tool.audit_record()['hits'][0]['rank'] == 1
    assert tool.audit_record()['hits'][0]['score'] == .9


def test_scoped_document_dispatches_to_same_local_backend():
    tool = ScopedSearchTools()
    builder = FakeBuilder()
    tool.window_builder = builder
    tool.searcher = FakeSearcher([])
    key = ('7', hashlib.sha256('document'.encode()).hexdigest())
    ref, _ = tool.handles.document(key)
    builder.documents[key] = {'title': 'T', 'url': 'U'}
    result = tool.execute('search', {'scope': 'document', 'doc_ref': ref, 'query': 'fact'})
    assert result['matches'][0]['text'] == 'LOCAL PASSAGE'
    assert result['matches'][0]['window_ref'] == 'W1'
    assert tool.searcher.calls == []
    assert tool.audit_record()['underlying_tool'] == 'find'
    try:
        tool.execute('search', {'query': 'fact'})
    except ValueError as exc:
        assert 'scope' in str(exc)
    else:
        raise AssertionError('missing scope was accepted')


def test_search_document_alias_keeps_find_arguments_and_backend():
    names = [t['function']['name'] for t in ALIAS_TOOLS]
    assert names == ['search', 'search_document', 'open']
    tool = SearchDocumentAliasTools()
    builder = FakeBuilder()
    tool.window_builder = builder
    tool.searcher = FakeSearcher([])
    key = ('8', hashlib.sha256('document'.encode()).hexdigest())
    ref, _ = tool.handles.document(key)
    builder.documents[key] = {'title': 'T', 'url': 'U'}
    result = tool.execute('search_document', {'doc_ref': ref, 'query': 'fact'})
    assert result['matches'][0]['text'] == 'LOCAL PASSAGE'
    assert result['matches'][0]['window_ref'] == 'W1'
    assert tool.searcher.calls == []
    assert tool.audit_record()['underlying_tool'] == 'find'
