"""Post-execution scoring from explicit reviewer-authored evidence facts.
No production input imports this module. Frozen truth is never rewritten.
"""
import json,hashlib,collections,re
from pathlib import Path
TOP=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
# Initial-state knowledge is manually mapped from the literal frozen Claims.
def seed_tags(cid):
 t=int(cid[1:3]);post=cid.endswith('POST');tags=set()
 if t in [1,2,3,4,5,6,7,8,9,10] and post:
  tags.update({1:['ding_opening'],2:['messi95'],3:['peter_name','peter_parents','peter_films'],4:['tuku_death'],5:['y_s4'],6:['rangers13'],7:['heart_exclusion'],8:['hijitus_exclusion'],9:['galacta_specs'],10:['dean_pc','dean_dust']}[t])
 if t in [11,12,18,19]:tags.add('tuku_death')
 if t in [11,12] and post or t==18:tags.update(['tuku_activist','tuku_first','tuku67','wasakara','forbes65','retrospective_separate'])
 if t==19 and post:tags.update(['tuku67','retrospective_separate'])
 if t in [13,14,20]:tags.add('y_s4')
 if t==13 and post or t in [14,20]:tags.update(['y_s3','y_roommate'])
 if t in [14,20]:tags.add('y_s1')
 if t==14 and post or t==20:tags.add('y_seasons')
 if t in [15,16]:tags.add('rangers13')
 if t==15 and post or t==16:tags.add('rangers_table')
 if t==16 and post:tags.add('rangers_founded')
 if t==17:
  tags.update(['peter_name','peter_parents','peter_films'])
  if post:tags.add('peter_police')
 return tags

def score(stage,knowledge=None,closure=None):
 b=TOP/stage;cat={x['evidence_id']:x for x in read(b/'EVIDENCE_CATALOG.json')};pack=read(b/'REVIEW_PACKETS.json');mp=read(b/'PRIVATE_PACKET_MAP.json')
 labels=read(TOP/'analysis_v2/EVIDENCE_LABELS.json');defs=read(TOP/'analysis_v2/FACT_DEFINITIONS.json');out=[]
 for p in pack:
  key=mp[p['packet_id']];cid=key['case_id'];k=cid+':'+key['arm']
  known=set(knowledge[k] if knowledge is not None else seed_tags(cid));resolved=closure[k] if closure is not None else p['gold_residual_rubric']['goal_status']=='resolved'
  rr={'packet_id':p['packet_id'],**{a:key[a] for a in ['case_id','qid','arm']},'resolved_before':resolved,'valid':not bool(p['error']),'decision':p['decision'],'actions':[]}
  primary_seen=set();all_seen=set();paths=set()
  for a in key['actions']:
   pri=set();allf=set();refs=[]
   for eid in a['evidence_ids']:
    w=cat[eid];lab=labels.get(eid,{'facts':[],'reason':'No qualifying original-goal relation identified in source screening; outside-pool candidates are not primary positives.'})
    facts=set(lab['facts'])-known if not resolved else set();allf |=facts
    if w['in_primary_pool']:pri |= facts
    refs.append({'evidence_id':eid,'new_facts':sorted(facts),'primary_eligible':w['in_primary_pool'],'reason':lab['reason']})
   path=json.dumps(a['action'],sort_keys=True).lower();direct=any(defs[t]['kind']=='direct' for t in pri);decision=any(defs[t]['kind']=='decision' for t in pri)
   rr['actions'].append({'action_index':a['action_index'],'tool':a['action']['tool'],'error':a['error'],'direct_progress':direct,'decision_progress':decision,'any_progress':bool(pri),'sensitivity_any_progress':bool(allf),'new_primary_facts':sorted(pri),'new_sensitivity_facts':sorted(allf),'marginal_primary_facts':sorted(pri-primary_seen),'marginal_sensitivity_facts':sorted(allf-all_seen),'exact_repeated_path':path in paths,'observations':refs})
   primary_seen |=pri;all_seen |=allf;paths.add(path)
  rr.update(any_progress=bool(primary_seen),direct_progress=any(defs[t]['kind']=='direct' for t in primary_seen),decision_progress=any(defs[t]['kind']=='decision' for t in primary_seen),sensitivity_any_progress=bool(all_seen),belief_updates=[defs[t] for t in sorted(primary_seen)])
  out.append(rr)
 write(b/'progress_reviews.json',out);metrics={}
 for arm in sorted(set(r['arm'] for r in out)):
  rows=[r for r in out if r['arm']==arm];aa=[a for r in rows for a in r['actions']];n=sum(r['any_progress'] for r in rows);second=[a for a in aa if a['action_index']==1]
  tools={t:{'calls':sum(a['tool']==t for a in aa),'progress':sum(a['tool']==t and a['any_progress'] for a in aa)} for t in ['search','find','open']}
  metrics[arm]={'planned':len(rows),'valid':sum(r['valid'] for r in rows),'open':sum(not r['resolved_before'] for r in rows),'acting':sum(r['decision']=='act' for r in rows),'any_progress':n,'direct_progress':sum(r['direct_progress'] for r in rows),'decision_progress':sum(r['decision_progress'] for r in rows),'no_progress_valid':sum(r['valid'] and not r['any_progress'] for r in rows),'no_progress_acting':sum(r['decision']=='act' and not r['any_progress'] for r in rows),'sensitivity_any_progress':sum(r['sensitivity_any_progress'] for r in rows),'tool_calls':len(aa),'tool_calls_per_progress':len(aa)/n if n else None,'by_tool':tools,'second_actions':len(second),'second_action_adds_primary_fact':sum(bool(a['marginal_primary_facts']) for a in second),'second_action_adds_sensitivity_fact':sum(bool(a['marginal_sensitivity_facts']) for a in second),'second_repeats_primary_facts_only':sum(a['any_progress'] and not a['marginal_primary_facts'] for a in second),'exact_duplicate_path':sum(a['exact_repeated_path'] for a in aa)}
 write(b/'progress_metrics.json',metrics);print(json.dumps(metrics,indent=2));return out,metrics
if __name__=='__main__':score('one_step_acquisition_v2')
