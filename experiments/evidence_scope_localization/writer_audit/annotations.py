"""Single-reviewer fact annotations over real prior observations.

Tuple: fact key, question condition, full/component, admitted claim index or None,
support regex. Coordinates: case, round starting at 1, wave starting at 0.
Repeated facts represent repeated opportunities only when pre-Claims lack them.
"""
F={}
CLAIM_OVERRIDES={
 ('VP10',1,4,0):('unsupported_strengthening',
  'The actual Latest Headlines observation begins with Mtukudzi performing in 1977. Neither this window/title nor pre-Claims contains 67 albums, four decades, or January 2019. Full-document knowledge is not visible evidence. The legacy supported verdict is retained separately, not overwritten.')
}
# Examples of shared atomic facts, not wholly redundant Claims. Not a recall metric.
PARTIAL_OVERLAP={
 ('VP02',1,1,0):'DOS version already retained; November 1992, shareware and single-player information are new.',
 ('VP02',1,4,0):'Publisher repeats; conflicting 1993 year and source attribution are new.',
 ('VP07',1,4,0):'Age66 repeats; January2019 death timing is new.',
 ('VP08',1,1,0):'January2019 death timing repeats; album count/career duration are new.',
 ('VN01',1,2,0):'Original run years repeat; original Channel13 broadcast is new (previous Claim only binds ElTrece to reruns).',
 ('VN10',1,0,1):'Messi95th-minute winner repeats the preceding addition; scoring sequence is new.',
 ('VN10',1,3,0):'PSG2-0 lead repeats; match date/minutes/scorers are new.',
 ('D02',3,4,0):'1992 DOS release repeats; November is new.'
}
def put(cid,r,w,*facts): F[cid,r,w]=list(facts)
def f(key,h,coverage,index,anchor):return (key,h,coverage,index,anchor)

put('VP01',1,4,f('rangers_signed13','177_H07','component',0,r'signed 13 new players'))
for cid in ['VP02','VP03','VP04','VP05']:
 w=1 if cid=='VP02' else 0
 vals=[]
 if cid!='VP02':vals.append(f('galacta_nov1992_dos','186_H03','full',0,r'November 1992 on DOS'))
 if cid!='VP04':vals.append(f('galacta_shareware','186_H05','full',0,r'Business Model\s+Shareware'))
 if cid!='VP03':vals.append(f('galacta_one_offline','186_H04','component',0,r'Number of Offline Players\s+1 Player'))
 if cid!='VP05':vals.append(f('galacta_three_credits','186_H06','full',1,r'Credits \(DOS version\)[\s\S]{0,600}Terri L\. Puckett'))
 vals.append(f('galacta_publisher_frog','186_H01','component',1 if cid in ['VP02','VP03'] else 0,r'Publishers\s+Albino Frog Software, Inc\.'))
 put(cid,1,w,*vals)
for cid,w,dev,former in [('VP02',2,0,1),('VP04',2,None,0),('VP05',1,0,1)]:
 put(cid,1,w,f('galacta_developer_frog','186_H01','full',dev,r'Developed by:\s+Albino Frog Software, Inc\.'),
 f('frog_former_name_foundation','186_H02','component',former,r'formerly Night Sky[\s\S]{0,250}October 1993'),
 f('galacta_no_multiplayer','186_H04','full',None,r'Multiplayer:\s+No Multiplayer'))
put('VP06',1,0,f('dodrill_jazz_artist','387_H03','component',None,r'working as an artist on Jazz Jack Rabbit 2'))
put('VP06',2,0,f('dodrill_jazz_artist','387_H03','component',0,r'working as an artist on Jazz Jack Rabbit 2'))
put('VP07',1,0,f('tuku_over60','435_H02','component',1,r'more than 60 albums'))
put('VP07',1,1,f('tuku_1978_discography','435_H03','component',0,r'Discography\s+\*1978 Ndipeiwo Zano'))
put('VP07',1,3,f('tuku_67','435_H02','full',0,r'four decades and 67 albums'),f('tuku_wasakara2001','435_H04','component',1,r'in 2001[\s\S]{0,250}77-year-old president'))
put('VP08',1,0,f('tuku_activist','435_H06','full',0,r'human rights activist'),f('tuku_death66','435_H01','full',1,r'22 September 1952[\s\S]{0,5}23 January 2019'))
put('VP08',1,4,f('tuku_wasakara2001','435_H04','component',0,r'in 2001[\s\S]{0,250}77-year-old president'))
put('VP10',1,0,f('tuku_death66','435_H01','full',None,r'22 September 1952[\s\S]{0,5}23 January 2019'))
# NPR title is explicit; tag separately and provide body-only sensitivity.
put('VP10',1,1,f('tuku_death66','435_H01','title_only',0,r'Zimbabwean Musician Oliver Mtukudzi Dies At 66'),f('tuku_over60','435_H02','component',1,r'more than 60 albums'))
put('VP10',1,4,f('tuku_wasakara2001','435_H04','component',1,r'in 2001[\s\S]{0,250}77-year-old president'))
for cid,birth,parent in [('VP11',1,None),('VP12',0,0),('VN12',0,1)]:
 vals=[f('peter_birth1970s','517_H01','full',birth,r'25 May 1978'),f('peter_fifth_estate','517_H06','component',None,r'roles in the films The Constant Gardener, The Fifth Estate and Sense8')]
 if parent is not None:vals.append(f('peter_parents','517_H02','full',parent,r'His father[\s\S]{0,150}military hospital'))
 if cid!='VP12':vals.append(f('peter_2005_minor','517_H04','component',None,r'In 2005[\s\S]{0,150}Fernando Meirelles'))
 put(cid,1,0,*vals)
