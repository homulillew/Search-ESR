"""Mechanical state selection and fixed parent routing; no new model outputs."""
from .common import *
def build():
 states={s['case_id']:s for s in read(OLD/'e0_reference/STATES.json')}
 audits={a['case_id']:a for a in read(OLD/'e0_addressability/ADDRESSABILITY.json') if a['skeleton_arm']=='D2'}
 gold={g['case_id']:g for g in read(OLD/'e1_alignment/GOLD_MASKS.json') if g['skeleton_arm']=='A1'}
 primary=sorted(k for k,a in audits.items() if a['status']=='subnode_only');assert len(primary)==11
 # TASK9/10 fixed trajectories take precedence over general parent priority.
 overrides={'G04':'R2','G05':'R2','G06':'R2','G16':'R3','G17':'R3','G18':'R3'}
 # In multi-ID subnode rows, select the node explicitly responsible in the old reason.
 reason_nodes={'G01':'R2','G14':'R4','G15':'R2'}
 controls=['G18'];pairing=[{'control':'G18','reason':'TASK8/10 mandatory trajectory endpoint; parentR3 override, not old fully-supported R5.'}]
 pool=[];excluded=[]
 for cid,a in audits.items():
  if a['status']=='subnode_only' or cid=='G18':continue
  candidates=[r for r in a['requirement_ids'] if gold[cid]['requirements'][r]['status']!=F]
  if candidates:pool.append(cid)
  else:excluded.append({'case_id':cid,'reason':'All historical addressable parent IDs fully supported. Prompt has no completed/STOP branch; exclude from control pool only.'})
 for cid in primary:
  if len(controls)>=8:break
  source=states[cid]
  def rank(k):
   s=states[k];return (s['qid']!=source['qid'],s['type']!=source['type'],bool(s['claims'])!=bool(source['claims']),k)
  match=min((k for k in pool if k not in controls),key=rank);controls.append(match)
  pairing.append({'primary':cid,'control':match,'rank':rank(match),'rule':'lexicographic mismatch(qid,type,Claims-empty), then case_id; without replacement'})
 rows=[];parents=[]
 skeletons=read(OLD/'e0_addressability/RUNTIME_SKELETON_D2.json')
 for cid in sorted(primary+controls):
  state=states[cid];audit=audits[cid]
  eligible=[r for r in audit['requirement_ids'] if gold[cid]['requirements'][r]['status']!=F]
  rid=overrides.get(cid) or reason_nodes.get(cid) or sorted(eligible,key=lambda r:int(r[1:]))[0]
  node=next(n for n in skeletons[state['qid']]['requirements'] if n['requirement_id']==rid)
  status=gold[cid]['requirements'][rid]['status'];assert status!=F
  row={**state,'bank_group':'primary_subnode' if cid in primary else 'control','historical_addressability':audit['status'],
   'parent_requirement_id':rid,'support_stratum':'P' if status=='partially_supported' else 'Z'}
  rows.append(row);parents.append({'case_id':cid,'qid':state['qid'],'parent':node,
   'selection_reason':'Explicit task trajectory parent' if cid in overrides else 'Parent named as coarse node in historical addressability reason' if cid in reason_nodes else 'Lowest numbered non-full node in frozen addressability mapping',
   'historical_requirement_ids':audit['requirement_ids'],'historical_addressability':audit['status'],'gold_parent_status':status})
 return rows,parents,{'primary':primary,'controls':sorted(controls),'control_matches':pairing,'excluded_control_candidates':excluded}

def main():
 assert git('rev-parse','origin/experiment/recoverable-control-equivalence')==BASE
 rows,parents,selection=build()
 write(P/'e0_reference/STATES.json',rows);write(P/'e0_reference/PARENT_REQUIREMENTS.json',parents);write(P/'e0_reference/SELECTION.json',selection)
 files=git('ls-tree','-r','--name-only',BASE,'experiments').splitlines();history={n:sha(ROOT/n) for n in files if (ROOT/n).is_file()}
 write(P/'analysis/HISTORICAL_HASHES.json',history)
 write(P/'e0_reference/SELECTION_RULE.md','''# Mechanical selection rule

All11 historical D2 subnode_only states are primary; no outcome-based filtering. Add8 unique direct/coherent historical states. G18 mandatory first. Exclude optional controls whose original mapped parent IDs are all fully supported, because this residual-only task has no full/STOP output. In ascending primary case order, select unused eligible control minimizing lexicographic mismatch(qid, historical type, Claims empty), then case_id. Stop at8 controls.

Parent priority: task-specific trajectories override general priority (q228 allR2; q637 allR3). For multi-ID subnode audit rows use the ID the historical reason identifies as coarse (G01R2,G14R4,G15R2). Others use the lowest-numbered non-full mapped parent. No new Selection calls. G18 uses R3 rather than old R5 per explicit task; it is an action-sized residual control under current clinical Claims, not evidence that raw R3 is globally fine-grained.

State labels and model packets are inherited read-only. Parent selection predates new residual references and all new model calls. Historical GoldO was available for audit mapping; references below use only current Q/parent/Claims and never future outcomes. E2 accessibility, if reached, will be a separate evaluation-only future-source audit after E1 reference freeze.
''')
 paths=[p for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
 write(P/'SELECTION_FREEZE.json',{'base_head':BASE,'files':{rel(p):sha(p) for p in paths},'new_calls':0})
 print(selection);print('Support strata',[(s['case_id'],s['support_stratum']) for s in rows])
if __name__=='__main__':main()
