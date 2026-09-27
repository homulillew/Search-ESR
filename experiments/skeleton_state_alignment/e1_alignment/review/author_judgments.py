"""Manual first-pass judgments keyed to masked packets; never reads references.

Defaults below are explicit reviewed acceptances within a viewed group, with
node-specific explanations and per-response exceptions. They are not inferred
from model status or imported Gold. All108 responses remain separate judgments.
"""
import json
from pathlib import Path
P=Path(__file__).resolve().parent
GROUPS=json.loads((P/'VIEW_GROUPS.json').read_text())
LABELS={};NOTES={}
def accept(group,reason,node_reasons=None,exceptions=None):
    g=GROUPS[group-1];assert g['group']==group
    node_reasons=node_reasons or {};exceptions=exceptions or {}
    NOTES[str(group)]={'reason':reason,'node_reasons':node_reasons,'exceptions':exceptions,'review_ids':[o['review_id'] for o in g['outputs']]}
    for o in g['outputs']:
        rid=o['review_id'];assert rid not in LABELS
        nodes={n['requirement_id']:{'status_correct':True,'support_correct':True,'reason':node_reasons.get(n['requirement_id'],reason)} for n in g['input']['Task Skeleton']}
        codes=[]
        for nid,(status,support,why,errors) in exceptions.get(rid,{}).items():
            assert nid in nodes;nodes[nid]={'status_correct':status,'support_correct':support,'reason':why};codes+=errors
        LABELS[rid]={'node_judgments':nodes,'error_codes':sorted(set(codes)),'reason':reason+' Each displayed node and its returned citations reviewed; exceptions recorded per node.'}

accept(1,'Claims are empty. No question condition, paper, author, table or answer is established. All U with empty citations is appropriate.')
accept(2,'C1/C2 substantively establish founder/company/games and graduation parts, but no release/earnings or university founding interval. No marital, gift or building evidence.',{'R1':'P with C1+C2 is appropriate for the coarse founder/education node; the remaining material conditions are absent.'})
accept(3,'Artist death facts support only local death-city/accidentality subsets. C2/C3 support partner and tribute portions, without an evidenced interview or song relation. No charity or song title/form evidence.',
 {'R2':'C1 establishes death/city; distance, deadliest aviation event and country ranking remain missing.',
  'R3':'C1 establishes accidental death and its date, but no aviation event or fifteen-year relation.',
  'R4':'C2/C3 establish partner and post-death tribute; they do not establish interview genre or direct song reference.',
  'R1':'No charity, registration date, unrelatedness or first-name-to-charity relation is evidenced.',
  'R5':'Tribute wording is not an evidenced song-title adjective condition.','R6':'No Claim identifies the referent song title.'},
 {'B003':{'R1':[False,False,'C1 mentions the artist but establishes no charity relation. Mere candidate mention cannot be P.',['entity_overlap_as_support','wrong_support_claim']],
           'R4':[True,False,'P is reasonable from C2/C3. C1 is death/background binding, not substantive support for partnership, interview or song-reference content; the extra citation is not justified here.',['wrong_support_claim']]}})
accept(4,'C7/C9 bind two clinical case records and their shared FOP diagnosis. Publication years and report-country religious history remain absent; childhood timing must not be strengthened.',
 {'R1':'C7/C9 substantively establish two distinct described cases, but no report dates: P is appropriate.',
  'R2':'Both case descriptions explicitly diagnose FOP, so C7+C9 support the shared-disorder relation.',
  'R3':'C7 supports the first clinical course. Pakistani patient nationality does not establish report country or historical religious-size condition.',
  'R4':'C9 establishes biopsy/two-month symptoms and childhood stiffness, but swellings over the next four years do not mean onset four years later.',
  'R5':'C7+C9 supply the scientific name shared by the two bound records; no outside diagnosis is needed.'},
 {'B004':{'R1':[False,False,'Two cases are substantively present in C7/C9. Missing dates justify P, not U.',['partial_as_none']],
           'R4':[False,False,'C9 supports a four-year course, not the required four-year-later onset. The citation is insufficient for F.',['false_supported','partial_as_full','insufficient_support_group']]},
  'B072':{'R4':[False,False,'The exact onset interval is unsupported; C9 warrants P, not F.',['false_supported','partial_as_full','insufficient_support_group']]}})
