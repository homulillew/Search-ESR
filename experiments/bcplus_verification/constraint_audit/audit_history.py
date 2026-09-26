"""Reinterpret immutable historical labels; no runtime import permitted."""
import json,hashlib,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
ann={x['qid']:x for x in read(P/'CONSTRAINTS.json')};states={}
for stage in ['dynamic_progress','asymmetric_progress']:
 for arm in ['PRIMARY','CHALLENGE']:
  base=ROOT/'experiments'/stage/'bank';labs=read(base/(arm+'_LABELS.json'))
  for b in read(base/(arm+'.json')):
   if not labs[b['case_id']]['gold_resolved']:continue
   claims=[c['statement'] for c in b['state']['verified_claims']];key=hashlib.sha256(json.dumps([b['question'],claims],ensure_ascii=False).encode()).hexdigest()
   states.setdefault(key,{'qid':b['qid'],'Q':b['question'],'claims':claims,'occurrences':[],'old_label':True,'strict_constraint_label':False})['occurrences'].append({'stage':stage,'bank':arm,'case_id':b['case_id'],'checkpoint':b['checkpoint_id']})
# Human semantic judgments on every original hard relation, retaining partial rather than binary collapse.
for key,s in states.items():
 q=s['qid'];c=s['claims'];cov=[]
 for u in ann[q]['units']:
  if u['classification'] not in ['HARD_CONSTRAINT','REQUESTED_RELATION']:continue
  n=int(u['id'][-2:]);status='supported';refs=[];reason=''
  if q=='435':
   if u['classification']=='REQUESTED_RELATION':refs=[i+1 for i,t in enumerate(c) if ('May' in t or '2017-05-01' in t) and ('65' in t or 'feature' in t)];reason='Dated feature/count explicitly bound; in long state C13 or C15+C16 supports scope.'
   elif n==1:refs=[1];reason='Death age explicitly 66.'
   elif n==2:refs=[i+1 for i,t in enumerate(c) if '67 albums' in t];reason='Career total explicitly 67.'
   elif n==3:status='missing';reason='Performance in 1977 or recording deal in 1975 does not entail first album release in the 1970s.'
   elif n==4:status='partial';refs=[i+1 for i,t in enumerate(c) if 'Wasakara' in t];reason='2001 song and president attribution do not establish urging retirement.'
   elif n==5:status='missing';reason='A 2016 interview reference or a different quotation does not entail the specified art/singing quotation.'
   elif n==6:
    refs=[i+1 for i,t in enumerate(c) if 'human' in t.lower() and 'activist' in t.lower()];status='supported' if refs else 'missing';reason='Human rights activism must be a Claim; outside biography cannot fill it.'
  elif q=='580':
   if u['classification']=='REQUESTED_RELATION':status='partial';reason='Series name appears in episode Claims, but complete target binding is conditional on the unresolved hard relations.'
   elif n==1:status='partial';reason='Assumption/upset/date exists, but sensitive issue causing no time together and explicit lead binding are absent.';refs=[i+1 for i,t in enumerate(c) if 'assumption' in t]
   elif n==2:status='partial';reason='Edgar sacrifice and Jimmy roommate are known; Jimmy male-lead role is not established. Episode 13 alone does not establish final position; numerical cutoff is sensitivity-only.';refs=[i+1 for i,t in enumerate(c) if any(w in t for w in ['sacrifice','roommate'])]
   elif n==3:status='partial';reason='Home/baby/reconnection in S4E7 is known; Gretchen female-lead role is not established. Exact midway threshold is sensitivity-only.';refs=[1]
   elif n==4:refs=[i+1 for i,t in enumerate(c) if 'five seasons' in t];reason='Five logically entails fewer than ten.'
  elif q=='186':
   if u['classification']=='REQUESTED_RELATION':status='partial';reason='Game name known, but original founding-name relation is not established.'
   elif n==1:refs=[i+1 for i,t in enumerate(c) if 'developed by Albino' in t or 'credited as the developer' in t];reason='Developer credit plus literal Frog name establishes this naming clue.'
   elif n==2:status='partial';refs=[3,4];reason='Former Night Sky and official October 1993 establishment do not establish the company name at its first establishment. No claim establishes Night Sky founding date.'
   elif n==3:refs=[1];reason='November 1992 supports November early 1990s. Alternative 1993 also fits decade; exact-year disagreement retained without inventing impossibility.'
   elif n in [4,5]:refs=[1];reason='One offline player and shareware explicit.'
   elif n==6:refs=[2];reason='Three named credits, two Pucketts.'
  cov.append({'constraint_id':u['id'],'status':status,'claim_refs':refs,'reason':reason})
 s['coverage']=cov;s['reason']='At least one explicit hard relation remains missing or partial; candidate familiarity does not entail it.';s['state_key']=key
