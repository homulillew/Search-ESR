# E1 public/internal reference contract repair audit

## Material Passport

Current user task: Contract Repair & Full Rerun. Remote fetched with prune and
confirmed at `99fbe47b9a6fa1bcfe628cb801cbd8e1ebcb29c5`; no newer commits.
New isolated branch: `experiment/claim-pipeline-contract-rerun`. This audit precedes
implementation. User authorization covers only corrected E1, at most96 calls;
E2/E3 are explicitly outside this task even if a mechanism gate passes.

## Fifteen audit answers

1. **window_ref** is the stable public W# handle in the observed research workspace.
   Model-produced evidence references must name a W# observed in that request.
2. **source_window_ref** identifies the underlying corpus/search window for harness
   integrity and provenance. It is not an alternative legal model citation.
3. Both were exposed because original `harness.inputs`/`evidence` deep-copied full
   internal Observation records. The full metadata were intended for source fidelity,
   but no public semantic projection separated machine bookkeeping from evidence.
4. A2 Selector already had a W-only field pattern and runtime membership validation.
   Its24 responses completed without namespace failures. This observation is
   consistent with a stronger contract; it does not alone isolate schema causality.
5. A1 and A2 Formulator produced evidence_refs under a generic nonempty-string item
   schema while viewing two identifier fields. Two A1 and six A2 outputs used the
   underlying alias alone or alongside W#. A0 happened not to fail in this sample.
6. The schema admitted any nonempty reference string; runtime admitted only observed
   window_ref values. Thus structural schema validity did not imply membership.
7. All8 attempted failures are documented in the original contract audit. Each
   offending ref equals a source_window_ref in that request's actual input.
8. No truly invented ref or blank factual statement caused those8 failures. The
   ninth failed chain was an unsent dependency after the frozen halt.
9. Keep window_ref,doc_ref,title,url,text exactly. These preserve public identity,
   source/publisher attribution and complete visible content. Also preserve an
   **optional existing date field**: it is source-date metadata, not a mechanical
   identifier. Six E1 records contain it; the q1094 record does not repeat it in
   its visible body. Removing a previously visible source date would introduce a
   semantic-metadata deletion unrelated to namespace repair. Do not add dates where
   absent or reinterpret dates as event dates. This exception is common to all arms.
10. Hide source_window_ref,docid,document_sha256,text_sha256,offset,end_char, and any
    other non-allowlisted fields. Hashes/offsets/corpus IDs support integrity/replay
    inside the harness; neither relevance selection nor factual formulation needs
    to choose among them. Original records remain intact in the frozen bank and
    private request-side provenance records.
11. Post-hoc mapping would change which historical outputs satisfy the frozen
    contract and conceal actual model behavior. Old invalid outputs must remain
    invalid under the new schema; no alias normalization or output repair is allowed.
12. Reusing successful old outputs while rerunning only failures would mix different
    representations/contracts and select survivors. Run all24×3 chains freshly,
    with at most24 dependent formulation calls. Empty selector outputs are valid.
13. H1/H2 information-flow treatments remain identical: A0 Gap+C, A1 Gap without C,
    A2 selection with Gap+C followed by evidence-only formulation. The common
    public view and reference schema are the only shared interface intervention.
    Keep prompts, bank/atoms/splits/C/Gap, rubric, gates and model parameters exact.
    Do not compare old/new semantic rates as a causal reference-repair estimate.
14. No production file is needed. Add a versioned adapter under `contract_rerun/`
    and reuse immutable original DAG/metrics/review export. The old diagnostic
    code, freeze, run001 and ROOT_CAUSE_CONCLUSION.md also remain untouched.
15. No persistent semantic state or new factual field is introduced.

## Planned implementation boundary

Use one allowlist projection for Observation/Evidence at the semantic-port boundary.
Save the original complete internal payload privately; the model request contains
only the public projection. A2 receives the full selected text, never a clipped
span or selector reason. Original source evidence remains the review unit.

For A0,A1,A2 Formulator and G1 inventory schemas, add W-pattern,uniqueItems and
nonempty refs. Bind each claim-producing request's ref items to a dynamic enum of
that request's public W handles. Keep selector schema byte-identical; its existing
W-pattern plus runtime membership remains. No other schema field changes. G1 is
covered by offline contracts only; this task sends no Grounding calls.

The dynamic enum derives solely from public handles, never evaluation labels.
Retain an independent runtime membership check after JSON-schema validation.
Every semantic prompt is reused byte-for-byte; no W-only reminder is added.

Freeze new request/schema/view hashes before paid calls. Use the same DeepSeek
Flash configuration,initial concurrency72,max_retries0,at most96 calls and the
same failure stop. Full valid72-chain completion is required before blind semantic
review. Any missing chain leaves H1/H2 inconclusive and forbids semantic scoring.

**Mechanical provenance must stay in the Harness. Semantic models should operate
only on stable public handles.**

**Do not ask a language model to choose between two machine identities when the
Harness already knows they are aliases.**
