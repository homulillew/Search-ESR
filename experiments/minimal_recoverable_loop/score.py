"""Frozen E1 scoring: content judgments are committed before Admission calls."""
from .common import *
from .run import OUT,jobs,rows
from .contracts import TAGS

def covered_slots(proofs, available_ids, field='sufficient_candidate_sets'):
    """One complete pre-reviewed witness set must survive; partial sets do not count."""
    return {(p['replicate'],p['atom_id']) for p in proofs
            if any(set(s)<=available_ids for s in p[field])}

def results():
    ws=rows('writer');ads=rows('admission')
    for phase,rr in [('writer',ws),('admission',ads)]:
        committed(OUT/phase/'ACCOUNTING.json')
        for r in rr:committed(OUT/phase/'calls'/f"{r['id']}.result.json")
    refs=read(P/'e0_reference/ADMISSION_REFERENCE.json')
    ledger=read(OUT/'CANDIDATE_LEDGER.json')
    reviews=read(OUT/'CANDIDATE_REVIEW.json');committed(OUT/'CANDIDATE_REVIEW.json')
    judged={r['candidate_id']:r for r in reviews['records']}
    assert set(judged)=={r['candidate_id'] for r in ledger} and len(judged)==len(ledger)==len(reviews['records'])
    calls={r['candidate_id']:r for r in ads}
    atomsets={r['source_id']:{a['atom_id'] for a in r['acceptable_claim_atoms']} for r in refs}
    expected={(rep,a) for rep in (1,2) for r in refs for a in atomsets[r['source_id']]}
    accepted=[];covered=set();raw_covered=set();fp=highrisk=relation=scope=unsupported=hardening=0
    by_id={c['candidate_id']:c for c in ledger}
    proofs=reviews['atom_support_sets']
    assert {(r['replicate'],r['atom_id']) for r in proofs}==expected and len(proofs)==len(expected)
    for proof in proofs:
        for field,entailed in [('sufficient_candidate_sets','claim_entailed_by_excerpt'),('observation_sufficient_candidate_sets','claim_entailed_by_observation')]:
            assert isinstance(proof[field],list)
            for subset in proof[field]:
                assert isinstance(subset,list) and subset and len(subset)==len(set(subset))
                assert all(cid in by_id and by_id[cid]['replicate']==proof['replicate'] and proof['atom_id'] in atomsets[by_id[cid]['source_id']] and judged[cid][entailed] for cid in subset)
        if proof['observation_sufficient_candidate_sets']:raw_covered.add((proof['replicate'],proof['atom_id']))
    for c in ledger:
        review=judged[c['candidate_id']]
        for k in ('claim_entailed_by_excerpt','claim_entailed_by_observation','high_risk','candidate_hardening','useful'):
            assert type(review[k]) is bool
        assert isinstance(review['reason'],str) and review['reason'].strip()
        assert set(review['matched_atom_ids'])<=atomsets[c['source_id']]
        assert isinstance(review['error_tags'],list) and set(review['error_tags'])<=TAGS
        if not review['claim_entailed_by_excerpt']:
            assert review['error_tags']
            if set(review['error_tags'])-{'other','excerpt_mismatch'} or review['candidate_hardening']:assert review['high_risk']
        row=calls.get(c['candidate_id'])
        admit=c['exact_excerpt_valid'] and row is not None and row['valid_output'] and row['output']['verdict']=='ADMIT'
        if not admit:continue
        good=review['claim_entailed_by_excerpt']
        if good:
            assert review['claim_entailed_by_observation'] and not review['high_risk'] and not review['candidate_hardening'] and not review['error_tags']
        else:
            fp+=1;highrisk+=review['high_risk'];hardening+=review['candidate_hardening']
            relation+=bool(set(review['error_tags'])&{'relation_change','argument_change'})
            scope+=bool(set(review['error_tags'])&{'temporal_scope_expansion','modality_expansion','quantifier_expansion','conditional_scope_expansion'})
            unsupported+=bool(set(review['error_tags'])&{'unsupported_inference','entity_binding_unproven','cross_source_composition'})
        accepted.append({'candidate_id':c['candidate_id'],'entailed':good,'high_risk':review['high_risk'],'tags':review['error_tags'],'matched_atom_ids':review['matched_atom_ids'] if good else []})
    good_ids={r['candidate_id'] for r in accepted if r['entailed']}
    covered=covered_slots(proofs,good_ids)
    eligible_good={c['candidate_id'] for c in ledger if c['exact_excerpt_valid'] and judged[c['candidate_id']]['claim_entailed_by_excerpt']}
    false_reject_ids=[cid for cid in sorted(eligible_good) if cid in calls and calls[cid]['valid_output'] and calls[cid]['output']['verdict']=='REJECT']
    failed_good_ids=[cid for cid in sorted(eligible_good) if cid not in calls or not calls[cid]['valid_output']]
    removed_unsafe=[c['candidate_id'] for c in ledger if not judged[c['candidate_id']]['claim_entailed_by_excerpt'] and c['candidate_id'] not in {a['candidate_id'] for a in accepted}]
    n=len(accepted)
    m={'planned_writer_calls':len(ws),'planned_admission_calls':len(ads),'writer_candidates':len(ledger),
       'admitted_claims':n,'true_admissions':n-fp,'false_admissions':fp,
       'precision':metric(n-fp,n),'recall':metric(len(covered),len(expected)),
       'writer_recall_before_admission':metric(len(raw_covered),len(expected)),
       'writer_observation_fidelity':metric(sum(r['claim_entailed_by_observation'] for r in judged.values()),len(ledger)),
       'writer_excerpt_fidelity':metric(sum(r['claim_entailed_by_excerpt'] for r in judged.values()),len(ledger)),
       'writer_candidate_hardening_count':sum(r['candidate_hardening'] for r in judged.values()),
       'mechanically_rejected_candidates':sum(not c['exact_excerpt_valid'] for c in ledger),
       'verifier_false_rejects':{'count':len(false_reject_ids),'candidate_ids':false_reject_ids},
       'eligible_good_candidates_lost_to_failed_calls':{'count':len(failed_good_ids),'candidate_ids':failed_good_ids},
       'unsafe_writer_candidates_not_admitted':{'count':len(removed_unsafe),'candidate_ids':removed_unsafe,
           'scope':'Includes mechanical rejection, verifier rejection and failed/unsent calls; not all are verifier rescues.'},
       'admitted_useful_claims':sum(a['entailed'] and judged[a['candidate_id']]['useful'] for a in accepted),
       'high_risk_false_admissions':highrisk,'relation_argument_corruption_rate':metric(relation,n),
       'temporal_modality_quantifier_expansion_rate':metric(scope,n),'unsupported_inference_count':unsupported,
       'QR_candidate_hardening_count':hardening,'H_to_C_intervention':'not measured in E1: H structurally excluded; QR-hardening is a proxy, not an H intervention',
       'exact_excerpt_validity':metric(n,n),
       'raw_writer_exact_excerpt_validity':metric(sum(c['exact_excerpt_valid'] for c in ledger),len(ledger)),
       'writer_schema':metric(sum(r['valid_output'] for r in ws),len(ws)),
       'admission_schema':metric(sum(r['valid_output'] for r in ads),len(ads)),
       'covered_reference_slots':sorted(covered),'admitted_ledger':accepted,
       'recall_by_replicate':{str(rep):metric(sum(r==rep for r,a in covered),sum(r==rep for r,a in expected)) for rep in (1,2)}}
    checks={}
    for key,threshold in read(P/'GATES.json')['E1'].items():
        name,op=key.rsplit('_',1);value=m[name]
        if isinstance(value,dict):value=value['value']
        checks[key]=value is not None and (value>=threshold if op=='min' else value<=threshold)
    return {'primary':m,'gate':{'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,
                             'later_stage_authorization':False},'all_failures_retained':True,
            'precision_scope':'Fidelity of entire admitted claim to its actual quoted evidence, including all unlisted but entailed outputs; not exact reference wording.',
            'recall_scope':'Coverage of 56 frozen useful semantic atoms in each of 2 Writer replicates, including empty/failed Writer slots.'}

if __name__=='__main__':
    x=results();write(OUT/'METRICS.json',x);print(json.dumps(x['gate'],indent=2))
