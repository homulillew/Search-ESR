# Belief → Need convergence — preregistered protocol

## Scope and material

Task: TASK.md. Base verified remotely: 99202167ab1c693514ef87534ca9f346f0813638.
Persistent state remains Q + verified Claim strings + provisional H. No tool,
retriever, Writer, production schema, ontology, gating or learning changes.
Only P4 receives an evaluator oracle. P3 passes one ephemeral issue within its
same-model two-call decision; no issue enters subsequent Belief/history.

Inventory: 437 exact QCH states / 10 qids from real archived research histories.
Five named bad-case qids are challenge only. Other apparent new questions have
no archived Belief, and old hand-built packets are not natural primary states.
The available less-exposed primary pool therefore has only 5 qids. There are
24 development states (5 qids), 10 challenge states (5 qids), 12 coverage pairs,
4 H pairs. Deduplication yields 55 unique runtime Beliefs, 275 output decisions,
at most 330 calls. One response per unique Belief/path; shared diagnostic
memberships reuse the response. All banks, prompts and labels frozen before calls.

The development set is less-exposed, not question-independent fresh data. Some
actual verification episodes start with a historically supplied candidate; these
are tagged by original V-arm provenance and are not claimed as autonomous H
discovery. Some G4/G5 seeds were source-backed reviewer-normalized checkpoints.
Controlled Delta B/H-removal projections are not natural primary states.

U4 has 1 genuinely audited one-gap state, below target 8. 21 unconsumed reserve
QC groups span only 5 qids and remain uncertified pending support/coverage review.
Targets 36 states/12 qids and dev 10 qids are not met. Larger same-question counts
cannot cure this. No formal confirmation can meet its minimum 8 fresh qids.
These shortages will not be hidden or relaxed after seeing results.

## Paths and execution

P0 mechanically removes closure from historical Direct Frontier and uses research
output. P1 uses task coverage-aware instructions; P2 adds only silent checks.
P3A extracts one ephemeral gap, P3B formulates it. P4 oracle diagnostic is excluded
from production selection. Every path shares identical QCH. Runtime payload has
no source window, qid, stratum, hard-unit label, gold answer or future observation.

CONFIG.json fixes provider/model, temperature 0, JSON mode, 4096 output tokens,
240-second timeout, 8 parallel HTTP workers, retries 0, horizon 1, no tools.
P3B depends on P3A and is not sent if A fails structurally. Other calls are
independent and deterministically shuffled to spread transient provider effects.
Each request is persisted before HTTP, raw response immediately afterwards,
with hashes, run HEAD, timings, usage, cache hit/miss and errors. Interrupted
attempts are retained; no resubmission. Authentication rejection stops queued
requests. Transport/schema/length failures count as strict failures, with
semantic dimensions reported separately as not assessable. No best-of or retry.

## Review and metrics

See RUBRIC.md. One Codex reviewer reads actual QCH and output; no statistical
independence or blinded reviewer claim. Any valid local frontier is accepted.
Primary dev, challenge, controlled deltas and unconsumed reserve stay distinct.
Report V/S/P/W/I/H/A, strict validity, per-qid counts, U1/U4/U5/U6, P3 issue
validity and issue-to-Need errors. Cost includes both P3 calls and failures.
Cache rate = sum(hit)/sum(input), not average per-request percentages.

Coverage-pair correctness: A strict valid, B strict valid, B no longer asks the
exact covered local g. A may choose another valid gap. Separately report the
activated-g subset (A actually asked g) and whether B moves away. High pair
correctness without activation is not evidence of a causal frontier switch.
H safety compares P errors on the four same-Claim A/B sides; specificity is
qualitative. Oracle gap is canonical per unique Belief, not chosen per pair.

Development integer gates: strict >=21/24; P <=1/24; S <=1/24; W <=2/24;
U4 >=1/1; coverage pairs >=11/12; U1 >=6/7. Meeting these is provisional numeric
readiness only: inadequate qid/U4 coverage blocks final PASS/NEAR-PASS.
Select P0–P3 lexicographically by strict, fewer P, fewer S, U4, Delta, fewer W,
then cost. P3 requires >=2/24 improvement (8.33pp) over best single call, or
an explicitly documented critical cross-qid mechanism fix, never challenge-only
aggregate gains. Diagnostic P4 is excluded.

## Finite iteration and stopping

If no production path clears numeric dev gates, inspect every failure of the best
path with true input, provenance and valid gaps. Freeze one mechanism, rationale,
minimal intervention, desired improvement and possible regression before creating
one variant. Exploration <=16 states / <=8 qids, baseline responses reused when
identical. At most 4 cycles; stop when qualified fresh material is exhausted.
At least one evidence-led exploration is authorized despite initial bank shortage.
Do not spend four cycles repeatedly optimizing already exposed material.

Formal confirmation requires >=24 new states / >=8 fresh qids and the task's
PASS/NEAR-PASS gates, excluding design failures and challenge. This material is
currently unavailable. Report EVIDENCE_EXHAUSTED, not replicated success.
Only qualified NEAR-PASS/PASS permits closure controls and offline autonomous
simulation. No certified full-coverage control is currently available; closure
is not validated. End-to-end search is outside this experiment.

All annotation corrections after calls are append-only, with original/corrected
sensitivity. Historical experiments are byte-hash protected and never rewritten.
