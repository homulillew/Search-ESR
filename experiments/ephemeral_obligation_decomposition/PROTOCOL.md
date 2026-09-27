# Source-Anchored Task Skeleton

## Material Passport

Mode: code experiment; primary unit: unique original question; reviewer: single Codex reviewer.
Base: `fc0746930edc4ad8aad4c8a04a5f2a138d1b5082`. Task specification: verbatim `TASK.md`.
Only Q → Task Skeleton. User authorization covers the scheduled provider calls.

## Design and separation

E1: 10 exposed unique questions × D0/D1/D2 × 2 independent responses = 60.
E2: 12 repository-experiment-unexposed questions × D0/D2 × 2 = 48,
only after both E1 gates pass. All 22 questions and references freeze before E1.
Same Q and mechanical Source Units across arms. System prompts are the exact
fenced text of task §§15/17/19 with CRLF normalized to LF. Prompts and splitter
are byte identical in E1/E2. No tools or research-state inputs. No arm names in
provider input. No inference about foundation-model training exposure.

`select.py` freezes the eligibility rule and seed before selecting fresh cases.
The exposure audit conservatively excludes explicit qid fields/lists, even
candidate inventories, and matches original-question text across repository
text and local experiment work. Raw corpus distribution is not experimental
exposure. No answer or retrieval content is used in reference construction.

## Source address space and mechanical validity

`source_units.py`: original bullet items are whole units; otherwise punctuation
sentence boundaries and semicolons split, with fixed initial/abbreviation
exceptions. No comma or conjunction split. Text and end-exclusive character
offsets are verbatim, with all non-whitespace characters retained. An initial
question can share its sentence with descriptive material; exact spans allow
separate addressing. Mechanical units are not reference requirements.

Output: exactly `requirements`, 1–12 nodes. D0: exactly nonempty `requirement`.
D1: exactly nonempty `requirement` and nonempty `source_spans`. D2: exactly
nonempty `source_spans`; no generated labels/prose. Spans have exactly `unit`,
nonempty `text`, and optional positive integer `occurrence` (one-based).
Unicode NFC + whitespace normalization + exact substring; repeated normalized
substring requires occurrence. No fuzzy matching or repair. Schema validity
and exact-anchor validity are reported separately and jointly.

## Frozen semantic reference

Human/Codex Q-only references specify material units, critical invariants,
question-inherent dependency checkpoints, forbidden inferences, answer target,
and grouping guidance. They do not prescribe wording or exact node count.
Reference spans are evidence of what Q asks, not evidence that a research fact
has already been established. Requirements expressing question-specified
existence are legitimate. Neither Claims nor old Dynamic-O labels enter review.

Each material unit: critical weight 2, material weight 1, minor weight 0 in the
primary material-weighted coverage. Coverage is binary fully preserved = 1,
partially preserved/missing/corrupted = 0; partial details retained in reasons.
Critical coverage uses critical units separately; minor is descriptive only.
All omitted modifiers inside a reference unit must matter to that unit's
meaning before marking it incomplete. Insignificant articles or style changes
are accepted. Multiple complementary nodes may jointly preserve a unit.

Invariants are scored for actual corruption, not mere omission (omission is
coverage loss). Categories: relation_argument, role_identity, temporal,
ownership, numeric. Critical structural corruption is the union of these five
categories per response; relation/role/time union also reported explicitly.
Invented semantics is new semantic content or strengthening, not ordinary
question-required existence. Dependency preserved means both the described
upstream referent/relationship and downstream attribute remain recognizable.
It does not require explicit edges, order, or one node per checkpoint.

Granularity: complementary clues of ONE referent/event may be grouped.
Independent episodes collapsed into a generic whole-question unit are severe
broadness. Several independent referent-identification chains collapsed in one
node are harmful merge even if all words are present. Merely large node count
is not fragmentation. Harmful split requires loss of relation context or
unresolvable roles, not a pronoun whose referent remains clear across nodes.
An explicit original-question referent can be resolved across groups; no new
role binding may be invented. Record acceptable/too_broad/over_fragmented/mixed,
severe flags, node numbers and reasons. Apply one rubric equally across arms.

Strict = jointly mechanical valid AND critical coverage 100% AND weighted
material coverage ≥90% AND no critical structural corruption AND no invented
semantics AND dependency recall ≥90% AND no severe broadness/fragmentation.
D1 anchor entailment is a separate mechanism outcome, not an extra strict gate
absent from task §39; a skeleton may be semantically correct but poorly anchored.

## Review order

First pass: masked packets containing only original Q and candidate task units.
D0/D1 display prose only; D2 concatenates selected exact spans with newlines.
No arm, replicate, provider reasoning, performance, provenance or aggregate.
Single reviewer knows the question/reference and may infer extractive style;
blinding is partial, not an independent or fully blind evaluation.
Per response record every material-unit coverage, invariant violations,
dependency checkpoint result, inventions, granularity, ambiguity and reasons.
Commit all first-pass labels before revealing provenance or calculating gates.

Second pass: reveal arm and anchors; score exact validity, D1 node-level
fully_supported/partially_supported/unsupported, D2 compatible grouping/harmful
merge/harmful split/coverage omission. First-pass labels remain immutable.
Reference defects trigger explicit quarantine; no silent reference changes or
denominator deletion. Sensitivity analyses never change the registered gate.

Replicate-pair review compares semantic sets (D0/D1) or span grouping (D2).
Labels: same_structure, compatible_structure, different_but_valid,
one_valid_one_invalid, both_invalid. Primary stability requires both strict
valid plus same/compatible. Raw both-strict fraction is separate and is the
gate criterion. Different valid decompositions receive strict credit.

## Denominators and gates

All planned slots remain denominators, including unsent, timeout, length,
invalid schema/anchors. No completed-response-only primary result. No content
means zero coverage/dependency; diagnostic corruption needs observed content
and is not fabricated for missing outputs. Exact-anchor failure does not erase
otherwise reviewable prose, but forces strict failure.
Primary coverage/dependency rates are macro over responses (equivalent to equal
weight per qid given fixed two replicates); micro numerator/denominator also
reported. Critical coverage gate requires every planned response 100%.
`GATES.json` is the executable threshold contract. E1 comparison gate requires
D2 corruption ≤ D0 −10pp OR absolute ≤5%, AND coverage loss vs D0 ≤5pp.
E2 requires strictly lower D2 corruption than D0; a zero–zero tie fails that
directional condition. No post-result relaxation. Gate failure stops paid work.
No p-value-based gate; descriptive small question bank, clustered replicates.

## Execution and cost

DeepSeek `deepseek-flash`; temperature 0; JSON mode; omit max_tokens; retries 0.
Max 8 concurrent independent requests; mixed deterministic schedule. First
scheduled request is the only authentication canary and counts in 60/48.
Timeout 240 seconds per HTTP inactivity operation, not a wall/token cap.
Contract/access/billing HTTP 400/401/402/403/404/422 halts unsent queue; retain
in-flight calls and all failures. No overwrite, resume, replacement or retry.
Retain raw request/response/status/final content/reasoning/usage and timing.
Reasoning is included in completion, never added twice. Report token-weighted
cache hit rate, missing-usage calls, median/P95/max latency and peak concurrency.
Uncapped output has no promised cost ceiling; no invented currency price.

## Stop and downstream boundary

E1 failure: stop. E2, if eligible, is the last stage regardless of outcome.
No prompt revisions, state alignment, selection, Gap, retrieval, Writer, Claims,
lazy expansion, DAG/requires, Binding IR, or extra sample calls in this run.
Preserve all historical experiments and unrelated working files.
