"""Score T1 using the T0 frozen expanded direct-source set."""
import json,re,statistics,sys
from collections import Counter
from pathlib import Path

BASE=Path(__file__).resolve().parent
TOP=BASE.parent
sys.path.insert(0,str(TOP))
from common import read,write

ALIASES={'517':['Peter King','Peter Nzioki'],'435':['Oliver Mtukudzi'],
 '1094':['Paris Saint-Germain','PSG'],'311':['Hijitus'],'186':['Galacta'],
 '1034':['Heart Evangelista'],'177':['Rangers','Enugu Rangers'],
 '580':["You're the Worst","Youre the Worst"],'546':['Ding Junhui']}
STOP=set('a an the of to in on for with by from and or is was were has have had did does do this that which who what when where how as at its their his her he she they it be been can could would should into between then than more less one two three four after before about against under over identified candidate current'.split())
KS=[1,3,5,10,20,50]
def toks(s):return re.findall(r"[\w]+(?:'[\w]+)?",s.lower())
def pct(n,d):return round(100*n/d,2) if d else None
def first(row,truth):
    return next((h['rank'] for h in row['hits'] if h['docid'] in truth),None)
def score(rows,ids):
    ranks=[first(r,ids[r['case_id']]) for r in rows];n=len(ranks)
    return {'n':n,'hit':{str(k):sum(v is not None and v<=k for v in ranks) for k in KS},
            'recall_pct':{str(k):pct(sum(v is not None and v<=k for v in ranks),n) for k in KS},
            'MRR@50':round(sum(1/v for v in ranks if v)/n,4) if n else None}
def features(q,c):
    query=(q['output'] or {}).get('search_query','');aliases=ALIASES[c['qid']]
    has=any(a.lower() in query.lower() for a in aliases)
    inp=json.loads(q['request']['messages'][1]['content'])
    supplied=json.dumps(inp,ensure_ascii=False)
    guessed=has and not any(a.lower() in supplied.lower() for a in aliases)
    blocked=set(toks(c['next_gap']))
    for a in aliases:blocked.update(toks(a))
    clues={w for w in toks(c['question']) if w not in blocked and w not in STOP and len(w)>2}
    words=[w for w in toks(query) if w not in STOP and len(w)>2]
    clue_load=sum(w in clues for w in words)/len(words) if words else 0
    gap_words={w for w in toks(c['next_gap']) if w not in STOP and len(w)>2}
    relation_coverage=len(set(words)&gap_words)/len(gap_words) if gap_words else 0
    return {'candidate_in_query':has,'candidate_guessed':guessed,'clue_load':round(clue_load,4),
            'relation_lexical_coverage':round(relation_coverage,4),'query_words':len(toks(query)),
            'prompt_tokens':(q.get('usage') or {}).get('prompt_tokens')}
def strength(delta,improved,worsened,n):
    if delta>=15 or (improved/n>=.5 and worsened/n<=.15):return 'Strong'
    if delta>=8 or (improved/n>=.3 and improved>=2*worsened):return 'Moderate'
    if improved>worsened or delta>0:return 'Weak'
    if worsened>improved or delta<0:return 'Negative'
    return 'Null'

