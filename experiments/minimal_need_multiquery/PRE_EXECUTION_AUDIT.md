# Pre-execution audit

## Material Passport

- Type: historical evidence audit + preregistration, offline, Codex single reviewer.
- Current-task model/API/retrieval calls: 0.
- New experiment only; original task retained byte-for-byte in TASK.md.

## Actual remote and branch

Initial commands executed: `git fetch origin --prune`, `git status`, `git branch --show-current`, `git rev-parse HEAD`, `git rev-parse origin/main`, `git log --oneline --decorate -20 origin/main`.

Actual origin/main: `8021aca19a1ee5201730e40b338012c65ecd51cf`. Latest checked research branch: `experiment/belief-need-budget-locality-repair` at `05d2eeec297c06ce7fa8d2cdd40bc7acb676b88c`, local and remote identical. Main is its ancestor (git merge-base check passed). New branch `experiment/minimal-need-multiquery` starts at that research commit, preserving both main Evidence Pointer and the later Need results. No new main commit beyond the task anchor was fetched.

Initial untracked user work: `experiments/auto_research/`, `research_loop/`, `指令提示词/agent_search_harness_state_research_notes .md`. These were not edited or staged. No applicable AGENTS.md was found.

## Main history inspected

```text
8021aca (origin/main, origin/HEAD, main) Add Evidence Pointer State v0 and authentication batch short-circuit
750257d Record P0/P1 note-fidelity comparison with credential failure batches
bf25c7e Add pinned P0/P1 note-fidelity experiment and pre-output coverage review
3d5fc3d Preserve literal whitespace in source excerpts and archived patch
2213b23 Fix retrieval asset configuration and run six first-observation source-note cases
5aa3bfd Record first-observation asset mismatch and paused preflight
edcfb92 Add raw-question first-observation note node and staged experiments
3278902 Run Qwen investigation-state pilot and formal S0 with complete failure audit
1581ba5 Audit state fixtures and archive failed S0 delivery pilot
4829a5e Add fixed-content investigation-state view node and staged experiments
396592c Record Atria C0/C1 rerun with 4096-token reviewer budget
ce8bb3d Record Atria C0/C1 replay with reasoning-budget failures and actor analysis
6319c64 Configure Atria model and opt in to stop-finished tool calls
850036f Record frozen C0/C1 source attribution paired experiment
6e6222c Complete E0 bad-case audit and validate reported token accounting
859e0f1 Audit real E0 failures and add isolated source-attribution paired probe
809dfeb Record frozen E0 need-review experiment and branch analysis
0193fc0 Add fixed-prefix Need Review E0 harness and experiment handoff
204bfc5 Add exploratory query policy experiments and analysis
6d1be8d Add verbatim selector comparison experiments and analysis
```

Evidence Pointer v0 changes mechanical evidence addressing and auth circuit behavior; it reports zero new model calls, so it does not supply contrary Need-control results. Main Need Review and Query studies reinforce the premise/relationship boundary. Later research result05d2eee is retained as the calibrated model/bank source. The scope remains Q+C+H and ephemeral Need; no main default component is replaced.

## Required historical reading and implications

