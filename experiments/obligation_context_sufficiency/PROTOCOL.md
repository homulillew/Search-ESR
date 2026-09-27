# Local Obligation Context Sufficiency — frozen protocol

## Material passport and scope

User-defined development mechanism experiment, 27 unchanged natural snapshots, 10 exposed question clusters. Tested model DeepSeek Flash; one Codex reviewer/executor, familiar with previous questions/references and context reconstruction. Artifact masking does not imply independent reviewers or erased familiarity. No new retrieval, Gap, Writer, persistent state, candidates, decomposition, or loop. Historical files read only. Existing explicit user API authorization applies to exactly 216 planned slots and no further experiments.

Only Recent Context array contents differ. One exact TASK §26 system prompt, one input schema, one output field obligation, temperature 0, JSON mode, omit max_tokens, retries 0, 2 independent replicates per state/arm, max8 workers. Deterministic SHA256-mixed schedule in one execution window. First formal cell is the auth canary and remains in the denominator. C0 is the formal baseline. Old 29/54 is descriptive only: unified prompt differs from the prior protocol, and provider variation remains possible.

## Prefix algorithm

Use original CASES snapshot path and hash; verify exact Q and positional C statements. Initial snapshot index0. For a checkpoint transition update_r_w, read only tools 1..r and Writer updates through (r,w), in the historical acquisition/run.py execution order. Every tool return and every completed Writer response is one event, including Writer updates without a claim change. Assert pre/post chains and UTC monotonicity. Compare current claims to immediate previous original snapshot S(n-1), including H-only checkpoints; never substitute the previous selected bank state.

Delta = exact statement set difference retaining current positional C IDs and current order. Path = last <=4 allowed events, original tool arguments without tool name, observed D/W references, and Writer-added C IDs. Writer argument contains only the observed window_ref, excluding H, need, reasoning, and all other semantic output. No inference from absence of claim delta.

Observations = <=2 blocks from Search/Find/Open events retained in that path, descending event index; simultaneous tool batch tie-break descending original observation array index. Preserve exact bounded text; no relevance choice, shortening, full-source access, or paraphrase. Historical run.py appends these exact bounded fields to actor_view visible_windows before writers. Intermediate Writer checkpoints have no contemporaneous Actor API call. We reconstruct the available Actor-view buffer; we do not claim a model consumed a separate request at that checkpoint. No future Actor request is read as validation. This restriction can leave Writer-only paths with no observation. All 27 states retained.

Eligibility frozen mechanically: delta-eligible iff previous checkpoint exists AND delta nonempty; path-eligible iff retained path nonempty; observation-eligible iff selected observations nonempty. Report each matched subset across ALL four arms as well as primary overall. Empty-context subset reports stochastic variation where inputs are byte-identical across arms. Q/C/reference values unchanged; Gold/H not in model inputs. Legitimate C1/C2 claim identifiers are not arm leakage; no condition labels/metadata are sent.

## Contract and failure handling

Exact endpoint/model/config/payload/schema, literal JSON, complete 216 cross-product and unique output paths, no H/Gold/arm metadata, source reconstruction identity checked before freeze. Each send checks immutable request equality and literal JSON. Credential only from environment or .env.deepseek, header only, never artifacts; no redirects, HTTPTransport retries=0. Missing credentials/preflight failure stops before send. HTTP400/401/402/403/404/422 stops queued requests; in-flight responses retained. Timeout240s per inactive HTTP operation, not a total token/billing bound. All planned slots remain denominator, even malformed/missing outputs. Exclusive writes, no retry, best-of, repair, or resume. Preserve raw bodies and unknown usage.

## Review

