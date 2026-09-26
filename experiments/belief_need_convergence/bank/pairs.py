"""Controlled belief deltas from archived supported Claim additions."""
import copy,json,re,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def rd(n):return json.loads((P/'bank'/n).read_text())
def dg(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
I={r['belief_hash']:r for r in rd('INVENTORY.json')};T=rd('TRANSITIONS.json')
# QID, actual-claim matcher, atomic g, safe oracle A, different unresolved oracle B.
SPECS=[
('177',r'^Rangers International Football Club was founded in 1970\.$','Rangers founding year','Rangers founding year is not established.','Whether Rangers won a league during1973–1983 is not established.'),
('177',r'^Rangers International Football Club is a Nigerian professional football team based in Enugu, Nigeria\.$','Rangers base city','The city in which Rangers is based is not established.','Whether Rangers won a league during1973–1983 is not established.'),
('177',r"^Enugu Rangers. 2016 Nigeria Premier League title was their first championship since 1982\.$",'Rangers league title within1973–1983','Whether Rangers won a league during1973–1983 is not established.','Whether the2023 article attributes fifteen trophies to Rangers is not established.'),
('387',r'^Dean Dodrill animates on normal 8x11','Dean animation paper type','What kind of paper Dean Dodrill uses for animation is not established.','Whether Dean Dodrill created the intro and end animations of the described Game B is not established.'),
('387',r"^Dean [\"']Noogy[\"'] Dodrill was an animator for Jazz Jackrabbit 2\.$",'Dean animation credit on Jazz Jackrabbit2','Dean Dodrill possible game animation credits remain unestablished.','Whether his work specifically included intro and end animations remains unestablished.'),
('387',r"^PC Gamer.s .How I Game: Dean Dodrill. article, dated 24 July 2013, reported",'Dean July2013 PC storage','The July2013 storage capacity of Dean Dodrill gaming PC is not established.','Whether Dean Dodrill used the described animation paper byJuly2013 is not established.'),
('517',r'^Peter Nzioki played the role of Policeman 1 in the 2005 film The Constant Gardener\.$','Peter Constant Gardener role','Peter Nzioki exact role in The Constant Gardener is not established.','Peter Nzioki birth decade remains unestablished.'),
('517',r"^Peter King Nzioki Mwania was born on 25 May 1978 in Nairobi, Kenya; his father Michael David Mwania",'Peter parent occupations','Peter Nzioki parent occupations are not established.','Whether Peter Nzioki satisfies the Goat zodiac clue remains unestablished.'),
('517',r'^Bill Condon (?:wrote and directed Kinsey|directed Kinsey and also wrote its screenplay)\.$','Condon Kinsey writer-director relation','Whether Bill Condon both wrote and directed Kinsey remains unestablished.','The zodiac classification of Peter King remains unestablished.'),
('546',r'^Ding Junhui turned professional in 2003\.$','Ding professional debut','Ding Junhui professional debut year remains unestablished.','Whether Ding Junhui follows the specified2023 match sequence remains unestablished.'),
('1034',r"^Nick Mutuma.s first big break on Kenyan television came in 2008 when he was cast in Tabasamu\.$",'Nick first television break year','Nick Mutuma first television breakthrough year remains unestablished.','Whether Nick Mutuma had a US-born child by2021 remains unestablished.'),
('1034',r'^Nick Mutuma released his first single,', 'Nick debut single year','Nick Mutuma debut single year remains unestablished.','Whether Nick Mutuma held the described coordinator-to-manager employment sequence remains unestablished.')]
rows=[]
for n,(qid,pattern,g,oa,ob) in enumerate(SPECS,1):
    cand=[]
    for t in T:
        if t['qid']!=qid or not t['proposal']:continue
        a=I[t['before']]
        if n==5 and 'Dean' not in a['hypothesis']:continue
        for j,c in enumerate(t['proposal'].get('claims_to_add',[])):
            if re.search(pattern,c) and c not in a['claims']:cand.append((len(a['claims']),t['id'],j,t,c))
    assert cand,(qid,pattern)
    _,_,j,t,c=sorted(cand,key=lambda x:x[:3])[0];a=I[t['before']];before={k:copy.deepcopy(a[k]) for k in ['question','claims','hypothesis']};after=copy.deepcopy(before);after['claims'].append(c)
    rows.append({'pair_id':f'DC{n:02}','kind':'coverage','qid':qid,'A':before,'B':after,'target_gap':g,'oracle_A':oa,'oracle_B':ob,'real_added_claim':c,'observation':t['observation'],'actual_transition':{k:t[k] for k in ['id','path','pointer']},'actual_proposal_claim_index':j,'base_inventory_id':a['inventory_id'],'construction':'A is an actual archived PRE state. B adds exactly one supported historical Claim and holds H fixed, even when the original Writer changed H or added other Claims. Diagnostic only, never a natural primary state.'})
for n,sid in enumerate(['B006','B134','B201','B244'],1):
    s=next(r for r in I.values() if r['inventory_id']==sid);b={k:copy.deepcopy(s[k]) for k in ['question','claims','hypothesis']};a=copy.deepcopy(b);a['hypothesis']=''
    rows.append({'pair_id':f'DH{n:02}','kind':'hypothesis','qid':s['qid'],'A':a,'B':b,'target_gap':None,'actual_hypothesis_origins':s['origins'],'base_inventory_id':sid,'construction':'B is an actual supported historical Belief; A removes only H for a controlled diagnostic. Neither side introduces an invented candidate.'})
(P/'bank/DELTA_PAIRS_DRAFT.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
for r in rows:print(r['pair_id'],r['qid'],r['base_inventory_id'],len(r['A']['claims']),r.get('real_added_claim',r['B']['hypothesis']))
