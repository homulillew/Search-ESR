# Claim Pipeline Root-Cause Ablation — frozen preparation protocol

## Status and scope

E0 complete; E1/E2/E3 NOT RUN. TASK sections49–50 require a new user authorization
after these three preparation commits. Standing authorization is insufficient.
No API connectivity probe, retrieval or semantic dry run is part of preparation.
All artifacts/code here are diagnostic; production is unchanged.

Base: dadf69f1c5fb96491f4fd3a34e0ece3418878de3. Bank commit: ac484eaa.
Selection and source review are frozen before model calls. `FREEZE.json` hashes
the code, prompts, schemas, rubric, bank and config; stage-specific freezes bind
new candidate-bank or component-decision artifacts before E2/E3 calls.
Store actual execution HEAD and user authorization provenance at run time.

## Design units

36 full observed-window packets,20 qids,8 reviewed relation families. At most2/qid.
D12/8 qids; H-diagnostic12/6 qids; H-confirmation12/6 qids. No qid overlap.
E1/E2 use24 D+H-diagnostic packets only. E3 uses reserved12 H-confirmation packets.
No repeats. Each packet retains its archived OneGap and C. One complete observed W
is the evidence unit; no source clipping, new enrichment, retrieval or whole-source
audit. It is not a complete-acquisition benchmark. Source hashes and JSON pointers
are in bank/provenance.json. A pre-existing legacy transformation added `date` to
review-context metadata; it is recorded, preserved, and never treated as event date.
22 packets are actual Reader requests and14 are archived review-designed contexts.
Report that context stratification. No claim that all36 are live natural prefixes.

Reviewed strata:16 positive packets,6 duplicate/no-new,8 relevant/no-new and6 other
ambiguous/off-gap packets;27 frozen new useful atoms. E1/E2 have20 atoms and10
primary silence packets. E3 has7 atoms and4 primary silence packets. E3 positivity
is small (5 packets) and shares qids: a passing gate licenses further study only.
Case/atom annotations are offline evaluation data, never role input or prompt examples.

## E1: construction

| Arm | First call input | Subsequent input | Output |
|---|---|---|---|
| A0 | OneGap,C,Observation | none | 0–3 findings |
| A1 | OneGap,Observation | none | 0–3 findings |
| A2 | OneGap,C,Observation | selected full Evidence only | 0–3 findings |

A0/A1 share the exact production Reader prompt/schema; A1 omits C without a new
safety rule. A2 selector returns refs/reasons only,0–3 unique observed refs. Empty
selection skips formulation as a valid empty output, not a failed request. Whole
selected W plus existing metadata goes to Formulator; reasons, Gap, C, question,
requirements, hypotheses, trace, labels and historical answers are absent.
All raw findings are reviewed before any dedup. Exact normalized and blinded
semantic dedup are applied equally offline. Primary FSSR/SSP use raw outputs.
Frozen-atom GRSR and raw/postdedup silence prevent winning by silence/duplicates.

H1=A1−A0; H2=A2−A1. Pooled FSSR relative decrease>=30%; GRSR drop<=10pp.
H2 also requires Gap-relevance precision drop<=10pp. On H-diagnostic require strict
same error-reduction direction and the same recall/relevance guardrails. Require
both mean paired-packet strengthened-count delta<0 and equal-weight qid mean<0
on pooled/H-diagnostic. Zero baseline FSSR or no denominator is inconclusive.
Report packet/qid counts, all paired deltas and family/context/C-nonempty/stratum
sensitivity tables. Empty-C packets cannot directly diagnose pressure from existing facts.
No confidence or p-value threshold. H1/H2 may remain unsupported.

## E2: admission

After E1, freeze actual A0/A1/A2 findings plus the10 preserved actual historical
Reader candidates (9 source-supported,1 strengthened temporal candidate). E1
outputs must supply any additional negatives naturally; do not manufacture them.
Current historical negative is only in D: if no H-diagnostic strengthened candidate
exists after E1, STOP E2/H3 for inadequate opportunities rather than manufacture one.
Require both source-supported positives and strengthened negatives in D and H-diagnostic.
Canonical dedup uses normalized statement, refs and exact full Evidence. Conflicting
duplicate labels stop preparation. Preserve all origins/exclusions. Per split choose
at most15 positives and15 negatives, by ascending pair SHA. All other unique pairs
remain archived, unsampled; no filling to spend budget. This is diagnostic sampling,
not a prevalence estimate. Ambiguity is an additional source-review flag.

