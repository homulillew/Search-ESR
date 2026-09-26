"""Single-reviewer, prefix-only frozen coverage. No Frontier outputs read."""
import json
from pathlib import Path

TOP = Path(__file__).resolve().parents[1]
PACKETS = {r['case_id']: r for r in json.load(open(TOP / 'bank/COVERAGE_PACKETS.json'))}
LABELS = {}


def add(cid, state, history, notes, refs, *, combined=None, strata=(), risks=()):
    p = PACKETS[cid]
    combined = set(state) | set(history) if combined is None else set(combined)
    coverage = {}
    for rid in p['requirements']['requirements']:
        n = int(rid[1:])
        claims, sources = refs.get(n, ([], []))
        assert all(1 <= i <= len(p['claims']) for i in claims), (cid, rid)
        assert set(sources) <= set(p['history_source_refs']), (cid, rid, sources)
        coverage[rid] = {'state_resolved': n in state, 'history_resolved': n in history,
                         'combined_resolved': n in combined,
                         'state_claim_refs': [f'C{i}' for i in claims], 'history_support_refs': sources,
                         'supported_and_missing_parts': notes[n]}
    LABELS[cid] = {'case_id': cid, 'qid': p['qid'], 'coverage': coverage,
                   'state_complete': all(v['state_resolved'] for v in coverage.values()),
                   'history_complete': all(v['history_resolved'] for v in coverage.values()),
                   'combined_complete': all(v['combined_resolved'] for v in coverage.values()),
                   'deferred_requirements': [k for k, v in coverage.items() if v['history_resolved'] and not v['state_resolved']],
                   'strata': list(strata), 'candidate_or_scope_risks': list(risks),
                   'reviewer': 'single Codex; original question and exact checkpoint prefix only; no new Frontier outputs'}


for cid in ['F03', 'F04']:
    late = cid == 'F04'
    add(cid, [1,2,3,4] if late else [2,3,4], [1,2,3,4] if late else [2,3,4], {
        1: 'Late: developer binding, former Night Sky and October1993 establishment jointly present. Early: publisher Albino Frog only; development/former-name binding missing.',
        2: 'November1992 DOS explicitly present. Late1993 listing is source disagreement within the same early-1990s range; exact-year reconciliation is optional, not a blocking requested condition.',
        3: 'One offline player and shareware explicit.',
        4: 'Three named credited people, two Pucketts; sufficient named-game binding. No need to invent another game.'},
        {1: ([3,4,9] if late else [2], ['E039','E044'] if late else ['E038']),
         2: ([1,5,11] if late else [1], ['E038','E040','E045'] if late else ['E038']),
         3: ([1], ['E038']), 4: ([2], ['E038'])}, strata=['resolved' if late else 'near_closure'])

for cid in ['F15', 'F16', 'F23']:
    online = cid == 'F23'
    add(cid, [1,2,3,4] if online else [1,2,3], [1,2,3,4], {
        1: 'Insouciance S1E2 uniquely matches the assumption/date setup; wording need not repeat every detail of the user description.',
        2: 'S3E13 Edgar sacrifice plus Edgar as Jimmy roommate jointly present.',
        3: 'S4E7 brother baby and Gretchen/Heidi reconnection explicitly supported.',
        4: 'History E122 explicitly num_seasons5. Only F23 Claims admit the total. Cast through season5 (F16 E125) cannot independently establish a total upper bound.'},
        {1: ([2,3] if online else [4], ['E121']), 2: ([6,7,8,9] if online else [2,3], ['E123','E124']),
         3: ([1], ['E120']), 4: ([4] if online else [], ['E122'])},
        strata=['resolved'] if online else ['near_closure','deferred_reactivation'])


for cid in ['F07', 'F08']:
    late = cid == 'F08'
    add(cid, [], [], {
        1: 'No GameA role-playing/release/funding relation in either view. Dust is a creator credit, not established as GameA.',
        2: 'Late history E083 gives JazzJackrabbit2(1998) and Orange/Epic developers; late Claims retain developers but omit1998. Neither view establishes GameA or seven-year relation; mammal/shooting premise is not fully grounded here.',
        3: 'Early PC source gives Dean, wireless keyboard, creator of Dust. Late adds paper animation and Jazz2 animator, but not intro/end-specific role or dated July2013 account. Those missing links are valid frontiers.',
        4: 'No 300–700 store-title/date relation is present.',
        5: '5TB for Dean’s PC is explicit in both views. The exposed window has no article-date header, and task-level animator binding remains incomplete. Reasking only the known5TB value is stale; verifying date or identity binding is valid.'},
        {1: ([2], ['E081']), 2: ([4,5] if late else [], ['E083'] if late else []),
         3: ([1,3,4] if late else [1,2], ['E081','E082','E083'] if late else ['E081']),
         4: ([], []), 5: ([1], ['E081'])},
        strata=['mid_research','deferred_subrelation'] if late else ['early'],
        risks=['Dean is provisional until GameA/GameB/date/store links; Dust must not be assumed GameB.',
               'F08 history-only1998is an omitted subrelation; composite R2 remains unresolved in all views.'])

