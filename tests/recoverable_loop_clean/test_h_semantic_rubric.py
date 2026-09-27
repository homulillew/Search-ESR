"""Scripted semantic boundary examples, explicitly NOT model accuracy tests."""
from dataclasses import replace
import json
from pathlib import Path
import pytest
from conftest import bridge, state, acquire, Script, EMPTY_READER
from llm_chat.recoverable_loop.engine import RecoverableLoop
from llm_chat.recoverable_loop.state import Hypothesis
from llm_chat.recoverable_loop.replay import replay_log

CASES = json.loads((Path(__file__).resolve().parents[2]/'experiments/recoverable_loop_clean/h_fix/SEMANTIC_COUNTEREXAMPLES.json').read_text())['cases']


@pytest.mark.parametrize('case', CASES, ids=lambda c: c['id'])
def test_scripted_semantic_rubric_does_not_promote_h_to_c(case, tmp_path):
    s = replace(state(), H=(Hypothesis('H1', case['hypothesis'], 'active', ()),))
    b = bridge(text=case['observation'] or 'unused', hits=[] if case['observation'] is None else None)
    op = case['allowed_operations'][0]
    update = {'operation': op, 'hypothesis_id': 'H1'}
    if op != 'KEEP': update['basis_refs'] = ['W1'] if case['observation'] else []
    outputs = [('actor', acquire(hids=['H1']))]
    if case['observation']: outputs.append(('reader', EMPTY_READER))
    outputs.append(('hypotheses', {'updates': [update], 'useful_source_refs': []}))
    p = Script(*outputs); loop = RecoverableLoop(s, b, p, tmp_path/'trace.jsonl')
    out = loop.step(); p.done(); loop.close()
    assert 'failure' not in out and out['auxiliary_failures'] == []
    assert loop.state.C == ()
    assert loop.state.H[0].status == ('rejected' if op == 'REJECT' else 'active')
    with pytest.raises(PermissionError): loop.finalize()
    assert replay_log(tmp_path/'trace.jsonl')[0] == loop.state
