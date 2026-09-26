"""Single-reviewer source-relative audit and prefix-only labels; no API imports."""
import sys,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from transport import P,rd,save,dg,head
B=P/'bank'; states=rd(B/'STATE_INVENTORY.json'); admissions=rd(B/'CLAIM_REVIEW_PACKET.json')
# Reasons refer to each admission's own archived observation, never later results.
reasons={
0:'Kaul quotation explicitly reports recording, custodians, dry well and motive; attribution retained.',
1:'Window quotes Kamil and explicitly explains his disputed attribution; claim is about his argument.',
2:'Azad quotation explicitly gives this interpretation, not an adjudicated authorship fact.',
3:'Window names Pemberton, final, clean sheet and Halesowen in his quotation.',4:'Opening paragraph directly describes progression and managing partnership.',
5:'Biography explicitly states partner Ryan and October 2012 business start.',6:'Biography names both professional clubs.',7:'Date of birth is explicit.',8:'Squad table explicitly lists both Chelsea seasons with 27.',
9:'Table gives all four counts and 49; claim retains incompleteness warning.',10:'Infobox lists these caps and total52. Claim reports the list, not a guarantee of comprehensive all-competition coverage.',
11:'Youth clubs/dates in infobox and body support claim.',12:'Named Nicolas entry explicitly describes retirement at24, chartered surveying and company.',
13:'Queen section explicitly gives reign dates and throne accession.',14:'Both superlatives occur verbatim in source; source-relative support is not independent historical verification.',
15:'Named Christina section explicitly gives dates, accession age and abdication.',16:'Customer review explicitly calls Maria first queen regnant; weak source quality is distinct from unsupported extraction.',
17:'Observed PDF body gives dated3Nov2023 and proposed method; arXiv identity comes from observed URL.',18:'PDF title and observed arXiv URL establish title.',19:'Ordered PDF byline names Beacom second.',
20:'Observed title Prof. MEHMET DİYADDİN YAŞAR plus harran.edu.tr profile URL supports profile-relative claim; not proof of employment as of2023.',
21:'Byline and bibliographic citation explicitly give names/date/title/volume/pages.',22:'Abstract explicitly enumerates five categories.',23:'Results text says data organized in five tables and labels Table2 Emotion; not proof of total table count.',24:'Happiness row gives33 and13.53.',
25:'Body gives foundation year and named games.',26:'Education paragraph states degree and Sogang.',27:'Dated Forbes snapshot explicitly gives separated and2 children; does not establish family status in2019.',
28:'Dated2019 story gives alias, founding month/year and games business.',29:'Same story gives degree and explicitly married without children at publication.',
30:'Dated news report gives same-day death, age, fall and reported Athens location.',31:'Infobox partner field names Evita Manji.',32:'Window explicitly attributes quote to a later online tribute, not automatically the question’s interview.',
33:'Observed product title/date/publisher and author biography give all components.',34:'Biography explicitly gives both scholarships and Dalhousie.',35:'PDF front matter gives title, author, journal, date and pagination.',
36:'Infobox gives exact birthday and Basel/Swiss Confederacy.',37:'NORD paragraph gives time course and stability/worsening.',38:'NORD paragraph gives all named symptoms and regions.',39:'NINDS explicitly says thought autoimmune.',40:'NINDS explicitly describes this type and symptom list; source-relative extraction only.',
41:'Case report explicitly confirms FOP with canonical mutation.',42:'Same report describes biopsy-site swelling and advice to avoid trauma.',43:'Case presentation gives country, age, six-month history and affected body parts.',44:'Opening paragraph explicitly links misdiagnosis, procedures and exacerbation.',
45:'Case presentation gives age16, biopsy two months earlier, stiffness at9 and swellings over next4years. Does not independently establish publication date.',46:'Introduction explicitly links mutations and diagnostic sequencing.',47:'MedlinePlus explicitly describes trauma-triggered swelling followed by ossification.',
48:'Repository metadata explicitly gives author, title, MA, Georgetown and2023.',49:'Same metadata names advisor.',50:'Steam observed product metadata gives title and release11Oct2016.',51:'Visible diary table supplies all three dates/topics.',52:'Claim correctly retains conflicting infobox/body dates instead of silently selecting one.',
53:'Manual opening explicitly states technology change.',54:'Same paragraph names government/subject changes and both examples.',55:'Manual credits list content designers in this order.',56:'Direct ordinal inference from three-name credit list.',
57:'Country and individual IOI results explicitly establish four-year medal sequence.',58:'Team-results row gives year label, actual date, full roster and championship.',59:'Observed world-finals-2021 factsheet URL supplies event year; body names host university UAP.',
60:'Footnote explicitly gives letter, transmission memorandum date and Donovan’s position.',61:'Footnote directly quotes unofficial delivery by OSS officer.',62:'Letter explicitly thanks Red Army for regaining North Transylvania.'}
assert set(reasons)==set(range(len(admissions)))
save(B/'CLAIM_SUPPORT_REVIEW.json',[dict(c,review={'status':'supported','reason':reasons[i],'reviewer':'Codex single reviewer; source-relative','not_global_truth_audit':True}) for i,c in enumerate(admissions)])
# Each row is an evaluator-only material relation, never model-visible state.
definitions={
'F01':['candidate identity from a single distinguishing biographical clue','parents state/country of origin','two older siblings reported2023','bachelor completion2018–22','doctor aspiration','talent noticed at age4 in2023 report','contract2019–22 and later extension2020–23'],
'F02':['recorded poems deposited in a dry well after death','birth in1720–1764','husband also a poet','earlier poetess beauty-derived name and chronological relationship'],
'F03':['retirement followed by chartered surveying','business with partner in early2010s','Premier League youth academy membership','birth in1980s','maximum appearances for any one club below48','jersey27'],
'F04':['non-English multilingual queen identity','only queen regnant of her kind in relevant era/country','book identity','more than300 pages','academic publisher and February after2010 publication','author identity','North American PhD since2000','coauthored coursebook before2019'],
'F05':['2018–22 article1 identity/title','second acknowledged person UCR associate professor throughSep2020','article1 second author = article2 third author','2016 article2 identity','article2 first author CCAPP affiliation','article2 second author = article3 second author','2023 article3 proposes practical neutrino-detection method'],
'F06':['individual birth1830–40','farmer parent','Wisconsin arrival before15','six to nine children','death1890–1900','adventures book edition2000–05','book author descendant identity','author directs youth organization for16–29years','organization founded1910–30','namesake cemetery block66 burial1960–70','baptismal name'],
'F07':['paper identity/date2012–22 and two authors','author JBSE publication2016–23','author Harran staff as of2023','total six tables','emotion at13.53 percent'],
'F08':['founder/company identity','game release2000–10 through games division','game top-earning status through2019','founder alma mater founded1930–70','married without children through2019','couple foundational building gift','building complex and opening2018–21 as of2019','recipient university'],
'F09':['artist identity/accidental death city and year','unrelated charity sharing first name registered2000–10','country deadliest aviation accident by2023','accident site20–30miles from death city','accident15years before death','partner interview and reference to own song','song title one-word adjective'],
'F10':['2022 associate-to-full-professor promotion','undergraduate/graduate alma mater equals employer','Canadian doctorate and completion year','Iranian advisor identity','advisor intended writer switched at end highschool','advisor Minnesota doctorate','book subject and publication20years afterPhD','journal article title six years afterbook'],
'F11':['book identity and130–140illustrations','telephone and telegraph descriptions','rust cleaning substance named in Three Dog Night song','alternative oil named in country song','referenced mechanical engineer born early1800s','scientist with poet father','L.E. early1700s centralEuropean birth and reference in book'],
'F12':['person identity/birth1948–52','birthplace official census growth5.88percent2010–20','1990 cultural-center presentation','recording hiatus1986–94','year of death'],
'F13':['first case half-year progressive pain and mobility symptoms','first case country largest of dominant religion at establishment','second case biopsy2months before pain/swelling','second case childhood stiffness then swelling4years later','two reports in different years within2010s','shared disorder identification'],
'F14':['2023 American masters thesis on postcolonialism in game','advisor identity','advisor two California-university degrees','advisor2020 videogames monograph','DLC more than3years after basegame','religion and technology changes','European playable nation mechanics','third credited content designer'],
'F15':['Australian coder IOI bronze/silver/gold/silver in consecutive years','championship team and competition title year','other two teammates from same country','host university'],
'F16':['ruler-to-ruler letter in first half20thcentury','delivery official nicknamed by recipient after body part','letter about6months after writer accession','regained region named in letter']}
# Covered indexes become established only at specified prefix; partials cannot close gaps.
covered={
'F02':{1:[0]},'F03':{2:[1],3:[3,5],5:[2],6:[0]},
'F05':{1:[6]},'F07':{2:[0,2],3:[4]},'F08':{3:[4]},'F09':{1:[0]},
'F10':{2:[7]},'F13':{4:[0],5:[2,3,5]},'F14':{1:[0,1],3:[5,6],4:[4],6:[7]},
'F15':{1:[0,1],2:[3]},'F16':{1:[0],2:[3]}}
partials={
'F01':{},'F02':{},'F03':{1:[0],4:[4]},'F04':{1:[0,1],2:[0,1]},
'F05':{1:[6],2:[5]},'F06':{},'F07':{1:[2],2:[4],3:[3]},
'F08':{1:[0,1,3],3:[0,1,3]},'F09':{2:[5],3:[5,6]},
'F10':{1:[2,6]},'F11':{1:[6]},'F12':{},
'F13':{1:[5],3:[2,5],4:[0],5:[3,5]},'F14':{2:[4]},'F15':{},'F16':{1:[1]}}
oracle_initial={
'F01':'Identify the individual in a2023 biographical article reporting that a parent noticed their talent at age4.',
'F02':'Identify the poetess whose recorded poems were reportedly deposited in a dry well after death.',
'F03':'Identify a former footballer who became a chartered surveyor after retirement.',
'F04':'Identify a non-English queen regnant documented as speaking several languages.',
'F05':'Identify a2023-submitted paper proposing a practical method of neutrino detection.',
'F06':'Identify the author who directed the youth organization described in the question for16–29years.',
'F07':'Identify a research paper reporting an emotion at13.53percent in a table.',
'F08':'Identify a university-building foundational gift made by a gaming-company founder and spouse.',
'F09':'Identify an interview in which a deceased musician’s partner links the musician to one of their songs.',
'F10':'Identify a book connecting mathematics with an ancient liberation practice.',
'F11':'Identify a book described as containing130–140illustrations.',
'F12':'Identify the birthplace whose official2010–2020 population growth was5.88percent.',
'F13':'Identify the diagnosis in a case report describing pain and swelling at a biopsy site two months after biopsy.',
'F14':'Identify the strategy game studied in a2023 American master’s thesis on postcolonialism.',
'F15':'Identify the Australian programmer with consecutive IOI bronze/silver/gold/silver medals.',
'F16':'Identify an official nicknamed after a body part by a ruler receiving a letter.'}
oracle_later={
'F02':'When was Arinimaal born?',
'F03':'When was Alexis Nicolas born?',
'F04':'Which languages did {candidate} speak?',
'F05':'Who is the second author of arXiv:2311.01667?',
'F07':'Did Mehmet Diyaddin Yaşar author a paper in the Journal of Baltic Science Education during2016–2023?',
'F08':'Did {candidate} and their spouse make a foundational gift for a university building?',
'F09':'Is there a charity with Sophie in its name registered during2000–2010?',
'F10':'Who supervised Alka Marwaha’s doctorate at Dalhousie?',
'F11':'Which illustrated books mention Leonhard Euler?',
'F13':'Was a case of {candidate} reported with swelling at a biopsy site two months after the procedure?',
'F14':'Which two degrees did Amanda D. Phillips obtain at a California university?',
'F15':'Were Mingyang Deng and Xiao Mao from the same country?',
'F16':'Was the official delivering King Michael’s letter given a body-part nickname by its recipient?'}
labels=[]
for s in states:
 cid=s['state_id'][:3];n=int(s['state_id'][-2:]);b=s['belief'];cv=set();pt=set()
 for k,v in covered.get(cid,{}).items():
  if n>=k:cv.update(v)
 for k,v in partials.get(cid,{}).items():
  if n>=k:pt.update(v)
 pt-=cv;gap=[d for j,d in enumerate(definitions[cid]) if j not in cv]
 issue=oracle_initial[cid] if not b['hypothesis'] else oracle_later[cid]
 if cid=='F03' and n==1:issue='When was Alan Pemberton born?'
 if cid=='F03' and n>=3:issue='Did Alexis Nicolas become a chartered surveyor after leaving football?'
 if cid=='F03' and n>=6:issue='What was the highest full-career appearance total Alexis Nicolas made for any single club?'
 if cid=='F04':issue=issue.format(candidate='Wilhelmina' if n==1 else 'Christina of Sweden')
 if cid=='F05' and n>=2:issue='Which2016 research papers list John F. Beacom as their second author?'
 if cid=='F08':issue=issue.format(candidate='Ding Lei' if n==3 else 'Kwon Hyuk-bin')
 if cid=='F13':issue=issue.format(candidate='stiff person syndrome' if n<3 else 'fibrodysplasia ossificans progressiva')
 if cid=='F13' and n>=3:issue='In which year was the FOP biopsy-site case report published?'
 if cid=='F15' and n==2:issue=oracle_later[cid]
 # Literal source-relative Claims permit a conservative remaining maximum-appearances gap.
 note='Coverage uses only current Claims. H, however assertively phrased, never establishes candidate=answer.'
 if cid=='F03' and n>=5:note+=' Reported per-club caps and incomplete competition totals do not unambiguously establish the full-career maximum; retain that local gap. A less strict reading would make S05 one-gap and S06 closure, reported as sensitivity only.'
 if cid=='F13' and n>=4:note+=' Pakistani boy is not an explicit reporting-country assertion in C7; country-history condition remains open. Neither case publication year is in Claims.'
 if cid=='F07' and n==3:note+=' Five data tables does not contradict six total tables without total-count evidence.'
 if cid=='F08' and n==2:note+=' Two children in2025 does not logically contradict childlessness in2019; H clearing is the historical Writer choice.'
 lab={'state_id':s['state_id'],'qid':s['qid'],'split':s['split'],'supported_claims':True,'eligible_unresolved':bool(gap),'covered':[d for j,d in enumerate(definitions[cid]) if j in cv],
 'partial':[d for j,d in enumerate(definitions[cid]) if j in pt],'open':[d for j,d in enumerate(definitions[cid]) if j not in cv and j not in pt],
 'acceptable_local_gap_family':gap,'oracle_issue':issue,'no_h':not bool(b['hypothesis']),
 'h_strength':'none' if not b['hypothesis'] else ('strong' if (cid=='F03' and n>=5) or(cid=='F15' and n>=1) or(cid=='F14' and n>=4) or(cid=='F13' and n>=5) else 'provisional'),
 'one_gap':len(gap)==1,'strong_h_one_gap':len(gap)==1 and bool(b['hypothesis']), 'note':note}
 labels.append(lab)
