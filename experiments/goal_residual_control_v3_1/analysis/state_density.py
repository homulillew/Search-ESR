"""Inherited-Claim relevance sensitivity uses archived v2 labels; increments use v3.1 review."""
import sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
old=ROOT/'experiments/goal_residual_control';b=TOP/'admission_replay'
labels=read(old/'analysis_v2/UPDATER_LABELS.json');streams=read(old/'three_round_loop_v2/UPDATER_STREAM_PACKETS.json')
m={}
for r in streams:
 if not r['proposal'] or r['review_id'] not in labels:continue
 for text,c in zip(r['proposal']['claims_to_add'],labels[r['review_id']]['claims']):m.setdefault((r['qid'],text),set()).add(not c['incidental'])
snaps={s['case_id']:s for s in read(old/'bank/SNAPSHOTS.json')}
for r in read(old/'three_round_loop_v2/selection.json'):
 for c in snaps[r['snapshot_id']]['verified_claims']:m.setdefault((r['qid'],c['statement']),set()).add(True)
rows=[]
for p in read(b/'BANK.json'):
 count=collections.Counter()
 for c in p['pre_state']['verified_claims']:
  vals=m.get((p['qid'],c['statement']),set());lab='relevant' if vals=={True} else 'incidental' if vals=={False} else 'unknown'
  count[lab+'_chars']+=len(c['statement']);count[lab+'_claims']+=1
 rows.append({'packet_id':p['packet_id'],'qid':p['qid'],**dict(count)})
write(b/'INHERITED_STATE_DENSITY.json',{'method':'Archived v2 incidental labels for inherited Claims; initial frozen seed Claims treated relevant. This is a sensitivity with a different historical relevance rubric; primary v3.1 comparison uses newly admitted character increments. Unknown is never imputed.', 'rows':rows,'totals':dict(sum((collections.Counter({k:v for k,v in r.items() if k.endswith('_chars') or k.endswith('_claims')}) for r in rows),collections.Counter()))})
print(dict(sum((collections.Counter({k:v for k,v in r.items() if k.endswith('_chars') or k.endswith('_claims')}) for r in rows),collections.Counter())))
