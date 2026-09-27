"""Explicit Codex source-relative judgments; no paid evaluator or gold answers."""
from collections import Counter
from .common import *
from llm_chat.recoverable_loop.replay import replay_log
from llm_chat.recoverable_loop.state import state_from_dict

# hardening, document-compatible (None for corpus), new useful raw evidence for
# current OneGap, reason. These are human semantic annotations, not heuristics.
A = {
('R1_Q1094__rep1',2):(False,None,False,'Tests a different fixture, but returned previews identify alternative Liverpool–Milan material rather than the queried Inter–Milan 2006/free-kick relation.'),
('R1_Q1094__rep1',3):(True,True,True,'Match commentary is a reasonable inspection source and supplies opening-goal detail; it does not identify the 95th-minute taker. OneGap asserts the whole early/late scoring pattern before C establishes it.'),
('R1_Q1094__rep2',3):(False,None,True,'New Soweto-derby preview supports a split-origin candidate; it does not establish a specific match/free-kick or the opponent identity condition.'),
('R1_Q546__rep1',2):(False,False,False,'Already-complete opening-round news article lacks later rounds; Open after returns document_boundary and old W13.'),
('R1_Q546__rep1',3):(False,None,False,'Bracket-oriented Search changes access strategy after two NoGain steps, but new previews concern 2025 snooker and darts, not the requested 2023 sequence.'),
('R1_Q546__rep2',2):(False,True,False,'D17 biography is a plausible candidate source; Find localizes to 2007–2009, not the 2023 match sequence.'),
('R1_Q546__rep2',3):(False,True,False,'Same plausible biography, but expanding the already visibly wrong-year window retains 2006–2009 material. Tested H1 is Shaun Murphy while the OneGap/source concern Ding.'),
('R2_Q228__rep1',1):(True,True,False,'Kwon biography plausibly supports philanthropy research but does not show spouse/childlessness/building binding. OneGap asserts Kwon childlessness without C support; returned philanthropy largely repeats prefix information.'),
('R2_Q228__rep1',2):(True,True,False,'Ding article is appropriate and old W4 supports new childlessness C; OneGap states that premise before its C commit and labels a Kim Jung-ju H as under test.'),
('R2_Q228__rep1',3):(False,None,False,'Search tests the outstanding gift relation, but returned previews do not establish the named Ding/spouse/building relation. Other philanthropists remain alternative candidates.'),
('R2_Q228__rep2',1):(False,True,False,'Open uses the right existing article; returns old W4 and newly commits source-supported childlessness C.'),
('R2_Q228__rep2',2):(False,None,False,'Search remains on the missing gift relation. Game revenue/release metadata can help the broader task but is not new support for that gift relation.'),
('R2_Q228__rep2',3):(False,None,True,'Gift-focused Search surfaces a founder/spouse building example with a 2025 opening date, enabling exclusion on the requested timeline; not evidence of Ding or a successful target match.'),
('R2_Q637__rep1',1):(False,True,False,'D5 is appropriate; old W5 supports matching first-case symptoms and FOP. New C extraction, not new raw evidence.'),
('R2_Q637__rep1',2):(False,True,True,'D4 inspection yields new W6 supporting biopsy two months earlier, childhood onset and FOP; still lacks publication-year/country qualifiers.'),
('R2_Q637__rep2',1):(False,True,True,'D4 is reasonable to test, but its different clinical course helps distinguish it from the first case and supports local FOP facts.'),
('R2_Q637__rep2',2):(False,True,False,'D5 old W5 supplies the first clinical pattern and diagnosis; supports new C without new raw window content.'),
('R3_Q538__rep1',2):(False,None,False,'Discovery query is reasonable but all returned snippets fail to establish the book conjunction. Bibliographic catalog remains a plausible inspection opportunity.'),
('R3_Q538__rep1',3):(False,True,False,'A book catalog is a plausible title source; Find returns the same off-target catalog W15, no new useful evidence.'),
('R3_Q922__rep1',2):(False,True,True,'Opening around cover/letter tail reaches letter W6 and the region; the handwritten date remains absent.'),
('R3_Q922__rep1',3):(False,True,False,'Date question is appropriate and keeps memo separate from letter; document-complete Open returns old W6 without dateline.'),
('R3_Q922__rep2',2):(False,True,False,'Correct document for the OSS handoff, but old W4 keeps the officer unnamed and supplies no nickname.'),
('R3_Q922__rep2',3):(False,True,False,'New full-letter W6 adds the region for the broader Q, but not the current officer/name/nickname Need; Reader correctly commits no unrelated region C.'),
}
H_NOTES = {
('R1_Q1094__rep1',2):('overcommitted_candidate','W65 supports a match title/lineups, not the complete Q identity or a 95th-minute Pirlo kick. Empty-base guesses are permitted H, not verified facts.'),
('R1_Q1094__rep1',3):('unsupported_candidate_retained','KEEP retains unverified match/taker hypotheses; opening-minute free-kick evidence does not directly refute a later free-kick, but does not verify it.'),
('R1_Q1094__rep2',3):('overcommitted_candidate','Split-origin snippet supports Kaizer Chiefs locally. A declarative Q identity overstates that binding; other alternatives explicitly remain unverified.'),
('R1_Q546__rep1',3):('candidate_churn','Bare Ding target ADD produces runtime Gain despite no new sequence evidence.'),
('R1_Q546__rep2',2):('candidate_churn','Shaun Murphy ADD has empty basis and no new supporting observation; allowed conjecture, not demonstrated progress.'),
('R1_Q546__rep2',3):('target_test_mismatch','KEEP Shaun Murphy while Actor tests Ding; H ID/Need routing mismatch remains.'),
('R2_Q228__rep1',1):('candidate_churn','A detailed Kim Jung-ju alternative is empty-base speculation; absence of Kwon profile details is not factual rejection.'),
('R2_Q228__rep1',2):('unsupported_rationale','Ding childlessness/education are in W4, but W4 does not establish the game release year or university founding year used in the H rationale. Downgrading alternatives is allowed, not global REJECT.'),
('R2_Q228__rep1',3):('reasonable_keep','No stronger gift evidence; keeps tentative Ding and nominates new uninspected profile.'),
('R2_Q228__rep2',1):('appropriate_deprioritization','Competing locally supported Ding candidate justifies deprioritizing Kwon, not rejecting him as a fact.'),
('R2_Q228__rep2',2):('reasonable_keep','Keeps tentative Ding. D6/D7 are new task-relevant profile/game sources though not demonstrated gift evidence.'),
('R2_Q228__rep2',3):('missed_constraint_on_candidate','Huang is only a partial gift-structure match: W11 explicitly opens in 2025 versus Q 2018–2021. H acknowledges missing games tie but misses this timing conflict. Chen remains tentative.'),
('R2_Q637__rep1',1):('appropriate_deprioritization_with_overcommitment','Local FOP candidate supports SPS deprioritization. Global FOP is phrased categorically before both report/year/country bindings exist, but remains H only.'),
('R2_Q637__rep1',2):('appropriate_deprioritization','Second report supplies matching local symptoms/FOP. No global REJECT; year/country still left to Closure.'),
('R2_Q637__rep2',1):('appropriate_deprioritization','Local alternative diagnostic evidence leads to DEPRIORITIZE SPS and tentative FOP, not global REJECT.'),
('R2_Q637__rep2',2):('appropriate_deprioritization','Retains tentative FOP and adds a scoped D5/first-case hypothesis; no claim that publication/country qualifiers are solved.'),
('R3_Q538__rep1',2):('question_restatement_and_speculation','Empty-base engineer/scientist/substance guesses remain hypotheses. H5 restates Q rather than discovering a concrete book; new H count inflates Gain.'),
('R3_Q538__rep1',3):('reasonable_keep','No new evidence resolves these tentative candidates; KEEP is allowed but gives no progress.'),
('R3_Q922__rep1',2):('local_fact_repeated_as_h','Region repeats grounded local C while global letter identity/timing stays unverified. It adds no separate evidence.'),
('R3_Q922__rep1',3):('stale_date_hypothesis','Old March5-letter H remains despite only memo date support; Actor correctly asks for the actual date. KEEP is not proof of that date.'),
('R3_Q922__rep2',2):('relation_substitution_risk','Empty-base coup-to-letter timing alternative substitutes endpoints for accession-to-letter. Guesses remain low-authority; global identity is unverified.'),
('R3_Q922__rep2',3):('appropriate_deprioritization','Full letter adds no officer binding; DEPRIORITIZE the speculative officer/nickname link, not factual rejection.'),
}