G0 retains production Grounding prompt/schema byte-for-byte. Its inherited concrete
examples are documented as unchanged-baseline exceptions; NEW prompts have none.
G1 first builds at most32 minimal source commitments from full Evidence and metadata
alone. Freeze that output before Coverage. Coverage sees Candidate + inventory and
no raw Evidence, Gap, C or labels. One inventory per unique Evidence/config/prompt
within the stage, generated independently of candidate availability or content.
No cross-stage reuse. Inventory calls list linked pairs/packets in PRIVATE metadata,
not the model input. Review source support/omissions of inventories separately.

FAR uses frozen unsupported-strengthened candidates; TPR uses explicit positives.
Ambiguous FAR is separate. Rescue means G0 false-admits and G1 rejects. H3 requires
pooled FAR decrease>=50%, G1 TPR>=85%, positive packet/candidate-paired and qid
direction, same strict error direction and TPR guard on H-diagnostic. Zero G0
false-admissions means inconclusive. G1's bottleneck and extra call confound a pure
psychological anchoring interpretation; conclusions name the structural intervention.

## E3: conditional integrated confirmation

Complete, valid E1/E2 reviews plus at least one full mechanism gate must pass.
Otherwise stop; do not open the confirmation set for model calls. If E2 cannot
form a valid bank, record that limitation and stop under this conservative plan.
Selection: H2 pass=>A2; else H1 pass=>A1; else A0. H3 pass=>G1; else G0.
Freeze report hashes, selected components and gate decision before E3.
Current=A0+G0; repaired=selected components. Only reserved H-confirmation12.
Preserve0–3 proposals and all admission verdicts. Skip exact duplicates as production
does; human semantic dedup is a common OFFLINE analysis endpoint. No human support
filter repairs false admissions: any admitted unsupported candidate is counted even
if later deemed redundant. `candidate_C` is a diagnostic artifact, not state mutation.

Pass requires0 false authoritative C,SSP>=95%, frozen-atom useful recall>=80%,
postdedup primary correct silence>=80%, all defined and no role/transport failures.
Report raw and postdedup candidate-C outcomes. Empty system cannot pass precision
or recall. No production changes, persistent fields or Recovery rollout in this task.
A two-arm integrated comparison cannot establish a factorial interaction; combined
benefit is consistent with joint mechanisms only. Future implementation is separate.

## Same model and execution policy

Read from frozen H2 config: DeepSeek endpoint /chat/completions,deepseek-flash,
thinking enabled,reasoning_effort high,temperature0,max_tokens32768,json_object,
stream=false,max_retries0. `user_id` stays omitted. No tools, search or SDK retries.

Independent tasks run asynchronously with a bounded semaphore and matched HTTP pool.
Initial=min(ready independent requests,256,available account quota). E1 maximum
ready chains72,E2 at most83,E3 24; these small batches cannot use256/512/1024.
No paid concurrency probes. Account-wide ceiling2400 remains a ceiling, not a target.
Caller must account for concurrent jobs through `--account-available`.
Timeouts connect30/read900/write60/pool30,total1200s; accept whitespace keep-alive
before a complete JSON response and archive partial bytes if interrupted.
Any schema/transport/finish/ref/model failure halts unsent requests and the affected
gate; already in-flight responses finish and remain archived. This section37 stop
is stricter than ordinary concurrency reduction. No retry, replacement or resume.

Store raw request/response bytes, reasoning/final content, parsed output, hash,
model,arm,packet/pair/source IDs,usage,latency,HTTP status and failures by request ID.
Do not serialize credentials. Report input/output/cache-hit/miss usage, complete
and inconsistent records, failure rates, peak concurrency and latency/wall time.
Cache rate=sum(hit)/sum(input) only over complete consistent usage records.
Failed/missing outputs are not refusals, empty findings or negative verdicts;
affected rates are undefined and the gate cannot pass.

## Review and authorized execution

Follow REVIEW_RUBRIC.md. Source packets and relevance packets are separated and use
opaque IDs; private mapping stays out of review. Do not inspect other-arm outputs.
No generated claim enters C without model admission; no reviewer rewrites a candidate.

Offline commands are in README.md. Live runner requires a new authorization artifact
referencing this exact freeze and a later explicit user message; no artifact is
created now. Budget ceilings: E1 96,E2 143,E3 conditional120. The24 E1 packets contain
23 distinct full Evidence payloads, so E2 needs at most60+60+23 calls. Exact E2/E3 planned
counts are computed from frozen candidates/components, not spent to the ceiling.

ROOT_CAUSE_CONCLUSION.md after authorized calls must answer TASK section53's17
questions, including rejected/inconclusive hypotheses, held-out direction, recall
cost and whether any runtime change is warranted. At preparation all causal effects
remain unmeasured; no conclusion of success/failure is available.
