"""Explicit single-reviewer judgments of final Need text, not hidden reasoning."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from transport import P,rd,save
D=P/'need/development';ids=list(rd(D/'INPUTS.json'));review={}
data={
'B0':[
('W','Combines siblings, degree date and doctor aspiration instead of one clue.'),
('P','Adds Indian nationality absent from empty QCH; dry-well relation itself is local.'),
('','Tests candidate birth interval, which Claims do not establish.'),
('','Tests the explicitly disputed historicity claim without treating the critic as proven correct.'),
('W','Conjoins birth decade, academy and profession.'),
('','Surveyor is established; chartered qualification is not.'),
('','Candidate post-football chartered qualification remains unknown.'),
('','Tests all-competition Brighton total. Reported caps do not settle that maximum; largest listed club is a reasonable inspection candidate.'),
('W','Bundles multilingualism, unique queenship and publication profile.'),
('W','Combines book page count, publisher and publication time.'),
('W','Whole-candidate fit across queen and bibliography conditions.'),
('W','Multilingualism and exclusive queenship are independent.'),
('','One authorship slot of the question-described2023 paper; no new candidate asserted.'),
('','One ordered byline for an already identified paper; second author remains unknown.'),
('W','Conjoins Beacom authorship with another author’s affiliation to locate2016 paper.'),
('W','Bundles book date, descent and organization founding/directorship conditions.'),
('','Second author of source-identified2023 paper remains unknown.'),
('W','Combines youth-academy membership and jersey number.'),
('PW','Introduces unobserved title, author, publisher and exact date as facts; asks whole book/author fit.'),
('','Husband-poet relation remains unknown even after poem claim.'),
('','Added title does not supply second author.'),
('','Added birth date does not answer chartered qualification.'),
('W','Third-author query carries an unverified first-author affiliation as an additional selection condition.'),
('','Added jersey does not answer chartered qualification.'),
('','One career transition; optional date elaborates occurrence rather than another independent requirement.'),
('','Added match statistics do not answer chartered qualification.'),
('','Added academy claim does not answer chartered qualification.'),
('','Chartered qualification remains the selected missing relation before final added Claim.')],
'B1':[
('W','Combines degree-date and doctor-aspiration clues.'),
('','Isolates dry-well-poems identity clue.'),
('','Candidate birth interval remains open.'),
('','Asks for independent attestation of disputed historical existence; does not assert it.'),
('','Isolates football-to-chartered-surveyor clue.'),
('W','Combines jersey and chartered-surveyor clues before either identifies a candidate.'),
('','One unknown candidate career transition.'),
('S','Springer Nicolas, Ryan and October2012 are already explicit in Claims.'),
('W','Combines multilingualism and uniqueness of queenship.'),
('','Candidate multilingualism is a direct unresolved attribute test.'),
('W','Bundles page count, publisher and publication date.'),
('W','Combines multilingualism and unique queenship.'),
('','One title/identity for question-described2023 paper.'),
('','Single unresolved author ordinal.'),
('W','Byline query also requires resolving2016 paper identity using author affiliation.'),
('W','Retains book date, descent and organization conditions; not a single discovery clue.'),
('','Second author remains unknown.'),
('','One academy-membership relation tested for business-linked candidate.'),
('W','Unverified page count, publisher and publication date jointly identify book.'),
('','Birth year is not established by poem-deposit Claim.'),
('','Added title does not answer second author.'),
('','Candidate birth date is grounded; chartered status remains open.'),
('W','Combines second-author and first-author-affiliation conditions.'),
('','Added jersey leaves chartered qualification unresolved.'),
('','One unresolved chartered-surveyor transition.'),
('','Match statistics do not answer chartered qualification.'),
('','Academy Claim does not answer chartered qualification.'),
('','Chartered qualification has not yet been added.')],
'B2':[
('PW','Adds Australian/Indian background, Melbourne Victory and exact2021/2023 contracts absent from QCH; bundles signing and extension.'),
('','One dry-well identity clue, explicitly attributed as reported.'),
('','Birth interval remains unknown; poem-deposit clause is supported by Kaul Claim.'),
('','Husband’s identity is the bridge needed to investigate whether he was a poet; one spouse-occupation relation.'),
('W','Birth decade, academy and chartered status are independent clues.'),
('W','Academy, jersey and career transition are three unresolved relations.'),
('','Birth decade is a local test of an existing provisional candidate.'),
('','Maximum per-club appearances and threshold comparison are the same numeric unknown; loan aggregation defines its scope.'),
('R','Richard D. McBride II has no QCH link to any candidate queen or book. The yes/no question asserts no coauthorship fact, but its usefulness is unsupported.'),
('R','Marlene Eilers Koenig is introduced without a QCH identity bridge. Unknown candidate relevance; not labelled a false coauthorship assertion.'),
('W','Book page count, publisher type and publication date remain independent.'),
('W','Combines book page count, publisher type and publication date.'),
('W','Requests both title and full byline rather than one identifying/authorship relation.'),
('','One unresolved second-author slot.'),
('W','Locates a paper by authorship and affiliation and additionally requests its third author.'),
('W','Combines book date, descendant authorship, organization founding and directorship duration.'),
('','One second-author slot for observed paper.'),
('P','Chelsea is absent from this projected input: only Pemberton Claims plus Nicolas business Claim, with empty H. Unobserved club affiliation is used as a premise in while-playing clause.'),
('W','Publisher type and exact February publication period jointly constrain an unidentified book.'),
('','Spouse identity is a bridge to the one missing spouse-occupation relation.'),
('','Added title leaves second author unresolved.'),
('','Birth date leaves chartered profession unresolved.'),
('W','Conjoins Beacom authorship with separate affiliation condition.'),
('','Jersey Claim leaves chartered qualification unresolved.'),
('W','Requests qualification, date and registering body as separate factual slots.'),
('W','Requests qualification, date and employer as separate factual slots.'),
('W','Chartered qualification and type of business are independently answerable.'),
('W','Bundles chartered qualification and business type before the career Claim arrives.')]
}
for arm,vals in data.items():
 assert len(vals)==len(ids),(arm,len(vals),len(ids))
 for sid,(code,reason) in zip(ids,vals):review[arm+'__'+sid]={'codes':list(code),'reason':reason}
oracle_reasons=[
('','One parent-talent-at-four clue.'),('W','Adds independent birth interval to supplied dry-well issue.'),('','Birth date unknown; poem qualifier supported.'),('','Asks birth date of explicitly provisional candidate.'),('','One football-to-surveyor identity clue.'),('','Pemberton birthday is not in Claims.'),('','Nicolas birthday is not yet in Claims.'),('','One career maximum under the frozen conservative coverage label.'),('','One multilingual-queen discovery clue.'),('','Candidate languages unknown.'),('','Candidate languages unknown.'),('','Candidate languages unknown.'),('','One paper identity from neutrino-method clue.'),('','Second author unknown.'),('','One coauthorship/date relation; no extra affiliation.'),('W','Adds organization founding interval to supplied directorship-duration identity issue.')]
for sid,(code,reason) in zip(ids[:16],oracle_reasons):review['ORACLE__'+sid]={'codes':list(code),'reason':reason}
save(D/'REVIEW.json',review)
# Explicit g activation means the requested answer addresses g, not merely requires
# g as a hidden prerequisite. Broad invalid answers can activate g but are separated.
acts={'B0':{'D00','D19','D12'},'B1':{'D17','D00','D19','D12'},'B2':{'D17','D00','D07','D19','D12'}}
pairs=[p for p in rd(P/'bank/COVERAGE_PAIRS.json') if p['split']=='development'];out=[]
for arm in data:
 for p in pairs:
  g=p['pair_id'];out.append({'arm':arm,'pair_id':g,'A_activated_g':g in acts[arm],'B_activated_g':False,'reason':('A explicitly requests this relation; B moves to a different relation. ' if g in acts[arm] else 'A selected another relation, so this pair supplies no activated-gap retirement evidence. ')+'B validity is scored separately, including broader or stale alternative Needs.'})
save(D/'DELTA_REVIEW.json',out)
