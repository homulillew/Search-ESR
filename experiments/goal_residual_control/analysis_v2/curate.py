from progress import *
facts={
'heart_exclusion':('decision','Heart began around 1998/age 13, conflicting with the 2006–10 break clue.','Reject Heart as the full binding; search other candidates.'),
'messi95':('decision','Messi took the 95th-minute free kick in PSG–Lille.','Check club histories and timing before binding this match.'),
'messi_timing':('decision','PSG scored both early and late (including Mbappe equaliser), incompatible with a clean early/late split.','Reject or explicitly resolve the PSG–Lille timing mismatch.'),
'rangers_founded':('direct','Rangers International was founded in 1970 in Nigeria.','Retain the requested relation provisionally while checking the club identification.'),
'rangers_titles':('direct','Rangers won five league titles during 1974–1982; the honours list distinguishes domestic and continental trophies.','Use the dated honours to check the 1973–83 and as-of-2023 clue; do not use the 2024 total unchanged.'),
'rangers13':('direct','Enugu Rangers signed 13 players before 2022/23.','Verify remaining league table and historical conditions.'),
'galacta_specs':('direct','Galacta has November 1992 DOS/shareware/single-player and three credits including two Pucketts.','Verify the developer and its former company name.'),
'galacta_company':('direct','Galacta is explicitly developed by Albino Frog, formerly Night Sky.','Combine with the release/credit constraints to assess original-goal closure.'),
'galacta_company_history':('direct','Albino Frog was formerly Night Sky in 1992–October 1993 and lists Galacta among its credited games.','Check explicit developer attribution, then assess closure.'),
'hijitus_exclusion':('decision','Hijitus has 1967 start/three writers/74 episodes, incompatible with the original constraints.','Leave the Hijitus path and identify a different program.'),
'dean_pc':('direct','Dean Dodrill reports 5 TB and a wireless keyboard.','Verify the Game B intro/end animation and company chain before binding the answer.'),
'dean_jazz':('decision','Dean Dodrill worked as an artist on Jazz Jackrabbit 2.','Investigate Jazz Jackrabbit 2 and Epic as the game/company route.'),
'peter_police':('direct','Peter Nzioki played Policeman 1 in The Constant Gardener (2005).','Resolve the birth-year/zodiac and director links.'),
'peter_birth_conflict':('decision','The Nzioki page category says 1979 births, conflicting with the incumbent 1978 claim.','Resolve the source disagreement rather than silently replacing the old date.'),
'ding_career':('direct','Ding turned professional in 2003 and has >600 centuries/seven maxima in the retrieved biography.','Check date scope and the exact 2023 tournament sequence; identity is still provisional.'),
'ding_counts':('direct','Ding has >600 centuries and seven maxima in the retrieved achievements passage.','Check date scope and exact 2023 sequence.'),
'ding_british':('decision','At the 2023 British Open, Ding beat Leclercq 4–0 then lost 2–4 to Williams.','Investigate British Open earlier rounds instead of locking onto English Open.'),
'ding_brecel':('decision','The 2023 English Open last-16 record shows Ding beating Brecel 4–3.','Do not assume Brecel was the required later defeat; reassess tournament sequence.'),
'tuku_death':('direct','Mtukudzi died at age 66.','Check remaining identifying clues and the date-specific Forbes album count.'),
'forbes65':('direct','The May 2017 Forbes Africa feature/list explicitly gives Mtukudzi 65 albums.','Use 65 for that feature; do not substitute retrospective 67.'),
'forbes_edition':('decision','A dated report links Mtukudzi to the May Forbes Africa list.','Inspect the May feature for its contemporaneous album count.'),
'tuku67':('direct','Mtukudzi had 67 albums over his career.','Keep lifetime count separate from count at the Forbes feature.'),
'wasakara':('direct','Wasakara (2000/2001 source dating) was interpreted as urging Mugabe to accept old age.','Check the remaining identity and feature-specific count.'),
'tuku_activist':('direct','Mtukudzi is explicitly described as a human-rights activist.','Check the remaining original clues.'),
'tuku_first':('direct','His first album followed the band single after joining Wagon Wheels in 1977.','Check the feature-specific count and remaining identity clues.'),
'tuku_quote':('direct','A source attributes “Why do we sing, why is there art?” to Mtukudzi in 2015.','The strict interview-quote requirement can now be supported; still verify the May count.'),
'y_s1':('direct','Insouciance S1E2 has the assumption/anger/friends-arranged date.','Combine with S3/S4, roommate and season-count constraints.'),
'y_s3':('direct','No Longer Just Us S3E13 describes Edgar’s sacrifice.','Verify Edgar is the male lead’s roommate and the other plots.'),
'y_s4':('direct','Not a Great Bet S4E7 has Gretchen’s brother’s baby and reunion with Heidi.','Verify S1/S3 plots and the season count.'),
'y_roommate':('direct','Edgar Quintero is Jimmy’s roommate.','Connect the S3 sacrifice to the male lead’s roommate.'),
'y_seasons':('direct','You’re the Worst has five seasons.','Assess closure with all three plot constraints.'),
'neves_candidate':('decision','Neves scored a 95th-minute free kick; Villa’s goals preceded Wolves’ three late goals.','Inspect this alternative match and club origins.'),
'cococinel_candidate':('decision','Cococinel lists 52 episodes, January–December 1992, with 4–10 minute runtime.','Inspect credits/network/characters and resolve runtime before identification.'),
'meirelles_iracema':('direct','Meirelles decided to become a filmmaker after seeing Iracema.','Connect him to the policeman’s 2005 film.'),
'meirelles_gardener':('direct','Fernando Meirelles directed The Constant Gardener (2005).','Join only with the supported director inspiration and role facts.'),
'condon_kinsey':('direct','Bill Condon directed and wrote Kinsey.','Connect to the 2013 thriller.'),
'condon_estate':('direct','The Fifth Estate is a 2013 thriller directed by Bill Condon.','Combine with the supported actor appearance and Kinsey link.')}
write(TOP/'analysis_v2/FACT_DEFINITIONS.json',{k:dict(kind=v[0],belief_update=v[1],next_decision=v[2]) for k,v in facts.items()})
M={}
def add(ids,tags,reason=None):
 for eid in ids.split():M[eid]={'facts':tags.split(),'reason':reason or ' '.join(facts[t][1] for t in tags.split())}
