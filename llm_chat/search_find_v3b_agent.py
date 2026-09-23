"""Orthogonal Search treatment: old documents cannot be locally re-localized by Search.

This module deliberately reuses the v3a tool schema, prompt, Find, and Open.
Only the Search execution path differs.
"""

import hashlib

from .search_find_agent import SEARCH_USAGE_HINT, SearchFindTools


ALREADY_DISCOVERED_HINT = (
    "This document is already in the workspace. Global search does not inspect "
    "another location inside an existing document. Use find(D#, query) to inspect "
    "a different location."
)


class OrthogonalSearchFindTools(SearchFindTools):
    def __init__(self):
        super().__init__()
        self.discovery_previews = {}

    def execute(self, name, arguments):
        if name != 'search':
            return super().execute(name, arguments)
        if not isinstance(arguments, dict):
            raise ValueError('Tool arguments must be an object')
        query = arguments.get('query')
        self._validate_query(query)
        k = arguments.get('k', 5)
        if type(k) is not int or not 1 <= k <= 10:
            raise ValueError('k must be an integer between 1 and 10')
        if self.searcher is None:
            from BCPlus.scripts.search_bcplus import BCPlusSearcher
            self.searcher = BCPlusSearcher()

        # The original retriever and exact top-k are preserved. Do not refill
        # new-document slots after removing previews from old-document hits.
        hits = self.searcher.search(query, k)
        results = []
        private_hits = []
        for rank, hit in enumerate(hits, start=1):
            docid = str(hit['docid'])
            key = (docid, hashlib.sha256(hit['text'].encode()).hexdigest())
            doc_ref, is_new_doc = self.handles.document(key)
            private = {'rank': rank, 'score': hit['score'], 'doc_ref': doc_ref,
                       'docid': docid, 'document_sha256': key[1],
                       'status': 'new_document' if is_new_doc else 'already_discovered'}
            if is_new_doc:
                # Precisely the v3a new-document localizer, with the same query
                # and 400-token preview budget.
                raw = self._windows().search(docid, hit['text'], hit['url'], query)
                if raw['document_sha256'] != key[1]:
                    raise AssertionError('retriever and preview canonical identity differ')
                window_ref, _ = self.handles.window(raw['window_ref'])
                self.discovery_previews[doc_ref] = window_ref
                results.append({
                    'doc_ref': doc_ref, 'previously_discovered': False,
                    'title': raw['title'], 'url': raw['url'],
                    'preview_ref': window_ref, 'preview': raw['text'],
                    'has_more_before': raw['has_more_before'],
                    'has_more_after': raw['has_more_after'], 'status': raw['status'],
                })
                private['raw_result'] = raw
            else:
                # This branch MUST NOT invoke _windows(), local BM25, or _emit.
                # Only metadata from the already registered document is returned.
                original = self.discovery_previews[doc_ref]
                doc = self.window_builder.documents[key]
                results.append({
                    'doc_ref': doc_ref, 'title': doc['title'], 'url': doc['url'],
                    'status': 'already_discovered',
                    'existing_preview_ref': original,
                    'usage_hint': ALREADY_DISCOVERED_HINT,
                })
            private_hits.append(private)
        model_result = {'status': 'ok' if results else 'no_results',
                        'query': query, 'results': results,
                        'usage_hint': SEARCH_USAGE_HINT}
        self._last_audit = {
            'protocol': 'search_find_v3b_orthogonal', 'tool': 'search',
            'hits': private_hits, 'handles': self.handles.snapshot(),
            'model_result': model_result,
        }
        return model_result