accept(5,'C1/C2 ground letter roles and transmission, but not courier nickname or accession interval. C3 directly supplies the letter’s regained-region statement and name.',
 {'R1':'P with C1/C2: the letter/transmission chain is evidenced; writing period cannot be established merely from memorandum date and nickname is absent.',
  'R2':'No Claim supplies accession date or letter-to-accession interval.',
  'R3':'C3 explicitly attributes regained North Transylvania to Romania within the letter.',
  'R4':'C3 directly identifies the region in the already bound letter.'})
accept(6,'Empty Claims provide no case records, dates, disorder or clinical facts. All U/empty citations is correct.')
accept(7,'Empty Claims establish no founder, university, spouse, gift or building. All U/empty citations is correct.')
accept(8,'Empty Claims establish no contest, coder, team, medal relation, edition or host. All U/empty citations is correct.')
accept(9,'Empty Claims establish no person, birthplace demographics, presentation, recording gap or death year. All U/empty citations is correct.')

accept(10,'C1/C2 support letter roles and transmission, but no nickname, accession timing, regained-region content or region name. P,U,U,U with the displayed citations is appropriate.',
 {'R1':'Partial letter/transmission support from C1/C2; memorandum date and letter date are distinct.','R2':'No accession date or six-month relation.','R3':'No letter content about regained territory.','R4':'No region name is evidenced.'})
accept(11,'C1 establishes a musical artist’s accidental death in Athens. It supports part of the death/aviation node, not charity, interview or song relations.',
 {'R1':'Artist identity is not a first-name-to-charity relation; no charity evidence exists.','R2':'C1 supports death/city/accidentality; aviation identity, distance, ranking and interval are absent.','R3':'No partner/interview/song evidence.','R4':'No song reference, title or adjective evidence.'},
 {'B055':{'R1':[False,False,'An artist mention alone does not establish any substantive charity predicate.',['entity_overlap_as_support','wrong_support_claim']]}})
accept(12,'Empty Claims support none of the game, DLC, thesis, advisor, mechanics or credits requirements. All U with empty citations is appropriate.')
accept(13,'Claims bind the letter and official transmission and explicitly give its region content; they do not date letter authorship or establish the courier nickname or accession interval.',
 {'R1':'Only the covering memorandum is dated1945. Letter roles are supported, writing interval is not: P rather than F.','R2':'C1/C2 establish official transmission/handoff, but not nickname: P.','R3':'No letter writing or accession date establishing six-month relation.','R4':'C3 directly supports the letter-content relation.','R5':'C3 directly supplies the named region.'},
 {'B013':{'R1':[False,False,'C1 dates the covering memorandum, not the enclosed letter. F moves a date across document roles.',['false_supported','partial_as_full','insufficient_support_group']],
           'R2':[False,False,'C1/C2 already establish official delivery/transmission. Missing nickname leaves P rather than U.',['partial_as_none']]},
  'B067':{'R1':[False,False,'The writing period is not established by the covering memorandum date; C1 cannot fully prove this node.',['false_supported','partial_as_full','insufficient_support_group']]}})
accept(14,'C1 is an undated professor profile. No Claim binds this person to authorship of any candidate target paper, so every paper-specific requirement remains unsupported.',
 {'R3':'Affiliation background without a paper-authorship relation is not substantive support for a target-paper writer’s affiliation.'},
 {'B014':{'R3':[False,False,'The professor-to-target-writer role binding is missing; a related Harran profile alone is not P.',['entity_overlap_as_support','wrong_support_claim']]}})
