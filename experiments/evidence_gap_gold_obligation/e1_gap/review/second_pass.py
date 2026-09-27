"""Explicit post-label pair judgments and H-exclusive-content review; no model calls."""
from experiments.evidence_gap_gold_obligation.common import *
from experiments.evidence_gap_gold_obligation.run import load_rows

def main():
 assert git('rev-parse','HEAD').startswith('af43b4f')
 rows=load_rows();lookup={(r['case_id'],r['arm'],r['replicate']):r for r in rows};reverse={v:k for k,v in read(P/'e1_gap/review/KEY.json').items()}
 # All constituent outputs were read in the first pass, then explicitly compared after unmask.
 pairs=[];hrows=[]
 why={
 'G01':'Both identify the same unknown two-author paper/date/table profile.',
 'G02':'Both leave journal authorship/date unestablished, using the professor profile only as an anchor.',
 'G03':'Both fields null; supporting table fact present. Ref-list granularity does not change gap.',
 'G04':'Both require linked founder/company/division/game/release/earnings evidence.',
 'G05':'Both leave spouse/joint foundational donation/building-complex relation unresolved.',
 'G06':'Both fields null for dated Ding family status.',
 'G07':'Same artist/accident identity, distance and time profile.',
 'G08':'G0 second response swaps Sophie with partner in evidence_needed; G1 pair preserves Sophie as subject and the interview relation.',
 'G09':'Both fields null for partner/tribute identification.',
 'G10':'Both require author identity and promotion/degree same-university relation.',
 'G11':'Both require article existence/identity/topic and six-year calendar interval; approximate date phrasing does not change intended calendar relation.',
 'G12':'Both fields null for known book/article relationship.',
 'G13':'Both require unknown book identity, count and telephone/telegraph coverage.',
 'G14':'G0 first keeps L. E. unresolved and geography open, second fixes the requested reference to Euler; G1 pair preserves unestablished book/referent and candidate-only status.',
 'G15':'Both require person identity, birth period, presentation and no-recording interval.',
 'G16':'Both require a dated matching clinical case/report and reported diagnosis.',
 'G17':'Both separate generic SPS features from the specific case diagnosis.',
 'G18':'Both fields null using both case-specific diagnoses.',
 'G19':'Both require game/thesis identity and dated institutional/theme relationship.',
 'G20':'Both require DLC identity and release/mechanics profile; thesis provides no qualifying support.',
 'G21':'Both fields null on the directly observed ordered credits.',
 'G22':'Both require linked winning event, coder and medal sequence.',
 'G23':'First preserves other-teammate equality but adds Jerry/Australia; second exclusively tests equality with Jerry. Compatible in the added unsupported equality, but substantively different scope; neither is correct.',
 'G24':'Both fields null on known final/host.',
 'G25':'Both require letter existence/identity and defining delivery/time relations.',
 'G26':'Both explicitly distinguish letter date from covering memorandum date.',
 'G27':'Both fields null for region; differences in optional anchor refs do not change deficit.'}
 hwhy={
 'G02':'H suggests Yaşar as target-paper coauthor; outputs do not assume that relation and only ask for journal authorship in O.',
 'G03':'H candidate paper is already explicitly scoped in O and C; outputs simply return null.',
 'G05':'Kwon founder is already in O/C; joint gift remains unknown despite H.',
 'G06':'Ding candidate already in O and dated C5; outputs null without importing question-wide identity.',
 'G08':'Sophie/death facts already in O/C; neither output imports another partner, song or interview from H.',
 'G09':'H suggests Immaterial as song, but outputs null for partner identity and do not add a song obligation.',
 'G11':'H repeats author/book already in O/C; article is not promoted to existence.',
 'G12':'C1/C3, rather than H, support satisfied article obligation.',
 'G14':'H suggests Euler as book referent, but both outputs retain unestablished book/reference and avoid hardwiring Euler into required evidence.',
 'G17':'H proposes SPS as shared disorder; outputs still require the actual case-specific diagnosis.',
 'G18':'H common FOP diagnosis independently supported by C7/C9; no extra gap or support.',
 'G20':'H game identity already in O/C; no H-only DLC is introduced.',
 'G21':'Rights of Man already named in O and credits in C; null is supported independently of H.',
 'G23':'H says host university remains unknown, but outputs do not switch to host search. Australia error draws on C1/O, not H-exclusive information; same error exists in G0.',
 'G26':'H transfers March 5 to letter; both outputs explicitly reject that transfer and request writing date.',
 'G27':'H March 5 letter label is not added to O; region null result is based on C3.'}
 for cid,c in bank().items():
  for a in ('G0','G1'):
   relation='different_gap' if a=='G0' and cid in ('G08','G14') else 'compatible_gap' if cid=='G23' else 'same_gap'
   pair=[lookup[cid,a,r] for r in (1,2)]
   pairs.append({'case_id':cid,'arm':a,'review_ids':[reverse[r['id']] for r in pair],'relation':relation,'reason':why[cid]})
  for rep in (1,2):
   r=lookup[cid,'G1',rep]
   hrows.append({'id':r['id'],'review_id':reverse[r['id']],'H_contamination':False,'H_present':c['belief']['hypothesis'] is not None,
    'reason':hwhy.get(cid,'Original H is null; no hypothesis content is available to contaminate the gap.')})
 write(P/'e1_gap/review/PAIR_REVIEW.json',pairs);write(P/'e1_gap/review/H_REVIEW.json',hrows)
 write(P/'e1_gap/review/SECOND_PASS_ATTESTATION.json',{'first_pass_commit':git('rev-parse','HEAD'),'first_pass_labels_unchanged':True,
  'pair_review_completed_before_aggregate':True,'H_revealed_after_first_pass_commit':True,'pairs':54,'G1_H_reviews':54,'independent_reviewer':False})
if __name__=='__main__':main()
