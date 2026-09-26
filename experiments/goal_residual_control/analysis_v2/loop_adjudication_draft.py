"""Record adjudication only through reviewed round 1; final round needs review."""
from progress import *
b=TOP/'three_round_loop_v2';cells=read(b/'checkpoint.json');out={}
reasons={
 '546':'The committed Claims do not establish the complete same-tournament 2023 decider → 4–3 → 4–0 → loss sequence plus all date-scoped player/opponent conditions.',
 '1094':'Real free-kick events and club-history fragments remain unjoined to one fixture satisfying the early/late scoring and origin conjunction.',
 '517':'Film-role/director facts do not establish or reconcile the requested Goat zodiac condition with the incumbent 25 May 1978 birth claim. Goal Reviewer closure is not independent truth.',
 '435':'Stored 65-album and May-2017-list statements lack the exact feature-time count binding. Retrospective 67 must not supply that relation. Source reconstruction can recover a count relation separately.',
 '580':'Five seasons is visible in initial Workspace W3 but never committed into Claims. Primary closure stays open under the frozen Claims-only rule; source-visible closure already holds at seed.',
 '177':'The founding answer alone, even with 13 signings and an older league title, does not establish the requested league-table/points/trophies identification.',
 '1034':'No single person is supported across commercial-model wealth, three-child family, career break, US-born child, education, musical debut, employment history and birth name.',
 '311':'Neither the provisional programs nor true miscellaneous cartoon facts establish the complete required program and Argentinian release name.',
 '186':'After round 0, former Night Sky company history and explicit Albino Frog developer attribution join the seed release/credit facts. Conflicting reported 1992/1993 release years both remain early-1990s; neither erases the seed November datum.',
 '387':'The storage fact and generic Jazz 2 animator/1998 relation do not establish the specific intro/end animation credit and Game A/company/time linkage.'}
for k,c in cells.items():
 r=0 if k in ['186:L0','186:L1'] else None
 source=-1 if c['qid']=='580' else 0 if k in ['435:L0','435:L2'] else r
 reason=reasons[c['qid']]
 if k=='186:L2':reason='Actor failed at first decision; developer/former-name facts were never acquired in this cell.'
 if k=='435:L1':reason='Actor failed at first decision; the date-specific requested album count remains unsupported.'
 out[k]={'reviewed_through_round':1,'resolved_after_round':r,'strict_resolved_after_round':r,'source_only_resolved_after_round':source,'goal_drift_rounds':[],'reason':reason}
write(b/'LOOP_ADJUDICATION_DRAFT.json',out)
