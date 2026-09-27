"""Explicit manual assessments after reading only masked VIEW_GROUPS.

No KEY, selection reference, historical GoldO, raw provider response, or
aggregate is read by this script. Identical visible choice/input gets the same
judgment; all108 response records are still authored separately.
"""
from experiments.recoverable_control_equivalence.common import P,read,write
R=P/'e1_selection/review'
# Manually reviewed alternatives actually present in each masked packet group.
notes={
 'V01':{
  'R1':(True,[], 'OPEN R1 pursues the artist/charity-name relation and the linked charity conditions as a concrete discovery objective; it does not assert that a candidate exists.'),
  'R2':(True,[], 'OPEN R2 targets the death/aviation-event geographic and temporal relation, a coherent event-identification objective. Unknown referents do not make discovery downstream extraction.'),
  'R3':(True,[], 'OPEN R3 seeks the partner interview and its artist/song statement, a source-linked relation that can identify unknown participants without extracting the final title prematurely.')},
 'V02':{'R1':(True,[], 'OPEN R1 is a bounded academic-career identity objective: the same author and university are linked by the2022 promotion and earlier degrees. Selecting it retains roles and dates.')},
 'V03':{
  'R2':(False,['coarse_nonlocal_node'],'OPEN R2 combines an unbound person birth-year/birthplace relation with a separate official town-population change calculation. No visible closure resolves either part; as a whole ID it is not one sufficiently local objective. This is a locality judgment, not a ban on unknown-entity discovery.'),
  'R3':(True,[], 'OPEN R3 can identify a person through one1990 presentation at a cultural center; it is a bounded event relation and does not jump straight to the year of death.')},
 'V04':{'R3':(False,['coarse_nonlocal_node'],'With every node OPEN, R3 bundles clinical case history with independent country/religion history. The selected whole node does not isolate one local research objective; no visible state indicates which part is already established.')},
 'V05':{'R2':(True,[], 'OPEN R2 is a coherent book-discovery objective using illustration count and telephone/telegraph contents of the same document; it avoids ungrounded title extraction.')},
 'V06':{'R3':(False,['coarse_nonlocal_node'],'Shared disorder/name are CLOSED, but R3 still visibly combines country/religion history and clinical history. The binary Mask does not identify which subcondition remains. On visible information alone, the whole R3 is not established as a single local residual objective; hidden Claims could change that judgment.')},
 'V07':{'R6':(True,[], 'Winning-team/year relations R2 and R5 are CLOSED. OPEN R6 asks for the host university associated with that winning year, a local remaining attribute; no need to finish every unrelated constraint before inspecting it.')},
 'V08':{
  'R2':(True,[], 'OPEN R2 concerns a single thesis/game/theme/year/university relation; a bounded verification target even though the precise missing component is not given.'),
  'R4':(True,[], 'The DLC relation is CLOSED in R1. OPEN R4 checks the linked gameplay changes for that DLC; the clauses describe one release feature set.')},
 'V09':{
  'R1':(True,[], 'OPEN R1 identifies or verifies one game/DLC release-time relation without extracting a designer before the DLC is grounded.'),
  'R2':(True,[], 'OPEN R2 can identify the thesis and its game relation by theme, year and university condition. An unknown thesis remains a legitimate research objective.'),
  'R3':(True,[], 'OPEN R3 permits discovery of the thesis advisor through one academic profile and linked monograph/degree history. The relation arguments remain intact; unknown identity is not by itself a reason to reject discovery.')},
 'V10':{'R3':(True,[], 'OPEN R3 identifies the coder from the ordered four-medal IOI history, a coherent individual/contest-record target; it preserves order instead of asking for a downstream host/year.')},
 'V11':{'R1':(True,[], 'The letter-region relationship and requested region are CLOSED, but OPEN R1 still contains letter identity/date/delivery conditions. Selecting that one letter/delivery event is legitimate remaining verification.')},
 'V12':{'R1':(False,['coarse_nonlocal_node'],'OPEN R1 packages company founder/game release/revenue history, a graduation relation, and a university founding interval. With no subcondition information these are multiple independent objectives inside one ID. The selection stays OPEN but fails the locality requirement.')},
 'V13':{
  'R3':(True,[], 'OPEN R3 targets a paper-author/Harran affiliation relationship, a valid way to identify or verify an unknown writer. It does not claim that a matching profile already belongs to the paper.'),
  'R5':(True,[], 'OPEN R5 seeks the distinctive13.53-percent emotion/table relationship in a paper, a local document-discovery/verification objective.')},
 'V14':{
  'R2':(True,[], 'The paper name, publication interval and distinctive table relation are CLOSED. OPEN R2 selects the bound paper-author/other-publication relation; it can be researched through authorship/publication records without rewriting nodes.'),
  'R3':(True,[], 'The paper identity is CLOSED. OPEN R3 checks its writer affiliation, a local relational verification objective.')},
 'V15':{'R1':(True,[], 'OPEN R1 identifies the letter/delivery event using rulers, period and courier nickname. These are linked attributes of one event; selecting it does not presume the letter or answer is already established.')},
 'V16':{'R1':(True,[], 'Article title/topic timing are CLOSED while the author-career condition remains OPEN. R1 remains a coherent profile verification objective and is not skipped just because the requested title is known.')},
 'V17':{'R4':(True,[], 'Winning team, coder record, year and host are CLOSED. OPEN R4 verifies the two teammates same-country relation; this is a local residual, not mere identity overlap.')},
 'V18':{'R3':(False,['coarse_nonlocal_node'],'Closing the second clinical case in R4 still does not expose the unresolved part of R3. R3 combines first-case clinical history and country/religion history; the visible binary state cannot establish that only one local subcondition remains. Hidden Claims are unavailable in this review.')}
}
def main():
 groups=read(R/'VIEW_GROUPS.json');judgments={}
 assert {g['group_id'] for g in groups}==set(notes)
 for group in groups:
  for response in group['responses']:
   rid=response['review_id'];selection=response['selection'];assert rid not in judgments
   if response['no_response']:
    assessment={'selection_appropriate_under_visible_mask':None,'error_codes':['no_response'],'reason':'No usable selection is present in this masked packet; no ID can be semantically reviewed and no output is repaired.'}
   else:
    assert isinstance(selection,dict) and set(selection)=={'selection'}
    value=selection['selection'];valid,codes,reason=notes[group['group_id']][value]
    assert group['input']['Control Mask'].get(value)=='OPEN'
    assessment={'selection_appropriate_under_visible_mask':valid,'error_codes':codes,'reason':reason}
   judgments[rid]={'visible_group':group['group_id'],**assessment}
 assert len(judgments)==108
 write(R/'MANUAL_GROUP_NOTES.json',notes);write(R/'JUDGMENTS.json',judgments)
 write(R/'FIRST_PASS_DISCLOSURE.md','''# First-pass review disclosure

One familiar Codex reviewer read all18 VIEW_GROUPS derived only from PACKETS.json. Grouping saves repeated reading, not independent observations. Each108 response has its own judgment. No new aggregate, key, frozen acceptable-ID reference or provider reasoning was opened during this first pass. Historical exposure and prior conversation memory persist; no independence or erased-memory claim.

The visible-state estimand can disagree with a frozen reference that uses hidden Claims to determine the residual of a coarse node. Such disagreement will be disclosed after commit, not resolved by changing Gold. Locality assessments for compound birth/census and clinical/country requirements are explicit in MANUAL_GROUP_NOTES.json.
''')
if __name__=='__main__':main()
