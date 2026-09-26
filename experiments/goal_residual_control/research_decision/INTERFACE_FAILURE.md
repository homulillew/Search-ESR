# Action interface failure — no repair applied

The frozen parser expects the task's flat action object:

```json
{"tool":"search","query":"...","k":5}
```

The exact supplied Actor prompt ends with `actions: [...]` without spelling out an action object. The harness supplied the historical OpenAI function-tool schemas in the user context, but omitted the separate concrete flat JSON example in task section 25. Those function-tool schemas describe tool arguments, not the surrounding JSON action discriminator. This left a preventable input/output contract ambiguity.

Observed responses include `type: search` and `name/arguments` wrappers, as well as the expected `tool` wrapper. The committed parser rejects the alternatives. This is a harness contract defect; these responses are not evidence that a model cannot select a relevant research action.

No parser relaxation, schema normalization, tool execution of rejected content, or model resampling is applied. Raw content, error and token usage remain archived. Only frozen-parser-valid decisions enter the diagnostic semantic review. Invalids remain in intention-to-treat counts. Differential validity across arms makes valid-only architecture comparisons selected and unreliable.

## Concrete contract for a separate future freeze

`PROPOSED_ACTION_SCHEMA.json` expresses the already intended response format, including the task's `tool` key, as a complete JSON schema. A future request should explicitly include this entire response contract and flat examples for Search, Find and Open, in addition to the unchanged parameter/tool semantics. This proposal is not used in any request in the present frozen experiment.

Example actions:

```json
{"tool":"search","query":"standalone query","k":5}
{"tool":"find","doc_ref":"D1","query":"local query"}
{"tool":"open","window_ref":"W1","direction":"around"}
```

Stop remains `{"decision":"stop","gap":"","actions":[]}`. This repair addresses serialization only; it adds no research-state field, tool hint, hard gating, candidate answer, residual or rewritten query. A separate append-only freeze would be required before new model calls. Deterministic schema checks can verify the contract, but do not establish that the provider will comply.
