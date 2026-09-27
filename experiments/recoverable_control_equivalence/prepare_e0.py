"""Freeze the new question and counting rules before this offline aggregation."""
from .common import *

def main():
    assert git('rev-parse','origin/experiment/skeleton-state-alignment')==BASE
    files=git('ls-tree','-r','--name-only',BASE,'experiments').splitlines()
    history={n:sha(ROOT/n) for n in files if (ROOT/n).is_file()}
    write(P/'analysis/HISTORICAL_HASHES.json',history)
    sources=['e0_reference/STATES.json','e0_reference/QUESTIONS.json','e0_addressability/ORACLE_RUNTIME_SKELETON.json',
      'e0_addressability/RUNTIME_SKELETON_D2.json','e0_addressability/ADDRESSABILITY.json','e0_addressability/METRICS.json',
      'e1_alignment/GOLD_MASKS.json','e1_alignment/SCHEDULE.json','e1_alignment/METRICS.json','e1_alignment/ACCOUNTING.json',
      'e2_selection/SELECTION_REFERENCE.json','analysis/MONOTONIC_PAIRS.json','contracts.py','CONFIG.json','FREEZE.json',
      'analysis/ERROR_LEDGER.json','analysis/FINAL_CONCLUSION.md']
    paths=[OLD/n for n in sources]+sorted((OLD/'e1_alignment/calls').glob('*.result.json'))
    write(P/'e0_control_equivalence/SOURCE_MANIFEST.json',{'baseline_head':BASE,'files':{rel(p):sha(p) for p in paths},
      'scope':'108 existing outputs, frozen Gold, D2 selection reference, 15 eligible natural Claims-addition pairs. No final answer or new source audit.'})
    gates={'E0_A1':{'binary_node_accuracy':['>=',.95],'open_requirement_recall':['>=',.97],'closure_precision':['>=',.90],
       'exact_binary_mask':['>=',.85],'false_empty_open_set':['<=',0],'false_stop_hazard':['<=',0],
       'schema_validity':['>=',1],'lost_all_acceptable_frontier':['<=',.10]},
       'E0_conditional_recoverability':{'minimum_evaluable_prior_false_closes':4,'safe_resolution_rate_minimum':.75},
       'S0':{'valid_selection':['>=',.85],'selected_closed':['<=',.05],'downstream_selection':['<=',.10],'false_stop':['<=',.05],'schema_validity':['>=',.95]},
       'S1':{'valid_selection':['>=',.80],'selected_closed':['<=',.075],'downstream_selection':['<=',.10],'false_stop':['<=',.075],'schema_validity':['>=',.95],'selection_loss':['<=',.10]}}
    write(P/'GATES.json',gates)
    write(P/'HYPOTHESES.md','''# Hypotheses

H1: U/P errors collapse under OPEN/CLOSED projection, improving exact masks without changing old labels or old gates.
H2: Runtime A1 preserves unresolved requirements and an acceptable active frontier on this exposed bank.
H3: Existing natural Claims additions may resolve false closes; a small/censored denominator cannot establish recoverability.
H4 (conditional paid E1): a correct OpenSet supports ID selection; fixed A1 replicate 1 transfers with <=10 pp valid-selection loss.

Old result remains A0 FAIL / A1 PASS / Joint FAIL / E2 NOT RUN. This is a new user-specified objective on already exposed data, not a fresh confirmatory validation.
''')
    write(P/'PROTOCOL.md','''# Recoverable Control Equivalence / Active Requirement Selection

## Material Passport

Mode: experiment execution / reproducibility. Source: frozen historical development bank at dd442dd. 27 states / 10 qids / 2 arms / 2 replicates. No independent sample or reviewer claim. User TASK.md is authoritative.

## E0 counting rules (frozen before new aggregation)

- F -> CLOSED; P/U -> OPEN for both historical prediction and frozen Gold. Original 3-way values retained alongside binary values. Unknown/invalid output is not repaired.
- Primary A1 Runtime D2 only. A0 is diagnostic. Every 54-response arm remains in response denominators; node denominators are all arm nodes. Source-schema completeness is an independent 100% gate.
- Binary accuracy uses all nodes. Open recall denominator Gold OPEN; open precision denominator predicted OPEN; closure precision denominator predicted CLOSED. False close denominator Gold OPEN. Exact masks require valid output and every node correct.
- Control-equivalent gain = exact binary minus exact 3-way (proportion/percentage points), not a replacement of historical metrics. Counts expose U/P collapsed errors, false closes and false opens.
- false_empty_open_set: valid prediction has no OPEN but Gold has OPEN. False STOP hazard (potential, not an observed selector action): prediction allows all-CLOSED STOP while frozen reference disallows STOP. For A0 with no selection reference, use Gold OPEN as material-residual criterion.
- lost_all_acceptable_frontier denominator: A1 responses whose frozen acceptable_active_ids is nonempty. Numerator: none of those IDs remain OPEN. Also report all 54-response counts. G04/G05 have no admissible ID at baseline, are representation_addressability_limit, not Alignment errors or legal STOP. They remain in every other E0 denominator and all E1 denominators.
- still_has_recovery_frontier denominator: A1 responses with >=1 false-close node; numerator retains >=1 frozen acceptable OPEN ID. This is available opportunity, not proof that an action will acquire corrective evidence.
- False-close response categories are exclusive, priority D(empty OpenSet), A(any acceptable OPEN), B(nonempty OpenSet entirely blocked/downstream), C(other no acceptable frontier). Node-level and response-level denominators never mixed.
- Frozen selection references apply ONLY to D2. Oracle A0 R# semantics differ: frontier measures and A/B/C categorization are unavailable, not fabricated by ID matching. Binary masks, empty-set hazards and temporal audits cover both arms.
- Temporal audit uses only original 15 eligible adjacent literal-Claims-addition edges. Exclude G05->G06 and G17->G18; never skip across these to a farther state. Match arm/qid/requirement_id/replicate. Evaluate immediate successor of every false-close node. End of eligible chain is right-censored. Counts: recovered_open / became_justified / persistent_false_close / reopened_incorrectly. Became justified is evidence completion, not model correction.
- Safe resolution denominator includes only prior false-close nodes with an evaluable eligible successor. Denominator<4 => INSUFFICIENT_NATURAL_DENOMINATOR, no hard recovery gate, no 100%-recoverable claim. >=4 requires >=75%. This applies to primary A1 only; A0 remains diagnostic.
- Maximum run length is observed consecutive FC states on eligible chains (not transitions), lower bound when right-censored. Median recovery steps among observed OPEN recoveries only; median safe-resolution steps additionally includes justified closure. Unobserved recovery is null, never zero.
- Report both arms, nonempty Claims, qid and replicate strata. Sensitivity: leave-one-qid-out, descriptive only. No p-values: ten exposed, correlated qids do not constitute 108 independent cases.

## Conditional E1

Only after E0 PASS and applicable new user authorization under TASK section46. 27 states x S0/S1 x 2 =108. S0 frozen Gold binary; S1 always old A1 replicate1, no fallback/best-of/repair. Original question + D2 runtime nodes + binary mask only. Exact system prompt from TASK section27. DeepSeek deepseek-flash, JSON, temperature0, omit max_tokens, max_retries0, workers<=8. No tool calls; horizon1.

All 108 requests mixed in a deterministic hash order and frozen before paid execution. First formal slot is the canary, not an extra call. Every failure and planned slot preserved. No replacement. Same conservative HTTP inactivity timeout240s and halt status policy as source experiment. Save hit/miss/input/output/reasoning/total/latency. Reasoning already belongs to completion tokens.

First-pass review sees Q/Skeleton/visible binary Mask/selection only; arm, replicate, reference, GoldO, aggregates, reasoning hidden. Commit all judgments before unmasking. Primary metrics remain frozen-reference mechanical scores; blind judgments are diagnostic. A familiar reviewer is not independent or memory-erased. Schema failure counts against planned denominator. Selected-Gold-CLOSED and selected-input-CLOSED separate; false STOP and input-mask false STOP separate. Two valid different IDs are stable in validity. G04/G05 retained; selection ceiling25/27.

S0/S1 thresholds in GATES.json. E0 FAIL stops all new calls. E1 completion stops whether pass or fail. No retriever/backend/state/schema modification, verifier, hard gate, DAG, majority vote, Gap, Search/Find/Open, Writer or rollout.

## Authority / budget

User authorizes offline E0 and concrete E1 preparation by this task. Prior experiment's paid authorization explicitly does not extend under TASK46. Freeze E1 and estimate then request a new applicable authorization. No paid call until recorded and committed. Preserve all historical experiments byte-for-byte. No automatic closure permanence: future masks must be recomputed from current Claims.
''')
    write(P/'PRE_EXECUTION_AUDIT.md',f'''# Pre-execution audit

- Fetched origin with prune. Remote baseline: `{BASE}`, exactly the task's expected HEAD; no intervening commits or same-family new experiment.
- New branch: `experiment/recoverable-control-equivalence` from that remote HEAD.
- Prior result: A0 FAIL / A1 PASS / Joint FAIL; E2 NOT RUN. No historical artifact modified.
- Historical tracked files protected by SHA256: {len(history)}. Existing unrelated untracked auto_research/, research_loop/ and user notes are outside this task.
- No applicable AGENTS.md found in workspace ancestors or experiment tree.
- Task's thresholds/data are already exposed. Freeze is for reproducibility and prospective Selection; E0 is explicitly retrospective reanalysis.
- D2-only selection reference cannot be numerically reused on A0. A0 frontier metrics are unavailable; this does not affect primary A1.
- Paid authorization: absent for this new experiment under TASK46. E0 is offline. E1 preparation is authorized; paid dispatch remains disabled until a new approval.
- Academic-research-suite experiment workflow applied inline for provenance, monitoring and reproducibility. User's explicit implementation/analysis task governs code creation; no extra role agents or redundant approval for offline analysis.
''')
    write(P/'README.md','''# Recoverable Control Equivalence

New question: does imperfect 3-way alignment preserve useful research opportunities after OPEN/CLOSED projection?

See TASK.md, PROTOCOL.md and GATES.json. E0 offline results: e0_control_equivalence/. E1 is conditional and needs its own applicable budget approval. Current status and conclusions live in STATUS.json and analysis/FINAL_CONCLUSION.md.

Historical experiment remains FAIL at its original joint gate; its E2 was not run. No history rewritten.

Run offline: `python -m experiments.recoverable_control_equivalence.e0` after E0 freeze commit. Commands create artifacts exclusively; no overwrite/resume.
''')
    paths=[p for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    write(P/'E0_FREEZE.json',{'source_head':BASE,'preparation_head':git('rev-parse','HEAD'),
      'files':{rel(p):sha(p) for p in sorted(paths)},'phase':'BEFORE_NEW_OFFLINE_AGGREGATION','new_calls':0})
if __name__=='__main__':main()
