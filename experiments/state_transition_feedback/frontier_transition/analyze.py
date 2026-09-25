"""Score T2 with the pre-frozen progress-source sets; do not relabel truth."""
import json,statistics,sys
from collections import Counter
from pathlib import Path

BASE=Path(__file__).resolve().parent
TOP=BASE.parent
sys.path.insert(0,str(TOP))
from common import read,write
from oracle_state_effect.analyze import first,score,features

def main():
    truth={x['case_id']:x for x in read(BASE/'PROGRESS_TRUTH.json')}
    cases={x['case_id']:x for x in read(TOP/'transition_bank/BANK.json')}
    early=read(BASE/'corrected/retrieval_results.json')
    premature=[dict(x,arm='F_PREMATURE') for x in read(TOP/'oracle_state_effect/retrieval_results.json') if x['arm']=='PRE']
    rows=early+premature
    assert len(early)==len(premature)==12
    ids={cid:set(x['early_progress_doc_ids']) for cid,x in truth.items()}
    clean=set(cases)-{'U1_B07'}
    out={}
    for cohort,keep in [('all',set(cases)),('clean',clean)]:
        a=[x for x in early if x['case_id'] in keep]
        b=[x for x in premature if x['case_id'] in keep]
        # The two arms answer different gaps, so each is scored against its own
        # pre-frozen progress set. Premature progress includes valid downstream bridges.
        pids={cid:set(x['premature_progress_doc_ids']) for cid,x in truth.items()}
        sa=score(a,ids);sb=score(b,pids)
        rank_a={x['case_id']:first(x,ids[x['case_id']]) or 51 for x in a}
        rank_b={x['case_id']:first(x,pids[x['case_id']]) or 51 for x in b}
        movement={cid:('early_better' if rank_a[cid]<rank_b[cid] else 'premature_better' if rank_b[cid]<rank_a[cid] else 'tie') for cid in keep}
        out[cohort]={'F_EARLY':sa,'F_PREMATURE':sb,'rank_movement':dict(Counter(movement.values())),
          'by_case':{cid:{'early_rank':rank_a[cid] if rank_a[cid]<=50 else None,
                          'premature_rank':rank_b[cid] if rank_b[cid]<=50 else None,
                          'movement':movement[cid]} for cid in sorted(keep)}}
    q={x['case_id']:x for x in read(BASE/'corrected/QUERIES.json')}
    req={x['case_id']:x for x in read(BASE/'corrected/REQUESTS.json')}
    early_features=[features(dict(q[cid],request=req[cid]['request']),cases[cid]) for cid in clean]
    out['clean']['F_EARLY_query_proxy']={
      'mean_clue_load':round(statistics.mean(x['clue_load'] for x in early_features),4),
      'candidate_inclusion':sum(x['candidate_in_query'] for x in early_features),
      'candidate_guessed':sum(x['candidate_guessed'] for x in early_features)}
    out['validity']={'early_valid_calls':sum(x['output'] is not None for x in q.values()),
       'early_retrieval_errors':sum(x['retrieval_error'] is not None for x in early)}
    usage=[x.get('usage') or {} for x in q.values()]
    h=sum(x.get('prompt_cache_hit_tokens',0) for x in usage)
    m=sum(x.get('prompt_cache_miss_tokens',0) for x in usage)
    out['cache']={'hit_tokens':h,'miss_tokens':m,'hit_rate':round(h/(h+m),4) if h+m else None}
    write(BASE/'summary.json',out)
    print('T2',out['clean']['F_EARLY']['hit']['5'],out['clean']['F_PREMATURE']['hit']['5'])

if __name__=='__main__':main()
