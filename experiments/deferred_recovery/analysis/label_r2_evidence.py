import json,hashlib
from pathlib import Path
TOP=Path(__file__).resolve().parents[1]
def dg(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
old=json.load(open(TOP/'r1/EVIDENCE_LABELS.json'))
new={
'c8f935d26072dad1':(False,'Character descriptions and school attendance do not establish educational purpose. No new corroboration beyond R1.' ,'none'),
'adeae1e66ea3cfde':(True,'Spanish source explicitly gives season1five minutes, season2eleven minutes and specials21; adds season scope to the contrary duration evidence.','refutes'),
'39a89d2e3a08599f':(False,'Generic runtime question page returns only placeholder/error text.','none'),
'8240d2c94c1577c0':(True,'AlloCine again visibly lists4min; preserves original omitted fact but does not reconcile contradictory sources.','supports'),
'1569c264978aea81':(False,'Second local query again returns cast mentions throughseason5, no total-season upper bound.','none')}
cs=json.load(open(TOP/'r2/post_tool_cells.json'));out={};mapping=[]
for key,c in cs.items():
 t=c['decisions'][-1]['tool']
 if not t:continue
 for i,w in enumerate(t['observations']):
  rid=dg([c['case_id'],w['url'],w['text']])[:16]
  if rid in old:v=old[rid]
  else:
   sufficient,reason,polarity=new[rid];v={'sufficient_need_evidence':sufficient,'evidence_outcome':'direct_need_support' if sufficient else 'no_progress','reason':reason,'polarity':polarity,'reviewer':'single Codex offline; arm visible; no independence claim'}
  out[rid]=v;mapping.append({'cell':key,'index':i,'review_id':rid})
(TOP/'r2/EVIDENCE_LABELS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
(TOP/'r2/EVIDENCE_LABEL_MAP.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n')
print('reviewed',len(mapping),'windows,',len(out),'unique')
