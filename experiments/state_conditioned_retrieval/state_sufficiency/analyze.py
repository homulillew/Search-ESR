"""Post-retrieval, frozen-truth scoring and descriptive mechanism audit."""
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

BASE=Path(__file__).resolve().parent
TOP=BASE.parent
STOP=set('a an the of to in on for with by from and or is was were has have had did does do this that which who what when where how as at its their his her he she they it be been can could would should into between then than more less one two three four after before about against under over'.split())

def read(p):return json.loads(p.read_text())
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def toks(s):return re.findall(r"[\w]+(?:'[\w]+)?",s.lower())
def pct(n,d):return round(100*n/d,2) if d else None
def rank(r):return r['first_sufficient_rank'] or 51
def hit(r,k):return r['first_sufficient_rank'] is not None and r['first_sufficient_rank']<=k
def progress(r,k):return hit(r,k) or (r['first_bridge_rank'] is not None and r['first_bridge_rank']<=k)

def metrics(rows):
    n=len(rows)
    return {'n':n,'recall':{str(k):{'hit':sum(hit(r,k) for r in rows),'pct':pct(sum(hit(r,k) for r in rows),n)}
                          for k in [1,3,5,10,20,50]},
            'MRR@50':round(sum(1/r['first_sufficient_rank'] for r in rows if r['first_sufficient_rank'])/n,4) if n else None,
            'ProgressHit@5':{'hit':sum(progress(r,5) for r in rows),'pct':pct(sum(progress(r,5) for r in rows),n)}}

def paired(rows,a,b):
    ids=sorted(set(x['case_id'] for x in rows if x['arm']==a)&set(x['case_id'] for x in rows if x['arm']==b))
    index={(x['case_id'],x['arm']):x for x in rows}
    movement={cid:'improved' if rank(index[cid,b])<rank(index[cid,a]) else
              'worsened' if rank(index[cid,b])>rank(index[cid,a]) else 'tie' for cid in ids}
    return {'n':len(ids),'counts':dict(Counter(movement.values())),
            'improved_qids':sorted({index[cid,a]['qid'] for cid in ids if movement[cid]=='improved'}),
            'movement':movement}

def query_features(item,case,freeze):
    q=item['search_query'] or ''
    qid=case['qid'];aliases=freeze['candidate_aliases'][qid]
    in_query=any(a.lower() in q.lower() for a in aliases)
    req=json.loads(item['request_user'])
    state=req['Current Research State']; state_text=json.dumps(state,ensure_ascii=False)
    explicit=any(a.lower() in state_text.lower() for a in aliases)
    question_gap=req['Question']+' '+req['Current Target Gap']
    in_supplied=any(a.lower() in (question_gap+' '+state_text).lower() for a in aliases)
    blocked=set(toks(case['target_gap']))
    for a in aliases:blocked.update(toks(a))
    question_clues={w for w in toks(case['raw_question']) if w not in blocked and w not in STOP and len(w)>2}
    qt=[w for w in toks(q) if w not in STOP and len(w)>2]
    clue=sum(w in question_clues for w in qt)
    relation=[a for a in freeze['relation_terms'][case['case_id']] if a.lower() in q.lower()]
    return {'case_id':case['case_id'],'qid':qid,'arm':item['arm'],'search_query':item['search_query'],
            'query_error':item['error'],'candidate_inclusion':in_query,
            'candidate_explicit_in_state':explicit,
            'candidate_guessed_without_input':in_query and not in_supplied,
            'relation_anchor_matches':relation,'relation_coverage':bool(relation),
            'query_word_count':len(toks(q)),
            'raw_question_clue_tokens':clue,'raw_question_clue_load':round(clue/len(qt),4) if qt else 0,
            'input_prompt_tokens':(item.get('usage') or {}).get('prompt_tokens')}

