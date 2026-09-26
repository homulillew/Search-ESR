# DeepSeek exact-schema capability report

## Decision

**FAIL_REQUIRED_EXACT_SCHEMA — stop before Admission Replay and G4/G5.**

The same provider `https://api.deepseek.com` and model `deepseek-flash` were used. Thirteen separately frozen diagnostic requests were attempted once each: eight Responses and five strict-function requests. Six returned HTTP 200 and seven HTTP 400. Four returned objects pass their local schemas; two completed responses violate the supplied schema. One of those is a deliberately impossible-schema negative control, so **4/13 is not a research-node validity estimate**.

The 24 historical requests are selected and frozen but **not submitted**, because the preceding capability gate failed. No U0 was resampled, no U1/Uc was called, and no v3 retrieval or state rollout ran.

## Decisive evidence

### Strict function calling: satisfiable array bound violated

Request ID in local diagnostics: `strict_array_auto`.

The request used `/beta/chat/completions`, `function.strict=true`, default thinking mode and `tool_choice=auto`. The function parameter schema required an integer array with `minItems=1,maxItems=2`. The service returned a completed function call:

```json
{"items":[1,2,3,4]}
```

The local validator rejects four items against maxItems=2. This is an actual counterexample to full conformity for a satisfiable schema. It agrees with the documented strict subset's lack of array-length support. Replacing the two-action/two-Claim constraint with a local-only check would leave a prohibited interface confound.

### Responses: contradictory-bound negative control completes invalidly

Request ID: `impossible_array_responses`.

The request used `/responses` with `text.format.type=json_schema`, `strict=true`, and an integer array requiring `minItems=3,maxItems=2`. No object can satisfy both. Instead of rejecting the request or returning failed/incomplete generation, the service returned `status=completed` and:

```json
{"items":[1,2,3]}
```

This violates maxItems=2. It shows that accepting a schema and returning completed JSON does not establish enforcement of every supplied bound. The test does not establish that all Responses constraints are ignored, nor that every satisfiable bound will fail. It does fail the predeclared exact-enforcement negative control.

### Production-shape schemas were not successfully established

The original Actor root oneOf and the Updater enum without an explicit type were rejected with HTTP 400. A separately frozen logical-equivalence diagnostic added implied types, converted disjoint oneOf branches to anyOf, and supplied an immaterial item type under maxItems=0. Actor root anyOf was still rejected because the service demands an object at the top level. This is a limitation of the tested representations, not proof that no conceivable equivalent representation can exist.

The compiled Updater and unchanged Goal schema each returned a schema-valid object. However, the synthetic Updater output was `set` with an empty statement, which fails the existing local semantic consistency check. Schema validity and semantic validity must remain distinct. This synthetic diagnostic is not a measurement of ordinary research-prompt behavior.

## Complete attempt ledger

| Probe | Surface | HTTP | Schema result / observation |
|---|---|---:|---|
| required_enum_range | Responses | 200 | valid singleton enum, integer range and closed keys |
| array_length | Responses | 200 | valid two-item output; one positive example |
| full_actor | Responses | 400 | required supported type/union representation absent |
| full_updater | Responses | 400 | required supported type/union representation absent |
| strict_array_length | beta strict function | 400 | selected tool_choice unsupported in thinking mode |
| strict_actor_exact | beta strict function | 400 | schema representation rejected |
| strict_actor_equivalent | beta strict function | 400 | empty-array branch requires items |
| compiled_actor_responses | Responses | 400 | top-level object required |
| compiled_updater_responses | Responses | 200 | schema valid; empty `set` fails local semantic rule |
| goal_responses | Responses | 200 | schema valid; no research closure evaluation |
| impossible_array_responses | Responses | 200 | completed object violates maxItems; negative control fails |
| strict_array_auto | beta strict function | 200 | four items violate satisfiable maxItems=2 |
| strict_compiled_actor_auto | beta strict function | 400 | top-level object required |

All errors, raw requests, responses, model fields and usage remain in the event/output files. No response was repaired, stripped, normalized, replaced, or used as a successful retry. The six extension probes have distinct IDs, schemas/API choices, a new protocol and a separate pre-call freeze. They are capability representation diagnostics, not replacement research samples.

## What is and is not established

- **Established:** this account/model/API combination does not provide the complete, verified contract needed by this protocol through the tested surfaces. Strict functions exhibit a direct array-bound violation; Responses fails an enforcement negative control and the tested complete Actor representations.
- **Not established:** that DeepSeek cannot produce useful JSON, that every supported keyword fails, that structured generation universally changes research semantics, or that the admission hypothesis is false.
- **Not permitted here:** replacing the original object/array contract with a new fixed-slot representation, weakening bounds, disabling thinking to bypass a surface error, prompt-only fallback, retrying until valid, or silently changing models.
- **Decision:** stop as explicitly required in section 七 of the user task. Further provider/contract changes require a separately scoped decision; this run supplies no Admission/G4/G5 effect estimate.

## Cost and integrity

Six successful HTTP responses report 1,002 input tokens and 2,181 output tokens (2,064 reasoning), totaling **3,183 reported tokens**. Cache hit/miss: **0 / 1,002**, weighted rate **0%**. The seven HTTP 400 responses report no usage; their usage is unknown, not certified zero cost. No credentials are archived.

Local tests: 39 initial tests plus two equivalence tests passed. All **519** protected historical artifacts are byte-identical. Both capability freezes' code, prompts, schemas and requests match. Thirteen unique attempt IDs, no retries, no research calls. See [metrics](CAPABILITY_METRICS.json) and [integrity](../analysis/INTEGRITY.json).

Official documents were checked on 2026-09-26: [Responses reference](https://api-docs.deepseek.com/api/create-response/), [compatibility guide](https://api-docs.deepseek.com/guides/responses_api/), [strict tool-call subset](https://api-docs.deepseek.com/guides/tool_calls/). Documentation motivated testing; the archived actual responses determine this gate result.
