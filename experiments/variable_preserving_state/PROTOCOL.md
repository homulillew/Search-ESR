# Variable-Preserving Research State

Stage order is V1 Test Representation, V2 Query Bias, V3 Evidence-to-Binding, V4 Small State Causal Probe. A failed gate stops later stages with `NOT_RUN.md`. No long rollout in this branch. Historical experiments are append-only and read-only.

V1 uses 30 normalized, prefix-only packets from 11 qids. The core is the prior A1 24-case family; six further real historical prefixes come from qids 186, 311 and 324. All SemanticGaps and explicit provisional hypotheses are reviewer-frozen before calls. V2 preselection of 16 source-uncertainty packets from 8 qids is frozen before any V1 call.

Each V1 packet receives one newly sampled C0 concrete-Claim, C1 natural TestCard and C2 provenance TestCard response in rotating order. Same model, packet and 0–3 budget. `max_retries=0`; retain invalid outputs and provider failures. Arm-blind prefix-only review scores unsupported bindings, premature-case rate, coverage, testability, minimality, unknown preservation and complexity. V1 gate requires one TestCard arm to meet all prespecified thresholds in the task book; only then can V2 begin.
