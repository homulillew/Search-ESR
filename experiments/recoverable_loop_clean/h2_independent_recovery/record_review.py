"""Explicit unblinded Codex source-relative review; no gold or paid reviewer."""
from collections import Counter
from .common import *
from llm_chat.recoverable_loop.replay import replay_log
from llm_chat.recoverable_loop.state import state_from_dict

# Premise hardening, source compatibility (None for Search), new useful RAW
# evidence for this Need. New W identifiers alone do not imply new information.
A={
('R1_Q169',1):(False,None,False,'Forced repeat returns no new observation; an empty-basis song hypothesis alone creates Gain.'),
('R1_Q169',2):(False,None,False,'Search tests the partner/interview/song link. New song/album pages do not verify the interview; Immaterial being a song is insufficient for that relation.'),
('R1_Q169',3):(False,True,False,'Biography is a reasonable place to seek the partner interview, but W18 repeats the partner/bio already in prefix W7 and never supplies that interview.'),
('R1_Q261',1):(False,None,False,'Frozen repeat returns no new observation; H KEEP leaves NoGain.'),
('R1_Q261',2):(False,True,False,'Official publication list is reasonable, but localization remains on 2023/2024 entries rather than the asked 2012–2022 emotion paper.'),
('R1_Q261',3):(False,True,False,'Appropriate PDF; expanded W12 repeats the title/authors already visible in initial W10. New useful C, but no new support for six tables or 13.53 and no new title information.'),
('R1_Q264',1):(False,None,False,'Frozen repeat returns no new observation; H KEEP leaves NoGain.'),
('R1_Q264',2):(False,True,False,'Correct candidate PDF, but generic author query localizes to detector simulations instead of the author list.'),
('R1_Q264',3):(False,True,False,'Open around known detector-simulation text remains far from the author list; source-compatible, unproductive local navigation.'),
('R1_Q601',1):(False,None,False,'Frozen repeat returns no new observation; empty H mechanically skipped.'),
('R1_Q601',2):(True,True,False,'Career-retrospective source is plausible; prefix D1 has no surveyor statement, yet OneGap presupposes a former Blackpool surveyor. Find returns no windows.'),
('R1_Q601',3):(False,None,True,'Changes from unsuccessful local inspection to business-partnership discovery; W7 supplies a new former-footballer/October2012 partnership relation.'),
('R2_Q177',1):(False,True,False,'Relevant 13-signing article is reasonable to inspect, but Find returns complete old W1 without founding/fifteen-trophy binding.'),
('R2_Q177',2):(True,True,False,'Already-complete W1 is reopened with no new content. OneGap calls it the 2023 article although visible header is 2025 and only season2022/23 was verified.'),
('R2_Q177',3):(False,None,True,'Search changes access and yields a local founding-year/country statement. League-title totals still do not establish fifteen trophies or the target season/capital.'),
('R2_Q186',1):(False,None,True,'Search directly resolves the company former-name relation and supplies developed-by/no-multiplayer evidence for the same candidate.'),
('R3_Q435',2):(False,True,False,'Retrospective is a plausible route to the quoted interview. New context does not time-bind 67 to2016; the key sentence was already in W2. The committed C5 overinterprets it.'),
('R3_Q435',3):(False,None,True,'Search obtains new W7 with an explicitly attributed May2017 Forbes listing and65-album statement, a useful alternative temporal lead. No final global identity proof.'),
('R3_Q517',2):(False,True,True,'Biography filmography now explicitly supplies Policeman1 for the2005 film, filling a named Closure gap.'),
('R3_Q517',3):(False,None,True,'New windows support Condon directing and writing Kinsey, one component of the current Need. They do not establish his Fifth Estate connection.'),
('R3_Q633',2):(False,None,False,'Query remains Wilhelmina-focused and returns an unrelated2009/200-page Maria book plus general history/publisher results. No matching book binding.'),
('R3_Q633',3):(False,None,True,'Broadens away from Wilhelmina to defining attributes; new publisher window gives Nwando Achebe/book/February2011/multilingual female king facts.'),
('R3_Q673',2):(False,True,False,'Appropriate biography/critical article; Find localizes to disputed poem attribution rather than birth/husband/beauty-name relations.'),
('R3_Q673',3):(False,True,False,'Expanded window remains on attribution debate. New C repeats Kaul material already in prefix W9; it does not resolve the stated biographical conditions.'),
}
H={
('R1_Q169',1):('question_inspired_speculation','Empty-basis Immaterial guess allowed in H; no evidence Gain.'),
('R1_Q169',2):('speculative_interview_retained','Partner was visible in prefix W7, but the posthumous interview/song link remains a guess. D11 song page is a weak route to an interview.'),
('R1_Q169',3):('speculative_timeline','Empty-basis Helios2005 speculation remains tentative and explicitly leaves the year gap unverified; it must not satisfy the15-year condition.'),
('R1_Q261',1):('reasonable_keep','No new observation to overturn tentative author.'),
('R1_Q261',2):('reasonable_keep','Unproductive list window is not a contradiction.'),
('R1_Q261',3):('scoped_candidate','Actual title/authors/date support a tentative paper candidate; no assertion that13.53/six tables are verified.'),
('R1_Q264',1):('reasonable_keep','No new observation to contradict the tentative paper.'),
('R1_Q264',2):('reasonable_keep','Wrong local window leaves the candidate undecided.'),
('R1_Q264',3):('route_based_deprioritization','Two poor localizations justify lower route priority, not rejection of the paper; no evidence proves H false.'),
('R1_Q601',3):('false_evidence_promotion_in_H','W7 supports professional Chelsea/Brighton career and business partnership, not Premier League youth/academy membership as H says it matches. Other unverified conditions are correctly retained as missing.'),
('R2_Q177',1):('reasonable_keep','Lack of founding details is not a global candidate contradiction.'),
('R2_Q177',2):('weak_candidate_retained','Seven league titles neither verify nor disprove fifteen total trophies. Candidate remains unbound; no global REJECT.'),
('R2_Q177',3):('weak_candidate_retained','New local founding fact is real; no evidence yet binds target season/capital/2023article. KEEP is not confirmation.'),
('R2_Q186',1):('source_discrepancy_retained','Alternative W4 says1993 versus C1/W1 November1992; tentative H preserves this discrepancy without overwriting C. Independent compatible sources support the main1992 claim.'),
('R3_Q435',2):('tentative_interview_lead','H keeps the2016 interview as a plausible May feature. The authoritative error is in C5; H explicitly remains tentative.'),
('R3_Q435',3):('appropriate_alternative_deprioritization','May2017/65 W7 justifies downgrading2016 route and introducing a tentative alternative. This H update does not retract unsupported C5.'),
('R3_Q517',2):('alias_churn','DEPRIORITIZE Peter King and ADD Peter Nzioki changes H ID for the same person already equated in seed C1; not wrong-candidate recovery.'),
('R3_Q517',3):('partial_support_with_overbroad_ref_summary','Condon/Kinsey relation is supported in W3/W4/W6; W5 explicitly gives director but does not separately establish screenwriter. Film-chain inference remains tentative.'),
('R3_Q633',2):('mismatched_source_nomination','W6 supplies Maria/book candidate but explicitly2009/200pages conflicts with target book conditions; D6 nomination is weak. Another book about Maria is not logically excluded.'),
('R3_Q633',3):('false_evidence_promotion_in_H','New book supports a better candidate, so Wilhelmina DEPRIORITIZE is reasonable. W12 does not establish only-one-in-era; H strengthens that condition beyond the observation.'),
('R3_Q673',2):('reasonable_keep','Attribution debate does not directly refute the initial poetess hypothesis.'),
('R3_Q673',3):('reasonable_keep','Extra attribution content is no resolution of the birth/spouse relation; keeping H is not progress.'),
}
C={
('R1_Q261','C2'):(True,True,False,'W12 gives exact title and two authors, already visible in prefix W10. Useful new C extracted from previously available semantic evidence.'),
('R1_Q601','C3'):(True,True,True,'W7 explicitly states professional Chelsea/Brighton career and starting Springer Nicolas with Ryan in October2012; no academy inference in C.'),
('R2_Q177','C2'):(True,False,False,'Old W1 says seven-time NPFL champions; this neither verifies fifteen total trophies nor founding year/country.'),
('R2_Q177','C3'):(True,True,True,'W2 explicitly gives Nigerian club founded1970. Local fact; target identity unproven.'),
('R2_Q177','C4'):(True,False,True,'W5 table supports eight league titles and listed years, including2023–24. Broader historical success clue is helped, but current fifteentrophies/founding gap is not resolved by a differently scoped total.'),
('R2_Q186','C3'):(True,True,True,'W2/W3 explicitly support NightSky former name,1992–October1993 period, and officialFloridaOctober1993 establishment.'),
('R3_Q435','C5'):(False,False,False,'Temporal binding unsupported: retrospective67-album narration adjoins a2016 quotation, but does not establish the count at that interview. W3 adds no binding beyond old W2. Frozen seed review and earlier Closure identified this same gap; not a gold-answer judgment.'),
('R3_Q435','C6'):(True,True,True,'W7 datedJune11,2017 separately reports May2017 Forbes listing and65albums. C retains attribution and does not equate June count with a verified final May feature answer.'),
('R3_Q517','C4'):(True,True,True,'W2 filmography explicitly assigns Policeman1 to PeterNzioki in2005ConstantGardener.'),
('R3_Q633','C3'):(True,True,True,'Observed publisher metadata title/author plus PublishedFebruary2011 support the statement.'),
('R3_Q633','C4'):(True,True,True,'W12 explicitly states AhebiUgbabe, Igbo woman king, exile, languages, and support by Igala kings/British officers for the successive offices. No only-one-in-era inference enters C.'),
('R3_Q673','C2'):(True,False,False,'Literal attributed Kaul statement in W12 already existed in prefix W9. It concerns poem attribution/contemporaryGami, not the asked birth range, poet spouse or earlier beauty-named poetess.'),
}

