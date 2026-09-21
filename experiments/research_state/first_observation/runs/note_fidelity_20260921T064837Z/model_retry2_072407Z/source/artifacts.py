"""Durable, exclusive artifacts and request journals for a small staged experiment."""
from __future__ import annotations

import hashlib
import importlib.metadata
import os
from pathlib import Path
import sys
import tempfile
from datetime import datetime, timezone
from .contracts import canonical, loads, seal, verify


def read(path):
    return loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    path = Path(path)
    data = canonical(value) + '\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.pending-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def exclusive(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        stream.write(canonical(value) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def runtime():
    value = {'python': sys.version}
    for name in ('openai', 'python-dotenv', 'transformers', 'torch', 'tokenizers', 'faiss-cpu', 'faiss-gpu'):
        try:
            value[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            value[name] = None
    return value


def source_files():
    root = Path(__file__).parent
    return sorted([*root.glob('*.py'), *root.glob('prompts/*.txt')])


def sources():
    root = Path(__file__).parent
    return {str(p.relative_to(root)): file_hash(p) for p in source_files()}


def fingerprint():
    return {'source_sha256': sources(), 'runtime': runtime()}


class Journal:
    def __init__(self, path):
        self.path, self.sequence = Path(path), 0
        if self.path.exists():
            raise ValueError('No implicit journal resume')

    def emit(self, kind, **fields):
        self.sequence += 1
        row = {'seq': self.sequence, 'time': datetime.now(timezone.utc).isoformat(),
               'kind': kind, **fields}
        with self.path.open('a', encoding='utf-8') as stream:
            stream.write(canonical(row) + '\n')
            stream.flush()
            os.fsync(stream.fileno())


def journal_prefix(path):
    rows, errors = [], []
    try:
        stream = Path(path).open(encoding='utf-8')
    except FileNotFoundError:
        return rows, errors
    with stream:
        for line in stream:
            try:
                row = loads(line)
                if not isinstance(row, dict) or type(row.get('seq')) is not int or row['seq'] != len(rows) + 1:
                    raise ValueError('Noncontiguous journal')
            except (ValueError, UnicodeError):
                errors.append('corrupt_journal_suffix')
                break
            rows.append(row)
    return rows, errors
