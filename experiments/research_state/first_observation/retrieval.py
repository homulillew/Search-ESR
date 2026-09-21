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


class LocalSearch:
    mode = 'live'

    def __init__(self):
        from llm_chat.agent import TOOLS
        from transformers import AutoTokenizer
        from BCPlus.scripts.search_bcplus import BCPlusSearcher
        metadata = read(INDEX / 'metadata.json')
        if not isinstance(metadata.get('query_prefix'), str):
            raise ValueError('Missing frozen retrieval query_prefix')
        self.prefix = metadata['query_prefix']
        self.tools = deepcopy(TOOLS)
        self.tokenizer = AutoTokenizer.from_pretrained(str(TOKENIZER), local_files_only=True, use_fast=True)
        self.searcher = BCPlusSearcher()
        self._files = sorted(set([*(ROOT / 'llm_chat').glob('*.py'),
            ROOT / 'BCPlus/scripts/search_bcplus.py',
            *[p for p in INDEX.rglob('*') if p.is_file()],
            *[p for p in TOKENIZER.glob('*') if p.is_file() and p.suffix in {'.json', '.txt', '.model', '.safetensors', '.bin', '.pt', '.tiktoken'}]]))
        if not self._files or not INDEX.is_dir():
            raise ValueError('Missing local retrieval assets')
        self._stats = {str(p): (p.stat().st_size, p.stat().st_mtime_ns) for p in self._files}
        self._passport = {'adapter': 'ObservedTools/baseline', 'index_directory': str(INDEX),
                          'tokenizer_directory': str(TOKENIZER), 'query_prefix': self.prefix,
                          'asset_sha256': {str(p): file_hash(p) for p in self._files}}
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
