"""Explicit pre-call single-reviewer semantic alignment judgments.

Reads only whitelisted states and frozen skeletons; never loads historical GoldO.
Unlisted nodes have no substantive support, with the per-state reason retained.
"""
from .common import *
F='fully_supported';PSTATUS='partially_supported';U='unsupported'
def f(groups,reason,contributors=None,context=(),ambiguity='low'):
 groups=[[f'C{i}' for i in g] for g in groups]
 return dict(status=F,acceptable_full_support_groups=groups,acceptable_partial_support_groups=[],contributing_claims=[f'C{i}' for i in contributors] if contributors else sorted({c for g in groups for c in g}),reason=reason,reference_binding_context=[f'C{i}' for i in context],ambiguity=ambiguity)
def p(claims,reason,groups=None,context=(),ambiguity='low'):
 return dict(status=PSTATUS,acceptable_full_support_groups=[],acceptable_partial_support_groups=[[f'C{i}' for i in g] for g in (groups or [[c] for c in claims])],contributing_claims=[f'C{i}' for i in claims],reason=reason,reference_binding_context=[f'C{i}' for i in context],ambiguity=ambiguity)
NOTES={
'G01':'No Claims. Requirements and Q are not evidence.',
'G02':'C1 is an undated Harran professor profile. No Claim binds this person to authorship of a candidate target paper; affiliation alone cannot instantiate the target-writer role.',
'G03':'C2 identifies a concrete coauthored candidate paper; later Claims explicitly concern that paper. Node-local evidence can cover a candidate property without establishing every other identifying clue. No other-JBSE relation or2023-dated affiliation. Five data tables does not establish six total tables.',
'G04':'No Claims.',
'G05':'Founder/company and education relations establish a candidate person; no gift-funded building or marital condition is established. Alma mater cannot supply building affiliation.',
'G06':'Two named founder candidates coexist. Never combine Kwon properties with Ding properties into a full proof. Ding marriage/childlessness as of2019 is supported; Kwon2025 children do not prove or disprove2019 childlessness. No building/gift evidence.',
'G07':'No Claims.',
'G08':'C1 identifies musical-artist death, city and accidentality. Charity, aviation crash, interview and song are absent.',
'G09':'Partner relationship is substantive support for part of the interview requirement. Online tribute is not established as an interview, nor does its wording establish a song-reference relation or title.',
'G10':'No Claims.',
'G11':'Concrete author-book and Canadian-PhD relations support local subsets. No Iranian advisor or later journal article. Book title cannot answer article-title requirement.',
'G12':'C1 and C3 jointly identify same-author related2016 book and2022 article, six calendar years apart. The author/advisor/degree/promotion requirements remain incompletely established.',
'G13':'No Claims.',
'G14':'Euler biography lacks any book-reference relationship. Initials/birth compatibility and candidate mention do not establish a substantive book-content relation.',
'G15':'No Claims.',
'G16':'No Claims.',
'G17':'General stiff-person-syndrome symptoms are background, not reports of the two described patients. No case-specific predicate is supported.',
'G18':'C7 and C9 explicitly describe different clinical case records matching the first and second histories. Treat these as two case records, without inventing publication years or report-country facts. Generic disease facts, anonymous mutation confirmation, and unlinked biopsy case cannot fill missing case-specific conditions.',
'G19':'No Claims.',
'G20':'Thesis and advisor relationships are explicit, but no DLC is identified. University US location and advisor California degrees/monograph are absent from Claims.',
'G21':'Named DLC/game can be locally bound using direct relations and release dates. Both conflicting August2013 base dates imply more than three years to October2016. Do not infer university country, advisor credentials or European/playable status from outside knowledge.',
'G22':'No Claims.',
'G23':'C1 supplies Australian coder and medal sequence; C2 supplies winning team and named edition. Teammate nationality and host university absent. Title-edition year is2021, not automatically actual2022 event date.',
'G24':'C3 adds host of the already linked winning edition. Teammate nationality and annual/global-university contest conditions remain incompletely supported.',
'G25':'No Claims.',
'G26':'Claims identify a letter/transmission chain but give memorandum date, not letter writing date or ruler accession date. Do not move March5,1945 onto the enclosed letter. No nickname or regained-region content.',
'G27':'C3 directly supplies the identified letter’s author-country regained-region statement and region name. It does not repair missing letter date, accession interval or courier nickname.'}
J={}
def put(g,a,nodes):J[(g,a)]={f'R{k}':v for k,v in nodes.items()}