for cid in ['F13', 'F14']:
    late = cid == 'F14'
    add(cid, [3] if late else [], [2,3] if late else [], {
        1: 'Late C21/E119 say>600centuries in career without anchoring that count to2025-01-30. No dated lower bound>300 in this prefix. Early has none.',
        2: 'Late C3fifth147 and C21sevenmaximums lack dates. H sees E109 explicit2012/13heading and fifth147, establishing>3beforecutoff. Current undated total alone cannot be backdated.',
        3: 'Late C20/E119 explicitly professional2003; early unknown.',
        4: 'Opening2023EnglishOpen4–3vsMa known. Late Ma9centuries bounds him below250, and separate2023BritishOpen4–0vsLeclercq is not the required connected sequence. The4–3Allen/4–0Maflin in E109 belongs2012/13, not2023. Full ordered wins/loss and final opponent count unresolved.'},
        {1: ([21] if late else [], ['E119'] if late else []),
         2: ([3,15,21] if late else [], ['E109','E119'] if late else []),
         3: ([20] if late else [], ['E119'] if late else []),
         4: ([1,2,3,4,5,17,18,19] if late else [1], ['E107','E108','E109','E110','E117','E118'] if late else ['E107'])},
        strata=['mid_research','deferred_reactivation'] if late else ['early'],
        risks=['Do not join2013PTCsequence to2023EnglishOpen. Ding remains a candidate.', 'Undated career counts do not certify the specified cutoff.'])


for cid in ['F11', 'F12']:
    late = cid == 'F12'
    add(cid, [2,3,4,5] if late else [2,5], [2,3,4,5] if late else [2,5], {
        1: '1978birth is stated, but Goat compatibility is not established. Checking/reconciling zodiac or birth year remains a material frontier; do not declare full identity merely from the strong other clues.',
        2: 'Soldier father and military-hospital mother explicitly present.',
        3: 'Early: film appearance only; H also knows2005andMeirelles from biography, but no policeman or Iracema link. Late: exact Policeman1,2005,Meirelles and Iracema inspiration jointly established.',
        4: 'Early: FifthEstate appearance only, no2013thriller/director/Kinsey conjunction. Late: all required role-film-director links present. Exact OscarKamau role is optional; user did not demand that role name.',
        5: 'Peter King is the explicit popular-name relation for PeterKingNziokiMwania in all views. This literal alias is resolved; task-wide identification still blocked by R1 and any other missing clue.'},
        {1: ([1], ['E096']), 2: ([2], ['E096']),
         3: ([3,4,7,9] if late else [3], ['E096','E097','E100','E102'] if late else ['E096']),
         4: ([3,5,6,8] if late else [3], ['E097','E098','E099','E101'] if late else ['E096']),
         5: ([1], ['E096'])}, strata=['near_closure'] if late else ['early'],
        risks=['Unresolved birth-year/Goat consistency cannot be treated as satisfied; the prefix itself contains no zodiac calendar.'])

