"""Single Codex offline semantic review of actual R1 windows; explicit per-window reasons."""
import json,hashlib
from pathlib import Path
TOP=Path(__file__).resolve().parents[1]
def dg(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
# D=direct active-need evidence; P=progress insufficient for omitted relation; N=no progress.
labels={
'DR01:G':[('N','Nature characters/magic-clover plot does not establish an educational intention.'),('N','Broadcast list and genre categories do not state educational purpose.'),('D','Explicitly says Cococinel familiarizes children with nature and the priority of protecting it.'),('N','Superhero/school-life synopsis has no educational-purpose assertion.'),('N','Romantic finale and Christmas plot do not establish pedagogical purpose.')],
'DR01:H':[],
'DR02:G':[('D','Section explicitly dates Jazz Jackrabbit2 to1998.'),('D','1998 games page lists Jazz Jackrabbit2 under May7; title supplies year context.'),('N','1999 table covers other games.'),('N','Epic list has Jazz2 developer but no release date in the visible row.'),('N','ZZT1991 supports another original-question requirement, not candidate GameB date.')],
'DR02:H':[('D','Section explicitly dates Jazz Jackrabbit2 to1998.'),('N','1998 critically acclaimed table contains other titles, not Jazz2.'),('N','1999 table contains other titles.'),('N','Catalog has original Jazz1994, not Jazz2 date.'),('N','Shareware history mentions first Jazz, not sequel date.')],
'DR03:G':[('D','AlloCine explicitly lists4min. Source-scoped support below5, without erasing conflicting ranges.'),('N','Education and named characters, no visible duration.'),('N','4–10minute range is already in initial Claims; does not newly establish below5.'),('D','After merchandise the same visible window explicitly states five-minute episodes and21-minute specials: source-scoped refutation of below5.'),('N','Argentine magazine discussion supports name/characters, not duration.')],
'DR03:H':[('D','French source explicitly states regular episodes5minutes and specials21minutes: grounded refutation of strict below5, NOT recovery of the original4minute fact.')],
'DR04:G':[('D','Seven total plus dated fourth2011/fifth2013/sixth2016 establishes>3 beforeJan2025.'),('D','Ding seven maximums with latest2024 establishes count by the cutoff.'),('N','Ronnie counts do not establish Ding count.'),('N','Official table excerpt covers early entries only; no Ding.'),('N','Tournament results and Robertson maximum do not establish Ding career threshold.')],
'DR04:H':[('D','Seven total plus dated fourth2011/fifth2013/sixth2016 establishes>3 beforeJan2025.')],
'DR05:G':[('D','Explicit total num_seasons5 establishes fewer than10.'),('N','Season3episode plot already known; no total bound.'),('N','Season1episode plot already known; no total bound.'),('N','Five final seasons refers to The Affair, a different program.'),('N','Embedded metadata for ranked shows has no target total season count.')],
'DR05:H':[('N','Cast spans up to season5 are a lower bound; no total-season upper bound.')],
'DR06:G':[('P','1992 listing corroborates existing semantic Claim; does not restore omitted conflicting1993.'),('P','November1992 corroborates existing date; no omitted conflict.'),('P','1992release and1993company founding are distinct relations, not themselves the omitted release-date conflict.'),('P','Version1.1dated1993 can help investigate version versus initial-release scope; not a conflicting initial-release assertion.'),('D','PlayDOSGames explicitly lists release year1993, conflicting with retained1992; preserve source binding.')],
'DR06:H':[('P','MobyGames confirms November1992 already committed; omitted1993conflict still absent.')],
'DR07:G':[('D','PC Gamer header July24,2013 and visible5TB/wireless specifications jointly establish availability byJuly25.'),('N','Razer products unrelated to this interview/date.'),('N','Dan Pinchbeck2016conference unrelated.'),('N','2023awards table unrelated.'),('N','Dean Takahashi/Cuphead essay is a different person/source.')],
'DR07:H':[('D','PC Gamer header July24,2013 and visible specifications establish availability byJuly25.')]
}
cs=json.load(open(TOP/'r1/post_tool_cells.json'));out={};mapping=[]
for key,ls in labels.items():
 c=cs[key];ws=c['decisions'][0]['tool']['observations'];assert len(ws)==len(ls),key
 for i,(w,(tag,reason)) in enumerate(zip(ws,ls)):
  rid=dg([c['case_id'],w['url'],w['text']])[:16];v={'sufficient_need_evidence':tag=='D','evidence_outcome':{'D':'direct_need_support','P':'decision_progress','N':'no_progress'}[tag], 'reason':reason,'polarity':'refutes' if (key=='DR03:H' or (key=='DR03:G' and i==3)) else 'supports' if tag=='D' else 'none', 'reviewer':'single Codex; arm visible in work log, no independence claim'}
  if rid in out:assert out[rid]['sufficient_need_evidence']==v['sufficient_need_evidence']
  else:out[rid]=v
  mapping.append({'cell':key,'index':i,'review_id':rid})
(TOP/'r1/EVIDENCE_LABELS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
(TOP/'r1/EVIDENCE_LABEL_MAP.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n')
print('reviewed',len(mapping),'windows,',len(out),'unique packets')
