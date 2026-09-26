"""Pre-call single-reviewer selections and semantic coverage; evaluator only."""
DEV=['B001','B006','B008','B010','B025','B130','B134','B136','B139','B190','B192','B201','B211','B218','B227','B235','B236','B242','B244','B295','B299','B303','B305','B306']
RESERVE=['B012','B015','B017','B023','B030','B135','B138','B140','B142','B193','B200','B204','B209','B224','B237','B239','B246','B248','B250','B307','B311','B316','B333','B358']
CHALLENGE=['B057','B078','B091','B096','B150','B180','B286','B293','B392','B412']
# Oracle descriptions contain no new fact; all targets already occur in Q/C/H.
GAPS={
'B001':'The club referred to by the 2023 article about signing thirteen players has not been identified.',
'B006':'The city in which the provisional club Rangers was based is not established.',
'B008':'It is not established which other club, if any, shared Rangers final points in the 2014 season.',
'B010':'Whether Rangers won the relevant league between 1973 and 1983 remains unestablished.',
'B025':'Whether the 2023 article attributed fifteen trophies to Rangers remains unestablished.',
'B130':'The mammal-shooting game released before 1999 has not been identified.',
'B134':'The storage capacity of the provisional animator Dean Dodrill gaming PC as of July2013 is not established.',
'B136':'Whether Dean Dodrill created the intro and end animations of the game described in the question is unestablished.',
'B139':'The earlier role-playing game associated with the possible Jazz Jackrabbit 2 company route has not been identified.',
'B190':'The filmmaker who was inspired by Iracema has not been identified.',
'B192':'Which 2005 film directed by the provisional filmmaker Fernando Meirelles is relevant remains unestablished.',
'B201':'The birth decade of the provisional actor Peter Nzioki remains unestablished.',
'B211':'It is not established whether Bill Condon wrote and directed Kinsey.',
'B218':'Whether Peter Nzioki satisfies the Goat zodiac clue remains unestablished; a birth-date claim is not an observed zodiac classification.',
'B227':'A plausible player who turned professional during the specified 1995–2006 interval has not been identified.',
'B235':'Ding Junhui professional debut year is not established.',
'B236':'A plausible player who turned professional during the specified interval is not established; the final score does not establish either finalist as the target.',
'B242':'Ding Junhui professional debut year is not established.',
'B244':'Which match followed Ding Junhui 2023 English Open Last16 win is not established.',
'B295':'The individual described by the 2020 coordinator-to-manager employment clue has not been identified.',
'B299':'Whether Nick Mutuma had a US-born child by2021 remains unestablished.',
'B303':'An alternative person who had an industry breakthrough during2006–2010 remains to be found; the Heart1998 route is incompatible.',
'B305':'Whether Nick Mutuma held the described coordinator-to-manager employment sequence remains unestablished.',
'B306':'The date of Nick Mutuma first industry breakthrough remains unestablished.',
'B057':'Whether Albino Frog actually developed Galacta, rather than merely publishing it, remains unestablished.',
'B078':'Whether Galacta excludes multiplayer remains unestablished; one offline player does not establish exclusivity.',
'B091':'A different programme fitting the original early-1990s broadcast clue remains unidentified; Hijitus is contradicted.',
'B096':'The Hijitus candidate is incompatible with the observed original-run dates and writer count; an alternative programme remains unidentified.',
'B150':'The musician career total of67 albums remains unestablished; more than60 is insufficient.',
'B180':'Whether Mtukudzi asked the specified why-sing/why-art question in a2010s interview remains unestablished.',
'B286':'Whether the male lead roommate made the described season-three sacrifice remains unestablished.',
'B293':'What assumption about a sensitive issue led to the season-one conflict remains unestablished; a generic assumption-and-date summary is incomplete.',
'B392':'Whether the PSG–Lille match has the required early/later all-goals pattern remains unestablished.',
'B412':'An alternative match remains unidentified after the PSG–Lille all-goals timing pattern was contradicted.'}
# Fully supported hard units for the incumbent route, from Claim statements alone.
# Anything else remains missing/partial; requested candidate answer can be known
# conditionally without proving the target identity.
FULL={
'B008':{1:[2],4:[2]},'B025':{6:[11,12]},
'B214':{1:[1],2:[2],4:[4],6:[5,6]},'B190':{},'B192':{},'B201':{4:[4],5:[1,3,4]},
'B211':{1:[1],2:[2],4:[4],6:[5,6]},
'B218':{1:[1],2:[2],4:[4],5:[4,7,9],6:[5,6],7:[6,8]},
'B299':{3:[1]},'B305':{3:[1]},'B306':{6:[1]},
'B057':{3:[1],5:[1],6:[2]},'B078':{1:[5,10],3:[1],5:[1],6:[2]},
'B150':{1:[1]},'B180':{1:[1],2:[5],6:[3]},
'B286':{4:[4]},'B293':{4:[4]},'B392':{5:[1]},'B412':{5:[1,2]}}
# Explicitly contradicted units, rather than valid gaps to reconfirm the same H.
CONTRADICTED={'B091':{1:[1],2:[2],3:[2]},'B096':{1:[1],2:[2,3],3:[2]},'B412':{4:[7,8]}}
PARTIAL_NOTES={
'177':'Signing13 lacks the fifteen-trophies/source-year conjunct; a2014 eighth-place/+8 Claim lacks the other equal-points team and all-three-pairs table property. Enugu name alone does not establish capital scope. Founding value can be known while club binding remains provisional.',
'387':'Animator is not specifically intro/end credit; same-company RPG/financial/store chains remain open. Undated PC/paper Claims do not alone establish the July2013 timing. A provisional game/company route may be tested, not presumed correct.',
'517':'Separate director and actor appearances require supported film/year/genre joins. Birth date alone leaves zodiac correspondence unverified in the supplied Claims. Conditional popular-name value does not close actor identity. A stale earlier snippet saying role absent is superseded by a later explicit role Claim.',
'546':'Undated current cumulative totals do not establish lower bounds by30January2025. One match or unbound different-year tournament cannot establish the full specified sequence/opponent counts. Local components of that sequence are valid Needs.',
'1034':'Model occupation does not prove2022 wealth attribution; photographed siblings are not exhaustive; child existence is not US birthplace; university year without2020-article attribution is partial. Professional-since year is not automatically first-break year. Heart1998 rules out that route.',
'186':'One offline player does not exclude multiplayer. Former Night Sky plus October1993 incorporation does not establish the name at FIRST establishment. Publisher is not developer. 1992/1993 alternatives both fit early1990s.',
'311':'Observed original-run years and writer count rule out Hijitus. Reconfirming unrelated attributes of that same route is not useful; reconciling contradictory source dates or finding alternatives can be useful. One minute meets duration but cannot repair identity mismatch.',
'435':'More than60 does not prove67; performing/recording-deal year does not date first album. Song interpretation about Mugabe old age does not fully establish an explicit retirement exhortation. Requested feature-count can be known while quote/identity conditions remain open.',
'580':'Assumption/upset/date alone lacks sensitive-issue/no-time binding. Edgar-roommate and Gretchen-baby facts lack explicit male/female-lead binding in Claims. Episode-number midpoint precision is not invented. Five seasons already covers the season cap.',
'1094':'A95th-minute goal alone does not bind club origins or the all-goals temporal separation. A PSG early lead and late equalizer explicitly refute that match pattern; neither all-goals inference nor target identity follows from the free kick.'}
STRATA={
'B001':['U1'],'B006':['U2'],'B008':['U3','U5'],'B010':['U2','U5'],'B025':['U3','U5'],
'B130':['U1'],'B134':['U2'],'B136':['U3','U5'],'B139':['U3','U5'],
'B190':['U1'],'B192':['U2'],'B201':['U3','U5'],'B211':['U3','U5'],'B218':['U4','U5'],
'B227':['U1'],'B235':['U2'],'B236':['U1'],'B242':['U2','U5'],'B244':['U2','U5'],
'B295':['U1'],'B299':['U2','U5'],'B303':['U1','U6'],'B305':['U3','U5'],'B306':['U2','U5'],
'B057':['U7','U3'],'B078':['U7','U3','U5'],'B091':['U7','U1','U6'],'B096':['U7','U6'],
'B150':['U7','U2'],'B180':['U7','U3','U5'],'B286':['U7','U3'],'B293':['U7','U3','U5'],
'B392':['U7','U2'],'B412':['U7','U6']}
