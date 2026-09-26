# Need → Evidence Access

## Material Passport

Code experiment; frozen historical corpus and live DeepSeek inference. No human
participants. Single Codex semantic reviewer. Authorization: TASK.md plus user's
request for concurrent retrieval/API execution. Status: R0/R1 preregistration.

## Invariants and arms

Base remote HEAD fcd195f0f0c6299f00f155c2a6ae37e915fa177e, verified after fetch.
Provider/model unchanged: https://api.deepseek.com / deepseek-flash. Original
JSON-mode transport and provider-default inference parameters. max_retries=0,
240-second HTTP timeout, no output repair or failed-case replacement.

State remains Q + Claims + H. Each natural-language Need is derived from a prior
oracle candidate/condition and frozen for this probe. No separate Candidate or
Constraint input fields. All arms get exactly the same prefix, all real observed
windows, document catalog, recent attempts and two decisions/one action each.
No Writer, no Claim/H updates, no hidden evaluator stop on evidence success.
Actor STOP is terminal; API/schema/tool/control failure is terminal and retained.

A0: free current verification policy adapted mechanically to natural-language
Need and no Writer. A1: A0 + exact generic scope paragraph. A2: A0 with Find
removed (Search/Open remain); schemas mechanically restricted. A3: A0 + the
sentence “For this diagnostic only, the required evidence is located somewhere
in document Dk.” Only Find in Dk and Open of a window in that Dk. No Search.
A3 does not receive A1's paragraph, gold text, answer, offset or query.

BC+ corpus, global ranking, v3a old-document re-localization, lexical Find,
Open and handles are byte-identical production imports. Source content is data.

## Bank and primary denominator

See bank/SELECTION_RULE.md and SELECTION.json. K=10 Need families / 5 qids;
N=8 families / 8 qids; challenge=5. This falls below K target 12 / 6 and limits
generalization. All eligible fresh screened families used, no replacement or
duplicate inflation. Raw archival universe includes 396 distinct prefixes;
screening is relation-specific and semantic review excludes already visible
evidence. Same-qid and shared-prefix dependence precludes independent-trial
significance claims. Challenge never contributes to fresh gates.

R1: 84 trajectories, at most 168 model calls and 168 tool actions; actual calls
depend only on model STOP/failure. All attempted failures remain in denominators.
ExactEvidenceFoundWithin2Actions counts any actual returned evidence by action 2,
including compatible support or refutation and combination with prefix evidence.
Later transport failure does not erase evidence already obtained; report a
failure-free sensitivity separately. A topical page is not evidence success.

## Frozen integer gates

K: A1 at least 8/10 exact success AND at least 2 more successes than A0.
N: A1 must have at least as many successes as A0 (one loss is 12.5 pp >10 pp);
local lock must be 0/8 (one is 12.5%). All four conditions for scope gate.
A3 ≥9/10: oracle local access usable on this small bank; ≤7/10 triggers formal
R2. Exactly 8/10 is gray: no R2 this round, no reliability claim; describe errors.
Challenge cannot trigger/waive R2. A1 vs A2 comparison is descriptive, including
paired outcomes and actions; no post hoc equivalence test.

## Concurrency and isolation

Eight independent trajectory workers overlap HTTP and tool work. Each owns its
tool session, tokenizer, read-only SQLite connection and D/W registry. Each
trajectory's two decisions are strictly sequential. One shared GPU1 embedding
model and read-only FAISS index; GPU forward passes use a lock with original
single-query computation, avoiding altered batched numerics and memory peaks.
Local lexical retrieval, document reads, result construction and independent
HTTP requests run concurrently. GPU0's current free memory cannot hold another
16GB embedding model; no unrelated processes are stopped. Event logs record
start/end times for measured overlap. One-attempt behavior also applies to 429,
timeout, incomplete generation, parse/schema error, and unknown handles.

Freeze initial requests and their schema hashes before calls. Adaptive requests
are deterministic from the frozen builder and actual earlier result; persist
each exact request/hash before sending. Start ordering is a stable hash of
case/arm, independent of outcomes. Parallel cache-hit effects are reported, not
treated as semantic effects. Costs include cached/input ratio weighted by tokens,
cache occurrence, input/output/reasoning tokens, model/tool durations and wall time.

## Conditional R2

Only K A3≤7/10. Reuse identical A3 F0 trajectories; new F1 uses the same prompts,
schema, prefix, Need, gold D and budget. Only Find implementation becomes top
three non-overlapping lexical windows, 400 tokens each (≤1200 total versus Search
top5 ≤2000). Preserve first single-window result and locator scoring; no new
embedding, parser, heading boost or query rewrite. Freeze adapter and all requests
before F1 calls. If a baseline first action is Open, retain that case and report
Find-first sensitivity instead of resampling. Separate K/challenge results.

## Secondary audit and optional exploration

Offline only: all 318 previous formal windows and associated unchanged U1 outputs.
Denominator is direct evidence for an explicit Original-Question hard condition
outside current Need, not already covered by pre-update Claims. Score relation
opportunities as well as windows; support and refutation both count. Original
Question applicability, not merely related topic. Save each decision and reason,
admission coordinates, unsupported strengthening and duplicate outputs. No new
Writer call or prompt change; separate Discovery sensitivity from Verification.

At most one optional separately frozen exploration after a failed formal gate,
≤12 cases / ≤24 model calls, one mechanism. It cannot override any primary gate.
No Frontier, end-to-end, persistent-state changes, training or production changes.
