"""Explicit manual first-pass judgments derived only from masked VIEW_GROUPS.
No case-ID key, Gold class sets, metrics or provider reasoning loaded here.
"""
from experiments.state_conditioned_residualization.common import P,read,write
R=P/'e1_residualization/review'
FLAGS=('parent_faithful','unresolved','local_coherent','non_downstream','scope_faithful','no_invented_premise')
ERRORS=('supported_content_leakage','broad_residual','downstream','relation_object_temporal_corruption','control_over_decomposition','candidate_hardening')
notes={
 'V01':('teammate_country',[], 'The same-country relation between the two other teammates is unresolved; supplied names and coder nationality only bind participants, not this comparison.'),
 'V02':('book_contents',[], 'No book content is supported. The coherent book-discovery objective includes the illustration count and telephone/telegraph descriptions; losing these constraints is evaluated separately below.'),
 'V03':('academic_career',[], 'No academic-career condition is supported. The full parent links2022 promotion and earlier degrees at the same university, rather than just any2022promotion.'),
 'V04':('book_engineer_reference',[], 'Euler birth biography does not support any book-reference relationship. One referenced-person/book relationship is a legitimate exploratory objective; no concrete book-reference is established.'),
 'V05':('first_case_clinical',[], 'With noClaims, the specific first clinical report or its country/history condition can be an exploratory objective. Unknown referents do not disqualify discovery.'),
 'V06':('jbse_publication',[], 'A Harran profile does not bind the target paper writer or another JBSEpublication. The output tests that publication relation without promoting Mehmet to a verified target writer.'),
 'V07':('jbse_publication',[], 'NoClaims: a paper authorship facet or the linked author other-publication relation is unresolved and parent faithful.'),
 'V08':('gift_building',['C5'], 'C5 supplies Ding2019marriage/childlessness; the requested foundational gift/building relation is still unestablished. Using Ding and spouse as participants does not re-request marital verification.'),
 'V09':('partner_interview_song',['C2','C3'], 'C2/C3 supply the partner and online tribute, not interview genre or song-reference relationship. Testing the latter uses already established context without re-verifying it.'),
 'V10':('report_country_history',[], 'Generic SPS symptom Claims are not target-case support. Country/history or the specific clinical presentation remains an exploratory facet; no SPS diagnosis may be presumed for the case.'),
 'V11':('partner_interview_song',[], 'An artist-death Claim does not establish the partner interview/song relation. The output asks for the relational episode rather than extracting an assumed song title.'),
 'V12':('DLC_release_relation',[], 'Thesis/game/advisor Claims do not establish anyDLC. The release relation remains an exploratory objective; preserve the pack/base-game timing attachment.'),
 'V13':('place_population',[], 'The official population-change place condition is one coherent demographic facet. No candidate place/person is introduced, and person birth is not added as a second verification.'),
 'V14':('gift_building',[], 'Founder and education facts do not support marriage/childlessness or a gift/building. Choose a single one of these unresolved facets without presenting both as one local goal.'),
 'V15':('letter_accession_interval',[], 'The letter transmission record supplies an author anchor but neither letter-writing date nor accession date. A correctly attached temporal comparison or one missing operand is legitimate; March5,1945 must not become the letter date.'),
 'V16':('later_article_relation',[], 'A known author/book and PhD do not establish a later journal article. Article existence/identity and its book-relative timing/topic must remain a research objective, not a presumed fact.'),
 'V17':('death_aviation_relation',[], 'This coherent discovery parent links death and aviation accident by both geography and time. No supporting anchor exists; isolated clues that discard the linked identifying conditions are marked below.'),
 'V18':('gift_building',[], 'With noClaims, the gift/building episode is a legitimate low-commitment facet; it need not also verify childlessness.'),
 'V19':('report_country_history',['C7'], 'C7 establishes the specific clinical history. Outputs use that history only to identify the report and request its country/history condition, which is unresolved. No report country is inferred solely from patient nationality.')}
classes={'B004':'book_LE_reference','B061':'book_LE_reference','B092':'report_country_history',
 'B011':'paper_authorship','B012':'paper_authorship','B014':'tribute_song_link','B100':'first_case_clinical',
 'B046':'marital_childlessness','B034':'author_accession_date','B069':'author_accession_date','B071':'author_accession_date'}
