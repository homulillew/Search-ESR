from progress import *
# Match the immutable harness digest formatting for evidence identity.
def hd(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def export():
 b=TOP/'three_round_loop_v2';cells=read(b/('results.json' if (b/'results.json').exists() else 'checkpoint.json'))
 packets=[];mapping={};ups=[];umap={};catalog={};pool=read(TOP/'bank/PRIVATE_TRUTH.json')['known_source_sets'];hist=read(TOP/'bank/HISTORICAL_SOURCE_SETS.json')['historical_fact_source_sets'];truth=read(TOP/'bank/PRIVATE_TRUTH.json')['snapshots']
 keys=[]
 for key,c in cells.items():
  for di,d in enumerate(c['decisions']):keys.append((key,di))
 for i,(key,di) in enumerate(sorted(keys,key=lambda k:hd(['loop-decision',k])),1):
  c=cells[key];d=c['decisions'][di];s=d['pre_state'];pid=f'L{i:03}';acts=[];obs=[]
  for ai,a in enumerate(d['actions']):
   ids=[];dids={v['doc_ref']:v['docid'] for v in a.get('audit',{}).get('handles',{}).get('documents',[])}
   for w in a['observations']:
    eid=hd([c['qid'],w['url'],w['text']])[:16];did=dids.get(w['doc_ref']);known=set(pool[c['qid']]['verified_fact_source_docids'])|set(hist.get(c['qid'],[]))
    catalog[eid]={'evidence_id':eid,'qid':c['qid'],'question':s['question'],'title':w['title'],'url':w['url'],'text':w['text'],'docid':did,'in_primary_pool':did in known};ids.append(eid);obs.append({'evidence_id':eid,**w})
   acts.append({'action_index':ai,'action':a['action'],'evidence_ids':ids,'error':a['error']})
  mapping[pid]={'case_id':key+':'+str(di),'cell':key,'qid':c['qid'],'arm':c['arm'],'round':di,'actions':acts}
  o=d['actor']['output'];packets.append({'packet_id':pid,'qid':c['qid'],'question':s['question'],'verified_claims':[x['statement'] for x in s['verified_claims']],'working_hypothesis':s['working_hypothesis'],'gold_residual_rubric':truth[c['seed_snapshot']],'gold_note':'seed-only reference; adjudicate current source-supported online state independently','selected_gap':o['gap'] if o else None,'decision':o['decision'] if o else None,'observations':obs,'error':d['error']})
 ukeys=[(key,ui) for key,c in cells.items() for ui in range(len(c['updates']))]
 for i,(key,ui) in enumerate(sorted(ukeys,key=lambda k:hd(['loop-updater',k])),1):
  c=cells[key];u=c['updates'][ui];uid=f'U{i:03}';umap[uid]={'cell':key,'update_index':ui,'round':u['round'],'wave':u['wave']}
  ups.append({'packet_id':uid,'qid':c['qid'],'question':c['state']['question'],'claims_before':[v['statement'] for v in u['pre_state']['verified_claims']],'hypothesis_before':u['pre_state']['working_hypothesis'],'observation':u['observation'],'proposal':u['proposal']['output'],'error':u['proposal']['error']})
 for name,x in [('REVIEW_PACKETS',packets),('PRIVATE_PACKET_MAP',mapping),('EVIDENCE_CATALOG',list(catalog.values())),('UPDATER_REVIEW_PACKETS',ups),('PRIVATE_UPDATER_MAP',umap)]:write(b/(name+'.json'),x)
 print('decisions',len(packets),'updates',len(ups),'unique evidence',len(catalog))
if __name__=='__main__':export()
