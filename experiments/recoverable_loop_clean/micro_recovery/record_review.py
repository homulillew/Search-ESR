"""Record Codex single-reviewer judgments after reading exact prefix/returned windows.

No model requests. Labels are explicit reviewer decisions, not string-based truth scores.
"""
from collections import Counter
from .common import *


def record():
    review=BASE/'analysis'
    paths=sorted((review/'review_packets').glob('*.json'))
    good_claims={
      ('R2_Q228__rep1','C3'):('The dated 2019-12-11 raw window explicitly says Ding is married but without children.','Useful local attribute; does not bind him to the university/gift.'),
      ('R2_Q637__rep1','C3'):('W4 explicitly states the mutation, absent in parents, and FOP diagnosis.','Useful candidate-local diagnosis; no matching of both report conditions.'),
      ('R2_Q637__rep2','C3'):('W4 explicitly confirms the D4 patient’s mutation and FOP diagnosis.','Useful candidate-local diagnosis; no matching of both report conditions.'),
      ('R3_Q538__rep1','C2'):('Actual source title binds the table of contents to Practical Mechanics for Boys; XIV lists Telegraph and Telephone.','Useful book candidate/contents evidence; illustration count and reference constraints remain open.'),
      ('R3_Q922__rep1','C3'):('Expanded W6 identifies the author/recipient and explicitly mentions regaining North Transylvania.','Direct local support for the asked region, while date/accession/nickname binding remains unresolved.'),
    }
    action_judgments={
      ('R2_Q228__rep1',1):(True,False,'reasonable_test',None,False,'Tentatively tests Ding. Global search returned new unrelated previews, no direct new Ding support.'),
      ('R2_Q228__rep1',2):(True,False,'reasonable_test',True,False,'Find in the already discovered Ding article fits family-status verification; returns old W4, newly converted into C.'),
      ('R2_Q228__rep2',1):(False,True,'reasonable_source_with_bad_premise',True,False,'The relative clause asserts Kwon had no children by2019 without C support. D2 profile is a reasonable place to check philanthropy; returned old W2 does not verify that premise.'),
      ('R2_Q637__rep1',1):(True,False,'reasonable_test',True,False,'Tentative alternative case report is suitable to investigate; local diagnosis appears, but queried half-year symptom binding is absent in returned old W4.'),
      ('R2_Q637__rep2',1):(True,False,'reasonable_test',True,False,'Candidate report inspection is appropriate; old W4 establishes diagnosis, not all first-case qualifiers.'),
      ('R3_Q538__rep1',2):(True,False,'weak_source_choice',False,False,'Gap targets missing book identity, but D8 concerns seventeenth-century scientific imaging, not the required telephone/telegraph book.'),
      ('R3_Q538__rep1',3):(True,False,'reasonable_exploration',None,True,'Moves from the irrelevant essay to discovery. Named book query is a hypothesis; returned W13 supports a useful new book candidate.'),
      ('R3_Q538__rep2',2):(True,False,'reasonable_exploration',None,False,'Tests an explicit possible conjunction of named references, rather than asserting it; returned previews do not establish the book relation.'),
      ('R3_Q922__rep1',2):(True,False,'reasonable_test',True,True,'Opening adjacent text around the cover/letter tail reaches the actual letter and its region statement.'),
      ('R3_Q922__rep2',2):(True,False,'reasonable_test',True,False,'Correct document type and relation query, but Find returns old W4 tail/footnotes, omitting the region. Local window failure, not unsupported C.'),
    }
    claims=[];actions=[];closures=[];hs=[];trajectories=[]
    for path in paths:
        p=read(path);tid=p['trajectory_id']
        initial_line=json.loads((BASE/'run001/trajectories'/tid/'trace.jsonl').open().readline())
        known_w={w['window_ref'] for w in initial_line['evidence']};known_d={w['doc_ref'] for w in initial_line['evidence']}
        known_c={c['claim_id'] for c in p['initial_state']['C']};known_r={r['requirement_id'] for r in p['initial_state']['R']}
        for s in p['steps']:
            decision=s['outcome']['decision'];slot=s['slot'];observed=[];new_docs=set();new_refs=set()
            for e in s['events']:
                if e['kind']=='tool_observation':
                    observed=e['windows'];new_refs={w['window_ref'] for w in observed}-known_w
                    new_docs={w['doc_ref'] for w in observed}-known_d
                if e['kind']=='claim_committed':
                    c=e['claim'];known_c.add(c['claim_id']);support,usefulness=good_claims[(tid,c['claim_id'])]
                    claims.append({'trajectory_id':tid,'slot':slot,'claim':c,'source_supported':True,'false_high_risk_claim':False,
                        'gap_useful':True,'global_task_complete':False,'uses_new_raw_window':any(r in new_refs for r in c['evidence_refs']),
                        'support_reason':support,'scope_reason':usefulness})
                if e['kind']=='closure_feedback':
                    closures.append({'trajectory_id':tid,'slot':slot,'status':e['status'],'correct_veto':True,'false_ready':False,
                        'reason':'Seed evidence supports only local biography/memo facts; listed material book/letter conditions are still unsupported. Local C is retained.',
                        'next_actor_acquired':any(z['slot']>slot and z['outcome']['decision']['decision']=='acquire' for z in p['steps'])})
            known_w.update(w['window_ref'] for w in observed);known_d.update(w['doc_ref'] for w in observed)
            for e in s['events']:
                if e['kind']=='role_response' and e.get('role')=='hypotheses':
                    value=e['output'];value=json.loads(value) if isinstance(value,str) else value
                    bad=[]
                    for u in value['updates']:
                        for ref in u.get('basis_refs',[]):
                            if ref not in known_w:
                                category='known_claim_id' if ref in known_c else 'known_document_id' if ref in known_d else 'known_requirement_id' if ref in known_r else 'unknown_reference'
                                bad.append({'ref':ref,'category':category})
                    bad_sources=[d for d in value['useful_source_refs'] if d not in new_docs]
                    hs.append({'trajectory_id':tid,'slot':slot,'basis_namespace_invalid':bool(bad),'invalid_refs':bad,
                        'source_nomination_not_new':bad_sources,'committed':any(v['kind']=='hypotheses_updated' for v in s['events']),
                        'reason':'Runtime accepts only observed W evidence refs; schema uses generic strings and exposes C/R/D elsewhere. No mapping/repair applied.'})
            if decision['decision']=='acquire':
                forced=tid.startswith('R1_') and slot==1
                label=(True,False,'frozen_suboptimal_repeat',None,False,'Repeated prefix Search returns existing-document metadata only; no next Actor after H failure.') if forced else action_judgments[(tid,slot)]
                usable,hardening,suitability,compatible,novel_useful,reason=label
                actions.append({'trajectory_id':tid,'slot':slot,'forced_intervention':forced,'action':decision['action'],
                    'one_gap_usable':usable,'premise_hardening':hardening,'action_valid':True,'execution_success':True,
                    'semantic_suitability':suitability,'source_compatible':compatible,'new_raw_window_refs':sorted(new_refs),
                    'new_useful_raw_evidence':novel_useful,'new_useful_claim':any(c['trajectory_id']==tid and c['slot']==slot for c in claims),
                    'reason':reason})
        trajectories.append({'trajectory_id':tid,'outcome':'truncated_by_H_reference_contract',
            'new_claims':[c['claim']['claim_id'] for c in claims if c['trajectory_id']==tid],
            'new_useful_raw_evidence':any(a['new_useful_raw_evidence'] for a in actions if a['trajectory_id']==tid),
            'complete_recovery_demonstrated':False})
    model_actions=[a for a in actions if not a['forced_intervention']]
    inspections=[a for a in actions if a['action']['tool'] in ['find','open']]
    metrics={'trajectories':12,'truncated_by_H_contract':12,'max_horizon_completed_without_failure':0,
      'model_acquisition_valid':{'numerator':len(model_actions),'denominator':len(model_actions)},
      'forced_acquisitions_valid':{'numerator':4,'denominator':4},
      'one_gap_explicit_premise_hardening':{'numerator':sum(a['premise_hardening'] for a in model_actions),'denominator':len(model_actions)},
      'new_claims_supported':{'numerator':len(claims),'denominator':len(claims)},
      'new_claims_from_previously_observed_window':sum(not c['uses_new_raw_window'] for c in claims),
      'new_claims_from_new_window':sum(c['uses_new_raw_window'] for c in claims),
      'closure_veto_and_next_actor':{'numerator':sum(c['correct_veto'] and c['next_actor_acquired'] for c in closures),'denominator':len(closures)},
      'R3_some_new_useful_evidence_within_horizon':{'numerator':2,'denominator':4},
      'false_C_observed':0,'false_READY_observed':0,'READY_decisions':0,'final_answers':0,
      'H_proposals_namespace_invalid':{'numerator':sum(h['basis_namespace_invalid'] for h in hs),'denominator':len(hs)},
      'H_proposals_bad_new_source_nominations':sum(bool(h['source_nomination_not_new']) for h in hs),
      'H_committed_semantic_changes':0,
      'R1_after_intervention_actor_opportunities':0,'two_consecutive_acquisition_NoGain_followed_by_Actor_opportunities':0,
      'single_acquisition_NoGain_followed_by_Actor':{'opportunities':2,'changed_tool_scope':2,'not_two_NoGain_recovery_test':True},
      'inspection_compatibility_descriptive':{'numerator':sum(a['source_compatible'] is True for a in inspections),'denominator':len(inspections)},
      'inspection_new_useful_raw_evidence_descriptive':{'numerator':sum(a['new_useful_raw_evidence'] for a in inspections),'denominator':len(inspections)},
      'warning':'All are descriptive, unblinded single-reviewer labels on six paired-replicate cells. Interface truncation prevents a mechanism pass/fail inference.'}
    save(review/'SEMANTIC_REVIEW.json',{'reviewer':'Codex single reviewer, no paid evaluator','scope':'all18 decisions, all5 accepted claims, all4 closures, all14 H proposals; exact source-relative windows read',
        'packets_sha256':{str(p.relative_to(ROOT)):sha(p) for p in paths},'claims':claims,'actions':actions,'closures':closures,'H_contract_audit':hs,'trajectories':trajectories,'metrics':metrics,
        'additional_semantic_risks':[
          {'trajectory':'R1_Q546__rep1','kind':'uncommitted_H_full_match_invention','reason':'No new observation, yet Tom Ford is presented with the complete desired sequence. Basis is empty; this is not an established fact.'},
          {'trajectory':'R3_Q538__rep2','kind':'uncommitted_H_overinterpretation','reason':'Observed D12 Euler-paper/D14 inventor material does not establish the proposed American Boy’s Handy Book illustration/rust/reference conjunction.'},
          {'trajectory':'R2_Q637__rep1/rep2','kind':'premature_global_H_rejection_proposal','reason':'D4 has FOP diagnosis, but returned window does not bind it to both question reports; rejecting global SPS is stronger than the verified local C.'},
          {'trajectory':'R3_Q922__rep1','kind':'uncommitted_timing_relation_substitution','reason':'The H proposal maps the accession-to-letter timing condition onto1944 realignment-to-memo timing. Neither relation substitution is established.'}]})
    print(json.dumps(metrics,indent=2))

if __name__=='__main__':record()
