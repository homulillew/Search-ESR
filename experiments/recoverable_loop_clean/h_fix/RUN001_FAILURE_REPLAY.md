# run001 H failure replay — execution counterfactual only

Original run001 is immutable. Its 12/14 invalid-H proposal count and incomplete
recovery conclusion remain unchanged. These offline replays inject identical raw
response strings into the repaired engine. They do not repair outputs, rescore the
old model, or count as independent recovery evidence.

## Method

Replay every original slot through the terminal H failure, using archived tool
observations and role outputs in order. Read actual `*.response.body` files and
assert their final message.content bytes equal the trace's H raw string. Record
SHA-256 for both the full provider body and raw content. The provider body is never
rewritten; original reasoning/usage remain in historical logs.

After that slot, append one **scripted** Actor request_closure and a scripted
CONTINUE response. This proves a subsequent decision is executable and receives
retained state. A separate real-tool mock test demonstrates a materially changed
Find/localization route after repeated Search/NoGain.

Four R1 cases would skip H under the new production rule. For the explicit invalid-
output test only, override `_should_update_hypotheses` to True. No validator is
overridden. Separately replay those four cases under the production rule, without
consuming an H response. Keep both result sets distinct.

## Results

| Original trajectory | Failed slot | New C retained | Feedback | Injected H outcome | Next scripted Actor |
|---|---:|---|---|---|---|
| R1_Q1094__rep1 | 1 | none | NoGain | rejected atomically | reached |
| R1_Q1094__rep2 | 1 | none | NoGain | rejected atomically | reached |
| R1_Q546__rep1 | 1 | none | NoGain | rejected atomically | reached |
| R1_Q546__rep2 | 1 | none | NoGain | rejected atomically | reached |
| R2_Q228__rep1 | 2 | C3 | Gain | rejected atomically | reached |
| R2_Q228__rep2 | 1 | none | NoGain | rejected atomically | reached |
| R2_Q637__rep1 | 1 | C3 | Gain | rejected atomically | reached |
| R2_Q637__rep2 | 1 | C3 | Gain | rejected atomically | reached |
| R3_Q538__rep1 | 3 | C2 | Gain | rejected atomically | reached |
| R3_Q538__rep2 | 2 | none | NoGain | rejected atomically | reached |
| R3_Q922__rep1 | 2 | C3 | Gain | rejected atomically | reached |
| R3_Q922__rep2 | 2 | none | NoGain | rejected atomically | reached |

- **12/12** unchanged invalid outputs isolated, with H unchanged and raw hash in T.
- **5/5** original new grounded Claim commits retained, with original Gain.
- **12/12** next scripted Actors reached; **0** top-level H step failures.
- **4/4** production R1 runs skipped H and preserved NoGain; next Actor reached.
- Both q546 pending D17 opportunities survived. An independent valid-basis/old-D17
  nomination fixture specifically tests the source restriction rather than merely
  relying on the namespace failure that occurs first in the historical outputs.
- All original traces and all 16 new replay traces reconstruct their states exactly.
- **0** new paid requests or live retrieval calls.

## Key paths

**q228 rep1:** historical slot1 KEEP then slot2 Find D4/old W4 → Reader → supported
Grounding → C3 (Ding 2019 childlessness) → unchanged C3-in-basis H output rejected
→ Gain → next Actor. No evidence mapping, no C rollback.

**q922 rep1:** forced Closure → CONTINUE → Actor Open W4 → W6 → grounded C3
(North Transylvania) → unchanged invalid H output → Gain → next Actor. Closure
still receives only Q/R/C/supporting Evidence.

**R1:** the production path is repeated Search → no new W/C/D, no active H → skip
→ NoGain → Actor. Fault injection establishes that even an invalid old H response
cannot terminate that path. It does not show that the model will change its route.

Full provenance and per-trajectory outcomes:
[SUMMARY.json](offline_validation/run001/SUMMARY.json).
Each `fault_injection/<trajectory>/` and `production_skip/<trajectory>/` contains
its own RESULT.json and append-only trace.jsonl under the new h_fix directory.
