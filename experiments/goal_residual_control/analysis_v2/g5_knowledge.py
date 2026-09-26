"""Reviewer-authored knowledge ledger from literal committed Claims, by round.
Not an online updater. Raw source support and Hypothesis never populate this map.
"""
from progress import *

# Additions after round 0, reviewed from the actual post-state Claim sentences.
R0={
 '546:L0':['ding_maximum_threshold','ma_centuries','williams_centuries'],
 '546:L1':['ding_counts','ding_maximum_threshold','ding_british','ding_british_win','ding_british_loss'],
 '546:L2':[],
 '1094:L0':['scienza_candidate'],
 '1094:L1':['scienza_candidate','messi_timing'],
 '1094:L2':['scienza_candidate','messi_timing'],
 '517:L0':['peter_police','condon_estate','meirelles_gardener','condon_kinsey'],
 '517:L1':['peter_police'],
 '517:L2':['meirelles_iracema','condon_estate','condon_kinsey'],
 '435:L0':['tuku_activist','tuku67','wasakara','forbes_edition'],
 '435:L1':[],
 '435:L2':['tuku67','wasakara','forbes_edition'],
 '580:L0':[], '580:L1':[], '580:L2':[],
 '177:L0':[], '177:L1':['rangers_founded','rangers_2016_excluded'], '177:L2':['rangers_founded','rangers_2016_excluded'],
 '1034:L0':[], '1034:L1':[], '1034:L2':[],
 '311:L0':[], '311:L1':[], '311:L2':['brum_candidate'],
 '186:L0':['galacta_company_history','galacta_company'],
 '186:L1':['galacta_company_history','galacta_company'], '186:L2':[],
 '387:L0':[], '387:L1':['dean_paper','dean_jazz'], '387:L2':['dean_jazz']
}
# Filled only after later actual states are reviewed.
R1={
 '546:L0':['ding_british_win'], '546:L2':[],
 '1094:L0':['milan_candidate','kroos_candidate'],
 '1094:L1':['kroos_candidate'],
 '1094:L2':['kroos_candidate','milan_candidate','dons_origin','newcastle_origin','scunthorpe_origin','stoke_origin'],
 '517:L0':['meirelles_iracema'], '517:L2':['peter_police','meirelles_gardener'],
 '435:L0':['tuku_quote'], '435:L2':[],
 '177:L0':[], '177:L2':['rangers_league_period'],
 '1034:L0':['kloss_candidate'], '1034:L1':[], '1034:L2':[],
 '311:L0':['cococinel_candidate'], '311:L2':[], '387:L2':['jazz_release']
}
R2={}

def build():
 b=TOP/'three_round_loop_v2';cells=read(b/'results.json');judgments=read(b/'LOOP_ADJUDICATION.json');knowledge={};closure={};ledger=[]
 for key,c in cells.items():
  known=seed_tags(c['seed_snapshot'])
  for di,d in enumerate(c['decisions']):
   k=key+':'+str(di)+':'+c['arm'];knowledge[k]=sorted(known)
   rr=judgments[key]['resolved_after_round'];closure[k]=rr is not None and di>rr
   ledger.append({'cell':key,'round':di,'knowledge_tags':sorted(known),'resolved_before':closure[k],'basis':'Independent review of literal committed Claims; no automatic promotion from source text or working hypothesis.'})
   if di<2:
    additions=[R0,R1][di]
    if any(z['round']==di for z in c['updates']):assert key in additions,('missing later state review',key,di)
    known.update(additions.get(key,[]))
 write(b/'KNOWLEDGE_REVIEW.json',ledger)
 return knowledge,closure

if __name__=='__main__':
 knowledge,closure=build();score('three_round_loop_v2',knowledge,closure)
