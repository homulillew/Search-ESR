"""Exact archived online checkpoints and complete recorded-episode projections.

No new model call, semantic state cleaning, trajectory splice or oracle post-state.
"""
import copy
import hashlib
import json
from pathlib import Path

TOP = Path(__file__).resolve().parents[1]
ROOT = TOP.parents[1]
OLD = ROOT / 'experiments/goal_residual_control'


def rd(path):
    return json.loads(path.read_text())


def wr(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def dg(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def bootstrap(state):
    return [{'event': 'initial_available_source', 'observation': {k: w[k] for k in ['title', 'url', 'text']}}
            for w in state['available_workspace']['observed_windows']]


def event(decision):
    o = decision['actor']['output']
    assert o is not None
    return {'event': 'research_decision', 'round': decision['round'], 'decision': o['decision'],
            'need': o['gap'], 'actions': [{'action': a['action'], 'result': a['result'],
                                         'error': a['error']} for a in decision['actions']]}


def minimal(history, rnd):
    attempts = []
    for e in history:
        for a in e.get('actions', []):
            attempts.append({'tool': a['action']['tool'], 'query': a['action'].get('query'),
                             'status': (a['result'] or {}).get('status', 'tool_error')})
    # Frontier probe does not inherit exhausted historical rollout budgets.
    # One next-frontier slot is identical in all views, not a forced goal stop.
    return {'round': rnd, 'remaining_frontier_decisions': 1, 'recent_tool_attempts': attempts[-2:]}


def record(cid, qid, state, history, pointer, rnd, origin, prior_gap=None):
    return {'checkpoint_id': cid, 'qid': qid, 'question': state['question'],
            'state': copy.deepcopy(state), 'history': copy.deepcopy(history),
            'mechanical_context': minimal(history, rnd), 'previous_gap': prior_gap,
            'provenance': pointer, 'state_origin': origin,
            'history_boundary': 'Complete archived replay episode from initial source exposures; ancestral pre-seed research is not recoverable as a complete chronological trajectory. No synthetic ancestral events.',
            'state_sha256': dg(state), 'history_sha256': dg(history),
            'history_chars': len(json.dumps(history, ensure_ascii=False)),
            'claim_count': len(state['verified_claims'])}


def main():
    g5path = OLD / 'three_round_loop_v2/results.json'
    g4path = OLD / 'transition_replan_v2/state_updates.json'
    g5 = rd(g5path); g4 = rd(g4path)
    snaps = {s['case_id']: s for s in rd(OLD / 'bank/SNAPSHOTS.json')}
    inventory = []
    for key, c in g5.items():
        seed = c['decisions'][0]['pre_state'] if c['decisions'] else snaps[c['seed_snapshot']]
        history = bootstrap(seed)
        inventory.append(record(f'G5_{key}_START', c['qid'], seed, history,
            {'path': str(g5path.relative_to(ROOT)), 'cell': key, 'pointer': 'decisions/0/pre_state' if c['decisions'] else 'seed_snapshot'},
            0, 'Actual online G5 episode; initial state inherited reviewer-normalized historical seed', c['persistent_gap'] if not c['decisions'] else seed['historical_active_gap']))
        for d in c['decisions']:
            if not d['actor']['output']:
                continue
            history.append(event(d))
            if d['actor']['output']['decision'] == 'stop':
                continue
            updates = [u for u in c['updates'] if u['round'] == d['round']]
            if any(u['proposal']['output'] is None for u in updates):
                continue
            following = next((x for x in c['decisions'] if x['round'] > d['round']), None)
            state = following['pre_state'] if following else c['state']
            pointer = f"decisions/{c['decisions'].index(following)}/pre_state" if following else 'state'
            inventory.append(record(f"G5_{key}_AFTER{d['round']}", c['qid'], state, history,
                {'path': str(g5path.relative_to(ROOT)), 'cell': key, 'pointer': pointer, 'through_round': d['round']},
                d['round'] + 1, 'Exact actual online G5 state; legacy Writer, no cleaning', d['actor']['output']['gap']))
    for tid in sorted({u['transition_id'] for u in g4}):
        updates = [u for u in g4 if u['transition_id'] == tid]
        seed = copy.deepcopy(updates[0]['pre_state'])
        # The historical implementation prepopulated POST Workspace before U1.
        # Chronology must begin with the archived PRE workspace, not future observation.
        pre_workspace = snaps[tid + '_PRE']['available_workspace']
        hstate = {**seed, 'available_workspace': pre_workspace}
        history = bootstrap(hstate)
        for i, u in enumerate(updates):
            history.append({'event': 'observed_source', 'observation': {k: u['observation'][k] for k in ['title', 'url', 'text']}})
            if u['proposal']['output'] is None:
                continue
            inventory.append(record(f'G4_{tid}_POST{i}', u['qid'], u['post_state'], history,
                {'path': str(g4path.relative_to(ROOT)), 'index': g4.index(u), 'pointer': 'post_state'},
                1, 'Actual G4 Writer mutation from inherited reviewer-normalized PRE; no oracle POST Claims', seed['historical_active_gap']))
    assert len({r['checkpoint_id'] for r in inventory}) == len(inventory)
    wr(TOP / 'bank/CHECKPOINT_INVENTORY.json', inventory)
    # Selection uses only real prefix existence, provenance and broad strata.
    chosen = []
    for qid in sorted({r['qid'] for r in inventory}, key=int):
        candidates = [r for r in inventory if r['checkpoint_id'].startswith(f'G5_{qid}:L0_')]
        later = candidates[1:]
        if not later:
            for arm in ['L1', 'L2']:
                later = [r for r in inventory if r['checkpoint_id'].startswith(f'G5_{qid}:{arm}_AFTER')]
                if later:
                    break
        assert later, qid
        chosen.extend(copy.deepcopy([candidates[0], later[-1]]))
    for tid in ['T07', 'T08', 'T13', 'T11']:
        chosen.append([r for r in inventory if r['checkpoint_id'].startswith(f'G4_{tid}_')][-1])
    assert len(chosen) == len({r['checkpoint_id'] for r in chosen}) == 24
    assert len({r['qid'] for r in chosen}) == 10
    for i, r in enumerate(chosen, 1):
        r['case_id'] = f'F{i:02}'
    wr(TOP / 'bank/CHECKPOINT_BANK.json', chosen)
    wr(TOP / 'bank/SELECTION.json', {
        'rule': 'For each of ten archived qids: exact L0 starting checkpoint and last completed L0 acting-round checkpoint; if L0 has no acting round use last completed acting round in L1 then L2 priority. Add actual G4 T07/T08 last post updates for contradiction, T13 for closure, T11 for near-closure. No online oracle post-state or manually cleaned Claims.',
        'selected': [r['checkpoint_id'] for r in chosen], 'sample_count': 24, 'qids': 10,
        'F4_reserve': 'Other L1/L2 episode checkpoints are not F1 inputs; if later gates pass, held-out case selection occurs before F4 calls. Same-question overlap must be reported.',
        'history_quartiles': 'Rank checkpoints by actual H first-replicate prompt_tokens; ties by case_id. Four equal groups of six. Provider-failed H1 uses H2 if available, otherwise frozen serialized-history character rank with explicit missing-token flag.',
        'no_model_output_used': True})
    for r in chosen:
        print(r['case_id'], r['checkpoint_id'], r['claim_count'], r['history_chars'])
    print('inventory', len(inventory))


if __name__ == '__main__':
    main()
