"""Masked, single-reviewer semantic judgments; coverage remains frozen."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
A={}
F={'s':'stale','d':'drift','u':'unsupported_premise','o':'over_broad','p':'premature_stop','m':'missed_stop','b':'belief_error'}
def add(mid,req,focus,flags,reason,sub=False):
    assert mid not in A
    A[mid]={'requirement_ids':req.split() if req else [],'focus':focus,'valid':not any(x in flags for x in 'sduopm'),
            **{name:k in flags for k,name in F.items()},'reason':reason,'reactivates_subrelation':sub}
def stop(mid,complete,reason):add(mid,'','stop','' if complete else 'pb',reason)

add('Md0d67651d9f3','R1','birth year and zodiac consistency','','Tests disputed birth date/zodiac relation;1979is a candidate alternative in a verification question, not acceptance of the full identity.')
add('M47ad8698631d','R1 R2 R3 R4 R5','entire club identification','o','Restates essentially the complete multi-clue goal and requested founding relation without choosing a bounded next frontier.')
stop('Mdae440a38203',False,'PC storage alone does not establish GameA/GameB, dated animator relation or store-title conjunction.')
stop('M58760659598b',False,'First-album date and strict May2017 attribution remain unresolved in this view.')
add('M80b5b47d4915','R4','2023 sequence','','Tests whether the candidate sequence fits; allows rejection/another candidate.')
add('Mdca993b58e13','R4','2023 sequence with Higgins','ub','Introduces John Higgins and asserts his cutoff century bound without visible evidence. Candidate can be proposed, but the relative clause treats the bound as established.')
add('M5f9a65b34c14','R4','2023 next-match sequence','','Asks for opponents/results after the observed opener, with the required pattern as the verification target.')
stop('M2f3d767f30d6',False,'Early biography does not establish all director/role/zodiac identifying conditions.')
add('M6a9c20cde961','R4','2023 next-match sequence','','Conditional verification of the ordered sequence and final opponent count.')
stop('M25dd2b2e9a23',True,'All material episode and season-total conditions supported in this view.')
stop('M2793efb64a1f',False,'Season-count upper bound is absent from the visible Claims.')
add('M9f63203b1e70','R5','May2017 Forbes scoped count','','Asks the missing exact feature-date attribution, not just the separately stated lifetime count.')
stop('M2bbd7d782578',False,'Initial film appearances and biography do not establish all required film/director/zodiac conditions.')
stop('Mf529286ff57e',False,'Known storage5TB does not establish game/animator/article-date/store binding.')
add('M18b6e4eb1d69','R1','former developer identity','','Tests the single developer identity/former-name relation; publisher status alone is insufficient.')
stop('Mada176bfd548',False,'GameA, interval, dated intro/end role and store relation remain unresolved.')
stop('Mbefb1490ba70',False,'Direct requested Forbes relation is known, but first-album date and requested quote remain open under frozen primary closure; valid in predeclared F24 sensitivity.')
add('Mdde91d61cedd','R4','95minute taker MilanLiverpool','ub','Assumes a95minute free kick in an unqualified2005fixture; visible Riise extra-time event is not established as95minutes.')
add('M1a6733e2c796','R4','2023 article club identity','','A bounded identifying article relation (15trophies/13signings) with club constraints, not the full table/founding problem.')
stop('Ma70b2310bd6e',False,'Zodiac/birth-year compatibility remains a material blocker despite other strong identity links.')

add('Mbfc8e94ba20d','R6','character conjunction','','Conditional character check addresses a missing material identification clue; does not assert the character list is already supported.')
stop('Md0129f5b0bea',True,'View includes all episode conditions and total five seasons.')
stop('M4df9c3a0544b',False,'First-album date and strict May2017 attribution still open.')
add('M38ed20063cfc','R5','Rangers founding relation','','Specific requested relation for a live candidate; does not claim every other clue already matches.')
stop('M9f326a14de40',True,'History has all material episode and total-season evidence.')
add('M681bdba348ae','R2 R3 R4 R5','whole club conjunction plus founding','o','Bundles capital,league,article,identity and founding into one multi-part goal. Naming the candidate conflict does not bound the missing research relation.')
add('M8c6e66787e07','R1','birth-year zodiac candidate test','','Primary frontier is a real unresolved zodiac consistency test, with a conditional candidate pivot if it fails.')
stop('Ma54f378a5ffb',False,'Birth-year zodiac relation remains unverified.')

add('M0c7c1dc03573','R1 R2 R3 R4 R5','entire celebrity identification','o','Restates essentially every original article/family/career clue as one whole-goal identification; no bounded next relation.')
add('M78eca0c2b7a7','R3 R4','identify 2020 career biography','','Selects the distinctive2020biography and linked education/career facts as a bounded source-identification target, omitting the other-year family/wealth problem.')
add('M2e0370cb4dfb','R3 R4 R5','2020 biography identity','','Asks identity/birth-name of the2020career-biography subject; a focused subset of the multi-article original question, not a claim that Heart matches it.')
add('M219e8244a2c3','R4 R5','coordinator career subject identity','','Specific career-article identity relation: coordinator2012→manager and debut interval. Does not assume Dolapo fits.')

add('Md33451af2ef8','R5','Rangers founding relation','','Tests a specific requested relation for the observed candidate without asserting all clues fit.')
add('M5f4111248066','R3 R4','2020 career article identity','','Targets the distinctive2020career biography; commercial model is a question-derived constraint, not an asserted fact about Dolapo.')

add('Mcbed2bb3b79e','R3 R4 R5','2020 career biography identity','','Targets identity/birth-name in the specific2020career article, leaving other-year wealth/family clues for later.')
add('M2c2937f0cd61','R1 R2 R3 R4 R5 R6','whole television identity','o','Rephrases almost the entire original clue conjunction rather than choosing a specific discriminating unresolved question.')

add('M059d1fa78cb8','R1 R2 R3 R4 R5','entire original person question','o','Repeats the complete original clue list plus birth-name goal; does not identify one actionable missing relation.')
add('Mdd27fd794088','R1 R2 R3 R4','95minute final assumed qualified','ub','Promotes unobserved Liverpool-origin/ACMilan-identity facts and a95minute event into established fixture qualification; visible timing evidence alone does not support that conjunction.')

add('M681b74184e01','R1','former studio name','','Former-name clue is missing from visible State.')
add('M5a95d1cbd3bd','R4 R5','article club and founding','','Specific identifying article relation and its subject founding facts; other unverified club conditions are not asserted.')
add('M48d20a972278','R5','Forbes dated count conflict','','Resolves the feature-date/count scope instead of joining separate retrospective counts and dates.')
add('M77e08389c758','R3 R5','founding with club constraint','','Read the unnamed club description as a question-derived qualification filter, not a factual assertion that Rangers has the league win. Conditional candidate founding research is allowed; wording is ambiguous.')
add('Mc103d9dac9e1','R4','95minute taker in assumed final','ub','Assumes the95minute event in the unqualified Liverpool–Milan fixture; timing-only clues do not establish it.')

add('M09dbb5367c0c','R1 R2 R3 R4 R5','entire biography question','o','Repeats all original constraints and final birth-name target; no single current unresolved relation selected.')

add('Mc893e566bd60','R1 R4 R5','club article table and founding','o','Bundles article qualification, complex historical table and founding into several independent investigations; needs one current relation.')
add('Mbc3e959913ae','R4','new Milan derby95minute event','ub','Introduces an unobserved2006fixture/score and assumes its95minute free kick; neither fixture qualification nor event is established in this prefix.')
add('Ma96107f69891','R2 R3 R4','2020 coordinator article subject','','Identifies the distinctive2020coordinator-to-manager article subject using question-derived personal constraints; does not presume Heart fits.')
add('M6881ea084858','R1 R2 R3 R6','broad programme identification','o','Several independent staff/schedule/count/runtime/character requirements restated with no bounded next relation or source.')
add('Mf8c71b452b79','R4','2023 match sequence','','Tests missing next-match scores/opponents and final-loss bound, one linked sequence.')

add('Mf9a05e43f9f3','R2 R3 R4 R5','full biography conjunction','o','Combines family,break,child,education,music,career and birth name; effectively restates the original multi-article goal.')
add('M9b9267feadbb','R4','conditional match sequence','','A conditional sequence test. Trump is offered as a possible example, not asserted to be the established final opponent; exact cutoff count still needs evidence.')
add('M2b55d7ca151e','R1 R2 R3 R4 R6 R7','entire television identity','o','Restates nearly all independent programme constraints and title goal without selecting one current discriminating relation.')
add('Md7693bbe5317','R3 R4','specific 2020 biography','','Focuses on identifying the distinctive2020career/education article, a bounded subset of the original multi-article problem.')

add('M5ffc43329a17','R1','developer and former name','','A bounded developer-identity/former-name check addresses the missing qualification.')
add('M3baeb42a464a','R2 R3 R4 R5 R6 R7','assumed French TF1 target','uob','French origin/TF1 are introduced as established target properties without prefix support, while multiple independent identification clues and final title are bundled.')

add('M5d50b81a43b5','R6','character-set test and conditional pivot','','Tests a missing character conjunction on the current programme; alternative candidate path is conditional on failure.')
add('M9752573befe6','R5','assumed May2016 feature count','ub','Joins the observed2016Forbes interview with the question’s May feature before establishing they are the same dated source. Need should test that attribution, not assume May2016.')
add('Mc0b32debecf4','R1 R2 R3 R4','whole fixture qualification','o','Restates both independent club histories plus match timing and final event goal; no one current missing relation is selected.')

add('M7a4615e42757','R2 R3 R4 R5 R6 R7','assumed Catalan TV3 programme','uob','Spanish/Catalan origin and TV3 are unverified new target restrictions; several independent programme constraints and title are bundled.')
add('Ma3ef7bdcd351','R2 R3 R4 R5 R6 R7','assumed French TF1 programme','uob','French origin and TF1 are promoted without prefix support; otherwise repeats the multi-clue title problem.')
add('M58fa9235e476','R5','Enugu candidate founding','','Specific founding relation for an observed candidate; repeats only supported identifying context, not unverified success on the other clues.')
add('M08404f7a75a5','R2 R3 R4 R6 R7','broad TV identification','o','Bundles schedule/count/runtime/characters/network and final title rather than selecting one unresolved relation.')

add('M35ff443b26f5','R4','Ding ordered2023 sequence','','Conditional sequence verification; Ma’s9centuries is already visible in this later history, so the lower bound premise is supported.')
add('Me91f9cc00a66','R4','unobserved Wimbledon MKDons95minute','ub','New fixture/date and its95minute event are assumed without visible qualification or event evidence.')
add('M90b73b708ed3','R4','Newcastle95minute presupposition','ub','Observed early/late scoring supports a provisional fixture, not the asserted95minute free kick. The Need promotes that missing event premise.')

add('M8d2537d677e5','R2 R3 R4 R5 R6 R7','assumed Indian DD1 programme','uob','Invents Indian origin/DD1/52episodes as established target context and changes under-five to five minutes; bundles the title problem.')
add('M5964bebeff6e','R1','birth year zodiac consistency','','Tests the question-described actor’s birth/zodiac relation.1979is explicitly an example to investigate, not accepted identity evidence.')
add('M4dbf0edebfc6','R2 R3 R4 R5 R6 R7','assumed Argentine C13 programme','uob','Introduces a qualifying Argentine/C13 programme despite the visible Hijitus conflict; Canal13 is not established as the requested three-character name. Whole programme clues remain bundled.')
add('M01ee908347c6','R2 R3 R4','broad biography with altered promotion date','uob','Conflates2012hiring with2012promotion, adds actress as target restriction, and bundles family/child/education/music/career conditions.')

add('Mf1feb8bec0b5','R4','2023 sequence after opener','','Specific missing connected match sequence with cutoff-qualified final-opponent condition.')
add('M2bda49564fdf','R3 R4 R5','2020 biography identity','','Despite introductory all-clues phrasing, the explicit focus is the distinctive2020career article and its subject identity, rather than a full list of all years/family conditions.')
add('Mb7b5a63c4b3d','R2 R3 R4 R5','full biography with promotion-date conflation','uob','Restates most requirements across articles and incorrectly moves the later promotion into2012, the supplied hiring year.')
add('M77834e6d26da','R5','May2016 attribution assumed','ub','Treats the2016interview as the May feature without establishing the month-year join.')
add('M5a6dff93cd85','R1','developer former identity','','Tests the remaining developer/former-name relation; no claim it is already established.')

add('M47eebc726200','R4','2023 ordered results','','One connected missing match sequence after the observed opener, expressed as a conditional fit test.')
add('Mfe24c91a9ec1','R4','unobserved Wimbledon95minute','ub','Assumes a new specific fixture/date and95minute event absent from visible evidence.')
add('M605cd63bf6f4','R1 R2 R3 R4','whole fixture verification or replacement','ob','Bundles both club histories and scoring pattern with whole-fixture replacement. History already contains scoring-order counterevidence to PSG, which this generic re-evaluation does not use; not a claim that PSG is true.')
add('Meaaf5295c0cb','R5','assumed May2016 feature','ub','Unverified join between the2016interview and the requested May feature.')
add('M5fef270e4bf8','R1 R2 R3 R4 R5','entire person identification','o','Repeats every original family/wealth/education/music/career constraint plus birth-name goal.')
add('M84804b45ff12','R5','assumed May2016 feature count','ub','Visible2016interview does not establish May2016feature attribution.')
add('M9235401f150c','R5','Enugu club founding','','Specific requested relation for the observed candidate; no unsupported extra qualification asserted.')
add('M0218efb09be8','R2 R3 R4 R5','broad club conjunction and founding','o','Capital,league,article and founding are multiple independent unresolved investigations, rather than one bounded next relation.')
add('M302da4a7dc19','R4 R5','2023 article club subject and founding','','Focuses on a distinctive single identifying article and its subject, without layering independent capital/league/table checks.')

add('M0ea9926bb45c','R1 R2 R3 R4 R5','entire multi-article profile','o','Restates the entire original cross-article conjunction and birth-name question without one current frontier.')

add('M81f00eb4ada0','R2 R3 R4 R5 R6','whole programme conjunction','o','Repeats nearly every original condition across schedule/runtime/network/country/characters; no bounded unresolved relation.')
add('M04023489c520','R1 R2 R3 R4','whole snooker question','o','Repeats career counts, professional dates and the complete match clue; does not select the missing next relation from the observed opener.')

add('M9b3743a9a6dd','R2 R3 R4 R5','whole biography with actress restriction','uob','Repeats the multi-clue person goal and narrows the unknown individual to an actress without establishing that target property.')
add('Mef85a0b80313','R4','95minute assumed LiverpoolMilan event','ub','The specific95minute event is not established by the visible fixture timing or end-of-extra-time Riise evidence.')
add('Med9771fb99ef','R4','unobserved ChelseaArsenal95minute','ub','Assumes an unobserved Chelsea–Arsenal fixture/date and95minute event rather than testing the missing fixture qualification.')

add('M79e099f3f85d','R4','unobserved final95minute event','ub','Early history only supports the PSG event, not this introduced final or95minute free kick.')

if __name__=='__main__':
    # STOP has no free-text proposition to map: apply the already human-reviewed,
    # pre-call all-material closure label deterministically to each masked view.
    contexts=rd(TOP/'f1_state_sufficiency/masked_contexts.json')
    for packet in rd(TOP/'f1_state_sufficiency/masked_packets.json'):
        if packet['review_id'] in A:continue
        if packet['output'] and packet['output']['decision']=='stop':
            c=contexts[packet['context_id']]
            missing=[k for k,x in c['coverage'].items() if not x['resolved']]
            stop(packet['review_id'],c['complete'],'Frozen prefix-only closure: '+('all material requirements covered.' if c['complete'] else 'material coverage remains incomplete for '+', '.join(missing)+'.'))
        elif packet['output'] is None:
            add(packet['review_id'],'','no valid response','','Provider/contract failure; not a semantic invention.')
            A[packet['review_id']]['valid']=False
    wr(TOP/'f1_state_sufficiency/semantic_review.json',A)
    print('judgments',len(A))
