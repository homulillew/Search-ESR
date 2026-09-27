"""Single-reviewer Q/current-C gold definitions. No model/future/source lookup."""
from experiments.evidence_gap_gold_obligation.common import *
SOURCE=ROOT/'experiments/belief_need_budget_locality_repair/need/confirmation/INPUTS.json'
DEFS=[]
def add(sid, kind, obligation, status, support, missing, needed, required, optional=(), risk=('none',), ambiguity='low', reason=''):
 DEFS.append(dict(state_id=sid, type=kind, gold_obligation=obligation, reference_status=status,
  reference_support=[{'claim_id':k,'supports':v} for k,v in support.items()], reference_missing=missing,
  reference_evidence_needed=needed, required_support_groups=required, optional_support=list(optional),
  binding_risk=list(risk), ambiguity=ambiguity, reason=reason))
add('F07_S00','identity_discovery',
 'Identify a research paper written between 2012 and 2022 by two authors that has a table reporting an emotion at 13.53 percent.',
 'unsupported',{},'The identity and existence of a two-author paper in the stated period with the 13.53-percent emotion table.',
 'A bibliographic record linked to the paper text or table establishing authors, date, and the emotion percentage.',[],risk=('target_as_prerequisite','downstream_jump'))
add('F07_S01','relation_verification',
 'Establish whether Mehmet Diyaddin Yaşar has a research paper in the Journal of Baltic Science Education published between 2016 and 2023.',
 'unsupported',{},'Whether Yaşar authored a paper in that journal during the specified period.',
 'A journal or bibliographic record identifying Yaşar as an author and giving the journal and publication year.',[],optional=('C1',),risk=('target_as_prerequisite',),reason='C1 may identify the candidate researcher but does not establish journal authorship; optional identity anchor only.')
add('F07_S03','satisfied_control',
 'Identify the emotion reported at 13.53 percent in the 2022 paper Examination of Prospective Teachers\' Creative Comparisons for the Concept of Science Education.',
 'satisfied',{'C2':'Names and dates the paper.','C4':'Locates its emotion table.','C5':'Identifies Happiness at 13.53 percent in that paper.'},None,None,[['C5']],optional=('C2','C4'),reason='Local table lookup is satisfied; no claim that every clue of Q is satisfied.')
add('F08_S00','identity_discovery',
 'Identify a company founder whose company\'s online video games division released a game during 2000–2010 that remained one of the top-earning games of all time at least through 2019.',
 'unsupported',{},'A founder/company/game identification with the release period and commercial record established.',
 'Evidence linking a founder to the company and its online games division, a qualifying release date, and the game\'s earnings status through 2019.',[],risk=('target_as_prerequisite',))
add('F08_S01','relation_verification',
 'For Kwon Hyuk-bin, the Smilegate founder, establish whether he and his spouse made a foundational gift for a building that was part of a larger university complex.',
 'partial',{'C1':'Identifies Kwon as Smilegate founder.'},'Whether Kwon and his spouse jointly made the described foundational gift, and its building/complex connection.',
 'A gift announcement or equivalent account linking Kwon and spouse jointly to a foundational contribution for a building within a university complex.',[['C1']],risk=('target_as_prerequisite','downstream_jump'))
add('F08_S03','satisfied_control',
 'Check whether candidate Ding Lei was married without children at the time of the 2019 account.',
 'satisfied',{'C5':'Directly states married without children at the time of the 2019 article.'},None,None,[['C5']],optional=('C4',),reason='Current C identifies this candidate and verifies the local family-status clue; C3 concerns Kwon in 2025, a different person/time.')
add('F09_S00','identity_discovery',
 'Identify a musical artist whose accidental death occurred in a city 20–30 miles from the site of that country\'s deadliest aviation accident as of 2023, with the accident occurring 15 years before the artist\'s death.',
 'unsupported',{},'The artist and the linked death-city/aviation-accident identification meeting the distance and timing constraints.',
 'Linked evidence for an artist\'s accidental death location/date and the aviation accident\'s site, national deadliest status, date, and distance from that city.',[],risk=('target_as_prerequisite','downstream_jump'))
add('F09_S01','relation_verification',
 'Establish whether the partner of Sophie, who died accidentally in Athens in 2021, gave an interview saying that after her death she had become a direct reference to a song whose title is a one-word adjective.',
 'partial',{'C1':'Establishes Sophie\'s accidental death in Athens in 2021.'},'The partner/interview event and its statement connecting Sophie after death to a one-word adjective song title have not been established.',
 'An interview transcript or faithful attributed account identifying her partner and the post-death statement, with enough information to establish the referenced song/title.',[['C1']],risk=('target_as_prerequisite','downstream_jump'))
