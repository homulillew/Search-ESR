"""Single-reviewer content judgments, authored before opening the masked key.

This expands manual reviews of identical context/output groups, not model votes.
No access to KEY.json, call identifiers, arms, replicates, or aggregate scores.
"""
from experiments.contextual_subtraction_qualification.common import P, read, write
from experiments.contextual_subtraction_qualification.score import validate_judgment

NOTES = {
1: 'DLC date alone leaves the base-game genre/date and required release interval unsupported.',
2: 'Founder and education facts do not establish the 2019 marriage/childlessness condition.',
3: 'The whole founder requirement lacks the game release/ranking qualifications.',
4: 'Nationality and championship-team membership jointly bind the Australian coder condition.',
5: 'Package identity and the technology/Coptic-system diary establish the local religion/technology condition; nation qualifications remain unresolved.',
6: 'Patient nationality supplies neither report-country attribution nor the country-history condition.',
7: 'The frozen policy allows the D10-bound table fact on a candidate branch. The response instead requires final target-paper identification. Its observed five-versus-six-table objection is real at the full-question level; the disagreement concerns whether that prevents local conditional subtraction.',
8: 'A degree at Sogang does not establish a building-university affiliation.',
9: 'The country-history condition is genuinely missing. Mention of a Pakistani patient still does not establish report-country attribution.',
10: 'The frozen general mechanics predicate is supported by government/subject changes; the response additionally requires religion, technology, and the nation condition. This scope boundary was predeclared ambiguous.',
11: 'An Athens death does not establish a distance to the specified aviation site.',
12: 'Both dated releases jointly establish the over-three-years interval.',
13: 'Children recorded in 2025 cannot establish childlessness through 2019.',
14: 'General FOP information does not establish the specific individual history.',
15: 'Ding marriage information does not establish the gift/building/complex relation of the entire Parent.',
16: 'The supplied coauthor claim establishes the candidate paper authorship under the frozen branch-conditional policy. Requiring that it already be the final target is an additional global identification requirement.',
17: 'Both publication years establish the six-year comparison under the frozen year-level convention. The response reasonably notes missing exact elapsed-day information, but that stricter interpretation is not this reference. Predeclared ambiguity.',
18: 'There is no supplied marriage/childlessness evidence for Kwon.',
19: 'Letter/author binding and the letter-content claim jointly establish the region-reference condition.',
20: 'Book publication alone lacks the later-article operand and comparison required by the Parent. Accepting the isolated publication fragment cuts that governing relation.',
21: 'Jerry nationality and teammate names do not establish that the other two teammates share a country.',
22: 'A thesis and advisor do not establish DLC release timing.',
23: 'The accession date is missing, so the required letter/accession interval cannot be established.',
24: 'Generic FOP facts do not supply this individual clinical presentation.',
25: 'FOP background is not case-specific half-year pain-history evidence.',
26: 'The named coauthors and paper establish candidate-local authorship; final target identification is not asserted.',
27: 'A professor profile does not establish two authors of the paper.',
28: 'The specific C7 case directly establishes the clinical-history condition explicitly designated positive in the task. Requiring the separate country/history clause first rejects that allowed partial support.',
29: 'The singleton that-paper table claim lacks its supplied antecedent under the strict frozen binding reference. Acceptance disagrees with that predeclared ambiguous anaphora convention.',
30: 'The DLC/game binding, strategy genre, and both release dates are supplied jointly.',
31: 'The death-city fact lacks a measured distance and the requisite aviation-site binding.',
32: 'Patient nationality is not report-country evidence, and the historical country qualification is also absent.',
33: 'Academic identity alone does not establish two-person authorship.',
34: 'Jerry nationality alone lacks the championship-team membership relation governing this locator.',
35: 'Rejection is correct. The explanation points to unsupported well-known/central-European attributes but does not identify the central missing book-to-Euler reference edge; explanatory fidelity is partial.',
36: 'The partner and tribute do not identify a charity or its name relation to the artist.',
37: 'No charity-name relation is established; mentioning other absent charity conditions does not cure that primary gap.',
38: 'Neither a letter-writing date nor an accession date is established by a transmission memorandum.',
39: 'A 2025 family-status claim does not prove the 2019 condition.',
40: 'The whole DLC condition lacks a supported specific playable European nation and its new mechanics.',
41: 'The accession-date operand is absent, precluding the required temporal comparison.',
42: 'General SPS symptoms do not establish the specific case history.',
43: 'A Canadian doctorate does not establish an Iranian supervisor.',
44: 'Article categories and tables do not establish the number of authors.',
45: 'The clinical case does not establish the required report-country/history condition.',
46: 'Ottoman flavor/details do not establish the full playable-European-nation qualification.',
47: 'Content categories and table descriptions leave authorship unsupported.',
48: 'Correctly identifies the missing target-book reference relation despite true Euler birth attributes.',
49: 'Artist identity alone does not establish a shared charity-name component.',
50: 'Partner/tribute evidence does not establish the charity-name condition.',
51: 'The whole founder Parent lacks university founding date and required game release/ranking facts.',
52: 'Coauthor and profile evidence establishes candidate-local authorship. Requiring final target-paper identification exceeds the frozen partial-support convention.',
53: 'Athens identity does not establish the required distance to the specified aviation site.',
54: 'Ding candidate binding plus contemporaneous marriage/childlessness evidence establishes this clause; gift and complex remain unresolved.',
55: 'University attendance is not evidence that the building belongs to that university.',
56: 'The named artist claim lacks any charity-name relation.',
57: 'The full founder condition lacks division/release, earnings-ranking, and university-founding qualifiers.',
58: 'Thesis/advisor facts do not establish a qualifying DLC release interval.',
59: 'Observed government/subject changes support the general mechanics predicate under the frozen scope policy; particular religion/technology/nation constraints remain separate. Predeclared ambiguity.',
60: 'General SPS progression does not establish the individual six-month history.',
61: 'Ding education/family facts do not establish the building, opening schedule, or university relation.',
62: 'The entire DLC Parent lacks its qualified nation-mechanics condition.',
63: 'Founder/degree facts supply no 2019 marriage/childlessness evidence.',
64: 'The thesis/advisor claims do not establish a DLC release or its timing relative to the base game.',
65: 'The response requires religion/technology before accepting the general mechanics predicate. Government/subject changes suffice under the frozen partial-scope convention, whose ambiguity was declared.',
66: 'The partner/tribute claims lack the artist-charity name relation.',
67: 'DLC evidence leaves the playable-European-nation new-mechanics condition unestablished.',
68: 'Neither teammate country is supplied; Jerry nationality does not establish their same-country relation.',
69: 'The half-year duration for a particular case is missing from generic SPS information; generic pain descriptions are not themselves proof about that individual.',
70: 'The DLC and base-game dated releases, genre and identity jointly establish the complete release Parent.',
71: 'Article date alone lacks the book operand/date of the six-year relation.',
72: 'Package binding and the manual establish the technology change.',
73: 'Founder/education facts leave material game and university qualifiers unsupported.',
74: 'Article content descriptions do not identify its two authors.',
75: 'A professor identity does not establish paper coauthorship.',
76: 'Named paper, table context, and table entry jointly establish the candidate table-emotion fact.',
77: 'The actual case claim establishes the clinical-history sentence; this does not close the country/history Parent.',
78: 'Under the frozen candidate-conditional policy the bound table fact qualifies. The response requires final-paper identity and cites the real five-versus-six-table discrepancy in Q; this is a disagreement over local versus global eligibility, not a fabricated discrepancy.',
79: 'Correctly notes missing countries of the other two teammates. The alternative as-Jerry comparison is not required by the Parent; the relevant relation is with each other.',
80: 'DLC date without base release date/genre cannot establish the complete release Parent.',
81: 'Correct rejection of book-only evidence, but the explanation demands author/PhD/target identification rather than naming the crucial missing later-article operand. Additional global premises are not generally required for every local fact under the frozen policy.',
82: 'The observed two-author paper meets the candidate-local authorship reference. Requiring proof of final target identity causes a missed positive under that convention.',
83: 'The category/table claims do not establish authorship count.',
84: 'No supplied claim establishes supervision by an Iranian professor.',
85: 'A 2022 article without a book date does not establish the six-year comparison.',
86: 'The degree claim establishes a person-university relation, not the Parent building-university relation; accepting it substitutes roles.',
87: 'Article-only evidence does not supply the book or required interval.',
88: 'The specific clinical case directly establishes six-month multisite pain.',
89: 'The death city alone supplies neither the specified aviation site nor its distance.',
90: 'The observed two-author candidate paper satisfies this local authorship certificate, without declaring the entire question solved.',
91: 'No building, schedule or building-university relation is supplied.',
92: 'The article claim lacks a book publication date and comparison.',
93: 'The frozen reference accepts handover/content as the bound letter case. The response identifies a genuine literal gap: these two selected claims do not explicitly say King Michael rules Romania. This is a post-review reference-boundary concern, not a Gold change; the strict referent reading is defensible.',
94: 'No Iranian-supervisor relation is supplied.',
95: 'Same-author book and later article jointly supply both operands, aligned topic and publication years for the Parent context.',
96: 'Teammate names do not establish their countries or equality of countries.',
97: 'D10 table binding and the emotion entry establish the candidate table fact.',
98: 'The doctorate claim lacks supervisor identity/nationality.',
99: 'The tribute gives no charity-name relation; the other charity qualifications also remain unresolved.',
100: 'Founder and education evidence has no marriage/childlessness information.',
101: 'Nationality without the championship-team relation is insufficient in the full Parent even though the standalone fragment is locally true.',
102: 'Thesis/advisor facts do not establish the DLC release condition.',
103: 'C7 directly supports walking/shoulder difficulty for the observed clinical case. Requiring the separate first-case country/history clause rejects task-specified partial support.',
104: 'Professor identity does not establish exactly two paper authors.',
105: 'Ottoman flavor/details do not establish a specific playable European nation receiving new mechanics.',
106: 'The individual case directly establishes walking and shoulder difficulty.',
107: 'The evidence lacks playability/European status and the required new-mechanics attribution.',
108: 'Marriage/childlessness is supported but the whole Parent additionally requires the gift/building/complex relation.',
109: 'The base-game release-date operand is missing.',
110: 'The supplied founder/degree claims provide no marriage/childlessness evidence.',
111: 'The DLC date alone cannot establish the required interval from the base-game release.',
112: 'Euler birth attributes are locally true, but the target-book reference relation is absent; this acceptance cuts the governing relation.',
113: 'Generic SPS progression supplies no case-specific half-year history.',
114: 'The two-author candidate-paper claim satisfies the frozen local reference. The response requires prior proof of final target identity.',
115: 'The whole Parent lacks the specific playable-European-nation new-mechanics condition.',
116: 'Ding biography does not establish the building/schedule/university condition.',
117: 'Nationality, coder identity, team membership and championship are jointly established.',
118: 'Artist identity provides no charity or artist-charity name relation.',
119: 'Family status in 2025 does not prove the historical 2019 condition.',
120: 'The supplied DLC claims do not establish the fully qualified nation/new-mechanics condition.',
121: 'Both same-author publications supply comparable mathematics/Vipassana subjects.',
122: 'No building affiliation or opening schedule appears in the supplied Ding facts.',
123: 'The 2016 and 2022 publication years meet the frozen six-year convention; exact elapsed-day equivalence remains a predeclared ambiguity.',
124: 'General FOP genetics/trauma facts do not establish the individual half-year pain history.',
125: 'Accepted under the frozen bound-letter reference. A post-review stricter reading notes that this selected pair does not explicitly bind King Michael as ruler of Romania; the ambiguity is disclosed without relabeling.',
126: 'A transmission-memo date is not a letter-writing date, and accession timing is absent.',
127: 'Ding marriage/childlessness cannot establish the entire gift/building/complex condition.',
128: 'Package binding, development diaries and manual jointly establish religion/technology mechanics; no claim is made that the qualified nation condition is solved.',
129: 'Jerry nationality alone does not establish membership in the winning championship team.',
}

