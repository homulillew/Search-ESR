"""Zero-network preparation of the exact first paid batch."""
import re
from .common import *

def literal_prompt(section):
    task=(P/'TASK.md').read_text()
    body=task.split(f'# {section}. ',1)[1].split('\n---',1)[0]
    blocks=re.findall(r'```text\n(.*?)\n```',body,re.S)
    return next(b.strip()+'\n' for b in blocks if b.startswith('You '))

def main():
    write(P/'prompts/verifier.txt',literal_prompt(10))
    write(P/'prompts/auditor.txt',literal_prompt(11))
    previous=read(ROOT/'experiments/contextual_subtraction_qualification/CONFIG.json')
    names=['provider','endpoint','base_url','model','temperature','max_retries','max_workers','replicates',
           'max_tokens_policy','response_format','timeout_seconds','timeout_semantics','halt_http_statuses',
           'credential_source','tool_calls','horizon','cache_metric','resumption_policy']
    cfg={k:previous[k] for k in names}
    cfg.update(authorization_policy='TASK33: each concrete paid batch requires new explicit user authorization after committed requests and hash freeze; no previous authorization reused.',
               planned_verifier_calls=96,possible_conditional_auditor_calls=[0,96],
               phase_boundary='E1V first. Then materialize only valid SUPPORTED auditor requests, commit/hash and request fresh exact-count authorization for E1A. E1 gate cannot pass before required audits finish.')
    write(P/'CONFIG.json',cfg)
    write(P/'GATES.json',{
        'E1':{'support_precision_min':0.97,'support_recall_min':0.90,
              'Euler_false_support_count_max':0,'book_only_false_support_count_max':0,
              'false_full_risk_count_max':0,'q637_clinical_recall_min':0.90,
              'Ding_marriage_recall_min':1.0,'schema_validity_min':0.95},
        'E2_B1':{'target_under_inheritance_max':0.03,'safe_package_min':0.90,
                 'exact_target_set_min':0.80,'sibling_over_inheritance_max':0.10,
                 'unitization_insufficient_max':0.10,'schema_validity_min':0.95},
        'E3':{'support_precision_min':0.95,'support_recall_min':0.85,
              'gold_minus_predicted_precision_max':0.05,'gold_minus_predicted_recall_max':0.10,
              'Euler_false_support_count_max':0,'false_full_risk_count_max':0},
        'E4':{'false_shrink_max':0.03,'false_FULLY_SUPPORTED_count_max':0,
              'residual_recall_min':0.90,'governing_relation_retention_min':0.95,
              'state_discrimination_min':0.85,'schema_validity_min':0.95},
        'sequencing':'Every preceding gate must pass. Every paid batch additionally requires new explicit authorization. Stop after E4 even if all pass.',
        'null_denominator':'not estimable and cannot pass a required metric',
        'primary_scope':'all48 fixed certificates, both replicates; ambiguity exclusions descriptive only'})
    from .inputs import verifier_schedule
    jobs=verifier_schedule()
    assert len(jobs)==96
    write(P/'e1_gold_support/VERIFIER_SCHEDULE.json',jobs)
    chars=sum(len(m['content']) for j in jobs for m in j['request']['messages'])
    write(P/'CALL_ESTIMATE.json',{
        'first_paid_batch':'E1V','provider':cfg['provider'],'model':cfg['model'],
        'actual_verifier_requests':len(jobs),'certificates':48,'replicates':2,
        'message_characters':chars,'rough_input_token_range_by_characters':[chars//5,chars//3],
        'estimate_limit':'Character heuristic only; output tokens and money not known. max_tokens omitted as in the inherited backend config.',
        'auditor_requests_materialized':0,'conditional_auditor_range':[0,96],
        'E1_total_possible_calls':[96,192],
        'auditor_exact_count_rule':'One request per schema-valid SUPPORTED verifier response, using only its cited Claims. Count known after E1V, before E1A authorization.',
        'current_authorized_calls':0,'current_actual_calls':0,'currency':None,
        'later_stage_requests_materialized':0,'maximum_concurrency':8,'retries':0})
    for stage in ('e2_boundary_recovery','e3_predicted_support','e4_residual_view'):
        write(P/stage/'STATUS.json',{'status':'NOT_ENTERED','actual_requests':0,'authorization':None,'condition':'preceding stage PASS, complete stage references/requests frozen, then new explicit authorization'})
    print(read(P/'CALL_ESTIMATE.json'))

if __name__=='__main__':
    main()