def record():
    dest=BASE/'analysis';actions=[];claims=[];hypotheses=[];closures=[];replays=[];failures=[]
    for path in sorted((dest/'review_packets').glob('*.json')):
        p=read(path);tid=p['trajectory_id'];cell=tid.split('__')[0]
        rawpath=BASE/'run001/trajectories'/tid/'trace.jsonl';initial=json.loads(rawpath.open().readline())
        evidence={w['window_ref']:w for w in initial['evidence']};known_w=set(evidence);known_d={w['doc_ref'] for w in evidence.values()}
        for s in p['steps']:
            slot=s['slot'];o=s['outcome'];d=o.get('decision') or {};obs=[]
            for e in s['events']:
                if e['kind']=='tool_observation':obs=e['windows'];evidence.update({w['window_ref']:w for w in obs})
            new_w={w['window_ref'] for w in obs}-known_w;new_d={w['doc_ref'] for w in obs}-known_d
            known_w.update(w['window_ref'] for w in obs);known_d.update(w['doc_ref'] for w in obs)
            if o.get('failure'):failures.append({'trajectory_id':tid,'slot':slot,'failure':o['failure'],'classification':'non_H_actor_schema_wrapper','no_retry_or_repair':True})
            for e in s['events']:
                if e['kind']=='claim_committed':
                    c=e['claim'];supported,useful,new_semantic,reason=C[(cell,c['claim_id'])]
                    claims.append({'trajectory_id':tid,'slot':slot,'claim':c,'source_supported':supported,'false_C':not supported,'false_evidence_promotion':not supported,'gap_useful':useful,'uses_new_raw_window':bool(set(c['evidence_refs'])&new_w),'new_semantic_support_vs_prefix':new_semantic,'reason':reason,'evidence_text_sha256':[evidence[r]['text_sha256'] for r in c['evidence_refs']]})
                if e['kind']=='role_response' and e.get('role')=='hypotheses':
                    h=json.loads(e['output']);kind,reason=H[(cell,slot)]
                    invalid=[r for u in h['updates'] for r in u.get('basis_refs',[]) if r not in known_w or not r.startswith('W')]
                    invalid_source=[r for r in h['useful_source_refs'] if r not in new_d or r in o['inspected_sources']]
                    hypotheses.append({'trajectory_id':tid,'slot':slot,'proposal':h,'invalid_basis_refs':invalid,'invalid_source_nominations':invalid_source,'committed':any(v['kind']=='hypotheses_updated' for v in s['events']),'semantic_label':kind,'reason':reason,'semantic_verification_not_implied_by_valid_refs':True})
                if e['kind'] in ('closure_feedback','closure_ready'):
                    e=e.get('result',e)
                    ready=e['status']=='READY'
                    closures.append({'trajectory_id':tid,'slot':slot,'status':e['status'],'correct_veto':None if ready else True,'source_supported_READY':True if ready else None,'false_READY':False,'reason':('C1/W1 binds November1992DOS/shareware/oneplayer; C2/W1 names threecredits/twoPucketts; C3/W2/W3 binds formerNightSky company history; W2 explicitly developed-byAlbinoFrog and no-multiplayer. No H input. Source-supported final, not gold-scored accuracy.' if ready else 'Missing feedback correctly preserves unbound book/identity/time/role/biography conditions in this incomplete prefix.'),'next_actor_acquisition':any(z['slot']>slot and (z['outcome'].get('decision') or {}).get('decision')=='acquire' for z in p['steps'])})
            if d.get('decision')=='acquire':
                hard,compatible,useful,reason=A[(cell,slot)]
                actions.append({'trajectory_id':tid,'slot':slot,'forced':cell.startswith('R1') and slot==1,'decision':d,'action_valid':True,'execution_success':o['failure'] is None,'premise_hardening':hard,'one_gap_usable':not hard,'source_compatible':compatible,'new_useful_raw_evidence_for_current_need':useful,'new_raw_refs':sorted(new_w),'reason':reason})
        final=state_from_dict(read(BASE/'run001/trajectories'/tid/'FINAL_STATE.json'));assert replay_log(rawpath)[0]==final
        replays.append({'trajectory':tid,'identical':True})
    assert len(actions)==len(A)==24 and len(hypotheses)==len(H)==22 and len(claims)==len(C)==12
    assert not any(h['invalid_basis_refs'] or h['invalid_source_nominations'] for h in hypotheses)
    ps=[read(p) for p in sorted((dest/'review_packets').glob('*.json'))];steps=[(p['trajectory_id'],s) for p in ps for s in p['steps']]
    inspections=[a for a in actions if a['decision']['action']['tool']!='search']
    gains=[(tid,s) for tid,s in steps if s['outcome']['feedback']=='Gain']
    results=read(BASE/'run001/RESULTS.json');counts=read(dest/'ACCOUNTING.json')['runtime_counts_unreviewed']
    metric={'trajectories':11,'family_counts':{'R1':4,'R2':3,'R3':4},'statuses':dict(Counter(r['status'] for r in results)),
      'completed_horizon_or_ready':sum(r['status'] in ['horizon_exhausted','ready_finalized'] for r in results),
      'H_calls':22,'H_contract_failures':0,'H_skips':counts['hypothesis_update_skipped'],'live_H_failure_continuation_opportunities':0,'live_H_failure_isolation_rate':None,
      'new_C':len(claims),'source_supported_C':sum(c['source_supported'] for c in claims),'false_or_unsupported_C':sum(c['false_C'] for c in claims),'gap_useful_C':sum(c['gap_useful'] for c in claims),
      'accepted_CONTINUE':sum(c['status']=='CONTINUE' for c in closures),'READY':sum(c['status']=='READY' for c in closures),'false_READY':0,'supported_final_answer':1,'gold_accuracy':'not measured',
      'R1_realized_initial_NoGain':{'numerator':3,'forced_repeats':4},'R1_NoGain_next_Actor_acquisition':{'numerator':3,'denominator':3},'R1_NoGain_immediate_scope_change':{'numerator':3,'denominator':3},'R1_NoGain_then_gap_useful_C_by_horizon':{'numerator':2,'denominator':3},'R1_all_forced_then_gap_useful_C':{'numerator':2,'denominator':4},
      'R2_confirmed_wrong_seed_H':0,'R2_evaluable_wrong_H_recovery_opportunities':0,'R2_wrong_H_recovery':'inconclusive; weak candidate confirmation1, unresolved1, actor format failure1',
      'R3_correct_veto_then_gap_addressing_acquisition':{'numerator':4,'denominator':4},'R3_gap_useful_C_by_horizon':{'numerator':3,'denominator':4},'R3_trajectories_with_authoritative_false_promotion':1,
      'inspection_compatibility':{'numerator':sum(a['source_compatible'] is True for a in inspections),'denominator':len(inspections)},'inspection_new_raw_evidence_yield':{'numerator':sum(a['new_useful_raw_evidence_for_current_need'] for a in inspections),'denominator':len(inspections)},
      'premise_hardening_free_acquisitions':{'numerator':sum(a['premise_hardening'] for a in actions if not a['forced']),'denominator':sum(not a['forced'] for a in actions)},
      'Gain_steps':len(gains),'Gain_without_any_new_C':sum(not any(e['kind']=='claim_committed' for e in s['events']) for _,s in gains),'Gain_without_gap_useful_supported_C':sum(not any(c['trajectory_id']==tid and c['slot']==s['slot'] and c['gap_useful'] and c['source_supported'] for c in claims) for tid,s in gains),
      'mechanical_replay_failures':0,'semantic_integrity_failures':1,'H_REJECT_operations':sum(u['operation']=='REJECT' for h in hypotheses for u in h['proposal']['updates'])}
    save(dest/'SEMANTIC_REVIEW.json',{'reviewer':'Codex single reviewer, unblinded, prefix-relative and source-relative, no gold/future-source adjudication; not an independent panel','actions':actions,'claims':claims,'hypotheses':hypotheses,'closures':closures,'failures':failures,'metrics':metric})
    protected=['experiments/recoverable_loop_clean/micro_recovery','experiments/recoverable_loop_clean/h_fix','llm_chat']
    unchanged=subprocess.check_output(['git','diff','--name-only','3fdb19bc','--',*protected],cwd=ROOT,text=True);assert not unchanged
    artifacts={str(p.relative_to(ROOT)):sha(p) for p in sorted((BASE/'run001').rglob('*')) if p.is_file()}
    save(dest/'INTEGRITY.json',{'replays':replays,'historical_and_runtime_git_diff':unchanged,'artifact_hashes':artifacts,'note':'Mechanical integrity does not certify semantic C truth; C5 temporal promotion is retained.'})
    save(BASE/'GATE.json',{'status':'DO_NOT_EXPAND','reason':'One unsupported temporal relationship admitted to authoritative C by Reader and Grounding; preserved original artifact. H formatting repair succeeded, but clean epistemic recovery not established.','paid_calls':81,'max_retries':0,'further_stage_started':False,'metrics':metric})
    print(json.dumps(metric,indent=2))
if __name__=='__main__':record()
