"""Post-execution diagnostics only; frozen decisions and Gold stay unchanged."""
from collections import Counter
from .common import *
from .run import OUT, jobs, load_rows, accounting
from .inputs import references
from .score import results, aggregate, witness_sufficient


def main():
    scored=results()
    assert scored==results()==read(OUT/'METRICS.json')
    refs=references()
    verifiers=load_rows('verifier')
    auditors=load_rows('auditor')
    by_a={r['id']:r for r in auditors}
    aj={j['id']:j for j in jobs('auditor')}
    vj={j['id']:j for j in jobs('verifier')}
    records=[{'verifier':v,'auditor':by_a.get(v['id'].replace('V_','A_',1))} for v in verifiers]
    review=[]
    for item in records:
        v,a=item['verifier'],item['auditor']
        ref=refs[v['certificate_id']]
        witness=witness_sufficient(ref,v.get('output'))
        verifier_accepted=v['valid_output'] and v['output']['verdict']=='SUPPORTED'
        if a is None:
            category='verifier_false_open' if ref['gold_support']=='SUPPORTED' and v['valid_output'] else 'verifier_reject' if v['valid_output'] else 'verifier_failure'
        elif not a['valid_output']:
            category='auditor_failure'
        elif a['output']['uncovered_target_unit_ids']:
            category='audit_introduced_false_open' if ref['gold_support']=='SUPPORTED' and witness else 'audit_rescue'
        else:
            category='retained_true_support' if ref['gold_support']=='SUPPORTED' and witness else 'retained_false_support'
        payload=json.loads((aj[a['id']] if a else vj[v['id']])['request']['messages'][1]['content'])
        review.append({'verifier_id':v['id'],'auditor_id':a['id'] if a else None,
                      'certificate_id':v['certificate_id'],'replicate':v['replicate'],
                      'gold_support':ref['gold_support'],'frozen_reference_reason':ref['gold_reason'],
                      'ambiguity_reason':ref['ambiguity_reason'],
                      'category':category,'witness_sufficient':witness,
                      'verifier_accepted':bool(verifier_accepted),
                      'actual_last_call_input':payload,
                      'verifier_output':v.get('output'),
                      'auditor_output':a.get('output') if a else None})
    data={
        'status':'descriptive diagnostics after complete frozen E1 score',
        'categories':dict(Counter(x['category'] for x in review)),
        'by_qid':{qid:aggregate([r for r in records if r['verifier']['qid']==qid],refs) for qid in sorted({r['qid'] for r in verifiers})},
        'by_case_tag':{tag:aggregate([r for r in records if tag in refs[r['verifier']['certificate_id']]['case_tags']],refs) for tag in sorted({t for r in refs.values() for t in r['case_tags']})},
        'review_records':review,
        'score_replay_identical':True,
        'score_sha256':digest(scored)}
    write(P/'analysis/FINAL_DIAGNOSTICS.json',data)
    phases={p:read(OUT/p/'ACCOUNTING.json') for p in ('verifier','auditor')}
    combined=accounting(verifiers+auditors)
    combined.update(phase_active_wall_seconds={p:a['wall_seconds'] for p,a in phases.items()},
                    sum_active_batch_wall_seconds=sum(a['wall_seconds'] for a in phases.values()),
                    wall_scope='sum of the two actual batch active durations; excludes preparation and time awaiting user approval',
                    peak_concurrency=max(a['peak_concurrency'] for a in phases.values()),
                    actual_verifier_calls=len(verifiers),actual_auditor_calls=len(auditors),
                    E2_calls=0,E3_calls=0,E4_calls=0,retrieval_calls=0,retries=0)
    write(P/'analysis/TOTAL_ACCOUNTING.json',combined)
    print('categories',data['categories'])
    print('accounting',combined)


if __name__=='__main__':
    main()