- [全链路排查报告/Search-Open节点排查与冻结报告.md](../../全链路排查报告/Search-Open节点排查与冻结报告.md): Source hit differs from visible support; fixed windows and immutable addressing do not guarantee semantic success.
- [全链路排查报告/Query初始化首轮对照实验.md](../../全链路排查报告/Query初始化首轮对照实验.md): Two directions occasionally complement, but overall evidence gain was not stable; display and compute budgets differ.
- [全链路排查报告/Query单入口初始化落地与联调.md](../../全链路排查报告/Query单入口初始化落地与联调.md): Fewer schema failures did not fix relation binding; legal refs do not certify query semantics.
- [全链路排查报告/Query固定线索表达对照与根因验证.md](../../全链路排查报告/Query固定线索表达对照与根因验证.md): Fixed clue still permits relation/time drift; deleting extra words can lose useful sources.
- [全链路排查报告/Query通用原则提示词落地与对照实验.md](../../全链路排查报告/Query通用原则提示词落地与对照实验.md): Lower token use did not imply fresh retrieval/semantic gain; basis_refs are not facts.
- [全链路排查报告/BasisPacket固定原文与保守编译对照实验.md](../../全链路排查报告/BasisPacket固定原文与保守编译对照实验.md): Input isolation helps, but compiler abstention and relation ambiguity remain; verbatim path is a useful comparator, not universal solution.
- [experiments/search_find_v3a/RESULTS.md](../../experiments/search_find_v3a/RESULTS.md): Find 0/88 despite mechanical capability. More Find is not itself the goal.
- [experiments/search_find_v3b/RESULTS.md](../../experiments/search_find_v3b/RESULTS.md): Local-only schema still produced undeclared Search; weak 4/50 Find signal, no hard-mask justification.
- [experiments/unified_global_retrieval/FINAL_CONCLUSION.md](../../experiments/unified_global_retrieval/FINAL_CONCLUSION.md): Old-D 19/20, new-D16/20; gate FAIL. GPU replay same ranking; document recall is not evidence yield.
- [experiments/deferred_recovery/FINAL_CONCLUSION.md](../../experiments/deferred_recovery/FINAL_CONCLUSION.md): Global five deferred recoveries vs hybrid three under strict scope; only one fresh case, no generalized safety/activation conclusion.
- [experiments/evidence_scope_localization/FINAL_CONCLUSION.md](../../experiments/evidence_scope_localization/FINAL_CONCLUSION.md): Fresh K A0 9/10 vs A1 8/10; more inspection did not improve evidence. Actor/locator/bank/Writer failures separated.
- [experiments/gap_evidence_claim_loop/FINAL_CONCLUSION.md](../../experiments/gap_evidence_claim_loop/FINAL_CONCLUSION.md): Curated admission protection did not prevent live-loop strengthening or premature closure; F3 failed.
- [experiments/bcplus_verification/FINAL_CONCLUSION.md](../../experiments/bcplus_verification/FINAL_CONCLUSION.md): Exact evidence -> valid Claim19/20 and contradiction clear6/6. Acquisition and strict full-constraint closure remain weak; old resolved labels were overpermissive.
- [experiments/variable_preserving_state/FINAL_CONCLUSION.md](../../experiments/variable_preserving_state/FINAL_CONCLUSION.md): Explicit unknowns reduce binding errors, not materially biased query generation; V2 gate failed.
- [experiments/research_state_v2/FINAL_CONCLUSION.md](../../experiments/research_state_v2/FINAL_CONCLUSION.md): Narrow mutation strong; gap-driven admission invented candidate details and A1 failed.
- [experiments/research_state_plan_handoff/FINAL_CONCLUSION.md](../../experiments/research_state_plan_handoff/FINAL_CONCLUSION.md): Plan altered Find from0/4 to3/4, but wrong-target amplification and low evidence yield remain.
- [experiments/research_state_qualification/FINAL_CONCLUSION.md](../../experiments/research_state_qualification/FINAL_CONCLUSION.md): Hypothesis-only target inspection2/7->3/7; helpful qualification gate failed, later phases unmeasured.
- [experiments/research_state_projection/FINAL_CONCLUSION.md](../../experiments/research_state_projection/FINAL_CONCLUSION.md): Combined card directional routing signal but S1 gate failed; components not causally separated.
- [experiments/research_progress_frontier/FINAL_CONCLUSION.md](../../experiments/research_progress_frontier/FINAL_CONCLUSION.md): Clean reviewer states support local chain; not a live persistent frontier reliability demonstration.
- [experiments/dynamic_progress/FINAL_CONCLUSION.md](../../experiments/dynamic_progress/FINAL_CONCLUSION.md): Blocker precision73.8%, P1 failed; bounded locality signal does not validate later stages. Loose closure judgments later challenged by BC+ audit.
- [experiments/asymmetric_progress/FINAL_CONCLUSION.md](../../experiments/asymmetric_progress/FINAL_CONCLUSION.md): Single-relation precision82.6% below gate; historical over-refusal interpretation requires later strict-closure audit.
- [experiments/goal_residual_control/FINAL_CONCLUSION_V2.md](../../experiments/goal_residual_control/FINAL_CONCLUSION_V2.md): Contract repair raises validity; reviewer stopping signal lacks final-resolution gain. Q+C+H plausible semantic core, not proved sufficient.
- [experiments/belief_need_convergence/FINAL_CONCLUSION.md](../../experiments/belief_need_convergence/FINAL_CONCLUSION.md): Artificial4096 cap confounded failures; fresh qid shortage. Do not interpret as uncapped policy failure.
- [experiments/belief_need_budget_locality_repair/FINAL_CONCLUSION.md](../../experiments/belief_need_budget_locality_repair/FINAL_CONCLUSION.md): Calibrated omit-max policy. B5dev15/16 vs fresh16/27; P4/W5/A1 plus length, no prompt improvement licensed from old grade alone.
- [experiments/research_state/evidence_pointer/README.md](../../experiments/research_state/evidence_pointer/README.md): Deterministic evidence materialization from observed addresses; avoids mechanical retyping and does not entail semantic control truth.
- [experiments/research_state/evidence_pointer/VALIDATION.md](../../experiments/research_state/evidence_pointer/VALIDATION.md): Offline only0 paidcalls. Auth short-circuit retains blocked planned denominator; no new model effect evidence.
- [experiments/research_state/need_review/AUDIT_809DFEB_FOLLOWUP.md](../../experiments/research_state/need_review/AUDIT_809DFEB_FOLLOWUP.md): Unsupported event binding can survive next-Need review; strict source attribution and partial usage accounting matter.

