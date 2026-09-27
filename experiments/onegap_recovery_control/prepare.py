"""Build a historical, source-bound bank. No model or retrieval access."""
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = Path(__file__).resolve().parent
HIST = ROOT / 'experiments/belief_need_budget_locality_repair'
SOURCES = {}


def digest(x):
    return hashlib.sha256(json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(path):
    p = ROOT / path
    SOURCES[str(p.relative_to(ROOT))] = sha(p)
    return json.loads(p.read_text())


def write(path, obj):
    p = P / path
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as f:
        f.write(obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


# Fixed by historical case coverage, before any new response. Two checkpoints
# are separate states, not independent questions and not sampling replicates.
SPECS = [
    ('S01', '261', 'F07', 'S01', 'R2', 'LOCATE_SOURCE'),
    ('S02', '228', 'F08', 'S01', 'R1', 'IDENTIFY_CANDIDATE'),
    ('S03', '228', 'F08', 'S03', 'R1', 'IDENTIFY_CANDIDATE'),
    ('S04', '971', 'F10', 'S01', 'R4', 'IDENTIFY_CANDIDATE'),
    ('S05', '971', 'F10', 'S02', 'R5', 'LOCATE_SOURCE'),
    ('S06', '538', 'F11', 'S01', 'R4', 'VERIFY_RELATION'),
    ('S07', '637', 'F13', 'S01', 'R3', 'LOCATE_SOURCE'),
    ('S08', '637', 'F13', 'S06', 'R4', 'LOCATE_SOURCE'),
    ('S09', '843', 'F14', 'S01', 'R2', 'LOCATE_SOURCE'),
    ('S10', '843', 'F14', 'S06', 'R5', 'LOCALIZE_IN_SOURCE'),
    ('S11', '1259', 'F15', 'S01', 'R2', 'IDENTIFY_CANDIDATE'),
    ('S12', '1259', 'F15', 'S02', 'R6', 'LOCATE_SOURCE'),
    ('S13', '922', 'F16', 'S01', 'R1', 'LOCATE_SOURCE'),
    ('S14', '922', 'F16', 'S02', 'R3', 'LOCALIZE_IN_SOURCE'),
]
RUNS = {'546': ('20260922T121742.932067Z', 33), '1094': ('20260922T113202.256169Z', 69)}


def action(a):
    kind = a.get('tool', a.get('type', '')).upper()
    return {'type': kind, 'query': a.get('query') if kind == 'SEARCH' else None,
            'source_ref': a.get('doc_ref', a.get('window_ref')),
            'pattern': a.get('query') if kind == 'FIND' else a.get('direction') if kind == 'OPEN' else None}


def source_view(o):
    return {'source_ref': o['doc_ref'], 'window_ref': o['window_ref'],
            'title': o.get('title', ''), 'url': o.get('url', '')}


def historical_state(spec, sk, reviews):
    sid, qid, trajectory, snap, rid, strategy = spec
    folder = HIST / 'acquisition/trajectories' / trajectory
    snapshot_path = folder / (snap + '.json')
    snapshot = read(snapshot_path)
    s = snapshot['state']
    cutoff, wave = map(int, snapshot['transition'].split('_')[1:])
    claims, provenance, unavailable = [], [], []
    for i, c in enumerate(s['claims'], 1):
        matches = [r for r in reviews if r['qid'] == qid and r['statement'] == c['statement']]
        if len(matches) != 1 or matches[0]['review']['status'] != 'supported':
            unavailable.append({'claim_index': i, 'reason': 'No unique prior supported review; no repair.'})
            continue
        tool = read(c['source_observation_path'])
        observation = tool['observations'][c['source_observation_index']]
        assert sha_text(observation['text']) in c['source_text_hashes']
        assert observation['window_ref'] in c['support_refs']
        assert matches[0]['observation_hash'] == sha_text(observation['text'])
        claims.append({'claim_id': f'C{i}', 'statement': c['statement'], 'evidence_refs': c['support_refs']})
        provenance.append({'claim_id': f'C{i}', 'snapshot_claim_index': i - 1,
                           'source_observation_path': c['source_observation_path'],
                           'source_observation_index': c['source_observation_index'],
                           'observation_sha256': sha_text(observation['text']),
                           'prior_review': matches[0]})
    hs = [{'hypothesis_id': 'H1', 'statement': s['hypothesis']}] if s['hypothesis'] else []
    recent, sources = [], {}
    for turn in range(1, cutoff + 1):
        tp = folder / f'decision{turn}_tool.json'
        t = read(tp)
        for o in t['observations']:
            sources[o['doc_ref']] = source_view(o)
        # Gain is the historical C delta observed up to this snapshot, not an
        # inferred statement about all unprocessed search results.
        delta = sum(1 for c in s['claims'] if c['source_observation_path'] == str(tp.relative_to(ROOT)))
        recent.append({'action': action(t['action']), 'feedback': 'Gain' if delta else 'NoGain',
                       'feedback_basis': 'accepted Claim additions visible at checkpoint',
                       'claim_additions': delta, 'origin': 'HISTORICAL_ACTION',
                       'source_record': str(tp.relative_to(ROOT))})
    state = {'qid': qid, 'Q': s['question'], 'R': sk[qid]['requirements'], 'C': claims, 'H': hs,
             'TraceView': {'recent_actions': recent[-3:], 'visited_sources': list(sources.values()),
                           'pending_source_opportunities': []}}
    return state, {'state_id': sid, 'snapshot': str(snapshot_path.relative_to(ROOT)),
                   'snapshot_sha256': sha(snapshot_path), 'transition': snapshot['transition'],
                   'claims': provenance, 'unavailable_claims': unavailable,
                   'R_source': sk[qid]['source'], 'R_policy': 'historical Stage 4 D2 replicate 1, unchanged',
                   'trace_cutoff_tool_decision': cutoff, 'trace_snapshot_wave': wave}, rid, strategy


def sha_text(s):
    return hashlib.sha256(s.encode()).hexdigest()


def legacy_state(qid, old_sk, seeds):
    stamp, cutoff = RUNS[qid]
    path = ROOT / f'experiments/runs/v003a_search_find/qid_{qid}/{stamp}/events.jsonl'
    SOURCES[str(path.relative_to(ROOT))] = sha(path)
    events = []
    for line in path.open():
        e = json.loads(line)
        if e['seq'] >= cutoff:
            break
        events.append(e)
    source = next(x for x in seeds if x['qid'] == qid)
    # Only initial Claims already reviewed and admitted in the earlier F2.
    assert source['prefix_review']['seed_claims_supported']
    claims = [{k: c[k] for k in ('claim_id', 'statement', 'evidence_refs')} for c in source['initial_claims']]
    sk = next(x for x in old_sk if x['qid'] == qid)
    assert sk['Q'] == source['raw_question']
    rs = [{'requirement_id': x['requirement_id'], 'source_spans': [{'text': x['text']}]} for x in sk['R']]
    recent, views, seen_windows = [], {}, set()
    for e in events:
        if e['kind'] != 'tool_internal':
            continue
        a = e['audit']; m = a['model_result']
        assert a['tool'] == 'search', 'These chosen historical prefixes should contain Search only.'
        results = m.get('results', [])
        new_windows = set(r['preview_ref'] for r in results) - seen_windows
        # New visible window is a mechanical feedback proxy, not semantic gain.
        recent.append({'action': action({'tool': a['tool'], 'query': m.get('query')}),
                       'feedback': 'Gain' if new_windows else 'NoGain',
                       'feedback_basis': 'new observed window handles only; not useful-evidence judgment',
                       'new_window_count': len(new_windows), 'origin': 'HISTORICAL_ACTION', 'event_seq': e['seq']})
        seen_windows.update(r['preview_ref'] for r in results)
        for r in results:
            views.setdefault(r['doc_ref'], dict(source_view({**r, 'window_ref': r['preview_ref']}),
                                                 preview=r['preview'], discovered_seq=e['seq'], locally_inspected=False))
    keep = {'D10', 'D17'} if qid == '546' else {'D34'}
    promising = views['D17' if qid == '546' else 'D34']
    s = {'qid': qid, 'Q': sk['Q'], 'R': rs, 'C': claims, 'H': [],
         'TraceView': {'recent_actions': recent[-3:],
                       'visited_sources': [{k: v for k, v in d.items() if k not in ('preview', 'discovered_seq')}
                                           for ref, d in views.items() if ref in keep],
                       'pending_source_opportunities': []}}
    return s, {'checkpoint': str(path.relative_to(ROOT)), 'before_seq': cutoff,
               'prefix_sha256': digest(events), 'C_source': 'experiments/gap_evidence_claim_loop/single_gap_rollout/BANK.json',
               'C_case': source['case_id'], 'prior_seed_review': source['prefix_review'],
               'R_source': 'experiments/minimal_recoverable_loop/e0_reference/QUESTION_SKELETONS.json',
               'R_policy': 'historical Q-only exact sentence spans; mechanical data reuse, no Writer/Admission logic',
               'promising_source': promising,
               'trace_projection': 'last 3 actions plus seed and promising source handles; not full workspace'}, views


def main():
    sk = read('experiments/skeleton_state_alignment/e0_addressability/RUNTIME_SKELETON_D2.json')
    reviews = read('experiments/belief_need_budget_locality_repair/bank/CLAIM_SUPPORT_REVIEW.json')
    old_sk = read('experiments/minimal_recoverable_loop/e0_reference/QUESTION_SKELETONS.json')
    seeds = read('experiments/gap_evidence_claim_loop/single_gap_rollout/BANK.json')
    bank, provenance, routes, special = {}, {}, {}, {}
    for spec in SPECS:
        s, p, rid, strategy = historical_state(spec, sk, reviews)
        sid = spec[0]; bank[sid] = s; provenance[sid] = p; routes[sid] = (rid, strategy)
    for sid, qid, rid in [('S15', '546', 'R1'), ('S16', '1094', 'R1')]:
        s, p, views = legacy_state(qid, old_sk, seeds)
        bank[sid] = s; provenance[sid] = p; routes[sid] = (rid, 'LOCATE_SOURCE'); special[sid] = views
    # Weak candidates are drawn from real observations/queries at each prefix.
    # Alternative later H strings can be borrowed only where their entity was
    # already visible; perturbation provenance is explicit, never naturalized.
    injections = {
        'S02': ('Ding Lei (William Ding) may be the founder described in the Original Question.', 'F08', 1, 'Ding'),
        'S03': ('Kwon Hyuk-bin, founder of Smilegate, may be the person referenced in the question.', 'F08', 1, 'Kwon'),
        'S07': ('The shared disorder in the two 2010s case reports may be fibrodysplasia ossificans progressiva (FOP).', 'F13', 1, 'fibrodysplasia'),
        'S08': ('The shared disorder in the two 2010s case reports may be stiff person syndrome (SPS).', 'F13', 1, 'Stiff'),
        'S11': ('The University of Melbourne may be the university associated with the target contest.', 'F15', 1, 'University of Melbourne'),
        'S12': ('The University of Melbourne may be the university associated with the target contest.', 'F15', 1, 'University of Melbourne'),
    }
    variants = []
    perturbations = []
    for sid, s in bank.items():
        variants.append({'id': sid + '__P0', 'state_id': sid, 'condition': 'P0', 'state': copy.deepcopy(s)})
        if sid in injections or sid in special:
            p1 = copy.deepcopy(s)
            if sid in injections:
                statement, traj, turn, needle = injections[sid]
                sp = HIST / f'acquisition/trajectories/{traj}/decision{turn}_tool.json'
                source = read(sp)
                assert needle.lower() in json.dumps(source, ensure_ascii=False).lower()
                evidence = {'path': str(sp.relative_to(ROOT)), 'candidate_marker': needle,
                            'construction': 'historically observed candidate; tentative role assignment is perturbation'}
            else:
                ref = 'D5' if sid == 'S15' else 'D34'
                statement = ('Mark Williams may be the player described by the question.' if sid == 'S15'
                             else 'The target match may be the PSG–Lille match involving Lionel Messi.')
                evidence = {'observed_source': special[sid][ref], 'construction': 'tentative target-role assignment from visible entity'}
            hid = 'H' + str(len(p1['H']) + 1)
            p1['H'].append({'hypothesis_id': hid, 'statement': statement})
            variants.append({'id': sid + '__P1', 'state_id': sid, 'condition': 'P1', 'state': p1})
            perturbations.append({'id': sid + '__P1', 'origin': 'EXPERIMENTAL_PERTURBATION',
                                  'changed_fields': ['H'], 'injected_hypothesis_id': hid, 'basis': evidence,
                                  'wrongness': 'weak/unestablished target identity; no gold-answer classification'})
        p2 = copy.deepcopy(s)
        last = copy.deepcopy(s['TraceView']['recent_actions'][-1])
        rid, strategy = routes[sid]
        last.update(origin='EXPERIMENTAL_PERTURBATION', feedback='NoGain',
                    feedback_basis='counterfactual: two attempts on this route yielded no useful progress',
                    focus_requirement_id=rid, strategy=strategy,
                    hypothesis_ids_under_test=[h['hypothesis_id'] for h in s['H']],
                    recent_one_gap='Investigate the route represented by the recorded action.')
        for k in ('claim_additions', 'new_window_count'):
            last.pop(k, None)
        p2['TraceView']['recent_actions'] = [dict(copy.deepcopy(last), attempt=i) for i in (1, 2)]
        variants.append({'id': sid + '__P2', 'state_id': sid, 'condition': 'P2', 'state': p2})
        perturbations.append({'id': sid + '__P2', 'origin': 'EXPERIMENTAL_PERTURBATION',
                              'changed_fields': ['TraceView.recent_actions'],
                              'family': [rid, strategy, last['hypothesis_ids_under_test']],
                              'historical_action': s['TraceView']['recent_actions'][-1],
                              'rule': 'Replay the most recent authentic action twice with explicit hypothetical NoGain; no tool execution.'})
        if sid in special:
            p3 = copy.deepcopy(s)
            pending = copy.deepcopy(provenance[sid]['promising_source'])
            pending['origin'] = 'EXPERIMENTAL_PERTURBATION'
            pending['opportunity'] = 'Previously discovered source; not locally inspected; consider whether it can help test the question.'
            p3['TraceView']['pending_source_opportunities'] = [pending]
            variants.append({'id': sid + '__P3', 'state_id': sid, 'condition': 'P3', 'state': p3})
            perturbations.append({'id': sid + '__P3', 'origin': 'EXPERIMENTAL_PERTURBATION',
                                  'changed_fields': ['TraceView.pending_source_opportunities'],
                                  'rule': 'Resurface an already observed discovery preview; no new facts and no tool directive.'})
    for v in variants:
        base = bank[v['state_id']]
        for k in ('Q', 'R', 'C'):
            assert v['state'][k] == base[k]
        v['state_sha256'] = digest(v['state'])
    assert len(bank) == 16 and len({s['qid'] for s in bank.values()}) == 10
    write('e0_state_bank/STATES.json', bank)
    write('e0_state_bank/PROVENANCE.json', provenance)
    write('e0_state_bank/PERTURBATIONS.json', perturbations)
    write('e0_state_bank/VARIANTS.json', variants)
    write('e0_state_bank/SOURCE_HASHES.json', SOURCES)
    print(json.dumps({'states': len(bank), 'qids': len({s['qid'] for s in bank.values()}),
                      'requests': len(variants), 'historical_sources': len(SOURCES)}, indent=2))


if __name__ == '__main__':
    main()
