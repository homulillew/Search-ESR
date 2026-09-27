# E2 next plan — no execution authorization in this task

## Decision and prerequisites

E1 construction gates both failed. Keep A0 as the descriptive construction baseline;
do not promote A1/A2 or open H-confirmation. A separate E2 can still test H3:
whether a candidate-visible Grounder over-admits a plausible strengthened claim,
and whether a source-only commitment inventory followed by Coverage reduces that.
This is an independent diagnostic, not evidence that A2 succeeded.

Current task section42 explicitly excludes all E2 paid calls. **Executed:0.**
No E2 request freeze or candidate execution bank was created. The following is a
concrete offline plan for a later explicitly authorized task.

## Fixed candidate opportunities and budget

Apply the original deterministic `freeze_e2_candidates` rules to reviewed run002
outputs plus the10 frozen actual historical candidates. Preserve every origin,
full source and source-relative label. No synthetic negatives or added retrieval.
Select≤15 positives and≤15 negatives per D/H-diagnostic split by ascending pair hash.

The current offline estimate is:

| Split | Supported | Strengthened negatives | Total |
|---|---:|---:|---:|
| D | 15 | 3 | 18 |
| H-diagnostic | 15 | 2 | 17 |
| Total | 30 | 5 | 35 |

There are15 distinct source inventories. Thus G0 needs35 calls, G1 inventory15,
and G1 Coverage35: **85 calls** if later authorized. This is an estimate computed
from actual deterministic candidates, not an authorization or a reason to spend
unused E1 budget. Recheck and freeze actual hashes before starting.

The D negatives are variations of the q435 temporal issue, and the two H negatives
come from one q673 attribution window. All four newly generated negatives are
ambiguity-flagged. The bank supports a small source-relative admission diagnostic;
it cannot establish broad cross-family Grounding reliability. Report ambiguous
admission separately. Zero G0 false admissions makes H3 inconclusive.

## Arms and isolation

- G0: original Candidate+full Evidence Grounding prompt/schema, unchanged.
- G1 inventory: full public Evidence only; no Candidate, Gap, C or labels.
- G1 Coverage: Candidate+frozen inventory only; no raw Evidence, Gap/C or labels.
- Build each source inventory once for its exact Evidence/model/prompt contract.
  Share only within this new E2 stage, retaining all linked pair IDs privately.
- Review inventory support and omissions separately. Inventory agreement is not
  itself evidence that the candidate is true. No response mapping or repair.
- Use public-view/W schema for inventory, preserving source title/url/date/text.
  Inventory and G0 inputs have no historical C; therefore the run002 legacy-C-ref
  display exception does not enter these E2 roles. Audit candidate refs as well.

## Gate and execution policy

Retain original H3 thresholds: pooled FAR relative reduction≥50%, G1 TPR≥85%,
beneficial paired and qid-weighted directions, strict same direction and TPR guard
on H-diagnostic. Undefined denominators or any failure prevent a pass. Do not lower
the gate because the new construction hypotheses failed.

Freeze source HEAD, bank/label hashes, candidate list, semantic prompts, schemas,
model/config, sample count,85-call ceiling, inventory sharing, concurrency and
failure policy. Same thinking-enabled/high DeepSeek Flash configuration. Independent
G0 calls and inventories may run together: initially up to50 requests, then dependent
Coverage as inventories finish, bounded by the available account quota and a proposed
70-request pool. No paid load test. Account for other processes before freezing.
Keep original timeout settings and max_retries0. On any failure halt unsent requests,
retain in-flight outputs, and stop the gate; no backfill or resume.

Report FAR/TPR with numerators/denominators, ambiguity stratum, qid grouping,
inventory omission/strengthening, cache hit/miss, complete usage coverage, actual
concurrency, latency, wall time and every failure. No production modifications.

E3 requires a separate future decision and authorization. With H1/H2 unsupported,
only a valid H3 result could support studying an A0+G1 integrated diagnostic under
the original selection rule. H-confirmation remains unused now.
