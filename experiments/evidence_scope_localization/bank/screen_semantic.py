"""Produce review candidates from all archived documents, not just old refs."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from extract import TOP,ROOT,rd,wr,doc
from relations import NEEDS,CHALLENGE,candidates
def main():
 old={r['case_id']:r for r in rd(ROOT/'experiments/bcplus_verification/bank/VERIFICATION_BANK.json')}
 out=[]
 for f in NEEDS:
  q=old[f]['qid']
  for p in rd(TOP/'bank/PREFIX_INVENTORY.json'):
   if p['qid']!=q:continue
   visible=[w['window_ref'] for w in p['registry']['windows'] if candidates(f,w['text'],w['title'])]
   claims=[c['statement'] for c in p['claims'] if candidates(f,c['statement'],old[f]['candidate'])]
   allvis='\n'.join(w['text'] for w in p['registry']['windows'])
   if candidates(f,allvis,old[f]['candidate']) and not visible:visible=['union-screen-needs-review']
   ds=[d for d in p['registry']['documents'] if candidates(f,doc(d['docid'])[0],d['title'])]
   out.append({'family':f,'qid':q,'checkpoint_id':p['checkpoint_id'],'source_candidates':ds,'visible_candidates':visible,'claim_candidates':claims,'size':[len(p['registry']['documents']),len(p['registry']['windows']),len(json.dumps(p))],'challenge':f in CHALLENGE})
 wr(TOP/'bank/SEMANTIC_SCREENS.json',out)
 for f in NEEDS:
  if f in CHALLENGE:continue
  ks=sorted([r for r in out if r['family']==f and r['source_candidates'] and not r['visible_candidates'] and not r['claim_candidates']],key=lambda r:(r['size'],r['checkpoint_id']))
  ns=sorted([r for r in out if r['family']==f and not r['source_candidates'] and not r['visible_candidates'] and not r['claim_candidates']],key=lambda r:(r['size'],r['checkpoint_id']))
  print(f,'K',[(r['checkpoint_id'],[(d['doc_ref'],d['docid']) for d in r['source_candidates']]) for r in ks[:2]],'N',[(r['checkpoint_id'],r['size'][:2]) for r in ns[:1]])
if __name__=='__main__':main()
