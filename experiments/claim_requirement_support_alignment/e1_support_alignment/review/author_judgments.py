"""Single-reviewer judgments after reading all64 masked content groups.

No KEY, model packet origin, aggregate metrics, raw response or provider
reasoning is read. Exact duplicate packets share a judgment, not a denominator.
"""
from experiments.claim_requirement_support_alignment.common import *

NOTES={
1:'C4 supplies technology/Coptic changes and Ottoman flavor, but no supplied Claim establishes European/playable. Copying that complete qualifier overreaches; together the listed spans cover the Parent despite the unresolved qualifier, hence a false-full hazard. C6 technology and C7 general mechanics-change spans are supported. This is unsupported qualification, not a transfer of an observed fact to a different argument. Frozen mechanics-scope ambiguity retained.',
2:'C1 book and C3 article are the same-author, aligned-topic, 2016/2022 operands of the frozen joint support group. Both selected; no unsupported Claim selected. Joint-support reference ambiguity remains.',
3:'C2 correctly establishes champion membership/year. Its Australian span is grounded only jointly with the observed C1 under the frozen joint-support convention, so scope is accepted on the complete Claims. However C1 itself establishes the nationality material condition and is incorrectly demoted to binding. This is missed true support and creates a possible typed-packet inconsistency; no invented nationality or actual false-full on this Gold-F parent.',
4:'C5 scope correctly limits support to Ding marriage/2019 childlessness. Founder contexts are not promoted, the 2025 Kwon family fact is not transferred to Ding or 2019, and no gift is claimed. Several secondary background/binding roles differ from reference.',
5:'Thesis identifies the candidate base game; neither thesis nor advisor establishes DLC release or interval. Empty support is correct.',
6:'C2 directly supplies Canadian PhD study; C1 author/book identity does not supply Iranian-advisor support. Correct selected support.',
7:'No support promoted for an unidentified building. Educational and 2025 family facts are labeled binding rather than background; frozen secondary-role ambiguity, without a false-subtraction assignment.',
8:'C2 supplies the two-author component. No evidence establishes the Baltic publication condition. Correct partial support selection.',
9:'C1 nationality and C2 champion membership are both selected and join on Jerry. Correct full support set; title year and held year are not reassigned.',
10:'Euler biography remains non-support: no observed book-to-Euler citation relation. Correct empty selection.',
11:'Sophie is candidate-binding only; no observed charity or name-sharing/registration relation. Correct empty support and binding role.',
12:'Names and Jerry nationality do not establish that the other two teammates share a country. Correct empty support.',
13:'Death city and accidental death are exactly the observed material portions. No aviation distance, deadliest status or fifteen-year relation is claimed.',
14:'Book-only C1 is binding under the frozen reference; no article exists in current Claims to support the comparison. Correct empty set; reference joint-support boundary is explicitly ambiguous.',
15:'Book-only C1 remains binding, not article support. C2 is labeled irrelevant instead of background; no safety error. Frozen book-anchor ambiguity retained.',
16:'Over-conservative empty selection misses C2, which directly establishes the candidate paper having two coauthors. The unverified Baltic paper does not erase that partial support.',
17:'No building support is promoted. Kwon candidate/context is discarded and Ding education/marriage are labeled binding; these are secondary reference-role differences, not observed cross-candidate mixing. Frozen background/binding ambiguity applies.',
18:'C4 and C7 spans improperly include the whole playable-European-nation qualifier. Claims state Ottoman flavor/new details, without those required properties. C6 technology scope is correct. The union purports to cover every material condition, a false-full hazard on the frozen partial parent. Mechanics interpretation was flagged ambiguous before calls.',
19:'Sophie identity binds the artist; partner identity and tribute remain background. No charity relation is invented.',
20:'No affiliation/opening support is promoted. Sogang education is binding in output but background in frozen reference; no established building relation follows under either interpretation. Frozen role ambiguity retained.',
21:'Founder and university graduation spans are limited to the facts in C1/C2; no company-founding-to-game-release date transfer or university-founding inference.',
22:'Only Ding marriage/2019 childlessness C5 selected; Kwon and Ding are not merged. Gift and complex relation remain unproved.',
23:'C5 directly establishes the emotion percentage in the identified table. Correct support selection; paper/author context is not promoted.',
24:'C3 copied span states the letter-content/author/country/region relation actually given. C1/C2 bind the same letter. Correct scope without introducing a letter date.',
25:'No charity support. Partner facts are irrelevant in output versus background in reference; secondary role disagreement only.',
26:'Jerry identity and the two named teammates are correctly treated as binding. No transfer of Jerry nationality to the other teammates.',
27:'Euler birth/identity is promoted to a material requirement fragment without the required book-reference relation. This drops the governing source/relation binding: false entity-overlap support and binding-to-support promotion, counted as relation-binding corruption. The other referenced people and overall book relation remain unclaimed, so no false-full hazard.',
28:'Empty output misses genuine partial support: artist death city and accidentality are explicitly observed even though the aviation relation remains unverified.',
29:'No author-count/Baltic-paper support is promoted. Harran professor identity is labeled irrelevant rather than candidate-binding; secondary-role omission only.',
30:'Book-publication and article-publication spans are genuine material contributions under the declared joint support group. Output does not claim the six-year comparison; narrower scope is sound precision, not evidence of complete scope recall. C2 scholarship labeled binding instead of background. Frozen joint-reference ambiguity retained.',
31:'Empty selection misses both established founder and graduation components. Remaining game-release/earning/university-date qualifiers do not negate those true partial facts.',
32:'C5 childlessness-from-marriage span is correct on Ding branch. C4 remains context; C3 is not used as 2019 marital evidence and branches are not combined.',
33:'C7 alone establishes the specific first-case clinical history. Correct support ID selection. ID-only output has no report-country scope assertion to evaluate.',
34:'Population-level SPS course and symptoms remain generic background; no case-specific or geographic support is created.',
35:'Euler biography is promoted to the cited-figure fragment without any observed book-to-person reference relation. Governing source/relation binding is dropped; entity relevance and binding context become false support. Entire multi-person Parent is not claimed covered, so no false-full hazard.',
36:'No observed charity relation; correct empty support for artist-only evidence.',
37:'Game-related thesis and advisor do not establish a downloadable-content release relation. Correct empty support.',
38:'Book-only C1 is promoted from its frozen binding role despite absence of any journal-article operand. The book fact is true, but treating it as article-relation support drops the required event/relation binding. False support and relation-binding corruption under primary frozen labels. This is a predeclared ambiguous reference; report its sensitivity without changing the label. No claim of full comparison coverage.',
39:'C7 spans correctly cover only the six-month clinical course and movement limitations. No transfer of Pakistani nationality into report-country/history. C9 separate-case context is labeled irrelevant instead of binding; C6 background is also demoted, with no support promotion.',
40:'C4 and C6 are valid support. C7 is missed under the frozen mechanics reference; its new government/subject details count as a material mechanics contribution. The reference boundary was marked ambiguous before calls.',
41:'Only two-author clause is claimed for C2; the separate Baltic paper stays unresolved. Roles and scope align with the reference.',
42:'Cover-memorandum date and handover identify the letter but do not establish its composition date or ruler accession interval. Both remain binding; no temporal/object transfer.',
43:'C7 exact clinical-history span is supported; no report-country or national-history scope is copied. The second-case context is discarded rather than merged into the first. Secondary role differences only.',
44:'Generic SPS facts do not establish a target case history. Correct empty selection.',
45:'Founder and alma mater supply no building affiliation or opening date. Correct empty support, with the frozen role-boundary ambiguity irrelevant to the binary selection.',
46:'Harran professor identifies a possible author but does not establish two coauthors or a Baltic-paper relation. Correct binding-only role.',
47:'Founder and graduation substrings are both directly supported. No unsupported release date, game ranking or university founding date is included.',
48:'C3 release of the DLC and C5 game genre/base release are supported operands. The fragments do not claim the >3-year comparison; this limits scope coverage but does not overreach. Date disagreement within August2013 does not change the frozen joint interval. Secondary role differences and frozen joint ambiguity retained.',
49:'C3 and C5 are correct release/genre operands; C3 strategy-game phrase is grounded through the declared C3+C5 joint support. C5 spans are supported but the >3-year comparison is not explicitly covered. Many adjacent facts are labeled binding rather than background/irrelevant; no false substantive support. Frozen joint ambiguity retained.',
50:'C3+C5 establish DLC/base release relation and >3-year interval, even with either reported August day. Correct joint support set, with frozen joint-reference ambiguity.',
51:'C1 nationality and C2 team-membership/championship spans preserve the distinct material contributions. Correct support set and scope; no teammate-country inference.',
52:'C3 directly establishes the complete letter-content/region relation. C1/C2 supply letter binding and do not contribute dates as support.',
53:'Neither covering memorandum nor handover gives the letter-writing/accession interval. Correct empty support.',
54:'Death city and accidentality substrings are supported; none of the absent aviation conditions is promoted.',
55:'Book/article publication and topical similarity are grounded jointly in C1+C3 as preregistered. Both selected. C2 scholarship is secondary binding/background disagreement. Interval is not explicitly claimed; no scope overreach. Frozen joint-reference ambiguity retained.',
56:'A Harran professor identity does not establish target-paper coauthors or another article. Correct empty support.',
57:'C2 Canadian PhD-study span is supported; Iranian advisor clause remains unresolved. Correct selected support and scope.',
58:'No Claim establishes a concrete building affiliation or opening, despite two founder branches and university names. Correct empty selection; frozen secondary-role ambiguity.',
59:'Kwon founder and degree do not establish spouse childlessness, gift or a building relation. Correct empty support.',
60:'C5 emotion percentage and table locator spans are supported. Other clues are over-labeled binding relative to reference, but none promoted to substantive support.',
61:'C2 two-author clause is supported and appropriately bounded. Other same-paper/Harran facts are demoted to irrelevant relative to reference; no false promotion.',
62:'Partner and song tribute do not establish any charity/name/registration condition. Correct empty support.',
63:'C3 states the letter refers to Romania regaining a region. Correct single support Claim; transmission facts alone are not substantive for this Parent.',
64:'Founder and degree are treated as candidate context, with no false marriage/gift support. Degree binding rather than background is a secondary role disagreement.'
}
SCOPES={1:['C6','C7'],3:['C2'],4:['C5'],13:['C1'],18:['C6'],21:['C1','C2'],24:['C3'],30:['C1','C3'],32:['C5'],39:['C7'],41:['C2'],43:['C7'],47:['C1','C2'],48:['C3','C5'],49:['C3','C5'],51:['C1','C2'],52:['C3'],54:['C1'],55:['C1','C3'],57:['C2'],60:['C5'],61:['C2']}
AMBIGUOUS={1,2,7,14,15,17,18,20,30,38,40,45,48,49,50,55,58}
CORRUPT={27,35,38}
FULL_HAZARD={1,18}
TAGS={
 1:['support_scope_overreach','false_full_support'],
 3:['missed_true_support'],16:['missed_true_support'],
 18:['support_scope_overreach','false_full_support'],
 27:['false_support_entity_overlap','false_support_wrong_relation','binding_context_promoted_to_support'],
 28:['missed_true_support'],31:['missed_true_support'],
 35:['false_support_entity_overlap','false_support_wrong_relation','binding_context_promoted_to_support'],
 38:['false_support_wrong_relation','binding_context_promoted_to_support'],
 40:['missed_true_support']}

