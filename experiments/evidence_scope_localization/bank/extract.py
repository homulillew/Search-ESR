"""Offline archival checkpoint extraction. No model calls or new retrieval."""
import copy, hashlib, json, sqlite3
from pathlib import Path
TOP=Path(__file__).resolve().parents[1]; ROOT=TOP.parents[1]
def rd(p): return json.loads(Path(p).read_text())
def wr(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def dg(x): return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def sh(s): return hashlib.sha256(s.encode()).hexdigest()
db=sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
def doc(d):
 t,u=db.execute('select text,url from documents where docid=?',(str(d),)).fetchone();return t,u
def convert(s):
 ws=s['available_workspace']; reg={'documents':[],'windows':[]}
 for d in ws['known_documents']:
  text,url=doc(d['docid']);reg['documents'].append({**d,'docid':str(d['docid']),'document_sha256':sh(text)})
 for w in ws['observed_windows']:
  d=next(d for d in reg['documents'] if d['doc_ref']==w['doc_ref']);text,_=doc(d['docid']);off=text.find(w['text'])
  if off<0: raise ValueError('non-exact archived observation')
  reg['windows'].append({k:w[k] for k in ['window_ref','doc_ref','title','url','text']}|{'offset':off,'text_sha256':sh(w['text'])})
 return {'qid':str(s['qid']),'question':s['question'],'claims':s['verified_claims'],'hypothesis':s['working_hypothesis'],'attempts':s.get('attempts',s.get('recent_attempt_context',[])),'registry':reg}
def main():
 rows=[];ex=[]
 for rnd in range(1,4):
  p=ROOT/f'experiments/bcplus_verification/round{rnd}/post_writer_cells.json'
  for key,c in rd(p).items():
   if not c['registry']['documents']:continue
   v={k:copy.deepcopy(c[k]) for k in ['qid','question','claims','hypothesis','attempts','registry']}
   rows.append(v|{'checkpoint_id':f'BC_R{rnd}_{key}','provenance':{'path':str(p.relative_to(ROOT)),'key':key},'origin':'actual preceding formal post-Writer state, unchanged'})
 for fn,kind in [('experiments/frontier_generation/bank/CHECKPOINT_INVENTORY.json','frontier'),('experiments/deferred_recovery/bank/HISTORICAL_INVENTORY.json','reserve')]:
  for i,r in enumerate(rd(ROOT/fn)):
   s=r['state'] if kind=='frontier' else r['post_state'];cid=r.get('checkpoint_id',r.get('id'))
   try: v=convert(s)
   except Exception as e:ex.append({'id':cid,'file':fn,'reason':str(e)});continue
   if not v['registry']['documents']:continue
   rows.append(v|{'checkpoint_id':f'{kind}_{cid}','provenance':{'path':fn,'index':i,'pointer':'state' if kind=='frontier' else 'post_state'},'origin':r.get('state_origin','actual archived post-state, inherited historical seed; no cleaning'),'reserve':kind=='reserve'})
 seen=set();unique=[]
 for r in rows:
  h=dg({k:r[k] for k in ['qid','question','claims','hypothesis','attempts','registry']})
  if h in seen:continue
  seen.add(h);r['prefix_sha256']=h;unique.append(r)
 wr(TOP/'bank/PREFIX_INVENTORY.json',unique);wr(TOP/'bank/EXTRACTION_EXCLUSIONS.json',ex)
 b=rd(ROOT/'experiments/bcplus_verification/bank/VERIFICATION_BANK.json');screen=[]
 for n in b:
  if n['case_id'] in ['VP16','VN12']:continue
  refs={e['docid'] for e in n['reference_evidence']}
  if n['case_id']=='VP03':refs={'22411'}
  for r in unique:
   if r['qid']!=n['qid']:continue
   gold=[d for d in r['registry']['documents'] if d['docid'] in refs]
   vis='\n'.join(w['text'] for w in r['registry']['windows'])+'\n'+'\n'.join(c['statement'] for c in r['claims'])
   anchors=[e['anchor'] for e in n['reference_evidence']]
   screen.append({'family':n['case_id'],'qid':r['qid'],'checkpoint_id':r['checkpoint_id'],'reference_docs':[d['doc_ref'] for d in gold],'screen_anchor_visible':[a for a in anchors if ' '.join(a.lower().split()) in ' '.join(vis.lower().split())], 'size':[len(r['registry']['documents']),len(r['registry']['windows']),len(json.dumps(r))],'reserve':r.get('reserve',False)})
 wr(TOP/'bank/SCREENS.json',screen)
 print('unique prefixes',len(unique),'exclusions',len(ex),'crosses',len(screen))
 for n in b:
  cand=sorted([x for x in screen if x['family']==n['case_id'] and x['reference_docs'] and not x['screen_anchor_visible']],key=lambda x:(x['size'],x['checkpoint_id']))
  print(n['case_id'],[(x['checkpoint_id'],x['reference_docs'],x['size'][:2]) for x in cand[:4]])
if __name__=='__main__':main()
