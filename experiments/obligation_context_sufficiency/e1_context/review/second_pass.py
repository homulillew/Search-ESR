"""Post-commit pair transcription; first-pass judgments remain immutable."""
from experiments.obligation_context_sufficiency.common import *
from experiments.obligation_context_sufficiency.run import OUT,load_rows
from experiments.obligation_context_sufficiency.score import strict
import subprocess
path=OUT/'review/FIRST_PASS.json'
assert subprocess.check_output(['git','show','HEAD:'+rel(path)],cwd=ROOT)==path.read_bytes()
key=read(OUT/'review/KEY.json');labels={key[x['review_id']]:x for x in read(path)};rows={r['id']:r for r in load_rows()}
manual={}
def pairs(cid,arms,relation,reason):
 for a in arms.split():manual[cid,a]=(relation,reason)
pairs('G03','C0','different_but_valid','One chooses either authors other JBSE paper; the other chooses paper identity through table/emotion content.')
pairs('G03','C1','same_obligation','Both check the identified papers total table count against six.')
pairs('G03','C2','compatible_obligation','Both check total tables; the second explicitly permits determining the actual count if not six.')
pairs('G04','CDELTA','compatible_obligation','Same generic gift-funded building identity, with complementary complex versus university-association wording.')
pairs('G04','C1','different_but_valid','Founder identity and building identity are separate unresolved branches.')
pairs('G08','C0','different_but_valid','Partner/interview source discovery versus accident geography/timing comparison.')
pairs('G09','CDELTA C1','same_obligation','Both identify the song referent of the concrete immaterial-girl quote.')
pairs('G10','C0 C1','same_obligation','Same author identity via promotion, degree institution and Canadian PhD profile.')
pairs('G10','C2','compatible_obligation','Same academic author identity, with additional supervisor-biography conditions in one response.')
pairs('G12','C0','different_but_valid','Supervisor identity/profile versus a broader author academic-profile test including an independent promotion/degree branch.')
pairs('G12','CDELTA','same_obligation','Same known authors promotion/same-university-degree relation.')
pairs('G12','C1','compatible_obligation','Supervisor identity with biography versus testing the supervisor-role biographical profile; same bounded relationship.')
pairs('G12','C2','different_but_valid','Promotion/degree institution versus Iranian supervisor identity.')
pairs('G18','CDELTA','same_obligation','Same two report years and different-year/2010s condition.')
pairs('G18','C1','different_but_valid','First report country/founding condition versus the pair publication-year relation.')
pairs('G18','C2','compatible_obligation','Same first-report country qualification, one also asks its publication year.')
pairs('G19','C0','compatible_obligation','Same DLC/base-game identification, explicit base-game naming added in one.')
pairs('G20','C0 CDELTA C1 C2','same_obligation','Same DLC identity from established EU4 game plus release/mechanics profile.')
pairs('G21','CDELTA C2','same_obligation','Same identified advisors two California degrees and2020 monograph.')
pairs('G23','C0 CDELTA C1 C2','same_obligation','Same known championship event host university.')
pairs('G24','C0 CDELTA C1 C2','same_obligation','Same country relation between Mingyang Deng and Xiao Mao, not Jerry Mao.')
pairs('G25','C0 CDELTA C1','compatible_obligation','Same letter identity through date/delivery profile with compatible participant/topic detail differences.')
pairs('G25','C2','same_obligation','Same letter date/delivery identity profile.')
pairs('G26','CDELTA C2','same_obligation','Same region content of the identified King Michael letter, keeping cover memo date separate.')
pairs('G27','CDELTA','compatible_obligation','Same final courier identity, with nickname qualification added by one response.')
pairs('G27','C1 C2','same_obligation','Same final delivering official and recipient nickname profile.')
output=[]
for cid in bank():
 for a in ARMS:
  rr=[rows[f'{a}__{cid}__R{i}'] for i in (1,2)];n=sum(strict(r,labels[r['id']]) for r in rr)
  if n==2:relation,reason=manual.pop((cid,a))
  else:relation='one_valid_one_invalid' if n==1 else 'both_invalid';reason='Derived from the committed individual validity judgments; no semantic stability credit for any invalid response.'
  output.append({'case_id':cid,'arm':a,'relation':relation,'reason':reason,'review_ids':[labels[r['id']]['review_id'] for r in rr]})
assert not manual
write(OUT/'review/PAIR_REVIEW.json',output)
