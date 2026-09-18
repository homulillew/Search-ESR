"""Combine saved offline judgments; no online calls or automatic semantic judging."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[3]
ARMS = ['verbatim', 'conservative', 'expression_packet', 'expression_full_context']


def read(path):
    return json.loads(path.read_text())


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2))


def summarize(run):
    run = Path(run)
    audit = read(run / 'audit.json')
    mapping = read(run / 'semantic_card_mapping.json')
    cards = {c['card_id']: c for c in read(run / 'semantic_cards.json')}
    rows = []
    methods = []
    for name in ['semantic_review_1117_786.json', 'semantic_review_551_645.json', 'semantic_review_1072_1172.json']:
        content = read(run / name)
        if isinstance(content, list):
            data = content
            methods.append(dict(file=name, method='Agent reviewer reported arm-hidden source review; see row notes.'))
        else:
            data = content.get('rows', content.get('cards'))
            methods.append(dict(file=name, method=content['method']))
        for row in data:
            assert row['qid'] == mapping[row['card_id']]['qid']
            assert row['query_evaluable'] == (cards[row['card_id']]['query'] is not None)
            rows.append(dict(row, **mapping[row['card_id']]))
    assert len(rows) == len(cards) == len({r['card_id'] for r in rows})
    # Preserve original reviewer labels, and expose a stricter sensitivity count.
    boundary_card = '2731bede208a'

    def semantic_counts(sub):
        return dict(attempts=len(sub), evaluable=sum(r['query_evaluable'] for r in sub),
                    abstained=sum(not r['query_evaluable'] for r in sub),
                    explicit_mutation=sum(bool(r['explicit_mutations']) for r in sub),
                    strict_explicit_mutation=sum(bool(r['explicit_mutations']) and r['card_id'] != boundary_card for r in sub),
                    ambiguity=sum(bool(r['ambiguities']) for r in sub),
                    ambiguity_or_mutation=sum(bool(r['ambiguities'] or r['explicit_mutations']) for r in sub),
                    outside_packet_question_fact=sum(bool(r['outside_packet_question_facts']) for r in sub),
                    outside_actual_input=sum(bool(r['outside_packet_question_facts']) and r['arm'] != 'expression_full_context' for r in sub),
                    unsupported_fact=sum(bool(r['unsupported_facts']) for r in sub),
                    condition_omitted=sum(bool(r['omissions']) for r in sub))

    annotations = {(a['qid'], a['docid']): a for a in read(run / 'reference_annotations.json')['annotations']}
    for name in ['supplemental_645.json', 'supplemental_786.json', 'supplemental_1172.json']:
        for ann in read(run / name)['annotations']:
            annotations[(ann['qid'], ann['docid'])] = ann
    with sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro', uri=True) as db:
        for ann in annotations.values():
            text, url = db.execute('select text,url from documents where docid=?', (ann['docid'],)).fetchone()
            assert ann['document_sha256'] == hashlib.sha256(text.encode()).hexdigest()
            assert ann['url'] == url
            for alternative in ann['proof_alternatives']:
                for proof in alternative:
                    assert proof['source_spans']
                    assert all(text[a:b] == proof['quote'] for a, b in proof['source_spans'])
    retrieval = []
    request_seconds, event_times = [], []
    for session in audit['sessions']:
        folder = run / session['session']
        result = read(folder / 'result.json')
        hits = []
        for rank, window in enumerate(result['result'], 1):
            ann = annotations.get((result['qid'], window['docid']))
            if not ann:
                continue
            ranges = [[window['offset'], window['end_char']]] + ([window['title_span']] if window['title_span'] else [])
            visible = any(all(any(any(lo <= a and b <= hi for lo, hi in ranges)
                                  for a, b in proof['source_spans']) for proof in alternative)
                          for alternative in ann['proof_alternatives'])
            hits.append(dict(docid=window['docid'], rank=rank, visible=visible,
                             kind=ann['kind'], packet_alignment=ann['packet_alignment']))
        selected = [h for h in hits if h['packet_alignment'] == 'selected_basis']
        retrieval.append(dict(session=session['session'], qid=session['qid'], arm=session['arm'],
                              document=bool(selected), visible=any(h['visible'] for h in selected), hits=hits))
        for event in [json.loads(line) for line in (folder / 'events.jsonl').read_text().splitlines()]:
            event_times.append(event['time'])
            if event['kind'] == 'api_response':
                request_seconds.append(dict(arm=session['arm'], seconds=event['elapsed_seconds']))

    def retrieval_counts(sub):
        return dict(attempts=len(sub), document=sum(r['document'] for r in sub),
                    visible=sum(r['visible'] for r in sub))

    output = dict(
        execution=audit['aggregates'],
        semantic={arm: semantic_counts([r for r in rows if r['arm'] == arm]) for arm in ARMS},
        semantic_per_qid={q: {arm: semantic_counts([r for r in rows if r['qid'] == q and r['arm'] == arm])
                             for arm in ARMS} for q in audit['per_qid']},
        semantic_rows=rows, review_methods=methods,
        semantic_sensitivity='2731bede208a can be read as a wrong direct elopement relationship or telegraphic ambiguity. Report one high-confidence mutation plus one borderline; original labels preserved. See review_adjudication_1117.json.',
        supplemental_retrieval={arm: retrieval_counts([r for r in retrieval if r['arm'] == arm]) for arm in ARMS},
        supplemental_per_qid={q: {arm: retrieval_counts([r for r in retrieval if r['qid'] == q and r['arm'] == arm])
                                 for arm in ARMS} for q in audit['per_qid']},
        retrieval_rows=retrieval,
        api_elapsed_seconds={arm: dict(count=len(rs := [r['seconds'] for r in request_seconds if r['arm'] == arm]),
                                      sum=sum(rs), mean=sum(rs) / len(rs) if rs else None) for arm in ARMS},
        first_event=min(event_times), last_event=max(event_times),
        limitation='Six known development packets, manually selected. Post-run positive pool is incomplete and includes partial leads. No final-answer assessment. Model repetitions within question are not independent questions. Semantic review is agent/manual, partly arm-hidden, no separate API judge or human gold annotation. Null reasons were not exposed by API.')
    dump(run / 'analysis.json', output)
    dump(run / 'merged_postrun_annotations.json', dict(method='Frozen positives plus explicitly post-run supplementary alternatives/leads; never overwrites frozen reference counts.', annotations=list(annotations.values())))
    dump(run / 'decision.json', dict(promote_default=False, freeze_compiler=False,
         completed_stage='fixed_packet_diagnostic', automatic_selector_tested=False,
         next_step='Retain exact-packet/Verbatim as the leading baseline; test automatic basis selection separately. Compiler remains experimental; do not hide nulls through fallback in this comparison.',
         evidence='Input/provenance plumbing passed, but compilation abstained and retained semantic risks without a stable paired retrieval advantage across these six packets.'))
    return output


if __name__ == '__main__':
    result = summarize(sys.argv[1])
    print(json.dumps({k: result[k] for k in ['semantic', 'supplemental_retrieval']}, ensure_ascii=False, indent=2))
