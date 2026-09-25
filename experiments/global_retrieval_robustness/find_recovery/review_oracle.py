"""Materialize the single-reviewer semantic audit of all 40 F1 windows."""
import hashlib
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parents[2]))
from experiments.global_retrieval_robustness.common import metrics, read, write

FAIL = {
    'U1_B01': ('partial', 'Window confirms film participation but stops at the filmography header before the Policeman 1 role row.'),
    'U1_B02': ('no_gain', 'Window shows the PC specification; the 8x11 animation paper sentence is outside it.'),
    'U1_B07': ('partial', 'Window reaches the G-mik programme but not the role Missy Sandejas.'),
    'U1_C04': ('no_gain', 'Window shows only the first four table rows; the Enugu Rangers row and goal difference are absent.'),
    'U1_C08': ('partial', 'Window identifies the cartoon by its English title but omits its native_name field.'),
    'U1_D03': ('no_gain', 'Window lands in table footer and days-as-leaders table; its Enugu Rangers mention is not the league position.'),
    'U1_D04': ('no_gain', 'Window lands in table footer and days-as-leaders table; it gives no Enugu Rangers goal difference.'),
}
SUCCESS_WITHOUT_ANCHOR = {
    'U1_C11': 'Window explicitly says Ding turned professional in 2003 and made seven maximum breaks.',
    'U1_D05': 'Window explicitly says Enugu Rangers won their seventh 2016 league title.',
    'U1_D08': 'Window explicitly says Ding turned professional in 2003.',
}


def main():
    bank = {x['case_id']: x for x in read(BASE / 'BANK.json')}
    events = [json.loads(line) for line in (BASE / 'oracle_find_events.jsonl').read_text().splitlines()]
    assert len(events) == len(bank) == 40
    reviews = []
    for event in events:
        cid = event['case_id']; b = bank[cid]
        w = event['result']['matches'][0]['text'] if event['result'] and event['result']['matches'] else ''
        hit = b['anchor'].lower() in w.lower()
        grade, reason = FAIL.get(cid, ('fully_sufficient', SUCCESS_WITHOUT_ANCHOR.get(
            cid, 'Returned window directly states the requested Gap fact in source context.')))
        if grade == 'fully_sufficient' and not hit and cid not in SUCCESS_WITHOUT_ANCHOR:
            raise AssertionError(f'Unreviewed anchor miss: {cid}')
        reviews.append({'case_id': cid, 'qid': b['qid'], 'primary_type': b['primary_type'],
                        'docid': b['docid'], 'window_sha256': hashlib.sha256(w.encode()).hexdigest() if w else None,
                        'anchor_hit': hit, 'grade': grade, 'useful': grade == 'fully_sufficient',
                        'fully_sufficient': grade == 'fully_sufficient',
                        'partial': grade == 'partial', 'no_gain': grade == 'no_gain', 'reason': reason})
    write(BASE / 'oracle_reviews.json', reviews)
    counts = {}
    for key in ['useful', 'fully_sufficient', 'anchor_hit']:
        counts[key] = metrics(reviews, key)
    write(BASE / 'oracle_metrics.json', counts)


if __name__ == '__main__':
    main()
