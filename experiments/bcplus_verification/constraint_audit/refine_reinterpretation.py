"""Append-only correction of historical-demand classification, not S1/S2 labels or gates."""
import json,collections
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
read=lambda p:json.loads(p.read_text());write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
# Inspecting full historical Claim packets exposed overinclusive pattern classification in audit_history.py.
corrections={
('da7c41c32f7c',3):('unsupported_incompatibility','Official incorporation after a credited release does not establish impossibility.'),
('ff7fd0f0ec2b',1):('unsupported_incompatibility','Same incorporation inference; not a mere exact-release-year dispute.'),
('669748fc90a9',3):('covered_coreference','Full Peter King Nzioki name, popular-name alias and matching two-film appearances allow ordinary within-Claims name coreference; no extra explicit Q condition asks for another alias certificate.'),
('3e71b4ce1c32',2):('covered_coreference','Same full-name and matching film Claims already bind ordinary name variants.'),
('d176176adcca',2):('covered_coreference','Same full-name and matching film Claims already bind ordinary name variants.'),
('b8fa11efbcfb',3):('stale_excluded_candidate_reconciliation','Reconciling an already disqualified Hijitus does not verify an explicit condition for a still usable target.'),
('b42aa54a33f4',9):('invented_geographic_scope','Question asks Argentine release name; it does not require original early-1990s broadcast to occur in Argentina. Argentine rerun dates do not contradict original-run date.'),
('402cab0848db',3):('sensitivity_only','Demand is phrased around exact midway position; role/event language alone is not evidence that this demand diagnoses the separate female-lead gap.'),
('dd33e3363895',4):('sensitivity_only','The old reviewer specifically identified exact relative episode position; retain temporal-cutoff sensitivity rather than counting all mixed wording as a clear hard-gap diagnosis.')}
rows=read(P/'OVERDEMAND_REAUDIT.json');applied=[]
# IDs are fixed, but recover unit indexes from semantic content to avoid indexing assumptions.
for x in rows:
 rid=x['review_id'];idx=x['unit_index'];t=x['text']
 candidate=[(k,v) for k,v in corrections.items() if k[0]==rid]
 if not candidate:continue
 v=candidate[0][1]
 match=(rid=='da7c41c32f7c' and 'timeline relation' in t.lower()) or (rid=='ff7fd0f0ec2b' and 'company/game' in t.lower()) or rid in ['669748fc90a9','3e71b4ce1c32','d176176adcca','b8fa11efbcfb','b42aa54a33f4'] or (rid in ['402cab0848db','dd33e3363895'] and 'season-four' in t.lower() or rid=='dd33e3363895' and 'season four' in t.lower())
 if not match:continue
 applied.append({'review_id':rid,'unit_index':idx,'old_new_audit_verdict':x['strict_verdict'],'corrected_verdict':v[0],'reason':v[1]});x['strict_verdict']=v[0];x['correction_reason']=v[1]
write(P/'REINTERPRETATION_CORRECTIONS.json',{'utc':datetime.now(timezone.utc).isoformat(),'timing':'After S1/S2 submissions began, while reviewing only historical packets; does not change any frozen bank relation, prompt, gate or runtime file. Original audit artifacts remain immutable.','corrections':applied,'corrected_counts':dict(collections.Counter(x['strict_verdict'] for x in rows))})
write(P/'OVERDEMAND_REVIEWED.json',rows)
# Record decision-level old-v-new interpretation on all previously resolved controls.
oldtrue={}
for s in read(P/'RESOLVED_REAUDIT.json'):
 for o in s['occurrences']:oldtrue[o['stage'],o['case_id']]=s
out=[]
for stage in ['dynamic_progress','asymmetric_progress']:
 packets=read(ROOT/'experiments'/stage/'analysis/review_packets.json')
 mapping=read(ROOT/'experiments'/stage/'analysis/review_map.json') if stage=='asymmetric_progress' else {}
 for p in packets:
  lab=p.get('frozen_label',p.get('label'));cid=lab['case_id'];o=p['output']
  if not lab['gold_resolved'] or not o:continue
  val=o.get('resolved',o.get('confirmed'))
  if not isinstance(val,bool):continue
  rid=p['review_id'];demand=[x for x in rows if x['stage']==stage and x['review_id']==rid]
  out.append({'stage':stage,'review_id':rid,'case_id':cid,'qid':p['qid'],'arm_metadata':mapping.get(rid),'old_gold_resolved':True,'strict_gold_resolved':False,'model_closure':val,'old_interpretation':'correct closure' if val else 'missed closure','strict_interpretation':'premature closure' if val else 'correct rejection','rejection_reason_status':[x['strict_verdict'] for x in demand],'note':'Correct rejection does not certify its supplied reason; unsupported incompatibility remains an error.'})
write(P/'HISTORICAL_CLOSURE_REINTERPRETATION.json',out)
print('Corrections',len(applied),'counts',collections.Counter(x['strict_verdict'] for x in rows));print('Closure outputs on old-resolved states',len(out),collections.Counter((x['stage'],x['strict_interpretation']) for x in out))
