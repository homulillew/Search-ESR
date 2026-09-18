import json
from types import SimpleNamespace
import pytest
from .holdout import collect_ids, digest, validate_lock


def test_exclusion_collects_nested_ids_without_treating_document_ids_as_questions():
    found = set()
    collect_ids({'tasks': [{'qid': 12}, {'source_qid': '13', 'docid': '14'}],
                 'qids': ['15', 'unrelated']}, {'12', '13', '14', '15'}, found)
    assert found == {'12', '13', '15'}


@pytest.mark.parametrize('change', ['none', 'prompt', 'model', 'qid', 'decision', 'overlap'])
def test_holdout_lock_rejects_drift(tmp_path, change):
    dataset = tmp_path / 'BCPlus/data/bcplus/qa.jsonl'
    dataset.parent.mkdir(parents=True)
    dataset.write_text('{}')
    prompt = tmp_path / 'prompt.txt'
    prompt.write_text('frozen')
    review = tmp_path / 'review.json'
    review.write_text(json.dumps({'proceed_holdout': True}))
    config = SimpleNamespace(model='fake', base_url='https://example.test/v1', request_options=lambda: {})
    args = SimpleNamespace(qids=['12'], arms=['minimal', 'entry_v1'], repeats=2)
    lock = dict(phase='holdout', qids=['12'], arms=list(args.arms), repeats=2,
                model=config.model, base_url=config.base_url, request_options={},
                dataset_sha256=digest(dataset), excluded_qids=['13'],
                source_sha256={'prompt.txt': digest(prompt)}, development_review='review.json',
                development_review_sha256=digest(review))
    if change == 'prompt': prompt.write_text('changed')
    if change == 'model': config.model = 'changed'
    if change == 'qid': args.qids = ['13']
    if change == 'decision': review.write_text(json.dumps({'proceed_holdout': False}))
    if change == 'overlap': lock['excluded_qids'] = ['12']
    if change == 'none':
        validate_lock(lock, tmp_path, config, args)
    else:
        with pytest.raises(ValueError):
            validate_lock(lock, tmp_path, config, args)
