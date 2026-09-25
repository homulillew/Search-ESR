"""T0: source-audited, pre-answer transition bank; no model or Search calls."""
import hashlib,json,sqlite3,subprocess
from pathlib import Path

BASE=Path(__file__).resolve().parent
TOP=BASE.parent
ROOT=TOP.parents[1]
SC0=ROOT/'experiments/state_conditioned_retrieval/state_bank'
DB=ROOT/'BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite'
SELECTED=['U1_B01','U1_B03','U1_B04','U1_B05','U1_B06','U1_B07',
          'U1_C01','U1_C03','U1_C05','U1_C06','U1_C07','U1_C11']

BRIDGE_GAP={
 '517':'Which Kenyan actor with a soldier father appeared in The Constant Gardener and The Fifth Estate?',
 '435':'Which musician matches the age-66 Zimbabwean musician and album-career clues?',
 '1094':'Which two teams played in the 4–3 match decided by a 95th-minute free kick?',
 '311':'Which 1967 Argentine animated series was created by Manuel García Ferré?',
 '186':'Which November 1992 DOS shareware game fits the question clues?',
 '1034':'Which performer appeared on G-mik and later worked as a singer and model?',
 '177':'Which NPFL club based in Enugu signed 13 players ahead of the 2022/23 season?',
 '580':'Which television series has the season-four episode Not a Great Bet featuring Gretchen and Jimmy?',
 '546':'Which snooker player beat Ma Hailong 4–3 in his 2023 English Open opener?',
}
NEXT_GAP={
 'U1_B01':'What exact filmography role did the identified Kenyan actor play in The Constant Gardener?',
 'U1_B03':'Which song by the identified musician was interpreted as urging Robert Mugabe to retire?',
 'U1_B04':'Which player scored the second goal for the identified winning team in that match?',
 'U1_B05':'Which object gives the identified Argentine cartoon character magical powers?',
 'U1_B06':'What was the planned name of the second episode of the identified DOS game?',
 'U1_B07':'What role did the identified performer play on the programme mentioned near the end of the article?',
 'U1_C01':'How many albums did the May 2017 Forbes Africa feature attribute to the identified musician?',
 'U1_C02':'Was the identified musician included in Forbes Africa’s 2017 richest-musicians list?',
 'U1_C03':'How many albums did a 2017 richest-African-musicians report attribute to the identified musician?',
 'U1_C05':'Did the identified NPFL club win the 2016 Nigeria Professional Football League?',
 'U1_C06':'Which season-one episode of the identified series involved Gretchen’s friends convincing Jimmy to take her on a date?',
 'U1_C07':'Which season-three finale of the identified series involved Edgar’s sacrifice?',
 'U1_C11':'When did the identified snooker player turn professional, and how many maximum breaks did he make?',
}
FORBIDDEN={
 'U1_B01':['Policeman 1'], 'U1_B03':['Wasakara'], 'U1_B04':['Neymar'],
 'U1_B05':['sombreritus'], 'U1_B06':['Last Stand on Mars'],
 'U1_B07':['Missy Sandejas'], 'U1_C01':['65 albums'],
 'U1_C02':['Oliver Mtukudzi is included in Forbes'], 'U1_C03':['65 albums'],
 'U1_C05':['winners: Enugu Rangers','won the 2016'],
 'U1_C06':['Insouciance'], 'U1_C07':['No Longer Just Us'],
 'U1_C11':['In 2003, Ding turned professional','seven maximum breaks'],
}
DIRECT_EXTRA={
 'U1_B03':['70761','79895'],
 'U1_B04':['70117','82883'],
 'U1_B05':['53641'],
 'U1_B06':['51927'],
 'U1_C02':['56154'],
 'U1_C05':['86072'],
}
BRIDGE_EXTRA={
 'U1_B01':['43080'],
 'U1_B06':['2855','22411','20115'],
}
CANDIDATE_ALIAS={
 '517':'Peter King','435':'Oliver Mtukudzi','1094':'Paris Saint-Germain','311':'Hijitus','186':'Galacta',
 '1034':'Heart Evangelista','177':'Rangers','580':"You're the Worst",'546':'Ding Junhui',
}
BOUND_VARIABLE={
 '517':'candidate_actor','435':'candidate_musician','1094':'match_teams','311':'candidate_cartoon','186':'candidate_game',
 '1034':'candidate_performer','177':'candidate_club','580':'candidate_series','546':'candidate_player',
}

def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')

