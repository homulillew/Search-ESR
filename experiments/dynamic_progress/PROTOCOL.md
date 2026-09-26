# Protocol: Dynamic Research Progress

## Scope and causal comparison

Base fafe06019326cef35aa40f6e6092bbb5c725306f; new branch experiment/dynamic-progress-blockers. P0 selection and materiality labels are completed before new calls. See DESIGN_AUDIT.md and bank/SELECTION.json. State is unchanged Q, Claims, Hypothesis. Progress is ephemeral. No persistent requirement map. Q+Claims only for all P1 inputs; indices are one-based, statements preserved verbatim. No model sees private labels.

Primary:24 novel Q+Claim inputs relative to prior F1,10qids,max3/qid. These are historical checkpoint variants, not independent new questions or a new U1 cohort. Challenge:all24previous F1 States separately,10qids. FULL sensitivity:12mechanically selected primary States,10qids. Existing legacy/reviewer-normalized ancestral Claims are neither cleaned nor rewritten.

## Arms / sample / execution

R: byte-identical old Goal Reviewer prompt, resolved/residual. B: task's minimal dynamic blocker semantics, 1–3gaps, strict missing/partial/conflict, main closure refs. Same numbered Q+Claims. Each independently submitted twice; provider defaults unchanged, no seed/best-of/retries. FULL: complete material requirements with supported/missing/conflict, independent diagnostic only, two calls per selected State; reuse corresponding B outputs.96primary+96Challenge+24FULL=216requests. Globalworkers4; exact requests committed; deterministic hash order interleaves arms. P1/FULL have0tool/Writer/Frontier calls, horizon1. HTTP240s is an operation timeout, not a total wall-clock cap. No failed response repair or replacement; auth failures latch subsequent submissions. All planned slots retained. Record raw response, reasoning proxy, input/output, hit/miss tokens, elapsed seconds and git SHA. Provider deepseek-flash at api.deepseek.com, existing credential configuration, JSON object transport.

## Pre-call gates

Primary has21unresolved/3resolved States; per arm42unresolved and6resolved submissions. B must meet all: false closure<=4/42; valid blocker presence>=36/42; blocker precision>=90%; correct closure6/6. Precision is a semantic content measure; status/ref fidelity and strict validity reported separately, not silently conflated. B cannot qualify with material unsupported-premise or genuine Claim-conflict misses recurring on >=3checkpoints across>=2qids, even if rounded aggregate gates pass. Schema/failure slots cannot earn valid presence or correct closure. Also report failure-inclusive wrong completion and semantic closure witness, so provider failure is not credited as safe unresolved.

Challenge comparison: historical48StateOnly Direct outputs are regraded for completion under newly frozen materiality labels, no new Direct samples. B completion accuracy must exceed Direct by>=10percentage points and avoid >=3checkpoint regressions across>=2qids (checkpoint regression = fewer correct B completions across2replicates than historical Direct). This is a noncontemporaneous diagnostic, not randomized fresh Direct-vs-B evidence. Primary gate is mandatory regardless of Challenge success. Report perqid and paired replicate categories. No p-value gate or independence claims; small resolved stratum2qids explicitly limits generalization.

## Subsequent stages

If P1 passes all gates, freeze P2D/O/B on mechanically chosen primary unresolved cases, both actual B replicates retained regardless of quality. D uses historical Direct prompt unchanged; O/BSelectorNeed-only, noSTOP, no tools. Freeze P3 separately on12–20actual pre/postWriter transitions>=6qids, including resolved-blocker/conflict/incidental/finalclosure. No synthetic postClaims. P4 only after positiveP1–P3:8–12heldoutcases>=6qids,<=3decisions/oneactioneach,frozenv3aSearch/Find/Open/U1. Never cross failedgate to complete architecture. Unexecuted metrics are unmeasured.

A failed major gate permits exactly one separately planned/committed exploration,<=12checkpoints/24calls, observed dominantfailure. It cannot overwrite primary or unlock laterstages. Independent FULL sensitivity still runs regardless of gate.

## Integrity and cache

Runtime validates only JSON/schema/index existence/structural consistency. All support/materiality decisions are offline. Hash(Q,Claims) cache reuses Progress when only Hypothesis,Workspace,attempts change; Claim mutation invalidates. No new refresh trigger. Unit checks prove software behavior only; P3/P4 required for empirical semantic adequacy. Historical tracked files pinned and rehashed; new experiment only. No changed retrieval, Writer, State schema, question/corpus or provider. Commit/push final records.
