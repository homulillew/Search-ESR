"""Live adapter around the existing frozen Search/Open implementation.

Only this module loads BC+ / GPU assets. No language-model initialization call.
The corpus, index and tokenizer are hashed once and stat-checked around capture.
Full documents remain in the existing per-case ObservationStore, not model input.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from .artifacts import file_hash, read
from .contracts import positive

ROOT = Path(__file__).resolve().parents[3]
TOKENIZER = Path('/data/model/Qwen3-Embedding-8B')
INDEX = ROOT / 'BCPlus/indexes/bcplus-qwen3-8b'
VECTORS = ROOT / 'BCPlus/indexes/qwen3-embedding-8b'


def retrieval_files(index, vectors, tokenizer):
    """Include the actual sibling vector shards, not only the document store."""
    shards = sorted(Path(vectors).glob('*.pkl'))
    if not shards or not (Path(index) / 'documents.sqlite').is_file():
        raise ValueError('Missing corpus or retrieval vector shards')
    return sorted(set([*[p for p in Path(index).rglob('*') if p.is_file()],
        *shards, *[p for p in Path(tokenizer).rglob('*') if p.is_file()
        and '.cache' not in p.parts
        and p.suffix in {'.json', '.txt', '.model', '.safetensors', '.bin', '.pt', '.tiktoken'}]]))


def checked_prefix(metadata, actual_prefix):
    prefix = metadata.get('query_prefix')
    if not isinstance(prefix, str) or prefix != actual_prefix:
        raise ValueError('Metadata query_prefix must match actual retrieval script PREFIX')
    return prefix


class LocalSearch:
    mode = 'live'

    def __init__(self):
        from llm_chat.agent import TOOLS
        from transformers import AutoTokenizer
        from BCPlus.scripts.search_bcplus import BCPlusSearcher, PREFIX, MODEL, BASE
        metadata = read(INDEX / 'metadata.json')
        self.prefix = checked_prefix(metadata, PREFIX)
        if Path(MODEL).resolve() != TOKENIZER.resolve() or (BASE / 'indexes/qwen3-embedding-8b').resolve() != VECTORS.resolve():
            raise ValueError('Actual retrieval model/vector paths differ from frozen assets')
        self.tools = deepcopy(TOOLS)
        self.tokenizer = AutoTokenizer.from_pretrained(str(TOKENIZER), local_files_only=True, use_fast=True)
        self._files = sorted(set([*(ROOT / 'llm_chat').glob('*.py'),
            ROOT / 'BCPlus/scripts/search_bcplus.py',
            *retrieval_files(INDEX, VECTORS, TOKENIZER)]))
        if not self._files or not INDEX.is_dir():
            raise ValueError('Missing local retrieval assets')
        self._stats = {str(p): (p.stat().st_size, p.stat().st_mtime_ns) for p in self._files}
        self._passport = {'adapter': 'ObservedTools/baseline', 'index_directory': str(INDEX),
                          'vector_directory': str(VECTORS),
                          'tokenizer_directory': str(TOKENIZER), 'query_prefix': self.prefix,
                          'asset_sha256': {str(p): file_hash(p) for p in self._files}}
        self.check_unchanged()
        self.searcher = BCPlusSearcher()
        self._passport['device'] = self.searcher.device
        self.check_unchanged()

    def passport(self):
        return deepcopy(self._passport)

    def check_unchanged(self):
        for name, expected in self._stats.items():
            stat = Path(name).stat()
            if (stat.st_size, stat.st_mtime_ns) != expected:
                raise ValueError('Retrieval asset changed during capture')

    def count_query(self, query):
        ids = self.tokenizer(self.prefix + query, add_special_tokens=True,
                             truncation=False)['input_ids']
        if ids and isinstance(ids[0], list):
            raise ValueError('Unexpected batched tokenizer result')
        actual = self.searcher.tokenizer(self.prefix + query, add_special_tokens=True,
                                        truncation=False)['input_ids']
        if ids != actual:
            raise ValueError('Guard and retrieval tokenizer disagree')
        return len(ids)

    def search(self, query, k, folder):
        from llm_chat.observations import ObservationStore
        from llm_chat.observed_agent import ObservedTools
        from llm_chat.raw_windows import RawWindowBuilder
        positive(k, 10)
        self.check_unchanged()
        store = ObservationStore(Path(folder) / 'observations.sqlite')
        tools = ObservedTools(store, variant='baseline')
        tools.searcher = self.searcher
        tools.window_builder = RawWindowBuilder(self.tokenizer)
        try:
            return tools.execute('search', {'query': query, 'k': k})
        finally:
            tools.close()
            store.close()

    def close(self):
        close = getattr(self.searcher, 'close', None)
        if callable(close):
            close()
