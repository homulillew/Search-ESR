"""Prefix-only coverage packets; read before any Frontier request is submitted."""
import hashlib
import json
from pathlib import Path

TOP = Path(__file__).resolve().parents[1]


def main():
    bank = json.load(open(TOP / 'bank/CHECKPOINT_BANK.json'))
    requirements = json.load(open(TOP / 'bank/REQUIREMENT_MAP.json'))
    source_map = {}
    packets = []

    def observe(w):
        text = w.get('text') or w.get('preview')
        if not text:
            return None
        key = hashlib.sha256(text.encode()).hexdigest()
        if key not in source_map:
            source_map[key] = {'source_id': f'E{len(source_map)+1:03}',
                               'title': w.get('title'), 'url': w.get('url'), 'text': text,
                               'text_sha256': key}
        return source_map[key]['source_id']

    for b in bank:
        refs = []
        for e in b['history']:
            if 'observation' in e:
                ref = observe(e['observation'])
                if ref:
                    refs.append(ref)
            for a in e.get('actions', []):
                r = a['result'] or {}
                for w in r.get('results', r.get('matches', [])):
                    ref = observe({**r, **w})
                    if ref:
                        refs.append(ref)
                if r.get('text'):
                    refs.append(observe(r))
        packets.append({'case_id': b['case_id'], 'qid': b['qid'], 'requirements': requirements[b['qid']],
                        'claims': [c['statement'] for c in b['state']['verified_claims']],
                        'hypothesis': b['state']['working_hypothesis'], 'history_source_refs': list(dict.fromkeys(refs)),
                        'checkpoint_id': b['checkpoint_id']})
    (TOP / 'bank/COVERAGE_PACKETS.json').write_text(json.dumps(packets, ensure_ascii=False, indent=2) + '\n')
    sources = {r['source_id']: r for r in source_map.values()}
    (TOP / 'bank/PREFIX_SOURCES.json').write_text(json.dumps(sources, ensure_ascii=False, indent=2) + '\n')
    for qid in requirements:
        ps = [r for r in packets if r['qid'] == qid]
        ss = list(dict.fromkeys(ref for r in ps for ref in r['history_source_refs']))
        lines = [f'QUESTION {qid}', requirements[qid]['question'], json.dumps(requirements[qid]['requirements'], ensure_ascii=False, indent=2)]
        for r in ps:
            lines += ['', r['case_id'] + ' ' + r['checkpoint_id'], 'Hypothesis: ' + str(r['hypothesis'])]
            lines += [f'C{i+1}: {c}' for i, c in enumerate(r['claims'])]
            lines += ['Visible history sources: ' + ', '.join(r['history_source_refs'])]
        for ref in ss:
            w = sources[ref]
            lines += ['', f"{ref}: {w['title']} {w['url']}", w['text']]
        path = TOP / 'bank' / ('review_' + qid + '.txt')
        path.write_text('\n'.join(lines) + '\n')
        print(qid, len(ss), path.stat().st_size)


if __name__ == '__main__':
    main()