# Explicit semantic exceptions following reading of each displayed residual.
overfragment={'B002','B005','B025','B085','B090','B003','B020','B048','B057','B079','B111','B082','B033','B037','B041','B072','B073','B093','B102'}
exceptions={
 'B106':{'false':['parent_faithful','scope_faithful'],'true':['relation_object_temporal_corruption'],
   'reason':'The parent requires the two other teammates to share a country with each other, not with Jerry. Adding whether that country is Australia introduces an extra relation to the coder and changes the required comparison.'},
 'B004':{'false':['no_invented_premise','scope_faithful'],'true':['candidate_hardening','relation_object_temporal_corruption'],
   'reason':'C1 names Euler and his birth, but does not identify him as the book-referenced L.E. figure. The explicit phrase identified byC1 asEuler hardens a plausible identity into a confirmed referent. A conditional book/Euler test would be admissible; this stronger identification is not established.'},
 'B084':{'false':['local_coherent'],'true':['broad_residual'],
   'reason':'The proposed gift episode still carries the independently unverified childlessness-through2019 clause as part of the target. It retains two independently testable facets instead of selecting one; no named-candidate fact is inferred solely from this descriptor.'}}
def main():
 groups=read(R/'VIEW_GROUPS.json');out={}
 assert {g['group_id'] for g in groups}==set(notes)
 for group in groups:
  default,substantive,reason=notes[group['group_id']]
  for row in group['responses']:
   bid=row['review_id'];v=row['output'];assert bid not in out
   if row['no_response']:
    x={k:None for k in FLAGS+ERRORS+('mode_correct','used_claims_substantive')};x.update(class_id=None,reason='No response available; no semantic repair.')
   else:
    x={k:True for k in FLAGS};x.update({k:False for k in ERRORS});x['class_id']=classes.get(bid,default)
    x['mode_correct']=v['mode']==('residual' if substantive else 'probe')
    used=set(v['used_claims']);x['used_claims_substantive']=bool(used & set(substantive)) and used<=set(substantive) if substantive else not used
    x['reason']=reason
    if bid in overfragment:
     x['scope_faithful']=False;x['control_over_decomposition']=True
     x['reason']+=' The output drops a defining linked constraint of this already coherent parent: '+('the author same-university promotion/degree relationship.' if group['group_id']=='V03' else 'the book count/content conjunction.' if group['group_id']=='V02' else 'the DLC/base-game more-than3years relation.' if group['group_id']=='V12' else 'the required six-year book/article interval.' if group['group_id']=='V16' else 'the death/accident spatial-temporal linkage; an isolated temporal/site/distance piece does not preserve the complete identifying relation.')
     x['ambiguity']='medium: faithful-subset permissive interpretation will be disclosed separately, without changing primary labels'
    if bid in exceptions:
     e=exceptions[bid]
     for k in e['false']:x[k]=False
     for k in e['true']:x[k]=True
     x['reason']=e['reason']
    if bid=='B004':x['ambiguity']='medium: candidate identity wording versus a conditional test'
    if bid in ('B104','B059'):
     x['reason']+=' Establishing the gift/building existence before verifying the complex membership is accepted as one discovery facet for this coarse primary parent, not a claim the full parent is complete.'
    if bid=='B097':x['reason']+=' Establishing report country is a legitimate anchor for its stated historical condition; the clinical condition is not requested again.'
    if bid=='B088':x['reason']+=' The explanatory clause correctly contrasts patient nationality with report country; it is support context, not a second requested research objective.'
    if not x['mode_correct']:x['reason']+=' Mode does not follow the no-substantive-parent-support probe rule; this is a separate diagnostic.'
    if not x['used_claims_substantive']:x['reason']+=' used_claims includes noncontributing identity/background context; report this diagnostic separately from objective validity.'
    if not row['schema_valid']:x['reason']+=' The extra type=json_object field violates the exact output contract; no field is stripped or repaired.'
   x['visible_group']=group['group_id'];out[bid]=x
 assert len(out)==114
 write(R/'MANUAL_NOTES.json',{'group_notes':notes,'class_overrides':classes,'over_decomposition_ids':sorted(overfragment),'exceptions':exceptions})
 write(R/'JUDGMENTS.json',out)
 write(R/'DISCLOSURE.md','''# First-pass disclosure

Single familiar Codex reviewer read19masked groups/all114outputs. Only VIEW_GROUPS/PACKETS read during semantic judgment; no KEY, percaseGoldresidualsets,newaggregate,providerreasoning orfuturetools. CurrentfullClaims shown to judge true unresolvedness; availableIDs and priorpacket shown to constrain modelpremises. Priorhistory memory and packetstyle inference cannot be erased. Identical inputs remain separate response records, not independent reviewers.

All labels committed before aggregate. Conservative control scope retention is explicit; potential faithful-subset reinterpretations are marked for descriptive sensitivity, not label edits. Euler identification wording is a second marked ambiguity. Partial-support outputs use knownconditions as identifiers rather than reasking them; no leakage flag solely for repeated text.
''')
if __name__=='__main__':main()
