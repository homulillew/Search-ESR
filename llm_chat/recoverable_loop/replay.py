"""Replay committed state from append-only logs, without semantic or tool calls.

This checks recorded verdict/provenance links, not the truth of model judgments.
A hash chain detects accidental edits; it is not an authenticated signature.
"""
import json
from dataclasses import asdict, replace
from .state import Claim, Hypothesis, state_from_dict, replay_events, digest
from .tools import EvidenceStore, EvidenceWindow


def replay_log(path):
    with open(path, encoding='utf-8') as stream:
        rows = [json.loads(line) for line in stream]
    if not rows or rows[0].get('kind') != 'initial_state': raise ValueError('missing initial state')
    state = state_from_dict(rows[0]['state'])
    initial_count = len(state.T)
    events = replay_events([asdict(e) for e in state.T] + rows[1:])
    evidence = EvidenceStore()
    evidence.add(EvidenceWindow(**w) for w in rows[0]['evidence'])
    for c in state.C: evidence.select(c.evidence_refs)
    for h in state.H: evidence.select(h.basis_refs)
    supported = {}
    for event in events[initial_count:]:
        p = event.payload()
        if event.kind == 'tool_observation':
            evidence.add(EvidenceWindow(**w) for w in p['windows'])
        elif event.kind == 'grounding_decision':
            if p['verdict']['verdict'] == 'supported': supported[p['payload_hash']] = p['candidate']
        elif event.kind == 'claim_committed':
            c = Claim(**{**p['claim'], 'evidence_refs': tuple(p['claim']['evidence_refs'])})
            candidate = {'statement': c.statement, 'evidence_refs': list(c.evidence_refs)}
            selected = evidence.select(c.evidence_refs)
            expected_hash = digest({'candidate': candidate, 'Evidence': selected})
            if (p['grounding_payload_hash'] != expected_hash or supported.pop(expected_hash, None) != candidate
                    or p['evidence_hash'] != digest(selected)):
                raise ValueError('claim has no matching supported evidence verdict')
            state = replace(state, C=state.C+(c,))
        elif event.kind == 'hypotheses_updated':
            if json.loads(json.dumps([asdict(h) for h in state.H])) != p['before']:
                raise ValueError('H transition does not match prior state')
            hs = tuple(Hypothesis(**{**h, 'basis_refs': tuple(h['basis_refs'])}) for h in p['after'])
            for h in hs: evidence.select(h.basis_refs)
            state = replace(state, H=hs)
        state = replace(state, T=state.T+(event,))
    return state, evidence
