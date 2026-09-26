"""Offline review export; never imported by production runner."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];TOP=ROOT/'experiments/deferred_recovery'
def rd(p):return json.loads(p.read_text())
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def dg(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def main(stage):
 cs=rd(TOP/stage/'post_writer_cells.json');bank={b['case_id']:b for b in rd(TOP/'bank/RECOVERY_BANK.json')};packets={};maps=[];actions=[];outputs=[]
 rnd=int(stage[-1])-1
 for key,c in cs.items():
  b=bank[c['case_id']];d=next((d for d in c['decisions'] if d['round']==rnd),None)
  if d is None:continue
  t=d['tool'];refs=[]
  if t:
   for i,w in enumerate(t['observations']):
    ident=dg([b['case_id'],w['url'],w['text']])[:16]
    packets.setdefault(ident,{'review_id':ident,'case_id':b['case_id'],'qid':b['qid'],'need':b['recovery_need'],
      'original_question':b['original_question'],'private_acceptable_relation':b['private_recovery_truth']['acceptable_relation'],
      'observation':{k:w[k] for k in ['title','url','text']}})
    refs.append(ident);maps.append({'cell':key,'round':rnd,'observation_index':i,'review_id':ident,'window_ref':w['window_ref'],'doc_ref':w['doc_ref']})
  actions.append({'cell':key,'round':rnd,'decision':d['actor']['output'],'error':d['actor']['error'],'tool_error':t['error'] if t else None,'review_ids':refs})
  for u in c['updates']:
   if u['round']!=rnd:continue
   outputs.append({'cell':key,'round':rnd,'wave':u['wave'],'need':b['recovery_need'],'observation_review_id':dg([b['case_id'],u['observation']['url'],u['observation']['text']])[:16],
      'pre_claims':[x['statement'] for x in u['pre_state']['claims']],'pre_hypothesis':u['pre_state']['hypothesis'],'output':u['proposal']['output'],'error':u['proposal']['error']})
 wr(TOP/stage/'EVIDENCE_REVIEW_PACKETS.json',list(packets.values()));wr(TOP/stage/'PRIVATE_REVIEW_MAP.json',maps);wr(TOP/stage/'ACTION_REVIEW_PACKETS.json',actions);wr(TOP/stage/'WRITER_REVIEW_PACKETS.json',outputs)
 print(stage,'unique observations',len(packets),'writer outputs',len(outputs))
if __name__=='__main__':main(sys.argv[1])
