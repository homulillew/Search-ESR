# F3 single-Gap short rollout results

Six distinct qids were paired under unchanged Orthogonal Search/Find/Open
semantics and `deepseek-flash`. Four decisions were allowed per arm. The trace
has 12 starts and 12 terminal records, 70 real retrievals, 147 W reads, 25
Verifier calls and 146 completed Gap Reviews. `177:R0` was interrupted after
one Gap Review request; that request has no response, was not repeated, and the
cell is retained as a failure. No other call failed. Every W has a separate
single-reviewer label in `REVIEWS.json`.

| Metric | R0 natural | R1 minimal loop |
| --- | ---: | ---: |
| True Gap closure by committed Claims | 1/6 | 1/6 |
| Evidence sufficient in Workspace, whether committed or not | 3/6 | 4/6 |
| Useful new W / retrieval action | 6/32 (18.8%) | 10/38 (26.3%) |
| Retrievals yielding at least one useful W | 4/32 (12.5%) | 6/38 (15.8%) |
| Supported new Claims / all new Claims | 5/6 (83.3%) | 11/12 (91.7%) |
| Model-declared closure | 3/6 | 3/6 |
| Premature closure | 2/6 | 2/6 |
| New Claims / case | 1.0 | 2.0 |
| Retrievals with no new W handle | 6/32 | 12/38 |
| Search / Find / Open | 21 / 8 / 3 | 24 / 14 / 0 |

After a no-useful-evidence decision, the first action of the next decision
was still Search in 4/7 R0 and 4/6 R1 transitions. This is descriptive;
another Search can be appropriate when no suitable document exists. It did
not establish the Ding match sequence or the PSG–Lille club-history pair in
this sample. R1 made more Find calls, but its extra Find did not translate to
more true Gap closure.

The full-sample paired direction rule (true closure first, then useful-action
rate) yields four R1 wins, one R0 win, one tie: net +3. Excluding the
interrupted `177` pair yields net +2. The threshold of +3 was frozen, but
this exact tie-break formula was operationalized during analysis, after some
outcomes were visible. Treat it as descriptive. The other two frozen gates
fail: R1 Claim precision is below 95%, and premature close is 2/6 cases
(2/3 of model-declared closes), above 10%. **F3 fails.**

Mechanism cases:

- `546`: both arms repeatedly retrieved adjacent snooker material; neither
  established Ding's ordered later match sequence. R1 chose more focused
  queries and more Find, without useful W.
- `1094`: R1 obtained a supported W about PSG's 1972 split from Paris FC,
  but that local fact does not establish both historical club clues. R0
  drifted to unrelated football history. Both left the Gap open.
- `517`: both arms found byte-identical filmography W text with “Policeman
  1.” R0's Verifier admitted a Peter King Claim; R1's rejected it because
  the isolated W lacks his name. Under the strict one-W rubric, R0's Claim
  overbinds identity, so its declared closure is premature. With known-D
  context allowed as evidence, R0's Claim could be accepted; this sensitivity
  still gives no R1 resolution advantage.
- `435`: both arms found May 2017 Forbes-related material and closed before
  the exact Forbes Africa article was read. R1 later saw the May 2017
  Forbes Africa article containing “65 albums” but extracted no Finding from
  that W. The Search result URL established the publisher, but the Reader's
  isolated W input omitted that URL. It also committed “67 albums at the 2016 interview” from a W that
  retrospectively says “67 albums later” and separately quotes a 2016
  interview; the temporal binding is unsupported. This is a dynamic
  Verifier false promotion missed by the curated F2 bank.
- `580`: both arms formed sufficient season-one and season-three Claims and
  correctly closed the Gap. R0 did so in one Actor decision; R1 took two
  and repeated an already visible W before extracting its useful season-one
  fact. R1 also committed a true but unnecessary season-count Claim.
- `177`: R1 found a 2014 league table with three equal-points pairs and
  Enugu Rangers in eighth place on 58 points with goal difference 8. The W
  text contained the rows, while the Search result title carried “2014”;
  Reader committed the rows but not the year. Gap Reviewer closed despite
  the missing temporal Claim. R0 was interrupted after irrelevant Search.

The observed difference is best described as more useful *raw* evidence in
R1, with failures at extraction, one-W verification and closure calibration.
It is not a successful persistent State loop.

## Execution and inference limits

The two full v3a prefixes and four exact legacy W snapshots were paired
within qid, but R0 saw a historical chat prefix while R1 saw a compact view.
This changes context presentation as well as State; the six-case contrast is
not a pure single-token intervention. The legacy checkpoint wrapper remapped
exact corpus slices to D1/W1, without changing source text. The reviewer saw
live progress before arm-masked packet scoring, so masking was incomplete.

The frozen runner allowed multiple tool calls in one Actor response. It
executed 11 queued retrievals after a first `resolved` verdict (R0: 4, R1:
7) before stopping at the decision boundary. Those actions remain in the
reported denominators; true closure is judged at the first verdict. Thus
the run exceeded the intended immediate-stop behavior. Every preselected
call and its result remains in the trace. This, and the one interrupted
baseline, further limit causal claims. No replacement rollout was run.

DeepSeek reported prompt-cache hit rates of 86.6% for Actor tokens, 35.8%
for Reader, 0% for Verifier and 50.8% for Gap Reviewer. The audit confirms
Reader/Verifier inputs contained no query rationale or review labels.
