# E0 execution calibration

All semantic prompts and QCH stayed identical to their archived requests.
Only max_tokens changed. Old E4096 results were reused, not rerun. Twelve cells
are deliberately sampled from old length failures, not a population sample.

| Budget | Final valid JSON | Length | Completion P90 | Max | >90% explicit cap |
|---|---:|---:|---:|---:|---:|
| 4096, archived | 0/12 | 12/12 | 4096 | 4096 | 12/12 |
| 8192 | 9/12 | 3/12 | 8192 | 8192 | 4/12 |
| 16384 | 10/12 | 2/12 | 15798.7 | 16384 | 2/12 |
| 32768 | 12/12 | 0/12 | 8951.8 | 11485 | 0/12 |
| omit max_tokens | 12/12 | 0/12 | 11179.2 | 17890 | unknown default cap |

Three fixed EDEFAULT preflight requests passed before formal calibration. Their
outputs were reused when that arm expanded to all12. No default request was
repeated. The first adequate explicit setting is32768. Historical-equivalent
primary selection is **omit max_tokens**, which also passed12/12.

The historical D10 actor request contains no max_tokens and actually generated
65535 completion/reasoning tokens before length termination. This does not prove
a configured provider field of65536. The current calibration had no persistent
32768/default cap exhaustion and does not establish E-BUDGET-SPIRAL. Two cases
that failed8192 and16384 completed at32768 and default.

## Semantics remain a separate issue

Strict validity on this failure-enriched calibration set:

| Arm | P1 | P5 |
|---|---:|---:|
| 8192 | 1/6 (1/4 given output) | 3/6 (3/5 given output) |
| 16384 | 3/6 (3/4 given output) | 4/6 (4/6 given output) |
| 32768 | 1/6 | 4/6 |
| default | 2/6 | 2/6 |

These are one draw per distinct execution configuration, not deterministic
continuations of the old truncated response. Nonmonotonic semantic scores are
retained; there is no best-of selection. The broader fresh experiment will
estimate policy quality beyond these deliberately difficult cases.

Default P5 C10 still asks the full multi-match sequence; C11 requests all
subsequent match results. Its old6/6 returned-valid score therefore does not
generalize to the previously censored cases. This supports concern about
completion-selection bias without estimating its exact population magnitude.

No final output is a budget/transport observation, never a semantic label.
With output restored, local-frontier selection and unsupported presuppositions
remain observable failures. Full row labels and usage are retained separately.
