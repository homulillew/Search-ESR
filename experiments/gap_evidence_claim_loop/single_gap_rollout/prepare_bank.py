"""Create six frozen, prefix-grounded F3 cells before any new model calls."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
F1 = json.loads((HERE.parent / 'finding_extraction/BANK.json').read_text())
F2 = json.loads((HERE.parent / 'claim_commit/BANK.json').read_text())
OUT = json.loads((HERE.parent / 'claim_commit/outcomes.json').read_text())

SPEC = [
    ('546', 'T1_546', 'v3a', 33,
     "What were Ding Junhui's subsequent 2023 English Open results after the opening 4–3 win, and did they follow the required 4–3, 4–0, loss order?", 1),
    ('1094', 'T1_1094', 'v3a', 69,
     'Which of the clubs in the PSG–Lille 4–3 fixture satisfies the split-founded history clue, and does the other satisfy the identity-evolution clue?', 2),
    ('517', 'T1_517', 'legacy', None,
     'What exact credited role did Peter King play in The Constant Gardener?', 1),
    ('435', 'T3_435', 'legacy', None,
     'Was Oliver Mtukudzi featured by Forbes in the manner required by the original question?', 2),
    ('580', 'T1_580', 'legacy', None,
     'Which series has the season-one reconciliation date and season-three roommate sacrifice described in the question?', 1),
    ('177', 'T1_177', 'legacy', None,
     'Did Enugu Rangers satisfy the historical equal-points table clue in the question?', 2),
]


def build():
    if (HERE / 'BANK.json').exists():
        raise FileExistsError('BANK.json')
    bank = []
    for qid, source_case, kind, seq, gap, nclaims in SPEC:
        source = next(c for c in F1 if c['case_id'] == source_case)
        verified = [p for p in F2 if p['source_case'] == source_case and p['part'] == 'A'
                    and OUT[p['packet_id']]['V_commit']]
        assert len(verified) >= nclaims
        ref = source['source_checkpoint']['historical_ref'] if kind == 'v3a' else 'W1'
        doc_ref = source['source_checkpoint']['historical_doc_ref'] if kind == 'v3a' else 'D1'
        if kind == 'v3a':
            # The historical ref is W13/W38 and D10/D34, not F1's local W1/D1.
            assert ref.startswith('W') and doc_ref.startswith('D')
        else:
            assert source['source_checkpoint']['historical_doc_ref'].isdigit()
        claims = [{'claim_id': f'C{i}', 'statement': p['finding']['statement'],
                   'evidence_refs': [ref], 'version': 1}
                  for i, p in enumerate(verified[:nclaims], 1)]
        bank.append({'case_id': f'F3_{qid}', 'qid': qid, 'source_case': source_case,
                     'source_kind': kind, 'source_checkpoint': source['source_checkpoint'],
                     'checkpoint_seq': seq, 'raw_question': source['raw_question'],
                     'active_gap': gap, 'initial_claims': claims,
                     'relevant_observed_window': {'ref': ref, 'doc_ref': doc_ref,
                                                  'title': source['new_observation']['title'],
                                                  'text': source['new_observation']['text']},
                     'working_hypothesis': None,
                     'prefix_review': {'semantic_gap': True, 'gap_open': True,
                                       'seed_claims_supported': True, 'ambiguity': 'medium',
                                       'reason': 'Question, visible W and F2-verified seed Claims support this still-open semantic Gap.'}})
    assert len(bank) == len({x['qid'] for x in bank}) == 6
    (HERE / 'BANK.json').write_text(json.dumps(bank, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    build()
