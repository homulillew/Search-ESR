"""Pre-call, single-reviewer control references; Gold masks already committed.

GoldO is evaluation-only here. It is never imported by the request builder.
"""
from collections import Counter
from .common import *

D='directly_addressable'; M='coherently_multi_addressable'
S='subnode_only'; N='not_addressable'
# D1 uses its frozen requirement prose; D2 uses authoritative source spans.
ADDRESS={
'G01':[(M,[2,3,8],'Publication interval, coauthorship and distinctive table value jointly identify one paper.'),(S,[1,2,5],'R2 also requires a separate JBSE publication, outside this initial discovery objective.')],
'G02':[(D,[4],'One author’s other JBSE paper and date interval are one relation target.'),(S,[2],'The same node also requires establishing the target paper’s complete two-author condition.')],
'G03':[(D,[8],'The percentage-emotion table relation supplies this local value.'),(D,[5],'Single percentage-emotion table target; paper identity is supplied by current context.')],
'G04':[(M,[1,2,3,4],'The founder/company/division/game chain is a coherent candidate discovery episode.'),(S,[1],'The node additionally requires education and university founding history, independent of the game/company chain.')],
'G05':[(M,[8,9],'Gift-funded building and its larger complex form one donation/building episode.'),(S,[2],'Childlessness through2019 is additionally bundled with the gift/building relation.')],
'G06':[(M,[6,7],'Spouse and childlessness at the stated time express the marital condition.'),(S,[2],'The node additionally asks for a foundational building gift and larger complex.')],
'G07':[(M,[4,5,6,7],'Death city, accidental death, aviation event and temporal/spatial links form the same identification chain.'),(D,[2],'The full death/aviation spatial-temporal chain matches this discovery target.')],
'G08':[(M,[8,9,10],'Interview, song-reference statement and title form comprise one interview/song episode.'),(M,[3,4],'Interview and the referent song/title-form nodes jointly carry this bounded relation inquiry; naming that song is coherent with identifying the reference.')],
'G09':[(S,[8],'Partner identification is a subrelation; the node additionally asserts an interview rather than merely a tribute.'),(S,[3],'Partner identification is embedded in an unestablished interview/song relation.')],
'G10':[(M,[1,2,3],'Nationality, promotion and same-university degrees jointly identify one author.'),(D,[1],'One node directly expresses the author/promotion/university condition.')],
'G11':[(D,[10],'The node establishes existence and identity of the later related article, not merely its title.'),(D,[5],'Later same-topic article six years after the book is the node’s relational objective.')],
'G12':[(D,[10],'The objective remains structurally addressable even when current Claims already establish it.'),(D,[5],'Satisfied-control designation does not change addressability or create STOP.')],
'G13':[(M,[2,3],'Illustration count and named objects jointly identify one book.'),(D,[2],'One book-content node matches the count and telephone/telegraph discovery target.')],
'G14':[(M,[2,3,7],'Book content and the L.E. reference are a coherent book identification episode.'),(S,[2,4],'R4 also adds two independent referenced people beyond the L.E. condition.')],
'G15':[(M,[2,5,6],'Birth interval, presentation and recording gap jointly identify one person.'),(S,[2,3,4],'Birth interval is bundled with separate official demographic history in R2.')],
'G16':[(S,[1,4,7],'Clinical first-case node is local, but report-decade node and disorder answer node bind both reports; the requested single-case dating/diagnosis is a subproblem.'),(S,[1,3,5],'First-case history is bundled with country/religious history; report dating and diagnosis nodes also cover both cases.')],
'G17':[(S,[1,4,7],'The specific first-case diagnosis/date inquiry cannot be expressed without extra second-case report/diagnosis scope.'),(S,[1,3,5],'The first-case syndrome binding is narrower than the country/history and shared-disorder groups.')],
'G18':[(D,[7],'Both clinical records are bound in current Claims; the shared scientific diagnosis is one node.'),(D,[5],'Shared scientific name for the two bound records is directly addressable.')],
'G19':[(D,[2],'The game/master’s-thesis relation, topic, year and university scope are one node.'),(D,[2],'The source-span thesis/game node has exactly this discovery scope.')],
'G20':[(M,[1,6,7],'DLC release timing and its gameplay changes describe one DLC discovery episode.'),(M,[1,4],'Timing and gameplay changes coherently identify one DLC; no unrelated advisor biography is added.')],
'G21':[(D,[8],'The third content-designer full name is directly represented.'),(D,[5],'The third content-designer full name is directly represented.')],
'G22':[(M,[2,3],'Winning Australian coder and consecutive medal pattern identify one championship victory.'),(M,[2,3],'Winning-team relation and distinctive coder history form one victory discovery chain.')],
'G23':[(D,[4],'The country equality is between the two other teammates, not between them and the Australian coder.'),(D,[4],'The same-country teammate relation is explicitly a single node.')],
'G24':[(D,[6],'Host university of the already bound winning edition is directly represented.'),(D,[6],'Host university of the already bound winning edition is directly represented.')],
'G25':[(M,[1,2,3,4],'Letter period, ruler roles, courier nickname and accession interval coherently identify one letter.'),(M,[1,2],'Letter identity/delivery and accession interval form the intended letter discovery episode.')],
'G26':[(S,[4],'Letter writing date is an input to the accession-interval relation; the interval node adds an independent accession-date requirement.'),(S,[2],'Exact letter writing date is only one operand of the accession interval; R1 additionally bundles delivery/nickname.')],
'G27':[(D,[6],'The region name in the already bound letter is directly addressable.'),(D,[4],'The region name in the already bound letter is directly addressable.')],
}
# Acceptable and blocked IDs. Remaining unresolved IDs are too broad/low-value.
# This is an existential action reference, not a demand to reproduce GoldO.
SELECT={
'G01':([1,2,3,4,5],[6]),'G02':([1,2,3,4,5],[6]),'G03':([2,3,4],[]),
'G04':([],[3,4]),'G05':([],[3,4]),'G06':([2],[3,4]),
'G07':([1,2,3],[4]),'G08':([1,2,3],[4]),'G09':([1,2,3],[4]),
'G10':([1,2,4],[3,5,6]),'G11':([1,2,4,5],[3,6]),'G12':([1,2,4],[3]),
'G13':([2,3],[1]),'G14':([2,3],[1]),'G15':([3,4],[1]),
'G16':([1,4],[2,5]),'G17':([1,4],[2,5]),'G18':([1,3,4],[]),
'G19':([1,2,3,4],[5]),'G20':([1,2,3,4],[5]),'G21':([2,3,4],[]),
'G22':([1,2,3],[4,5,6]),'G23':([1,4,6],[]),'G24':([1,4],[]),
'G25':([1,2,3],[4]),'G26':([1,2,3],[4]),'G27':([1,2],[]),
}
SEL_REASON={
'261':'Discovery may establish an unknown paper through a bounded date, author/publication, affiliation or table condition. Pure paper-name extraction waits for a concrete paper. Once Claims bind the paper, only unresolved author/affiliation/table-count conditions remain.',
'228':'Founder/company/game history AND university founding history in R1 remain independent unresolved objectives. In G04/G05 R2 likewise bundles unresolved childlessness AND a gift/building relation; neither is one sufficiently local objective. G06 establishes the marital condition, leaving the gift/building episode as the local residual of R2. R3/R4 are building schedule/affiliation attributes before a gift-funded building is bound. G04/G05 therefore have no admissible single ID; do not manufacture STOP or relax locality.',
'169':'Charity association, the linked death/aviation episode, or the partner/interview/song-reference episode can establish their unknown referents. R4 asks the name/form of that song without a grounded song-reference relation. A partner tribute alone does not ground it.',
'971':'Author employment, Canadian PhD/advisor relation, and author-book relation can be established locally. Advisor biography R3 is downstream until an advisor is bound. R5 is a legitimate article-discovery relation once Claims establish the book; R6 is pure article-title extraction and requires an article. G12 already establishes R5/R6.',
'538':'Illustrated content or the alternative cleaning-method clue can discover the book. R4 bundles three independent person-reference checks; Euler background does not reduce this to a local unresolved book relation. R1 is pure title extraction before any book is bound.',
'122':'Presentation and recording-gap predicates are legitimate person discovery targets. R2 bundles birth details with independent official population history; R1 requests a death-year attribute before any person is bound.',
'637':'Dated report discovery R1 and the second patient’s linked clinical history R4 are legitimate unknown-referent objectives. Initially R3 adds independent country/religion history to clinical history, and R2/R5 cannot compare/extract a shared diagnosis without bound case records. In G18 clinical first-case history is supported, leaving country provenance as the local residual of R3; shared diagnosis nodes are fully supported.',
'843':'Game/DLC relation, thesis/game relation, advisor profile, and linked gameplay changes each permit a bounded identification or verification episode; unknown referents are not automatically disqualifying. Pure credited-name extraction waits for a DLC. G21 already supports release timing and credited designer.',
'1259':'Contest identity/scope, Australian winner identity and the medal sequence can establish unknown contest/coder referents. Teammate equality, winning year and host are downstream before a concrete winning team/edition. Once C1/C2 bind these, teammate equality and host are legitimate distinct objectives. C3 then fully establishes host.',
'922':'Letter/delivery identity, accession interval, or letter/region-content relation can establish an unknown letter or its predicates. Pure region-name extraction requires the letter-content relationship, absent until G27. Memorandum date is not letter date.'}

