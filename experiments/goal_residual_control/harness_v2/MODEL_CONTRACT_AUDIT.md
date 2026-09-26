# Model contract audit before live calls

Source of tool definitions: llm_chat/search_find_agent.py, SEARCH_FIND_TOOLS. Search query/k and range 1–10, Find doc_ref/query, Open window_ref/direction {before,after,around}. Underlying tool definitions are imported unchanged. The v2 response wrapper requires explicit k for Search as requested by the task.

Research Actor receives the complete response schema and five complete JSON examples. It never needs to infer a discriminator from the function-style tool schema in its user context. The research-instruction prefix is byte-identical to v1. Examples contain no frozen qid, known answer or gold source.

Goal Reviewer uses the exact original prompt, with the same two fields and consistency rule. Its typed example is explicit but is not a literal JSON instance (it uses true | false); offline tests cover both concrete valid forms. No Goal Reviewer prompt tuning or A1 residual resampling occurs.

State Updater retains the existing two semantic layers and three hypothesis actions, with explicit concrete serialization examples added. All output nodes have closed schemas, exact parsers and deterministic tests. See CONTRACT_MATRIX.md.

Main's authentication fix is already inherited. The shared AuthFailureLatch is used by both old execution code and v2; existing authentication regression tests verify unchanged serial behavior, and v2 shares one latch across its bounded four-worker batch. Historical archived results are untouched.

Phase A contains no live model response or experiment result. Phase B requires a separate committed freeze, request-object audit and offline test record before the first call.