add('F09_S03','satisfied_control',
 'Identify Sophie\'s partner associated with the post-death tribute.',
 'satisfied',{'C2':'Names Sophie\'s partner as Evita Manji.','C3':'Attributes the later tribute to partner Evita Manji.'},None,None,[['C3']],optional=('C1','C2'),reason='C3 alone binds person, partner role and tribute; C2 alone omits tribute association. Do not infer that the tribute was an interview.')
add('F10_S00','identity_discovery',
 'Identify an Indian author who was promoted from associate professor to professor in 2022 at the same university where they completed both undergraduate and graduate degrees.',
 'unsupported',{},'An author and the linked 2022 promotion and same-university undergraduate/graduate education.',
 'A biographical or institutional record linking the author, promotion year/ranks and both degrees to the same university.',[],risk=('target_as_prerequisite',))
add('F10_S01','downstream_temptation',
 'Establish and identify a journal article by Alka Marwaha on a topic similar to her book The Secret World of Vipassana and Mathematics, published six years after that book, including whether such an article exists.',
 'partial',{'C1':'Establishes Marwaha\'s book, its Vipassana/mathematics topic and 2016 publication.'},'Whether an identifiable Marwaha journal article on the similar topic was published six years after the 2016 book.',
 'A journal record or article text establishing authorship, article identity, date and topic, allowing comparison with the book.',[['C1']],risk=('downstream_jump','target_as_prerequisite'),reason='Article existence/identification is the target; a title-only lookup assuming existence is too downstream. C2 is unrelated to this local obligation.')
add('F10_S02','satisfied_control',
 'Establish and identify a journal article by Alka Marwaha on a topic similar to her book The Secret World of Vipassana and Mathematics, published six years after that book, including whether such an article exists.',
 'satisfied',{'C1':'2016 book and Vipassana/mathematics topic.','C3':'Named 2022 journal article with matching author/topic; six-year interval.'},None,None,[['C1'],['C3']],reason='No need to re-prove the entire author biography for this local article obligation.')
add('F11_S00','identity_discovery',
 'Identify a book containing between 130 and 140 illustrations and descriptions of objects including the telephone and telegraph.',
 'unsupported',{},'The identity of a book with the specified illustration count and object coverage.',
 'A book record or text establishing its title, illustration count and coverage of telephone and telegraph.',[],risk=('target_as_prerequisite','downstream_jump'))
add('F11_S01','downstream_temptation',
 'Establish and identify a book containing 130–140 illustrations, descriptions of the telephone and telegraph, and a reference to the figure with initials L. E. born in the early 1700s in a central European country.',
 'partial',{'C1':'Provides Leonhard Euler as an initials/birth-period candidate, born in Basel in 1707; establishes no book relation.'},'An identifiable book with the illustration/object profile and the stated biographical reference; the candidate\'s actual mention in such a book is unverified.',
 'Bibliographic and book-content evidence establishing identity, illustration count, object coverage and the matching referenced person.',[['C1']],risk=('wrong_object_scope','downstream_jump'),ambiguity='medium',reason='C1 supports a candidate name/date/place, not a book or its citation; central-European classification is not explicitly in C and may remain to verify. Do not require Euler to be the only possible L. E.')
add('F12_S00','identity_discovery',
 'Identify a person born between 1948 and 1952 who gave an important presentation in 1990 at a prominent cultural center in their country and recorded no material between 1986 and 1994.',
 'unsupported',{},'A person satisfying the birth-period, 1990 presentation and recording-hiatus profile.',
 'Biographical/performance/discographic evidence identifying the person and supporting those dated features.',[],risk=('target_as_prerequisite','downstream_jump'))
add('F13_S00','identity_discovery',
 'Identify the case report from the 2010s describing an individual with a six-month history of gradually worsening pain in different body parts, difficulty walking and restricted shoulder movement, including the reported disorder.',
 'unsupported',{},'The report/case identity and the disorder attributed to the described symptom history.',
 'A dated case report linking the six-month course and walking/shoulder symptoms to its stated diagnosis.',[],risk=('target_as_prerequisite','downstream_jump'))
add('F13_S01','scope_binding',
 'Establish whether stiff person syndrome is the reported disorder in the specific 2010s case involving six months of worsening multi-site body pain with difficulty walking and moving the shoulders.',
 'partial',{'C1':'Generic SPS time course could be compatible, without identifying a report.','C2':'Generic SPS pain/shoulder/walking symptoms overlap the description, without establishing a specific case diagnosis.'},'A specific dated case report matching the six-month clinical history and linking that patient to SPS or another diagnosis; generic symptoms do not establish the report.',
 'The matching case report or a reliable case-specific account giving date, individual symptom history and diagnosis.',[['C2']],optional=('C1',),risk=('wrong_object_scope','target_as_prerequisite'),reason='Generic symptoms count only as partial compatibility, not positive identification or diagnosis of the described individual.')