INHERITED_RUBRIC.md contains the unmodified previous semantic dimensions, operational boundaries and error taxonomy. Those rules apply unchanged; historical H/Gold-specific second-pass procedures are superseded ONLY by this task's context audit. First pass: Q, current C, generated O, mechanical validity; hide case/arm/replicate/context/Gold/aggregates/provider reasoning. Review IDs deterministic masked. Explicit individual judgments, reasons and ambiguity committed before unmasking/aggregate. No post-aggregate primary relabel. Accepted alternative local objectives are equally successful. Eight dimensions plus schema define strict. Broadness is whole_question_restatement OR bundled_objectives, overlapping errors permitted. Mechanical failures have zero success dimensions and mechanical_failure, not invented semantic errors.

Second pass only after first-pass commit: reveal context to assess path_fact_promotion, path_created_requirement, path_candidate_hardening, observation_overreach. Each gets an explicit boolean and reason/provenance. A name present in C is not automatically context contamination, but a role/relation unsupported by Q/C may be. Asking whether a raw-text candidate satisfies Q is not asserting it. Content overlap alone is insufficient causal attribution; repeated C0 errors are disclosed.

Pairs unchanged: same_obligation, compatible_obligation, different_but_valid, one_valid_one_invalid, both_invalid. Stable counts same+compatible with BOTH strict valid /27 each arm; raw both-valid also reported. Shared invalid text is both_invalid. Two valid independent branches are different_but_valid, not strict errors.

## Metrics and decisions

Report strict/all8/schema/all errors/broadness/pair categories/raw both-valid/stable. Primary table Context | Strict | Broad | Downstream | RelationArg | Scope | Stable. For overall and every frozen eligible matched subset, compute CΔ/C1/C2 minus concurrent C0, plus C1-CΔ and C2-C1; descriptive pp, not significance. Clusters and repeats are dependent; no p-value or production claim.

Mechanism signal exactly: (strict improvement >=10pp OR broadness reduction >=10pp OR stable increase >=15pp) AND relation-argument worsening <=5pp. Evaluate primary overall and each eligible subset separately, label denominator; subset-only signal cannot be called overall success. Incremental signal uses same thresholds. Approximate equivalence is descriptive only: abs(strict)<10pp, abs(broadness)<10pp, abs(stability)<15pp, abs(relationarg)<=5pp; failure to cross a threshold is not proof of equivalence. H3 'modest' and H4 'substantial' use 10pp downstream/argument changes as descriptive cutoffs, not new gates.

Direct-O viability requires ALL strict>=75%, broadness<=15%, downstream<=15%, ScopeFaithful>=85%, stable>=65%, relationarg<=7.5%. Evaluate overall and subsets; only overall all-checks supports the stated overall engineering signal. C2 remains exploratory even if best. No selection of winning replicate.

Interpret A: delta meaningful and no additional path/observation signal -> prefer minimal recency; B: path incremental signal -> path may add frontier value; C: lower broadness but fidelity/downstream unresolved -> locality improvement doesn't solve projection; D: no meaningful effect including eligible -> no support for path blindness as dominant; E: C2 deterioration with contamination -> potential salience interference. Report mixed evidence rather than force categories. No quantitative causal fraction of all failure from this small bank.

Sensitivity prespecified: matched eligible, empty-context, each replicate, each question cluster, leave-one-question-out, low-ambiguity subset, and relaxed locality-only (ignore Local+Coherent; primary unchanged). Identify all exposed-bank/single-reviewer limitations. Stop after these 216 scheduled slots regardless of outcome; future experiment only a recommendation.

## Accounting/integrity

Freeze source mapping/context bytes/code/availability/schema/config/prompts/schedule/rubric/metrics/thresholds/failure policy, commit before sends. Offline tests cover prefix bounds/QC identity/delta/lastK/matched raw text/isolation and real no-network transport failure behavior. Final audit replays raw parsing/scoring/accounting, verifies frozen and historical hashes, scans secrets without printing values, and commits/pushes artifacts. Report sent/returned/HTTP/schema failures, input/completion/reasoning/total, cache hit/miss/weighted hit rate, median/P95/max latency/peak concurrency, unknown usage. Reasoning is included in completion. Historical 65,535 completion tail is exposure scenario, not maximum. No unverified monetary cost.