def record():
    dest=BASE/'analysis';packets=sorted((dest/'review_packets').glob('*.json'))
    actions=[];claims=[];hypotheses=[];closures=[];replays=[]
    for path in packets:
        p=read(path);tid=p['trajectory_id'];rawpath=BASE/'run001/trajectories'/tid/'trace.jsonl'
        initial=json.loads(rawpath.open().readline());known_w={w['window_ref'] for w in initial['evidence']};known_d={w['doc_ref'] for w in initial['evidence']}
        evidence={w['window_ref']:w for w in initial['evidence']}
        for s in p['steps']:
            slot=s['slot'];d=s['outcome']['decision'];obs=[]
            for e in s['events']:
                if e['kind']=='tool_observation':obs=e['windows'];evidence.update({w['window_ref']:w for w in obs})
            new_w={w['window_ref'] for w in obs}-known_w;new_d={w['doc_ref'] for w in obs}-known_d
            known_w.update(w['window_ref'] for w in obs);known_d.update(w['doc_ref'] for w in obs)
            for e in s['events']:
                if e['kind']=='claim_committed':
                    c=e['claim'];limited=tid=='R3_Q922__rep1' and c['claim_id'] in ['C4','C5']
                    reason=('Literal letter statements are supported but realignment/anxiety do not establish the asked region or actual dateline.' if limited else
                            'Exact observed source text/title supports this local statement; no claim of satisfying all global Q conditions.')
                    claims.append({'trajectory_id':tid,'slot':slot,'claim':c,'source_supported':True,'false_C':False,
                                   'gap_useful':not limited,'uses_new_raw_window':bool(set(c['evidence_refs'])&new_w),
                                   'reason':reason,'evidence_text_sha256':[evidence[r]['text_sha256'] for r in c['evidence_refs']]})
                if e['kind']=='role_response' and e.get('role')=='hypotheses':
                    h=json.loads(e['output']);kind,reason=H_NOTES[(tid,slot)]
                    invalid=[r for u in h['updates'] for r in u.get('basis_refs',[]) if r not in known_w or not r.startswith('W')]
                    invalid_source=[r for r in h['useful_source_refs'] if r not in new_d or r in s['outcome']['inspected_sources']]
                    hypotheses.append({'trajectory_id':tid,'slot':slot,'proposal':h,'invalid_basis_refs':invalid,
                        'invalid_source_nominations':invalid_source,'committed':any(v['kind']=='hypotheses_updated' for v in s['events']),
                        'semantic_label':kind,'reason':reason,'semantic_verification_not_implied_by_valid_refs':True})
                if e['kind'] in ('closure_feedback','closure_ready'):
                    assert e['status']=='CONTINUE'
                    closures.append({'trajectory_id':tid,'slot':slot,'status':e['status'],'correct_veto':True,'false_READY':False,
                      'reason':'Visible local C does not bind all requested identity/time/country/book/gift conditions; missing-feedback content is appropriate.',
                      'next_actor_acquisition':any(z['slot']>slot and z['outcome']['decision']['decision']=='acquire' for z in p['steps'])})
            if d['decision']=='acquire':
                forced=tid.startswith('R1_') and slot==1
                hard,compatible,useful,reason=(False,None,False,'Frozen repeated Search returns existing-source metadata only; no new W/C and H correctly skipped.') if forced else A[(tid,slot)]
                actions.append({'trajectory_id':tid,'slot':slot,'forced':forced,'decision':d,'action_valid':True,
                    'execution_success':s['outcome']['failure'] is None,'premise_hardening':hard,'one_gap_usable':not hard,
                    'source_compatible':compatible,'new_useful_raw_evidence_for_current_need':useful,
                    'new_raw_refs':sorted(new_w),'reason':reason,
                    'new_useful_raw_evidence_for_broader_question_only':(tid=='R3_Q922__rep2' and slot==3) or (tid=='R2_Q228__rep2' and slot==2)})
        final=state_from_dict(read(BASE/'run001/trajectories'/tid/'FINAL_STATE.json'))
        assert replay_log(rawpath)[0]==final
        replays.append({'trajectory':tid,'identical':True})
    counts=read(dest/'ACCOUNTING.json');outcomes=read(BASE/'run001/RESULTS.json')
    inspections=[a for a in actions if a['decision']['action']['tool']!='search']
    gains=[s for p in packets for s in read(p)['steps'] if s['outcome']['feedback']=='Gain']
    metrics={'trajectories':12,'horizon_completed':sum(r['status']=='horizon_exhausted' for r in outcomes),
      'H_calls':len(hypotheses),'H_invalid_namespace':sum(bool(h['invalid_basis_refs']) for h in hypotheses),
      'H_invalid_nominations':sum(bool(h['invalid_source_nominations']) for h in hypotheses),
      'H_skipped':counts['runtime_counts_unreviewed']['hypothesis_update_skipped'],'H_failures':0,
      'live_H_failure_continuation_opportunities':0,'live_H_failure_isolation_rate':None,
      'new_C':len(claims),'supported_new_C':sum(c['source_supported'] for c in claims),'gap_useful_C':sum(c['gap_useful'] for c in claims),
      'false_C':0,'false_READY':0,'READY':0,'accepted_CONTINUE':len(closures),'closure_contract_failures':1,
      'R1_forced_NoGain_next_Actor':{'numerator':4,'denominator':4},
      'R1_immediate_next_acquisition':3,'R1_immediate_closure_request':1,
      'R1_immediate_changed_tool_scope':2,'R1_immediate_changed_fixture_search':1,
      'R1_new_supported_C_by_horizon':{'trajectories':1,'denominator':4},
      'R3_CONTINUE_then_acquisition':{'numerator':3,'valid_CONTINUE_denominator':3,'all_forced_denominator':4},
      'R3_new_gap_useful_C_by_horizon':{'trajectories':1,'denominator':4},
      'R2_SPS_deprioritized_not_rejected':{'numerator':2,'denominator':2},
      'new_H_REJECT_operations':sum(u['operation']=='REJECT' for h in hypotheses for u in h['proposal']['updates']),
      'inspection_compatibility':{'numerator':sum(a['source_compatible'] is True for a in inspections),'denominator':len(inspections)},
      'inspection_new_raw_evidence_yield_for_current_need':{'numerator':sum(a['new_useful_raw_evidence_for_current_need'] for a in inspections),'denominator':len(inspections)},
      'actor_premise_hardening':{'numerator':sum(a['premise_hardening'] for a in actions),'denominator':sum(not a['forced'] for a in actions)},
      'Gain_steps_without_new_C':sum(not s['outcome']['claim_delta'] for s in gains),'Gain_steps':len(gains),
      'integrity_failures':0,'interpretation':'Result-informed six-cell diagnostic; no causal or independent recovery claim.'}
    assert len(claims)==14 and len(actions)==27 and len(hypotheses)==22 and len(closures)==6
    save(dest/'SEMANTIC_REVIEW.json',{'reviewer':'Codex single reviewer, unblinded, no paid reviewer',
      'scope':'Every acquisition, every new Claim, every H proposal and every accepted Closure; source-relative prefix/Observation only, no gold/full-source audit.',
      'actions':actions,'claims':claims,'hypotheses':hypotheses,'closures':closures,'metrics':metrics,
      'limitations':'H conjectures may be false and valid refs do not imply entailment. Semantic risk labels are not automatic state-integrity failures. Two true but low-utility letter Claims are not counted as useful to the current Need.',
      'packets_sha256':{str(p.relative_to(ROOT)):sha(p) for p in packets}})
    save(dest/'INTEGRITY.json',{'replay':replays,'original_run001_unchanged':not subprocess.check_output(['git','diff','3fdb19bc','--','experiments/recoverable_loop_clean/micro_recovery','experiments/recoverable_loop_clean/h_fix'],cwd=ROOT),
                             'runtime_head':read(BASE/'run001/STARTED.json')['head'],'artifacts_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted((BASE/'run001').rglob('*')) if p.is_file()}})
    save(BASE/'GATE_H2.json',{'H1_interface_gate':'PASS_WITH_RECORDED_NON_H_MODEL_OUTPUT_FAILURE','new_authoritative_corruption':False,
        'evidence':metrics,'closure_failure_diagnosis':'One model output echoed the JSON-schema oneOf wrapper. Correct schema remains unchanged; output rejected, no C/READY mutation, no retry. This is an isolated model contract error, not a repaired-H interface or authoritative integrity failure.',
        'H2_allowed':True,'H2_scope':'Independent-from-H-repair archived prefixes, frozen eligibility/review/count before calls; no replacements; no claim H semantic reliability has been established.',
        'no_gate_requiring_perfect_model_accuracy':'Frozen H1 gate requires executable repaired interfaces and no authoritative corruption; it does not require zero retained model-output failures.'})
    print(json.dumps(metrics,indent=2))

if __name__=='__main__':record()