for cid in ['F09', 'F10', 'F24']:
    late, direct = cid == 'F10', cid == 'F24'
    covered = [1,3,4] if late else [1,3,5] if direct else []
    add(cid, covered, covered, {
        1: 'All have death66; activist is absent from early F09 and present in late F10/F24.',
        2: '67career albums present. First recording1975, performing1977 and firstalbum following a successful single are not an explicitly dated first-album release in the1970s. That remaining scope can be investigated; reasking lifetime67alone is stale.',
        3: 'F10/F24 Wasakara2001, interpreted as referring to then-president Mugabe, materially matches the protest-song clue. Early F09 source excerpt lacks it.',
        4: 'Only F10 C15/E094 explicitly bind the why-sing/why-art quote to2015. F09/F24 contain a different2016career quote and2015legacy quote, not the requested one.',
        5: 'F24 C7/E183 directly bind65albums to the May1,2017ForbesAfrica feature. F09 retrospective67+separate2016interview does not. F10 secondary2017list gives65and mentionsForbesMay2017 but Claims separate these; strict date-attribution remains unresolved. Count/secondary-context sensitivity must not silently replace this relation.'},
        {1: ([1,5] if late else [1,3] if direct else [1], ['E087','E089'] if late or direct else ['E087']),
         2: ([3,9,10] if late else [4,5,8,9] if direct else [2,3], ['E088','E089','E091'] if late else ['E088','E089','E093'] if direct else ['E088']),
         3: ([13] if late else [6] if direct else [], ['E093'] if late or direct else []),
         4: ([15,16] if late else [], ['E094'] if late else ['E088']),
         5: ([11,12] if late else [7] if direct else [3,4], ['E092'] if late else ['E183'] if direct else ['E088'])},
        strata=['near_closure'] if late or direct else ['early'],
        risks=['No lifetime-count/feature-date join. First-recording date is not first-album date.'])
    if direct:
        LABELS[cid]['predeclared_closure_sensitivity'] = {
            'name': 'discriminative_identity_plus_direct_requested_relation',
            'S': True, 'H': True, 'SH': True,
            'reason': 'Matches historical v2 primary policy: multiple discriminative identity facts plus direct dated Forbes answer. New F1 primary retains all-material-question coverage; this sensitivity makes F24 STOP acceptable without changing requirement labels.'}


for cid in ['F19', 'F20']:
    late = cid == 'F20'
    add(cid, [3] if late else [], [3] if late else [], {
        1: 'Neither view establishes discord-origin history for a team in a qualifying fixture. Club-history discrimination or a new candidate is legitimate.',
        2: 'No team-identity-iteration history is established for the opposing club.',
        3: 'F20 C23/24 and E182 establish Arsenal early4/Newcastle later4 in2011; C17/18/E176 also establish Milan early3/Liverpool later3. Neither is fully qualified by origin/free-kick clues. Early S lacks timing; early H E163 already has PSG both opening scoring and late equaliser, counterevidence to the PSG timing hypothesis.',
        4: 'Messi95minutePSG fact is known in both. It does not identify the question’s fixture. F20 multiple95minute candidates do not establish a95minute free kick in Newcastle–Arsenal. Riise at end of extra time is not95minutes. A conditional whether/who check is legitimate; declaring an unverified candidate fixture established is not.'},
        {1: ([], []), 2: ([], []),
         3: ([6,7,17,18,23,24] if late else [], ['E163','E168','E176','E182'] if late else ['E163']),
         4: ([1,2,4,14,21,22] if late else [1], ['E163','E164','E173','E178'] if late else ['E163'])},
        strata=['candidate_pivot','mid_research'] if late else ['early','candidate_contradiction_in_history'],
        risks=['A95minute event alone cannot promote a fixture.',
               'F19 H/SH have scoring-order counterevidence omitted from S; F20 Newcastle hypothesis only has timing support.'])


for cid in ['F01', 'F02']:
    late = cid == 'F02'
    add(cid, [2] if late else [], [2] if late else [], {
        1: 'No2011–2016table with the required tied-points pairs/rank/goal-difference conjunction.2023/24United8th with negativeGD and transfer lists are not it.',
        2: 'Early only Enugu location; whether the question means national or regional capital remains a useful clarification/check. Late BFCBerlin is explicitly listed as a German-capital club; this local property is supported, not overall BFCidentity. Other London/Bern alternatives are also known capital clubs.',
        3: 'No dated1973–83league win for Rangers or late BFC hypothesis. History lists alternatives (Hapoel1981, Wolves1976/77seconddivision), not a verified same-club conjunction. League Cup is not league championship; do not import external BFCtitles.',
        4: 'Rangers13signings ahead2022/23 present; fifteen-trophy and2023article conjunction absent. E001 timestamp2025does not certify2023report.',
        5: 'Founding facts for incidental Canberra/Leicester/Notts clubs do not settle Rangers or BFC identification. Conditional candidate founding research is allowed; full target identity remains unknown.'},
        {1: ([4,38] if late else [], ['E007','E028'] if late else []),
         2: ([1,10,11,18] if late else [1], ['E001','E011','E016','E021'] if late else ['E001']),
         3: ([35,36,37,46,47] if late else [], ['E026','E027','E032'] if late else ['E001']),
         4: ([1], ['E001']), 5: ([12,13,41,53] if late else [], ['E013','E029','E035'] if late else [])},
        strata=['mid_research','candidate_pivot'] if late else ['early'],
        risks=['BFC is promoted only from capital-city relevance, not the complete question.',
               'Known facts about distinct clubs cannot be joined into one candidate’s requirements.'])


