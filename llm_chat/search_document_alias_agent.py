"""Name-only local-search alias over the frozen Orthogonal Search backends."""

from copy import deepcopy

from .search_find_agent import SEARCH_FIND_PROMPT, SEARCH_FIND_TOOLS, SearchFindTools
from .search_find_v3b_agent import OrthogonalSearchFindTools


ALIAS_TOOLS = deepcopy(SEARCH_FIND_TOOLS)
for tool in ALIAS_TOOLS:
    fn = tool['function']
    if fn['name'] == 'find':
        fn['name'] = 'search_document'
    fn['description'] = fn['description'].replace('find', 'search_document')
ALIAS_PROMPT = SEARCH_FIND_PROMPT.replace('find', 'search_document')


class SearchDocumentAliasTools(OrthogonalSearchFindTools):
    def execute(self, name, arguments):
        if name == 'search_document':
            result = SearchFindTools.execute(self, 'find', arguments)
            result['usage_hint'] = result['usage_hint'].replace('find', 'search_document')
            self._last_audit = {**self._last_audit,
                                'protocol': 'search_document_alias',
                                'underlying_tool': 'find', 'model_result': result}
            return result
        if name in ('search', 'open'):
            result = super().execute(name, arguments)
            result['usage_hint'] = result['usage_hint'].replace('find', 'search_document')
            if name == 'search':
                for hit in result['results']:
                    if 'usage_hint' in hit:
                        hit['usage_hint'] = hit['usage_hint'].replace('find', 'search_document')
            self._last_audit = {**self._last_audit,
                                'protocol': 'search_document_alias',
                                'underlying_tool': name, 'model_result': result}
            return result
        raise ValueError(f'Unknown tool: {name}')
