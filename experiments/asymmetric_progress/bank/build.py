"""Frozen pre-call, Q+Claims-only selection and single-reviewer labels."""
import copy,json,hashlib
from pathlib import Path
T=Path(__file__).resolve().parents[1]; R=T.parents[1]
def rd(p):return json.loads(p.read_text())
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
pool={c['pool_id']:c for c in rd(T/'bank/ELIGIBLE_POOL.json')}
# All five remaining resolved states, one diagnostic attribution join, then
# qid coverage and within-qid evidence-depth spread. Chosen before any new call.
selected=[1,2,6,8,9,10,16,17,18,19,21,23,24,25,27,29,30,31,32,33,38,39,42,43]
primary=[]
for i,k in enumerate(selected,1):
 c=copy.deepcopy(pool[f'E{k:02}']);c.update(case_id=f'A{i:02}',set='primary');primary.append(c)
challenge=[]
for bank,ids in [('PRIMARY',['P17','P19']),('CHALLENGE',['C04','C06','C07','C08','C10','C12','C15'])]:
 for oldid in ids:
  c=copy.deepcopy(next(x for x in rd(R/f'experiments/dynamic_progress/bank/{bank}.json') if x['case_id']==oldid))
  c.update(case_id=f'S{len(challenge)+1:02}',set='challenge',prior_case_id=oldid,prior_bank=bank,
   challenge_provenance=f'experiments/dynamic_progress/bank/{bank}.json#{oldid}')
  challenge.append(c)
wr(T/'bank/PRIMARY.json',primary);wr(T/'bank/CHALLENGE.json',challenge)

def g(text,refs=(),status='missing'):return dict(gap=text,claim_refs=list(refs),status=status)
def label(c):
 q=c['qid'];e=c.get('pool_id');old=c.get('prior_case_id');cs=c['state']['verified_claims']
 out=dict(case_id=c['case_id'],qid=q,gold_resolved=False,acceptable_single_relation_blockers=[],
  known_invalid_joins=[],known_unsupported_assumptions=[],minimal_closure_support_families=[],
  near_closure=False,material_claim_conflict=False,materiality_notes=[],
  review_basis='Only original question and numbered current Claim statements. No Hypothesis, history, source bodies, future or gold answer.')
 gs=[];joins=[];assum=[];families=[]
 if q=='177':
  gs=[g('The candidate club is not established as based in the required capital city.',[1],'partial'),g('The qualifying 2023 article is not established as reporting fifteen trophies for this club.',[1],'partial')]
  if e=='E01':gs.append(g('The founding year of the qualifying club is not established.'))
  joins=['13 signings does not entail fifteen trophies or capital-city status.','A club name/founding year does not qualify the club against the identifying conditions.']
  assum=['Enugu is the required capital; Rangers satisfies the whole table pattern.']
 elif q=='311':
  if old=='C06':
   gs=[g('The total episode count for the candidate programme is not reconciled between 52 and 78.',[28,35],'conflict'),g('The programme end year is inconsistent across current Claims.',[27,35,37],'conflict'),g('The candidate episode duration is not established as below five minutes.',[28],'partial')]
   out['material_claim_conflict']=True
  else:gs=[g('No candidate programme is bound to the required two-writer credit.',[1],'partial'),g('The Argentine release title of the qualifying programme remains unestablished.')]
  joins=['Facts from different programmes do not qualify one programme.','An Argentine alias alone does not resolve material run/count conflicts.']
  assum=['Hijitus satisfies the question despite the stated writer/run mismatch.','Question-vs-Claim mismatch is itself an inter-Claim conflict.']
 elif q=='387':
  gs=[g('The PC owner is not established as responsible specifically for Game B intro and end animations.',[1],'partial'),g('The PC storage description is not bound to 25 July 2013.',[1],'partial'),g('The same company is not bound to the required Game A to Game B release interval.')]
  joins=['Generic artist/animator credit does not entail intro/end animation responsibility.','5 TB plus a wireless keyboard does not establish the required dated PC or qualified owner.']
  assum=['Dean is already the fully qualified target.','Dust is established as Game A.']
 elif q=='435':
  if e in ['E16','E17','E18']:
   out['gold_resolved']=True
   families=[{'relation':'Discriminative musician identity through age, activism and Wasakara/career facts.','claim_refs':[1,3,5,6]}, {'relation':'Album count directly attributed to the May 2017 Forbes Africa feature.','claim_refs':[7]}]
  else:
   gs=[g('The album count is not directly bound to the specified May Forbes Africa feature.',[11,12],'partial')];out['near_closure']=True
  joins=['A separate 65-album statement and May 2017 Forbes listing do not establish count at that feature.','Career total 67 does not entail a May feature total.']
  assum=['The requested count is already established by a temporal/attribution join.']
  out['materiality_notes']=['Discriminative biographical identity plus directly dated final count suffices; do not demand separate redundant first-album/quotation corroboration.']
 elif q=='517':
  gs=[g('The candidate is not established as born under the Chinese zodiac Goat sign.',[1],'partial')]
  if e in ['E21','E23']:gs.append(g('Meirelles is not bound to the Iracema filmmaking-inspiration relation.'))
  if e=='E24':gs.append(g('Peter King is not established as the policeman in The Constant Gardener.',[3],'partial'))
  out['near_closure']=old=='C12'
  joins=['A birth year without a zodiac mapping does not establish the Goat condition.','An appearance credit does not establish a policeman role.']
  assum=['Outside calendar knowledge establishes Horse or a specific Goat-year list.','Candidate identity is qualified despite missing zodiac binding.']
 elif q=='546':
  gs=[g('The candidate is not bound to the question\'s consecutive 2023 match sequence.'),g('The final losing opponent\'s century count is not established above 400 at the specified cutoff.'),g('The candidate\'s professional debut is not established within 1995–2006.')]
  joins=['Results from different tournaments or years do not form a consecutive 2023 sequence.','Career totals for one player do not qualify another player.']
  assum=['Ding is already the qualified player.','The observed 4–3 win establishes all later matches.']
  out['materiality_notes']=['A single next-match relation is valid; a whole four-match chain bundled with career conditions is broad. The consecutive sequence itself is one ordered-event relation if not bundled with independent player biography/counts.']
 elif q=='580':
  if e in ['E31','E32']:
   out['gold_resolved']=True
   families=[{'relation':'Season-one date and season-four family visit identify the series.','claim_refs':[1,4]}, {'relation':'Season-three sacrifice bound to the male lead\'s roommate.','claim_refs':[2,3]}, {'relation':'Total seasons below ten.','claim_refs':[6 if e=='E31' else 5]}]
  elif old=='P19':
   gs=[g('Edgar is not established as the male lead\'s roommate.',[7],'partial')];out['near_closure']=True
  elif old=='C15':
   gs=[g('The series total number of seasons is not established below ten.')];out['near_closure']=True
  else:
   gs=[g('The series total number of seasons is not established below ten.'),g('A late-season-three sacrifice has not been bound to the male lead\'s roommate.')]
  joins=['A season-four/five appearance is not a total-season upper bound.','Edgar\'s sacrifice alone does not establish his roommate role.','One distinctive episode does not establish remaining material role/quantity bindings.']
  assum=['Edgar is known to be Jimmy\'s roommate without a supporting Claim.']
 elif q=='1034':
  gs=[g('A candidate is not bound to a 2012 coordinator appointment.'),g('The qualifying individual\'s birth name is not established.'),g('A candidate is not bound to university admission for Business Administration within 2001–2007.')]
  joins=['Generic career-outcome job titles do not establish a specific person\'s appointment.','Several unrelated biographies do not qualify one person.','Wealthy family does not establish showbiz as the main source of personal wealth.']
  assum=['Heart Evangelista or another merely mentioned celebrity is the established target.']
 elif q=='1094':
  gs=[g('No observed fixture is established as involving the club born from the specified discord.'),g('No observed fixture binds the scoring-phase pattern and the required 95th-minute free kick.')]
  joins=['The Milan/Liverpool half-time pattern and a different fixture\'s 95th-minute event cannot be joined.','PSG scored late goals in the Claims, so its early lead does not satisfy all-goals-early.']
  assum=['The 2005 final already contains a 95th-minute free kick.','Messi\'s known event establishes the queried fixture.']
 elif q=='186':
  assert old=='C04';out['gold_resolved']=True
  families=[{'relation':'November early-1990s DOS single-player shareware game.','claim_refs':[1]}, {'relation':'Credits with two shared surnames.','claim_refs':[2]}, {'relation':'Amphibian-named developer with former name and establishment.','claim_refs':[3,4,9,10]}]
  out['materiality_notes']=['Retain previous frozen materiality: 1992/1993 both fit requested early-1990s range; no additional corporate chronology reconciliation needed to identify game.']
 out.update(acceptable_single_relation_blockers=gs,known_invalid_joins=joins,known_unsupported_assumptions=assum,minimal_closure_support_families=families)
 out['reason']='Direct supporting relation families establish closure.' if out['gold_resolved'] else 'At least one material relation listed above is not established by current Claims.'
 return out
