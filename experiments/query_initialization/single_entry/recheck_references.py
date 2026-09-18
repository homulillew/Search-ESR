"""Recheck pre-existing positive spans. Unmatched results are unassessed, not negatives."""
import hashlib
import json
from pathlib import Path
import sys


def recheck(run, annotations_file):
    run, annotations_file = Path(run), Path(annotations_file)
    annotations = json.loads(annotations_file.read_text())['annotations']
    lookup = {(a['qid'], a['docid']): a for a in annotations}
    sessions = []
    for folder in sorted(run.glob('qid_*')):
        summary = json.loads((folder / 'summary.json').read_text())
        handoff = json.loads((folder / 'handoff.json').read_text())
        hits = []
        for attempt in handoff['search_attempts']:
            for view in attempt['result']:
                annotation = lookup.get((summary['qid'], view['docid']))
                if annotation is None:
                    continue
                assert view['document_sha256'] == annotation['document_sha256']
                ranges = [[view['offset'], view['end_char']]]
                if view['title_span']:
                    ranges.append(view['title_span'])
                visible = any(all(any(any(lo <= a and b <= hi for lo, hi in ranges)
                                          for a, b in proof['source_spans']) for proof in option)
                              for option in annotation['proof_alternatives'])
                hits.append(dict(docid=view['docid'], window_ref=view['window_ref'],
                                 kind=annotation['kind'], reference_visible=visible))
        sessions.append(dict(session=folder.name, qid=summary['qid'], arm=summary['arm'],
                             confirmed_document=bool(hits), reference_visible=any(h['reference_visible'] for h in hits),
                             hits=hits))
    result = dict(method='Existing positive reference spans only; no new qrels or automatic relevance judging. Unmatched windows unassessed. qid645 is outside the previous holdout pool.',
                  annotations_file=str(annotations_file.resolve()),
                  annotations_sha256=hashlib.sha256(annotations_file.read_bytes()).hexdigest(),
                  aggregates={a: dict(attempts=sum(s['arm'] == a for s in sessions),
                      confirmed_document=sum(s['arm'] == a and s['confirmed_document'] for s in sessions),
                      reference_visible=sum(s['arm'] == a and s['reference_visible'] for s in sessions))
                      for a in sorted({s['arm'] for s in sessions})}, sessions=sessions)
    (run / 'reference_recheck.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result['aggregates'], indent=2))


if __name__ == '__main__':
    recheck(sys.argv[1], sys.argv[2])
