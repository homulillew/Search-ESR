"""Frozen single-reviewer corpus audit and selection; evaluator-only labels."""
import copy,json,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from extract import TOP,ROOT,rd,wr,doc,sh,dg
from relations import NEEDS,TERMS,CHALLENGE

# Semantic review of the mechanical full-source and visible-prefix screens.
# No model outputs from this study exist at this point.
K={
'VP01':('frontier_G4_T16_POST0','D3','list','The title list contains league wins in the interval; visible biography only gives founding/location, with no league-winning year.'),
'VP09':('frontier_G5_435:L0_START','D2','prose','Visible retrospective discusses 67 albums and a different career quote; the why-art interview is elsewhere in the same document.'),
'VP10':('BC_R1_VP07:V','D2','prose','Biography preview covers death/discography; human-rights activism is in its unseen introduction. Other windows do not establish this label.'),
'VP11':('BC_R2_D06:D','D10','prose','Filmography and career previews establish acting credits but not his parents occupations; biography has the parental relation.'),
'VP13':('BC_R1_VP14:V','D2','prose','Visible windows concern maximum breaks after 2006; first professional year is unseen in the known biography.'),
'VP14':('BC_R1_VN09:V','D1','mixed','Known maximum-break article has a Ding seven/latest-2024 bullet and table; visible sections cover historical trends, Williams and other players.'),
'VP18':('BC_R1_VP16:V','D2','prose','Visible Nick profile ends around early life; first-single paragraph is unseen. Siblings and career-break Claims do not establish music release.'),
'VN06':('BC_R1_D07:D','D3','prose','Williams biography contains the explicit Class of 92 sentence binding Ronnie to professional debut; visible tournament table does not.'),
'VN08':('BC_R1_D07:D','D3','mixed','Williams professional start is in prose and infobox; visible table is later tournament results, not professional debut.'),
'VN09':('BC_R1_D07:D','D3','mixed','Williams cumulative maximum count is in biography/infobox; visible tournament results do not give that count or its time bound.')}
N={
'VP01':('frontier_G5_177:L2_START','Squad-signing story says seven-time champions but provides no league-winning year. Full text does not support or refute the interval.'),
'VP03':('frontier_G5_186:L2_START','Complete MobyGames entry specifies one offline player, without an exhaustive mode list or exclusion of multiplayer. Strict only-single-player relation remains unresolved; this partial-source control is intentional.'),
'VN05':('frontier_G5_311:L1_START','Complete Hijitus document has no Brum mention and no Brum broadcast dates.'),
'VP08':('frontier_G4_T04_POST0','Complete Africanews article says more than 60 albums, never 67; the exact career count is not established.'),
'VP11':('BC_R1_D06:D','All five complete documents concern Iracema or Brazilian filmmakers. Neither Peter Nzioki nor Peter King occurs; soldier mentions refer to Brazilian filming/political events, not his father.'),
'VP13':('frontier_G5_546:L0_START','Complete Guardian match report gives the 2023 trousers incident/results and no professional-debut year.'),
'VP15':('frontier_G4_T05_POST0','Complete episode page establishes a season-4 episode, not an upper bound on the complete series season count.'),
'VP17':('frontier_G5_1034:L0_START','Complete source is about Heart Evangelista; Nick Mutuma does not occur, so her career date cannot answer the Need.')}
ANCHORS={
'VP01':('86072','* Nigeria Premier League','* Nigerian FA Cup'),
'VP09':('54137','Why do we sing',None),
'VP10':('30145','human rights activist',None),
'VP11':('67431','His father',None),
'VP13':('38231','In 2003, Ding turned professional',None),
'VP14':('64519','- 🌟 Ding Junhui: Ding has made 7 maximum breaks',None),
'VP18':('53719','In 2013, Mutuma released his first single',None),
'VN06':('4975','He is one of the three players collectively known',None),
'VN08':('4975','Williams became a professional player in 1992',None),
'VN09':('4975','Professional\t1992',None),
'VP06':('5266','8x11',None),
'VP12':('67431','| 2005 | The Constant Gardener | Policeman 1',None),
'VN01':('20521','writer:',None),
'VN03':('20521','first_aired:',None)}
def span(f):
 did,a,end=ANCHORS[f];t,u=doc(did);pos=t.index(a)
 if f=='VP09':start=max(0,t.rfind('\n\n',0,pos-1)+2);stop=t.find('\n\n',pos)+2
 elif f in ['VP10','VP11','VP13','VP18','VN06','VN08']:start=max(0,t.rfind('\n\n',0,pos)+2);stop=t.find('\n\n',pos)+2
 elif f in ['VN01','VN03','VN09']:start=max(0,pos-120);stop=min(len(t),pos+700)
 elif f=='VP06':start=max(0,pos-350);stop=min(len(t),pos+500)
 elif end: start=pos;stop=t.index(end,pos)
 else:start=pos;stop=t.find('\n',pos)+1
 if stop<=start:stop=min(len(t),pos+700)
 return {'docid':did,'url':u,'document_sha256':sh(t),'offset':start,'end':stop,'text':t[start:stop],'text_sha256':sh(t[start:stop])}