accept(15,'C7/C9 support two clinical records and their common FOP diagnosis. Country of reporting and report years are absent. The second clinical history must retain its actual timing.',
 {'R1':'C7/C9 support existence of two case records, not their publication dates: P.',
  'R2':'Both records explicitly diagnose FOP: C7+C9 suffice.',
  'R3':'Pakistani patient nationality does not establish where the case was reported, nor historical country/religion conditions: U.',
  'R4':'C7 gives the six-month multi-site progressive pain and walking/shoulder limitation.',
  'R5':'C9 gives the upper-body biopsy-site episode and two-month interval.',
  'R6':'Over the next four years of swellings does not establish onset exactly four years after stiffness: P.',
  'R7':'C7/C9 explicitly name the same scientific disorder in both bound cases.'},
 {'B015':{'R3':[False,False,'Patient nationality is a different relation from report country; C7 does not materially establish this country-history node.',['wrong_support_claim']],
           'R6':[False,False,'C9 does not establish the exact four-year-later onset.',['false_supported','partial_as_full','insufficient_support_group']]},
  'B058':{'R6':[False,False,'The four-year course is weaker than the required onset timing. C9 warrants P, not F.',['false_supported','partial_as_full','insufficient_support_group']]}})
accept(16,'Empty Claims supply no artist/charity/death/aviation/interview/song facts. All U/empty citations is appropriate.')
accept(17,'Empty Claims supply no DLC, game, thesis, advisor, mechanics or designer facts. All U/empty citations is appropriate.')
accept(18,'C1/C2 establish the Australian coder, medal sequence, champion team and named2021 edition. Teammate nationality and host are not supplied; annual/global scope remains incomplete.',
 {'R1':'C2 supplies a university-team world-final event but not annual recurrence or global university participation: P.',
  'R2':'C1 Australian identity plus C2 team/championship relationship jointly suffice.',
  'R3':'C1 explicitly lists bronze/silver/gold/silver in four consecutive IOIs.',
  'R4':'Names of two teammates do not establish equality of their countries.',
  'R5':'C2 states the title edition2021, separately from the actual2022 event date.',
  'R6':'No Claim identifies the host university; MIT is the team university.'})

accept(19,'Empty Claims establish no letter, courier, dates, recovered region or answer. All U/empty citations is appropriate.')
accept(20,'Empty Claims establish no letter identity/delivery, accession interval or regained-region content. All U/empty citations is appropriate.')
accept(21,'C1/C2 support a specific2023 game-related master’s thesis and its advisor. No Claim identifies a DLC, gives advisor degrees/monograph or explicitly supplies American geography.',
 {'R1':'No DLC or release interval in Claims.',
  'R2':'C1 establishes thesis topic/game/year; C2 also expressly repeats2023 master’s thesis, Georgetown and EU4, so both are substantive citations for P. Neither establishes university country.',
  'R3':'C2 establishes the advisor relation, but California degrees and2020 monograph are absent.',
  'R4':'No DLC mechanics evidence.','R5':'No DLC credits or third designer evidence.'})
accept(22,'Current Claims bind the author,2016 mathematics/Vipassana book and2022 same-topic article. They do not establish promotion, same degree university, Iranian advisor or twenty-year PhD interval.',
 {'R1':'C1 supports author/associate-professor role; promotion and degree-university conditions remain missing.',
  'R2':'C2 supports Canadian PhD pursuit; advisor/nationality relation is missing.',
  'R3':'No advisor biography is given.',
  'R4':'C1 supports the book’s mathematics/Vipassana content; ancient liberation characterization and20-year interval are not evidenced.',
  'R5':'C1+C3 support same-author related book/article,2016→2022 six calendar years. This is local coverage, not proof of every author clue.',
  'R6':'C3 directly states the title of the article relationally bound by C1+C3.'})
accept(23,'Empty Claims establish none of the contest, winner, medal, teammate, edition or host facts. All U with no citations is correct.')
accept(24,'C1/C2 describe general SPS symptoms, not either of the two specific case records. There is no case/report binding, so none of the clinical, dating, shared-diagnosis or answer requirements has substantive support.',
 exceptions={'B108':{
 'R2':[False,False,'Generic syndrome descriptions do not establish a diagnosis shared by two particular individuals.',['entity_overlap_as_support','wrong_support_claim']],
 'R3':[False,False,'General symptom progression is not evidence about the first reported patient’s six-month course or country.',['entity_overlap_as_support','wrong_support_claim']],
 'R4':[False,False,'Generic symptoms do not establish the second patient’s biopsy or childhood trajectory.',['entity_overlap_as_support','wrong_support_claim']],
 'R5':[False,False,'A disease name in background Claims is not the scientific diagnosis shared by the two requested reports.',['entity_overlap_as_support','wrong_support_claim']]}})