def summarize(rows):
 c=Counter(r['status'] for r in rows); n=len(rows)
 return {'n':n,'counts':{s:c[s] for s in (D,M,S,N)},'direct':c[D]/n,
 'direct_plus_coherent':(c[D]+c[M])/n,'subnode_only':c[S]/n,'not_addressable':c[N]/n,
 'critical_not_addressable':sum(r['critical'] and r['status']==N for r in rows)/sum(r['critical'] for r in rows)}

def main():
 subprocess.run(['git','merge-base','--is-ancestor','4b8e9d8','HEAD'],cwd=ROOT,check=True)
 cases=bank(); historical={c['case_id']:c for c in read(HIST/'e0_reference/CASES.json')}
 rows=[]
 for sid,c in cases.items():
  for arm,(status,ids,reason) in zip(('D1','D2'),ADDRESS[sid]):
   rids=[f'R{i}' for i in ids];assert set(rids)<={n['requirement_id'] for n in skeletons(arm)[str(c['qid'])]['requirements']}
   rows.append(dict(case_id=sid,state_id=c['state_id'],qid=c['qid'],type=c['type'],skeleton_arm=arm,
    gold_obligation=historical[sid]['gold_obligation'],status=status,requirement_ids=rids,reason=reason,critical=True))
 write(P/'e0_addressability/ADDRESSABILITY.json',rows)
 metrics={a:{'overall':summarize([r for r in rows if r['skeleton_arm']==a]),
  'by_type':{t:summarize([r for r in rows if r['skeleton_arm']==a and r['type']==t]) for t in sorted({c['type'] for c in cases.values()})},
  'by_qid':{q:summarize([r for r in rows if r['skeleton_arm']==a and str(r['qid'])==q]) for q in sorted({str(c['qid']) for c in cases.values()})}}
  for a in ('D1','D2')}
 metrics['D2_representation_warning']=metrics['D2']['overall']['direct_plus_coherent']<.8 or metrics['D2']['overall']['critical_not_addressable']>.1
 write(P/'e0_addressability/METRICS.json',metrics)
 text='# E0 Control Addressability\n\nSingle-reviewer offline judgments; no provider calls. GoldO is evaluation-only.\n\n'
 text+='| Skeleton | Direct | Direct + coherent | Subnode-only | Not addressable |\n|---|---:|---:|---:|---:|\n'
 for a in ('D1','D2'):
  m=metrics[a]['overall'];text+=f"| {a} | {m['direct']:.1%} | {m['direct_plus_coherent']:.1%} | {m['subnode_only']:.1%} | {m['not_addressable']:.1%} |\n"
 text+='''
D2 remains primary. Its direct + coherent rate is below80%; this warns that
the representation is too coarse for some narrower historical targets. E1 still
proceeds under the task's rule. Subnode-only does not mean that the whole node
can never be a useful discovery episode. Conversely, matching an old GoldO does
not make a currently fully supported target a valid next action.

All27 historical material LocalO targets are marked critical before calls;
critical-not-addressable denominator is27 per skeleton. No selective critical
subset. Up to four tightly connected nodes can constitute one coherent episode;
unrelated extra predicates trigger subnode-only. An exact date used as an operand
of an accession interval is a subnode, not an absent concept. D1 diagnostics use
frozen requirement prose and its source provenance; D2 uses source spans. This
comparison does not pretend D1 is a pure extractive representation.

Type/qid strata and all54 reasons are in METRICS.json and ADDRESSABILITY.json.
Oracle construction committed81caa52 precedes reading GoldO; Gold masks committed
4b8e9d8 also precede GoldO. Neither is changed by this audit.
'''
 write(P/'e0_addressability/REPORT.md',text)
 gold={r['case_id']:r for r in read(P/'e1_alignment/GOLD_MASKS.json') if r['skeleton_arm']=='A1'}
 refs=[]
 for sid,c in cases.items():
  req=gold[sid]['requirements'];a,b=SELECT[sid];a=[f'R{i}' for i in a];b=[f'R{i}' for i in b]
  full=[i for i,v in req.items() if v['status']=='fully_supported']
  other=[i for i in req if i not in a+b+full]
  assert len(set(a+b+full+other))==len(req)==len(a+b+full+other)
  assert not set(a+b)&set(full)
  refs.append(dict(case_id=sid,state_id=c['state_id'],qid=c['qid'],type=c['type'],acceptable_active_ids=a,
    invalid_supported_ids=full,blocked_or_downstream_ids=b,other_invalid_ids=other,stop_allowed=len(full)==len(req),
    no_admissible_single_id=not a and len(full)<len(req),reason=SEL_REASON[str(c['qid'])]))
 write(P/'e2_selection/SELECTION_REFERENCE.json',refs)
 write(P/'e2_selection/REFERENCE_NOTES.md','''# Selection reference

Frozen before E1; uses Q, frozen D2, current Claims and Gold Mask. Historical
GoldO is not a unique next-action gold. Every node is classified, and any member
of acceptable_active_ids succeeds. These are evaluation labels only; they never
enter either model input. Unknown discovery referents are allowed. Pure
downstream attributes wait for an evidenced relational target. Independent
objectives still bundled after subtracting current support are too broad.

G04/G05 have no admissible single ID under this rule; all nodes are too broad
or downstream, yet unresolved. These cells stay in the27-state denominator.
STOP is still wrong. Structural selection ceiling is25/27 (92.59%), before
model errors. This explicit reference limitation cannot be solved by better
alignment. No hand-split node or oracle substitution is permitted.

No natural positive STOP controls in this bank. Missed STOP is not evaluated.
Whole-node locality is a semantic judgment, not a word-count rule. A coherent
unknown candidate discovery episode may include several identifying conditions;
E0 can nevertheless mark that node subnode-only for a narrower historical LocalO.
For sensitivity only, relaxed-locality accepts G04/G05 R2 and strict-locality
excludes multi-clue discovery IDs specified in analysis/SENSITIVITY.json. Neither
changes primary references or gates.
''')

if __name__=='__main__':main()
