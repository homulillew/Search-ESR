# Frozen evidence and failure rubric

Single reviewer inspects raw observed text, prefix and frozen Need. Exact
support/refutation must bind the right entity, relation and temporal scope.
Unrelated candidate facts, a title, incomplete list and one of two requested
conjuncts are insufficient. Combine returned evidence with prefix evidence;
do not combine observations from different arms. Dates/counts require their
specified cutoff. Source truth is corpus-relative, not a new web fact check.

Examples: one offline player does not exclude multiplayer; a company's
collaborators do not establish a game's complete credits; a season-4 episode
does not establish the total seasons. One correct counterexample can refute a
compound condition. Future/corpus exact spans are permitted for offline outcome
review only and never count as Actor-visible evidence without an actual window.

Each action: raw query, scope (global/local/adjacent), repeated exact query,
same-document rediscovery, pre-frozen entity/relation regex presence, correct
source hit, exact window, returned evidence budget. New unannotated sources
are adjudicated from their actual raw text/full-document audit when necessary.
Matching a gold span is sufficient, not necessary; valid alternative sources
receive the same semantic test. Record all judgments and excerpts/offsets.

Failure labels (multi-label; separate API/control failures): S1 global failure
despite a known exact source; S2 local source lacks relation; S3 two failed local
inspections in the same wrong source with no global fallback; S4 global fails to
return an exact source; S5 exact source returned but exact relation not visible;
S6 correct-document Find selects wrong occurrence/section; S7 adjacent-context
miss when an already relevant passage lacks nearby required continuation;
S8 STOP before evidence. A failed Find on a correct but hard document is S6,
not S3. Mere absence from a snippet cannot establish source-level S2/S4.

Primary success denominator includes failures and stops. Action-1 success,
action-2 recovery, first known-source use (direct Find/Open; global rediscovery
reported separately), cost and source-hit/window-miss are secondary. Source hit
includes known audited exact sources and independently verified alternatives.
Do not use S/F/O count or regex quality as the primary outcome.
