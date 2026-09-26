"""Reviewer-normalized states from real historical source windows and action prefixes.

No model call, gold answer, or newly invented research Gap is used here.
"""
import hashlib,json,re,sqlite3,subprocess
from pathlib import Path

BASE=Path(__file__).resolve().parent
TOP=BASE.parent
ROOT=TOP.parents[1]
def read(p):return json.loads((ROOT/p).read_text())
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def write(name,x):(BASE/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
VPATH='experiments/minimal_research_loop/verify_necessity/OBSERVATIONS.json'
FPATH='experiments/gap_evidence_claim_loop/single_gap_rollout/REVIEW_PACKETS.json'
TPATH='experiments/state_transition_feedback/online_state_update/corrected/REQUESTS.json'
OPATH='experiments/state_transition_feedback/online_state_update/corrected/OUTPUTS.json'
QPATH='experiments/state_transition_feedback/oracle_state_effect/REQUESTS.json'
QOUT='experiments/state_transition_feedback/oracle_state_effect/QUERIES.json'
v={x['case_id']:x for x in read(VPATH)}
f={x['review_id']:x for x in read(FPATH)}
t={x['case_id']:json.loads(x['request']['messages'][1]['content']) for x in read(TPATH)}
o={x['case_id']:x for x in read(OPATH)}
oldq={(x['case_id'],x['arm']):x for x in read(QPATH)}
oldqueries={(x['case_id'],x['arm']):x for x in read(QOUT)}
db=sqlite3.connect(f"{(ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite').as_uri()}?mode=ro",uri=True)
sources={};source_cache={};snapshots=[];transitions=[];truth={};audits=[]

def source(obs,path,pointer,first_seen):
    text=obs.get('text',obs.get('preview',''));url=obs.get('url','')
    assert text and url,(path,pointer)
    key=(url,sha(text),path,pointer)
    if key in source_cache:return source_cache[key]
    rows=db.execute('select docid,text from documents where url=?',(url,)).fetchall()
    exact=[(did,body,body.find(text)) for did,body in rows if text in body]
    assert len(exact)==1,(url,len(exact),text[:40])
    did,body,offset=exact[0];sid=f'E{len(sources)+1:03}'
    sources[sid]={'source_id':sid,'docid':str(did),'url':url,'title':obs.get('title',''),
      'text':text,'text_sha256':sha(text),'document_sha256':sha(body),'offset':offset,
      'history_path':path,'history_pointer':pointer,'first_seen_time':first_seen,
      'time_kind':'historical checkpoint/action ordinal; wall clock retained only when available'}
    source_cache[key]=sid;return sid

def vsource(key):
    x=v[key];return source(x['observation'],VPATH,key,
       x['historical_origin'].get('checkpoint',x['historical_origin']))

def fsource(rid,idx,ref):
    packet=f[rid];a=packet['actions'][idx];rr=a['result']
    z=next(z for z in rr.get('results',rr.get('matches',[])) if z.get('preview_ref',z.get('window_ref'))==ref)
    identity=z
    if not z.get('url'):
        did=z.get('doc_ref',rr.get('doc_ref'))
        identity=next(z2 for aa in packet['actions'][:idx+1] for z2 in aa['result'].get('results',[]) if z2.get('doc_ref')==did and z2.get('url'))
    obs={'text':z.get('text') or z.get('preview'),'url':identity['url'],'title':identity.get('title','')}
    return source(obs,FPATH,f'{rid}/actions/{idx}/{ref}',{'review_id':rid,'action_index':idx,'window_ref':ref})

def claim(statement,refs):
    return {'statement':statement,'support_refs':refs,
      'source_text_hashes':[sources[r]['text_sha256'] for r in refs],
      'first_seen_time':[sources[r]['first_seen_time'] for r in refs]}

def workspace(refs):
    docs={};windows=[]
    for ref in dict.fromkeys(refs):
        s=sources[ref];did=s['docid']
        if did not in docs:docs[did]={'doc_ref':f'D{len(docs)+1}','docid':did,'title':s['title'],'url':s['url']}
        windows.append({'window_ref':f'W{len(windows)+1}','doc_ref':docs[did]['doc_ref'],
          'source_id':ref,'title':s['title'],'url':s['url'],'text':s['text']})
    return {'known_documents':list(docs.values()),'observed_windows':windows}

GOALS={
 '546':'Identify the player who jointly satisfies the dated professional-start and break-count constraints and the full ordered 2023 win/win/win/loss sequence, including the opponents’ count constraints.',
 '1094':'Identify the free-kick taker in the fixture that jointly matches the club-history and goal-timing clues; a PSG–Lille free kick alone does not establish that fixture as the target.',
 '517':'Establish the actor’s popular name with the parental-work and film-credit clues, including the policeman role and director links; reconcile the supplied birth year with the Goat clue rather than assume the match.',
 '435':'Establish the described musician from discriminative biographical clues and the exact album count attributed to the May Forbes Africa feature; do not join a lifetime count to a separate interview.',
 '580':'Identify a series that matches the season-one date scene, season-three roommate sacrifice, season-four family-baby visit, and fewer-than-ten-season constraint.',
 '177':'Identify the club matching the historical tied-points table and signing/trophy/city clues, then establish its founding year and country.',
 '1034':'Identify the person matching the original modelling, music, university, child-birthplace and coordinator-to-manager career clues and establish that person’s birth name.',
 '387':'Identify the Game B animator through the original game/company and paper-animation clues, then establish that person’s gaming-PC storage as of the specified date.',
 '311':'Identify the programme satisfying the original country, network, year, episode, staffing and character clues and establish its Argentinian release title.',
 '186':'Identify the game satisfying the November early-1990s DOS/shareware/single-player/credits clues and verify its developer’s amphibian name and former name.',
}

def add(qid,q,gap,pre,post,obs,pre_refs,post_refs,pre_hyp=None,post_hyp=None,
        categories=None,kind='partial_progress',resolved_pre=False,resolved_post=False,
        residual_pre=None,residual_post=None,hyp_origin=None,history=None):
    tid=f'T{len(transitions)+1:02}';pair=[]
    for phase,claims,refs,hyp,resolved,residual in [
      ('PRE',pre,pre_refs,pre_hyp,resolved_pre,residual_pre),
      ('POST',post,post_refs,post_hyp,resolved_post,residual_post)]:
        cid=f'{tid}_{phase}';pair.append(cid)
        cats=list(categories or [])
        if resolved:
            cats=[c for c in cats if c not in ('candidate_unresolved','candidate_verified_final_relation_unresolved')]
            cats+=['fully_resolved','stale_gap']
        elif hyp:cats+=['hypothesis_only']
        else:cats+=['candidate_unresolved']
        snapshots.append({'case_id':cid,'transition_id':tid,'phase':phase,'qid':qid,'question':q,
          'verified_claims':claims,'working_hypothesis':hyp,'hypothesis_provenance':
              (hyp_origin.get(phase,hyp_origin) if isinstance(hyp_origin,dict) else hyp_origin) if hyp else None,
          'historical_active_gap':gap,'recent_attempt_context':history or {},
          'available_workspace':workspace(refs),'categories':sorted(set(cats)),
          'state_origin':'reviewer-normalized historical replay; source facts and gaps retain exact historical provenance'})
        truth[cid]={'goal_status':'resolved' if resolved else 'open',
          'residual_must_include':[] if resolved else [residual or GOALS[qid]],
          'residual_must_not_include':['Invent a new objective about the named entity unrelated to the original question.']+
             ([gap] if resolved else []),
          'already_supported_facts':[x['statement'] for x in claims],
          'unsupported_join_traps':(['Lifetime album count plus existence of Forbes interview does not entail the May feature count.'] if qid=='435' else []),
          'reason':'All material original-goal requirements supported jointly.' if resolved else 'One or more original-goal requirements remain unsupported; hypotheses do not close them.'}
    transitions.append({'transition_id':tid,'qid':qid,'question':q,'pre_snapshot':pair[0],
      'post_snapshot':pair[1],'observation_source_refs':obs,'category':kind,
      'historical_active_gap':gap,'history':history or {}})

# Ten source-supported starting transitions from the previous actual T3 requests.
# Unsupported task-level binding is normalized to a hypothesis, never a verified Claim.
BASIC=[
 ('546','U1_C11','E1_F1_T1_546',[
   'Ding Junhui won his opening match at the 2023 English Open 4–3 against Ma Hailong.'],
   'Ding Junhui may be the player described in the question.'),
 ('1094','U1_B04','E1_F1_T1_1094',[
   'Lionel Messi took a 95th-minute free kick in Paris Saint-Germain’s home match against Lille, which PSG won 4–3.'],
   'The PSG–Lille match may be the fixture described in the question.'),
 ('517','U1_B01','E1_F1_T5_517',[
   'Peter King Nzioki Mwania is popularly known as Peter King; the source gives his birth date as 25 May 1978.',
   'Peter King’s father served in the Kenyan Army and his mother worked at the military hospital.',
   'Peter King appeared in The Constant Gardener and The Fifth Estate; the observed biography does not give his exact Constant Gardener role.'],
   'Peter King may be the actor described in the question.'),
 ('435','U1_B03','E1_F1_T1_435',[
   'Oliver Mtukudzi died in January 2019 at age 66.',
   'Oliver Mtukudzi had more than 60 albums over a career spanning 45 years.'],
   'Oliver Mtukudzi may be the musician described in the question.'),
 ('580','U1_C06','E1_F1_T1_580',[
   'In You’re the Worst, Not a Great Bet is season 4 episode 7; Gretchen returns home for her brother’s baby and reconnects with Heidi.'],
   'You’re the Worst may be the series described in the question.'),
 ('177','U1_C05','E1_F1_T1_177',[
   'Rangers is based in Enugu and signed 13 new players ahead of the 2022/23 Nigeria Professional Football League season.'],
   'Rangers may be the club described in the question.'),
 ('1034','U1_B07','E1_F1_T1_1034',[
   'The March 2021 source says Heart Evangelista began her rise to stardom 23 years earlier and appeared on G-mik at age 13.',
   'Heart Evangelista grew up in a wealthy family; this fact alone does not establish what fraction of her own wealth came from showbiz.'],None),
 ('311','U1_B05','E1_F1_T5_311',[
   'The Adventures of Hijitus credits three writers: Manuel García Ferré, Inés Geldstein, and Néstor D’Alessandro.',
   'The Adventures of Hijitus aired on Canal 13 from 7 August 1967 to 1 March 1996; these facts conflict with the original two-writer and early-1990s January-to-December clues.'],None),
 ('186','U1_B06','E1_F1_T5_186',[
   'Galacta: The Battle for Saturn was released in November 1992 on DOS as shareware with one offline player.',
   'Galacta credits Sean Michael Puckett, Rocco Caputo, and Terri L. Puckett; Albino Frog Software is listed as publisher.'],
   'Galacta: The Battle for Saturn may be the game described in the question.'),
]
basic_refs={};basic_claims={}
for qid,oldid,vkey,statements,hyp in BASIC:
    obs=t[oldid]['Current Observation']
    sid=source({'text':obs['text'],'url':obs['url'],'title':v[vkey]['observation']['title']},TPATH,oldid+'/Current Observation',
      {'historical_stage':'T3','case_id':oldid})
    claims=[claim(s,[sid]) for s in statements];basic_refs[qid]=sid;basic_claims[qid]=claims
    pre_hyp=None;gap=t[oldid]['Current Gap'];pre_context={'source_path':TPATH,'case_id':oldid}
    if qid in ('311','1034'):
        # Actual earlier persisted candidate input; downgrade unsupported old
        # oracle binding to WH, retaining the genuine historical local Gap.
        req=oldq[oldid,'POST'];view=json.loads(req['request']['messages'][1]['content'])
        pre_hyp=view['Current Research State']['claims'][0]
        gap=view['Current Gap']
        pre_context={'source_path':QPATH,'case_id':oldid,'arm':'POST',
          'historical_reasoning_path':QOUT,'historical_reasoning_arm':'RAW',
          'historical_model_query':oldqueries[oldid,'RAW']['output']['search_query'],
          'normalization':'historical unsupported persisted binding moved to hypothesis; not treated as evidence',
          'transition_observation_origin':TPATH}
    add(qid,t[oldid]['Question'],gap,[],claims,[sid],[],[sid],pre_hyp,hyp,
        ['candidate_unresolved'], 'hypothesis_rejection' if qid in ('311','1034') else 'hypothesis_strengthening',
        hyp_origin={'PRE':{'path':QOUT,'case_id':oldid,'arm':'RAW','normalization':'candidate from actual earlier model query'},
                    'POST':{'path':OPATH,'case_id':oldid,'normalization':'task identification remains provisional'}},history=pre_context)

# T10: a genuine hardware interview window; storage alone cannot identify the
# Game B animator, so the original goal remains open.
x=v['E1_F1_T1_387'];sid=vsource(x['case_id'])
claims=[claim('Dean Dodrill says his gaming/workstation PC has 5 TB of storage and a wireless keyboard.',[sid]),
        claim('Dean Dodrill describes himself as the creator of Dust: An Elysian Tail.',[sid])]
basic_refs['387']=sid;basic_claims['387']=claims
add('387',x['raw_question'],x['active_gap'],[],claims,[sid],[],[sid],None,
  'Dean Dodrill may be the animator described in the question.',['candidate_unresolved'],'hypothesis_strengthening',
  hyp_origin={'path':'experiments/minimal_research_loop/verify_necessity/reader_outcomes.json','case_id':x['case_id']},
  history={'source_path':VPATH,'case_id':x['case_id']})

def facts435(rid):
    # Both recorded search batches contain these same observed pages.
    mapping={'P05':{'bio':'W3','obit':'W4','feature':'W10','retrospective':'W7'},
             'P10':{'bio':'W3','obit':'W5','feature':'W9','retrospective':'W7'}}[rid]
    rr={k:fsource(rid,0,ref) for k,ref in mapping.items()}
    cs=[claim('Oliver Mtukudzi was a human-rights activist, began performing in 1977, and his first album followed his band’s early successful single.',[rr['bio']]),
        claim('Oliver Mtukudzi died at 66 after a career of 67 albums; his 2001 Wasakara was interpreted as referring to Robert Mugabe being old.',[rr['obit']]),
        claim('The Forbes Africa feature dated 1 May 2017, Top 10 most bankable artists in Africa, states that Oliver Mtukudzi had 65 albums.',[rr['feature']]),
        claim('A retrospective separately mentions 67 albums and quotes a 2016 Forbes Africa interview; it does not attribute 67 albums to the May 2017 feature.',[rr['retrospective']])]
    return rr,cs

states435={}
for rid in ['P05','P10']:
    rr,cs=facts435(rid);pre=basic_claims['435'];post=pre+cs;refs=[basic_refs['435']]+list(rr.values())
    states435[rid]=(post,refs)
    add('435',f[rid]['raw_question'],f[rid]['active_gap'],pre,post,list(rr.values()),[basic_refs['435']],refs,
      'Oliver Mtukudzi is the musician currently investigated in the historical query.',None,
      ['unsupported_join'], 'direct_resolution',resolved_post=True,
      residual_pre='Confirm the musician using discriminative clues and obtain the exact May Forbes feature album count; a lifetime count alone is insufficient.',
      hyp_origin={'path':FPATH,'pointer':rid+'/actions/0/arguments/query'},
      history={'source_path':FPATH,'review_id':rid,'action_index':0,'recorded_action':f[rid]['actions'][0]['arguments']})

# q580: the archived first Search returned S1/S3 and the five-season series page
# together; the prior W1 supplies S4. No new downstream question is invented.
rr580={k:fsource('P12',0,ref) for k,ref in {'s1':'W2','series':'W3','s3':'W4','edgar':'W5'}.items()}
facts580=[
 claim('Insouciance is You’re the Worst season 1 episode 2: Gretchen is angry at Jimmy’s assumption, and her friends convince him to take her on a date.',[rr580['s1']]),
 claim('No Longer Just Us is You’re the Worst season 3 episode 13 and includes Edgar’s sacrifice.',[rr580['s3']]),
 claim('You’re the Worst has five seasons and follows Jimmy and Gretchen with their friends Edgar and Lindsay.',[rr580['series']]),
 claim('Edgar Quintero is a main character in You’re the Worst and is Jimmy Shive-Overly’s roommate.',[rr580['edgar']])]
post580=basic_claims['580']+[facts580[1],facts580[3]]
refs580=[basic_refs['580']]+list(rr580.values())
add('580',f['P12']['raw_question'],f['P12']['active_gap'],basic_claims['580'],post580,list(rr580.values()),
 [basic_refs['580']],refs580,'You’re the Worst is the series investigated in the recorded query.',None,
 ['candidate_unresolved'],'partial_progress',resolved_post=False,
 residual_pre='Verify the season-one date scene, season-three sacrifice and total-season constraint for the candidate series.',
 residual_post='The season-three sacrifice and roommate link are verified; the season-one date scene and fewer-than-ten-seasons condition remain uncommitted.',
 hyp_origin={'path':FPATH,'pointer':'P12/actions/0/arguments/query'},
 history={'source_path':FPATH,'review_id':'P12','action_index':0,'recorded_action':f['P12']['actions'][0]['arguments']})
sid=fsource('P12',4,'W8')
pre580final=post580+[facts580[0]]
post580final=pre580final+[claim('You’re the Worst has five seasons.',[sid])]
add('580',f['P12']['raw_question'],f['P12']['active_gap'],pre580final,post580final,[sid],refs580,refs580+[sid],
 None,None,['candidate_verified_final_relation_unresolved'],'direct_resolution',False,True,
 residual_pre='The series matches the three plot clues; the remaining material requirement is that it has fewer than ten seasons.',
 history={'source_path':FPATH,'review_id':'P12','action_index':4,'recorded_action':f['P12']['actions'][4]['arguments']})

# q177 table and founding source at actual later checkpoints.
table=vsource('E1_F3_P07_W17')
table_claim=claim('The 2014 Nigeria Professional Football League table places Enugu Rangers eighth with 58 points and +8 goal difference.',[table])
pre177=basic_claims['177'];post177=pre177+[table_claim]
add('177',f['P07']['raw_question'],f['P07']['active_gap'],pre177,post177,[table],[basic_refs['177']],
 [basic_refs['177'],table],'Enugu Rangers is the club investigated in the historical query.','Enugu Rangers remains a candidate for the described club.',
 ['candidate_unresolved'],'partial_progress',residual_post='Verify the remaining club-identification constraints and establish the founding year and country; the table alone does not supply founding facts.',
 hyp_origin={'path':FPATH,'pointer':'P07/actions/1/arguments/query'},history={'source_path':FPATH,'review_id':'P07','action_index':1})
found=fsource('P07',2,'W20')
post177b=post177+[claim('Rangers International Football Club is based in Enugu, Nigeria, and was founded in 1970.',[found])]
add('177',f['P07']['raw_question'],f['P07']['active_gap'],post177,post177b,[found],[basic_refs['177'],table],
 [basic_refs['177'],table,found],'Enugu Rangers remains a candidate for the described club.','Enugu Rangers remains a candidate for the described club.',
 ['unsupported_join'],'partial_progress',residual_post='Confirm the fifteen-trophy and original season-specific identity conditions before applying Rangers’ 1970 Nigeria founding facts as the final answer.',
 hyp_origin={'path':FPATH,'pointer':'P07/actions/1/arguments/query'},history={'source_path':FPATH,'review_id':'P07','action_index':2})

# q517 exact film role resolves a local gap without licensing original closure.
role=vsource('E1_F3_P03_W21');pre517=basic_claims['517']
post517=pre517+[claim('Peter King Nzioki was credited as Policeman 1 in The Constant Gardener (2005).',[role])]
add('517',f['P03']['raw_question'],f['P03']['active_gap'],pre517,post517,[role],[basic_refs['517']],
 [basic_refs['517'],role],'Peter King is the actor investigated by the historical query.','Peter King remains a candidate pending the remaining original clues.',
 ['stale_gap'],'partial_progress',residual_post='The policeman role is verified; the remaining director-link and Goat/birth-year consistency conditions still need support.',
 hyp_origin={'path':FPATH,'pointer':'P03/actions/0/arguments/query'},history={'source_path':FPATH,'review_id':'P03','action_index':4})

# The next recorded find in P05 rereads identity material after a direct feature
# was already returned. This gives a genuine historical stale-focus stress case.
sid=fsource('P05',1,'W11');post,refs=states435['P05']
add('435',f['P05']['raw_question'],f['P05']['active_gap'],post,post,[sid],refs,refs+[sid],None,None,
 ['stale_gap','unsupported_join'],'resolved_preserving',True,True,
 history={'source_path':FPATH,'review_id':'P05','action_index':1,'recorded_action':f['P05']['actions'][1]['arguments']})

# A real single-window reader checkpoint intentionally retains only what that
# archived W supports. It cannot join the retrospective count to the interview.
joinref=vsource('E1_F3_P05_W7')
joinclaims=basic_claims['435']+[
 claim('A retrospective article says “67 albums later” when discussing Oliver Mtukudzi’s career.',[joinref]),
 claim('The same retrospective quotes an Oliver Mtukudzi interview with Forbes Africa in 2016.',[joinref])]
add('435',v['E1_F3_P05_W7']['raw_question'],v['E1_F3_P05_W7']['active_gap'],basic_claims['435'],joinclaims,
 [joinref],[basic_refs['435']],[basic_refs['435'],joinref],
 'Oliver Mtukudzi is the musician investigated in the historical query.','Oliver Mtukudzi remains the candidate being investigated.',
 ['unsupported_join'],'partial_progress',residual_post='The exact count in the May Forbes feature is still unknown: the separate retrospective 67-album statement and 2016 interview must not be joined.',
 hyp_origin={'path':FPATH,'pointer':'P05/actions/0/arguments/query'},
 history={'source_path':VPATH,'case_id':'E1_F3_P05_W7','projection':'archived single-window Reader checkpoint; sibling batch windows are not supplied'})
repeat=fsource('P12',5,'W4')
seasonref=next(r for r,s in sources.items() if s['history_pointer']=='P12/actions/4/W8')
add('580',f['P12']['raw_question'],f['P12']['active_gap'],post580final,post580final,[repeat],refs580+[seasonref],
 refs580+[seasonref,repeat],None,None,
 ['stale_gap'],'resolved_preserving',True,True,
 history={'source_path':FPATH,'review_id':'P12','action_index':5,'recorded_action':f['P12']['actions'][5]['arguments']})

assert len(transitions)==20 and len(snapshots)==40
assert len({s['qid'] for s in snapshots})==10
assert all(c['support_refs'] and all(r in sources for r in c['support_refs']) for s in snapshots for c in s['verified_claims'])
write('SNAPSHOTS.json',snapshots);write('TRANSITIONS.json',transitions)
write('SOURCE_WINDOWS.json',sources);write('PRIVATE_TRUTH.json',{'snapshots':truth,
 'interpretation':'Material identity is supported by multiple discriminative clues without a known contradiction; never by a name alone. q435 exact interview quote remains a conservative sensitivity issue.',
 'sensitivity_open_cases':[s['case_id'] for s in snapshots if s['qid']=='435' and truth[s['case_id']]['goal_status']=='resolved'],
 'known_source_sets':{qid:{'verified_fact_source_docids':sorted({sources[r]['docid'] for s in snapshots if s['qid']==qid for c in s['verified_claims'] for r in c['support_refs']}),
                         'exhaustiveness':'known observed sufficient sources for the explicitly recorded facts; no claim of exhaustive whole-goal answer coverage'} for qid in GOALS}})
write('freeze.json',{'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'snapshot_count':len(snapshots),'transition_count':len(transitions),'distinct_qids':10,
 'resolved_snapshots':sum(t['goal_status']=='resolved' for t in truth.values()),
 'files':{n:sha((BASE/n).read_text()) for n in ['SNAPSHOTS.json','TRANSITIONS.json','SOURCE_WINDOWS.json','PRIVATE_TRUTH.json']},
 'history_hashes':{p:sha((ROOT/p).read_text()) for p in [VPATH,FPATH,TPATH,OPATH,QPATH,QOUT]},
 'no_new_model_calls':True,'failure_policy':'no replacement or post-result relabeling; exact source support and original-goal audit before calls'})
db.close()
print('built',len(snapshots),'snapshots',len(transitions),'transitions',len(sources),'windows')
