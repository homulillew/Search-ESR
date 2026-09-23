# State v2 contract

| Layer | Contents | Owner |
| --- | --- | --- |
| L0 TaskSpec / WorldLedger | Raw question, near-verbatim anchors, append-only actions, observations, D/W refs, provenance | Harness |
| L1 Verified semantic state | Claim status and exact observed evidence refs | Verifier decides; Harness commits and versions |
| L2 Research structure | Gap ancestry and closure rule, Claim definition and parent Gap | Model proposes through dedicated admission; Harness validates |
| L3 Working policy | Provisional hypothesis, active eligible Gap, expected source type and target | Model chooses; Harness validates |

Observation never creates a Claim. New Claims come only from Gap-driven Claim Admission, begin `open`, and cannot be marked supported in that same operation. The Evidence Router references existing Claim IDs only and cannot set status or alter Gaps. Closed Gaps cannot remain active. Hypotheses are never promoted to verified truth automatically.

`DerivedFrontier` is computed from open Gaps with satisfied prerequisite Claims and no rejected linked hypothesis. The model may choose one eligible Gap; it cannot rewrite the frontier. The Actor receives a compact ControlProjection with separately marked VERIFIED, OPEN, WORKING HYPOTHESIS, and ACTIVE RESEARCH GAP sections.
