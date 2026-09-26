"""Mechanical counts from frozen atoms and explicit offline semantic reviews."""
import sys,collections,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
b=TOP/'admission_replay';bank=read(b/'BANK.json');gold={x['packet_id']:x for x in read(b/'GOLD_ADMISSION_ATOMS.json')};reviews=read(b/'REVIEWS.json')
rows=[{'case_id':p['packet_id'],'qid':p['qid'],'arm':'U0',**{k:p['U0'][k] for k in ['output','error']}} for p in bank]
rows += read(b/'Uc_outputs.json')+read(b/'U1_outputs.json')
assert len(rows)==165
states={p['packet_id']:p['pre_state'] for p in bank};out=[]
def semantic(s):return {'Original Question':s['question'],'Verified Claims':[c['statement'] for c in s['verified_claims']],'Working Hypothesis':s['working_hypothesis']}
def chars(s):return len(json.dumps(semantic(s),ensure_ascii=False,sort_keys=True))
for x in rows:
 pid=x['case_id'];g=gold[pid];uid=digest(['admission-review',pid,x['output']])[:16]
 if x['output'] is not None:assert uid in reviews,uid
 rev=reviews.get(uid,{'claims':[],'captured_atoms':[],'hypothesis_verdict':'interface_failure'})
 before=states[pid];after=copy.deepcopy(before);o=x['output'];cl=rev['claims']
 if o:
  for s in o['claims_to_add']:after['verified_claims'].append({'statement':s})
  h=o['hypothesis_update']
  if h['action']=='set':after['working_hypothesis']=h['statement']
  elif h['action']=='clear':after['working_hypothesis']=None
 a={'packet_id':pid,'qid':x['qid'],'arm':x['arm'],'review_id':uid,'valid':o is not None,'error':x['error'],
    'claims':len(cl),'supported':sum(c['source_supported'] for c in cl),'relevant':sum(c['decision_relevant'] for c in cl),
    'incidental':sum(c['incidental'] for c in cl),'novel':sum(c['novel'] for c in cl),'scope_loss':sum(not c['scope_preserved'] for c in cl),
    'admissible':sum(c['source_supported'] and c['decision_relevant'] and c['novel'] and c['scope_preserved'] for c in cl),
    'atom_denominator':len(g['atoms']),'captured_atoms':len(rev['captured_atoms']),
    'mutation':semantic(before)!=semantic(after),'no_change':o is not None and semantic(before)==semantic(after),
    'no_claim_expected':g['no_new_claim_expected'],'correct_empty':o is not None and g['no_new_claim_expected'] and not cl,
    'empty':o is not None and not cl,'before_chars':chars(before),'after_chars':chars(after),'char_delta':chars(after)-chars(before),
    'relevant_new_claim_chars':sum(len(c['statement']) for c in cl if c['decision_relevant']),
    'incidental_new_claim_chars':sum(len(c['statement']) for c in cl if c['incidental']),
    'hypothesis_verdict':rev['hypothesis_verdict'],'hypothesis_error':o is not None and not rev['hypothesis_verdict'].startswith('correct_'),
    'hypothesis_operation':o['hypothesis_update']['action'] if o else None,'post_semantic_state':semantic(after)}
 out.append(a)
write(b/'COUNTERFACTUAL_POST_STATES.json',out)
fields=['valid','claims','supported','relevant','incidental','novel','scope_loss','admissible','atom_denominator','captured_atoms','mutation','no_change','no_claim_expected','correct_empty','empty','before_chars','after_chars','char_delta','relevant_new_claim_chars','incidental_new_claim_chars','hypothesis_error']
def stats(rs):
 d={k:sum(r[k] for r in rs) for k in fields};d['packets']=len(rs)
 for k in ['supported','relevant','novel','admissible']:d[k+'_precision']=d[k]/d['claims'] if d['claims'] else None
 d['recall']=d['captured_atoms']/d['atom_denominator'] if d['atom_denominator'] else None
 d['hypothesis_verdicts']=dict(collections.Counter(r['hypothesis_verdict'] for r in rs));d['hypothesis_operations']=dict(collections.Counter(r['hypothesis_operation'] for r in rs));return d
m={'arms':{a:stats([r for r in out if r['arm']==a]) for a in ['U0','Uc','U1']},'qid_arms':{q:{a:stats([r for r in out if r['qid']==q and r['arm']==a]) for a in ['U0','Uc','U1']} for q in sorted({r['qid'] for r in out},key=int)},'paired':{}}
lookup={(r['packet_id'],r['arm']):r for r in out}
for control,treatment in [('Uc','U1'),('U0','Uc'),('U0','U1')]:
 p={}
 for metric in ['incidental','captured_atoms','scope_loss','hypothesis_error','correct_empty','char_delta']:
  dif=[lookup[r['packet_id'],treatment][metric]-lookup[r['packet_id'],control][metric] for r in bank]
  p[metric]={'treatment_minus_control':sum(dif),'negative':sum(v<0 for v in dif),'tie':sum(v==0 for v in dif),'positive':sum(v>0 for v in dif)}
 m['paired'][treatment+'-'+control]=p
u={}
for arm in ['Uc','U1']:
 rr=[r for r in rows if r['arm']==arm];uu=[r['usage'] for r in rr if r.get('usage')]
 u[arm]={'calls':len(rr),'usage_reported':len(uu),**{k:sum(v[k] for v in uu if v.get(k) is not None) for k in ['input','output','hit','miss','reasoning']}}
 u[arm]['cache_rate']=u[arm]['hit']/(u[arm]['hit']+u[arm]['miss']);u[arm]['failures']=dict(collections.Counter(r['error']['category'] for r in rr if r['error']))
m['incremental_cost']=u;write(b/'metrics.json',m)
print(json.dumps({'arms':m['arms'],'paired':m['paired'],'cost':u},ensure_ascii=False,indent=2))