accept(25,'Separate founder candidates supply partial company/game and education relations. Ding’s2019 childless marriage is explicit. No gift-funded building is evidenced, and2025 children do not refute a2019 condition.',
 {'R1':'C1 and C4 support alternative founder/game candidates; neither proves all game release/earnings conditions. Their properties are not conjoined into F.',
  'R2':'C2 and C5 establish degrees of separate candidate founders, not university founding intervals.',
  'R3':'C5 explicitly establishes Ding married without children at the2019 article time.',
  'R4':'Marriage is antecedent context, not evidence of a gift or building relation.',
  'R5':'No building schedule or affiliation evidence.','R6':'No target-building university evidence.'})
accept(26,'The coarse founder/education node has substantive partial support on one or both alternative candidate branches. C5 supports childless marriage but no gift. No building facts are established.',
 {'R1':'C4+C5 suffice for partial Ding founder/education predicates; C1+C2 also contribute an alternative Kwon branch. Neither response asserts a mixed-candidate full proof.',
  'R2':'C5 directly supports a substantive marital subcondition; gift/complex remain absent.',
  'R3':'No building schedule or affiliation.', 'R4':'No target building or university.'})
accept(27,'Book/article Claims support the2016→2022 relation and title. Author/education/book-PhD timing are only partial; advisor biography is absent.',
 {'R1':'C1 supports author and associate-professor role, not2022 promotion or undergraduate/graduate institution identity.',
  'R2':'C2 supports Canadian PhD pursuit, not the Iranian advisor. C1 is author/book background rather than substantive PhD evidence.',
  'R3':'No advisor identity or biography.',
  'R4':'C1 establishes the mathematics/Vipassana book; the20-year PhD-completion interval is missing.',
  'R5':'C1+C3 establish same author, related subject and six-calendar-year publication difference.',
  'R6':'C3 supplies the named article after its book relation is grounded.'},
 {'B064':{'R2':[True,False,'P is correct from C2. C1 contributes author identity/book background, not the Canadian-PhD/advisor predicate, so that extra citation is not substantive here.',['wrong_support_claim']]}})

accept(28,'Claims establish winning Australian coder, medal sequence, edition and its host. No teammate-country equality is evidenced. Annual/global-contest scope remains partial.',
 {'R1':'C2 supports a university-team world-final episode, not annual recurrence/global participation.',
  'R2':'C1 nationality plus C2 winning-team membership support the full relation.',
  'R3':'C1 gives the exact consecutive medal sequence.',
  'R4':'C2 names the other teammates but does not give either country or compare them.',
  'R5':'C2 gives winning title edition2021, distinct from the2022 held-on date.',
  'R6':'C3 names the host for the bound edition. C2 additionally establishes the explicit winning-year relationship in this node; C2+C3 or contextual C3 alone is acceptable.'},
 {'B105':{'R4':[False,False,'Known teammate identities are not substantive support for their same-country relation.',['entity_overlap_as_support','wrong_support_claim']]}})
accept(29,'Empty Claims do not establish any paper, author, affiliation, table or title fact. All U/empty citations is correct.')
accept(30,'C1/C2 support Australian winner, exact medal sequence and winning title year; contest scope is partial, teammate-country equality and host are unsupported.',
 {'R1':'C2 establishes one university-team final, not recurrence/global participation.',
  'R2':'C1+C2 combine nationality and team victory without changing argument roles.',
  'R3':'C1 gives bronze/silver/gold/silver at2015–2018 IOIs.',
  'R4':'Names do not establish a country comparison.',
  'R5':'C2 explicitly identifies the2021 title edition.',
  'R6':'MIT is the team institution, not evidence of a host university.'})
