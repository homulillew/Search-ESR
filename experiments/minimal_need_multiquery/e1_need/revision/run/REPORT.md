# E1 sole bounded revision r1 — stop

## Scope and result

18 exposed natural QCH states / 9 qids, 8 No-H; 36 new calls: concurrent exact B0 and revised B3. This is the one allowed development revision, not fresh confirmation. The combined prompt was replaced as one package; no individual sentence effect is identifiable. Inputs, gates and implementation were committed at `83ac224a3add22b3326260196c2b87870cf1b00b` before calls.

| Arm | Strict /18 | Valid output | P | A | W | S | X | No-H /8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Concurrent exact B0 |10|18|3|4|1|0|0|6|
| Revised combined B3 |2|17|7|3|6|2|1|0|

Error categories can overlap. B3 P/A union is9/18; conservative P+A sum is10/18. Its valid-output-conditional strict rate is2/17. There is1 paired strict gain and9 losses. Every planned cell remains in the denominator.

The gate is **STOP_E1_NO_MORE_REVISIONS**. B3 misses strict≥16, P+A≤1, W=0, gain≥3 and No-H≥7. Both arms meet the execution threshold≥17. No fresh acquisition or E2/E3/E4 calls follow. This is a development failure, not a failed fresh confirmation.

## Observed mechanisms

- B3 often rephrases nearly the entire question: paper content plus author employment/publications; author promotion plus education and supervisor biography; artist birth/population plus performance and recording hiatus. A single requested identity does not make these one current objective.
- Attribute questions still presume candidate events: Marwaha's later article, Kwon's joint donation, and Sophie's partner interview. The memorandum date is again attached to a letter in F16_S02. F14_S00 introduces Civilization VI despite empty C/H; F13_S00 changes country establishment into religion establishment.
- F13_S06 asks again for the disorder already present in both verified case descriptions. F14_S06 asks again for an already covered DLC release/mechanics profile. Unresolved advisor/history/date conditions remain available.
- F14_S01 remains a legitimate coherent DLC discovery Need. F13_S01 is accepted as diagnosis discovery from a Q-provided clinical profile, with explicit ambiguity about discovery versus attribution to a particular unidentified report.

The intended internal premise/subject check did not reliably appear in the returned Need. We did not measure hidden reasoning correctness or isolate which instruction caused these failures. These results reject this tested prompt package; they do not establish that every possible minimal QCH policy must fail.

## Review and sensitivity

A single reviewer recorded arm-masked primary judgments and their hashes, committed them, then opened the arm mapping. Prior familiarity with prompts/cases and execution progress logs prevents a claim of perfect blinding. There is no independent reviewer. Each packet has all six dimensions, premise anchors, objective decomposition, ambiguity and reasons.

Book-content coherence and source-referent boundaries are not treated as unquestionable gold. A deliberately generous sensitivity removes **every A and W failure**, even low-ambiguity ones, while retaining P/S/X. It gives B0 **15/18**, B3 **8/18**: the stop decision remains. Even hypothetical success for the sole execution failure would raise that relaxed B3 ceiling only to9/18. This sensitivity does not overwrite labels or redefine the gate. See `SENSITIVITY.json`.

The identical B0 payload yielded14/18 in v1 and10/18 in r1. Four previously valid cells changed their Needs and became W/P/A failures. This small one-response experiment exhibits run variability even with temperature0. Cross-run comparisons are descriptive; the r1 causal comparator is its concurrent B0. No qid-level generalization, significance or fresh reliability is claimed.

## Execution and cost

All36 requests reached a raw HTTP200 response.35 yielded valid output. B3 F11_S01 returned `finish_reason=length`, completion65,535 tokens, all reported as reasoning; no Need was available. The request omitted `max_tokens`. This is a retained provider length failure, not a timeout or an imposed4096-token cap. It was not retried.

Input20,400; output274,140 including reasoning272,226; total294,540. Cache hit9,472, miss10,928; weighted hit rate **46.43%**. All36 usage records are complete and internally consistent. Wall395.27s, peak concurrency8. No currency estimate without a verified price.

`INTEGRITY.json` verifies36 exact request/response/result archives,343 frozen files and15,286 historical files unchanged. Tool calls0, retries0. The single revision budget is exhausted.
