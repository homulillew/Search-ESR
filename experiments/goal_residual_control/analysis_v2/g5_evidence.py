"""Stage-local, reviewer-authored additions; never revise earlier stage labels."""
from progress import *

b=TOP/'three_round_loop_v2'
p=b/'evidence_labels.json'
labels=read(p) if p.exists() else read(TOP/'analysis_v2/EVIDENCE_LABELS.json')
defs=read(TOP/'analysis_v2/FACT_DEFINITIONS.json')
defs.update({
 'scienza_candidate':{'kind':'decision','belief_update':'Scienza scored a 95th-minute equalising free kick for Heidenheim.','next_decision':'Inspect this alternative fixture and club histories; timing alone does not identify the requested match.'},
 'brum_candidate':{'kind':'decision','belief_update':'Brum is a living car in an observed UK animation list covering 1990–2009.','next_decision':'Test this alternative against schedule, short runtime, other characters and Argentinian title; no full match is established.'},
 'ma_centuries':{'kind':'direct','belief_update':'The observed career table gives Ma Hailong nine centuries, including 2023/24 and 2024/25.','next_decision':'This bounds the earlier count below 250, but the rest of the tournament sequence remains unverified.'},
 'williams_centuries':{'kind':'decision','belief_update':'Williams has over 600 career centuries in the observed 2025 biography.','next_decision':'He remains a plausible high-century opponent; establish the as-of-2023 count rather than assuming a later total is contemporaneous.'}
})
def setlabel(eid,facts,reason):
 labels[eid]={'facts':facts,'reason':reason,'review_depth':'full returned window read by single reviewer; stage G5'}
setlabel('375f0180b700685c',['scienza_candidate'],'A named player plus the exact 95th-minute free-kick event supplies an inspectable alternative fixture, not a verified answer.')
setlabel('a49d7c4ada2c861a',['brum_candidate'],'Living transport and a period-bounded UK program list give a narrow new route; other identifying conditions still require inspection.')
setlabel('1598dabc87d4f2f6',['ma_centuries'],'Nine total centuries including later seasons implies fewer than 250 at the earlier event. It does not validate the whole sequence.')
setlabel('7195e954279140b4',['williams_centuries'],'Later career statistics motivate checking Williams as opponent; do not silently turn 2025 into 2023 support.')
setlabel('0ad82b18c7242532',['condon_kinsey','condon_estate'],'The observed biography explicitly links Condon to writing/directing Kinsey and directing the thriller The Fifth Estate.')
setlabel('9125a772d4d519e2',[],'The returned British Open section concerns Selby–Xiao and Williams–Vafaei; no new Ding sequence relation.')
setlabel('49c3c8e6b3b7a940',[],'One 2007 Ding maximum is not evidence for the required more-than-three threshold; unrelated table entries do not reduce the relevant uncertainty.')
setlabel('75323a8e2bcb2b56',[],'Milan–Liverpool names and a free kick at the end of extra time do not establish the 95th-minute clue or new early/late timing pattern.')
setlabel('2cbb4b1bf8261129',[],'The visible 71–84 minute commentary and 3–3 title do not supply the discriminating 95th-minute event or early/late pattern.')
setlabel('63651fd812183acc',[],'Quarxs appears as an educational creature premise but lacks the schedule/character combination needed for a supported alternative route here.')
write(p,labels);write(TOP/'analysis_v2/FACT_DEFINITIONS.json',defs)
