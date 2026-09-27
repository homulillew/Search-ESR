# E1 — Completed, safety gate failed

## Material Passport

Study: Claim–Requirement Support Alignment. Frozen baseline fc799239; bank selection df671a2b; Gold d0e51d05; requests3bb5c12a; fresh E1 authorization acf43ea2; raw responses and semantic review sealed/committed at feb7a780 before aggregation. All96 planned calls completed. No retries, replacements, prompt edits, model switches or additional model calls. E2 not entered.

## Primary results

| Metric | S0 binary | S1 typed + scope | S1 absolute gate |
|---|---:|---:|---|
| Support precision | 27/27 =100% | 35/38 =92.11% | **FAIL**, >=95% |
| Support recall | 27/36 =75.00% | 35/36 =97.22% | PASS, >=90% |
| False promotion, all Gold non-support | 0/128 =0% | 3/128 =2.34% | PASS, <=5% |
| Correct scope among true selected support | Not elicited | 32/35 =91.43% | PASS, >=90% |
| Relation/source-binding corruption | 0/48 =0% | 3/48 =6.25% | **FAIL**, <=3% |
| Candidate-branch mixing | 0/48 | 0/48 | PASS, <=2% |
| False-full assignment hazard | Not identifiable from IDs alone | **2 outputs** | **FAIL**, must be0 |
| Schema validity | 48/48 | 48/48 | PASS, >=95% |

S1 also fails the comparative rule: both promotion rates are within the preregistered near-zero band, but2.34% is greater than0%, so S1<=S0 is false. No erroneous0<0 comparison was used.

The safety stop does not depend on recall. This is TASK24 Case D, not the safe-but-conservative Case C. E2_safety_entry_pass=false; no E2 approval was sought or calls sent.

### Denominators and scope

The all-non-support promotion denominator128 includes non-support Claims in positive cells. On Z only, S1 promotion is3/50=6%;3/24 negative outputs contain false support (two Euler replicates and one book-only replicate). This additional view exposes concentrated risk without replacing the frozen primary denominator. All96 outputs remain counted; none failed transport or schema.

The two E1 false-full hazards are **coverage risks**, not observed residualizer closures. They occur in the same A20 parent at two replicates:2/48 planned typed outputs, or2/38 non-full-parent typed outputs. E2 false subtraction and actual false FULLY_SUPPORTED are **unmeasured**, not zero.

## Useful positive signal and its limit

S1 recovers35 rather than27 of36 true support Claim-slots (+22.22 percentage points recall). In the P stratum, S0 recovers11/20 true supports (55%) versus S1 20/20 (100%); exact P support sets improve7/14→14/14. S0 misses founder/graduation components, artist death/city facts, one two-author fact and the government-mechanics contribution. Thus explicit typed/scoped prompting helps recognize partial evidence on this bank.

That benefit coexists with three false support promotions and scope overreach in a parent whose selected support set is otherwise correct. Selecting the correct Claim IDs does not establish a safe subtraction boundary. The intervention combines role typing and copied scope; this design cannot isolate which component causes the recall gain or the errors.

F controls: S0 recovers16/16 and exact10/10; S1 recovers15/16 and exact9/10. One S1 output labels Jerry's Australian nationality as binding rather than substantive while using a joint nationality/champion span for C2. The full current Claims ground the joint span under the frozen convention, so it gets scope credit; an E2 typed packet that forbids binding from satisfying a condition may expose an interface inconsistency. That downstream behavior was not tested.

## Error cases

| Cell / output | Observation | Error |
|---|---|---|
| A15 G14R4, S1 r1+r2 | Euler biography gives his birth/identity; no target-book reference observed | Both outputs promote C1 and copy attributes of the purported cited figure. The governing book-reference relation is missing. |
| A13 G11R5, S1 r2 | Book exists, but no journal article is observed | C1 book-publication anchor promoted to article-relation support under the frozen primary reference. Predeclared ambiguous boundary. |
| A20 G21R4, S1 r1+r2 | Diary/manual Claims give technology, religious mechanics and Ottoman changes | C4 spans in both outputs, and C7 in one, add the complete playable-European-nation qualifier. No supplied Claim states those qualifications. Union of fragments purports to cover the whole Parent. Predeclared mechanics-scope ambiguity. |
| A21 G23R2, S1 r2 | C1 directly says Jerry is Australian | True support is demoted to binding; one missed support. |

