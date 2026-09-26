"""Export selected actual Claim -> archived raw observation support packets."""
import collections,hashlib,json
from pathlib import Path
from curation import DEV,CHALLENGE
P=Path(__file__).resolve().parents[1];R=P.parents[1]
def rd(p):return json.loads(p.read_text())
def sh(s):return hashlib.sha256(s.encode()).hexdigest()
inv=rd(P/'bank/INVENTORY.json');trans=rd(P/'bank/TRANSITIONS.json');windows={};origins=collections.defaultdict(list)
def walk(x,path,ptr=''):
 if isinstance(x,dict):
  if isinstance(x.get('text'),str) and ('url' in x or 'window_ref' in x):
   h=sh(x['text']);windows.setdefault(h,{k:x.get(k) for k in ['title','url','text','window_ref']});origins[h].append({'path':str(path.relative_to(R)),'pointer':ptr})
  for k,v in x.items():
   if k not in ['answer','gold_answer','gold','raw_response','messages']:walk(v,path,ptr+'/'+str(k))
 elif isinstance(x,list):
  for i,v in enumerate(x):walk(v,path,ptr+'/'+str(i))
for p in ['experiments/frontier_generation/bank/CHECKPOINT_INVENTORY.json','experiments/deferred_recovery/bank/HISTORICAL_INVENTORY.json','experiments/goal_residual_control/bank/SOURCE_WINDOWS.json','experiments/goal_residual_control/transition_replan_v2/state_updates.json','experiments/bcplus_verification/RESULTS.json']:
 walk(rd(R/p),R/p)
rows=[]
for r in inv:
 if r['inventory_id'] not in DEV+CHALLENGE:continue
 for i,c in enumerate(r['claim_records']):
  hs=c.get('source_text_hashes',[]);found=[h for h in hs if h in windows]
  row={'state_id':r['inventory_id'],'claim_index':i+1,'statement':c['statement'],'claim_record':c,'support':[{'hash':h,'observation':windows[h],'origins':origins[h][:2]} for h in found]}
  rows.append(row)
(P/'bank/CLAIM_SUPPORT_PACKETS.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print('Claims',len(rows),'unique',len({r['statement'] for r in rows}),'missing',sum(not r['support'] for r in rows))
for r in rows:
 if not r['support']:print(r['state_id'],r['claim_index'],r['statement'])
(P/'bank/OBSERVED_TEXT_INDEX.json').write_text(json.dumps({h:{'text':v['text'],'title':v['title'],'url':v['url'],'origin':origins[h][0]} for h,v in windows.items()},ensure_ascii=False,indent=2)+'\n')
