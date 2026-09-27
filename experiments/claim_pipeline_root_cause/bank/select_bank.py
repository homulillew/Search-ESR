import hashlib,json
from pathlib import Path
from build_inventory import save,sha
B=Path(__file__).resolve().parent
D={'228':'identity_entity','435':'temporal','517':'role','538':'source_document','546':'conjunction_sequence','637':'qualifier_quantifier','922':'attribution_modality','1094':'cross_entity'}
H={'169':'identity_entity','177':'qualifier_quantifier','186':'role','261':'qualifier_quantifier','264':'source_document','311':'temporal','324':'temporal','387':'role','580':'conjunction_sequence','601':'role','633':'qualifier_quantifier','673':'attribution_modality','776':'attribution_modality','1034':'cross_entity'}
def h(s):return hashlib.sha256(s.encode()).hexdigest()
def main():
 inv=json.loads((B/'inventory.json').read_text());rows=inv['packets'];by={}
 for r in rows:by.setdefault(r['qid'],[]).append(r)
 legacy=json.loads((B.parents[1]/'minimal_research_loop/verify_necessity/OBSERVATIONS.json').read_text())
 chosen=[]
 def add(r,split):chosen.append({**r,'split':split,'family_prestratum':(D|H)[r['qid']]})
 for q in sorted(D,key=int):
  pool=by[q]
  def dup(r):
   if 'minimal_research_loop' not in r['origin']['path']:return False
   return 'T6_' in legacy[int(r['origin']['pointer'][1:])]['case_id']
  add(min(pool,key=lambda r:(not dup(r),r['packet_id'])),'D')
 for q in sorted(D,key=lambda q:h('claim-root-v1:D:'+q)):
  pool=[r for r in by[q] if r['packet_id'] not in {x['packet_id'] for x in chosen}]
  add(min(pool,key=lambda r:(not (r['C'] and r['historical_candidates']),r['packet_id'])),'D')
  if len(chosen)==12:break
 qs=sorted([q for q in by if q not in D and len(by[q])>=2],key=lambda q:h('claim-root-v1:H:'+q))
 for i,q in enumerate(qs[:12]):
  for r in sorted(by[q],key=lambda r:r['packet_id'])[:2]:add(r,'H_diagnostic' if i<6 else 'H_confirmation')
 assert len(chosen)==36,len(chosen)
 selected={r['packet_id'] for r in chosen}
 save(B/'selection.json',{'protocol_sha256':sha(B.parent/'BANK_PROTOCOL.md'),'inventory_sha256':sha(B/'inventory.json'),'packets':chosen,'unselected':[{'packet_id':r['packet_id'],'qid':r['qid'],'reason':'deterministic partition/order/qid cap'} for r in rows if r['packet_id'] not in selected],'new_calls':0})
 for r in chosen:print(r['split'],r['packet_id'],r['qid'],r['family_prestratum'],r['OneGap'],r['Observation'][0].get('title'),len(r['historical_candidates']))
if __name__=='__main__':main()