Relation/source-binding corruption counts the Euler book-reference drop twice and the book-only article-relation drop once. It does not imply that their biographical/publication facts are false in isolation. A20 qualifier overreach is counted separately as scope overreach; it is not double-counted as an argument transfer.

## Historical cases and transitions

- **Euler:** reproduced in S1 both replicates; S0 correctly returns no support both times.
- **Generic SPS:** neither arm promotes generic symptoms to the particular first case. S1 labels them background.
- **Patient nationality/report country:** both S1 outputs restrict C7 to clinical-history fragments; neither claims reporting geography or country-at-establishment history. S0 selects C7 but has no scope to inspect.
- **Memorandum/letter date:** neither arm transfers the covering memorandum date to letter composition or invents accession timing.
- **Coder/other teammates:** neither arm uses Jerry's nationality or teammate names as the other-two same-country relation.
- **Alma mater/building:** no false substantive support in either founder snapshot; secondary context labels vary.
- **Artist/charity:** no substantive promotion with either artist-only or artist-plus-partner Claims.
- **Kwon/Ding:** both arms change from no support at G05R2 to C5 at G06R2, without merging the founder branches or transferring the 2025 Kwon family statement to2019 Ding.
- **G17→G18 clinical case:** both arms change from no support to C7.

Both required E1 support-set transitions are correct in both replicates (4/4 transition opportunities per arm). This is a descriptive E1 observation; **E2 residual state discrimination is not measured**.

## Ambiguity, replicates and limitations

All six predeclared ambiguous cells remain in primary scoring. Removing them only for frozen sensitivity gives S1 precision21/23=91.30%, recall21/22=95.45%, relation-binding corruption2/36=5.56%, scope21/21 and no remaining false-full hazard. Thus the precision safety failure persists outside ambiguous references; no Gold label was changed to improve a result. A20 is the sole source of false-full hazards, so that specific count is reference-sensitive and is not presented as ambiguity-independent evidence.

S1 replicate1 precision18/19=94.74%; replicate2 17/19=89.47%. Each has one false-full hazard. Neither replicate provides a safe alternative; no best-of selection is allowed. Support-set agreement between replicas is S0 23/24, S1 22/24. Full parsed-output agreement is S0 23/24, S1 9/24, reflecting large secondary-role/scope variation.

Secondary S1 measures: role accuracy109/164=66.46%; binding recall45/56=80.36%; background accuracy28/66=42.42%; exact substring validity56/56=100%. Perfect literal copying does not establish evidence entailment or a valid governing relation. Background-to-support promotion is0; all3 false promotions originate from Gold binding context.

24 cells share16 natural snapshots and9 questions, with two correlated replicates. Selection is task-enriched and based on familiar historical cases; at least10-qid target was not met. This is not fresh generalization, a random prevalence estimate or96 independent questions. Review is one task-familiar reviewer; IDs and replicates were masked, but output structure revealed binary/typed format. Provider reasoning was never read for semantic review. Primary labels and ambiguous-cell sensitivity were fixed before calls. Semantic scope precision allows sound narrower spans and declared joint support, so it is not a measure of complete condition-coverage recall.

## Execution and integrity

96/96 sent and returned; peak concurrency8; wall133.03s; median6.50s, p95 35.50s, maximum52.72s. HTTP errors0, schema failures0, timeouts0, retries0. Prompt tokens79,812; output224,626 (provider-reported reasoning217,906); total304,438. Cache hits43,904, misses35,908: **55.01% token-weighted input cache hit rate**. All96 calls have complete consistent usage. No monetary cost was inferred from an unverified price.

20,343 historical files unchanged. Frozen requests, prompts, Gold and rubric unchanged. Raw-response reparsing, accounting and sealed-score replay are identical. Preparation INTEGRITY/STATUS files remain immutable snapshots; current checks are in analysis/E1_INTEGRITY.json and actual accounting in analysis/EXECUTION_ACCOUNTING.json.

**Decision: stop after E1.** No E2, Search, Query, Probe, Find/Open, Writer, Bootstrap or persistent-state changes. The next research decision should address relation-conditioned support/qualification safety before permitting support-based subtraction or closure; no follow-up experiment was run here.