save(B/'OFFLINE_LABELS.json',{'qch_commit':head(),'question_conditions':definitions,'labels':labels,'reviewer':'Codex single reviewer; no model results available'})
idx={x['state_id']:x for x in labels};selected=[]
for cid in definitions:
 ss=[s for s in states if s['state_id'].startswith(cid) and idx[s['state_id']]['eligible_unresolved']];limit=4 if ss[0]['split']=='development' else 3
 picks=[ss[0]]
 if len(ss)>1:
  if limit==4:picks.append(ss[1])
  hs=next((s for s in ss[2 if limit==4 else 1:] if s['belief']['hypothesis']),ss[1]);picks+=[hs,ss[-1]]
 uniq={s['state_id']:s for s in picks}
 while len(uniq)<min(limit,len(ss)):
  remaining=[s for s in ss if s['state_id'] not in uniq];positions=[ss.index(s) for s in uniq.values()]
  s=max(remaining,key=lambda s:(min(abs(ss.index(s)-i) for i in positions),-ss.index(s)));uniq[s['state_id']]=s
 selected.extend(uniq.values())
selected.sort(key=lambda s:s['state_id'])
for split in ['development','confirmation']:
 rows=[dict(s,label=idx[s['state_id']]) for s in selected if s['split']==split];save(B/(split.upper()+'.json'),rows)
 print(split,len(rows),'qids',len({s['qid'] for s in rows}),'noH',sum(s['label']['no_h'] for s in rows))
