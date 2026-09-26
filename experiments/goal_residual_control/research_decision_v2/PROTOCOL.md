# G2v2 Research Actor contract repair

Parent experiment: `experiment/goal-residual-control` at `f53a43c9342fa643c117b9362dce1164abaf3e4a`.

This stage is append-only. The frozen G2 parser, prompt, responses, `research_decision/`
artifacts, and the historical 75/120 valid result remain unchanged.

## Treatment

G2v2 keeps the same 40 snapshots × A0/A1/A2 = 120 planned cells, the same
counterbalanced order, the same DeepSeek model/settings, the same Actor user
messages, the same tool argument schemas, and the same old G1 outputs. In
particular, A1 reuses the already archived Goal Residual in the old G2 request;
the Goal Reviewer is not rerun.

The only request treatment is the Actor system prompt's output-contract section:
it now gives complete flat examples for STOP, Search, Find, Open, and a valid
two-action batch, and explicitly forbids `type` and `name`/`arguments` wrappers.

## Validation

`actor_contract_v2.py` is a separate fail-closed parser/runner. It does not
modify or call the frozen G2 parser. It validates the top-level Actor object and
each flat action against the unchanged historical Search/Find/Open argument
schemas. It additionally rejects Find/Open references that were not present in
the pre-batch Available Workspace, so a dependent Search→Find/Open batch cannot
pass the contract.

Deterministic tests cover:
- valid stop
- valid search
- valid find
- valid open
- valid two-action batch
- invalid `type` wrapper
- invalid `name`/`arguments` wrapper
- missing query
- invalid tool
- dependent batch

## Integrity and gate

No response repair, normalization, retry, resampling, parser relaxation, or
selected-sample replacement is allowed. Raw valid and invalid responses are
archived.

Primary integrity gate: at least 96/120 (80%) G2v2 calls must satisfy the frozen
v2 contract. If the gate fails, G3 remains stopped and the failures are audited.
If the gate passes, G3 must execute the v2 decisions in a new append-only
one-step acquisition directory; it must not reuse the old `one_step_acquisition/`
placeholder as if old G2 had passed.

Architecture comparisons remain invalid until real tool observations exist.