def main():
    cases={x['case_id']:x for x in read(TOP/'transition_bank/BANK.json')}
    truths={x['case_id']:x for x in read(TOP/'transition_bank/PRIVATE_TRUTH.json')}
    queries=read(BASE/'QUERIES.json');results=read(BASE/'retrieval_results.json')
    reqs={(x['case_id'],x['arm']):x for x in read(BASE/'REQUESTS.json')}
    assert len(queries)==len(results)==36
    qix={(x['case_id'],x['arm']):dict(x,request=reqs[x['case_id'],x['arm']]['request']) for x in queries}
    rix={(x['case_id'],x['arm']):x for x in results}
    direct={cid:set(x['direct_sufficient_doc_ids']) for cid,x in truths.items()}
    canonical={cid:set(x['canonical_direct_doc_ids']) for cid,x in truths.items()}
    arms=['PRE','POST','RAW']
    summary={'arms':{a:score([x for x in results if x['arm']==a],direct) for a in arms},
             'canonical':{a:score([x for x in results if x['arm']==a],canonical) for a in arms}}
    pairs={}
    for a,b in [('PRE','POST'),('PRE','RAW'),('RAW','POST')]:
        movement={cid:'improved' if (first(rix[cid,b],direct[cid]) or 51)<(first(rix[cid,a],direct[cid]) or 51) else
                  'worsened' if (first(rix[cid,b],direct[cid]) or 51)>(first(rix[cid,a],direct[cid]) or 51) else 'tie'
                  for cid in cases}
        pairs[f'{a}->{b}']={'counts':dict(Counter(movement.values())),'movement':movement,
          'improved_qids':sorted({cases[cid]['qid'] for cid,m in movement.items() if m=='improved'})}
    summary['pairs']=pairs
    feat={a:[features(qix[cid,a],c) for cid,c in cases.items()] for a in arms}
    summary['query_mechanism']={a:{'candidate_inclusion':sum(x['candidate_in_query'] for x in xs),
      'candidate_guessed':sum(x['candidate_guessed'] for x in xs),
      'mean_clue_load':round(statistics.mean(x['clue_load'] for x in xs),4),
      'mean_relation_lexical_coverage':round(statistics.mean(x['relation_lexical_coverage'] for x in xs),4),
      'mean_query_words':round(statistics.mean(x['query_words'] for x in xs),2),
      'median_prompt_tokens':statistics.median(x['prompt_tokens'] for x in xs if x['prompt_tokens'] is not None)}
      for a,xs in feat.items()}
    summary['qid']={qid:{a:score([x for x in results if x['qid']==qid and x['arm']==a],direct)
                              for a in arms} for qid in sorted({c['qid'] for c in cases.values()})}
    usage=[x.get('usage') or {} for x in queries]
    h=sum(x.get('prompt_cache_hit_tokens',0) for x in usage)
    m=sum(x.get('prompt_cache_miss_tokens',0) for x in usage)
    summary['cache']={'hit_tokens':h,'miss_tokens':m,'hit_rate':round(h/(h+m),4) if h+m else None}
    summary['validity']={'valid_query_calls':sum(x['output'] is not None for x in queries),
                         'retrieval_errors':sum(x['retrieval_error'] is not None for x in results)}
    delta=summary['arms']['POST']['recall_pct']['5']-summary['arms']['PRE']['recall_pct']['5']
    counts=pairs['PRE->POST']['counts']
    summary['effect']={'POST_minus_PRE_Direct5_pp':round(delta,2),
      'strength':strength(delta,counts.get('improved',0),counts.get('worsened',0),len(cases))}
    write(BASE/'summary.json',summary)
    lines=['# T1 paired case results','','Rank is first frozen **any-sufficient** document; `>50` is a miss.','',
      '| Case | qid | PRE | POST | RAW | POST–PRE | PRE query | POST query |',
      '|---|---:|---:|---:|---:|---|---|---|']
    def rankstr(cid,arm):return str(first(rix[cid,arm],direct[cid]) or '>50')
    for cid,c in cases.items():
        lines.append(f"| {cid} | {c['qid']} | {rankstr(cid,'PRE')} | {rankstr(cid,'POST')} | {rankstr(cid,'RAW')} | "+
          f"{pairs['PRE->POST']['movement'][cid]} | {qix[cid,'PRE']['output']['search_query'] if qix[cid,'PRE']['output'] else '[invalid]'} | "+
          f"{qix[cid,'POST']['output']['search_query'] if qix[cid,'POST']['output'] else '[invalid]'} |")
    (BASE/'CASE_ANALYSIS.md').write_text('\n'.join(lines).rstrip()+'\n')
    print('T1 analyzed',summary['effect'],flush=True)

if __name__=='__main__':main()