put('VP11',1,3,f('peter_fifth_estate','517_H06','component',None,r'roles in the films[\s\S]{0,100}The Fifth Estate[\s\S]{0,40}Sense8'))
put('VP12',1,1,f('peter_fifth_estate','517_H06','component',1,r'roles in the films[\s\S]{0,100}The Fifth Estate[\s\S]{0,40}Sense8'))
put('VN12',1,1,f('peter_fifth_estate','517_H06','component',None,r'roles in the films[\s\S]{0,100}The Fifth Estate[\s\S]{0,40}Sense8'))
put('VN12',2,0,f('peter_2005_minor','517_H04','component',0,r'In 2005[\s\S]{0,150}Fernando Meirelles'),f('peter_fifth_estate','517_H06','component',1,r'roles in the films The Constant Gardener, The Fifth Estate and Sense8'))
put('VP13',1,1,f('ding_ma2023','546_H04','component',0,r'4-3 victory over Ma Hailong'))
put('VP15',1,1,f('worst_edgar_sacrifice','580_H02','component',0,r"Edgar's sacrifice comes with unforeseen consequences"))
put('VP15',1,2,f('worst_s1_date','580_H01','component',0,r'Gretchen gets angry[\s\S]{0,150}date'))
put('VP16',1,0,f('nick_has_child','1034_H04','component',None,r'wife, kid, parents'))
put('VP16',2,0,f('nick_has_child','1034_H04','component',None,r'wife, kid, parents'))
put('VP16',1,1,f('nick_professional2008','1034_H03','component',1,r'working professionally since 2008'))
put('VP16',1,2,f('nick_break2008','1034_H03','full',None,r'first big break on Kenyan television came in 2008'),f('nick_commercial_model','1034_H01','component',0,r'commercial model'),f('nick_university2005','1034_H05','component',1,r'In 2005[\s\S]{0,140}Business Administration'))
put('VP16',2,2,f('nick_break2008','1034_H03','full',None,r'first big break on Kenyan television came in 2008'))
put('VP17',1,0,f('nick_commercial_model','1034_H01','component',None,r'commercial model'),f('nick_university2005','1034_H05','component',None,r'In 2005[\s\S]{0,140}Business Administration'))
put('VP17',1,1,f('nick_university2005','1034_H05','component',0,r'In 2005[\s\S]{0,180}Business Administration'))
put('VP17',1,2,f('nick_two_siblings','1034_H02','component',0,r'2 good siblings'),f('nick_has_child','1034_H04','component',1,r'wife, kid, parents'))
put('VP17',1,3,f('nick_commercial_model','1034_H01','component',0,r'commercial model'))
put('VP18',1,0,f('nick_has_child','1034_H04','component',None,r'In 2018, Nick welcomed a baby girl'))
put('VP18',1,1,f('nick_break2008','1034_H03','full',None,r'first big break on Kenyan television came in 2008'),f('nick_commercial_model','1034_H01','component',None,r'commercial model'),f('nick_university2005','1034_H05','component',1,r'In 2005[\s\S]{0,140}Business Administration'))
put('VP18',1,2,f('nick_two_siblings','1034_H02','component',0,r'2 good siblings'),f('nick_has_child','1034_H04','component',1,r'wife, kid, parents'))
put('VN01',1,1,f('hijitus_run1967_74','311_H02','full',0,r'between 1967 and 1974'),f('hijitus_network_rerun','311_H06','full',0,r'El Trece channel'))
put('VN01',1,2,f('hijitus_network_original','311_H06','full',0,r'Channel 13'))
put('VN02',1,0,f('hijitus_network_original','311_H06','full',0,r'Channel 13'),f('hijitus_daily_minute','311_H05','component',1,r'microprogram which was only one minute long'))
put('VN03',1,0,f('hijitus_run1967_74','311_H02','full',0,r'between 1967 and 1974'),f('hijitus_network_original','311_H06','full',0,r'Channel 13'),f('hijitus_daily_minute','311_H05','component',0,r'microprogram which was only one minute long'))
put('VN04',1,0,f('hijitus_run1967_74','311_H02','full',0,r'between 1967 and 1974'),f('hijitus_daily_minute','311_H05','component',0,r'microprogram which was only one minute long'))
put('VN06',1,0,f('ronnie_15_maxima','546_H02','full',0,r'fifteen official maximum breaks'))
put('VN09',1,2,f('williams_pro1992','546_H03','full',1,r'Williams became a professional player in 1992'))
put('VN10',1,0,f('messi_95','1094_H05','full',0,r'95th.minute'))