put('G03','A0',{
1:f([[2]],'C2 provides bibliographic2022 date of the candidate paper, within required interval.'),
2:f([[2]],'C2 names the two coauthors as the article author list; no indication the list is partial.',ambiguity='medium'),
4:p([1,2],'C1 establishes Harran academic affiliation; C2 binds the professor to authorship of the same paper. As-of2023 is not stated.',groups=[[1]],context=[2]),
5:p([4],'Paper-specific organized data tables are supported; five data tables does not prove exactly six total tables.',ambiguity='medium'),
6:f([[5]],'C5 directly reports a table emotion at13.53 percent in the same paper.',context=[2,4]),
7:f([[2]],'C2 explicitly names the candidate paper; other identifying constraints are scored in their own nodes.')})
put('G03','A1',{
1:J['G03','A0']['R1'],
2:p([2],'Two-author condition is supported but another JBSE paper by one author is absent.',ambiguity='medium'),
3:J['G03','A0']['R4'],4:J['G03','A0']['R5'],5:J['G03','A0']['R6'],6:J['G03','A0']['R7']})
put('G05','A0',{
1:p([1],'Concrete founder-company-game relation; no division release year or top-earning condition.'),
2:p([2],'Degree establishes graduation; university founding interval is absent.',context=[1])})
put('G05','A1',{1:p([1,2],'Founder/company/game and graduation are separate supported parts of the coarse node; remaining release/earning/founding conditions absent.')})
put('G06','A0',{
1:p([1,4],'Either founder/company-games candidate supports a substantive subset; no cross-candidate combination proves full node.'),
2:p([2,5],'Each candidate has a degree from a named university, but neither university founding interval is supported.',context=[1,4]),
3:f([[5]],'C5 explicitly reports Ding married without children at the2019 article time.',context=[4])})
put('G06','A1',{
1:p([1,2,4,5],'Two separate candidate founder/education branches support subsets; no one candidate satisfies every coarse-node condition.'),
2:p([5],'Ding’s2019 childless marriage is supported, but no foundational gift, building or larger complex is established.',context=[4])})
for g in ('G08','G09'):
 put(g,'A0',{
 2:p([1],'Artist death city is explicit; aviation-site distance, identity and deadliest ranking are not.'),
 3:p([1],'Accidental death event/date is explicit; the15-year aviation-accident relation is unestablished.')})
 put(g,'A1',{2:p([1],'Artist death/city/accidentality are supported, but aviation-site distance, ranking and15-year relationship are absent.')})
partner=p([2,3],'Artist-partner relation and partner tribute are substantive subsets; no interview genre or reference-to-song relation is established.',context=[1],ambiguity='medium')
J['G09','A0']['R4']=partner;J['G09','A1']['R3']=partner
for g in ('G11','G12'):
 values={
 1:p([1],'Author and associate-professor role are explicit; Indian nationality,2022 promotion and same degree university are not fully established.'),
 2:p([2],'Canadian PhD pursuit is explicit; Iranian advisor relation is absent.',context=[1]),
 4:p([1],'Same author’s mathematics/Vipassana book is explicit; ancient liberation characterization and20-year PhD-completion interval are not established.')}
 for a in ('A0','A1'):put(g,a,values.copy())
for a in ('A0','A1'):
 J['G12',a]['R5']=f([[1,3]],'Same author has2016 mathematics/Vipassana book and2022 related-topic journal article: six calendar years apart.',ambiguity='medium')
 J['G12',a]['R6']=f([[3]],'C3 states the title of the now-bound later article; C1 provides book context for reference resolution.',context=[1])

put('G18','A0',{
1:p([7,9],'Two described case records are present; different report years and2010s dates are absent.',ambiguity='medium'),
2:f([[7,9]],'Both separately described clinical case records explicitly diagnose FOP.',ambiguity='medium'),
4:f([[7]],'Six-month progressive multi-site pain and walking/shoulder restrictions directly match.'),
5:f([[9]],'Upper-back pain/swelling at biopsy site with biopsy two months before directly match.'),
6:p([9],'Early stiffness and later swellings are supported; over the next4 years is not onset exactly four years later.',ambiguity='medium'),
7:f([[7,9]],'Scientific name FOP is explicitly shared by the two matched clinical records.',ambiguity='medium')})
put('G18','A1',{
1:J['G18','A0']['R1'],2:J['G18','A0']['R2'],
3:p([7],'First clinical history is supported; patient nationality does not establish report country or its historical religious-size condition.'),
4:p([9],'Biopsy/upper-body/two-month episode and early stiffness are supported, but exact four-year-later swelling onset is not.',ambiguity='medium'),
5:J['G18','A0']['R7']})
for g in ('G20','G21'):
 values={
 2:p([1],'Master’s thesis, game, year and colonialism-related topic are stated; American-university condition is not in Claims.'),
 3:p([2],'Thesis-advisor relation is explicit; two California degrees and2020 monograph absent.',context=[1])}
 for a in ('A0','A1'):put(g,a,values.copy())
for a in ('A0','A1'):
 J['G21',a]['R1']=f([[3,5]],'DLC/game relationship, strategy-game type and release-date difference greater than3 years are explicit; both base-game dates satisfy interval.')
 J['G21',a]['R4']=p([4,6,7],'Technology/religious-system and Ottoman mechanics are supported; European/playable-nation condition is not explicitly established.',context=[3,5],ambiguity='medium')
 J['G21',a]['R5']=f([[8],[9]],'Ordered credits or direct third-designer statement independently give full name for the bound DLC.',context=[3,5])
