"""Experimental table-entry repair, with frozen locator and unchanged Open."""
from llm_chat.raw_windows import RawWindowBuilder


class TableEntryWindowBuilder(RawWindowBuilder):
    def __init__(self, tokenizer):
        super().__init__(tokenizer)
        self._search_active = False
        self.last_repair = None

    def search(self, docid, text, url, query):
        self._search_active = True
        self.last_repair = None
        try:
            return super().search(docid, text, url, query)
        finally:
            self._search_active = False

    def _expand(self, key, start, end, budget, before=True, after=True):
        a, z = super()._expand(key, start, end, budget, before, after)
        if self._search_active:
            return self._repair_table_entry(key, a, z, (start, end), budget)
        return a, z

    def _repair_table_entry(self, key, start, end, protected, budget):
        """Complete a visible table entrance; trim only context before the anchor."""
        doc = self.documents[key]
        text = doc['text']
        for header, body, table_end in doc['tables']:
            if not (start <= header < end and body < table_end):
                continue
            newline = text.find('\n', body, table_end)
            first_row_end = newline + 1 if newline >= 0 else table_end
            if end >= first_row_end:
                continue
            # Only a header/separator/partial first row is visible. Preserve the
            # exact repaired locator anchor; never select rows by query/answer.
            candidates = sorted({start, *(x for x in doc['unit_starts']
                                           if start < x <= min(protected[0], header))})
            for a in candidates:
                if a <= protected[0] and first_row_end >= protected[1] and self.count(text[a:first_row_end]) <= budget:
                    self.last_repair = {'status': 'repaired', 'old_span': [start,end],
                        'new_span': [a,first_row_end], 'protected_anchor': list(protected),
                        'table_header': header, 'first_row_end': first_row_end}
                    return a, first_row_end
            self.last_repair = {'status': 'unchanged_budget_or_anchor',
                'old_span': [start,end], 'protected_anchor': list(protected),
                'table_header': header, 'first_row_end': first_row_end}
            return start, end
        return start, end
