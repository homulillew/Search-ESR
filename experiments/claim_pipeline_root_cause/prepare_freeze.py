"""Offline final freeze. Excludes only its own hash and later execution outputs."""
from datetime import datetime,timezone
import importlib.metadata
import subprocess
import sys
from .harness import HERE,ROOT,read,save,file_hash,digest,bank,inputs,request

def main():
    config=read(HERE/'CONFIG.json');packets=bank(['D','H_diagnostic']);all_packets=bank()
    n=len(packets);distinct=len({digest(p['Observation']) for p in packets});e2_max=120+distinct
    assert n==24 and distinct==23 and config['stage_call_ceiling']['E2']==e2_max
    estimate={'status':'OFFLINE_ONLY_NOT_AUTHORIZED','model':config['model'],'new_calls_so_far':0,
        'E1':{'packets':n,'arms':['A0','A1','A2'],'replicates':1,'initial_independent_calls':3*n,
            'formula':'A0 N + A1 N + Selector N + Formulator K, 0<=K<=N','min_calls':3*n,'max_calls':4*n,
            'max_completion_tokens_at_frozen_cap':4*n*config['max_tokens']},
        'E2':{'candidate_count':'unknown until actual E1 outputs and source review','max_candidates':60,
            'max_distinct_evidence':distinct,'formula':'2*M + I; M<=60, I<=min(M,23)',
            'max_calls':e2_max,'not_automatic':'Stop if required positive/strengthened-negative D/H strata are absent.',
            'max_completion_tokens_at_frozen_cap':e2_max*config['max_tokens']},
        'E3':{'conditional':True,'packets':12,'condition':'complete E1/E2; at least one complete mechanism gate supported',
            'formula':'12 * (4 current + (1 or 2 construction) + 3 admission + (1 if G1 else 0))',
            'ceilings_by_components':{'A1_G0':96,'A2_G0':108,'A0_G1':108,'A1_G1':108,'A2_G1':120},
            'max_calls':120,'max_completion_tokens_at_frozen_cap':120*config['max_tokens']},
        'E1_E2_max_calls':4*n+e2_max,'including_conditional_E3_max_calls':4*n+e2_max+120,
        'input_tokens':'Not guessed as tokenizer-accurate. Per-call request bytes and actual usage archived at execution.',
        'cost':'No price assumption or paid probe. Counts/token caps are ceilings, not expected spend; do not call to fill budget.',
        'retries':0,'new_retrieval_calls':0}
    save(HERE/'CALL_ESTIMATE.json',estimate)
    initial=[]
    for p in packets:
        for role in ['a0_current_reader','a1_no_c_reader','a2_selector']:
            data=request(role,inputs(role,p),config)
            initial.append({'packet_id':p['packet_id'],'role':role,'request_sha256':digest(data)})
        selected={'selections':[{'window_ref':p['Observation'][0]['window_ref'],'reason':'not sent to formulator'}]}
        data=request('a2_evidence_formulator',inputs('a2_evidence_formulator',p,selected=selected),config)
        initial.append({'packet_id':p['packet_id'],'role':'a2_evidence_formulator','conditional_on_selection':True,'request_sha256':digest(data)})
    save(HERE/'e1/REQUEST_HASHES.json',initial)
    files={str(p.relative_to(HERE)):file_hash(p) for p in sorted(HERE.rglob('*')) if p.is_file()
        and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts
        and p.name not in ['FREEZE.json','OFFLINE_TEST_RESULTS.json','OFFLINE_TEST_OUTPUT.txt']}
    save(HERE/'FREEZE.json',{'created_utc':datetime.now(timezone.utc).isoformat(),
        'base_head':'dadf69f1c5fb96491f4fd3a34e0ece3418878de3',
        'pre_harness_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'execution_head_policy':'Record actual third-commit HEAD at execution and bind authorization to this freeze hash.',
        'files':files,'prefix_hashes':{p['packet_id']:p['content_sha256'] for p in all_packets},
        'historical_config':{'path':'experiments/recoverable_loop_clean/h2_independent_recovery/CONFIG.json','sha256':file_hash(ROOT/'experiments/recoverable_loop_clean/h2_independent_recovery/CONFIG.json')},
        'historical_roles':{'path':'llm_chat/recoverable_loop/roles.py','sha256':file_hash(ROOT/'llm_chat/recoverable_loop/roles.py')},
        'sample_count':36,'E1_E2_packet_count':24,'E3_reserved_count':12,'replicates':1,
        'tools':[],'retrieval_calls':0,'actor_horizon':0,'max_retries':0,
        'provider_model_parameters':{k:config[k] for k in ['endpoint','model','thinking','reasoning_effort','temperature','max_tokens','user_id']},
        'failure_policy':config['failure_policy'],'stage_budget':config['stage_call_ceiling'],
        'python':sys.version,'dependencies':{p:importlib.metadata.version(p) for p in ['httpx','jsonschema','pytest']},
        'live_authorized':False,'paid_calls':0})
    print('Frozen',len(files),'files; E1<=96, E2<=143, E3 conditional<=120; paid calls=0')

if __name__=='__main__':main()