def main():
 prefixes={p['checkpoint_id']:p for p in rd(TOP/'bank/PREFIX_INVENTORY.json')}
 old={r['case_id']:r for r in rd(ROOT/'experiments/bcplus_verification/bank/VERIFICATION_BANK.json')}
 runtime=[];labels=[]
 for bank,sel in [('K',K),('N',N)]:
  for f,values in sorted(sel.items()):
   p=copy.deepcopy(prefixes[values[0]]);cid=bank+'_'+f
   runtime.append({'case_id':cid,'qid':p['qid'],'question':p['question'],'claims':p['claims'],'hypothesis':p['hypothesis'],'attempts':p['attempts'],'registry':p['registry'],'need':NEEDS[f]})
   lab={'case_id':cid,'family':f,'bank':bank,'qid':p['qid'],'checkpoint_id':p['checkpoint_id'],'provenance':p['provenance'],'prefix_sha256':dg(runtime[-1]),'need_sha256':sh(NEEDS[f]),'origin':p['origin'],'reason':values[-1],'structure':values[2] if bank=='K' else 'not_applicable','relation_category':old[f]['category'],'gold_doc_ref':values[1] if bank=='K' else None,'reference_spans':[span(f)] if bank=='K' else old[f]['reference_evidence']}
   if f=='VP03':
    t,u=doc('22411');pos=t.index('No Multiplayer');lab['reference_spans']=[{'docid':'22411','url':u,'offset':max(0,pos-30),'text':t[max(0,pos-30):pos+40],'document_sha256':sh(t)}]
   if bank=='K':
    d=next(d for d in p['registry']['documents'] if d['doc_ref']==values[1]);assert d['docid']==lab['reference_spans'][0]['docid']
   labels.append(lab)
 challenge=rd(ROOT/'experiments/bcplus_verification/exploration/INPUTS.json')
 for f in sorted(CHALLENGE):
  if f=='VN03':p=prefixes['BC_R1_VN03:V']
  else:p=next(c for c in challenge.values() if c['case_id']==f)
  cid='C_'+f;v={k:copy.deepcopy(p[k]) for k in ['qid','question','claims','hypothesis','attempts','registry']};v.update(case_id=cid,need=NEEDS[f]);runtime.append(v)
  gold='D4' if f=='VN07' else 'D1'
  source=span('VN06') if f=='VN07' else span(f)
  labels.append({'case_id':cid,'family':f,'bank':'challenge','qid':p['qid'],'checkpoint_id':'previous_exploration_input' if f!='VN03' else 'BC_R1_VN03:V','provenance':{'path':'experiments/bcplus_verification/exploration/INPUTS.json','case_id':f} if f!='VN03' else p['provenance'],'prefix_sha256':dg(v),'need_sha256':sh(NEEDS[f]),'reason':'Previously analyzed failure; excluded from all fresh gates. Exact prefix reused without cleaned Claims or Hypothesis.','gold_doc_ref':gold,'structure':'table' if f in ['VP12','VN01','VN03'] else 'prose','reference_spans':[source]})
 wr(TOP/'bank/RUNTIME_INPUTS.json',runtime);wr(TOP/'bank/LABELS.json',labels)
 wr(TOP/'bank/QUERY_LEXICONS.json',{f:{'entity':a,'relation':b,'match':'case-insensitive regex presence only; never query quality score'} for f,(a,b) in TERMS.items()})
 audits=[]
 for r in runtime:
  lab=next(l for l in labels if l['case_id']==r['case_id'])
  for d in r['registry']['documents']:
   t,u=doc(d['docid']);assert sh(t)==d['document_sha256']
   ent=TERMS[lab['family']][0];rel=TERMS[lab['family']][1]
   audits.append({'case_id':r['case_id'],'doc_ref':d['doc_ref'],'docid':d['docid'],'document_sha256':sh(t),'full_document_chars':len(t),'audit_scope':'complete corpus bytes, not visible previews','entity_occurrences':[m.start() for m in re.finditer(ent,t,re.I)],'relation_occurrences':[m.start() for m in re.finditer(rel,t,re.I)],'contains_exact_relation':False if lab['bank']=='N' else True if d['doc_ref']==lab['gold_doc_ref'] else None,'reason':lab['reason'] if lab['bank']=='N' or d['doc_ref']==lab['gold_doc_ref'] else 'Not required for K eligibility; unreviewed alternative source, not asserted negative.'})
 wr(TOP/'bank/SOURCE_AUDIT.json',audits)
 wr(TOP/'bank/SELECTION.json',{'K':len(K),'K_qids':len({old[f]['qid'] for f in K}),'N':len(N),'N_qids':len({old[f]['qid'] for f in N}),'challenge':5,'shortfall':'K has 10 unique Need families across 5 qids, below requested 12 / 6. No synthetic insertion, repeated equivalent prefix, or new Need family used. Gates remain descriptive with this limited fresh coverage.','N_rule_clarification':'Within each qid prefer the smallest eligible Workspace family, then family ID; chosen before any new model output. Eight qids, one each.','eligibility_exclusions':{'VP16':'Non-exhaustive sibling source','VN12':'Conflicting birth-year sources','VP02/VP04':'Exact release/shareware already visible when an exact source is known','VP03':'No-multiplayer source already visible whenever discovered; MobyGames alone is partial','VP05':'Exact game credits already visible; company 3079 collaborator list does not bind all names to this game','VP07/VP08':'Exact age/count already visible or retained in Claims when exact source known','VP15':'Exact total already visible when series overview known','VP17':'Break year visible in IMDb even when Wikipedia query preview misses it','VN02/VN04':'Broadcast year/network already visible via other snippets/Claims','VN05':'Exact Brum date source already visible when known','VN10':'Initial ESPN preview already shows PSG opening scoring and later equalising; a refutation need not await all goal minutes','VN06_false_screen':'OLBG Class-of-92 reference is about Higgins/Williams, not a bound Ronnie debut-year statement'},'screening_caveat':'Regex screens are aids, not semantic judgments. Unselected unknown sources are not labeled absent. Single Codex reviewer, not independent inter-rater validation.'})
 print('K',len(K),'N',len(N),'C',5)
 for r in labels:
  if r['bank']!='N':print(r['case_id'],r['reference_spans'][0]['text'][:700])
if __name__=='__main__':main()
