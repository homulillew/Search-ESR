"""Offline semantic verdicts, backed by frozen raw texts; no model calls.

Each positive coordinate below was inspected for entity/relation/time binding.
All other windows were screened and the near misses reviewed explicitly.
"""
import collections,datetime,hashlib,json,re,sqlite3,statistics
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
def rd(p):return json.loads(Path(p).read_text())
def wr(name,x):(P/'analysis'/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def ratio(n,d):return {'n':n,'d':d,'rate':n/d if d else None}
def mean(xs):return statistics.mean(xs) if xs else None

# Coordinates: (decision step, zero-based returned-window ordinal).
POS={
'C_VN01:A0':[(1,0)],'C_VN01:A1':[(2,0)],'C_VN01:A2':[(1,0)],
'C_VN03:A0':[(1,0)],'C_VN03:A1':[(1,0)],'C_VN03:A2':[(2,0)],'C_VN03:A3':[(1,0)],
'C_VN07:A1':[(1,2)],
'C_VP06:A1':[(1,0)],'C_VP06:A3':[(1,0)],
'C_VP12:A0':[(2,0)],'C_VP12:A1':[(2,0)],'C_VP12:A2':[(1,0)],'C_VP12:A3':[(1,0)],
'K_VN06:A0':[(1,2),(1,3)],'K_VN06:A1':[(2,3),(2,4)],'K_VN06:A2':[(1,2),(1,3)],
'K_VN08:A0':[(1,0)],'K_VN08:A1':[(1,0)],'K_VN08:A2':[(1,0)],'K_VN08:A3':[(1,0)],
'K_VN09:A1':[(1,0)],'K_VN09:A2':[(1,3)],'K_VN09:A3':[(1,0)],
'K_VP01:A0':[(1,0)],'K_VP01:A2':[(1,0)],'K_VP01:A3':[(1,0)],
'K_VP09:A0':[(1,1)],'K_VP09:A1':[(1,0)],'K_VP09:A2':[(1,1)],'K_VP09:A3':[(1,0)],
'K_VP10:A0':[(1,0),(2,0)],'K_VP10:A1':[(1,0)],'K_VP10:A2':[(1,0),(2,0)],'K_VP10:A3':[(1,0)],
'K_VP11:A0':[(1,0)],'K_VP11:A1':[(1,0)],'K_VP11:A2':[(1,0)],'K_VP11:A3':[(1,0)],
'K_VP13:A0':[(1,0)],'K_VP13:A1':[(1,0)],'K_VP13:A2':[(1,0)],'K_VP13:A3':[(1,0)],
'K_VP14:A0':[(1,1)],'K_VP14:A2':[(1,1)],'K_VP14:A3':[(1,0)],
'K_VP18:A0':[(1,0)],'K_VP18:A1':[(1,0)],'K_VP18:A2':[(1,0)],'K_VP18:A3':[(1,0)],
'N_VP01:A0':[(1,0)],'N_VP01:A1':[(1,0)],'N_VP01:A2':[(1,0)],
'N_VP08:A0':[(1,3),(1,4)],'N_VP08:A1':[(1,4)],'N_VP08:A2':[(1,3),(1,4)],
'N_VP11:A0':[(1,0),(1,1)],'N_VP11:A1':[(1,0),(1,1)],'N_VP11:A2':[(1,0),(1,3)],
'N_VP13:A0':[(1,0)],'N_VP13:A1':[(1,0)],'N_VP13:A2':[(1,0)],
'N_VP15:A0':[(1,0)],'N_VP15:A1':[(1,0)],'N_VP15:A2':[(1,0)],
'N_VP17:A0':[(1,0),(1,1),(1,3)],'N_VP17:A1':[(1,0),(1,1),(1,3)],'N_VP17:A2':[(1,0),(1,1)]}
REASONS={
'VN01':'The actual infobox lists one director and three named writers; this refutes exactly two writers.',
'VN03':'Actual first_aired/last_aired fields include August/March, refuting January/December; DVD dates are not used.',
'VN06':'The Class of 92 sentence explicitly names Ronnie and binds all three professional debuts to 1992–93, refuting the interval.',
'VN07':'Class of 92 explicitly binds John Higgins to the professional debut season; a junior match against Higgins alone is insufficient.',
'VN08':'Explicit Williams professional debut in 1992 refutes 1995–2006.',
'VN09':'Williams profile explicitly gives cumulative maximum total three alongside later-2025 date context; an earlier cutoff cannot exceed that total.',
'VP01':'Rangers Nigeria Premier League honours explicitly list wins in 1974/1975/1977/1981/1982, within the required interval.',
'VP06':'Returned PC interview passage explicitly states normal 8x11 printing paper; its dated prefix already establishes the wireless keyboard. No 8.5x11 query substitution is treated as evidence.',
'VP08':'The same musician is explicitly attributed 67 career albums, rather than merely more than 60.',
'VP09':'The actual quote is attributed to Mtukudzi in the 2015 interview, binding wording and decade.',
'VP10':'The actual biography lead explicitly calls Mtukudzi a human rights activist.',
'VP11':'Actor-specific paragraph states father served in Kenyan Army and mother worked in military/barracks hospital.',
'VP12':'Actual 2005 Constant Gardener filmography row binds Peter Nzioki to Policeman 1.',
'VP13':'Ding biography explicitly says turned professional in 2003, within the required interval.',
'VP14':'Either Ding seven/latest-2024 or the fourth maximum in 2011 establishes more than three before January 2025; generic 2025 cumulative total alone would be insufficient.',
'VP15':'Series metadata explicitly states five seasons, establishing fewer than ten.',
'VP17':'Nick Mutuma first big/break-out role explicitly dated 2008.',
'VP18':'The Music paragraph explicitly dates Mutuma first single to 2013.'}
SOURCES={
'VN01':{'20521'},'VN03':{'20521'},'VN05':{'68507'},
'VN06':{'4975','41736'},'VN07':{'4975'},'VN08':{'4975'},'VN09':{'4975','64519','42120'},
'VP01':{'86072'},'VP03':{'22411'},'VP06':{'5266'},'VP08':{'54137','57503','70761'},'VP09':{'54137'},'VP10':{'30145'},
'VP11':{'67431','43080'},'VP12':{'67431','63369'},'VP13':{'38231'},'VP14':{'64519','42120','38231'},'VP15':{'10836'},'VP17':{'53719','19441','43080'},'VP18':{'53719'}}
# Sparse overrides for source-level audit context, not relevance inferred from a title.
NEG_REASON={
'VN01':'Production writer/director credits are absent; fictional museum director or a clipped infobox is not the requested credit list.',
'VN03':'No original-run month evidence; broadcast year ranges, unrelated show dates and DVD release dates do not answer the Need.',
'VN05':'No Brum run dates in this window. A2 retrieves correct full source 68507 once, but its preview starts below the Brum 1991–2002 row.',
'VN06':'No Ronnie professional-debut relation; maximum counts and Williams own 1992 debut cannot substitute.',
'VN07':'No Higgins professional-debut relation; Williams professional date and Higgins junior matches cannot establish it.',
'VP03':'One offline player, reviews and game credits do not exclude other player modes; no explicit no-multiplayer source was acquired.',
'VP06':'Dated setup preview repeats wireless keyboard but still omits exact paper/animation relation.',
'VP12':'Biography says a minor role or shows table header only, without the exact Constant Gardener role.',
'VP14':'Wrong player, global per-year maximum totals or table beginning omit Ding qualifying dated count.'}
def main():
 cs=rd(P/'r1/RESULTS.json');labels={r['case_id']:r for r in rd(P/'bank/LABELS.json')};prefix={r['case_id']:r for r in rd(P/'bank/RUNTIME_INPUTS.json')};lex=rd(P/'bank/QUERY_LEXICONS.json')
 windows=[];actions=[];cells=[];calls=[]
 for key,c in sorted(cs.items()):
  lab=labels[c['case_id']];f=lab['family'];ds={d['doc_ref']:d['docid'] for d in c['registry']['documents']};old_docs={d['docid'] for d in prefix[c['case_id']]['registry']['documents']};priorq=[];seen_docids=set(old_docs);flags=[]
  for d in c['decisions']:
   calls.append({'cell':key,'bank':lab['bank'],'arm':c['arm'],'step':d['step'],**d['actor']})
   if not d['tool']:continue
   t=d['tool'];a=t['action'];ws=t['observations'];s=d['step'];tool=a['tool'];query=a.get('query')
   aw=[]
   for i,w in enumerate(ws):
    good=(s,i) in POS.get(key,[]);sid=ds[w['doc_ref']];source=sid in SOURCES[f]
    assert not good or source,(key,s,i,sid)
    r={'cell':key,'case_id':c['case_id'],'arm':c['arm'],'bank':lab['bank'],'family':f,'step':s,'wave':i,'tool':tool,'doc_ref':w['doc_ref'],'docid':sid,'window_ref':w['window_ref'],'url':w['url'],'offset':w['offset'],'text_sha256':w['text_sha256'],'correct_source':source,'exact_evidence':good,'reason':REASONS[f] if good else NEG_REASON.get(f,'This window does not bind the required entity, relation and time scope; topical source identity alone is insufficient.')}
    windows.append(r);aw.append(r)
   exact=any(w['exact_evidence'] for w in aw);source=any(w['correct_source'] for w in aw)
   used=a.get('doc_ref') or next((w['doc_ref'] for w in c['registry']['windows'] if w['window_ref']==a.get('window_ref')),None)
   inspected_id=ds.get(used)
   fl=[]
   if not exact:
    if tool=='search':
     if lab['bank'] in ['K','challenge']:fl.append('S1')
     fl.append('S5' if source else 'S4')
    elif inspected_id in SOURCES[f]:fl.extend(['S5','S6' if tool=='find' else 'S7'])
    else:fl.append('S2')
   r={'cell':key,'bank':lab['bank'],'arm':c['arm'],'step':s,'tool':tool,'scope':{'search':'global','find':'local','open':'adjacent'}[tool],'action':a,'query':query,'repeated_query':bool(query is not None and (tool,used,query) in priorq),'entity_terms_present':bool(query and re.search(lex[f]['entity'],query,re.I)),'relation_terms_present':bool(query and re.search(lex[f]['relation'],query,re.I)),'correct_source_hit':source,'exact_evidence':exact,'window_count':len(ws),'existing_exact_source_directly_used':bool(tool!='search' and inspected_id in SOURCES[f] and inspected_id in old_docs),'same_document_rediscovery_count':sum(w['docid'] in seen_docids for w in aw) if tool=='search' else 0,'returned_exact_source_windows':sum(w['correct_source'] for w in aw),'source_hit_window_misses':sum(w['correct_source'] and not w['exact_evidence'] for w in aw),'inspected_docid':inspected_id,'failure_labels':fl,'tool_error':t['error'],'elapsed_seconds':t['elapsed_seconds'],'started_utc':d['tool_started_utc'],'completed_utc':d['tool_completed_utc']}
   actions.append(r);priorq.append((tool,used,query));seen_docids.update(w['docid'] for w in aw)
  ac=[a for a in actions if a['cell']==key];first=next((a['step'] for a in ac if a['exact_evidence']),None)
  lock=bool(len(ac)==2 and all(a['tool'] in ['find','open'] and not a['exact_evidence'] and a['inspected_docid'] not in SOURCES[f] for a in ac) and ac[0]['inspected_docid']==ac[1]['inspected_docid'])
  if lock:flags.append('S3')
  if first is None:
   flags.extend(x for a in ac for x in a['failure_labels'])
   if c['status']=='actor_stop':flags.append('S8')
  if c['status'].endswith('failure'):flags.append('API/schema' if c['status']=='actor_failure' else 'runtime/tool')
  cells.append({'cell':key,'case_id':c['case_id'],'qid':c['qid'],'bank':lab['bank'],'arm':c['arm'],'family':f,'structure':lab['structure'],'status':c['status'],'exact_evidence':first is not None,'first_evidence_action':first,'failure_free_success':first is not None and not c['status'].endswith('failure'),'actions':len(ac),'action1_success':first==1,'action2_recovery':first==2,'first_known_source_direct_use':bool(ac and ac[0]['existing_exact_source_directly_used']),'local_lock':lock,'failure_labels':sorted(set(flags)),'reason':REASONS[f] if first is not None else NEG_REASON.get(f,'No valid tool observation; retained schema/provider failure.'),'runtime_error':c.get('runtime_error')})
 def group(rows):
  keys={r['cell'] for r in rows};aa=[a for a in actions if a['cell'] in keys];ww=[w for w in windows if w['cell'] in keys];rr=[r for r in calls if r['cell'] in keys];uu=[r['usage'] for r in rr if r.get('usage')];s=[a for a in aa if a['tool']=='search'];sh=[a for a in s if a['correct_source_hit']]
  cost={k:sum(u.get(k) or 0 for u in uu) for k in ['input','output','reasoning','hit','miss']}
  cost.update(api_calls=sum(r['attempted'] for r in rr),writer_calls=0,usage_records=len(uu),api_failures=sum(r['error'] is not None for r in rr),runtime_failures=sum(r['status']=='runtime_failure' for r in rows),cache_hit_rate=ratio(cost['hit'],cost['input']),cache_occurrence=ratio(sum(bool(u.get('hit')) for u in uu),len(uu)),model_elapsed_seconds_sum=sum(r['elapsed_seconds'] for r in rr),tool_elapsed_seconds_sum=sum(a['elapsed_seconds'] for a in aa))
  cost['actor_failures']=cost['api_failures']
  cost['api_failures']=sum(bool(r['error'] and r['error']['category']=='provider/API failure') for r in rr)
  cost['schema_or_control_failures']=cost['actor_failures']-cost['api_failures']
  return {'n':len(rows),'qids':len({r['qid'] for r in rows}),'exact_evidence':ratio(sum(r['exact_evidence'] for r in rows),len(rows)),'failure_free_success':ratio(sum(r['failure_free_success'] for r in rows),len(rows)),'action1_success':ratio(sum(r['action1_success'] for r in rows),len(rows)),'action2_recovery':ratio(sum(r['action2_recovery'] for r in rows),sum(not r['action1_success'] for r in rows)),'first_known_source_direct_use':ratio(sum(r['first_known_source_direct_use'] for r in rows),len(rows)),'mean_actions':mean([r['actions'] for r in rows]),'mean_actions_to_evidence_successes':mean([r['first_evidence_action'] for r in rows if r['exact_evidence']]),'restricted_actions_to_evidence_failure_as_3':mean([r['first_evidence_action'] or 3 for r in rows]),'tools':dict(collections.Counter(a['tool'] for a in aa)),'local_lock':ratio(sum(r['local_lock'] for r in rows),len(rows)),'search_source_hit_window_miss_actions':ratio(sum(not a['exact_evidence'] for a in sh),len(sh)),'search_exact_source_window_miss':ratio(sum(w['tool']=='search' and w['correct_source'] and not w['exact_evidence'] for w in ww),sum(w['tool']=='search' and w['correct_source'] for w in ww)),'cost':cost}
 groups={bank:{arm:group([r for r in cells if r['bank']==bank and r['arm']==arm]) for arm in ['A0','A1','A2','A3'] if any(r['bank']==bank and r['arm']==arm for r in cells)} for bank in ['K','N','challenge']}
 # Paired common-case sensitivity excludes infrastructure/schema failures for either arm.
 paired={}
 for bank in ['K','N','challenge']:
  for other in ['A0','A2']:
   ids=[r['case_id'] for r in labels.values() if r['bank']==bank];pairs=[]
   for cid in ids:
    a=next(r for r in cells if r['cell']==cid+':A1');b=next(r for r in cells if r['cell']==cid+':'+other)
    if a['status'].endswith('failure') or b['status'].endswith('failure'):continue
    pairs.append((a,b))
   paired[bank+'_A1_vs_'+other]={'n':len(pairs),'A1':sum(a['exact_evidence'] for a,b in pairs),'comparator':sum(b['exact_evidence'] for a,b in pairs),'A1_only':sum(a['exact_evidence'] and not b['exact_evidence'] for a,b in pairs),'comparator_only':sum(b['exact_evidence'] and not a['exact_evidence'] for a,b in pairs)}
 wr('WINDOW_REVIEW.json',windows);wr('ACTION_REVIEW.json',actions);wr('CELL_REVIEW.json',cells);wr('CALL_AUDIT.json',calls)
 wr('METRICS.json',{'groups':groups,'all':group(cells),'paired_failure_free':paired,'by_structure':{st:{arm:group([r for r in cells if r['bank']=='K' and r['structure']==st and r['arm']==arm]) for arm in ['A0','A1','A2','A3']} for st in sorted({r['structure'] for r in cells if r['bank']=='K'})},'wall_time':rd(P/'r1/COMPLETED.json')})
 k=groups['K'];n=groups['N'];g={'K_A1_8_of_10':k['A1']['exact_evidence']['n']>=8,'K_A1_minus_A0_2':k['A1']['exact_evidence']['n']-k['A0']['exact_evidence']['n']>=2,'N_no_more_than_10pp_loss':n['A1']['exact_evidence']['n']>=n['A0']['exact_evidence']['n'],'N_local_lock_0_of_8':n['A1']['local_lock']['n']==0}
 verdict={'evaluated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'gates':g,'scope_gate_pass':all(g.values()),'K_sampling_target_met':False,'A3_exact':k['A3']['exact_evidence'],'A3_failure_free':k['A3']['failure_free_success'],'R2_run':k['A3']['exact_evidence']['n']<=7,'formal_history_rewritten':False,'runtime_incident':'Nine trajectories terminated after their first successful tool execution because three historical attempts contexts are dictionaries. All nine already returned exact evidence; none lost a primary success. Failure-free paired sensitivities remain required. Two additional schema failures retained; no retries.'}
 wr('GATES.json',verdict)
 print(json.dumps({'groups':{b:{a:r['exact_evidence'] for a,r in v.items()} for b,v in groups.items()},'gates':verdict,'paired':paired,'cost':group(cells)['cost']},indent=2))
if __name__=='__main__':main()