accept(31,'C1 supports founder/company/games and C2 supports degree; missing game release/earnings and university founding intervals leave P. There are no marital, donation or building Claims.',
 {'R1':'C1 supports the company/game chain only in part.', 'R2':'C2 supports graduation, not institution founding dates.',
  'R3':'No spouse/childlessness Claim.', 'R4':'No donation/building relation.',
  'R5':'No building opening or affiliation evidence.', 'R6':'No target-building university.'})
accept(32,'No Claims: artist, charity, aviation event, partner interview and song are all unestablished. All U/empty citations is correct.')
accept(33,'C1/C2 support author employment/book and Canadian PhD pursuit in part. No advisor biography or later article exists in the current Claims; do not use the book title as article evidence.',
 {'R1':'C1 supports author and associate-professor role, not promotion/degrees-university identity.',
  'R2':'C2 supports Canadian PhD pursuit, not Iranian advisor.',
  'R3':'No advisor identity/background.',
  'R4':'C1 supports mathematics/Vipassana book but not the ancient-liberation characterization or20-year PhD interval.',
  'R5':'Book existence does not establish any later journal article relation.',
  'R6':'No referent article/title Claim.'})
accept(34,'C1/C2 bind the2023 EU4 thesis and advisor. University country and advisor credentials are not stated, and no DLC or credits are discovered.',
 {'R1':'No DLC release relation.', 'R2':'C1 provides substantive thesis/game/topic/year support, but not American-university condition.',
  'R3':'C2 establishes advisor relation only; degrees/monograph remain absent.',
  'R4':'No DLC mechanics evidence.', 'R5':'No specific DLC or designer credits.'})
accept(35,'Empty Claims support none of the case/report/date/clinical/diagnostic requirements. All U/empty citations is correct.')
accept(36,'The sole Claim is an undated Harran professor profile with no relation to authorship of a target paper. Paper-specific requirements remain U.',
 {'R4':'Affiliation of an unbound candidate is background; no target-paper writer role has been established.'},
 {'B044':{'R4':[False,False,'C1 does not establish that this professor wrote the target paper. Candidate affiliation alone cannot supply P for that bound writer relation.',['entity_overlap_as_support','wrong_support_claim']]}})

accept(37,'No Claims: author, career, PhD/advisor, book, later article and title are all unestablished. All U/empty citations is correct.')
accept(38,'Euler birth biography is not evidence about a book referencing him. No book-content, cleaning method, other referenced people or title relationship is established.',
 exceptions={rid:{'R4':[False,False,'Matching a possible L.E. biography does not establish that the target book references this figure. The required source-to-person binding is absent.',['entity_overlap_as_support','wrong_support_claim']]} for rid in ('B046','B104')})
accept(39,'C1/C2 support author/book and Canadian PhD parts only. No Iranian advisor, later journal article or article title is supplied.',
 {'R1':'C1 supplies author and associate-professor position, not2022 promotion/same degree institution.',
  'R2':'C2 supplies Canadian PhD pursuit, not advisor nationality.', 'R3':'Advisor biography absent.',
  'R4':'C1 supplies the math/Vipassana book, not20-year PhD timing or ancient-liberation characterization.',
  'R5':'A book alone is not evidence that the described later article exists.', 'R6':'No article title; book title cannot substitute.'})
accept(40,'Only an Euler birth Claim is visible, with no book-reference relationship. Every book requirement remains unsupported.',
 exceptions={rid:{'R5':[False,False,'C1 gives a plausible L.E. candidate biography, not the material book-references-figure relation.',['entity_overlap_as_support','wrong_support_claim']]} for rid in ('B050','B059')})
accept(41,'No Claims establish author career, PhD/advisor, book or article. All U/empty citations is correct.')
accept(42,'Letter/transmission roles are supported in C1/C2. The memorandum date is not the letter writing date; nickname, accession interval and regained-region content are absent.',
 {'R1':'Role/letter support is partial because only the covering memorandum is dated.',
  'R2':'Official transmission/handoff is a substantive part; missing nickname leaves P rather than U.',
  'R3':'No accession interval evidence.', 'R4':'No region content in the visible letter Claims.', 'R5':'No region name.'},
 {rid:{'R1':[False,False,'Neither C1 nor C2 dates authorship of the letter; F transfers the covering memorandum date to another document.',['false_supported','partial_as_full','insufficient_support_group']],
       'R2':[False,False,'C1/C2 explicitly supply official transmission/handoff. U discards that substantive partial support.',['partial_as_none']]} for rid in ('B053','B069')})