def main():
 groups=read(P/'e1_support_alignment/review/VIEW_GROUPS.json');assert len(groups)==len(NOTES)==64;out={}
 for v in groups:
  i=int(v['group_id'][1:]);typed='claims' in v['output'];j={'scope_correct_claim_ids':SCOPES.get(i,[]),'relation_argument_corruption':i in CORRUPT,'candidate_branch_mixing':False,'false_full_support_hazard':i in FULL_HAZARD if typed else None,'error_tags':TAGS.get(i,[]),'reason':NOTES[i],'ambiguous_reference':i in AMBIGUOUS}
  assert typed or not j['scope_correct_claim_ids']
  for bid in v['review_ids']:assert bid not in out;out[bid]=j
 assert len(out)==96
 write(P/'e1_support_alignment/review/JUDGMENTS.json',dict(sorted(out.items())))
 write(P/'e1_support_alignment/review/MANUAL_GROUP_NOTES.json',{'review_input_sha256':sha(P/'e1_support_alignment/review/VIEW_GROUPS.json'),'groups_read':64,'packets_covered':96,'KEY_read_before_judgment':False,'provider_reasoning_read':False,'single_task_familiar_reviewer':True,'note':'Primary Gold labels are unchanged. Exact duplicates receive the same semantic judgment and retain separate scoring slots. All detailed judgments were authored before aggregate scores or unmasking.'})
if __name__=='__main__':main()
