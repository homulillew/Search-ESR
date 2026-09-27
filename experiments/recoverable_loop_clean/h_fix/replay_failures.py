"""Offline counterfactual execution of frozen bytes, never a new model experiment.

Recorded observations bypass retrieval entirely. H output bytes are passed verbatim,
not mapped/repaired. Four R1 fault replays force only H scheduling, because normal
production now skips that call. The actual skip policy is replayed separately.
"""
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from llm_chat.search_find_agent import HandleRegistry
from llm_chat.recoverable_loop.engine import RecoverableLoop
from llm_chat.recoverable_loop.replay import replay_log
from llm_chat.recoverable_loop.state import state_from_dict, canonical, trace_view
from llm_chat.recoverable_loop.tools import EvidenceStore, EvidenceWindow

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT/'experiments/recoverable_loop_clean'
RUN = BASE/'micro_recovery/run001/trajectories'


def sha(data): return hashlib.sha256(data).hexdigest()


class RecordedBridge:
    """Exact archived tool results. No Searcher, corpus, GPU, tokenizer or network."""
    def __init__(self, initial, registry, observations):
        self.tools = SimpleNamespace(handles=HandleRegistry())
        self.evidence = EvidenceStore()
        self.observations = deepcopy(observations)
        self._restore_handles(registry)
        self.evidence.add(EvidenceWindow(**w) for w in initial['evidence'])

    def _restore_handles(self, snapshot):
        for d in snapshot['documents']:
            assert self.tools.handles.document((d['docid'], d['document_sha256']))[0] == d['doc_ref']
        for w in snapshot['windows']:
            assert self.tools.handles.window(w['source_window_ref'])[0] == w['window_ref']

    def source_handles(self):
        windows = list(self.evidence._windows.values())
        return {'documents': [{'doc_ref': d['doc_ref'],
                               'title': next(w.title for w in windows if w.doc_ref == d['doc_ref']),
                               'url': next(w.url for w in windows if w.doc_ref == d['doc_ref'])}
                              for d in self.tools.handles.snapshot()['documents']],
                'windows': [{'window_ref': w.window_ref, 'doc_ref': w.doc_ref} for w in windows]}

    def execute(self, action):
        p = self.observations.pop(0)
        assert action == p['action'], 'Recorded acquisition action changed'
        old_docs = {d['doc_ref'] for d in self.tools.handles.snapshot()['documents']}
        self._restore_handles(p['audit']['handles'])
        windows = tuple(EvidenceWindow(**w) for w in p['windows'])
        self.evidence.add(windows)
        inspected = [] if action['tool'] == 'search' else sorted({w.doc_ref for w in windows})
        if action['tool'] == 'find' and not windows: inspected = [action['arguments']['doc_ref']]
        return {'result': p['result'], 'windows': windows, 'audit': p['audit'],
                'new_document_refs': sorted({w.doc_ref for w in windows} - old_docs), 'inspected_sources': inspected}


class RecordedPort:
    def __init__(self, outputs): self.outputs, self.requests = outputs, []
    def complete(self, req):
        self.requests.append(req)
        role, output = self.outputs.pop(0)
        assert req.role == role, (req.role, role)
        return deepcopy(output)


