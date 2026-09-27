"""Descriptive decomposition only; the frozen score.py determines the E1 gate."""
from collections import Counter
from .common import *
from .run import OUT,rows,accounting

def calculate():
    m=read(OUT/'METRICS.json');committed(OUT/'METRICS.json')
    primary=m['primary'];judgments={r['candidate_id']:r for r in read(OUT/'CANDIDATE_REVIEW.json')['records']}
    ledger={r['candidate_id']:r for r in read(OUT/'CANDIDATE_LEDGER.json')}
    accepted=primary['admitted_ledger'];ids={r['candidate_id'] for r in accepted}
    cases={};failures=[]
    for r in accepted:
        cid=r['candidate_id'];c=ledger[cid];j=judgments[cid]
        d=cases.setdefault(c['source_id'],{'admitted':0,'strict_true':0,'whole_observation_true':0,'excerpt_context_loss':0,'whole_observation_unsupported':0})
        d['admitted']+=1;d['strict_true']+=j['claim_entailed_by_excerpt'];d['whole_observation_true']+=j['claim_entailed_by_observation']
        if not j['claim_entailed_by_excerpt']:
            kind='excerpt_context_loss' if j['claim_entailed_by_observation'] else 'whole_observation_unsupported'
            d[kind]+=1
            failures.append({'candidate_id':cid,'source_id':c['source_id'],'kind':kind,
                'claim':c['candidate']['statement'],'actual_excerpt':c['candidate']['supporting_excerpt'],
                'pre_admission_review_reason':j['reason'],'tags':j['error_tags']})
    whole_bad=[x for x in failures if x['kind']=='whole_observation_unsupported']
    quote_only=[x for x in failures if x['kind']=='excerpt_context_loss']
    # This group was explicitly disclosed before Admission in PRE_ADMISSION_REVIEW_NOTES.
    borderline={f'W_S045_r2_C{i}' for i in range(1,11)}
    remaining=ids-borderline
    writer_rows=rows('writer');admission_rows=rows('admission')
    # Primary annotations are unchanged; this is not an alternative gate.
    diag={
        'primary_gate':m['gate'],'descriptive_only':True,
        'no_gate_override':True,
        'review_qualification':'Single task-familiar reviewer. Candidate labels and proof sets committed before Admission. No statistical independence of candidates, windows or replicates is claimed.',
        'accepted_whole_observation_fidelity':metric(len(ids)-len(whole_bad),len(ids)),
        'accepted_quote_context_losses':len(quote_only),
        'accepted_whole_observation_unsupported':len(whole_bad),
        'strict_false_admission_tags':dict(Counter(t for x in failures for t in x['tags'])),
        'borderline_dev_diary_subset':{'pre_disclosed_candidates':sorted(borderline),'admitted':sorted(ids&borderline),
            'strict_precision_without_subset':metric(sum(judgments[c]['claim_entailed_by_excerpt'] for c in remaining),len(remaining)),
            'whole_observation_fidelity_without_subset':metric(sum(judgments[c]['claim_entailed_by_observation'] for c in remaining),len(remaining)),
            'reason':'The visible window has entries but not a dev-diary heading; the reference used a loose diary descriptor. Exclusion is a sensitivity description, not relabeling or gate rescue.'},
        'source_counts':cases,'false_admission_cases':failures,
        'mechanical_rejects':[{'candidate_id':c['candidate_id'],'reason':c['mechanical_reject']} for c in ledger.values() if not c['exact_excerpt_valid']],
        'writer_full_observation_unsupported':sum(not j['claim_entailed_by_observation'] for j in judgments.values()),
        'writer_invalid_whole_observation_that_did_not_enter_C':sum(not j['claim_entailed_by_observation'] and cid not in ids for cid,j in judgments.items()),
        'raw_writer_correct_candidates_rejected_by_verifier':primary['verifier_false_rejects'],
        'claims_per_writer_output':{'total_candidates':len(ledger),'planned_Writer_calls':len(writer_rows),
            'empty_valid_outputs':sum(r['valid_output'] and not r['output']['candidate_claims'] for r in writer_rows)},
        'study_accounting':accounting(writer_rows+admission_rows),
        'H_to_C':'Not experimentally measured in E1: H excluded from both components. QR candidate-hardening proxy is measured separately.',
        'new_retrieval_calls':0,
    }
    return diag

if __name__=='__main__':
    d=calculate();write(OUT/'DIAGNOSTICS.json',d)
    print(json.dumps({k:d[k] for k in ['accepted_whole_observation_fidelity','accepted_quote_context_losses','accepted_whole_observation_unsupported','strict_false_admission_tags','study_accounting']},indent=2))