add('d8543f654536e517','heart_exclusion')
add('88d97b2dc688d9ec','messi95 messi_timing')
add('77f51764feee6967','messi_timing')
add('3c2467898084a05c 65a8251339b28300 8a33a21933654767 8af38542072fd6ad','rangers_founded')
add('622593fa63fc60ff','rangers_titles')
add('ec85601db06ccf0b','rangers13')
add('8bfc35f0f40c8877','galacta_specs')
add('e68292a2acb478c8','galacta_company')
add('1318bbecab5edd0f 62a33624eb258304','hijitus_exclusion')
add('1115fa24a5dfb981','dean_pc')
add('3dc254f8e6f8099e','dean_jazz')
add('699483366625a55c','dean_pc dean_jazz')
add('afb7af2fdec8efc0','peter_police')
add('c3ab063cbb8010cf','peter_police peter_birth_conflict')
add('a318fecb49447765 e11fda90ae0a9085','ding_career')
add('a82709d6bdc2bb45','ding_counts')
add('0176b125388bef2d 0c161ef7a6433826 22dd58f1289735b2 c6809fba4f418d71','forbes65')
add('658c76704534bf2f','forbes_edition')
add('1be46f291c5bbb20','tuku_death tuku67 wasakara')
add('33b43ba2a3f985d8 8bc687e9a08e7c57','wasakara')
add('814c681331bbe4c8 c906ab52d8b47f52','tuku_activist tuku_first')
add('b5861ed34e377b31','tuku_first')
add('921a71d15d007211 9ffa35431a0204b8 a0cec144c6709aa0','tuku_death')
add('7c13ff71a4bff55c','tuku67')
add('7571130f39880806','tuku_quote')
add('54af5bf327a4a416','y_seasons')
add('7dc9bed101f0f350','y_s3')
add('8fd1b601968b5121','y_s1')
add('b45dea469dbb6496','y_s4')
add('fa5138ac69b5acfe','y_roommate')
# Alternative-source sensitivity; never adds a doc to frozen primary pool.
add('19933c0836f57a29','messi95 messi_timing')
add('2b1edea7e5e86161','neves_candidate')
add('45b5c2cfeffc33c9 bb2bde6d4b26cb39','galacta_company_history')
add('3437147d3cd26e0b 5e523b6bcdb7ff24','hijitus_exclusion')
add('d8b85a6d938fb0d3','cococinel_candidate')
add('7a9f87fcd0d20cc8 cd1e07cc3ef8b368','dean_jazz')
add('3b3f47f173195899','meirelles_iracema')
add('9087480e77b3b256','meirelles_iracema meirelles_gardener')
add('c6db1ecc28a41f73','meirelles_gardener')
add('80f4708db3d25675 a3a85c18c78857c0','condon_kinsey')
add('6acbae2f53479a59 e87f299a14b4df42','condon_estate')
add('e4e14212daed79cd','ding_british')
add('eb2eb8c478f7cf75 f26d21eab6342644','ding_brecel')
cat=read(TOP/'one_step_acquisition_v2/EVIDENCE_CATALOG.json')
for w in cat:
 if w['evidence_id'] not in M:
  M[w['evidence_id']]={'facts':[],'reason':('Returned passage does not establish a new discriminative original-goal constraint; document membership alone is insufficient.' if w['in_primary_pool'] else 'Outside frozen primary source pool. Title/topic screening found no qualifying relation; not an exhaustive alternative-source audit.'),'review_depth':'full_observation' if w['in_primary_pool'] else 'title_topic_screen'}
 else:M[w['evidence_id']]['review_depth']='full_observation'
write(TOP/'analysis_v2/EVIDENCE_LABELS.json',M)
