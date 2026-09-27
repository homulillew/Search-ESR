"""Mechanical integrity boundary; no semantic judgment or output repair."""
from dataclasses import asdict
import re
from .replay import replay_state
from .tools import EvidenceStore


class IntegrityError(RuntimeError):
    """Authoritative state/provenance failure; never an auxiliary H failure."""


def observed_evidence(bridge):
    registry = bridge.tools.handles
    snapshot = registry.snapshot()
    docs = {d['doc_ref']: (d['docid'], d['document_sha256']) for d in snapshot['documents']}
    windows = {w['window_ref']: w['source_window_ref'] for w in snapshot['windows']}
    if (len(docs) != len(snapshot['documents']) or len(windows) != len(snapshot['windows'])
            or any(not re.fullmatch(r'D[1-9][0-9]*', r) for r in docs)
            or any(not re.fullmatch(r'W[1-9][0-9]*', r) for r in windows)):
        raise ValueError('invalid registry identities')
    # Check both directions, including dangling reverse entries.
    if (docs != registry._doc_ref_to_key or windows != registry._window_ref_to_source
            or {v: k for k, v in docs.items()} != registry._doc_key_to_ref
            or {v: k for k, v in windows.items()} != registry._window_source_to_ref):
        raise ValueError('inconsistent D/W registry')
    if set(windows) != set(bridge.evidence._windows):
        raise ValueError('registry and observed evidence disagree')
    selected = bridge.evidence.select(windows)
    verified = EvidenceStore()
    for row in selected:
        w = bridge.evidence.get(row['window_ref'])
        if docs.get(w.doc_ref) != (w.docid, w.document_sha256) or windows[w.window_ref] != w.source_window_ref:
            raise ValueError('evidence identity and registry disagree')
        verified.add((w,))  # Validate raw text hash, span and immutable identity.
    return selected


def validate_integrity(initial_state, initial_evidence, state, bridge):
    try:
        current_evidence = observed_evidence(bridge)
        if state.T[:len(initial_state.T)] != initial_state.T:
            raise ValueError('initial Trace changed')
        replayed, archived = replay_state(initial_state, initial_evidence,
                                         [asdict(e) for e in state.T[len(initial_state.T):]])
        if replayed != state:
            raise ValueError('state differs from replayable commits')
        if archived.select([w['window_ref'] for w in current_evidence]) != current_evidence:
            raise ValueError('observed evidence differs from archive')
        if set(archived._windows) != set(bridge.evidence._windows):
            raise ValueError('archived evidence missing from registry')
    except (ValueError, KeyError, TypeError) as exc:
        raise IntegrityError(str(exc)) from exc
