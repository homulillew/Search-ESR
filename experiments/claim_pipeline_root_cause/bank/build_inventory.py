"""Mechanical extraction of immutable observed windows; no network or inference."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
BASE_HEAD='dadf69f1c5fb96491f4fd3a34e0ece3418878de3'

def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 with p.open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')

def main():
 rows=[];sources={};excluded=[]
 def load(p):
  raw=p.read_bytes();assert raw==subprocess.check_output(['git','show',BASE_HEAD+':'+str(p.relative_to(ROOT))],cwd=ROOT)
  sources[str(p.relative_to(ROOT))]=sha(p);return json.loads(raw)
 def add(qid,gap,claims,w,origin,context,historical=()):
  if not w.get('text') or not gap:excluded.append({'origin':origin,'reason':'empty observation or Gap'});return
  obs=dict(w)
  if 'ref' in obs:obs['window_ref']=obs.pop('ref')
  obs['text_sha256']=hashlib.sha256(obs['text'].encode()).hexdigest()
  p={'qid':str(qid),'OneGap':gap,'C':claims,'Observation':[obs]}
  ident=digest(p);rows.append({'packet_id':'P_'+ident[:16],**p,'content_sha256':ident,'origin':origin,'context_kind':context,'historical_candidates':list(historical)})
 p=ROOT/'experiments/minimal_research_loop/verify_necessity/OBSERVATIONS.json'
 for i,x in enumerate(load(p)):
  add(x['qid'],x['active_gap'],x['relevant_committed_claims'],x['observation'],{'commit':BASE_HEAD,'path':str(p.relative_to(ROOT)),'pointer':f'/{i}','historical_origin':x['historical_origin']},'archived_review_packet; Gap/C may be reviewer-constructed, source observed')
 for stage in ['micro_recovery','h1_contract_continuation','h2_independent_recovery']:
  for p in sorted((ROOT/'experiments/recoverable_loop_clean'/stage/'run001/trajectories').glob('*/calls/*_reader.request.json')):
   wrapper=load(p);q=wrapper['request'];body=json.loads(q['messages'][-1]['content']);tid=p.parts[-3];qid=tid.split('_Q')[1].split('__')[0]
   response=p.with_name(p.name.replace('.request.json','.response.body'));candidates=[]
   if response.exists():
    raw=load(response)
    try:candidates=json.loads(raw['choices'][0]['message']['content'])['findings']
    except (ValueError,KeyError,TypeError,IndexError):pass
   for i,w in enumerate(body['Observation']):
    ref=w['window_ref'];cs=[c for c in candidates if set(c.get('evidence_refs',[]))=={ref}]
    add(qid,body['OneGap'],body['C'],w,{'commit':BASE_HEAD,'path':str(p.relative_to(ROOT)),'pointer':'/request/messages/-1/content:json/Observation/'+str(i),'response_path':str(response.relative_to(ROOT)) if response.exists() else None,'trajectory':tid},'actual_reader_request; one full observed window selected mechanically from acquisition',cs)
 unique={}
 for r in rows:
  ident=r['content_sha256']
  if ident in unique:
   unique[ident]['other_origins'].append(r['origin'])
   for c in r['historical_candidates']:
    if c not in unique[ident]['historical_candidates']:unique[ident]['historical_candidates'].append(c)
  else:unique[ident]={**r,'other_origins':[]}
 rs=sorted(unique.values(),key=lambda x:x['packet_id'])
 save(BASE/'inventory.json',{'base':BASE_HEAD,'sources':sources,'packets':rs,'excluded':excluded,'calls':0,'retrieval_calls':0})
 from collections import Counter
 print('rows',len(rows),'dedup',len(rs),'qids',len({r['qid'] for r in rs}));print(Counter(r['qid'] for r in rs))
if __name__=='__main__':main()
