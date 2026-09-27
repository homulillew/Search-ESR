# Frozen preparation state

- Source/base HEAD: `dadf69f1c5fb96491f4fd3a34e0ece3418878de3`.
- Audit commit: `74145c2f`; bank/annotation/rubric commit: `ac484eaa`.
- Harness freeze: this third preparation commit; complete hashes in `FREEZE.json`.
- Provider/model: DeepSeek / `deepseek-flash`; temperature0; thinking enabled;
  reasoning_effort high; max_tokens32768; max_retries0; user_id omitted.
- Bank:36 packets/20 qids;24 E1/E2 inputs;12 reserved E3 inputs. Every selected
  prefix has a canonical content hash and original source paths/metadata hashes.
- Prompts/schema snapshots:7 roles; A0/A1/G0 exact baseline comparison tested.
- Fixed initial request hashes:72 unconditional E1 requests and24 possible A2
  formulation requests; subsequent E2/E3 inputs receive stage freezes after review.
- Replicates1; Actor horizon0; tools=[]; new retrieval budget0.
- Initial concurrency bounded by ready tasks and remaining account quota:
  E1<=72,E2<=83,E3<=24; maximum configured cap256. No performance probe.
- Request ceilings:E1<=96,E2<=143,E3 conditional<=120. No replacement/retry/resume.
- Failure policy:any transport/schema/reference/finish/model error stops unsent
  requests and affected gate; archive failures and already in-flight completions.
- Status:offline prepared;0 new semantic calls;0 retrieval calls;NO NEW AUTHORIZATION.

The final commit cannot embed its own SHA without changing it. `FREEZE.json` pins
all substantive preparation files and prior commits; run metadata records actual
execution HEAD, this freeze hash, stage input freeze and a new authorization hash.
The preparation test log is committed alongside the freeze, excluded from its hash
map to permit recording the test result without a circular self-reference.
