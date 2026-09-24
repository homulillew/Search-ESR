"""Single-reviewer W-level labels over arm-masked F3 packets.

The arm mapping is opened only by analyze.py. The reviewer had seen live
progress, so this is arm-masked packet presentation, not full blinding.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKETS = json.loads((HERE / 'REVIEW_PACKETS.json').read_text())

# Indices refer to chronological newly returned observations in each packet.
# All unlisted observations were separately inspected as providing no new
# material support, contradiction or valid exclusion for that frozen Gap.
LABELS = {
    'P01': {'useful': {}, 'valid_claims': [], 'claim_gap_resolved': False,
            'premature_close': False, 'missed_close': False,
            'evidence_answer_available': False,
            'failure_codes': ['GE12'],
            'reason': 'Find/Open were spent inside an unrelated last-minute-goals list; later East Bengal searches drifted from PSG–Lille.'},
    'P02': {'useful': {}, 'valid_claims': [], 'claim_gap_resolved': False,
            'premature_close': False, 'missed_close': False,
            'evidence_answer_available': False,
            'failure_codes': ['GE12'],
            'reason': 'The only completed Search surfaced Manchester and Premier League material; the next Gap Review call was interrupted.'},
    'P03': {'useful': {19: 'D1 filmography row supplies Policeman 1, if bound to the previously observed Peter King document.'},
            'valid_claims': [], 'claim_gap_resolved': False,
            'premature_close': True, 'missed_close': False,
            'evidence_answer_available': True,
            'failure_codes': ['GE7', 'GE10'],
            'reason': 'W21 alone has a filmography row but no Peter King name; the one-W Claim overstates its identity binding. Gap Reviewer closed on that Claim. Other queued calls continued after first closure.'},
    'P04': {'useful': {1: 'W64 states PSG split from Paris FC in 1972; this is a relevant partial club-history fact.'},
            'valid_claims': ['C3'], 'claim_gap_resolved': False,
            'premature_close': False, 'missed_close': False,
            'evidence_answer_available': False,
            'failure_codes': ['GE12'],
            'reason': 'PSG split is locally supported, but no W establishes that both PSG and Lille satisfy the complete historical clues; repeated global searches persisted.'},
    'P05': {'useful': {
                4: 'W6 relates a May 2017 Forbes listing and 65 albums, but names Forbes Magazine rather than Forbes Africa.',
                5: 'W7 quotes an Oliver Mtukudzi Forbes Africa interview and 67 albums in 2016; May timing is absent.',
                8: 'W10 is an exact May 2017 Forbes Africa URL with Oliver and 65 albums; the Reader did not commit it.'},
            'valid_claims': ['C3', 'C4', 'C5'], 'claim_gap_resolved': False,
            'premature_close': True, 'missed_close': False,
            'evidence_answer_available': True,
            'failure_codes': ['GE10', 'GE14'],
            'reason': 'First resolved verdict followed W6, before the exact Forbes Africa May W10 was read. Claims at that point did not bind the required publisher and date. A later Find reread an unrelated document.'},
    'P06': {'useful': {}, 'valid_claims': [], 'claim_gap_resolved': False,
            'premature_close': False, 'missed_close': False,
            'evidence_answer_available': False,
            'failure_codes': ['GE12', 'GE13'],
            'reason': 'Search drifted to Championship League and unrelated snooker; Open repeated seed W13 and Find landed on Ding biography/titles, not the later match sequence.'},
    'P07': {'useful': {15: 'W17 lists Enugu Rangers 8th, 58 points, goal difference 8 and exactly three equal-points pairs; Search title dates the table 2014.'},
            'valid_claims': ['C3', 'C4'], 'claim_gap_resolved': False,
            'premature_close': True, 'missed_close': False,
            'evidence_answer_available': True,
            'failure_codes': ['GE10', 'GE14'],
            'reason': 'Claims omit the season year visible only in the Search result title, so Claims alone do not establish the 2011–2016 condition. Gap Reviewer nevertheless closed. Later W24 repeats the same table.'},
    'P08': {'useful': {}, 'valid_claims': [], 'claim_gap_resolved': False,
            'premature_close': False, 'missed_close': False,
            'evidence_answer_available': False,
            'failure_codes': ['GE12', 'GE13'],
            'reason': 'Queries focused on Ding and the English Open but returned old seed W13, Ding biography, an unrelated head-to-head page and 2025 Championship League.'},
    'P09': {'useful': {
                5: 'W7 explicitly links the season-three Edgar sacrifice episode to You’re the Worst.',
                9: 'W11 explicitly links Gretchen/Jimmy’s season-one reconciliation date to You’re the Worst.'},
            'valid_claims': ['C2', 'C3'], 'claim_gap_resolved': True,
            'premature_close': False, 'missed_close': False,
            'evidence_answer_available': True,
            'failure_codes': [],
            'reason': 'Committed season-one and season-three plot facts identify the series and satisfy the single Gap.'},
    'P10': {'useful': {
                4: 'W6 gives a May 2017 Forbes listing and 65 albums but not the exact Forbes Africa source.',
                5: 'W7 gives a Forbes Africa interview in 2016 and 67 albums but no May timing.',
                7: 'W9 is the exact May 2017 Forbes Africa article with 65 albums; the Reader missed it.',
                9: 'W11 confirms Oliver on a top-ten list featured in a May Forbes Africa edition.'},
            'valid_claims': ['C3', 'C4', 'C5', 'C7'],
            'claim_gap_resolved': False, 'premature_close': True,
            'missed_close': False, 'evidence_answer_available': True,
            'failure_codes': ['GE5', 'GE7', 'GE10', 'GE14', 'GE9'],
            'reason': 'First resolved verdict followed W6, before the exact Forbes Africa W9. W9 yielded no Finding. W7 says “67 albums later” in retrospective narration and separately quotes a 2016 interview; C6 falsely binds 67 to the 2016 interview. It also conflicts with the 65-in-2017 Claim without reconciliation.'},
    'P11': {'useful': {10: 'W12 has the exact role row in the same known Peter King source, but no name inside this isolated W.'},
            'valid_claims': [], 'claim_gap_resolved': False,
            'premature_close': False, 'missed_close': False,
            'evidence_answer_available': True,
            'failure_codes': ['GE8', 'GE14'],
            'reason': 'Reader found the role, Verifier rejected the identity link, then Actor answered the original question while the Gap remained open. The rejection is defensible under strict one-W support; the opposite arm accepted identical bytes.'},
    'P12': {'useful': {
                0: 'W2 directly describes the season-one Gretchen/Jimmy date scene.',
                2: 'W4 describes Edgar’s season-three sacrifice.',
                3: 'W5 identifies Edgar as Jimmy’s roommate in You’re the Worst.'},
            'valid_claims': ['C2', 'C3', 'C4', 'C5'],
            'claim_gap_resolved': True, 'premature_close': False,
            'missed_close': False, 'evidence_answer_available': True,
            'failure_codes': ['GE14', 'GE16', 'GE9'],
            'reason': 'First Search already returned season-one and season-three evidence, but Reader missed W2 until two repeated Finds of the same W. C5 about five seasons is grounded yet unnecessary for this Gap.'},
}


def main():
    if (HERE / 'REVIEWS.json').exists():
        raise FileExistsError('REVIEWS.json')
    assert set(LABELS) == {p['review_id'] for p in PACKETS}
    reviews = []
    for packet in PACKETS:
        rid = packet['review_id']
        label = LABELS[rid]
        assert all(0 <= n < len(packet['observations']) for n in label['useful'])
        assert set(label['valid_claims']) <= {c['claim_id'] for c in packet['claims']}
        observations = []
        for i, obs in enumerate(packet['observations']):
            observations.append({'observation_index': i, 'ref': obs['ref'],
                                 'action_index': obs['action_index'],
                                 'useful_evidence': i in label['useful'],
                                 'reason': label['useful'].get(i, 'No new Gap-relevant support, refutation or valid exclusion in this W.')})
        claims = [{'claim_id': c['claim_id'], 'evidence_refs': c['evidence_refs'],
                   'supported_by_exact_W': c['claim_id'] in label['valid_claims']}
                  for c in packet['claims']]
        reviews.append({'review_id': rid, 'observations': observations,
                        'claims': claims,
                        'claim_gap_resolved': label['claim_gap_resolved'],
                        'premature_close': label['premature_close'],
                        'missed_close': label['missed_close'],
                        'evidence_answer_available': label['evidence_answer_available'],
                        'failure_codes': label['failure_codes'],
                        'reason': label['reason']})
    (HERE / 'REVIEWS.json').write_text(json.dumps(reviews, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