save(B/'ONE_GAP_STRESS.json',[dict(s,label=idx[s['state_id']]) for s in states if idx[s['state_id']]['one_gap']])
# Manually reviewed material local relations answered by authentic single claims.
delta_issues={0:'Which poetess had recorded poems deposited in a dry well after death, according to T.N. Kaul?',
5:'When did Alexis Nicolas start Springer Nicolas with Ryan?',7:'When was Alexis Nicolas born?',8:'Which shirt number did Alexis Nicolas wear for Chelsea in2002/03?',9:'What overall club-match total does WorldFootball report for Alexis Nicolas?',11:'Was Alexis Nicolas a Chelsea youth player?',12:'Did Alexis Nicolas leave football to become a chartered surveyor?',
13:'In which years did Wilhelmina reign?',15:'When did Christina of Sweden abdicate?',16:'Was Maria I Portugal’s first queen regnant?',
17:'Does arXiv:2311.01667 propose a practical method for atmospheric tau-neutrino detection?',18:'What is the title of arXiv:2311.01667?',19:'Who is the second author of arXiv:2311.01667?',
20:'Is Mehmet Diyaddin Yaşar listed as a professor on a Harran profile?',21:'Who coauthored the2022 creative-comparisons science-education paper?',24:'What percentage is Happiness in Table2 of that paper?',
25:'Which company did Kwon Hyuk-bin found?',26:'Where did Kwon Hyuk-bin earn his degree?',29:'Was Ding Lei reported married without children in2019?',
30:'In which city did Sophie die?',31:'Who was Sophie’s partner?',32:'What did Evita Manji say about Sophie in the later online tribute?',
33:'Who wrote The Secret World of Vipassana and Mathematics?',34:'At which Canadian university did Alka Marwaha pursue a doctorate?',35:'What2022 Vipassana journal article did Alka Marwaha author?',
36:'Where and when was Leonhard Euler born?',
42:'Did a confirmed FOP case report describe pain and swelling at a biopsy site?',43:'Did a Pakistani FOP case involve six months of progressive pain restricting walking?',45:'Did a FOP case involve biopsy two months before presentation?',
48:'Which game did Mitchell Losito’s2023 thesis study?',49:'Who advised Mitchell Losito’s2023 thesis?',50:'When was Europa Universalis IV: Rights of Man released?',52:'In which year was Europa Universalis IV released?',56:'Who is the third content designer credited for Rights of Man?',
57:'Which Australian programmer won the consecutive2015–2018 IOI bronze/silver/gold/silver sequence?',58:'Which championship title year was won by MIT ZEROONE with Jerry Mao?',59:'Which university hosted the ICPC2021 World Finals?',
60:'When was King Michael’s letter transmitted under Donovan’s memorandum?',61:'To whom did King Michael hand the letter in Bucharest?',62:'Which regained region is named in King Michael’s letter?'}
# Only independently answerable relation; Euler birth year/location are separable.
delta_issues[36]='Which well-known figure with initials L.E. was born in the early1700s in central Europe?'
# Discovery issues contain no candidate/title first learned in the added Claim.
delta_issues[0]='Which poetess had recorded poems deposited in a dry well after death?'
delta_issues[5]='Which former footballer started a business with a partner in the early2010s?'
delta_issues[13]='Identify a non-English queen regnant and her reign period.'
delta_issues[15]='Identify a queen regnant of Sweden.'
delta_issues[16]='Identify Portugal’s first queen regnant.'
delta_issues[17]='Identify a2023 paper proposing a practical neutrino-detection method.'
delta_issues[20]='Identify a member of Harran University’s academic staff.'
delta_issues[21]='Identify a2012–2022 research paper coauthored by Mehmet Diyaddin Yaşar.'
delta_issues[25]='Identify a company founder associated with a high-earning online video game.'
delta_issues[29]='Identify a gaming-company founder reported married without children in2019.'
delta_issues[30]='Identify a musical artist who died accidentally.'
delta_issues[33]='Identify the author of a book connecting mathematics and an ancient liberation technique.'
delta_issues[34]='At which Canadian university did the author of the mathematics/liberation book pursue a doctorate?'
delta_issues[48]='Identify the game studied in a2023 American master’s thesis on postcolonialism.'
delta_issues[49]='Who advised the2023 American thesis on postcolonialism in a strategy game?'
delta_issues[50]='Identify a Europa Universalis IV expansion released over three years after the base game.'
delta_issues[60]='Identify a first-half-twentieth-century letter from one country’s ruler to another.'
delta_issues[61]='Who delivered the ruler-to-ruler letter described in the question?'
# Do not use identity examples that only establish a subset of the specified clue,
# or a claim whose scope does not actually close that relation.
for i in [13,21,25,34,49,50,61]:delta_issues.pop(i)
ts=rd(B/'TRANSITIONS.json');pairs=[]
for i,issue in delta_issues.items():
 c=admissions[i];t=next(t for t in ts if t['case_id']==c['case_id'] and t['observation_hash']==c['observation_hash'] and c['statement'] in t['actual_claims_to_add'])
 a=t['pre_state'];belief={'question':a['question'],'claims':[v['statement'] for v in a['claims']],'hypothesis':a['hypothesis'] or ''}
 if c['statement'] in belief['claims']:continue
 bb=copy.deepcopy(belief);bb['claims'].append(c['statement'])
 pairs.append({'pair_id':f'D{i:02d}','qid':c['qid'],'case_id':c['case_id'],'split':t['split'],'g':issue,'A':belief,'B':bb,'added_claim':c['statement'],'claim_admission_index':i,'observation_hash':c['observation_hash'],'A_natural':True,'B_controlled_projection':True,'H_held_fixed':True})
chosen=[]
for split in ['development','confirmation']:
 qs=sorted({p['qid'] for p in pairs if p['split']==split});groups={q:[p for p in pairs if p['qid']==q] for q in qs}
 out=[]
 while len(out)<12 and any(groups.values()):
  for q in qs:
   if groups[q] and len(out)<12:out.append(groups[q].pop(0))
 chosen+=out;print('pairs',split,len(out),'qids',len({p['qid'] for p in out}))
save(B/'COVERAGE_PAIRS.json',chosen)
save(B/'SELECTION.json',{'qch_commit':head(),'rules':'REVIEW_RULES.md','primary_ids':[s['state_id'] for s in selected], 'all_support_reviewed':63,'unsupported_exclusions':[],
'one_gap_adequate_predeclared':{'minimum_states':8,'minimum_qids':3},'one_gap_limitation':'Only one strict strong-H one-gap state plus one No-H one-gap state naturally acquired. No estimate of90percent reliability supported.',
'confirmation_untouched_by_need':True,'oracle_policy':'One local example only; any valid local alternative accepted. Evaluator labels never in primary request.'})
