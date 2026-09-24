# V1 prefix-only review audit

Codex reviewed the 90 arm-masked packets in `REVIEW_PACKETS.json`. The helper
`transcribe_review.py` records the per-item and per-known-field decisions in
`REVIEWS.json`; it is review transcription, not a model call. The reviewer used
the original question, explicit provisional H, visible W, and frozen Gap and
requirements only. The private arm mapping was not used to assign labels.

## Decisions that matter to the gate

- A declarative assertion that the candidate *satisfies* a missing relation is
  unsupported even when the candidate name itself came from H or W. Thus an
  `open` status does not make the assertion epistemically safe. The one
  already-observed background claim is the 2005 film/director fact in packet
  64, item 2. Declarative claims without a supported test path receive no
  coverage credit under the frozen rubric, even if they echo a clue.
- Packet 47 conflates the observed publisher with the developer. Packet 75
  turns an observed title in Dodrill's biography into *Game B* without support.
  These are VP1/VP2 semantic failures despite structurally valid outputs.
- Packets 14, 34, and 42 test the program's run, runtime, network and
  characters but omit a path to verify the Argentine release name; the third
  coverage requirement is false.
- The poker packet 12 includes an irrelevant Annie Duke detour, but explicitly
  leaves that possible link under test; it is overextended, not a bound answer.
- Packet 9 and 77 ended with abnormal model output; packet 76 had one request
  in flight when the process was interrupted. The interrupted request was
  recorded as failure and never retried. The remaining unrequested cell was
  issued once. All three failed cells retain zero coverage and testability.

## Interpretation limits

These 30 cases are correlated siblings from 11 questions; cell counts are not
independent trials. Specificity and coverage depend on one reviewer's
semantic judgments. The C0 coverage score is deliberately strict about
unsupported answer assertions; the V1 gate chiefly uses C0's paired premature
specificity and checks TestCard coverage separately. This stage does not show
that a TestCard changes query policy, evidence binding, or Actor behavior.
The binding-rate denominators also differ by output schema: C0 uses one
reviewed factual proposition per Claim, while C1/C2 count individual known
fields plus any unsupported condition-only exact relation. Cross-arm
binding-rate magnitudes are descriptive; the case-level paired comparison is
the more comparable specificity result.
