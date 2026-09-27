"""Read-only preparation audit; importing this module cannot call a provider."""
import json
from .prepare import BASE, OLD, P, git, read, sha
from .run import audit_prepared

def audit():
    report = audit_prepared()
    reviews = read(P / 'e0_w_reaudit/REVIEW.json')
    old_review = read(OLD / 'need/confirmation/REVIEW.json')
    old_bank = read(OLD / 'bank/CONFIRMATION.json')
    expected = {s['state_id'] for s in old_bank if old_review['B5__' + s['state_id']]['codes'] == ['W']}
    if {r['state_id'] for r in reviews} != expected or len(reviews) != 5:
        raise ValueError('E0 not exactly the five primary historical W')
    for r in reviews:
        if r['old_label'] != 'W' or r['old_review'] != old_review['B5__' + r['state_id']]:
            raise ValueError('Historical label overwritten')
    if sum(r['new_label'] == 'W_multiquery' for r in reviews) != 3:
        raise ValueError('Reaudit count mismatch')
    exclusions = read(P / 'analysis/FRESHNESS_EXCLUSIONS.json')
    if not {s['qid'] for s in read(P / 'e1_need/BANK.json')} <= set(exclusions['excluded_qids']):
        raise ValueError('Exposed current cases missing from exclusions')
    if sha(P / 'prompts/b0.txt') != sha(OLD / 'need/prompts/B5.txt'):
        raise ValueError('B0 is not byte-identical')
    # Assert committed and uncommitted tracked changes stay in this new experiment.
    changed = git('diff', '--name-only', BASE).splitlines()
    outside = [p for p in changed if not p.startswith('experiments/minimal_need_multiquery/')]
    if outside:
        raise ValueError('Changes outside experiment: ' + repr(outside))
    report.update(e0_exact_primary_five=True, E0_W_independent=2, E0_W_multiquery=3,
                  exposure_excluded_qids=len(exclusions['excluded_qids']), exposure_scanned_files=exclusions['scanned_files'],
                  historical_B0_prompt_byte_identical=True, changes_outside_new_experiment=0,
                  paid_run_exists=(P / 'e1_need/development_run').exists(),
                  status='PREPARED_FOR_REAL_RUN' if not (P / 'e1_need/development_run').exists() else 'RUN_EXISTS_CHECK_RUN_RECORDS')
    return report

if __name__ == '__main__':
    print(json.dumps(audit(), ensure_ascii=False, indent=2))
