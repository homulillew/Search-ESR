# E1 Premise Checker — STOP

## Material Passport

22 frozen B0 candidate instances /12 states /7 qids;11 premise/referent errors plus11 H/No-H-matched valid controls. Each arm has two separately scheduled responses per candidate. Reference labels, prompts, schedule and code were committed at `ee6ab821a20d2f1a87c7149816373d8924cbf1b2` before requests. Historical experiments remain read-only.

Single Codex reviewer used QCH, the Candidate Need, frozen reference and returned JSON; no gold, future tools or hidden model reasoning. The output schema exposes the arm, so no arm-blind or independent-review claim is made. All88 review records were committed before aggregate scoring.

## Execution limitation: V0 unavailable

V0:44/44 HTTP400 rejections because the provider requires the literal `json` somewhere in JSON-mode prompt text. The exact task-supplied V0 text lacked it; our offline input contract check failed to catch that. No V0 verifier output exists. **Relative V1-versus-V0 efficacy is unmeasured.** Do not interpret planned-denominator zero success counts as V0 model accuracy. Full incident and offline correction: [FORMAT_INCIDENT.md](../analysis/FORMAT_INCIDENT.md).

V1:44/44 HTTP200 and parseable complete JSON;43/44 schema-valid. One response added an unrequested top-level `type` key; it was retained as schema-invalid, not stripped or retried. No out-of-inventory support refs occurred in the returned V1 objects; existing IDs still require semantic entailment review.

## V1 primary results

| Metric | Observed | Frozen gate |
|---|---:|---:|
| Invalid detection recall |16/22 =72.73%|≥85%|
| Valid-control specificity |10/22 =45.45%|≥85%|
| Balanced accuracy |59.09%|Relative comparator unavailable|
| Entire-response support binding correct |30/44 =68.18%|≥85%|
| Target/premise distinction |28/44 =63.64%|≥85%|
| Exact decision replicate agreement |16/22 =72.73%|≥80%|
| Complete schema-valid output |43/44 =97.73%|≥95% for each arm|

**All five absolute semantic/agreement thresholds fail independently of the missing V0 comparator.** No E2 repairs or E3 fresh calls are allowed. Even making the V0 comparison available would not rescue this V1 run.

Additional metrics: target identification43/44; subject interpretation/status27/44; exact three-way decision23/44. Binary replicate agreement18/22 =81.82%, but the preregistered gate uses exact three-way decisions. Required-background recall52/78 =66.67%; precision126/161 =78.26%; unsupported-background detection16/26 =61.54%. Binding-slot accuracy178/204 =87.25% is a micro diagnostic, not the response-level gate. A response with one wrong anchor fails the all-binding criterion.

First replicate detects6/11 invalids and preserves5/11 controls; second detects10/11 invalids and preserves5/11 controls. Temperature0 did not remove variation. No-H has only2 candidate instances/4 responses,3/4 binary correct; no broader No-H reliability claim is warranted. Per-qid and output-conditional metrics are in `../analysis/DIAGNOSTICS.json`. Same-QCH and identical-Need instances are not independent questions.

## Observed failure modes

Among43 schema-valid responses, errors can overlap: false premise21, subject error16, target/premise confusion15, wrong anchor13, missed premise8.

- The direct Kwon/spouse joint-donation and Sophie/partner interview tests are rejected because the checker demands the participant relationship first. Under the frozen scope, that participation is part of the existential target. It need not already be verified.
- Both DLC discovery controls are rejected because the DLC identity has not been found. The identity is precisely what those questions are asking to discover.
- Pakistan's religion/founding parameters and the company division in a release profile are treated as separately required proof, although the controls are direct tests of those unresolved conditions.
- Some outputs successfully distinguish the memorandum date from the letter date; another keeps the wrongly dated letter. Some infer a concrete source from only its Q description or miss the book by focusing solely on Euler.
- Correct keep decisions can coexist with bad audits: one monograph output treats the publication being tested as already supported by Q. Other audits unnecessarily require that a candidate already satisfy the whole original identity description.

Thus accurate restatement of the target (43/43 schema-valid outputs) does **not** imply a correct separation of target from required evidence. The main observed difficulty is rejecting legal targets or demanding excessive prerequisites, alongside missed source/date bindings.

## Ambiguity sensitivity

The preregistered sensitivity removes every medium/high reference-ambiguity instance:14 candidate instances/28 slots remain. Invalid recall is7/10 =70%; specificity8/18 =44.44%. Failure is not confined to the controversial report/accident/courier cases. Even granting all disputed support-binding judgments would not fix recall/specificity/agreement. No sensitivity is used to replace the frozen primary labels or open a gate.

## Cost and integrity

88 archived HTTP attempts;44 usage-bearing V1 responses,44 rejected V0 requests with usage unavailable. Reported partial totals: input46,184, completion248,746 including reasoning238,692, total294,930. V1 cache hit31,104 and miss15,080 give **67.35%** weighted hit rate. This is not a billing estimate for the unknown-usage rejected requests. Wall155.22s, peak concurrency8; zero retries and zero tools/Writer.

The provider-format incident limits the planned causal comparison. It does not erase the independently negative V1 absolute results. Both limitations and all failures remain archived. E1 ends here with no prompt revision.