for cid in ['F05', 'F06', 'F22']:
    late = cid == 'F06'
    add(cid, [1,4,7] if late else [], [1,4,7] if late else [], {
        1: 'Hijitus has three writers, conflicting with two. Late Cococinel explicitly has Raymond Burlet and two named writers in C39/E076.',
        2: 'Hijitus dates conflict. Late C27/28 and E069 give Jan–Dec1992/52, but C35/E073 give1992–1996/78. E076 distinguishes first52/second26, without binding the full end-date clue. Reconciling season versus full-run scope remains valid; simply reasking the stated first52 count is stale.',
        3: 'Late State says4–10min. History additionally gives4min in E072. Positive short-runtime evidence exists but the contradictory range needs scope resolution; neither unqualified all-episodes claim is established.',
        4: 'Late TF1 is explicit; initial Canal13 does not match the three-character clue.',
        5: 'Late France/Belgium origin is explicit but the WorldCup-country conjunction is not. No external sports facts are imported.',
        6: 'Late E073 explicitly says teaching nature/protection; omitted from Claims. Specific twins/poet/complainer/living transport conjunction is absent from both views. A Need solely for educational purpose is stale in H/SH and positive subrelation reactivation in S.',
        7: 'Late C31/38/E071/E076 directly establish Argentine title Cocomiel for Cococinel; reasking only this alias is stale. Overall identification remains provisional because other material clues are unresolved.'},
        {1: ([39] if late else [1], ['E076'] if late else ['E047']),
         2: ([27,28,35,37] if late else [2], ['E069','E073','E074','E076'] if late else ['E047']),
         3: ([28] if late else [], ['E069','E072'] if late else ['E047']),
         4: ([34,37] if late else [], ['E073','E074'] if late else ['E047']),
         5: ([32,34] if late else [], ['E072','E073'] if late else []),
         6: ([], ['E073'] if late else []),
         7: ([31,38] if late else [], ['E071','E076'] if late else [])},
        strata=['mid_research','scope_conflict','deferred_subrelation'] if late else ['candidate_contradiction','early'],
        risks=['Do not treat Hijitus as the target after explicit writer/date conflicts.', 'Known Cocomiel title does not establish all identifying conditions.'])

for cid in ['F17', 'F18', 'F21']:
    late = cid == 'F18'
    add(cid, [], [], {
        1: 'Heart wealthy-family story is2021 and does not establish personal wealth mainly from showbiz in2022. Late incidental celebrity/business snippets do not bind all clues to Dolapo.',
        2: 'Heart age13/23years before2021 points to1998, conflicting with2006–10break. Late Dolapo US-born child is explicit, but family-of-three, industry breakthrough and2021account remain absent. Do not transfer eLDee singer occupation to his wife.',
        3: 'No candidate-specific2020article/university-entry-year/BBA conjunction. Incidental Belmont alumni, MBAs and Guldner BBA do not establish that relation for Dolapo.',
        4: 'No same-candidate2010–15debut plus coordinator2012→manager2020article. Many unrelated promotion/single facts are distractors, not one joined career.',
        5: 'No birth-name relation for a jointly supported candidate. Eminem/Soulja names are incidental. A conditional test of Dolapo is possible; assuming Dolapo established is unsupported.'},
        {1: ([1,2], ['E126']), 2: ([1,2,47,48] if late else [1,2], ['E126','E156'] if late else ['E126']),
         3: ([4,5,21,22,38,52] if late else [], ['E131','E141','E150','E158'] if late else []),
         4: ([7,11,28,31,32,43,44,57] if late else [], ['E132','E135','E144','E146','E153','E162'] if late else []),
         5: ([3,6] if late else [], ['E130','E132'] if late else [])},
        strata=['candidate_pivot','mid_research'] if late else ['candidate_contradiction','early'],
        risks=['Heart is contradicted on career dates; family wealth is not fraction of own wealth.', 'Dolapo only has the US-born-child subclue; spouse biography must not be transferred.'])


def main():
    assert set(LABELS) == set(PACKETS) and len(LABELS) == 24
    (TOP / 'bank/COVERAGE.json').write_text(json.dumps(LABELS, ensure_ascii=False, indent=2) + '\n')
    print('coverage labels', len(LABELS))


if __name__ == '__main__':
    main()
