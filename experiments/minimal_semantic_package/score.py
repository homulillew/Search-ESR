"""Frozen E1 certificate and witness scoring. No voting or model repair."""
from .common import *

def witness_sufficient(reference, output):
    selected=set(output.get('supporting_claim_ids',[])) if output else set()
    return any(set(s)<=selected for s in reference['minimal_sufficient_claim_sets'])

def combine(verifier, auditor):
    if not verifier.get('valid_output'):
        return {'qualified':False,'valid_chain':False,'status':'FAILED_VERIFIER'}
    if verifier['output']['verdict']!='SUPPORTED':
        return {'qualified':False,'valid_chain':True,'status':'OPEN_VERIFIER'}
    if auditor is None or not auditor.get('valid_output'):
        return {'qualified':False,'valid_chain':False,'status':'FAILED_OR_PENDING_AUDITOR'}
    passed=not auditor['output']['uncovered_target_unit_ids']
    return {'qualified':passed,'valid_chain':True,'status':'QUALIFIED_SUPPORT' if passed else 'OPEN_AUDITOR'}

def aggregate(records, refs):
    tp=fp=positive=negative=valid=raw_tp=raw_fp=raw_supported=raw_verdict_tp=raw_verdict_fp=0
    false_open=rescue=auditor_harm=raw_unsafe=audit_valid=audit_required=risk_fp=risk_n=0
    euler_fp=euler_n=book_fp=book_n=clinical_tp=clinical_n=ding_tp=ding_n=0
    rows=[]
    for record in records:
        v,a=record['verifier'],record.get('auditor')
        ref=refs[v['certificate_id']]
        yes=ref['gold_support']=='SUPPORTED'
        good_witness=witness_sufficient(ref,v.get('output'))
        raw_yes=v.get('valid_output') and v['output']['verdict']=='SUPPORTED'
        final=combine(v,a)
        good=final['qualified'] and yes and good_witness
        bad=final['qualified'] and not (yes and good_witness)
        positive+=yes;negative+=not yes;tp+=good;fp+=bad;valid+=final['valid_chain']
        raw_supported+=raw_yes;raw_tp+=raw_yes and yes and good_witness;raw_fp+=raw_yes and not (yes and good_witness)
        raw_verdict_tp+=raw_yes and yes;raw_verdict_fp+=raw_yes and not yes
        false_open+=yes and final['valid_chain'] and not final['qualified']
        raw_unsafe+=raw_yes and not (yes and good_witness)
        rescue+=raw_yes and not (yes and good_witness) and final['status']=='OPEN_AUDITOR'
        auditor_harm+=raw_yes and yes and good_witness and final['status']=='OPEN_AUDITOR'
        audit_required+=raw_yes;audit_valid+=raw_yes and a is not None and a.get('valid_output',False)
        if ref['false_full_risk']:risk_n+=1;risk_fp+=bad
        if 'Euler' in ref['case_tags']:euler_n+=1;euler_fp+=bad
        if ref['certificate_id']=='A13_CAND1':book_n+=1;book_fp+=bad
        if 'q637_clinical' in ref['case_tags']:clinical_n+=1;clinical_tp+=good
        if ref['certificate_id']=='A07_CAND1':ding_n+=1;ding_tp+=good
        rows.append({'id':v['id'],'certificate_id':v['certificate_id'],'replicate':v['replicate'],
                     'gold':ref['gold_support'],**final,'witness_sufficient':good_witness,
                     'false_support':bool(bad),'missed_positive':bool(yes and not good),
                     'verifier_output':v.get('output'),'auditor_output':a.get('output') if a else None})
    pairs=[]
    indexed={(r['certificate_id'],r['replicate']):r for r in rows}
    for cid in {r['certificate_id'] for r in rows}:
        if (cid,1) in indexed and (cid,2) in indexed:pairs.append((indexed[cid,1],indexed[cid,2]))
    stability=sum(a['valid_chain'] and b['valid_chain'] and a['qualified']==b['qualified'] for a,b in pairs)
    return {'planned':len(records),'positive_slots':positive,'negative_slots':negative,
            'TP':tp,'FP':fp,'missed_positives':positive-tp,
            'support_precision':metric(tp,tp+fp),'support_recall':metric(tp,positive),
            'false_support_count':fp,'false_open_count':false_open,
            'false_open_rate':metric(false_open,positive),'schema_validity':metric(valid,len(records)),
            'failed_or_pending_chains':len(records)-valid,
            'Euler_false_support_count':euler_fp,'Euler_denominator':euler_n,
            'book_only_false_support_count':book_fp,'book_only_denominator':book_n,
            'false_full_risk_count':risk_fp,'false_full_risk_rate':metric(risk_fp,risk_n),
            'q637_clinical_recall':metric(clinical_tp,clinical_n),'Ding_marriage_recall':metric(ding_tp,ding_n),
            'replicate_stability':metric(stability,len(pairs)),
            'verifier_only_witness_precision':metric(raw_tp,raw_tp+raw_fp),
            'verifier_only_witness_recall':metric(raw_tp,positive),
            'verifier_only_verdict_precision':metric(raw_verdict_tp,raw_verdict_tp+raw_verdict_fp),
            'verifier_only_verdict_recall':metric(raw_verdict_tp,positive),
            'raw_unsafe_support_count':raw_unsafe,'uncovered_audit_rescue':metric(rescue,raw_unsafe),
            'auditor_introduced_false_open':auditor_harm,
            'required_audits':audit_required,'auditor_schema_validity':metric(audit_valid,audit_required),
            'ledger':rows}

def gate(metrics, complete):
    checks={}
    for name,threshold in read(P/'GATES.json')['E1'].items():
        key,op=name.rsplit('_',1)
        value=metrics[key]
        if isinstance(value,dict):value=value['value']
        checks[name]=value is not None and (value>=threshold if op=='min' else value<=threshold)
    return {'status':'PASS' if complete and all(checks.values()) else 'FAIL' if complete else 'PENDING',
            'batch_complete':complete,'checks':checks,'E1_PASS':complete and all(checks.values()),
            'E2_authorized':False}

def results():
    from .run import OUT,jobs,load_rows
    from .inputs import references,auditor_job
    committed(OUT/'verifier/ACCOUNTING.json')
    refs=references();verifiers=load_rows('verifier')
    needed=[auditor_job(j,v) for j,v in zip(jobs('verifier'),verifiers)]
    needed=[j for j in needed if j is not None]
    audits={}
    if needed:
        committed(OUT/'auditor/ACCOUNTING.json')
        assert jobs('auditor')==needed
        audits={r['id']:r for r in load_rows('auditor')}
    for v in verifiers:committed(OUT/'verifier/calls'/f"{v['id']}.result.json")
    for a in audits.values():committed(OUT/'auditor/calls'/f"{a['id']}.result.json")
    records=[{'verifier':v,'auditor':audits.get(v['id'].replace('V_','A_',1))} for v in verifiers]
    main=aggregate(records,refs)
    sensitivity=aggregate([r for r in records if not refs[r['verifier']['certificate_id']]['ambiguity_reason']],refs)
    return {'primary':main,'gate':gate(main,complete=True),
            'ambiguous_reference_exclusion_descriptive_only':sensitivity,
            'by_replicate':{str(rep):aggregate([r for r in records if r['verifier']['replicate']==rep],refs) for rep in (1,2)}}

if __name__=='__main__':
    scored=results()
    write(P/'e1_gold_support/METRICS.json',scored)
    print(json.dumps(scored['gate'],indent=2))