FALSE_ACCEPT = {20, 29, 86, 101, 112}
GLOBAL_OR_SCOPE_REJECTION = {7, 10, 16, 28, 52, 65, 78, 82, 103, 114}
PARTIAL_RATIONALE = {35, 79, 81}
PREDECLARED_AMBIGUOUS_GROUPS = {10, 17, 29, 59, 65, 123}
POST_REVIEW_REFERENT_CONCERN = {93, 125}

def main():
    groups = read(P/'e1_qualification/review/VIEW_GROUPS.json')
    assert set(NOTES) == set(range(1, len(groups)+1))
    judgments = {}
    for g in groups:
        i = int(g['group_id'][1:])
        diagnostic = 'consistent'
        fidelity = 'not_applicable' if g['output']['verdict'] == 'SUBTRACTABLE' else 'faithful'
        if i in FALSE_ACCEPT:
            diagnostic = 'semantic_binding_missing'
        if i in GLOBAL_OR_SCOPE_REJECTION:
            diagnostic, fidelity = 'other', 'unfaithful'
        if i == 17:
            diagnostic, fidelity = 'qualifier_or_scope_missing', 'unfaithful'
        if i in PARTIAL_RATIONALE:
            fidelity = 'partly_faithful'
        if i == 93:
            diagnostic, fidelity = 'other', 'partly_faithful'
        j = dict(reason=NOTES[i], diagnostic=diagnostic,
                 missing_semantics_fidelity=fidelity,
                 ambiguity=i in PREDECLARED_AMBIGUOUS_GROUPS | POST_REVIEW_REFERENT_CONCERN)
        validate_judgment(j)
        for bid in g['review_ids']:
            assert bid not in judgments
            judgments[bid] = j
    assert len(judgments) == 192
    write(P/'e1_qualification/review/JUDGMENTS.json', judgments)
    write(P/'e1_qualification/review/REVIEW_METHOD.json', {
        'groups_manually_reviewed': len(groups), 'packet_count': len(judgments),
        'masked_key_read_by_reviewer': False,
        'aggregate_scores_inspected_before_sealing': False,
        'provider_reasoning_used': False, 'gold_relabeling': False,
        'primary_reference': 'unchanged pre-call E0 Gold',
        'fidelity_interpretation': 'sufficiency under frozen local eligibility policy, not denial that other global conditions remain unresolved',
        'post_review_reference_concern_groups': ['V093', 'V125'],
        'post_review_concern': 'selected letter Claims omit explicit author-country rulership; retain primary Gold and report separate post-hoc sensitivity',
        'limitation': 'single task-familiar reviewer; candidate-local versus final-target identity is an explicit reference-policy choice; masking can leak through rationale wording'
    })
    print({'reviewed_groups': len(groups), 'sealed_ready_packets': len(judgments)})

if __name__ == '__main__':
    main()