# Discovery: classify against the actual dynamic Need, not only the original Q.
put('D05',2,1,f('tuku_death66','435_H01','full',0,r'died on Wednesday at the age of 66'),f('tuku_over60','435_H02','component',1,r'more than 60 albums'))
put('D05',2,4,f('tuku_67','435_H02','full',0,r'67 albums'))
put('D05',3,1,f('tuku_activist','435_H06','full',None,r'human rights activist'))
put('D05',3,4,f('tuku_wasakara2001','435_H04','component',0,r'in 2001[\s\S]{0,250}77-year-old president'))
put('D08',2,1,f('worst_five_seasons','580_H04','full',0,r'num_seasons: 5'))
put('D08',2,2,f('worst_edgar_sacrifice','580_H02','component',0,r"Edgar's sacrifice comes with unforeseen consequences"))
put('D08',2,4,f('worst_edgar_roommate','580_H02','component',0,r'roommates with Jimmy'))
put('D10',1,2,f('psg_interleaving','1094_H04','full',None,r'opened the scoring[\s\S]{0,450}equalised to make 3-3'))

# Directly observed but already covered by pre-Claims, not recall opportunities.
COVERED={
('VP07',1,4):'67 career albums already admitted at wave 3.',
('VP10',1,2):'Age66 and more-than-60 count already retained at wave1; first album year is not established by generic career chronology.',
('VP10',1,3):'Age66 already retained; this window lacks the specific interview quote and album count.',
('VP11',1,3):'Birth decade1970s and parent occupations already retained; different exact birth date is a conflict, not a missing decade.',
('VP12',1,1):'Birth decade and parents already retained; Fifth Estate appearance is separately scored.',
('VN12',1,1):'Birth decade and parents already retained; Fifth Estate appearance remains unretained.',
('VN12',2,1):'Parents/birth decade already retained and Fifth Estate just admitted at wave0.',
('VN03',1,1):'Original run years already retained at wave0.',
('VN03',2,0):'Run years/network/daily duration already retained; month-level target still missing.',
('VN03',2,1):'Run years already retained; rerun dates do not solve target months.',
('VN06',2,0):'Ronnie fifteen maxima already admitted in round1.',
('VP16',2,1):'Professional-work year and TV debut title already retained; text still does not explicitly date that debut to2008.',
('VP16',2,2):'Commercial-model and education facts retained; explicit breakout-year binding separately scored as missing.',
('D08',2,3):'Season4 birth/reconnection plot already retained in round1.',
('D05',3,2):'Death age66 already retained in round2.',
('D05',3,4):'Career count67 and death age66 already retained; political-song fact separately scored.'}
NEAR={
('VP13',1,0):'Ding >600 centuries and seven maximums are dated only by a page containing2025 material; these totals alone do not bind the earlier30Jan2025 cutoff.',
('VP14',2,0):'Ding >600 centuries without a pre-cutoff date is not complete off-Need numerical coverage. The dated fourth/sixth maxima belong to the current Need.',
('VN09',1,2):'668 centuries as of July2025 cannot establish a lower bound at January2025; only professional debut is scored off-Need.',
('VN07',1,4):'Selby is an alternative candidate, not the supplied Higgins; current800/six totals also lack the required cutoff.',
('VN08',1,3):'Ding is an alternative candidate to Williams; totals lack the exact cutoff. This is not same-candidate off-Need recall.',
('VN06',2,2):'Williams >600/three totals concern a different candidate; not same-candidate Ronnie off-Need recall.',
('VP03',1,2):'Single-player wording still does not explicitly exclude multiplayer; it concerns the current Need, not an off-Need opportunity.',
('VP02',1,4):'A different site release year conflicts with an already retained date; it does not newly establish a still-unresolved off-Need condition.',
('VP04',1,4):'Alternative release year is a source conflict for an already represented condition.',
('VP17',1,2):'Two photographed siblings are non-exhaustive; child existence does not establish US birth. Both are scored only as verified components.',
('VP18',1,2):'Same sibling/child scope limitation; component admission does not imply hard-condition closure.'}
