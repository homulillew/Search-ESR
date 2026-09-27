# Claim pipeline root-cause audit

## Material Passport

- Origin: user Claim Pipeline Root-Cause Ablation task; ARS experiment planning.
- Date: 2026-09-28. Status: offline audit; mechanisms UNMEASURED.
- Remote base verified after fetch: dadf69f1c5fb96491f4fd3a34e0ece3418878de3.
- Branch: experiment/claim-pipeline-root-cause; isolated worktree preserves the
  separate Random50 working directory and its uncommitted artifacts.
- Authority: TASK section50 overrides prior standing API authorization. Paid
  calls and new retrieval are prohibited during this preparation task.

## Existing pipeline and evidence

`llm_chat/recoverable_loop/engine.py::_claim_chain` sends OneGap, committed C and
full current Observation to Reader. It checks referenced windows, skips exact
normalized duplicates, then sends candidate + cited full Evidence to Grounding.
Only a supported verdict commits C. Neither selection nor Grounding mechanically
checks semantic entailment. Grounding sees no Gap/C but does see the proposed
interpretation of the source.

The existing reader prompt already requires full direct support, preservation of
subject/object/relation/time/quantity/modality/conditions/identity, and forbids
using Gap/C as evidence. The latest q435 failure occurred despite these rules.
Adding another instance-specific warning would not identify the information-flow
mechanism. Current Grounding also already contains specific counterexamples.

Historical `gap_evidence_claim_loop/FINAL_CONCLUSION.md` reports irrelevant
findings 67/110 observation-only, 1/46 Gap-conditioned and0/38 with Gap+C, with a
stricter post hoc strengthening correction. Its F3 reports a temporal overbinding
and source-identity problems after strong curated F1/F2 results. The separate
H2 run again admits an unsupported time binding. These are repeated observations,
not independent error distributions: q435 reuses related material. They motivate
cross-qid, cross-relation ablations; they do not identify any hypothesis as true.

`research_state_v2/FINAL_CONCLUSION.md` reports unsupported specificity in gap-led
admission (18/37). Those outputs include proposed open claims, so this must not be
pooled with authoritative C failures. Existing C still has real novelty/dedup value.
The proposed study changes where information is visible, not the authority of C.

## Baselines and unavoidable distinctions

A0 copies current Reader prompt/schema exactly. A1 uses exactly that same prompt
and schema, with C omitted from the generation payload; its later novelty review
still sees C. References to C in the identical prompt are retained so the only
A0/A1 intervention is input visibility. No extra safety instruction is introduced.

G0 copies current Grounding exactly, including its inherited memo/nationality
examples. The task's specific unchanged-baseline requirement takes precedence
over the general ban on adding case-specific examples. All NEW prompts contain
only abstract responsibilities. Baseline exceptions and byte hashes are explicit.

A2 changes both selection and formulation domains and requires a second call;
its effect cannot isolate prompt wording, call count, or evidence truncation from
information separation. G1 changes candidate visibility during evidence reading
and introduces an inventory bottleneck. A G1 advantage is evidence for the tested
structural pathway, not proof of a single psychological anchoring mechanism.
Inventory omissions/strengthening and true-positive recall must be reviewed.

## Bank audit plan

Inventory all named historical experiment lines, including immutable Git blobs
from branches not in this base checkout. Save source commit/path/row pointers and
hashes. Never switch the user's original worktree or copy future conclusions into
role input. Real observed source bytes and metadata remain exact. Any legacy
review-authored Gap/C context is flagged as such; synthetic source text and
newly authored negative claims cannot enter the primary natural-evidence bank.

36 packets with at most2/qid implies at least18 qids, stronger than the nominal
12-qid minimum. Target D12 + H-diagnostic12 + H-confirmation12, disjoint qids
between all subsets. E1/E2 use D and H-diagnostic; E3 reserves H-confirmation so
component selection does not consume its confirmation cases. This is a stricter
held-out split within the requested36–48 primary packets. If eligibility cannot
provide it with six relation families and positive/trap/no-new strata, stop and
report the shortage. No model call can fix deficient provenance or coverage.

Selection uses a source inventory, mechanical eligibility/dedup/qid cap,
source-relative relation labels, frozen quotas and fixed hash ordering. Reviewer
labels may establish strata before calls; outputs never affect selection.
Historical support judgments are audited from the observed text rather than
treated as truth. q435 is eligible only for D and has no success veto or exemption.

## Review and uncertainty

Codex performs offline semantic annotation. Review packets omit arm/hypothesis
and other-arm outputs. Role/input isolation is mechanically testable; full reviewer
independence is not, because the preparer knows the hypotheses and some old cases.
Keep that limitation explicit. Source-support review is separate from Gap/C
relevance/duplication review. Ambiguous language is insufficient for an unqualified
stronger claim; report a sensitivity keeping ambiguous cases separate.

No fresh outcomes exist. No production runtime, role, Search/Find/Open, H, Actor,
Closure, Finalizer, Gain policy or persistent-state schema will change. This task
ends after offline tests, provenance freeze, budgets and READY_FOR_AUTHORIZATION.
