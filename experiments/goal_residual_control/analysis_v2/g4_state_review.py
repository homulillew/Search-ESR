from progress import *
b=TOP/'transition_replan_v2';updates=read(b/'state_updates.json');rows=[]
# Manual clause-level inspection against the exact source windows (no gold answer).
nonatomic={('T01',0,0),('T03',0,0),('T03',0,1),('T04',0,1),('T05',0,1),('T07',0,0),('T09',0,0),('T09',0,1),('T10',0,1),('T11',0,0),('T12',0,0),('T12',0,1),('T13',0,1),('T15',0,0),('T11',3,1),('T13',3,1)}
incidental={('T05',0,0),('T13',1,1),('T11',3,0),('T12',3,0),('T12',3,1),('T19',0,0),('T13',3,0)}
for u in updates:
 tid=u['transition_id'];wave=u['wave'];o=u['proposal']['output']
 for i,c in enumerate(o['claims_to_add'] if o else []):
  key=(tid,wave,i);bad=key==('T19',0,1)
  rows.append({'transition_id':tid,'wave':wave,'claim_index':i,'claim':c,'source_id':u['observation'].get('source_id'),'source_supported':not bad,'atomic':key not in nonatomic,'unsupported_join':bad,'candidate_overpromotion':False,'incidental_admission':key in incidental,'reason':'Retrospective 67 albums and a separate 2016 interview do not entail the count at that interview; time anchoring is invented.' if bad else 'Current source explicitly supports the factual clauses.' if tid!='T14' or i!=0 else 'Task identification is supported jointly by existing three plot/roommate claims and the current five-season observation; not a partial-clue promotion.'})
write(b/'claim_reviews.json',rows)
write(b/'state_metrics.json',{'updater_calls':len(updates),'valid':sum(u['proposal']['output'] is not None for u in updates),'claims_added':len(rows),'source_supported':sum(r['source_supported'] for r in rows),'precision':sum(r['source_supported'] for r in rows)/len(rows),'atomic':sum(r['atomic'] for r in rows),'unsupported_join':sum(r['unsupported_join'] for r in rows),'candidate_overpromotion':0,'hypothesis_rejections':{'eligible':['T07','T08'],'cleared':['T07','T08']},'warning':'Support is adjudicated per proposed sentence; compounds count once. Unsupported claims remain in production state.'})
# Source-grounded online state knowledge, explicitly distinct from oracle-post truth.
base={t['transition_id']:seed_tags(t['pre_snapshot']) for t in read(TOP/'bank/TRANSITIONS.json')}
new={'T01':['ding_opening'],'T02':['messi95'],'T03':['peter_name','peter_parents','meirelles_gardener'],'T04':['tuku_death'],'T05':['y_s4'],'T06':['rangers13'],'T07':['heart_exclusion'],'T08':['hijitus_exclusion'],'T09':['galacta_release','galacta_credits'],'T10':['dean_pc'],'T11':['tuku_activist','tuku67','wasakara','forbes65'],'T12':['tuku_activist','tuku67','wasakara','forbes65'],'T13':['y_s1','y_seasons','y_s3','y_roommate'],'T14':['y_seasons'],'T15':['rangers_table','rangers_equal_pair'],'T16':['rangers_founded'],'T17':['peter_police','peter_films'],'T18':[],'T19':[],'T20':['y_s3']}
knowledge={};closure={}
truth=read(TOP/'bank/PRIVATE_TRUTH.json')['snapshots']
for t in read(TOP/'bank/TRANSITIONS.json'):
 tid=t['transition_id'];online=base[tid]|set(new[tid])
 for arm in ['R0','R1','R2','R3']:
  key=tid+':'+arm;knowledge[key]=sorted(seed_tags(t['post_snapshot']) if arm=='R2' else online)
  closure[key]=truth[t['post_snapshot']]['goal_status']=='resolved' if arm=='R2' else tid in ['T11','T12','T13','T14','T18','T20']
write(b/'ONLINE_KNOWLEDGE_REVIEW.json',{'knowledge':knowledge,'closure':closure,'notes':['T13 online state commits S1 and season count from its real observation batch; oracle POST intentionally leaves them uncommitted. Online closure is therefore resolved while oracle reference is open.','T11/T12 online states have highly discriminative age/67 albums/activist/Wasakara plus exact May 2017 count. Primary identity-plus-requested-relation closure is met; strict all-clues sensitivity remains open (first album and quote uncommitted).','T19 unsupported temporal join never counts as new verified knowledge in offline evaluation. Production is unrepaired.']})
print(read(b/'state_metrics.json'))
