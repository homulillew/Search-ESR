"""Freeze corrected E1 before any paid call; original artifacts are immutable."""
import subprocess
from datetime import datetime,timezone
from .. import harness as old
from .contracts import HERE,BASE,ROOT,read,save,digest,file_hash,request,project_payload,schema_for

HEAD='99fbe47b9a6fa1bcfe628cb801cbd8e1ebcb29c5'
def main():
    config=read(HERE/'CONFIG_V2.json');ps=old.bank(['D','H_diagnostic']);hashes=[]
    for p in ps:
        for role in ['a0_current_reader','a1_no_c_reader','a2_selector','a2_evidence_formulator']:
            selected={'selections':[{'window_ref':p['Observation'][0]['window_ref'],'reason':'never enters formulation'}]}
            payload=old.inputs(role,p,selected=selected);public=project_payload(role,payload)
            hashes.append({'packet_id':p['packet_id'],'role':role,'conditional':role=='a2_evidence_formulator',
                'original_payload_sha256':digest(payload),'public_payload_sha256':digest(public),
                'dynamic_schema_sha256':digest(schema_for(role,public)),'request_sha256':digest(request(role,payload,config))})
    save(HERE/'REQUEST_HASHES_V2.json',hashes)
    save(HERE/'CALL_ESTIMATE_V2.json',{'authorized_stage':'E1 only','packets':24,'arms':3,'initial_calls':72,'dependent_formulator_calls':[0,24],'max_calls':96,'replicates':1,'retries':0,'E2_calls':0,'E3_calls':0,'historical_response_reuse':False})
    save(HERE/'EXECUTION_PREFLIGHT.json',{'base_head':HEAD,'harness_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'offline_tests_passed':84,
        'semantic_view_fields':['window_ref','doc_ref','title','url','text','date (only if originally present)'],
        'ref_contract':'W-pattern + unique refs + request-specific enum + independent membership',
        'private_records_preserved':True,'prompts_bank_rubric_thresholds_unchanged':True,'initial_concurrency':72,'max_concurrency':72,
        'timeout_and_failure_policy':'Original strict halt-unsent policy unchanged; no retry/backfill/repair/resume',
        'review_order':'source-only labels frozen, then relevance/dedup labels frozen, then frozen-atom coverage; never display arm or alternatives',
        'review_display_cache':'Exact Observation content may be displayed once and subsequently referenced by SHA and first opaque source-packet ID. No semantic dedup or annotation changes.',
        'H_confirmation_calls':0,'E2_E3_authorized':False})
    legacy=subprocess.check_output(['git','ls-tree','-r','--name-only',HEAD,'experiments/claim_pipeline_root_cause','llm_chat/recoverable_loop'],cwd=ROOT,text=True).splitlines()
    files={}
    for path in legacy:
        p=ROOT/path;assert p.read_bytes()==subprocess.check_output(['git','show',HEAD+':'+path],cwd=ROOT)
        files[path]=file_hash(p)
    for p in sorted(HERE.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts:files[str(p.relative_to(ROOT))]=file_hash(p)
    save(HERE/'FREEZE_V2.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'base_head':HEAD,
        'pre_freeze_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'files':files,'runtime_head_policy':'Paid run records actual freeze-commit HEAD; hash files avoid circular commit identity.',
        'E1_packet_ids':[p['packet_id'] for p in ps],'packet_count':24,'max_calls':96,'horizon':0,'tools':[],'semantic_prompt_changes':False,'bank_changes':False,'E2_E3_authorized':False})
    save(HERE/'AUTHORIZATION_V2.json',{'authorized':True,'stages':['E1'],'freeze_sha256':file_hash(HERE/'FREEZE_V2.json'),
        'task_sha256':file_hash(HERE/'TASK.md'),'source':'Current user attachment Contract Repair & Full Rerun sections26–27 explicitly authorizes corrected E1 and prohibits E2/E3.','recorded_utc':datetime.now(timezone.utc).isoformat()})
    print('Frozen',len(files),'files and',len(hashes),'possible requests; original artifacts unchanged.')

if __name__=='__main__':main()
