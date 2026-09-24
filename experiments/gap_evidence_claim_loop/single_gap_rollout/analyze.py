"""F3 paired metrics from frozen events and the single-reviewer labels."""
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKETS = {p['review_id']: p for p in json.loads((HERE / 'REVIEW_PACKETS.json').read_text())}
REVIEWS = {r['review_id']: r for r in json.loads((HERE / 'REVIEWS.json').read_text())}
MAPPING = json.loads((HERE / 'PRIVATE_MAPPING.json').read_text())
EVENTS = [json.loads(line) for line in (HERE / 'events.jsonl').open()]


def one(rid):
    p, review = PACKETS[rid], REVIEWS[rid]
    cell = MAPPING[rid]
    caseid, arm = cell.split(':')
    useful = [o for o in review['observations'] if o['useful_evidence']]
    useful_actions = {o['action_index'] for o in useful}
    claims = review['claims']
    first_resolved = next((g for g in p['gap_status'] if g['review']['status'] == 'resolved'), None)
    first_close_action = first_resolved['action_index'] if first_resolved else None
    post_close_queued_actions = len(p['actions']) - first_close_action - 1 if first_resolved else 0
    # A retrieval is repeated if it yielded no new W handle in the ongoing
    # episode. This is a conservative mechanical redundancy proxy.
    first = p['seed_claims'][0]['evidence_refs'][0] if p['seed_claims'] else None
    seen = {first} if first else set()
    no_new_actions = 0
    for i, action in enumerate(p['actions']):
        refs = [o['ref'] for o in p['observations'] if o['action_index'] == i]
        if not any(ref not in seen for ref in refs):
            no_new_actions += 1
        seen.update(refs)
    return {'review_id': rid, 'cell': cell, 'qid': p['qid'], 'arm': arm,
            'status': p['status'], 'actor_decisions': max([a['decision'] for a in p['actions']], default=0),
            'retrieval_actions': len(p['actions']),
            'action_counts': dict(Counter(a['name'] for a in p['actions'])),
            'new_W_observations': len(p['observations']),
            'useful_W_observations': len(useful),
            'useful_action_count': len(useful_actions),
            'useful_W_per_action': len(useful) / len(p['actions']) if p['actions'] else 0,
            'useful_action_rate': len(useful_actions) / len(p['actions']) if p['actions'] else 0,
            'new_claims': len(claims), 'supported_claims': sum(c['supported_by_exact_W'] for c in claims),
            'unsupported_claims': sum(not c['supported_by_exact_W'] for c in claims),
            'claim_gap_resolved': review['claim_gap_resolved'],
            'evidence_answer_available': review['evidence_answer_available'],
            'model_resolved': bool(first_resolved),
            'premature_close': review['premature_close'], 'missed_close': review['missed_close'],
            'first_close_action_index': first_close_action,
            'post_close_queued_actions': post_close_queued_actions,
            'no_new_window_actions': no_new_actions,
            'failure_codes': review['failure_codes']}