for g in ('G23','G24'):
 values={
 1:p([2],'A university-team world final and championship event are present; annual recurrence and global participation are not established by Claims.',ambiguity='medium'),
 2:f([[1,2]],'C1 establishes Australian coder, C2 establishes that coder on champion team.'),
 3:f([[1]],'Four consecutive years and bronze/silver/gold/silver sequence explicit.'),
 5:f([[2]],'C2 explicitly identifies the winning title edition as ICPC2021 World Finals, separately noting actual2022 event date.',context=[1])}
 if g=='G24':values[6]=f([[3]],'C3 explicitly names host university of the bound winning edition; do not substitute winning team university.',context=[1,2])
 for a in ('A0','A1'):put(g,a,values.copy())
for g in ('G26','G27'):
 put(g,'A0',{
 1:p([1,2],'Letter author/recipient/transmission are supported; memorandum date does not establish letter writing period.',ambiguity='medium'),
 2:p([1,2],'Official transmission/handoff relationship is supported, but recipient-given body-part nickname is absent.',ambiguity='medium')})
 put(g,'A1',{1:p([1,2],'Letter author/recipient and official transmission are supported; letter writing interval and courier nickname remain absent.',ambiguity='medium')})
for a,content,target in (('A0',4,5),('A1',3,4)):
 J['G27',a][f'R{content}']=f([[3]],'C3 explicitly attributes regained North Transylvania to author’s country in the identified letter.',context=[1,2])
 J['G27',a][f'R{target}']=f([[3]],'C3 directly supplies the region name in the bound letter.',context=[1,2])

def main():
 rows=[]
 for sid,state in bank().items():
  q=str(state['qid']);ids={c['claim_id'] for c in state['claims']}
  for arm in ('A0','A1'):
   labels={}
   for node in runtime_nodes(q,arm):
    rid=node['requirement_id']
    labels[rid]=J.get((sid,arm),{}).get(rid,dict(status=U,acceptable_full_support_groups=[],acceptable_partial_support_groups=[],contributing_claims=[],reason=NOTES[sid]+' No Claim establishes a substantive part of this node with the required role/relationship binding.',reference_binding_context=[],ambiguity='low'))
    v=labels[rid];assert set(v['contributing_claims'])<=ids and set(v['reference_binding_context'])<=ids
    for group in v['acceptable_full_support_groups']+v['acceptable_partial_support_groups']:assert group and set(group)<=set(v['contributing_claims'])
   rows.append({'case_id':sid,'state_id':state['state_id'],'qid':q,'skeleton_arm':arm,'claims_sha256':state['claims_sha256'],'skeleton_sha256':digest(runtime_nodes(q,arm)),'state_reason':NOTES[sid],'requirements':labels})
 write(P/'e1_alignment/GOLD_MASKS.json',rows)
 write(P/'e1_alignment/GOLD_CONSTRUCTION.md','''# Alignment reference construction

Single-Codex-reviewer judgments from Q + frozen Skeleton + current whitelisted
Claims only, recorded before any new provider call. Historical GoldO has not
been opened in this construction. All27 states × both skeletons are included.

Source spans are authoritative. Labels add no facts. Only Claims have evidential
authority. Local direct relations can ground a candidate referent without all
other question clues being verified. Candidate biography without a link to the
required relational role cannot establish support (e.g. Euler without book link,
Harran professor without target-paper authorship, syndrome background without
case reports). Full on one node never certifies the candidate satisfies all Q.

Reference binding uses the complete current Claims, recorded separately as
reference_binding_context. supported_by need not repeat every antecedent fact
from other nodes once a referent is grounded, but must prove every material
condition actually expressed by this node. This is contextual sufficiency, not
standalone proof stripped of all other Claims. Several alternative full proof
groups are accepted; extra claims count toward support precision only when they
contribute. Partial groups identify substantive evidence, avoiding credit for a
mere binding name without any supported predicate.

No cross-candidate conjunction can prove a full node. Coexisting alternative
candidates may each supply a valid partial proof. Pointwise masks are not a
global same-candidate closure certificate; no complete natural STOP control is
manufactured. Candidate consistency across all-full nodes remains a future
closure-audit issue, not a new runtime Binding IR in this task.

Conventions: listed coauthors treated as complete when Claim is unqualified;
paper bibliographic year operationalizes question written/publication interval;
explicit article/book year difference licenses six calendar years. Normal lexical
entailment and arithmetic are allowed; no geographic/professional/date knowledge
is imported from a name. Two independently described clinical case records can
be compared without inventing their report dates. A four-year course of recurrent
swellings does not establish that swelling began exactly four years after stiffness.
These ambiguity-sensitive conventions are frozen and receive descriptive
sensitivity reporting, never post-result relabeling.
''')
if __name__=='__main__':main()
