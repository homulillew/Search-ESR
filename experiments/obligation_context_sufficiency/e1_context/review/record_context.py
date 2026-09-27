"""Explicit second-pass context provenance judgments; no changes to primary labels."""
from experiments.obligation_context_sufficiency.common import *
from experiments.obligation_context_sufficiency.run import OUT,load_rows
import subprocess
assert subprocess.check_output(['git','show','HEAD:'+rel(OUT/'review/FIRST_PASS.json')],cwd=ROOT)==(OUT/'review/FIRST_PASS.json').read_bytes()
notes={
 'G02':'The path query does not assign the two author roles to one/different people. Raw W10 gives a paper/author profile, but C2 outputs do not promote its title or coauthor as facts. Role merging/splitting is a Q-projection error, not demonstrated new-context content uptake.',
 'G03':'Table2/Happiness/paper identity already appear in C. Checking total tables does not promote data-in-five to total-five, and no raw-only fact enters the obligation.',
 'G05':'The generic query names no donor. Raw W4 concerns Ding and W5 Gates, neither is promoted by C2 outputs. Kwon/gift/childlessness hardening also occurs in C0; it cannot be assigned to those raw biographies.',
 'G06':'Retained path contains only Writer window references and C deltas. Ding is already in C, but the gift relation is not; primary candidate hardening has no query/observation provenance here.',
 'G08':'The path explicitly queried SOPHIE+partner interview+song reference while C only establishes death. Four path-arm outputs promote that unverified candidate-interview binding; raw W9/W10 are unrelated artist text and supply none of the asserted binding. Similar hardening occurs in CDELTA, so origin is not causally identified.',
 'G09':'C3 supplies the immaterial-girl quote. Most outputs discover its song referent without new context facts. C2 R1 instead asserts the stronger song-reference utterance matching the query direction; the same error occurs in C0 R1. Raw observations concern other artists and are not used as factual premises.',
 'G11':'Query is a generic question-derived direction, without Marwaha. Raw Prabhu/Devi biographies are not used. Later-article presupposition occurs also in C0/CDELTA and has no specific new context fact provenance.',
 'G12':'Outputs use Q/C academic profiles, not raw unrelated thesis rows or Ganita Bharati journal metadata. No context-created requirement.',
 'G14':'C supplies Euler birth but not a book citation. C1 R2 fixes him into the book-reference role present in the previous query; C0 R2 and CDELTA R2 do the same without that query. Raw W9/W10 and other query candidates (Ericsson/Huygens/wine/olive oil) are not promoted.',
 'G17':'C2 raw text names FOP and concrete cases, but outputs do not assert those raw-only names or case facts. They still request an unbound final diagnosis; this is the same dependency error seen without context.',
 'G18':'C7/C9 already establish the clinical case identities. Year/country objectives use these claims, not the raw CNO or House-fiction text. No raw-only diagnosis promoted.',
 'G20':'EU4 is in C; other games/authors in raw bibliography are not substituted or asserted. DLC profile remains from Q.',
 'G21':'Raw designer names already admitted in C8/C9; C2 shifts to the Q-required advisor profile. C1 stale nation request is a Q/C state-use issue, not new raw evidence promotion.',
 'G23':'The query includes University of Melbourne, absent from C; no path-arm output fixes Melbourne as host or team university. All ask the host of the C-established ICPC event. Raw IOI details are not promoted.',
 'G24':'No current need is invented from raw Kazakhstan/2024 material. All outputs test the two known teammates countries, without asserting a country from the raw text.',
 'G26':'No Search/Find/Open remains in path and raw is empty. C1 date-attachment error comes from the covering-memo claim, not from additional context facts.',
 'G27':'Raw letter text supplies region content already in C3; outputs ask final-courier identity/nickname, not raw-only claims. The C0 initial-handoff role substitution and Roosevelt insertion have no context source.'}
flags={
 'C1__G08__R1':('SOPHIE musician died Athens Greece partner interview song reference','recent_events[2].argument.query'),
 'C1__G08__R2':('SOPHIE musician died Athens Greece partner interview song reference','recent_events[2].argument.query'),
 'C2__G08__R1':('SOPHIE musician died Athens Greece partner interview song reference','recent_events[2].argument.query'),
 'C2__G08__R2':('SOPHIE musician died Athens Greece partner interview song reference','recent_events[2].argument.query'),
 'C2__G09__R1':('SOPHIE musician died Athens Greece partner interview song reference','recent_events[0].argument.query'),
 'C1__G14__R2':('book illustrations telephone telegraph John Ericsson Christiaan Huygens Leonhard Euler rust wine olive oil','recent_events[1].argument.query')}
review=[]
for r in load_rows():
 ctx=input_for(bank()[r['case_id']],r['arm'])['Recent Context'];flag=r['id'] in flags
 row={k:r[k] for k in ('id','case_id','arm','replicate')}
 if not r['valid_output']:reason='No final obligation: context uptake unassessable; no observed promotion credited.'
 elif not any(ctx.values()):reason='All Recent Context arrays empty. This response cannot demonstrate uptake of additional context.'
 elif r['arm']=='CDELTA':reason='Delta repeats only exact current Verified Claims. No additional unverified path/observation content is present. '+notes[r['case_id']]
 else:reason=notes[r['case_id']]
 row.update(path_fact_promotion=flag,path_created_requirement=False,path_candidate_hardening=flag,observation_overreach=False,
  reason=reason,assessable=r['valid_output'],context_present=any(ctx.values()),observations_present=bool(ctx['recent_observations']),
  context_exclusive_new_fact_observed=False,causal_attribution='not identified',ambiguity='medium' if flag else 'low')
 if flag:
  query,where=flags[r['id']];assert any(e.get('argument',{}).get('query')==query for e in ctx['recent_events'])
  row.update(provenance={'path_field':where,'query':query},
   interpretation='Observable unsupported binding matches the prior query. This tag is content-compatible promotion, not proof that context caused it; the name was already in C and related errors occur without path. No raw-only fact is asserted.')
 review.append(row)
write(OUT/'review/CONTEXT_REVIEW.json',review)
write(OUT/'review/CONTEXT_ATTESTATION.json',{'first_pass_commit':'3834417d56e031b99808d0ab149b0b9295045d8c','first_pass_sha256':sha(OUT/'review/FIRST_PASS.json'),
 'method':'Read all17 eligible path cards, all15 raw observation cards and all related outputs; initial empty cards and delta-only projections checked separately. Four required boolean tags transcribed explicitly; first-pass labels unchanged.',
 'attribution_limit':'Six flags concern unsupported bindings also represented in a past query, not context-exclusive factual content. The same or analogous errors occur without the query. Do not report six causal contamination effects or claim raw-text overreach merely from a scope error.',
 'raw_observation_overreach':'No demonstrated raw-only factual premise uptake in final obligations; this does not establish absence in hidden reasoning.'})
