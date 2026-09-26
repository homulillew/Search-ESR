"""Freeze runtime-only Beliefs and evaluator-only labels without model calls."""
import copy,hashlib,json,collections
from pathlib import Path
from curation import DEV,RESERVE,CHALLENGE,GAPS,FULL,CONTRADICTED,PARTIAL_NOTES,STRATA
P=Path(__file__).resolve().parents[1];R=P.parents[1]
def rd(p):return json.loads(p.read_text())
def dg(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def wr(n,x):(P/'bank'/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
I={r['inventory_id']:r for r in rd(P/'bank/INVENTORY.json')};constraints={r['qid']:r for r in rd(R/'experiments/bcplus_verification/constraint_audit/CONSTRAINTS.json')}
cases=[];labels={};byhash={};members=collections.defaultdict(list)
def add(qid,belief,role,oracle,origins,strata=None,source_id=None):
    h=dg(belief)
    if h in byhash:
        cid=byhash[h];members[role].append(cid);labels[cid]['roles'].append(role);return cid
    cid=f'N{len(cases)+1:03}';byhash[h]=cid
    cases.append({'case_id':cid,**belief})
    coverage=[]
    for u in constraints[qid]['units']:
        if u['classification'] not in ['HARD_CONSTRAINT','REQUESTED_RELATION']:continue
        i=int(u['id'][-2:]);hard=u['classification']=='HARD_CONSTRAINT'
        status='unresolved_or_partial';refs=[]
        if hard and i in FULL.get(source_id,{}):status='supported';refs=FULL[source_id][i]
        if hard and i in CONTRADICTED.get(source_id,{}):status='contradicted';refs=CONTRADICTED[source_id][i]
        if not hard:status='target_binding_unresolved; candidate_answer_value_may_already_be_known'
        coverage.append({**u,'status':status,'claim_refs':refs})
    labels[cid]={'case_id':cid,'qid':qid,'belief_sha256':h,'source_inventory_id':source_id,'origins':origins,'roles':[role],'strata':strata or ([] if belief['hypothesis'] else ['U1']),'oracle_gap':oracle,'coverage':coverage,'valid_gap_set':'Any genuinely unestablished material local relation/component from the question or safe alternative discovery after contradiction. Not a unique reference Need. Already stated facts are excluded, even inside partly covered hard conditions.','scope_notes':PARTIAL_NOTES[qid],'strict_unresolved':True,'reviewer':'Single Codex reviewer'}
    members[role].append(cid);return cid
for role,ids in [('development',DEV),('challenge',CHALLENGE)]:
 for sid in ids:
    r=I[sid];add(r['qid'],{k:r[k] for k in ['question','claims','hypothesis']},role,GAPS[sid],r['origins'],STRATA[sid],sid)
pairs=rd(P/'bank/DELTA_PAIRS_DRAFT.json')
for r in pairs:
    sid=r['base_inventory_id'];base=I[sid]
    for side in ['A','B']:
        oracle=r.get('oracle_'+side,GAPS.get(sid))
        assert oracle
        c=add(r['qid'],r[side],'delta_'+r['kind'],oracle,base['origins'],source_id=sid)
        r[side+'_case']=c
    assert r['A']['question']==r['B']['question']
    if r['kind']=='coverage':assert r['A']['hypothesis']==r['B']['hypothesis'] and r['B']['claims']==r['A']['claims']+[r['real_added_claim']]
    else:assert r['A']['claims']==r['B']['claims'] and r['A']['hypothesis']==''
# Carry unchanged Claim coverage through controlled projections, then add only
# coverage actually established by the newly appended Claim.
extra={'DC03':{6:[11]},'DC07':{4:[4],5:[1,3,4]},'DC08':{1:[5],2:[5]},'DC09':{7:[6,8]},'DC10':{3:[1]},'DC11':{3:[1]},'DC12':{6:[1]}}
for r in pairs:
 for side in ['A','B']:
  lab=labels[r[side+'_case']]
  lab.setdefault('projection_provenance',[]).append({'pair_id':r['pair_id'],'side':side,'base':r['base_inventory_id'],'construction':r['construction']})
 for u in labels[r['B_case']]['coverage']:
  index=int(u['id'][-2:])
  if u['classification']=='HARD_CONSTRAINT' and index in extra.get(r['pair_id'],{}):
   u['status']='supported';u['claim_refs']=extra[r['pair_id']][index]
# Correct local Claim coverage is part of each delta label; no target gap leaks
# into normal runtime. P4 uses one canonical oracle per unique Belief.
for r in pairs:
 for side in ['A','B']:
    labels[r[side+'_case']].setdefault('delta_memberships',[]).append({'pair_id':r['pair_id'],'side':side,'kind':r['kind'],'target_gap':r['target_gap'],'target_covered':side=='B' if r['kind']=='coverage' else None})
used_qc={dg({'question':r['question'],'claims':r['claims']}) for r in cases};reserve=[]
for sid in RESERVE:
 r=I[sid]
 if r['state_group'] in used_qc:continue
 assert not r['named_challenge_qid'] and not r['prior_frontier_or_progress_exposed']
 reserve.append({'inventory_id':sid,'qid':r['qid'],'belief_sha256':r['belief_hash'],'state_group':r['state_group'],'status':'unconsumed reserve; support/coverage review required before any future confirmation call','origins':r['origins']})
wr('RUNTIME_INPUTS.json',cases);wr('LABELS.json',list(labels.values()));wr('MEMBERSHIP.json',dict(members));wr('DELTA_PAIRS.json',pairs);wr('CONFIRMATION_RESERVE.json',reserve)
summary={'development_states':len(DEV),'development_qids':len({I[x]['qid'] for x in DEV}),'challenge_states':len(CHALLENGE),'coverage_pairs':12,'hypothesis_pairs':4,'unique_runtime_beliefs':len(cases),'reserve_groups':len(reserve),'reserve_qids':len({r['qid'] for r in reserve}),'development_strata':dict(collections.Counter(s for x in DEV for s in STRATA[x])),'historical_QCH_inventory':437,'fresh_qids_available':5,'development_target_10_qids_met':False,'primary_target_12_qids_met':False,'confirmation_minimum_8_qids_met':False,'genuine_one_gap_development':1,'one_gap_target_8_met':False,'all_selected_claim_occurrences_have_archived_source_hash':True,'selection_basis':'Fixed strata, provenance and archived Claim coverage before calls; no new model output. Shared questions across states and reserve are disclosed. Canonical single sample per unique Belief/path even if diagnostic memberships overlap.','closure_controls':{'natural_full_coverage':0,'assembled_full_coverage':0,'status':'No certified full-coverage controls available; strict missing chain/role/date relations remain. Not a universal proof no such state exists outside audited material.'}}
wr('SELECTION.json',summary)
wr('CLOSURE_CONTROLS.json',[])
wr('PRECALL_CORRECTIONS.json',[{'historical_file':'experiments/bcplus_verification/constraint_audit/RESOLVED_REAUDIT.json','issue':'Some old Galacta rows treat one offline player as full exclusive single-player coverage.','new_bank_rule':'186_H04 remains partial unless no-multiplayer/exclusivity is stated in Claims. The complete observed source is not supplied to this Need model, so unretained no-multiplayer evidence cannot fill the Claim gap.','timing':'Before any current model call; no historical label edited.','impact':'Keeps Galacta challenge more strictly unresolved; report original-label sensitivity for any Need which exclusively tests multiplayer.'}])
print(json.dumps(summary,indent=2))