for name,bank in [('PRIMARY',primary),('CHALLENGE',challenge)]:wr(T/f'bank/{name}_LABELS.json',{c['case_id']:label(c) for c in bank})
pair={c['case_id']:{'L1_primary':1+int(hashlib.sha256(c['case_id'].encode()).hexdigest(),16)%2,'Audit_primary':1+int(hashlib.sha256((c['case_id']+':audit').encode()).hexdigest(),16)%2} for c in primary+challenge}
wr(T/'bank/PAIRING.json',pair)
wr(T/'bank/SELECTION.json',{'primary_pool_ids':[f'E{k:02}' for k in selected],'rule':'Pre-call Q+Claims semantic strata; all five resolved, one attribution case under q435 cap, every eligible qid, depth-spread exemplars. Not random sampling. No new outcomes used.', 'primary_n':24,'qids':9,'unresolved':19,'resolved':5,'resolved_qids':2,'max_per_qid':4,'near_closure_strict_n':1,'near_closure_strict_qids':1,'near_closure_definition':'Strong candidate with only one clearly remaining material relation family. E23/E30 each have at least two; not counted.', 'shortfalls':['6 resolved target unavailable: only 5 remaining fresh controls.','10–12 near-closure/5-qid target unavailable; actual 1/1 in selected fresh bank.','No material inter-Claim conflict in fresh primary; covered only in separate S04 stress.'],'challenge_n':9,'challenge_resolved':1,'challenge_note':'Prior P17/P19 plus C06,C07,C08,C10,C12,C15 failure stress and C04 known over-demand resolved control. No primary denominator pooling.'})
wr(T/'bank/POOL_REVIEW.json',{k:{'gold_resolved':k in ['E16','E17','E18','E31','E32'],'selected':k in [f'E{i:02}' for i in selected],'reason':'All current Q+Claims reviewed; unselected states are redundant within-qid trajectories under cap/budget; no remaining additional resolved state.'} for k in pool})
print('primary',len(primary),'challenge',len(challenge))
