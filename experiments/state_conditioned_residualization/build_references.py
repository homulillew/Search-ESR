"""Single-reviewer Q/parent/current-Claims residual references, before new calls."""
from .common import *
def cls(id,target,units):return {'class_id':id,'semantic_target':target,'source_units':units}
def main():
 states=read(P/'e0_reference/STATES.json');parents={p['case_id']:p for p in read(P/'e0_reference/PARENT_REQUIREMENTS.json')}
 oldgold={g['case_id']:g for g in read(OLD/'e1_alignment/GOLD_MASKS.json') if g['skeleton_arm']=='A1'}
 paper=[cls('paper_authorship','Establish the target paper two-author authorship relation; unknown paper/authors may be discovered as this relation.',['Q4']),cls('jbse_publication','Establish whether a target-paper author (or explicitly provisional named candidate) has another JBSE paper in2016–2023. Do not assert an unverified target-writer binding.',['Q4'])]
 marriage=cls('marital_childlessness','Establish the person/spouse marriage and childlessness through2019, without assuming it or also demanding a building gift.',['Q2'])
 gift=cls('gift_building','Establish whether the person and spouse made a foundational gift for a building in a larger complex; identify/bind that gift/building episode, not an assumed building affiliation.',['Q2'])
 interview=cls('partner_interview_song','Establish the partner interview and attributed artist/song-reference relationship as one source episode, without assuming an existing interview or final song title.',['Q5'])
 partner=cls('partner_identity','Identify/establish the artist partner at the relevant death-time as a binding facet; do not assert an unknown partner name.',['Q5'])
 clinical=cls('first_case_clinical','Identify/establish the specific first case report with half-year worsening pain and walking/shoulder impairment; no generic syndrome fact stands in for that case.',['Q4'])
 country=cls('report_country_history','Establish the first report country and whether it meets the required country-at-establishment/religion-size condition; this country/history binding is a coherent linked objective. Patient nationality is not report country.',['Q3'])
 refs={
 'G01':paper,'G02':paper,'G04':[marriage,gift],'G05':[marriage,gift],'G06':[gift],
 'G07':[cls('death_aviation_relation','Identify/verify the artist death and deadliest-aviation-event relation, preserving the20–30mile and15year relational constraints. These jointly define one event linkage; removing the linkage is over-decomposition.',['Q3','Q4'])],
 'G08':[interview,partner],
 'G09':[interview,cls('interview_genre','Establish whether the attributed partner statement was made in an interview rather than merely the observed online tribute; do not re-establish who the partner is.',['Q5']),cls('tribute_song_link','Establish whether the already attributed partner tribute refers to one of the artist songs; do not assume a song title or re-verify the partner/quote already given.',['Q5'])],
 'G10':[cls('academic_career','Identify/establish the author promotion at the same undergraduate/graduate university in2022 as a coherent career profile. Do not extract a tiny unrelated attribute or fabricate candidate.',['Q1'])],
 'G11':[cls('later_article_relation','Establish the author later same-topic journal article six years after the book, including existence/identity. Book is a contextual anchor, not proof the article exists.',['Q3'])],
 'G13':[cls('book_contents','Identify/establish the book with130–140illustrations and telephone/telegraph descriptions as one document-content objective, retaining its discriminating constraints.',['Q1'])],
 'G14':[cls('book_engineer_reference','Establish/discover the book-reference relation to the early1800s-born mechanical engineer, without bundling the other two referenced people.',['Q3']),cls('book_scientist_reference','Establish/discover the book-reference relation to a scientist with a poet father, without treating a scientist identity as proof of book content.',['Q3']),cls('book_LE_reference','Establish/discover the book-reference relation to the L.E. figure; Euler may be tested as a candidate where supplied, never treated as an established book reference.',['Q3'])],
 'G15':[cls('person_birth','Establish/discover the person born1948–1952 and their birthplace, without independently requiring the census change calculation.',['Q1']),cls('place_population','Establish/discover a place with5.88% population growth2010–2020 according to official country data, without asserting a target person was born there.',['Q1'])],
 'G16':[clinical,country],'G17':[clinical,country],'G18':[country],
 'G20':[cls('DLC_release_relation','Establish/identify a DLC released more than3years after its base game, preserving which release belongs to which object; game identity supplied inClaims can anchor discovery but does not establish a DLC.',['Q1'])],
 'G23':[cls('teammate_country','Establish whether the two other teammates share a country. Retain the two-person comparison; their supplied names alone are not nationality.',['Q4'])],
 'G26':[cls('letter_writing_date','Establish the writing date of the actual letter, not its covering memorandum or transmission.',['Q2']),cls('author_accession_date','Establish when the letter author came to power, retaining uncertainty about accession relevant to this letter; no outside accession date.',['Q2']),cls('letter_accession_interval','Establish the letter-writing/author-accession interval as one coherent comparison using correctly attached dates; do not use March5,1945 as the letter date.',['Q2'])]
 }
 forbidden={
 'G06':['Re-establish Ding2019 marriage/childlessness already inC5. Mentioning it as grounding context is allowed, requiring it again is not.'],
 'G09':['Re-establish Sophie partner identity givenC2/C3.','Re-establish the already recorded online tribute wording. It may identify what unverified interview/song relation to test.'],
 'G18':['Re-establish the first patient clinical symptom/history already givenC7. Its description may identify the report without becoming another requested verification.']}
 downstream={
 'G01':['Extract an assumed paper title without discovering/verifying an authorship/publication relation.'],
 'G02':['Presume Mehmet is an established author of the target paper.'],
 'G04':['Extract university affiliation of an assumed gifted building.'],'G05':['Extract university affiliation of an assumed gift/building.'],'G06':['Extract affiliation/name of a building before its gift relation is established.'],
 'G08':['Ask for final song title assuming the partner interview/song relation.'],'G09':['Extract final song title based solely on tribute wording.'],
 'G11':['Extract title/date of an assumed later article without establishing existence/author relation.'],
 'G14':['Extract a book title assuming Euler biography establishes the book-reference relation.'],
 'G15':['Ask year of death outside this parent or assume an unbound person-place relation.'],
 'G16':['Use a diagnosis as established for the specific case.'],'G17':['Promote generic SPS background to diagnosis of the target case.'],
 'G18':['Treat Pakistani nationality as proof of report country, or import a religion/history fact.'],
 'G20':['Extract designer identity for an unestablished DLC.'],'G23':['Treat known teammate names as established same-country evidence.'],
 'G26':['Shift memorandum date onto the enclosed letter; insert accession date from outside knowledge.']}
 out=[];support=[]
 for s in states:
  cid=s['case_id'];parent=parents[cid];rid=s['parent_requirement_id'];g=oldgold[cid]['requirements'][rid]
  ids=g['contributing_claims'];claims={c['claim_id']:c for c in s['claims']}
  prior=read(OLD/f'e1_alignment/calls/A1__{cid}__R1.result.json');prior=next(n for n in prior['output']['requirements'] if n['requirement_id']==rid)
  support.append({'case_id':cid,'parent_requirement_id':rid,'gold_status':g['status'],'support_stratum':s['support_stratum'],
     'gold_contributing_claim_ids':ids,'gold_contributing_claims':[claims[i] for i in ids],
     'binding_context_ids_not_in_oracle_packet':g['reference_binding_context'],'gold_reason':g['reason'],
     'model_packet':prior,'model_packet_claims':[claims[i] for i in prior['supported_by']],
     'model_source':rel(OLD/f'e1_alignment/calls/A1__{cid}__R1.result.json'),
     'model_source_sha256':sha(OLD/f'e1_alignment/calls/A1__{cid}__R1.result.json')})
  out.append({'case_id':cid,'qid':s['qid'],'parent_requirement_id':rid,'bank_group':s['bank_group'],
    'support_stratum':s['support_stratum'],'acceptable_residual_classes':refs[cid],
    'forbidden_supported_targets':forbidden.get(cid,[]),'forbidden_downstream_targets':downstream.get(cid,[]),
    'expected_mode':'residual' if s['support_stratum']=='P' else 'probe',
    'over_decomposition_control':s['bank_group']=='control',
    'reference_rule':'Semantic class, not unique wording. Named input candidates may be tested conditionally; no target-role promotion. Supported descriptions may be identifiers without becoming research demands.',
    'parent_sha256':digest(parent['parent']),'claims_sha256':digest(s['claims'])})
 write(P/'e0_reference/RESIDUAL_REFERENCE.json',out);write(P/'e0_reference/SUPPORT_REFERENCE.json',support)
 pairs=[{'from':'G05','to':'G06','parent_requirement_id':'R2','removed_classes':['marital_childlessness'],'retained_classes':['gift_building'],'reason':'C5 establishes Ding marital condition; gift remains.'},
        {'from':'G08','to':'G09','parent_requirement_id':'R3','removed_classes':['partner_identity'],'retained_classes':['partner_interview_song'],'reason':'C2/C3 establish partner/tribute, interview/song relation remains.'},
        {'from':'G17','to':'G18','parent_requirement_id':'R3','removed_classes':['first_case_clinical'],'retained_classes':['report_country_history'],'reason':'C7 establishes specific clinical history; report-country/history still unresolved.'}]
 write(P/'analysis/STATE_DISCRIMINATION_REFERENCE.json',pairs)
 write(P/'e0_reference/REFERENCE_CONSTRUCTION.md','''# Prefix-only reference construction

One familiar Codex reviewer; Q, fixed parent and currentClaims only for semantic residual labels. Prior source-bound Gold parent status/contributing IDs inherited exactly for R1 and support strata. R2 always oldA1replicate1, no correction. No new output existed. Historical audit supplied parent mapping, not a unique Gold sentence. Future/source accessibility is deferred until these references are committed and P gate permits E2.

19states:11primary+8controls;16Z+3P. Gold supporting packet is empty forZ even when fullClaims contain useful candidate anchors (e.g.known book, teammate names, transmission record); this deliberately measures support-only compression, not complete contextual sufficiency. R2 differs substantively from R1 at G14: it promotes Euler biography to partial book-reference support. No routing repair.

Task trajectory priority overrides G04 old mappedR1 and G18 old mappedR5. All three q228 parentsR2 and all three q637 parentsR3. Control parents may have linked constraints; over-decomposition requires cutting a coherent episode into a fragment that no longer performs its intended relation/discovery test, not merely using a shorter sentence. G08 permits partner binding as a useful exploratory facet; this specific allowance is frozen, not inferred from later outputs.

P-state source contribution: G06C5; G09C2/C3; G18C7. R1 excludes prior reference_binding_context rather than secretly adding extraClaims. R2 retains actual status and supported_by, including errors. Gold support denominator is always original current state, not model belief.
''')
 write(P/'e0_reference/ACCESSIBILITY_REFERENCE.json',{'status':'DEFERRED_UNTIL_P_GATE','model_calls':0,
  'reason':'Future Claims/source provenance not opened for new accessibility labels before E1 reference freeze. Evaluation-only E2 audit will precede any E2 model call.'})
 paths=[P/'e0_reference/RESIDUAL_REFERENCE.json',P/'e0_reference/SUPPORT_REFERENCE.json',P/'analysis/STATE_DISCRIMINATION_REFERENCE.json',P/'e0_reference/REFERENCE_CONSTRUCTION.md',P/'build_references.py']
 write(P/'REFERENCE_FREEZE.json',{'head':git('rev-parse','HEAD'),'files':{rel(p):sha(p) for p in paths},'new_calls':0})
if __name__=='__main__':main()
