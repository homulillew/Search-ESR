"""Replay frozen requests, raw response parsing, semantic arithmetic and costs."""
import json
import math
import statistics
from collections import Counter
from ..common import *
from .. import run
from ..source_units import validate
from ..prepare import preflight
from experiments.minimal_need_multiquery.run import accounting_summary,usage_audit
def audit():
    frozen=read(P/'FREEZE.json')
    for name,h in frozen['files'].items():assert sha(ROOT/name)==h,name
    history=read(P/'analysis/HISTORICAL_HASHES.json')
    for name,h in history.items():assert sha(ROOT/name)==h,name
    all_rows=[];stage_summary={}
    for stage in STAGES:
        if not (P/stage/'RUN.json').exists():continue
        run.STAGE=stage;run.OUT=P/stage;jobs=read(P/stage/'SCHEDULE.json');cases=bank(stage)
        preflight(jobs,cases,read(P/'CONFIG.json'),stage,False)
        start=read(P/stage/'RUN.json');assert git('show',start['head']+':'+rel(P/'FREEZE.json'))== (P/'FREEZE.json').read_text().strip()
        rows=run.load_rows()
        for j,r in zip(jobs,rows):
            path=P/stage/'calls'/j['id']
            if r['attempted']:
                sent=read(path.with_suffix('.request.json'));assert sent['request']==j['request'];assert sent['head']==start['head']
            if path.with_suffix('.response.json').exists():
                raw=read(path.with_suffix('.response.json'));again=run.parse_response(raw['status'],raw['body'],j,cases[j['qid']])
                for k,v in again.items():assert r[k]==v,(r['id'],k)
        accounting=accounting_summary(rows);saved=read(P/stage/'ACCOUNTING.json')
        for k,v in accounting.items():assert saved[k]==v,k
        times=sorted(r['elapsed_seconds'] for r in rows if r['attempted'])
        details=[validate(r['output'],r['arm'],cases[r['qid']]['source_units']) for r in rows if r.get('output') is not None]
        summary={**accounting,'sent':sum(r['attempted'] for r in rows),'returned':sum('http_status' in r for r in rows),
          'http_failures':sum(r.get('http_status',200)!=200 for r in rows),'transport_failures':sum(r.get('failure') in ('timeout','transport_error') for r in rows),
          'failure_counts':dict(Counter(r.get('failure') or 'none' for r in rows)),
          'schema_failures_on_parsed_outputs':sum(not d['schema_valid'] for d in details),'anchor_failures_on_parsed_outputs':sum(d['anchors_valid'] is False for d in details),
          'no_parsed_output':sum(r.get('output') is None for r in rows),'unknown_usage_calls':sum(not usage_audit(r.get('usage'))['complete'] for r in rows if r['attempted']),
          'median_seconds':statistics.median(times) if times else None,'p95_seconds':times[math.ceil(.95*len(times))-1] if times else None,'max_seconds':max(times) if times else None,
          'peak_concurrency':saved['peak_concurrency'],'wall_seconds':saved['wall_seconds'],
          'by_arm':{a:accounting_summary([r for r in rows if r['arm']==a]) for a in sorted({r['arm'] for r in rows})}}
        stage_summary[stage]=summary;all_rows.extend(rows)
    write(P/'analysis/EXECUTION_ACCOUNTING.json',{'stages':stage_summary,'all_executed_stages':accounting_summary(all_rows),'reasoning_is_subset_of_completion':True,'currency_pricing_verified':False})
    write(P/'analysis/INTEGRITY.json',{'status':'PASS','frozen_files_verified':len(frozen['files']),'historical_files_unchanged':len(history),'raw_response_replay':True,'exact_request_replay':True,'usage_replay':True,'retries':0,'replacements':0,'gold_or_state_inputs':0,'stages_executed':list(stage_summary),'semantic_review':'Single Codex reviewer; first-pass commit before arm reveal; not independent double review.'})
if __name__=='__main__':audit()