Exact source hashes are in analysis/HISTORY_READING.json. The 15,286 protected files include tracked historical experiments, reports and llm_chat. Protection uses actual pre-edit file hashes plus a final diff against the base; it does not claim an audit of corpus correctness.

## Frozen design choices

1. Need means a coherent premise-closed unresolved objective; atomic count is no longer a validity gate. E0 is a separate re-audit, not an amended old result.
2. B0 retains exact B5 text and constant research tag; B1/B2/B3 append only requested mechanism paragraphs. Inherited atomic/coherence tension is disclosed; no silent baseline edit.
3. E1 development uses all10 old P/A/W cases and8 mechanically chosen valid controls,18 states/9qids, including8 No-H. Concurrent B0 avoids using selected historical failures as the treatment counterfactual.
4. All QCH derive from natural archived U1 snapshots. Inherited source-relative support reviews are retained for29 unique Claims over18 observed text hashes; no new Claim or H is written by reviewer. Model payload receives statements only, not audit labels or sources.
5. Need config retains omitted max_tokens, not4096. Transport/request schema/token accounting and authentication short-circuit are mechanical. No tool/backend change.
6. Task§35 requires current-task explicit paid-call authorization. This delivery completes E0, implementation, offline tests, bank/prompt freeze, dry run and estimates, then stops PREPARED_FOR_REAL_RUN.
7. Fresh exclusion scan covers10,653 tracked JSON/JSONL files and finds201 qids. It is conservative and incomplete for qids in arbitrary prose/untracked materials; it cannot certify new qids. No new fresh qid/QCH bank is claimed ready.
8. Later gates remain closed. Q1 reserves6 slots, returns up to3×top2, leaves unused slots empty; actual compute/display cost is reported separately. No dependent query is instantiated before its prerequisite result.

## Claim/H audit boundaries

Provenance records verify byte/hash identity with old natural state and recorded source support. This is source-relative evidence, not independent external verification. H may contain false dates or categorical phrasing; it is deliberately not cleaned before E1. E0 reviews only the five matching QCH and historical Need; broad historical reading about other cases does not enter their inputs. Researcher annotations are private offline artifacts, never model state.
