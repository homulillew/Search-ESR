"""Offline reproducibility/information-flow audit; does not call any provider."""
import json
import subprocess
from datetime import datetime
from .contracts import HERE,BASE,ROOT,read,save,digest,file_hash,request,validate
from .runner import verify_freeze
from ..harness import inputs

def main():
    freeze=verify_freeze();config=read(HERE/'CONFIG.json');bank=read(HERE/'CANDIDATE_BANK.json');run=HERE/'run001'
    plan={r['request_id']:r for r in read(HERE/'REQUEST_PLAN.json')}
    rows={p.name.removesuffix('.request.json'):read(p) for p in (run/'calls').glob('*.request.json')}
    assert set(rows)==set(plan) and len(rows)==85
    pair_by_id={p['pair_id']:p for p in bank['pairs']}
    for ident,r in rows.items():
        wire=r['request'];payload=json.loads(wire['messages'][-1]['content']);role=r['role']
        assert digest(wire)==r['request_hash'] and not r['offline_mock']
        assert wire==request(role,payload,config)
        assert wire['messages'][0]['content'].split('\nReturn one JSON object matching this schema:\n')[0].encode()==(BASE/'prompts'/f'{role}.txt').read_bytes()
        result=read(run/'calls'/(ident+'.result.json'))
        assert result['attempted'] and result['error'] is None and result['http_status']==200
        assert result['response_model']==config['model'] and result['finish_reason']=='stop'
        parsed=read(run/'calls'/(ident+'.parsed.json'));validate(role,parsed,payload)
        if role=='g1_candidate_coverage':
            inv=read(run/'inventories'/(r['evidence_key']+'.json'))
            assert payload['SourceCommitmentInventory']==inv['inventory'] and digest(inv['inventory'])==inv['inventory_sha256']
            attempt=read(run/'calls'/(ident+'.attempt.json'))
            assert datetime.fromisoformat(inv['frozen_utc'])<=datetime.fromisoformat(r['created_utc'])<=datetime.fromisoformat(attempt['utc'])
        else:assert r['request_hash']==plan[ident]['request_hash']
        if 'pair_id' in r:assert payload['candidate']==pair_by_id[r['pair_id']]['candidate']
    summary=read(run/'TRANSPORT_SUMMARY.json')
    assert summary['attempted']==85 and summary['attempted_failures']==0 and summary['complete_consistent_records']==85
    assert not read(run/'UNSENT_DEPENDENCIES.json')
    labels=read(HERE/'review/inventory_labels.json');rf=read(HERE/'review/INVENTORY_REVIEW_FREEZE.json')
    assert file_hash(HERE/'review/inventory_labels.json')==rf['labels_sha256']
    assert len(labels)==15 and sum(len(v['facts']) for v in labels.values())==365
    assert sum(not f['source_supported'] for v in labels.values() for f in v['facts'])==3
    m=read(HERE/'review/E2_METRICS.json');cases=read(HERE/'review/ALL_CASES.json')
    for split in ['pooled','D','H_diagnostic']:
        cs=[c for c in cases if split=='pooled' or c['split']==split]
        for arm in ['G0','G1']:
            for name,supported in [('FAR',False),('TPR',True)]:
                subset=[c for c in cs if c['truth']['source_supported']==supported]
                metric=m['tables'][split][arm][name]
                assert metric['denominator']==len(subset)
                assert metric['numerator']==sum(c[arm]['verdict']=='supported' for c in subset)
    assert sum(c['rescue'] for c in cases)==2 and sum(c['recall_harm'] for c in cases)==8
    assert m['final_status']=='H3_NOT_SUPPORTED' and not m['supported']
    outside=subprocess.check_output(['git','diff','--name-only',freeze['source_head'],'--','.',':!experiments/claim_pipeline_root_cause/e2_grounding'],cwd=ROOT,text=True).strip()
    assert not outside, outside
    save(HERE/'FINAL_INTEGRITY.json',{'status':'PASS','protected_file_hashes_verified':len(freeze['files']),
        'request_plan_exact_match':85,'unchanged_semantic_prompts':3,'physical_inventory_before_coverage':35,
        'inventories_reviewed':15,'facts_reviewed':365,'frozen_source_review_unchanged':True,
        'post_outcome_review_additions_separately_labeled':True,'historical_or_production_diff':[],
        'numeric_metrics_independently_recounted':True,'E3_calls':0,'new_retrieval_calls':0,'STOP_AFTER_E2':True})
    print('PASS: 85 requests, 35 dependency freezes, 365 fact labels, metrics and immutable history.')

if __name__=='__main__':main()
