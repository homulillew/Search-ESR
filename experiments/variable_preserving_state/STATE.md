# Minimal research state

`ResearchProgress = {WorkingHypotheses, SemanticGaps, TestCards}`. A WorkingHypothesis has an ID, provisional status, binding and observed basis refs. A SemanticGap says what is unknown, without Search/Find/Open instructions. A TestCard has one natural-language condition, known slots, unknown slots, status (`open|satisfied|refuted`) and evidence refs. No graph or logic DSL is used.

Unknown is first-class and does not imply a hypothesis. A hypothesis is not evidence. Concrete persistent known values require a question anchor, currently observed W ref or explicit provisional H ref. The harness validates identifiers and ref existence; a semantic reviewer checks whether the cited source really supports the value. A temporary query guess never persists automatically.

ControlProjection, including expected source type, is separate from SemanticGap. Candidate names are displayed as `WORKING HYPOTHESIS`, `status=provisional`, with basis refs. Actor tools remain available without hard gating.