accept(43,'General SPS symptoms do not bind either specific patient/report. Every case-specific requirement remains unsupported, even though the symptom descriptions are topically related.',
 exceptions={
 'B056':{'R7':[False,False,'A generic disease name is not the scientific diagnosis shared by the two target cases.',['entity_overlap_as_support','wrong_support_claim']]},
 'B098':{rid:[False,False,'The cited general syndrome Claims do not establish this predicate for the requested clinical records; the patient/report binding is missing.',['entity_overlap_as_support','wrong_support_claim']] for rid in ('R2','R4','R5','R6','R7')}})
accept(44,'DLC/game dates support a greater-than-three-year interval; current Claims also supply advisor relation, mechanics subsets and ordered designer credits. Missing geography, advisor credentials and playable-European-nation condition remain unresolved.',
 {'R1':'C3+C5 jointly establish strategy game, DLC relation and interval; either conflicting August2013 date is more than three years before October2016.',
  'R2':'C1 gives thesis/topic/game/year, but not American university location. P is justified.',
  'R3':'C2 supports advisor relationship, but neither California degrees nor2020 monograph.',
  'R4':'C4/C6/C7 support religious, technology and Ottoman/government mechanics; European/playable nation is unestablished.',
  'R5':'C8 ordered credits and C9 explicit third-designer statement each suffice for the name.'},
 {'B060':{'R2':[False,False,'C1 does not state that Georgetown is American. F requires an unprovided geographic condition. Output alone cannot distinguish recalled world knowledge from importing the question premise.',['false_supported','partial_as_full','insufficient_support_group']],
           'R4':[True,False,'P is supported by C4/C6/C7. C3 supplies release/identity context, not any mechanics predicate; the extra citation is not substantive here.',['wrong_support_claim']]}})
accept(45,'Artist death supports part of the aviation/death node and partner/tribute Claims support part of the interview node. There is no charity or evidenced song-reference/title relation.',
 {'R1':'No charity facts; artist name alone is insufficient.', 'R2':'C1 supplies death/city/accidentality, not aviation linkage.',
  'R3':'C2/C3 support partner/tribute subset, not interview genre or song reference.', 'R4':'Tribute phrase is not evidence of an actual song title or its adjective form.'},
 {'B062':{'R1':[False,False,'C1 contains no charity predicate; P promotes candidate mention into relational support.',['entity_overlap_as_support','wrong_support_claim']]}})

accept(46,'C2 binds a concrete2022 coauthored paper; C1 adds an undated affiliation and C5 its exact emotion percentage. JBSE and2023-specific affiliation remain unestablished; paper table evidence is partial.',
 {'R1':'Treat bibliographic2022 as the question’s written/publication interval in ordinary paper identification; the literal distinction is an ambiguity.',
  'R2':'C2 supports the two-coauthor portion, not another JBSE paper.',
  'R3':'C1+C2 jointly bind professor/affiliation to an actual paper writer;2023 remains missing.',
  'R4':'C4 establishes organized paper-specific data tables and particular information, but not six total. Under the substantive-subcondition reading this is P; count-conflict versus U is an annotation-sensitive boundary.',
  'R5':'C5 explicitly states a table emotion at13.53 percent in the bound paper.',
  'R6':'C2 names the candidate paper; other identifying conditions remain separate unresolved nodes.'},
 {rid:{'R4':[False,False,'The paper-specific tables/content in C4 provide substantive partial support despite the five/six count mismatch. U discards that part. This P/U boundary is semantically ambiguous and not equivalent to a false-full error.',['partial_as_none']]} for rid in ('B063','B066')})
