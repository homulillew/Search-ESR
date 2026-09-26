"""Stage-local, reviewer-authored additions; never revise earlier stage labels."""
from progress import *

b=TOP/'three_round_loop_v2'
p=b/'evidence_labels.json'
labels=read(p) if p.exists() else read(TOP/'analysis_v2/EVIDENCE_LABELS.json')
defs=read(TOP/'analysis_v2/FACT_DEFINITIONS.json')
defs.update({
 'coco_argentine':{'kind':'direct','belief_update':'Cococinel was released in Argentina as Cocomiel.','next_decision':'Verify the remaining program-identification conjunction; a release-name relation alone is not closure.'},
 'coco_runtime':{'kind':'direct','belief_update':'Allocine reports four-minute episodes for Cococinel.','next_decision':'Reconcile the earlier four-to-ten-minute runtime and distinguish seasons before closure.'},
 'coco_network':{'kind':'direct','belief_update':'Cococinel aired on TF1, a three-character network containing a digit.','next_decision':'Verify cast, educational purpose and date/episode scope.'},
 'coco_credits':{'kind':'direct','belief_update':'Cocomiel credits Raymond Burlet as director and Yolande Baillet and Jean Montagne as writers.','next_decision':'Check the remaining character and schedule conditions rather than closing from the requested title alone.'},
 'coco_education':{'kind':'direct','belief_update':'The observed French synopsis explicitly describes teaching children about nature protection.','next_decision':'Verify the remaining program-character and schedule constraints.'},
 'newcastle_arsenal_candidate':{'kind':'decision','belief_update':'The 2011 Newcastle–Arsenal 4–4 fixture had Arsenal four goals by minute 26 and Newcastle four goals from minute 68 onward.','next_decision':'Inspect the precise late free-kick event and origins; do not equate a scoring pattern with a complete match identification.'},
 'scienza_candidate':{'kind':'decision','belief_update':'Scienza scored a 95th-minute equalising free kick for Heidenheim.','next_decision':'Inspect this alternative fixture and club histories; timing alone does not identify the requested match.'},
 'brum_candidate':{'kind':'decision','belief_update':'Brum is a living car in an observed UK animation list covering 1990–2009.','next_decision':'Test this alternative against schedule, short runtime, other characters and Argentinian title; no full match is established.'},
 'ma_centuries':{'kind':'direct','belief_update':'The observed career table gives Ma Hailong nine centuries, including 2023/24 and 2024/25.','next_decision':'This bounds the earlier count below 250, but the rest of the tournament sequence remains unverified.'},
 'williams_centuries':{'kind':'decision','belief_update':'Williams has over 600 career centuries in the observed biography that also includes events after January 2025.','next_decision':'He remains a plausible high-century opponent; establish the as-of-30-January-2025 count rather than assuming a later total is contemporaneous.'},
 'rangers_league_period':{'kind':'direct','belief_update':'Rangers had a league championship in 1982, within the requested 1973–1983 range.','next_decision':'Verify the table/points/trophy conjunction rather than closing from founding and one title alone.'},
 'ding_british_win':{'kind':'decision','belief_update':'Ding beat Julien Leclercq 4–0 on 27 September 2023 at the British Open.','next_decision':'Inspect adjacent rounds of this alternative tournament; one win does not establish the whole chain.'},
 'ding_british_loss':{'kind':'decision','belief_update':'Ding lost 2–4 to Williams after the Leclercq win at the 2023 British Open.','next_decision':'Check the earlier decider and 4–3 result in the same tournament.'},
 'kroos_candidate':{'kind':'decision','belief_update':'Kroos scored a 95th-minute free kick for Germany against Sweden in 2018.','next_decision':'Inspect the teams origins and entire scoring pattern before identifying the requested match.'},
 'jazz_release':{'kind':'direct','belief_update':'The candidate Game B, Jazz Jackrabbit 2, is dated 1998.','next_decision':'Check the seven-year company/game chain and precise intro/end animation credit.'},
 'dons_origin':{'kind':'decision','belief_update':'Milton Keynes Dons was founded in 2004 and originates from Wimbledon.','next_decision':'Check this concrete club-lineage route against the discord clue and 95th-minute match; the whole match remains unbound.'},
 'kloss_candidate':{'kind':'decision','belief_update':'Karlie Kloss is a model whose emergence is placed in the late 2000s.','next_decision':'Test the requested education, employment and musical-debut conjunction for this provisional lead; occupation and timing alone do not identify the answer.'},
 'newcastle_origin':{'kind':'decision','belief_update':'Newcastle United resulted from a controversial merger of West End and East End.','next_decision':'Check whether this candidate club participates in the required scoring/free-kick match.'},
 'scunthorpe_origin':{'kind':'decision','belief_update':'Scunthorpe linked with North Lindsey United in 1910 and was called Scunthorpe And Lindsey United for 48 years.','next_decision':'Inspect this club-lineage alternative; do not assume a fixture against Newcastle.'},
 'stoke_origin':{'kind':'decision','belief_update':'Stoke City was formerly Stoke Football Club until a 1925 name change.','next_decision':'Inspect the club-lineage clue and required fixture; an old name alone does not bind a match.'},
 'rangers_league_total':{'kind':'direct','belief_update':'The June 2024 championship is explicitly Rangers eighth league title.','next_decision':'Use the dated league component to check the as-of-2023 fifteen-trophy conjunction; do not apply the 2024 count unchanged.'},
 'rangers_2016_excluded':{'kind':'decision','belief_update':'In the 2016 final table Rangers were first with 63 points and +16 goals, outside the requested rank/GD ranges.','next_decision':'Exclude 2016 as the target Rangers season and inspect another year in the permitted interval.'}
})
def setlabel(eid,facts,reason):
 labels[eid]={'facts':facts,'reason':reason,'review_depth':'full returned window read by single reviewer; stage G5'}