def main():
    assert len(SELECTED)==len(set(SELECTED))==12
    prior={x['case_id']:x for x in json.loads((SC0/'BANK.json').read_text())}
    truth={x['case_id']:x for x in json.loads((SC0/'PRIVATE_TRUTH.json').read_text())}
    prev_results=json.loads((ROOT/'experiments/state_conditioned_retrieval/state_sufficiency/retrieval_results.json').read_text())
    previous={}
    for r in prev_results:
        if r['arm'] in ('S0','S3'):
            previous.setdefault(r['case_id'],set()).update(h['docid'] for h in r['hits'])
    db=sqlite3.connect(f'{DB.as_uri()}?mode=ro',uri=True)
    public,private,source_reviews=[],[],[]
    try:
        for cid in SELECTED:
            sc=prior[cid]; old=truth[cid]; qid=sc['qid']; claim=old['prior_facts'][0]['statement']
            question=sc['raw_question']; gap=NEXT_GAP[cid]; obs=old['prior_window_text']
            assert CANDIDATE_ALIAS[qid].lower() not in question.lower(),cid
            assert CANDIDATE_ALIAS[qid].lower() not in gap.lower(),cid
            for term in FORBIDDEN[cid]:
                assert term.lower() not in obs.lower(),(cid,term)
                assert term.lower() not in gap.lower(),(cid,term)
                assert term.lower() not in claim.lower(),(cid,term)
            assert old['prior_facts'][0]['source_supported']
            direct=sorted(set(old['sufficient_doc_ids'])|set(DIRECT_EXTRA.get(cid,[])))
            bridge=sorted(set([old['prior_source_docid']]+BRIDGE_EXTRA.get(cid,[])))
            # Some bridge windows come from a document whose later section is direct;
            # preserve the overlap explicitly for T4 and exclude it for T5 routing.
            non_direct_bridge=sorted(set(bridge)-set(direct))
            reviewed=[]
            for docid in direct+sorted(set(bridge)-set(direct)):
                row=db.execute('SELECT text,url FROM documents WHERE docid=?',(docid,)).fetchone()
                assert row,(cid,docid)
                text,url=row
                role='direct' if docid in direct else 'bridge_only'
                reviewed.append({'docid':docid,'url':url,'text_sha256':digest(text),'role':role,
                                 'audit_reason':('answers the frozen next Gap' if role=='direct' else
                                  'identifies the unresolved referent without the next-Gap answer')})
            source_reviews.append({'case_id':cid,'reviewed_sources':reviewed,
                'prior_top50_candidate_pool_size':len(previous.get(cid,set())),
                'canonical_source_ids':old['sufficient_doc_ids'],
                'added_direct_source_ids':DIRECT_EXTRA.get(cid,[]),
                'bridge_doc_overlap_with_direct':sorted(set(bridge)&set(direct))})
            public.append({'case_id':cid,'qid':qid,'question':question,
                'state_pre':{'claims':[]},'bridge_gap':BRIDGE_GAP[qid],
                'bridge_observation':{'text':obs,'url':old['prior_source_url'],
                    'window_ref':old['prior_evidence_ref']},
                'bridge_claim':{'statement':claim,'type':'referent_binding',
                    'bound_variable':BOUND_VARIABLE[qid]},
                'state_post':{'claims':[claim]},'next_gap':gap})
            private.append({'case_id':cid,'qid':qid,'question_sha256':digest(question),
                'bridge_gap_sha256':digest(BRIDGE_GAP[qid]),'next_gap_sha256':digest(gap),
                'observation_text_sha256':digest(obs),'observation_url_sha256':digest(old['prior_source_url']),
                'historical_observation_case':old['source_observation_case'],
                'historical_prior_event':old['prior_event'],
                'target_first_seen_event':old['target_evidence_first_seen_event'],
                'target_first_seen_right_censored':old['target_first_seen_right_censored_after_prior'],
                'bridge_claim_support_quote':old['prior_facts'][0]['support_quote'],
                'bridge_claim_support_location':old['prior_facts'][0]['support_location'],
                'what_variable_is_bound':BOUND_VARIABLE[qid],
                'why_decision_changes':f'The previously unnamed {BOUND_VARIABLE[qid]} is now bound to {CANDIDATE_ALIAS[qid]}, allowing a relation-specific next query.',
                'canonical_direct_doc_ids':old['sufficient_doc_ids'],
                'direct_sufficient_doc_ids':direct,
                'alternative_sufficient_doc_ids':sorted(set(direct)-set(old['sufficient_doc_ids'])),
                'bridge_source_doc_ids':bridge,
                'bridge_only_doc_ids':non_direct_bridge,
                'forbidden_leak_strings':FORBIDDEN[cid],
                'review_decision':'admit: genuine pre-answer observation binds an unnamed referent; next Gap preserves reference'})
    finally:db.close()
    assert len(public)==len(private)==12 and len({x['qid'] for x in public})==9
    write(BASE/'BANK.json',public);write(BASE/'PRIVATE_TRUTH.json',private)
    write(BASE/'SOURCE_REVIEWS.json',source_reviews)
    write(BASE/'freeze.json',{'base_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
       'case_order':SELECTED,'qid_count':9,'sample_count':12,
       'input_sha256':{str(x.relative_to(ROOT)):sha(x) for x in [SC0/'BANK.json',SC0/'PRIVATE_TRUTH.json',
          ROOT/'experiments/state_conditioned_retrieval/state_sufficiency/retrieval_results.json',DB]},
       'bank_sha256':sha(BASE/'BANK.json'),'truth_sha256':sha(BASE/'PRIVATE_TRUTH.json'),
       'source_reviews_sha256':sha(BASE/'SOURCE_REVIEWS.json'),
       'question_hashes':{x['case_id']:x['question_sha256'] for x in private},
       'observation_hashes':{x['case_id']:x['observation_text_sha256'] for x in private},
       'next_gap_hashes':{x['case_id']:x['next_gap_sha256'] for x in private},
       'failure_policy':'No new calls in T0; any discovered later alternative is reported separately, never added to frozen primary truth'})
    print('T0',len(public),'transitions',len({x['qid'] for x in public}),'qids')

if __name__=='__main__':main()
