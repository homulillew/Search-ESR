# Separate schema-representation capability diagnostic

The first seven frozen probes are complete and retained. Responses accepted two simple schemas and rejected original Actor/Updater schemas for missing supported type/union representation. Strict beta rejected the selected tool in default thinking mode; exact/partially compiled Actor schemas also failed schema parsing. No research preflight/replay has run.

Before declaring the whole service unavailable, this separately frozen extension tests **equivalent schema representations**, not repaired model outputs or tuned research prompts. New IDs and requests remain separate from the original seven; no successful result replaces a failed call.

Logical transformations:

1. Disjoint `decision`/`tool` singleton-discriminated oneOf branches become anyOf.
2. String const becomes typed singleton enum; string-only enum receives the logically implied type.
3. minLength=1 is redundant where the existing non-whitespace pattern is required.
4. An array with maxItems=0 receives an item type: no item can exist, so its type cannot affect the accepted language.

All array limits, keys, types and ranges remain. Offline equivalence fixtures passed two tests, including original negative cases and a cross-product of actions/lengths.

Six fresh probes: compiled Actor and Updater with Responses; unchanged Goal schema; an **intentionally impossible** array schema (minItems=3,maxItems=2) as an enforcement negative control; strict bounded array and compiled Actor with auto tool choice (preserving default thinking). No runtime registry or research semantics are relaxed. The function surface must produce exactly one named function; ordinary text does not count as constrained success.

An impossible schema must not yield a completed JSON object claimed to satisfy it. Such an output is direct evidence that full bounds are not enforced, even when ordinary positive examples happen to conform. A rejected impossible schema alone does not establish complete support: the production schemas must also work. If full enforcement remains unavailable or uncertain, stop the study and report which stages were not run. This extension does not authorize dropping constraints, switching model/thinking mode, or additional unbounded capability retries.
