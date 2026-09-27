"""Explicit Gold/H/pair judgments after first-pass commit; no model calls."""
from experiments.dynamic_local_obligation.common import *
from experiments.dynamic_local_obligation.run import OUT,load_rows
from experiments.dynamic_local_obligation.score import strict

def main():
 assert git('rev-parse','HEAD')=='06f31332fa3fac1574cdaebdcaec55e69f180245'
 key=read(OUT/'review/KEY.json');reverse={v:k for k,v in key.items()};labels={key[l['review_id']]:l for l in read(OUT/'review/REVIEW.json')};rows=load_rows();cases=bank();lookup={(r['case_id'],r['arm'],r['replicate']):r for r in rows}
 equivalent={'R006','R097','R104','R016','R025','R035','R077','R060','R072'}
 eq_reason={
  'R035':'Same Sophie-partner post-death interview discovery as Gold. One-word-adjective filter is omitted; near core-objective equivalence, not literal identity.',
  'R077':'Same Sophie partner/interview relation; explicitly asks partner identification too. One-word title qualifier omitted; near semantic objective.',
  'R060':'Same letter identity/delivery/relative-date objective; adds the region-mention clue without asking its name. Near equivalence with a content-profile addition.',
  'R072':'Same letter identity objective and main defining relations; region mention is an extra identifying context, not the final region-name task.'}
 comparison=[]
 for r in rows:
  rid=reverse[r['id']];ok=strict(r,labels[r['id']]);classification='invalid' if not ok else 'gold_equivalent' if rid in equivalent else 'alternate_valid'
  reason=labels[r['id']]['reason'] if not ok else eq_reason.get(rid,'Semantic paraphrase of the same frozen DLC/letter identification objective.' if classification=='gold_equivalent' else 'Different or substantively expanded/narrowed objective from historical Gold, independently passed all eight first-pass dimensions. A valid alternative receives full strict credit.')
  comparison.append({'id':r['id'],'review_id':rid,'classification':classification,'reason':reason,
   'near_equivalence_scope_note':eq_reason.get(rid),'historical_gold_unchanged':True})
 # Explicit pair judgments over the already-read output pairs.
 paircodes={
 'G01':('both_invalid','both_invalid'), 'G02':('both_invalid','one_valid_one_invalid'),
 'G03':('one_valid_one_invalid','both_invalid'), 'G04':('compatible_obligation','compatible_obligation'),
 'G05':('both_invalid','both_invalid'), 'G06':('both_invalid','both_invalid'),
 'G07':('one_valid_one_invalid','one_valid_one_invalid'), 'G08':('compatible_obligation','different_but_valid'),
 'G09':('same_obligation','both_invalid'), 'G10':('different_but_valid','same_obligation'),
 'G11':('both_invalid','both_invalid'), 'G12':('same_obligation','different_but_valid'),
 'G13':('both_invalid','both_invalid'), 'G14':('both_invalid','both_invalid'),
 'G15':('both_invalid','both_invalid'), 'G16':('both_invalid','both_invalid'),
 'G17':('one_valid_one_invalid','both_invalid'), 'G18':('one_valid_one_invalid','different_but_valid'),
 'G19':('same_obligation','same_obligation'), 'G20':('same_obligation','same_obligation'),
 'G21':('same_obligation','different_but_valid'), 'G22':('both_invalid','both_invalid'),
 'G23':('same_obligation','same_obligation'), 'G24':('same_obligation','one_valid_one_invalid'),
 'G25':('same_obligation','one_valid_one_invalid'), 'G26':('same_obligation','one_valid_one_invalid'),
 'G27':('one_valid_one_invalid','different_but_valid')}
 notes={
 'G01':'Full paper restatement in both; some also merge author roles.',
 'G02':'O0 broad/fixed author or wrong coauthor; O1 first direct authorship test valid, second full question/role merge invalid.',
 'G03':'O0 second checks unestablished total table count; other outputs repeat full Q.',
 'G04':'Both discover the same gift-funded building; explicit university/opening context differs compatibly.',
 'G05':'Both bundle unestablished gift/building with final university extraction.',
 'G06':'Both bundle unestablished donor-gift/building and university; no valid repetition.',
 'G07':'One bounded artist profile is valid; other either adds all interview stages or changes country binding.',
 'G08':'O0 interview discovery with/without explicit partner identity remains compatible. O1 switches between interview source and aviation accident.',
 'G09':'O0 maps actual quote to song; O1 assumes interview/stronger song-reference event.',
 'G10':'O0 switches author identity to article identity; both valid but different targets. O1 stays author academic-profile identification.',
 'G11':'Both request title of an unestablished article event.',
 'G12':'O0 stays supervisor identity/profile; O1 switches promotion/education to supervision.',
 'G13':'Both copy full book question.',
 'G14':'Both fix unverified Euler reference; broadness varies but neither strict-valid.',
 'G15':'Both repeat all independent identifying clues.',
 'G16':'Both ask diagnosis of unbound reports.',
 'G17':'O0 direct SPS/case relation test valid, other unbound diagnosis requests invalid.',
 'G18':'O0 first stale common diagnosis, second unresolved case/date correspondence. O1 country-history versus publication dates are different valid qualifiers.',
 'G19':'Same DLC profile discovery.', 'G20':'Same known-game DLC profile discovery.',
 'G21':'O0 same advisor qualification; O1 advisor versus nation mechanics are different valid objectives.',
 'G22':'Both jump to edition/calendar attributes before winning event is identified.',
 'G23':'Same host university of established final; valid alternative to Gold teammate-origin relation.',
 'G24':'O0 preserves same-country equality between the other two; O1 second incorrectly adds Jerry.',
 'G25':'O0 both identify letter profile without region name; O1 second appends final extraction.',
 'G26':'O0 same region of established letter; O1 second skips final-courier identification to nickname relation.',
 'G27':'O0 first substitutes initial handoff officer for final courier; second valid courier discovery. O1 switches courier to qualifying-letter identification.'}
 pairs=[]
 for cid,codes in paircodes.items():
  for a,code in zip(('O0','O1'),codes):
   pairs.append({'case_id':cid,'arm':a,'review_ids':[reverse[lookup[cid,a,i]['id']] for i in (1,2)],'relation':code,'reason':notes[cid]})
 hnotes={
 'G02':'H suggests Yaşar target authorship. O1 rep1 asks whether, without promoting it; rep2 uses generic author roles. Named candidate is already in C.',
 'G03':'O1 repeats generic Q constraints, no H-only paper title or match asserted.',
 'G05':'O1 leaves donor generic; Kwon name is not imported. Bundling failure is independent of H-only content.',
 'G06':'O1 leaves founder/person generic; Ding candidate is not made a required donor.',
 'G08':'Sophie/death/city/date are in C; one output remains generic interview discovery, one tests aviation relation. No exclusive H fact.',
 'G09':'H suggests title Immaterial, but neither O1 output supplies that title. Interview/song-reference presuppositions are erroneous, yet not identifiable as an H-exclusive candidate fact; no causal attribution from presence alone.',
 'G11':'C already gives Marwaha/book. Both arms assume later article; H itself does not assert article existence. No H-exclusive content promoted.',
 'G12':'Known author/PhD setting from C, other qualification clues from Q; no H-only fact.',
 'G14':'H alone explicitly proposes Euler as the book\'s referenced L.E.; C gives birth details only. O1 makes the book-reference relation mandatory. Count provisional-role promotion, not mere occurrence of Euler\'s name. O0 also makes this error, so H causation is not established.',
 'G17':'H names SPS as shared disorder, but O1 does not assume it; generic diagnosis requests are a separate defect.',
 'G18':'H shared FOP content does not enter selected obligations; O1 checks country/history and dates.',
 'G20':'EU4 is already explicit in C; no extra candidate pack introduced.',
 'G21':'Rights of Man and advisor already in C; direct Q-profile checks need no H-only match assertion.',
 'G23':'H suggests host need, independently unresolved from Q/C. No exclusive fact; both arms choose it.',
 'G26':'Bad H letter date not promoted: one output explicitly attaches date to memo, other omits date.',
 'G27':'Neither output imports H\'s March5 letter label; courier/profile targets stay separate.'}
 hs=[]
 for r in rows:
  if r['arm']!='O1':continue
  c=cases[r['case_id']];present=c['belief']['hypothesis'] is not None
  hs.append({'id':r['id'],'review_id':reverse[r['id']],'H_present':present,'H_contamination':r['case_id']=='G14',
   'reason':hnotes.get(r['case_id'],'Original H is null, so no H content can be promoted.'),
   'interpretation':'Content-based provisional-role promotion when present; not a proven causal effect of H.'})
 write(OUT/'review/GOLD_COMPARISON.json',comparison);write(OUT/'review/PAIR_REVIEW.json',pairs);write(OUT/'review/H_REVIEW.json',hs)
 write(OUT/'review/SECOND_PASS_ATTESTATION.json',{'first_pass_commit':git('rev-parse','HEAD'),'first_pass_labels_changed':False,
  'Gold_H_KEY_revealed_after_commit':True,'pairs_reviewed':54,'H_outputs_reviewed':54,'aggregate_computed_before_this_pass':False,
  'gold_equivalence_boundary':'Same or near core local objective; substantive new relation/profile treated alternate-valid. Near equivalents explicitly record scope deltas; direct old-Gap inheritance would need verification if E2 were reached.'})
if __name__=='__main__':main()