setlabel('375f0180b700685c',['scienza_candidate'],'A named player plus the exact 95th-minute free-kick event supplies an inspectable alternative fixture, not a verified answer.')
setlabel('bbc99faf13d8b82e',['coco_argentine'],'The returned collector account explicitly identifies the Argentine release title Cocomiel; it does not verify the complete clue conjunction.')
setlabel('e22817c2400f5d1e',['coco_runtime'],'The Allocine metadata reports four-minute episodes. This is new specific runtime support, although other sources give broader duration ranges.')
setlabel('8a483539fc7c13c9',['coco_network','coco_education'],'The French page supports TF1 and educational nature protection, while its two-season 78-episode 1992–1996 scope conflicts with treating the whole program as one year.')
setlabel('6475902c978fd7f1',['coco_network'],'The returned broadcasting section explicitly lists TF1. The section does not contain the requested cast or exact first-season schedule.')
setlabel('83279b52444f05ec',['coco_argentine','coco_credits'],'The Spanish source supports the Argentine title and exact director/writer list. It distinguishes a first season of 52 episodes from 78 total but does not establish all character or exact schedule clues.')
setlabel('410719e0bd8ce570',['newcastle_arsenal_candidate'],'The observed retrospective supplies a concrete early/late scoring-pattern candidate. No 95th-minute free-kick or team-history conjunction is established.')
setlabel('a49d7c4ada2c861a',['brum_candidate'],'Living transport and a period-bounded UK program list give a narrow new route; other identifying conditions still require inspection.')
setlabel('1598dabc87d4f2f6',['ma_centuries'],'Nine total centuries including later seasons implies fewer than 250 at the earlier event. It does not validate the whole sequence.')
setlabel('7195e954279140b4',['williams_centuries'],'Later career statistics motivate checking Williams as opponent; do not silently turn 2025 into 2023 support.')
setlabel('0ad82b18c7242532',['condon_kinsey','condon_estate'],'The observed biography explicitly links Condon to writing/directing Kinsey and directing the thriller The Fifth Estate.')
setlabel('9125a772d4d519e2',[],'The returned British Open section concerns Selby–Xiao and Williams–Vafaei; no new Ding sequence relation.')
setlabel('49c3c8e6b3b7a940',[],'One 2007 Ding maximum is not evidence for the required more-than-three threshold; unrelated table entries do not reduce the relevant uncertainty.')
setlabel('75323a8e2bcb2b56',[],'Milan–Liverpool names and a free kick at the end of extra time do not establish the 95th-minute clue or new early/late timing pattern.')
setlabel('2cbb4b1bf8261129',[],'The visible 71–84 minute commentary and 3–3 title do not supply the discriminating 95th-minute event or early/late pattern.')
setlabel('63651fd812183acc',[],'Quarxs appears as an educational creature premise but lacks the schedule/character combination needed for a supported alternative route here.')
setlabel('9e97d87e37f9472e',['rangers_league_period'],'The observed historical section says the 2016 league championship was the first since 1982, directly establishing the required period title.')
setlabel('39f3aed8bd68a7f1',['messi_timing'],'Explicit early PSG goals, Lille comeback, late Mbappe equaliser and Messi free kick refute the clean early/late team split.')
setlabel('70edad5ad4e9553e',['ding_british_win'],'The single 4–0 result supplies an alternative 2023 tournament route; no later loss is included in this window.')
setlabel('aa283b062811fd63',['milan_candidate'],'Milan first-half goals and Liverpool second-half comeback supply a relevant alternative fixture; 95th-minute free kick and origins remain open.')
setlabel('cd1e07cc3ef8b368',['dean_jazz','jazz_release'],'The observed section names Dean as a Jazz 2 animator and dates Jazz 2 to 1998; neither establishes the precise intro/end credit.')
setlabel('ed37be1066c7d87d',['dons_origin'],'The table explicitly links MK Dons to Wimbledon, a concrete provisional lineage route rather than a completed match identification.')
setlabel('5704084e3bf2e51c',['newcastle_origin','scunthorpe_origin'],'Observed controversial merger and successive club names address the requested origin clues. The two independent histories do not establish a match between the clubs.')
setlabel('1999da522adbf089',['stoke_origin'],'The observed 1925 name change provides a provisional club-lineage check; it does not establish several iterations or any Newcastle fixture.')
setlabel('5d15d66647b438b9',['rangers_league_total'],'The 2024 eighth league title provides a dated component for the trophy-count check. The current league total must not be silently treated as the 2023 total.')
setlabel('40e658773328fb3a',['rangers_2016_excluded'],'The eligible-range 2016 table excludes that season for Rangers by rank and goal difference. It does not establish the correct season.')
setlabel('1f96a13b9bff66b7',[],'The 2017/18 team event and other wrong-year matches do not establish the required 2023 singles sequence or a missing career threshold.')
setlabel('cf50a3990cb8b9de',[],'The mixed 2019–2023 section supplies no required 4–3/4–0 sequence or new career threshold. A 2023 UK 6–5 win alone does not discriminate the requested chain.')
setlabel('9188d61c63eef9d0',[],'The opened continuation concerns other musicians, not Mtukudzi or the requested feature-time album count.')
for row in labels.values():
 if 'ding_british' in row['facts']:row['facts']=sorted(set(row['facts'])|{'ding_british_win','ding_british_loss'})
for w in read(b/'EVIDENCE_CATALOG.json'):
 if w['url']=='https://www.bavarianfootballworks.com/2018/6/23/17497446/germany-sweden-world-cup-toni-kroos-video-omg':
  assert '95th minute' in w['text'] and 'Reus scored' in w['text']
  setlabel(w['evidence_id'],['kroos_candidate'],'Exact observed 95th-minute free kick and later German scoring provide a provisional alternative; no team-history binding is made.')
 if w['url']=='https://www.fashiongonerogue.com/supermodels-list/' and 'Kloss' in w['text'] and 'late 2000s' in w['text']:
  setlabel(w['evidence_id'],['kloss_candidate'],'Occupation plus the requested emergence interval supports a tentative candidate check. All other clue links remain unverified; alternative-source sensitivity only.')
write(p,labels);write(TOP/'analysis_v2/FACT_DEFINITIONS.json',defs)
