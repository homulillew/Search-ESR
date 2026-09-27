# Interface contracts

## Real acquisition tools

The action union is generated directly from `SEARCH_FIND_TOOLS`.

```json
{"decision":"acquire","focus_requirement_id":"R1","one_gap":"Verify whether the target book references Euler.","strategy":"VERIFY_RELATION","hypothesis_ids_under_test":["H1"],"action":{"tool":"find","arguments":{"doc_ref":"D7","query":"Euler"}}}
```

```python
SearchFindTools.execute(action['tool'], action['arguments'])
```

| Tool | Exact arguments | Mechanical checks |
|---|---|---|
| search | `query`, optional `k` | nonblank <=16000 chars; exact integer k1..10, default5 |
| find | `doc_ref`, `query` | observed D alias; nonblank query <=16000 chars |
| open | `window_ref`, `direction` | observed W alias; before/after/around |

Extra keys, wrong alias type, missing arguments, unknown aliases, booleans/floats
for k and invented tool names are rejected and recorded. No keyword-to-direction,
OPEN-to-FIND, source_ref guessing, or semantic query repair. Find localizes elsewhere
within D using a query; Open continues around a W using position. They may return
some of the same text, but their argument meanings are distinct.

Closure is a separate decision with exactly:

```json
{"decision":"request_closure"}
```

It requires no fake OneGap, strategy or empty tool arguments. Actor cannot STOP,
answer Q, write C or mark a requirement complete. Strategy is a small action label
in T, not persistent requirement status. H IDs must already exist.

## Semantic role contracts

All role outputs are strict JSON objects (or their JSON text), no markdown or
model-generated source metadata. Duplicate JSON keys and nonfinite values fail.
Schemas are available through `roles.schemas()`; prompts through `roles.PROMPTS`.

| Role | Input | Output |
|---|---|---|
| Actor | Q, R, C, H, TraceView, observed source handles | acquisition decision or closure request |
| Reader | OneGap, C, full current Observation list | `{findings:[{statement,evidence_refs}]}`, 0–3 |
| Grounding | candidate, full cited raw Evidence | `{verdict:supported\|insufficient,reason}` |
| H manager | Q/R/H, current Observation, newly accepted C, trace outcome | bounded updates plus <=3 useful new D nominations |
| Closure | Q/R/C and Evidence supporting C | CONTINUE with missing R IDs/summaries, or READY with reason/C IDs |
| Finalizer | Q/C/Evidence/current Closure verdict | answer and cited C IDs |

H operations: `ADD(statement,basis_refs)`, `KEEP(hypothesis_id)`,
`DEPRIORITIZE(hypothesis_id,basis_refs)`, `REJECT(hypothesis_id,basis_refs)`.
Refs must be observed; rejection cannot use an empty basis. Empty basis is allowed
for a tentative candidate or NoGain-driven deprioritization. No model-assigned IDs,
confidence, C patches, requirement coverage or final-answer permissions.

## Boundaries that are semantic, not decidable by schema

- OneGap premise remains tentative when C has not established it. Euler/Ding/memo
  examples constrain the prompt and offline review rubric, not a phrase blacklist.
- A finding must advance the current gap and be semantically new. Exact duplicate
  suppression is mechanical; paraphrased duplicates require semantic judgment.
- Grounding must preserve full identity/relation/time/modality/qualifier binding.
  Valid existing W citations are necessary, not sufficient, for truth.
- Useful source nominations need relevance; a new D is not automatically useful.
- Closure must check all material Q conditions even if a coarse R omitted one.
  A structurally valid false READY is possible and is a high-risk model failure.

The offline suite tests role separation and scripted decisions. It does not
certify these natural-language judgments for DeepSeek or any other model.
