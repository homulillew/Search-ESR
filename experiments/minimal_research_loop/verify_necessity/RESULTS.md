# V1 Verify Necessity: result

The pre-call bank held 52 real historical W packets from 12 qids. One Reader call per packet yielded 55 natural Findings from 10 qids, with no Reader failures. The prefix-only review, frozen before Verify, marked 53/55 source-supported and 47/55 fully eligible to become a new Claim for the current Gap.

| Path | Extra calls | Accepted | Source precision | Full Claim precision | Supported recall | Unsupported promotions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Direct | 0 | 55 | 53/55 (96.36%) | 47/55 (85.45%) | 53/53 (100%) | 2 |
| Verify | 55 | 54 | 53/54 (98.15%) | 47/54 (87.04%) | 53/53 (100%) | 1 |

All 55 Verify responses were valid; no request failed. Verify rejected the unsupported claim that a season-three episode was the *finale*. It accepted the other unsupported temporal join: a later retrospective's “67 albums later” was attached to a separate 2016 interview. It also accepted all six source-supported but off-Gap Findings. The Verifier saw neither Question nor Gap, so this last limitation is a design consequence as well as an empirical result.

Verify used 33,502 input and 12,624 output tokens; the provider reported 768 prompt cache-hit tokens (2.29% of prompt tokens). The sum of response latencies was 83.54 seconds, with a 1.16 second median; parallel wall time is different. Direct incurred no additional call after the shared Reader. Cache telemetry follows the provider's reported token fields; it does not imply savings without a confirmed price schedule.

The pre-registered A/B/C necessity decision falls in the gray zone: Direct misses the 97% source-precision threshold, but had only two unsupported Findings, below the five needed for the B intervention test. Verify removed one of two, below B's 60% target, while preserving supported recall. Neither path reaches the pre-registered 95% full Claim precision needed to enter R1. V1 therefore supplies **no deployable Claim-commit policy** for R1.

Sensitivity: the “67 albums later” temporal label is somewhat judgment-sensitive. Relabeling that one Finding as source-supported would make Direct source precision 54/55 and qualify the narrow A condition; it remains off-Gap under either reading. Full Claim precision and the R1 exclusion are unchanged. Findings within a qid and repeated source passages are correlated, so the cell ratios are descriptive rather than independent-sample estimates.