write(P/'RESOLVED_REAUDIT.json',list(states.values()))
# Reclassify every old invented-requirement annotation in both rounds, preserving model/output mapping.
rows=[]
for stage in ['dynamic_progress','asymmetric_progress']:
 ap=ROOT/'experiments'/stage/'analysis';reviews=read(ap/'semantic_review.json');pack={x['review_id']:x for x in read(ap/'review_packets.json')}
 for rid,r in reviews.items():
  for u in r.get('units',[]):
   if 'invented_requirement' not in u.get('errors',[]):continue
   p=pack[rid];q=str(p['qid']);t=u['text'];lo=t.lower();cl='HARD_CONSTRAINT';verdict='valid_uncovered_hard_constraint';reason='Original Question explicitly limits target; old candidate-confidence redundancy is not verification coverage.'
   if 'best known' in lo or 'critically acclaimed' in lo:cl='AMBIGUOUS';verdict='sensitivity_only';reason='Ranking/praise has no reliable primary threshold; writing/directing Kinsey remains hard.'
   elif q=='580' and ('midway' in lo or 'final episodes' in lo or 'final episode' in lo) and not any(x in lo for x in ['roommate','sensitive issue','male lead','female lead']):cl='AMBIGUOUS';verdict='sensitivity_only';reason='Relative episode-position requirement is real, but exact cutoffs are unspecified; exclude numerical-cutoff disputes from primary.'
   elif q=='186' and any(x in lo for x in ['could not have','could have developed','timeline between','developer/publisher identity and timeline','required link between','timeline is unreconciled']):verdict='unsupported_incompatibility';reason='Later official incorporation does not logically preclude earlier credited development. A true founding-name gap does not rescue that inference.'
   elif q=='186' and ('1992' in lo and '1993' in lo) and not ('different name' in lo or 'formerly night sky' in lo or 'first establishment' in lo):verdict='extra_exact_year_reconciliation';reason='Both years satisfy early 1990s; November is explicitly observed. Record inconsistency without requiring an unasked unique year.'
   rows.append({'stage':stage,'review_id':rid,'qid':q,'unit_index':u['index'],'text':t,'old_errors':u['errors'],'classification':cl,'strict_verdict':verdict,'reason':reason})
write(P/'OVERDEMAND_REAUDIT.json',rows)
summary={'questions':len(ann),'qids':len(ann),'hard_counts':{q:sum(u['classification']=='HARD_CONSTRAINT' for u in x['units']) for q,x in ann.items()},'historical_resolved_occurrences':sum(len(s['occurrences']) for s in states.values()),'historical_resolved_unique_states':len(states),'strict_resolved_survivors':0,'reaudited_invented_requirement_units':len(rows),'verdict_counts':dict(collections.Counter(x['strict_verdict'] for x in rows)),'by_stage':{st:dict(collections.Counter(x['strict_verdict'] for x in rows if x['stage']==st)) for st in ['dynamic_progress','asymmetric_progress']},'review_limit':'Single reviewer, grouping-dependent counts; historical candidate exposure disclosed. No inter-rater reliability estimate.'}
write(P/'SUMMARY.json',summary);print(json.dumps(summary,ensure_ascii=False,indent=2))