def main():
    if set(PACKETS) != set(REVIEWS) or set(PACKETS) != set(MAPPING):
        raise ValueError('review/mapping mismatch')
    rows = [one(rid) for rid in sorted(PACKETS)]
    assert len(rows) == 12 and len({r['cell'] for r in rows}) == 12
    by_arm = {}
    for arm in ('R0', 'R1'):
        group = [r for r in rows if r['arm'] == arm]
        nogain_transitions = Counter()
        for row in group:
            packet = PACKETS[row['review_id']]
            review = REVIEWS[row['review_id']]
            useful_indices = {o['action_index'] for o in review['observations'] if o['useful_evidence']}
            decisions = sorted({a['decision'] for a in packet['actions']})
            for before, after in zip(decisions, decisions[1:]):
                prior_indices = [i for i, a in enumerate(packet['actions']) if a['decision'] == before]
                if any(i in useful_indices for i in prior_indices):
                    continue
                first_next = next(a for a in packet['actions'] if a['decision'] == after)
                nogain_transitions[first_next['name']] += 1
        actions = sum(r['retrieval_actions'] for r in group)
        useful_w = sum(r['useful_W_observations'] for r in group)
        useful_actions = sum(r['useful_action_count'] for r in group)
        claims = sum(r['new_claims'] for r in group)
        supported = sum(r['supported_claims'] for r in group)
        by_arm[arm] = {'cases': len(group),
                       'completed_without_interruption': sum(not r['status'].startswith('interrupted') for r in group),
                       'true_claim_based_gap_resolutions': sum(r['claim_gap_resolved'] for r in group),
                       'evidence_answer_available': sum(r['evidence_answer_available'] for r in group),
                       'model_resolved': sum(r['model_resolved'] for r in group),
                       'premature_close_cases': sum(r['premature_close'] for r in group),
                       'retrieval_actions': actions,
                       'tool_counts': dict(sum((Counter(r['action_counts']) for r in group), Counter())),
                       'W_observations': sum(r['new_W_observations'] for r in group),
                       'useful_W_observations': useful_w,
                       'useful_W_per_retrieval': useful_w / actions,
                       'useful_retrieval_actions': useful_actions,
                       'useful_action_rate': useful_actions / actions,
                       'new_claims': claims, 'supported_claims': supported,
                       'committed_claim_precision': supported / claims if claims else None,
                       'claim_bloat_per_case': claims / len(group),
                       'no_new_window_actions': sum(r['no_new_window_actions'] for r in group),
                       'post_close_queued_actions': sum(r['post_close_queued_actions'] for r in group),
                       'next_scope_after_nogain_decision': dict(nogain_transitions)}
    paired = {}
    wins = Counter()
    complete_wins = Counter()
    for qid in sorted({r['qid'] for r in rows}):
        a = next(r for r in rows if r['qid'] == qid and r['arm'] == 'R0')
        b = next(r for r in rows if r['qid'] == qid and r['arm'] == 'R1')
        if a['claim_gap_resolved'] != b['claim_gap_resolved']:
            winner = 'R1' if b['claim_gap_resolved'] else 'R0'
        else:
            a_rate = Fraction(a['useful_action_count'], a['retrieval_actions'])
            b_rate = Fraction(b['useful_action_count'], b['retrieval_actions'])
            winner = 'R1' if b_rate > a_rate else ('R0' if a_rate > b_rate else 'tie')
        wins[winner] += 1
        if not (a['status'].startswith('interrupted') or b['status'].startswith('interrupted')):
            complete_wins[winner] += 1
        paired[qid] = {'R0': a['cell'], 'R1': b['cell'], 'winner': winner,
                       'resolution_R0': a['claim_gap_resolved'],
                       'resolution_R1': b['claim_gap_resolved'],
                       'useful_action_rate_R0': a['useful_action_rate'],
                       'useful_action_rate_R1': b['useful_action_rate']}
    response_kinds = ('actor_response', 'reader_response', 'verifier_response', 'gap_review_response')
    cache = {}
    for kind in response_kinds:
        rs = [e for e in EVENTS if e['kind'] == kind]
        prompt = sum((e.get('cache_usage') or {}).get('prompt_tokens') or 0 for e in rs)
        hit = sum((e.get('cache_usage') or {}).get('prompt_cache_hit_tokens') or 0 for e in rs)
        cache[kind] = {'calls': len(rs), 'prompt_tokens': prompt,
                       'hit_tokens': hit, 'weighted_hit_rate': hit / prompt if prompt else None}
    codes = Counter(code for r in rows for code in r['failure_codes'])
    net = wins['R1'] - wins['R0']
    gate = {'paired_net_improvements_min_3': net >= 3,
            'R1_claim_precision_min_95pct': by_arm['R1']['committed_claim_precision'] >= .95,
            'R1_premature_close_max_10pct': by_arm['R1']['premature_close_cases'] / 6 <= .10}
    out = {'by_arm': by_arm, 'paired': paired, 'paired_wins': dict(wins),
           'net_R1_case_wins': net,
           'complete_pair_wins': dict(complete_wins),
           'complete_pair_net_R1_wins': complete_wins['R1'] - complete_wins['R0'],
           'gate_checks': gate, 'f3_pass': all(gate.values()),
           'failure_code_counts': dict(codes), 'cache_usage': cache, 'rows': rows,
           'audit': {'event_count': len(EVENTS),
                     'cell_starts': sum(e['kind'] == 'cell_start' for e in EVENTS),
                     'cell_ends': sum(e['kind'] == 'cell_end' for e in EVENTS),
                     'unanswered_gap_review_requests': sum(e['kind'] == 'gap_review_request' for e in EVENTS) -
                                                      sum(e['kind'] == 'gap_review_response' for e in EVENTS),
                     'interrupted_cell': 'F3_177:R0'}}
    (HERE / 'results.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in ('by_arm', 'paired_wins', 'net_R1_case_wins',
                                          'gate_checks', 'f3_pass', 'audit')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
