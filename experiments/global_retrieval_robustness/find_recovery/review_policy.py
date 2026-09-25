"""Single-reviewer assessment of both Find windows in every F2 decision."""
import hashlib
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parents[2]))
from experiments.global_retrieval_robustness.common import metrics, read, write

# Explicit cell/rank labels, decided by reading the actual returned W and Gap.
FULL = {
    ('U1_A01', 1), ('U1_A02', 1), ('U1_A03', 1), ('U1_A04', 1), ('U1_A04', 2),
    ('U1_A05', 1), ('U1_A06', 1), ('U1_A07', 1), ('U1_A09', 1), ('U1_A10', 1),
    ('U1_B03', 1), ('U1_B04', 1), ('U1_B05', 1), ('U1_B05', 2),
    ('U1_B06', 2), ('U1_B08', 1),
    ('U1_C02', 1), ('U1_C03', 1), ('U1_C05', 1), ('U1_C06', 1), ('U1_C07', 1),
    ('U1_D02', 1), ('U1_D05', 1), ('U1_D06', 1), ('U1_D07', 1), ('U1_D08', 1),
}
PARTIAL_USEFUL = {
    ('U1_A11', 2): 'Galacta page directly names Albino Frog as publisher, but dates release 1993 rather than frozen November 1992.',
    ('U1_C09', 1): 'Company catalog lists Galacta: The Battle for Saturn as a 1992 DOS game, but not November/shareware.',
    ('U1_C09', 2): 'Game page says Galacta is Albino Frog shareware, but states 1993, leaving November 1992 unverified.',
}
SPECIAL = {
    ('U1_A08', 1): 'Wrong football match: window concerns Sidemen rather than PSG versus Lille.',
    ('U1_A08', 2): 'Placeholder page names Messi and PSG but does not identify both teams in the returned W.',
    ('U1_A11', 1): 'Company catalog associates Albino Frog with Galacta; it does not establish the game publisher relation.',
    ('U1_A12', 1): 'Window discusses other singers and their mothers, not the 2021 Heart Evangelista article.',
    ('U1_B01', 1): 'Correct actor D, but Find stops at filmography table header before the Policeman 1 row.',
    ('U1_B02', 1): 'Correct Dean Dodrill D, but window stops before animation paper size.',
    ('U1_B04', 2): 'Neymar is named as a scorer, but the returned W does not say his goal was PSG’s second.',
    ('U1_B06', 1): 'Game page gives publisher and shareware facts but omits planned episode-two title.',
    ('U1_B07', 1): 'Correct article reaches G-mik programme mention but omits the Missy Sandejas role.',
    ('U1_C01', 1): 'Peter Gabriel human-rights page, not the Forbes album-count source.',
    ('U1_C04', 2): 'Canonical final standings D, but Find shows only early rows before Enugu Rangers.',
    ('U1_C08', 1): 'Generic cartoon list does not show native title.',
    ('U1_C10', 1): 'Cast page returns role names including Policeman 1, but no actor-to-role mapping in W.',
    ('U1_C11', 1): 'Ronnie O’Sullivan maximum-break page, not Ding Junhui.',
    ('U1_C11', 2): 'Mark Williams page, not Ding Junhui.',
    ('U1_C12', 1): 'League finance passage does not discuss the PSG merger.',
    ('U1_D01', 1): 'NPR passage says more than 60 albums, not the May 2017 Forbes count of 65.',
    ('U1_D03', 1): 'Nonfinal standings page shows Rangers sixth after 37 matches; frozen Gap asks where it finished after 38.',
    ('U1_D03', 2): 'Final standings D, but Find lands in leaders table; its Rangers mention is not final position.',
    ('U1_D04', 1): 'Nonfinal standings row shows +8 after 37 matches; it does not establish the final-table difference.',
    ('U1_D04', 2): 'Final standings D, but Find lands in leaders table without the Rangers goal difference.',
}


def main():
    events = [json.loads(x) for x in (BASE / 'policy_find_events.jsonl').read_text().splitlines()]
    assert len(events) == 40
    oracle = read(BASE / 'oracle_reviews.json')
    reviews = []
    for event in events:
        cid = event['case_id']
        for call in event['calls']:
            key = cid, call['rank']
            w = call['result']['matches'][0]['text'] if call['result'] and call['result']['matches'] else ''
            if key in FULL:
                grade = 'fully_sufficient'; reason = 'Returned W directly states the requested Gap fact with the needed entity and relation.'
            elif key in PARTIAL_USEFUL:
                grade = 'partial'; reason = PARTIAL_USEFUL[key]
            else:
                grade = 'no_gain'; reason = SPECIAL.get(key, 'Returned W does not establish the requested Gap fact.')
            reviews.append({'case_id': cid, 'qid': event['qid'], 'primary_type': event['primary_type'],
                            'rank': call['rank'], 'docid': call['docid'],
                            'window_sha256': hashlib.sha256(w.encode()).hexdigest() if w else None,
                            'grade': grade, 'useful': grade == 'fully_sufficient' or key in PARTIAL_USEFUL,
                            'fully_sufficient': grade == 'fully_sufficient',
                            'reason': reason})
    assert len(reviews) == 80
    write(BASE / 'REVIEWS.json', {'oracle': oracle, 'policy': reviews})
    rows = []
    for event in events:
        rev = [r for r in reviews if r['case_id'] == event['case_id']]
        rows.append({'case_id': event['case_id'], 'qid': event['qid'], 'primary_type': event['primary_type'],
                     'P1_useful': rev[0]['useful'], 'P1_full': rev[0]['fully_sufficient'],
                     'P2_useful': any(r['useful'] for r in rev),
                     'P2_full': any(r['fully_sufficient'] for r in rev),
                     'rank2_useful': rev[1]['useful']})
    summary = {key: metrics([dict(r, hit=r[key]) for r in rows])
               for key in ['P1_useful', 'P2_useful', 'P1_full', 'P2_full']}
    summary['top2_rescue'] = [r['case_id'] for r in rows if not r['P1_useful'] and r['P2_useful']]
    summary['rank2_useful_count'] = sum(r['rank2_useful'] for r in rows)
    summary['rank2_waste_count'] = 40 - summary['rank2_useful_count']
    summary['P1_useful_per_find_call'] = summary['P1_useful']['overall']['hit'] / 40
    summary['P2_useful_per_find_call'] = (summary['P1_useful']['overall']['hit'] +
                                          summary['rank2_useful_count']) / 80
    summary['P2_select'] = (summary['P2_useful']['overall']['rate'] -
                            summary['P1_useful']['overall']['rate'] >= 0.10 and
                            summary['P1_useful_per_find_call'] -
                            summary['P2_useful_per_find_call'] <= 0.05)
    write(BASE / 'policy_metrics.json', summary)


if __name__ == '__main__':
    main()
