"""Immutable epistemic records and deterministic Trace projections."""
from dataclasses import dataclass, asdict, replace
import hashlib
import json
import re


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


@dataclass(frozen=True)
class SourceSpan:
    text: str
    start: int
    end: int
    unit: str = ''


@dataclass(frozen=True)
class Requirement:
    requirement_id: str
    source_spans: tuple[SourceSpan, ...]

    def __post_init__(self):
        if type(self.source_spans) is not tuple or any(type(s) is not SourceSpan for s in self.source_spans):
            raise TypeError('source_spans must be immutable SourceSpan records')


@dataclass(frozen=True)
class Claim:
    claim_id: str
    statement: str
    evidence_refs: tuple[str, ...]
    version: int = 1

    def __post_init__(self):
        immutable_refs(self.evidence_refs)


@dataclass(frozen=True)
class Hypothesis:
    hypothesis_id: str
    statement: str
    status: str
    basis_refs: tuple[str, ...]

    def __post_init__(self):
        immutable_refs(self.basis_refs)


def immutable_refs(refs):
    if type(refs) is not tuple or any(type(r) is not str or not r for r in refs):
        raise TypeError('references must be an immutable tuple of strings')
    if len(set(refs)) != len(refs): raise ValueError('duplicate evidence references')


@dataclass(frozen=True)
class TraceEvent:
    seq: int
    kind: str
    payload_json: str
    previous_hash: str
    event_hash: str

    def payload(self): return json.loads(self.payload_json)


@dataclass(frozen=True)
class State:
    Q: str
    R: tuple[Requirement, ...]
    C: tuple[Claim, ...] = ()
    H: tuple[Hypothesis, ...] = ()
    T: tuple[TraceEvent, ...] = ()

    def __post_init__(self):
        for name, cls in (('R', Requirement), ('C', Claim), ('H', Hypothesis), ('T', TraceEvent)):
            value = getattr(self, name)
            if type(value) is not tuple or any(type(x) is not cls for x in value):
                raise TypeError(name + ' must contain immutable typed records')
        if not self.Q.strip() or not self.R: raise ValueError('Q and R required')
        for r in self.R:
            if not r.source_spans: raise ValueError('R must be source anchored')
            for s in r.source_spans:
                if not 0 <= s.start < s.end <= len(self.Q) or self.Q[s.start:s.end] != s.text: raise ValueError('invalid Q anchor')
        for items, attr in ((self.R, 'requirement_id'), (self.C, 'claim_id'), (self.H, 'hypothesis_id')):
            ids = [getattr(x, attr) for x in items]
            if len(ids) != len(set(ids)): raise ValueError('duplicate IDs')
        if sum(h.status == 'active' for h in self.H) > 6: raise ValueError('too many active H')
        if any(h.status not in ('active', 'deprioritized', 'rejected') for h in self.H): raise ValueError('invalid H status')
        if any(not h.statement.strip() for h in self.H): raise ValueError('empty H')
        if any(not c.statement.strip() or not c.evidence_refs or c.version < 1 for c in self.C): raise ValueError('invalid C')


def skeleton(question, rows):
    out = []
    for i, row in enumerate(rows, 1):
        spans = []
        for span in row['source_spans']:
            text = span['text']; start = span.get('start', question.find(text))
            if start < 0 or not text: raise ValueError('R anchor absent from Q')
            spans.append(SourceSpan(text, start, start+len(text), span.get('unit', '')))
        out.append(Requirement(row.get('requirement_id', f'R{i}'), tuple(spans)))
    return tuple(out)


def append_event(state, kind, payload):
    seq = len(state.T) + 1; prior = state.T[-1].event_hash if state.T else ''
    text = canonical(payload)
    h = digest({'seq': seq, 'kind': kind, 'payload_json': text, 'previous_hash': prior})
    return replace(state, T=state.T + (TraceEvent(seq, kind, text, prior, h),))


def replay_events(rows):
    events = []; prior = ''
    for seq, row in enumerate(rows, 1):
        event = TraceEvent(**row)
        core = {k: row[k] for k in ('seq', 'kind', 'payload_json', 'previous_hash')}
        if event.seq != seq or event.previous_hash != prior or digest(core) != event.event_hash:
            raise ValueError('trace integrity failure')
        json.loads(event.payload_json)
        events.append(event); prior = event.event_hash
    return tuple(events)


def fact_view(state):
    return {'Q': state.Q, 'R': [asdict(x) for x in state.R], 'C': [asdict(x) for x in state.C]}


def family(decision):
    if decision.get('decision') != 'acquire': return None
    return [decision['focus_requirement_id'], decision['strategy'], sorted(decision['hypothesis_ids_under_test'])]


def trace_view(state):
    attempts = []; pending = {}; closure = None
    for e in state.T:
        p = e.payload()
        if e.kind == 'step_outcome':
            attempts.append(p)
            for d in p.get('inspected_sources', []): pending.pop(d, None)
            for s in p.get('new_source_opportunities', []): pending[s['doc_ref']] = s
        elif e.kind == 'closure_feedback': closure = p
    recent = attempts[-3:]; count = 0
    if recent and recent[-1].get('family'):
        target = recent[-1]['family']
        for p in reversed(recent):
            if p.get('family') != target or p.get('feedback') != 'NoGain': break
            count += 1
    return {'recent_attempts': recent, 'same_family_consecutive_nogain': count,
            'pending_source_opportunities': list(pending.values()), 'latest_closure_feedback': closure}


def actor_view(state, source_handles):
    return {**fact_view(state), 'H': [asdict(h) for h in state.H],
            'TraceView': trace_view(state), 'available_source_handles': source_handles}


def next_id(items, attr, prefix):
    nums = [int(getattr(x, attr)[len(prefix):]) for x in items if re.fullmatch(prefix+r'[1-9][0-9]*', getattr(x, attr))]
    return prefix + str(max(nums, default=0)+1)


def state_from_dict(row):
    return State(row['Q'], tuple(Requirement(r['requirement_id'], tuple(SourceSpan(**s) for s in r['source_spans'])) for r in row['R']),
                 tuple(Claim(**{**c, 'evidence_refs': tuple(c['evidence_refs'])}) for c in row['C']),
                 tuple(Hypothesis(**{**h, 'basis_refs': tuple(h['basis_refs'])}) for h in row['H']),
                 replay_events(row['T']))
