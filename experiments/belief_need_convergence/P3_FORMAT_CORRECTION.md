# Separate technical correction — not a replacement of Round 0

Observed after first requests: DeepSeek HTTP400 says JSON mode requires the word
`json` in the prompt. P3A had a JSON example but omitted that literal word.
This is an experiment implementation error, not a model coverage failure.

Preserve every original P3 request/rejection and its attempted denominator.
A new separately frozen batch changes exactly `Return only {` to
`Return only one JSON object {`. All 55 P3 Beliefs, model parameters, samples,
P3B prompt and two-call dependencies remain fixed. Maximum 110 new calls.
No corrected request has been sent before this note/manifest commit.

This is a new protocol version and a disclosed exception to the initial single
attempt plan for API-rejected P3 cells. It is not an SDK retry or a semantic
failure resample. Report original intention-to-run P3 and the corrected technical
cohort separately; never merge the two to hide the original 400s. Semantic or
other failures in the corrected batch remain terminal. The P0/P1/P2/P4 calls
are not resampled. Do not count a structural-only correction as a successful
mechanism intervention.
