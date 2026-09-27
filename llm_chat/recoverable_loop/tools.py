"""Real executor bridge and immutable evidence normalization. No retriever changes."""
from dataclasses import dataclass, asdict
from copy import deepcopy
import hashlib
from .contracts import validate_action


@dataclass(frozen=True)
class EvidenceWindow:
    window_ref: str
    doc_ref: str
    source_window_ref: str
    docid: str
    document_sha256: str
    text: str
    text_sha256: str
    title: str
    url: str
    offset: int
    end_char: int


class EvidenceStore:
    def __init__(self): self._windows = {}

    def add(self, windows):
        additions = {}
        for w in windows:
            if hashlib.sha256(w.text.encode()).hexdigest() != w.text_sha256: raise ValueError('text hash mismatch')
            if w.end_char-w.offset != len(w.text) or w.offset < 0: raise ValueError('invalid span')
            if w.window_ref in self._windows and self._windows[w.window_ref] != w: raise ValueError('W alias changed')
            if w.window_ref in additions and additions[w.window_ref] != w: raise ValueError('duplicate W conflict')
            additions[w.window_ref] = w
        self._windows.update(additions)

    def get(self, ref):
        if ref not in self._windows: raise ValueError('evidence reference not observed')
        return self._windows[ref]

    def select(self, refs): return [asdict(self.get(r)) for r in dict.fromkeys(refs)]


class ToolBridge:
    def __init__(self, tools, evidence=None):
        self.tools = tools
        self.evidence = evidence if evidence is not None else EvidenceStore()

    def source_handles(self):
        docs = []; windows = []
        for d in self.tools.handles.snapshot()['documents']:
            key = (d['docid'], d['document_sha256'])
            doc = self.tools.window_builder.documents[key]
            docs.append({'doc_ref': d['doc_ref'], 'title': doc['title'], 'url': doc['url']})
        for w in self.tools.handles.snapshot()['windows']:
            e = self.evidence.get(w['window_ref'])
            windows.append({'window_ref': e.window_ref, 'doc_ref': e.doc_ref})
        return {'documents': docs, 'windows': windows}

    def execute(self, action):
        validate_action(action, self.tools.handles)
        before = self.tools.handles.snapshot()
        # This is the only dispatch: exact name and arguments, no compiler.
        result = self.tools.execute(action['tool'], deepcopy(action['arguments']))
        audit = deepcopy(self.tools.audit_record())
        windows = self._normalize(audit)
        self.evidence.add(windows)
        old = {d['doc_ref'] for d in before['documents']}
        new_docs = sorted({w.doc_ref for w in windows} - old)
        inspected = [] if action['tool'] == 'search' else sorted({w.doc_ref for w in windows})
        if action['tool'] == 'find' and not windows: inspected = [action['arguments']['doc_ref']]
        return {'result': result, 'windows': windows, 'new_document_refs': new_docs,
                'inspected_sources': inspected, 'audit': audit}

    def _normalize(self, audit):
        if audit['tool'] == 'search' and 'hits' in audit:
            raw = [h['raw_result'] for h in audit['hits'] if 'raw_result' in h]
        else:
            raw = audit['raw_result']; raw = raw if isinstance(raw, list) else [raw]
        registry = audit['handles']
        ws = {w['source_window_ref']: w['window_ref'] for w in registry['windows']}
        ds = {(d['docid'], d['document_sha256']): d['doc_ref'] for d in registry['documents']}
        out = []
        for r in raw:
            if 'text' not in r: continue  # Explicit find miss has no fabricated observation.
            key = (r['docid'], r['document_sha256'])
            doc = self.tools.window_builder.documents[key]
            pinned = self.tools.window_builder.windows[r['window_ref']]
            if (pinned.docid, pinned.digest, pinned.start, pinned.end) != (*key, r['offset'], r['end_char']):
                raise ValueError('window identity and raw span disagree')
            if hashlib.sha256(doc['text'].encode()).hexdigest() != key[1]: raise ValueError('document changed')
            if doc['text'][r['offset']:r['end_char']] != r['text']: raise ValueError('raw span changed')
            if r['title'] != doc['title'] or r['url'] != doc['url']: raise ValueError('source metadata changed')
            out.append(EvidenceWindow(ws[r['window_ref']], ds[key], r['window_ref'], key[0], key[1], r['text'],
                                      hashlib.sha256(r['text'].encode()).hexdigest(), r['title'], r['url'],
                                      r['offset'], r['end_char']))
        return tuple(out)