def replay_case(trajectory, destination, force_r1_h=True):
    directory = RUN/trajectory
    lines = [json.loads(line) for line in (directory/'trace.jsonl').read_text().splitlines()]
    initial = lines[0]; events = [(row['kind'], json.loads(row['payload_json'])) for row in lines[1:]]
    prefix = json.loads((BASE/'micro_recovery/prefixes'/f'{trajectory.split("__")[0]}.json').read_text())
    old_outcomes = [p for kind, p in events if kind == 'step_outcome']
    outputs = [(p['role'], p['output']) for kind, p in events if kind == 'role_response']
    h_raw = [raw for role, raw in outputs if role == 'hypotheses'][-1]
    assert isinstance(h_raw, str)
    matching = [f for f in (directory/'calls').glob('*hypotheses.response.body')
                if json.loads(f.read_text())['choices'][0]['message']['content'] == h_raw]
    assert len(matching) == 1
    body_file = matching[0]
    is_r1 = trajectory.startswith('R1_')
    if is_r1 and not force_r1_h: outputs = [(r, v) for r, v in outputs if r != 'hypotheses']
    # The continuation is deliberately scripted; no model behavior is measured.
    continuation = {'status': 'CONTINUE', 'missing': [{'requirement_id': initial['state']['R'][0]['requirement_id'],
                                                     'summary': 'Offline scripted continuation; no new truth assertion.'}]}
    outputs += [('actor', {'decision': 'request_closure'}), ('closure', continuation)]
    port = RecordedPort(outputs)
    b = RecordedBridge(initial, prefix['registry'], [p for kind, p in events if kind == 'tool_observation'])
    destination.mkdir(parents=True, exist_ok=False)
    loop = RecoverableLoop(state_from_dict(initial['state']), b, port, destination/'trace.jsonl')
    if is_r1 and force_r1_h:
        loop._should_update_hypotheses = lambda *args: True  # explicit test-only fault injection
    results = []
    for old in old_outcomes:
        result = loop.step(); results.append(result)
        assert 'failure' not in result
        assert result['feedback'] == old['feedback']
    final_old = state_from_dict(json.loads((directory/'FINAL_STATE.json').read_text()))
    assert loop.state.C == final_old.C and loop.state.H == final_old.H
    last = results[-1]
    if is_r1 and not force_r1_h:
        assert last['hypothesis_outcome'] == 'skipped' and not last['auxiliary_failures']
    else:
        assert last['auxiliary_failures'][0]['error_type'] == 'invalid_basis_ref_namespace'
        assert last['auxiliary_failures'][0]['raw_output_hash'] == sha(h_raw.encode())
        archived_raw = [e.payload()['output'] for e in loop.state.T if e.kind == 'role_response' and e.payload()['role'] == 'hypotheses'][-1]
        assert archived_raw.encode() == h_raw.encode()
    if trajectory.startswith('R1_Q546'):
        assert any(p['doc_ref'] == 'D17' for p in trace_view(loop.state)['pending_source_opportunities'])
    next_result = loop.step()
    assert 'failure' not in next_result and next_result['closure']['status'] == 'CONTINUE'
    assert not port.outputs and not b.observations
    loop.close()
    assert replay_log(destination/'trace.jsonl')[0] == loop.state
    # Original log also replays unchanged under the refactored replay utility.
    assert replay_log(directory/'trace.jsonl')[0] == final_old
    report = {'trajectory': trajectory, 'mode': 'fault_injection' if force_r1_h else 'production_skip',
              'r1_h_schedule_forced': is_r1 and force_r1_h,
              'historical_response_body': str(body_file.relative_to(ROOT)), 'body_sha256': sha(body_file.read_bytes()),
              'raw_content_sha256': sha(h_raw.encode()), 'historical_steps': results,
              'historical_claims_retained': [c.claim_id for c in final_old.C[len(initial['state']['C']):]],
              'H_unchanged': loop.state.H == final_old.H, 'next_scripted_actor_reached': True,
              'new_and_historical_trace_replay_identical': True, 'paid_calls': 0,
              'interpretation': 'Execution-path diagnostic only; no model recovery or semantic accuracy claim.'}
    (destination/'RESULT.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    def denied(*args, **kwargs): raise AssertionError('Offline replay forbids network and API configuration')
    with patch('socket.socket.connect', denied), patch('socket.socket.connect_ex', denied), patch('socket.create_connection', denied), patch('llm_chat.client.Config.load', denied):
        reports = [replay_case(p.name, args.output/'fault_injection'/p.name) for p in sorted(RUN.iterdir()) if p.is_dir()]
        skips = [replay_case(p.name, args.output/'production_skip'/p.name, False) for p in sorted(RUN.glob('R1_*'))]
    assert len(reports) == 12 and len(skips) == 4
    summary = {'paid_calls': 0, 'invalid_outputs_replayed_verbatim': 12, 'next_scripted_actor_reached': 12,
               'grounded_claim_commits_retained': sum(len(r['historical_claims_retained']) for r in reports),
               'production_r1_skips': 4, 'reports': reports, 'skip_reports': skips}
    (args.output/'SUMMARY.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in summary.items() if k not in ('reports', 'skip_reports')}))


if __name__ == '__main__': main()
