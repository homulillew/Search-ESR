"""Offline mechanical bank preparation; original selector is imported unchanged."""
from pathlib import Path
import subprocess
from collections import Counter
from ..harness import read, save, file_hash, digest, freeze_e2_candidates, ROOT

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROLES = ('g0_current_grounding', 'g1_evidence_inventory', 'g1_candidate_coverage')

def main():
    inputs = [BASE/'contract_rerun/review/REVIEWED.json', BASE/'bank/historical_candidates.json']
    b = freeze_e2_candidates(*(read(p) for p in inputs))
    if b['calls'] > 85: raise ValueError('authorization ceiling exceeded')
    save(HERE/'CANDIDATE_BANK.json', b)
    packets = read(BASE/'bank/diagnostic.json') + read(BASE/'bank/heldout.json')
    # Only the D/H_diagnostic metadata are used; confirmation payloads are not read by execution.
    families = {p['packet_id']:p['family_prestratum'] for p in packets if p['split'] != 'H_confirmation'}
    negatives = [p for p in b['pairs'] if not p['label']['source_supported']]
    counts = {s:{'positive':sum(p['split']==s and p['label']['source_supported'] for p in b['pairs']),
                 'negative':sum(p['split']==s and not p['label']['source_supported'] for p in b['pairs'])}
              for s in ('D','H_diagnostic')}
    save(HERE/'CALL_ESTIMATE.json', {'G0':b['count'],'G1_inventory':b['inventory_count'],
        'G1_coverage':b['count'],'total':b['calls'],'authorization_ceiling':85,'splits':counts,
        'negative_qids':sorted({p['qid'] for p in negatives}), 'negative_families':dict(Counter(families[p['origins'][0]['packet_id']] for p in negatives))})
    config = read(BASE/'contract_rerun/CONFIG_V2.json')
    config.update(concurrency_cap=50, connection_pool_max=70, maximum_active_concurrency=50,
        stage_independent_requests={'E2':b['count']+b['inventory_count']}, stage_call_ceiling={'E2':b['calls']},
        authorization='E2 TASK section 4; new explicit user authorization, <=85 calls; STOP_AFTER_E2.',
        credential_source='DEEPSEEK_API_KEY environment; never archived',
        failure_policy='Any transport/schema/ref/model/finish/parse/inventory contract failure halts unsent, completes inflight; zero retry/replacement/repair/resume.',
        concurrency_policy='Fixed active cap 50, pool 70. Initial 35 G0 + 15 inventory. Coverage becomes ready only after its on-disk inventory freeze. Any failure sets dispatch cap to 0; no escalation needed for 85-call DAG.')
    save(HERE/'CONFIG.json',config)
    save(HERE/'BANK_FREEZE.json', {
        'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'source_inputs':{str(p.relative_to(ROOT)):file_hash(p) for p in inputs},
        'selector':{'file':'experiments/claim_pipeline_root_cause/harness.py','sha256':file_hash(BASE/'harness.py'),'function':'freeze_e2_candidates'},
        'bank_sha256':file_hash(HERE/'CANDIDATE_BANK.json'),'counts':counts,
        'pairs':[{'pair_id':p['pair_id'],'pair_sha256':digest(p),'candidate_sha256':digest(p['candidate']),
            'Evidence_sha256':digest(p['Evidence']),'qid':p['qid'],'split':p['split'],'label':p['label'],
            'family_prestratum':families[p['origins'][0]['packet_id']]} for p in b['pairs']],
        'distinct_inventories':b['inventory_count'],'exact_call_count':b['calls'],
        'prompts':{r:file_hash(BASE/'prompts'/f'{r}.txt') for r in ROLES},
        'schemas':{r:file_hash(BASE/'contract_rerun/schemas'/f'{r}.json') for r in ROLES},
        'config_sha256':file_hash(HERE/'CONFIG.json'),
        'truth':'Frozen source-relative support/strengthening/ambiguity only; relevance is not truth.',
        'H3':{'pooled_relative_FAR_reduction_min':.5,'G1_TPR_min':.85,'paired_negative_delta':'<0',
              'equal_weight_negative_qid_delta':'<0','H_diagnostic':'strict FAR reduction and TPR >= .85; paired and qid delta <0',
              'zero_baseline_FAR':'H3_INCONCLUSIVE_NO_BASELINE_FALSE_ADMISSION','missingness':'H3_INCONCLUSIVE',
              'severe_inventory_unreliability':'Report gate separately; final H3 not pass/inconclusive if verdicts uninterpretable'},
        'authorization':{'source':'TASK.md sections 4,20,41','task_sha256':file_hash(HERE/'TASK.md'),'ceiling':85,'stages':['E2'],'STOP_AFTER_E2':True}})

if __name__ == '__main__':main()
