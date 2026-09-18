import json,sqlite3,hashlib
from pathlib import Path
R=Path('/data/WSH/Search-ESR/experiments/query_initialization/selector_verbatim/runs/20260918T085353.300461Z')
Q=['71','1039','446','1035','1147']; pool=[x for x in json.loads((R/'review_pool.json').read_text()) if x['qid'] in Q]
cards=[x for x in json.loads((R/'semantic_cards.json').read_text()) if x['qid'] in Q]
D=sqlite3.connect('file:/data/WSH/Search-ESR/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
annotations=[]
def add(q,d,quotes,rationale,next_action):
 text,url=D.execute('select text,url from documents where docid=?',(d,)).fetchone();proof=[]
 for quote in quotes:
  assert quote in text,(d,quote)
  starts=[]; pos=0
  while (a:=text.find(quote,pos))>=0:
   starts.append([a,a+len(quote)]);pos=a+len(quote)
  proof.append(dict(quote=quote,source_spans=starts))
 annotations.append(dict(qid=q,docid=d,kind='confirmed_useful_source',packet_alignment='question_aligned',document_sha256=hashlib.sha256(text.encode()).hexdigest(),url=url,rationale=rationale,next_action=next_action,proof_alternatives=[proof]))
add('71','10907',[
'The Ballast Bank is a rather curious man-made island in Wexford Harbour opposite the Talbot Hotel. It was erected to provide a place for loading and unloading ballast, which was essential to stabilise ships sailing without cargo.',
'Both the Talbot Hotel and the Ballast Bank were constructed in 1905 and so it seems fitting to name one of Wexford\'s landmark bars after one of Wexford\'s most famous landmarks.'
], 'Named Irish water structure has an explicit ship-stability purpose, hotel/bar naming link and 1905 date. This is strong question-aligned candidate evidence, not independent confirmation of every historical date.', 'Read history to compare the competing 19th-century construction claim.')
add('71','15985',[
'The Ballast Bank, situated in Wexford Harbour, Ireland, is a man made structure, built in 1832.',
'Ballast is any material used for stabilisation.'
], 'Full-source opening explicitly provides the 19th-century construction date and stabilisation function of Ballast Bank. These opening facts are outside the delivered window.', 'Open toward the beginning to obtain the 1832 construction/function passages and reconcile with hotel source.')
add('446','63560',[
'Taylor Swift is named after James Taylor, one of her parents\' favorite artists.',
'She grew up on a Christmas tree farm in Reading, PA (which inspired her song "Christmas Tree Farm").'
], 'Two distinctive question relations identify the intermediate singer as Taylor Swift; this does not identify the requested author.', 'Establish the singer\'s birth year and then investigate debut-novel film adaptations in that year.')
add('446','89090',[
'Swift, born December 13, 1989, in Reading, Pennsylvania to parents Andrea (Finlay) Swift and Scott Kingsley Swift is, without doubt, one of the most famous people in the world.',
'Young Taylor spent the first 11 years of her life on a Christmas tree farm.',
'Swift was named after legendary Boston-born singer-songwriter James Taylor.'
], 'Connects the named-after and childhood-farm clues with a sourced 1989 birth year, yielding an actionable intermediate year.', 'Search or read candidate debut novels from the 1970s adapted into a film released in 1989; keep author identity open.')
add('446','43979',[
'I was surprised to find out Taylor Swift is named after you.',
'I was too! Taylor and I played a gig together about two years before she became so amazingly successful.'
], 'James Taylor interview directly acknowledges the namesake relation, grounding an intermediate singer candidate.', 'Confirm the farm clue and birth year before linking a film release year to an author.')
add('446','40395',[
'On Friday (Dec. 6), Taylor Swift released "Christmas Tree Farm," the first original Christmas song of her career. The nostalgic track clued listeners into a fact devoted Swifties have known "fir" years: that prior to moving to Nashville to pursue music, the superstar grew up on an actual Christmas tree farm in Reading, Penn.'
], 'Explicit farm upbringing and identically named song link match the question\'s distinctive intermediate clue.', 'Verify the namesake clue and birth year; do not treat this as identification of the final novelist.')
add('1035','38647',[
'Jan Koum — WhatsApp',
'Fleeing persecution in Ukraine as a teenager, Koum settled with his family in Mountain View, California, an ideal landing pad for a budding computer enthusiast.',
'Ignoring offers from venture capitalists, WhatsApp boomed in popularity and Facebook took notice, purchasing the 5-year-old company for $19B.'
], 'Provides an immigrant app entrepreneur, the destination city Mountain View, and a billion-dollar app outcome. This grounds an intermediate city candidate; birth decade, parent detail and Company A identity remain unverified.', 'Verify Koum\'s birth/parent migration details and investigate the company-city naming connection.')
add('1147','72658',[
'Kid Trunks is a Vietnamese-American rapper based in Florida .',
'Kid Trunk is Vietnam Born in Ho Chi Minh City , he grew up in a single-parent family and is the youngest of three siblings.',
'Throughout middle school and high school in Florida, he was constantly bullied because he was Asian.',
'He uploaded his first single "Talk" on YouTube in August 2017, and made his name known to people with his sharp flow and rapping skills that he couldn\'t believe was Asian.'
], 'Delivered window connects Kid Trunks with youngest-sibling status, middle-school bullying and 2017 breakthrough. Strong candidate lead; real name and birth date appear elsewhere in source and are not counted as visible.', 'Open before the window to inspect the biography header for birth date and real name, and after for the 2018 hit.')
semantic=[]
for c in cards:
 reason={'71':'The water structure and hotel-naming relationship are self-contained. Omitting stability narrows information but does not change a retained relationship; its retrieval cost is evaluated separately.',
 '1039':'Both original units retained; article identity, publication/submission interval and Wikipedia-keyword condition preserve their original relationships.',
 '446':'First unit preserves the novelist-film-year-singer chain intact. It remains long and multi-hop, but the local unit scheme cannot isolate the inner singer clue; this is not semantic mutation.',
 '1035':'Company remains an unknown placeholder. The city/immigrant/app relation is intact; where q2 starts with this company, q3 explicitly names Company A and supplies sufficient local referent. No entity identity is invented.',
 '1147':'Rapper subject, youngest-sibling relation, school bullying and 2017 attention are preserved with self-contained pronoun context. Omitted name-request/successful-song details need later research.'}[c['qid']]
 semantic.append(dict(card_id=c['card_id'],qid=c['qid'],coherent=True,context_sufficient=True,acceptable=True,issues=[],reason=reason))
positive={(a['qid'],a['docid']):a for a in annotations}
reasons={
'71':{'11502':'Ice-house construction/hotel/restaurant overlap, but refrigeration rather than stabilisation; no confirmed named-after water-structure relationship.', '20529':'Irish spa history without the required stability/hotel naming relationship.', '73125':'Irish river naming and course, without the structure/hotel naming relationship.', '75337':'Castle catalogue; no matching water-stability structure and hotel relation.', '71183':'Architecture/castles passage; no matching structure/hotel relation.', '47257':'Travel itinerary with restaurants/hotels, no requested structural relationship.'},
'1039':{'87305':'Wikipedia health-review search strategy; no distinctive six-keyword/2021 submission/researcher-background match.', '52224':'General Wikipedia epistemology text; inspected opening and targeted metadata terms, no confirmed author-background/submission/keyword relation.', '50836':'2022 Wikipedia dataset paper provides a plausible title only; source opening and ending do not establish six keywords, spring-2021 submission or stated author background.', '75887':'Comparison of encyclopedia references is topical overlap; inspected abstract does not establish the distinctive requested relationships.', '26074':'Wikipedia science paper is explicitly posted in 2017/revised2019, date-written2018 and shows five keywords; not confirmed as 2022 six-keyword target.', '43773':'Same health-review methodological text as appendix; no distinctive requested match.'},
'446':{'89123':'Kingsbury profile gives bestseller/film overlap; further source around6498-7030 describes first novel followed by1996 contract, not the requested1970s debut. No target-author confirmation.', '91945':'List of popular second novels; no concrete mentorship/debut/adaptation relationship from question.', '89176':'Celebrity books list, without the requested author/mentor/1970s debut relationship.', '71847':'Carly Simon biography and marriage to James Taylor are different relationships from being named after him.', '66009':'James Taylor biography gives career information but no new namesake/farm/birth-year bridge in delivered window.'},
'1035':{'50510':'Broad entrepreneur list; delivered windows discuss Dorsey/Ma/Musk, no city-with-parent/app bridge. Targeted full-source search for Jan Koum/Mountain View/WhatsApp found no relevant match.', '63672':'Athletes becoming entrepreneurs is a different relation from Company A partnering with an athlete; windows lack the city/concert/1992-born endorsement relation.', '43801':'Athlete investments and endorsements generally; no specific Company A relation.', '35737':'Spiegel biography describes app founding but neither migration-with-parent to named city nor 1970s birth decade.', '67397':'Athlete-owned businesses are not evidence for Company A\'s stated partnership.', '7940':'Ben Francis is an entrepreneur born1992, not the described athlete partner; unsupported relation substitution would be required.', '35703':'Kobe Bryant venture-investment story lacks target relations and explicit age41 in2020 differs from1992-born athlete.', '17519':'Generic athlete-investor collection; no matching company/city/athlete/concert bridge.', '98405':'Technology-entrepreneur list; returned Jobs/Gates/Bezos narrative and targeted WhatsApp mention only acquisition, no migration/city bridge.', '5089':'Billion-dollar startup list has app valuation overlap but no stated entrepreneur/migration/city identity connection.', '89479':'Entrepreneur profiles give generic founding roles; no matched migration/city bridge in returned passage or targeted Koum/MountainView/WhatsApp lookup.', '68581':'Teen entrepreneurs, not the 1970s-born immigrant/app/city relationship.'},
'1147':{'56314':'Bullied-rappers list covers earlier artists; window gives Eminem, not a matched2000-2010-born/youngest/2017breakthrough combination.', '53389':'General real-name list without a target-identifying relation; targeted full-source KidTrunks lookup absent.', '98951':'Young brothers gaining viral attention in2016 are plausible youth/sibling overlap, but no bullying/youngest/2017song linkage; not confirmed.', '94227':'General real-name list; no target-identifying relation, targeted KidTrunks lookup absent.', '43278':'General real-name list; no target-identifying relation, targeted KidTrunks lookup absent.', '75325':'Bully lyrics and annotation show bullying theme only; no matched age/sibling/breakthrough connection.', '99208':'YouTube placeholder supplies no substantive evidence beyond title.', '58466':'Reddit placeholder gives a Pop Smoke title only; no substantive confirming evidence.'}}
source=[]
for item in pool:
 key=(item['qid'],item['docid']);a=positive.get(key)
 scope=dict(delivered_windows=[dict(window_ref=w['window_ref'],start=w['offset'],end=w['end_char']) for w in item['windows']],outside_window_reads=[])
 if key==('71','15985'):scope['outside_window_reads']=[[0,1600]]
 if key==('1039','52224'):scope['outside_window_reads']=[[0,1600]];scope['targeted_terms']=['Keywords','Received','Submitted','2022']
 if key==('1039','50836'):scope['outside_window_reads']=[[0,1600],[28605,28713]]
 if key==('1039','75887'):scope['outside_window_reads']=[[0,1600]]
 if key==('446','89123'):scope['outside_window_reads']=[[6378,6898],[6498,7030]]
 if key==('1147','72658'):scope['outside_window_reads']=[[0,400],[2166,2690]]
 if item['qid']=='1035' and item['docid'] in ['50510','89479','98405']:scope['targeted_terms']=['Koum','Mountain View','WhatsApp']
 if item['qid']=='1147' and item['docid'] in ['53389','94227','43278','56314']:scope['targeted_terms']=['Trunks','Trunk','2000','bullied','youngest']
 status='confirmed_useful_source' if a else ('plausible_unconfirmed' if key in {('1039','50836'),('1147','98951')} else 'no_confirmed_utility')
 source.append(dict(qid=item['qid'],docid=item['docid'],status=status,review_scope=scope,reason=a['rationale'] if a else reasons[item['qid']][item['docid']]))
out=dict(method='Agent qualitative review of original questions, exact packets and all returned windows for assigned qids; source records inspected only within returned pool. No gold, no additional model judge/API. Partially unblinded: arm/session identities had been seen while auditing and preparing early diagnostics. Positive annotations are post-run and incomplete qrels; negative labels mean no confirmed utility in reviewed material.',qids=Q,semantic=semantic,annotations=annotations,source_review=source)
(R/'review_part_c.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print('semantic',len(semantic),'annotations',len(annotations),'sources',len(source))
