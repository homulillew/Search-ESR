"""Offline selection and freeze, never imported by runtime."""
import sys,json,hashlib,subprocess
from pathlib import Path
E=Path(__file__).resolve().parent;P=E.parent;ROOT=P.parents[1]
sys.path.insert(0,str(E))
from run_exploration import actor
from runtime import read,write,sha,head,now
units=read(P/'analysis/UNIT_REVIEW.json');bank={u['case_id']:u for u in read(P/'bank/VERIFICATION_BANK.json')};prefix=read(P/'round1/post_writer_cells.json');controls=read(P/'RESULTS.json')
elig=[];sel=[];seen=set()
for u in sorted([u for u in units if u['arm']=='V'],key=lambda u:u['case_id']):
 cid=u['case_id'];refs={e['docid'] for e in bank[cid]['reference_evidence']};docs={d['docid'] for d in prefix[cid+':V']['registry']['documents']};ok=(not u['success']) and (not u['evidence_found']) and u['bank_eligible'] and not u['status'].endswith('_failure') and bool(refs&docs)
 take=ok and u['qid'] not in seen and len(sel)<4
 elig.append({'case_id':cid,'eligible':ok,'selected':take,'observed_reference_docids':sorted(refs&docs),'exclusion':'not one of target failures with valid bank/reference document observed' if not ok else 'qid already selected' if not take else None})
 if take:sel.append(cid);seen.add(u['qid'])
assert sel==['VN01','VN07','VP06','VP12'],sel
cells={cid+':V':prefix[cid+':V'] for cid in sel};write(E/'SELECTION.json',{'all_candidates':elig,'selected':sel});write(E/'INPUTS.json',cells);write(E/'REQUESTS.json',[actor(c) for c in cells.values()])
write(E/'CONTROLS.json',{cid:controls[cid+':V'] for cid in sel})
files=[p for p in E.glob('*') if p.is_file() and p.name!='freeze.json']+[P/'RESULTS.json',P/'round1/post_writer_cells.json',P/'analysis/UNIT_REVIEW.json',P/'analysis/GATES.json',P/'freeze.json']
write(E/'freeze.json',{'parent_head':head(),'utc':now(),'max_calls':24,'max_retries':0,'units':4,'decisions_per_unit':1,'same_original_decision_boundary':2,'provider':'same primary frozen deepseek-flash config','files':{str(p.relative_to(ROOT)):sha(p) for p in files},'primary_runtime_checks':'run_exploration invokes primary.check for all55 frozen text/runtime files and17 binary identities before calls'})
print(sel)
