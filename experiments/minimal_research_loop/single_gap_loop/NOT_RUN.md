# R1 Minimal Single-Gap Loop: not run

The pre-registered R1 admission rule requires both a deployable V1 Claim-commit policy and a deployable C1 closure policy. C1 selected binary review, which passed its local gate. V1 did not yield a deployable Claim-commit policy: Direct full Claim precision was 47/55 (85.45%), and Verify full Claim precision was 47/54 (87.04%); both are below the frozen 95% R1 admission threshold. The source-only Verifier cannot screen Gap relevance, so running the four-action integration loop would knowingly promote off-Gap Findings to Claims.

No R1 cases were sampled, no R1 model or tool calls were made, and no integration metrics are reported. The pending-W-first, one-tool-per-Actor and immediate-stop mechanisms remain untested in this round. F1 is independent and cannot waive this gate.
