"""Strict, durable artifact IO. No credentials, model calls, or source retrieval."""
from __future__ import annotations
import json
import os
from pathlib import Path
import tempfile
from ..need_review.checkpoint import canonical_json, digest


def loads(text: str) -> object:
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ValueError('Duplicate JSON key')
            out[key] = value
        return out
    def constant(_):
        raise ValueError('Nonfinite JSON constant')
    value = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    canonical_json(value)  # Reject overflow such as 1e999 as well.
    return value


def read(path: Path) -> object:
    return loads(Path(path).read_text(encoding='utf-8'))


def write(path: Path, value: object) -> None:
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent,
                                         prefix=path.name + '.', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
        if hasattr(os, 'O_DIRECTORY'):
            fd = os.open(path.parent, os.O_DIRECTORY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def safe_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or '..' in Path(relative).parts:
        raise ValueError('Expected a contained relative path')
    path = (Path(root) / relative).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError('Path escapes its artifact root')
    return path


def sealed(value: dict, key: str) -> dict:
    out = dict(value)
    out.pop(key, None)
    out[key] = digest(out)
    return out


def verify_seal(value: dict, key: str) -> None:
    if not isinstance(value, dict) or value != sealed(value, key):
        raise ValueError(f'{key} mismatch')


def read_journal(path: Path) -> tuple[list[dict], list[str]]:
    try:
        lines = Path(path).read_bytes().splitlines()
    except FileNotFoundError:
        return [], []
    events, errors = [], []
    for number, line in enumerate(lines, 1):
        try:
            row = loads(line.decode('utf-8'))
            if not isinstance(row, dict) or type(row.get('seq')) is not int or row['seq'] != len(events) + 1:
                raise ValueError('Invalid sequence')
            if row.get('kind') not in {'request', 'response', 'api_error', 'harness_error'}:
                raise ValueError('Invalid event kind')
        except (ValueError, UnicodeError):
            errors.append(f'journal_corruption_at_line_{number}')
            break  # Never skip damage and manufacture a contiguous history.
        events.append(row)
    return events, errors
