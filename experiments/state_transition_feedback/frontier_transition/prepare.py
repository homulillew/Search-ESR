"""Freeze T2 early requests and exact T1 PRE reuse before calls."""
import random,subprocess,sys
from pathlib import Path

BASE=Path(__file__).resolve().parent
TOP=BASE.parent
ROOT=TOP.parents[1]
sys.path.insert(0,str(TOP))
from common import read,write,sha,digest,provider,model_request

def main():
    assert not (BASE/'query_events.jsonl').exists()
    cases=read(TOP/'transition_bank/BANK.json');truth=read(TOP/'transition_bank/PRIVATE_TRUTH.json')
    t1={x['case_id']:x for x in read(TOP/'oracle_state_effect/REQUESTS.json') if x['arm']=='PRE'}
    prompt_path=TOP/'prompts/query_writer.md';prompt=prompt_path.read_text().rstrip();p=provider()
    rows=[];reuse=[]
    for c in cases:
        req=model_request(prompt,{'Question':c['question'],'Current Gap':c['bridge_gap'],
                                  'Current Research State':c['state_pre']})
        rows.append({'case_id':c['case_id'],'qid':c['qid'],'arm':'F_EARLY',
                     'request_sha256':digest(req),'request':req})
        reuse.append({'case_id':c['case_id'],'from_stage':'T1','from_arm':'PRE',
                      'as_arm':'F_PREMATURE','request_sha256':t1[c['case_id']]['request_sha256']})
    random.Random(202609262).shuffle(rows)
    write(BASE/'REQUESTS.json',rows)
    write(BASE/'REUSE.json',reuse)
    write(BASE/'PROGRESS_TRUTH.json',[{'case_id':x['case_id'],'qid':x['qid'],
         'early_progress_doc_ids':x['bridge_source_doc_ids'],
         'premature_progress_doc_ids':sorted(set(x['direct_sufficient_doc_ids'])|set(x['bridge_source_doc_ids'])),
         'direct_doc_ids':x['direct_sufficient_doc_ids'],
         'bridge_only_doc_ids':x['bridge_only_doc_ids']} for x in truth])
    old=read(TOP/'oracle_state_effect/freeze.json')
    write(BASE/'freeze.json',{'t0_commit':old['t0_commit'],'t1_request_sha256':old['requests_sha256'],
      'bank_sha256':sha(TOP/'transition_bank/BANK.json'),'truth_sha256':sha(TOP/'transition_bank/PRIVATE_TRUTH.json'),
      'prompt_sha256':sha(prompt_path),'common_sha256':sha(TOP/'common.py'),
      'requests_sha256':sha(BASE/'REQUESTS.json'),'reuse_sha256':sha(BASE/'REUSE.json'),
      'progress_truth_sha256':sha(BASE/'PROGRESS_TRUTH.json'),
      'provider':{k:p[k] for k in ['model','base_url','timeout_seconds','max_retries']},
      'generation_config':'SDK defaults; exact T1 PRE reuse for premature arm',
      'random_seed':202609262,'call_order':[(x['case_id'],x['arm'],x['request_sha256']) for x in rows],
      'sample_count':12,'new_query_count':12,'reused_query_count':12,
      'device':'cuda:1','retrieval_depth':50,'k_values':[1,3,5,10,20,50],
      'retriever_sha256':old['retriever_sha256'],'index_sha256':old['index_sha256'],
      'progress_rubric':'top-k contains a frozen source capable of verified, decision-changing Bridge Claim or direct next-Gap answer',
      'failure_policy':'one new call per F_EARLY; PRE response reused once; no repair or relabel'})
    print('T2 prepared',len(rows),'new and',len(reuse),'reused')

if __name__=='__main__':main()
