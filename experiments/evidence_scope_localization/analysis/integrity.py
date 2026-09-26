"""Post-run integrity verification, no inference or retrieval."""
import collections,datetime,hashlib,json,sqlite3,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];sys.path.insert(0,str(ROOT))
from experiments.evidence_scope_localization import runtime
from experiments.goal_residual_control_v3.capability import digest,sha

def rd(p):return json.loads(Path(p).read_text())
def sh(t):return hashlib.sha256(t.encode()).hexdigest()
def dt(t):return datetime.datetime.fromisoformat(t).timestamp()
def concurrency(intervals):
    events=sorted((dt(t),v) for a,b in intervals for t,v in [(a,1),(b,-1)])
    active=peak=0;overlap=0;prev=events[0][0] if events else 0
    for t,v in events:
        if active>1:overlap+=t-prev
        active+=v;peak=max(peak,active);prev=t
    return {'peak_active':peak,'seconds_with_at_least_two':overlap}

def main():
    runtime.check('r1')
    hist=rd(P/'HISTORICAL_HASHES.json')
    for p,h in hist.items():assert sha(ROOT/p)==h,p
    inp={r['case_id']:r for r in rd(P/'bank/RUNTIME_INPUTS.json')}
    labs={r['case_id']:r for r in rd(P/'bank/LABELS.json')}
    for k,r in inp.items():assert digest(r)==labs[k]['prefix_sha256'] and sh(r['need'])==labs[k]['need_sha256'],k
    manifests={(r['case_id'],r['arm']):r for r in rd(P/'r1/MANIFEST.json')}
    initial={(r['case_id'],r['arm']):r['request'] for r in rd(P/'r1/INITIAL_REQUESTS.json')}
    cs=rd(P/'r1/RESULTS.json');assert len(cs)==len(manifests)==84
    db=sqlite3.connect(f'file:{ROOT}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro',uri=True)
    docs={};window_checks=observations=0;api=[];tool=[];raw_status=collections.Counter()
    immutable=['question','claims','hypothesis','need']
    for key,c in cs.items():
        cid=c['case_id'];arm=c['arm'];m=manifests[cid,arm];base=inp[cid];directory=P/'r1/cells'/f'{cid}__{arm}'
        assert c==rd(directory/'RESULT.json');assert len(c['decisions'])<=2
        for k in immutable:assert c[k]==base[k],(key,k)
        docmap={d['doc_ref']:d for d in c['registry']['documents']}
        for d in docmap.values():
            sid=d['docid']
            if sid not in docs:docs[sid]=db.execute('select text from documents where docid=?',(sid,)).fetchone()[0]
            assert sh(docs[sid])==d['document_sha256']
        winmap={w['window_ref']:w for w in c['registry']['windows']}
        assert len(winmap)==len(c['registry']['windows'])
        for w in winmap.values():
            doc=docs[docmap[w['doc_ref']]['docid']];assert doc[w['offset']:w['offset']+len(w['text'])]==w['text'];assert sh(w['text'])==w['text_sha256'];window_checks+=1
        for w in base['registry']['windows']:assert {k:winmap[w['window_ref']][k] for k in w}==w
        seen={w['window_ref']:w for w in base['registry']['windows']}
        for d in c['decisions']:
            s=d['step'];a=d['actor'];rp=directory/f'decision{s}_request.json';req=rd(rp);fr=rd(directory/f'decision{s}_REQUEST_FREEZE.json');v=json.loads(req['messages'][1]['content'])
            assert digest(req)==a['request_sha256']==fr['request_sha256'];assert sha(rp)==fr['request_file_sha256'];assert dt(fr['utc'])<=dt(a['started_utc'])
            assert v['Original Question']==base['question'] and v['Current Research Need']==base['need'] and v['Working Hypothesis']==base['hypothesis'] and v['Current Claims']==[x['statement'] for x in base['claims']]
            assert {w['window_ref']:w for w in v['New Observations']}=={ref:{k:w[k] for k in ['window_ref','doc_ref','title','url','text']} for ref,w in seen.items()}
            assert 'Candidate' not in v and 'Constraint' not in v and 'gold_doc_ref' not in v
            if s==1:assert req==initial[cid,arm]==runtime.make_request(base,arm,m.get('oracle'))
            if a['output']:
                cc={**c,'registry':{'documents':c['registry']['documents'],'windows':list(seen.values())}}
                runtime.validate(a['output'],cc,arm,m.get('oracle'))
            raw=rd(directory/f'decision{s}_raw_response.json');raw_status[raw['http_status']]+=1
            api.append((a['started_utc'],a['completed_utc']))
            if d['tool']:
                assert dt(a['completed_utc'])<=dt(d['tool_started_utc']);tool.append((d['tool_started_utc'],d['tool_completed_utc']))
                for w in d['tool']['observations']:assert w==winmap[w['window_ref']];seen[w['window_ref']]=w;observations+=1
            if s>1:assert dt(c['decisions'][s-2]['tool_completed_utc'])<=dt(a['started_utc'])
        assert len(list(directory.glob('*raw_response.json')))==len(c['decisions'])
    assert observations==len(rd(P/'analysis/WINDOW_REVIEW.json'))==312
    assert len(tool)==len(rd(P/'analysis/ACTION_REVIEW.json'))==100
    assert len(api)==len(rd(P/'analysis/CALL_AUDIT.json'))==156
    assert len(list((P/'r1/cells').glob('*/decision*_request.json')))==156
    # Secret check emits only pass/fail; credentials never appear in output.
    from dotenv import dotenv_values
    secret=dotenv_values(ROOT/'.env.deepseek').get('DEEPSEEK_API_KEY');assert secret
    for p in P.rglob('*'):
        if p.is_file() and '__pycache__' not in str(p):assert secret.encode() not in p.read_bytes(),'secret detected in artifact'
    out={'historical_files_unchanged':len(hist),'frozen_inputs_unchanged':len(rd(P/'r1/FREEZE.json')['files']),
    'prefix_hashes_verified':len(inp),'trajectories':len(cs),'model_requests':len(api),'raw_http_statuses':dict(raw_status),'retries':0,'writer_calls':0,
    'tools':len(tool),'returned_windows':observations,'registry_window_byte_checks':window_checks,'unique_full_documents_hashed':len(docs),
    'Q_Claims_H_Need_unchanged':True,'adaptive_observations_equal_actual_previous_history':True,'tool_contracts_validated':True,'every_request_frozen_before_call':True,'artifact_secret_scan':'pass',
    'api_concurrency':concurrency(api),'tool_concurrency':concurrency(tool),'within_trajectory_order':'strictly sequential',
    'binary_verification':'Frozen size/mtime only; known/returned document bytes independently SHA256-checked. No full model/index SHA256 claim.',
    'r1_run_head':rd(P/'r1/STARTED.json')['head']}
    (P/'analysis/INTEGRITY.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
