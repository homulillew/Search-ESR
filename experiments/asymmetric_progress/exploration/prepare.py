import sys,copy,hashlib
from pathlib import Path
T=Path(__file__).resolve().parents[1];sys.path.insert(0,str(T))
from runtime import ROOT,rd,wr,item,sha,head,now

E=T/'exploration';assert not (E/'freeze.json').exists()
ids=['A07','A08','A09','A18','A19','S03','S01','S02','S07','S08','S09','A24']
bank={c['case_id']:c for b in ['PRIMARY','CHALLENGE'] for c in rd(T/f'bank/{b}.json')}
base=(T/'prompts/Audit.md').read_text()
addition='''
Materiality check before rejecting:
Ask whether a plausible resolution of the missing detail, consistent with the Verified Claims, could materially change the discriminative candidate identity or the requested answer. If the Claims already bind that identity and the requested final relation, the mere absence of redundant corroboration is not a blocker. Do not require an extra Claim that only repeats an incidental biographical detail, exact quotation, descriptive prominence label, or relative episode-position wording. Ordinary referent alignment across connected Claims about the same named participants does not require a separate Claim repeating every role noun in the question.
This does not waive an unestablished explicit quantity bound, requested date or source attribution, required participant-role link, or material contradiction. If the Claims do not actually establish such a relation, reject closure; never supply the missing relation from outside knowledge or from the plausibility of a candidate.
'''
(E/'prompt.md').write_text(base+addition)
reqs=[]
for cid in ids:
 c=copy.deepcopy(bank[cid]);c['set']='exploration'
 reqs += [item(c,'Audit',rep,prompt=base+addition) for rep in [1,2]]
reqs.sort(key=lambda x:hashlib.sha256(('exploration:'+x['id']).encode()).hexdigest())
wr(E/'requests.json',reqs)
baseline=[];reviews=rd(T/'analysis/semantic_review.json');mp=rd(T/'analysis/review_map.json')
for stage in ['primary','challenge']:
 for r in rd(T/stage/(stage+'_outputs.json')):
  if r['case_id'] in ids and r['arm']=='Audit':
   uid=next(k for k,v in mp.items() if v['stage']==stage and v['id']==r['id'])
   baseline.append({'stage':stage,'result':r,'review':reviews[uid]})
assert len(baseline)==24
wr(E/'baseline.json',baseline)
files=[T/'runtime.py',T/'cache.py',T/'analysis/RUBRIC.md',T/'PROTOCOL.md',T/'analysis/GATE.json',T/'prompts/Audit.md',T/'schemas/Audit.json',ROOT/'experiments/model_backend_deepseek/provider.json']
files += [T/f'bank/{n}.json' for n in ['PRIMARY','CHALLENGE','PRIMARY_LABELS','CHALLENGE_LABELS']]
files += [p for p in E.iterdir() if p.is_file()]
wr(E/'freeze.json',{'stage':'exploration','prepared_utc':now(),'preparation_head':head(),'sample_count':24,'checkpoint_count':12,'qid_count':5,'resolved_slots':12,'unresolved_slots':12,'horizon':1,'model':'deepseek-flash','provider_defaults':True,'max_retries':0,'timeout_seconds_per_http_operation':240,'workers':4,'tools':[],'selected_ids':ids,'failure_direction':'over-demand / materiality calibration only','full_style_audit':False,'gate_override':False,'failure_policy':'One attempt only, no repair/resample, raw failures retained, failed output cannot authorize STOP.','file_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted(files)}})
print('prepared 24 exploration requests; commit before run')
