# Budget and locality repair — staged protocol

Base remotely verified: 3d754d160a02eae8900c4f6bb43ef4999bb530a2.
All prior results remain immutable. Persistent state stays Q + Claims + H.

## E0 (before any new semantic prompt experiment)

Mechanically select 12 actual previous length failures: six P1, six P5,
two each empty-H, strong-H, and other provisional-H per arm; maximize qid
coverage then fixed SHA256 tie-break. Other provisional-H can include a stale
candidate; diagnostic H-removal inputs remain labelled as such in original
provenance. No expected/new answer is consulted. Old 4096 requests/results are
reused exactly. Previous broad outputs on related frozen cases are descriptive.

Every E0 request copies its old payload byte-equivalent in semantic fields.
Only max_tokens changes (8192,16384,32768,omitted); temperature, prompts, QCH,
JSON mode and timeout remain unchanged. Historical request metadata confirms
max_tokens absent and D10 round2 reached 65535 output/reasoning tokens. This
observed usage is not an asserted provider setting.

Three fixed EDEFAULT representatives are real API preflight and mandatory
historical-default control. All three must produce stop + schema-valid JSON +
reasoning usage before a formal batch. A failure stops formal batches for
transport/exhaustion diagnosis; it never authorizes a blind retry.
Then adaptive explicit ladder: first >=11/12 valid JSON, <=1/12 length and fewer
than3/12 outputs above90% of cap qualifies. Stop further explicit arms at that
point. Complete EDEFAULT's remaining nine fixed cases once (reuse preflight)
to qualify preferred historical-equivalent primary; choose default if adequate,
otherwise the qualified explicit setting. Every actual call is frozen first,
max_retries=0, no semantic best-of. Preserve failures and skipped arms.

Completion, schema, usage, reasoning/final tokens, P50/P90/max and headroom are
separate from semantic labels. Need results report ITT strict and conditional
validity given final output, including schema failures in the latter denominator
when nonempty final content exists. Cache hit rate is token-weighted.

## D0 independent acquisition

Prepare at least12 previously unused Need-development BC+ qids; split at qid
level into4 development and8 confirmation before acquisition. No answer/gold
fields are passed to any runtime. Use frozen historical discovery Actor,
Search/Find/Open and exact U1 Writer; never B1/B2/B3 for acquisition. Preserve
raw observations, hashes, Writer outputs and complete QCH transitions. Empty
initial QCH is a natural state. Do not fabricate H/Claims/one-gap states.

Freeze acquired QCH and commit. Then offline support/coverage labels and commit.
Only then instantiate/run new Need prompts. Unsupported Writer Claims are
excluded as contaminated natural states, not silently repaired. No hand-written
Claim fills a stratum. Confirmation qids remain unavailable for policy design.

## N1 semantic experiment

Primary no tools and no STOP. B0=exact oldP1, B1=exact oldP5 with E0-qualified
budget. B2 uses the user's minimal existential prompt. Oracle gap is diagnostic.
B3 is conditional on B2 still showing broadness; not a default extra arm.
Each state/arm one response, failed outputs retained. No P0/P2 sweep.

Before semantic calls freeze bank selection, labels, rubric, prompts, gates,
provider settings, horizon/sample count and failure policy in its own manifest.
Semantic development: completion>=95%, strict>=85%, premise/stale<=5%, W<=10%,
No-H>=80%, one-gap>=90% where adequate, Delta retirement>=85%. Fresh gate:
>=24 states/8 unseen qids, completion>=95%, strict>=90%, premise/stale/W<=5%,
No-H>=85%, one-gap>=90% where adequate, Delta>=90%. NEAR_PASS uses task §39;
no relaxed qid coverage or systemic broadness/promotion. Closure is separate.

Bad-case loop targets one semantic mechanism and prefers task simplification;
monitor P90 reasoning and output failures. Finite development interventions,
no reused confirmation failures as fresh evidence. No persistent Requirement Map,
external verifier, retriever or Writer changes. Stop at qualified result or
honestly reported execution/data/semantic limitations; preserve all versions.
