"""Single-reviewer prefix-only gold; written before replay calls, no new outputs read."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
B=read(TOP/'admission_replay/PREFIX_REVIEW_PACKETS.json')
# Each entry: novel useful atoms, hypothesis expectation, pre-call reasoning.
A={
0:([], 'keep', 'The 1982 league-success condition is already committed. Later 2024 eighth title and ambiguous five wins do not establish the 2023 fifteen-trophy total; no novel decisive relation.'),
1:([], 'keep', 'A gaming challenge gives a long non-discriminative capital-club list without the distinctive signing/trophy conjunction. Replacing Rangers with BFC on this alone is weak promotion.'),
2:([], 'keep', '2025 youth-academy usage is unrelated to the 2011–16 standings and 2023 signing/trophy relation.'),
3:(['Rangers won the Nigeria Premier League in 1982 (the 2016 win is described as its first since 1982).','Rangers won the 1974 double including the cup final.'], 'keep', 'These dated honours establish a previously uncommitted historical-success clue. They do not settle the fifteen-trophy/standings conjunction. Other late honours are incidental.'),
4:([], 'keep', 'Hapoel honours do not test current BFC/Rangers path or distinctive conjunction; no basis for replacing or clearing BFC.'),
5:(['Rangers International Football Club was founded in 1970.','Rangers International Football Club is a Nigerian football club.'], 'keep', 'Direct requested final founding relation for a still-provisional candidate; do not promote full identification.'),
6:(["PlayDOSGames lists Galacta release year as 1993, conflicting with the committed November 1992 date.",'PlayDOSGames credits Sean Puckett as Galacta developer (Albino Frog as publisher).'], 'keep_conflict', 'New source-specific timing and developer-role counterevidence matters. Conflicting catalogue year alone does not conclusively reject a candidate matching other clues.'),
7:([], 'keep', 'Winkysoft history is unrelated to the observed Albino Frog/Galacta candidate and renamed-company requirement.'),
8:([], 'keep', 'Same unrelated Winkysoft window; novelty of its facts does not give control value.'),
9:([], 'keep', 'Shareware already known; proposed unmade episodes, gameplay and later v1.1 files do not establish original release or company rename. Tentative freeware note is not an original-release contradiction.'),
10:(["MyAbandonware lists Galacta as published in 1992 on DOS by Albino Frog, counterevidence to the committed PlayDOSGames 1993 listing."], 'keep_conflict', 'Already-known 1992 becomes useful only with source attribution in the existing release-date dispute; bare repeat is duplicate. Genre/comments are incidental.'),
11:(['Galacta: The Battle for Saturn was developed by Albino Frog Software, Inc.'], 'keep', 'Developer company binding is missing; company rename/establishment and single-player/DOS details already present. Single employee is not three credited contributors.'),
12:(["AlloCine lists Cococinel runtime as 4 minutes (not the prior 4–10 range).",'AlloCine lists Cococinel nationalities as France and Belgium.'], 'keep_conflict', 'Runtime directly tests less-than-five; co-nationalities bear on origin without asserting sole origin. 52 episodes and one season are duplicates. Neither identifies required character conjunction.'),
13:([], 'clear_prior_contradiction', 'Current song window supplies no useful atom. Existing Claims already explicitly disqualify Hijitus timing/writers; clearing that retained hypothesis is warranted, but cannot attribute the contradiction to this Observation.'),
14:([], 'keep_none', 'Hijitus was already rejected on timing/writers. Another incompatible timing account and Ferré biography add no needed discriminator; must not reintroduce Hijitus.'),
15:([], 'keep', 'Fragmentary Musketeers/Aladdin synopses do not bind dates, short runtime, educational role or network. One transport-like character is too weak for a new persistent candidate.'),
16:(['Serializd gives Cococinel premiere January 1, 1992 and last airing December 23, 1992.','Serializd lists Cococinel as one season with 52 episodes.','Serializd lists Cococinel runtime as 4–10 minutes.'], 'optional_set_Cococinel', 'Conjunction of dates/episode count makes a plausible provisional direction; preserve range, do not turn it into under-five. Synopsis mentions second season despite one-season field: record source-specific scope; no final identity.'),
17:([], 'keep', 'Disney early-series table does not match the specified one-year run/short episodes/network and supplies no justified new candidate.'),
}

A.update({
18:([], 'keep', 'Unrelated Dilworth biography does not test Dodrill, intro/end animation, PC storage or company chain.'),
19:(["Dean Noogy Dodrill was an animator for Jazz Jackrabbit 2.","Jazz Jackrabbit 2 was developed by Orange Games and Epic MegaGames.","Jazz Jackrabbit 2 is dated 1998."], 'keep', 'Useful partial animator/company/year links support candidate investigation, not specific intro/end credit or the missing Game A relation.'),
20:([], 'keep', 'Printing-software marketing/history has no connection to the animator or requested PC specification.'),
21:([], 'keep', 'Del/Sega concert account supplies no relation to the current game/company/animator identification.'),
22:([], 'keep', 'Chuck Jones biography is topical animation background, not evidence about the current candidate or PC.'),
23:([], 'keep', '2025 tablet artist interview does not establish the specified 2013 gaming-PC relation.'),
24:(["Afrikanza reports 65 albums for Oliver Mtukudzi in its entry discussing his inclusion in Forbes May 2017 richest-musicians release."], 'keep', 'Retain count and contemporaneous source/list context together. This is a secondary account, not a direct Forbes quotation; do not attach the retrospective 67 to 2016/2017.'),
25:([], 'keep', 'More-than-60 is already committed; song themes and son death do not resolve count at May feature or any unmet discriminative clue.'),
26:([], 'keep', 'This adjacent window concerns other musicians, not Mtukudzi. Same document and Forbes date do not permit transferring their facts.'),
27:([], 'keep', 'Career-total 67 is already adequately represented; established in late 1970s is not a first-album date and does not resolve the requested feature count.'),
28:(["The June 11, 2017 Afrikanza entry reports Mtukudzi had produced 65 albums while discussing his inclusion in Forbes May 2017 richest-musicians release."], 'keep', 'New relevant quantity/list context must retain source binding. Publication June is not an event date; no invented direct Forbes quotation.'),
29:([], 'keep', 'Exact Forbes May 2017 65-album relation is already committed. Biography, homemade guitar and gold record are not new requested relations; repetition need not mutate State.'),
})

A.update({
30:([], 'keep', 'Iracema plot/censorship background does not add the missing actor-role/director relation or zodiac resolution.'),
31:(["Bill Condon directed Kinsey.","Bill Condon wrote Kinsey screenplay."], 'keep', 'Both links directly establish the director clue; do not transfer them to The Fifth Estate without its own source.'),
32:([], 'keep', 'Both film roles are already committed. Other roles are incidental; no observation here resolves the Goat/birthday discrepancy.'),
33:(["Fernando Meirelles decided to become a filmmaker after seeing Iracema (1975)."], 'keep', 'Exact missing inspiration relation; movie inspiration date is not his birth or later film date.'),
34:([], 'keep', 'Iracema production/interview details are irrelevant to the remaining actor/director links, which require other evidence.'),
35:([], 'keep', 'The Crown cast window is unrelated; previous film links are now present but zodiac remains unresolved. No task identity promotion.'),
36:(["Ding Junhui made his fifth career 147 at the 2012/2013 Players Tour Championship Finals."], 'keep', 'Directly verifies a separate more-than-three maximum condition despite wrong year for the sequence. Must keep 2012/13; Allen/Maflin scores cannot establish the 2023 run.'),
37:([], 'keep', '2024 forum totals count first-round tournament centuries, not individual career centuries; no candidate relation.'),
38:(["Ding Junhui turned professional in 2003.","The observed Ding biography reports more than 600 career centuries."], 'keep', 'Pro year and century threshold were missing. Source does not date the 600/seven totals to January 30 2025; do not manufacture that cutoff. More-than-three maxima already supported by fifth-147 Claim.'),
39:([], 'keep', 'Ronnie records alone give no discriminating alternative to Ding or required sequence/opponent binding.'),
40:(["The official 147 list records Ding Junhui first maximum at the Saga Masters in 2007."], 'keep', 'A dated maximum event is a partial tally anchor for still-unestablished Ding career threshold; it does not establish more than three or justify switching current Mark Allen candidate.'),
41:([], 'keep', 'Current late-career matches do not establish the 2023 ordered run; recent Masters maximum and 2024 title already represented. No causal curse claim merits admission.'),
42:([], 'keep_none', 'Cast entries through season 5 give no upper bound on total seasons. The original five-season Workspace window is not this Observation and is not admissible evidence for this one-window replay.'),
})

A.update({
43:([], 'keep_none', 'Unrelated school-dropout profiles lack the discriminating BBA/coordinator/family conjunction. Cameron modelling/showbiz alone is not a durable new direction.'),
44:([], 'keep', 'A 2011 single alone matches a broad date clue but gives no connection to commercial model, family or coordinator career. Jun K replacement would be weak promotion.'),
45:([], 'keep', 'Pacific Crest staff degrees and jobs do not establish coordinator-2012 to manager/showbiz/model relation; incidental same-keyword evidence.'),
46:([], 'keep_none', 'Mothers managing celebrities do not establish the required individual and dated coordinator promotion; no supported replacement for rejected Heart.'),
47:([], 'keep', 'Staff-list BBA and business-manager facts do not connect to the current model candidate or distinctive coordinator history.'),
48:([], 'keep_none', 'DJ Blaze alias, early career and 2012 events do not bind the coordinator position, modelling, degree or family; a birth/stage-name fact about an unrelated entity is not the answer relation.'),
49:([], 'keep', 'PSG late equaliser/winner contradiction is already represented. Added 87th-minute detail is redundant to exclusion; this different fixture does not reject current Milan-final hypothesis.'),
50:([], 'clear_prior_contradiction', 'FUT game-clock discussion does not describe real-world match timing. Prior Claims already contradict the retained PSG/Messi fixture, so clear is warranted from prior evidence, not this source.'),
51:(["PSG led Lille 2–0, then trailed 2–3, and Mbappe scored a late equaliser before Messi late winner."], 'clear', 'New scoring progression materially contradicts all-goals-early versus all-goals-late split. Retain contradiction and clear this Messi/PSG hypothesis; preserve match binding.'),
52:(["PSG led Lille 2–0, then trailed 2–3, and Mbappe scored a late equaliser before Messi late winner."], 'clear', 'Same source independently in another pre-state: timing directly rejects current PSG–Lille fixture. Cannot reject an unrelated candidate.'),
53:([], 'keep', '1974 Liverpool–Newcastle final is outside the target period and is not current Newcastle–Stoke fixture. Unrelated match cannot clear that candidate.'),
54:([], 'keep', '1995 Intertoto and 2004 squad footnotes do not establish discord-origin or any specified 95th-minute fixture. No justified replacement of Mendoza with invented Wimbledon player.'),
})

def save():
 out=[]
 for i,(atoms,h,why) in sorted(A.items()):
  b=B[i];out.append({'packet_id':b['packet_id'],'qid':b['qid'],'prefix_sha256':digest(b),'atoms':[{'atom_id':f'A{i:02}_{j+1}','statement':s} for j,s in enumerate(atoms)],'hypothesis_expectation':h,'reason':why,'reviewer':'single Codex prefix-only','atom_scope':'new decision-relevant information; alternative phrasings allowed, all material qualifiers retained','no_new_claim_expected':not atoms})
 write(TOP/'admission_replay/GOLD_ADMISSION_ATOMS.json',out)
if __name__=='__main__':save()
