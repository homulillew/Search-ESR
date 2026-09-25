"""Pre-call T2/T3 prefix-only Gap correction; preserves committed v0 requests."""
import json,random,subprocess,sys
from pathlib import Path

TOP=Path(__file__).resolve().parent
ROOT=TOP.parents[1]
sys.path.insert(0,str(TOP))
from common import read,write,sha,digest,provider,model_request

def main():
    bank=read(TOP/'transition_bank/BANK.json')
    gaps=read(TOP/'transition_bank/PREFIX_GAPS.json')
    assert set(gaps)=={x['case_id'] for x in bank}
    aliases={'517':'Peter King','435':'Oliver Mtukudzi','1094':'Paris Saint-Germain',
       '311':'Hijitus','186':'Galacta','1034':'Heart Evangelista','177':'Enugu Rangers',
       '580':"You're the Worst",'546':'Ding Junhui'}
    for c in bank:
        assert aliases[c['qid']].lower() not in gaps[c['case_id']].lower(),c['case_id']
    p=provider();head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for stage in ['frontier_transition','online_state_update']:
        base=TOP/stage/'corrected';base.mkdir(parents=True,exist_ok=True)
        assert not (base/'REQUESTS.json').exists()
        prompt_path=TOP/'prompts/query_writer.md' if stage=='frontier_transition' else TOP/'prompts/state_updater.md'
        prompt=prompt_path.read_text().rstrip();rows=[]
        for c in bank:
            gap=gaps[c['case_id']]
            if stage=='frontier_transition':
                content={'Question':c['question'],'Current Gap':gap,'Current Research State':c['state_pre']}
                arm='F_EARLY'
            else:
                content={'Question':c['question'],'Current Research State':c['state_pre'],
                         'Current Gap':gap,'Current Observation':c['bridge_observation']}
                arm='ONLINE_UPDATE'
            req=model_request(prompt,content)
            rows.append({'case_id':c['case_id'],'qid':c['qid'],'arm':arm,
                         'request_sha256':digest(req),'request':req})
        seed=202609264 if stage=='frontier_transition' else 202609265
        random.Random(seed).shuffle(rows)
        write(base/'REQUESTS.json',rows)
        old=read(TOP/stage/'freeze.json')
        freeze={'pre_call_head':head,'amendment':'transition_bank/PRECALL_GAP_AMENDMENT.md',
          'prefix_gap_sha256':sha(TOP/'transition_bank/PREFIX_GAPS.json'),
          'bank_sha256':sha(TOP/'transition_bank/BANK.json'),
          'truth_sha256':sha(TOP/'transition_bank/PRIVATE_TRUTH.json'),
          'prompt_sha256':sha(prompt_path),'common_sha256':sha(TOP/'common.py'),
          'requests_sha256':sha(base/'REQUESTS.json'),
          'original_unused_freeze_sha256':sha(TOP/stage/'freeze.json'),
          'provider':{k:p[k] for k in ['model','base_url','timeout_seconds','max_retries']},
          'random_seed':seed,'call_order':[(x['case_id'],x['arm'],x['request_sha256']) for x in rows],
          'sample_count':12,'clean_subset_count':11,'clean_qid_count':8,
          'clean_exclusion':['U1_B07'],
          'failure_policy':'one call per case; max_retries=0; retain all 12 raw outcomes; clean analysis excludes pre-audited B07'}
        if stage=='frontier_transition':
            freeze.update({'device':'cuda:1','retrieval_depth':50,'k_values':[1,3,5,10,20,50],
              'retriever_sha256':old['retriever_sha256'],'index_sha256':old['index_sha256'],
              'progress_truth_sha256':old['progress_truth_sha256'],
              'reused_PRE_sha256':old['reuse_sha256']})
        else:
            freeze.update({'rubric_sha256':old['rubric_sha256'],'max_new_claims':2})
        write(base/'freeze.json',freeze)
        print(stage,'corrected',len(rows))

if __name__=='__main__':main()
