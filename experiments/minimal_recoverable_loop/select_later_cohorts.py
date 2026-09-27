"""Freeze historical source IDs for gated future stages; no judgments/calls."""
from .common import *
from .select_bank import RECENT

def main():
    recovery=[]
    path=ROOT/'experiments/frontier_generation/bank/CHECKPOINT_BANK.json'
    for r in read(path):
        if r['qid'] in ('546','1094'):
            recovery.append({'qid':r['qid'],'checkpoint_id':r['checkpoint_id'],'path':rel(path),'sha256':sha(path),
                             'state_sha256':r['state_sha256'],'history_sha256':r['history_sha256'],
                             'provenance':r['provenance'],'historical_origin_disclosure':r['state_origin']})
    for tag,qid in [('F08','228'),('F13','637'),('F14','843'),('F10','971')]:
        paths=sorted((ROOT/RECENT/tag).glob('S[0-9][0-9].json'))
        nonempty=[p for p in paths if read(p)['state']['claims']]
        selected=[nonempty[0],nonempty[-1]]
        for p in dict.fromkeys(selected):
            r=read(p)
            recovery.append({'qid':qid,'checkpoint_id':r['state_id'],'path':rel(p),'sha256':sha(p),
                             'historical_origin_disclosure':'Actual uncleaned historical Writer state. Grounding eligibility must be reviewed before E2; not automatically trusted C.'})
    write(P/'e0_reference/RECOVERY_COHORT.json',{'qids':['546','1094','228','637','843','971'],'sources':recovery,
          'selection':'For546/1094 use the existing START and AFTER2 archival checkpoint IDs; for228/637/843/971 use earliest and latest nonempty-C natural snapshot in the named frozen trajectories. IDs chosen before new calls.',
          'planned_perturbations':['P0 normal','P1 historical natural bad H, only where available','P2 two same-family NoGain in trace, explicitly synthetic control history','P3 observed promising but uninspected source'],
          'prerequisites':'E1 PASS; prefix-only grounding/perturbation reference review; do not silently clean inherited C; unsupported inherited states are explicit ineligible cells, not false-C injections; then actual requests freeze and fresh consent.',
          'requests_materialized':0,'status':'SOURCE_IDS_FROZEN; E2 references and requests not yet constructed'})
    qs={r['case_id']:r['qid'] for r in read(ROOT/'experiments/belief_need_budget_locality_repair/acquisition/QUESTIONS.json')}
    candidates=[]
    for tag,qid in qs.items():
        for p in sorted((ROOT/RECENT/tag).glob('S[0-9][0-9].json')):
            candidates.append({'qid':qid,'checkpoint_id':tag+'_'+p.stem,'path':rel(p),'sha256':sha(p)})
    # Round-robin avoids concentrating all40 snapshots in a small set of questions.
    by_q={q:sorted([r for r in candidates if r['qid']==q],key=lambda r:digest(['minimal-loop-closure-v1',r['checkpoint_id']])) for q in sorted({r['qid'] for r in candidates},key=int)}
    selected=[]
    for i in range(max(map(len,by_q.values()))):
        for q,rs in by_q.items():
            if i<len(rs):selected.append(rs[i])
    selected=selected[:40]
    write(P/'e0_reference/CLOSURE_COHORT.json',{'selection':'Census57 real S00+ natural snapshots in16 frozen acquisition trajectories; within qid SHA256(seed,checkpoint_id), then round-robin numeric qid; first40. No final answers/old verdicts used.',
           'seed':'minimal-loop-closure-v1','eligible_snapshots':len(candidates),'selected':selected,
           'selected_count':len(selected),'selected_qids':len({r['qid'] for r in selected}),
           'semantic_strata':'UNREVIEWED. Complete/near-complete/H-only/relation-trap counts must be established from prefix before E3 calls; no complete labels fabricated.',
           'shortfall_policy':'If no eligible complete state exists, complete-state READY recall is null and E3 cannot pass under strict gates. Do not manufacture evidence or silently supplement after observing outputs.',
           'status':'SOURCE_IDS_FROZEN; E3 grounding/coverage references and requests not yet constructed'})
    live={'historical_qids':['546','1094','228','637','843','971'],'normal_and_perturbed_each':True,
          'historical_trajectories':12,'fresh_qids':read(P/'e0_reference/FRESH_SELECTION.json')['selected_qids'],
          'fresh_trajectories':10,'max_acquisition_actions_per_trajectory':8,'max_closure_audits_per_trajectory':2,
          'max_total_acquisition_actions':176,'max_Search_calls':176,'max_closure_calls':44,
          'retrieval_k':5,'max_first_wave_preview_observations':880,
          'perturbations':{'546':'first action forced to global SEARCH; historical route frozen before E4 calls',
                           '1094':'inject historical failed route in Trace, not C',
                           '228':'plausible historical wrong H candidate, not C',
                           '637':'historical candidate uncertainty in H, not C',
                           '843':'historical unproductive acquisition route in Trace',
                           '971':'historical book-only candidate belief in H without asserting later article'},
          'status':'DESIGN_AND_QIDS_FROZEN_ONLY; exact adaptive requests not known or authorized',
          'authorization_constraint':'TASK47 requires exact payloads and fresh consent. Each dependent live wave must be materialized/committed/hashed and separately authorized; a budget ceiling alone does not authorize unknown future requests.'}
    write(P/'e0_reference/LIVE_COHORT.json',live)
    cases={
        'Euler biography':['S038'],'book-only to article':['S035','S036'],
        'q637 clinical':['S041','S042','S043'],'memo date to letter':['S052','S053'],
        'patient nationality to report country':['S041','S042'],
        'teammate same-country':['S049','S051'],'alma-mater to building':['S032','S034'],
        'DLC nation qualifier':['S045','S047'],'Ding2019 marriage':['S034'],
        'ambiguous pronoun or source binding':['S026','S053'],
    }
    write(P/'regression/semantic_safety_cases/INDEX.json',{'cases':cases,'uses':['Writer admission fidelity','future Closure relation coverage'],
          'not_actor_runtime_fields':True,'source_bank':'../../e0_reference/ADMISSION_BANK.json',
          'admission_reference':'../../e0_reference/ADMISSION_REFERENCE.json','Closure_reference_status':'pending E1/E2 PASS; never inferred from Admission labels'})
    print('Frozen recovery',len(recovery),'prefixes; closure',len(selected),'natural snapshots; fresh',len(live['fresh_qids']))

if __name__=='__main__': main()
