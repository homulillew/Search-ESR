"""Freeze T3 updater calls and reviewer rubric."""
import random,subprocess,sys
from pathlib import Path

BASE=Path(__file__).resolve().parent
TOP=BASE.parent
ROOT=TOP.parents[1]
sys.path.insert(0,str(TOP))
from common import read,write,sha,digest,provider,model_request

def main():
    assert not (BASE/'events.jsonl').exists()
    cases=read(TOP/'transition_bank/BANK.json');p=provider()
    prompt_path=TOP/'prompts/state_updater.md';prompt=prompt_path.read_text().rstrip()
    rows=[]
    for c in cases:
        content={'Question':c['question'],'Current Research State':c['state_pre'],
                 'Current Gap':c['bridge_gap'],'Current Observation':c['bridge_observation']}
        req=model_request(prompt,content)
        rows.append({'case_id':c['case_id'],'qid':c['qid'],'arm':'ONLINE_UPDATE',
                     'request_sha256':digest(req),'request':req})
    random.Random(202609263).shuffle(rows)
    write(BASE/'REQUESTS.json',rows)
    write(BASE/'freeze.json',{'pre_call_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      't0_commit':read(TOP/'oracle_state_effect/freeze.json')['t0_commit'],
      'bank_sha256':sha(TOP/'transition_bank/BANK.json'),
      'prompt_sha256':sha(prompt_path),'rubric_sha256':sha(BASE/'REVIEW_RUBRIC.md'),
      'common_sha256':sha(TOP/'common.py'),'requests_sha256':sha(BASE/'REQUESTS.json'),
      'provider':{k:p[k] for k in ['model','base_url','timeout_seconds','max_retries']},
      'generation_config':'SDK defaults; one call per observation',
      'random_seed':202609263,'call_order':[(x['case_id'],x['arm'],x['request_sha256']) for x in rows],
      'sample_count':12,'max_new_claims':2,
      'metrics':['support_precision','decision_relevance_precision','oracle_binding_recall',
                 'incidental_admission_rate','target_leakage_rate'],
      'failure_policy':'one call per case, zero retries, no repair, invalid output counts as no recovered claim'})
    print('T3 prepared',len(rows))

if __name__=='__main__':main()