def main():
    freeze=read(BASE/'freeze.json')
    bank={x['case_id']:x for x in read(TOP/'state_bank/BANK.json')}
    queries=read(BASE/'QUERIES.json');results=read(BASE/'retrieval_results.json')
    reqs={(x['case_id'],x['arm']):x for x in read(BASE/'REQUESTS.json')}
    assert len(queries)==len(results)==len(reqs)==120
    qix={(x['case_id'],x['arm']):x for x in queries}
    rix={(x['case_id'],x['arm']):x for x in results}
    assert set(qix)==set(rix)==set(reqs)
    enriched=[]
    for x in queries:
        req=reqs[x['case_id'],x['arm']]['request']['messages'][1]['content']
        enriched.append(query_features(dict(x,request_user=req),bank[x['case_id']],freeze))
    write(BASE/'QUERY_ANALYSIS.json',enriched)
    arms=['S0','S1','S2','S3','S_noise','S_history']
    overall={a:metrics([x for x in results if x['arm']==a]) for a in arms}
    qid={qid:{a:metrics([x for x in results if x['qid']==qid and x['arm']==a])
              for a in ['S0','S1','S2','S3']} for qid in sorted({x['qid'] for x in results})}
    typ={t:{a:metrics([x for x in results if bank[x['case_id']]['primary_type']==t and x['arm']==a])
           for a in ['S0','S1','S2','S3']} for t in sorted({x['primary_type'] for x in bank.values()})}
    pairs={f'{a}->{b}':paired(results,a,b) for a,b in [('S0','S1'),('S1','S2'),('S2','S3'),('S0','S3'),
                                                          ('S0','S_noise'),('S0','S_history'),('S3','S_history')]}
    mechanism={a:{'n':len(fs),'candidate_inclusion_pct':pct(sum(x['candidate_inclusion'] for x in fs),len(fs)),
                  'candidate_guessed_without_input':sum(x['candidate_guessed_without_input'] for x in fs),
                  'relation_coverage_pct':pct(sum(x['relation_coverage'] for x in fs),len(fs)),
                  'mean_clue_load':round(statistics.mean(x['raw_question_clue_load'] for x in fs),4),
                  'mean_query_words':round(statistics.mean(x['query_word_count'] for x in fs),2),
                  'median_prompt_tokens':statistics.median(x['input_prompt_tokens'] for x in fs if x['input_prompt_tokens'] is not None)}
               for a in arms for fs in [[x for x in enriched if x['arm']==a]]}
    usage=[x.get('usage') or {} for x in queries]
    cache_hit=sum(x.get('prompt_cache_hit_tokens',0) for x in usage)
    cache_miss=sum(x.get('prompt_cache_miss_tokens',0) for x in usage)
    delta=overall['S3']['recall']['5']['pct']-overall['S0']['recall']['5']['pct']
    controls=[cid for cid in bank if (cid,'S_noise') in rix]
    r5=lambda arm: pct(sum(hit(rix[cid,arm],5) for cid in controls),len(controls))
    cdelta=r5('S3')-r5('S0');ndelta=r5('S_noise')-r5('S0')
    raw_adv=r5('S_history')-r5('S3')
    raw_better=sum(rank(rix[cid,'S_history'])<rank(rix[cid,'S3']) for cid in controls)
    ceiling=100-overall['S0']['recall']['5']['pct']<15
    p=pairs['S0->S3']
    primary=delta>=15 or (ceiling and p['counts'].get('improved',0)>=12 and p['counts'].get('worsened',0)<=3 and len(p['improved_qids'])>=4)
    mechanism_pass=(mechanism['S3']['candidate_inclusion_pct']>mechanism['S0']['candidate_inclusion_pct']
                    and mechanism['S3']['mean_clue_load']<mechanism['S0']['mean_clue_load'])
    noise_pass=cdelta>0 and ndelta<.5*cdelta
    history_pass=raw_adv<=5 and raw_better<=6
    summary={'overall':overall,'qid':qid,'case_type':typ,'pairs':pairs,'mechanism':mechanism,
             'cache':{'hit_tokens':cache_hit,'miss_tokens':cache_miss,
                      'hit_rate':round(cache_hit/(cache_hit+cache_miss),4) if cache_hit+cache_miss else None},
             'controls_paired12':{'S0_recall5_pct':r5('S0'),'S3_recall5_pct':r5('S3'),
                                  'noise_recall5_pct':r5('S_noise'),'history_recall5_pct':r5('S_history'),
                                  'S3_gain_pp':cdelta,'noise_gain_pp':ndelta,'history_advantage_pp':raw_adv,
                                  'history_rank_better_count':raw_better},
             'gate':{'S3_minus_S0_recall5_pp':delta,'ceiling_condition':ceiling,
                     'primary':primary,'mechanism':mechanism_pass,'noise':noise_pass,
                     'history':history_pass,'full_S1_pass':all([primary,mechanism_pass,noise_pass,history_pass])},
             'failures':{'query':sum(x['error'] is not None for x in queries),
                         'retrieval':sum(x['retrieval_error'] is not None for x in results)}}
    write(BASE/'summary.json',summary)
    def rankstr(x):return str(x['first_sufficient_rank']) if x['first_sufficient_rank'] else '>50'
    lines=['# S1 case analysis','','Ranks are first frozen sufficient documents; `>50` is a miss. No truth was expanded after retrieval.','',
           '| Case | qid | Type | S0 | S1 | S2 | S3 | S3 vs S0 | Bridge S0→S3 |','|---|---:|---|---:|---:|---:|---:|---|---|']
    for cid,c in bank.items():
        rs=[rix[cid,a] for a in ['S0','S1','S2','S3']]
        lines.append(f"| {cid} | {c['qid']} | {c['primary_type']} | "+' | '.join(rankstr(r) for r in rs)+
                     f" | {p['movement'][cid]} | {rankstr({'first_sufficient_rank':rs[0]['first_bridge_rank']})}→{rankstr({'first_sufficient_rank':rs[3]['first_bridge_rank']})} |")
    lines += ['','## Query examples','']
    for cid in ['U1_B06','U1_C01','U1_B04','U1_C05','U1_C06']:
        lines.append(f"### {cid}")
        lines.append('')
        for a in ['S0','S1','S2','S3']:
            lines.append(f"- {a}: `{qix[cid,a]['search_query']}` (rank {rankstr(rix[cid,a])})")
        lines.append('')
    (BASE/'CASE_ANALYSIS.md').write_text('\n'.join(lines)+'\n')
    print('analysis complete',summary['gate'],flush=True)

if __name__=='__main__':main()
