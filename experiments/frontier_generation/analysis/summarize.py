import sys,statistics,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *

FLAGS=['stale','drift','unsupported_premise','over_broad','premature_stop','missed_stop','belief_error']
def rate(n,d):return {'n':n,'d':d,'rate':n/d if d else None}
def metrics(rows):
    n=len(rows);out={'valid':rate(sum(r['valid'] for r in rows),n)}
    for k in FLAGS:out[k]=rate(sum(r[k] for r in rows),n)
    out['critical']=rate(sum(r['critical'] for r in rows),n)
    out['provider_or_contract_failure']=rate(sum(r['output'] is None for r in rows),n)
    acts=[r for r in rows if r['output'] and r['output']['decision']=='act']
    stops=[r for r in rows if r['output'] and r['output']['decision']=='stop']
    out['valid_act']=rate(sum(r['valid'] for r in acts),len(acts))
    out['correct_stop']=rate(sum(r['valid'] for r in stops),len(stops))
    for k in ['input','output','reasoning','hit','miss']:
        vals=[r['usage'][k] for r in rows if r.get('usage') and r['usage'].get(k) is not None]
        out[k]={'reported':len(vals),'sum':sum(vals) if vals else None,'mean':statistics.mean(vals) if vals else None,'median':statistics.median(vals) if vals else None}
    cache=[r['usage'] for r in rows if r.get('usage') and r['usage'].get('input') is not None and r['usage'].get('hit') is not None]
    out['cache_hit_rate']=rate(sum(u['hit'] for u in cache),sum(u['input'] for u in cache))
    secs=[r['elapsed_seconds'] for r in rows if r['attempted']]
    out['elapsed']={'mean':statistics.mean(secs) if secs else None,'median':statistics.median(secs) if secs else None,'sum':sum(secs)}
    return out

def main():
    base=TOP/'f1_state_sufficiency';rows=rd(base/'frontier_outputs.json');key=rd(base/'private_review_key.json')
    ann=rd(base/'semantic_review.json');assert set(ann)==set(key)
    byid={key[k]:v for k,v in ann.items()}
    cov=rd(TOP/'bank/COVERAGE.json');bank={c['case_id']:c for c in rd(TOP/'bank/CHECKPOINT_BANK.json')}
    for r in rows:
        r.update(byid[r['id']]);r['critical']=any(r[k] for k in ['premature_stop','drift','unsupported_premise'])
        r['deferred_requirement']=bool(r['arm']=='S' and r['valid'] and any(k in cov[r['case_id']]['deferred_requirements'] for k in r['requirement_ids']))
        r['deferred_subrelation']=bool(r['arm']=='S' and r['valid'] and r.get('reactivates_subrelation',False))
    groups=collections.defaultdict(list)
    for r in rows:groups[r['case_id'],r['arm']].append(r)
    stability=[]
    for (case,arm),rs in sorted(groups.items()):
        assert len(rs)==2
        n=sum(r['valid'] for r in rs)
        if n==2:
            same=bool(set(rs[0]['requirement_ids'])&set(rs[1]['requirement_ids'])) or all(r['output']['decision']=='stop' for r in rs)
            category='same_valid_requirement' if same else 'different_both_valid'
        else:category='one_valid' if n==1 else 'both_invalid'
        stability.append({'case_id':case,'qid':bank[case]['qid'],'arm':arm,'category':category,'focuses':[r['focus'] for r in rs]})
    ranking=[]
    for case in bank:
        hs=sorted(groups[case,'H'],key=lambda x:x['replicate']);u=next((r['usage']['input'] for r in hs if r.get('usage') and r['usage'].get('input') is not None),None)
        ranking.append((u if u is not None else bank[case]['history_chars'],case,u is None))
    ranking.sort();quartiles={case:'Q'+str(i//6+1) for i,(_,case,_) in enumerate(ranking)}
    repaired=[]
    for case in bank:
        if any(r['critical'] for r in groups[case,'S']) and all(r['valid'] and not r['critical'] for r in groups[case,'SH']):repaired.append(case)
    summary={'planned':len(rows),'attempted':sum(r['attempted'] for r in rows),
        'arms':{a:metrics([r for r in rows if r['arm']==a]) for a in ['H','S','SH']},
        'per_qid':{str(q):{a:metrics([r for r in rows if r['qid']==q and r['arm']==a]) for a in ['H','S','SH']} for q in sorted({r['qid'] for r in rows})},
        'quartiles':{q:{a:metrics([r for r in rows if quartiles[r['case_id']]==q and r['arm']==a]) for a in ['H','S','SH']} for q in ['Q1','Q2','Q3','Q4']},
        'quartile_membership':quartiles,'quartile_fallback_cases':[c for _,c,missing in ranking if missing],
        'stability':{a:dict(collections.Counter(x['category'] for x in stability if x['arm']==a)) for a in ['H','S','SH']},
        'deferred':{'full_requirement_outputs':[r['id'] for r in rows if r['deferred_requirement']],
                    'subrelation_outputs':[r['id'] for r in rows if r['deferred_subrelation']],
                    'eligible_S_calls':2*sum(bool(c['deferred_requirements']) for c in cov.values())},
        'critical_repairs':{'cases':repaired,'qids':sorted({bank[c]['qid'] for c in repaired})}}
    s=summary['arms']['S']['valid']['rate'];sh=summary['arms']['SH']['valid']['rate']
    critical=len(repaired)>=3 and len(summary['critical_repairs']['qids'])>=2
    summary['gate']={'S_at_least_85_percent':s>=.85,'SH_minus_S_at_most_5pp':sh-s<=.05+1e-9,
                     'no_multicase_critical_deficit':not critical,'SH_minus_S_pp':100*(sh-s),
                     'pass':s>=.85 and sh-s<=.05+1e-9 and not critical,
                     'SH_positive_refutation':sh-s>=.10-1e-9 or critical}
    summary['closure_sensitivity']={a:rate(sum(r['valid'] or (r['case_id']=='F24' and r['output'] and r['output']['decision']=='stop') for r in rows if r['arm']==a),48) for a in ['H','S','SH']}
    summary['total_usage']=metrics(rows)
    wr(base/'reviewed_outputs.json',rows);wr(base/'replicate_stability.json',stability);wr(base/'summary.json',summary)
    print(json.dumps({'arms':{a:{k:v[k] for k in ['valid','stale','drift','unsupported_premise','over_broad','premature_stop','missed_stop']} for a,v in summary['arms'].items()},'gate':summary['gate'],'stability':summary['stability'],'deferred':summary['deferred']},indent=2))

if __name__=='__main__':main()