accept(47,'Empty Claims do not establish the person, birthplace population, presentation, recording hiatus or death year. All U/empty citations is correct.')
accept(48,'C2 provides a concrete dated paper and two named coauthors; affiliation and tables remain only partial, while C5 supplies the exact emotion value. No separate JBSE relation is evidenced.',
 {'R1':'Bibliographic2022 licenses the paper-year interval under ordinary identification usage; writing-versus-publication is a known ambiguity.',
  'R2':'The unqualified two-coauthor Claim is read as the author list. Exhaustiveness is an ambiguity, not an imported author.',
  'R3':'No other-JBSE-paper Claim.',
  'R4':'C1 establishes Harran affiliation and C2 authorship of this paper, but not as-of2023.',
  'R5':'C4 supports organized paper-specific tables/content, but not six total. P/U under conflicting count is annotation-sensitive.',
  'R6':'C5 directly establishes a named emotion at13.53 percent.',
  'R7':'C2 supplies the bound candidate’s name, not a certificate that all remaining clues are satisfied.'},
 {rid:{'R5':[False,False,'Some substantive table/content predicates are supported by C4; the unestablished six-table total should leave P under this reading, rather than erase that support.',['partial_as_none']]} for rid in ('B070','B078')})
accept(49,'C1/C2 establish winner, nationality, medal history and edition; C3 establishes the host. Neither teammate country is given. Annual/global scope remains partial.',
 {'R1':'C2 supports the university-team final, not annual recurrence/global participation.',
  'R2':'C1 nationality and C2 team victory jointly cover the relation.',
  'R3':'C1 directly gives the consecutive medal sequence.',
  'R4':'Teammate identities are not evidence of the country comparison.',
  'R5':'C2 directly identifies the2021 winning title edition.',
  'R6':'C2 binds the explicit winning-year condition and C3 supplies its host university. Both citations contribute to the node as phrased, although C3 is sufficient with current context.'})
accept(50,'C1 supports accidental death, city and death date, but supplies no charity, partner interview or song evidence.',
 {'R1':'No charity relationship or charity facts.', 'R2':'Death/city subset supported by C1; aviation distance/ranking missing.',
  'R3':'Accidental-death operand supported by C1; fifteen-year aviation interval absent.',
  'R4':'No partner/interview relation.', 'R5':'No song adjective condition.', 'R6':'No song title.'},
 {'B074':{'R1':[False,False,'Artist identity alone is not substantive evidence for the charity/name relation.',['entity_overlap_as_support','wrong_support_claim']]}})
accept(51,'C3+C5 establish DLC/game timing, C2 the advisor link, C4/C6/C7 some mechanics and C8/C9 the third-designer name. Geographic and advisor credentials remain missing.',
 {'R1':'Both August2013 base-game dates give an interval greater than three years to October2016; C3+C5 suffice.',
  'R2':'C1 gives thesis/game/topic/year but no American-country fact.',
  'R3':'C2 gives advisor relationship, not California degrees or monograph.',
  'R4':'C4/C6/C7 give religious/technology/Ottoman mechanics, not the European/playable qualification.',
  'R5':'C8 ordering and C9 explicit third credit each establish the full name.'},
 {'B086':{'R2':[False,False,'C1 never states the American-university condition. F requires importing an unprovided geography fact; visible output cannot distinguish memory from question-premise promotion.',['false_supported','partial_as_full','insufficient_support_group']]}})
accept(52,'Empty Claims establish no book, illustration/object content, cleaning method or referenced person. All U/empty citations is correct.')
accept(53,'Empty Claims establish no founder/game, education, marriage, gift, building or university. All U/empty citations is correct.')
accept(54,'Empty Claims establish none of the book content, methods, person-reference relationships or title. All U/empty citations is correct.')

if __name__=='__main__':
    assert len(NOTES)==54 and len(LABELS)==108,'Review all masked groups before sealing'
    assert set(LABELS)=={p['review_id'] for p in json.loads((P/'PACKETS.json').read_text())}
    for name,value in [('MANUAL_GROUP_NOTES.json',NOTES),('JUDGMENTS.json',LABELS)]:
        with (P/name).open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