add('F13_S06','satisfied_control',
 'Identify the disorder reported in both the case of the 10-year-old Pakistani boy with six months of worsening body pain and impaired walking/shoulder movement and the case of the sixteen-year-old male with upper-back pain/swelling two months after biopsy and earlier stiffness followed by swellings over four years.',
 'satisfied',{'C7':'First profile directly linked to FOP.','C9':'Second profile directly linked to FOP.'},None,None,[['C7'],['C9']],reason='Only common reported disorder for the two described cases; publication-year/country-history clues and general disease mechanisms are outside this local obligation.')
add('F14_S00','identity_discovery',
 'Identify a strategy video game that was the subject of a 2023 master\'s thesis at an American university on postcolonialism.',
 'unsupported',{},'The game and an identifiable 2023 American-university master\'s thesis on its postcolonialism theme.',
 'A thesis record or thesis text linking title/theme, game, university, degree and year.',[],risk=('target_as_prerequisite',))
add('F14_S01','identity_discovery',
 'Identify a downloadable content pack for Europa Universalis IV released more than three years after the base game that changed religion and technology mechanics and added mechanics for a specific playable European nation.',
 'unsupported',{},'An identifiable EU4 DLC and evidence of the release interval and religion/technology/nation mechanics profile.',
 'Release records for the game and DLC together with DLC descriptions or documentation establishing the specified mechanic changes and nation.',[],optional=('C1','C2'),risk=('target_as_prerequisite','downstream_jump'),reason='Thesis/game/advisor anchors may contextualize EU4 but establish no DLC profile; do not infer Rights of Man from another snapshot.')
add('F14_S06','satisfied_control',
 'Identify the full name of the third content designer credited for the Europa Universalis IV Rights of Man downloadable content.',
 'satisfied',{'C8':'Ordered three-person content-designer credit list.','C9':'Explicitly states third credited content designer.'},None,None,[['C8','C9']],optional=('C3',),reason='Either ordered credits or explicit third-designer statement suffices; release/game identification optional. No need to prove unrelated thesis clues.')
add('F15_S00','relation_verification',
 'Establish and identify a university-team programming world championship victory involving an Australian coder who earned IOI medals bronze, silver, gold and silver in four consecutive years.',
 'unsupported',{},'The coder\'s identity/medal sequence and a linked university-team championship victory have not been established.',
 'Competition records linking an Australian coder\'s consecutive IOI medals to membership on a winning university team in a specified world final.',[],risk=('target_as_prerequisite','downstream_jump'),reason='Discover the winning event before extracting its host/title year; no candidate name supplied from future C.')
add('F15_S01','relation_verification',
 'Establish whether Jerry Mao\'s university-team world championship victory involved two other teammates from the same country, with Jerry being the Australian coder with consecutive IOI medals bronze, silver, gold and silver.',
 'partial',{'C1':'Australian coder and consecutive IOI medal sequence.','C2':'Establishes Jerry\'s team, victory and names the two other teammates.'},'Whether the two other teammates, Mingyang Deng and Xiao Mao, were from the same country.',
 'Team profiles or comparable records establishing the national origins of both named teammates for that winning team.',[['C1'],['C2']],risk=('wrong_object_scope',),reason='Shared team membership or similar names do not establish shared country; do not demand that Jerry share their country.')
add('F15_S02','satisfied_control',
 'Identify the host university of the ICPC 2021 World Finals Dhaka won by Jerry Mao\'s MIT ZEROONE team.',
 'satisfied',{'C2':'Links the team and Jerry to the specific winning final.','C3':'Identifies the host university for that final.'},None,None,[['C3']],optional=('C2',),reason='Competition title-year 2021 and holding date in 2022 must not be conflated or treated as contradiction.')
add('F16_S00','downstream_temptation',
 'Establish and identify a first-half-twentieth-century ruler-to-ruler letter written roughly six months after its author came to power and delivered by an official nicknamed after a body part by the recipient, including whether such a letter is evidenced.',
 'unsupported',{},'An identifiable letter and the author/recipient, timing and nicknamed-delivery-official relations.',
 'A letter or archival account linking its date and author\'s accession to the recipient, delivering official and recipient-given nickname.',[],risk=('downstream_jump','target_as_prerequisite'),reason='The region cannot be extracted from a source that has not been identified.')
