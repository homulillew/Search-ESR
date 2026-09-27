"""Certificate-level frozen verdict scores; reason review is diagnostic only."""
from .common import *

def aggregate(rows,refs):
 out={}
 for arm in ('Q0','Q1'):
  rs=[r for r in rows if r['arm']==arm];tp=fp=tn=pos=neg=valid=0;bind_fp=bind_n=qual_fp=qual_n=full_fp=full_n=euler_fp=euler_n=book_fp=book_n=0
  for r in rs:
   c=refs[r['certificate_id']];yes=c['gold_verdict']=='SUBTRACTABLE';ok=r['valid_output'];accept=ok and r['output']['verdict']=='SUBTRACTABLE';reject=ok and r['output']['verdict']=='NOT_SUBTRACTABLE'
   pos+=yes;neg+=not yes;valid+=ok;tp+=yes and accept;fp+=(not yes) and accept;tn+=(not yes) and reject
   if c['category']=='binding_missing':bind_n+=1;bind_fp+=accept
   if c['category']=='qualifier_incomplete':qual_n+=1;qual_fp+=accept
   if c['false_full_risk']:full_n+=1;full_fp+=accept
   if 'Euler' in c['case_tags']:euler_n+=1;euler_fp+=accept
   if 'book_article' in c['case_tags']:book_n+=1;book_fp+=accept
  by={(r['certificate_id'],r['replicate']):r for r in rs};pairs=[]
  for cid in sorted({r['certificate_id'] for r in rs}):
   if (cid,1) in by and (cid,2) in by:pairs.append((by[cid,1],by[cid,2]))
  agreement=sum(a['valid_output'] and b['valid_output'] and a['output']['verdict']==b['output']['verdict'] for a,b in pairs)
  out[arm]={'planned':len(rs),'valid_outputs':valid,'invalid_or_missing':len(rs)-valid,'TP':tp,'FP':fp,'TN':tn,'missed_positives':pos-tp,'subtraction_precision':metric(tp,tp+fp),'subtraction_recall':metric(tp,pos),'hard_negative_rejection':metric(tn,neg),'hard_negative_false_acceptance':metric(fp,neg),'binding_missing_false_acceptance':metric(bind_fp,bind_n),'qualifier_incomplete_false_acceptance':metric(qual_fp,qual_n),'false_full_risk_acceptance':metric(full_fp,full_n),'false_full_risk_acceptance_count':full_fp,'Euler_false_acceptance_count':euler_fp,'Euler_denominator':euler_n,'book_article_false_acceptance_count':book_fp,'book_article_denominator':book_n,'schema_validity':metric(valid,len(rs)),'replicate_verdict_agreement':metric(agreement,len(pairs)),'exact_reference_verdict':metric(tp+tn,len(rs))}
 return out

def gate(metrics):
 cfg=read(P/'GATES.json');q=metrics['Q1'];checks={}
 for name,threshold in cfg['E1_Q1'].items():
  key,op=name.rsplit('_',1);raw=q[key];v=raw['value'] if isinstance(raw,dict) else raw
  checks[name]=v is not None and (v>=threshold if op=='min' else v<=threshold)
 p0=metrics['Q0']['subtraction_precision']['value'];p1=q['subtraction_precision']['value'];r0=metrics['Q0']['subtraction_recall']['value'];r1=q['subtraction_recall']['value']
 comp={'precision':p0 is not None and p1 is not None and p1>=p0,'recall':r0 is not None and r1 is not None and r1>=r0-.05}
 return {'absolute_checks':checks,'comparative_checks':comp,'Q1_absolute_pass':all(checks.values()),'E1_PASS':all(checks.values()) and all(comp.values()),'E2_eligible':all(checks.values()) and all(comp.values()),'E2_authorized':False}

def validate_judgment(j):
 assert set(j)=={'reason','diagnostic','missing_semantics_fidelity','ambiguity'}
 assert isinstance(j['reason'],str) and j['reason'].strip()
 assert j['diagnostic'] in ('consistent','local_fact_missing','semantic_binding_missing','qualifier_or_scope_missing','other')
 assert j['missing_semantics_fidelity'] in ('faithful','partly_faithful','unfaithful','not_applicable')
 assert type(j['ambiguity']) is bool

def results():
 from .run import OUT,load_rows
 seal=read(OUT/'review/REVIEW_SEAL.json');key=read(OUT/'review/KEY.json');judgments=read(OUT/'review/JUDGMENTS.json');committed(OUT/'review/REVIEW_SEAL.json')
 for path,h in seal['files'].items():assert sha(ROOT/path)==h;committed(ROOT/path)
 rows=load_rows();refs={c['certificate_id']:c for c in read(P/'e0_reference/CERTIFICATES.json')};assert set(key)==set(judgments) and set(key.values())=={r['id'] for r in rows}
 inv={v:k for k,v in key.items()}
 ledger=[]
 for r in rows:
  j=judgments[inv[r['id']]];validate_judgment(j);c=refs[r['certificate_id']]
  ledger.append({'id':r['id'],'certificate_id':r['certificate_id'],'cell_id':r['cell_id'],'arm':r['arm'],'replicate':r['replicate'],'gold':c['gold_verdict'],'predicted':r['output']['verdict'] if r['valid_output'] else None,'failure':r['failure'],'judgment':j})
 primary=aggregate(rows,refs)
 return {'primary':primary,'gate':gate(primary),'by_category':{cat:aggregate([r for r in rows if refs[r['certificate_id']]['category']==cat],refs) for cat in sorted({c['category'] for c in refs.values()})},'by_qid':{q:aggregate([r for r in rows if r['qid']==q],refs) for q in sorted({r['qid'] for r in rows})},'by_replicate':{str(k):aggregate([r for r in rows if r['replicate']==k],refs) for k in (1,2)},'nonambiguous_sensitivity':aggregate([r for r in rows if not refs[r['certificate_id']]['ambiguity_reason']],refs),'ledger':ledger}

def main():
 a=results();assert a==results();write(P/'e1_qualification/METRICS.json',a);write(P/'analysis/ERROR_LEDGER.json',a['ledger']);write(P/'analysis/SENSITIVITY.json',a['nonambiguous_sensitivity']);print(json.dumps(a['gate'],indent=2))
if __name__=='__main__':main()
