"""Freeze T1 inputs and call order before any model invocation."""
import hashlib,json,random,subprocess,sys
from pathlib import Path

BASE=Path(__file__).resolve().parent
TOP=BASE.parent
ROOT=TOP.parents[1]
sys.path.insert(0,str(TOP))
from common import read,write,sha,digest,provider,model_request

def main():
    assert not (BASE/'query_events.jsonl').exists()
    cases=read(TOP/'transition_bank/BANK.json')
    prompt_path=TOP/'prompts/query_writer.md';prompt=prompt_path.read_text().rstrip()
    p=provider();rows=[]
    for c in cases:
        for arm in ['PRE','POST','RAW']:
            state={'claims':c['state_pre']['claims'] if arm!='POST' else c['state_post']['claims']}
            content={'Question':c['question'],'Current Gap':c['next_gap'],'Current Research State':state}
            if arm=='RAW':
                content['Raw Prior Observation']={'text':c['bridge_observation']['text'],
                                                   'url':c['bridge_observation']['url']}
            req=model_request(prompt,content)
            rows.append({'case_id':c['case_id'],'qid':c['qid'],'arm':arm,
                         'request_sha256':digest(req),'request':req})
    assert len(rows)==36
    random.Random(202609261).shuffle(rows)
    write(BASE/'REQUESTS.json',rows)
    old=read(ROOT/'experiments/state_conditioned_retrieval/state_sufficiency/freeze.json')
    assert sha(ROOT/'BCPlus/scripts/search_bcplus.py')==old['retriever_sha256']
    write(BASE/'freeze.json',{'t0_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
       'bank_sha256':sha(TOP/'transition_bank/BANK.json'),
       'truth_sha256':sha(TOP/'transition_bank/PRIVATE_TRUTH.json'),
       'prompt_sha256':sha(prompt_path),'common_sha256':sha(TOP/'common.py'),
       'requests_sha256':sha(BASE/'REQUESTS.json'),
       'provider':{k:p[k] for k in ['model','base_url','timeout_seconds','max_retries']},
       'generation_config':'SDK defaults; same for all arms',
       'random_seed':202609261,'call_order':[(x['case_id'],x['arm'],x['request_sha256']) for x in rows],
       'sample_count':12,'query_count':36,'device':'cuda:1','retrieval_depth':50,
       'retriever_sha256':old['retriever_sha256'],'index_sha256':old['index_sha256'],
       'sqlite_sha256':old['sqlite_sha256'],
       'k_values':[1,3,5,10,20,50],
       'primary_metric':'first any frozen sufficient doc rank; miss=51; direct recall at each k and MRR@50',
       'failure_policy':'one call per arm; max_retries=0; no repair; invalid query/retrieval is a miss'})
    print('T1 prepared',len(rows))

if __name__=='__main__':main()