add('F16_S01','scope_binding',
 'Establish the date on which the King Michael of Romania letter to the United States President was written, so its relation to the author\'s accession can subsequently be tested.',
 'partial',{'C1':'Identifies a letter and separately dates its covering memorandum.','C2':'Describes handoff of the same letter, without giving its writing date.'},'The writing date of the letter itself; March 5, 1945 is the covering memorandum\'s date only.',
 'The letter\'s own dateline or an archival statement explicitly assigning a writing date to the letter itself.',[['C1']],optional=('C2',),risk=('wrong_object_scope',),reason='Accession comparison is stated as subsequent use, not a second required current fact. An unnamed handoff officer is not established as final courier.')
add('F16_S02','satisfied_control',
 'Identify the regained region mentioned in King Michael of Romania\'s letter to the United States President.',
 'satisfied',{'C1':'Identifies the letter\'s sender and recipient.','C3':'Directly gives North Transylvania as the regained region in that letter.'},None,None,[['C3']],optional=('C1','C2'),reason='No letter-date qualification in O; H\'s March 5 label must not expand the obligation or transfer the memorandum date.')

def main():
 source=read(SOURCE); cases=[]; gaps=[]
 assert len(DEFS)==27 and len({d['state_id'] for d in DEFS})==27
 jobs={j['input_id']:j for j in read(SOURCE.parent/'JOBS.json')}
 # qid mapping comes only from historical identity metadata, not later content.
 qids={'F07':'261','F08':'228','F09':'169','F10':'971','F11':'538','F12':'122','F13':'637','F14':'843','F15':'1259','F16':'922'}
 for n,d in enumerate(DEFS,1):
  sid=d['state_id']; b=source[sid]; folder,step=sid.split('_')
  snapshot=ROOT/f'experiments/belief_need_budget_locality_repair/acquisition/trajectories/{folder}/{step}.json'
  original=read(snapshot)['state']
  assert b['question']==original['question'] and b['claims']==[c['statement'] for c in original['claims']]
  assert b['hypothesis']==(original['hypothesis'] or '')
  b={**b,'hypothesis':original['hypothesis']}  # Preserve original null, not the old API projection's empty string.
  cid=f'G{n:02d}'
  cases.append({'case_id':cid,'state_id':sid,'qid':qids[folder],'type':d['type'],'belief':b,
   'claims':[{'claim_id':f'C{i}','statement':s} for i,s in enumerate(b['claims'],1)],
   'gold_obligation':d['gold_obligation'],'natural':True,'fresh':False,'belief_sha256':digest(b),
   'snapshot':rel(snapshot),'snapshot_sha256':sha(snapshot),'source':rel(SOURCE),'source_sha256':sha(SOURCE)})
  gaps.append({'case_id':cid,**d})
 write(P/'e0_reference/CASES.json',cases)
 write(P/'e0_reference/GOLD_OBLIGATIONS.json',[{'case_id':c['case_id'],'gold_obligation':c['gold_obligation']} for c in cases])
 write(P/'e0_reference/GOLD_GAPS.json',gaps)
 write(P/'e0_reference/SELECTION.json',{'rule':'Census of all F07–F16 natural snapshots present in frozen confirmation INPUTS; exclude D* artificial delta states; one manually fixed local obligation per snapshot; no post-call selection.',
  'instances':27,'unique_QCH':len({c['belief_sha256'] for c in cases}),'unique_questions':10,'satisfied_controls':sum(g['reference_status']=='satisfied' for g in gaps),
  'source_sha256':sha(SOURCE),'selected_states':[c['state_id'] for c in cases],'excluded':[s for s in source if not s.startswith('F')],
  'limitations':'Exposed development census; related snapshots clustered by question, not independent tasks. Local obligations manually scoped; not global answer correctness.'})
 write(P/'e0_reference/REPORT.md','''# E0 reference freeze\n\n27 unchanged natural QCH snapshots, 10 question clusters, 8 satisfied controls (29.63%). One local obligation per snapshot. All five requested case types are represented. D* synthetic delta states are excluded.\n\nSingle Codex reviewer inspected Q/current C/H, without gold answers, external lookup, source audit or future tool output. The same reviewer knows multiple separately presented historical snapshots and prior experiments; this is not independent or perfectly blind reference construction. Each definition is justified exclusively from its own Q/C. H contributes no required fact, target identity or support. All obligations embed their own scope because Q is absent from API payloads.\n\nClaims and H are exact strings from the original snapshot; C IDs are positional wrappers only. Source-relative archived Claims are treated as the supplied verified premise set, without claiming a new global factual audit. Eight satisfied controls establish local components, not full original-question closure.\n\nSupport groups record materially necessary facts: at least one ref in each group must be present. Optional refs may identify/locate the exact entity, event or source already in O, but may not be used as proof of its unknown relation. All other refs need case-specific semantic justification, not keyword overlap. Generic symptom compatibility supports only compatibility. Equivalent evidence is allowed; exact gold phrasing is never required.\n''')
if __name__=='__main__':main()
