"""Read-only, coordinate-bound audit of the previously completed U1 run."""
import collections,hashlib,json,re,statistics
from pathlib import Path
from annotations import F,COVERED,NEAR,CLAIM_OVERRIDES,PARTIAL_OVERLAP
P=Path(__file__).resolve().parent;OLD=P.parents[1]/'bcplus_verification'
def rd(p):return json.loads(p.read_text())
def wr(name,x):(P/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def ratio(n,d):return {'n':n,'d':d,'rate':n/d if d else None}
def norm(t):return re.sub(r'\W+',' ',t.lower()).strip()
def main():
 cs=rd(OLD/'RESULTS.json');oldwins={(w['case_id'],w['round'],w['wave']):w for w in rd(OLD/'analysis/WINDOW_REVIEW.json')};oldclaims={(w['case_id'],w['round'],w['wave'],w['claim_index']):w for w in rd(OLD/'analysis/CLAIM_REVIEW.json')};bank={c['case_id']:c for c in rd(OLD/'bank/VERIFICATION_BANK.json')}
 rows=[];ops=[];claims=[];found=set()
 for c in cs.values():
  for u in c['updates']:
   key=(c['case_id'],u['round']+1,u['wave']);o=u['observation'];out=u['proposal']['output'];new=out['claims_to_add'] if out else [];pre=[z['statement'] for z in u['pre_state']['claims']];jud=oldwins[key]
   r={'case_id':key[0],'qid':c['qid'],'arm':c['arm'],'round':key[1],'wave':key[2],'need':u['need'],'window_ref':o['window_ref'],'text_sha256':o['text_sha256'],'old_window_grade':jud['grade'],'new_claims':new,'off_need_opportunities':[],'already_covered_review':COVERED.get(key),'near_miss_review':NEAR.get(key),'exclusion_reason':None}
   for fact,h,coverage,idx,anchor in F.get(key,[]):
    found.add(key)
    if c['arm']=='V':assert h!=bank[c['case_id']]['constraint_id'],(key,h,'not off need')
    text=o['title'] if coverage=='title_only' else o['text'];m=re.search(anchor,text,re.I)
    assert m,(key,fact,anchor)
    admitted=idx is not None
    if admitted:assert 0<=idx<len(new),(key,idx)
    op={'opportunity_id':f'{key[0]}:{key[1]}:{key[2]}:{fact}','case_id':key[0],'arm':c['arm'],'round':key[1],'wave':key[2],'fact_key':fact,'question_condition_id':h,'coverage':coverage,'direct_support':True,'new_relative_to_pre_claims':True,'admitted_immediately':admitted,'admitted_claim_index':idx,'admitted_claim':new[idx] if admitted else None,'claim_whole_verdict':oldclaims.get((*key,idx),{}).get('verdict') if admitted else None,'support_channel':'title' if coverage=='title_only' else 'body','support_excerpt':m.group(0),'support_offset':m.start(),'observation_text_sha256':o['text_sha256'],'pre_claims':pre,'reason':'Direct observed fact is absent as a retained relation; partial facts do not close the full question condition.' if coverage=='component' else 'Direct full relation or counterexample is absent from retained Claims; only the supplied candidate/bridge is scored.'}
    if admitted and (*key,idx) in CLAIM_OVERRIDES:op['claim_whole_verdict']=CLAIM_OVERRIDES[*key,idx][0]
    ops.append(op);r['off_need_opportunities'].append(op['opportunity_id'])
   if not r['off_need_opportunities']:
    if key in COVERED:r['exclusion_reason']='Relevant fact already covered by pre-Claims; no new admission opportunity.'
    elif key in NEAR:r['exclusion_reason']=NEAR[key]
    elif jud['grade']=='i':r['exclusion_reason']='No directly supported off-Need fact for the supplied candidate/explicit question bridge: '+jud['reason']
    else:r['exclusion_reason']='Reviewed source offers current-Need evidence, already retained facts, a requested answer relation, or incomplete/unbound contextual clues; no additional direct off-Need hard-condition fact identified. '+jud['reason']
   rows.append(r)
   for j,t in enumerate(new):
    cr=oldclaims[*key,j];earlier=pre+new[:j]
    verdict,reason=CLAIM_OVERRIDES.get((*key,j),(cr['verdict'],cr['reason']))
    # Exact and whole-claim semantic duplicate review. No source conflict is a duplicate.
    exact=norm(t) in {norm(s) for s in earlier}
    claims.append({'case_id':key[0],'arm':c['arm'],'round':key[1],'wave':key[2],'claim_index':j,'statement':t,'verdict':verdict,'legacy_verdict':cr['verdict'],'verdict_changed_in_this_audit':verdict!=cr['verdict'],'unsupported_reason':reason if verdict!='supported' else None,'observation_text_sha256':o['text_sha256'],'pre_claims':earlier,'exact_duplicate':exact,'whole_claim_semantic_duplicate':exact,'partial_overlap_example':PARTIAL_OVERLAP.get((*key,j)),'duplicate_reason':'Exact normalized repetition.' if exact else 'Manual review found a new relation, value, date qualifier, source-conflicting date, or source attribution; shared clauses alone do not make the entire Claim redundant.'})
 assert found==set(F),(set(F)-found)
 assert len(rows)==318 and len(claims)==140
 def summary(arm=None,full=False,body=False):
  oo=[x for x in ops if (arm is None or x['arm']==arm) and (not full or x['coverage'] in ['full','title_only']) and (not body or x['support_channel']=='body')]
  bywin=collections.defaultdict(list);byfact=collections.defaultdict(list)
  for x in oo:bywin[x['case_id'],x['round'],x['wave']].append(x);byfact[x['case_id'],x['fact_key']].append(x)
  return {'fact_admission':ratio(sum(x['admitted_immediately'] for x in oo),len(oo)),'windows_with_any_admission':ratio(sum(any(x['admitted_immediately'] for x in xx) for xx in bywin.values()),len(bywin)),'windows_with_all_facts_admitted':ratio(sum(all(x['admitted_immediately'] for x in xx) for xx in bywin.values()),len(bywin)),'deduplicated_case_fact_ever_admitted':ratio(sum(any(x['admitted_immediately'] for x in xx) for xx in byfact.values()),len(byfact)),'coverage_counts':dict(collections.Counter(x['coverage'] for x in oo))}
 for op in ops:
  later=[x for x in ops if x['case_id']==op['case_id'] and x['fact_key']==op['fact_key'] and (x['round'],x['wave'])>=(op['round'],op['wave'])]
  op['admitted_by_later_scored_opportunity']=any(x['admitted_immediately'] for x in later)
 metrics={'audit_windows':len(rows),'window_arm_counts':dict(collections.Counter(x['arm'] for x in rows)),'all_direct_question_facts':summary(),'verification_direct_question_facts':summary('V'),'verification_full_conditions':summary('V',True),'verification_full_body_only':summary('V',True,True),'discovery_direct_question_facts':summary('D'),'claims':{'new_claims':len(claims),'verification_new_claims':sum(c['arm']=='V' for c in claims),'unsupported_strengthening':sum(c['verdict']!='supported' for c in claims),'exact_duplicate':sum(c['exact_duplicate'] for c in claims),'whole_claim_semantic_duplicate':sum(c['whole_claim_semantic_duplicate'] for c in claims)},'selection_note':'All318 observations screened; coordinate-bound positive/covered/near-miss judgments; V primary, Discovery separated. Requested-answer facts excluded from hard-condition recall. Single reviewer.'}
 wr('WINDOW_AUDIT.json',rows);wr('OPPORTUNITIES.json',ops);wr('CLAIM_AUDIT.json',claims);wr('METRICS.json',metrics)
 print(json.dumps(metrics,indent=2))
if __name__=='__main__':main()
