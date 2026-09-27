"""Verifier-only descriptive scores; does not impersonate completed E1 audits."""
from collections import Counter
from .common import *
from .inputs import references
from .run import OUT, jobs, load_rows
from .score import aggregate, witness_sufficient


def summarize(rows, refs):
    records=[{'verifier':r,'auditor':None} for r in rows]
    raw=aggregate(records,refs)
    answer={k:raw[k] for k in (
        'planned','positive_slots','negative_slots',
        'verifier_only_witness_precision','verifier_only_witness_recall',
        'verifier_only_verdict_precision','verifier_only_verdict_recall',
        'raw_unsafe_support_count','required_audits')}
    tp=raw['verifier_only_witness_recall']['numerator']
    fp=raw['raw_unsafe_support_count']
    index={(r['certificate_id'],r['replicate']):r for r in rows}
    pairs=[(index[cid,1],index[cid,2]) for cid in {r['certificate_id'] for r in rows} if (cid,1) in index and (cid,2) in index]
    agree=sum(a['valid_output'] and b['valid_output'] and a['output']['verdict']==b['output']['verdict'] for a,b in pairs)
    answer.update(TP=tp,FP=fp,missed_positive=raw['positive_slots']-tp,
                  schema_validity=metric(sum(r['valid_output'] for r in rows),len(rows)),
                  verdict_counts=dict(Counter(r['output']['verdict'] if r['valid_output'] else 'FAILED' for r in rows)),
                  raw_verdict_replicate_stability=metric(agree,len(pairs)))
    return answer


def main():
    committed(OUT/'verifier/ACCOUNTING.json')
    rows=load_rows('verifier')
    refs=references()
    lookup={j['id']:j for j in jobs('verifier')}
    ledger=[]
    for r in rows:
        ref=refs[r['certificate_id']]
        output=r['output']
        yes=r['valid_output'] and output['verdict']=='SUPPORTED'
        gold_yes=ref['gold_support']=='SUPPORTED'
        correct_witness=witness_sufficient(ref,output)
        ledger.append({'id':r['id'],'certificate_id':r['certificate_id'],
                       'qid':r['qid'],'replicate':r['replicate'],
                       'gold':ref['gold_support'],'verifier_output':output,
                       'valid_output':r['valid_output'],
                       'correct_supported_witness':bool(yes and gold_yes and correct_witness),
                       'false_support':bool(yes and not (gold_yes and correct_witness)),
                       'false_open':bool(r['valid_output'] and output['verdict']=='OPEN' and gold_yes),
                       'ambiguity_reason':ref['ambiguity_reason']})
    primary=summarize(rows,refs)
    critical={}
    for name,ids in {
        'Euler':['A15_CAND1'],'book_only':['A13_CAND1'],
        'clinical':['A17_CAND1','A17_CAND2','A17_CAND3'],
        'Ding_marriage':['A07_CAND1'],
        'DLC_nation':['A20_CAND5','A20_CAND6'],
        'DLC_technology':['A20_CAND2'],
        'generic_SPS':['A16_CAND1'],'nationality_report_country':['A17_CAND4'],
        'memo_letter':['A23_CAND1'],'teammates':['A22_CAND1'],
        'alma_mater_building':['A06_CAND1'],
        'champion_binding':['A21_CAND3']}.items():
        critical[name]=summarize([r for r in rows if r['certificate_id'] in ids],refs)
    result={
        'status':'E1V_COMPLETE_E1A_NOT_RUN', 'primary':primary,
        'E1_final_gate_status':'PENDING_REQUIRED_AUDITOR_OUTCOMES',
        'E1_PASS':None,'E2_authorized':False,
        'gate_reachability':{
            'can_meet_frozen_recall_gate':False,
            'maximum_final_recall':primary['verifier_only_witness_recall'],
            'maximum_final_clinical_recall':critical['clinical']['verifier_only_witness_recall'],
            'proof':'Frozen auditor is rejection-only. It cannot resurrect any Verifier OPEN or change its cited witness. Final TP is a subset of the32 existing true supports; six clinical slots are all OPEN.',
            'not_a_completed_auditor_result':True},
        'critical_cases':critical,
        'by_replicate':{str(rep):summarize([r for r in rows if r['replicate']==rep],refs) for rep in (1,2)},
        'by_qid':{qid:summarize([r for r in rows if r['qid']==qid],refs) for qid in sorted({r['qid'] for r in rows})},
        'predeclared_ambiguous_exclusion_descriptive':summarize([r for r in rows if not refs[r['certificate_id']]['ambiguity_reason']],refs),
        'actual_distinct_verifier_payloads':len({j['request_sha256'] for j in lookup.values()}),
        'auditor_requests':len(jobs('auditor')),
        'auditor_actual_calls':0,'auditor_rescue':None,'auditor_introduced_false_open':None,
        'qualified_support_precision':None,'qualified_support_recall':None,
        'false_full_risk_after_audit':None,
        'ledger':ledger}
    assert result['auditor_requests']==primary['required_audits']==35
    write(OUT/'VERIFIER_INTERIM_METRICS.json',result)
    errors=[r for r in ledger if r['false_support'] or r['false_open']]
    packets=[]
    for error in errors:
        payload=json.loads(lookup[error['id']]['request']['messages'][1]['content'])
        packets.append({**error,'actual_input':payload})
    write(OUT/'VERIFIER_ERROR_PACKETS.json',packets)
    print({'verifier_only':primary,'critical_clinical':critical['clinical'],
           'distinct_payloads':result['actual_distinct_verifier_payloads'],
           'sensitivity':result['predeclared_ambiguous_exclusion_descriptive']})


if __name__=='__main__':
    main()
